"""The recording-identity measurement's builders, on synthetic recordings only.

What must hold for the measurement to mean what ``docs/learned/recording_identity.md``
declares: a chimera replaces exactly the declared share of ROIs, keeps the rest untouched,
re-bases every donor train inside the target window, takes donors only from its tier, and
never hands the same-recording tier the target window itself. The bootstrap must cover the
truth on data with no signal.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import measure_recording_identity as mri  # noqa: E402

AW = 600


def _rec(rid, mouse, group, date="d1", n_roi=10, n_win=4, seed=0, offset=0):
    rs = np.random.RandomState(seed)
    lo = offset
    hi = lo + n_win * AW
    trains = [np.sort(rs.randint(lo, hi, size=rs.randint(0, 40))).astype(np.int64)
              for _ in range(n_roi)]
    return mri.Rec(rid, mouse, group, date, 0.1, (lo, hi), trains)


@pytest.fixture
def recs():
    return [
        _rec("a1", "m1", "G1", seed=1),
        _rec("a2", "m1", "G1", seed=2, offset=123),
        _rec("b1", "m2", "G1", date="d2", seed=3),
        _rec("c1", "m3", "G2", date="d3", seed=4, n_roi=7),
    ]


def test_donor_pools_respect_their_tier(recs):
    t = recs[0]
    assert [r.recording_id for r in mri.donor_pool(t, recs, "self_other_time")] == ["a1"]
    assert [r.recording_id for r in mri.donor_pool(t, recs, "same_mouse")] == ["a2"]
    assert [r.recording_id for r in mri.donor_pool(t, recs, "same_group")] == ["b1"]
    assert [r.recording_id for r in mri.donor_pool(t, recs, "other_group")] == ["c1"]
    assert mri.donor_pool(recs[3], recs, "same_mouse") == []


@pytest.mark.parametrize("tier", mri.TIERS)
@pytest.mark.parametrize("share", mri.SWAP_SHARES)
def test_chimera_replaces_the_declared_share_and_keeps_the_rest(recs, tier, share):
    t = recs[0]
    w = t.windows(AW)[1]
    trains, meta = mri.chimera(t, w, share, tier, recs, np.random.RandomState(7))
    assert len(trains) == len(t.trains)
    assert meta["replaced"] == int(round(share * len(t.trains)))
    native = [mri.cut(tr, w, w[0]) for tr in t.trains]
    unchanged = sum(np.array_equal(a, b) for a, b in zip(trains, native))
    assert unchanged >= len(t.trains) - meta["replaced"]
    for tr in trains:
        assert tr.size == 0 or (tr.min() >= w[0] and tr.max() < w[1])


def test_same_recording_tier_never_uses_the_target_window():
    # One-window-apart recording: every donor train must come from the OTHER window, so
    # with a train that fires only in the target window the chimera's donors are empty.
    t = mri.Rec("x", "m", "G", "d", 0.1, (0, 2 * AW),
                [np.arange(0, AW, 50, dtype=np.int64) for _ in range(6)])
    trains, meta = mri.chimera(t, (0, AW), 1.0, "self_other_time", [t], np.random.RandomState(0))
    assert meta["replaced"] == 6
    assert all(tr.size == 0 for tr in trains)


def test_cut_rebases_onto_the_target_window():
    got = mri.cut(np.array([5, 610, 650, 1300]), (600, 1200), 0)
    assert got.tolist() == [10, 50]


def test_donors_rotate_before_repeating(recs):
    many = recs + [_rec(f"o{i}", f"mo{i}", "G2", seed=10 + i) for i in range(5)]
    t = many[0]
    _, meta = mri.chimera(t, t.windows(AW)[0], 0.5, "other_group", many, np.random.RandomState(3))
    assert meta["n_donor_recordings"] == 5          # 5 replaced ROIs, 6 donors: no repeat
    assert meta["max_rois_per_donor"] == 1


def test_mouse_bootstrap_covers_chance_on_coin_flips():
    rs = np.random.RandomState(0)
    mice = np.repeat(np.arange(40), 20)
    vals = (rs.random_sample(mice.size) < 0.5).astype(float)
    lo, hi = mri.mouse_bootstrap(vals, mice, seed=1)
    assert lo < 0.5 < hi
    assert hi - lo < 0.12


def test_verdict_bands():
    assert mri.verdict((0.50, 0.58)) == "ADMISSIBLE"
    assert mri.verdict((0.62, 0.70)) == "NOT ADMISSIBLE"
    assert mri.verdict((0.55, 0.65)) == "UNDECIDED"
