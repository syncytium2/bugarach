"""Generic data ingestion — the way IN for labs without event_store files.

The detectors need only per-ROI event-onset times. ``slice_from_events``
wraps plain arrays into a Slice (any number of streams, any names, regions
optional); ``load_events_csv`` reads a long-format CSV of (time, roi[,
stream]) rows; ``load_folder`` reads a whole export folder as specified in
``docs/export_folder_spec.md``. Foreign data typically has no
amplitudes/widths/rise times — those fields are filled with NaN and onset
times double as ``t50rise``, so every detector runs unchanged; CICADA's
per-event duration modes need real durations and stay unavailable unless
provided.

**A recorded ROI that fired nothing is still a recorded ROI.** An event
table can only name ROIs that produced a row, so deriving the ROI set from
it silently drops every silent cell and shrinks the denominator of every
per-ROI rate. That is why the folder carries an optional ``rois.csv``
roster: when it is present the ROI set is what the producer declared, not
what the events happened to mention. When it is absent the set is still
derived — the only thing available — and ``Slice.roi_set_declared`` is False
so a consumer can say "at least this many" instead of "this many".
"""

from __future__ import annotations

import csv
import warnings
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
    roi_set_declared: bool = False,
    meta: dict[str, str] | None = None,
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
                 roi_ids=roi_ids, roi_set_declared=roi_set_declared,
                 meta=dict(meta or {}))


def load_events_csv(
    path,
    *,
    time_col: str = "time_sec",
    roi_col: str = "roi",
    stream_col: str | None = None,
    slice_id: str | None = None,
    roster: list[str] | None = None,
) -> Slice:
    """Load a long-format CSV of events: one row per event, columns for time
    (seconds) and ROI id, optionally a stream column for multi-stream data.
    ROIs are index-aligned across streams by their sorted union of ids.

    ``roster`` declares the ROIs that were recorded, in order, so cells that
    fired nothing still occupy a row. Without it the ROI set is whatever the
    events mention, which is a lower bound — see the module docstring."""
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

    return _assemble(rows, slice_id=slice_id or path.stem, roster=roster)


def _assemble(rows, *, slice_id: str, roster: list[str] | None,
              regions=None, meta: dict[str, str] | None = None) -> Slice:
    """Build one Slice from (time, roi, stream) triples.

    With a roster the ROI set is the producer's; every ROI in the events must
    appear in it, because an event in an ROI nobody declared means the two
    files disagree about what was recorded, and picking a winner here would
    hide that."""
    seen = {r[1] for r in rows}
    if roster is None:
        roi_ids, declared = sorted(seen), False
    else:
        undeclared = seen - set(roster)
        if undeclared:
            raise ValueError(
                f"{slice_id}: events name {len(undeclared)} ROI(s) missing from "
                f"the roster ({sorted(undeclared)[:5]}) — the roster must list "
                f"every recorded ROI")
        roi_ids, declared = list(roster), True
    roi_index = {rid: i for i, rid in enumerate(roi_ids)}
    stream_names = sorted({r[2] for r in rows})
    events = {name: [[] for _ in roi_ids] for name in stream_names}
    for t, rid, sname in rows:
        events[sname][roi_index[rid]].append(t)
    return slice_from_events(events, slice_id=slice_id, roi_ids=roi_ids,
                             regions=regions, roi_set_declared=declared,
                             meta=meta)


class RosterNotDeclaredWarning(UserWarning):
    """No ``rois.csv``, so the ROI set was derived from the events and any
    silent cell is missing from it. Every per-ROI rate is then an upper bound
    on a population that is a lower bound."""


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def _require(rows, cols, path: Path) -> None:
    missing = [c for c in cols if rows and c not in rows[0]]
    if missing:
        raise ValueError(f"{path.name} must have column(s) {missing} "
                         f"(found {sorted(rows[0]) if rows else 'no rows'})")


def load_folder(folder) -> list[Slice]:
    """Read an export folder — the contract in ``docs/export_folder_spec.md``.

    Three things are read and nothing else: event times per ROI
    (``events.csv``, required), the ROIs that were recorded (``rois.csv``),
    and treatment timing (``regions.csv``). ``slices.csv`` is carried through
    to ``Slice.meta`` verbatim and interpreted nowhere here.

    Returns one Slice per ``slice_id``, ordered by id. Extra columns in any
    file are ignored, so one folder can serve several consumers.
    """
    folder = Path(folder)
    events_path = folder / "events.csv"
    if not events_path.is_file():
        raise FileNotFoundError(
            f"{folder} is not an export folder: events.csv is required "
            f"(see docs/export_folder_spec.md)")

    ev = _read_csv(events_path)
    if not ev:
        raise ValueError(f"no event rows in {events_path}")
    _require(ev, ["roi", "time_sec"], events_path)
    has_slice = "slice_id" in ev[0]
    has_stream = "stream" in ev[0]

    by_slice: dict[str, list] = {}
    for r in ev:
        sid = r["slice_id"] if has_slice else folder.name
        by_slice.setdefault(sid, []).append(
            (float(r["time_sec"]), r["roi"],
             r["stream"] if has_stream and r["stream"] else "events"))

    rosters: dict[str, list[str]] = {}
    roster_path = folder / "rois.csv"
    if roster_path.is_file():
        rows = _read_csv(roster_path)
        _require(rows, ["roi"], roster_path)
        for r in rows:
            sid = r["slice_id"] if "slice_id" in r else folder.name
            rosters.setdefault(sid, []).append(r["roi"])
    else:
        warnings.warn(
            f"{folder.name}: no rois.csv, so the ROI set comes from the events "
            f"and silent cells are absent from it. Per-ROI rates are computed "
            f"over a population that is a lower bound.",
            RosterNotDeclaredWarning, stacklevel=2)

    regions: dict[str, list[Region]] = {}
    regions_path = folder / "regions.csv"
    if regions_path.is_file():
        rows = _read_csv(regions_path)
        _require(rows, ["region_idx", "label", "start_sec", "end_sec"],
                 regions_path)
        for r in sorted(rows, key=lambda r: int(r["region_idx"])):
            sid = r["slice_id"] if "slice_id" in r else folder.name
            regions.setdefault(sid, []).append(
                Region(name=r["label"] or None, slot=str(r["region_idx"]),
                       start_sec=float(r["start_sec"]),
                       end_sec=float(r["end_sec"])))

    meta: dict[str, dict[str, str]] = {}
    slices_path = folder / "slices.csv"
    if slices_path.is_file():
        for r in _read_csv(slices_path):
            sid = r.get("slice_id", folder.name)
            meta[sid] = dict(r)

    return [
        _assemble(rows, slice_id=sid, roster=rosters.get(sid),
                  regions=regions.get(sid), meta=meta.get(sid))
        for sid, rows in sorted(by_slice.items())
    ]
