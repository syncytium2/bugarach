"""Reader for interface2 event_store_onset* slice files.

Each ``<slice_id>.mat`` holds per-ROI event onsets for two streams::

    slice_id : str
    fast     : struct with per-ROI cell arrays  locs / amp / width / t50rise
    slow     : same shape as fast
    regions  : struct array  name / slot / start_sec / end_sec
    roi_ids  : (optional) per-ROI identifiers

``locs`` are onset times in seconds; they are the primary input to every
detector. Files exist in two MATLAB formats: v7 (scipy) and v7.3 (HDF5).
v7 files pad the per-ROI arrays to a rectangle with NaN; the loader strips
that padding (masking every field by valid ``locs``). Unused region slots
are stored with empty fields and are skipped.

MATLAB ``string``-class values in v7.3 files are stored in the opaque MCOS
subsystem and cannot be decoded portably; where one is hit, the field falls
back to ``None`` (``slice_id`` falls back to the filename stem).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import h5py
import numpy as np
import scipy.io as sio

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
    slice_id: str
    fast: Stream
    slow: Stream
    regions: list[Region] = field(default_factory=list)
    roi_ids: list[str] | None = None


def load_slice(path: str | Path) -> Slice:
    """Load one event_store_onset slice file (MATLAB v7 or v7.3)."""
    path = Path(path)
    if h5py.is_hdf5(path):
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
        fast=_stream_v7(m["fast"]),
        slow=_stream_v7(m["slow"]),
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
        fast=fast,
        slow=slow,
        regions=regions,
    )
