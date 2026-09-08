"""The before/after figure's numbers: a rate per scored window, paired per recording.

Four claims a reader cannot check from the picture:

* the y value is calls inside the period divided by the length of the window the
  folder was SCORED on — resolved by `detect_folder.folder_analysis_windows`, the
  same function `bugarach detect` used, so numerator and denominator come from one
  code path (murderboard 2026-09-07, role 7: the first version re-derived the
  window and would have accepted half a window);
* both periods are named by the caller — the contract reserves no baseline slot;
* a recording lacking either period is skipped and named, never drawn at zero;
* a detector with no calls in a period is a zero, not a missing point, and a call
  outside every declared period is counted nowhere.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "src"))

import make_before_after_figure as mod  # noqa: E402
from bugarach.emit import NA  # noqa: E402

SLICES = ("slice_id,frame_interval_sec,group_id\n"
          "s1,0.1,MALE\n"
          "s2,0.1,MALE\n")
REGIONS = (
    "slice_id,region_idx,label,start_sec,end_sec,analysis_start_sec,analysis_end_sec\n"
    "s1,1,baseline,0,1200,0,1200\n"
    "s1,2,APV+CNQX+GZ,1200,2820,1320,2820\n"
    "s1,3,high K+,2820,3300,2820,3300\n"
    "s2,1,baseline,0,1200,,\n"
    "s2,2,washout,1200,2400,,\n"
)
#: s1 pins the producer's analysis windows on every period (the loader refuses a
#: half-pinned recording — one policy per recording); s2 sends raw bounds only.
EVENTS = ("roi,time_sec,stream\n"
          "1,10.0,fast\n1,1500.0,fast\n2,20.0,fast\n1,30.0,slow\n2,2900.0,fast\n")
DETECTIONS = (
    "slice_id,stream,detector,mode,region_idx,region_label,onset_sec\n"
    "s1,fast,coact,threshold,1,baseline,10\n"
    "s1,fast,coact,threshold,1,baseline,20\n"
    "s1,fast,coact,threshold,2,APV+CNQX+GZ,1500\n"
    "s1,slow,coact,threshold,1,baseline,30\n"
    "s1,fast,loco,threshold,3,high K+,2900\n"
    f"s1,fast,rate,threshold,{NA},{NA},40\n"
    "s2,fast,coact,threshold,1,baseline,5\n"
)


def _write(tmp_path: Path):
    # The folder and the run output live apart, as they do in a real run: a
    # `detections.csv` inside the folder would be read as a recording.
    folder = tmp_path / "folder"
    folder.mkdir()
    (folder / "slices.csv").write_text(SLICES)
    (folder / "regions.csv").write_text(REGIONS)
    for sid in ("s1", "s2"):
        (folder / f"{sid}.csv").write_text(EVENTS)
    run = tmp_path / "run"
    run.mkdir()
    det = run / "detections.csv"
    det.write_text(DETECTIONS)
    return folder, det


def test_rates_are_per_minute_of_the_scored_window(tmp_path):
    folder, det = _write(tmp_path)
    rows, detectors, streams, missing = mod.rates(folder, det, baseline="baseline", treatment="APV+CNQX+GZ")
    by = {(d, s, sid): (b, t) for d, s, sid, b, t, _, _ in rows}
    # baseline: 2 calls / 20 min; treatment: 1 call / (2820-1320)/60 = 25 min —
    # the producer's analysis windows, not the raw periods
    assert by[("coact", "fast", "s1")] == pytest.approx((2 / 20.0, 1 / 25.0))
    assert streams == ["fast", "slow"]


def test_a_recording_without_the_treatment_is_skipped_and_named(tmp_path):
    folder, det = _write(tmp_path)
    rows, _, _, missing = mod.rates(folder, det, baseline="baseline", treatment="APV+CNQX+GZ")
    assert missing == ["s2"]
    assert not any(sid == "s2" for _, _, sid, _, _, _, _ in rows)


def test_both_periods_are_named_by_the_caller(tmp_path):
    """No slot is assumed: asking for a period the folder does not have draws nothing."""
    folder, det = _write(tmp_path)
    rows, _, _, missing = mod.rates(folder, det, baseline="baseline", treatment="TTX")
    assert rows == [] and missing == ["s1", "s2"]
    # and the same call with the periods swapped is a different figure, not an error
    rows, _, _, _ = mod.rates(folder, det, baseline="APV+CNQX+GZ", treatment="baseline")
    by = {(d, s, sid): (b, t) for d, s, sid, b, t, _, _ in rows}
    assert by[("coact", "fast", "s1")] == pytest.approx((1 / 25.0, 2 / 20.0))


def test_no_calls_is_a_zero_not_a_gap(tmp_path):
    folder, det = _write(tmp_path)
    rows, detectors, _, _ = mod.rates(folder, det, baseline="baseline", treatment="APV+CNQX+GZ")
    by = {(d, s, sid): (b, t) for d, s, sid, b, t, _, _ in rows}
    # loco called only in high K+, which is neither period drawn
    assert by[("loco", "fast", "s1")] == (0.0, 0.0)
    # a detection outside every declared period (region_idx NA) is not counted anywhere
    assert by[("rate", "fast", "s1")] == (0.0, 0.0)
    assert "loco" in detectors and "rate" in detectors
    # detectors come out in the glossary's order, not the file's
    assert detectors == [d for d in mod.DETECTORS if d in ("rate", "coact", "loco")]
