"""Aim 2 preview: the count detector's recall and false alarms, predicted vs simulated.

count_detect: fixed 2 s bins, distinct-ROI count >= K, merge gaps <= 3 s.
Predicted, stationary Poisson background b on N ROIs, q = 1 - exp(-2b):
  false alarms per hour  FA(K) = 1800 * pi_K (1 - pi_K)^2,  pi_K = P(Binom(N, q) >= K)
  recall(K) = P( max_bins [ n_bin + Binom(N - k, q) ] >= K ),  n_bin = participants per bin from a
              participants-only Monte Carlo of one event (bins independent given the split).
Simulated: simulate_coordination, 33 ROIs, 45 min, 45 events; hit = an episode within 2 s of the
planted time; false alarm = an episode with no planted event within 5 s.
"""
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
N, T, BIN = 33, 2700.0, 2.0


def pred(k, sigma, b, K, n_mc=40000, seed=0):
    rng = np.random.default_rng(seed)
    q = 1 - np.exp(-BIN * b)
    x = np.round((sigma * rng.standard_normal((n_mc, k)) + rng.uniform(0, BIN, (n_mc, 1))) / 0.1) * 0.1
    bi = np.floor(x / BIN).astype(int)
    bi -= bi.min(1, keepdims=True)
    cnt = np.zeros((n_mc, bi.max() + 1), int)
    np.add.at(cnt, (np.repeat(np.arange(n_mc), k), bi.ravel()), 1)
    # P(no bin reaches K) = prod_bins P(Binom(N-k, q) < K - n_bin)
    p_miss = np.prod(stats.binom.cdf(K - 1 - cnt, N - k, q), axis=1)
    recall = 1 - p_miss.mean()
    pi = stats.binom.sf(K - 1, N, q)
    return recall, 1800 * pi * (1 - pi) ** 2


def sim(args):
    k, sigma, b, K, seed = args
    from bugarach.detectors.count import count_detect
    from bugarach.simulate import simulate_coordination
    s, gt = simulate_coordination(duration_sec=T, n_roi=N, bg_rate_hz=b, participation=(k / N,),
                                  n_per_level=(45,), jitter_sec=sigma, min_sep_sec=20.0, seed=300 + seed)
    st = next(iter(s.streams.values()))
    d = count_detect([np.asarray(t) for t in st.t50rise], (0.0, T), bin_sec=BIN, min_rois=K, merge_gap_sec=3.0)
    ev = np.array([e.time for e in gt.events])
    mid = d.onset_sec + d.width_sec / 2
    hit = np.array([np.any(np.abs(mid - t) <= 2.0 + d.width_sec / 2) for t in ev])
    fa = np.array([not np.any(np.abs(ev - m) <= 5.0) for m in mid])
    return hit.mean(), fa.sum() / ((T - 45 * 10) / 3600)


if __name__ == "__main__":
    cases = [(k, s, b, K) for k in (5, 10) for s in (0.2, 1.0) for b in (0.01, 0.05) for K in (4, 6, 9)]
    with ProcessPoolExecutor(20) as ex:
        res = list(ex.map(sim, [(*c, sd) for c in cases for sd in range(6)]))
    print(f"{'k':>3} {'sig':>4} {'b':>5} {'K':>2} | {'recall pr':>9} {'sim':>5} | {'FA/h pr':>8} {'sim':>7}")
    for i, c in enumerate(cases):
        r = np.array(res[6 * i:6 * i + 6])
        rp, fp = pred(*c)
        print(f"{c[0]:3d} {c[1]:4.1f} {c[2]:5.2f} {c[3]:2d} | {rp:9.3f} {r[:, 0].mean():5.3f} | {fp:8.2f} {r[:, 1].mean():7.2f}")
