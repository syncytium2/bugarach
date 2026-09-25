"""A score reported with the background it was measured at, rather than at one point.

`docs/RESET.md` §7 item 2: *"The background axis becomes a reported curve, not a
point."* §6 says why — operating points are chosen at one place on this axis and
quoted as though they held across it, across a 3.7-fold rate change that is only
the interquartile spread of *untreated* slices.

This is the same move `TOLERANCE_GRID` made for the matching tolerance, and it
lands in the opposite place. **Five of six detectors were flat across the
tolerance grid**, so that inherited constant was granting slack nobody used and
no comparison rested on it — reassuring, and cheap. **Five of six are *not* flat
across the background grid**, which is the claim that matters, and it was *six of
six* until 2026-09-22: adopting the measured jitter (0.36 → 0.106 s) put
SPIKE-synch flat at F1 0.657, spread 0.026. See `BACKGROUND_FLAT` below for the
mechanism and for what is still open about it.

⚠ **Re-measured 2026-09-22, when `REGIMES` became BACKGROUND rates** (Tony: *background,
end to end*) and the axis moved from 5.2–19 mHz to 4.2–16.5 mHz, the grid with it. Two
claims below reversed, and they are restated as measured rather than re-baselined — no
tolerance was loosened and no test skipped:

* **No detector is a steady leader across the whole axis any more.** Three now win
  somewhere on the grid: CoactDetect at the quiet end, LoCo through the middle,
  SPIKE-synch at the busy end. The leader *does* still hold between the two named
  `REGIMES` endpoints, which is where the project reports.
* **The fitted/flat contrast this file is named for is gone.** Both fields now show the
  same flat set, the same three winners and the same largest rank change (four places,
  SPIKE-synch, *rising*). What still separates them is magnitude: mean own-range 0.126
  fitted against 0.171 flat, so the fitted axis is about a quarter shorter and has not
  gone dead.

Both follow from one thing already ruled a result rather than a defect (#738): SPIKE-synch
went flat when the measured jitter was adopted, and **a flat detector on a declining axis
eventually overtakes the ones that decline**. Nothing collapses down the table; the mover
is the detector that does not move.

What these tests pin
--------------------
1. Every detector outside `BACKGROUND_FLAT` refuses a bare F1 (`describe_background`),
   and the flat set is exactly what was last measured — it fails in both directions.
2. The axis still discriminates on the fitted field — every detector moves across it, and
   they stay apart at any given rate — and the leader holds **between the two named
   `REGIMES` endpoints**, though no longer across the whole grid.
3. **The reordering the first version of this file pinned was the flat field's** — and as
   of 2026-09-22 the fitted field reorders the same way, so only the magnitude contrast
   is asserted.
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

**Re-measured 2026-09-16**, when locust's shipped setting stopped holding every cell
for a fixed second and started reading each event's width. Same twelve seeds:
fitted field, one winner (CoactDetect) and a largest rank change of two, mean
own-range 0.133; flat field, three winners (CoactDetect, LoCo, rate+context) and a
largest rank change of **two**, own-range 0.187. The winner contrast is unchanged;
the rank-change contrast is gone — both fields now move a detector two places — so
the paired test asserts the first strictly and the second only as "no worse".

**And again the same day, after the gated retune** (LoCo 99.5, rate+context 4.5 Hz,
binned SCE 98). Fitted field: CoactDetect and LoCo sit 0.003–0.008 F1 apart over most
of the axis, and a raw "first place" flipped to LoCo at 19 mHz on a 0.003 difference;
CoactDetect's largest deficit to the top anywhere is **0.003**. Flat field: no detector
stays within 0.03 of the top everywhere (LoCo 0.033, CoactDetect 0.069). So the claim
is restated with a tie margin (``TIE_F1``, 0.01): the fitted field has a steady leader
and the flat field does not. Largest rank change: fitted **three** (rate+context,
third to last at 40 mHz inside a 0.49–0.53 cluster), flat two — no longer asserted as
a contrast.

The regime argument does not change the curve. `baseline_quiet` and
`baseline_busy` differ only in `bg_rate_hz`, which is the parameter the sweep
replaces, so `evaluate_background_curve` returns the same numbers for either.
The tests run `baseline_quiet` and say so, rather than pretending to sweep two.

Nothing here recalibrates anything. `REGIMES` is untouched, no operating point
moves, and `evaluate` is unchanged — this reports across the axis that already
exists, which is what makes it checkable rather than a new opinion.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from bugarach import bench, bench_combined, bench_slow, dataset, groups
from bugarach.bench import (BACKGROUND_GRID, BACKGROUND_TOLERABLE_SPREAD,
                            DETECTORS, REGIMES, background_spread,
                            describe_background, evaluate,
                            evaluate_background_curve)

# Pre-ADR-0008 by construction: these pin measurements taken before the floor, or exercise detector
# mechanics it has nothing to do with. The floor's own tests are tests/test_bench_floor.py.
pytestmark = pytest.mark.usefixtures("pre_adr_0008_bench")


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


BENCHES = {"fast": bench, "slow": bench_slow, "combined": bench_combined}

GROUP_RECORD = (Path(__file__).resolve().parents[1] / "docs" / "learned" / "runs"
                / "2026-09-23-groups-rates-comod-66" / "coordination_rates.json")


@pytest.mark.parametrize("stream", list(BENCHES))
def test_both_regime_endpoints_are_on_the_grid(stream):
    """The grid has to contain the axis it is reporting across, or the curve and
    the shipped numbers are measured at different places and cannot be compared.
    Each bench carries its own grid since 2026-09-23."""
    b = BENCHES[stream]
    quiet = b.REGIMES["baseline_quiet"]["bg_rate_hz"]
    busy = b.REGIMES["baseline_busy"]["bg_rate_hz"]
    assert quiet in b.BACKGROUND_GRID, (quiet, b.BACKGROUND_GRID)
    assert busy in b.BACKGROUND_GRID, (busy, b.BACKGROUND_GRID)
    assert min(b.BACKGROUND_GRID) < quiet, (
        "the grid stops at the quiet endpoint, so it cannot show whether a "
        "detector was about to fall off it")
    assert sum(r > busy for r in b.BACKGROUND_GRID) >= 2, "two points above busy"
    assert list(b.BACKGROUND_GRID) == sorted(b.BACKGROUND_GRID)


@pytest.mark.parametrize("stream", list(BENCHES))
def test_the_grid_covers_every_groups_interquartile_background(stream):
    """The regimes turned out to be the spread between groups (2026-09-23), so a grid that
    stops at them leaves ORX below it and DI above it. Checked against the group record
    itself, and against the folder that record was measured on, so a grid that drifts
    or a record that goes stale fails here rather than in a figure."""
    rec = json.loads(GROUP_RECORD.read_text(encoding="utf-8"))
    assert rec["dataset"]["name"] == dataset.current_name("default"), (
        "the group record was measured on another folder: re-run it before trusting "
        "this coverage check")
    stats = rec["by_group"][stream]["stats"]
    grid = BENCHES[stream].BACKGROUND_GRID
    for g in groups.GROUP_ORDER:
        lo = stats["background_q25_hz"]["groups"][g]["value"]
        hi = stats["background_q75_hz"]["groups"][g]["value"]
        assert min(grid) <= lo, f"{stream}: {g} lower quartile {lo:.5f} Hz is below the grid"
        assert max(grid) >= hi, f"{stream}: {g} upper quartile {hi:.5f} Hz is above the grid"


@pytest.mark.parametrize("stream", ["slow", "combined"])
def test_the_slow_and_combined_curves_agree_with_the_point_estimate(stream):
    """The same identity as the fast test below, on the benches that gained a grid."""
    b = BENCHES[stream]
    name = b.DETECTORS[0]
    quiet = b.REGIMES["baseline_quiet"]["bg_rate_hz"]
    seeds = (1, 2)
    curve = b.evaluate_background_curve(name, "baseline_quiet", seeds, rates=(quiet,))
    point = b.evaluate(name, "baseline_quiet", seeds)
    assert curve[quiet].f1 == pytest.approx(point.f1)


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


# ------------------------------------------------- five of six are not flat

#: The detectors measured flat across the background axis on the CURRENT bench.
#:
#: Empty until 2026-09-22, and the section above this line used to be called "nothing is
#: flat". Adopting the measured jitter (0.36 -> 0.106 s, Tony's ruling that evening) put
#: SPIKE-synch at F1 0.657 with a spread of 0.026 across the whole grid, under
#: `BACKGROUND_TOLERABLE_SPREAD`. The other five still spread 0.081 to 0.178.
#:
#: The mechanism is not mysterious: `sync` is the one detector keying on coincidence
#: TIMING rather than on counts or rate, so sharpening planted jitter by about 3.4x
#: sharpened exactly what it reads, and it stopped degrading as the field fills up. The
#: bench got easier for one detector in particular. It is NOT a quantisation artefact of
#: planting 0.106 s on a 0.1 s grid -- the correlogram's calibration resolves 0.05 from
#: 0.10 from 0.15 s cleanly.
#:
#: ⚠ This records a MEASUREMENT, not a decision. Whether the difficulty axis should be
#: re-derived around the corrected jitter, or the MILESTONES row that says "nothing is
#: flat across it" corrected to match, is Tony's and is open:
#: `docs/todo/2026-09-22-the-corrected-jitter-flattens-spike-synch-across-the-axis.md`.
#: The tolerance was NOT loosened to absorb this, and the test below fails if the set
#: changes in either direction.
BACKGROUND_FLAT = {"sync"}


def test_the_flat_set_is_exactly_what_was_measured(curves):
    """The guard that keeps `BACKGROUND_FLAT` honest.

    It fails if another detector goes flat — the axis losing its power to
    discriminate is the thing worth knowing early — and equally if `sync` stops being
    flat, because then the exception above is stale and should come out rather than sit
    there excusing a detector that no longer needs it.
    """
    spreads = {n: background_spread(curves[n]) for n in DETECTORS}
    flat = {n for n, s in spreads.items() if s <= BACKGROUND_TOLERABLE_SPREAD}
    assert flat == BACKGROUND_FLAT, (
        f"the set of background-flat detectors moved: measured {sorted(flat)}, "
        f"BACKGROUND_FLAT holds {sorted(BACKGROUND_FLAT)}. Spreads: "
        + ", ".join(f"{n} {s:.3f}" for n, s in sorted(spreads.items(), key=lambda kv: kv[1]))
        + f" against a tolerance of {BACKGROUND_TOLERABLE_SPREAD}.")


def test_every_detector_but_the_known_flat_one_refuses_a_bare_f1(curves):
    """The headline, and the contrast with the tolerance curve.

    `describe_curve` settles for five of six on the tolerance axis. On the background
    axis `describe_background` settled for none of them until 2026-09-22 and now settles
    for one: five detectors' scores still move more across the axis than the threshold
    allows, so a single F1 for any of those five hides where it was measured.
    """
    said = {n: describe_background(curves[n]) for n in DETECTORS}
    for n, s in said.items():
        if n in BACKGROUND_FLAT:
            assert "flat across" in s, f"{n} is in BACKGROUND_FLAT but reported: {s}"
            continue
        assert "NOT one number" in s, f"{n} reported a bare F1: {s}"
        assert "depends on the background rate" in s, (n, s)


def test_the_spreads_dwarf_the_differences_the_bakeoff_asks_about(curves):
    """0.017 separates the top two rows of the published table. Every detector outside
    `BACKGROUND_FLAT` moves several times that with the background alone, which is what
    makes a bare F1 uncomparable rather than merely imprecise."""
    spreads = {n: background_spread(curves[n]) for n in DETECTORS
               if n not in BACKGROUND_FLAT}
    assert spreads, "every detector went flat — the axis has stopped discriminating"
    assert min(spreads.values()) > BACKGROUND_TOLERABLE_SPREAD, spreads
    # the published gap between the tube and CoactDetect
    assert min(spreads.values()) > 3 * 0.017, spreads


# ------------------------------------------------- and the ranking holds

def _order(curves, rate):
    return sorted(DETECTORS, key=lambda n: -curves[n][rate].f1)


def _winners(curves):
    return {_order(curves, r)[0] for r in BACKGROUND_GRID}


def _worst_rank_change_with_name(curves):
    """The largest rank change and who made it — the name matters since 2026-09-22,
    when the mover became the detector that RISES rather than one that falls."""
    worst, who = 0, None
    for n in DETECTORS:
        ranks = [_order(curves, r).index(n) for r in BACKGROUND_GRID]
        if max(ranks) - min(ranks) > worst:
            worst, who = max(ranks) - min(ranks), n
    return worst, who


def _worst_rank_change(curves):
    worst = 0
    for n in DETECTORS:
        ranks = [_order(curves, r).index(n) for r in BACKGROUND_GRID]
        worst = max(worst, max(ranks) - min(ranks))
    return worst


def _mean_own_range(curves):
    return sum(background_spread(curves[n]) for n in DETECTORS) / len(DETECTORS)


#: F1 inside which two detectors are tied for the purposes of "who leads". Since the
#: 2026-09-16 retune, CoactDetect and LoCo sit 0.003–0.008 apart over most of the axis,
#: and a strict "first place" flipped between them on a 0.003 difference at one grid
#: point. Twelve recordings do not resolve that, so a raw rank was measuring noise.
TIE_F1 = 0.01


def _steady_leaders(curves, rates=BACKGROUND_GRID):
    """Detectors never more than TIE_F1 below the top at any of ``rates``."""
    return {n for n in DETECTORS
            if all(max(curves[m][r].f1 for m in DETECTORS) - curves[n][r].f1 <= TIE_F1
                   for r in rates)}


def test_no_winner_holds_across_the_whole_axis_since_the_regimes_became_background(curves):
    """**Reversed 2026-09-22, re-measured rather than re-baselined.**

    This test asserted the opposite — that some detector stays within ``TIE_F1`` of the
    best at every rate — and that held while the axis ran 5.2 to 19 mHz. Adopting the
    **background** regimes moved it to 4.2 to 16.5 mHz, and the grid with it, and at
    twelve seeds on the fitted field **no detector is a steady leader any more**.

    The mechanism is one #738 already ruled on. SPIKE-synch went flat when the measured
    jitter was adopted, and a flat detector on a declining axis eventually overtakes:
    every other detector falls with rate and sync does not, so sync is **top at 25 mHz**
    (0.665 against LoCo 0.657 and CoactDetect 0.633) having been fourth at 2.1 mHz.
    Three detectors now win somewhere on the grid — CoactDetect at the quiet end, LoCo
    through the middle, SPIKE-synch at the busy end.

    **The leader still holds where the project reports**, between the two named
    ``REGIMES`` endpoints: that is the test below, and it still passes, LoCo being
    within the tie margin at both. What ended is the stronger claim across the whole
    grid, including the two points beyond the busy endpoint.

    Asserted as the mechanism and not merely as an absence, so it cannot pass for an
    unrelated reason. ``TIE_F1`` is untouched.

    **Re-measured 2026-09-23 on the bench retuned to the 66-recording default**, grid
    1.8–37 mHz, twelve seeds. Still no steady leader, and SPIKE-synch is still flat
    (spread 0.021) and still rises, from fifth at 1.8 mHz to **second** at 25 mHz (0.654
    against LoCo 0.665). It no longer takes the top anywhere, so the winners are two,
    CoactDetect and LoCo, alternating through the quiet half and LoCo from 16.9 mHz up."""
    assert not _steady_leaders(curves), (
        "a steady leader is back across the whole axis; that is a real change from the "
        "2026-09-23 measurement and the docstring above is now wrong")
    assert _winners(curves) == {"coact", "loco"}, _winners(curves)
    assert _order(curves, 0.0250).index("sync") == 1, (
        "SPIKE-synch is no longer second at 25 mHz, so the rise this test explains has "
        "changed shape")
    assert background_spread(curves["sync"]) <= BACKGROUND_TOLERABLE_SPREAD, (
        "SPIKE-synch is no longer flat, so the overtaking has a different cause and "
        "the explanation must be re-measured")


def test_the_winner_holds_between_the_two_named_endpoints(curves):
    """`baseline_quiet` to `baseline_busy` is the interquartile spread of
    untreated slices — both regimes this project fits and reports at. The old
    assertion was that the winner changed between them. It does not: one detector
    is within ``TIE_F1`` of the best at both, and twelve is the seed count this was
    measured at."""
    assert _steady_leaders(curves, (QUIET_HZ, BUSY_HZ)), (
        "no detector is within the tie margin of the best at both named regimes "
        "— a reordering between them is exactly what the fitted field was measured "
        "not to do")


def test_the_largest_rank_change_is_spike_synch_rising(curves):
    """**Restated 2026-09-22**, and the direction is the point.

    This asserted no detector moved more than three places, the fitted field having
    measured two and then three (rate+context falling into a 0.49–0.53 cluster). On the
    background axis the largest change is **four places, and it is a rise, not a fall**:
    SPIKE-synch goes from fourth at 2.1 mHz to first at 25 mHz.

    That is the same flatness as the test above, counted a second way, and it is worth
    counting separately because the old claim's *worry* was a detector collapsing down
    the table — the flat field's signature. Nothing collapses here: the mover is the one
    detector that does not decline, overtaking four that do. The rank change is
    therefore not evidence that the fitted field has started behaving like the flat one,
    and the paired test below is where that comparison is actually made.

    Pinned exactly, with the mover and its direction named, so that a detector
    genuinely crossing the table downwards still fails this.

    **Three places since 2026-09-23**, on the bench retuned to the 66-recording default:
    SPIKE-synch goes from fifth at 1.8 mHz to second at 25 and 37 mHz. Same mover, same
    direction, one place shorter, because it no longer overtakes LoCo at the busy end."""
    worst, who = _worst_rank_change_with_name(curves)
    assert (worst, who) == (3, "sync"), (
        f"the largest rank change is {worst} places by {who}; 2026-09-23 measured three "
        "by SPIKE-synch, rising. A different mover, or a larger change, is a new "
        "finding and needs measuring rather than re-baselining")
    quiet_rank = _order(curves, BACKGROUND_GRID[0]).index("sync")
    best_rank = min(_order(curves, r).index("sync") for r in BACKGROUND_GRID)
    assert best_rank < quiet_rank, (
        "SPIKE-synch's largest rank change is downward, which would be the flat "
        "field's signature rather than the flatness this test describes")


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
    # ⚠ REVERSED 2026-09-22 — for Tony. This asserted the contrast the whole file is
    # named for: a steady leader on the fitted field and none on the flat one. On the
    # background axis **neither field has one**, and the two now agree on every
    # structural measure — same flat set {sync}, same three winners
    # {coact, loco, sync}, same largest rank change of four, both by SPIKE-synch.
    # The ordering contrast is gone, so it is not asserted; what survives is the
    # magnitude contrast below, and it is the reading the 2026-08-28 handoff called
    # (a). Kept as a measured equality rather than deleted, so that the fields
    # SEPARATING again is itself a failure worth seeing.
    #
    # ⚠ SEPARATED AGAIN 2026-09-23, on the bench retuned to the 66-recording default and
    # its 1.8–37 mHz grid — the failure the comment above asked to see. Neither field has
    # a steady leader, but the fitted field now has two winners {coact, loco} and a
    # largest rank change of three, while the flat field keeps three {loco, rate, sync}
    # and four. So the ordering contrast is back, in the direction the file is named for:
    # the flat field reorders more.
    assert not _steady_leaders(curves) and not _steady_leaders(flat_curves), (
        "the two fields no longer agree about steady leaders; on 2026-09-23 neither "
        "had one, and a difference reopening here is a finding, not a regression")
    assert _winners(curves) == {"coact", "loco"}, _winners(curves)
    assert _winners(flat_curves) == {"loco", "rate", "sync"}, _winners(flat_curves)
    assert _worst_rank_change(curves) < _worst_rank_change(flat_curves), (
        "the fitted field reorders as much as the flat one again; on 2026-09-23 it "
        "measured three places against four")
    # Rank change no longer separates the fields. It was `>= 3` flat and strictly
    # less fitted; after locust went per-event both measured two, and after the
    # retune of the same day fitted measures three and flat two — the move being
    # rate+context inside a 0.04-wide cluster. The steady-leader contrast above is
    # the one that survives: see the module docstring's 2026-09-16 notes.

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
