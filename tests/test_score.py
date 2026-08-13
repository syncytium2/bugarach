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

from bugarach.score import score_detections, score_stream
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


# --- detections are intervals ----------------------------------------------
#
# A binned detector reports the bin, not the instant. Scoring its bin edge as if
# it were an onset measures it at a resolution it never claimed to have.

def test_a_span_containing_the_event_is_a_hit_at_any_tolerance():
    """SCE's failure in one line: the bin edge is 3.3 s early, the bin is not."""
    s = score_detections(gt_at([43.3]), [40.0], widths=[10.0], tol_sec=1.5)
    assert s.n_hit == 1 and s.n_fa == 0


def test_the_same_detection_misses_when_scored_as_a_point():
    s = score_detections(gt_at([43.3]), [40.0], tol_sec=1.5)
    assert s.n_hit == 0 and s.n_fa == 1


def test_tolerance_still_applies_outside_the_span():
    """The span is not a licence to match anything — tol_sec is measured from
    the nearer edge, so a span that falls short by more than tol still misses."""
    gt = gt_at([60.0])
    assert score_detections(gt, [40.0], widths=[19.0], tol_sec=1.5).n_hit == 1
    assert score_detections(gt, [40.0], widths=[17.0], tol_sec=1.5).n_hit == 0


def test_omitting_widths_is_point_matching():
    """The generalization must not move the onset-resolution detectors."""
    gt = gt_at([10.0, 11.0])
    a = score_detections(gt, [10.9, 10.1], tol_sec=1.5)
    b = score_detections(gt, [10.9, 10.1], widths=[0.0, 0.0], tol_sec=1.5)
    assert a.n_hit == b.n_hit == 2
    np.testing.assert_allclose(a.matched, b.matched)


def test_a_wide_span_cannot_claim_two_events():
    """Greedy consumption still holds: one detection, one event, even when the
    span covers both. The second is a miss, not a second hit."""
    s = score_detections(gt_at([100.0, 105.0]), [98.0], widths=[10.0])
    assert s.n_hit == 1 and s.n_miss == 1 and s.n_fa == 0


def test_overlapping_spans_go_to_the_one_centred_on_the_event():
    """Two spans both contain the event and tie at gap 0. The tie-break is
    distance to the span's midpoint, so the better-centred detection wins
    instead of whichever happened to start earlier."""
    s = score_detections(gt_at([50.0]), [41.0, 48.0], widths=[10.0, 4.0])
    np.testing.assert_allclose(s.matched, [48.0])


def test_widths_ride_along_with_the_sort():
    """Onsets are sorted internally; widths are per-detection, so a width that
    stayed put would be paired with its neighbour's span."""
    # unsorted: the 10 s span belongs to the detection at 40, not the one at 200
    s = score_detections(gt_at([43.3]), [200.0, 40.0], widths=[0.0, 10.0])
    assert s.n_hit == 1 and s.n_fa == 1


def test_non_finite_and_negative_widths_are_treated_as_points():
    s = score_detections(gt_at([10.0, 50.0]), [10.0, 50.0],
                         widths=[np.nan, -5.0])
    assert s.n_hit == 2


def test_widths_must_be_column_aligned():
    with pytest.raises(ValueError, match="column-aligned"):
        score_detections(gt_at([10.0]), [10.0, 20.0], widths=[1.0])


def test_a_straddling_false_alarm_counts_in_the_hot_window():
    """A span that starts before the dense block and runs into it was still
    fired inside it — the probe counts overlap, not left-edge containment."""
    gt = gt_at([100.0], hot_window=(400.0, 700.0))
    s = score_detections(gt, [100.0, 390.0], widths=[0.0, 20.0])
    assert s.n_fa == 1 and s.hot_fa == 1


def test_distractors_are_matched_by_span_too():
    gt = gt_at([100.0])
    gt.distractors = [PlantedEvent(time=505.0, frac=0.5, n_part=15,
                                   rois=tuple(range(15)), jitter_sec=0.3,
                                   kind="distractor")]
    assert score_detections(gt, [100.0, 500.0]).distractor_hits == 0
    s = score_detections(gt, [100.0, 500.0], widths=[0.0, 10.0])
    assert s.distractor_hits == 1


def test_the_binned_detector_is_scored_as_the_instrument_it_is():
    """The regression this whole rule exists for. SCE bins at 10 s and reports
    the bin's left edge; scored as points it read 0.00 recall on detections that
    each spanned a planted event, while LoCo — which reports true onsets — is
    unmoved by the change. Both halves matter: the fix must lift SCE without
    inflating anything else."""
    from bugarach.detectors.loco import loco_detect
    from bugarach.detectors.sce import sce_detect
    s_, gt = simulate_coordination(seed=3)

    sce = sce_detect(s_).streams["events"]
    assert score_detections(gt, sce.onset_sec).recall == 0.0, "the old reading"
    assert score_detections(gt, sce.onset_sec, widths=sce.width_sec).recall >= 0.85

    loco = loco_detect(s_).streams["events"]
    points = score_detections(gt, loco.onset_sec)
    spans = score_detections(gt, loco.onset_sec, widths=loco.width_sec)
    assert points.n_hit == spans.n_hit and points.n_fa == spans.n_fa


def test_score_stream_reads_the_spans_itself():
    """The bench should not have to remember widths= — the failure it prevents
    is silent, so the short call has to be the correct one."""
    from bugarach.detectors.sce import sce_detect
    s_, gt = simulate_coordination(seed=3)
    sce = sce_detect(s_).streams["events"]
    assert score_stream(gt, sce).recall == \
        score_detections(gt, sce.onset_sec, widths=sce.width_sec).recall


def test_score_stream_handles_the_other_field_convention():
    """RateDetect and spike-sync say locs/widths, not onset_sec/width_sec."""
    from bugarach.detectors.rate import recording_extent, stream_trains
    from bugarach.detectors.sync import sync_detect
    s_, gt = simulate_coordination(seed=3)
    ext = recording_extent(s_)
    det = sync_detect(stream_trains(s_.streams["events"], ext), ext,
                      tau_max=0.25, max_gap=0.5)
    assert score_stream(gt, det).n_detected == np.isfinite(det.locs).sum()


def test_score_stream_refuses_something_that_is_not_a_detection():
    with pytest.raises(TypeError, match="no detection times"):
        score_stream(gt_at([10.0]), object())


def _all_six(s):
    """Every detector on one single-stream slice. Two call shapes, two field
    conventions — score_stream absorbs both, which is the point of it."""
    from bugarach.detectors.cicada import cicada_detect
    from bugarach.detectors.coact import coact_detect
    from bugarach.detectors.loco import loco_detect
    from bugarach.detectors.rate import rate_detect, recording_extent, stream_trains
    from bugarach.detectors.sce import sce_detect
    from bugarach.detectors.sync import sync_detect
    ext = recording_extent(s)
    tr = stream_trains(s.streams["events"], ext)
    return {
        "loco": loco_detect(s).streams["events"],
        "cicada": cicada_detect(s).streams["events"],
        "sce": sce_detect(s).streams["events"],
        "coact": coact_detect(tr, ext),
        "rate": rate_detect(tr, ext),
        "sync": sync_detect(tr, ext, tau_max=0.25, max_gap=0.5),
    }


@pytest.mark.parametrize("name", ["loco", "cicada", "sce", "coact", "rate", "sync"])
def test_spans_reclassify_but_never_invent(name):
    """The control on the interval rule, across every detector rather than the
    convenient three.

    Scoring by span must not be a tolerance quietly loosened for everyone. Two
    properties say it isn't: the detection count is untouched (no detector gains
    events by being scored differently), and hits only ever go up, by a
    detection whose own span reached an event the point rule placed just out of
    reach. Measured when this landed: SCE 0.08-0.38 F1 to 0.77-0.97, coact
    +1 hit on 3 seeds in 7, and loco / cicada / rate / sync identical.

    A regression here means the rule started matching on something other than
    the detector's own claimed extent.
    """
    s_, gt = simulate_coordination(seed=3)
    det = _all_six(s_)[name]
    onsets = getattr(det, "onset_sec", None)
    onsets = det.locs if onsets is None else onsets

    points = score_detections(gt, onsets)
    spans = score_stream(gt, det)

    assert spans.n_detected == points.n_detected, "spans must not add detections"
    assert spans.n_hit >= points.n_hit, "spans must not lose a hit"
    assert spans.n_hit + spans.n_fa == points.n_hit + points.n_fa, \
        "every detection is still either a hit or a false alarm"


def test_only_the_binned_detector_moves_much():
    """SCE is the one the point rule misread badly; the rest were already being
    scored at roughly the right resolution. If a second detector ever swings
    like SCE did, its reported resolution has changed and the bench's numbers
    need re-reading before they are believed."""
    s_, gt = simulate_coordination(seed=3)
    for name, det in _all_six(s_).items():
        onsets = getattr(det, "onset_sec", None)
        onsets = det.locs if onsets is None else onsets
        gained = score_stream(gt, det).n_hit - score_detections(gt, onsets).n_hit
        if name == "sce":
            assert gained >= 10, "the whole reason the rule exists"
        else:
            assert gained <= 1, f"{name} gained {gained} hits — check its width_kind"
