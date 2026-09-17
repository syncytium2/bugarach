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


def test_the_same_settings_are_scored_once(search):
    """A fold pays for a search; paying twice for one setting is the caller's compute."""
    calls = []
    search.choose_settings("rate", score=lambda p: (calls.append(1), 1.0)[1])
    got = search.choose_settings("rate", score=lambda p: 1.0)
    assert got.n_scored == len(calls)
