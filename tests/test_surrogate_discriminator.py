"""The per-ROI-only discriminator, on synthetic data only.

The plan (``docs/proposals/2026-09-10-surrogate-evaluation-overnight.md``) asks three
things of this tier, and each has a test here:

- **blind to coordination** — no feature function ever receives more than one ROI, the
  pooling is symmetric, and two windows differing only in cross-ROI timing are
  indistinguishable to it;
- **a forced choice with a within-pair null, folds grouped by mouse**, sized at
  α = 0.05 for 55% accuracy;
- **controls** — uniform dither is detected, real against real is not, and a failed
  control voids the candidate's result.

No recording is read. Every train below is drawn from a renewal process with a hard
floor on the frame grid, the shape of the leak the earlier review found.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from bugarach import surrogate_discriminator as sd

WIN = 600          # analysis window, frames
N_WIN = 4          # analysis windows per generation window
FLOOR = 8          # hard within-ROI floor, frames
BAND = 50          # edge band, frames (5 s at 0.1 s)


# -- synthetic recordings --------------------------------------------------------------------

def _renewal(rs, stop, floor, mean_iv):
    """A renewal train on [0, stop): intervals floor + exponential, whole frames."""
    out, x = [], int(rs.randint(0, int(mean_iv)))
    while x < stop:
        out.append(x)
        x += floor + int(round(rs.exponential(mean_iv - floor)))
    return np.asarray(out, dtype=np.int64)


def _recordings(seed, n_mice=12, recs_per_mouse=2, n_roi=15):
    """(mouse, recording id, per-ROI mean intervals, trains) over one generation window."""
    rs = np.random.RandomState(seed)
    out = []
    for m in range(n_mice):
        mouse_mean = rs.uniform(40, 120)              # mice differ, as real ones do
        for r in range(recs_per_mouse):
            means = mouse_mean * rs.uniform(0.7, 1.3, n_roi)
            trains = [_renewal(rs, N_WIN * WIN, FLOOR, mu) for mu in means]
            out.append((f"mouse{m}", f"mouse{m}-rec{r}", means, trains))
    return out


def _uniform_dither(train, J, rs):
    moved = train + rs.randint(-J, J + 1, train.size)
    return np.sort(moved[(moved >= 0) & (moved < N_WIN * WIN)]).astype(np.int64)


def _pairs(recordings, surrogate, seed):
    """Cut every recording and its surrogate (generated over the whole generation window)
    into analysis windows. Returns real, surrogate, windows, mice, recording ids."""
    rs = np.random.RandomState(seed)
    real, surr, windows, mice, recs = [], [], [], [], []
    for mouse, rec, means, trains in recordings:
        s_trains = [surrogate(tr, mu, rs) for tr, mu in zip(trains, means)]
        for k in range(N_WIN):
            real.append(trains)
            surr.append(s_trains)
            windows.append((k * WIN, (k + 1) * WIN))
            mice.append(mouse)
            recs.append(rec)
    return real, surr, windows, mice, recs


UD = lambda tr, mu, rs: _uniform_dither(tr, 6, rs)                      # noqa: E731
FRESH = lambda tr, mu, rs: _renewal(rs, N_WIN * WIN, FLOOR, mu)         # noqa: E731
NOTHING = lambda tr, mu, rs: tr.copy()                                  # noqa: E731


# -- the structural guarantee ----------------------------------------------------------------

def test_no_feature_function_ever_receives_more_than_one_roi(monkeypatch):
    """Wrap every per-ROI feature function and the pooling step, then run the whole path —
    pairs, features, the forced choice. Every call a feature function receives must be one
    ROI's 1-D train; the pooling step must receive only already-reduced rows, one per ROI,
    with no time axis left in them."""
    seen = {name: [] for name, _, _ in sd.ROI_FEATURES}
    wrapped = []
    for name, cols, fn in sd.ROI_FEATURES:
        def spy(t, window, band, _fn=fn, _name=name):
            arr = np.asarray(t)
            assert arr.ndim == 1, f"{_name} received shape {arr.shape}: more than one ROI"
            assert arr.dtype.kind in "iu", f"{_name} received {arr.dtype}, not frame indices"
            a, b = window
            assert np.all((arr >= a) & (arr < b)), f"{_name} saw onsets outside its window"
            seen[_name].append(arr.size)
            return _fn(t, window, band)
        wrapped.append((name, cols, spy))
    monkeypatch.setattr(sd, "ROI_FEATURES", tuple(wrapped))

    pooled_shapes = []
    real_pool = sd.pool_symmetric

    def pool_spy(per_roi):
        M = np.asarray(per_roi)
        assert M.ndim == 2 and M.shape[1] == len(sd.roi_feature_names()), M.shape
        pooled_shapes.append(M.shape)
        return real_pool(per_roi)
    monkeypatch.setattr(sd, "pool_symmetric", pool_spy)

    recs = _recordings(0, n_mice=3, recs_per_mouse=1, n_roi=7)
    real, surr, windows, mice, _ = _pairs(recs, UD, seed=1)
    res = sd.discriminate_windows(real, surr, windows, mice, BAND, n_permutations=39)

    n_calls = 2 * len(windows) * 7                   # real and surrogate, every ROI
    for name, sizes in seen.items():
        assert len(sizes) == n_calls, f"{name}: {len(sizes)} calls, expected {n_calls}"
    assert pooled_shapes == [(7, len(sd.roi_feature_names()))] * (2 * len(windows))
    assert 0.0 <= res.accuracy <= 1.0


def test_roi_features_refuses_anything_but_one_train():
    with pytest.raises(TypeError, match="one ROI"):
        sd.roi_features(np.array([[1, 2], [3, 4]]), (0, 10), 2)


def test_pooling_does_not_depend_on_roi_order():
    rs = np.random.RandomState(2)
    trains = [_renewal(rs, WIN, FLOOR, rs.uniform(30, 90)) for _ in range(12)]
    trains.append(np.array([], dtype=np.int64))
    trains.append(np.array([300], dtype=np.int64))
    base = sd.window_features(trains, (0, WIN), BAND)
    for _ in range(5):
        order = rs.permutation(len(trains))
        assert np.array_equal(sd.window_features([trains[i] for i in order], (0, WIN), BAND), base)


def test_cross_roi_timing_is_invisible_to_it():
    """Every ROI carries the same train: once all together (perfect synchrony), once each
    shifted by its own offset (no two ROIs coincide), everything clear of the edge bands.
    Per-ROI features are identical, so the pooled features are identical and the forced
    choice is a tie on every pair — accuracy exactly 0.5, P = 1."""
    base = np.array([100, 130, 190, 260, 330, 400], dtype=np.int64)
    n_roi = 20
    sync = [base.copy() for _ in range(n_roi)]
    shifts = np.arange(n_roi) * 4 - 38                     # −38 … +38, distinct
    desync = [base + s for s in shifts]
    assert all(t.min() >= BAND and t.max() < WIN - BAND for t in desync)
    f_sync = sd.window_features(sync, (0, WIN), BAND)
    f_desync = sd.window_features(desync, (0, WIN), BAND)
    assert np.array_equal(f_sync, f_desync)

    n_pairs = 40
    Xr = np.tile(f_sync, (n_pairs, 1))
    Xs = np.tile(f_desync, (n_pairs, 1))
    mice = [f"m{i % 8}" for i in range(n_pairs)]
    res = sd.forced_choice(Xr, Xs, mice, n_permutations=39)
    assert res.accuracy == 0.5 and res.p_value == 1.0 and not res.significant


# -- hand vectors for the features ------------------------------------------------------------

def test_roi_features_hand_vector():
    """Onsets 0, 3, 10, 50, 97 in (0, 100) with −5 and 100 outside; band 5.

    Intervals 3, 7, 40, 47; numpy's linear quantiles at positions 3q put q10 at 4.2,
    q25 at 6, q50 at 23.5, q75 at 41.75, q90 at 44.9. Start band [0, 5) holds 0 and 3;
    end band [95, 100) holds 97.
    """
    got = sd.roi_features(np.array([-5, 0, 3, 10, 50, 97, 100]), (0, 100), 5)
    want = np.concatenate([[5.0], np.log1p([4.2, 6.0, 23.5, 41.75, 44.9]),
                           [math.log1p(3.0)], [2.0, 1.0]])
    assert sd.roi_feature_names() == ["count", "interval_q10", "interval_q25", "interval_q50",
                                      "interval_q75", "interval_q90", "interval_min",
                                      "edge_start", "edge_end"]
    np.testing.assert_allclose(got, want, rtol=0, atol=1e-12)


def test_an_roi_without_intervals_is_left_out_of_interval_statistics():
    rows = np.vstack([sd.roi_features(np.array([10, 20, 60]), (0, 100), 5),
                      sd.roi_features(np.array([40]), (0, 100), 5)])
    pooled = sd.pool_symmetric(rows)
    names = sd.feature_names()
    v = dict(zip(names, pooled))
    assert (v["mean_count"], v["sd_count"], v["min_count"], v["median_count"],
            v["max_count"]) == (2.0, 1.0, 1.0, 2.0, 3.0)
    assert v["min_interval_min"] == pytest.approx(math.log1p(10))
    assert v["max_interval_min"] == pytest.approx(math.log1p(10))   # the lone ROI's only
    assert v["frac_active"] == 1.0 and v["frac_with_interval"] == 0.5
    empty = sd.window_features([], (0, 100), 5)
    assert empty.shape == (len(names),) and not empty.any()


# -- the forced choice ------------------------------------------------------------------------

def test_uniform_dither_is_detected():
    """UD ±6 frames against a hard floor of 8 manufactures sub-floor intervals one ROI at a
    time — the leak that killed the proposal's surrogate. The discriminator must see it."""
    real, surr, windows, mice, _ = _pairs(_recordings(3), UD, seed=4)
    res = sd.discriminate_windows(real, surr, windows, mice, BAND, n_permutations=99, seed=5)
    assert res.accuracy > 0.8
    assert res.p_value == pytest.approx(1 / 100) and res.significant
    assert abs(res.null_accuracy.mean() - 0.5) < 0.05
    assert "interval_min" in " ".join(n for n, _ in res.top_features(5))


def test_doing_nothing_reads_exactly_chance():
    real, surr, windows, mice, _ = _pairs(_recordings(6, n_mice=5), NOTHING, seed=7)
    res = sd.discriminate_windows(real, surr, windows, mice, BAND, n_permutations=39)
    assert res.accuracy == 0.5 and res.p_value == 1.0


def test_an_exchangeable_surrogate_is_flagged_at_about_alpha():
    """A fresh draw of each ROI's own process is exchangeable with the real train, so the
    within-pair null is exact and the false-positive rate is α. Over 20 independent
    datasets, four or more rejections would happen by chance 1.6% of the time."""
    rejections, accs = 0, []
    for seed in range(20):
        real, surr, windows, mice, _ = _pairs(_recordings(100 + seed, n_mice=8), FRESH,
                                              seed=200 + seed)
        res = sd.discriminate_windows(real, surr, windows, mice, BAND, n_permutations=49,
                                      seed=seed)
        rejections += res.significant
        accs.append(res.accuracy)
    assert rejections <= 3, rejections
    assert abs(np.mean(accs) - 0.5) < 0.04


def test_same_seed_same_answer():
    real, surr, windows, mice, _ = _pairs(_recordings(8, n_mice=6), UD, seed=9)
    a = sd.discriminate_windows(real, surr, windows, mice, BAND, n_permutations=39, seed=3)
    b = sd.discriminate_windows(real, surr, windows, mice, BAND, n_permutations=39, seed=3)
    assert a.accuracy == b.accuracy and a.p_value == b.p_value
    assert np.array_equal(a.null_accuracy, b.null_accuracy)


def test_too_few_permutations_to_reach_alpha_is_refused():
    """With B permutations the smallest P is 1/(B + 1); at B = 19 that is exactly 0.05, so
    P < 0.05 is impossible and every candidate would read "not detected"."""
    X = np.random.RandomState(0).normal(size=(20, 3))
    mice = [f"m{i % 4}" for i in range(20)]
    with pytest.raises(ValueError, match="cannot reach"):
        sd.forced_choice(X, X + 1, mice, n_permutations=19)
    sd.forced_choice(X, X + 1, mice, n_permutations=20)


def test_folds_never_split_a_mouse():
    rs = np.random.RandomState(10)
    mice = [f"m{i}" for i in rs.randint(0, 17, 300)]
    folds = sd.mouse_folds(mice, n_folds=5, seed=1)
    for m in set(mice):
        assert np.unique(folds[np.array(mice) == m]).size == 1, m
    assert np.unique(folds).size == 5
    load = np.bincount(folds)
    biggest = max(mice.count(m) for m in set(mice))
    assert load.max() - load.min() <= biggest
    assert np.unique(sd.mouse_folds(["a", "a", "b", "c"], n_folds=5)).size == 3
    with pytest.raises(ValueError, match="two mice"):
        sd.mouse_folds(["a", "a"], n_folds=5)


def test_the_null_permutes_within_pairs():
    """Under the null the label is swapped within each pair: a pair's two feature rows keep
    their pairing. So if every pair is identical up to its orientation, every permutation
    gives the same accuracy as its mirror image, and the null is symmetric about 0.5."""
    real, surr, windows, mice, _ = _pairs(_recordings(11, n_mice=6), UD, seed=12)
    res = sd.discriminate_windows(real, surr, windows, mice, BAND, n_permutations=199, seed=0)
    null = res.null_accuracy
    assert null.size == 199
    assert abs(np.median(null) - 0.5) < 0.05
    assert res.p_value == pytest.approx((1 + np.sum(null >= res.accuracy - 1e-12)) / 200)


# -- sizing -----------------------------------------------------------------------------------

def _exact_power(n, alpha=0.05, p1=0.55):
    """Independent of the module: log-space binomial tails with math.lgamma."""
    def logpmf(k, p):
        return (math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
                + k * math.log(p) + (n - k) * math.log(1 - p))
    tail0, c = 0.0, n + 1
    for k in range(n, -1, -1):                      # smallest c with P0(X ≥ c) ≤ α
        t = tail0 + math.exp(logpmf(k, 0.5))
        if t > alpha:
            break
        tail0, c = t, k
    return sum(math.exp(logpmf(k, p1)) for k in range(c, n + 1))


def test_required_pairs_at_alpha_05_for_55_percent():
    n = sd.required_pairs(0.05, 0.55, 0.8)
    # The normal approximation, ((1.645·0.5 + 0.842·√(0.55·0.45)) / 0.05)², gives 617.
    assert 580 < n < 660
    assert _exact_power(n) >= 0.8
    assert _exact_power(n - 1) < 0.8
    assert sd.binomial_power(n) == pytest.approx(_exact_power(n), abs=1e-9)
    for m in range(n, n + 40):                      # and it stays powered above
        assert sd.binomial_power(m) >= 0.8


def test_the_size_is_stated_in_mice_through_the_design_effect():
    real, surr, windows, mice, _ = _pairs(_recordings(13), UD, seed=14)
    res = sd.discriminate_windows(real, surr, windows, mice, BAND, n_permutations=39)
    assert res.n_mice == 12 and res.pairs_per_mouse == pytest.approx(len(windows) / 12)
    assert res.design_effect == pytest.approx(1 + (res.pairs_per_mouse - 1) * res.icc)
    assert res.required_mice == math.ceil(res.required_pairs * res.design_effect
                                          / res.pairs_per_mouse)
    assert res.powered == (res.n_mice >= res.required_mice)
    assert not res.powered                          # 96 pairs cannot size a 55% test


def test_icc_hand_values():
    assert sd.within_mouse_icc(np.array([1, 1, 0, 0.]), ["a", "a", "b", "b"]) == 1.0
    assert sd.within_mouse_icc(np.array([1, 0, 1, 0.]), ["a", "a", "b", "b"]) == 0.0


# -- controls ---------------------------------------------------------------------------------

def test_negative_control_pairs_windows_within_their_own_recording():
    X = np.arange(10, dtype=float)[:, None] * np.ones((1, 3))
    recs = ["a", "a", "a", "b", "b", "c", "c", "c", "c", "d"]
    mice = ["m1", "m1", "m1", "m1", "m1", "m2", "m2", "m2", "m2", "m3"]
    A, B, pm = sd.negative_control_pairs(X, recs, mice, seed=0)
    pairs = {tuple(sorted((int(a[0]), int(b[0])))) for a, b in zip(A, B)}
    assert pairs == {(0, 1), (3, 4), (5, 6), (7, 8)}
    assert pm == ["m1", "m1", "m2", "m2"]
    firsts = [int(a[0]) for a in sd.negative_control_pairs(X, recs, mice, seed=1)[0]]
    flips = [int(sd.negative_control_pairs(X, recs, mice, seed=s)[0][0, 0]) for s in range(20)]
    assert set(flips) == {0, 1}, "orientation is not randomised"
    assert len(firsts) == 4


def test_a_failed_control_voids_the_candidate():
    real, surr, windows, mice, recs = _pairs(_recordings(15), UD, seed=16)
    Xr, Xs = sd.pair_features(real, surr, windows, BAND)
    detected = sd.forced_choice(Xr, Xs, mice, n_permutations=39)
    blind = sd.forced_choice(Xr, Xr.copy(), mice, n_permutations=39)
    fresh = lambda: sd.forced_choice(Xr, Xs, mice, n_permutations=39)       # noqa: E731

    ok = sd.apply_controls(fresh(), positive=detected, negative=blind)
    assert not ok.void and ok.void_reason == ""
    no_power = sd.apply_controls(fresh(), positive=blind, negative=blind)
    assert no_power.void and "positive control" in no_power.void_reason
    broken = sd.apply_controls(fresh(), positive=detected, negative=detected)
    assert broken.void and "negative control" in broken.void_reason
    unrun = sd.apply_controls(fresh(), positive=None, negative=None)
    assert unrun.void and "not run" in unrun.void_reason


def test_run_cell_runs_the_candidate_beside_both_controls():
    real, surr, windows, mice, recs = _pairs(_recordings(17), FRESH, seed=18)
    _, ud, _, _, _ = _pairs(_recordings(17), UD, seed=19)
    Xr, Xs = sd.pair_features(real, surr, windows, BAND)
    _, Xpos = sd.pair_features(real, ud, windows, BAND)
    cand, pos, neg = sd.run_cell(Xr, Xs, mice, recs, X_positive=Xpos, n_permutations=49, seed=2)
    assert pos.significant and pos.accuracy > 0.8
    assert neg is not None and not neg.significant
    assert not cand.void
    assert not cand.significant
    summary = cand.summary()
    assert set(summary) >= {"accuracy", "p_value", "required_pairs", "required_mice",
                            "powered", "void", "void_reason"}
    unrun, _, _ = sd.run_cell(Xr, Xs, mice, recs, X_positive=None, n_permutations=39)
    assert unrun.void
