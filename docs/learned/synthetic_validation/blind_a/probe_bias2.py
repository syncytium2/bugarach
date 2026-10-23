import sys, numpy as np
sys.path.insert(0, "../tools")
import measure_coordination_rates as mcr
N, T, L = 33, 2700.0, 27000
def mk(bg, k, m, jit, rs):
    tr = [list(rs.random_sample(rs.poisson(bg*T))*T) for _ in range(N)]
    times = 10 + np.sort(rs.choice(np.arange(130), m, replace=False))*20.0 + rs.random_sample(m)*5
    for t in times:
        for r in rs.choice(N, k, replace=False): tr[r].append(t + jit*rs.randn())
    return [np.minimum(mcr._frames(np.asarray(t), 0, T), L-1) for t in tr]
for bg in (0.0, 0.01, 0.05):
    R = []
    for s in range(40):
        rs = np.random.RandomState(s)
        tr = mk(bg, 5, 45, 0.05, rs)
        R.append(mcr.population_cumulants(tr, L, 10))
    R = np.array(R); print(bg, R.mean(0).round(4), (R.std(0)/np.sqrt(len(R))).round(4))
# pure background
R=[]
for s in range(200):
    rs = np.random.RandomState(s); tr = mk(0.05, 5, 0, 0.05, rs); R.append(mcr.population_cumulants(tr, L, 10))
R=np.array(R); print("bg only", R.mean(0).round(4), (R.std(0)/np.sqrt(len(R))).round(4), "sd", R.std(0).round(4))
