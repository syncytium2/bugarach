"""stack: the sliding distinct-ROI count at several widths, each against a local exact null,
the least likely width winning (Tony's "stacking blocks", 2026-10-07).

Stack the onsets inside a sliding window: the tower's **height** is the number of distinct ROIs,
its **stability** how tightly their onsets sit. Stability needs no statistic of its own, because
a tight tower is a high count in a *narrow* window. So at each width in ``widths_sec``:

* the count is the step function of distinct ROIs with an onset in ``(t - w, t]``, exactly, with
  no grid (:func:`_pieces`);
* each piece's count is turned into a tail probability under the **context-window circular
  shift** null that LoCo and CoactDetect use: every ROI's onsets circularly shifted, independently,
  within a context of ``context_sec`` around the window, so the null follows the local rate
  (Tony, 2026-10-07: *"operate similar to loco and coact, using a context window circular shift
  rather than a single value based on the entire region"*). The probability is exact: each ROI's
  chance of landing in the window has a closed form, and the count is their Poisson-binomial
  (:func:`_catch_probabilities`, :func:`_poisson_binomial`);
* ``null_context_mode="maxlt"`` (the default, as in LoCo) takes the trailing and the leading
  half-context separately and keeps the **larger** of the two tail probabilities, so a rate edge
  on one side cannot make a window look unlikely. ``"symmetric"`` uses one context centred on the
  window;
* a piece is called when its count reaches ``min_rois`` and its tail probability is at most
  ``alpha / len(widths_sec)``: ``alpha`` is shared across the widths (Bonferroni), so looking at
  several widths does not buy extra calls.

Called pieces from every width are joined across gaps of at most ``merge_gap_sec``. Each call
reports its first and last participating onset, its smallest tail probability, and the width
that produced it (:attr:`StackDetection.stability_sec`; the narrowest wins a tie).

**One width is LoCo in a sliding window.** With ``widths_sec=(w,)`` and
``alpha = 1 - threshold_pctile / 100`` this calls exactly where LoCo's sliding path does at bin
width ``w``, the same context, null mode, guard, ``min_rois`` and merge gap, on a recording with no
region windows (``tests/test_stack.py``). That case is the ablation: the difference between the
two is what the narrower widths add.

**Self-contained on purpose** (Tony, 2026-10-07: stack should not depend on code that might
change under it). This module imports numpy and the standard library and nothing else from
``bugarach``; the exact null, the sweep and the result types are its own.
``tests/test_stack.py`` fails if an import from the package appears here. The equivalence with
LoCo is tested from outside, so a change to LoCo shows up as a failing test, never as a silent
change to stack.

⚠ **Nothing here is tuned.** The defaults are LoCo's: a 120 s context, ``maxlt``,
``alpha`` 1e-3 (LoCo's 99.9th percentile). The widths are 0.25, 0.5, 1 and 2 s, and the merge gap
is the 3 s the first version used. A run that wants the floor passes the window's ADR-0008 floor
as ``min_rois``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

NULL_CONTEXT_MODES = ("maxlt", "symmetric")


@dataclass
class StackSignal:
    """The plot-ready trace, with the field names of the detector output contract's
    ``emit_signal`` (``docs/detector_output_spec.md``): the count at the widest width (``y``)
    and its local tail probability at each piece (``ref``; 1 where the count is under
    ``min_rois`` and nothing was computed)."""

    t: np.ndarray
    y: np.ndarray
    ref: np.ndarray
    threshold: None
    hilite: np.ndarray
    name: str = "stack: distinct ROIs / widest window"
    kind: str = "local_coincidence"


@dataclass
class StackDetection:
    """Calls as parallel arrays of length ``n_events``, under the field names every other
    detector's result uses. ``strength`` is ``-log10`` of the call's smallest tail probability."""

    onset_sec: np.ndarray
    width_sec: np.ndarray
    strength: np.ndarray
    nrois: np.ndarray
    width_kind: str
    ctr: np.ndarray
    obs: np.ndarray
    threshold: int
    signal: StackSignal
    ext: tuple[float, float]
    opts: dict
    stability_sec: np.ndarray = field(default_factory=lambda: np.empty(0))
    """Per call, the window width whose count was least likely under its local null."""
    p_value: np.ndarray = field(default_factory=lambda: np.empty(0))
    """Per call, that smallest tail probability."""
    alpha_per_width: float = 0.0
    """The tail probability a piece must reach at any one width: ``alpha / len(widths)``."""

    @property
    def n_events(self) -> int:
        return int(self.onset_sec.size)


# ------------------------------------------------------------------------- the exact pieces

def _clip_sorted(trains, lo: float, hi: float) -> list[np.ndarray]:
    """Per ROI, its finite onsets within ``[lo, hi]``, sorted."""
    out = []
    for v in trains:
        v = np.asarray(v, dtype=float).ravel()
        v = v[np.isfinite(v)]
        out.append(np.sort(v[(v >= lo) & (v <= hi)]))
    return out


def _pieces(ev: list[np.ndarray], w: float, t_lo: float, t_hi: float):
    """``(starts, ends, S)``: the step function of distinct ROIs with an onset in ``(t - w, t]``,
    pieces of positive length inside ``[t_lo, t_hi]`` only."""
    times, deltas = [], []
    for s in ev:
        if s.size == 0:
            continue
        e = s + w
        brk = np.flatnonzero(s[1:] > e[:-1])     # one ROI counts once while any window is open
        m_start = np.concatenate(([s[0]], s[brk + 1]))
        m_end = np.concatenate((e[brk], [e[-1]]))
        times += [m_start, m_end]
        deltas += [np.ones(m_start.size), -np.ones(m_end.size)]
    if not times:
        return np.empty(0), np.empty(0), np.empty(0)
    t = np.concatenate(times)
    d = np.concatenate(deltas)
    order = np.lexsort((d, t))                     # at equal times, ends before starts
    t, d = t[order], d[order]
    level = np.cumsum(d)
    last = np.r_[t[1:] != t[:-1], True]
    ut, lv = t[last], level[last]
    starts, ends, S = ut[:-1], ut[1:], lv[:-1]
    starts = np.maximum(starts, t_lo)
    ends = np.minimum(ends, t_hi)
    keep = ends > starts
    return starts[keep], ends[keep], S[keep]


class _Index:
    """Every ROI's onsets in one flat array keyed by ROI, so the onsets of all ROIs inside a
    context are found with two ``searchsorted`` calls."""

    def __init__(self, ev: list[np.ndarray]):
        lens = np.array([v.size for v in ev], dtype=int)
        n = len(ev)
        self.t = np.concatenate(ev).astype(float) if lens.sum() else np.empty(0)
        roi = np.repeat(np.arange(n), lens)
        self.base = float(self.t.min()) if self.t.size else 0.0
        span = float(self.t.max() - self.base) if self.t.size else 0.0
        self.margin = span + 1e5
        self.scale = 4.0 * self.margin
        self.key = roi * self.scale + (self.t - self.base)
        self.rows = np.arange(n) * self.scale

    def _offset(self, t: float) -> float:
        return float(np.clip(t - self.base, -self.margin, self.margin * 2))

    def catch_probabilities(self, lo: float, hi: float, w: float) -> np.ndarray:
        """Per ROI with onsets in ``[lo, hi)``: the chance a width-``w`` window catches it when
        its onsets are shifted uniformly around a circle of length ``hi - lo``. Put a point at
        each onset; the ROI is caught for the part of the circle within ``w`` after one of them,
        ``sum(min(w, gap to the next point)) / L``."""
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
        nxt[offs + cnt - 1] = x[offs] + L          # each ROI wraps to its own first onset
        return np.add.reduceat(np.minimum(nxt - x, w), offs) / L


def _poisson_binomial(p: np.ndarray) -> np.ndarray:
    """P(count = k), k = 0 .. len(p), for independent Bernoulli(p_i), by the recursion one ROI
    at a time. Slower than the FFT form and right in relative terms, which a tail compared
    between widths needs."""
    dist = np.zeros(p.size + 1)
    dist[0] = 1.0
    for i, pi in enumerate(p, start=1):
        dist[1:i + 1] = dist[1:i + 1] * (1 - pi) + dist[0:i] * pi
        dist[0] *= (1 - pi)
    return dist


def _tail(index: _Index, lo: float, hi: float, w: float, s: int) -> float:
    """P(count >= s) under the circular shift within ``[lo, hi)``; 1 for an empty context."""
    if hi <= lo:
        return 1.0
    pmf = _poisson_binomial(index.catch_probabilities(lo, hi, w))
    return float(pmf[s:].sum()) if s < pmf.size else 0.0


def _span_of(ev: list[np.ndarray], lo: float, hi: float):
    """First and last onset in ``[lo, hi)`` across ROIs, and how many ROIs had one."""
    tfirst, tlast, n = np.inf, -np.inf, 0
    for v in ev:
        a = np.searchsorted(v, lo, side="left")
        b = np.searchsorted(v, hi, side="left")
        if b > a:
            n += 1
            tfirst = min(tfirst, v[a])
            tlast = max(tlast, v[b - 1])
    return tfirst, tlast, n


def _runs(starts: np.ndarray, ends: np.ndarray, gap: float) -> np.ndarray:
    """Run label per interval, intervals sorted by start and possibly overlapping: a new run
    wherever an interval starts more than ``gap`` after everything before it has ended."""
    if starts.size == 0:
        return np.empty(0, dtype=int)
    reach = np.maximum.accumulate(ends)
    return np.r_[0, np.cumsum(starts[1:] - reach[:-1] > gap)]


# ------------------------------------------------------------------------------- the detector

def stack_detect(
    trains: list[np.ndarray],
    t_range: tuple[float, float],
    *,
    widths_sec: tuple[float, ...] = (0.25, 0.5, 1.0, 2.0),
    context_sec: float = 120.0,
    null_context_mode: str = "maxlt",
    alpha: float = 1e-3,
    min_rois: int = 3,
    merge_gap_sec: float = 3.0,
    guard_sec: float = 0.0,
    frame_interval_sec: float | None = None,
) -> StackDetection:
    """Run stack on one stream's onsets (``trains``: one array of onset times per ROI, seconds)
    over ``t_range``. See the module docstring for the rule.

    ``frame_interval_sec``: widths under it are dropped, since a window narrower than a frame
    resolves nothing. ``guard_sec`` pulls each ``maxlt`` half away from the window by
    ``guard_sec / 2``, as LoCo's guard does; it is refused with ``"symmetric"``, as in LoCo.
    """
    if null_context_mode not in NULL_CONTEXT_MODES:
        raise ValueError(f"null_context_mode must be one of {NULL_CONTEXT_MODES}")
    if guard_sec and null_context_mode == "symmetric":
        raise ValueError("guard_sec is only supported with null_context_mode='maxlt'")
    widths = sorted({float(w) for w in widths_sec})
    if not widths or min(widths) <= 0:
        raise ValueError("widths_sec must be positive")
    if frame_interval_sec is not None:
        widths = [w for w in widths if w >= float(frame_interval_sec)]
        if not widths:
            raise ValueError(f"every width is under the frame interval {frame_interval_sec:g} s")
    if not 0 < alpha < 1:
        raise ValueError("alpha must lie in (0, 1)")
    if context_sec <= 0 or merge_gap_sec < 0 or guard_sec < 0:
        raise ValueError("context_sec must be positive; merge_gap_sec and guard_sec >= 0")

    t0, t1 = map(float, t_range)
    K = max(1, int(min_rois))
    a_w = float(alpha) / len(widths)
    half, g = float(context_sec) / 2, float(guard_sec) / 2
    ev = _clip_sorted(trains, t0, t1)
    index = _Index(ev)

    def tail_at(c: float, w: float, s: int) -> float:
        if null_context_mode == "maxlt":
            return max(_tail(index, max(c - half, t0), c - g, w, s),
                       _tail(index, c + g, min(c + half, t1), w, s))
        return _tail(index, max(c - half, t0), min(c + half, t1), w, s)

    per_width = []
    st, en, sv, pv, wi = [], [], [], [], []
    for i, w in enumerate(widths):
        starts, ends, S = _pieces(ev, w, t0, t1)
        p = np.ones(starts.size)
        for j in np.flatnonzero(S >= K):
            p[j] = tail_at(starts[j] - w / 2, w, int(S[j]))
        per_width.append((starts, S, p))
        m = (S >= K) & (p <= a_w + 1e-12)
        st.append(starts[m])
        en.append(ends[m])
        sv.append(S[m])
        pv.append(p[m])
        wi.append(np.full(int(m.sum()), i))
    st, en, sv, pv, wi = map(np.concatenate, (st, en, sv, pv, wi))
    o = np.argsort(st, kind="stable")
    st, en, sv, pv, wi = st[o], en[o], sv[o], pv[o], wi[o]

    run = _runs(st, en, float(merge_gap_sec))
    n = int(run[-1] + 1) if run.size else 0
    onset, width, nrois = np.zeros(n), np.zeros(n), np.zeros(n)
    stab, pcall = np.zeros(n), np.zeros(n)
    for j in range(n):
        m = run == j
        tfirst, tlast = np.inf, -np.inf
        for i in np.unique(wi[m]):
            mi = m & (wi == i)
            a, b, _ = _span_of(ev, st[mi].min() - widths[i], en[mi].max())
            tfirst, tlast = min(tfirst, a), max(tlast, b)
        onset[j], width[j] = tfirst, tlast - tfirst
        best = np.lexsort((wi[m], pv[m]))[0]        # smallest p, then the narrowest width
        stab[j], pcall[j] = widths[wi[m][best]], pv[m][best]
        nrois[j] = sv[m][wi[m] == wi[m][best]].max()
    with np.errstate(divide="ignore"):
        strength = -np.log10(pcall)

    starts, S, p_wide = per_width[-1]
    opts = dict(widths_sec=tuple(widths), context_sec=float(context_sec),
                null_context_mode=null_context_mode, alpha=float(alpha), min_rois=int(min_rois),
                merge_gap_sec=float(merge_gap_sec), guard_sec=float(guard_sec),
                frame_interval_sec=frame_interval_sec, window_mode="sliding")
    return StackDetection(
        onset_sec=onset, width_sec=width, strength=strength, nrois=nrois,
        width_kind="tightness", ctr=starts, obs=S, threshold=K,
        signal=StackSignal(t=starts, y=S, ref=p_wide, threshold=None,
                           hilite=np.empty((0, 2))),
        ext=(t0, t1), opts=opts, stability_sec=stab, p_value=pcall, alpha_per_width=a_w,
    )
