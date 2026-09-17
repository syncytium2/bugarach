"""The population cross-correlogram behind the slow co-modulation explainer, on synthetic trains.

What must hold for ``docs/learned/slow_comodulation/README.md`` to mean what it says: the pair
count equals a brute-force count over unordered ROI pairs at every lag the page reads, including
past 40 s; the circular-shift arm reads zero in every lag bin, the shortest included; a fixed
cross-ROI lag lands in its bin; the block control keeps each ROI's count per block; rigid shift
moves each ROI by one whole-frame offset and drops what leaves the window; the count-variance
measure is the variance of the binned population count; and the worlds have the shapes the page
teaches with.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import measure_slow_comodulation as msc  # noqa: E402
from tube_self_supervised import rigid_frames  # noqa: E402

DT = 0.1
NB = len(msc.LAG_EDGES_SEC) - 1


def _brute(trains, max_lag):
    """Unordered pairs of distinct ROIs, onset pairs at |lag| = k, k = 0..max_lag."""
    obs = np.zeros(max_lag + 1)
    for i in range(len(trains)):
        for j in range(i + 1, len(trains)):
            d = np.abs(np.subtract.outer(np.asarray(trains[i]), np.asarray(trains[j]))).ravel()
            d = d[d <= max_lag]
            obs += np.bincount(d, minlength=max_lag + 1)
    return obs


@pytest.mark.parametrize("L", [400, 5000])
def test_pair_count_matches_brute_force(L):
    rs = np.random.RandomState(L)
    trains = [np.unique(rs.randint(0, L, size=rs.randint(0, 40))) for _ in range(5)]
    max_lag = min(int(round(msc.MAX_LAG_SEC / DT)), L - 1)
    idx = msc.lag_bins(DT, max_lag)
    want = np.bincount(idx[idx >= 0], _brute(trains, max_lag)[idx >= 0], minlength=NB)
    got, _ = msc.pair_counts(trains, L, DT)
    np.testing.assert_allclose(got, want, atol=1e-6)
    if L > 3000:
        b = msc.lag_bins(DT, max_lag)[450]                    # 45 s of lag
        assert b >= 0 and msc.LAG_EDGES_SEC[b] > 40           # a bin past 40 s was reached
        assert want[b] > 0                                     # and it holds pairs


def _heavy_removal(seed, n_roi=14, L=9000, dt=0.1):
    """Independent background in every ROI plus a whole-field event every 9 s, so CoactDetect
    removes the events and about 60 % of the onsets and what is left is independent by
    construction: any removal arm must then read about 1 against its null."""
    rs = np.random.RandomState(seed)
    events = np.arange(300, L - 300, 90)
    trains = [np.unique(np.clip(np.concatenate([rs.randint(0, L, size=90), events]), 0, L - 1))
              for _ in range(n_roi)]
    return trains, L, dt


def test_the_removal_null_keeps_both_the_holes_and_the_counts():
    """The null for the removal arms shifts each ROI inside the stretches no episode covers, so
    it carries the arm's episode-shaped holes and its onset count. The earlier null — the circular
    shift of the already-removed trains — fails the first half, and that is what is tested."""
    trains, L, dt = _heavy_removal(500)
    removed, episodes, extra = msc.coact_removed(trains, L, dt, "fast")
    assert extra["share_removed"] > 0.3 and len(episodes) > 20
    trim = int(np.ceil(msc.TRIM_SEC / dt))
    rt, Lt = msc.trimmed(removed, L, trim)
    keep = msc.surviving_frames(episodes, Lt, dt, trim)
    shifted = msc.masked_circular_shift(rt, keep, np.random.RandomState(0))
    assert [len(t) for t in shifted] == [len(t) for t in rt]           # every count survives
    assert all(keep[np.asarray(t, np.int64)].all() for t in shifted)   # no onset inside an episode
    mismatched = msc.sg.circular_shift(rt, (0, Lt), ("x", 1)).trains
    assert sum(int((~keep[np.asarray(t, np.int64)]).sum()) for t in mismatched) > 0


@pytest.mark.parametrize("arm", ["minus_coact", "minus_coact_block_120"])
def test_removal_arms_read_one_when_what_survives_is_independent(arm):
    """At every bin width the page reads, the 1-minute bin included — and the null the tool used
    before reads above it, which is the defect this guards."""
    rows = []
    for i in range(10):
        trains, L, dt = _heavy_removal(500 + i)
        arms, _, _ = msc.arms_for(trains, L, dt, ("heavy", i), 2, "fast")
        rows.append(dict(arms=arms, mouse=str(i)))
    assert msc.null_of(arm) == "circular_mask"
    vr = msc.pooled(rows, arm)[1]
    assert np.all(np.abs(vr - 1.0) < 0.25), vr
    mismatched = msc.pooled(rows, arm, null="circular_minus_coact")[1]
    assert mismatched[0] > vr[0], (mismatched, vr)


def test_same_roi_pairs_are_not_counted():
    L = 2000
    got, _ = msc.pair_counts([np.arange(0, L, 7), np.array([], np.int64)], L, DT)
    assert np.allclose(got, 0.0)


def test_a_fixed_lag_lands_in_its_bin():
    L = 12000
    a = np.arange(100, 11000, 97)
    got, exp = msc.pair_counts([a, a + 30], L, DT)
    excess = got / exp - 1
    b = np.searchsorted(msc.LAG_EDGES_SEC, 3.0, side="right") - 1
    assert excess[b] == np.max(excess)
    assert np.all(np.delete(excess, b) < 0.5 * excess[b])


def test_the_circular_arm_reads_zero_in_every_bin():
    rows = []
    for i in range(30):
        trains, L, dt = msc.synthetic_recording("sim_events", i)
        arms, _, _ = msc.arms_for(trains, L, dt, ("t", i), 1, None)
        rows.append(dict(arms=arms, mouse=str(i)))
    ex, vr = msc.pooled(rows, "circular")
    assert np.all(np.abs(ex) < 0.1), ex
    np.testing.assert_allclose(vr, 1.0)


def test_block_control_keeps_each_rois_count_per_block():
    rs = np.random.RandomState(3)
    L, block = 6000, 1200
    trains = [np.unique(rs.randint(0, L, size=60)) for _ in range(6)]
    blk = msc.sg.window_circular_shift(trains, (0, L), ("t",), analysis_window=block).trains
    edges = np.arange(0, L + block, block)
    for t, s in zip(trains, blk):
        np.testing.assert_array_equal(np.histogram(t, edges)[0], np.histogram(s, edges)[0])


def test_rigid_shift_moves_each_roi_by_one_whole_frame_offset_and_drops_the_rest():
    L, J = 1000, 25.0
    t = np.arange(0, L, 61)          # spacing > 2J, so every onset's shift is unambiguous
    shifts = []
    for seed in range(200):
        for s in rigid_frames([t, t, t], L, J, np.random.RandomState(seed)):
            shift = int(s[1] - t[np.argmin(np.abs(t - s[1]))])
            kept = t + shift
            np.testing.assert_array_equal(s, kept[(kept >= 0) & (kept < L)])
            shifts.append(shift)
    assert min(shifts) == -J and max(shifts) == J


def test_count_variance_is_the_variance_of_the_binned_population_count():
    rs = np.random.RandomState(5)
    L = 6000
    trains = [np.unique(rs.randint(0, L, size=50)) for _ in range(4)]
    pop = msc.raster(trains, L).sum(axis=0)
    want = pop.reshape(60, 100).sum(axis=1).var(ddof=1)
    assert msc.count_variance(trains, L, DT)[1] == pytest.approx(want)


def test_detrended_variance_is_the_residual_variance_of_a_fitted_line():
    rs = np.random.RandomState(8)
    L = 12000
    trains = [np.unique(rs.randint(0, L, size=80)) for _ in range(5)]
    pop = msc.raster(trains, L).sum(axis=0)
    c = pop.reshape(20, 600).sum(axis=1)
    x = np.arange(20.0)
    resid = c - np.polyval(np.polyfit(x, c, 1), x)
    want = np.sum(resid ** 2) / 18
    got = msc.count_variance(trains, L, DT)
    assert got[len(msc.VAR_BIN_SEC) + 2] == pytest.approx(want)


def test_arms_trim_both_ends_by_the_largest_displacement():
    trains, L, dt = msc.synthetic_recording("shared_20s", 7)
    arms, _, used = msc.arms_for(trains, L, dt, ("t",), 1, None)
    assert used == pytest.approx(L * dt - 2 * msc.TRIM_SEC)
    assert set(arms) == {"real", "circular", "circular_ref8", "circular_single_0",
                         "circular_single_1", "circular_single_2", "block_120", "rigid_1.6",
                         "rigid_10", "rigid_20"}


def _world(world, n=10):
    rows = []
    for i in range(n):
        trains, L, dt = msc.synthetic_recording(world, 500 + i)
        o, e = msc.pair_counts(trains, L, dt)
        rows.append(dict(arms={"real": np.concatenate([o, e, [1, 1, 1]]),
                               "circular": np.concatenate([o, e, [1, 1, 1]])}))
    return msc.pooled(rows, "real")[0]


def test_the_worlds_have_the_shapes_the_page_teaches():
    lo = np.asarray(msc.LAG_EDGES_SEC[:-1])
    short, mid = lo < 0.6, (lo >= 5) & (lo < 30)
    events, background, hot, shared = (_world(w) for w in
                                       ("sim_events", "sim_background", "sim_hot_window",
                                        "shared_20s"))
    # The generator plants 15 events of 3-7 ROIs in 3,525 s, so its peak is modest; it must
    # still stand clear of zero at short lags and fall to nothing by 5 s.
    assert events[short].mean() > 0.3 and abs(events[mid].mean()) < 0.15
    assert abs(background[short].mean()) < 0.2 and abs(background[mid].mean()) < 0.15
    assert hot[mid].mean() > 0.5
    assert shared[mid].mean() > 0.2
