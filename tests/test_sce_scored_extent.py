"""Binned SCE is scored over the bin its call was made on, not over its event spread.

``sce_detect`` reports a call with ``onset_sec`` at its bin's start and
``width_sec = tlast - tfirst``, the spread of the events inside the bin. That is
the ``generate_sce`` contract and the parity fixtures lock it. Read as a span,
the pair describes a stretch that starts at the bin edge and is only as long as
the event spread — so a coordinated event late in its bin sat outside the stretch
its own call was scored over, and read as a miss **and** a false alarm.

Tony ruled on 2026-09-16 to give the scorer the bin's own extent and leave the
detector's outputs alone. ``SceStream.extent_sec`` carries it and
``bugarach.score.score_stream`` prefers it
(``docs/todo/2026-09-15-binned-sce-calls-are-scored-over-the-wrong-stretch.md``).
"""

from __future__ import annotations

import numpy as np
import pytest

from bugarach.detectors.sce import sce_detect
from bugarach.io import slice_from_events
from bugarach.score import TOL_SEC, score_detections, score_stream
from bugarach.simulate import GroundTruth, PlantedEvent

N_ROI = 20
DURATION = 600.0
BIN = 10.0
LATE = 58.0          # 8 s into the bin that starts at 50 s
PARTICIPANTS = 15


def _gt(times):
    return GroundTruth(events=[
        PlantedEvent(time=float(t), frac=PARTICIPANTS / N_ROI,
                     n_part=PARTICIPANTS, rois=tuple(range(PARTICIPANTS)),
                     jitter_sec=0.1) for t in times])


def _slice(event_times):
    """Twenty ROIs, each with three background events scattered over 100-550 s
    (clear of every bin these tests plant into), and every time in
    ``event_times`` joined by the first fifteen ROIs within ±0.2 s.

    ROI 0 carries events at exactly 0 s and 600 s, so the recording extent — and
    with it the bin grid — starts at zero and the bin boundaries are known."""
    rng = np.random.RandomState(5)
    trains = []
    for r in range(N_ROI):
        v = list(rng.uniform(100.0, 550.0, size=3))   # clear of every test bin
        if r < PARTICIPANTS:
            for t in event_times:
                v.append(t + rng.uniform(-0.2, 0.2))
        if r == 0:
            v += [0.0, DURATION]
        trains.append(np.sort(np.asarray(v)))
    return slice_from_events(trains, dt=0.1)


def _detect(event_times, **kw):
    s = _slice(event_times)
    return sce_detect(s, bin_width_sec=BIN, n_surrogates=200, rng_seed=3,
                      **kw).streams["events"]


def _call_on(det, t):
    """Index of the call whose bin run contains ``t``."""
    ends = det.onset_sec + det.extent_sec
    idx = np.flatnonzero((det.onset_sec <= t) & (t <= ends))
    assert idx.size == 1, (
        f"expected exactly one call over {t:g} s, found {idx.size} — onsets "
        f"{det.onset_sec.tolist()}")
    return int(idx[0])


def test_a_late_event_is_a_hit_over_its_bin_and_was_a_miss_over_its_spread():
    """The regression. Same detection, same planted event, two readings."""
    det = _detect([LATE])
    gt = _gt([LATE])
    i = _call_on(det, LATE)
    assert det.onset_sec[i] == pytest.approx(50.0), "the bin starts at 50 s"
    assert det.width_sec[i] < 1.0, "the event spread is under a second"

    # the stretch as the scorer used to read it: [50, 50 + spread], nowhere near 58
    old = score_detections(gt, det.onset_sec, widths=det.width_sec)
    assert old.n_hit == 0 and old.n_fa >= 1, (
        "over the event spread the call should score as a miss plus a false "
        "alarm — the defect this test pins")

    new = score_stream(gt, det)
    assert new.n_hit == 1, "over its own bin the call contains the event it was made on"
    assert new.n_detected == old.n_detected, "rescoring must not add or drop calls"
    assert new.n_fa == old.n_fa - 1, "the false alarm was the same call as the miss"


def test_the_extent_is_the_bin_not_the_width():
    det = _detect([LATE])
    i = _call_on(det, LATE)
    assert det.extent_sec[i] == pytest.approx(BIN)
    assert det.extent_sec.shape == det.onset_sec.shape


def test_the_detector_contract_is_untouched():
    """onset stays the bin edge and width stays the event spread — the parity
    fixtures in test_sce_detect.py lock both, and detections.csv writes them."""
    det = _detect([LATE])
    i = _call_on(det, LATE)
    assert det.width_kind == "tightness"
    assert det.onset_sec[i] == pytest.approx(50.0)
    assert det.width_sec[i] < 1.0


def test_a_merged_run_is_scored_over_every_bin_in_it():
    """With merging on, adjacent supra-threshold bins become one call; its
    stretch runs from the first bin's start to the last bin's end."""
    det = _detect([48.0, 52.0], merge_gap_sec=10.0)
    i = _call_on(det, 52.0)
    assert det.onset_sec[i] == pytest.approx(40.0)
    assert det.extent_sec[i] == pytest.approx(2 * BIN)
    assert score_stream(_gt([48.0, 52.0]), det).n_hit == 1, \
        "one call, two planted events — matching stays one-to-one"


def test_a_partial_last_bin_ends_at_the_window():
    """600 s / 10 s is exact, so move the extent to 605 s: the last bin runs
    600-610 on paper but the analysis window ends at 605."""
    s = _slice([602.0])
    s_trains = [np.append(v, 605.0) if r == 0 else v
                for r, v in enumerate(s.streams["events"].locs)]
    det = sce_detect(slice_from_events(s_trains, dt=0.1), bin_width_sec=BIN,
                     n_surrogates=200, rng_seed=3).streams["events"]
    i = _call_on(det, 602.0)
    assert det.onset_sec[i] == pytest.approx(600.0)
    assert det.onset_sec[i] + det.extent_sec[i] == pytest.approx(605.0)


def test_peak_mode_extent_is_its_width():
    """Peak mode's width is already the half-prominence stretch of the call."""
    det = _detect([LATE], detection_mode="peak")
    assert det.n_events >= 1
    assert np.array_equal(det.extent_sec, det.width_sec, equal_nan=True)


def test_a_result_without_an_extent_is_scored_on_its_width():
    """Every other detector: nothing changes for a result that does not declare one."""

    class Plain:
        onset_sec = np.array([50.0])
        width_sec = np.array([0.4])

    gt = _gt([LATE])
    assert score_stream(gt, Plain()).n_hit == 0
    assert score_detections(gt, [50.0], widths=[0.4], tol_sec=TOL_SEC).n_hit == 0
