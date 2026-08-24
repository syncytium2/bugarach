"""A score reported with the background it was measured at, rather than at one point.

`docs/RESET.md` §7 item 2: *"The background axis becomes a reported curve, not a
point."* §6 says why — operating points are chosen at one place on this axis and
quoted as though they held across it, across a 3.7-fold rate change that is only
the interquartile spread of *untreated* slices.

This is the same move `TOLERANCE_GRID` made for the matching tolerance, and it
lands in the opposite place. **Five of six detectors were flat across the
tolerance grid**, so that inherited constant was granting slack nobody used and
no comparison rested on it — reassuring, and cheap. **Nothing is flat across the
background grid**, and the ranking does not survive it either.

What these tests pin
--------------------
1. Every one of the six refuses a bare F1 (`describe_background`).
2. The **winner changes** across the axis, and it changes between the two named
   `REGIMES` endpoints rather than only at the extremes nobody runs at.
3. The curve agrees with `evaluate` where the grid meets a regime, so the curve
   is the same measurement rather than a second one.

Nothing here recalibrates anything. `REGIMES` is untouched, no operating point
moves, and `evaluate` is unchanged — this reports across the axis that already
exists, which is what makes it checkable rather than a new opinion.
"""

from __future__ import annotations

import pytest

from bugarach.bench import (BACKGROUND_GRID, BACKGROUND_TOLERABLE_SPREAD,
                            DETECTORS, REGIMES, background_spread,
                            describe_background, evaluate,
                            evaluate_background_curve)

SEEDS = (1, 2, 3)
REGIME = "baseline_quiet"

QUIET_HZ = REGIMES["baseline_quiet"]["bg_rate_hz"]
BUSY_HZ = REGIMES["baseline_busy"]["bg_rate_hz"]


@pytest.fixture(scope="module")
def curves():
    return {n: evaluate_background_curve(n, REGIME, SEEDS) for n in DETECTORS}


def test_both_regime_endpoints_are_on_the_grid():
    """The grid has to contain the axis it is reporting across, or the curve and
    the shipped numbers are measured at different places and cannot be compared."""
    assert QUIET_HZ in BACKGROUND_GRID, (QUIET_HZ, BACKGROUND_GRID)
    assert BUSY_HZ in BACKGROUND_GRID, (BUSY_HZ, BACKGROUND_GRID)
    assert min(BACKGROUND_GRID) < QUIET_HZ, (
        "the grid stops at the quiet endpoint, so it cannot show whether a "
        "detector was about to fall off it")
    assert max(BACKGROUND_GRID) > BUSY_HZ, "same, at the busy end"


def test_the_curve_agrees_with_the_point_estimate_at_the_regime(curves):
    """Where the grid meets `baseline_quiet`, the curve must equal `evaluate`.

    If it drifts, the curve is a second measurement rather than the same one
    reported across an axis, and every comparison below is against a different
    quantity than the shipped numbers.
    """
    for n in DETECTORS:
        point = evaluate(n, REGIME, SEEDS)
        assert curves[n][QUIET_HZ].f1 == pytest.approx(point.f1), n
        assert curves[n][QUIET_HZ].n_hit == point.n_hit, n


# ------------------------------------------------- nothing is flat

def test_every_detector_refuses_a_bare_f1(curves):
    """The headline, and the contrast with the tolerance curve.

    `describe_curve` settles for five of six. `describe_background` settles for
    none of them: every detector's score moves more across the background axis
    than the threshold allows, so a single F1 for any of them is a number that
    hides where it was measured.
    """
    said = {n: describe_background(curves[n]) for n in DETECTORS}
    for n, s in said.items():
        assert "NOT one number" in s, f"{n} reported a bare F1: {s}"
        assert "depends on the background rate" in s, (n, s)


def test_the_spreads_dwarf_the_differences_the_bakeoff_asks_about(curves):
    """0.017 separates the top two rows of the published table. Every detector
    here moves several times that with the background alone, which is what makes
    a bare F1 uncomparable rather than merely imprecise."""
    spreads = {n: background_spread(curves[n]) for n in DETECTORS}
    assert min(spreads.values()) > BACKGROUND_TOLERABLE_SPREAD, spreads
    # the published gap between the tube and CoactDetect
    assert min(spreads.values()) > 3 * 0.017, spreads


# ------------------------------------------------- and the ranking moves

def _order(curves, rate):
    return sorted(DETECTORS, key=lambda n: -curves[n][rate].f1)


def test_the_winner_changes_across_the_axis(curves):
    """The tolerance curve could report the reassuring version of this — the top
    of the table never moved. Here it does: more than one detector is best
    somewhere on the grid."""
    winners = {_order(curves, r)[0] for r in BACKGROUND_GRID}
    assert len(winners) > 1, (
        f"one detector won everywhere ({winners}), which would make the axis "
        "safe to quote across and is not what was measured")


def test_the_winner_changes_between_the_two_named_endpoints(curves):
    """**The one that matters.** A reordering only at rates nobody runs at would
    be a curiosity. This one happens between `baseline_quiet` and
    `baseline_busy` — the interquartile spread of untreated slices, both of them
    regimes this project fits and reports at."""
    quiet_best = _order(curves, QUIET_HZ)[0]
    busy_best = _order(curves, BUSY_HZ)[0]
    assert quiet_best != busy_best, (
        f"{quiet_best} wins at both endpoints — the reordering this test was "
        "written for has gone, which is good news worth looking at")


def test_a_detector_falls_most_of_the_way_down_the_table(curves):
    """CoactDetect was first at the quiet end and fifth at the busy end of the
    grid when this was written. Pinned as a large rank change rather than that
    exact pair, so the test says something true if the detectors move."""
    worst_drop = 0
    for n in DETECTORS:
        ranks = [_order(curves, r).index(n) for r in BACKGROUND_GRID]
        worst_drop = max(worst_drop, max(ranks) - min(ranks))
    assert worst_drop >= 3, (
        f"the largest rank change across the axis is {worst_drop} places; this "
        "was written when a detector moved four, and a table that stable would "
        "make the background safe to leave out of a comparison")


# ------------------------------------------------- the helper's own rule

def test_describe_background_settles_when_the_curve_really_is_flat():
    """Built by hand so the detectors cannot quietly change what is tested, and
    so the settling branch is exercised at all — no real detector reaches it."""
    class R:
        def __init__(self, f1):
            self.f1 = f1

    flat = {0.005: R(0.700), 0.019: R(0.710), 0.040: R(0.705)}
    said = describe_background(flat)
    assert "flat across" in said, said
    assert "NOT one number" not in said, said
    assert background_spread(flat) == pytest.approx(0.010)

    moving = {0.005: R(0.800), 0.019: R(0.700), 0.040: R(0.500)}
    said = describe_background(moving)
    assert "NOT one number" in said, said
    assert background_spread(moving) == pytest.approx(0.300)
