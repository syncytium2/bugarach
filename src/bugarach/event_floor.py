"""Each window's event floor: the larger of 3 ROIs and that window's own chance floor (ADR-0008).

**What it answers.** How many ROIs must be active together, inside one window, for a moment to count
as a coordinated event. ADR-0006 says what counts as chance: coincidence the ROIs' own event rates
explain, rates that change together included. ADR-0008 turns that into a number per window:

* the **chance floor** is the smallest count *K* of co-active ROIs whose calls, under the per-ROI
  rigid shift, come to at most :data:`FA_PER_HOUR` per hour of the window;
* the **event floor** is ``max(MINIMUM_ROIS, chance floor)``. 3 is a stated choice, so that a pair
  never counts as a coordinated event.

**The method** is the one ``tools/measure_chance_floor.py`` measured on the 66 recordings (#790),
and that tool now calls this module rather than holding its own copy:

* co-activity is the number of ROIs with at least one onset in a sliding :data:`WINDOW_SEC` window;
* the null is :func:`rigid_frames` with ``shared=False``: every ROI's train slid by its own offset,
  uniform in ±:data:`J_SEC`, onsets pushed past either end dropped. It keeps each ROI's rate, its own
  timing and the minute-scale shared change, and destroys the alignment between ROIs;
* a call at *K* is one unbroken run of window positions with at least *K* co-active ROIs;
* the real window and every null draw are read on the window trimmed by *J* at both ends, so no
  onset the shift pushed out enters;
* at least :data:`MIN_DRAWS` draws, and the floor from each half of the draws is reported beside the
  full one (:attr:`Floor.stable`).

**Every setting here is ADR-0008's**, and changing one takes a new ADR that supersedes it.

**Treatment windows** are scored under two floors (ADR-0008, decision 4): the window's own, and the
same recording's baseline floor carried over. :func:`treatment_floors` pairs them; on a baseline
window they are the same number.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass

import numpy as np

MINIMUM_ROIS = 3
"""The absolute minimum: a pair never counts as a coordinated event (ADR-0008, decision 1)."""
WINDOW_SEC = 2.0
"""Co-activity window, seconds: CoactDetect's ``int_win_sec`` when the floor was measured."""
J_SEC = 20.0
"""The rigid shift's half-width, seconds (ADR-0006, decision 3; ADR-0008, decision 2)."""
FA_PER_HOUR = 1.0
"""Null calls per hour of window at or below which a count is past chance."""
MIN_DRAWS = 1000
"""Rigid-shift draws per window; the floor is stable to 1 ROI at this many on the 66 (#790)."""


def rigid_frames(trains, L, J_frames, rng, shared=False):
    """Each train moved by an offset uniform in ``[-J_frames, J_frames)``, one per ROI unless
    ``shared``; frame ``k`` goes to ``floor(k + 0.5 + u)`` and onsets outside ``[0, L)`` are dropped.

    Moved here from ``tools/tube_self_supervised.py`` (which now imports it) so the package can
    compute a floor without reaching into a tool. Same arithmetic, same draws for the same ``rng``.
    """
    u_all = rng.uniform(-J_frames, J_frames, size=1 if shared else len(trains))
    out = []
    for r, t in enumerate(trains):
        u = u_all[0] if shared else u_all[r]
        k = np.floor(np.asarray(t, float) + 0.5 + u).astype(np.int64)
        out.append(k[(k >= 0) & (k < L)])
    return out


def coactive_counts(trains, L: int, wf: int) -> np.ndarray:
    """ROIs with at least one onset in frames ``[s, s + wf)``, for every start ``s`` in
    ``0 .. L - wf``. ``trains`` are onset frames; anything outside ``[0, L)`` is ignored."""
    n_pos = L - wf + 1
    if n_pos <= 0:
        return np.zeros(0, np.int64)
    out = np.zeros(n_pos, np.int64)
    for t in trains:
        t = np.asarray(t, np.int64)
        t = t[(t >= 0) & (t < L)]
        if not t.size:
            continue
        cs = np.concatenate([[0], np.cumsum(np.bincount(t, minlength=L))])
        out += (cs[wf:wf + n_pos] - cs[:n_pos]) > 0
    return out


def exceedances(counts: np.ndarray, n_max: int) -> tuple[np.ndarray, np.ndarray]:
    """``(runs, frames)`` for every threshold ``K = 0 .. n_max + 1``.

    ``runs[K]``: maximal runs of positions with ``count >= K`` (one call per run).
    ``frames[K]``: positions with ``count >= K``.
    """
    size = n_max + 2
    c = np.minimum(np.asarray(counts, np.int64), n_max)
    frames = np.cumsum(np.bincount(c, minlength=size)[::-1])[::-1].astype(float)
    prev = np.concatenate([[0], c[:-1]])
    rise = c > prev
    diff = np.zeros(size + 1)
    np.add.at(diff, prev[rise] + 1, 1.0)
    np.add.at(diff, c[rise] + 1, -1.0)
    runs = np.cumsum(diff)[:size]
    runs[0] = 1.0 if c.size else 0.0
    return runs, frames


def floor_of(per_hour, budget: float) -> int:
    """Smallest ``K >= 1`` whose rate per hour is at most ``budget``; one more than any ROI count
    when none is."""
    ok = np.flatnonzero(np.asarray(per_hour)[1:] <= budget)
    return int(ok[0] + 1) if ok.size else int(len(per_hour) - 1)


@dataclass(frozen=True)
class Floor:
    """One window's floor and how it was reached. ``floor`` is what a detector and a scorer use."""
    floor: int
    chance_floor: int
    minimum: int
    n_roi: int
    draws: int
    first_half: int
    second_half: int
    analysed_hours: float
    window_sec: float
    j_sec: float
    fa_per_hour: float

    @property
    def stable(self) -> bool:
        """Both halves of the draws give the full-draw chance floor."""
        return self.first_half == self.second_half == self.chance_floor

    def as_dict(self) -> dict:
        return {**asdict(self), "stable": self.stable}


def null_curve(trains, n_frames: int, dt: float, *, key, draws: int = MIN_DRAWS,
               window_sec: float = WINDOW_SEC, j_sec: float = J_SEC):
    """The rigid-shift null's calls and frames per hour at every *K*, summed over each half of the
    draws: ``(runs[2, N+2], frames[2, N+2], hours, trimmed_trains, L, wf)``. Draw ``d`` goes to half
    ``d % 2``. ``key`` seeds every draw (``bugarach.surrogate_stats.rng_of((*key, "rigid", d))``)."""
    from bugarach import surrogate_stats as ss

    trim = int(math.ceil(j_sec / dt))
    L = n_frames - 2 * trim
    wf = max(1, int(round(window_sec / dt)))
    if L < wf:
        raise ValueError(f"window of {n_frames} frames is too short for J = {j_sec} s at "
                         f"dt = {dt} s and a {window_sec} s co-activity window")
    full = [np.asarray(t, np.int64) for t in trains]
    N = len(full)

    def trimmed(ts):
        return [t[(t >= trim) & (t < n_frames - trim)] - trim for t in ts]

    hours = (L - wf + 1) * dt / 3600.0
    runs = np.zeros((2, N + 2))
    frames = np.zeros((2, N + 2))
    for d in range(draws):
        rng = ss.rng_of((*key, "rigid", d))
        shifted = trimmed(rigid_frames(full, n_frames, j_sec / dt, rng, shared=False))
        r_, f_ = exceedances(coactive_counts(shifted, L, wf), N)
        runs[d % 2] += r_
        frames[d % 2] += f_
    return runs, frames, hours, trimmed(full), L, wf


def window_floor(trains, n_frames: int, dt: float, *, key, draws: int = MIN_DRAWS,
                 window_sec: float = WINDOW_SEC, j_sec: float = J_SEC,
                 fa_per_hour: float = FA_PER_HOUR, minimum: int = MINIMUM_ROIS) -> Floor:
    """ADR-0008's floor for one window.

    ``trains``: each ROI's onset frames, relative to the window's first frame; ``n_frames``: the
    window's length in frames; ``dt``: the frame interval in seconds (required, FOUNDATIONS §6);
    ``key``: a tuple naming the window, which seeds the null so the same window always gets the same
    floor. ``draws`` below :data:`MIN_DRAWS` is allowed for tests and smoke runs only.
    """
    if dt is None or not dt > 0:
        raise ValueError("dt is required and must be positive")
    runs, _, hours, _, _, _ = null_curve(trains, n_frames, dt, key=key, draws=draws,
                                         window_sec=window_sec, j_sec=j_sec)
    n = len(trains)
    chance = floor_of(runs.sum(axis=0) / (draws * hours), fa_per_hour)
    halves = [floor_of(runs[h] / (((draws + 1 - h) // 2) * hours), fa_per_hour) for h in (0, 1)]
    return Floor(floor=max(minimum, chance), chance_floor=chance, minimum=minimum, n_roi=n,
                 draws=draws, first_half=halves[0], second_half=halves[1],
                 analysed_hours=hours, window_sec=window_sec, j_sec=j_sec,
                 fa_per_hour=fa_per_hour)


def treatment_floors(own: Floor, baseline: Floor) -> dict:
    """The two floors a treatment window is scored under (ADR-0008, decision 4): its own, and the
    same recording's baseline floor carried over. On a baseline window pass the same floor twice."""
    return {"own": own.floor, "baseline": baseline.floor,
            "own_detail": own.as_dict(), "baseline_detail": baseline.as_dict()}
