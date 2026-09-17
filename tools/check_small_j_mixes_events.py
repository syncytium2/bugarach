#!/usr/bin/env python3
"""Does the small-*J* control mix sub-second events into what it attributes to slow modulation?

    python tools/check_small_j_mixes_events.py --out <folder> [--twins 50] [--draws 4] [--jobs 4]

The rigid-shift report's training checks put rigid shift at *J* = 1.6 s beside 10–20 s, on the
reasoning that slow shared modulation survives a 1.6 s shift and sub-second alignment does not. On
real crops the zero-parameter ``slow_modulation`` scorer, which averages the share of active ROIs
over 10 s and so cannot resolve a sub-second event, still separated real from a 1.6 s shift at
0.62–0.63. A reviewing session (2026-09-17) argued the reason: a sub-second event raises the peak
of a 10 s average, and a 1.6 s shift pushes some member onsets out of that peak. If so, the control
mixes events and modulation.

This measures it on synthetic twins, where each ingredient is known. Four twins per draw, all from
``look_rigid_shift_controls.twin_pair`` at the paired checks' participation (0.2):

* ``events`` — planted coordinated events, no modulation;
* ``independent_modulation_with_events`` — the same planted twin, each ROI's rate modulated on its
  own phase (so nothing moves together except the events);
* ``independent_modulation`` — no events, each ROI on its own phase (must read chance);
* ``shared_modulation`` — no events, one phase for every ROI.

Each is scored against its own rigid shift at 1.6, 10 and 20 s by the three count baselines of
``tools/tube_self_supervised.py``, with the same crops, crop score (top 1 %) and tie rule as the
paired checks. If ``slow_modulation`` separates ``independent_modulation_with_events`` from its
1.6 s shift, the small-*J* control reads events as well as modulation. Exploratory.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

J_SEC = (1.6, 10.0, 20.0)
PARTICIPATION = 0.2
TWINS = ("events", "independent_modulation_with_events", "independent_modulation",
         "shared_modulation")


def task(args):
    t, draws = args
    import look_rigid_shift_controls as lc
    import tube_self_supervised as ts

    from bugarach.learn.train import pin_threads

    pin_threads()
    pl, un, shape = lc.twin_pair("fast", None, PARTICIPATION, t)
    L, dt = shape["n_frames"], shape["dt"]
    scorers = {name: ts.model_scorer(ts.baseline_model(name).eval()) for name in ts.BASELINES}
    pairs = {(tw, J, s): [] for tw in TWINS for J in J_SEC for s in scorers}
    for d in range(draws):
        rng_mod = np.random.RandomState(ts.seed31("small-j-mix-mod", t, d))
        twins = {"events": pl,
                 "independent_modulation_with_events": ts.modulated(pl, L, dt, rng_mod, False),
                 "independent_modulation": ts.modulated(un, L, dt, rng_mod, False),
                 "shared_modulation": ts.modulated(un, L, dt, rng_mod, True)}
        for tw, trains in twins.items():
            real = ts.raster_of(trains, L)
            for J in J_SEC:
                Jf = J / dt
                margin = int(np.ceil(max(J_SEC) / dt)) + 1   # one crop grid for every J
                starts = list(range(margin, L - margin - ts.CROP + 1, ts.CROP))
                rng = np.random.RandomState(ts.seed31("small-j-mix-shift", t, d, tw, J))
                sur = ts.raster_of(ts.rigid_frames(trains, L, Jf, rng), L)
                for s, score in scorers.items():
                    pairs[(tw, J, s)] += ts.crop_pairs(score, real, sur, starts)
    return {f"{tw}|{J:g}|{s}": v for (tw, J, s), v in pairs.items()}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--twins", type=int, default=50)
    ap.add_argument("--draws", type=int, default=4)
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args(argv)
    import tube_self_supervised as ts

    from bugarach import provenance

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    merged: dict = {}
    with mp.get_context("spawn").Pool(a.jobs) as pool:
        for r in pool.imap_unordered(task, [(t, a.draws) for t in range(a.twins)]):
            for k, v in r.items():
                merged.setdefault(k, []).extend(v)
    results = {k: ts.paired_summary(v) for k, v in sorted(merged.items())}
    doc = {"meta": {"twins": a.twins, "draws_per_twin": a.draws, "participation": PARTICIPATION,
                    "J_sec": J_SEC, "crop_frames": ts.CROP, "baselines": ts.BASELINES,
                    "modulation": {"period_sec": ts.MOD_PERIOD_SEC, "depth": ts.MOD_DEPTH},
                    "seconds": time.time() - t0, "exploratory": True,
                    "provenance": provenance.stamp(
                        produced_by="tools/check_small_j_mixes_events.py")},
           "share_real_higher": results}
    (out / "results.json").write_text(json.dumps(doc, indent=1, default=float) + "\n")
    for k, v in results.items():
        print(f"{k:60s} {v['share_real_higher']:.3f}  (n={v['n_crops']}, ties {v['tie_share']:.2f})")


if __name__ == "__main__":
    main()
