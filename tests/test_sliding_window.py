"""The sliding count and the exact null behind LoCo's and CoactDetect's window_mode="sliding".

Each piece is checked against the slow, obvious version of itself: the step function
against counting at many times, the catch probability against actually shifting, the
Poisson-binomial against simulation. Then the property the change exists for: shifting
a recording moves every call by exactly the shift.
"""
from __future__ import annotations

import dataclasses

import numpy as np
import pytest

from bugarach import bench
from bugarach.detectors import sliding as sl


def _trains(seed=0, n_roi=12, T=300.0, rate=0.08):
    rng = np.random.RandomState(seed)
    return [np.sort(np.round(rng.uniform(0, T, rng.poisson(rate * T)), 1)) for _ in range(n_roi)]


def test_the_step_function_equals_counting_at_every_time():
    ev = _trains()
    w = 2.0
    starts, ends, S = sl.pieces(ev, w, 0.0, 300.0)
    for t in np.arange(0.05, 300.0, 0.1):          # between frames, so no boundary ties
        i = np.searchsorted(starts, t, side="right") - 1
        brute = sum(bool(np.any((v > t - w) & (v <= t))) for v in ev)
        got = S[i] if i >= 0 and t < ends[i] else 0
        assert got == brute, t


def test_the_catch_probability_equals_shifting():
    rng = np.random.RandomState(1)
    ev = [np.sort(rng.uniform(10, 70, k)) for k in (1, 3, 8, 20)]
    lo, hi, w = 10.0, 70.0, 2.0
    p = sl.catch_probabilities(ev, lo, hi, w)
    L = hi - lo
    shifts = rng.uniform(0, L, 200_000)
    for v, pv in zip(ev, p):
        x = np.mod(v[None, :] - lo + shifts[:, None], L)
        mc = np.mean(np.any(x < w, axis=1))
        assert pv == pytest.approx(mc, abs=0.005)


def test_the_null_distribution_equals_simulation():
    p = np.array([0.05, 0.1, 0.3, 0.02, 0.5, 0.15])
    dist = sl.poisson_binomial(p)
    assert dist.sum() == pytest.approx(1.0)
    rng = np.random.RandomState(2)
    sims = (rng.random_sample((400_000, p.size)) < p).sum(axis=1)
    emp = np.bincount(sims, minlength=p.size + 1) / sims.size
    np.testing.assert_allclose(dist, emp, atol=0.003)
    mu, sd = sl.moments(p)
    assert mu == pytest.approx(sims.mean(), abs=0.01)
    assert sd == pytest.approx(sims.std(), abs=0.01)
    k = sl.quantile(p, 99.0)
    assert np.cumsum(dist)[int(k)] >= 0.99 > (np.cumsum(dist)[int(k) - 1] if k > 0 else 0)


@pytest.mark.parametrize("name", ["loco", "coact"])
def test_shifting_the_recording_moves_every_call_by_the_shift(name):
    """The defect this exists to fix: binned, a sub-bin shift changed which events were
    called (docs/todo/2026-09-07-detector-calls-move-with-the-grid.md)."""
    s, _ = bench.make_recording("baseline_busy", 3)
    ref = np.sort(bench.run_detector(name, s, window_mode="sliding").onset_sec)
    assert ref.size > 5
    st = s.streams[bench.STREAM]
    for d in (0.3, 0.7):
        moved = dataclasses.replace(st, **{f: [np.asarray(a) + d for a in getattr(st, f)]
                                           for f in ("locs", "t50rise")})
        got = np.sort(bench.run_detector(
            name, dataclasses.replace(s, streams={bench.STREAM: moved}),
            window_mode="sliding").onset_sec) - d
        assert got.size == ref.size, d
        np.testing.assert_allclose(got, ref, atol=1e-6)


def test_the_index_equals_the_obvious_form_for_every_context():
    ev = _trains(seed=4, n_roi=30, T=600.0, rate=0.05)
    index = sl.EventIndex(ev)
    rng = np.random.RandomState(5)
    for _ in range(300):
        lo = rng.uniform(-20, 580)
        hi = lo + rng.uniform(0.5, 150)
        w = rng.choice([0.5, 1.0, 2.0, 10.0])
        fast = index.catch_probabilities(lo, hi, w)
        slow = sl.catch_from_positions([v[(v >= lo) & (v < hi)] - lo for v in ev], hi - lo, w)
        np.testing.assert_allclose(fast, slow, atol=1e-12)


@pytest.mark.parametrize("n", [1, 5, 34, 405])
def test_the_one_call_null_equals_the_recursion(n):
    p = np.random.RandomState(n).uniform(0, 0.6, n)
    np.testing.assert_allclose(sl.poisson_binomial(p), sl._poisson_binomial_loop(p), atol=1e-12)


def _burst_trains():
    """Sparse background, and every ROI firing within 0.5 s at t = 150."""
    ev = _trains(seed=7, n_roi=15, T=300.0, rate=0.02)
    return [np.sort(np.r_[v[np.abs(v - 150) > 5], 150.0 + 0.03 * i]) for i, v in enumerate(ev)]


def test_the_coact_guard_keeps_the_burst_out_of_its_own_null():
    from bugarach.detectors.coact import coact_detect
    ev = _burst_trains()
    kw = dict(int_win_sec=2.0, context_win_sec=40.0, alpha=1e-4, window_mode="sliding")
    plain = coact_detect(ev, (0.0, 300.0), **kw)
    for norm in ("compact", "exposure"):
        guarded = coact_detect(ev, (0.0, 300.0), guard_sec=10.0, guard_norm=norm, **kw)
        at = np.flatnonzero(np.abs(guarded.ctr - 151) < 1.5)
        i = at[np.nanargmax(guarded.obs[at])]
        j = np.flatnonzero(plain.ctr == guarded.ctr[i])[0]
        assert guarded.nullmean_prof[i] < plain.nullmean_prof[j], norm
        assert guarded.z_prof[i] > plain.z_prof[j], norm


def test_the_loco_guard_lowers_the_bar_at_the_burst():
    from bugarach.io import slice_from_events
    from bugarach.detectors.loco import loco_detect
    s = slice_from_events({"events": _burst_trains()}, dt=0.1)
    kw = dict(bin_width_sec=1.0, context_win_sec=60.0, threshold_pctile=99.0,
              merge_gap_sec=2.0, window_mode="sliding")
    plain = loco_detect(s, **kw).streams["events"].signal
    guarded = loco_detect(s, guard_sec=10.0, **kw).streams["events"].signal
    i = int(np.nanargmax(np.where(np.abs(guarded.t - 151) < 1.5, guarded.y, -1)))
    j = np.flatnonzero(plain.t == guarded.t[i])[0]
    assert guarded.threshold[i] <= plain.threshold[j]


def test_sliding_refuses_peak_mode_rather_than_guessing():
    from bugarach.detectors.coact import coact_detect
    with pytest.raises(ValueError, match="threshold"):
        coact_detect(_trains(), (0.0, 300.0), window_mode="sliding", detection_mode="peak")
