"""Generic data ingestion — the way IN for labs without event_store files.

The detectors need only per-ROI event-onset times. ``slice_from_events``
wraps plain arrays into a Slice (any number of streams, any names, regions
optional); ``load_events_csv`` reads a long-format CSV of (time, roi[,
stream]) rows. Foreign data typically has no amplitudes/widths/rise times —
those fields are filled with NaN and onset times double as ``t50rise``, so
every detector runs unchanged; CICADA's per-event duration modes need real
durations and stay unavailable unless provided.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from bugarach.store import Region, Slice, Stream


def _as_stream(per_roi: list, durations: list | None = None) -> Stream:
    locs = [np.sort(np.asarray(v, dtype=float).ravel()) for v in per_roi]
    nan = [np.full(v.size, np.nan) for v in locs]
    width = ([np.asarray(d, dtype=float).ravel() for d in durations]
             if durations is not None else [v.copy() for v in nan])
    return Stream(locs=locs, amp=[v.copy() for v in nan], width=width,
                  t50rise=[v.copy() for v in locs])


def slice_from_events(
    events,
    *,
    slice_id: str = "events",
    regions=None,
    roi_ids: list[str] | None = None,
    durations=None,
) -> Slice:
    """Build a Slice from per-ROI event-onset times.

    events: dict of stream name -> list of per-ROI time arrays (seconds), or
    a bare list of per-ROI arrays for the common single-stream case (stream
    named "events"). All streams must have the same ROI count (index-aligned).
    regions: optional list of Region objects or (name, start_sec, end_sec)
    tuples; omit entirely for un-annotated recordings — detectors then treat
    the whole recording as one implicit region.
    durations: optional per-event durations (same shape as events), stored as
    the width field for CICADA's per_event mode.
    """
    if not isinstance(events, dict):
        events = {"events": events}
    if durations is not None and not isinstance(durations, dict):
        durations = {next(iter(events)): durations}
    streams = {name: _as_stream(per_roi,
                                None if durations is None
                                else durations.get(name))
               for name, per_roi in events.items()}
    if not streams:
        raise ValueError("events must contain at least one stream")
    n_rois = {name: st.n_rois for name, st in streams.items()}
    if len(set(n_rois.values())) != 1:
        raise ValueError(f"streams must be index-aligned (ROI counts {n_rois})")

    region_objs = []
    for r in regions or []:
        if isinstance(r, Region):
            region_objs.append(r)
        else:
            name, start, end = r
            region_objs.append(Region(name=name, slot=None,
                                      start_sec=float(start),
                                      end_sec=float(end)))
    return Slice(slice_id=slice_id, streams=streams, regions=region_objs,
                 roi_ids=roi_ids)


def load_events_csv(
    path,
    *,
    time_col: str = "time_sec",
    roi_col: str = "roi",
    stream_col: str | None = None,
    slice_id: str | None = None,
) -> Slice:
    """Load a long-format CSV of events: one row per event, columns for time
    (seconds) and ROI id, optionally a stream column for multi-stream data.
    ROIs are index-aligned across streams by their sorted union of ids."""
    path = Path(path)
    rows = []
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or time_col not in reader.fieldnames \
                or roi_col not in reader.fieldnames:
            raise ValueError(
                f"CSV must have columns '{time_col}' and '{roi_col}' "
                f"(found {reader.fieldnames})")
        has_stream = stream_col is not None and stream_col in reader.fieldnames
        for row in reader:
            rows.append((float(row[time_col]), row[roi_col],
                         row[stream_col] if has_stream else "events"))
    if not rows:
        raise ValueError(f"no event rows in {path}")

    roi_ids = sorted({r[1] for r in rows})
    roi_index = {rid: i for i, rid in enumerate(roi_ids)}
    stream_names = sorted({r[2] for r in rows})
    events = {name: [[] for _ in roi_ids] for name in stream_names}
    for t, rid, sname in rows:
        events[sname][roi_index[rid]].append(t)
    return slice_from_events(
        events, slice_id=slice_id or path.stem, roi_ids=roi_ids)
