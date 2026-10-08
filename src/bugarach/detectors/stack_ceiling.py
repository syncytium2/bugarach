"""stack_ceiling: how much of the tallest possible stack is already standing (a prototype).

Tony, 2026-10-08: *"what is the tallest stack of width w we can create from circular shifting
events over period p?"* Asked to break out of the approaches ``stack`` shares with LoCo and count
(sliding), so this module computes no tail probability, calibrates nothing and makes no draws.

**The tallest stack is a count, not a search.** Take a period of ``period_sec`` around a moment
and let every ROI's onsets be circularly shifted within it, each ROI by its own amount. Any ROI
with at least one onset in the period can be slid into a window of any width, so the tallest
stack that shifting can build is the number of ROIs with an onset in the period. That is the
**ceiling**, and it does not depend on the window's width.

What does depend on the width is how much of that ceiling the recording holds unshifted:

* the **height** at a moment is the number of distinct ROIs with an onset within ``width_sec / 2``
  of it, the same count ``stack`` and count (sliding) use, in a window centred on the moment;
* the **fill** is the height divided by the ceiling, from 0 to 1;
* an ROI's **shift needed** is how far its nearest onset must move to reach the window, 0 for an
  ROI already in it. Sorted, those are the **growth curve**: the tower's height as a function of
  the shift each ROI is allowed. It starts at the height, ends at the ceiling, and the shift at
  which it passes half the ceiling (:attr:`StackCeiling.half_shift_sec`) says how far apart the
  ROIs sit without choosing a width at all.

:func:`expected_height` is the one reference line: the mean height when every ROI is shifted at
random around the period, exactly, from the fraction of the circle each ROI's onsets cover. It
is a mean to draw beside the growth curve, not a threshold.

**A call rule to try** (:func:`rebuild_cost`, :func:`call_moments`). A shared rise in rate
raises the height while the ceiling stays put, so fill alone calls all through a raised-rate
stretch. The tower at a moment stands with no shift; the **cost to rebuild it elsewhere** is the
shift per ROI it takes to build one as tall at a typical other moment of the same period, in
seconds. A tall tower in a raised-rate stretch is cheap to rebuild a few seconds away, and a
coordinated event is not. A moment is called when that cost reaches a threshold and at least
:data:`MINIMUM_ROIS` stand.

⚠ **Still a prototype.** The threshold is unchosen, and nothing has been run on a bench or on a
recording. An event of few ROIs in a busy period is cheap to rebuild however tightly its onsets
sit, so this rule does not find it.

Self-contained like ``stack``: numpy and the standard library only
(``tests/test_stack_ceiling.py`` fails on an import from the package).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class StackCeiling:
    """Per moment in ``centres``: the height, the ceiling and what lies between them."""

    centres: np.ndarray
    height: np.ndarray
    """Distinct ROIs with an onset within ``width_sec / 2`` of the moment."""
    ceiling: np.ndarray
    """Distinct ROIs with an onset within ``period_sec / 2`` of the moment: the tallest stack
    independent circular shifts of the period can build."""
    fill: np.ndarray
    """``height / ceiling``; 0 where the period holds no onset."""
    half_shift_sec: np.ndarray
    """The smallest shift per ROI at which the tower reaches half the ceiling (rounded up); 0
    when the unshifted height is already there, ``nan`` where the period holds no onset."""
    shift_needed: np.ndarray
    """``(n_centres, n_roi)``: how far each ROI's nearest onset is from the window, ``inf`` for an
    ROI with no onset in the period."""
    width_sec: float
    period_sec: float


def onset_gaps(trains, centres, period_sec: float) -> np.ndarray:
    """``(n_centres, n_roi)``: the distance from each moment to each ROI's nearest onset, ``inf``
    when that onset is more than ``period_sec / 2`` away (the ROI has none in the period)."""
    centres = np.atleast_1d(np.asarray(centres, float))
    gaps = np.full((centres.size, len(trains)), np.inf)
    for r, train in enumerate(trains):
        v = np.sort(np.asarray(train, float))
        v = v[np.isfinite(v)]
        if not v.size:
            continue
        i = np.searchsorted(v, centres)
        before = np.abs(centres - v[np.clip(i - 1, 0, v.size - 1)])
        after = np.abs(v[np.clip(i, 0, v.size - 1)] - centres)
        gaps[:, r] = np.minimum(before, after)
    gaps[gaps > period_sec / 2.0] = np.inf
    return gaps


def stack_ceiling(trains, centres, *, width_sec: float, period_sec: float) -> StackCeiling:
    """Height, ceiling, fill and growth curve at each moment in ``centres``.

    A window edge that lands exactly on an onset is a tie the caller should avoid: with onsets on
    a frame grid, put ``centres`` half a frame off it.
    """
    if not 0 < width_sec <= period_sec:
        raise ValueError("need 0 < width_sec <= period_sec")
    centres = np.atleast_1d(np.asarray(centres, float))
    gaps = onset_gaps(trains, centres, period_sec)
    need = np.maximum(gaps - width_sec / 2.0, 0.0)
    height = (need == 0).sum(axis=1)
    ceiling = np.isfinite(need).sum(axis=1)
    fill = np.divide(height, ceiling, out=np.zeros(centres.size), where=ceiling > 0)
    half = np.full(centres.size, np.nan)
    if need.shape[1]:
        ordered = np.sort(need, axis=1)
        k = np.ceil(ceiling / 2.0).astype(int)
        has = ceiling > 0
        half[has] = ordered[has, k[has] - 1]
    return StackCeiling(centres=centres, height=height, ceiling=ceiling, fill=fill,
                        half_shift_sec=half, shift_needed=need, width_sec=float(width_sec),
                        period_sec=float(period_sec))


MINIMUM_ROIS = 3
"""The fewest ROIs a call may stand on. ADR-0008, decision 1: a pair never counts as a
coordinated event. Copied because this module imports nothing from the package;
``tests/test_stack_ceiling.py`` checks it against ``bugarach.event_floor.MINIMUM_ROIS``."""

SCORES = ("rebuild", "fill")


def rebuild_cost(r: StackCeiling, *, stride: int = 5) -> np.ndarray:
    """Per moment, the shift per ROI it takes to build a tower as tall as the one standing there
    at a **typical other moment of the same period**, in seconds. 0 where nothing stands.

    The tower at a moment stands without any shift. Elsewhere in the period a tower of the same
    height ``H`` has to be built, and the shift that takes at a moment ``u`` is the ``H``-th
    smallest shift needed there (the growth curve at ``u``, read at ``H``). This is the median of
    that over the other moments of the period, taking every ``stride``-th moment and leaving out
    those whose window would overlap the tower. A tower that is as easy to build anywhere, as in a
    stretch where every ROI's rate is raised, costs little; one whose ROIs are otherwise far
    apart costs a lot. Where the period cannot reach ``H`` ROIs at ``u`` at all, the cost there
    is the most a shift can be, half the period.

    ⚠ It saturates. When a tower holds most of the period's ROIs, the nearest onset of each at
    another moment is the tower itself, so the cost is the typical distance back to it: about a
    quarter of the period, whatever the tower's height.

    ``r.centres`` must be evenly spaced.
    """
    centres = r.centres
    n = centres.size
    out = np.zeros(n)
    if n < 2:
        return out
    dt = float(centres[1] - centres[0])
    half_period = int(round(r.period_sec / 2.0 / dt))
    apart = max(int(round(r.width_sec / dt)), 1)
    ordered = np.minimum(np.sort(r.shift_needed, axis=1), r.period_sec / 2.0)
    for i in np.flatnonzero(r.height > 0):
        lo = max(0, i - half_period)
        j = np.arange(lo + (-lo) % stride, min(n - 1, i + half_period) + 1, stride)
        j = j[np.abs(j - i) >= apart]
        if j.size:
            out[i] = np.median(ordered[j, r.height[i] - 1])
    return out


def call_moments(r: StackCeiling, score: np.ndarray, threshold: float, *,
                 min_rois: int = MINIMUM_ROIS, merge_gap_sec: float = 0.5):
    """Calls as ``(start_sec, end_sec, peak_sec)`` rows: runs of moments whose ``score`` is at
    least ``threshold`` and whose height is at least ``min_rois``, joined across gaps of at most
    ``merge_gap_sec``. ``peak_sec`` is the run's tallest moment (the first, on a tie).

    A prototype rule: the threshold is a setting nobody has chosen.
    """
    on = np.flatnonzero((score >= threshold - 1e-9) & (r.height >= min_rois))
    if not on.size:
        return np.empty((0, 3))
    t = r.centres[on]
    breaks = np.flatnonzero(np.diff(t) > merge_gap_sec + 1e-9) + 1
    rows = []
    for run in np.split(on, breaks):
        peak = run[np.argmax(r.height[run])]
        rows.append((r.centres[run[0]], r.centres[run[-1]], r.centres[peak]))
    return np.asarray(rows, float)


@dataclass
class StackCeilingDetection:
    """Calls as parallel arrays, under the field names every other detector's result uses."""

    onset_sec: np.ndarray
    """Where the call's first called window begins."""
    width_sec: np.ndarray
    """From there to the end of its last called window."""
    strength: np.ndarray
    """The cost to rebuild the call's tallest tower elsewhere, in seconds."""
    nrois: np.ndarray
    """The height of that tower."""
    opts: dict

    @property
    def n_events(self) -> int:
        return int(self.onset_sec.size)


def frame_centres(t_range, frame_interval_sec: float) -> np.ndarray:
    """Every moment of ``t_range`` half a frame off the frame grid, so that with onsets on the
    grid no window edge lands on one."""
    lo, hi = float(t_range[0]), float(t_range[1])
    n = int(np.floor((hi - lo) / frame_interval_sec + 1e-9))
    return lo + (np.arange(n) + 0.5) * frame_interval_sec


def detection_from(r: StackCeiling, cost: np.ndarray, *, threshold_sec: float, min_rois: int,
                   merge_gap_sec: float) -> StackCeilingDetection:
    """The calls at one threshold, from a measure already computed. A search over thresholds
    computes :func:`stack_ceiling` and :func:`rebuild_cost` once and calls this for each."""
    calls = call_moments(r, cost, threshold_sec, min_rois=min_rois, merge_gap_sec=merge_gap_sec)
    peak = np.searchsorted(r.centres, calls[:, 2]) if len(calls) else np.empty(0, int)
    peak = np.clip(peak, 0, max(r.centres.size - 1, 0))
    return StackCeilingDetection(
        onset_sec=calls[:, 0] - r.width_sec / 2.0,
        width_sec=calls[:, 1] - calls[:, 0] + r.width_sec,
        strength=cost[peak].astype(float), nrois=r.height[peak].astype(int),
        opts=dict(width_sec=r.width_sec, period_sec=r.period_sec, threshold_sec=threshold_sec,
                  min_rois=int(min_rois), merge_gap_sec=merge_gap_sec))


def stack_ceiling_detect(trains, t_range, *, min_rois: int, frame_interval_sec: float,
                         threshold_sec: float, width_sec: float = 2.0,
                         period_sec: float = 120.0, merge_gap_sec: float = 0.5,
                         stride: int = 5) -> StackCeilingDetection:
    """Call the moments whose tower is costly to rebuild elsewhere in its period.

    ``min_rois`` is required, as in ``stack``: the recording's ADR-0008 floor, never under
    :data:`MINIMUM_ROIS`. ``threshold_sec`` has no default because nobody has chosen one.
    """
    if min_rois < MINIMUM_ROIS:
        raise ValueError(f"min_rois must be at least {MINIMUM_ROIS} (ADR-0008, decision 1)")
    r = stack_ceiling(trains, frame_centres(t_range, frame_interval_sec), width_sec=width_sec,
                      period_sec=period_sec)
    return detection_from(r, rebuild_cost(r, stride=stride), threshold_sec=threshold_sec,
                          min_rois=min_rois, merge_gap_sec=merge_gap_sec)


def expected_height(trains, centre: float, *, period_sec: float, radii_sec) -> np.ndarray:
    """The mean number of ROIs within each of ``radii_sec`` of a moment when every ROI's onsets
    in the period around ``centre`` are circularly shifted by an independent, uniform amount.

    Exact. A shifted ROI lands within ``r`` of the moment when the shift falls in the union of the
    arcs of half-length ``r`` around its onsets, so its chance is that union's share of the circle.
    """
    radii = np.atleast_1d(np.asarray(radii_sec, float))
    lo = centre - period_sec / 2.0
    out = np.zeros(radii.size)
    for train in trains:
        v = np.asarray(train, float)
        v = np.sort(v[(v >= lo) & (v < lo + period_sec)])
        if not v.size:
            continue
        spacing = np.diff(np.append(v, v[0] + period_sec))
        out += np.minimum(spacing[None, :], 2.0 * radii[:, None]).sum(axis=1) / period_sec
    return out
