"""Does the guard, or a multiplicative bar, actually help rate+context?

Scores the shipped detector against each new mechanism on the bench recording,
at the same knob sweep, using bench.pick_operating_point to choose. Reports F1
and the promiscuity-probe firings, because the probe is what the argument
predicts should move.
"""
import numpy as np

from bugarach.bench import (BENCH_RECORDING, REGIMES, DegenerateSweep,
                            EdgeOfRange, OPERATING_POINTS, evaluate,
                            make_recording, pick_operating_point, run_detector)
from bugarach.detectors.rate import recording_extent, rate_detect, stream_trains
from bugarach.score import score_stream

REGIME, SEEDS = "baseline_quiet", (1, 2, 3)
GRID = OPERATING_POINTS["rate"].grid
ALPHA_GRID = (5.0, 10.0, 15.0, 20.0, 30.0, 40.0, 55.0, 70.0, 90.0, 120.0)


def score(mode, knob, guard, alpha=None):
    """Pooled counts over the seeds, mirroring bench.evaluate's pooling."""
    hit = det = plant = hot = 0
    hot_lo, hot_hi = BENCH_RECORDING["hot_window"]
    for s in SEEDS:
        sl, gt = make_recording(REGIME, s)
        ext = recording_extent(sl)
        trains = stream_trains(sl.streams["events"], ext)
        kw = dict(context_win=60.0, rate_win=1.0, grid_dt=0.1, guard_sec=guard)
        if mode == "multiplicative":
            kw.update(threshold_mode="multiplicative", threshold_alpha=alpha)
        else:
            kw.update(excess_threshold_hz=knob)
        r = rate_detect(trains, ext, **kw)
        sc = score_stream(gt, r, tol_sec=1.5)
        hit += sc.n_hit
        det += sc.n_detected
        plant += sc.n_planted
        hot += int(np.sum((r.locs >= hot_lo) & (r.locs <= hot_hi)))
    prec = hit / det if det else float("nan")
    rec = hit / plant if plant else float("nan")
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return f1, prec, rec, hot / len(SEEDS)


def best(mode, guard, grid):
    rows = []
    for v in grid:
        f1, p, r, hot = score(mode, v, guard, alpha=v)
        rows.append((v, f1, p, r, hot))
    top = max(rows, key=lambda x: x[1])
    return top, rows


print(f"regime {REGIME}, seeds {SEEDS}, probe window "
      f"{BENCH_RECORDING['hot_window']}\n")
print(f"{'configuration':44s} {'knob':>6s} {'F1':>6s} {'prec':>6s} "
      f"{'rec':>6s} {'probe':>6s}")
for label, mode, guard, grid in [
    ("additive, no guard  (SHIPPED)", "additive", 0.0, GRID),
    ("additive, guard 5 s", "additive", 5.0, GRID),
    ("additive, guard 15 s", "additive", 15.0, GRID),
    ("multiplicative, no guard", "multiplicative", 0.0, ALPHA_GRID),
    ("multiplicative, guard 5 s", "multiplicative", 5.0, ALPHA_GRID),
    ("multiplicative, guard 15 s", "multiplicative", 15.0, ALPHA_GRID),
]:
    (v, f1, p, r, hot), _ = best(mode, guard, grid)
    print(f"{label:44s} {v:6.2f} {f1:6.3f} {p:6.3f} {r:6.3f} {hot:6.1f}")
