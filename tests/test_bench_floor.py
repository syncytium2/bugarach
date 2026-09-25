"""ADR-0008's floor on the bench, as ADR-0009 applies it (the final-parameters night, 2026-09-25).

Each recording's floor comes from its own events (`bench.recording_floor`), sets the participation
minimum of every detector that has one (`bench.run_detector`), and makes planted events under it
"don't care" in the score (`score.score_detections`). The search no longer walks `min_rois` or
SPIKE-synch's `min_n`, the context grids run 20–120 s, and a proposal left at a grid edge or at the
extension cap is marked unbracketed.

The recordings here are built without the elevated-rate stretch (`hot_window=None`), which is the
bench ADR-0009 decision 1 describes, so these tests hold whether or not that change has landed.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

from bugarach import bench, bench_combined, bench_slow
from bugarach.score import score_detections, score_stream
from bugarach.simulate import GroundTruth, PlantedEvent

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import detect_with_floors as dwf  # noqa: E402
import score_bench_candidates as sbc  # noqa: E402
import search_all_settings as S  # noqa: E402

NO_STRETCH = dict(hot_window=None, hot_rate_hz=0.0, ramp_sec=0.0)


@pytest.fixture(scope="module")
def recording():
    return bench.make_recording("baseline_busy", 1, **NO_STRETCH)


def _gt(n_parts, floor=None):
    events = [PlantedEvent(time=100.0 * (i + 1), frac=n / 30, n_part=n, rois=tuple(range(n)),
                           jitter_sec=0.1) for i, n in enumerate(n_parts)]
    params = {} if floor is None else {"event_floor": floor}
    return GroundTruth(events=events, params=params)


# ------------------------------------------------------------------ the recording's floor

def test_every_bench_recording_carries_its_own_floor_of_at_least_three(recording):
    s, gt = recording
    f = bench.recording_floor(s)
    assert gt.params["event_floor"] == f.floor >= 3
    assert gt.params["event_floor_detail"]["draws"] >= 1000


def test_the_floor_is_the_same_for_the_same_recording_in_a_fresh_process_cache(recording,
                                                                                  monkeypatch,
                                                                                  tmp_path):
    s, gt = recording
    monkeypatch.setattr(bench, "_FLOORS", {})
    monkeypatch.setenv(bench.FLOOR_CACHE_ENV, str(tmp_path))
    first = bench.recording_floor(s)
    assert list(tmp_path.glob("*.json")), "the floor is written to the shared cache"
    monkeypatch.setattr(bench, "_FLOORS", {})
    again = bench.recording_floor(s)               # read back from the file
    assert again == first and again.floor == gt.params["event_floor"]


def test_slow_and_combined_recordings_carry_theirs_too():
    for b in (bench_slow, bench_combined):
        s, gt = b.make_recording("baseline_quiet", 2, **NO_STRETCH)
        assert gt.params["event_floor"] == bench.recording_floor(s).floor >= 3


def test_the_switch_turns_the_floor_off(monkeypatch):
    monkeypatch.setenv(bench.FLOOR_SWITCH_ENV, "off")
    s, gt = bench.make_recording("baseline_quiet", 3, **NO_STRETCH)
    assert "event_floor" not in gt.params


# ------------------------------------------------------------------ the detectors

@pytest.mark.parametrize("name", ["coact", "sync"])
def test_run_detector_sets_the_participation_minimum_to_the_floor(recording, name):
    s, _ = recording
    k = bench.recording_floor(s).floor
    setting = bench.FLOORED_SETTING[name]
    got = bench.run_detector(name, s)
    want = bench.run_detector(name, s, floor=False, **{setting: k})
    on = lambda d: np.asarray(getattr(d, "onset_sec", getattr(d, "locs", None)), float)
    np.testing.assert_array_equal(on(got), on(want))


def test_a_caller_cannot_set_what_the_floor_sets(recording):
    s, _ = recording
    with pytest.raises(ValueError, match="ADR-0008"):
        bench.run_detector("coact", s, min_rois=99)


def test_passing_the_operating_point_through_unchanged_is_not_an_override(recording):
    s, _ = recording
    op = dict(bench.OPERATING_POINTS["coact"].params)
    a = bench.run_detector("coact", s, **op)
    b = bench.run_detector("coact", s)
    np.testing.assert_array_equal(a.onset_sec, b.onset_sec)


def test_detectors_without_a_participation_minimum_are_not_touched():
    assert set(bench.FLOORED_SETTING) == {"coact", "loco", "sce", "sync"}
    assert dwf.FLOORED is bench.FLOORED_SETTING


# ------------------------------------------------------------------ the scorer

def test_a_planted_event_under_the_floor_leaves_recall_and_its_call_leaves_precision():
    gt = _gt([3, 6, 10])
    # Calls on all three events, plus one on nothing.
    sc = score_detections(gt, [100.0, 200.0, 300.0, 1000.0], floor=5)
    assert sc.n_planted == 2 and sc.n_hit == 2 and sc.recall == 1.0
    assert sc.n_detected == 3                     # the call on the 3-ROI event is gone
    assert sc.precision == pytest.approx(2 / 3)   # the call on nothing still costs
    assert sc.n_under_floor == 1 and sc.n_dont_care_calls == 1
    assert sc.dont_care_by_frac == {3 / 30: (1, 1)}
    assert sc.floor == 5


def test_an_under_floor_event_missed_is_not_a_miss():
    sc = score_detections(_gt([3, 10]), [200.0], floor=5)
    assert sc.n_miss == 0 and sc.recall == 1.0 and sc.dont_care_by_frac[3 / 30] == (1, 0)


def test_the_floor_is_read_from_the_ground_truth_when_not_passed():
    gt = _gt([3, 10], floor=5)
    assert score_detections(gt, [100.0, 200.0]).n_planted == 1
    # A ground truth without one is scored as it always was.
    assert score_detections(_gt([3, 10]), [100.0, 200.0]).n_planted == 2


def test_pooling_carries_the_under_floor_counts_and_the_floors():
    gt = _gt([3, 6, 10])
    scores = [score_detections(gt, [100.0, 300.0], floor=5),
              score_detections(gt, [300.0], floor=7)]
    r = bench.pool_scores(scores, detector="coact", regime="q")
    assert r.floors == (5, 7)
    rep = bench.under_floor_report(r)
    assert rep["floor"] == bench.FLOOR_LABEL
    assert rep["floors"] == dict(min=5, median=6.0, max=7)
    lvl = rep["by_participation"]
    assert lvl[f"{3 / 30:g}"] == dict(scored=0, under_floor=2, calls_on_under_floor=1)
    assert lvl[f"{6 / 30:g}"] == dict(scored=1, under_floor=1, calls_on_under_floor=0)


def test_a_whole_bench_recording_scores_under_its_floor(recording):
    s, gt = recording
    sc = score_stream(gt, bench.run_detector("coact", s))
    assert sc.floor == gt.params["event_floor"]
    under = sum(e.n_part < sc.floor for e in gt.events)
    assert sc.n_planted == len(gt.events) - under and sc.n_under_floor == under


# ------------------------------------------------------------------ the grids

@pytest.mark.parametrize("b", [bench, bench_slow, bench_combined], ids=lambda m: m.__name__)
def test_no_grid_searches_what_the_floor_sets(b):
    for det, axes in b.FULL_GRIDS.items():
        assert "min_rois" not in axes, det
        assert "min_n" not in axes, det
        setting = bench.FLOORED_SETTING.get(det)
        if setting:
            assert setting in b.NOT_SEARCHED[det], det


@pytest.mark.parametrize("b", [bench, bench_slow, bench_combined], ids=lambda m: m.__name__)
def test_the_context_grids_run_20_to_120_seconds(b):
    assert bench.CONTEXT_GRID_SEC == (20.0, 30.0, 45.0, 60.0, 90.0, 120.0)
    assert tuple(b.FULL_GRIDS["coact"]["context_win_sec"]) == bench.CONTEXT_GRID_SEC
    assert tuple(b.FULL_GRIDS["loco"]["context_win_sec"]) == bench.CONTEXT_GRID_SEC
    assert tuple(b.FULL_GRIDS["rate"]["context_win"]) == bench.CONTEXT_GRID_SEC


def test_a_guard_longer_than_a_quarter_of_its_context_is_not_valid():
    p = dict(bench.OPERATING_POINTS["coact"].params, int_win_sec=2.0, context_win_sec=20.0)
    assert bench.settings_are_valid("coact", {**p, "guard_sec": 5.0})
    assert not bench.settings_are_valid("coact", {**p, "guard_sec": 8.0})
    r = dict(bench.OPERATING_POINTS["rate"].params, rate_win=1.0, context_win=30.0)
    assert not bench.settings_are_valid("rate", {**r, "guard_sec": 8.0})
    assert bench.settings_are_valid("rate", {**r, "guard_sec": 4.0})


# ------------------------------------------------------------------ bracketing

def test_more_extensions_than_the_three_that_left_spike_synch_unbracketed():
    assert S.MAX_EXTENSIONS > 3


def test_an_interior_optimum_is_bracketed():
    grids = {"alpha": [1e-4, 1e-3, 1e-2], "context_win_sec": [20.0, 60.0, 120.0]}
    br = S.bracketing("coact", {"alpha": 1e-3, "context_win_sec": 60.0}, grids, grids, 6)
    assert br == dict(bracketed=True, unbracketed_axes={}, only_at_limits=False)


def test_an_optimum_on_an_edge_or_at_the_cap_is_unbracketed():
    declared = {"alpha": [1e-4, 1e-3], "int_win_sec": [1.0, 2.0]}
    grown = {"alpha": [1e-6, 3e-6, 1e-5, 3e-5, 1e-4, 1e-3], "int_win_sec": [1.0, 2.0]}
    br = S.bracketing("coact", {"alpha": 1e-6, "int_win_sec": 2.0}, grown, declared, 4)
    assert br["bracketed"] is False
    assert br["unbracketed_axes"]["alpha"]["reason"] == "cap"
    assert br["unbracketed_axes"]["int_win_sec"]["reason"] == "edge"


def test_a_value_at_a_hard_limit_is_unbracketed_and_said_to_be_a_limit():
    grids = {"guard_sec": [0.0, 0.5, 1.0]}
    p = dict(guard_sec=0.0)
    br = S.bracketing("coact", p, grids, grids, 6)
    assert br["bracketed"] is False and br["only_at_limits"] is True


def test_a_switched_off_axis_has_no_edge():
    grids = {"peak_prominence": [0.0, 1.0]}
    br = S.bracketing("coact", {"detection_mode": "threshold", "peak_prominence": 0.0},
                      grids, grids, 6)
    assert br["bracketed"] is True


def test_candidates_json_never_calls_an_unbracketed_proposal_adoptable():
    row = dict(gain_vs_shipped=dict(lo=0.01, mid=0.02, hi=0.03))
    assert sbc.adoptable_on_the_search("rounds", row, dict(bracketed=True))
    assert not sbc.adoptable_on_the_search("rounds", row, dict(bracketed=False))
    assert not sbc.adoptable_on_the_search("shipped", row, dict(bracketed=True))
    # A search from before the record cannot say, and is not taken as bracketed.
    old = sbc.bracketing_of({"held_out": {}}, "coact", "rounds")
    assert old["bracketed"] is None
    assert not sbc.adoptable_on_the_search("rounds", row, old)


def test_detect_with_floors_runs_every_window_under_both_floors_and_nothing_pre_adr():
    assert dwf.VARIANTS == ("own_floor", "baseline_floor")
