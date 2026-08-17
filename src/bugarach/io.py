"""Generic data ingestion — the way IN for labs without event_store files.

The detectors need only per-ROI event-onset times. ``slice_from_events``
wraps plain arrays into a Slice (any number of streams, any names, regions
optional); ``load_events_csv`` reads a long-format CSV of (time, roi[,
stream]) rows; ``load_folder`` reads a whole export folder, which is the
documented way in — see ``docs/export_folder_spec.md``. Foreign data
typically has no amplitudes/widths/rise times — those fields are filled with
NaN and onset times double as ``t50rise``, so every detector runs unchanged;
CICADA's per-event duration modes need real durations and stay unavailable
unless provided.

The folder is one file per recording, because that is what a lab's pipeline
emits — a batch table would make them write a concatenation script before
they could try the tool. Two reserved filenames carry the facts that are not
events and do not look like an event table: ``slices.csv`` (the frame
interval, plus whatever identity columns the lab keeps) and ``regions.csv``
(treatment windows). Everything else in the folder is a recording, named by
its file stem.

**An ROI that was imaged and fired nothing is one row with no time.** Long
format can otherwise only name ROIs that produced an event, so silent cells
would vanish and shrink the denominator of every per-ROI rate. Writing the
time as ``NA`` — the spec's own convention for a missing value — states the
ROI without asserting an event, so the format carries the population and no
code has to reconstruct it.
"""

from __future__ import annotations

import csv
import re
import warnings
from pathlib import Path

import numpy as np

from bugarach.store import Region, Slice, Stream

#: Filenames in an export folder that are not recordings. Everything else is.
#: ``metric_dictionary.csv`` is here because it belongs to the OUTPUT contract:
#: unreserved it would be read as a recording called "metric_dictionary" and
#: fail on its columns, which is a confusing way to learn you shipped it.
RESERVED = ("slices.csv", "regions.csv", "metric_dictionary.csv")

#: Spellings of "this ROI was recorded and produced no event here". The bare
#: empty field is included because that is what a spreadsheet writes.
NO_EVENT = ("", "na", "nan", "none", "null")


class TableMissesARecordingWarning(UserWarning):
    """A reserved table is present but has no row for some recording.

    The producer shipped the table, so they meant to describe that recording —
    a `slice_id` that matches no file, or a file that matches no row, is
    usually one typo. Silence here costs a window or an interval and looks
    exactly like a deliberate omission.

    Not an error: a batch table legitimately covers more recordings than a
    given folder holds, so extra rows are fine. What is reported is the other
    direction — a recording the table failed to reach.
    """


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
                 roi_ids=roi_ids, meta=dict(meta or {}))


def load_events_csv(
    path,
    *,
    time_col: str = "time_sec",
    roi_col: str = "roi",
    stream_col: str | None = None,
    slice_id: str | None = None,
    meta: dict[str, str] | None = None,
    regions=None,
) -> Slice:
    """Load a long-format CSV of events: one row per event, columns for time
    (seconds) and ROI id, optionally a stream column for multi-stream data.
    ROIs are index-aligned across streams by their sorted union of ids.

    A row whose time is empty or ``NA`` declares that its ROI was recorded and
    produced no event — the ROI is present, with no times against it."""
    path = Path(path)
    rows = _read_event_rows(path, time_col=time_col, roi_col=roi_col,
                            stream_col=stream_col)
    return _assemble(rows, slice_id=slice_id or path.stem, regions=regions,
                     meta=meta)


def _read_event_rows(path: Path, *, time_col: str, roi_col: str,
                     stream_col: str | None) -> list[tuple]:
    """(time | None, roi, stream) per row. None is a recorded ROI, no event."""
    out = []
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or time_col not in reader.fieldnames \
                or roi_col not in reader.fieldnames:
            raise ValueError(
                f"{path.name} must have columns '{time_col}' and '{roi_col}' "
                f"(found {reader.fieldnames})")
        # a stream column is honoured whenever the file carries one
        sc = stream_col or "stream"
        has_stream = sc in reader.fieldnames
        for n, row in enumerate(reader, start=2):
            raw = (row[time_col] or "").strip()
            if raw.lower() in NO_EVENT:
                t = None
            else:
                try:
                    t = float(raw)
                except ValueError as exc:
                    spellings = ", ".join(x or "an empty field" for x in NO_EVENT)
                    raise ValueError(
                        f"{path.name} line {n}: {time_col} is {raw!r}, which is "
                        f"neither a time in seconds nor a missing value "
                        f"({spellings})") from exc
            stream = (row.get(sc) or "").strip() if has_stream else ""
            out.append((t, row[roi_col], stream or "events"))
    if not out:
        raise ValueError(f"no rows in {path}")
    return out


def _natural(s: str) -> tuple:
    """Order ROI ids the way a lab numbers them: ROI 2 before ROI 10.

    Plain string ordering puts '10' before '2', so a reader comparing a
    printed ROI list against their own gets a shuffle with no explanation.
    Digit runs compare as numbers, everything else as text."""
    out = []
    for part in re.split(r"(\d+)", s):
        if part.isdigit():
            out.append((0, int(part), ""))
        elif part:
            out.append((1, 0, part))
    return tuple(out)


def _assemble(rows, *, slice_id: str, regions=None,
             meta: dict[str, str] | None = None) -> Slice:
    """Build one Slice from (time | None, roi, stream) triples.

    Every ROI named by any row is present, whether or not it has a time, so a
    recording in which nothing fired still has its full ROI count. Stream
    names come from the rows rather than the times, so a wholly quiet
    recording still knows which streams it has."""
    roi_ids = sorted({r[1] for r in rows}, key=_natural)
    roi_index = {rid: i for i, rid in enumerate(roi_ids)}
    events = {name: [[] for _ in roi_ids] for name in sorted({r[2] for r in rows})}
    for t, rid, sname in rows:
        if t is not None:
            events[sname][roi_index[rid]].append(t)
    return slice_from_events(events, slice_id=slice_id, roi_ids=roi_ids,
                             regions=regions, meta=meta)


def _read_table(path: Path, required: tuple[str, ...]) -> list[dict[str, str]]:
    """One of the two reserved tables. Absent is fine; malformed is not."""
    if not path.is_file():
        return []
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    missing = [c for c in required if rows and c not in rows[0]]
    if missing:
        raise ValueError(f"{path.name} must have column(s) {missing} "
                         f"(found {sorted(rows[0])})")
    return rows


def load_folder(folder) -> list[Slice]:
    """Read an export folder — the contract in ``docs/export_folder_spec.md``.

    One CSV per recording, named by its slice id, holding that recording's
    event times per ROI. Two reserved filenames carry what is not an event:
    ``slices.csv`` (frame interval + identity columns) and ``regions.csv``
    (treatment windows). Both are optional; each buys one thing, so a folder
    of nothing but event files is a valid input.

    Returns one Slice per recording, ordered by slice id.
    """
    folder = Path(folder)
    if not folder.is_dir():
        raise NotADirectoryError(f"{folder} is not a folder")

    files = sorted(p for p in folder.glob("*.csv") if p.name not in RESERVED)
    if not files:
        raise FileNotFoundError(
            f"{folder} holds no recordings: an export folder is one CSV per "
            f"recording, plus optionally {' and '.join(RESERVED)} "
            f"(see docs/export_folder_spec.md)")

    regions: dict[str, list[Region]] = {}
    rows = _read_table(folder / "regions.csv",
                       ("region_idx", "label", "start_sec", "end_sec"))
    for n, r in enumerate(rows, start=2):
        # region_idx is the ordering and the only ordering, so a non-integer
        # here is not a detail to coerce past — it means the producer put
        # something else in the column, usually the label.
        try:
            int(r["region_idx"])
        except (TypeError, ValueError):
            raise ValueError(
                f"regions.csv line {n}: region_idx is {r['region_idx']!r}, "
                f"which is not a 1-based integer. It is the chronological "
                f"ordering of the windows, not their name — the name is "
                f"'label'.") from None
    for r in sorted(rows, key=lambda r: int(r["region_idx"])):
        # The analysis window is optional, and either both bounds or neither:
        # half of one is a producer bug, not a partial answer, and guessing the
        # missing half would invent the policy this column exists to carry.
        a0 = (r.get("analysis_start_sec") or "").strip()
        a1 = (r.get("analysis_end_sec") or "").strip()
        if bool(a0) != bool(a1):
            raise ValueError(
                f"regions.csv, {r.get('slice_id', '?')} region "
                f"{r['region_idx']}: analysis_start_sec and analysis_end_sec "
                f"must be given together (got {a0!r} and {a1!r})")
        regions.setdefault(r.get("slice_id", ""), []).append(
            Region(name=r["label"] or None, slot=str(r["region_idx"]),
                   start_sec=float(r["start_sec"]),
                   end_sec=float(r["end_sec"]),
                   analysis_start_sec=float(a0) if a0 else None,
                   analysis_end_sec=float(a1) if a1 else None))

    meta = {r.get("slice_id", ""): dict(r)
            for r in _read_table(folder / "slices.csv", ("slice_id",))}

    for name, table, present in (("regions.csv", regions,
                                  (folder / "regions.csv").is_file()),
                                 ("slices.csv", meta,
                                  (folder / "slices.csv").is_file())):
        if not present:
            continue                      # absent is a choice, not a mistake
        missed = [p.stem for p in files if p.stem not in table]
        if missed:
            shown = ", ".join(missed[:5]) + (" …" if len(missed) > 5 else "")
            warnings.warn(
                f"{folder.name}: {name} has no row for {len(missed)} of "
                f"{len(files)} recording(s) ({shown}). Those recordings get "
                f"nothing from it — check the slice_id spelling against the "
                f"file names.", TableMissesARecordingWarning, stacklevel=2)

    return [
        load_events_csv(p, slice_id=p.stem, regions=regions.get(p.stem),
                        meta=meta.get(p.stem))
        for p in files
    ]
