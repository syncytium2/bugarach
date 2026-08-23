"""A score reported with the tolerance it needed, rather than at one constant.

The bench counts a hit at a 1.5 s edge gap against a median realized event 0.80 s
wide. That constant was inherited, never chosen, and a bare F1 built on it asserts
a timing accuracy nobody checked — `docs/todo/2026-08-17-scoring-cannot-see-
localization.md`.

Rather than pick a different constant, the bench reports the **curve**, which is
what DOSED does. These tests pin the two things that makes true: the curve costs
nothing (the ranking does not depend on it) and it names the one detector whose
score does.
"""

from __future__ import annotations

import pytest

from bugarach.bench import (DETECTORS, TOLERANCE_GRID, describe_curve,
                            evaluate, evaluate_curve, plateau_tol)

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


def test_five_of_six_are_flat_well_below_the_shipped_tolerance(curves):
    """The reassuring half, and the reason this is cheap. If a detector's score
    stops moving far below 1.5 s, then the inherited constant was granting slack
    nobody was using and no comparison rested on it."""
    flat = {n: plateau_tol(curves[n]) for n in DETECTORS}
    settled = {n: t for n, t in flat.items() if t is not None}
    assert len(settled) == 5, f"expected five to settle, got {flat}"
    assert max(settled.values()) <= 1.5, (
        f"a detector plateaus only above the shipped tolerance: {settled}")


def test_binned_sce_is_the_one_whose_score_depends_on_the_slack(curves):
    """The finding the curve exists to surface, recorded as a measurement.

    SCE bins at 10 s, so its detections are coarse and only a loose tolerance
    credits them — it is still climbing at the widest gap scored. A single F1 for
    it is a statement about the tolerance as much as about the detector.

    **Expected to fail if SCE's bin width changes**, which is the point: update
    the measurement rather than deleting the test."""
    assert plateau_tol(curves["sce"]) is None, (
        "SCE settled — if its binning changed, re-record this")
    for n in DETECTORS:
        if n != "sce":
            assert plateau_tol(curves[n]) is not None, (
                f"{n} is now tolerance-dependent too; that is a finding")


def test_only_the_tolerance_dependent_detector_reorders(curves):
    """How low-stakes the choice is — stated more precisely than I first had it.

    ⚠ **A correction.** An earlier reading of `docs/learned/tolerance_sweep.json`
    said the ranking is *unchanged* from 0.4 s to 2.0 s, and the caption of
    `docs/learned/two_decisions.png` says so. That is true of that archived
    sweep and **not** true here at the shipped operating points: `sce` and
    `sync` swap at the bottom between 0.4 s and 0.5 s.

    The robust claim, true in both runs, is better than the one it replaces:
    **the top of the table never moves, and every reordering involves the one
    detector whose score depends on the tolerance.** Which is the argument for
    reporting a curve rather than against it — the instability is located in
    exactly the place the curve exists to expose."""
    def order(t):
        return [n for n in sorted(DETECTORS, key=lambda k: -curves[k][t].f1)]

    mid = [t for t in TOLERANCE_GRID if 0.4 <= t <= 2.0]
    first = order(mid[0])
    for t in mid[1:]:
        now = order(t)
        assert now[:4] == first[:4], (
            f"the top of the ranking moved at {t}s: {now} vs {first}")
        moved = {a for a, b in zip(now, first) if a != b}
        assert not moved or "sce" in moved, (
            f"a reordering at {t}s that does not involve SCE: {moved}")


def test_a_climbing_detector_is_not_reported_as_a_bare_number(curves):
    """describe_curve is what anything human-facing should print. For a detector
    still climbing it must say so rather than hand over a number that reads like
    an accuracy."""
    said = describe_curve(curves["sce"])
    assert "STILL CLIMBING" in said, said
    assert "depends on the matching tolerance" in said, said

    settled = describe_curve(curves["coact"])
    assert "flat from" in settled, settled


def test_plateau_is_none_when_the_curve_is_still_rising_at_the_end():
    """The helper's own rule, on a curve built by hand so the detectors cannot
    quietly change what is being tested."""
    class R:
        def __init__(self, f1):
            self.f1 = f1

    assert plateau_tol({0.5: R(0.4), 1.0: R(0.6), 1.5: R(0.9)}) is None
    assert plateau_tol({0.5: R(0.4), 1.0: R(0.9), 1.5: R(0.9)}) == 1.0
    assert plateau_tol({0.5: R(0.9), 1.0: R(0.9), 1.5: R(0.9)}) == 0.5
