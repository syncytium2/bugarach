"""Plant nothing, and see what the assessor says is there.

``docs/RESET.md`` §7 puts this first in the order of work, ahead of the
background axis and ahead of the fresh assessment the K decision waits on, and
§1 gives the reason:

    The obvious validation test is circular and must not be written as written.
    Asking the assessor to recover planted events is the convention agreeing
    with itself, because the simulation is parameterised from the assessor.
    What survives is the **null**: plant nothing, and the excess must read zero.
    A rate-matched null that leaks is a defect in the arithmetic whatever
    convention sits on top, and every generator spec derived afterwards
    inherits it.

**It leaks.** On independent Poisson ROIs — no coordination anywhere, every
train drawn on its own — the coactivity excess is strictly positive everywhere
the assessor reports anything at all. At the busy end of this project's own
difficulty axis (``bench.REGIMES`` busy, 19.0 mHz/ROI) it reports about **6.2
excess co-active ROI·events per minute at K=3**, reproducibly across seeds, on
data with nothing in it.

Where it comes from, read off ``assess.py`` rather than inferred
--------------------------------------------------------------
::

    bk = np.flatnonzero(obs >= K)      # bins chosen BY THE OBSERVED counts
    obs_mass  = obs[bk].sum()  / win_min
    null_mass = null_mean[bk].sum() / win_min
    coact_excess = obs_mass - null_mass

The bins are selected where the **observed** count reaches K, and then the
observed is compared against the null's **mean** in those same bins. Selecting
on the observed value guarantees the observed is high there; the null mean is
the ensemble average and is not. The difference is positive by construction
whenever any bin reaches K, with or without coordination. It is the winner's
curse, not a measurement.

:func:`test_a_draw_from_the_null_reads_almost_the_same_excess` is the decisive
one: it hands the estimator a circular shift of the same trains — by
construction a draw *from* the null the estimator is comparing against — and
that reads **96%** of what the real observation reads. Whatever the excess is
measuring, it is nearly all selection rule.

What this file does NOT do
--------------------------
**It does not touch the arithmetic.** ``assess_coactivity`` is held to 1e-9
against ``measure_coordination_timescale.m`` and parity is the product
(FOUNDATIONS §2), so the same bias is in the MATLAB and correcting it here would
break the one property the port exists to have. Whether to fork it is Tony's
call and belongs in ``docs/forks.md`` — see
``docs/todo/2026-08-24-the-null-leaks-and-the-excess-is-mostly-selection.md``.

So the tests below **pin the leak rather than forbid it**, which is what makes
this a measurement somebody can act on instead of a red suite nobody can land
past. The property that *should* hold is written down too, as a strict xfail:
the day the arithmetic is fixed, that test starts passing and the strictness
turns it into a failure that says so. Nobody has to remember to come back.
"""

from __future__ import annotations

import numpy as np
import pytest

from bugarach.assess import _coact_count, assess_coactivity
from bugarach.store import Region, Slice, Stream

#: 30 minutes — comfortably over the 900 s region floor `assess_coactivity`
#: refuses under, so the refusal path is not what is being measured.
DUR = 1800.0
N_ROI = 40
BIN = 1.0
WIN_MIN = DUR / 60.0

#: The two endpoints of this project's own difficulty axis (`bench.REGIMES`,
#: corrected 2026-08-20), plus one busier still. Quoted here rather than
#: imported: the axis moves, and a null test that moved with it would stop
#: comparing against the same thing.
QUIET_HZ = 0.0052
BUSY_HZ = 0.0190
CROWDED_HZ = 0.05


def independent_slice(rate_hz: float, seed: int, *, n_roi: int = N_ROI,
                      dur: float = DUR) -> Slice:
    """A recording with **nothing planted in it**.

    Every ROI's train is drawn on its own from a homogeneous Poisson process.
    There is no shared process, no common drive, no injected event — so every
    co-active moment in it is a coincidence, and the rate-matched null is
    exactly the right model of what produced it.
    """
    rng = np.random.default_rng(seed)
    trains = [np.sort(rng.uniform(0.0, dur, size=rng.poisson(rate_hz * dur)))
              for _ in range(n_roi)]
    st = Stream(locs=trains,
                amp=[np.ones(t.size) for t in trains],
                width=[np.full(t.size, 0.5) for t in trains],
                t50rise=trains,
                width_def="synthetic, half-second, unused by the excess")
    return Slice(slice_id=f"null_{seed}", streams={"fast": st}, dt=0.1,
                 regions=[Region(name="baseline", slot=None,
                                 start_sec=0.0, end_sec=dur)])


def assess(rate_hz: float, seed: int, ks=(3, 4, 6, 8), n_surrogates: int = 200):
    """The assessor on nothing-planted data.

    200 surrogates rather than the MATLAB default 1000: this file measures a
    bias, and the bias does not depend on how finely the null mean is estimated
    — `test_the_leak_does_not_shrink_with_more_surrogates` is what says so.
    """
    s = independent_slice(rate_hz, seed)
    return {a.min_rois: a for a in assess_coactivity(
        s, window=(0.0, DUR), min_rois=list(ks), n_surrogates=n_surrogates)}


# --------------------------------------------------------------- the leak

@pytest.mark.parametrize("seed", (1, 2, 3))
def test_the_excess_is_positive_on_data_with_nothing_planted(seed):
    """The headline statistic, on a recording that contains no coordination.

    Pinned as a POSITIVE number rather than asserted to be zero, because zero is
    what it should read and is not what it reads. See this module's docstring
    for why that is recorded rather than fixed here.
    """
    got = assess(BUSY_HZ, seed)
    a = got[3]
    assert a.n_coact_bins > 0, (
        "no bin reached K=3, so this seed exercises nothing — the leak only "
        "shows where the statistic is defined")
    assert a.coact_excess > 1.0, (
        f"K=3, {BUSY_HZ*1000:.1f} mHz/ROI, nothing planted, excess "
        f"{a.coact_excess:.3f} — this test pins a KNOWN leak, and an excess "
        "near zero here means somebody fixed the arithmetic. That is good "
        "news: read the module docstring and retire this test.")


def test_the_leak_is_reproducible_rather_than_noise():
    """Three independent draws, three similar numbers. A leak that varied wildly
    across seeds would be sampling noise and would not be worth a campaign."""
    got = [assess(BUSY_HZ, seed)[3].coact_excess for seed in (1, 2, 3)]
    assert all(g > 1.0 for g in got), got
    spread = (max(got) - min(got)) / np.mean(got)
    assert spread < 0.35, (
        f"excesses {got} differ by {spread:.0%} of their mean — too variable to "
        "call a bias; this test was written when they agreed to within 12%")


def test_the_leak_grows_with_the_background_rate():
    """Which is the property that makes it dangerous rather than merely wrong.

    The excess is quoted as an absolute per-minute magnitude, and a treatment
    window sits at a different background rate than the baseline the generator
    was parameterised from (`RESET` §6). A bias that tracks the rate is a bias
    that manufactures a treatment effect.
    """
    quiet = assess(QUIET_HZ, 1)[3].coact_excess
    busy = assess(BUSY_HZ, 1)[3].coact_excess
    crowded = assess(CROWDED_HZ, 1)[3].coact_excess
    assert quiet < busy < crowded, (quiet, busy, crowded)
    assert crowded > 5 * busy or crowded - busy > 10.0, (
        f"quiet {quiet:.3f} busy {busy:.3f} crowded {crowded:.3f} — the leak "
        "was measured growing steeply with rate; it has stopped")


def test_the_leak_does_not_shrink_with_more_surrogates():
    """It is a bias, not an estimation error.

    More surrogates estimate the null MEAN more precisely. They do not touch
    the fact that the bins were chosen by the observed counts, so the excess
    does not converge toward zero — which is what separates this from something
    a bigger ensemble would fix.
    """
    small = assess(BUSY_HZ, 1, n_surrogates=50)[3].coact_excess
    large = assess(BUSY_HZ, 1, n_surrogates=800)[3].coact_excess
    assert large > 1.0, large
    assert abs(large - small) / max(small, 1e-9) < 0.2, (
        f"{small:.3f} at 50 surrogates, {large:.3f} at 800 — a leak that moved "
        "this much with the ensemble size would be estimation error, and the "
        "remedy would be more surrogates rather than different arithmetic")


# ------------------------------------------------------- what it actually is

def test_a_draw_from_the_null_reads_almost_the_same_excess():
    """**The decisive one.**

    Take the same trains and circularly shift them once. That draw is, by
    construction, exactly what the null models — it is a sample FROM the null
    distribution the estimator compares against. Run the estimator's own
    arithmetic on it and it reads nearly the same excess as the real recording.

    So the excess is not mostly measuring coordination in the data. It is mostly
    measuring the rule that picked the bins.
    """
    s = independent_slice(BUSY_HZ, seed=1)
    trains = [np.asarray(t, dtype=float) for t in s.streams["fast"].t50rise]
    n_bins = int(np.ceil(DUR / BIN))

    obs = _coact_count(trains, DUR, BIN, n_bins)

    # the null ensemble, built the way `assess_coactivity` builds it
    rng = np.random.RandomState(20260722)
    null_sum = np.zeros(n_bins)
    for _ in range(200):
        off = rng.random_sample(len(trains)) * DUR
        null_sum += _coact_count(
            [np.mod(v + off[r], DUR) if v.size else v
             for r, v in enumerate(trains)], DUR, BIN, n_bins)
    null_mean = null_sum / 200.0

    # one more shift, handed to the estimator as if it were the recording
    off = np.random.RandomState(999).random_sample(len(trains)) * DUR
    as_obs = _coact_count(
        [np.mod(v + off[r], DUR) if v.size else v
         for r, v in enumerate(trains)], DUR, BIN, n_bins)

    def excess(counts, K):
        bk = np.flatnonzero(counts >= K)
        return (counts[bk].sum() - null_mean[bk].sum()) / WIN_MIN

    real, from_null = excess(obs, 3), excess(as_obs, 3)
    assert from_null > 1.0, from_null
    ratio = from_null / real
    assert ratio > 0.75, (
        f"a draw from the null reads {from_null:.3f} against the recording's "
        f"{real:.3f} — {ratio:.0%}. This test was written when it read 96%, "
        "and the whole finding is that the two are close: if they have come "
        "apart, the estimator has started measuring the data instead of the "
        "selection rule, and that is worth knowing about.")


# --------------------------------------------------- the property that should hold

@pytest.mark.xfail(strict=True, reason=(
    "RESET §7 item 1: plant nothing, expect zero. It reads ~6.2 at K=3 on the "
    "busy background instead. Left as a strict xfail rather than deleted so "
    "that fixing the arithmetic turns this into a passing test and the "
    "strictness turns THAT into a failure nobody can miss — which is the point "
    "at which the leak-pinning tests above should be retired together with it."))
def test_plant_nothing_expect_zero():
    """What the reset asks for, stated as it asks for it.

    The tolerance is deliberately generous: a tenth of an excess co-active
    ROI·event per minute on a 30-minute window is far looser than any use this
    number is put to, so passing it would be a real result rather than a
    threshold chosen to be passable.
    """
    for seed in (1, 2, 3):
        got = assess(BUSY_HZ, seed)[3]
        assert abs(got.coact_excess) < 0.1, (
            f"seed {seed}: nothing was planted and the assessor reports "
            f"{got.coact_excess:.3f} excess co-active ROI·events/min")
