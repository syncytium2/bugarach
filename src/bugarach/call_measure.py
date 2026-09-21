"""One yardstick for every detector's calls: width and amplitude from the member events.

**Why this exists.** Each detector reports a call's width by its own rule — a supra-threshold
span, an episode, a half-prominence extent, an onset spread floored at a window — so the
``width_sec`` column in ``detections.csv`` means six different things and cannot be compared
across detectors. locust made that concrete: on the 2026-09-09 full-cohort run every one of its
4,958 senktide calls had ``width_sec = 0.3``, its window floor, and a lab figure plotted that
constant as "event width" for four groups and two conditions.

**The concept** (Tony, 2026-07-22 for interface2, and 2026-09-21 for this build: *"take the
concept for width and amp and build our own"*): the detector decides WHERE a coordinated event
is; this module decides HOW WIDE and HOW STRONG it is, from the recording's own calcium events —
"coordination begins at the first event onset and ends at the last event onset within the
coordination window". Nothing here reads the detector's width, so the same moment measures the
same whichever detector called it.

**How.** Around each call's centre, an aperture of the same size for every detector collects
every cell's events whose onset (the producer's t50rise) falls inside it. The onsets are sorted
and split wherever consecutive onsets are more than ``gap_sec`` apart; the **core** is the group
holding the most distinct cells, so one straggler at the edge of the aperture does not stretch
the width. From the core:

- ``core_span_sec`` — last onset minus first: **the width of the coordinated event**
- ``core_n_roi`` — distinct cells in it
- ``amplitude`` — **the amplitude of the coordinated event**: ``core_n_roi`` divided by its
  width, ``core_span_sec``, in cells per second. Tony, 2026-09-21: *"shouldn't amplitude be
  number of ROIs / width of the coordinated event. reader sees 14 cells participating and
  1.6 s width, then 130 cells/s makes no sense"* — so a reader can check it from the two
  columns beside it. (The first draft divided by the mean interval between onsets, which is
  roughly cells² over width and matched neither column.) The width is floored at the
  recording's frame interval: onsets in one frame are as close as the recording can tell
  apart, and a zero would divide to infinity. A single cell is not coordination, so its
  amplitude is NaN. What it measures is **packing**: at a steady spacing a bigger event is
  also a wider one, so the cell count is its own column and not folded in here.
- ``member_amp_median`` — the member calcium events' own amplitude, in the producer's units
  (the export's ``amp``). **Not the amplitude above**, and named so it cannot be mistaken
  for it.
- ``member_width_median`` — the member events' own widths, under the producer's rule
  (``width_def``), when the folder sent one

and from everything in the aperture, ``span_sec`` (the honest full extent, stragglers included)
and ``peak_coactivity`` (the most distinct cells with onsets inside any ``gap_sec`` window —
how tight the vertical line in the raster is).

**Built from the concept, not ported.** interface2's ``characterize_coord_window.m`` did this
first; this is a fresh implementation and matches none of its numbers on purpose. One deliberate
difference: the core is chosen by **distinct cells**, not by onset count, because coordination
is about cells — one cell firing four times is not four cells.

**The two lengths per stream are judgements, not measurements.** Fast: gap 0.5 s, aperture
±1.0 s. Slow: gap 2.5 s, aperture ±5.0 s — the slow stream's events are about five times
slower, so both scale by five. They are parameters, recorded in every output, and a sweep over
them is the way to show a result does not hang on them.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

#: Per-stream (gap_sec, half_aperture_sec). A judgement — see the module docstring.
DEFAULTS = {"fast": (0.5, 1.0), "slow": (2.5, 5.0)}


@dataclass(frozen=True)
class CallMeasure:
    """What one call's member events say about it. NaN where there is nothing to measure."""

    n_events: int                 # events with an onset in the aperture, every cell
    n_roi: int                    # distinct cells among them
    span_sec: float               # last minus first onset, everything in the aperture
    core_n_events: int
    core_n_roi: int
    core_first_sec: float
    core_span_sec: float          # THE width: last minus first onset of the core
    amplitude: float              # THE amplitude: core_n_roi / core_span_sec (floored), cells/s
    member_amp_median: float      # the member calcium events' own amp — not `amplitude`
    member_width_median: float
    peak_coactivity: int          # most distinct cells with onsets inside any gap_sec window
    gap_sec: float
    half_aperture_sec: float
    min_interval_sec: float

    def row(self) -> dict:
        return asdict(self)


def defaults_for(stream_name: str) -> tuple[float, float]:
    """(gap_sec, half_aperture_sec) for a stream, by name; fast's for an unknown name."""
    return DEFAULTS.get(str(stream_name).strip().lower(), DEFAULTS["fast"])


def _collect(stream, lo: float, hi: float):
    """(onset, roi, amp, member width) for every event with lo <= onset <= hi."""
    on, roi, amp, wid = [], [], [], []
    for r, times in enumerate(stream.locs):
        t = np.asarray(times, dtype=float)
        if t.size == 0:
            continue
        keep = (t >= lo) & (t <= hi)
        if not keep.any():
            continue
        on.append(t[keep])
        roi.append(np.full(int(keep.sum()), r))
        a = np.asarray(stream.amp[r], dtype=float) if stream.amp is not None else None
        amp.append(a[keep] if a is not None and a.size == t.size else np.full(int(keep.sum()), np.nan))
        w = np.asarray(stream.width[r], dtype=float) if stream.width is not None else None
        ok_w = stream.width_def is not None and w is not None and w.size == t.size
        wid.append(w[keep] if ok_w else np.full(int(keep.sum()), np.nan))
    if not on:
        e = np.array([])
        return e, e.astype(int), e, e
    on, roi, amp, wid = (np.concatenate(x) for x in (on, roi, amp, wid))
    order = np.argsort(on, kind="stable")
    return on[order], roi[order], amp[order], wid[order]


def _groups(onsets: np.ndarray, gap_sec: float) -> list[slice]:
    """Split sorted onsets wherever consecutive ones are more than gap_sec apart."""
    if onsets.size == 0:
        return []
    cuts = np.flatnonzero(np.diff(onsets) > gap_sec) + 1
    edges = np.concatenate(([0], cuts, [onsets.size]))
    return [slice(int(a), int(b)) for a, b in zip(edges[:-1], edges[1:])]


def _peak_coactivity(onsets: np.ndarray, rois: np.ndarray, window: float) -> int:
    """Most distinct cells with onsets inside any window of length ``window``."""
    best, j = 0, 0
    for i in range(onsets.size):
        while onsets[i] - onsets[j] > window:
            j += 1
        best = max(best, len(set(rois[j:i + 1].tolist())))
    return best


def _nan_stat(fn, x: np.ndarray) -> float:
    x = x[np.isfinite(x)]
    return float(fn(x)) if x.size else float("nan")


def measure_call(stream, center_sec: float, *, gap_sec: float, half_aperture_sec: float,
                 min_interval_sec: float, window: tuple[float, float] | None = None
                 ) -> CallMeasure:
    """Measure one call from the member events of ``stream`` around ``center_sec``.

    ``stream`` is a :class:`bugarach.store.Stream`; ``locs`` must be the event onsets (an export
    folder's ``time_sec``, the t50rise). ``min_interval_sec`` is the recording's frame interval,
    the floor under the width when the amplitude divides by it. Raises on a non-positive length.

    **Where to look** is ``center_sec ± half_aperture_sec``, widened to cover ``window`` — the
    call's own span, when the detector reported one. The first version looked only at the
    aperture, and on binned SCE's 10 s bins the cluster can sit up to 5 s from the bin's centre:
    166 of 834 fast calls on the 2026-09-09 senktide run measured a single cell. Widening where
    to look does not widen the measurement — the gap rule still decides which onsets are in the
    coordinated event, and the width runs from its earliest onset to its last.
    """
    if not (gap_sec > 0 and half_aperture_sec > 0 and min_interval_sec > 0):
        raise ValueError(f"gap_sec, half_aperture_sec and min_interval_sec must be positive "
                         f"(got {gap_sec}, {half_aperture_sec}, {min_interval_sec})")
    lo, hi = center_sec - half_aperture_sec, center_sec + half_aperture_sec
    if window is not None and all(np.isfinite(window)) and window[1] >= window[0]:
        lo, hi = min(lo, float(window[0])), max(hi, float(window[1]))
    on, roi, amp, wid = _collect(stream, lo, hi)
    nan = float("nan")
    if on.size == 0:
        return CallMeasure(0, 0, nan, 0, 0, nan, nan, nan, nan, nan, 0,
                           gap_sec, half_aperture_sec, min_interval_sec)
    groups = _groups(on, gap_sec)
    # Most distinct cells; ties to more events, then to the group nearest the centre.
    core = max(groups, key=lambda g: (len(set(roi[g].tolist())), g.stop - g.start,
                                      -abs(float(np.mean(on[g])) - center_sec)))
    c_on = on[core]
    core_n_roi = len(set(roi[core].tolist()))
    span = float(c_on[-1] - c_on[0])
    # One cell is not coordination; otherwise cells over the width, floored at one frame.
    amplitude = nan if core_n_roi < 2 else core_n_roi / max(span, min_interval_sec)
    return CallMeasure(
        n_events=int(on.size),
        n_roi=len(set(roi.tolist())),
        span_sec=float(on[-1] - on[0]),
        core_n_events=int(c_on.size),
        core_n_roi=core_n_roi,
        core_first_sec=float(c_on[0]),
        core_span_sec=span,
        amplitude=amplitude,
        member_amp_median=_nan_stat(np.median, amp[core]),
        member_width_median=_nan_stat(np.median, wid[core]),
        peak_coactivity=_peak_coactivity(on, roi, gap_sec),
        gap_sec=gap_sec,
        half_aperture_sec=half_aperture_sec,
        min_interval_sec=min_interval_sec,
    )


def call_center(onset_sec: float, width_sec: float | None) -> float:
    """The call's centre: onset plus half its detector-reported width, or the onset.

    The centre anchors the aperture and nothing else — the aperture is wide enough that
    where a detector puts its onset (start, peak or middle) moves the collection little.
    """
    if width_sec is None or not np.isfinite(width_sec) or width_sec < 0:
        return float(onset_sec)
    return float(onset_sec) + float(width_sec) / 2.0
