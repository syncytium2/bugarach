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


# ------------------------------------------------- heterogeneous background

# A real baseline field is not flat: over 81 windows, 35% of ROIs record no
# event at all and the busiest reaches 486 mHz, while a flat field at the same
# mean leaves 2% silent and tops out near 138. `bg_rate_shape` draws each ROI's
# own rate from a Gamma so both ends move. What is pinned here is the contract,
# not the fitted value — that lives in bench.MEASURED_RATE_SHAPE and is re-derived
# by tools/fit_background_shape.py against the archive.

HETERO = dict(duration_sec=1800.0, n_roi=200, bg_rate_hz=0.01,
              participation=(), n_per_level=(), grid_sec=0.0)


def _rates(slice_, duration):
    return np.array([len(v) / duration for v in trains_of(slice_)])


def test_the_default_background_is_still_flat_and_untouched():
    """None must not consume random numbers, or every existing seed moves."""
    a, _ = simulate_coordination(seed=11)
    b, _ = simulate_coordination(seed=11, bg_rate_shape=None)
    for x, y in zip(trains_of(a), trains_of(b)):
        np.testing.assert_array_equal(x, y)


def test_heterogeneity_changes_the_field_it_is_given():
    flat, _ = simulate_coordination(seed=3, **HETERO)
    hetero, _ = simulate_coordination(seed=3, bg_rate_shape=0.275, **HETERO)
    assert not np.array_equal(_rates(flat, 1800.0), _rates(hetero, 1800.0))


def test_it_produces_silent_rois_without_modelling_them():
    """No zero-inflation term exists — silence falls out of the drawn rate."""
    flat, _ = simulate_coordination(seed=3, **HETERO)
    hetero, _ = simulate_coordination(seed=3, bg_rate_shape=0.275, **HETERO)
    silent_flat = np.mean(_rates(flat, 1800.0) == 0)
    silent_hetero = np.mean(_rates(hetero, 1800.0) == 0)
    assert silent_flat < 0.05
    assert silent_hetero > 0.20


def test_it_produces_the_busy_tail_a_flat_field_cannot():
    flat, _ = simulate_coordination(seed=3, **HETERO)
    hetero, _ = simulate_coordination(seed=3, bg_rate_shape=0.275, **HETERO)
    assert _rates(hetero, 1800.0).max() > 3 * _rates(flat, 1800.0).max()


def test_bg_rate_hz_stays_the_mean():
    """The knob reshapes the field; it does not move its level."""
    hetero, _ = simulate_coordination(seed=5, n_roi=4000, duration_sec=1800.0,
                                      bg_rate_hz=0.01, bg_rate_shape=0.275,
                                      participation=(), n_per_level=(),
                                      grid_sec=0.0)
    assert _rates(hetero, 1800.0).mean() == pytest.approx(0.01, rel=0.1)


def test_a_large_shape_converges_on_the_flat_field():
    """shape -> infinity is the homogeneous generator, so the limit must hold."""
    tight, _ = simulate_coordination(seed=5, bg_rate_shape=5000.0, **HETERO)
    flat, _ = simulate_coordination(seed=5, **HETERO)
    assert np.std(_rates(tight, 1800.0)) == pytest.approx(
        np.std(_rates(flat, 1800.0)), rel=0.35)


def test_same_seed_same_heterogeneous_output():
    a, _ = simulate_coordination(seed=9, bg_rate_shape=0.275, **HETERO)
    b, _ = simulate_coordination(seed=9, bg_rate_shape=0.275, **HETERO)
    for x, y in zip(trains_of(a), trains_of(b)):
        np.testing.assert_array_equal(x, y)


@pytest.mark.parametrize("bad", [0.0, -1.0])
def test_rejects_a_non_positive_shape(bad):
    with pytest.raises(ValueError, match="bg_rate_shape"):
        simulate_coordination(seed=1, bg_rate_shape=bad)


def test_the_shape_is_recorded_in_ground_truth():
    _, gt = simulate_coordination(seed=1, bg_rate_shape=0.275)
    assert gt.params["bg_rate_shape"] == 0.275


def test_turning_heterogeneity_on_redraws_the_schedule():
    """Pinned because a figure assumed the opposite and marked the wrong times.

    The background draw consumes random numbers and its per-ROI counts consume a
    varying quantity more, so at one seed the planted events land elsewhere with
    the knob on. Same as `bg_rate_hz`. Anything comparing a flat run against a
    varied one must read each run's OWN ground truth.
    """
    kw = dict(seed=5, duration_sec=1800.0, n_roi=37, bg_rate_hz=0.0095,
              participation=(0.30, 0.18, 0.10), n_per_level=(4, 4, 4),
              jitter_sec=0.36, min_sep_sec=120.0, interval_cv=1.0)
    _, flat = simulate_coordination(**kw)
    _, varied = simulate_coordination(bg_rate_shape=0.275, **kw)
    assert len(flat.times) == len(varied.times)
    assert not np.allclose(flat.times, varied.times)


def test_it_reaches_the_concentration_a_real_field_has():
    """The point of the knob: one ROI carrying a large share of the recording.

    Real slice 20240813_39 puts 28% of its events in one ROI of 37. A flat field
    at the same mean reaches about 4%. Pinned loosely — this is a draw, and the
    assertion is that the tail exists at all, not that it hits a number.
    """
    kw = dict(duration_sec=1800.0, n_roi=37, bg_rate_hz=0.0095,
              participation=(0.30, 0.18, 0.10), n_per_level=(4, 4, 4),
              jitter_sec=0.36, min_sep_sec=120.0, interval_cv=1.0)
    for seed in (5, 6, 7):
        flat, _ = simulate_coordination(seed=seed, **kw)
        varied, _ = simulate_coordination(seed=seed, bg_rate_shape=0.275, **kw)
        f = np.array([len(v) for v in trains_of(flat)])
        v = np.array([len(v) for v in trains_of(varied)])
        assert f.max() / f.sum() < 0.08
        assert v.max() / v.sum() > 0.12


# ------------------------------------------------------ bursty in time

# The partner of bg_rate_shape, on the other axis. Real ROIs are over-dispersed
# in time — variance/mean 1.8 at 30 s bins and 5.7 at 300 s, against 1.0 for a
# constant rate — and the growth with bin width is why one scale is not enough.

BURSTY = dict(duration_sec=1800.0, n_roi=60, bg_rate_hz=0.02,
              participation=(), n_per_level=(), grid_sec=0.0)


def _fano(slice_, dur, w, min_events=10):
    """Mean variance/mean of per-bin counts, over ROIs with enough events."""
    edges = np.arange(0.0, dur + w, w)
    out = []
    for v in trains_of(slice_):
        if v.size >= min_events:
            c = np.histogram(v, bins=edges)[0].astype(float)
            if c.mean() > 0:
                out.append(c.var() / c.mean())
    return float(np.mean(out)) if out else float("nan")


def test_the_default_is_still_homogeneous_in_time():
    """None must not consume random numbers, or every existing seed moves."""
    a, _ = simulate_coordination(seed=13)
    b, _ = simulate_coordination(seed=13, bg_burst_shape=None)
    for x, y in zip(trains_of(a), trains_of(b)):
        np.testing.assert_array_equal(x, y)


def test_a_constant_rate_is_not_overdispersed_and_bursting_is():
    flat, _ = simulate_coordination(seed=2, **BURSTY)
    burst, _ = simulate_coordination(seed=2, bg_burst_shape=1.388,
                                     bg_burst_bin_sec=60.0, **BURSTY)
    # Expected Fano for one scale is 1 + (rate*bin)/shape = 1 + 1.2/1.388 ~ 1.86;
    # thirty bins per ROI leave real sampling noise around it, so the bar is set
    # where it still separates cleanly from a constant rate rather than at the
    # analytic value.
    assert _fano(flat, 1800.0, 60.0) == pytest.approx(1.0, abs=0.35)
    assert _fano(burst, 1800.0, 60.0) > 1.4


def test_one_scale_stops_growing_and_two_scales_keep_going():
    """The reason a sequence is accepted at all.

    A single bin draws independent bins, so looking at windows much wider than
    the bin averages the modulation away. Real ROIs keep getting more
    over-dispersed the wider you look, and only a coarse scale reproduces that.
    """
    one, _ = simulate_coordination(seed=4, bg_burst_shape=1.388,
                                   bg_burst_bin_sec=60.0, **BURSTY)
    two, _ = simulate_coordination(seed=4, bg_burst_shape=(1.547, 1.388),
                                   bg_burst_bin_sec=(300.0, 60.0), **BURSTY)
    grow_one = _fano(one, 1800.0, 300.0) / _fano(one, 1800.0, 60.0)
    grow_two = _fano(two, 1800.0, 300.0) / _fano(two, 1800.0, 60.0)
    assert grow_two > grow_one


def test_bursting_does_not_move_the_mean_rate():
    """The multiplier has mean 1, so only the distribution over time changes."""
    flat, _ = simulate_coordination(seed=8, n_roi=4000, duration_sec=1800.0,
                                    bg_rate_hz=0.01, participation=(),
                                    n_per_level=(), grid_sec=0.0)
    burst, _ = simulate_coordination(seed=8, n_roi=4000, duration_sec=1800.0,
                                     bg_rate_hz=0.01, bg_burst_shape=(1.547, 1.388),
                                     bg_burst_bin_sec=(300.0, 60.0),
                                     participation=(), n_per_level=(), grid_sec=0.0)
    n_flat = sum(v.size for v in trains_of(flat))
    n_burst = sum(v.size for v in trains_of(burst))
    assert n_burst == pytest.approx(n_flat, rel=0.1)


def test_same_seed_same_bursty_output():
    a, _ = simulate_coordination(seed=3, bg_burst_shape=(1.547, 1.388),
                                 bg_burst_bin_sec=(300.0, 60.0), **BURSTY)
    b, _ = simulate_coordination(seed=3, bg_burst_shape=(1.547, 1.388),
                                 bg_burst_bin_sec=(300.0, 60.0), **BURSTY)
    for x, y in zip(trains_of(a), trains_of(b)):
        np.testing.assert_array_equal(x, y)


def test_both_axes_compose():
    """Rate heterogeneity across ROIs and clumping within one are independent."""
    both, _ = simulate_coordination(seed=6, bg_rate_shape=0.275,
                                    bg_burst_shape=(1.547, 1.388),
                                    bg_burst_bin_sec=(300.0, 60.0), **BURSTY)
    rates = np.array([v.size for v in trains_of(both)], dtype=float)
    assert rates.max() / rates.sum() > 0.10          # a busy ROI exists
    assert _fano(both, 1800.0, 60.0) > 1.4           # and it clumps in time


@pytest.mark.parametrize("bad", [0.0, -1.0])
def test_rejects_a_non_positive_burst_shape(bad):
    with pytest.raises(ValueError, match="bg_burst_shape"):
        simulate_coordination(seed=1, bg_burst_shape=bad)


def test_rejects_mismatched_scale_lengths():
    with pytest.raises(ValueError, match="same"):
        simulate_coordination(seed=1, bg_burst_shape=(1.5, 1.4),
                              bg_burst_bin_sec=(300.0, 60.0, 10.0))


def test_a_sequence_of_shapes_needs_a_sequence_of_bins():
    with pytest.raises(ValueError, match="bg_burst_bin_sec"):
        simulate_coordination(seed=1, bg_burst_shape=(1.5, 1.4),
                              bg_burst_bin_sec=60.0)
