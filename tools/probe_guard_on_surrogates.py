#!/usr/bin/env python3
"""Does a guard interval help the two surrogate-null detectors?

    python tools/probe_guard_on_surrogates.py

`docs/forks.md` §4 records that the guard does nothing for `rate+context`, and why
in arithmetic: its bar is a fixed 2-5 Hz constant while the contamination it
removes is worth 0.14 Hz. It also predicts where the guard SHOULD matter — `loco`
and `coact`, whose bar is a percentile of a null pool built from the events inside
the window, so contamination scales the threshold directly rather than adding to a
constant.

**The measurement is within one recording, not between two**, and that is what
decides the question. ``CROWDED_RECORDING`` runs three hours so that about 38% of
its events have a neighbour inside their own ±30 s reference window and about 31%
have nothing within 60 s. Recall is per-event, so splitting it by each event's own
nearest-neighbour gap (:func:`~bugarach.bench.nearest_neighbour_gaps`) holds the
event count, the duration, the background and the false-alarm opportunity fixed by
construction.

**The guard's signature, if masking is what it relieves:** recall rises for events
*with* a close neighbour and does nothing for isolated ones, where there is no
neighbour to unmask. A gain that is flat across the gap is a threshold shift
wearing a masking costume.

⚠ **Two earlier runs of this probe were wrong, and the second is the instructive
one.** The first, 2026-08-23, ran off the difficulty axis:
``make_crowded_recording`` merged no regime, so its background came from
``simulate_coordination``'s 0.05 Hz default, ~10× the quiet endpoint. The second
fixed that but still compared *between* recordings, on a 45-minute crowded
recording in which every event was crowded — so it had no control group, read the
guard's uniform bar-lowering as masking relief, and reported that the prediction
held. It does not. `docs/forks.md` §4a.
"""

from __future__ import annotations

import sys

import numpy as np

from bugarach.bench import (CROWDING_GAP_SEC, make_crowded_recording,
                            make_recording, nearest_neighbour_gaps)
from bugarach.detectors.coact import coact_detect
from bugarach.detectors.loco import loco_detect
from bugarach.detectors.rate import recording_extent, stream_trains
from bugarach.score import score_stream

SEEDS = (1, 2, 3, 4, 5, 6, 7, 8)
GUARDS = (0.0, 5.0, 10.0, 20.0)
STREAM = "events"
REGIME = "baseline_quiet"

#: Nearest-neighbour bands, in units of :data:`CROWDING_GAP_SEC`. The last is the
#: control: no neighbour within twice the half-context, so nothing to unmask.
BANDS = ((0.0, 0.5), (0.5, 1.0), (1.0, 2.0), (2.0, np.inf))


def detect(which, sl, guard):
    if which == "loco":
        return loco_detect(sl, rng_seed=7, bin_width_sec=1.0, context_win_sec=120.0,
                           thr_step_sec=15.0, merge_gap_sec=2.0,
                           threshold_pctile=99.9, n_surrogates=100,
                           guard_sec=guard).streams[STREAM]
    ext = recording_extent(sl)
    trains = stream_trains(sl.streams[STREAM], ext)
    return coact_detect(trains, ext, rng_seed=7, int_win_sec=2.0,
                        context_win_sec=60.0, alpha=1e-4, n_surrogates=100,
                        guard_sec=guard)


def pooled(which, maker, guard, by_gap=False):
    """Pooled score, and — on request — recall split by nearest-neighbour gap."""
    hits, gaps = [], []
    n_hit = n_det = n_plant = 0
    for seed in SEEDS:
        sl, gt = maker(seed)
        sc = score_stream(gt, detect(which, sl, guard), tol_sec=1.5)
        n_hit += sc.n_hit
        n_det += sc.n_detected
        n_plant += sc.n_planted
        if by_gap:
            hits.append(sc.hits)
            gaps.append(nearest_neighbour_gaps(gt))
    p = n_hit / n_det if n_det else float("nan")
    rc = n_hit / n_plant if n_plant else float("nan")
    f1 = 2 * p * rc / (p + rc) if p + rc else 0.0
    if not by_gap:
        return f1, p, rc, None
    h, g = np.concatenate(hits), np.concatenate(gaps)
    band = [(h[(g >= lo * CROWDING_GAP_SEC) & (g < hi * CROWDING_GAP_SEC)])
            for lo, hi in BANDS]
    return f1, p, rc, band


def main(argv=None) -> int:
    print(f"{len(SEEDS)} seeds, shipped operating points, tol 1.5 s, "
          f"regime {REGIME!r}\n")

    print("BETWEEN recordings — the sparse bench, where contamination is "
          "IMPOSSIBLE by construction")
    print(f"  {'detector':8s} {'guard':>6s} {'F1':>6s} {'prec':>6s} {'rec':>6s}")
    for which in ("loco", "coact"):
        base = None
        for g in GUARDS:
            f1, p, rc, _ = pooled(which, lambda s: make_recording(REGIME, s), g)
            base = f1 if base is None else base
            mark = "" if g == 0 else f"  ({f1 - base:+.3f})"
            print(f"  {which:8s} {g:6.1f} {f1:6.3f} {p:6.3f} {rc:6.3f}{mark}")

    print("\nWITHIN the crowded recording — recall by each event's own "
          "nearest-neighbour gap")
    edges = "  ".join(f"{lo * CROWDING_GAP_SEC:g}-"
                      f"{hi * CROWDING_GAP_SEC:g}s".replace("-infs", "+s")
                      for lo, hi in BANDS)
    print(f"  {'detector':8s} {'guard':>6s} {'F1':>6s} {'prec':>6s} "
          f"{'rec':>6s}  |  {edges}   <- last band is the CONTROL")
    for which in ("loco", "coact"):
        base = None
        for g in GUARDS:
            f1, p, rc, band = pooled(
                which, lambda s: make_crowded_recording(REGIME, s), g, by_gap=True)
            rates = [b.mean() if b.size else float("nan") for b in band]
            if base is None:
                base, cells = rates, [f"{r:.3f}       " for r in rates]
            else:
                cells = [f"{r:.3f}({r - b:+.3f})" for r, b in zip(rates, base)]
            print(f"  {which:8s} {g:6.1f} {f1:6.3f} {p:6.3f} {rc:6.3f}  |  "
                  + "  ".join(cells))
        ns = [b.size for b in band]
        print(f"  {'':8s} {'':6s} {'':6s} {'':6s} {'':6s}  |  "
              + "  ".join(f"n={n:<11d}" for n in ns))
    return 0


if __name__ == "__main__":
    sys.exit(main())
