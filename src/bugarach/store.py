"""Reader for interface2 event_store_onset* slice files.

Each ``<slice_id>.mat`` holds per-ROI event times for two streams::

    slice_id : str
    fast     : struct with per-ROI cell arrays  locs / amp / width / t50rise
    slow     : same shape as fast
    regions  : struct array  name / slot / start_sec / end_sec
    roi_ids  : (optional) per-ROI identifiers

**``locs`` is the PEAK. ``t50rise`` is the onset — when the event began.**
Both are seconds, both are per event, and they are not interchangeable: the
peak lags the onset by roughly 0.3 s in FAST and roughly 2 s in SLOW, which
is enough to mistime SLOW coincidence and change what a coactivity detector
counts. That is why the store carries both, and why the ``_onset`` store
exists at all.

**The three detectors that take an ``onset_field`` do not agree, and that is
deliberate.** ``sce_detect`` and ``loco_detect`` default to ``t50rise``;
:func:`bugarach.detectors.cicada.cicada_detect` — **the detector named locust;
``cicada`` is its key because that is the ``detections.csv`` contract value** —
defaults to ``locs``, the peak. interface2's ``generate_sce_cicada`` — the MATLAB
this is a port of, which is not CICADA itself — anchors its raster on the peak, as
CICADA does, and §2 makes
matching it the product — so the port keeps the peak rather than improving on
it. The science agrees with the parity: a single-cell event runs 10-60+ s from
half-rise to peak, and treating events that long as points would find almost
any pair of them coincident. ``t50rise`` locates an event; ``locs`` closes it.

**The interval between them is NOT this package's to compute**, and this
sentence used to say it *was* — *"the interval between them is its duration"*,
sitting one line under the two field names, which read as a licence and was
taken as one. :func:`~bugarach.detectors.cicada.rise_durations` computed exactly
that subtraction. It refuses now. **An event's duration arrives from the
producer** in ``width_sec``, under the ``width_def`` naming the rule that made
it, and this package paints what it is given. **It does not interpret it, and
nothing here describes what a duration means** — different producers, and even
different streams from one producer, measure it differently, and a repo that
writes any of those rules down is a repo whose description goes stale and whose
readers mistake the producer's decision for ours. Tony, 2026-08-29: *"matlab
decides duration. bugarach python and webapp is not responsible for what the
duration is derived from"* — and, on how little of this is ours to know,
*"bugarach doesn't care what you put in the duration column. your mother's social
security number works fine for 5 of 6 detectors."* Read ``Stream.width`` behind
``Stream.has_width``; sapper SAP012 blocks the subtraction; ADR-0002's
2026-08-28 addendum and FOUNDATIONS §7 carry the reasoning. The correctness
argument is the smaller of the two: on **folder** input ``locs`` holds the
``t50rise``, so that subtraction was identically zero for all 2,215 events in
the corpus — right shape, right dtype, no error.

**Do not "correct" cicada to ``t50rise``.** Two sentences claiming otherwise
have already been written in this file. Until 2026-08-17 it said *"``locs`` are
onset times… the primary input to every detector"*; the correction that
replaced it asserted that *every* detector taking an ``onset_field`` defaults
to ``t50rise``, which is false for exactly the one that matters. Neither
sentence changed a number — the prose was wrong on its own, which costs
nothing until somebody builds from it. Two have: interface2 read the first and
raised it against ``docs/export_folder_spec.md``, and a bugarach session read
the second and reported cicada's default as a bug. This paragraph is the third
attempt, and it names the defaults one by one so there is no universal left to
be wrong.

Files exist in two MATLAB formats: v7 (scipy) and v7.3 (HDF5). v7 files pad
the per-ROI arrays to a rectangle with NaN; the loader strips that padding
(masking every field by valid ``locs``). Unused region slots are stored with
empty fields and are skipped.

MATLAB ``string``-class values in v7.3 files are stored in the opaque MCOS
subsystem and cannot be decoded portably; where one is hit, the field falls
back to ``None`` (``slice_id`` falls back to the filename stem).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import scipy.io as sio

# h5py is imported lazily, inside the v7.3 branch only. It is a compiled
# extension with no pure-Python fallback, so a top-level import makes the whole
# package unimportable anywhere h5py is unavailable — notably Pyodide, which is
# how the viewer would run in a browser with no server. v7 stores (scipy) and
# foreign CSV/array data need none of it.

EVENT_FIELDS = ("locs", "amp", "width", "t50rise")


@dataclass
class Stream:
    """Per-ROI event data for one stream (FAST or SLOW).

    ``width_def`` and ``peak`` are for **folder** input and stay ``None`` for a
    store, which carries neither: a store's peak IS ``locs``, and its ``width``
    is whatever the MATLAB pipeline put there under no stated rule. An export
    folder is the other way round — ``locs`` there is the half-rise, the only
    time ``docs/export_folder_spec.md`` guarantees, so a peak the producer sent
    has nowhere else to go, and the width arrives with the producer's own name
    for the rule that made it. ``bugarach.io`` fills both; nothing else should.

    **A width whose rule did not travel is worse than no width** (spec rule 6),
    so the two move together: a folder stream with real widths has a
    ``width_def``, and ``width_def is None`` means there is no width worth
    reading, whatever ``width`` holds.
    """

    locs: list[np.ndarray]
    amp: list[np.ndarray]
    width: list[np.ndarray]
    t50rise: list[np.ndarray]
    width_def: str | None = None
    peak: list[np.ndarray] | None = None

    @property
    def has_width(self) -> bool:
        """Did a producer-defined width arrive, with the rule that produced it?"""
        return self.width_def is not None

    @property
    def has_peak(self) -> bool:
        """Is a peak time available apart from ``locs``?"""
        return self.peak is not None

    @property
    def n_rois(self) -> int:
        return len(self.locs)

    @property
    def n_events(self) -> int:
        return sum(len(v) for v in self.locs)


@dataclass
class Region:
    """A period of a recording, and optionally the part of it to analyse.

    ``start_sec``/``end_sec`` are **what happened** — when the period began and
    ended. ``analysis_start_sec``/``analysis_end_sec`` are **what to score**,
    when the producer has already decided: a wash-in delay, a duration cap, a
    window trimmed for any reason of their own.

    The two are kept apart rather than collapsed because they answer different
    questions and only the producer knows the second. When they are absent
    bugarach derives the analysis window itself, applying this project's
    convention — which is right for this project and an inherited assumption
    for anybody else (see ``docs/export_folder_spec.md``)."""

    name: str | None
    slot: str | None
    start_sec: float
    end_sec: float
    analysis_start_sec: float | None = None
    analysis_end_sec: float | None = None

    @property
    def has_analysis_window(self) -> bool:
        return (self.analysis_start_sec is not None
                and self.analysis_end_sec is not None)


class FrameIntervalNotDeclaredError(ValueError):
    """Something asked a recording for its sampling interval and it has none.

    The interval is a property of the microscope, no arithmetic on onset times
    recovers it, and there is no default — FOUNDATIONS §6. So a recording that
    was never told one cannot be measured, and this is what says so instead of
    a number appearing from a constant somewhere.

    It is raised by :meth:`Slice.require_dt`, which is the only way anything in
    this project reads the interval off a recording. Nothing catches it to
    substitute a value; the caller's answer is to supply the interval.
    """


def validated_dt(dt, *, what: str) -> float | None:
    """A sampling interval, or ``None`` for "nobody has said".

    ``what`` names the thing being constructed so the message points at the
    caller rather than at this function. A value that is present and unusable
    is refused here rather than carried: a negative, zero, NaN or unparseable
    interval is a mistake at the source, and the whole point of §6 is that a
    bad interval must not become a silent one.
    """
    if dt is None:
        return None
    try:
        v = float(dt)
    except (TypeError, ValueError):
        raise FrameIntervalNotDeclaredError(
            f"{what}: dt is {dt!r}, which is not a number of seconds. Pass the "
            f"acquisition sampling interval, or None to say it is unknown — "
            f"and then nothing may be computed from it (FOUNDATIONS §6)."
        ) from None
    if not (np.isfinite(v) and v > 0):
        raise FrameIntervalNotDeclaredError(
            f"{what}: dt is {v!r}, which is not a positive number of seconds. "
            f"An interval of zero or less is not a slower rig, it is a typo.")
    return v


@dataclass
class Slice:
    """A recording: N named event streams + optional region annotations.

    ``streams`` is the generic surface — an ordered name -> Stream mapping.
    The on-disk event_store format carries exactly FAST and SLOW, but that
    pairing is specific to this project; foreign data (see bugarach.io) may
    carry one stream or several under any names. Consumers should iterate
    ``streams`` rather than hardcoding .fast/.slow, which are conveniences
    for the canonical two-stream stores.

    ``dt`` is the acquisition sampling interval in seconds and **has no
    default: every construction path has to state it** (FOUNDATIONS §6). It is
    third in the signature, before the optional fields, so that forgetting it
    is a ``TypeError`` at the line that forgot rather than a wrong number three
    layers down.

    **What a recording with no interval is.** ``dt=None`` is a legal *answer*
    and it means one thing: nobody has said. It is not a default and it is not
    unknown-but-probably-0.1 — a folder may legally omit ``slices.csv``
    entirely (``docs/export_folder_spec.md``: only the recording files are
    required), and the spec's own instruction for that case is that bugarach
    **asks**. Such a recording draws — a raster needs no interval — and cannot
    be measured: :meth:`require_dt` refuses, and no detector carries a fallback
    to fill the hole any more. What is *not* legal is silence: omitting the
    argument raises, so "we never thought about it" and "we know we do not
    know" are different states of the program rather than the same one.

    **Read it through :meth:`require_dt`, never off the attribute.** The
    attribute can be ``None``; the accessor cannot return one.

    ``meta`` holds the producer's own per-recording columns, verbatim and
    uninterpreted — including ``frame_interval_sec`` as the raw string the
    producer wrote, which is what ``bugarach check`` reports on. ``dt`` is that
    column *read*; ``meta`` is that column *carried*. The two are kept apart so
    a conformance check can still name a producer's typo after the loader has
    declined to turn it into a number."""

    slice_id: str
    streams: dict[str, Stream]
    dt: float | None
    regions: list[Region] = field(default_factory=list)
    roi_ids: list[str] | None = None
    meta: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.dt = validated_dt(self.dt, what=f"slice {self.slice_id!r}")

    @property
    def has_dt(self) -> bool:
        """Can this recording be measured at all? Ask before offering to."""
        return self.dt is not None

    def require_dt(self, what: str = "this analysis") -> float:
        """The sampling interval, or a refusal naming how to supply one.

        Every consumer of the interval goes through here, which is what makes
        "no default, no inference, no fallback constant" checkable rather than
        aspirational: there is one place a number can come from, and it either
        has one or it stops.
        """
        if self.dt is None:
            raise FrameIntervalNotDeclaredError(
                f"{self.slice_id}: {what} needs the acquisition sampling "
                f"interval and this recording never stated one. It is a "
                f"property of the microscope, it cannot be recovered from "
                f"onset times, and there is no default because a default here "
                f"is a guess about somebody else's rig (FOUNDATIONS §6). "
                f"Declare frame_interval_sec in the folder's slices.csv, or "
                f"pass dt= to the loader — load_folder(folder, dt=...) is the "
                f"script's version of the prompt "
                f"docs/export_folder_spec.md describes.")
        return self.dt

    @property
    def fast(self) -> Stream:
        return self.streams["fast"]

    @property
    def slow(self) -> Stream:
        return self.streams["slow"]


def _h5py():
    """Import h5py on demand, with a message that says what is actually wrong."""
    try:
        import h5py
    except ImportError as exc:                       # pragma: no cover - env
        raise ImportError(
            "reading a MATLAB v7.3 (HDF5) store needs h5py, which is not "
            "installed here. v7 stores and CSV/array input do not need it."
        ) from exc
    return h5py


def is_v73(path: str | Path) -> bool:
    """Is this an HDF5-backed (MATLAB v7.3) store? False when h5py is absent —
    the caller then takes the scipy path, which is the right answer for v7."""
    try:
        return bool(_h5py().is_hdf5(Path(path)))
    except ImportError:
        return False


def store_recordings(directory: str | Path) -> list[Path]:
    """The ``.mat`` recordings in a directory, sorted. Opens none of them.

    **Here so that recognising a store does not require reading one.** SAP007 blocks
    ``.mat`` access outside this module precisely because analyses kept going around
    the export folder, and two lab-withdrawn recordings ended up inside published
    numbers. But `bugarach.dataset` has to be able to say "that is a store, and this
    analysis reads folders" — refusing a store is the rule's purpose, not an exception
    to it. Keeping the knowledge in the store reader also keeps SAP007's exclusion list
    what its own comment says it is: a shrinking backlog of analyses, not a standing
    list of helpers.

    Returns ``[]`` for anything that is not a directory, so a caller can ask without
    checking first.
    """
    p = Path(directory)
    return sorted(p.glob("*.mat")) if p.is_dir() else []


def load_slice(path: str | Path, *, dt: float | None) -> Slice:
    """Load one event_store_onset slice file (MATLAB v7 or v7.3).

    ``dt`` is required and has no default. **The store does not carry the
    sampling interval** — that is recorded in FOUNDATIONS §6 and filed with the
    pipeline team, and it is exactly why the reader asks for it instead of
    reading it. Pass the interval the recording was acquired at, or ``None`` to
    say it is not known here; ``None`` produces a recording that can be drawn
    and not measured, and omitting the argument produces a ``TypeError``.

    A reader that defaulted this would be answering, for every store and every
    lab, a question only the person who ran the microscope can answer.
    """
    path = Path(path)
    if is_v73(path):
        return _load_v73(path, dt)
    return _load_v7(path, dt)


def _finalize_stream(cols: dict[str, list[np.ndarray]]) -> Stream:
    """Drop NaN padding: v7 stores pad per-ROI arrays to a rectangle with
    NaN. ``locs`` defines which entries are real events; the same mask is
    applied to every field so the four stay index-aligned."""
    for i, locs in enumerate(cols["locs"]):
        valid = ~np.isnan(locs)
        if valid.all():
            continue
        for f in EVENT_FIELDS:
            a = cols[f][i]
            if a.size == valid.size:
                cols[f][i] = a[valid]
    return Stream(**cols)


# ---------------------------------------------------------------- v7 (scipy)

def _as_event_array(v) -> np.ndarray:
    """A squeezed cell entry may be a 0-d scalar, empty, or a vector."""
    return np.atleast_1d(np.asarray(v, dtype=float)).ravel()


def _stream_v7(s) -> Stream:
    cols = {}
    for f in EVENT_FIELDS:
        cells = np.atleast_1d(getattr(s, f))
        cols[f] = [_as_event_array(c) for c in cells]
    return _finalize_stream(cols)


def _load_v7(path: Path, dt: float | None) -> Slice:
    m = sio.loadmat(path, squeeze_me=True, struct_as_record=False)
    regions = []
    for r in np.atleast_1d(m.get("regions", np.array([]))):
        # unused slots (e.g. treat3/treat4) are stored with empty fields — skip
        if np.asarray(r.start_sec).size == 0:
            continue
        regions.append(
            Region(
                name=str(r.name) if hasattr(r, "name") else None,
                slot=str(r.slot) if hasattr(r, "slot") else None,
                start_sec=float(r.start_sec),
                end_sec=float(r.end_sec),
            )
        )
    roi_ids = None
    if "roi_ids" in m:
        roi_ids = [str(x) for x in np.atleast_1d(m["roi_ids"])]
    return Slice(
        slice_id=str(m["slice_id"]),
        streams={"fast": _stream_v7(m["fast"]), "slow": _stream_v7(m["slow"])},
        dt=dt,
        regions=regions,
        roi_ids=roi_ids,
    )


# ---------------------------------------------------------------- v7.3 (hdf5)

def _deref_cell(f: h5py.File, ds: h5py.Dataset) -> list[np.ndarray]:
    out = []
    for ref in np.asarray(ds).ravel():
        node = f[ref]
        if node.attrs.get("MATLAB_empty"):
            out.append(np.empty(0))
        else:
            out.append(np.asarray(node, dtype=float).ravel())
    return out


def _stream_v73(f: h5py.File, g: h5py.Group) -> Stream:
    return _finalize_stream({fld: _deref_cell(f, g[fld]) for fld in EVENT_FIELDS})


def _maybe_str(node) -> str | None:
    """Decode a char-array dataset; MATLAB string class (MCOS) -> None."""
    if node.attrs.get("MATLAB_class") == b"char":
        return "".join(map(chr, np.asarray(node).ravel()))
    return None


def _load_v73(path: Path, dt: float | None) -> Slice:
    h5py = _h5py()
    with h5py.File(path, "r") as f:
        fast = _stream_v73(f, f["fast"])
        slow = _stream_v73(f, f["slow"])
        regions = []
        if "regions" in f:
            rg = f["regions"]
            starts = np.atleast_1d(np.asarray(rg["start_sec"], dtype=float).ravel())
            ends = np.atleast_1d(np.asarray(rg["end_sec"], dtype=float).ravel())
            for start, end in zip(starts, ends):
                regions.append(
                    Region(
                        name=_maybe_str(rg["name"]) if "name" in rg else None,
                        slot=_maybe_str(rg["slot"]) if "slot" in rg else None,
                        start_sec=float(start),
                        end_sec=float(end),
                    )
                )
        slice_id = None
        if "slice_id" in f:
            slice_id = _maybe_str(f["slice_id"])
    return Slice(
        slice_id=slice_id or path.stem,
        streams={"fast": fast, "slow": slow},
        dt=dt,
        regions=regions,
    )
