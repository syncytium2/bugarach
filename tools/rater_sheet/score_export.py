"""Score a rater sheet export against its answer key.

Reads a Qualtrics CSV export (or the preview page's CSV, laid out the same way). Every cell the
sheet wrote is one self-describing line, ``row=r07;real=0.45;marks=31.2,52.0``, so no column map is
needed: the scorer finds those cells wherever they are. ``real`` is the slider: +1 sure it is real,
0 no idea, -1 sure it is synthetic.

For each rater (one response, keyed by ``ResponseId``) it reports:

- **marks against planted events.** A mark is a hit when it falls within ``TOL_SEC`` of an
  event's median onset (``bugarach.score.TOL_SEC``, the bench's own tolerance), matched one to
  one, nearest first. Recall and precision overall; recall by each event's participation, and by
  the row's timing spread and background. Marks on rows with nothing planted are all false marks.
- **real or synthetic.** In the pilot, "real" is the fitted field and "synthetic" the flat one
  (``make_pilot.py``). The scorer reports the mean slider value per field and the **AUC**, the
  chance that a fitted row was rated more real than a flat one (ties count half): 0.5 is chance.
  d′ is derived from it under the equal-variance model, d′ = √2·z(AUC).

    python tools/rater_sheet/score_export.py EXPORT.csv KEY.json [--json OUT]
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from statistics import NormalDist

from bugarach.score import TOL_SEC

CELL = re.compile(r"^row=(r\d+);real=(-?[0-9.]*);marks=([0-9.,]*)$")


def parse_export(path: Path) -> dict[str, dict[str, dict]]:
    """``{response_id: {row_id: {"real": float | None, "marks": [float]}}}``."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    if not rows:
        return {}
    header = rows[0]
    rid_col = header.index("ResponseId") if "ResponseId" in header else None
    out: dict[str, dict[str, dict]] = {}
    for n, r in enumerate(rows[1:], start=1):
        cells = [CELL.match(c.strip()) for c in r]
        found = [m for m in cells if m]
        if not found:
            continue                                   # Qualtrics' second and third header rows
        rid = r[rid_col] if rid_col is not None and rid_col < len(r) else f"response{n}"
        resp = out.setdefault(rid, {})
        for m in found:
            marks = [float(x) for x in m.group(3).split(",") if x]
            resp[m.group(1)] = dict(real=float(m.group(2)) if m.group(2) else None, marks=sorted(marks))
    return out


def match(marks: list[float], events: list[dict], tol: float = TOL_SEC) -> tuple[list[bool], int]:
    """One-to-one, nearest pairs first. Returns (hit per event, false marks)."""
    pairs = sorted((abs(m - e["time"]), i, j) for i, m in enumerate(marks)
                   for j, e in enumerate(events) if abs(m - e["time"]) <= tol)
    used_m, used_e = set(), set()
    for _, i, j in pairs:
        if i in used_m or j in used_e:
            continue
        used_m.add(i)
        used_e.add(j)
    return [j in used_e for j in range(len(events))], len(marks) - len(used_m)


def auc(signal: list[float], noise: list[float]) -> float | None:
    """P(a signal rating exceeds a noise rating), ties counting half."""
    if not signal or not noise:
        return None
    wins = sum((s > n) + 0.5 * (s == n) for s in signal for n in noise)
    return wins / (len(signal) * len(noise))


def dprime_from_auc(a: float | None) -> float | None:
    if a is None:
        return None
    a = min(max(a, 0.5 / 1000), 1 - 0.5 / 1000)
    return 2 ** 0.5 * NormalDist().inv_cdf(a)


def _rate(a: int, b: int) -> float | None:
    return round(a / b, 3) if b else None


def score_response(resp: dict[str, dict], key: dict[str, dict], tol: float = TOL_SEC) -> dict:
    tot = dict(hits=0, events=0, false_marks=0, marks=0)
    by = defaultdict(lambda: dict(hits=0, events=0))
    ratings = defaultdict(list)                       # field -> slider values
    missing = []
    for rid, k in key.items():
        if rid not in resp:
            missing.append(rid)
            continue
        a = resp[rid]
        hit, fm = match(a["marks"], k["events"], tol)
        tot["hits"] += sum(hit)
        tot["events"] += len(hit)
        tot["false_marks"] += fm
        tot["marks"] += len(a["marks"])
        for ev, h in zip(k["events"], hit):
            for label in (f"participation {ev['participation']:.2f}", f"jitter {k['jitter_sec']:g} s",
                          f"background {k['background']}"):
                by[label]["hits"] += h
                by[label]["events"] += 1
        if a["real"] is not None:
            ratings[k["field"]].append(a["real"])
    a_ = auc(ratings["fitted"], ratings["flat"])
    mean = lambda v: round(sum(v) / len(v), 3) if v else None
    return dict(
        rows_answered=len(key) - len(missing), rows_missing=missing,
        recall=_rate(tot["hits"], tot["events"]),
        precision=_rate(tot["marks"] - tot["false_marks"], tot["marks"]),
        **tot,
        recall_by={k: dict(v, recall=_rate(v["hits"], v["events"])) for k, v in sorted(by.items())},
        mean_realness=dict(fitted=mean(ratings["fitted"]), flat=mean(ratings["flat"])),
        auc_fitted_vs_flat=None if a_ is None else round(a_, 3),
        dprime_fitted_vs_flat=None if a_ is None else round(dprime_from_auc(a_), 3),
        tol_sec=tol,
    )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("export", type=Path)
    ap.add_argument("key", type=Path)
    ap.add_argument("--json", type=Path, help="also write the scores here")
    args = ap.parse_args(argv)
    key = json.loads(args.key.read_text(encoding="utf-8"))["rows"]
    responses = parse_export(args.export)
    if not responses:
        print("No rater sheet answers found in", args.export)
        return 1
    scores = {rid: score_response(r, key) for rid, r in responses.items()}
    for rid, s in scores.items():
        print(f"{rid}: {s['rows_answered']} rows; recall {s['recall']} ({s['hits']} of "
              f"{s['events']} events), precision {s['precision']} ({s['false_marks']} false marks of "
              f"{s['marks']}); mean realness: fitted {s['mean_realness']['fitted']}, flat "
              f"{s['mean_realness']['flat']}; AUC {s['auc_fitted_vs_flat']}, d' {s['dprime_fitted_vs_flat']}")
        for label, v in s["recall_by"].items():
            print(f"    {label}: recall {v['recall']} ({v['hits']} of {v['events']} events)")
    if args.json:
        args.json.write_text(json.dumps(scores, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
