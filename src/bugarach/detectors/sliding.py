"""A sliding window and an exact circular-shift null, shared by LoCo and CoactDetect.

**Why.** Both detectors counted distinct active ROIs in fixed bins laid from the start
of the recording, and both drew their surrogate nulls from one random stream consumed
bin by bin (anchor by anchor for LoCo). Shift a recording by a fraction of a bin and
the counts move with the bin edges; and any change in which bins are candidates moves
every later draw, so calls change far from the shift. Measured on real baselines,
2026-09-07: LoCo kept 64% of its calls under a sub-second shift, CoactDetect 70%, and
CoactDetect's loss grew with the size of the shift — the random stream, not the bins
(``docs/todo/2026-09-07-detector-calls-move-with-the-grid.md``). The fix here removes both.

**The count.** ``S(t)`` is the number of distinct ROIs with an event in the trailing
window ``(t - w, t]``. It changes only where an event enters (``t = e``) or leaves
(``t = e + w``), so it is exactly a step function over *pieces* between those times,
found with one sweep — no grid.

**The null, computed rather than sampled.** Both nulls shift each ROI's events by an
independent uniform amount around a circle of the context's length ``L`` and ask
whether the ROI lands in a window of width ``w``. For one ROI that probability does not
depend on where the window is, and it has a closed form: put a point at each event,
and the ROI is caught for exactly the part of the circle lying within ``w`` after one of
them — ``sum(min(w, gap to the next point)) / L``. ROIs shift independently, so the null
count is a Poisson-binomial with those probabilities. Its mean and variance
(CoactDetect's z-test) and its quantiles (LoCo's percentile bar) are exact. The Monte
Carlo estimated precisely this distribution, with sampling noise and an order-dependent
random stream; there is no random number here at all.
"""
from __future__ import annotations

import numpy as np


def pieces(ev: list[np.ndarray], w: float, t_lo: float, t_hi: float):
    """``(starts, ends, S)``: the step function of distinct ROIs in ``(t - w, t]``.

    Only pieces inside ``[t_lo, t_hi]`` with positive length are returned.
    """
    times, deltas = [], []
    for v in ev:
        if v.size == 0:
            continue
        s = np.asarray(v, dtype=float)
        e = s + w
        # merge this ROI's [s, s + w) intervals so it counts once while any is open
        brk = np.flatnonzero(s[1:] > e[:-1])
        m_start = np.concatenate(([s[0]], s[brk + 1]))
        m_end = np.concatenate((e[brk], [e[-1]]))
        times += [m_start, m_end]
        deltas += [np.ones(m_start.size), -np.ones(m_end.size)]
    if not times:
        return np.empty(0), np.empty(0), np.empty(0)
    t = np.concatenate(times)
    d = np.concatenate(deltas)
    order = np.lexsort((d, t))          # at equal times, ends (-1) before starts (+1)
    t, d = t[order], d[order]
    level = np.cumsum(d)
    last = np.r_[t[1:] != t[:-1], True]  # the level after all changes at a time
    ut, lv = t[last], level[last]
    starts, ends = ut[:-1], ut[1:]
    S = lv[:-1]
    starts = np.maximum(starts, t_lo)
    ends = np.minimum(ends, t_hi)
    keep = ends > starts
    return starts[keep], ends[keep], S[keep]


def catch_probabilities(ev: list[np.ndarray], lo: float, hi: float, w: float) -> np.ndarray:
    """Per ROI with events in ``[lo, hi]``: P(caught by a width-``w`` window) under a
    uniform circular shift of its in-context events around a circle of length ``hi - lo``."""
    L = hi - lo
    if L <= 0:
        return np.empty(0)
    if w >= L:
        return np.array([1.0 for v in ev if np.any((v >= lo) & (v <= hi))])
    out = []
    for v in ev:
        a = np.searchsorted(v, lo, side="left")
        b = np.searchsorted(v, hi, side="right")
        if b <= a:
            continue
        x = np.sort(np.mod(v[a:b] - lo, L))
        gaps = np.diff(np.r_[x, x[0] + L])
        out.append(np.minimum(gaps, w).sum() / L)
    return np.asarray(out, dtype=float)


def poisson_binomial(p: np.ndarray) -> np.ndarray:
    """P(count = k), k = 0..len(p), for independent Bernoulli(p_i)."""
    dist = np.zeros(p.size + 1)
    dist[0] = 1.0
    for i, pi in enumerate(p, start=1):
        dist[1:i + 1] = dist[1:i + 1] * (1 - pi) + dist[0:i] * pi
        dist[0] *= (1 - pi)
    return dist


def quantile(p: np.ndarray, pctile: float) -> float:
    """Smallest count k with P(count <= k) >= pctile / 100 — LoCo's bar, exactly."""
    if p.size == 0:
        return 0.0
    cdf = np.cumsum(poisson_binomial(p))
    return float(np.searchsorted(cdf, pctile / 100.0 - 1e-12, side="left"))


def moments(p: np.ndarray) -> tuple[float, float]:
    """Mean and standard deviation of the null count — CoactDetect's z-test, exactly."""
    return float(p.sum()), float(np.sqrt((p * (1 - p)).sum()))


def span_of(ev: list[np.ndarray], lo: float, hi: float):
    """First and last event in ``[lo, hi)`` across ROIs, and how many ROIs took part."""
    tfirst, tlast, n = np.inf, -np.inf, 0
    for v in ev:
        a = np.searchsorted(v, lo, side="left")
        b = np.searchsorted(v, hi, side="left")
        if b > a:
            n += 1
            tfirst = min(tfirst, v[a])
            tlast = max(tlast, v[b - 1])
    return tfirst, tlast, n


def merge_runs(starts: np.ndarray, ends: np.ndarray, gap: float) -> list[tuple[int, int]]:
    """Index runs of firing pieces whose gaps are at most ``gap`` seconds."""
    runs = []
    for i in range(starts.size):
        if runs and starts[i] - ends[runs[-1][1]] <= gap:
            runs[-1] = (runs[-1][0], i)
        else:
            runs.append((i, i))
    return runs
