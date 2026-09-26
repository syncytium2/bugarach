#!/usr/bin/env python3
"""ADR-0008's floor on the bench's own recordings, and what it leaves the bench to score.

    python tools/probe_bench_floor.py --out <folder> [--seeds 8] [--jobs 20]

**Why.** ADR-0008 decision 5: every bench recording gets its floor from its own null, so a detector
is tuned under the definition it is scored under. The first measurement (2026-09-24, #793) found the
fast and combined recordings' floors at 16–20 co-active ROIs, above every planted event, because
the elevated-rate stretch inside them lifted the whole recording's null. ADR-0009 moved the stretch
into a recording of its own and expected the planted recordings' floors to fall to 5–10 on fast and
combined and 6–8 on slow, the numbers measured then with the stretch generated away. This tool
re-measures on the generator as ADR-0009 builds it:

* ``bench``: each planted recording as one window, which is now the literal reading and the only
  one (no recording's floor is computed with any part of it left out, ADR-0009 decision 1);
* ``elevated_rate``: the elevated-rate recording, stretch included, at each background;
* ``null``: the no-coordination recording's floor, which the empty-recording budget runs on.

For the planted recordings, the share of planted events whose participant count falls below the
floor, overall and **by participation level**: under ADR-0009 decision 2 those are "don't care",
neither hit nor miss.

**The stop rule is printed, not decided here.** Phase 0 step 7 of
``docs/handoffs/2026-09-25-overnight-final-parameters.md``: outside ADR-0009's expected ranges, or the middle planted
level mostly under the floor on quiet recordings, goes to Tony before anything else runs.

It measures and decides nothing. Floors are the ones each recording carries
(``bugarach.bench.recording_floor``: ``event_floor.window_floor`` at ADR-0008's settings, 1,000
draws), so they are the floors the scorer and ``run_detector`` use.
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

BENCHES = ("bugarach.bench", "bugarach.bench_slow", "bugarach.bench_combined")
REGIMES = ("baseline_quiet", "baseline_busy")
STREAM_OF = {"bugarach.bench": "fast", "bugarach.bench_slow": "slow",
             "bugarach.bench_combined": "combined"}
EXPECTED = {"fast": (5, 10), "slow": (6, 8), "combined": (5, 10)}
"""ADR-0009's expected planted-recording floors, in co-active ROIs (its Consequences section)."""


def job(args):
    import importlib

    name, regime, seed = args
    b = importlib.import_module(name)
    # The floor each recording carries (`bench.with_floor`, PR B), which is the one the scorer and
    # `run_detector` use, so this measures what the bench actually scores under.
    s, gt = b.make_recording(regime, seed)
    assert gt.params["hot_window"] is None, "a planted recording still carries the stretch"
    floor = int(gt.params["event_floor"])
    _, ge = b.make_elevated_rate_recording(regime, seed)
    parts = np.array([ev.n_part for ev in gt.events])
    levels = {}
    for ev in gt.events:
        n, u = levels.get(ev.n_part, (0, 0))
        levels[ev.n_part] = (n + 1, u + int(ev.n_part < floor))
    row = dict(bench=STREAM_OF[name], regime=regime, seed=seed, n_roi=gt.params["n_roi"],
               elevated_rate_seed=ge.params["seed"],
               floors=dict(bench=gt.params["event_floor_detail"],
                           elevated_rate=ge.params["event_floor_detail"]),
               share_below_floor=float(np.mean(parts < floor)),
               below_floor_by_participants={str(k): dict(planted=n, below_floor=u)
                                            for k, (n, u) in sorted(levels.items())})
    if regime == "baseline_quiet":
        _, gn = b.make_null_recording(seed)
        row["floors"]["null"] = gn.params["event_floor_detail"]
    return row


def summarize(rows):
    summary, stops = {}, []
    for bench in STREAM_OF.values():
        lo, hi = EXPECTED[bench]
        for regime in REGIMES:
            rs = [r for r in rows if r["bench"] == bench and r["regime"] == regime]
            if not rs:
                continue
            fl = [r["floors"]["bench"]["floor"] for r in rs]
            by = {}
            for r in rs:
                for k, v in r["below_floor_by_participants"].items():
                    n, u = by.get(k, (0, 0))
                    by[k] = (n + v["planted"], u + v["below_floor"])
            levels = sorted(by, key=int)
            ent = dict(bench_floor_range=[min(fl), max(fl)],
                       elevated_rate_floor_range=[
                           min(r["floors"]["elevated_rate"]["floor"] for r in rs),
                           max(r["floors"]["elevated_rate"]["floor"] for r in rs)],
                       share_below_floor_mean=float(np.mean([r["share_below_floor"] for r in rs])),
                       below_floor_by_participants={
                           k: dict(planted=by[k][0], below_floor=by[k][1],
                                   share=by[k][1] / by[k][0]) for k in levels})
            nulls = [r["floors"]["null"]["floor"] for r in rs if "null" in r["floors"]]
            if nulls:
                ent["null_floor_range"] = [min(nulls), max(nulls)]
            summary[f"{bench}/{regime}"] = ent
            if min(fl) < lo or max(fl) > hi:
                stops.append(f"{bench}/{regime}: bench floor {min(fl)}-{max(fl)} co-active ROIs, "
                             f"outside ADR-0009's expected {lo}-{hi}")
            if regime == "baseline_quiet" and len(levels) >= 3:
                mid = levels[len(levels) // 2]
                if by[mid][1] / by[mid][0] > 0.5:
                    stops.append(f"{bench}/{regime}: the middle planted level ({mid} participants) "
                                 f"is mostly under the floor ({by[mid][1]} of {by[mid][0]} events)")
    return summary, stops


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--seeds", type=int, default=8)
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument("--spacing", choices=("bench", "realistic", "orx"), default="bench",
                    help="how the bench spaces its planted events (bench.SPACINGS). ADR-0009's "
                         "expected ranges, and so its stop rule, describe the 'bench' spacing "
                         "only; under the others the floors are measured and reported")
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    from bugarach import bench as _b
    _b.use_spacing(a.spacing)                 # before the pool: every worker reads it
    jobs = [(n, r, s) for n in BENCHES for r in REGIMES for s in range(1, a.seeds + 1)]
    with mp.Pool(a.jobs) as pool:
        rows = pool.map(job, jobs)
    summary, stops = summarize(rows)
    if a.spacing != "bench":
        stops = [f"not applied: ADR-0009's expected ranges describe the 'bench' spacing, and this "
                 f"is '{a.spacing}'"]
    (a.out / "bench_floor.json").write_text(json.dumps(
        dict(rows=rows, summary=summary, stop_rule=stops, expected=EXPECTED,
             spacing=a.spacing,
             note="ADR-0008 per-window floor, bench per ADR-0009"), indent=1))
    for k, v in summary.items():
        print(k, json.dumps(v))
    print("STOP RULE:", "; ".join(stops) if stops else "nothing raised")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
