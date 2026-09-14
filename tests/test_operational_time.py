"""Operational-time dither (Louis, Gerstein, Grün & Diesmann 2010), on frames.

Synthetic trains only. Each test names the property it pins; the module
docstring of ``bugarach.operational_time`` states the decisions they check.
The hand-derived vectors, written independently from the paper and the plan,
are in ``tests/test_operational_time_vectors.py``.
"""

from __future__ import annotations

import numpy as np
import pytest

from bugarach import operational_time as ot
from bugarach.detectors.rate import event_rate, train_rate


def _poisson_train(rate_per_frame, T, seed, start=0):
    rs = np.random.RandomState(seed)
    n = rs.poisson(rate_per_frame * T)
    return np.sort(rs.randint(start, start + T, size=n)).astype(np.int64)


def _step_train(T, lo_rate, hi_rate, seed):
    """First half quiet, second half busy — Louis et al.'s single step."""
    rs = np.random.RandomState(seed)
    h = T // 2
    a = rs.randint(0, h, size=rs.poisson(lo_rate * h))
    b = rs.randint(h, T, size=rs.poisson(hi_rate * (T - h)))
    return np.sort(np.concatenate((a, b))).astype(np.int64)


@pytest.fixture(autouse=True)
def _fresh_cache():
    ot.clear_cache()
    yield
    ot.clear_cache()


# ---------------------------------------------------------------- the contract


@pytest.mark.parametrize("kernel,bw", [("gaussian", 300.0), ("gaussian", 20.0),
                                       ("box", 400.0)])
def test_output_is_sorted_int64_in_the_window_with_the_count_kept(kernel, bw):
    tr = _poisson_train(0.02, 3000, seed=3, start=500)
    for draw in range(20):
        y = ot.operational_time_dither(tr, (500, 3500), 40.0, bw,
                                       np.random.RandomState(draw), kernel=kernel)
        assert y.dtype == np.int64
        assert y.size == tr.size, "reflecting edges never drop an onset"
        assert np.all(np.diff(y) >= 0)
        assert y.min() >= 500 and y.max() < 3500


def test_zero_jitter_is_the_identity():
    tr = _poisson_train(0.03, 2000, seed=4)
    y = ot.operational_time_dither(tr, (0, 2000), 0.0, 200.0,
                                   np.random.RandomState(0))
    np.testing.assert_array_equal(y, tr)


def test_onsets_on_the_window_edges_survive():
    tr = np.array([0, 1, 5, 400, 798, 799], dtype=np.int64)
    for draw in range(50):
        y = ot.operational_time_dither(tr, (0, 800), 30.0, 150.0,
                                       np.random.RandomState(draw))
        assert y.size == tr.size and y.min() >= 0 and y.max() <= 799


def test_the_same_seed_gives_the_same_surrogate_and_another_does_not():
    tr = _poisson_train(0.02, 3000, seed=5)
    y1 = ot.operational_time_dither(tr, (0, 3000), 30.0, 300.0,
                                    np.random.RandomState(11))
    ot.clear_cache()  # a cold map must give the same answer as a cached one
    y2 = ot.operational_time_dither(tr, (0, 3000), 30.0, 300.0,
                                    np.random.RandomState(11))
    y3 = ot.operational_time_dither(tr, (0, 3000), 30.0, 300.0,
                                    np.random.RandomState(12))
    np.testing.assert_array_equal(y1, y2)
    assert not np.array_equal(y1, y3)


def test_one_uniform_per_onset_is_drawn_from_the_generator_given():
    tr = _poisson_train(0.02, 3000, seed=6)
    rs = np.random.RandomState(9)
    ot.operational_time_dither(tr, (0, 3000), 30.0, 300.0, rs)
    ref = np.random.RandomState(9)
    ref.uniform(size=tr.size)
    assert rs.uniform() == ref.uniform()


def test_the_width_is_jitter_times_the_mean_rate():
    assert ot.dither_width(50, 1000, 20.0) == pytest.approx(1.0)
    tr = _poisson_train(0.05, 1000, seed=7)
    _, info = ot.operational_time_dither_info(tr, (0, 1000), 20.0, 100.0,
                                              np.random.RandomState(0))
    assert info["width_op"] == pytest.approx(20.0 * tr.size / 1000)
    assert info["edge"] == "reflect" and info["kernel"] == "gaussian"


# ---------------------------------------------------------------- memory bounds


def test_a_map_too_big_to_cache_gives_the_same_surrogates(monkeypatch):
    """Streaming the rows block by block, instead of holding the N x T map,
    must not change a single draw or the exact distribution."""
    tr = _step_train(3000, 0.005, 0.05, seed=14)
    cached = [ot.operational_time_dither(tr, (0, 3000), 40.0, 120.0,
                                         np.random.RandomState(s))
              for s in range(5)]
    d_cached = ot.displacement_distribution(tr, (0, 3000), 40.0, 120.0)
    ot.clear_cache()
    monkeypatch.setattr(ot, "_CACHE_BYTES", 0)
    monkeypatch.setattr(ot, "_CHUNK_BYTES", 8 * 3001 * 7)  # 7 rows a block
    streamed = [ot.operational_time_dither(tr, (0, 3000), 40.0, 120.0,
                                           np.random.RandomState(s))
                for s in range(5)]
    d_streamed = ot.displacement_distribution(tr, (0, 3000), 40.0, 120.0)
    assert ot._op_map(tr, 0, 3000, 120.0, "gaussian").cum is None
    for a, b in zip(cached, streamed):
        np.testing.assert_array_equal(a, b)
    np.testing.assert_array_equal(d_cached.pmf, d_streamed.pmf)


def test_the_build_block_size_does_not_change_the_map(monkeypatch):
    tr = _poisson_train(0.03, 2000, seed=15)
    one = ot._op_map(tr, 0, 2000, 150.0, "gaussian")
    ot.clear_cache()
    monkeypatch.setattr(ot, "_CHUNK_BYTES", 8 * 2001 * 3)  # 3 rows a block
    many = ot._op_map(tr, 0, 2000, 150.0, "gaussian")
    np.testing.assert_array_equal(many.cum, one.cum)
    np.testing.assert_array_equal(many.flat, one.flat)


# ---------------------------------------------------------------- refusals


@pytest.mark.parametrize("bad", [
    dict(train=np.array([5, 1000]), window=(0, 1000)),      # onset at the end
    dict(train=np.array([-1, 5]), window=(0, 1000)),        # before the start
    dict(train=np.array([1.5, 7.0]), window=(0, 1000)),     # not whole frames
    dict(train=np.array([1, 7]), window=(10, 10)),          # empty window
])
def test_bad_trains_and_windows_are_refused(bad):
    with pytest.raises(ValueError):
        ot.operational_time_dither(bad["train"], bad["window"], 5.0, 50.0,
                                   np.random.RandomState(0))


@pytest.mark.parametrize("J,bw", [(-1.0, 50.0), (5.0, 0.0), (np.nan, 50.0),
                                  (5.0, np.inf)])
def test_bad_scales_are_refused(J, bw):
    with pytest.raises(ValueError):
        ot.operational_time_dither(np.array([1, 7]), (0, 100), J, bw,
                                   np.random.RandomState(0))


def test_an_unknown_kernel_is_refused():
    with pytest.raises(ValueError):
        ot.operational_time_dither(np.array([1, 7]), (0, 100), 5.0, 50.0,
                                   np.random.RandomState(0), kernel="epan")


# ---------------------------------------------------------------- not estimable


@pytest.mark.parametrize("tr", [np.array([], dtype=np.int64),
                                np.array([42], dtype=np.int64)])
def test_fewer_than_two_onsets_is_not_estimable_and_comes_back_unchanged(tr):
    y, info = ot.operational_time_dither_info(tr, (0, 100), 10.0, 50.0,
                                              np.random.RandomState(0))
    np.testing.assert_array_equal(y, tr)
    assert y.dtype == np.int64
    assert not info["estimable"] and "two onsets" in info["reason"]
    d = ot.displacement_distribution(tr, (0, 100), 10.0, 50.0)
    assert not d.estimable and d.p_unmoved == 1.0


def test_a_box_narrower_than_the_gap_leaves_each_onset_no_rate_of_its_own():
    """Box of 20 frames, onsets 500 apart: each onset's leave-one-out rate is
    the other's box alone, which has operational time (so the ROI is
    estimable) but none on the onset's own frame (so it is degenerate, and is
    carried into the other's box)."""
    tr = np.array([100, 600], dtype=np.int64)
    y, info = ot.operational_time_dither_info(tr, (0, 1000), 10.0, 20.0,
                                              np.random.RandomState(0),
                                              kernel="box")
    assert info["estimable"]
    assert info["flat_at_onset"] == 2, "neither onset has rate on its own frame"
    assert np.all(np.abs(y - 350) >= 239), "each lands in the other's box"


def test_a_gaussian_tail_that_underflows_is_counted_as_degenerate():
    # sigma 2 frames, onsets 1000 apart: exp(-0.5 * 500**2) is exactly zero,
    # so each onset has no leave-one-out rate on its own frame and is carried
    # into the other onset's kernel — the degeneracy the plan warns of.
    tr = np.array([100, 1100], dtype=np.int64)
    y, info = ot.operational_time_dither_info(tr, (0, 1200), 0.0, 2.0,
                                              np.random.RandomState(0))
    assert info["estimable"]
    assert info["flat_at_onset"] == 2
    assert not np.array_equal(y, tr), "a degenerate onset moves even at J = 0"


# ---------------------------------------------------------------- the rate


def test_the_leave_one_out_rate_is_the_rate_of_the_others():
    """Onset i's row is the full-train estimate computed without it, to the
    rounding of a subtraction."""
    rel = np.array([3.0, 3.0, 40.0, 41.0, 90.0, 150.0])
    T, sigma = 160, 12.0
    loo = ot._loo_masses(rel, T, sigma)
    k = np.arange(T)
    denom = np.array([np.exp(-0.5 * ((kk - k) / sigma) ** 2).sum() for kk in k])
    for i in range(rel.size):
        others = np.delete(rel, i)
        num = np.exp(-0.5 * ((k[None, :] - others[:, None]) / sigma) ** 2).sum(0)
        np.testing.assert_allclose(loo[i], num / denom, rtol=1e-9, atol=1e-13)


def test_the_gaussian_rate_is_edge_corrected_like_the_detectors():
    """A train with an onset on every frame has rate 1 everywhere, edges
    included, because the divisor is the kernel mass inside the window —
    event_rate's truncated-span divisor, carried to a Gaussian. Leave-one-out
    takes exactly the onset's own kernel share out."""
    T, sigma = 200, 15.0
    k = np.arange(T)
    loo = ot._loo_masses(k.astype(float), T, sigma)
    denom = np.array([np.exp(-0.5 * ((kk - k) / sigma) ** 2).sum() for kk in k])
    full = loo[0] + np.exp(-0.5 * (k / sigma) ** 2) / denom
    np.testing.assert_allclose(full, 1.0, rtol=1e-12)


def test_the_box_kernel_is_the_rate_detectors_own_estimator():
    rel = np.array([2.0, 10.0, 11.0, 60.0, 99.0])
    loo = ot._loo_masses(rel, 100, 30.0, "box")
    for i in range(rel.size):
        _, y = train_rate(np.delete(rel, i), (0.0, 99.0), 30.0, 1.0)
        np.testing.assert_array_equal(loo[i], y)


def test_train_rate_is_event_rates_core():
    rs = np.random.RandomState(0)
    trains = [np.sort(rs.uniform(0, 300, size=rs.randint(0, 40)))
              for _ in range(12)]
    for win in (1.0, 7.3, 60.0):
        x1, y1 = event_rate(trains, (0.0, 300.0), win, 0.1)
        x2, y2 = train_rate(np.concatenate(trains), (0.0, 300.0), win, 0.1)
        np.testing.assert_array_equal(x1, x2)
        np.testing.assert_array_equal(y1, y2)


def test_event_rate_keeps_its_population_rule():
    x, y = event_rate([np.array([1.0, 2.0])], (0.0, 10.0), 1.0, 0.1)
    assert x.size == 0 and y.size == 0
    x, y = train_rate(np.array([1.0, 2.0]), (0.0, 10.0), 1.0, 0.1)
    assert x.size == 101 and y.sum() > 0


# ---------------------------------------------------------------- the dither


def test_on_a_flat_rate_it_is_a_uniform_dither_of_width_J_N_over_N_minus_1():
    """A regular train and a kernel far wider than the window: the rate is
    flat, operational time is real time scaled by (N-1)/T, and the dither is
    uniform over +-J*N/(N-1) frames — the N/(N-1) being the leave-one-out cost
    the module docstring flags."""
    T, J = 4000, 30.0
    tr = np.arange(10, T, 20, dtype=np.int64)
    n = tr.size
    d = ot.displacement_distribution(tr, (0, T), J, 1e7)
    half = J * n / (n - 1)
    # the middle onsets never feel an edge
    mid = (tr > 200) & (tr < T - 200)
    np.testing.assert_allclose(d.per_onset_rms[mid],
                               np.sqrt(half ** 2 / 3 + 1 / 12), rtol=2e-3)
    assert d.offsets.min() >= -np.ceil(half) - 1
    assert d.offsets.max() <= np.ceil(half) + 1


def test_the_distribution_is_what_a_draw_samples():
    tr = _step_train(3000, 0.005, 0.05, seed=8)
    J, bw = 60.0, 150.0
    d = ot.displacement_distribution(tr, (0, 3000), J, bw)
    assert d.pmf.sum() == pytest.approx(1.0)
    moves = []
    for draw in range(400):
        _, info = ot.operational_time_dither_info(tr, (0, 3000), J, bw,
                                                  np.random.RandomState(draw))
        moves.append(info["displacement"])
    moves = np.concatenate(moves)
    emp = np.bincount(moves - d.offsets[0], minlength=d.offsets.size)
    assert emp.size == d.offsets.size, "a draw moved farther than the support"
    tv = 0.5 * np.abs(emp / emp.sum() - d.pmf).sum()
    assert tv < 0.08, f"sampled moves disagree with the exact distribution: {tv}"
    assert np.sqrt(np.mean(moves.astype(float) ** 2)) == pytest.approx(d.rms,
                                                                     rel=0.05)


def test_zero_jitter_is_a_point_mass_at_zero():
    tr = _poisson_train(0.03, 1000, seed=9)
    d = ot.displacement_distribution(tr, (0, 1000), 0.0, 100.0)
    assert d.p_unmoved == pytest.approx(1.0) and d.rms == 0.0


def test_busy_stretches_move_less_than_quiet_ones():
    """Louis et al. eq. 8: the real-time dither follows the rate, so for one
    operational-time width the busy half's onsets move about rate-ratio less."""
    T = 6000
    tr = _step_train(T, 0.004, 0.04, seed=10)
    d = ot.displacement_distribution(tr, (0, T), 40.0, 100.0)
    quiet = (tr > 500) & (tr < T // 2 - 1000)
    busy = (tr > T // 2 + 1000) & (tr < T - 500)
    ratio = np.mean(d.per_onset_rms[quiet]) / np.mean(d.per_onset_rms[busy])
    assert 6.0 < ratio < 14.0, ratio


def test_it_keeps_a_rate_step_that_uniform_dither_smears():
    """Counts in a band just before a rate step: operational-time dither keeps
    them near the original, a real-time uniform dither of the same RMS carries
    busy onsets into the quiet side."""
    T = 6000
    h = T // 2
    tr = _step_train(T, 0.004, 0.04, seed=12)
    J, bw = 150.0, 60.0
    band = lambda y: int(np.sum((y >= h - 150) & (y < h)))  # noqa: E731
    base = band(tr)
    d = ot.displacement_distribution(tr, (0, T), J, bw)
    ot_band, ud_band = [], []
    for draw in range(200):
        rs = np.random.RandomState(draw)
        ot_band.append(band(ot.operational_time_dither(tr, (0, T), J, bw, rs)))
        r = d.rms * np.sqrt(3)
        ud = tr + np.round(rs.uniform(-r, r, size=tr.size)).astype(np.int64)
        ud_band.append(band(ud[(ud >= 0) & (ud < T)]))
    assert abs(np.mean(ot_band) - base) < 0.5 * abs(np.mean(ud_band) - base)


def test_reflecting_edges_neither_thin_nor_pile_a_flat_train():
    """Expected occupancy per frame, summed over onsets, for a regular train
    on a flat rate: the 100 frames at each edge hold what the middle does."""
    T = 3000
    tr = np.arange(5, T, 10, dtype=np.int64)
    m = ot._op_map(tr, 0, T, 1e7, "gaussian")
    rows = ot._rows(m, np.arange(tr.size))
    w = ot.dither_width(tr.size, T, 200.0)
    occ = sum(ot._cell_probabilities(rows[i], m.pos[i], m.total[i], w)
              for i in range(tr.size))
    edge = np.r_[occ[:100], occ[-100:]].mean()
    middle = occ[1000:2000].mean()
    assert edge == pytest.approx(middle, rel=0.02)
    assert occ.sum() == pytest.approx(tr.size)


def test_the_dither_moves_things():
    tr = _poisson_train(0.02, 3000, seed=13)
    y = ot.operational_time_dither(tr, (0, 3000), 50.0, 300.0,
                                   np.random.RandomState(1))
    assert not np.array_equal(y, tr)
