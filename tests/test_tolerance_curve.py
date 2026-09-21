"""A score reported with the tolerance it needed, rather than at one constant.

The bench counts a hit at a 1.5 s edge gap against a median realized event 0.80 s
wide. That constant was inherited, never chosen, and a bare F1 built on it asserts
a timing accuracy nobody checked — `docs/todo/2026-08-17-scoring-cannot-see-
localization.md`.

Rather than pick a different constant, the bench reports the **curve**, which is
what DOSED does. These tests pin the two things that makes true: the curve costs
nothing (the top of the ranking does not depend on it) and it would name any
detector whose score does. It named binned SCE until 2026-09-16, when SCE began
to be scored over its own bin and its curve went flat — the dependence had been
the scorer's.
"""

from __future__ import annotations

import pytest

from bugarach.bench import (DETECTORS, TOLERANCE_GRID, describe_curve,
                            evaluate, evaluate_curve, plateau_tol)
from bugarach.score import TOL_SEC

SEEDS = (1, 2, 3)
REGIME = "baseline_quiet"


@pytest.fixture(scope="module")
def curves():
    return {n: evaluate_curve(n, REGIME, SEEDS) for n in DETECTORS}


def test_the_curve_scores_the_same_detections_the_point_estimate_does(curves):
    """The curve must isolate the SCORING rule. Detection runs once per seed and
    every tolerance scores those same detections, so the value at 1.5 s has to
    match `evaluate` at 1.5 s exactly — if it drifts, the curve is folding
    detector RNG into what is supposed to be a property of the scorer."""
    for n in DETECTORS:
        point = evaluate(n, REGIME, SEEDS, tol_sec=1.5)
        assert curves[n][1.5].f1 == pytest.approx(point.f1), n
        assert curves[n][1.5].n_hit == point.n_hit, n


def test_all_six_settle_at_or_below_the_shipped_tolerance(curves):
    """The reassuring half, and the reason this is cheap: a detector whose score
    has stopped moving by the shipped tolerance is one no comparison rests on the
    slack of.

    **Six, since 2026-09-16; it was five.** Binned SCE was the exception, and its
    exception was the scorer's: see the next test.

    **It reads the constant now, not a literal 1.5.** On the flat background the
    five settled *far* below the shipped value and this test said so. Wiring the
    fitted background in moved LoCo and CoactDetect to 2.5 s and RateDetect to
    2.0 s — a realistic field spreads the same events over a wider window — so
    the tolerance moved with them (`score.TOL_SEC`, 1.5 → 2.5; Tony, 2026-08-28:
    *"expand the tolerance"*).

    Asserting against the constant is what keeps the two from drifting apart
    again: lower `TOL_SEC` under a plateau and this fails, which is the alarm
    worth having, because every F1 in the bench would be understating its
    detector.
    """
    flat = {n: plateau_tol(curves[n]) for n in DETECTORS}
    settled = {n: t for n, t in flat.items() if t is not None}
    assert len(settled) == 6, f"expected all six to settle, got {flat}"
    assert max(settled.values()) <= TOL_SEC, (
        f"a detector plateaus only above the shipped tolerance {TOL_SEC}s: "
        f"{settled} — every F1 in the bench is understating it")


def test_binned_sce_does_not_depend_on_the_slack_once_scored_over_its_bin(curves):
    """The finding this test used to record, and why it no longer holds.

    Until 2026-09-16 this test asserted the opposite: binned SCE was **still
    climbing at 3 s** (F1 0.239 at 0.1 s rising to 0.448 at 3 s on these seeds),
    and the reading was that 10 s bins are coarse and only a loose tolerance
    credits them. That was the scorer. It read a call as ``[bin start, bin start
    + event spread]``, a stretch that ends before any event late in the bin, so
    every extra second of tolerance reached a few more events the call had
    actually been made on. Scored over its own bin (``SceStream.extent_sec``),
    every planted event it found lies inside the stretch, the curve is flat from
    the narrowest gap scored, and F1 is 0.567 at every tolerance
    (``docs/todo/2026-09-15-binned-sce-calls-are-scored-over-the-wrong-stretch.md``).

    **Expected to fail if the scorer stops reading ``extent_sec``**, which is the
    point: that is the defect coming back."""
    assert plateau_tol(curves["sce"]) == min(TOLERANCE_GRID), (
        f"SCE's F1 moves with the tolerance again "
        f"({describe_curve(curves['sce'])}) — is the scorer still reading the "
        "bin extent rather than width_sec?")


def test_the_top_never_moves_and_a_reordering_needs_a_score_that_moved(curves):
    """How low-stakes the choice is — stated more precisely than I first had it.

    ⚠ **A correction.** An earlier reading of `docs/learned/tolerance_sweep.json`
    said the ranking is *unchanged* from 0.4 s to 2.0 s, and the caption of
    `docs/learned/two_decisions.png` says so. That is true of that archived
    sweep and **not** true at the shipped operating points.

    ⚠ **And a second one, 2026-09-16.** This test used to say every reordering
    involves SCE, "the one detector whose score depends on the tolerance". Scored
    over its bin, SCE's score does not depend on it (the test above), and the one
    swap left — SCE and RateDetect in third and fourth at 2.0 s — happens because
    RateDetect's F1 steps from 0.564 to 0.590 where its own curve plateaus, past
    SCE's flat 0.567.

    What survives both: **the top two never move, and a reordering always needs
    a detector whose own F1 moved between the two tolerances** — the instability
    is where some curve is still changing, which is what the curve exists to
    show."""
    def order(t):
        return [n for n in sorted(DETECTORS, key=lambda k: -curves[k][t].f1)]

    mid = [t for t in TOLERANCE_GRID if 0.4 <= t <= 2.0]
    first = order(mid[0])
    for t in mid[1:]:
        now = order(t)
        assert now[:2] == first[:2], (
            f"the top of the ranking moved at {t}s: {now} vs {first}")
        moved = {a for a, b in zip(now, first) if a != b}
        changed = {n for n in DETECTORS
                   if abs(curves[n][t].f1 - curves[n][mid[0]].f1) > 1e-9}
        assert not moved or moved & changed, (
            f"a reordering at {t}s ({moved}) with no score that moved")


def test_a_climbing_detector_is_not_reported_as_a_bare_number(curves):
    """describe_curve is what anything human-facing should print. For a detector
    still climbing it must say so rather than hand over a number that reads like
    an accuracy.

    No detector on the bench climbs any more (binned SCE did until it was scored
    over its bin), so the climbing case is a curve built by hand."""
    class R:
        def __init__(self, f1):
            self.f1 = f1

    said = describe_curve({0.5: R(0.3), 1.5: R(0.4), 3.0: R(0.45)})
    assert "STILL CLIMBING" in said, said
    assert "depends on the matching tolerance" in said, said

    for n in ("coact", "sce"):
        settled = describe_curve(curves[n])
        assert "flat from" in settled, (n, settled)


def test_plateau_is_none_when_the_curve_is_still_rising_at_the_end():
    """The helper's own rule, on a curve built by hand so the detectors cannot
    quietly change what is being tested."""
    class R:
        def __init__(self, f1):
            self.f1 = f1

    assert plateau_tol({0.5: R(0.4), 1.0: R(0.6), 1.5: R(0.9)}) is None
    assert plateau_tol({0.5: R(0.4), 1.0: R(0.9), 1.5: R(0.9)}) == 1.0
    assert plateau_tol({0.5: R(0.9), 1.0: R(0.9), 1.5: R(0.9)}) == 0.5
