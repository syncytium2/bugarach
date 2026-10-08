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

⚠ **Nothing here is a detector yet.** There is no rule that turns fill into a call, and nothing
has been run on a bench or on a recording. A shared rise in rate raises the height while the
ceiling stays put, so fill is not immune to it; and an event of few ROIs in a busy period has a
small fill however tightly its onsets sit.

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
