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


def count_sliding_detect(
    trains: list[np.ndarray],
    t_range: tuple[float, float],
    *,
    win_sec: float = 2.0,
    min_rois: int = 3,
    k_offset: int = 0,
    merge_gap_sec: float = 3.0,
) -> CountDetection:
    """v2, the sliding form (Tony, 2026-09-26: *"Simple rule v2 should be sliding"*).

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
    t0, t1 = t_range
    w = float(win_sec)
    K = max(1, int(min_rois) + int(k_offset))
    ev = clip_sorted(trains, t0, t1)
    starts, ends, S = sl.pieces(ev, w, t0, t1)
    sig = np.flatnonzero(S >= K)
    runs = sl.merge_runs(starts[sig], ends[sig], merge_gap_sec)
    n = len(runs)
    onset, width, nrois = np.zeros(n), np.zeros(n), np.zeros(n)
    for j, (a, b) in enumerate(runs):
        idx = sig[a:b + 1]
        tfirst, tlast, _ = sl.span_of(ev, starts[idx[0]] - w, ends[idx[-1]])
        onset[j], width[j] = tfirst, tlast - tfirst
        nrois[j] = S[idx].max()
    opts = dict(win_sec=win_sec, min_rois=min_rois, k_offset=k_offset,
                merge_gap_sec=merge_gap_sec, window_mode="sliding")
    return CountDetection(
        onset_sec=onset, width_sec=width, strength=nrois.copy(), nrois=nrois,
        width_kind="tightness", ctr=starts, obs=S, threshold=K,
        signal=DetectorSignal(t=starts, y=S, ref=np.full(S.size, float(K)), threshold=None,
                              hilite=np.empty((0, 2)), name="count (sliding) / floor + k",
                              kind="count"),
        ext=t_range, opts=opts,
    )
