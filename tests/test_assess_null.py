"""Plant nothing, and the assessor now says nothing is there.

`docs/RESET.md` §7 put this first in the order of work: *"plant nothing, and the
excess must read zero. A rate-matched null that leaks is a defect in the
arithmetic whatever convention sits on top, and every generator spec derived
afterwards inherits it."*

**On 2026-08-24 it leaked**, and this file pinned the leak rather than forbidding
it, because correcting the arithmetic would have broken parity with the MATLAB and
that was not a session's call. **On 2026-08-25 Tony took the correction**
(`docs/forks.md` §13; ADR-0003 for why parity stopped being the obstacle), so
these tests now check the thing they were written wanting.

What the correction is
----------------------
Every surrogate is scored exactly the way the observation is — the bins where
*that surrogate* reaches K, summed against the ensemble mean — and the median of
that is subtracted. A surrogate holds no coordination by construction, so whatever
it scores is the selection rule. No new sampling and no new parameter: it reuses
the ensemble already being computed.

What it fixes, measured here
----------------------------
Independent Poisson ROIs at three backgrounds, K=3, seed 1::

    background          raw    surrogate median    corrected
    quiet   5.2 mHz     0.28            0.27          0.01
    busy   19.0 mHz     6.14            5.75          0.39
    crowded  50 mHz    30.09           30.06          0.04

**The residual does not grow with the background**, which is how it is told from
the bias it replaced: the raw leak ran 0.28 → 6.14 → 30.09 across those three and
the corrected number does not follow. What is left is sampling noise around zero,
and it is **signed** — some seeds read slightly negative, which is what says it is
noise rather than a clamp.

`coact_excess_raw` still carries the uncorrected quantity and
`tests/test_assess.py` still holds it to the MATLAB fixtures at 1e-9. The
inheritance stayed verified rather than exempted, which is what ADR-0003 means by
the fixtures being a baseline rather than a gate.
"""

from __future__ import annotations

import numpy as np
import pytest

from bugarach.assess import _coact_count, assess_coactivity
from bugarach.store import Region, Slice, Stream

#: 30 minutes — over the 900 s floor `assess_coactivity` refuses under, so the
#: refusal path is not what is being measured.
DUR = 1800.0
N_ROI = 40
BIN = 1.0
WIN_MIN = DUR / 60.0

#: The endpoints of this project's difficulty axis (`bench.REGIMES`, corrected
#: 2026-08-20) plus one busier still. Quoted rather than imported: the axis moves,
#: and a null test that moved with it would stop comparing like with like.
QUIET_HZ = 0.0052
BUSY_HZ = 0.0190
CROWDED_HZ = 0.05

#: What "reads zero" means for a sampled statistic. The corrected value is one
#: draw measured against a median, so it fluctuates; the largest magnitude seen
#: across three backgrounds and three seeds was 1.16, at the busy endpoint. This
#: bounds the noise without pretending it is absent, and it is far below the 6.15
#: the raw statistic reported on the same data.
NULL_TOLERANCE = 2.0


def independent_slice(rate_hz: float, seed: int, *, n_roi: int = N_ROI,
                      dur: float = DUR) -> Slice:
    """A recording with **nothing planted in it**.

    Every ROI's train drawn on its own from a homogeneous Poisson process. No
    shared process, no common drive, no injected event — so every co-active
    moment is a coincidence and the rate-matched null is exactly the right model
    of what produced it.
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


def assess(rate_hz: float, seed: int, ks=(3, 4, 6, 8), n_surrogates: int = 200,
           **kw):
    s = independent_slice(rate_hz, seed)
    return {a.min_rois: a for a in assess_coactivity(
        s, window=(0.0, DUR), min_rois=list(ks),
        n_surrogates=n_surrogates, **kw)}


# ------------------------------------------------- plant nothing, expect zero

@pytest.mark.parametrize("rate,label", [(QUIET_HZ, "quiet"),
                                        (BUSY_HZ, "busy"),
                                        (CROWDED_HZ, "crowded")])
@pytest.mark.parametrize("seed", (1, 2, 3))
def test_plant_nothing_expect_zero(rate, label, seed):
    """What the reset asked for, at every background and every seed.

    **This was a strict xfail until 2026-08-25.** It passes now.
    """
    got = assess(rate, seed)[3]
    assert abs(got.coact_excess) < NULL_TOLERANCE, (
        f"{label}, seed {seed}: nothing was planted and the assessor reports "
        f"{got.coact_excess:.3f} excess co-active ROI·events/min "
        f"(raw {got.coact_excess_raw:.3f}, surrogate median "
        f"{got.sur_excess_med:.3f})")


def test_the_correction_removes_almost_all_of_it():
    """Not merely 'small' but small **relative to what it replaced**, which is
    the claim that matters where the raw number is 30."""
    for rate in (BUSY_HZ, CROWDED_HZ):
        a = assess(rate, 1)[3]
        assert a.coact_excess_raw > 5.0, a.coact_excess_raw
        left = abs(a.coact_excess) / a.coact_excess_raw
        assert left < 0.20, (
            f"{rate*1000:.1f} mHz: raw {a.coact_excess_raw:.3f} → corrected "
            f"{a.coact_excess:.3f}, still {left:.0%} of it")


def test_the_residual_does_not_grow_with_the_background():
    """**How the leftover is told apart from the bias it replaced.** The raw leak
    ran 0.28 → 6.14 → 30.09 across these three backgrounds. Sampling noise has no
    reason to, and does not."""
    raw = [assess(r, 1)[3].coact_excess_raw
           for r in (QUIET_HZ, BUSY_HZ, CROWDED_HZ)]
    cor = [abs(assess(r, 1)[3].coact_excess)
           for r in (QUIET_HZ, BUSY_HZ, CROWDED_HZ)]
    assert raw[0] < raw[1] < raw[2], raw
    assert raw[2] > 20 * raw[0], f"the raw leak stopped tracking the rate: {raw}"
    assert max(cor) < NULL_TOLERANCE, cor
    # the crowded end, where the raw leak is ~100x the quiet end's
    assert cor[2] < 1.0, f"the corrected value tracks the background too: {cor}"


def test_the_correction_is_signed_rather_than_a_floor():
    """A clamp at zero would also make the null 'read zero', and would be a lie —
    it would bias every real measurement upward. Some draws must read below."""
    vals = [assess(r, s)[3].coact_excess
            for r in (QUIET_HZ, BUSY_HZ, CROWDED_HZ) for s in (1, 2, 3)]
    assert min(vals) < 0.0, (
        f"no null draw read below zero across {len(vals)} of them — that is "
        f"what a clamp looks like: {[round(v, 3) for v in vals]}")


# ------------------------------------------------- what it is measuring

def test_the_raw_statistic_still_carries_the_old_number():
    """The baseline has to survive, or ADR-0003's *"the fixtures are the before
    in every claim of improvement"* is not true of this one."""
    a = assess(BUSY_HZ, 1)[3]
    assert a.coact_excess_raw > 5.0, a.coact_excess_raw
    assert a.sur_excess_med > 5.0, a.sur_excess_med
    assert a.coact_excess == pytest.approx(
        a.coact_excess_raw - a.sur_excess_med)


def test_raw_mode_returns_the_uncorrected_headline():
    """`excess_mode="raw"` is the mode `tests/test_assess.py` holds to the
    MATLAB, so it has to be the uncorrected quantity in the headline field."""
    a = assess(BUSY_HZ, 1, excess_mode="raw")[3]
    assert a.coact_excess == pytest.approx(a.coact_excess_raw)
    assert a.coact_excess > 5.0, a.coact_excess


def test_excess_mode_refuses_a_value_it_does_not_know():
    with pytest.raises(ValueError, match="excess_mode"):
        assess(BUSY_HZ, 1, excess_mode="whatever")


def test_a_draw_from_the_null_reads_almost_the_same_raw_excess():
    """**Why the correction has the shape it has**, and still true of the raw
    statistic: hand the uncorrected estimator a circular shift of the same trains
    — by construction a draw *from* the null it compares against — and it reads
    nearly what the recording reads. That quantity is what gets subtracted."""
    s = independent_slice(BUSY_HZ, seed=1)
    trains = [np.asarray(t, dtype=float) for t in s.streams["fast"].t50rise]
    n_bins = int(np.ceil(DUR / BIN))

    obs = _coact_count(trains, DUR, BIN, n_bins)
    rng = np.random.RandomState(20260722)
    null_sum = np.zeros(n_bins)
    for _ in range(200):
        off = rng.random_sample(len(trains)) * DUR
        null_sum += _coact_count(
            [np.mod(v + off[r], DUR) if v.size else v
             for r, v in enumerate(trains)], DUR, BIN, n_bins)
    null_mean = null_sum / 200.0

    off = np.random.RandomState(999).random_sample(len(trains)) * DUR
    as_obs = _coact_count(
        [np.mod(v + off[r], DUR) if v.size else v
         for r, v in enumerate(trains)], DUR, BIN, n_bins)

    def raw_excess(counts, K):
        bk = np.flatnonzero(counts >= K)
        return (counts[bk].sum() - null_mean[bk].sum()) / WIN_MIN

    real, from_null = raw_excess(obs, 3), raw_excess(as_obs, 3)
    assert from_null > 1.0, from_null
    assert from_null / real > 0.75, (
        f"a draw from the null reads {from_null:.3f} against the recording's "
        f"{real:.3f} — the uncorrected statistic is supposed to barely tell them "
        "apart, and removing that is what the correction is for")
