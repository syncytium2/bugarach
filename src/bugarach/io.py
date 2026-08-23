"""Generic data ingestion — the way IN for labs without event_store files.

The detectors need only per-ROI event-onset times. ``slice_from_events``
wraps plain arrays into a Slice (any number of streams, any names, regions
optional); ``load_events_csv`` reads a long-format CSV of (time, roi[,
stream]) rows; ``load_folder`` reads a whole export folder, which is the
documented way in — see ``docs/export_folder_spec.md``. Foreign data
typically has no amplitudes/widths/rise times — those fields are filled with
NaN and onset times double as ``t50rise``, so every detector runs unchanged.

**The four per-event columns the contract asks for are read, not ignored.**
``width_sec`` becomes ``Stream.width``, ``amp`` becomes ``Stream.amp``,
``peak_sec`` becomes ``Stream.peak``, and ``width_def`` — the producer's own
name for the rule that made the width — rides on ``Stream.width_def``. For a
year the loader read three columns and dropped the rest, so a producer that
did the work the contract asked for reached nothing, and CICADA's
``active_duration_mode="per_event"`` was unreachable through this project's
own input format while the browser viewer read all four from the same files.
Two implementations of one contract disagreeing is worse than a missing
feature: each is evidence for the other being right.

**Width carries its definition or it does not travel.** ``width_sec`` without
``width_def`` is refused at the line that has it, and two different
``width_def`` values inside one stream are refused for the recording — a fast
half-prominence width and a slow rise interval are not the same measurement,
and once they are in one array nothing downstream can tell them apart. What is
*not* refused is a folder with no width at all: the contract asks for width and
does not require it, so such a folder loads with ``width_def is None``, which
is the caller's unambiguous tell. ``load_folder(..., require_width=True)`` is
there for the caller who cannot proceed without one.

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
from typing import NamedTuple

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

#: The per-event columns the contract asks for beyond ``roi`` and ``time_sec``.
#: Their names are the spec's, not the caller's: ``time_sec`` and ``roi`` can be
#: renamed at the call because foreign CSVs spell them anything, but these four
#: only exist because ``docs/export_folder_spec.md`` named them.
WIDTH_COL, WIDTH_DEF_COL, PEAK_COL, AMP_COL = (
    "width_sec", "width_def", "peak_sec", "amp")

#: ``width_def`` values that name a width running from the half-rise to the
#: peak, so that ``time_sec + width_sec`` locates one.
#:
#: **These are the producer's strings, not the spec's.** The spec offers
#: ``t50rise_to_peak`` as an illustration and says in terms that bugarach
#: carries the string without parsing it. This is the one place that has to
#: look, so it matches the vocabulary actually in use: interface2 sends
#: ``rise_interval_peak_minus_t50rise`` on its slow stream and
#: ``halfprom_width_findpeaks_w`` on its fast one. Both are legitimate widths
#: and only the first reaches a peak — adding a half-prominence width to an
#: onset produces a plausible wrong answer rather than an error.
#:
#: A name that is not here is not refused for being unknown. ``peak_sec`` still
#: carries it, and that is the route every current export takes; this list only
#: decides whether the WIDTH may stand in when no peak was sent. Kept identical
#: to ``WIDTH_REACHES_PEAK`` in ``docs/site/raster_viewer.html``, which is the
#: same rule in the other implementation.
WIDTH_REACHES_PEAK = frozenset({
    "rise_interval_peak_minus_t50rise",   # interface2, `slow`
    "t50rise_to_peak",                    # the spec's illustration
})


class WidthNotSuppliedError(ValueError):
    """A caller asked for width and the folder does not carry one.

    Raised only by ``load_folder(..., require_width=True)``. The default is to
    load such a folder — the contract asks for width and does not require it,
    so refusing one would be the consumer overruling a conforming producer.
    Refusal belongs where the need is known, which is the caller.
    """


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


def _aligned(src, i: int, n: int, what: str) -> np.ndarray:
    """One ROI's per-event column, or a run of NaN when the producer sent none."""
    if src is None:
        return np.full(n, np.nan)
    v = np.asarray(src[i], dtype=float).ravel()
    if v.size != n:
        raise ValueError(
            f"{what} has {v.size} value(s) for ROI index {i}, which has {n} "
            f"event(s). Per-event columns are index-aligned with the times.")
    return v


def _as_stream(per_roi: list, durations: list | None = None, *,
               peaks: list | None = None, amps: list | None = None,
               width_def: str | None = None) -> Stream:
    """One Stream from per-ROI arrays, every per-event column kept aligned.

    Events are ordered by time and **their widths, peaks and amplitudes travel
    with them**. Sorting the times on their own — which this did until the
    width column was read — would move each event's width onto a different
    event, which is a wrong number rather than a missing one.
    """
    locs, width, peak, amp = [], [], [], []
    for i, raw in enumerate(per_roi):
        t = np.asarray(raw, dtype=float).ravel()
        order = np.argsort(t, kind="stable")
        locs.append(t[order])
        width.append(_aligned(durations, i, t.size, "durations")[order])
        peak.append(_aligned(peaks, i, t.size, "peaks")[order])
        amp.append(_aligned(amps, i, t.size, "amps")[order])
    return Stream(locs=locs, amp=amp, width=width,
                  t50rise=[v.copy() for v in locs],
                  width_def=width_def,
                  peak=peak if peaks is not None else None)


def _by_stream(value, events: dict, what: str) -> dict:
    """A per-stream argument given as a dict, or as one value for one stream."""
    if value is None:
        return {}
    if isinstance(value, dict):
        unknown = [k for k in value if k not in events]
        if unknown:
            raise ValueError(f"{what} names stream(s) {unknown} that are not in "
                             f"{sorted(events)}")
        return value
    return {next(iter(events)): value}


def slice_from_events(
    events,
    *,
    slice_id: str = "events",
    regions=None,
    roi_ids: list[str] | None = None,
    durations=None,
    peaks=None,
    amps=None,
    width_def=None,
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
    peaks / amps: optional per-event peak times and amplitudes, same shape.
    width_def: the name of the rule that produced ``durations`` — one string
    for a single stream, or a name-keyed dict. Widths measured two ways must
    never be pooled, so a caller supplying durations should say what they are.
    """
    if not isinstance(events, dict):
        events = {"events": events}
    durations = _by_stream(durations, events, "durations")
    peaks = _by_stream(peaks, events, "peaks")
    amps = _by_stream(amps, events, "amps")
    width_def = _by_stream(width_def, events, "width_def")
    streams = {name: _as_stream(per_roi, durations.get(name),
                                peaks=peaks.get(name), amps=amps.get(name),
                                width_def=width_def.get(name))
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


class EventRow(NamedTuple):
    """One row of a recording file. ``time is None`` is a recorded ROI, no event.

    The four optional columns are NaN / "" when the producer did not send them,
    which is legal: the contract asks for them and requires only the first two.
    """

    time: float | None
    roi: str
    stream: str
    width: float = np.nan
    width_def: str = ""
    peak: float = np.nan
    amp: float = np.nan


def _number(raw: str | None, *, path: Path, line: int, col: str) -> float:
    """A per-event number, or NaN where the producer wrote it as missing."""
    s = (raw or "").strip()
    if s.lower() in NO_EVENT:
        return np.nan
    try:
        return float(s)
    except ValueError:
        raise ValueError(
            f"{path.name} line {line}: {col} is {s!r}, which is neither a "
            f"number nor a missing value") from None


def _read_event_rows(path: Path, *, time_col: str, roi_col: str,
                     stream_col: str | None) -> list[EventRow]:
    """The rows of one recording file, with every per-event column the contract
    asks for. Absent columns read as missing; a width without its rule does not."""
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
            width = _number(row.get(WIDTH_COL), path=path, line=n, col=WIDTH_COL)
            wdef = (row.get(WIDTH_DEF_COL) or "").strip()
            if np.isfinite(width) and not wdef:
                # The contract's rule 6, at the only place that can enforce it.
                # A width is not one quantity; a number whose rule did not
                # travel cannot be compared with anything, and reading it
                # anyway is how a column comes to mean two things.
                raise ValueError(
                    f"{path.name} line {n}: {WIDTH_COL} is {width!r} with no "
                    f"{WIDTH_DEF_COL}. Width is defined by the producer, so the "
                    f"name of the rule that produced it travels in the same row "
                    f"— `fwhm`, `t50rise_to_peak`, `above_threshold`, whatever "
                    f"was actually computed (docs/export_folder_spec.md).")
            out.append(EventRow(
                t, row[roi_col], stream or "events", width, wdef,
                _number(row.get(PEAK_COL), path=path, line=n, col=PEAK_COL),
                _number(row.get(AMP_COL), path=path, line=n, col=AMP_COL)))
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


def _assemble(rows: list[EventRow], *, slice_id: str, regions=None,
             meta: dict[str, str] | None = None) -> Slice:
    """Build one Slice from the rows of a recording file.

    Every ROI named by any row is present, whether or not it has a time, so a
    recording in which nothing fired still has its full ROI count. Stream
    names come from the rows rather than the times, so a wholly quiet
    recording still knows which streams it has.

    Width, peak and amplitude ride alongside the time and stay index-aligned
    with it. ``width_def`` is collected only from rows that carry an event: a
    silent ROI's row has a rule and no width to apply it to, and letting that
    declare a width the stream does not have would make ``has_width`` lie about
    an all-quiet recording.
    """
    roi_ids = sorted({r.roi for r in rows}, key=_natural)
    roi_index = {rid: i for i, rid in enumerate(roi_ids)}
    names = sorted({r.stream for r in rows})
    events = {name: [[] for _ in roi_ids] for name in names}
    widths = {name: [[] for _ in roi_ids] for name in names}
    peaks = {name: [[] for _ in roi_ids] for name in names}
    amps = {name: [[] for _ in roi_ids] for name in names}
    defs: dict[str, set[str]] = {name: set() for name in names}
    for r in rows:
        if r.time is None:
            continue
        i = roi_index[r.roi]
        events[r.stream][i].append(r.time)
        widths[r.stream][i].append(r.width)
        amps[r.stream][i].append(r.amp)
        if r.width_def:
            defs[r.stream].add(r.width_def)
        # The peak, by the two routes the contract allows and no third. A width
        # that does not run to the peak is not a peak when added to an onset,
        # and using it anyway is the spec's own failure mode — a plausible
        # wrong answer instead of an error.
        peaks[r.stream][i].append(
            r.peak if np.isfinite(r.peak)
            else (r.time + r.width
                  if r.width_def in WIDTH_REACHES_PEAK and np.isfinite(r.width)
                  else np.nan))

    width_def = {}
    for name, seen in defs.items():
        if len(seen) > 1:
            raise ValueError(
                f"{slice_id}: the '{name}' stream sends {len(seen)} different "
                f"{WIDTH_DEF_COL} values ({', '.join(sorted(seen))}). The "
                f"contract asks for one rule per stream, and widths measured "
                f"two ways cannot be compared, let alone pooled — once they "
                f"are in one array nothing downstream can separate them.")
        if seen:
            width_def[name] = next(iter(seen))

    # A column nobody sent stays absent rather than becoming a run of NaN with
    # a shape: `width_def is None` and `peak is None` are what a caller checks.
    durations = {n: widths[n] for n in names if n in width_def}
    with_peaks = {n: peaks[n] for n in names
                  if any(np.isfinite(v).any() for v in peaks[n])}
    with_amps = {n: amps[n] for n in names
                 if any(np.isfinite(v).any() for v in amps[n])}
    return slice_from_events(events, slice_id=slice_id, roi_ids=roi_ids,
                             regions=regions, meta=meta,
                             durations=durations or None,
                             peaks=with_peaks or None,
                             amps=with_amps or None,
                             width_def=width_def or None)


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


#: Spellings a producer may already use for the reserved subject column. Accepting
#: them costs nothing and means a lab that has written `mouse_id` for years does not
#: have to rename a column to be conforming (spec revision 4).
SUBJECT_ALIASES = ("subject_id", "mouse_id", "animal_id")


def _identity(row: dict) -> dict:
    """Carry every column through, and make the reserved subject column findable.

    The row keeps whatever the producer wrote — nothing is renamed away — and gains
    ``subject_id`` when one of its accepted spellings is present. bugarach reads the
    ROLE of this column and never its value: it learns that two recordings came from
    one animal, not what the animal is.
    """
    if "subject_id" not in row or not str(row.get("subject_id", "")).strip():
        for alias in SUBJECT_ALIASES[1:]:
            v = row.get(alias)
            if v not in (None, "") and str(v).strip():
                row["subject_id"] = v
                break
    return row


def load_folder(folder, *, require_width: bool = False) -> list[Slice]:
    """Read an export folder — the contract in ``docs/export_folder_spec.md``.

    One CSV per recording, named by its slice id, holding that recording's
    event times per ROI. Two reserved filenames carry what is not an event:
    ``slices.csv`` (frame interval + identity columns) and ``regions.csv``
    (treatment windows). Both are optional; each buys one thing, so a folder
    of nothing but event files is a valid input.

    Per-event ``width_sec`` / ``width_def`` / ``peak_sec`` / ``amp`` are read
    where the producer sent them, onto ``Stream.width`` / ``.width_def`` /
    ``.peak`` / ``.amp``.

    **require_width decides what a folder with no width means to YOU.** The
    default is False and the folder loads: the contract asks for width and does
    not require it, so a loader that refused would be the consumer overruling a
    conforming producer — revision 6's exact defect class. The caller tells the
    two cases apart with ``Stream.has_width``, which is False precisely when no
    rule arrived. Pass True from an analysis that cannot proceed on widthless
    data, and the refusal names the recordings and streams that lack one, at
    load, before any number exists.

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

    meta = {r.get("slice_id", ""): _identity(dict(r))
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

    slices = [
        load_events_csv(p, slice_id=p.stem, regions=regions.get(p.stem),
                        meta=meta.get(p.stem))
        for p in files
    ]

    if require_width:
        bare = [f"{s.slice_id}/{name}" for s in slices
                for name, st in s.streams.items() if not st.has_width]
        if bare:
            shown = ", ".join(bare[:5]) + (" …" if len(bare) > 5 else "")
            raise WidthNotSuppliedError(
                f"{folder.name}: {len(bare)} stream(s) carry no per-event width "
                f"({shown}). {WIDTH_COL} is asked for and not required by "
                f"docs/export_folder_spec.md, so this folder is conforming — it "
                f"is this analysis that cannot run without one. Either ask the "
                f"producer for {WIDTH_COL} and {WIDTH_DEF_COL}, or run without "
                f"require_width and use a fixed duration.")

    return slices
