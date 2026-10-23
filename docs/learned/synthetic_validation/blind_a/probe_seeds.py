import sys, numpy as np
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, "../tools")
N, T, L = 33, 2700.0, 27000
def one(args):
    bg, part, m, jit, seed = args
    import measure_coordination_rates as mcr
    from bugarach.simulate import simulate_coordination
    s, gt = simulate_coordination(duration_sec=T, n_roi=N, bg_rate_hz=bg, participation=(part,),
        n_per_level=(m,), jitter_sec=jit, min_sep_sec=20.0, grid_sec=0.1, seed=1000+seed)
    st = next(iter(s.streams.values()))
    tr = [np.minimum(mcr._frames(np.asarray(t), 0.0, T), L-1) for t in st.t50rise]
    ev = {(r, o) for e in gt.events for r, o in zip(e.rois, e.onsets)}
    bgtr = [np.minimum(mcr._frames(np.asarray([x for x in t if (i, x) not in ev]), 0.0, T), L-1) for i, t in enumerate(st.t50rise)]
    rng = np.random.RandomState(7+seed)
    m_ = mcr.measure(tr, L, rng)
    c = m_["cum"]["1.0"]
    sol = mcr.solve(c["f2"], c["f3"], N, 1.0, "fixed")
    b = mcr.population_cumulants(bgtr, L, 10)
    return sol["k"], c["f2"], c["f3"], b[0], b[1]
if __name__ == "__main__":
    for seeds in (range(5), range(5, 45)):
        with ProcessPoolExecutor(20) as ex:
            R = np.array(list(ex.map(one, [(0.05, 0.15, 45, 0.05, s) for s in seeds])))
        print(len(R), "k/5 median %.3f mean %.3f" % (np.nanmedian(R[:,0])/5, np.nanmean(R[:,0])/5), "f2 %.3f f3 %.3f  bg-only f2 %.4f f3 %.4f" % tuple(R[:,1:].mean(0)))
        if len(R)==5: print(R.round(3))
