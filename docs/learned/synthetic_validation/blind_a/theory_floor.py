"""ADR-0008 chance floor, analytic: up-crossing (flux) rate of the sliding-window distinct-ROI count.
u_K = (N-K+1) b * Binom.pmf(K-1; N, 1-exp(-b W))   per s;   floor = max(3, min{K: 3600 u_K <= 1}).
Checked against bugarach.event_floor.window_floor on Poisson-background recordings."""
import numpy as np
from scipy.stats import binom
from bugarach.event_floor import window_floor, null_curve
N, T, W, DT = 33, 2700.0, 2.0, 0.1
def u(K, b, n=N):
    q = 1 - np.exp(-b * W)
    return (n - K + 1) * b * binom.pmf(K - 1, n, q)
def floor_analytic(b, n=N):
    ok = [K for K in range(1, n + 2) if all(3600 * u(j, b, n) <= 1 for j in range(K, n + 1))]
    return ok[0]
for b in (0.005, 0.01, 0.02, 0.05, 0.1, 0.2):
    rs = np.random.RandomState(int(b * 1000))
    L = int(T / DT)
    tr = [np.unique(np.floor(rs.random_sample(rs.poisson(b * T)) * L).astype(int)) for _ in range(N)]
    runs, frames, hours, *_ = null_curve(tr, L, DT, key=("t", b), draws=100)
    per_h = runs.sum(0) / (100 * hours)
    fl = window_floor(tr, L, DT, key=("t", b), draws=100)
    Ks = range(2, 12)
    print(f"b={b}: chance floor MC {fl.chance_floor}, analytic {floor_analytic(b)} | calls/h MC vs analytic at K=2..11:")
    print("   ", " ".join(f"{per_h[K]:.3g}/{3600*u(K,b):.3g}" for K in Ks))
