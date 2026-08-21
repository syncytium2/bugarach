#!/usr/bin/env python3
"""Does the quiet tail survive the events planted on top of it?

    python tools/quiet_tail_vs_events.py            # the table in the todo
    python tools/quiet_tail_vs_events.py --seeds 60

``bg_rate_shape`` exists to reproduce one fact about real fields: 35% of ROIs
record no event at all in a baseline window. It does — and then the coordinated
events go in, participants drawn uniformly over ROIs, and almost nobody is left
quiet. This prints that, so the claim in
``docs/todo/2026-08-17-planted-events-erase-the-quiet-tail.md`` can be re-taken
rather than believed, and moves when the generator does.

Reads no store: everything here comes from a seed.
"""

from __future__ import annotations

import argparse

import numpy as np

from bugarach.bench import (
    MEASURED_BURST_BINS,
    MEASURED_BURST_SHAPE,
    MEASURED_RATE_SHAPE,
)
from bugarach.simulate import simulate_coordination

# The bench recording's own structure, so the answer is about the regime the
# detectors are actually scored in — 33 ROIs, 45 minutes, the measured rate.
RECORDING = dict(duration_sec=2700.0, n_roi=33, bg_rate_hz=0.0096,
                 jitter_sec=0.36, min_sep_sec=120.0)
MEASURED_PART = (0.30, 0.18, 0.10)
GUESSED_PART = (1.0, 0.75, 0.50)


def quiet_fraction(seeds: int, *, shaped: bool, n_per_level, participation):
    """Share of ROIs whose train is empty, averaged over seeds.

    Empty means **no events in this window** and nothing more: it is not a
    viability verdict, which is the exporter's and needs every treatment of an
    ROI at once (FOUNDATIONS §9).
    """
    out = []
    for seed in range(1, seeds + 1):
        slice_, _ = simulate_coordination(
            **RECORDING,
            bg_rate_shape=MEASURED_RATE_SHAPE if shaped else None,
            bg_burst_shape=MEASURED_BURST_SHAPE if shaped else None,
            bg_burst_bin_sec=MEASURED_BURST_BINS if shaped else 60.0,
            participation=participation, n_per_level=n_per_level, seed=seed)
        locs = slice_.streams["events"].locs
        out.append(float(np.mean([len(v) == 0 for v in locs])))
    return 100.0 * float(np.mean(out))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seeds", type=int, default=20)
    args = ap.parse_args(argv)

    none = (0, 0, 0)
    fifteen = (5, 5, 5)
    rows = [
        ("fitted background, no planted events", True, none, MEASURED_PART),
        ("fitted background, 15 events at 30/18/10%", True, fifteen, MEASURED_PART),
        ("fitted background, 15 events at 100/75/50%", True, fifteen, GUESSED_PART),
        ("flat background, no planted events", False, none, MEASURED_PART),
        ("flat background, 15 events at 30/18/10%", False, fifteen, MEASURED_PART),
    ]
    print(f"{RECORDING['n_roi']} ROI, {RECORDING['duration_sec'] / 60:.0f} min, "
          f"{RECORDING['bg_rate_hz'] * 1000:.1f} mHz mean per ROI, "
          f"{args.seeds} seeds\n")
    for label, shaped, n_per_level, part in rows:
        pct = quiet_fraction(args.seeds, shaped=shaped, n_per_level=n_per_level,
                             participation=part)
        print(f"  {label:44s} {pct:5.1f}%  ROIs with no event")

    print("\n35% is what real baseline windows give (bench.MEASURED_RATE_SHAPE, "
          "81 windows / 2 643 ROIs).")
    print("Participants are drawn uniformly, so at a mean participating fraction "
          "of 19% an ROI\nescapes all 15 events with probability 0.81^15 — about "
          "4%, or one ROI of 33.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
