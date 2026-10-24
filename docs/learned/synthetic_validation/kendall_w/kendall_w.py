"""No-order (null) mean of the order indicator F under the score sort: exact formula, Gaussian
form, large-E constant c(N, k), and checks against fresh simulation with order_limit.py.

See derivation.md. Usage:
    python kendall_w.py [path/to/synthetic_validation]   > kendall_w_output.txt
"""
import sys
import time

import numpy as np
from scipy.stats import norm

from pathlib import Path

# order_limit.py lives one folder up, in docs/learned/synthetic_validation/
SV = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parents[1])
sys.path.insert(0, SV)
import order_limit as ol  # noqa: E402

SIGMA = 0.2  # onset jitter; irrelevant under the null (only the within-event ranking matters)


# ---------------------------------------------------------------- predictions
def probs(N, k):
    p2 = k * (k - 1) / (N * (N - 1))          # a given pair both in an event
    p1 = k * (N - k) / (N * (N - 1))          # cell i in, cell j out
    return p2, p1


def gap_weights(k):
    """P(|r_i - r_j| = d) for two distinct cells of one event, d = 1..k-1."""
    d = np.arange(1, k)
    return d, 2 * (k - d) / (k * (k - 1))


def event_pmf(N, k):
    """pmf of one event's contribution to s_i - s_j, on the integer grid -L..L."""
    p2, p1 = probs(N, k)
    L = 2 * (k - 1)
    q = np.zeros(2 * L + 1)
    q[L] += 1 - p2 - 2 * p1
    d, w = gap_weights(k)
    q[L + 2 * d] += p2 * w / 2
    q[L - 2 * d] += p2 * w / 2
    for r in range(1, k + 1):                 # u = k + 1 - 2r, and -u, each with p1 / k
        q[L + k + 1 - 2 * r] += 2 * p1 / k
    return q, L


def F_exact(N, k, E):
    """E[F_score] = sum_d w_d [P(|S| < 2d) + P(|S| = 2d)/2], S = sum of E-1 i.i.d. event pmfs."""
    q, L = event_pmf(N, k)
    n = E - 1
    size = 2 * n * L + 1
    nf = 1 << int(np.ceil(np.log2(size)))
    S = np.clip(np.fft.irfft(np.fft.rfft(q, nf) ** n, nf)[:size], 0, None)
    off = n * L
    cdf = np.concatenate([[0.0], np.cumsum(S)])

    def P(a, b):
        a, b = max(a, -off), min(b, off)
        return cdf[b + off + 1] - cdf[a + off] if b >= a else 0.0

    d, w = gap_weights(k)
    return float(sum(wd * (P(-2 * dd + 1, 2 * dd - 1) + 0.5 * (P(2 * dd, 2 * dd) + P(-2 * dd, -2 * dd)))
                     for dd, wd in zip(d, w)))


def F_gauss(N, k, E):
    """Same with S ~ Normal(0, (E-1) sigma1^2), sigma1^2 = p2 * 2N(k+1)/3."""
    p2, _ = probs(N, k)
    sS = np.sqrt((E - 1) * p2 * 2 * N * (k + 1) / 3)
    d, w = gap_weights(k)
    return float(np.sum(w * (2 * norm.cdf(2 * d / sS) - 1)))


def c_score(N, k):
    """Large-E constant: E[F] sqrt(n_bar) -> sqrt(4(k+1) / (3 pi N))."""
    return np.sqrt(4 * (k + 1) / (3 * np.pi * N))


def c_union_bound(N, k):
    """Crude upper bound on the constant for ANY order (so for the search): union bound over N!."""
    from math import lgamma
    return np.sqrt(2 * lgamma(N + 1) * 2 * (2 * k + 5) / (9 * N * (N - 1)))


# ---------------------------------------------------------------- simulation
def sim(N, k, E, reps, rng):
    v = np.array([ol.indicators(ol.simulate(N, k, E, 1, 0.0, SIGMA, rng), N)[:2] for _ in range(reps)])
    return v.mean(0), v.std(0, ddof=1), v.std(0, ddof=1) / np.sqrt(reps)


def z(meas, se, pred):
    return (meas - pred) / se


if __name__ == "__main__":
    t0 = time.time()
    rng = np.random.default_rng(20261024)
    print("Null mean of F under the score sort: exact formula, Gaussian form, c(N,k) = sqrt(4(k+1)/(3 pi N))")
    print("Simulated with order_limit.simulate / order_limit.indicators (one template, spread 0 => no order).")
    print("SE = SD / sqrt(recordings). z = (simulated - exact) / SE.\n")

    # A. the six fields at 400 events
    print("A. Six fields, 400 events, 200 recordings each")
    print(f"{'N':>4}{'k':>4}{'n_bar':>7} | {'c pred':>7}{'c fit(json)':>12}{'c sim':>8}{'+-SE':>7} | "
          f"{'F exact':>8}{'F gauss':>8}{'F sim':>8}{'+-SE':>8}{'z':>6} | {'c search sim':>12}{'+-SE':>7}")
    old = {(15, 5): (0.408, 0.548), (33, 5): (0.259, 0.408), (33, 10): (0.374, 0.497),
           (33, 20): (0.507, 0.602), (100, 10): (0.216, 0.314), (100, 30): (0.373, 0.448)}
    search_rows = []
    for (N, k), (cfit, _) in old.items():
        E = 400
        nb = ol.nbar(N, k, E)
        m, sd, se = sim(N, k, E, 200, rng)
        fe, fg = F_exact(N, k, E), F_gauss(N, k, E)
        search_rows.append((N, k, m[0] * np.sqrt(nb), m[1] * np.sqrt(nb), se[1] * np.sqrt(nb)))
        print(f"{N:4d}{k:4d}{nb:7.2f} | {c_score(N, k):7.3f}{cfit:12.3f}{m[0] * np.sqrt(nb):8.3f}"
              f"{se[0] * np.sqrt(nb):7.3f} | {fe:8.4f}{fg:8.4f}{m[0]:8.4f}{se[0]:8.4f}{z(m[0], se[0], fe):6.1f}"
              f" | {m[1] * np.sqrt(nb):12.3f}{se[1] * np.sqrt(nb):7.3f}")

    # B. small runs
    print("\nB. Small runs, 33 cells, 1000 recordings each (score sort)")
    print(f"{'k':>4}{'E':>5}{'n_bar':>7} | {'old sim':>14} | {'F exact':>8}{'F gauss':>8}{'c/sqrt(nb)':>11}"
          f"{'F sim':>8}{'+-SE':>8}{'SD':>7}{'z':>6}")
    old_small = {(7, 10): "0.48 +- 0.06", (7, 25): "0.31 +- 0.045", (7, 60): "0.21 +- 0.03",
                 (7, 140): "0.14 +- 0.02", (13, 10): "0.34 +- 0.04", (13, 25): "0.22 +- 0.03",
                 (13, 60): "0.14 +- 0.02", (13, 140): "0.094 +- 0.012"}
    for (k, E), o in old_small.items():
        N = 33
        nb = ol.nbar(N, k, E)
        m, sd, se = sim(N, k, E, 1000, rng)
        fe = F_exact(N, k, E)
        print(f"{k:4d}{E:5d}{nb:7.2f} | {o:>14} | {fe:8.4f}{F_gauss(N, k, E):8.4f}{c_score(N, k) / np.sqrt(nb):11.4f}"
              f"{m[0]:8.4f}{se[0]:8.4f}{sd[0]:7.3f}{z(m[0], se[0], fe):6.1f}")

    # C. sweep in E at 33 cells, 10 per event
    print("\nC. 33 cells, 10 per event, sweep in E, 200 recordings: F sqrt(n_bar)")
    print(f"{'E':>5}{'n_bar':>7} | {'exact':>7}{'sim':>7}{'+-SE':>7}{'z':>6} | {'search sim':>10}{'+-SE':>7}")
    for E in (5, 10, 25, 50, 100, 200, 400, 800):
        N, k = 33, 10
        nb = ol.nbar(N, k, E)
        m, sd, se = sim(N, k, E, 200, rng)
        fe = F_exact(N, k, E)
        print(f"{E:5d}{nb:7.2f} | {fe * np.sqrt(nb):7.3f}{m[0] * np.sqrt(nb):7.3f}{se[0] * np.sqrt(nb):7.3f}"
              f"{z(m[0], se[0], fe):6.1f} | {m[1] * np.sqrt(nb):10.3f}{se[1] * np.sqrt(nb):7.3f}")
    print(f"   large-E constant c(33,10) = {c_score(33, 10):.4f}")

    # D. k = N (Kendall's W case) and k = 2 (pairwise contests)
    print("\nD1. Every cell in every event (k = N, Kendall's W setting), 1000 recordings: F sqrt(m), m = E")
    print(f"{'N':>4}{'E':>5} | {'exact':>7}{'sim':>7}{'+-SE':>7}{'z':>6} | {'(2/pi)asin(1/sqrt m)sqrt m':>27}"
          f" | {'mean Spearman to consensus':>26}{'sqrt(W)':>8}")
    for N in (10, 33):
        for E in (2, 4, 10, 25, 100):
            vals, sp, sw = [], [], []
            for _ in range(1000):
                ev = ol.simulate(N, N, E, 1, 0.0, SIGMA, rng)
                vals.append(ol.indicators(ev, N)[0])
                # identity check: mean Spearman between each event's ranking and the rank sums = sqrt(W)
                R = np.zeros((E, N))
                for e, (cells, t) in enumerate(ev):
                    R[e, cells] = np.argsort(np.argsort(t)) + 1
                Rs = R.sum(0)
                sp.append(np.mean([np.corrcoef(R[e], Rs)[0, 1] for e in range(E)]))
                W = 12 * np.sum((Rs - E * (N + 1) / 2) ** 2) / (E ** 2 * (N ** 3 - N))
                sw.append(np.sqrt(W))
            vals = np.array(vals)
            fe = F_exact(N, N, E)
            se = vals.std(ddof=1) / np.sqrt(len(vals))
            print(f"{N:4d}{E:5d} | {fe * np.sqrt(E):7.3f}{vals.mean() * np.sqrt(E):7.3f}{se * np.sqrt(E):7.3f}"
                  f"{z(vals.mean(), se, fe):6.1f} | {2 / np.pi * np.arcsin(1 / np.sqrt(E)) * np.sqrt(E):27.3f}"
                  f" | {np.mean(sp):26.4f}{np.mean(sw):8.4f}")
        print(f"   N = {N}: large-m constant sqrt(4(N+1)/(3 pi N)) = {c_score(N, N):.4f}")

    print("\nD2. Two cells per event (k = 2, independent pairwise contests), 1000 recordings")
    print(f"{'N':>4}{'E':>5}{'n_bar':>7} | {'exact':>8}{'gauss':>8}{'sim':>8}{'+-SE':>8}{'z':>6}")
    for N, E in ((10, 30), (10, 300), (33, 300), (33, 3000)):
        m, sd, se = sim(N, 2, E, 1000, rng)
        fe = F_exact(N, 2, E)
        print(f"{N:4d}{E:5d}{ol.nbar(N, 2, E):7.2f} | {fe:8.4f}{F_gauss(N, 2, E):8.4f}{m[0]:8.4f}{se[0]:8.4f}"
              f"{z(m[0], se[0], fe):6.1f}")

    # E. local search: fitted, plus bounds
    print("\nE. Local search (stretch): constant c_search = F_search sqrt(n_bar), 400 events")
    extra = [(15, 10), (60, 10), (60, 30), (200, 20), (200, 60)]
    for N, k in extra:
        reps = 100 if N >= 200 else 200
        nb = ol.nbar(N, k, 400)
        m, sd, se = sim(N, k, 400, reps, rng)
        search_rows.append((N, k, m[0] * np.sqrt(nb), m[1] * np.sqrt(nb), se[1] * np.sqrt(nb)))
    rows = np.array(search_rows)
    # fit c_search^2 - c_score^2 = a * N^b  (score part from the exact large-E constant)
    Ns, ks, csc, cse = rows[:, 0], rows[:, 1], rows[:, 2], rows[:, 3]
    gap = cse ** 2 - c_score(Ns, ks) ** 2
    b, loga = np.polyfit(np.log(Ns), np.log(gap), 1)
    a = np.exp(loga)
    print(f"   fit: c_search^2 = 4(k+1)/(3 pi N) + a N^b, a = {a:.3f}, b = {b:.3f}")
    print(f"{'N':>4}{'k':>4} | {'c score pred':>12}{'c score sim':>12} | {'c search sim':>12}{'+-SE':>7}"
          f"{'fit':>7}{'ratio':>7} | {'union bound':>11}")
    for (N, k, cs, cl, sel) in search_rows:
        fit = np.sqrt(c_score(N, k) ** 2 + a * N ** b)
        print(f"{int(N):4d}{int(k):4d} | {c_score(N, k):12.3f}{cs:12.3f} | {cl:12.3f}{sel:7.3f}{fit:7.3f}"
              f"{cl / cs:7.2f} | {c_union_bound(int(N), int(k)):11.3f}")
    print(f"\nrun time {time.time() - t0:.0f} s")
