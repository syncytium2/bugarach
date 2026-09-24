"""ADR-0008's per-window event floor, ``bugarach.event_floor``, on synthetic windows.

What the todo asks the tests to hold: the floor is never below 3; on a baseline window both floors are
the same number; a window with its rates raised gets a floor at least as high; and the tool that
measured the floor on the 66 recordings calls this module rather than its own copy.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

from bugarach import event_floor as ef

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

DT = 0.1


def _poisson(seed, n_roi, rate_hz, sec, dt=DT):
    rng = np.random.RandomState(seed)
    L = int(round(sec / dt))
    return [np.flatnonzero(rng.random_sample(L) < rate_hz * dt) for _ in range(n_roi)], L


def test_the_floor_is_never_below_three():
    trains, L = _poisson(0, 20, 0.0005, 1800)       # so sparse chance alone reaches only 1 or 2
    f = ef.window_floor(trains, L, DT, key=("t", "sparse"), draws=40)
    assert f.chance_floor < ef.MINIMUM_ROIS
    assert f.floor == ef.MINIMUM_ROIS
    empty = ef.window_floor([np.array([], int)] * 10, L, DT, key=("t", "empty"), draws=10)
    assert empty.floor == ef.MINIMUM_ROIS


def test_a_window_with_its_rates_raised_gets_a_floor_at_least_as_high():
    quiet, L = _poisson(1, 30, 0.005, 1800)
    busy, _ = _poisson(1, 30, 0.03, 1800)
    fq = ef.window_floor(quiet, L, DT, key=("t", "q"), draws=60)
    fb = ef.window_floor(busy, L, DT, key=("t", "b"), draws=60)
    assert fb.chance_floor >= fq.chance_floor
    assert fb.floor > fq.floor


def test_on_a_baseline_window_both_floors_are_the_same_number():
    trains, L = _poisson(2, 25, 0.01, 1200)
    f = ef.window_floor(trains, L, DT, key=("t", "base"), draws=40)
    both = ef.treatment_floors(f, f)
    assert both["own"] == both["baseline"] == f.floor


def test_a_treatment_that_raises_rates_separates_the_two_floors():
    base, L = _poisson(3, 30, 0.004, 1800)
    treat, _ = _poisson(4, 30, 0.04, 1800)
    fb = ef.window_floor(base, L, DT, key=("t", "base"), draws=60)
    ft = ef.window_floor(treat, L, DT, key=("t", "treat"), draws=60)
    both = ef.treatment_floors(ft, fb)
    assert both["own"] > both["baseline"]
    assert both["own_detail"]["floor"] == ft.floor and both["baseline_detail"]["floor"] == fb.floor


def test_the_same_window_always_gets_the_same_floor():
    trains, L = _poisson(5, 20, 0.02, 900)
    a = ef.window_floor(trains, L, DT, key=("t", "same"), draws=30)
    b = ef.window_floor(trains, L, DT, key=("t", "same"), draws=30)
    assert a == b


def test_dt_is_required():
    trains, L = _poisson(6, 5, 0.01, 300)
    with pytest.raises(ValueError):
        ef.window_floor(trains, L, None, key=("t",), draws=2)


def test_a_window_too_short_for_the_shift_is_refused():
    with pytest.raises(ValueError):
        ef.window_floor([np.array([1, 2])], 300, DT, key=("t",), draws=2)   # 30 s < 2 J + 2 s


def test_the_settings_are_adr_0008s():
    assert (ef.MINIMUM_ROIS, ef.WINDOW_SEC, ef.J_SEC, ef.FA_PER_HOUR, ef.MIN_DRAWS) == (
        3, 2.0, 20.0, 1.0, 1000)


def test_the_measuring_tool_and_the_rigid_shift_tool_use_this_module():
    import measure_chance_floor as mcf
    import tube_self_supervised as tss

    assert mcf.coactive_counts is ef.coactive_counts
    assert mcf.exceedances is ef.exceedances
    assert mcf.floor_of is ef.floor_of
    assert tss.rigid_frames is ef.rigid_frames
