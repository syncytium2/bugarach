"""Does the guard help where mutual masking can actually happen?

The bench plants events >=120 s apart against a +/-30 s reference window, so a
second event can never contaminate the first one's context. That is the exact
condition the guard exists for, so the bench cannot measure it — which is the
finding, not a null result.

This sweeps event SPACING instead: same recording length, same background, same
detector, events packed from far apart to well inside one context window.
"""
import numpy as np

from bugarach.detectors.rate import (rate_detect, recording_extent,
                                     stream_trains)
from bugarach.score import score_stream
from bugarach.simulate import simulate_coordination

SEEDS = (1, 2, 3, 4)
DUR, N_ROI, BG = 2700.0, 33, 0.0052
GRID = (0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 12.0, 16.0)


def run(min_sep, n_ev, guard, knob):
    hit = det = plant = 0
    for s in SEEDS:
        sl, gt = simulate_coordination(
            seed=s, duration_sec=DUR, n_roi=N_ROI, bg_rate_hz=BG,
            n_per_level=(n_ev, n_ev, n_ev), min_sep_sec=min_sep,
            jitter_sec=0.36, participation=(0.30, 0.18, 0.10),
            n_distractors=0)
        ext = recording_extent(sl)
        trains = stream_trains(sl.streams["events"], ext)
        r = rate_detect(trains, ext, excess_threshold_hz=knob, rate_win=1.0,
                        context_win=60.0, grid_dt=0.1, guard_sec=guard)
        sc = score_stream(gt, r, tol_sec=1.5)
        hit += sc.n_hit
        det += sc.n_detected
        plant += sc.n_planted
    p = hit / det if det else float("nan")
    rc = hit / plant if plant else float("nan")
    return (2 * p * rc / (p + rc) if p + rc else 0.0), p, rc


def best(min_sep, n_ev, guard):
    rows = [(k, *run(min_sep, n_ev, guard, k)) for k in GRID]
    return max(rows, key=lambda x: x[1])


print(f"{N_ROI} ROI, {DUR:.0f}s, bg {BG} Hz, {len(SEEDS)} seeds, "
      f"context 60 s (reference spans +/-30 s)\n")
print(f"{'event spacing':>16s} {'n/level':>8s} | {'no guard':>18s} | "
      f"{'guard 10 s':>18s} | delta")
print(f"{'':>16s} {'':>8s} | {'knob':>5s} {'F1':>5s} {'rec':>5s} | "
      f"{'knob':>5s} {'F1':>5s} {'rec':>5s} |")
for min_sep, n_ev in [(120.0, 5), (60.0, 8), (30.0, 12), (20.0, 16), (14.0, 20)]:
    k0, f0, p0, r0 = best(min_sep, n_ev, 0.0)
    k1, f1, p1, r1 = best(min_sep, n_ev, 10.0)
    inside = "  <- inside the reference window" if min_sep < 30 else ""
    print(f"{min_sep:14.0f}s {n_ev:8d} | {k0:5.1f} {f0:5.3f} {r0:5.3f} | "
          f"{k1:5.1f} {f1:5.3f} {r1:5.3f} | {f1 - f0:+.3f}{inside}")
