import sys, json
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "src"))
import measure_coordination_rates as mcr
from bugarach.simulate import simulate_coordination
rec = json.loads((ROOT / "docs/learned/synthetic_validation/aim1_one_source.json").read_text())
for seed in range(5):
    s, gt = simulate_coordination(duration_sec=2700.0, n_roi=33, bg_rate_hz=0.05, participation=(0.15,),
        n_per_level=(45,), jitter_sec=0.05, min_sep_sec=20.0, grid_sec=0.1, seed=1000 + seed)
    st = next(iter(s.streams.values()))
    L = 27000
    trains = [np.minimum(mcr._frames(np.asarray(t), 0.0, 2700.0), L - 1) for t in st.t50rise]
    raw = mcr.population_cumulants(trains, L, 10)
    rng = np.random.RandomState(7 + seed)
    m = mcr.measure(trains, L, rng)
    row = [r for r in rec["rows"] if r["seed"] == seed and r["true"]["jitter"] == 0.05 and r["true"]["k"] == 5 and r["true"]["n_events"] == 45 and r["true"]["bg_rate"] == 0.05][0]
    c = m["cum"]["1.0"]
    print(seed, "raw", np.round(raw, 3), "excess", round(c["f2"], 3), round(c["f3"], 3), "solve", mcr.solve(c["f2"], c["f3"], 33, 1.0)["k"], "json k", row["coord_rates"]["1.0"]["k"], "ev", len(gt.events))
