"""stack_global: stack's first form, kept as it was (Tony's "stacking blocks", 2026-10-07).

The sliding distinct-ROI count at several widths, each against **one exact circular-shift null
for the whole range**, the least likely width winning. The calling probability is not a setting:
it is calibrated on rigid shifts of the same recording so this rule calls no more often than the
plain sliding count does at the reference width and the floor.

**Why it is kept.** ``stack`` moved to a local context-window null on 2026-10-07. The same day
Tony looked at this first form's calls on real recordings and asked for it to be preserved
(*"make sure the old stack is preserved. i've just looked at its performance on real data and
wow"*). It is the form ``docs/learned/runs/2026-10-07-stack/`` measured, on the benches and on
the September pilot recordings.

**Unchanged, and proven so.** The algorithm is the one ``stack_detect`` ran at ``8646eb4``, line
for line. ``tests/test_stack_global.py`` checks it against a fixture of that commit's output,
``tests/fixtures/stack_global_8646eb4.json``, exactly, on recordings that exercise the rigid-shift
calibration.

**Self-contained** (Tony, 2026-10-07: stack should not depend on code that might change under
it). This module imports numpy and the standard library only, and its test fails if that
changes. The helpers below are copies of ``sliding.py``'s and ``_shared.py``'s at ``8646eb4``,
not imports.

The rule:

* at each width in ``widths_sec`` the count is the step function of distinct ROIs with an onset
  in ``(t - w, t]``, with no grid;
* each count is turned into its tail probability under the exact circular-shift null taken over
  the whole of ``t_range`` (each ROI's catch probability, then a Poisson-binomial);
* a moment is called when the smallest of those probabilities is at most ``alpha``. With one null
  per width that is the same as one needed count per width (:attr:`StackGlobalDetection.thresholds`);
* called stretches from every width are joined across gaps of at most ``merge_gap_sec``, and
  each call reports the width that won it (:attr:`StackGlobalDetection.stability_sec`).

**``alpha`` is not a setting.** It is the largest tail probability at which this rule calls no
more often than the sliding count does at ``ref_win_sec`` and ``min_rois + k_offset`` on
``null_draws`` per-ROI rigid shifts of the same recording, uniform in ±``j_sec`` (ADR-0006's
null, ADR-0008's draws). ``alpha`` never exceeds the reference count's own tail probability, so
the reference width never calls under the floor.

**With ``widths_sec == (ref_win_sec,)`` this is count (sliding) exactly** (``split_dip`` off): no
draw is made and every call agrees.

⚠ The tail probabilities take each ROI's rate as constant over ``t_range``. A stretch where every
ROI's rate rises together makes every width's count likelier than its tail says; the rigid-shift
calibration keeps that stretch, so it is accounted for in ``alpha`` on average and not moment by
moment.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

import numpy as np


@dataclass
class StackGlobalSignal:
    """The plot-ready trace, with the field names of the detector output contract's
    ``emit_signal`` (``docs/detector_output_spec.md``)."""

    t: np.ndarray
    y: np.ndarray
    ref: np.ndarray
    threshold: None
    hilite: np.ndarray
    name: str = "stack (global)"
    kind: str = "count"


@dataclass
class StackGlobalDetection:
    """Calls as parallel arrays of length ``n_events``, under the field names count (sliding)'s
    result uses. ``strength`` is ``-log10`` of the call's smallest tail probability."""

    onset_sec: np.ndarray
    width_sec: np.ndarray
    strength: np.ndarray
    nrois: np.ndarray
    width_kind: str
    ctr: np.ndarray
    obs: np.ndarray
    threshold: int
    signal: StackGlobalSignal
    ext: tuple[float, float] = (0.0, 0.0)
    opts: dict = field(default_factory=dict)
    stability_sec: np.ndarray = field(default_factory=lambda: np.empty(0))
    """Per call, the window width whose count was least likely under the shift null."""
    p_value: np.ndarray = field(default_factory=lambda: np.empty(0))
    """Per call, that smallest tail probability."""
    alpha: float = 0.0
    """The tail probability a count must reach at any width to be called."""
    thresholds: dict = field(default_factory=dict)
    """``{width_sec: count}``: ``alpha`` restated per width, the count a window must hold."""
    null: dict = field(default_factory=dict)
    """How ``alpha`` was set: the rigid-shift draws, and both rules' call counts on them."""

    @property
    def n_events(self) -> int:
        return self.onset_sec.size


# --------------------------------------------- copies of sliding.py / _shared.py at 8646eb4

def _clip_sorted(trains, lo: float, hi: float) -> list[np.ndarray]:
    out = []
    for v in trains:
        v = np.asarray(v, dtype=float).ravel()
        v = v[np.isfinite(v)]
        out.append(np.sort(v[(v >= lo) & (v <= hi)]))
    return out


def _pieces(ev: list[np.ndarray], w: float, t_lo: float, t_hi: float):
    times, deltas = [], []
    for v in ev:
        if v.size == 0:
            continue
        s = np.asarray(v, dtype=float)
        e = s + w
        brk = np.flatnonzero(s[1:] > e[:-1])
        m_start = np.concatenate(([s[0]], s[brk + 1]))
        m_end = np.concatenate((e[brk], [e[-1]]))
        times += [m_start, m_end]
        deltas += [np.ones(m_start.size), -np.ones(m_end.size)]
    if not times:
        return np.empty(0), np.empty(0), np.empty(0)
    t = np.concatenate(times)
    d = np.concatenate(deltas)
    order = np.lexsort((d, t))
    t, d = t[order], d[order]
    level = np.cumsum(d)
    last = np.r_[t[1:] != t[:-1], True]
    ut, lv = t[last], level[last]
    starts, ends = ut[:-1], ut[1:]
    S = lv[:-1]
    starts = np.maximum(starts, t_lo)
    ends = np.minimum(ends, t_hi)
    keep = ends > starts
    return starts[keep], ends[keep], S[keep]


class _Index:
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
        nxt[last] = x[offs] + L
        return np.add.reduceat(np.minimum(nxt - x, w), offs) / L


def _poisson_binomial_loop(p: np.ndarray) -> np.ndarray:
    dist = np.zeros(p.size + 1)
    dist[0] = 1.0
    for i, pi in enumerate(p, start=1):
        dist[1:i + 1] = dist[1:i + 1] * (1 - pi) + dist[0:i] * pi
        dist[0] *= (1 - pi)
    return dist


def _span_of(ev: list[np.ndarray], lo: float, hi: float):
    tfirst, tlast, n = np.inf, -np.inf, 0
    for v in ev:
        a = np.searchsorted(v, lo, side="left")
        b = np.searchsorted(v, hi, side="left")
        if b > a:
            n += 1
            tfirst = min(tfirst, v[a])
            tlast = max(tlast, v[b - 1])
    return tfirst, tlast, n


# ------------------------------------------------------------- stack's own helpers at 8646eb4

def _null_tail(ev: list[np.ndarray], t0: float, t1: float, w: float) -> np.ndarray:
    """``tail[s]`` = P(count >= s), s = 0 .. N + 1, for the sliding count at width ``w`` under an
    independent circular shift of every ROI around ``[t0, t1)``. The ROI-by-ROI recursion,
    because a tail compared between widths has to be right in relative terms."""
    p = np.zeros(len(ev))
    caught = _Index(ev).catch_probabilities(t0, t1, w)
    p[:caught.size] = caught
    pmf = _poisson_binomial_loop(p)
    return np.r_[np.cumsum(pmf[::-1])[::-1], 0.0]


def _counts_needed(tails: list[np.ndarray], alpha: float, ref: int, K: int) -> list[int]:
    needed = [int(np.searchsorted(-t, -alpha * (1 + 1e-12), side="left")) for t in tails]
    needed[ref] = max(needed[ref], K)
    return needed


def _runs(starts: np.ndarray, ends: np.ndarray, gap: float) -> np.ndarray:
    if starts.size == 0:
        return np.empty(0, dtype=int)
    reach = np.maximum.accumulate(ends)
    return np.r_[0, np.cumsum(starts[1:] - reach[:-1] > gap)]


def _stack_pieces(per_width, needed):
    st, en, sv, wi = [], [], [], []
    for i, ((starts, ends, S), k) in enumerate(zip(per_width, needed)):
        m = S >= k
        st.append(starts[m])
        en.append(ends[m])
        sv.append(S[m])
        wi.append(np.full(int(m.sum()), i))
    st, en, sv, wi = map(np.concatenate, (st, en, sv, wi))
    o = np.argsort(st, kind="stable")
    return st[o], en[o], sv[o], wi[o]


# ------------------------------------------------------------------------------- the detector

def stack_global_detect(
    trains: list[np.ndarray],
    t_range: tuple[float, float],
    *,
    widths_sec: tuple[float, ...] = (0.25, 0.5, 1.0, 2.0),
    ref_win_sec: float = 2.0,
    min_rois: int = 3,
    k_offset: int = 0,
    merge_gap_sec: float = 3.0,
    frame_interval_sec: float | None = None,
    null_draws: int = 200,
    j_sec: float = 20.0,
) -> StackGlobalDetection:
    """stack's first form. See the module docstring for the rule.

    ``frame_interval_sec``: widths under it are dropped, since a window narrower than a frame
    resolves nothing. ``ref_win_sec`` must be one of the widths that remain.
    """
    widths = sorted({float(w) for w in widths_sec})
    if not widths or min(widths) <= 0:
        raise ValueError("widths_sec must be positive")
    if frame_interval_sec is not None:
        widths = [w for w in widths if w >= float(frame_interval_sec)]
    if float(ref_win_sec) not in widths:
        raise ValueError(f"ref_win_sec={ref_win_sec} must be one of the widths kept: {widths}")
    if k_offset < 0:
        raise ValueError("k_offset must be >= 0: below the floor is chance (ADR-0008)")
    if merge_gap_sec < 0:
        raise ValueError("merge_gap_sec must be >= 0")
    t0, t1 = map(float, t_range)
    K = max(1, int(min_rois) + int(k_offset))
    gap = float(merge_gap_sec)
    ref = widths.index(float(ref_win_sec))
    ev = _clip_sorted(trains, t0, t1)

    tails = [_null_tail(ev, t0, t1, w) for w in widths]
    alpha_max = float(tails[ref][min(K, tails[ref].size - 1)])
    alpha, null = alpha_max, dict(draws=0, ref_calls=None, stack_calls=None, hours=0.0)
    if len(widths) > 1 and alpha_max > 0:
        if t1 - t0 <= 2 * j_sec + max(widths):
            raise ValueError(f"a {t1 - t0:g} s range is too short to calibrate against rigid "
                             f"shifts of ±{j_sec:g} s")
        h = hashlib.sha256(repr((t0, t1, tuple(widths), K, gap, float(j_sec))).encode())
        for v in ev:
            h.update(v.tobytes())
            h.update(b"|")
        rng = np.random.RandomState(int.from_bytes(h.digest()[:4], "little"))
        lo, hi = t0 + j_sec, t1 - j_sec
        loosest = _counts_needed(tails, alpha_max, ref, K)
        draws, ref_calls = [], 0
        for _ in range(int(null_draws)):
            u = rng.uniform(-j_sec, j_sec, size=len(ev))
            shifted = _clip_sorted([v + du for v, du in zip(ev, u)], t0, t1)
            per = []
            for w, k in zip(widths, loosest):
                s_, e_, S_ = _pieces(shifted, w, lo, hi)
                m = S_ >= k
                per.append((s_[m], e_[m], S_[m]))
            draws.append(per)
            r = _runs(per[ref][0], per[ref][1], gap)
            ref_calls += int(r[-1] + 1) if r.size else 0

        def calls_at(a: float) -> int:
            needed = _counts_needed(tails, a, ref, K)
            total = 0
            for per in draws:
                st, en, _, _ = _stack_pieces(per, needed)
                r = _runs(st, en, gap)
                total += int(r[-1] + 1) if r.size else 0
            return total

        cand = np.unique(np.concatenate([t[(t > 0) & (t <= alpha_max * (1 + 1e-12))]
                                         for t in tails]))[::-1]
        pick = 0
        if calls_at(cand[0]) > ref_calls:
            a_i, b_i = 0, cand.size - 1
            while b_i - a_i > 1:
                m_i = (a_i + b_i) // 2
                if calls_at(cand[m_i]) <= ref_calls:
                    b_i = m_i
                else:
                    a_i = m_i
            pick = b_i
        alpha = float(cand[pick])
        null = dict(draws=int(null_draws), ref_calls=int(ref_calls),
                    stack_calls=int(calls_at(alpha)),
                    hours=float(null_draws * (hi - lo) / 3600.0), j_sec=float(j_sec))

    needed = _counts_needed(tails, alpha, ref, K)
    per_width = [_pieces(ev, w, t0, t1) for w in widths]
    st, en, sv, wi = _stack_pieces(per_width, needed)
    run = _runs(st, en, gap)
    n = int(run[-1] + 1) if run.size else 0
    pv = np.array([tails[i][int(s)] for i, s in zip(wi, sv)]) if st.size else np.empty(0)
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
        best = np.lexsort((wi[m], pv[m]))[0]
        stab[j], pcall[j] = widths[wi[m][best]], pv[m][best]
        nrois[j] = sv[m][wi[m] == wi[m][best]].max()
    with np.errstate(divide="ignore"):
        strength = -np.log10(pcall)
    starts, _, S = per_width[ref]
    opts = dict(widths_sec=tuple(widths), ref_win_sec=ref_win_sec, min_rois=min_rois,
                k_offset=k_offset, merge_gap_sec=merge_gap_sec,
                frame_interval_sec=frame_interval_sec, null_draws=null_draws, j_sec=j_sec,
                window_mode="sliding")
    return StackGlobalDetection(
        onset_sec=onset, width_sec=width, strength=strength, nrois=nrois,
        width_kind="tightness", ctr=starts, obs=S, threshold=needed[ref],
        signal=StackGlobalSignal(t=starts, y=S, ref=np.full(S.size, float(needed[ref])),
                                 threshold=None, hilite=np.empty((0, 2)),
                                 name=f"stack (global): count in {ref_win_sec:g} s / count needed"),
        ext=t_range, opts=opts, stability_sec=stab, p_value=pcall, alpha=alpha,
        thresholds={w: k for w, k in zip(widths, needed)}, null=null,
    )
