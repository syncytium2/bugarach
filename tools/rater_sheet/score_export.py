"""Score a rater sheet export against its answer key.

Reads a Qualtrics CSV export (or the preview page's CSV, laid out the same way). Every cell the
sheet wrote is one self-describing line, ``row=r07;judge=probably_real;marks=31.2,52.0``, so no
column map is needed: the scorer finds those cells wherever they are.

For each rater (one response, keyed by ``ResponseId``) it reports:

- **marks against planted events.** A mark is a hit when it falls within ``TOL_SEC`` of an
  event's median onset (``bugarach.score.TOL_SEC``, the bench's own tolerance), matched one to
  one, nearest first. Recall and precision overall and by participation, timing spread and
  background. Marks on rows with nothing planted are all false marks.
- **real or synthetic.** In the pilot, "real" is the fitted field and "synthetic" the flat one
  (``make_pilot.py``). The scorer reports how often each field was called real, and d′ with the
  log-linear correction (add 0.5 to each count), so a rater at chance reads near 0.

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

CELL = re.compile(r"^row=(r\d+);judge=([a-z_]*);marks=([0-9.,]*)$")
REAL = {"sure_real", "probably_real"}


def parse_export(path: Path) -> dict[str, dict[str, dict]]:
    """``{response_id: {row_id: {"judge": str, "marks": [float]}}}``."""
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
            resp[m.group(1)] = dict(judge=m.group(2), marks=sorted(marks))
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


def dprime(hits: int, n_signal: int, fas: int, n_noise: int) -> float:
    z = NormalDist().inv_cdf
    return z((hits + 0.5) / (n_signal + 1)) - z((fas + 0.5) / (n_noise + 1))


def _rate(a: int, b: int) -> float | None:
    return round(a / b, 3) if b else None


def score_response(resp: dict[str, dict], key: dict[str, dict], tol: float = TOL_SEC) -> dict:
    tot = dict(hits=0, events=0, false_marks=0, marks=0)
    by = defaultdict(lambda: dict(hits=0, events=0))
    real_calls = defaultdict(lambda: [0, 0])          # field -> [called real, rows]
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
        if k["events"]:
            for label in (f"participation {k['participation']:.2f}", f"jitter {k['jitter_sec']:g} s",
                          f"background {k['background']}"):
                by[label]["hits"] += sum(hit)
                by[label]["events"] += len(hit)
        real_calls[k["field"]][1] += 1
        real_calls[k["field"]][0] += a["judge"] in REAL
    fit, flat = real_calls["fitted"], real_calls["flat"]
    return dict(
        rows_answered=len(key) - len(missing), rows_missing=missing,
        recall=_rate(tot["hits"], tot["events"]),
        precision=_rate(tot["marks"] - tot["false_marks"], tot["marks"]),
        **tot,
        recall_by={k: dict(v, recall=_rate(v["hits"], v["events"])) for k, v in sorted(by.items())},
        called_real=dict(fitted=_rate(*fit), flat=_rate(*flat)),
        dprime_fitted_vs_flat=round(dprime(fit[0], fit[1], flat[0], flat[1]), 3),
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
              f"{s['marks']}); called real: fitted {s['called_real']['fitted']}, flat "
              f"{s['called_real']['flat']}; d' {s['dprime_fitted_vs_flat']}")
        for label, v in s["recall_by"].items():
            print(f"    {label}: recall {v['recall']} ({v['hits']} of {v['events']} events)")
    if args.json:
        args.json.write_text(json.dumps(scores, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
