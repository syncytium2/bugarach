"""count — the simple rule: a bin and a count.

Split time into fixed bins of ``bin_sec``. In each bin, count the distinct ROIs with an
onset (each ROI capped at one, so a lone bursty ROI cannot drive it). Call a bin when that
count is at least ``min_rois + k_offset``. Join called bins whose gap is at most
``merge_gap_sec``. There is no null, no z-score and no percentile.

**Why it exists** (Tony, 2026-09-26: *"Have we tried to optimize the simple rule: a bin and a
count?"*). Every coded detector here puts a statistic between the count and the call —
CoactDetect a rate-local surrogate null, LoCo and binned SCE a percentile, SPIKE-synch a
synchrony profile. Since ADR-0008 each recording's own chance floor already sets the
participation minimum, so the question is whether anything past the floor earns its cost.
This detector is the answer's baseline: the count against the floor and nothing else.

**The count is CoactDetect's binned statistic** (``coact.py``, the ``obs`` array), counted
the same way here rather than by calling it, for two reasons. CoactDetect draws surrogates
for every candidate bin, which this rule does not need and should not pay for; and a rule
run as "coact at alpha = 1" would put its result under another detector's name.

**The floor is the detector's own minimum**, as for CoactDetect (ADR-0008): the bench sets
``min_rois`` to the recording's floor (``bench.FLOORED_SETTING``) and a search tunes only
``k_offset``, the number of cells above the floor a bin must reach. ``k_offset`` cannot go
below zero, because below the floor is chance by ADR-0008's definition.

Calls are episode spans, like CoactDetect's binned threshold mode: onset at the first called
bin's left edge, width to the last called bin's right edge.

**Two forms, two detector keys**: ``count`` (v1, :func:`count_detect`, fixed bins) and
``count_sliding`` (v2, :func:`count_sliding_detect`, a window that slides). Neither is a flag
on the other, so no result can be read as one when it was the other.

**A third key, ``stack``** (:func:`stack_detect`, 2026-10-07): the sliding count at several
window widths at once, each judged against its own exact shift null, the smallest tail
probability winning. Its single-width case is ``count_sliding``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from bugarach.detectors._shared import clip_sorted
from bugarach.detectors.rate import DetectorSignal


@dataclass
class CountDetection:
    """Called episodes plus the per-bin count. Event fields are parallel arrays of length
    ``n_events``; ``width_kind`` is always ``"episode_span"``."""

    onset_sec: np.ndarray
    width_sec: np.ndarray
    strength: np.ndarray            # = nrois: the rule has no statistic past the count
    nrois: np.ndarray               # the episode's largest distinct-ROI count
    width_kind: str
    ctr: np.ndarray                 # bin centres (s)
    obs: np.ndarray                 # distinct ROIs with an onset, per bin
    threshold: int                  # min_rois + k_offset, the count a bin must reach
    signal: DetectorSignal
    ext: tuple[float, float] = (0.0, 0.0)
    opts: dict = field(default_factory=dict)

    @property
    def n_events(self) -> int:
        return self.onset_sec.size


def count_detect(
    trains: list[np.ndarray],
    t_range: tuple[float, float],
    *,
    bin_sec: float = 2.0,
    min_rois: int = 3,
    k_offset: int = 0,
    merge_gap_sec: float = 3.0,
) -> CountDetection:
    """Bins of ``bin_sec`` whose distinct-ROI count reaches ``min_rois + k_offset``, joined
    across gaps of at most ``merge_gap_sec``.

    ``trains`` are per-ROI onset times, clipped to ``t_range`` here. A merge gap of 0 still
    joins called bins that touch; it joins nothing across a bin that was not called.
    """
    if bin_sec <= 0:
        raise ValueError("bin_sec must be positive")
    if k_offset < 0:
        raise ValueError("k_offset must be >= 0: below the floor is chance (ADR-0008)")
    if merge_gap_sec < 0:
        raise ValueError("merge_gap_sec must be >= 0")
    t0, t1 = t_range
    bw = float(bin_sec)
    K = max(1, int(min_rois) + int(k_offset))

    ev = clip_sorted(trains, t0, t1)
    nb = max(1, int(np.ceil((t1 - t0) / bw)))
    edges = t0 + np.arange(nb + 1) * bw
    ctr = t0 + (np.arange(1, nb + 1) - 0.5) * bw

    obs = np.zeros(nb)
    for e in ev:
        if e.size == 0:
            continue
        bi = np.clip(np.floor((e - t0) / bw).astype(int), 0, nb - 1)
        obs[np.unique(bi)] += 1     # distinct-ROI: 1 per ROI per bin

    called = np.flatnonzero(obs >= K)
    starts_b, ends_b = [], []
    if called.size:
        s_cur = prev = called[0]
        for b in called[1:]:
            if edges[b] - edges[prev + 1] <= merge_gap_sec:
                prev = b
            else:
                starts_b.append(s_cur)
                ends_b.append(prev)
                s_cur = prev = b
        starts_b.append(s_cur)
        ends_b.append(prev)

    onset = np.array([edges[s] for s in starts_b], dtype=float)
    width = np.array([edges[e + 1] - edges[s] for s, e in zip(starts_b, ends_b)], dtype=float)
    nrois = np.array([obs[s:e + 1].max() for s, e in zip(starts_b, ends_b)], dtype=float)
    opts = dict(bin_sec=bin_sec, min_rois=min_rois, k_offset=k_offset,
                merge_gap_sec=merge_gap_sec)
    return CountDetection(
        onset_sec=onset, width_sec=width, strength=nrois.copy(), nrois=nrois,
        width_kind="episode_span", ctr=ctr, obs=obs, threshold=K,
        signal=DetectorSignal(t=ctr, y=obs, ref=np.full(nb, float(K)), threshold=None,
                              hilite=np.empty((0, 2)), name="count / floor + k",
                              kind="count"),
        ext=t_range, opts=opts,
    )


def _split_at_dips(S: np.ndarray, idx: np.ndarray, K: int, ratio: float) -> list[np.ndarray]:
    """One merged run (``idx``: its pieces at or above ``K``) cut at every deep valley.

    Walks every piece from the run's first to its last, those under ``K`` included, keeping
    the current peak and the lowest point since it. When the count climbs back to at least
    ``K`` and the valley behind it is below ``ratio`` times the smaller of the two peaks, the
    run is cut at the valley. A higher peak with no deep valley before it simply becomes the
    current peak, so a count that wobbles near its top never splits.
    """
    lo, hi = int(idx[0]), int(idx[-1])
    cuts = []
    peak, valley, v_at = S[lo], np.inf, None
    for i in range(lo + 1, hi + 1):
        s = S[i]
        if v_at is not None and s >= K and valley < ratio * min(peak, s):
            cuts.append(v_at)
            peak, valley, v_at = s, np.inf, None
        elif s > peak:
            peak, valley, v_at = s, np.inf, None
        elif s < valley:
            valley, v_at = s, i
    if not cuts:
        return [idx]
    out, prev = [], lo
    for c in cuts + [hi + 1]:
        part = idx[(idx >= prev) & (idx < c)]
        if part.size:
            out.append(part)
        prev = c
    return out


def count_sliding_detect(
    trains: list[np.ndarray],
    t_range: tuple[float, float],
    *,
    win_sec: float = 2.0,
    min_rois: int = 3,
    k_offset: int = 0,
    merge_gap_sec: float = 3.0,
    split_dip: float | None = None,
) -> CountDetection:
    """v2, the sliding form (Tony, 2026-09-26: *"Simple rule v2 should be sliding"*).

    **``split_dip``** (off by default) splits a call where the count falls between two peaks:
    at a valley below ``split_dip`` times the smaller of the peaks on either side of it,
    both peaks at or above the threshold. It exists because the window keeps the count up
    for ``win_sec`` after each coordinated event, so two events *a* and *b* seconds apart
    leave runs only *b* − *a* − ``win_sec`` apart, and a 3 s merge gap joins any pair
    closer than about 5 s into one call. Tony found two such pairs on the DI combined
    senktide raster page (2026-09-28, 20260130_270 near 2.5 min, 20260130_272 near 4.5
    min): *"we need to fix the merge"*. A split is taken at the valley, so a ragged single
    event whose count wobbles without falling far stays one call.

    At every instant t, the distinct ROIs with an onset in ``(t - win_sec, t]``; a call while
    that count is at least ``min_rois + k_offset``, and called runs joined when their gap is at
    most ``merge_gap_sec``. Computed exactly as a step function between events
    (:func:`bugarach.detectors.sliding.pieces`), so there is no frame step and no grid for an
    edge to fall between four onsets.

    **It is CoactDetect's sliding form with the null taken out**: the same count, the same run
    merge (:func:`~bugarach.detectors.sliding.merge_runs`) and the same call extent, from the
    first participating event to the last (``width_kind="tightness"``). Kept apart from
    :func:`count_detect` under its own detector key (``count_sliding``) so a result always says
    which form it used; ``search_all_settings --sliding`` switches only LoCo and CoactDetect.

    **The viewer's turbo marks** (``docs/site/viewer.template.html``, ``turboMarks``) count the
    same thing and differ in three details: their window is closed at both ends (a tie at
    exactly ``win_sec`` apart counts, here it does not); their merge gap is measured from the
    end of the events a mark covers, which in these terms joins runs up to
    ``merge_gap_sec + win_sec`` apart; and a mark's time is the middle of its events, not the
    first of them. Those marks have never been scored; this is the scored form.
    """
    from bugarach.detectors import sliding as sl

    if win_sec <= 0:
        raise ValueError("win_sec must be positive")
    if k_offset < 0:
        raise ValueError("k_offset must be >= 0: below the floor is chance (ADR-0008)")
    if merge_gap_sec < 0:
        raise ValueError("merge_gap_sec must be >= 0")
    if split_dip is not None and not 0.0 < split_dip < 1.0:
        raise ValueError("split_dip must be None or strictly between 0 and 1")
    t0, t1 = t_range
    w = float(win_sec)
    K = max(1, int(min_rois) + int(k_offset))
    ev = clip_sorted(trains, t0, t1)
    starts, ends, S = sl.pieces(ev, w, t0, t1)
    sig = np.flatnonzero(S >= K)
    runs = sl.merge_runs(starts[sig], ends[sig], merge_gap_sec)
    calls = []                          # arrays of piece indices at or above K, one per call
    for a, b in runs:
        idx = sig[a:b + 1]
        if split_dip is None:
            calls.append(idx)
        else:
            calls.extend(_split_at_dips(S, idx, K, split_dip))
    n = len(calls)
    onset, width, nrois = np.zeros(n), np.zeros(n), np.zeros(n)
    for j, idx in enumerate(calls):
        tfirst, tlast, _ = sl.span_of(ev, starts[idx[0]] - w, ends[idx[-1]])
        onset[j], width[j] = tfirst, tlast - tfirst
        nrois[j] = S[idx].max()
    opts = dict(win_sec=win_sec, min_rois=min_rois, k_offset=k_offset,
                merge_gap_sec=merge_gap_sec, split_dip=split_dip, window_mode="sliding")
    return CountDetection(
        onset_sec=onset, width_sec=width, strength=nrois.copy(), nrois=nrois,
        width_kind="tightness", ctr=starts, obs=S, threshold=K,
        signal=DetectorSignal(t=starts, y=S, ref=np.full(S.size, float(K)), threshold=None,
                              hilite=np.empty((0, 2)), name="count (sliding) / floor + k",
                              kind="count"),
        ext=t_range, opts=opts,
    )


@dataclass
class StackDetection(CountDetection):
    """A :class:`CountDetection` plus what the several widths add. Per-call arrays are parallel
    to ``onset_sec``; ``strength`` is ``-log10`` of the call's smallest tail probability."""

    stability_sec: np.ndarray = field(default_factory=lambda: np.empty(0))
    """Per call, the window width whose count was least likely under the shift null: how
    tightly the tower's onsets sit. The narrowest width wins a tie."""
    p_value: np.ndarray = field(default_factory=lambda: np.empty(0))
    """Per call, that smallest tail probability."""
    alpha: float = 0.0
    """The tail probability a count must reach at any width to be called."""
    thresholds: dict = field(default_factory=dict)
    """``{width_sec: count}``: ``alpha`` restated per width, the count a window must hold."""
    null: dict = field(default_factory=dict)
    """How ``alpha`` was set: the rigid-shift draws, and both rules' call counts on them."""


def _null_tail(ev: list[np.ndarray], t0: float, t1: float, w: float) -> np.ndarray:
    """``tail[s]`` = P(count >= s), s = 0 .. N + 1, for the sliding count at width ``w`` under an
    independent circular shift of every ROI around ``[t0, t1)``: the exact null of ``sliding.py``.

    Uses the ROI-by-ROI recursion rather than the FFT form. The FFT's error is absolute, about
    1e-16, and a tail compared between widths has to be right in relative terms far below that.
    """
    from bugarach.detectors import sliding as sl

    p = np.zeros(len(ev))
    caught = sl.catch_probabilities(ev, t0, t1, w)
    p[:caught.size] = caught            # order is irrelevant to the count's distribution
    pmf = sl._poisson_binomial_loop(p)
    return np.r_[np.cumsum(pmf[::-1])[::-1], 0.0]


def _counts_needed(tails: list[np.ndarray], alpha: float, ref: int, K: int) -> list[int]:
    """Per width, the smallest count whose tail probability is at most ``alpha``; the reference
    width never under ``K``."""
    needed = [int(np.searchsorted(-t, -alpha * (1 + 1e-12), side="left")) for t in tails]
    needed[ref] = max(needed[ref], K)
    return needed


def _runs(starts: np.ndarray, ends: np.ndarray, gap: float) -> np.ndarray:
    """Run label per interval, intervals sorted by start and possibly overlapping: a new run
    wherever an interval starts more than ``gap`` after everything before it has ended. On the
    non-overlapping pieces of one width this is :func:`sliding.merge_runs`."""
    if starts.size == 0:
        return np.empty(0, dtype=int)
    reach = np.maximum.accumulate(ends)
    return np.r_[0, np.cumsum(starts[1:] - reach[:-1] > gap)]


def _stack_pieces(per_width, needed):
    """Every piece at or above its width's needed count, across widths, sorted by start:
    ``(starts, ends, S, width_index)``."""
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


def stack_detect(
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
) -> StackDetection:
    """The sliding count at several widths, the least likely one winning (Tony's "stacking
    blocks", 2026-10-07).

    Stack the onsets inside a sliding window: the tower's **height** is the number of distinct
    ROIs, its **stability** how tightly their onsets sit. Stability needs no statistic of its
    own, because a tight tower is a high count in a *narrow* window. So:

    * at each width in ``widths_sec`` the count is :func:`sliding.pieces`, as ``count_sliding``;
    * each count is turned into its tail probability under the exact circular-shift null of
      ``sliding.py``, taken over the whole of ``t_range`` (each ROI's catch probability, then a
      Poisson-binomial; no random draw);
    * a moment is called when the smallest of those probabilities is at most ``alpha``. With one
      null per width over the whole range that is the same as one needed count per width
      (:attr:`StackDetection.thresholds`), which is how it is computed;
    * called stretches from every width are joined across gaps of at most ``merge_gap_sec``,
      and each call reports the width that won it (:attr:`StackDetection.stability_sec`).

    **``alpha`` is not a setting.** It is the largest tail probability at which this rule calls
    no more often than count (sliding) does at ``ref_win_sec`` and ``min_rois + k_offset`` on
    ``null_draws`` per-ROI rigid shifts of the same recording, uniform in ±``j_sec`` (ADR-0006's
    null, ADR-0008's draws). Looking at several widths is therefore paid for in the needed
    counts, not in extra false alarms. ``alpha`` never exceeds the reference count's own tail
    probability, so the reference width never calls under the floor.

    **With ``widths_sec == (ref_win_sec,)`` this is** :func:`count_sliding_detect` **exactly**
    (``split_dip`` off): no draw is made and every call agrees. That case is the ablation, so a
    difference between the two keys is what the narrower widths add.

    ``frame_interval_sec``: widths under it are dropped, since a window narrower than a frame
    resolves nothing. ``ref_win_sec`` must be one of the widths that remain.

    ⚠ The tail probabilities take each ROI's rate as constant over ``t_range``. A stretch where
    every ROI's rate rises together makes every width's count likelier than its tail says; the
    rigid-shift calibration keeps that stretch, so it is accounted for in ``alpha`` on average
    and not moment by moment.
    """
    import hashlib

    from bugarach.detectors import sliding as sl

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
    ev = clip_sorted(trains, t0, t1)

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
            shifted = clip_sorted([v + du for v, du in zip(ev, u)], t0, t1)
            per = []
            for w, k in zip(widths, loosest):
                s_, e_, S_ = sl.pieces(shifted, w, lo, hi)
                m = S_ >= k             # nothing under the loosest allowed count is ever used
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

        # Candidates: every tail value any width can take, at or under the reference's own,
        # largest first. Bisect for the largest that calls no more often than the reference.
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
    per_width = [sl.pieces(ev, w, t0, t1) for w in widths]
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
            a, b, _ = sl.span_of(ev, st[mi].min() - widths[i], en[mi].max())
            tfirst, tlast = min(tfirst, a), max(tlast, b)
        onset[j], width[j] = tfirst, tlast - tfirst
        best = np.lexsort((wi[m], pv[m]))[0]    # smallest p, then the narrowest width
        stab[j], pcall[j] = widths[wi[m][best]], pv[m][best]
        nrois[j] = sv[m][wi[m] == wi[m][best]].max()
    with np.errstate(divide="ignore"):
        strength = -np.log10(pcall)
    starts, _, S = per_width[ref]
    opts = dict(widths_sec=tuple(widths), ref_win_sec=ref_win_sec, min_rois=min_rois,
                k_offset=k_offset, merge_gap_sec=merge_gap_sec,
                frame_interval_sec=frame_interval_sec, null_draws=null_draws, j_sec=j_sec,
                window_mode="sliding")
    return StackDetection(
        onset_sec=onset, width_sec=width, strength=strength, nrois=nrois,
        width_kind="tightness", ctr=starts, obs=S, threshold=needed[ref],
        signal=DetectorSignal(t=starts, y=S, ref=np.full(S.size, float(needed[ref])),
                              threshold=None, hilite=np.empty((0, 2)),
                              name=f"stack: count in {ref_win_sec:g} s / count needed",
                              kind="count"),
        ext=t_range, opts=opts, stability_sec=stab, p_value=pcall, alpha=alpha,
        thresholds={w: k for w, k in zip(widths, needed)}, null=null,
    )
