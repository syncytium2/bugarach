"""stack: the sliding count at several widths, each against a local context-window null, the
least likely width winning (2026-10-07).

Four parts:
- the module stands alone: it imports nothing from ``bugarach``;
- one width alone is LoCo's sliding path, call for call, which makes the comparison between
  the two an ablation;
- the null it reads is the exact local null that ``sliding.py`` computes for LoCo and CoactDetect;
- the several-width form does what it says: it shares ``alpha`` across the widths, finds a tight
  tower a wide window misses, names the width that won, and follows the local rate.

The comparisons with LoCo and ``sliding.py`` live here, outside the module, on purpose. A change
to either shows up as a failing test, never as a silent change to stack.
"""

from __future__ import annotations

import ast
from pathlib import Path

import numpy as np
import pytest

from bugarach.detectors import DISPLAY_NAMES, stack_detect
from bugarach.detectors import sliding as sl
from bugarach.detectors import stack as st
from bugarach.detectors.loco import _detect_stream_sliding


def _background(seed: int, n_roi: int = 30, rate_hz: float = 0.01, dur: float = 1800.0):
    r = np.random.RandomState(seed)
    return [np.sort(r.uniform(0.0, dur, r.poisson(rate_hz * dur))) for _ in range(n_roi)], dur


def _plant(trains, t: float, rois, spread: float, seed: int = 0):
    r = np.random.RandomState(seed)
    return [np.sort(np.r_[v, t + r.uniform(0.0, spread)]) if i in rois else v
            for i, v in enumerate(trains)]


def _near(det, t: float, tol: float = 3.0) -> np.ndarray:
    return np.flatnonzero(np.abs(det.onset_sec - t) < tol)


# ---------------------------------------------------------------- it stands alone

def test_the_module_imports_nothing_from_the_package():
    """Tony, 2026-10-07: stack should not depend on code that might change under it."""
    tree = ast.parse(Path(st.__file__).read_text())
    allowed = {"__future__", "dataclasses", "numpy"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0, "no relative imports"
            names = [node.module]
        else:
            continue
        for name in names:
            assert name.split(".")[0] in allowed, f"stack.py imports {name}"


# ---------------------------------------------------------------- one width is LoCo (sliding)

@pytest.mark.parametrize("seed", [1, 2, 3])
@pytest.mark.parametrize("w, ctx, gap, K, pctile, mode, guard", [
    (1.0, 120.0, 2.0, 3, 99.5, "maxlt", 0.0),
    (2.0, 60.0, 8.0, 3, 99.9, "symmetric", 0.0),
    (0.5, 120.0, 3.0, 2, 99.0, "maxlt", 4.0),
])
def test_one_width_alone_is_loco_sliding(seed, w, ctx, gap, K, pctile, mode, guard):
    trains, dur = _background(seed, rate_hz=0.02)
    trains = _plant(trains, 600.0, range(8), 0.3)
    ev = [np.sort(np.asarray(v, float)) for v in trains]
    a = _detect_stream_sliding(ev, [], (0.0, dur), binw=w, mgap=gap, ctx=ctx, pctile=pctile,
                               min_rois=K, null_context_mode=mode, clamp_context_to_region=True,
                               guard_sec=guard)
    b = stack_detect(trains, (0.0, dur), widths_sec=(w,), context_sec=ctx,
                     null_context_mode=mode, alpha=1 - pctile / 100, min_rois=K,
                     merge_gap_sec=gap, guard_sec=guard)
    assert a.onset_sec.size > 0
    assert np.array_equal(a.onset_sec, b.onset_sec)
    assert np.array_equal(a.width_sec, b.width_sec)
    assert np.array_equal(a.magnitude, b.nrois)
    assert np.all(b.stability_sec == w)


# ---------------------------------------------------------------- the null it reads

def test_the_tail_is_the_exact_local_null_of_sliding_py():
    trains, dur = _background(5)
    ev = [np.sort(v) for v in trains]
    index = st._Index(ev)
    for w, lo, hi in ((0.25, 100.0, 220.0), (2.0, 900.0, 960.0), (1.0, 0.0, dur)):
        assert np.allclose(index.catch_probabilities(lo, hi, w),
                           sl.catch_probabilities(ev, lo, hi, w), rtol=0, atol=1e-15)
        pmf = sl.poisson_binomial(sl.catch_probabilities(ev, lo, hi, w))
        for s in range(0, 5):
            assert st._tail(index, lo, hi, w, s) == pytest.approx(pmf[s:].sum(), abs=1e-12)


def test_pieces_and_run_labels_agree_with_sliding_py():
    trains, dur = _background(6, rate_hz=0.03)
    ev = [np.sort(v) for v in trains]
    a, b = st._pieces(ev, 2.0, 0.0, dur), sl.pieces(ev, 2.0, 0.0, dur)
    for x, y in zip(a, b):
        assert np.array_equal(x, y)
    starts, ends, S = a
    m = S >= 3
    for gap in (0.0, 3.0):
        runs = sl.merge_runs(starts[m], ends[m], gap)
        labels = st._runs(starts[m], ends[m], gap)
        assert labels[-1] + 1 == len(runs)
        assert [int(np.flatnonzero(labels == j)[0]) for j in range(len(runs))] == \
            [r0 for r0, _ in runs]


# ---------------------------------------------------------------- several widths

def test_alpha_is_shared_across_the_widths():
    trains, dur = _background(7, rate_hz=0.02)
    b = stack_detect(trains, (0.0, dur), alpha=1e-3)
    assert b.alpha_per_width == pytest.approx(1e-3 / 4)
    assert np.all(b.p_value <= b.alpha_per_width + 1e-12)


def test_widths_under_the_frame_interval_are_dropped():
    trains, dur = _background(4, rate_hz=0.02)
    b = stack_detect(trains, (0.0, dur), frame_interval_sec=0.4)
    assert b.opts["widths_sec"] == (0.5, 1.0, 2.0)
    assert b.alpha_per_width == pytest.approx(1e-3 / 3)


def test_the_same_cells_tight_and_spread_out_win_at_different_widths():
    """Five ROIs within 0.2 s, and the same five spread evenly over 1.8 s. On a quiet
    background both are unlikely under the local null; what differs is the width that finds
    them, and that width is what the call reports as the tower's stability."""
    trains, dur = _background(9, rate_hz=0.004)
    tight = _plant(trains, 900.0, range(5), 0.2)
    loose = [np.sort(np.r_[v, 900.0 + 0.45 * i]) if i < 5 else v for i, v in enumerate(trains)]
    b = stack_detect(tight, (0.0, dur), min_rois=3)
    hit = _near(b, 900.0)
    assert hit.size == 1
    assert b.stability_sec[hit[0]] == 0.25
    assert b.nrois[hit[0]] == 5
    c = stack_detect(loose, (0.0, dur), min_rois=3)
    hit = _near(c, 900.0)
    assert hit.size == 1
    assert c.stability_sec[hit[0]] == 2.0
    assert c.p_value[hit[0]] > b.p_value[_near(b, 900.0)[0]], "tight is less likely than loose"


def test_the_winning_width_follows_how_tightly_the_onsets_sit():
    trains, dur = _background(10, rate_hz=0.004)
    wide = [np.sort(np.r_[v, 900.0 + 1.8 * i / 14]) if i < 15 else v
            for i, v in enumerate(trains)]
    b = stack_detect(wide, (0.0, dur), min_rois=5)
    j = _near(b, 900.0)
    assert j.size == 1 and b.stability_sec[j[0]] == 2.0


def test_the_null_follows_the_local_rate():
    """The same planted tower is less surprising where the background is busy, because the
    null is drawn from the context around the window rather than the whole recording."""
    r = np.random.RandomState(12)
    dur, n = 1800.0, 30
    trains = [np.sort(np.r_[r.uniform(0, 900, r.poisson(0.004 * 900)),
                            r.uniform(900, dur, r.poisson(0.05 * 900))]) for _ in range(n)]
    planted = _plant(_plant(trains, 450.0, range(6), 0.4, seed=1), 1350.0, range(6), 0.4, seed=1)
    b = stack_detect(planted, (0.0, dur), widths_sec=(1.0,), min_rois=1)
    t, S, p = b.signal.t, b.signal.y, b.signal.ref     # every piece's count and local tail

    def at(c):
        m = (t >= c) & (t <= c + 1.4)
        return S[m].max(), p[m].min()

    (s_quiet, p_quiet), (s_busy, p_busy) = at(450.0), at(1350.0)
    assert s_quiet >= 6 and s_busy >= 6, "the tower is there in both stretches"
    assert p_quiet < p_busy / 100, "and is far less surprising where the background is busy"


# ---------------------------------------------------------------- refusals and the name

def test_refusals():
    trains, dur = _background(11)
    with pytest.raises(ValueError, match="null_context_mode"):
        stack_detect(trains, (0.0, dur), null_context_mode="global")
    with pytest.raises(ValueError, match="guard_sec"):
        stack_detect(trains, (0.0, dur), null_context_mode="symmetric", guard_sec=2.0)
    with pytest.raises(ValueError, match="frame interval"):
        stack_detect(trains, (0.0, dur), widths_sec=(0.25,), frame_interval_sec=0.5)
    with pytest.raises(ValueError, match="alpha"):
        stack_detect(trains, (0.0, dur), alpha=0.0)


def test_it_has_a_name_a_person_reads():
    assert DISPLAY_NAMES["stack"] == "stack"
