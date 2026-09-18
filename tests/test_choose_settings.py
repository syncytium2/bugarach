"""`choose_settings` searches a caller's objective and never reaches for data of its own.

This is the seam goal 2 calls inside each outer fold of its nested cross-validation
(`docs/todo/2026-09-17-how-is-the-coded-side-searched-inside-nested-cross-validation.md`,
option A). What it guarantees is structural: the search sees two callbacks and a grid, so
it cannot score a recording the caller did not choose to score — which is how the
comparison keeps "nothing about a configuration is chosen with the fold it is scored on"
without either machine having to remember it.

So these tests use arithmetic objectives, not detectors: what is under test is the search,
not what it finds.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from bugarach import bench

TOOLS = Path(__file__).resolve().parents[1] / "tools"


@pytest.fixture(scope="module")
def search():
    spec = importlib.util.spec_from_file_location("_sas", TOOLS / "search_all_settings.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["_sas"] = m
    spec.loader.exec_module(m)
    return m


def test_it_finds_the_best_value_on_an_axis(search):
    """alpha 1e-3 is the peak; every other setting is flat."""
    got = search.choose_settings(
        "coact", score=lambda p: 1.0 if p["alpha"] == pytest.approx(1e-3) else 0.0)
    assert got.params["alpha"] == pytest.approx(1e-3)
    assert got.n_scored > 0 and got.detector == "coact"
    assert any(m["setting"] == "alpha" for m in got.moves)


def test_a_gain_smaller_than_min_gain_does_not_move_it(search):
    """`min_gain` defaults to an F1-sized epsilon, so an objective on another scale must
    say so or the search returns the starting point and reports nothing wrong."""
    def tiny(p):
        return 1e-6 if p["alpha"] == pytest.approx(1e-3) else 0.0

    start = {k: search.shipped_value("coact", k) for k in bench.FULL_GRIDS["coact"]}
    assert search.choose_settings("coact", score=tiny).params["alpha"] == \
        pytest.approx(start["alpha"]), "a gain under min_gain is not a move"
    assert search.choose_settings("coact", score=tiny, min_gain=1e-9).params["alpha"] == \
        pytest.approx(1e-3), "and the caller can say what counts as a gain"


def test_a_gate_keeps_it_off_settings_the_caller_refuses(search):
    """The ungated best is refused, so the search must take the best admissible one."""
    grid = bench.FULL_GRIDS["coact"]["alpha"]
    best, second = min(grid), sorted(grid)[1]

    def score(p):
        return {best: 10.0, second: 9.0}.get(p["alpha"], 0.0)

    ungated = search.choose_settings("coact", score=score)
    assert ungated.params["alpha"] == pytest.approx(best)

    gated = search.choose_settings("coact", score=score,
                                   admissible=lambda p: p["alpha"] != best)
    assert gated.params["alpha"] == pytest.approx(second)
    assert gated.n_refused >= 1 and ungated.n_refused == 0


def test_an_edge_is_reported_and_the_grid_does_not_grow(search):
    """Inside a fold the declared grid is fixed: the edge is data, not an extension.

    A grid that grew per fold would make the candidate set differ between folds, and the
    declaration on `main` would stop describing what ran.
    """
    grid = list(bench.FULL_GRIDS["sce"]["threshold_pctile"])
    got = search.choose_settings("sce", score=lambda p: p["threshold_pctile"])
    assert got.params["threshold_pctile"] == max(grid)
    assert got.edges.get("threshold_pctile") == "high"
    assert list(got.grids["threshold_pctile"]) == sorted(grid), "the grid must not grow"


def test_it_can_still_extend_for_goal_ones_own_search(search):
    """Goal 1 ships the value, so its search grows a range until the optimum is bracketed."""
    grid = list(bench.FULL_GRIDS["sce"]["threshold_pctile"])
    got = search.choose_settings("sce", score=lambda p: p["threshold_pctile"],
                                 extend_ranges=True)
    assert max(got.grids["threshold_pctile"]) > max(grid)


def test_it_scores_only_what_the_caller_gives_it(search):
    """Every setting scored must come from the declared grid, with the rest at the start.

    The structural half of the fairness guarantee: a search that reached for a recording,
    a background or a budget of its own could not make that promise.
    """
    grids = {"alpha": [1e-3, 1e-4], "int_win_sec": [1.0, 2.0], "context_win_sec": [60.0]}
    seen = []

    def score(p):
        seen.append(dict(p))
        return 1.0 if p["alpha"] == pytest.approx(1e-4) else 0.0

    got = search.choose_settings("coact", score=score, grids=grids,
                                 start={"alpha": 1e-3, "int_win_sec": 2.0,
                                        "context_win_sec": 60.0})
    assert got.params["alpha"] == pytest.approx(1e-4)
    for p in seen:
        assert set(p) == set(grids)
        for k, v in p.items():
            assert v in grids[k]


def test_invalid_combinations_are_never_scored(search):
    """`bench.settings_are_valid` is shared, so both machines reject the same combinations."""
    seen = []

    def score(p):
        seen.append(dict(p))
        return 0.0

    search.choose_settings("coact", score=score)
    assert seen, "the search must have scored something"
    assert all(bench.settings_are_valid("coact", p) for p in seen)


def test_a_categorical_axis_is_never_extended_and_never_called_an_edge(search):
    """"peak" is not an end of ("threshold", "peak") — a name has no ends, and `extend` has
    nothing to double past one."""
    got = search.choose_settings(
        "loco", score=lambda p: 1.0 if p["detection_mode"] == "peak" else 0.0,
        extend_ranges=True)
    assert got.params["detection_mode"] == "peak"
    assert "detection_mode" not in got.edges
    assert set(got.grids["detection_mode"]) == {"threshold", "peak"}


def test_a_switched_off_axis_is_not_searched_and_returns_when_its_parent_moves(search):
    """The peak-mode pair means nothing under threshold detection.

    Varying it there costs evaluations and returns identical answers, and a readout listing
    it as searched is a claim nobody can back.
    """
    seen = set()

    def flat(p):
        seen.add((p["detection_mode"], p["peak_prominence"]))
        return 0.0

    search.choose_settings("loco", score=flat)
    assert {m for m, _ in seen} == {"threshold", "peak"}, "the mode itself is searched"
    assert len({pr for m, pr in seen if m == "threshold"}) == 1, (
        "prominence must not be varied under threshold mode")

    seen.clear()

    def prefers_peak(p):
        seen.add((p["detection_mode"], p["peak_prominence"]))
        return 1.0 if p["detection_mode"] == "peak" else 0.0

    search.choose_settings("loco", score=prefers_peak)
    assert len({pr for m, pr in seen if m == "peak"}) > 1, (
        "once peak mode wins, its own settings must be searched")


def test_a_nan_start_is_carried_rather_than_put_in_the_grid(search):
    """Binned SCE ships `merge_gap_sec` NaN, meaning "do not merge".

    NaN is not equal to itself, so a grid holding it breaks `min`, `max` and every "is the
    start still the best" comparison in the search.
    """
    import math

    got = search.choose_settings("sce", score=lambda p: 0.0)
    assert math.isnan(got.params["merge_gap_sec"]), "nothing beat it, so it stays"
    assert not any(isinstance(v, float) and math.isnan(v) for v in got.grids["merge_gap_sec"])
    assert "merge_gap_sec" not in got.edges

    moved = search.choose_settings(
        "sce", score=lambda p: 0.0 if math.isnan(p["merge_gap_sec"]) else 1.0)
    assert not math.isnan(moved.params["merge_gap_sec"]), "and it can be moved off"


def test_every_declared_axis_is_a_real_parameter_of_its_detector():
    """A grid for a parameter the function does not take is a search of nothing."""
    import inspect

    from bugarach.detectors import (cicada_detect, coact_detect, loco_detect, rate_detect,
                                    sce_detect, sync_detect)

    fns = {"coact": coact_detect, "loco": loco_detect, "rate": rate_detect,
           "sce": sce_detect, "sync": sync_detect, "cicada": cicada_detect}
    for det, axes in bench.FULL_GRIDS.items():
        takes = set(inspect.signature(fns[det]).parameters)
        assert set(axes) <= takes, f"{det}: {sorted(set(axes) - takes)} is not a parameter"
    for det, skipped in bench.NOT_SEARCHED.items():
        takes = set(inspect.signature(fns[det]).parameters)
        assert set(skipped) <= takes, f"{det}: {sorted(set(skipped) - takes)} is not a parameter"
        assert not (set(skipped) & set(bench.FULL_GRIDS[det])), (
            f"{det}: a parameter cannot be both searched and recorded as not searched")


def test_the_same_settings_are_scored_once(search):
    """A fold pays for a search; paying twice for one setting is the caller's compute."""
    calls = []
    search.choose_settings("rate", score=lambda p: (calls.append(1), 1.0)[1])
    got = search.choose_settings("rate", score=lambda p: 1.0)
    assert got.n_scored == len(calls)
