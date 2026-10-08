"""stack_ceiling: the tallest stack circular shifting can build, and how much of it stands."""

from __future__ import annotations

import ast
from pathlib import Path

import numpy as np
import pytest

from bugarach.detectors import stack_ceiling as sc

SRC = Path(sc.__file__)


def test_it_imports_nothing_from_the_package():
    tree = ast.parse(SRC.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            assert node.level == 0 and not (node.module or "").startswith("bugarach"), node.module
        if isinstance(node, ast.Import):
            assert not any(a.name.startswith("bugarach") for a in node.names)


def test_a_hand_built_period():
    # Four ROIs around t = 100 s: two in a 2 s window, one 10 s away, one outside the period.
    trains = [[99.5], [100.8, 140.0], [110.0], [200.0], []]
    r = sc.stack_ceiling(trains, [100.0], width_sec=2.0, period_sec=120.0)
    assert r.height.tolist() == [2]
    assert r.ceiling.tolist() == [3]
    assert r.fill[0] == pytest.approx(2 / 3)
    assert r.shift_needed[0].tolist() == [0.0, 0.0, 9.0, np.inf, np.inf]
    assert r.half_shift_sec[0] == 0.0          # two of three already stand


def test_a_fully_aligned_period_has_fill_one_and_an_empty_one_zero():
    r = sc.stack_ceiling([[50.0], [50.1], [49.9]], [50.0, 500.0], width_sec=0.5, period_sec=60.0)
    assert r.fill.tolist() == [1.0, 0.0]
    assert r.ceiling.tolist() == [3, 0]
    assert np.isnan(r.half_shift_sec[1])


def _wrap(v, lo, period):
    return lo + np.mod(v - lo, period)


def test_shifting_each_roi_by_its_shift_needed_builds_the_ceiling():
    rng = np.random.default_rng(3)
    period, width, centre = 120.0, 2.0, 300.05
    trains = [np.sort(rng.uniform(0, 600, rng.poisson(6))) for _ in range(40)]
    r = sc.stack_ceiling(trains, [centre], width_sec=width, period_sec=period)
    lo = centre - period / 2
    in_window = 0
    for train, need in zip(trains, r.shift_needed[0]):
        v = train[(train >= lo) & (train < lo + period)]
        if not v.size:
            assert np.isinf(need)
            continue
        nearest = v[np.argmin(np.abs(v - centre))]
        moved = _wrap(v + np.sign(centre - nearest) * need, lo, period)
        in_window += bool(np.any(np.abs(moved - centre) <= width / 2 + 1e-9))
    assert in_window == r.ceiling[0] > r.height[0]


def test_the_growth_curve_is_the_height_at_a_wider_window():
    rng = np.random.default_rng(5)
    trains = [np.sort(rng.uniform(0, 600, rng.poisson(8))) for _ in range(30)]
    centres = np.arange(60.05, 540, 7.3)
    r = sc.stack_ceiling(trains, centres, width_sec=1.0, period_sec=120.0)
    for shift in (0.0, 2.5, 20.0):
        wider = sc.stack_ceiling(trains, centres, width_sec=1.0 + 2 * shift, period_sec=120.0)
        assert ((r.shift_needed <= shift).sum(axis=1) == wider.height).all()


def test_expected_height_matches_random_circular_shifts():
    rng = np.random.default_rng(11)
    period, centre = 120.0, 300.0
    lo = centre - period / 2
    trains = [np.sort(rng.uniform(lo, lo + period, n)) for n in (1, 1, 2, 3, 5, 9, 0, 14)]
    radii = np.array([0.15, 1.0, 5.0, 30.0, 60.0])
    want = sc.expected_height(trains, centre, period_sec=period, radii_sec=radii)
    draws = 4000
    got = np.zeros(radii.size)
    for _ in range(draws):
        for train in trains:
            if train.size:
                moved = _wrap(train + rng.uniform(0, period), lo, period)
                got += np.abs(moved - centre).min() <= radii
    got /= draws
    assert np.allclose(got, want, atol=0.08)
    assert want[-1] == pytest.approx(7.0)       # the whole period: every ROI with an onset
