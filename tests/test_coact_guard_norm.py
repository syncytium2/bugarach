"""What the guard removes: the excised events, or the excised span as well.

`docs/reviews/guard_prior_art_2026-08-26.md` shows that CoactDetect's bar is a
DENSITY — the chance a shifted event lands in one bin width scales as (events
retained) / (line length) — so compacting the retained reference onto a shorter
line multiplies the bar by ``C / (C - guard)`` at every bin, including the ones
where the guard excised nothing at all.

These tests pin the two branches apart at the size the closed form predicts. They
are deliberately loose: the exact ratio depends on the surrogate draw, and a test
that flakes gets deleted rather than fixed. What they will catch is either branch
quietly becoming the other one.
"""

import numpy as np
import pytest

from bugarach.detectors.coact import coact_detect

CTX = 60.0
BW = 2.0
GUARD = 5.0
T_END = 600.0


def _sparse_trains(seed=11, n_roi=5, per_roi=7):
    """Widely spaced events, so most guard bands are empty and the empty
    stratum — the whole point — is large enough to average over."""
    rng = np.random.RandomState(seed)
    return [np.sort(rng.uniform(20.0, T_END - 20.0, per_roi)) for _ in range(n_roi)]


def _nullmean(trains, guard, norm, n_sur=1500):
    d = coact_detect(trains, (0.0, T_END), rng_seed=3, int_win_sec=BW,
                     context_win_sec=CTX, alpha=1e-4, n_surrogates=n_sur,
                     min_rois=0, guard_sec=guard, guard_norm=norm)
    return np.asarray(d.ctr, float), np.asarray(d.nullmean_prof, float)


def _empty_stratum_ratio(norm):
    """Mean bar(guard)/bar(0) over bins whose excised band held no event and whose
    context window is not clipped by the ends of the recording."""
    trains = _sparse_trains()
    pooled = np.sort(np.concatenate(trains))
    t, b0 = _nullmean(trains, 0.0, norm)
    _, b1 = _nullmean(trains, GUARD, norm)
    lo = np.searchsorted(pooled, t - GUARD / 2, "left")
    hi = np.searchsorted(pooled, t + GUARD / 2, "right")
    interior = (t > CTX / 2) & (t < T_END - CTX / 2)   # keep C exactly CTX
    keep = interior & ((hi - lo) == 0) & np.isfinite(b0) & np.isfinite(b1) & (b0 > 0)
    assert keep.sum() > 100, "the empty stratum is too small to average over"
    return float(np.mean(b1[keep] / b0[keep]))


def test_guard_norm_rejects_unknown_value():
    with pytest.raises(ValueError):
        coact_detect([np.array([1.0])], (0.0, 10.0), guard_norm="bogus")


def test_guard_zero_is_identical_under_both_normalizations():
    """No guard, no guarded branch — the two must not differ by one bit."""
    trains = _sparse_trains()
    _, a = _nullmean(trains, 0.0, "compact", n_sur=200)
    _, b = _nullmean(trains, 0.0, "exposure", n_sur=200)
    np.testing.assert_array_equal(np.nan_to_num(a, nan=-1.0),
                                  np.nan_to_num(b, nan=-1.0))


def test_compact_raises_the_bar_where_it_excised_nothing():
    """The shipped branch multiplies the bar by C / (C - guard) at empty bins."""
    predicted = CTX / (CTX - GUARD)          # 1.0909 at C = 60 s, guard = 5 s
    got = _empty_stratum_ratio("compact")
    assert got == pytest.approx(predicted, rel=0.05), (
        f"empty-stratum ratio {got:.4f} is not the exposure factor {predicted:.4f}")


def test_exposure_leaves_the_bar_alone_where_it_excised_nothing():
    """Removing counts and not exposure: an empty band changes nothing."""
    got = _empty_stratum_ratio("exposure")
    assert got == pytest.approx(1.0, abs=0.03), (
        f"empty-stratum ratio {got:.4f} should be 1 when no events were removed")
