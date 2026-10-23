import sys, numpy as np
sys.path.insert(0, "../tools")
import measure_coordination_rates as mcr
from bugarach.simulate import simulate_coordination
from theory_cr import predict
N, T = 33, 2700.0
L = int(round(T / mcr.DT))
def run(bg, part, m, jit, seed, w=1.0):
    s, gt = simulate_coordination(duration_sec=T, n_roi=N, bg_rate_hz=bg, participation=(part,),
        n_per_level=(m,), jitter_sec=jit, min_sep_sec=20.0, grid_sec=0.1, seed=1000+seed)
    st = next(iter(s.streams.values()))
    tr = [np.minimum(mcr._frames(np.asarray(t), 0.0, T), L-1) for t in st.t50rise]
    # event-only trains
    ev = [[] for _ in range(N)]
    for e in gt.events:
        for r, o in zip(e.rois, e.onsets): ev[r].append(o)
    tre = [np.minimum(mcr._frames(np.asarray(t), 0.0, T), L-1) for t in ev]
    wf = int(round(w/mcr.DT)); rng = np.random.RandomState(7+seed)
    a = mcr.population_cumulants(tr, L, wf)
    b = mcr.excess_cumulants(tr, L, wf, 20, rng)
    c = mcr.population_cumulants(tre, L, wf)
    return a, b, c
for bg in (0.01, 0.05):
    R = np.array([np.ravel(run(bg, 0.15, 45, 0.05, s)) for s in range(10)])
    p = predict(0.05, 0.15, 45, bg, 1.0)
    print(bg, "raw f2,f3 | excess f2,f3 | events-only f2,f3 (mean over 10 seeds)")
    print(np.round(R.mean(0), 4), " sd:", np.round(R.std(0), 4))
    print("pred f2,f3", round(p["f2"],4), round(p["f3"],4))
