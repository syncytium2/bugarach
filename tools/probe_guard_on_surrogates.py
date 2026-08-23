#!/usr/bin/env python3
"""Does a guard interval help the two surrogate-null detectors?

    python tools/probe_guard_on_surrogates.py

`docs/forks.md` §4 records that the guard does nothing for `rate+context`, and why
in arithmetic: its bar is a fixed 2-5 Hz constant while the contamination it
removes is worth 0.14 Hz. It also predicts where the guard SHOULD matter — `loco`
and `coact`, whose bar is a percentile of a null pool built from the events inside
the window, so contamination scales the threshold directly rather than adding to a
constant.

This tests that prediction on two recordings:

* ``baseline_quiet`` — events >=120 s apart against a +/-30 s reference window, so
  a second event can never contaminate the first one's context. The guard should
  do nothing here **by construction**, and if it appears to, something else moved.
* ``CROWDED_RECORDING`` — 120 events, median gap 19.4 s, 97 of 119 gaps inside one
  reference window. This is the condition the guard exists for.
"""

from __future__ import annotations

import sys

import numpy as np

from bugarach.bench import (BENCH_RECORDING, make_crowded_recording,
                            make_recording)
from bugarach.detectors.coact import coact_detect
from bugarach.detectors.loco import loco_detect
from bugarach.detectors.rate import recording_extent, stream_trains
from bugarach.score import score_stream

SEEDS = (1, 2, 3, 4)
GUARDS = (0.0, 5.0, 10.0, 20.0)
STREAM = "events"


def run(which, maker, guard, seed):
    sl, gt = maker(seed)
    ext = recording_extent(sl)
    if which == "loco":
        r = loco_detect(sl, rng_seed=7, bin_width_sec=1.0, context_win_sec=120.0,
                        thr_step_sec=15.0, merge_gap_sec=2.0,
                        threshold_pctile=99.9, n_surrogates=100,
                        guard_sec=guard).streams[STREAM]
    else:
        trains = stream_trains(sl.streams[STREAM], ext)
        r = coact_detect(trains, ext, rng_seed=7, int_win_sec=2.0,
                         context_win_sec=60.0, alpha=1e-4, n_surrogates=100,
                         guard_sec=guard)
    return score_stream(gt, r, tol_sec=1.5)


def pooled(which, maker, guard):
    hit = det = plant = 0
    for s in SEEDS:
        sc = run(which, maker, guard, s)
        hit += sc.n_hit
        det += sc.n_detected
        plant += sc.n_planted
    p = hit / det if det else float("nan")
    rc = hit / plant if plant else float("nan")
    return (2 * p * rc / (p + rc) if p + rc else 0.0), p, rc


def main(argv=None) -> int:
    print(f"{len(SEEDS)} seeds, shipped operating points, tol 1.5 s\n")
    for label, maker in (("baseline_quiet — events >=120 s apart, "
                          "contamination IMPOSSIBLE",
                          lambda s: make_recording("baseline_quiet", s)),
                         ("CROWDED — median gap 19.4 s, contamination LIKELY",
                          make_crowded_recording)):
        print(label)
        print(f"  {'detector':8s} {'guard':>6s} {'F1':>6s} {'prec':>6s} {'rec':>6s}")
        for which in ("loco", "coact"):
            base = None
            for g in GUARDS:
                f1, p, rc = pooled(which, maker, g)
                base = f1 if base is None else base
                mark = "" if g == 0 else f"  ({f1 - base:+.3f})"
                print(f"  {which:8s} {g:6.1f} {f1:6.3f} {p:6.3f} {rc:6.3f}{mark}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
