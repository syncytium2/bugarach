"""Scoring against planted truth.

Unlike the generator, this port IS exact — there is no RNG in the matching rule,
so it transfers literally from `score_coord_detection.m`.

The property worth pinning hardest is greedy-nearest matching. Walking planted
events in time order and taking the first detection within tolerance lets an
early planted event consume a detection that belonged to the next one, turning a
clean result into a spurious miss plus a spurious false alarm.
"""

import numpy as np
import pytest

from bugarach.score import score_detections
from bugarach.simulate import GroundTruth, PlantedEvent, simulate_coordination


def gt_at(times, fracs=None, **params):
    fracs = fracs if fracs is not None else [1.0] * len(times)
    return GroundTruth(
        events=[PlantedEvent(time=float(t), frac=float(f), n_part=10,
                             rois=tuple(range(10)), jitter_sec=0.05)
                for t, f in zip(times, fracs)],
        params=params)


def test_exact_matches():
    s = score_detections(gt_at([10.0, 50.0, 90.0]), [10.0, 50.0, 90.0])
    assert s.n_hit == 3 and s.n_fa == 0
    assert s.recall == 1.0 and s.precision == 1.0 and s.f1 == 1.0


def test_within_tolerance_counts_as_a_hit():
    s = score_detections(gt_at([10.0]), [11.4], tol_sec=1.5)
    assert s.n_hit == 1
    s2 = score_detections(gt_at([10.0]), [11.6], tol_sec=1.5)
    assert s2.n_hit == 0 and s2.n_fa == 1


def test_greedy_nearest_beats_time_order():
    """Two planted events, two detections. Naive in-order matching gives the
    first planted event the detection that clearly belongs to the second."""
    gt = gt_at([10.0, 11.0])
    s = score_detections(gt, [10.9, 10.1], tol_sec=1.5)
    assert s.n_hit == 2, "closest-pair-first should recover both"
    assert s.n_fa == 0
    np.testing.assert_allclose(s.matched, [10.1, 10.9])


def test_one_detection_cannot_satisfy_two_planted_events():
    s = score_detections(gt_at([10.0, 10.5]), [10.2], tol_sec=1.5)
    assert s.n_hit == 1 and s.n_miss == 1 and s.n_fa == 0


def test_extra_detections_are_false_alarms():
    s = score_detections(gt_at([10.0]), [10.0, 200.0, 300.0])
    assert s.n_hit == 1 and s.n_fa == 2
    np.testing.assert_allclose(np.sort(s.fa_times), [200.0, 300.0])


def test_recall_broken_down_by_participation():
    """The headline number hides the thing worth knowing: a detector that finds
    every all-ROI event and nothing at 50% is a different instrument."""
    gt = gt_at([10.0, 50.0, 90.0, 130.0], fracs=[1.0, 1.0, 0.5, 0.5])
    s = score_detections(gt, [10.0, 50.0])          # both 100% events, neither 50%
    assert s.recall_at(1.0) == 1.0
    assert s.recall_at(0.5) == 0.0
    assert s.recall == 0.5


def test_hot_window_false_alarms_are_counted_separately():
    """Detections in the dense-but-random block are the promiscuity signal —
    that block has an elevated rate and no planted events by construction."""
    gt = gt_at([100.0], hot_window=(400.0, 700.0))
    s = score_detections(gt, [100.0, 500.0, 600.0, 900.0])
    assert s.n_fa == 3
    assert s.hot_fa == 2, "only the two inside the window"


def test_distractor_hits_counted_but_not_penalised():
    """A correlated burst is real coincidence that is not a coordinated event.
    Firing on it is recorded, not scored as a false alarm by default."""
    gt = gt_at([100.0])
    gt.distractors = [PlantedEvent(time=500.0, frac=0.5, n_part=15,
                                   rois=tuple(range(15)), jitter_sec=0.3,
                                   kind="distractor")]
    s = score_detections(gt, [100.0, 500.0])
    assert s.distractor_hits == 1
    assert s.n_fa == 1, "still a false alarm against planted truth"


def test_empty_cases_do_not_explode():
    assert score_detections(gt_at([]), []).n_planted == 0
    s = score_detections(gt_at([10.0]), [])
    assert s.n_hit == 0 and s.recall == 0.0
    assert np.isnan(s.precision)
    s2 = score_detections(gt_at([]), [10.0])
    assert s2.n_fa == 1 and np.isnan(s2.recall)


def test_non_finite_detections_are_dropped():
    s = score_detections(gt_at([10.0]), [10.0, np.nan, np.inf])
    assert s.n_detected == 1 and s.n_hit == 1


def test_summary_mentions_the_probe_when_it_fires():
    gt = gt_at([100.0], hot_window=(400.0, 700.0))
    s = score_detections(gt, [100.0, 500.0])
    assert "hot-window FA" in s.summary()


def test_scores_a_real_detector_run():
    from bugarach.detectors.coact import coact_detect
    from bugarach.detectors.rate import recording_extent
    s_, gt = simulate_coordination(seed=3, duration_sec=1200, n_per_level=(4, 4, 4))
    ext = recording_extent(s_)
    tr = [np.asarray(v, dtype=float) for v in s_.streams["events"].locs]
    det = coact_detect(tr, ext, int_win_sec=1.0, alpha=1e-4, n_surrogates=100)
    sc = score_detections(gt, det.onset_sec, tol_sec=2.0)
    assert sc.recall >= 0.9, sc.summary()
