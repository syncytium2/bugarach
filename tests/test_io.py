"""Tests for generic ingestion (foreign single-stream, region-less data) and
the region-optional detection path."""

from pathlib import Path

import numpy as np
import pytest

from bugarach.detectors.loco import effective_region_windows, loco_detect
from bugarach.detectors.rate import recording_extent
from bugarach.detectors.sce import sce_detect
from bugarach.io import (RosterNotDeclaredWarning, load_events_csv,
                         load_folder, slice_from_events)


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


# ------------------------------------------------- the ROI roster (denominator)

EVENTS_3_OF_5 = ("slice_id,roi,time_sec\n"
                 "s1,1,1.0\ns1,1,2.0\ns1,3,5.0\n"
                 "s1,4,7.0\ns1,4,8.5\ns1,4,9.0\n")


def test_roster_keeps_the_rois_that_fired_nothing(tmp_path: Path):
    """Five cells were recorded, three fired. Without the roster the other two
    vanish and every per-ROI rate is inflated by 5/3."""
    p = tmp_path / "events.csv"
    p.write_text(EVENTS_3_OF_5)

    derived = load_events_csv(p)
    assert derived.streams["events"].n_rois == 3
    assert derived.roi_set_declared is False

    declared = load_events_csv(p, roster=["1", "2", "3", "4", "5"])
    assert declared.streams["events"].n_rois == 5
    assert declared.roi_set_declared is True
    assert declared.roi_ids == ["1", "2", "3", "4", "5"]
    # the silent ones are present and empty, not absent
    assert declared.streams["events"].locs[1].size == 0
    assert declared.streams["events"].locs[4].size == 0
    # and the events did not move
    assert declared.streams["events"].n_events == derived.streams["events"].n_events


def test_roster_order_is_the_producers(tmp_path: Path):
    p = tmp_path / "events.csv"
    p.write_text(EVENTS_3_OF_5)
    s = load_events_csv(p, roster=["5", "4", "3", "2", "1"])
    assert s.roi_ids == ["5", "4", "3", "2", "1"]
    np.testing.assert_allclose(s.streams["events"].locs[1], [7.0, 8.5, 9.0])


def test_event_in_an_undeclared_roi_is_an_error(tmp_path: Path):
    """Two files disagreeing about what was recorded is not something to
    silently resolve in favour of either one."""
    p = tmp_path / "events.csv"
    p.write_text(EVENTS_3_OF_5)
    with pytest.raises(ValueError, match="missing from the roster"):
        load_events_csv(p, roster=["1", "2"])


# ------------------------------------------------------------ the whole folder

def _folder(tmp_path: Path, **files) -> Path:
    d = tmp_path / "export"
    d.mkdir(exist_ok=True)
    for name, text in files.items():
        (d / f"{name}.csv").write_text(text)
    return d


def test_load_folder_reads_the_three_inputs(tmp_path: Path):
    d = _folder(
        tmp_path,
        events=EVENTS_3_OF_5,
        rois="slice_id,roi\ns1,1\ns1,2\ns1,3\ns1,4\ns1,5\n",
        regions=("slice_id,region_idx,label,start_sec,end_sec\n"
                 "s1,2,TTX,60,120\n"
                 "s1,1,pre-drug,0,60\n"),
        slices="slice_id,frame_interval_sec,sex,cohort\ns1,0.05,F,spring\n",
    )
    slices = load_folder(d)
    assert len(slices) == 1
    s = slices[0]

    assert s.slice_id == "s1"
    assert s.streams["events"].n_rois == 5 and s.roi_set_declared is True
    # regions come back in the producer's chronological order, by region_idx
    assert [r.name for r in s.regions] == ["pre-drug", "TTX"]
    assert [r.slot for r in s.regions] == ["1", "2"]
    assert (s.regions[1].start_sec, s.regions[1].end_sec) == (60.0, 120.0)
    # the sidecar is carried verbatim and interpreted nowhere
    assert s.meta["sex"] == "F" and s.meta["cohort"] == "spring"
    assert s.meta["frame_interval_sec"] == "0.05"


def test_load_folder_warns_when_no_roster_is_declared(tmp_path: Path):
    d = _folder(tmp_path, events=EVENTS_3_OF_5)
    with pytest.warns(RosterNotDeclaredWarning, match="lower bound"):
        s, = load_folder(d)
    assert s.streams["events"].n_rois == 3
    assert s.roi_set_declared is False


def test_load_folder_splits_by_slice_and_needs_events(tmp_path: Path):
    d = _folder(tmp_path,
                events="slice_id,roi,time_sec\nb,1,1.0\na,1,2.0\na,2,3.0\n",
                rois="slice_id,roi\na,1\na,2\na,9\nb,1\n")
    a, b = load_folder(d)
    assert (a.slice_id, b.slice_id) == ("a", "b")
    assert a.streams["events"].n_rois == 3     # ROI 9 recorded, never fired
    assert b.streams["events"].n_rois == 1

    with pytest.raises(FileNotFoundError, match="events.csv is required"):
        load_folder(tmp_path / "nothing")


def test_load_folder_ignores_extra_columns(tmp_path: Path):
    """One folder can serve several consumers; whatever else a producer ships
    is inert here rather than an error."""
    d = _folder(tmp_path,
                events="slice_id,roi,time_sec,amplitude,roi_rejected\n"
                       "s1,1,1.0,3.4,0\n",
                rois="slice_id,roi,anything_else\ns1,1,ignored\n")
    s, = load_folder(d)
    assert s.streams["events"].n_rois == 1
    np.testing.assert_allclose(s.streams["events"].locs[0], [1.0])
