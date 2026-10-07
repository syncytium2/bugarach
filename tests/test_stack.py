"""stack: the sliding count at several widths, the least likely one winning (2026-10-07).

Three halves. That one width alone is ``count_sliding``, call for call, which is what makes
the comparison between the two keys an ablation. That the exact null it reads is the one
``sliding.py`` computes. And that the several-width form does what it says: it is matched to
``count_sliding`` on rigid shifts, it finds a tight tower the wide window alone misses, and it
names the width that won.
"""

from __future__ import annotations

import numpy as np
import pytest

from bugarach.detectors import DISPLAY_NAMES, count_sliding_detect, stack_detect
from bugarach.detectors import sliding as sl
from bugarach.detectors.count import _null_tail, _runs


def _background(seed: int, n_roi: int = 30, rate_hz: float = 0.01, dur: float = 1800.0):
    r = np.random.RandomState(seed)
    return [np.sort(r.uniform(0.0, dur, r.poisson(rate_hz * dur))) for _ in range(n_roi)], dur


def _plant(trains, t: float, rois, spread: float, seed: int = 0):
    r = np.random.RandomState(seed)
    return [np.sort(np.r_[v, t + r.uniform(0.0, spread)]) if i in rois else v
            for i, v in enumerate(trains)]


# ---------------------------------------------------------------- one width is count_sliding

@pytest.mark.parametrize("seed", [1, 2, 3])
@pytest.mark.parametrize("win, gap, K", [(2.0, 3.0, 3), (0.5, 0.0, 2), (1.0, 8.0, 4)])
def test_one_width_alone_is_count_sliding(seed, win, gap, K):
    trains, dur = _background(seed, rate_hz=0.02)
    trains = _plant(trains, 600.0, range(8), 0.3)
    a = count_sliding_detect(trains, (0.0, dur), win_sec=win, min_rois=K, merge_gap_sec=gap)
    b = stack_detect(trains, (0.0, dur), widths_sec=(win,), ref_win_sec=win, min_rois=K,
                     merge_gap_sec=gap)
    assert a.n_events > 0
    assert np.array_equal(a.onset_sec, b.onset_sec)
    assert np.array_equal(a.width_sec, b.width_sec)
    assert np.array_equal(a.nrois, b.nrois)
    assert b.threshold == a.threshold == K
    assert np.all(b.stability_sec == win)
    assert b.null["draws"] == 0, "one width needs no calibration, so it must draw nothing"


def test_one_width_holds_with_the_offset_and_on_a_short_range():
    trains = [np.array([1.0, 1.5, 9.1]), np.array([1.2, 9.5]), np.array([1.9, 11.0]),
              np.array([5.0]), np.array([9.9])]
    for k in (0, 1):
        a = count_sliding_detect(trains, (0.0, 20.0), min_rois=3, k_offset=k, merge_gap_sec=0.0)
        b = stack_detect(trains, (0.0, 20.0), widths_sec=(2.0,), min_rois=3, k_offset=k,
                         merge_gap_sec=0.0)
        assert np.array_equal(a.onset_sec, b.onset_sec) and np.array_equal(a.nrois, b.nrois)


def test_widths_under_the_frame_interval_are_dropped_down_to_count_sliding():
    trains, dur = _background(4, rate_hz=0.02)
    a = count_sliding_detect(trains, (0.0, dur), win_sec=2.0, min_rois=3)
    b = stack_detect(trains, (0.0, dur), widths_sec=(0.25, 0.5, 1.0, 2.0), min_rois=3,
                     frame_interval_sec=1.5)
    assert b.opts["widths_sec"] == (2.0,)
    assert np.array_equal(a.onset_sec, b.onset_sec)


# ---------------------------------------------------------------- the null it reads

def test_the_tail_is_sliding_pys_exact_null():
    trains, dur = _background(5)
    for w in (0.25, 2.0):
        p = sl.catch_probabilities(trains, 0.0, dur, w)
        pmf = sl.poisson_binomial(p)
        tail = _null_tail(trains, 0.0, dur, w)
        assert tail[0] == pytest.approx(1.0)
        assert tail[-1] == 0.0
        assert np.all(np.diff(tail) <= 0)
        assert np.allclose(tail[:pmf.size], np.cumsum(pmf[::-1])[::-1], atol=1e-12)


def test_run_labels_agree_with_merge_runs_on_one_widths_pieces():
    trains, dur = _background(6, rate_hz=0.03)
    starts, ends, S = sl.pieces(trains, 2.0, 0.0, dur)
    m = S >= 3
    for gap in (0.0, 3.0):
        runs = sl.merge_runs(starts[m], ends[m], gap)
        labels = _runs(starts[m], ends[m], gap)
        assert labels[-1] + 1 == len(runs)
        assert [int(np.flatnonzero(labels == j)[0]) for j in range(len(runs))] == \
            [a for a, _ in runs]


# ---------------------------------------------------------------- several widths

def test_it_is_matched_to_count_sliding_on_rigid_shifts_and_never_looser_at_the_reference():
    trains, dur = _background(7, rate_hz=0.02)
    b = stack_detect(trains, (0.0, dur), min_rois=4)
    assert b.null["draws"] == 200
    assert b.null["stack_calls"] <= b.null["ref_calls"]
    assert b.thresholds[2.0] >= 4, "the reference width must not call under the floor"
    counts = [b.thresholds[w] for w in sorted(b.thresholds)]
    assert counts == sorted(counts), "a narrower window cannot need more ROIs than a wider one"


def test_it_is_deterministic():
    trains, dur = _background(8, rate_hz=0.02)
    a = stack_detect(trains, (0.0, dur), min_rois=4)
    b = stack_detect(trains, (0.0, dur), min_rois=4)
    assert a.alpha == b.alpha and np.array_equal(a.onset_sec, b.onset_sec)


def test_a_tight_tower_under_the_reference_count_is_called_and_a_loose_one_is_not():
    """Five ROIs within 0.2 s, where the 2 s window needs seven: the narrow window's count is
    what calls it. The same five spread over 2 s are an ordinary 2 s count and stay uncalled."""
    trains, dur = _background(9, rate_hz=0.004)
    K = 7
    tight = _plant(trains, 900.0, range(5), 0.2)
    loose = [np.sort(np.r_[v, 900.0 + 0.45 * i]) if i < 5 else v for i, v in enumerate(trains)]

    def near(det):
        return np.flatnonzero(np.abs(det.onset_sec - 900.0) < 3.0)

    assert near(count_sliding_detect(tight, (0.0, dur), min_rois=K)).size == 0
    b = stack_detect(tight, (0.0, dur), min_rois=K)
    assert b.thresholds[0.25] <= 5 < b.thresholds[2.0]
    hit = near(b)
    assert hit.size == 1
    assert b.stability_sec[hit[0]] == 0.25, "the winning width is the tower's stability"
    assert b.nrois[hit[0]] == 5
    assert near(stack_detect(loose, (0.0, dur), min_rois=K)).size == 0


def test_the_winning_width_follows_how_tightly_the_onsets_sit():
    trains, dur = _background(10, rate_hz=0.004)
    wide = [np.sort(np.r_[v, 900.0 + 1.8 * i / 14]) if i < 15 else v
            for i, v in enumerate(trains)]
    b = stack_detect(wide, (0.0, dur), min_rois=5)
    j = np.flatnonzero(np.abs(b.onset_sec - 900.0) < 3.0)
    assert j.size == 1 and b.stability_sec[j[0]] == 2.0


# ---------------------------------------------------------------- refusals and the name

def test_refusals():
    trains, dur = _background(11)
    with pytest.raises(ValueError, match="ref_win_sec"):
        stack_detect(trains, (0.0, dur), widths_sec=(0.25, 0.5), ref_win_sec=2.0)
    with pytest.raises(ValueError, match="k_offset"):
        stack_detect(trains, (0.0, dur), k_offset=-1)
    with pytest.raises(ValueError, match="too short"):
        stack_detect(trains, (0.0, 30.0))


def test_it_has_a_name_a_person_reads():
    assert DISPLAY_NAMES["stack"] == "stack"
