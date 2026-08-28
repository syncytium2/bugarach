"""The DANDI importer, and the contract claim nobody had ever tested.

Two things are under test and the second is the reason this file exists.

**The conversion.** A binary raster is turned into event rows: rising edges
become `time_sec`, run lengths become `width_sec`, and an ROI that never fires
becomes a `roi,NA` row rather than vanishing.

**That a MINIMAL folder actually loads.** `docs/export_folder_spec.md` says
everything past `roi` and `time_sec` is optional and `io.py`'s docstring says the
absent fields are NaN-filled — but every folder bugarach had ever read came from
one exporter that sends the full per-event set, so the tolerance was asserted and
never exercised. These tests build a folder with no `stream`, no `peak_sec` and
no `amp` and put it through `load_folder`.

Synthetic fixtures only — no real recording is committed (FOUNDATIONS §5).
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

from bugarach.io import load_folder  # noqa: E402

import_dandi = pytest.importorskip("import_dandi")


def _session(raster, dt=0.1, t0=0.0, slice_id="synthetic_a", n_roi=None):
    r = np.asarray(raster, dtype=np.int8)
    return dict(slice_id=slice_id, raster=r, dt=dt, t0=t0,
                roi_ids=[str(i) for i in range(n_roi or r.shape[1])],
                age="P7D", subject="synthetic")


def test_rising_edges_and_run_lengths_are_read_off_the_raster():
    # one ROI, frames 2-4 active (3 frames), then frame 7 active (1 frame)
    col = np.array([0, 0, 1, 1, 1, 0, 0, 1, 0, 0], dtype=np.int8)
    onsets, widths = import_dandi.runs(col[:, None], dt=0.5, t0=10.0)
    assert onsets[0] == pytest.approx([10.0 + 2 * 0.5, 10.0 + 7 * 0.5])
    assert widths[0] == pytest.approx([3 * 0.5, 1 * 0.5])


def test_a_run_still_active_at_the_last_frame_is_closed_at_the_end():
    """The recording stopped; the cell did not. Closing at the end is the honest
    reading, and dropping the run entirely would lose a real event."""
    col = np.array([0, 0, 1, 1], dtype=np.int8)
    onsets, widths = import_dandi.runs(col[:, None], dt=1.0, t0=0.0)
    assert onsets[0] == pytest.approx([2.0])
    assert widths[0] == pytest.approx([2.0])          # frames 2 and 3


def test_an_roi_that_never_fires_becomes_an_NA_row_not_a_missing_one(tmp_path):
    """The contract's only way to say "recorded, fired nothing". Dropping it makes
    every per-ROI rate divide by the wrong denominator."""
    raster = np.zeros((6, 3), dtype=np.int8)
    raster[1:3, 0] = 1                                 # ROI 0 fires, 1 and 2 silent
    n_roi, n_events, n_silent = import_dandi.write_recording(
        tmp_path, _session(raster))
    assert (n_roi, n_events, n_silent) == (3, 1, 2)

    rows = list(csv.DictReader((tmp_path / "synthetic_a.csv").open()))
    silent = [r for r in rows if r["time_sec"] == "NA"]
    assert {r["roi"] for r in silent} == {"1", "2"}
    assert len(rows) == 3                              # 1 event + 2 NA rows


def test_width_def_travels_on_every_event_row(tmp_path):
    """A width without its definition does not travel — the contract refuses to
    infer what a width means, and this producer's is not a transient width."""
    raster = np.zeros((6, 2), dtype=np.int8)
    raster[1:3, 0] = 1
    raster[4:5, 1] = 1
    import_dandi.write_recording(tmp_path, _session(raster))
    rows = list(csv.DictReader((tmp_path / "synthetic_a.csv").open()))
    events = [r for r in rows if r["time_sec"] != "NA"]
    assert events, "expected event rows"
    assert {r["width_def"] for r in events} == {import_dandi.WIDTH_DEF}


def test_the_written_folder_loads_with_no_stream_no_peak_and_no_amp(tmp_path):
    """The claim the contract makes and nothing had exercised.

    A folder carrying only roi/time_sec/width_sec/width_def must load, with the
    absent per-event fields NaN-filled rather than raising.
    """
    raster = np.zeros((20, 3), dtype=np.int8)
    raster[2:4, 0] = 1
    raster[10:11, 0] = 1
    raster[5:8, 1] = 1
    # ROI 2 stays silent on purpose — a real corpus is full of them.
    sess = _session(raster, dt=0.25)
    n_roi, _, _ = import_dandi.write_recording(tmp_path, sess)
    import_dandi.write_sidecar(tmp_path, [dict(
        slice_id=sess["slice_id"], dt=sess["dt"], age=sess["age"],
        subject=sess["subject"], n_roi=n_roi)])

    slices = load_folder(tmp_path)

    assert len(slices) == 1
    s = slices[0]
    assert s.dt == pytest.approx(0.25)
    stream = next(iter(s.streams.values()))
    # Three ROIs survive the round trip, including the silent one.
    assert len(stream.locs) == 3
    assert stream.locs[2].size == 0, "the silent ROI must survive as an empty train"
    # The width the producer sent arrives with its rule attached.
    assert np.isfinite(stream.width[0]).all()
    assert stream.has_width and stream.width_def == import_dandi.WIDTH_DEF
    # An absent peak is `None` on the stream, not a NaN array — `Stream` documents
    # this and `has_peak` is the way to ask. Amplitude, which is not optional on
    # the dataclass, is NaN-filled instead. The two absences are not alike and a
    # consumer that assumes they are will crash on `stream.peak[i]`.
    assert stream.has_peak is False
    assert stream.peak is None
    assert np.isnan(stream.amp[0]).all()


def test_the_folder_is_not_written_where_a_bare_name_would_resolve_it():
    """A foreign corpus under `exports/bugarach/` is one typo from being read as
    this lab's data — the hazard `current_export.toml` exists to close."""
    assert import_dandi.DEFAULT_OUT_SUBPATH[:2] == ("exports", "external")
    assert "bugarach" not in import_dandi.DEFAULT_OUT_SUBPATH
