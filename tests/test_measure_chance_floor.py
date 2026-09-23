"""The chance floor behind ``tools/measure_chance_floor.py``, on synthetic trains with known answers.

No data needed. What must hold: the co-active count counts ROIs, not onsets; a call is a run, so
one long excursion is one call; the Poisson-binomial tail is the binomial when every probability is
equal; on independent ROIs the frame-counted empirical floor lands where the closed form at the same
window puts it; and the scaling summary reads 0 for a fixed count and 1 for a fixed fraction.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import measure_chance_floor as m  # noqa: E402
import probe_field_size as probe  # noqa: E402


def test_the_count_is_of_rois_not_onsets():
    # ROI 0 has three onsets inside one 5-frame window, ROI 1 one; the window at 0 holds 2 ROIs.
    c = m.coactive_counts([np.array([0, 1, 2]), np.array([4]), np.array([], int)], 10, 5)
    assert c.tolist() == [2, 2, 2, 1, 1, 0]


def test_a_long_excursion_is_one_call():
    counts = np.array([0, 3, 3, 3, 0, 1, 2, 0, 3])
    runs, frames = m.exceedances(counts, 4)
    # K=1: runs at 1-3, 5-6, 8 -> 3. K=2: 1-3, 6, 8 -> 3. K=3: 1-3, 8 -> 2. K=4: none.
    assert runs[1:].tolist() == [3, 3, 2, 0, 0]
    assert frames[1:].tolist() == [6, 5, 4, 0, 0]


def test_the_floor_is_the_first_count_within_budget():
    assert m.floor_of(np.array([9.0, 5.0, 2.0, 0.9, 0.1, 0.0]), 1.0) == 3
    assert m.floor_of(np.array([9.0, 5.0, 2.0]), 1.0) == 2          # never within budget: N + 1


def test_poisson_binomial_with_equal_probabilities_is_the_binomial():
    n, p = 30, 0.07
    sf = m.poisson_binomial_sf([p] * n)
    for k in (0, 1, 3, 8, 15):
        assert sf[k] == pytest.approx(probe.binom_sf(k, n, p), rel=1e-9, abs=1e-300)


def test_heterogeneous_rates_move_the_closed_form_floor():
    """At the same mean rate, a field where a few ROIs carry most of the onsets has a lower floor
    than a homogeneous one: most ROIs rarely take part, so large counts are rarer."""
    even = np.full(40, 0.01)
    skew = np.concatenate([np.full(4, 0.091), np.full(36, 0.001)])
    assert skew.mean() == pytest.approx(even.mean())
    cf_even = m.closed_forms(even, 0.1, 2.0)
    cf_skew = m.closed_forms(skew, 0.1, 2.0)
    assert cf_even["window_homogeneous"] == cf_skew["window_homogeneous"]
    assert cf_skew["window_poisson_binomial"] < cf_even["window_poisson_binomial"]


def _rec(trains, L, rid="r0", dt=0.1):
    return SimpleNamespace(window=(0, L), dt=dt, trains=trains, recording_id=rid,
                           mouse="m0", group="DI")


def test_independent_rois_land_on_the_closed_form_at_the_same_window():
    """Poisson ROIs with no coordination and no dead time: the rigid shift leaves them what they
    were, so the frame-counted floor must sit at the window closed form, give or take one."""
    rng = np.random.RandomState(0)
    L, N, rate = int(3 * 3600 / 0.1), 30, 0.02
    trains = [np.flatnonzero(rng.random_sample(L) < rate * 0.1) for _ in range(N)]
    out = m.recording_task(("fast", _rec(trains, L), 4, 2.0))
    cf = out["closed_form"]["window_poisson_binomial"]
    assert abs(out["floor_frames"] - cf) <= 1
    # Calls are runs of frames, so the call floor can only be at or below the frame floor.
    assert out["floor"] <= out["floor_frames"]
    assert out["n_roi"] == N and out["floor_fraction"] == pytest.approx(out["floor"] / N)


def test_planted_coordination_raises_the_real_count_not_the_null_floor():
    """Planted 12-ROI moments put real calls far above budget at the floor, and the null, which
    breaks the alignment, is back near what the same rates alone give."""
    rng = np.random.RandomState(1)
    L, N = int(2 * 3600 / 0.1), 30
    trains = [list(np.flatnonzero(rng.random_sample(L) < 0.01 * 0.1)) for _ in range(N)]
    for t in rng.randint(600, L - 600, 120):
        for r in rng.choice(N, 12, replace=False):
            trains[r].append(int(t + rng.randint(0, 5)))
    trains = [np.unique(np.array(t, int)) for t in trains]
    out = m.recording_task(("fast", _rec(trains, L), 4, 2.0))
    assert out["null_calls_per_hour_at_floor"] <= m.FA_PER_HOUR
    assert out["real_calls_per_hour_at_floor"] > 20 * m.FA_PER_HOUR
    assert abs(out["floor_frames"] - out["closed_form"]["window_poisson_binomial"]) <= 2


def _row(n, floor, rate=0.01, rid=None, g="DI", mouse=None):
    return dict(n_roi=n, floor=floor, floor_fraction=floor / n, mean_rate_hz=rate,
                recording_id=rid or f"r{n}", group=g, mouse=mouse or f"m{n}")


def test_scaling_reads_zero_for_a_count_and_one_for_a_fraction():
    ns = [10, 15, 20, 30, 40, 60]
    count = m.scaling([_row(n, 5) for n in ns])
    frac = m.scaling([_row(n, 0.2 * n) for n in ns])
    assert count["slope_log_floor_on_log_rois"] == pytest.approx(0.0, abs=1e-9)
    assert count["count_rule"]["median_miss_rois"] == 0
    assert frac["slope_log_floor_on_log_rois"] == pytest.approx(1.0, abs=1e-9)
    assert frac["fraction_rule"]["median_miss_rois"] == pytest.approx(0.0, abs=1e-9)
    both = m.scaling([_row(n, 2 + 0.1 * n) for n in ns])
    assert both["count_and_fraction_rule"]["count"] == pytest.approx(2.0)
    assert both["count_and_fraction_rule"]["fraction"] == pytest.approx(0.1)


def test_by_group_orders_groups_and_keeps_a_pooled_entry():
    rows = ([_row(n, 4, rid=f"orx{n}", g="ORX") for n in (10, 20, 30, 40)]
            + [_row(n, 8, rid=f"di{n}", g="DI") for n in (12, 22, 32, 42)])
    G = m.by_group(rows, n_boot=20, seed_key=("t",))
    assert G["groups"] == ["DI", "ORX"]
    assert G["recordings"] == {"DI": 4, "ORX": 4, "pooled": 8}
    med = G["stats"]["median_floor"]
    assert med["groups"]["DI"]["value"] == 8 and med["groups"]["ORX"]["value"] == 4
    assert med["pairwise"]["DI - ORX"]["outlives"]
    # Every DI recording sits at 8 and every ORX one at 4, so every resample differs by 4.
    assert med["pairwise"]["DI - ORX"]["bootstrap_interval"] == [4.0, 4.0]
    assert med["pairwise"]["DI - ORX"]["robust"]
    assert math.isfinite(G["scaling"]["pooled"]["slope_log_floor_on_log_rois"])
