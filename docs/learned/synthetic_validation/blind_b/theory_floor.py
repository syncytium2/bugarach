"""ADR-0008 chance floor: closed-form prediction vs event_floor.window_floor on simulated recordings.

Null = independent Poisson ROIs (what the per-ROI rigid shift makes of homogeneous Poisson trains).
Sliding window w = 2 s, a call = a maximal run of window positions with >= K co-active ROIs.
Upcrossing (Rice-type) rate per second:
    nu_K = sum_i b_i * P(C_{-i} = K - 1),  C_{-i} = co-active ROIs among the others, Poisson-binomial
         ~ (N - K + 1) b P(Binom(N, q) = K - 1) / (1 - q) ... for equal rates, q = 1 - exp(-b w)
chance floor = min K with 3600 nu_K <= 1.  Event floor = max(3, chance floor).
"""
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
W = 2.0


def nu(K, rates, w=W):
    """Calls per second at K, heterogeneous rates (Poisson-binomial of the other ROIs)."""
    rates = np.asarray(rates, float)
    q = 1 - np.exp(-rates * w)
    tot = 0.0
    for i in range(len(rates)):
        qq = np.delete(q, i)
        # Poisson-binomial pmf by convolution
        pmf = np.array([1.0])
        for x in qq:
            pmf = np.convolve(pmf, [1 - x, x])
        if K - 1 < len(pmf):
            # ROI i must be inactive in the window and then have an event: rate b_i * P(i inactive) * P(others = K-1)
            tot += rates[i] * np.exp(-rates[i] * w) * pmf[K - 1]
    return tot


def floor_pred(rates, budget=1.0):
    # search upward from the mean co-active count: below it nu_K is not monotone (a saturated field is
    # rarely empty, so "runs at K=1" are rare too) -- see the note in the report
    k0 = int(np.sum(1 - np.exp(-np.asarray(rates) * W))) + 1
    for K in range(k0, len(rates) + 2):
        if 3600 * nu(K, rates) <= budget:
            return K, [3600 * nu(k, rates) for k in range(max(1, K - 2), K + 1)]
    return len(rates) + 1, []


def sim_floor(args):
    N, b, shape, seed, draws, extra = args
    from bugarach.event_floor import window_floor
    from bugarach.simulate import simulate_coordination
    kw = dict(participation=(0.3,), n_per_level=(45,), jitter_sec=0.2) if extra else dict(participation=(), n_per_level=())
    s, gt = simulate_coordination(duration_sec=2700.0, n_roi=N, bg_rate_hz=b, bg_rate_shape=shape,
                                  min_sep_sec=20.0, grid_sec=0.1, seed=seed, **kw)
    st = next(iter(s.streams.values()))
    L = 27000
    trains = [np.minimum(np.round(np.asarray(t) / 0.1).astype(int), L - 1) for t in st.t50rise]
    rates = np.array([len(t) for t in trains]) / 2700.0
    f = window_floor(trains, L, 0.1, key=("theory", N, b, seed), draws=draws)
    return f.chance_floor, f.first_half, f.second_half, rates


if __name__ == "__main__":
    cases = [(33, 0.01, None, False), (33, 0.02, None, False), (33, 0.05, None, False), (33, 0.1, None, False),
             (100, 0.02, None, False), (100, 0.05, None, False), (15, 0.05, None, False),
             (33, 0.05, 1.0, False), (33, 0.05, None, True), (33, 0.01, None, True)]
    jobs = [(N, b, sh, 100 + s, 200, ex) for (N, b, sh, ex) in cases for s in range(3)]
    with ProcessPoolExecutor(20) as exr:
        res = list(exr.map(sim_floor, jobs))
    print(f"{'N':>4} {'b':>5} {'shape':>5} {'events':>6} | pred floor (from realised per-ROI rates)  [calls/h at K-2..K] | window_floor chance floor (halves), 3 seeds x 200 draws")
    for i, c in enumerate(cases):
        rr = res[3 * i:3 * i + 3]
        preds = [floor_pred(r[3]) for r in rr]
        print(f"{c[0]:4d} {c[1]:5.2f} {str(c[2]):>5} {str(c[3]):>6} | " + "; ".join(
            f"{p[0]} [{', '.join(f'{x:.3g}' for x in p[1])}]" for p in preds) + " | " + "; ".join(f"{r[0]} ({r[1]},{r[2]})" for r in rr))
