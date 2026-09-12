"""Hand-derived vectors for the operational-time dither.

Written from Louis, Gerstein, Grün & Diesmann 2010 (*Frontiers in Computational
Neuroscience* 4:127) and the overnight plan
(``docs/proposals/2026-09-10-surrogate-evaluation-overnight.md``, the candidates
table) **only** — ``src/bugarach/operational_time.py`` was not read. Each case below
has an answer derived on paper from the paper's equations, not from running any
implementation.

What the plan specifies:

- ``operational_time_dither(train, window, J, bandwidth, rng)`` returns an int64
  array of frame indices.
- It dithers in time warped by a **leave-one-out** Gaussian kernel estimate of the
  ROI's own rate, of width ``bandwidth`` (the kernel's σ).
- The dither is uniform in operational time with half-width ``J·N/T`` in
  expected-count units, ``N`` being the onsets inside the window and ``T`` its length.
- Every generator works on frame indices; a frame index is the nearest whole number.

**Units assumed here: ``J`` and ``bandwidth`` are both in frames**, because the
plan says every generator works on frame indices and ``pattern_jitter`` takes its
``L`` and ``R`` in frames. If the implementation takes seconds, every call below
goes through ``_dither`` and only that helper changes.

The derivation the constant- and two-rate cases rest on (the paper's Eq. 6 and 8):
operational time is τ(t) = ∫ λ(u) du, the expected count up to t. A uniform dither
of half-width w' in τ maps back to real time with density λ(t)/(2w') on
[τ⁻¹(τ(tᵢ) − w'), τ⁻¹(τ(tᵢ) + w')]. Where λ is locally constant at λ₀ that
interval is tᵢ ± w'/λ₀ and the density is flat — a real-time uniform dither of
half-width w'/λ₀. With w' = J·N/T:

- **constant rate** λ₀ = N/T ⇒ half-width exactly J, at any rate;
- **two rates**, λ₁ on the first half and λ₂ on the second ⇒ N/T = (λ₁ + λ₂)/2 and
  half-width J·(λ₁ + λ₂)/(2λ_k) in half k — so the half-widths stand in the ratio
  λ₁/λ₂, the inverse of the rates.

A regular train with spacing d under a Gaussian kernel with σ ≫ d estimates a rate
flat at 1/d (the comb's ripple is of order exp(−2π²σ²/d²)). Leaving onset i out
removes its own kernel, whose height at its centre is K(0) = 1/(σ√(2π)) and which is
flat to (J/σ)² over the dither, so the local rate onset i is warped by is
1/d − 1/(σ√(2π)). The expected half-widths below carry that correction; it is 1–3%.

Edges: the plan leaves the edge behaviour to the build ("recorded in the build"),
so every quantitative check uses only onsets at least four kernel widths from any
window edge or rate change, and pairs each surrogate onset with its source by
nearest neighbour — valid because every half-width here is under half the spacing.
"""

from __future__ import annotations

import math

import numpy as np
import pytest
from scipy.special import ndtr

from bugarach.operational_time import operational_time_dither

SQRT_2PI = math.sqrt(2.0 * math.pi)


def _dither(train, window, J, bandwidth, seed):
    out = operational_time_dither(np.asarray(train, dtype=np.int64), tuple(window),
                                  J, bandwidth, np.random.RandomState(seed))
    return np.asarray(out)


def _comb(start, stop, spacing, phase=0):
    return np.arange(start + phase, stop, spacing, dtype=np.int64)


def _displacements(src, out, keep):
    """Displacement of every kept source onset, pairing each output with its nearest source.

    Asserts that each kept source onset has exactly one surrogate onset — the interior
    count is conserved — so a displacement cannot be silently invented or lost.
    """
    src = np.asarray(src, dtype=np.int64)
    out = np.asarray(out, dtype=np.int64)
    idx = np.searchsorted(src, out)
    left = np.clip(idx - 1, 0, src.size - 1)
    right = np.clip(idx, 0, src.size - 1)
    nearest = np.where(np.abs(out - src[left]) <= np.abs(out - src[right]), left, right)
    kept = keep[nearest]
    got = nearest[kept]
    want = np.flatnonzero(keep)
    assert np.array_equal(np.sort(got), want), (
        "interior onsets were lost, duplicated or moved past a neighbour: "
        f"{want.size} interior sources, {got.size} surrogate onsets matched to them, "
        f"{np.setdiff1d(want, got).size} unmatched")
    return (out - src[nearest])[kept]


def _uniform_rms(half_width):
    """RMS of a continuous uniform ±W displacement rounded to the nearest frame."""
    return math.sqrt(half_width ** 2 / 3.0 + 1.0 / 12.0)


def _pooled(train, window, J, bandwidth, keep, seeds):
    return np.concatenate([_displacements(train, _dither(train, window, J, bandwidth, s),
                                          keep) for s in seeds])


def _check_uniform(disp, half_width, *, label):
    """A rounded uniform dither of half-width W: bounded, centred, filled and flat."""
    W = half_width
    mx = int(np.abs(disp).max())
    assert mx <= math.floor(W + 0.5) + 1, f"{label}: moved {mx} frames, half-width {W:.2f}"
    assert mx >= W - 1.5, f"{label}: never reached the edge, max {mx} of half-width {W:.2f}"
    assert abs(disp.mean()) < 0.25, (
        f"{label}: mean displacement {disp.mean():.3f} frames — rounding is not to "
        "the nearest frame, or the dither is not centred")
    rms = float(np.sqrt(np.mean(disp.astype(float) ** 2)))
    want = _uniform_rms(W)
    assert abs(rms / want - 1) < 0.06, f"{label}: RMS {rms:.3f}, uniform ±{W:.2f} gives {want:.3f}"
    # Flat: the inner half of the support holds half the mass (rounding moves it ≤ 5%).
    inner = float(np.mean(np.abs(disp) <= W / 2))
    assert 0.44 < inner < 0.61, f"{label}: {inner:.3f} of mass in the inner half, uniform gives 0.5"


# -- contract ------------------------------------------------------------------------------

def test_output_is_sorted_int64_frames_inside_the_window():
    rs = np.random.RandomState(3)
    train = np.sort(rs.choice(np.arange(100, 5100), 120, replace=False)).astype(np.int64)
    out = _dither(train, (100, 5100), 12, 300, seed=1)
    assert out.dtype == np.int64
    assert np.all(np.diff(out) >= 0)
    assert out.size <= train.size
    assert np.all((out >= 100) & (out < 5100))


def test_same_seed_gives_the_same_surrogate_and_another_seed_does_not():
    rs = np.random.RandomState(4)
    train = np.sort(rs.choice(np.arange(0, 6000), 150, replace=False)).astype(np.int64)
    a = _dither(train, (0, 6000), 10, 400, seed=11)
    b = _dither(train, (0, 6000), 10, 400, seed=11)
    c = _dither(train, (0, 6000), 10, 400, seed=12)
    assert np.array_equal(a, b)
    assert not np.array_equal(a, c)


def test_an_empty_train_comes_back_empty():
    out = _dither(np.array([], dtype=np.int64), (0, 1000), 5, 200, seed=0)
    assert out.dtype == np.int64 and out.size == 0


def test_zero_width_moves_nothing():
    """w' = J·N/T = 0, so every onset maps to itself and back."""
    rs = np.random.RandomState(5)
    train = np.sort(rs.choice(np.arange(0, 4000), 90, replace=False)).astype(np.int64)
    assert np.array_equal(_dither(train, (0, 4000), 0, 300, seed=2), train)


def test_a_single_onset_does_not_crash():
    """Leaving the only onset out leaves no rate to warp by. The plan expects degeneracy
    on data this sparse and leaves its handling to the build; the call must still return
    at most that onset, inside the window, and half the real ROIs look like this."""
    out = _dither(np.array([2500], dtype=np.int64), (0, 5000), 20, 600, seed=0)
    assert out.dtype == np.int64 and out.size <= 1
    assert np.all((out >= 0) & (out < 5000))


def test_moving_train_and_window_together_moves_the_surrogate_with_them():
    """τ depends on positions relative to each other and to the window, never on the
    window's absolute start — the failure Elephant's ``jitter_spikes`` has at non-zero
    starts. Same seed, same train shifted by S: the surrogate shifts by exactly S."""
    rs = np.random.RandomState(6)
    train = np.sort(rs.choice(np.arange(0, 6000), 140, replace=False)).astype(np.int64)
    S = 100_000
    base = _dither(train, (0, 6000), 15, 500, seed=9)
    moved = _dither(train + S, (S, 6000 + S), 15, 500, seed=9)
    assert np.array_equal(moved, base + S)


# -- constant rate: operational time is linear ---------------------------------------------

def test_constant_rate_reduces_to_a_uniform_dither_of_half_width_J():
    """Spacing d = 40, σ = 800 ≫ d: rate 1/d everywhere, N/T = 1/d, so w' = J/d counts
    maps back to ±J·(1/d)/(1/d − K(0)) = ±J·1.020 frames, uniform."""
    d, sigma, J, T = 40, 800, 10, 20_000
    train = _comb(0, T, d, phase=20)
    keep = (train >= 4 * sigma) & (train < T - 4 * sigma)
    disp = _pooled(train, (0, T), J, sigma, keep, seeds=range(10))
    W = J * (1 / d) / (1 / d - 1 / (sigma * SQRT_2PI))
    _check_uniform(disp, W, label="constant rate")
    # And each interior displacement value is about equally likely.
    counts = np.array([np.sum(disp == k) for k in range(-(J - 1), J)])
    assert counts.min() > 0.75 * counts.mean() and counts.max() < 1.25 * counts.mean(), counts


@pytest.mark.parametrize("d", [24, 96])
def test_the_real_half_width_is_J_at_any_constant_rate(d):
    """The width is set in expected counts, J·N/T, so the rate cancels: a train four
    times denser gets the same real-time dither, not one four times narrower."""
    sigma, J = 1200, 8
    T = 48 * sigma
    train = _comb(0, T, d, phase=d // 2)
    keep = (train >= 4 * sigma) & (train < T - 4 * sigma)
    disp = _pooled(train, (0, T), J, sigma, keep, seeds=range(6))
    W = J * (1 / d) / (1 / d - 1 / (sigma * SQRT_2PI))
    _check_uniform(disp, W, label=f"spacing {d}")


# -- two rates: a warping derived by hand ---------------------------------------------------

D1, D2, SIGMA2, J2, HALF = 20, 60, 800, 9, 24_000


def _two_rate():
    """Spacing 20 on [0, 24000), spacing 60 on [24000, 48000).

    N = 1200 + 400 = 1600 in T = 48000, so N/T = 1/30 and w' = 9/30 = 0.3 counts.
    Half-widths: 0.3·20 = 6 frames in the dense half, 0.3·60 = 18 in the sparse one
    (times the leave-one-out factor 1/(1 − d·K(0)), 1.010 and 1.030).
    """
    first = _comb(0, HALF, D1, phase=10)
    second = _comb(HALF, 2 * HALF, D2, phase=30)
    train = np.concatenate([first, second])
    margin = 4 * SIGMA2
    dense = (train >= margin) & (train < HALF - margin)
    sparse = (train >= HALF + margin) & (train < 2 * HALF - margin)
    return train, dense, sparse


def _two_rate_displacements():
    train, dense, sparse = _two_rate()
    seeds = range(8)
    return (_pooled(train, (0, 2 * HALF), J2, SIGMA2, dense, seeds),
            _pooled(train, (0, 2 * HALF), J2, SIGMA2, sparse, seeds))


def test_two_rate_train_dithers_each_half_uniformly_at_its_derived_half_width():
    n_over_t = (HALF / D1 + HALF / D2) / (2 * HALF)
    assert n_over_t == pytest.approx(1 / 30)
    w = J2 * n_over_t
    k0 = 1 / (SIGMA2 * SQRT_2PI)
    dense_w = w / (1 / D1 - k0)
    sparse_w = w / (1 / D2 - k0)
    assert dense_w == pytest.approx(6.06, abs=0.01)
    assert sparse_w == pytest.approx(18.55, abs=0.01)
    dense, sparse = _two_rate_displacements()
    _check_uniform(dense, dense_w, label="dense half")
    _check_uniform(sparse, sparse_w, label="sparse half")


def test_two_rate_half_widths_stand_in_the_inverse_ratio_of_the_rates():
    """Whatever the normalisation, the warping alone fixes the ratio: λ₁/λ₂ = 3,
    so the sparse half's dither is three times the dense half's (2.94 after the
    leave-one-out correction). A real-time dither would give 1."""
    dense, sparse = _two_rate_displacements()
    ratio = np.sqrt(np.mean(sparse.astype(float) ** 2)) / np.sqrt(np.mean(dense.astype(float) ** 2))
    k0 = 1 / (SIGMA2 * SQRT_2PI)
    want = _uniform_rms(J2 / 30 / (1 / D2 - k0)) / _uniform_rms(J2 / 30 / (1 / D1 - k0))
    assert ratio == pytest.approx(want, rel=0.06)


# -- leave-one-out: the onset's own kernel is not in its warp --------------------------------

def _loo_warp(x, spacing, sigma, reach=6):
    """τ₋ᵢ(x) for onset i at 0 in a comb of the given spacing, up to a constant:
    the sum of Φ((x − t_j)/σ) over the neighbours j ≠ i."""
    nb = np.array([k * spacing for k in range(-reach, reach + 1) if k != 0], dtype=float)
    return float(ndtr((x - nb) / sigma).sum())


def _solve(f, target, lo, hi):
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if f(mid) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def test_leave_one_out_warp_gives_the_hand_derived_support_and_shape():
    """Spacing d = 40 with σ = 20 = d/2. With its own kernel the rate at an onset is
    ≈1/d and the support would be ±3.9 frames; left out, the rate there comes from the
    neighbours alone — about a fifth as high and rising towards them — so the same
    w' = J/d = 0.1 counts spans ±14.7 frames, and the density ∝ λ₋ᵢ piles towards the
    edges of that support instead of sitting flat.
    """
    d, sigma, J, T = 40, 20, 4, 8_000
    train = _comb(0, T, d, phase=20)
    keep = (train >= 400) & (train < T - 400)
    w = J * train.size / T
    assert w == pytest.approx(J / d)

    u0 = _loo_warp(0.0, d, sigma)
    s = _solve(lambda x: _loo_warp(x, d, sigma) - u0, w, 0.0, d / 2)
    assert s == pytest.approx(14.66, abs=0.02)
    # the shape: P(|x| ≥ 7.5) before rounding, i.e. |displacement| ≥ 8 frames after
    outer = 1 - (_loo_warp(7.5, d, sigma) - _loo_warp(-7.5, d, sigma)) / (2 * w)

    disp = _pooled(train, (0, T), J, sigma, keep, seeds=range(20))
    mx = int(np.abs(disp).max())
    assert round(s) - 1 <= mx <= round(s) + 1, (
        f"support ±{mx} frames; leave-one-out gives ±{s:.1f}, keeping the onset's own "
        "kernel gives ±3.9")
    got = float(np.mean(np.abs(disp) >= 8))
    assert got == pytest.approx(outer, abs=0.05), (
        f"{got:.3f} of onsets moved 8+ frames; the leave-one-out density gives {outer:.3f}")
    assert abs(disp.mean()) < 0.3
