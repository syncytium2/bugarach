"""Run sliding CoactDetect and LoCo twice on the same recordings and check the calls are identical."""
import json

import numpy as np

from bugarach.bench import OPERATING_POINTS, run_detector
from bugarach.simulate import simulate_coordination

spec = json.load(open("docs/learned/generator_spec.json"))["generator"]
for det in ("coact", "loco"):
    assert OPERATING_POINTS[det].params["window_mode"] == "sliding"
    for seed in (1000, 1013, 1023):
        s, _ = simulate_coordination(seed=seed, **spec)
        runs = [run_detector(det, s, rng_seed=r) for r in (20260706, 1)]
        a, b = runs
        fields = [f for f in ("onset_sec", "width_sec", "extent_sec") if getattr(a, f, None) is not None]
        same = all(np.array_equal(getattr(a, f), getattr(b, f)) for f in fields)
        print(det, seed, "calls", len(a.onset_sec), "identical across rng_seed" if same else "DIFFERENT", fields)
