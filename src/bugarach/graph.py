"""Pairwise coupling and graph modularity, on this repo's own footing.

**Why this exists.** The assembly answer has two halves. The membership half
(`bugarach.assembly`) asks whether *who participates* departs from uniform, and it
fires on almost every testable recording — a positive. The half that makes the
answer a *negative* asks whether the coupled cells form **modules**, and until now
that half was computed by `eval_modularity_null` in the interface2 connectivity
project. That project has no maintainer, and its pipeline does not run out of the
box: its dead-ROI roster path resolves into a quarantined export. A published
negative should not rest on a pipeline nobody can execute.

**This is a PORT, not a clean-room, and the distinction is recorded because it
changes what the validation is worth.** The MATLAB driver was read while
investigating the quarantined roster, so an independent reimplementation was no
longer available for the *procedure* — the window, the surrogate scheme, the
best-of-N restarts. What was **not** read is `if2_sttc.m`: the coefficient below is
written from Cutts & Eglen (2014) as published, so that part is independent, and
`tests/test_graph.py` checks it against 155 recordings of reference output.

**What the null is, and why it is this one.** Louvain finds *some* partition in any
graph, and it scores sparser, weaker graphs higher — so a raw modularity is
uninterpretable. Each recording is therefore compared against jitter surrogates of
**itself**: the same cells, the same event counts, the same region, only the timing
moved. Node count, sparsity and the weak-edge structure are held fixed, so they
cancel, and what is left is whether the *timing* carries module structure.

References
----------
Cutts C.S. & Eglen S.J. (2014) Detecting pairwise correlations in spike trains: an
objective comparison of methods and application to the study of retinal waves.
*J Neurosci* 34(43):14288–14303 — the spike time tiling coefficient.

Blondel V.D. et al. (2008) Fast unfolding of communities in large networks.
*J Stat Mech* P10008 — Louvain.

Newman M.E.J. (2004) Analysis of weighted networks. *Phys Rev E* 70:056131 — the
weighted modularity this maximizes.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .detectors._shared import matlab_prctile

__all__ = ["sttc", "sttc_matrix", "modularity", "louvain", "ModularityResult",
           "jitter_trains", "modularity_vs_null"]


# ---- the coefficient -------------------------------------------------------

def _tile_fraction(train: np.ndarray, dt: float, t0: float, t1: float) -> float:
    """Fraction of ``[t0, t1]`` lying within ``dt`` of any spike — the T of the paper.

    Tiles are ``[s - dt, s + dt]`` around each spike, **unioned** (overlapping tiles
    are not double counted) and clipped to the window. Forgetting either the union
    or the clip inflates T, which biases every coefficient that uses it toward 0.
    """
    total = t1 - t0
    if train.size == 0 or total <= 0:
        return 0.0
    lo = np.clip(train - dt, t0, t1)
    hi = np.clip(train + dt, t0, t1)
    order = np.argsort(lo)
    lo, hi = lo[order], hi[order]
    covered = 0.0
    cur_lo, cur_hi = lo[0], hi[0]
    for a, b in zip(lo[1:], hi[1:]):
        if a > cur_hi:                       # disjoint: bank the run
            covered += cur_hi - cur_lo
            cur_lo, cur_hi = a, b
        else:                                # overlapping: extend
            cur_hi = max(cur_hi, b)
    covered += cur_hi - cur_lo
    return float(covered / total)


def _proportion_near(a: np.ndarray, b: np.ndarray, dt: float) -> float:
    """Fraction of spikes in ``a`` within ``dt`` of at least one spike in ``b`` — P.

    Uses ``searchsorted`` on a sorted ``b`` rather than a pairwise distance matrix,
    so a recording with thousands of events per cell stays linear.
    """
    if a.size == 0 or b.size == 0:
        return float("nan")
    idx = np.searchsorted(b, a)
    left = np.where(idx > 0, np.abs(a - b[np.clip(idx - 1, 0, b.size - 1)]), np.inf)
    right = np.where(idx < b.size, np.abs(a - b[np.clip(idx, 0, b.size - 1)]), np.inf)
    return float(np.mean(np.minimum(left, right) <= dt))


def sttc(a, b, dt: float, t0: float, t1: float) -> float:
    """Spike time tiling coefficient between two trains, on ``[t0, t1]``.

    Cutts & Eglen's measure, chosen by the connectivity work over correlation
    because it does not inflate with firing rate. Returns NaN when either train is
    empty in the window — **undefined, not zero**: a cell that never fired has no
    coupling to report, and calling it zero would drag a mean toward zero for a
    reason that is not about coupling.
    """
    a = np.sort(np.asarray(a, dtype=float))
    b = np.sort(np.asarray(b, dtype=float))
    a = a[(a >= t0) & (a < t1)]
    b = b[(b >= t0) & (b < t1)]
    if a.size == 0 or b.size == 0:
        return float("nan")

    ta = _tile_fraction(a, dt, t0, t1)
    tb = _tile_fraction(b, dt, t0, t1)
    pa = _proportion_near(a, b, dt)
    pb = _proportion_near(b, a, dt)

    # Each half is undefined when its denominator vanishes — that happens when the
    # tiles already cover the whole window, where the measure has nothing to say.
    da, db = 1.0 - pa * tb, 1.0 - pb * ta
    ha = (pa - tb) / da if abs(da) > 1e-12 else float("nan")
    hb = (pb - ta) / db if abs(db) > 1e-12 else float("nan")
    if not np.isfinite(ha) and not np.isfinite(hb):
        return float("nan")
    if not np.isfinite(ha):
        return float(hb)
    if not np.isfinite(hb):
        return float(ha)
    return float(0.5 * (ha + hb))


def sttc_matrix(trains, dt: float, t0: float, t1: float):
    """Symmetric all-pairs STTC, and the mean over pairs.

    The mean is taken over the pairs that are **defined**, matching the convention
    the connectivity work settled on: an empty cell contributes no pair rather than
    a zero.
    """
    n = len(trains)
    S = np.full((n, n), np.nan)
    vals = []
    for i in range(n):
        S[i, i] = 1.0
        for j in range(i + 1, n):
            v = sttc(trains[i], trains[j], dt, t0, t1)
            S[i, j] = S[j, i] = v
            vals.append(v)
    vals = np.asarray(vals, dtype=float)
    mean = float(np.nanmean(vals)) if np.any(np.isfinite(vals)) else float("nan")
    return S, mean


# ---- modularity ------------------------------------------------------------

def modularity(W: np.ndarray, labels: np.ndarray, gamma: float = 1.0) -> float:
    """Newman's weighted modularity of a partition.

    ``Q = 1/2m * sum_ij (W_ij - gamma * k_i k_j / 2m) * delta(c_i, c_j)``
    """
    W = np.asarray(W, dtype=float)
    k = W.sum(axis=1)
    two_m = k.sum()
    if two_m <= 0:
        return float("nan")
    same = labels[:, None] == labels[None, :]
    return float((np.sum(W[same]) - gamma * np.sum(np.outer(k, k)[same]) / two_m) / two_m)


def _one_louvain_pass(W: np.ndarray, gamma: float, rng) -> np.ndarray:
    """Louvain: local moving to convergence, then aggregate, then repeat.

    Node order is randomized each sweep — the algorithm is order-dependent, and
    fixing the order would make the "best of N restarts" below N copies of one run.
    """
    n0 = W.shape[0]
    labels = np.arange(n0)
    Wc = W.copy()
    mapping = np.arange(n0)

    while True:
        n = Wc.shape[0]
        k = Wc.sum(axis=1)
        two_m = k.sum()
        if two_m <= 0:
            break
        comm = np.arange(n)
        tot = k.copy()                    # summed degree per community
        improved_any = False

        for _sweep in range(100):
            improved = False
            for i in rng.permutation(n):
                ci = comm[i]
                ki = k[i]
                tot[ci] -= ki
                # weight from i into each community
                w_to = np.zeros(n)
                np.add.at(w_to, comm, Wc[i])
                w_to[ci] -= Wc[i, i]
                gain = w_to - gamma * ki * tot / two_m
                best = int(np.argmax(gain))
                if gain[best] <= gain[ci] + 1e-12:
                    best = ci
                tot[best] += ki
                comm[i] = best
                if best != ci:
                    improved = improved_any = True
            if not improved:
                break

        uniq, comm = np.unique(comm, return_inverse=True)
        labels = comm[mapping]
        if not improved_any or uniq.size == n:
            break
        # aggregate
        m = uniq.size
        Agg = np.zeros((m, m))
        for a in range(n):
            np.add.at(Agg[comm[a]], comm, Wc[a])
        Wc = Agg
        mapping = labels
    return labels


def louvain(W, gamma: float = 1.0, n_restarts: int = 5, seed: int = 7):
    """Best-of-N Louvain. Returns ``(labels, Q)``.

    **Best-of-N, and the caller must use the same N for observed and null.**
    Louvain is stochastic, so a single observed run against single null runs
    compares noise to noise; and taking the best of N is an upward-biased estimator
    of the achievable Q, so an observed best-of-5 against a null best-of-1 is rigged
    in favour of finding structure. `modularity_vs_null` holds them equal.
    """
    W = np.asarray(W, dtype=float)
    W = np.where(np.isfinite(W), W, 0.0)
    np.fill_diagonal(W, 0.0)
    if W.shape[0] < 2 or not np.any(W > 0):
        return np.zeros(W.shape[0], dtype=int), float("nan")
    rng = np.random.RandomState(seed)
    best_lab, best_q = None, -np.inf
    for _ in range(max(1, n_restarts)):
        lab = _one_louvain_pass(W, gamma, rng)
        q = modularity(W, lab, gamma)
        if np.isfinite(q) and q > best_q:
            best_lab, best_q = lab, q
    if best_lab is None:
        return np.zeros(W.shape[0], dtype=int), float("nan")
    return best_lab, float(best_q)


# ---- the null --------------------------------------------------------------

def jitter_trains(trains, jit: float, t0: float, t1: float, rng):
    """Each event displaced uniformly in ``+/- jit``, wrapped inside the window.

    Preserves **each cell's event count** and the window, so a surrogate graph has
    the same node count, the same sparsity and the same weak edges as the observed
    one. Only the timing differs — which is what makes the comparison a test of
    timing structure rather than of graph size.
    """
    L = t1 - t0
    out = []
    for t in trains:
        t = np.asarray(t, dtype=float)
        if t.size == 0:
            out.append(t)
            continue
        out.append(t0 + np.mod(t + (rng.random_sample(t.size) * 2 - 1) * jit - t0, L))
    return out


@dataclass(frozen=True)
class ModularityResult:
    """One recording's answer to "are the coupled cells a module?"."""

    n_active: int
    mean_sttc: float
    q_obs: float
    q_null_mu: float
    q_null_hi: float
    z: float
    defined: bool
    """False when the graph was too sparse to score. Every field is NaN and the
    caller reports an **exclusion**, never a negative — counting a recording nobody
    could test as one that was tested and found nothing is how the reference
    pipeline understated its own rates."""

    n_surrogates: int = 0

    @property
    def above_null(self) -> bool:
        """Observed modularity beyond the surrogate percentile.

        ``False`` when undefined, and callers must check ``defined`` first — this
        property alone cannot distinguish "tested, not modular" from "not tested".
        """
        return bool(self.defined and np.isfinite(self.q_obs)
                    and self.q_obs > self.q_null_hi)


def modularity_vs_null(trains, *, dt: float = 2.0, t0: float, t1: float,
                       n_surrogates: int = 200, n_restarts: int = 5,
                       jitter: float = 20.0, pctl: float = 95.0,
                       seed: int = 7, min_active: int = 3) -> ModularityResult:
    """Is this recording's modularity above what its own timing-scrambled copies give?

    Cells with no events in the window are dropped first: they contribute no edges,
    and leaving them in would pad the node count differently between observed and
    surrogate graphs.
    """
    rng = np.random.RandomState(seed)
    keep = [np.asarray(t, dtype=float) for t in trains]
    keep = [t[(t >= t0) & (t < t1)] for t in keep]
    active = [t for t in keep if t.size > 0]
    n_active = len(active)
    nan = float("nan")
    if n_active < min_active:
        return ModularityResult(n_active, nan, nan, nan, nan, nan, False, 0)

    S, mean_s = sttc_matrix(active, dt, t0, t1)
    W = np.where(np.isfinite(S), S, 0.0)
    W = np.maximum(W, 0.0)          # Louvain needs non-negative weights
    np.fill_diagonal(W, 0.0)
    _, q_obs = louvain(W, n_restarts=n_restarts, seed=int(rng.randint(1 << 30)))
    if not np.isfinite(q_obs):
        return ModularityResult(n_active, mean_s, nan, nan, nan, nan, False, 0)

    qs = np.full(n_surrogates, nan)
    for s in range(n_surrogates):
        js = jitter_trains(active, jitter, t0, t1, rng)
        Sj, _ = sttc_matrix(js, dt, t0, t1)
        Wj = np.maximum(np.where(np.isfinite(Sj), Sj, 0.0), 0.0)
        np.fill_diagonal(Wj, 0.0)
        _, qs[s] = louvain(Wj, n_restarts=n_restarts, seed=int(rng.randint(1 << 30)))

    ok = qs[np.isfinite(qs)]
    if ok.size < 2:
        return ModularityResult(n_active, mean_s, q_obs, nan, nan, nan, False, int(ok.size))
    mu, sd = float(np.mean(ok)), float(np.std(ok))
    # MATLAB `prctile`, not numpy's — they disagree, and the reference this port is
    # validated against is MATLAB's. Caught by sapper SAP001 before it ever ran.
    hi = float(matlab_prctile(ok, pctl))
    z = (q_obs - mu) / sd if sd > 1e-12 else nan
    return ModularityResult(n_active, mean_s, float(q_obs), mu, hi, float(z),
                            True, int(ok.size))
