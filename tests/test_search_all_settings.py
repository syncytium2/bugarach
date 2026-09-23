"""The search logic in tools/search_all_settings.py, on made-up curves with known answers.

The detectors are not run here: the evaluator is injected, so these check what the
search DOES with scores — moving, widening, respecting the false-alarm gate and the
validity rules — rather than what the bench scores are.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import search_all_settings as S  # noqa: E402


def _fake(f, admissible=lambda d, p: True):
    """An evaluator over a closed-form mean F1 ``f(params)``."""
    def evaluate(points):
        pass

    def summarize(d, p):
        return dict(mean_f1=f(p), params=dict(p))

    def is_admissible(d, s):
        return admissible(d, s["params"])

    return evaluate, summarize, is_admissible


def test_rounds_reach_a_coupled_optimum_one_setting_at_a_time():
    """Best at x=3, y=3, with an interaction term: the first round stops at (2, 2),
    because with y at 1 the best x is 2; the second round reaches (3, 3).

    The weights are unequal on purpose. With equal ones x=2 and x=3 tie exactly in
    round two, and a tie is correctly not a move — the first draft of this test
    asserted the optimum anyway and failed for that reason."""
    f = lambda p: 1 - (p["x"] - 3) ** 2 * 0.01 - (p["y"] - p["x"]) ** 2 * 0.005
    space = {"d": {"x": [1.0, 2.0, 3.0, 4.0, 5.0], "y": [1.0, 2.0, 3.0, 4.0, 5.0]}}
    ev, summ, adm = _fake(f)
    state, history, _ = S.coordinate_rounds(["d"], {"d": {"x": 1.0, "y": 1.0}}, space,
                                            ev, summ, adm, log=lambda m: None)
    assert state["d"] == {"x": 3.0, "y": 3.0}
    assert len({h["round"] for h in history["d"]}) >= 2


def test_a_best_value_on_the_grid_edge_widens_the_grid():
    f = lambda p: p["x"]                      # always wants bigger
    space = {"d": {"x": [1.0, 2.0]}}
    ev, summ, adm = _fake(f)
    state, _, grown = S.coordinate_rounds(["d"], {"d": {"x": 1.0}}, space, ev, summ, adm,
                                          log=lambda m: None)
    assert max(grown["d"]["x"]) == 16.0       # 2 -> 4 -> 8 -> 16, three extensions
    assert state["d"]["x"] == 16.0


def test_an_inadmissible_value_is_never_chosen_however_good():
    f = lambda p: p["x"]
    space = {"d": {"x": [1.0, 2.0, 3.0]}}
    ev, summ, adm = _fake(f, admissible=lambda d, p: p["x"] <= 2.0)
    state, _, _ = S.coordinate_rounds(["d"], {"d": {"x": 1.0}}, space, ev, summ, adm,
                                      log=lambda m: None)
    assert state["d"]["x"] == 2.0


def test_a_move_inside_the_tie_margin_is_not_taken():
    f = lambda p: 0.5 + (0.001 if p["x"] == 2.0 else 0.0)
    space = {"d": {"x": [1.0, 2.0, 3.0]}}
    ev, summ, adm = _fake(f)
    state, history, _ = S.coordinate_rounds(["d"], {"d": {"x": 1.0}}, space, ev, summ, adm,
                                            log=lambda m: None)
    assert state["d"]["x"] == 1.0 and not history["d"]


def test_pair_grid_skips_invalid_combinations_and_finds_the_best_admissible():
    f = lambda p: p["a"] + p["b"]
    space = {"d": {"a": [1.0, 2.0, 3.0], "b": [1.0, 2.0, 3.0]}}
    ev, summ, adm = _fake(f, admissible=lambda d, p: p["a"] + p["b"] <= 5)
    out = S.pair_grids(["d"], {"d": {"a": 1.0, "b": 1.0}}, space, {"d": ("a", "b")},
                       ev, summ, adm, is_valid=lambda d, p: p["a"] != p["b"])
    assert len(out["d"]["cells"]) == 6
    assert out["d"]["best"] in ({"a": 2.0, "b": 3.0}, {"a": 3.0, "b": 2.0})


@pytest.mark.parametrize("setting,grid,low,expected", [
    ("threshold_pctile", [99.0, 99.9], False, 99.95),
    ("threshold_pctile", [99.0, 99.9], True, 98.0),
    ("n_synchronous_frames", [1, 2], True, None),    # cannot go below one frame
    ("alpha", [1e-4, 1e-2], False, 3e-2),
    ("C_threshold", [0.1, 0.9], False, 1.0),
    # Counts step as counts, and a participant floor stops at two cells (PR #754: the
    # combined search returned SPIKE-synch at min_n 0.25 by halving 2 -> 1 -> 0.5 -> 0.25).
    ("min_n", [2, 3, 8], True, None),
    ("min_rois", [3, 6, 8], True, 2),
    ("min_rois", [2, 3, 8], False, 16),
    ("min_n", [2, 3], False, 4),
    ("n_surrogates", [100, 200], True, 50),              # an all-integer grid is a count too
])
def test_extending_a_grid_respects_what_the_setting_can_be(setting, grid, low, expected):
    new = S.extend(setting, grid, low_end=low)
    assert new == (None if expected is None else pytest.approx(expected))


def test_validity_rejects_a_window_shorter_than_what_fills_it():
    assert not S.valid("coact", {"int_win_sec": 5.0, "context_win_sec": 10.0})
    assert S.valid("coact", {"int_win_sec": 2.0, "context_win_sec": 60.0})
    assert not S.valid("sync", {"C_min": 0.2, "C_threshold": 0.1})
