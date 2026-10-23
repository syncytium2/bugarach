import numpy as np
from bugarach.simulate import simulate_coordination
def bgset(jit, part, m, seed=1000, bg=0.05):
    s, gt = simulate_coordination(duration_sec=2700., n_roi=33, bg_rate_hz=bg, participation=(part,),
        n_per_level=(m,), jitter_sec=jit, min_sep_sec=20.0, grid_sec=0.1, seed=seed)
    st = next(iter(s.streams.values()))
    ev = {(r, o) for e in gt.events for r, o in zip(e.rois, e.onsets)}
    return [tuple(x for x in t if (i, x) not in ev) for i, t in enumerate(st.t50rise)]
a = bgset(0.05, 0.15, 15); b = bgset(1.0, 0.6, 45)
print("identical background trains in", sum(x == y for x, y in zip(a, b)), "of 33 cells")
