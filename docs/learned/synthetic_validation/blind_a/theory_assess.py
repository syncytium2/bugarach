"""Semi-analytic prediction of assess_coactivity's cluster statistics (clusters/min, part_n_obs,
jit_obs) on Aim 1a, vs the record.

Model.  Bins of 1 s; per bin, the number of background-active cells is Binomial(N, q), q = 1-e^{-b}.
Bins are independent under Poisson background, so chance clusters (runs of >=K bins merged across
<= 1 empty bin) START at rate  r_K = p_K (1-p_K)^2  per second, p_K = P(Bin(N,q) >= K)  [exact].
A planted event adds a neighbourhood of +-R s; E[#clusters in it] = G(K; k, sigma, b) from a
single-event Monte Carlo of that neighbourhood only (the bugarach clustering code itself).
  clusters/min = 60 [ r_K (T - m 2R) + m G ] / T
Cluster statistics are the mixture of chance clusters (weight r_K (T - 2Rm)) and event-neighbourhood
clusters (weight m G); medians of the mixture.
"""
from __future__ import annotations

import itertools
import sys

import numpy as np
from scipy.stats import binom

from theory_common import N, T, kpart, load

from bugarach.assess import _clusters, _coact_count  # noqa: E402

JITS, PARTS, NEVS, BGS, KS = (0.05, 0.2, 0.5, 1.0), (0.15, 0.3, 0.6), (15, 45), (0.01, 0.05), (3, 4, 6)


def chance_rate(b, K):
    q = 1 - np.exp(-b)
    p = binom.sf(K - 1, N, q)
    return p * (1 - p) ** 2


def q01(x):
    return np.round(np.floor(np.asarray(x) / 0.1 + 0.5) * 0.1, 10)


def local(b, K, k=0, sigma=0.0, R=None, n=3000, seed=0):
    """Clusters (sd, part, span) inside a +-R neighbourhood: with one event at its centre (k>0)
    or background only (k=0). Window 2R+10 s, clusters kept if their centre lies within +-R."""
    rs = np.random.RandomState(seed)
    R = R if R is not None else 3 * sigma + 4.0
    W = 2 * R + 10.0
    nb = int(np.ceil(W))
    sds, parts, cnt = [], [], 0
    for _ in range(n):
        tr = [rs.random_sample(rs.poisson(b * W)) * W for _ in range(N)]
        c0 = W / 2 + rs.random_sample()
        if k:
            for r in rs.choice(N, k, replace=False):
                tr[r] = np.append(tr[r], c0 + sigma * rs.randn())
        tr = [np.sort(q01(np.clip(t, 0, W - 1e-9))) for t in tr]
        counts = _coact_count(tr, W, 1.0, nb)
        sd, pt, _, _, mem = _clusters(tr, counts, K, 1.0, nb, 2, 1.5, with_members=True)
        # recover each cluster's centre by recomputing groups (same rule as _clusters)
        over = np.flatnonzero(counts >= K)
        groups, cur = [], []
        for f in over:
            if cur and f - cur[-1] > 2:
                groups.append(cur); cur = []
            cur.append(f)
        if cur:
            groups.append(cur)
        cents = []
        for g in groups:
            tc = float(np.mean((np.asarray(g) + 0.5)))
            near = sum(1 for t in tr if np.any(np.abs(t - tc) <= 1.5))
            if near >= K:
                cents.append(tc)
        for tc, s_, p_ in zip(cents, sd, pt):
            if abs(tc - W / 2) <= R:
                cnt += 1; sds.append(s_); parts.append(p_)
    return cnt / n, np.array(sds), np.array(parts), R


def wmedian(vals, weights):
    v = np.concatenate(vals); w = np.concatenate([np.full(len(x), wt / max(len(x), 1))
                                                  for x, wt in zip(vals, weights)])
    if v.size == 0 or w.sum() == 0:
        return np.nan
    o = np.argsort(v); c = np.cumsum(w[o]) / w.sum()
    return float(v[o][np.searchsorted(c, 0.5)])


def main():
    rows = load()
    null = {}
    for b, K in itertools.product(BGS, KS):
        g, sd, pt, R = local(b, K, 0, 0.0, R=20.0, n=1500, seed=11)
        null[(b, K)] = (sd, pt)
        print(f"chance clusters b={b} K={K}: analytic {60*chance_rate(b, K):.3f}/min, "
              f"local MC {60*g/40.0:.3f}/min, median part {np.median(pt) if pt.size else np.nan}, "
              f"median sd {np.median(sd) if sd.size else np.nan:.3f}")
    res = []
    for sg, f, m, b, K in itertools.product(JITS, PARTS, NEVS, BGS, KS):
        k = kpart(f)
        G, sd, pt, R = local(b, K, k, sg, n=800, seed=hash((sg, f, b, K)) % 2**31)
        rc = chance_rate(b, K)
        nchance, nev = rc * (T - 2 * R * m), m * G
        pm = 60 * (nchance + nev) / T
        part = wmedian([null[(b, K)][1], pt], [nchance, nev])
        jit = wmedian([null[(b, K)][0], sd], [nchance, nev])
        rr = [r for r in rows if (r["true"]["jitter"], r["true"]["part_frac"], r["true"]["n_events"],
                                  r["true"]["bg_rate"]) == (sg, f, m, b)]
        A = [r["assess"][str(K)] for r in rr]
        res.append(dict(sg=sg, f=f, m=m, b=b, K=K, k=k, G=G, pm=pm, part=part, jit=jit,
                        pm_o=np.median([a["per_min"] for a in A]),
                        part_o=np.nanmedian([a["part"] for a in A]),
                        jit_o=np.nanmedian([a["jit"] for a in A]), true_pm=60 * m / T))
    np.save(__import__("pathlib").Path(__file__).with_suffix(".npy"), res, allow_pickle=True)
    print(" b    K  sg   f    m | G     | /min pred obs   | part pred obs | jit pred obs")
    for o in res:
        print(f"{o['b']:.2f} {o['K']} {o['sg']:4.2f} {o['f']:.2f} {o['m']:2d} | {o['G']:.2f} | "
              f"{o['pm']:6.3f} {o['pm_o']:6.3f} | {o['part']:4.1f} {o['part_o']:4.1f} | "
              f"{o['jit']:.2f} {o['jit_o']:.2f}")


if __name__ == "__main__":
    main()
