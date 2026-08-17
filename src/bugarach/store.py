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

This docstring claimed the opposite until 2026-08-17 — *"``locs`` are onset
times… the primary input to every detector"* — while the code around it had
it right the whole time: every detector taking an ``onset_field`` defaults
to ``t50rise``, and :mod:`bugarach.detectors.cicada` calls ``locs`` the peak
in its own comment. Nothing computed the wrong answer; the prose was wrong
on its own, which costs nothing until somebody builds from the prose.
interface2 did, writing an export folder against
``docs/export_folder_spec.md``, whose ``time_sec`` column asks for when the
event *began* — they read the code rather than this paragraph and sent
``t50rise``, which is correct.

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
    """Per-ROI event data for one stream (FAST or SLOW)."""

    locs: list[np.ndarray]
    amp: list[np.ndarray]
    width: list[np.ndarray]
    t50rise: list[np.ndarray]

    @property
    def n_rois(self) -> int:
        return len(self.locs)

    @property
    def n_events(self) -> int:
        return sum(len(v) for v in self.locs)


@dataclass
class Region:
    name: str | None
    slot: str | None
    start_sec: float
    end_sec: float


@dataclass
class Slice:
    """A recording: N named event streams + optional region annotations.

    ``streams`` is the generic surface — an ordered name -> Stream mapping.
    The on-disk event_store format carries exactly FAST and SLOW, but that
    pairing is specific to this project; foreign data (see bugarach.io) may
    carry one stream or several under any names. Consumers should iterate
    ``streams`` rather than hardcoding .fast/.slow, which are conveniences
    for the canonical two-stream stores.

    ``meta`` holds the producer's own per-recording columns, verbatim and
    uninterpreted — the frame interval, group, sex, cohort, whatever the lab
    records. bugarach carries them to its output and reads none of them."""

    slice_id: str
    streams: dict[str, Stream]
    regions: list[Region] = field(default_factory=list)
    roi_ids: list[str] | None = None
    meta: dict[str, str] = field(default_factory=dict)

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


def load_slice(path: str | Path) -> Slice:
    """Load one event_store_onset slice file (MATLAB v7 or v7.3)."""
    path = Path(path)
    if is_v73(path):
        return _load_v73(path)
    return _load_v7(path)


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


def _load_v7(path: Path) -> Slice:
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


def _load_v73(path: Path) -> Slice:
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
        regions=regions,
    )
