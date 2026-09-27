"""The fast gallery's stated rules: how examples are picked, and what the tally flags mean."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import fast_disagreement_gallery as g  # noqa: E402

GROUPS = ["DI", "OVX", "MALE", "ORX"]


def _c(sid, label, group, on, region="1"):
    return dict(slice_id=sid, label=label, group=group, onset_sec=str(on), width_sec="0.5",
                region_idx=region)


def test_picks_rotate_through_treatments_and_skip_calls_near_the_edge():
    wins = {(f"r{i}", "1"): (0.0, 1000.0) for i in range(12)}
    pool = [_c(f"r{i}", t, grp, 500.0) for i, (t, grp) in enumerate(
        [(t, grp) for t in g.TREATMENTS for grp in GROUPS])]
    pool.append(_c("r0", "baseline", "DI", 5.0))          # inside the zoom of the window's start
    got = g.pick(pool, wins, GROUPS, seed=1, n=6)
    assert [(c["label"], c["group"]) for c in got] == [
        ("baseline", "DI"), ("TTX", "OVX"), ("senktide", "MALE"),
        ("baseline", "OVX"), ("TTX", "MALE"), ("senktide", "ORX")]
    assert all(float(c["onset_sec"]) == 500.0 for c in got)


def test_the_pick_is_the_same_for_the_same_seed():
    wins = {("r", "1"): (0.0, 1000.0)}
    pool = [_c("r", "baseline", "DI", t) for t in range(20, 900, 40)]
    assert g.pick(pool, wins, GROUPS, seed=7, n=3) == g.pick(pool, wins, GROUPS, seed=7, n=3)


def test_flags_follow_the_stated_thresholds():
    assert g.flags(dict(over=2, spread=1.0, rel=1.0)) == ["tight"]
    assert g.flags(dict(over=3, spread=2.0, rel=1.5)) == ["wide", "busy"]
    assert g.flags(dict(over=None, spread=None, rel=None)) == []
