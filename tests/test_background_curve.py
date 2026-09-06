"""A score reported with the background it was measured at, rather than at one point.

`docs/RESET.md` §7 item 2: *"The background axis becomes a reported curve, not a
point."* §6 says why — operating points are chosen at one place on this axis and
quoted as though they held across it, across a 3.7-fold rate change that is only
the interquartile spread of *untreated* slices.

This is the same move `TOLERANCE_GRID` made for the matching tolerance, and it
lands in the opposite place. **Five of six detectors were flat across the
tolerance grid**, so that inherited constant was granting slack nobody used and
no comparison rested on it — reassuring, and cheap. **Nothing is flat across the
background grid.**

What these tests pin
--------------------
1. Every one of the six refuses a bare F1 (`describe_background`).
2. The axis still discriminates on the fitted field — every detector moves across
   it, and they stay apart at any given rate — and **one winner holds across it**,
   at both named `REGIMES` endpoints and everywhere between.
3. **The reordering the first version of this file pinned was the flat field's.**
   That version asserted three winners along the axis and one detector moving four
   places, and it was measured before `BENCH_RECORDING` carried the fitted
   background. The paired measurement below runs the same seeds on the same grid
   with the background shapes switched off: the flat field reorders the table and
   the fitted one does not. On a flat field a higher mean rate raises every ROI
   together, so the whole field degrades into a crowded low-F1 tail where crossings
   are cheap; on a heterogeneous field the same increase concentrates in ROIs that
   were already busy, and nobody falls into that tail. The rank change was real, and
   it was happening in a regime the flat background manufactured.
   Measured and written up before it was asserted here:
   `docs/handoffs/2026-08-28-the-winner-stopped-changing.md`.
4. The curve agrees with `evaluate` where the grid meets a regime, so the curve
   is the same measurement rather than a second one.

Seeds — twelve, chosen on purpose. The first version ran three and the handoff
that measured the change ran six; at those counts *"one winner"* and *"one winner
nearly everywhere"* are inside seed noise, and a ranking is exactly the kind of
assertion seeds move. At twelve, on 2026-09-06: fitted field, one winner at all
seven grid points and a largest rank change of two; flat field, same seeds, three
winners and a largest rank change of three. Mean own-range 0.132 against 0.170,
so the axis shrank by about a quarter and did not go dead.

The regime argument does not change the curve. `baseline_quiet` and
`baseline_busy` differ only in `bg_rate_hz`, which is the parameter the sweep
replaces, so `evaluate_background_curve` returns the same numbers for either.
The tests run `baseline_quiet` and say so, rather than pretending to sweep two.

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

SEEDS = tuple(range(1, 13))
REGIME = "baseline_quiet"

# The old background, reached from the new tree: `evaluate` and the curve accept a
# generator override, and the two shapes set to None is exactly the flat field every
# number published before 2026-08-28 was measured on.
FLAT_FIELD = {"bg_rate_shape": None, "bg_burst_shape": None}

QUIET_HZ = REGIMES["baseline_quiet"]["bg_rate_hz"]
BUSY_HZ = REGIMES["baseline_busy"]["bg_rate_hz"]


@pytest.fixture(scope="module")
def curves():
    return {n: evaluate_background_curve(n, REGIME, SEEDS) for n in DETECTORS}


@pytest.fixture(scope="module")
def flat_curves():
    return {n: evaluate_background_curve(n, REGIME, SEEDS, gen=FLAT_FIELD)
            for n in DETECTORS}


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


# ------------------------------------------------- and the ranking holds

def _order(curves, rate):
    return sorted(DETECTORS, key=lambda n: -curves[n][rate].f1)


def _winners(curves):
    return {_order(curves, r)[0] for r in BACKGROUND_GRID}


def _worst_rank_change(curves):
    worst = 0
    for n in DETECTORS:
        ranks = [_order(curves, r).index(n) for r in BACKGROUND_GRID]
        worst = max(worst, max(ranks) - min(ranks))
    return worst


def _mean_own_range(curves):
    return sum(background_spread(curves[n]) for n in DETECTORS) / len(DETECTORS)


def test_one_winner_holds_across_the_axis(curves):
    """The first version of this test asserted the opposite — more than one
    detector best somewhere on the grid — and that was true of the flat field.
    On the fitted one the top of the table does not move. Pinned as *one winner*
    rather than as its name, so the test says something true if the detectors
    change and a different one comes to lead."""
    winners = _winners(curves)
    assert len(winners) == 1, (
        f"the winner changes along the axis ({sorted(winners)}); at twelve seeds on "
        "the fitted field it did not, and the reordering that used to be here was "
        "measured to be the flat field's — see the module docstring before "
        "re-baselining this")


def test_the_winner_holds_between_the_two_named_endpoints(curves):
    """`baseline_quiet` to `baseline_busy` is the interquartile spread of
    untreated slices — both regimes this project fits and reports at. The old
    assertion was that the winner changed between them. It does not, and the
    gap to the runner-up at the busy end is small enough that this is the
    assertion seeds could most plausibly move; twelve is the count it holds at."""
    quiet_best = _order(curves, QUIET_HZ)[0]
    busy_best = _order(curves, BUSY_HZ)[0]
    assert quiet_best == busy_best, (
        f"{quiet_best} wins at the quiet endpoint and {busy_best} at the busy one "
        "— a reordering between the two named regimes is exactly what the fitted "
        "field was measured not to do")


def test_no_detector_falls_most_of_the_way_down_the_table(curves):
    """CoactDetect went from first to fifth across the grid on the flat field.
    On the fitted field the largest rank change is two places — a detector can
    swap with a neighbour, and nothing crosses most of the table."""
    worst = _worst_rank_change(curves)
    assert worst <= 2, (
        f"the largest rank change across the axis is {worst} places; the fitted "
        "field was measured at two, and a table that unstable is the flat field's "
        "signature, not this one's")


def test_the_reordering_was_the_flat_fields(curves, flat_curves):
    """The paired measurement, and the reason the three tests above changed.

    Same seeds, same grid, same detectors; only the background model differs.
    The flat field reorders the table — several winners along the axis, a
    detector crossing most of it — and the fitted field does not. And the axis
    did not go dead in the move: every detector still travels across it on the
    fitted field, by at least half of what it travelled on the flat one.
    """
    assert len(_winners(flat_curves)) > 1, (
        "the flat field used to have three winners along the axis; if it now has "
        "one, the comparison this test rests on has changed and the docstring "
        "is wrong")
    assert _worst_rank_change(flat_curves) >= 3, (
        "the flat field used to move a detector most of the way down the table")
    assert _worst_rank_change(curves) < _worst_rank_change(flat_curves), (
        "the fitted field must be the more stable of the two, or the explanation "
        "in the module docstring is false")

    fitted, flat = _mean_own_range(curves), _mean_own_range(flat_curves)
    assert fitted > 0.5 * flat, (
        f"mean own-range fell from {flat:.3f} to {fitted:.3f} — more than half — "
        "which would mean the axis went dead rather than stable, the reading the "
        "handoff calls (b) and did not find")
    assert fitted > BACKGROUND_TOLERABLE_SPREAD, (fitted, BACKGROUND_TOLERABLE_SPREAD)


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
