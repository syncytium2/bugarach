import sys, numpy as np
sys.path.insert(0, "../tools")
import measure_coordination_rates as mcr
from bugarach.simulate import simulate_coordination
N, T, L = 33, 2700.0, 27000
R=[]; VM=[]
for seed in range(60):
    s, gt = simulate_coordination(duration_sec=T, n_roi=N, bg_rate_hz=0.05, participation=(0.15,),
        n_per_level=(1,), jitter_sec=0.05, min_sep_sec=20.0, grid_sec=0.1, seed=1000+seed)
    st = next(iter(s.streams.values()))
    tr = [np.minimum(mcr._frames(np.asarray(t), 0.0, T), L-1) for t in st.t50rise]
    R.append(mcr.population_cumulants(tr, L, 10))
    X = np.bincount(np.concatenate(tr)//10, minlength=2700)
    VM.append(X.var()/X.mean())
    if seed==0: print([len(t) for t in tr]); print(np.sort(np.diff(np.concatenate([t for t in tr[:1]])))[:10])
R=np.array(R); print(R.mean(0), R.std(0)/np.sqrt(60), R.std(0), np.mean(VM))
