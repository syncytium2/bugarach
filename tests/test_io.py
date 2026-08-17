"""Tests for generic ingestion (foreign single-stream, region-less data) and
the region-optional detection path."""

import warnings
from pathlib import Path

import numpy as np
import pytest

from bugarach.detectors.loco import effective_region_windows, loco_detect
from bugarach.detectors.rate import recording_extent
from bugarach.detectors.sce import sce_detect
from bugarach.io import (TableMissesARecordingWarning, load_events_csv,
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


# ------------------- a recorded ROI that fired nothing (the denominator)

def test_na_time_declares_a_recorded_roi_with_no_events(tmp_path: Path):
    """Five ROIs imaged, three fired. The quiet two are rows with no time, so
    the population is five — not the three the events alone would name."""
    p = tmp_path / "s1.csv"
    p.write_text("roi,time_sec\n"
                 "1,1.0\n1,2.0\n"
                 "2,NA\n"                    # recorded, silent
                 "3,5.0\n"
                 "4,7.0\n4,8.5\n4,9.0\n"
                 "5,\n")                     # recorded, silent (spreadsheet style)
    s = load_events_csv(p)
    assert s.streams["events"].n_rois == 5
    assert s.roi_ids == ["1", "2", "3", "4", "5"]
    assert s.streams["events"].locs[1].size == 0
    assert s.streams["events"].locs[4].size == 0
    assert s.streams["events"].n_events == 6


def test_a_recording_where_nothing_fired_still_loads(tmp_path: Path):
    p = tmp_path / "quiet.csv"
    p.write_text("roi,time_sec,stream\n1,NA,fast\n2,NA,fast\n3,NA,fast\n")
    s = load_events_csv(p)
    assert s.streams["fast"].n_rois == 3
    assert s.streams["fast"].n_events == 0


def test_unparseable_time_is_an_error_naming_the_line(tmp_path: Path):
    p = tmp_path / "s1.csv"
    p.write_text("roi,time_sec\n1,1.0\n2,about noon\n")
    with pytest.raises(ValueError, match="line 3"):
        load_events_csv(p)


# ------------------------------------------------- the folder, one file per slice

def _folder(tmp_path: Path, **files) -> Path:
    d = tmp_path / "export"
    d.mkdir(exist_ok=True)
    for name, text in files.items():
        (d / f"{name}.csv").write_text(text)
    return d


def test_load_folder_one_file_per_recording(tmp_path: Path):
    d = _folder(
        tmp_path,
        # deliberately not alphabetical on disk order of writing
        s2="roi,time_sec\n1,4.0\n2,NA\n",
        s1="roi,time_sec,stream\n1,1.0,fast\n1,2.0,slow\n2,NA,fast\n",
        regions=("slice_id,region_idx,label,start_sec,end_sec\n"
                 "s1,2,TTX,60,120\n"
                 "s1,1,pre-drug,0,60\n"
                 "s2,1,baseline,0,90\n"),
        slices="slice_id,frame_interval_sec,sex\ns1,0.05,F\ns2,0.1,M\n",
    )
    a, b = load_folder(d)

    assert (a.slice_id, b.slice_id) == ("s1", "s2")
    assert sorted(a.streams) == ["fast", "slow"]
    assert a.streams["fast"].n_rois == 2          # ROI 2 recorded, silent
    # treatment windows arrive in the producer's own chronological order
    assert [r.name for r in a.regions] == ["pre-drug", "TTX"]
    assert (a.regions[1].start_sec, a.regions[1].end_sec) == (60.0, 120.0)
    # the sidecar rides along verbatim, interpreted nowhere
    assert a.meta["frame_interval_sec"] == "0.05" and a.meta["sex"] == "F"
    assert b.meta["frame_interval_sec"] == "0.1"
    assert [r.name for r in b.regions] == ["baseline"]


def test_load_folder_needs_only_the_event_files(tmp_path: Path):
    """Each reserved table buys one thing; a folder of event files is valid."""
    d = _folder(tmp_path, s1="roi,time_sec\n1,1.0\n")
    s, = load_folder(d)
    assert s.slice_id == "s1" and s.regions == [] and s.meta == {}


def test_load_folder_reserved_names_are_not_recordings(tmp_path: Path):
    d = _folder(tmp_path,
                s1="roi,time_sec\n1,1.0\n",
                slices="slice_id,frame_interval_sec\ns1,0.05\n",
                regions="slice_id,region_idx,label,start_sec,end_sec\ns1,1,base,0,9\n")
    assert [s.slice_id for s in load_folder(d)] == ["s1"]


def test_load_folder_rejects_a_folder_with_no_recordings(tmp_path: Path):
    d = _folder(tmp_path, slices="slice_id,frame_interval_sec\ns1,0.05\n")
    with pytest.raises(FileNotFoundError, match="no recordings"):
        load_folder(d)
    with pytest.raises(NotADirectoryError):
        load_folder(tmp_path / "nope")


def test_load_folder_ignores_extra_columns(tmp_path: Path):
    """One folder can serve several consumers; anything else is inert here."""
    d = _folder(tmp_path,
                s1="roi,time_sec,amplitude,roi_rejected\n1,1.0,3.4,0\n")
    s, = load_folder(d)
    assert s.streams["events"].n_rois == 1
    np.testing.assert_allclose(s.streams["events"].locs[0], [1.0])


def test_load_folder_rejects_a_label_in_the_region_idx_column(tmp_path: Path):
    """The producer's most likely mistake: the ordering column holding the name.
    It must say so, not raise int() at the reader."""
    d = _folder(tmp_path,
                s1="roi,time_sec\n1,1.0\n",
                regions=("slice_id,region_idx,label,start_sec,end_sec\n"
                         "s1,baseline,baseline,0,60\n"))
    with pytest.raises(ValueError, match="not a 1-based integer"):
        load_folder(d)


# --------------------------------------------- store -> folder -> store, exactly

def test_a_store_round_trips_through_the_folder_contract(tmp_path: Path):
    """Write a real store out as the contract, read it back, and require the
    population and the events to survive intact — silent ROIs included, which
    is the whole reason the NA row exists.

    This doubles as the worked example of a conforming producer, so it sends
    **t50rise**: `time_sec` is when the event began, and in these stores that
    is `t50rise`, not `locs` (the peak). Sending `locs` would round-trip just
    as cleanly and be wrong by ~0.3 s in FAST and ~2 s in SLOW — a silent
    error the format cannot catch, because both are plausible seconds."""
    import csv as _csv

    from bugarach import load_slice

    ref = load_slice(Path(__file__).parent / "fixtures" / "synth_fastcal_s1.mat")
    d = tmp_path / "export"
    d.mkdir()
    with (d / f"{ref.slice_id}.csv").open("w", newline="") as f:
        w = _csv.writer(f)
        w.writerow(["roi", "time_sec", "stream"])
        for sname, st in ref.streams.items():
            for i, onsets in enumerate(st.t50rise):
                roi = ref.roi_ids[i] if ref.roi_ids else str(i + 1)
                onsets = np.sort(onsets[np.isfinite(onsets)])
                if onsets.size == 0:
                    w.writerow([roi, "NA", sname])       # recorded, fired nothing
                for t in onsets:
                    w.writerow([roi, f"{t:.6f}", sname])
    with (d / "regions.csv").open("w", newline="") as f:
        w = _csv.writer(f)
        w.writerow(["slice_id", "region_idx", "label", "start_sec", "end_sec"])
        for idx, r in enumerate(ref.regions, start=1):
            w.writerow([ref.slice_id, idx, r.name, r.start_sec, r.end_sec])

    got, = load_folder(d)
    assert got.slice_id == ref.slice_id
    assert sorted(got.streams) == sorted(ref.streams)
    ref_ids = ref.roi_ids or [str(i + 1) for i in range(ref.fast.n_rois)]
    for sname, rst in ref.streams.items():
        gst = got.streams[sname]
        assert gst.n_rois == rst.n_rois, f"{sname}: population changed"
        assert gst.n_events == rst.n_events, f"{sname}: events changed"
        # compare by ROI identity, not by position: the folder orders ROIs
        # itself, and the contract promises the ids, not an index
        for i, rid in enumerate(ref_ids):
            j = got.roi_ids.index(rid)
            onsets = np.sort(rst.t50rise[i][np.isfinite(rst.t50rise[i])])
            np.testing.assert_allclose(onsets, gst.locs[j], atol=1e-6)
    assert [r.name for r in got.regions] == [r.name for r in ref.regions]


def test_a_table_that_misses_a_recording_is_reported(tmp_path: Path):
    """A typo'd slice_id costs a window or an interval and looks deliberate."""
    d = _folder(tmp_path,
                s1="roi,time_sec\n1,1.0\n",
                regions=("slice_id,region_idx,label,start_sec,end_sec\n"
                         "s7,1,baseline,0,60\n"))
    with pytest.warns(TableMissesARecordingWarning, match="regions.csv"):
        s, = load_folder(d)
    assert s.regions == []


def test_a_table_covering_extra_recordings_is_silent(tmp_path: Path):
    """One batch table may legitimately cover more than this folder holds."""
    d = _folder(tmp_path,
                s1="roi,time_sec\n1,1.0\n",
                regions=("slice_id,region_idx,label,start_sec,end_sec\n"
                         "s1,1,baseline,0,60\n"
                         "s2,1,baseline,0,60\n"))
    with warnings.catch_warnings():
        warnings.simplefilter("error", TableMissesARecordingWarning)
        s, = load_folder(d)
    assert [r.name for r in s.regions] == ["baseline"]


def test_roi_ids_order_numerically_not_lexicographically(tmp_path: Path):
    """ROI 2 before ROI 10 — a lab reading its own ROI list back should not
    have to explain why 10 came second."""
    d = _folder(tmp_path,
                s1="roi,time_sec\n10,1.0\n2,2.0\n1,3.0\n")
    s, = load_folder(d)
    assert s.roi_ids == ["1", "2", "10"]
