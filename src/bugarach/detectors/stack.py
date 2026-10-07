"""stack: the sliding distinct-ROI count at several widths, each against a local exact null,
the least likely width winning, calibrated per recording (Tony's "stacking blocks", 2026-10-07).

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
  chance of landing in the window has a closed form, and the count is their Poisson-binomial;
* ``null_context_mode="maxlt"`` (the default, as in LoCo) takes the trailing and the leading
  half-context separately and keeps the **larger** of the two tail probabilities, so a rate edge
  on one side cannot make a window look unlikely. ``"symmetric"`` uses one context centred on the
  window;
* a piece is called when its count reaches ``min_rois`` and its tail probability is at most the
  recording's calling probability ``alpha``, the same at every width.

**``alpha`` is calibrated, not set** (Tony, 2026-10-07: match count (sliding) at the floor). A
probability per window is not a rate per hour: a 0.3 s window is tested about seven times as often
per hour as a 2 s one, so a fixed ``alpha`` let the narrow widths add false calls (on independent
simulated background, about 4 per hour at ``alpha`` 1e-3 against the bench's limit of 3). So on
``null_draws`` per-ROI rigid shifts of the recording, uniform in ±``j_sec``, ``alpha`` is the
largest tail probability at which stack calls no more often than count (sliding) does at
``ref_win_sec`` and the floor ``min_rois``, merged at the same gap. The draws are seeded from the
recording itself, so a run is repeatable. Passing ``alpha`` skips the calibration and uses it at
every width as given.

Called pieces from every width are joined across gaps of at most the merge gap. Each call reports
its first and last participating onset, its smallest tail probability, and the width that produced
it (:attr:`StackDetection.stability_sec`; the narrowest wins a tie).

**Settings, and where each comes from:**

* ``stream`` is required and sets the merge gap, :data:`MERGE_GAP_SEC`: fast 0.5 s, slow 2.5 s,
  combined 2.5 s. They are the gaps that define one event's onsets in ``bugarach.call_measure``
  (Tony, 2026-09-21), copied here and checked against it from outside, so each stream merges as it
  defines an event (Tony, 2026-10-07: *"stack should have merge gaps consistent with each
  stream"*). On combined that replaces the 3 s first form, which his September pilot rasters show
  joining distinct events.
* ``min_rois`` is required: the window's ADR-0008 floor. A default let a caller run under it.
* ``widths_sec`` 0.3, 0.5, 1 and 2 s: 3, 5, 10 and 20 frames at the 0.1 s frame interval of all
  internal work (Tony, 2026-10-07), the narrowest spanning the fast stream's onset jitter
  (σ ≈ 0.11 s). Widths under ``frame_interval_sec`` are dropped.
* ``context_sec`` 120 s and ``maxlt``: LoCo's. Untuned.

**One width with a fixed ``alpha`` is LoCo in a sliding window.** With ``widths_sec=(w,)`` and
``alpha = 1 - threshold_pctile / 100`` this calls exactly where LoCo's sliding path does at bin
width ``w``, the same context, null mode, guard, ``min_rois`` and merge gap, on a recording with no
region windows (``tests/test_stack.py``).

**Self-contained on purpose** (Tony, 2026-10-07: stack should not depend on code that might
change under it). This module imports numpy and the standard library and nothing else from
``bugarach``; the exact null, the sweep and the result types are its own.
``tests/test_stack.py`` fails if an import from the package appears here. The equivalences with
LoCo and ``call_measure`` are tested from outside, so a change to either shows up as a failing
test, never as a silent change to stack.

``stack_global`` (``stack_global.py``) is stack's first form, kept unchanged: one null for the
whole recording.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

import numpy as np

NULL_CONTEXT_MODES = ("maxlt", "symmetric")

MERGE_GAP_SEC = {"fast": 0.5, "slow": 2.5, "combined": 2.5}
"""Per stream, the gap at which called pieces join into one call: ``call_measure``'s per-stream
gap, the spacing that defines one event's onsets on that stream."""

MINIMUM_ROIS = 3
"""The fewest ROIs any width may call on. ADR-0008, decision 1: a pair never counts as a
coordinated event. Copied here because this module imports nothing from the package;
``tests/test_stack.py`` checks it against ``bugarach.event_floor.MINIMUM_ROIS`` from outside."""

WIDTHS_SEC = (0.3, 0.5, 1.0, 2.0)
"""3, 5, 10 and 20 frames at the 0.1 s frame interval."""


@dataclass
class StackSignal:
    """The plot-ready trace, with the field names of the detector output contract's
    ``emit_signal`` (``docs/detector_output_spec.md``): the count at the reference width (``y``)
    and its local tail probability at each piece (``ref``; 1 where the count is under
    ``min_rois`` and nothing was computed)."""

    t: np.ndarray
    y: np.ndarray
    ref: np.ndarray
    threshold: None
    hilite: np.ndarray
    name: str = "stack: distinct ROIs / reference window"
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
    alpha: float = 0.0
    """The tail probability a piece must reach, at any width, to be called."""
    null: dict = field(default_factory=dict)
    """How ``alpha`` was set: the rigid-shift draws, and both rules' call counts on them."""

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



def _scored_pieces(ev, t0, t1, lo, hi, widths, kmin, context_sec, mode, guard_sec):
    """Every piece in ``[lo, hi]`` whose count reaches its width's minimum ``kmin[i]``, across
    the widths, with its local tail probability: ``(starts, ends, S, p, width_index)``, sorted
    by start. Also each width's full ``(starts, S, p)`` for the signal."""
    index = _Index(ev)
    half, g = float(context_sec) / 2, float(guard_sec) / 2

    def tail_at(c: float, w: float, s: int) -> float:
        if mode == "maxlt":
            return max(_tail(index, max(c - half, t0), c - g, w, s),
                       _tail(index, c + g, min(c + half, t1), w, s))
        return _tail(index, max(c - half, t0), min(c + half, t1), w, s)

    st, en, sv, pv, wi, full = [], [], [], [], [], []
    for i, w in enumerate(widths):
        starts, ends, S = _pieces(ev, w, lo, hi)
        p = np.ones(starts.size)
        for j in np.flatnonzero(S >= kmin[i]):
            p[j] = tail_at(starts[j] - w / 2, w, int(S[j]))
        full.append((starts, S, p))
        m = S >= kmin[i]
        st.append(starts[m])
        en.append(ends[m])
        sv.append(S[m])
        pv.append(p[m])
        wi.append(np.full(int(m.sum()), i))
    st, en, sv, pv, wi = map(np.concatenate, (st, en, sv, pv, wi))
    o = np.argsort(st, kind="stable")
    return (st[o], en[o], sv[o], pv[o], wi[o]), full


def _n_calls(st, en, keep, gap) -> int:
    r = _runs(st[keep], en[keep], gap)
    return int(r[-1] + 1) if r.size else 0


# ------------------------------------------------------------------------------- the detector

def stack_detect(
    trains: list[np.ndarray],
    t_range: tuple[float, float],
    *,
    stream: str,
    min_rois: int,
    widths_sec: tuple[float, ...] = WIDTHS_SEC,
    ref_win_sec: float = 2.0,
    context_sec: float = 120.0,
    null_context_mode: str = "maxlt",
    alpha: float | None = None,
    merge_gap_sec: float | None = None,
    guard_sec: float = 0.0,
    frame_interval_sec: float | None = None,
    null_draws: int = 200,
    j_sec: float = 20.0,
    min_rois_narrow: int = MINIMUM_ROIS,
) -> StackDetection:
    """Run stack on one stream's onsets (``trains``: one array of onset times per ROI, seconds)
    over ``t_range``. See the module docstring for the rule and where each setting comes from.

    ``min_rois`` (the window's ADR-0008 floor, measured at a 2 s window) applies at
    ``ref_win_sec``. A narrower width needs ``min_rois_narrow`` ROIs and is judged by its
    tail probability: the floor counts co-activity at 2 s, and a tight group of fewer cells
    than that is what the narrow widths are for. Gating every width at the 2 s floor would make
    stack a subset of count (sliding).

    **Neither may be under** :data:`MINIMUM_ROIS`. This used to let the narrow widths call on
    2 ROIs. Tony, 2026-10-07: *"2 rois do not make a coordinated event under any
    circumstances."*

    ``merge_gap_sec`` overrides the stream's :data:`MERGE_GAP_SEC`. ``alpha`` skips the
    calibration. ``guard_sec`` pulls each ``maxlt`` half away from the window by ``guard_sec / 2``,
    as LoCo's guard does; it is refused with ``"symmetric"``, as in LoCo.
    """
    if stream not in MERGE_GAP_SEC:
        raise ValueError(f"stream must be one of {tuple(MERGE_GAP_SEC)}")
    if null_context_mode not in NULL_CONTEXT_MODES:
        raise ValueError(f"null_context_mode must be one of {NULL_CONTEXT_MODES}")
    if guard_sec and null_context_mode == "symmetric":
        raise ValueError("guard_sec is only supported with null_context_mode='maxlt'")
    widths = sorted({float(w) for w in widths_sec})
    if not widths or min(widths) <= 0:
        raise ValueError("widths_sec must be positive")
    if frame_interval_sec is not None:
        widths = [w for w in widths if w >= float(frame_interval_sec) - 1e-12]
        if not widths:
            raise ValueError(f"every width is under the frame interval {frame_interval_sec:g} s")
    if float(ref_win_sec) not in widths:
        raise ValueError(f"ref_win_sec={ref_win_sec} must be one of the widths kept: {widths}")
    if min_rois < MINIMUM_ROIS or min_rois_narrow < MINIMUM_ROIS:
        raise ValueError(f"min_rois and min_rois_narrow must be >= {MINIMUM_ROIS}: a pair is "
                         f"never a coordinated event (ADR-0008, decision 1)")
    if alpha is not None and not 0 < alpha < 1:
        raise ValueError("alpha must lie in (0, 1)")
    if context_sec <= 0 or guard_sec < 0:
        raise ValueError("context_sec must be positive and guard_sec >= 0")
    gap = MERGE_GAP_SEC[stream] if merge_gap_sec is None else float(merge_gap_sec)
    if gap < 0:
        raise ValueError("merge_gap_sec must be >= 0")

    t0, t1 = map(float, t_range)
    K = max(1, int(min_rois))
    ref = widths.index(float(ref_win_sec))
    kmin = [K if i == ref else min(K, int(min_rois_narrow)) for i in range(len(widths))]
    ev = _clip_sorted(trains, t0, t1)
    args = (widths, kmin, context_sec, null_context_mode, guard_sec)

    null = dict(draws=0, ref_calls=None, stack_calls=None, hours=0.0)
    if alpha is None:
        if t1 - t0 <= 2 * j_sec + max(widths):
            raise ValueError(f"a {t1 - t0:g} s range is too short to calibrate against rigid "
                             f"shifts of ±{j_sec:g} s")
        h = hashlib.sha256(repr((t0, t1, tuple(widths), tuple(kmin), gap, float(j_sec),
                                 float(context_sec), null_context_mode,
                                 float(guard_sec))).encode())
        for v in ev:
            h.update(v.tobytes())
            h.update(b"|")
        rng = np.random.RandomState(int.from_bytes(h.digest()[:4], "little"))
        lo, hi = t0 + j_sec, t1 - j_sec
        draws, ref_calls = [], 0
        for _ in range(int(null_draws)):
            u = rng.uniform(-j_sec, j_sec, size=len(ev))
            shifted = _clip_sorted([v + du for v, du in zip(ev, u)], t0, t1)
            (st, en, _, p, wi), _ = _scored_pieces(shifted, t0, t1, lo, hi, *args)
            draws.append((st, en, p))
            ref_calls += _n_calls(st, en, wi == ref, gap)    # count (sliding) at the floor

        def calls_at(a: float) -> int:
            return sum(_n_calls(st, en, p <= a, gap) for st, en, p in draws)

        cand = np.unique(np.concatenate([p for _, _, p in draws] + [np.ones(1)]))
        a_i, b_i = -1, cand.size - 1                     # calls_at(cand[-1] = 1) is the most
        if calls_at(cand[b_i]) <= ref_calls:
            pick = float(cand[b_i])
        else:
            while b_i - a_i > 1:                          # largest candidate within the reference
                m_i = (a_i + b_i) // 2
                if calls_at(cand[m_i]) <= ref_calls:
                    a_i = m_i
                else:
                    b_i = m_i
            pick = float(cand[a_i]) if a_i >= 0 else float(cand[0]) / 2
        alpha = pick
        null = dict(draws=int(null_draws), ref_calls=int(ref_calls),
                    stack_calls=int(calls_at(alpha)),
                    hours=float(null_draws * (hi - lo) / 3600.0), j_sec=float(j_sec),
                    reference=f"count (sliding) at {ref_win_sec:g} s and min_rois {K}")

    (st, en, sv, pv, wi), full = _scored_pieces(ev, t0, t1, t0, t1, *args)
    keep = pv <= alpha
    st, en, sv, pv, wi = st[keep], en[keep], sv[keep], pv[keep], wi[keep]
    run = _runs(st, en, gap)
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

    starts, S, p_sig = full[ref]
    opts = dict(stream=stream, widths_sec=tuple(widths), ref_win_sec=float(ref_win_sec),
                context_sec=float(context_sec), null_context_mode=null_context_mode,
                alpha=float(alpha), min_rois=int(min_rois),
                min_rois_narrow=int(min_rois_narrow), merge_gap_sec=gap,
                guard_sec=float(guard_sec), frame_interval_sec=frame_interval_sec,
                null_draws=int(null_draws), j_sec=float(j_sec), window_mode="sliding")
    return StackDetection(
        onset_sec=onset, width_sec=width, strength=strength, nrois=nrois,
        width_kind="tightness", ctr=starts, obs=S, threshold=K,
        signal=StackSignal(t=starts, y=S, ref=p_sig, threshold=None, hilite=np.empty((0, 2))),
        ext=(t0, t1), opts=opts, stability_sec=stab, p_value=pcall, alpha=float(alpha),
        null=null,
    )
