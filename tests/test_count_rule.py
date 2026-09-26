"""count, the simple rule: a bin and a count against the floor (2026-09-26).

Two halves. The rule itself, on a raster small enough to count by eye; and its registration,
because there is no detector registry here and a detector missing from one hard-coded list is
a search, a scorer or a folder run that silently leaves it out.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import numpy as np
import pytest

from bugarach.detectors import DISPLAY_NAMES, count_detect, count_sliding_detect

#: The two forms, and the setting that is each one's width.
FORMS = {"count": "bin_sec", "count_sliding": "win_sec"}

ROOT = Path(__file__).resolve().parent.parent


def _trains(*rois):
    return [np.asarray(r, float) for r in rois]


# ---------------------------------------------------------------- the rule, by eye
#
# 20 s, 2 s bins, so bin b is [2b, 2b + 2). Per bin, the ROIs with an onset:
#   bin 0 [0, 2):   A (1.0 and 1.5: two onsets, one ROI), B, C     -> 3
#   bin 2 [4, 6):   D                                              -> 1
#   bin 4 [8, 10):  A, B, E                                        -> 3
#   bin 5 [10, 12): C                                              -> 1
RASTER = _trains([1.0, 1.5, 9.1],   # A
                 [1.2, 9.5],        # B
                 [1.9, 11.0],       # C
                 [5.0],             # D
                 [9.9])             # E


def test_the_count_is_distinct_rois_per_bin():
    r = count_detect(RASTER, (0.0, 20.0), bin_sec=2.0, min_rois=3, merge_gap_sec=0.0)
    assert r.obs.tolist() == [3, 0, 1, 0, 3, 1, 0, 0, 0, 0]
    assert r.threshold == 3


def test_bins_at_the_threshold_are_called():
    r = count_detect(RASTER, (0.0, 20.0), bin_sec=2.0, min_rois=3, merge_gap_sec=0.0)
    assert r.onset_sec.tolist() == [0.0, 8.0]
    assert r.width_sec.tolist() == [2.0, 2.0]
    assert r.nrois.tolist() == [3, 3]


def test_the_offset_raises_the_threshold_above_the_floor():
    r = count_detect(RASTER, (0.0, 20.0), bin_sec=2.0, min_rois=3, k_offset=1,
                     merge_gap_sec=0.0)
    assert r.threshold == 4 and r.n_events == 0


def test_called_bins_join_across_a_gap_no_wider_than_the_merge_gap():
    # The two called bins are 6 s apart (edge 2 s to edge 8 s).
    apart = count_detect(RASTER, (0.0, 20.0), bin_sec=2.0, min_rois=3, merge_gap_sec=5.0)
    joined = count_detect(RASTER, (0.0, 20.0), bin_sec=2.0, min_rois=3, merge_gap_sec=6.0)
    assert apart.n_events == 2
    assert joined.onset_sec.tolist() == [0.0] and joined.width_sec.tolist() == [10.0]


def test_a_zero_merge_gap_still_joins_bins_that_touch():
    tr = _trains([0.5, 2.5], [0.6, 2.6], [0.7, 2.7])
    r = count_detect(tr, (0.0, 10.0), bin_sec=2.0, min_rois=3, merge_gap_sec=0.0)
    assert r.onset_sec.tolist() == [0.0] and r.width_sec.tolist() == [4.0]


def test_one_bursty_roi_counts_once():
    tr = _trains(np.linspace(0.1, 1.9, 20), [9.0])
    r = count_detect(tr, (0.0, 10.0), bin_sec=2.0, min_rois=2, merge_gap_sec=0.0)
    assert r.obs[0] == 1 and r.n_events == 0


def test_there_is_no_null_so_nothing_is_random():
    a = count_detect(RASTER, (0.0, 20.0), bin_sec=0.5, min_rois=2)
    b = count_detect(RASTER, (0.0, 20.0), bin_sec=0.5, min_rois=2)
    assert a.onset_sec.tolist() == b.onset_sec.tolist()


def test_below_the_floor_is_refused():
    with pytest.raises(ValueError, match="k_offset"):
        count_detect(RASTER, (0.0, 20.0), k_offset=-1)
    with pytest.raises(ValueError, match="k_offset"):
        count_sliding_detect(RASTER, (0.0, 20.0), k_offset=-1)


# ---------------------------------------------------------------- v2, sliding, by eye
#
# The same raster, a 2 s window ending at t: an ROI counts while t is in [onset, onset + 2).
#   A 1.0, 1.5 -> [1.0, 3.5)   B 1.2 -> [1.2, 3.2)   C 1.9 -> [1.9, 3.9)
#   so three ROIs from t = 1.9 until B leaves at 3.2: one call, events 1.0 to 1.9.
#   A 9.1 -> [9.1, 11.1)  B 9.5 -> [9.5, 11.5)  E 9.9 -> [9.9, 11.9)  C 11.0 -> [11.0, 13.0)
#   so three from 9.9, four in [11.0, 11.1), three until B leaves at 11.5: events 9.1 to 11.0.
# The two runs are 9.9 - 3.2 = 6.7 s apart.


def test_the_sliding_calls_by_eye():
    r = count_sliding_detect(RASTER, (0.0, 20.0), win_sec=2.0, min_rois=3, merge_gap_sec=0.0)
    assert r.onset_sec.tolist() == pytest.approx([1.0, 9.1])
    assert r.width_sec.tolist() == pytest.approx([0.9, 1.9])
    assert r.nrois.tolist() == [3, 4]
    assert r.width_kind == "tightness"


def test_sliding_runs_join_across_the_merge_gap():
    apart = count_sliding_detect(RASTER, (0.0, 20.0), win_sec=2.0, min_rois=3,
                                 merge_gap_sec=6.6)
    joined = count_sliding_detect(RASTER, (0.0, 20.0), win_sec=2.0, min_rois=3,
                                  merge_gap_sec=6.8)
    assert apart.n_events == 2
    assert joined.onset_sec.tolist() == pytest.approx([1.0])
    assert joined.width_sec.tolist() == pytest.approx([10.0])


def test_a_bin_edge_splits_what_the_sliding_window_keeps():
    """What v2 is for (Tony, 2026-09-26: "Simple rule v2 should be sliding"). Three onsets
    within 0.4 s straddle the edge at 2 s: the bins see 1 and 2, the window sees 3."""
    tr = _trains([1.8], [2.1], [2.2])
    binned = count_detect(tr, (0.0, 10.0), bin_sec=2.0, min_rois=3)
    sliding = count_sliding_detect(tr, (0.0, 10.0), win_sec=2.0, min_rois=3)
    assert binned.n_events == 0
    assert sliding.onset_sec.tolist() == pytest.approx([1.8])


# ---------------------------------------------------------------- registered everywhere


BENCHES = ["bugarach.bench", "bugarach.bench_slow", "bugarach.bench_combined"]


@pytest.mark.parametrize("key", list(FORMS))
@pytest.mark.parametrize("mod", BENCHES)
def test_every_bench_declares_it(mod, key):
    b = importlib.import_module(mod)
    assert key in b.OPERATING_POINTS and key in b.DETECTORS
    assert set(b.FULL_GRIDS[key]) == {FORMS[key], "k_offset", "merge_gap_sec"}
    for budget in (b.MAX_PROBE_PER_MIN, b.MAX_FALSE_POSITIVES_PER_HOUR, b.MAX_PRECISION_DROP):
        assert key in budget


@pytest.mark.parametrize("key", list(FORMS))
def test_the_floor_is_its_minimum_and_the_offset_rides_on_top(key):
    from bugarach import bench

    assert bench.FLOORED_SETTING[key] == "min_rois"
    s, _ = bench.make_recording("baseline_quiet", 1)
    floor = int(bench.recording_floor(s, bench.STREAM).floor)
    assert bench.run_detector(key, s).threshold == floor
    assert bench.run_detector(key, s, k_offset=2).threshold == floor + 2


@pytest.mark.parametrize("key", list(FORMS))
@pytest.mark.parametrize("mod", BENCHES[1:])
def test_the_slow_benches_run_it(mod, key):
    b = importlib.import_module(mod)
    s, _ = b.make_recording("baseline_quiet", 1)
    assert b.run_detector(key, s).n_events >= 0


def test_the_two_forms_are_two_results():
    """Each result says which form made it: its own key, its own width setting, its own
    width_kind. `--sliding` in the search switches LoCo and CoactDetect only."""
    from bugarach import bench

    s, _ = bench.make_recording("baseline_quiet", 1)
    v1, v2 = bench.run_detector("count", s), bench.run_detector("count_sliding", s)
    assert (v1.width_kind, v2.width_kind) == ("episode_span", "tightness")
    assert "window_mode" not in v1.opts and v2.opts["window_mode"] == "sliding"
    src = (ROOT / "tools" / "search_all_settings.py").read_text(encoding="utf-8")
    assert 'for d in ("loco", "coact"):' in src


def _tool(name):
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        return importlib.import_module(name)
    finally:
        sys.path.pop(0)


def test_the_search_reads_it():
    S = _tool("search_all_settings")
    for key, width in FORMS.items():
        assert key in S.SPACE and key in S.NAMES and key in S.ORDER
        assert S.shipped_value(key, width) == 2.0
        # Bins and windows stop at one frame.
        assert S.extend(width, [0.1, 0.5, 1.0], low_end=True) is None
        assert S.extend(width, [0.15, 0.5], low_end=True) == 0.1
    assert S.NAMES["count"] != S.NAMES["count_sliding"]
    # The offset stops at the floor; merge gap 0 is an off-limit.
    assert S.extend("k_offset", [0, 1, 2, 3], low_end=True) is None
    assert S.extend("k_offset", [0, 1, 2, 3], low_end=False) == 4
    assert S.is_off_limit("merge_gap_sec", 0.0)
    assert not S.is_off_limit("k_offset", 0)


def test_the_scorer_and_the_folder_paths_read_it():
    from bugarach import detect_folder as df

    src = (ROOT / "tools" / "detect_with_floors.py").read_text(encoding="utf-8")
    for key in FORMS:
        assert key in _tool("score_bench_candidates").CODED
        assert key in df.AVAILABLE and key in df.FLAT
        assert key not in df.DETECTORS, "runs when named, not in every folder run"
        assert df.ONSET_FIELD[key] == "t50rise"
    assert '"count": count_detect' in src and '"count_sliding": count_sliding_detect' in src
    assert DISPLAY_NAMES["count"] == "count (binned)"
    assert DISPLAY_NAMES["count_sliding"] == "count (sliding)"


def test_it_is_benched_and_not_published():
    """Measured against the six, not shipped: absent from the default folder run (above), the
    viewer page and the public site's figures, until the bench says it earns a place."""
    assert set(FORMS) <= set(_tool("build_site").BENCH_ONLY)
    drift = (ROOT / "tests" / "test_registries_do_not_drift.py").read_text(encoding="utf-8")
    assert 'NOT_IN_THE_BROWSER = {\n    "count":' in drift and '"count_sliding":' in drift
