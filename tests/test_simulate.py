"""The simulator's contract: determinism, correct ground truth, and data the
detectors can actually find things in.

There is no MATLAB parity test here, deliberately — see the module docstring of
`bugarach.simulate`. The original draws from `poissrnd`, `randn` and `randperm`,
none of which are bit-compatible with numpy's; only `rand` is. So what is pinned
is what a generator actually owes its callers: same seed same output, ground
truth that matches the data, and negatives that stay out of the positives.
"""

import numpy as np
import pytest

from bugarach.detectors.coact import coact_detect
from bugarach.detectors.rate import recording_extent
from bugarach.simulate import GroundTruth, simulate_coordination


def trains_of(slice_, name="events"):
    return [np.asarray(v, dtype=float) for v in slice_.streams[name].locs]


# --------------------------------------------------------------- determinism

def test_same_seed_same_output():
    a, ga = simulate_coordination(seed=7)
    b, gb = simulate_coordination(seed=7)
    for x, y in zip(trains_of(a), trains_of(b)):
        np.testing.assert_array_equal(x, y)
    np.testing.assert_array_equal(ga.times, gb.times)
    assert [e.rois for e in ga.events] == [e.rois for e in gb.events]


def test_different_seeds_differ():
    _, ga = simulate_coordination(seed=1)
    _, gb = simulate_coordination(seed=2)
    assert not np.array_equal(ga.times, gb.times)


def test_seed_none_is_not_pinned():
    _, ga = simulate_coordination(seed=None)
    _, gb = simulate_coordination(seed=None)
    assert not np.array_equal(ga.times, gb.times)


# ------------------------------------------------------------- ground truth

def test_ground_truth_matches_the_data():
    """Every planted event should have a real onset near it in each participating
    ROI — the label has to describe the data, or nothing downstream means anything."""
    s, gt = simulate_coordination(seed=5, jitter_sec=0.05, grid_sec=0.1)
    tr = trains_of(s)
    for e in gt.events:
        for r in e.rois:
            assert np.min(np.abs(tr[r] - e.time)) <= 0.5, (
                f"ROI {r} has no onset near planted event at {e.time:.2f}")


def test_participation_counts_and_mask_agree():
    s, gt = simulate_coordination(seed=5, n_roi=20, participation=(1.0, 0.5),
                                  n_per_level=(2, 2))
    mask = gt.participation_mask(20)
    assert mask.shape == (len(gt.events), 20)
    for i, e in enumerate(gt.events):
        assert mask[i].sum() == e.n_part == len(e.rois)
        assert e.n_part == max(1, round(e.frac * 20))


def test_events_are_sorted_and_separated():
    _, gt = simulate_coordination(seed=11, min_sep_sec=15.0)
    t = gt.times
    assert np.all(np.diff(t) > 0), "events must be time-sorted"
    assert np.all(np.diff(t) >= 15.0 - 1e-9), "min_sep_sec violated"


def test_non_participants_are_not_labelled():
    _, gt = simulate_coordination(seed=5, n_roi=30, participation=(0.5,),
                                  n_per_level=(3,))
    for e in gt.events:
        assert len(set(e.rois)) == len(e.rois), "duplicate participants"
        assert e.n_part < 30, "a 50% event should not include every ROI"


# ------------------------------------------------------- variable timing

def test_interval_cv_controls_regularity():
    """Evenly spaced events are a shortcut a model can learn instead of the
    signal, so irregularity has to be a knob — and the default must not be 0."""
    _, regular = simulate_coordination(seed=4, interval_cv=0.0, n_per_level=(6, 6, 6))
    _, varied = simulate_coordination(seed=4, interval_cv=2.0, n_per_level=(6, 6, 6))

    def cv(g):
        d = np.diff(g.times)
        return d.std() / d.mean()

    assert cv(regular) < 1e-9, "interval_cv=0 should give constant spacing"
    assert cv(varied) > 0.3, "interval_cv=2 should give visibly variable spacing"


def test_renewal_is_the_default():
    """A regular default would make every training set predictable from the clock."""
    _, gt = simulate_coordination(seed=4, n_per_level=(6, 6, 6))
    d = np.diff(gt.times)
    assert d.std() / d.mean() > 0.05, "default spacing should not be metronomic"


def test_uniform_spacing_still_available():
    _, gt = simulate_coordination(seed=4, spacing="uniform", min_sep_sec=15.0)
    assert np.all(np.diff(gt.times) >= 15.0 - 1e-9)


def test_rejects_an_unknown_spacing():
    with pytest.raises(ValueError, match="spacing"):
        simulate_coordination(spacing="bogus")


def test_refuses_an_impossible_schedule():
    """Failing loudly beats silently emitting fewer events than asked for."""
    with pytest.raises(ValueError):
        simulate_coordination(duration_sec=60, min_sep_sec=15,
                              n_per_level=(20, 0, 0))


# ------------------------------------------------------------- negatives

def test_distractors_are_tracked_separately():
    """A distractor is real coincidence that is NOT a coordinated event. If it
    leaked into gt.events it would be scored as a target and teach the wrong thing."""
    _, gt = simulate_coordination(seed=9, n_distractors=4, duration_sec=1200)
    assert len(gt.distractors) == 4
    assert all(d.kind == "distractor" for d in gt.distractors)
    assert all(e.kind == "coordinated" for e in gt.events)
    for d in gt.distractors:
        assert not np.any(np.isclose(gt.times, d.time)), "distractor in gt.events"


def test_hot_window_has_no_planted_events():
    """The dense-but-random block exists so a rate-fooled detector fires there.
    A planted event inside it would destroy the probe."""
    hw = (400.0, 700.0)
    _, gt = simulate_coordination(seed=13, duration_sec=1500, hot_window=hw,
                                  hot_rate_hz=0.3, n_per_level=(3, 3, 3))
    assert len(gt.events) == 9, "excluding a window must not silently drop events"
    assert not np.any((gt.times >= hw[0]) & (gt.times <= hw[1]))
    # The gap is padded by min_sep on both sides, so the pair straddling it must
    # still respect the floor — the compress/expand trick has to preserve that.
    assert np.all(np.diff(gt.times) >= 15.0 - 1e-9)


def test_hot_window_actually_raises_the_rate():
    hw = (400.0, 700.0)
    quiet, _ = simulate_coordination(seed=13, duration_sec=1500, n_per_level=(3, 3, 3))
    dense, _ = simulate_coordination(seed=13, duration_sec=1500, hot_window=hw,
                                     hot_rate_hz=0.3, n_per_level=(3, 3, 3))

    def count_in(s):
        return sum(int(np.sum((t >= hw[0]) & (t <= hw[1]))) for t in trains_of(s))

    assert count_in(dense) > count_in(quiet) * 1.5


# ----------------------------------------------------------------- shape

def test_single_stream_by_default():
    s, _ = simulate_coordination(seed=1)
    assert list(s.streams) == ["events"]


def test_two_stream_form_is_the_duplicate():
    """The MATLAB original emits fast and slow byte-identical; duplicating one
    stream reproduces that exactly, so two-stream is a special case not a mode."""
    s, _ = simulate_coordination(seed=1, streams=("fast", "slow"))
    assert list(s.streams) == ["fast", "slow"]
    for a, b in zip(s.fast.locs, s.slow.locs):
        np.testing.assert_array_equal(a, b)


def test_onsets_land_on_the_grid():
    s, _ = simulate_coordination(seed=1, grid_sec=0.1)
    for t in trains_of(s):
        if t.size:
            np.testing.assert_allclose(t, np.round(t / 0.1) * 0.1, atol=1e-9)


def test_onsets_stay_inside_the_recording():
    s, _ = simulate_coordination(seed=2, duration_sec=600)
    for t in trains_of(s):
        if t.size:
            assert t.min() >= -1e-9 and t.max() <= 600 + 1e-9


def test_rejects_mismatched_participation_lengths():
    with pytest.raises(ValueError, match="same length"):
        simulate_coordination(participation=(1.0, 0.5), n_per_level=(3,))


# ------------------------------------------------------------ integration

def test_a_detector_finds_what_was_planted():
    """The end-to-end claim: simulated data goes into a real detector with no
    adapter, and the planted events come back out."""
    s, gt = simulate_coordination(seed=3, duration_sec=1200, n_per_level=(4, 4, 4),
                                  jitter_sec=0.05)
    ext = recording_extent(s)
    det = coact_detect(trains_of(s), ext, int_win_sec=1.0, alpha=1e-4,
                       n_surrogates=200)
    found = sum(np.any(np.abs(det.onset_sec - e.time) <= 2.0) for e in gt.events)
    assert found >= len(gt.events) - 1, (
        f"only {found}/{len(gt.events)} planted events recovered")


def test_ground_truth_is_a_ground_truth_object():
    _, gt = simulate_coordination(seed=1)
    assert isinstance(gt, GroundTruth)
    assert gt.params["seed"] == 1
    assert gt.params["spacing"] == "renewal"
