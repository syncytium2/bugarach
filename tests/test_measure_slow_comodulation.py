"""The population cross-correlogram behind the slow co-modulation explainer, on synthetic trains.

What must hold for ``docs/learned/slow_comodulation/README.md`` to mean what it says: the pair
count equals a brute-force count, reads zero for independent ROIs, puts a fixed cross-ROI lag in
the bin that holds it, and ignores same-ROI pairs; the two nulls keep what they claim to keep; and
the synthetic worlds produce the shapes the page teaches with — a narrow peak for events, a
shoulder for shared modulation, nothing for modulation drawn per ROI.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import measure_slow_comodulation as msc  # noqa: E402

DT = 0.1


def _brute(trains, L, max_lag):
    obs = np.zeros(max_lag + 1)
    for i, a in enumerate(trains):
        for j, b in enumerate(trains):
            if i == j:
                continue
            for x in a:
                for y in b:
                    if 0 <= y - x <= max_lag:
                        obs[y - x] += 1
    return obs


def test_pair_count_matches_brute_force():
    rs = np.random.RandomState(1)
    L = 400
    trains = [np.unique(rs.randint(0, L, size=rs.randint(0, 25))) for _ in range(5)]
    max_lag = L - 1
    idx = msc.lag_bins(DT, max_lag)
    want = np.bincount(idx[idx >= 0], _brute(trains, L, max_lag)[idx >= 0],
                       minlength=len(msc.LAG_EDGES_SEC) - 1)
    got, _ = msc.pair_counts(trains, L, DT)
    np.testing.assert_allclose(got, want, atol=1e-6)


def test_same_roi_pairs_are_not_counted():
    L = 2000
    train = np.arange(0, L, 7)
    got, _ = msc.pair_counts([train, np.array([], np.int64)], L, DT)
    assert np.allclose(got, 0.0)


def test_a_fixed_lag_lands_in_its_bin():
    L = 12000
    a = np.arange(100, 11000, 97)
    lag = 30                                   # 3.0 s
    got, exp = msc.pair_counts([a, a + lag], L, DT)
    excess = got / exp - 1
    b = np.searchsorted(msc.LAG_EDGES_SEC, lag * DT, side="right") - 1
    assert excess[b] == np.max(excess)
    # The 2.66-3.72 s bin spans eleven lag frames and only one holds pairs, so the bin's ratio
    # is diluted about elevenfold; it still stands far above every other bin.
    others = np.delete(excess, b)
    assert excess[b] > 2 and np.all(others < 0.5 * excess[b])


def test_independent_rois_read_zero_when_pooled():
    rows = []
    for i in range(40):
        trains, L = msc.synthetic_recording("independent", 1000 + i)
        o, e = msc.pair_counts(trains, L, DT)
        rows.append(dict(arms={"real": [list(o), list(e)]}, mouse=str(i)))
    ex = msc.pooled(rows, "real")
    assert np.all(np.abs(ex[1:]) < 0.15), ex


def test_circular_and_block_nulls_keep_what_they_claim():
    rs = np.random.RandomState(3)
    L, block = 6000, 1200
    trains = [np.unique(rs.randint(0, L, size=60)) for _ in range(6)]
    circ = msc.circular(trains, L, np.random.RandomState(4))
    assert [len(t) for t in circ] == [len(t) for t in trains]
    blk = msc.block_circular(trains, L, block, np.random.RandomState(5))
    edges = np.arange(0, L + block, block)
    for t, s in zip(trains, blk):
        np.testing.assert_array_equal(np.histogram(t, edges)[0], np.histogram(s, edges)[0])


def test_arms_trim_both_ends_by_the_largest_displacement():
    trains, L = msc.synthetic_recording("events", 7)
    arms, _, used = msc.arms_for(trains, L, DT, ("t",), 1, None)
    assert used == pytest.approx(L * DT - 2 * msc.TRIM_SEC)
    assert set(arms) == {"real", "circular", "block_120", "rigid_1.6", "rigid_10", "rigid_20"}


def _world_excess(world, n=12):
    rows = []
    for i in range(n):
        trains, L = msc.synthetic_recording(world, 500 + i)
        o, e = msc.pair_counts(trains, L, DT)
        rows.append(dict(arms={"real": [list(o), list(e)]}))
    return msc.pooled(rows, "real")


def test_the_worlds_have_the_shapes_the_page_teaches():
    lo = np.asarray(msc.LAG_EDGES_SEC[:-1])
    short, mid = lo < 0.5, (lo >= 5) & (lo < 30)
    events, shared, per_roi = (_world_excess(w) for w in ("events", "shared", "per_roi"))
    assert events[short].mean() > 1.0 and abs(events[mid].mean()) < 0.1
    assert shared[mid].mean() > 0.2
    assert abs(per_roi[short].mean()) < 0.15 and abs(per_roi[mid].mean()) < 0.1
