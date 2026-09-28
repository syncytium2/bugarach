"""tools/calibrate_bench_inputs.py: the arithmetic the three steps rest on, on units small enough to
check by hand. The runs themselves are in the darkroom (2026-09-28-calibrated-inputs)."""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import calibrate_bench_inputs as C  # noqa: E402


def unit(**kw):
    base = dict(n_roi=20, rate_hz=0.0, peaks=[], n_calls=0, spreads=[], seed=1, mouse="m1",
                obs=[0.0] * 101, exp=[1.0] * 101)
    base.update(kw)
    return base


def test_the_chance_rois_are_the_rate_times_the_window_for_a_rare_event():
    u = unit(n_roi=30, rate_hz=0.01)
    assert C.chance_rois(u) == pytest.approx(30 * (1 - math.exp(-0.02)))
    assert C.chance_rois(u) == pytest.approx(30 * 0.01 * 2.0, rel=0.02)


def test_the_sliding_share_subtracts_chance_and_divides_by_the_rois():
    u = unit(n_roi=20, rate_hz=0.05, peaks=[8, 10, 12])
    c = 20 * (1 - math.exp(-0.1))
    assert C.sliding_share([u], subtract=False) == pytest.approx(10 / 20)
    assert C.sliding_share([u]) == pytest.approx((10 - c) / 20)


def test_excess_pairs_count_only_what_sits_above_the_shoulder():
    # Expected 1 pair per lag everywhere; observed 1 + 5 at lags 0-2 and 1.2 in the shoulder:
    # the shoulder says 20 % of everything is slow shared change, so each peak lag keeps 5 - 0.2.
    obs = [1.2] * 101
    for k in range(3):
        obs[k] = 6.0
    u = unit(obs=obs, exp=[1.0] * 101)
    assert C.excess_pairs(u) == pytest.approx(3 * (6.0 - 1.2) + 28 * 0.0, abs=1e-9)


def test_pairs_per_event_give_back_the_participants():
    # 10 events of 6 participants: C(6, 2) = 15 excess pairs each, 150 in all, at zero lag.
    obs = [1.0] * 101
    obs[0] = 151.0
    u = unit(n_roi=30, n_calls=10, obs=obs, exp=[1.0] * 101)
    assert C.corr_share([u]) == pytest.approx(6 / 30)


def test_invert_reads_a_rising_curve_and_refuses_outside_it():
    x, y = [0.1, 0.2, 0.3], [0.15, 0.25, 0.4]
    assert C.invert(x, y, 0.25) == pytest.approx(0.2)
    assert math.isnan(C.invert(x, y, 0.5))
    assert math.isnan(C.invert(x, y, 0.1))
    # a dip is raised to the running maximum and the flat stretch is not inverted twice
    assert C.invert([0.1, 0.2, 0.3, 0.4], [0.2, 0.18, 0.3, 0.4], 0.35) == pytest.approx(0.35)


def test_the_bootstrap_says_when_the_reading_falls_off_the_curve():
    units = [unit(seed=i) for i in range(10)]
    got = C.boot_units(units, lambda us: float("nan"), n=20)
    assert got == dict(lo=None, hi=None, off_curve_share=1.0)
    got = C.boot_units(units, lambda us: float(len(us)), n=20)
    assert got["off_curve_share"] == 0.0 and got["lo"] == got["hi"] == 10.0


def test_the_stored_curves_are_the_ones_the_real_numbers_came_from():
    cur = C.curves()
    assert cur["fast"]["correlogram"]["real_jitter"] == pytest.approx(0.105, abs=5e-4)
    assert cur["slow"]["calls"]["real_jitter"] == pytest.approx(0.320, abs=5e-4)
    for s in C.STREAMS:
        for m in ("correlogram", "calls"):
            assert np.all(np.diff(cur[s][m]["jitter"]) > 0)
