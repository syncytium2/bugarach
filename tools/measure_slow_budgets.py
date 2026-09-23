#!/usr/bin/env python3
"""Re-measure the false-alarm budgets on the slow bench, at the settings the search starts from.

    python tools/measure_slow_budgets.py --jobs 12     # measure both benches, write the record

Tony, 2026-09-21, asked how the slow bench's false-alarm budgets should be set: *"remeasure"*.
The fast budgets in ``bench.py`` are **measured baselines with headroom** — each detector's
rate at its shipped setting, rounded up — so a slow copy of the fast numbers would be a
budget measured on a different stream. This measures the same three quantities the search's
admissibility test reads (``tools/search_all_settings.py``, ``admissible``), at
``bench_slow.OPERATING_POINTS`` (the fast settings, which is where the slow search starts):

- **elevated-rate test**: calls per minute inside the probe window, on each background; the
  budget is against the larger of the two;
- **no-coordination test**: calls per hour on the empty recording at the quiet background;
- **precision swing**: |precision quiet − precision busy| at one setting.

**It measures the fast bench too, same seeds, same code path**, so the headroom rule that
turns a measurement into a ceiling can be checked against the ceilings ``bench.py`` already
declares before it is applied to slow. The record says both.

Seeds 1–48: the recordings the search chooses on.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import importlib
import json
import math
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO / "src") not in sys.path:
    sys.path.insert(0, str(REPO / "src"))

RECORD = "docs/learned/bench_slow_budgets.json"
SEEDS = tuple(range(1, 49))
REGIMES = ("baseline_quiet", "baseline_busy")


def _job(args):
    module, det, what = args
    b = importlib.import_module(module)
    if what == "null":
        return module, det, what, b.false_positives_per_hour(det, seeds=SEEDS)
    r = b.evaluate(det, what, SEEDS)
    return module, det, what, dict(probe=r.hot_fa_per_min, precision=r.precision, f1=r.f1)


def ceiling_rate(measured: float) -> float:
    """A rate budget from a measured rate: 1.6 times it, rounded up to a whole call, at least 1."""
    return float(max(1, math.ceil(1.6 * measured - 1e-9)))


def ceiling_swing(measured: float) -> float:
    """A precision-swing budget: the measured swing plus 0.05, up to a 0.05 step, at least 0.10."""
    return round(max(0.10, math.ceil((measured + 0.05) / 0.05 - 1e-9) * 0.05), 2)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--jobs", type=int, default=1)
    p.add_argument("--no-write", action="store_true")
    p.add_argument("--bench", choices=("slow", "combined"), default="slow",
                   help="the bench to budget (default slow); combined writes "
                        "bench_combined.BUDGETS_RECORD. The fast bench is always measured beside it")
    a = p.parse_args(argv)

    from bugarach import bench

    target = importlib.import_module(f"bugarach.bench_{a.bench}")
    bench_slow = target  # the name the rest of this function reads; slow unless --bench combined
    record_path = target.BUDGETS_RECORD
    mods = {"bugarach.bench": bench, target.__name__: target}
    tasks = [(m, d, w) for m in mods for d in bench_slow.DETECTORS
             for w in (*REGIMES, "null")]
    if a.jobs > 1:
        with ProcessPoolExecutor(max_workers=a.jobs) as ex:
            out = list(ex.map(_job, tasks))
    else:
        out = [_job(t) for t in tasks]
    got: dict = {}
    for m, d, w, v in out:
        got.setdefault(m, {}).setdefault(d, {})[w] = v

    rows = {}
    for m, mod in mods.items():
        rows[m] = {}
        for d in bench_slow.DETECTORS:
            g = got[m][d]
            probe = max(g[r]["probe"] for r in REGIMES)
            swing = abs(g["baseline_quiet"]["precision"] - g["baseline_busy"]["precision"])
            row = dict(probe_per_min=probe, null_per_hour=g["null"], precision_swing=swing,
                       f1_quiet=g["baseline_quiet"]["f1"], f1_busy=g["baseline_busy"]["f1"],
                       ceiling_probe=ceiling_rate(probe), ceiling_null=ceiling_rate(g["null"]),
                       ceiling_swing=ceiling_swing(swing))
            if m == "bugarach.bench":
                row.update(declared_probe=bench.MAX_PROBE_PER_MIN[d],
                           declared_null=bench.MAX_FALSE_POSITIVES_PER_HOUR[d],
                           declared_swing=bench.MAX_PRECISION_DROP[d])
            rows[m][d] = row

    for m in mods:
        print(f"\n{m}  (seeds 1-48, at {target.__name__}.OPERATING_POINTS)")
        print(f"{'detector':8s} {'probe/min':>10s} {'null/h':>8s} {'swing':>7s}   "
              f"{'-> ceilings':>12s}{'':14s}{'declared (fast)':>18s}")
        for d, r in rows[m].items():
            dec = (f"{r['declared_probe']:5g} {r['declared_null']:5g} {r['declared_swing']:5g}"
                   if "declared_probe" in r else "")
            print(f"{d:8s} {r['probe_per_min']:10.2f} {r['null_per_hour']:8.2f} "
                  f"{r['precision_swing']:7.3f}   {r['ceiling_probe']:5g} {r['ceiling_null']:5g} "
                  f"{r['ceiling_swing']:5g}      {dec}")

    if not a.no_write:
        from bugarach import dataset
        rec = dict(tool="tools/measure_slow_budgets.py", measured_on=_dt.date.today().isoformat(),
                   seeds=[SEEDS[0], SEEDS[-1]], rule_rate="max(1, ceil(1.6 x measured))",
                   rule_swing="max(0.10, ceil((measured + 0.05) / 0.05) x 0.05)",
                   slow_measured_on=dataset.current_name(), rows=rows)
        (REPO / record_path).write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n",
                                   encoding="utf-8")
        print(f"\nwrote {record_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
