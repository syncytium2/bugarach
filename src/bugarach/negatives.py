"""Rate-matched negatives: a recording's own channels, with the alignment between them destroyed.

**What it is for.** Scoring a detector's false calls. A negative is a recording that keeps what
chance is allowed to explain and holds no coordination, so every call on it is a false alarm
(``docs/adr/0006-a-false-alarm-is-coincidence-the-event-rates-explain.md``, decisions 1 and 3).
The decoys that used to play this part were coordination by construction and are retired
(``docs/adr/0019-the-decoys-are-retired-negatives-are-rate-matched.md``); that record asks for
this as a tool of the general toolset, tied to no bench and to no lab's export.

**The input** is the general one
(``docs/adr/0021-the-toolset-is-validated-on-synthetic-data-first-with-coded-detectors.md``,
decision 2): onset times in seconds for each channel, and the recording's duration. No labels, no
frame interval, no export folder. Simulated and real recordings go through the same call.

**The construction** is the per-channel rigid shift. Every channel's whole train is moved by one
offset of its own, uniform in ±``j_sec``:

* **kept:** each channel's event count and every interval between its own events, so its rate and
  its own timing; and any change in rate that the channels share over spans much longer than
  ``j_sec``, because a shift of seconds moves a minute-long rise by seconds;
* **destroyed:** which channels are active within a second or two of each other.

It is the null the event floor already uses (:func:`bugarach.event_floor.rigid_frames` with
``shared=False``, at ``j_sec`` = 20 s). That one works on frame indices for one fixed purpose;
this one works on seconds so it needs no frame interval. The two are the same construction and
are not draw-for-draw identical.

**The edges.** An onset moved past either end of the recording is dropped, not wrapped: wrapping
would lay the end of a recording over its start. So the first and last ``j_sec`` of a negative
are thinned, and scoring should read :attr:`Negative.valid_window`, where every original onset
is still present.

**What a negative of a recording with coordinated events still holds.** Every one of those
onsets, scattered. Its channels are therefore busier than the true background, which makes a
false-call rate measured on it too high, never too low
(``docs/adr/0008-the-event-floor-is-set-per-window-from-its-own-null.md``, consequences). On
simulated data the size of that excess can be measured against a recording with nothing planted.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from bugarach.event_floor import J_SEC

__all__ = ["Negative", "rate_matched_negative", "rate_matched_negatives"]


@dataclass(frozen=True)
class Negative:
    """One rate-matched negative of a recording."""

    times: tuple[np.ndarray, ...]
    """Onset times in seconds, one sorted array per channel, in the input's channel order."""
    duration_sec: float
    offsets_sec: tuple[float, ...]
    """The shift applied to each channel, seconds."""
    j_sec: float
    seed: int
    dropped: int
    """Onsets moved past either end of the recording and dropped, over all channels."""

    @property
    def valid_window(self) -> tuple[float, float]:
        """``(start, end)`` in seconds where no onset can have been dropped or be missing."""
        return (self.j_sec, self.duration_sec - self.j_sec)


def _checked(times, duration_sec: float, j_sec: float) -> list[np.ndarray]:
    if not np.isfinite(duration_sec) or duration_sec <= 0:
        raise ValueError(f"duration_sec must be a positive number of seconds, got {duration_sec!r}")
    if not np.isfinite(j_sec) or j_sec <= 0:
        raise ValueError(f"j_sec must be a positive number of seconds, got {j_sec!r}")
    if 2 * j_sec >= duration_sec:
        raise ValueError(
            f"a shift of ±{j_sec:g} s leaves nothing of a {duration_sec:g} s recording to score: "
            f"the valid window is the recording less {j_sec:g} s at each end")
    out = []
    for c, t in enumerate(times):
        a = np.sort(np.asarray(t, dtype=float).ravel())
        if a.size and (not np.all(np.isfinite(a)) or a[0] < 0 or a[-1] > duration_sec):
            raise ValueError(f"channel {c} has an onset outside 0 to {duration_sec:g} s, "
                             f"or one that is not a number")
        out.append(a)
    if not out:
        raise ValueError("a recording needs at least one channel")
    return out


def _shift(trains: list[np.ndarray], duration_sec: float, j_sec: float, rng, seed: int) -> Negative:
    offsets = rng.uniform(-j_sec, j_sec, size=len(trains))
    moved, dropped = [], 0
    for a, u in zip(trains, offsets):
        b = a + u
        keep = (b >= 0.0) & (b < duration_sec)
        dropped += int(a.size - keep.sum())
        moved.append(b[keep])
    return Negative(times=tuple(moved), duration_sec=float(duration_sec),
                    offsets_sec=tuple(float(u) for u in offsets), j_sec=float(j_sec),
                    seed=int(seed), dropped=dropped)


def rate_matched_negative(times, duration_sec: float, *, seed: int,
                          j_sec: float = J_SEC) -> Negative:
    """One negative of a recording: each channel's train moved by its own offset in ±``j_sec``.

    ``times`` is one array of onset times (seconds) per channel. ``seed`` is required: a negative
    is part of a score, and a score has to be reproducible.
    """
    trains = _checked(times, duration_sec, j_sec)
    return _shift(trains, duration_sec, j_sec, np.random.RandomState(int(seed)), seed)


def rate_matched_negatives(times, duration_sec: float, n: int, *, seed: int,
                           j_sec: float = J_SEC) -> list[Negative]:
    """``n`` negatives of one recording, each from its own stream of draws.

    Negative ``i`` is :func:`rate_matched_negative` at ``seed + i``, so any one of them can be
    made again by itself.
    """
    if n < 1:
        raise ValueError(f"n must be at least 1 negative, got {n!r}")
    trains = _checked(times, duration_sec, j_sec)
    return [_shift(trains, duration_sec, j_sec, np.random.RandomState(int(seed) + i), int(seed) + i)
            for i in range(int(n))]
