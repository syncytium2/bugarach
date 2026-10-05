"""The combined stream: every fast and every slow onset of a ROI, as one train, labelled.

Tony, 2026-09-22: *"the pipeline fed the onsets of both fast and slow as a single stream
preserving the event labels for later plotting"* — measured, simulated, searched and drawn
exactly as fast and slow are, giving a third parameter set.

**The merge keeps every onset.** Nothing is dropped as a duplicate: whether a slow onset near a
fast one is the same event is goal 4's open question
(``docs/goals/combined-stream-coordination.md``), and deduplicating would answer it by
construction. ``tools/measure_coordination_rates.merge_streams`` drops a slow onset within one
frame of a fast one; that was a report-only assumption and is not this stream.
:func:`near_coincident` counts how often the question arises, so the record can say.

``label`` carries each onset's source stream in the same per-ROI order as ``locs``, for the
two-ink raster. Detectors never read it.

**Never add ``COMBINED`` to a ``Slice`` beside ``fast`` and ``slow``.** LoCo, CICADA and SCE draw
their surrogates for every stream in ``slice.streams`` from one generator, so a third entry
would change the fast and slow draws. Use :func:`only_combined` to run detectors, and
:func:`stream_of` to read one stream by name.
"""
from __future__ import annotations

from dataclasses import replace

import numpy as np

from .store import Slice, Stream

COMBINED = "combined"
SOURCES = ("fast", "slow")


def _cat(a: np.ndarray, b: np.ndarray, order: np.ndarray) -> np.ndarray:
    return np.concatenate([np.asarray(a, float), np.asarray(b, float)])[order]


def combine(fast: Stream, slow: Stream) -> Stream:
    """One stream holding both, per ROI sorted by onset, with each event's source in ``label``."""
    if fast.n_rois != slow.n_rois:
        raise ValueError(f"fast has {fast.n_rois} ROIs and slow {slow.n_rois}; a ROI is one "
                         f"cell in both streams (FOUNDATIONS §9), so they must agree")
    cols: dict[str, list[np.ndarray]] = {k: [] for k in ("locs", "amp", "width", "t50rise")}
    peak: list[np.ndarray] | None = [] if (fast.has_peak and slow.has_peak) else None
    label: list[np.ndarray] = []
    # One stream's field per line, on purpose: sapper SAP012 reads two event-time fields on
    # one line as a duration being derived, and nothing here derives one — each field is
    # concatenated with the SAME field of the other stream, in one shared order.
    for i in range(fast.n_rois):
        f_on = np.asarray(fast.t50rise[i], float)
        s_on = np.asarray(slow.t50rise[i], float)
        order = np.argsort(np.concatenate([f_on, s_on]), kind="stable")
        for k in cols:
            cols[k].append(_cat(getattr(fast, k)[i], getattr(slow, k)[i], order))
        if peak is not None:
            f_pk = fast.peak[i]
            s_pk = slow.peak[i]
            peak.append(_cat(f_pk, s_pk, order))
        label.append(np.array(["fast"] * f_on.size + ["slow"] * s_on.size,
                              dtype=object)[order])
    width_def = None
    if fast.has_width and slow.has_width:
        # Each event keeps its own stream's width rule; ``label`` says which applies.
        width_def = f"per-event by label: fast={fast.width_def}; slow={slow.width_def}"
    return Stream(**cols, width_def=width_def, peak=peak, label=label)


def has_sources(s: Slice) -> bool:
    return all(k in s.streams for k in SOURCES)


def stream_of(s: Slice, name: str) -> Stream:
    """``s.streams[name]``, building the combined stream on demand when it is asked for."""
    if name == COMBINED and COMBINED not in s.streams:
        if not has_sources(s):
            raise KeyError(f"{s.slice_id}: the combined stream needs both fast and slow; "
                           f"this recording has {sorted(s.streams)}")
        return combine(s.streams["fast"], s.streams["slow"])
    return s.streams[name]


def only_combined(s: Slice) -> Slice:
    """The same recording carrying the combined stream and nothing else — what detectors see."""
    return replace(s, streams={COMBINED: stream_of(s, COMBINED)})


def near_coincident(fast: Stream, slow: Stream, tol_sec: float) -> tuple[int, int]:
    """(slow onsets within ``tol_sec`` of a fast onset on the same ROI, all slow onsets)."""
    near = total = 0
    f_rows = fast.t50rise
    s_rows = slow.t50rise
    for f, sl in zip(f_rows, s_rows):
        sl = np.asarray(sl, float)
        total += sl.size
        f = np.sort(np.asarray(f, float))
        if not f.size or not sl.size:
            continue
        j = np.searchsorted(f, sl)
        left = f[np.clip(j - 1, 0, f.size - 1)]
        right = f[np.clip(j, 0, f.size - 1)]
        d = np.minimum(np.abs(sl - left), np.abs(sl - right))
        near += int((d <= tol_sec).sum())
    return near, total
