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

import numpy as np

from bugarach.score import TOL_SEC

CELL = re.compile(r"^row=(r\d+);real=(-?[0-9.]*);marks=([0-9.,]*)(?:;spans=([0-9.,]*))?$")


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
            spans = [float(x) for x in (m.group(4) or "").split(",") if x]
            resp[m.group(1)] = dict(real=float(m.group(2)) if m.group(2) else None, marks=marks,
                                    spans=spans if len(spans) == len(marks) else [None] * len(marks))
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
        if k.get("kind") == "separation":
            continue                                  # scored by score_separation
        if rid not in resp:
            missing.append(rid)
            continue
        a = resp[rid]
        hit, fm = match(sorted(a["marks"]), k["events"], tol)
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
        rows_answered=sum(k.get("kind") != "separation" for k in key.values()) - len(missing),
        rows_missing=missing,
        recall=_rate(tot["hits"], tot["events"]),
        precision=_rate(tot["marks"] - tot["false_marks"], tot["marks"]),
        **tot,
        recall_by={k: dict(v, recall=_rate(v["hits"], v["events"])) for k, v in sorted(by.items())},
        mean_realness=dict(fitted=mean(ratings["fitted"]), flat=mean(ratings["flat"])),
        auc_fitted_vs_flat=None if a_ is None else round(a_, 3),
        dprime_fitted_vs_flat=None if a_ is None else round(dprime_from_auc(a_), 3),
        tol_sec=tol,
    )


# ---- the separation test (Tony, 2026-10-25: "What is the limit of human detection of separation") ----

def separation_outcomes(resp: dict[str, dict], key: dict[str, dict], tol: float = TOL_SEC) -> list[dict]:
    """One outcome per planted item on the separation rows.

    A **pair** is looked at over [first event - tol, second event + tol], each event at its median
    onset. Every mark in that stretch goes to the nearer of the two events. The pair is **resolved**
    when both events got a mark, and **detected** when either did. A **single** is looked at over
    [event - tol, event + tol], and it is **split** when it got two marks or more: that is the
    false alarm for "two where there was one". ``zoom_sec`` is the narrowest view, in seconds, that
    any mark in the stretch was placed at (None when the export has no spans)."""
    out = []
    for rid, k in key.items():
        if k.get("kind") != "separation" or rid not in resp:
            continue
        a = resp[rid]
        marks = list(zip(a["marks"], a.get("spans") or [None] * len(a["marks"])))
        for it in k["items"]:
            times = [e["median_onset"] for e in it["events"]]
            lo, hi = times[0] - tol, times[-1] + tol
            inside = [(m, w) for m, w in marks if lo <= m <= hi]
            widths = [w for _, w in inside if w is not None]
            o = dict(row=rid, kind=it["kind"], delta_sec=it["delta_sec"], jitter_sec=k["jitter_sec"],
                     background=k["background"], n_marks=len(inside),
                     zoom_sec=min(widths) if widths else None)
            if it["kind"] == "pair":
                got = [False, False]
                for m, _ in inside:
                    got[0 if abs(m - times[0]) <= abs(m - times[1]) else 1] = True
                # The planned separation is the design variable. The realized one, between the two
                # groups' median onsets, can be smaller: at wide timing and 0.5 s the two medians can
                # coincide, and then no rater can split the pair.
                o.update(resolved=all(got), detected=any(got),
                         realized_delta_sec=round(abs(times[1] - times[0]), 2))
            else:
                o.update(split=len(inside) >= 2, detected=bool(inside))
            out.append(o)
    return out


def fit_threshold(points: list[tuple[float, bool]], fa: float) -> dict:
    """Maximum likelihood fit of P(resolved | D) = fa + (1 - fa) / (1 + exp(-(ln D - ln D50) / s)).

    ``fa`` is the split rate on singles, so D50 is where resolving runs halfway between the
    false-alarm floor and certainty, and D75 three quarters of the way. A grid search, deliberately:
    there are a few dozen points at most, and the answer must be the same everywhere it is run."""
    if not points:
        return dict(n=0, delta50_sec=None, delta75_sec=None, slope=None, false_alarm=None,
                    note="no pairs answered")
    fa = min(max(fa, 0.0), 0.95)
    d = np.array([p[0] for p in points], float)
    y = np.array([p[1] for p in points], float)
    best = (-np.inf, None, None)
    for l50 in np.linspace(np.log(0.05), np.log(50.0), 400):
        for s in np.linspace(0.05, 3.0, 60):
            pr = fa + (1 - fa) / (1 + np.exp(-(np.log(d) - l50) / s))
            pr = np.clip(pr, 1e-6, 1 - 1e-6)
            ll = float(np.sum(y * np.log(pr) + (1 - y) * np.log(1 - pr)))
            if ll > best[0]:
                best = (ll, l50, s)
    _, l50, s = best
    d50, d75 = float(np.exp(l50)), float(np.exp(l50 + s * np.log(3.0)))
    lo, hi = float(d.min()), float(d.max())
    if y.all():
        note = "every pair resolved: the limit is below the smallest separation tested"
    elif not y.any():
        note = "no pair resolved: the limit is above the largest separation tested"
    elif not (lo <= d50 <= hi):
        note = "outside the tested range; read it as a bound"
    else:
        note = ""
    return dict(n=len(points), delta50_sec=round(d50, 2), delta75_sec=round(d75, 2),
                slope=round(float(s), 2), false_alarm=round(fa, 3), note=note)


def score_separation(outcomes: list[dict]) -> dict:
    """P(resolved) against separation, overall and per condition, with the singles' split rate and
    a fitted limit."""
    def summarise(rows):
        pairs = [o for o in rows if o["kind"] == "pair"]
        singles = [o for o in rows if o["kind"] == "single"]
        fa = sum(o["split"] for o in singles) / len(singles) if singles else 0.0
        by_delta = {}
        for dlt in sorted({o["delta_sec"] for o in pairs}):
            g = [o for o in pairs if o["delta_sec"] == dlt]
            z = [o["zoom_sec"] for o in g if o["zoom_sec"] is not None]
            by_delta[f"{dlt:g}"] = dict(n=len(g), resolved=_rate(sum(o["resolved"] for o in g), len(g)),
                                        detected=_rate(sum(o["detected"] for o in g), len(g)),
                                        median_zoom_sec=float(np.median(z)) if z else None)
        return dict(singles=len(singles), split_rate=round(fa, 3) if singles else None,
                    p_resolved_by_delta=by_delta,
                    fit=fit_threshold([(o["delta_sec"], o["resolved"]) for o in pairs], fa))
    conds = sorted({(o["jitter_sec"], o["background"]) for o in outcomes})
    return dict(overall=summarise(outcomes),
                by_condition={f"jitter {j:g} s, {b}": summarise(
                    [o for o in outcomes if (o["jitter_sec"], o["background"]) == (j, b)])
                    for j, b in conds})


def _print_separation(label: str, sep: dict) -> None:
    ov = sep["overall"]
    if not ov["p_resolved_by_delta"] and not ov["singles"]:
        return
    f = ov["fit"]
    print(f"  separation, {label}: limit D50 {f['delta50_sec']} s, D75 {f['delta75_sec']} s; "
          f"singles split {ov['split_rate']}" + (f" ({f['note']})" if f["note"] else ""))
    for dlt, v in ov["p_resolved_by_delta"].items():
        print(f"    separation {dlt} s: resolved {v['resolved']}, detected {v['detected']} "
              f"(n {v['n']}), narrowest view {v['median_zoom_sec']} s")


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
    outcomes = {rid: separation_outcomes(r, key) for rid, r in responses.items()}
    for rid in scores:
        scores[rid]["separation"] = score_separation(outcomes[rid])
    for rid, s in scores.items():
        print(f"{rid}: {s['rows_answered']} rows; recall {s['recall']} ({s['hits']} of "
              f"{s['events']} events), precision {s['precision']} ({s['false_marks']} false marks of "
              f"{s['marks']}); mean realness: fitted {s['mean_realness']['fitted']}, flat "
              f"{s['mean_realness']['flat']}; AUC {s['auc_fitted_vs_flat']}, d' {s['dprime_fitted_vs_flat']}")
        for label, v in s["recall_by"].items():
            print(f"    {label}: recall {v['recall']} ({v['hits']} of {v['events']} events)")
        _print_separation("this rater", s["separation"])
    pooled = score_separation([o for v in outcomes.values() for o in v])
    if len(responses) > 1:
        _print_separation(f"all {len(responses)} raters pooled", pooled)
    if args.json:
        args.json.write_text(json.dumps(dict(raters=scores, separation_pooled=pooled), indent=1),
                             encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
