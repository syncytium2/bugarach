"""Own re-implementation (not Elephant code) of the ordering logic of
CAD (pairwise argmax-lag of the cross-correlogram) and ASSET (first-appearance
order of neurons along a diagonal cluster, i.e. sort by binned latency in one
occurrence), compared with a net-lead (Borda) ranking over shared events.

Model: E events; each of N cells joins an event with prob q, fires once at
event_time + latency_i + N(0, jitter). latency_i is a fixed template spread
uniformly over [0, spread]. Times are binned at 1 frame.
"""
import numpy as np
from scipy.stats import kendalltau

rng = np.random.default_rng(1)


def simulate(N=33, E=60, q=0.6, spread=4.0, jitter=1.0, T_gap=50):
    lat = np.sort(rng.uniform(0, spread, N))
    perm = rng.permutation(N)           # hide true order
    lat = lat[perm]
    part = rng.random((E, N)) < q
    t = np.full((E, N), np.nan)
    onsets = np.arange(E) * T_gap + 10
    tt = onsets[:, None] + lat[None, :] + rng.normal(0, jitter, (E, N))
    t[part] = tt[part]
    return lat, t, onsets


def net_lead_rank(t):
    E, N = t.shape
    score = np.zeros(N)
    for i in range(N):
        for j in range(N):
            if i == j:
                continue
            both = ~np.isnan(t[:, i]) & ~np.isnan(t[:, j])
            d = np.sign(t[both, j] - t[both, i])  # +1 when i leads j
            score[i] += d.sum()
    return score  # larger = earlier


def cad_like_rank(t, max_lag=6):
    """CAD pair step: best_lag = argmax over lags in [-max_lag, max_lag] of the
    binned cross-correlogram; aggregate by summing sign(best_lag)."""
    E, N = t.shape
    b = np.floor(t)
    score = np.zeros(N)
    for i in range(N):
        for j in range(i + 1, N):
            both = ~np.isnan(b[:, i]) & ~np.isnan(b[:, j])
            d = (b[both, j] - b[both, i]).astype(int)
            d = d[np.abs(d) <= max_lag]
            if d.size == 0:
                continue
            counts = np.bincount(d + max_lag, minlength=2 * max_lag + 1)
            best = np.argmax(counts) - max_lag  # first max -> ties go negative
            score[i] += np.sign(best)
            score[j] -= np.sign(best)
    return score


def cad_anchor_rank(t, anchor):
    """CAD assembly output: lags of every member relative to the first
    agglomerated unit, each = pairwise argmax lag to that anchor."""
    b = np.floor(t)
    N = t.shape[1]
    lags = np.zeros(N)
    for j in range(N):
        both = ~np.isnan(b[:, anchor]) & ~np.isnan(b[:, j])
        d = (b[both, j] - b[both, anchor]).astype(int)
        vals, cnt = np.unique(d, return_counts=True)
        lags[j] = vals[np.argmax(cnt)] if vals.size else 0
    return -lags  # larger = earlier


def asset_like_rank(t, e1, e2):
    """ASSET SSE ordering for one pair of occurrences: neurons spiking in both
    occurrences in matching relative bins (+-1 diagonal width), ordered by bin
    in occurrence e1 (row-major np.where order, first appearance)."""
    b = np.floor(t)
    N = t.shape[1]
    rel1 = b[e1] - np.nanmin(b[e1])
    rel2 = b[e2] - np.nanmin(b[e2])
    ok = ~np.isnan(rel1) & ~np.isnan(rel2) & (np.abs(rel1 - rel2) <= 1)
    idx = np.where(ok)[0]
    return idx, -rel1[idx]


def asset_mean_rank(t):
    """ASSET ordering averaged over all occurrence pairs = mean binned latency."""
    b = np.floor(t)
    rel = b - np.nanmin(b, axis=1, keepdims=True)
    return -np.nanmean(rel, axis=0)


def tau(a, b):
    return kendalltau(a, b).statistic


print("spread jitter | tau(net-lead,true) tau(CADsign,true) tau(CADanchor,true)"
      " tau(ASSET1pair,true) tau(ASSETmean,true) | tau(CADsign,netlead)"
      " tau(ASSETmean,netlead)")
for spread, jitter in [(4, 0.5), (4, 1), (4, 2), (2, 2), (8, 1)]:
    rows = []
    for rep in range(20):
        lat, t, _ = simulate(spread=spread, jitter=jitter)
        truth = -lat
        nl = net_lead_rank(t)
        cs = cad_like_rank(t)
        ca = cad_anchor_rank(t, anchor=int(np.argmin(lat)) )
        idx, a1 = asset_like_rank(t, 0, 1)
        am = asset_mean_rank(t)
        rows.append([tau(nl, truth), tau(cs, truth), tau(ca, truth),
                     tau(a1, truth[idx]), tau(am, truth),
                     tau(cs, nl), tau(am, nl)])
    m = np.nanmean(rows, axis=0)
    print(f"{spread:>4} {jitter:>5}   | " + "  ".join(f"{x:5.2f}" for x in m))

# Identity check: net lead of a pair == (CCG mass at positive lags) - (mass at
# negative lags) when each cell fires at most once per event.
lat, t, _ = simulate()
i, j = 0, 1
both = ~np.isnan(t[:, i]) & ~np.isnan(t[:, j])
d = t[both, j] - t[both, i]
print("pair net lead:", int(np.sign(d).sum()),
      " CCG(+)-CCG(-):", int((d > 0).sum() - (d < 0).sum()))
