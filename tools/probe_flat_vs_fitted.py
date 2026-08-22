"""What changes if the bench moves from a flat field to the fitted one?

Runs every detector at its SHIPPED operating point on both backgrounds, same
seeds, same recording otherwise. The question is not which background is right —
that is measured already — but how much the numbers move if it changes, which is
what makes it a decision rather than a correction.
"""
import json
import os

import numpy as np

from bugarach.bench import (BENCH_RECORDING, DETECTORS, MEASURED_RATE_SHAPE,
                            OPERATING_POINTS, make_recording, run_detector)
from bugarach.score import score_stream

SEEDS = (1, 2, 3)
HOT = BENCH_RECORDING["hot_window"]


def score(name, shape, seeds=SEEDS):
    hit = det = plant = hot = 0
    for s in seeds:
        kw = {} if shape is None else {"bg_rate_shape": shape}
        sl, gt = make_recording("baseline_quiet", s, **kw)
        r = run_detector(name, sl, rng_seed=s)
        sc = score_stream(gt, r, tol_sec=1.5)
        hit += sc.n_hit
        det += sc.n_detected
        plant += sc.n_planted
        on = getattr(r, "onset_sec", None)
        if on is None:
            on = getattr(r, "locs", np.empty(0))
        on = np.asarray(on, dtype=float)
        hot += int(np.sum((on >= HOT[0]) & (on <= HOT[1])))
    p = hit / det if det else float("nan")
    rc = hit / plant if plant else float("nan")
    f1 = 2 * p * rc / (p + rc) if p + rc else 0.0
    return dict(f1=f1, precision=p, recall=rc, probe=hot / len(seeds))


out = {"shape": MEASURED_RATE_SHAPE, "seeds": list(SEEDS), "flat": {}, "fitted": {}}
print(f"{'detector':9s} {'FLAT F1':>8s} {'FIT F1':>8s} {'delta':>7s} "
      f"{'FLAT probe':>11s} {'FIT probe':>10s}")
for name in DETECTORS:
    a = score(name, None)
    b = score(name, MEASURED_RATE_SHAPE)
    out["flat"][name] = a
    out["fitted"][name] = b
    print(f"{name:9s} {a['f1']:8.3f} {b['f1']:8.3f} {b['f1']-a['f1']:+7.3f} "
          f"{a['probe']:11.1f} {b['probe']:10.1f}")

# the per-ROI rate distributions the two backgrounds actually produce
rng = np.random.RandomState(0)
mean = 0.0052
flat = np.full(20000, mean)
fitted = rng.gamma(MEASURED_RATE_SHAPE, mean / MEASURED_RATE_SHAPE, 20000)
win = BENCH_RECORDING["duration_sec"]
out["rates"] = {
    "flat": {"median_mhz": float(np.median(flat) * 1000),
             "max_mhz": float(flat.max() * 1000),
             "silent_frac": float(np.mean(rng.poisson(flat * win) == 0))},
    "fitted": {"median_mhz": float(np.median(fitted) * 1000),
               "max_mhz": float(fitted.max() * 1000),
               "silent_frac": float(np.mean(rng.poisson(fitted * win) == 0))},
    "fitted_hist": np.histogram(fitted * 1000, bins=60, range=(0, 60))[0].tolist(),
    "edges_mhz": np.histogram(fitted * 1000, bins=60, range=(0, 60))[1].tolist(),
}
print("\nper-ROI rate, over a bench-length window:")
for k, v in out["rates"].items():
    if isinstance(v, dict) and "median_mhz" in v:
        print(f"  {k:7s} median {v['median_mhz']:6.1f} mHz  max {v['max_mhz']:7.1f}"
              f"  silent {100*v['silent_frac']:4.1f}%")

with open(os.environ.get("BUGARACH_PROBE_OUT", "flat_vs_fitted.json"), "w") as f:

    json.dump(out, f, indent=1)
print("\nwrote", os.environ.get("BUGARACH_PROBE_OUT", "flat_vs_fitted.json"))
