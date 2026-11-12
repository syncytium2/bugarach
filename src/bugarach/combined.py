"""The combined stream, as the export ships it. bugarach reads it and never builds it.

The lab has three streams: fast, slow and combined. The combined stream holds every fast and
every slow event of a ROI, nothing de-duplicated (Tony, 2026-09-22), and **the producer makes
it** (ADR-0023). Each of its rows names the stream the event came from in the export's
``source_stream`` column; the loader keeps that as ``Stream.label``, in the same per-ROI order
as ``locs``, for the two-ink raster. Detectors never read it.

Until 2026-11-12 this module merged fast and slow itself (``combine``). That is gone. A
recording whose export has no combined stream has none here, and asking for it is refused:
what is missing from an export is a request to the producer.

**Detectors never see ``COMBINED`` beside ``fast`` and ``slow``.** LoCo, CICADA and SCE draw
their surrogates for every stream in ``slice.streams`` from one generator, so a third entry
would change the fast and slow draws. :func:`only_combined` and :func:`without_combined`
split a three-stream recording for them; ``detect_slice`` does this itself.
"""
from __future__ import annotations

from dataclasses import replace

import numpy as np

from .store import Slice, Stream

COMBINED = "combined"


def has_combined(s: Slice) -> bool:
    """Did the export ship a combined stream for this recording?"""
    return COMBINED in s.streams


def stream_of(s: Slice, name: str) -> Stream:
    """``s.streams[name]``, with the refusal written for a combined stream that was not shipped."""
    if name == COMBINED and COMBINED not in s.streams:
        raise KeyError(f"{s.slice_id}: this export carries {sorted(s.streams)} and no combined "
                       f"stream. bugarach does not build one (ADR-0023); the producer ships it "
                       f"(docs/export_folder_spec.md, the combined stream)")
    return s.streams[name]


def only_combined(s: Slice) -> Slice:
    """The same recording carrying the combined stream and nothing else — what detectors see."""
    return replace(s, streams={COMBINED: stream_of(s, COMBINED)})


def without_combined(s: Slice) -> Slice:
    """The same recording without its combined stream — what detectors see for fast and slow."""
    return replace(s, streams={k: v for k, v in s.streams.items() if k != COMBINED})


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
