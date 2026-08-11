"""Tests for generic ingestion (foreign single-stream, region-less data) and
the region-optional detection path."""

from pathlib import Path

import numpy as np
import pytest

from bugarach.detectors.loco import effective_region_windows, loco_detect
from bugarach.detectors.rate import recording_extent
from bugarach.detectors.sce import sce_detect
from bugarach.io import load_events_csv, slice_from_events


def _single_stream_events(n_rois=6, seed=11):
    rng = np.random.RandomState(seed)
    events = [np.sort(rng.uniform(0, 400, 25)) for _ in range(n_rois)]
    for e in events:                      # plant a synchronous burst at t=200
        e[np.argmin(np.abs(e - 200))] = 200.0 + rng.uniform(0, 0.05)
    return events


def test_single_stream_region_less_slice():
    s = slice_from_events(_single_stream_events(), slice_id="foreign")
    assert list(s.streams) == ["events"]
    assert s.regions == []
    assert s.streams["events"].n_rois == 6
    with pytest.raises(KeyError):
        _ = s.fast                        # canonical accessor absent, loudly


def test_effective_region_windows_fallback():
    s = slice_from_events(_single_stream_events())
    ext = recording_extent(s)
    rw = effective_region_windows(s, ext)
    assert len(rw) == 1
    assert rw[0].label == "recording"
    assert (rw[0].win_start, rw[0].win_end) == ext


def test_region_less_sce_analyzes_whole_recording():
    s = slice_from_events(_single_stream_events())
    det = sce_detect(s, bin_width_sec=1.0, n_surrogates=50, min_rois=4,
                     rng_seed=5, emit_signal=True)
    res = det.streams["events"]
    assert res.signal.t.size > 0, "regional pass must cover the extent"
    hits = (res.onset_sec >= 199.0) & (res.onset_sec <= 201.0)
    assert hits.any(), "planted burst not detected on region-less data"
    assert all(r == "recording" for r in res.region)


def test_region_less_loco_runs_generically():
    s = slice_from_events(_single_stream_events())
    det = loco_detect(s, bin_width_sec=1.0, context_win_sec=60.0,
                      thr_step_sec=30.0, merge_gap_sec=2.0,
                      n_surrogates=30, min_rois=4, rng_seed=5)
    assert list(det.streams) == ["events"]
    res = det.streams["events"]
    hits = (res.onset_sec >= 199.0) & (res.onset_sec <= 201.0)
    assert hits.any()


def test_per_stream_param_dict_and_errors():
    s = slice_from_events({"a": [[1.0, 2.0]] * 3, "b": [[1.5]] * 3})
    det = loco_detect(s, bin_width_sec={"a": 1.0, "b": 2.0},
                      context_win_sec=30.0, thr_step_sec=15.0,
                      merge_gap_sec=2.0, n_surrogates=5, min_rois=2,
                      rng_seed=1)
    assert set(det.streams) == {"a", "b"}
    with pytest.raises(ValueError, match="missing streams"):
        loco_detect(s, bin_width_sec={"a": 1.0}, n_surrogates=5, rng_seed=1)
    with pytest.raises(ValueError, match="scalar"):
        loco_detect(s, bin_width_sec=(1.0, 2.0, 3.0), n_surrogates=5,
                    rng_seed=1)


def test_streams_must_be_index_aligned():
    with pytest.raises(ValueError, match="index-aligned"):
        slice_from_events({"a": [[1.0]], "b": [[1.0], [2.0]]})


def test_csv_roundtrip(tmp_path: Path):
    p = tmp_path / "events.csv"
    p.write_text(
        "time_sec,roi\n"
        "1.5,cell_b\n"
        "0.5,cell_a\n"
        "2.5,cell_a\n"
        "3.5,cell_b\n")
    s = load_events_csv(p)
    assert s.slice_id == "events"
    assert list(s.streams) == ["events"]
    assert s.roi_ids == ["cell_a", "cell_b"]
    np.testing.assert_allclose(s.streams["events"].locs[0], [0.5, 2.5])
    np.testing.assert_allclose(s.streams["events"].locs[1], [1.5, 3.5])


def test_csv_multistream(tmp_path: Path):
    p = tmp_path / "multi.csv"
    p.write_text(
        "time_sec,roi,stream\n"
        "1.0,r1,alpha\n"
        "2.0,r1,beta\n"
        "3.0,r2,alpha\n")
    s = load_events_csv(p, stream_col="stream")
    assert sorted(s.streams) == ["alpha", "beta"]
    assert s.streams["alpha"].n_rois == 2      # index-aligned union of ROIs
    assert s.streams["beta"].locs[0].size == 1
    assert s.streams["beta"].locs[1].size == 0


def test_csv_missing_columns(tmp_path: Path):
    p = tmp_path / "bad.csv"
    p.write_text("a,b\n1,2\n")
    with pytest.raises(ValueError, match="must have columns"):
        load_events_csv(p)
