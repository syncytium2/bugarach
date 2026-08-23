"""A per-ROI rate says which statistic of the field it is.

The generator's ``bg_rate_hz`` is the **mean** — `simulate.py` says so, and
`bench.REGIMES` states its endpoints as the interquartile spread of slice-mean
per-ROI rate, so the bench and the generator agree. What did not agree was the
calibration path, which handed over ``roi_rate_med``: a median.

On a **flat** field that is harmless, because one rate for every ROI makes the
mean and the median the same number — which is why it survived. On the uneven
field the browser generates by default, and the one `MEASURED_RATE_SHAPE` exists
to give Python, they are a factor of about five apart:

    rates ~ Gamma(k, mean/k)   =>   mean = the knob, exactly
                               =>   median/mean = median(Gamma(k,1))/k

At the fitted k = 0.275 that ratio is 0.2098. A field whose typical ROI fires at
15 mHz has a mean of 71.

So the number now travels with a flag. Tony, 2026-08-21: *"can we flag the input
to the generator as median or mean so the generator can handle either?"* — which
is this repo's existing idiom rather than a new one: ``strength_unit`` travels
with ``strength`` and ``width_def`` travels with ``width_sec``, both because a
column that means two things without saying which yields a plausible wrong
answer rather than an error.

**And the default moved to the mean, which is a separate claim.** Not merely
because the knob wants one, but because the median is a bad estimator here: at a
realistic 33 ROIs it spans 0.56 to 5.56 mHz between its 5th and 95th percentiles
around a population value of 2.14, and is exactly zero about one run in a
hundred. That is measured in `test_the_median_is_a_noisy_estimator_at_real_roi_counts`
rather than asserted.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pytest

from bugarach import bench
from bugarach.simulate import median_over_mean, rate_as_mean, simulate_coordination

ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "docs/site/raster_viewer.html"


def _locs(slice_):
    """The per-ROI onset arrays of the slice's only stream."""
    name = next(iter(slice_.streams))
    return [np.asarray(v, dtype=float) for v in slice_.streams[name].locs]


# ------------------------------------------------------------------ the ratio

@pytest.mark.parametrize("k", [0.1, 0.275, 0.5, 1.0, 2.0, 5.0, 20.0])
def test_the_ratio_matches_scipy(k):
    """`simulate.py` computes it without scipy, which is not a dependency here.
    scipy IS available in the test environment, so the two are compared."""
    stats = pytest.importorskip("scipy.stats")
    assert median_over_mean(k) == pytest.approx(stats.gamma.ppf(0.5, k) / k,
                                                rel=1e-9)


def test_the_ratio_is_exactly_ln2_for_the_exponential():
    """Gamma(1) is Exponential, whose median is ln(2)·mean. A closed form the
    bisection has to reproduce, independent of scipy."""
    assert median_over_mean(1.0) == pytest.approx(np.log(2.0), rel=1e-12)


def test_the_typical_roi_fires_at_a_fifth_of_the_field_mean():
    """The number this whole change is about, at the fitted shape."""
    assert median_over_mean(bench.MEASURED_RATE_SHAPE) == pytest.approx(0.2098,
                                                                       abs=1e-4)


# ------------------------------------------------------- the flag, and refusal

def test_a_rate_that_does_not_say_which_statistic_it_is_is_refused():
    """The point of the exercise. Guessing is a factor of five."""
    with pytest.raises(ValueError, match="mean.*median"):
        rate_as_mean(0.01, "typical", shape=0.275)
    with pytest.raises(ValueError):
        rate_as_mean(0.01, "", shape=0.275)


def test_a_mean_passes_through_untouched():
    assert rate_as_mean(0.0102, "mean", shape=0.275) == 0.0102


def test_a_median_on_a_flat_field_passes_through_untouched():
    """One rate for every ROI, so the two statistics are one number. This is
    why the defect was invisible for as long as it was."""
    assert rate_as_mean(0.0102, "median", shape=None) == 0.0102


def test_a_median_on_an_uneven_field_is_converted():
    got = rate_as_mean(0.00214, "median", shape=0.275)
    assert got == pytest.approx(0.00214 / median_over_mean(0.275), rel=1e-12)
    assert got > 0.0102 * 0.9        # lands near the bench's median slice mean


# --------------------------------------------------- it actually comes out right

def test_asking_for_a_median_produces_that_median():
    """End to end through the real generator, not through the arithmetic.

    A large ROI count so the sample median is close to the population one — the
    point here is that the conversion is right, and `the noisy estimator` test
    below is where the small-n behaviour is measured.
    """
    target_median = 0.002
    s, _ = simulate_coordination(
        seed=11, duration_sec=6000.0, n_roi=4000,
        bg_rate_hz=target_median, bg_rate_stat="median",
        bg_rate_shape=bench.MEASURED_RATE_SHAPE,
        participation=(0.3,), n_per_level=(0,),
    )
    rates = np.array([len(v) / 6000.0 for v in _locs(s)])
    assert np.median(rates) == pytest.approx(target_median, rel=0.15)


def test_asking_for_a_mean_produces_that_mean():
    target_mean = 0.0102
    s, _ = simulate_coordination(
        seed=11, duration_sec=6000.0, n_roi=4000,
        bg_rate_hz=target_mean, bg_rate_stat="mean",
        bg_rate_shape=bench.MEASURED_RATE_SHAPE,
        participation=(0.3,), n_per_level=(0,),
    )
    rates = np.array([len(v) / 6000.0 for v in _locs(s)])
    assert rates.mean() == pytest.approx(target_mean, rel=0.10)


def test_the_two_flags_are_a_factor_of_five_apart_on_an_uneven_field():
    """The regression this is really guarding: if the flag stops being read,
    these two collapse onto each other."""
    kw = dict(seed=3, duration_sec=4000.0, n_roi=3000,
              bg_rate_shape=bench.MEASURED_RATE_SHAPE,
              participation=(0.3,), n_per_level=(0,))
    as_mean, _ = simulate_coordination(bg_rate_hz=0.01, bg_rate_stat="mean", **kw)
    as_med, _ = simulate_coordination(bg_rate_hz=0.01, bg_rate_stat="median", **kw)
    m1 = np.mean([len(v) for v in _locs(as_mean)])
    m2 = np.mean([len(v) for v in _locs(as_med)])
    assert m2 / m1 == pytest.approx(1 / 0.209838, rel=0.15)


def test_a_flat_field_ignores_the_flag_entirely():
    """Same seed, same output — the two statistics coincide, so nothing may
    change, including the random stream."""
    kw = dict(seed=5, duration_sec=600.0, n_roi=40, bg_rate_hz=0.05,
              participation=(0.5,), n_per_level=(3,))
    a, _ = simulate_coordination(bg_rate_stat="mean", **kw)
    b, _ = simulate_coordination(bg_rate_stat="median", **kw)
    ta = [list(v) for v in _locs(a)]
    tb = [list(v) for v in _locs(b)]
    assert ta == tb


def test_the_default_is_mean_so_every_existing_caller_is_unchanged():
    kw = dict(seed=9, duration_sec=600.0, n_roi=40, bg_rate_hz=0.05,
              bg_rate_shape=0.5, participation=(0.5,), n_per_level=(3,))
    a, _ = simulate_coordination(**kw)
    b, _ = simulate_coordination(bg_rate_stat="mean", **kw)
    ta = [list(v) for v in _locs(a)]
    tb = [list(v) for v in _locs(b)]
    assert ta == tb


# ------------------------------------------------- why the default is the mean

def test_the_median_is_a_noisy_estimator_at_real_roi_counts():
    """The reason the calibration path now hands over the mean.

    Measured rather than asserted: draw a realistic field many times and look at
    how far the SAMPLE median wanders from the population value it is estimating.
    """
    rng = np.random.RandomState(0)
    k, slice_mean, n_roi, dur = bench.MEASURED_RATE_SHAPE, 0.0102, 33, 1800.0
    pop_median = slice_mean * median_over_mean(k)

    meds, means = [], []
    for _ in range(1500):
        rates = rng.gamma(k, slice_mean / k, size=n_roi)
        counts = rng.poisson(rates * dur)
        meds.append(np.median(counts / dur))
        means.append(np.mean(counts / dur))
    meds, means = np.array(meds), np.array(means)

    lo, hi = np.percentile(meds, [5, 95])
    assert hi / max(lo, 1e-9) > 5, (
        "the sample median is expected to be a wide estimator here; if this "
        "stops holding the shape has changed and the default should be revisited")
    # and the mean is materially steadier, which is the actual claim
    assert (means.std() / means.mean()) < (meds.std() / max(meds.mean(), 1e-12))


# ------------------------------------------------------- the two implementations

def _js_const(name):
    m = re.search(rf"const {name} = ([0-9.]+);", VIEWER.read_text(encoding="utf-8"))
    assert m, f"{name} not found in the viewer"
    return float(m.group(1))


def test_the_browsers_constant_is_the_one_its_own_shape_implies():
    """Recomputed from `RATE_SHAPE` as the page states it, so the two cannot
    drift: change the shape and this fails until the constant follows."""
    shape = _js_const("RATE_SHAPE")
    assert shape == pytest.approx(bench.MEASURED_RATE_SHAPE), (
        "the page's rate shape has drifted from bench.MEASURED_RATE_SHAPE")
    assert _js_const("RATE_MEDIAN_OVER_MEAN") == pytest.approx(
        median_over_mean(shape), abs=5e-7)


def test_the_viewer_no_longer_feeds_a_median_to_the_rate_box():
    html = VIEWER.read_text(encoding="utf-8")
    assert 'set("sRate", Math.max(1, Math.min(500, Math.round(a.roiRateMed * 1000))))' \
        not in html, "the calibration line is back to handing over a median"
    assert "roiRateMean" in html, "the assessment does not report a mean"
    assert 'id="sRateStat"' in html, "the rate box does not say which statistic"


def test_the_panel_quotes_the_current_regime_endpoints():
    """The note under the rate box quoted 3.8-17.5 mHz, which `bench.REGIMES`
    moved off on 2026-08-20 when it was re-derived from the approved folder."""
    html = VIEWER.read_text(encoding="utf-8")
    lo = bench.REGIMES["baseline_quiet"]["bg_rate_hz"] * 1000
    hi = bench.REGIMES["baseline_busy"]["bg_rate_hz"] * 1000
    assert f"{lo:.1f}" in html and f"{hi:.1f}" in html, (
        f"the panel should quote {lo:.1f}-{hi:.1f} mHz, the current endpoints")
    assert "3.8–17.5" not in html, "the stale pre-2026-08-20 endpoints are back"
