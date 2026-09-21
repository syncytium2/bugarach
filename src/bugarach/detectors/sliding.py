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


def catch_from_positions(positions: list[np.ndarray], L: float, w: float) -> np.ndarray:
    """P(caught) for each non-empty ROI, given its events' positions on a circle of length
    ``L``. The slow, obvious form: the reference for :class:`EventIndex`, and what the
    guard uses, where the circle is assembled from two pieces of the context."""
    if L <= 0:
        return np.empty(0)
    out = []
    for x in positions:
        if x.size == 0:
            continue
        if w >= L:
            out.append(1.0)
            continue
        x = np.sort(np.mod(x, L))
        gaps = np.diff(np.r_[x, x[0] + L])
        out.append(np.minimum(gaps, w).sum() / L)
    return np.asarray(out, dtype=float)


def catch_probabilities(ev: list[np.ndarray], lo: float, hi: float, w: float) -> np.ndarray:
    """Per ROI with events in ``[lo, hi)``: P(caught by a width-``w`` window) under a
    uniform circular shift of its in-context events around a circle of length ``hi - lo``.
    One-off form; a detector evaluating many contexts builds an :class:`EventIndex`."""
    return EventIndex(ev).catch_probabilities(lo, hi, w)


class EventIndex:
    """Every ROI's sorted events in one flat array, so a context query is a handful of
    vectorised calls rather than a loop over ROIs.

    Events are keyed ``roi * scale + (t - base)``; ``scale`` exceeds any query offset, so
    one ``searchsorted`` over the key finds every ROI's slice of a context at once.
    """

    def __init__(self, ev: list[np.ndarray]):
        lens = np.array([v.size for v in ev], dtype=int)
        self.n = len(ev)
        self.t = np.concatenate(ev).astype(float) if lens.sum() else np.empty(0)
        roi = np.repeat(np.arange(self.n), lens)
        self.base = float(self.t.min()) if self.t.size else 0.0
        span = float(self.t.max() - self.base) if self.t.size else 0.0
        self.margin = span + 1e5
        self.scale = 4.0 * self.margin
        self.key = roi * self.scale + (self.t - self.base)
        self.rows = np.arange(self.n) * self.scale

    def _offset(self, t: float) -> float:
        return float(np.clip(t - self.base, -self.margin, self.margin * 2))

    def catch_probabilities(self, lo: float, hi: float, w: float) -> np.ndarray:
        L = hi - lo
        if L <= 0 or self.t.size == 0:
            return np.empty(0)
        a = np.searchsorted(self.key, self.rows + self._offset(lo), side="left")
        b = np.searchsorted(self.key, self.rows + self._offset(hi), side="left")
        cnt = b - a
        nz = cnt > 0
        if not nz.any():
            return np.empty(0)
        a, cnt = a[nz], cnt[nz]
        if w >= L:
            return np.ones(a.size)
        offs = np.cumsum(cnt) - cnt
        idx = np.repeat(a - offs, cnt) + np.arange(cnt.sum())
        x = self.t[idx] - lo
        nxt = np.empty_like(x)
        nxt[:-1] = x[1:]
        last = offs + cnt - 1
        nxt[last] = x[offs] + L                   # each ROI wraps to its own first event
        return np.add.reduceat(np.minimum(nxt - x, w), offs) / L


def poisson_binomial(p: np.ndarray) -> np.ndarray:
    """P(count = k), k = 0..len(p), for independent Bernoulli(p_i).

    From the characteristic function at the n+1 roots of unity and one FFT (Hong 2013,
    the DFT-CF method): one vectorised product instead of a loop over ROIs. Checked
    against :func:`_poisson_binomial_loop` in the tests."""
    n = p.size
    if n == 0:
        return np.ones(1)
    z = np.exp(2j * np.pi * np.arange(n + 1) / (n + 1))
    phi = np.prod(1 - p[:, None] + p[:, None] * z[None, :], axis=0)
    pmf = np.real(np.fft.fft(phi)) / (n + 1)
    return np.clip(pmf, 0.0, None)


def _poisson_binomial_loop(p: np.ndarray) -> np.ndarray:
    """The recursion, one ROI at a time — the reference :func:`poisson_binomial` must match."""
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
