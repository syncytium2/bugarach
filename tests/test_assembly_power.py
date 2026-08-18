"""The power analysis behind the assembly question, wired into the normal suite.

Two of these lock a *finding*, not just an implementation. The double-margin null
losing all power at full assembly strength is the reason
`docs/todo/2026-08-18-do-real-slices-have-recurring-assemblies.md` runs two nulls
instead of the one its first correction argued for; if a future change makes that
null see a saturated assembly, the todo's method is wrong and this test should
fail loudly rather than the finding quietly becoming stale.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).parent.parent
sys.path.insert(0, str(REPO / "tools"))

import assembly_power as ap  # noqa: E402

GEO = dict(n_roi=24, n_events=18, part=4.5)


def _slice(rng, A, strength):
    return ap.simulate_slice(rng, GEO["n_roi"], GEO["n_events"], GEO["part"],
                             A, strength)


def test_geometry_comes_from_the_derived_spec():
    """The numbers are read, never transcribed — the hazard in
    `docs/todo/2026-08-14-generator-doc-numbers-are-transcribed.md`."""
    g = ap.geometry()
    assert g["n_roi"] > 0 and g["n_events"] > 0 and g["part"] > 0
    assert g["win_sec"] > 0


def test_trade_conserves_both_margins():
    """A curveball trade may move membership but may not change any row or column
    sum — which is the whole reason the null can be read as 'beyond rate'."""
    rng = np.random.RandomState(0)
    M = _slice(rng, 6, 0.5)
    masks = ap._to_masks(M)
    for _ in range(400):
        i, j = rng.randint(0, GEO["n_events"], 2)
        if i != j:
            ap._trade(rng, masks, int(i), int(j))
    S = ap._from_masks(masks, GEO["n_roi"])
    assert np.array_equal(M.sum(axis=1), S.sum(axis=1))
    assert np.array_equal(M.sum(axis=0), S.sum(axis=0))
    assert not np.array_equal(M, S), "the chain never moved"


@pytest.mark.parametrize("which", ["margin", "uniform"])
def test_size_is_nominal_with_nothing_planted(which):
    """Uniform participation is the null hypothesis, so both tests must reject it
    at about alpha and not more."""
    rng = np.random.RandomState(11)
    fn = ap.pvalues if which == "margin" else ap.pvalues_uniform
    ps = np.array([fn(rng, _slice(rng, 6, 0.0), 100)[0] for _ in range(60)])
    assert np.mean(ps < 0.05) < 0.20, f"size {np.mean(ps < 0.05):.2f} at alpha .05"


def test_uniform_null_passes_the_full_strength_control():
    """A test that cannot fire on a saturated assembly is not measuring anything."""
    rng = np.random.RandomState(5)
    ps = np.array([ap.pvalues_uniform(rng, _slice(rng, 6, 1.0), 100)[0]
                   for _ in range(20)])
    assert np.mean(ps < 0.05) > 0.8


def test_double_margin_null_is_blind_to_a_saturated_assembly():
    """The finding that makes one null insufficient.

    At full strength the non-members never participate, so the assembly is
    entirely encoded in the column sums this null holds fixed and there is nothing
    left for a margin-preserving shuffle to destroy. Power falls back to chance —
    not monotonic in the quantity being measured.
    """
    rng = np.random.RandomState(5)
    ps = np.array([ap.pvalues(rng, _slice(rng, 6, 1.0), 100)[0]
                   for _ in range(20)])
    assert np.mean(ps < 0.05) < 0.3, (
        "the double-margin null now sees a saturated assembly — if this is real, "
        "the two-null method in the assembly todo needs revisiting")


def test_both_nulls_find_a_mid_strength_assembly():
    """Between the two failure modes, both nulls work and agree."""
    rng = np.random.RandomState(9)
    a = np.array([ap.pvalues(rng, _slice(rng, 5, 0.5), 100)[0] for _ in range(20)])
    b = np.array([ap.pvalues_uniform(rng, _slice(rng, 5, 0.5), 100)[0]
                  for _ in range(20)])
    assert np.mean(a < 0.05) > 0.6
    assert np.mean(b < 0.05) > 0.6


def test_fisher_combination_is_defined_at_the_extremes():
    assert ap.fisher(np.ones(5)) == pytest.approx(1.0)
    assert ap.fisher(np.full(5, 1e-6)) < 1e-9
