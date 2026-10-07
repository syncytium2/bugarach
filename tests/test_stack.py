"""stack: the sliding count at several widths, each against a local context-window null, the
least likely width winning (2026-10-07).

Six parts:
- the module stands alone: it imports nothing from ``bugarach``;
- one width with a fixed ``alpha`` is LoCo's sliding path, call for call;
- the null it reads is the exact local null that ``sliding.py`` computes for LoCo and CoactDetect;
- its settings come from where they say: ``call_measure``'s per-stream gaps, whole frames at
  0.1 s, and a stream and a floor that must be named;
- the calibration holds it to count (sliding)'s call rate on rigid shifts;
- the several-width form does what it says: it calls a tight group under the 2 s floor, names
  the width that won, and follows the local rate.

The comparisons with LoCo, ``sliding.py``, ``call_measure`` and count (sliding) live here, outside
the module, on purpose. A change to any of them shows up as a failing test, never as a silent
change to stack.
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
    allowed = {"__future__", "dataclasses", "hashlib", "numpy"}
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
def test_one_width_with_a_fixed_alpha_is_loco_sliding(seed, w, ctx, gap, K, pctile, mode, guard):
    trains, dur = _background(seed, rate_hz=0.02)
    trains = _plant(trains, 600.0, range(8), 0.3)
    ev = [np.sort(np.asarray(v, float)) for v in trains]
    a = _detect_stream_sliding(ev, [], (0.0, dur), binw=w, mgap=gap, ctx=ctx, pctile=pctile,
                               min_rois=K, null_context_mode=mode, clamp_context_to_region=True,
                               guard_sec=guard)
    b = stack_detect(trains, (0.0, dur), stream="fast", widths_sec=(w,), ref_win_sec=w,
                     context_sec=ctx, null_context_mode=mode, alpha=1 - pctile / 100,
                     min_rois=K, merge_gap_sec=gap, guard_sec=guard)
    assert a.onset_sec.size > 0
    assert np.array_equal(a.onset_sec, b.onset_sec)
    assert np.array_equal(a.width_sec, b.width_sec)
    assert np.array_equal(a.magnitude, b.nrois)
    assert np.all(b.stability_sec == w)
    assert b.null["draws"] == 0, "a fixed alpha draws nothing"


# ---------------------------------------------------------------- the null it reads

def test_the_tail_is_the_exact_local_null_of_sliding_py():
    trains, dur = _background(5)
    ev = [np.sort(v) for v in trains]
    index = st._Index(ev)
    for w, lo, hi in ((0.3, 100.0, 220.0), (2.0, 900.0, 960.0), (1.0, 0.0, dur)):
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


# ---------------------------------------------------------------- the settings' sources

def test_the_merge_gaps_are_call_measures_per_stream_gaps():
    """Tony, 2026-10-07: merge gaps consistent with each stream. Copied, not imported, so a
    change to call_measure shows up here rather than silently in stack."""
    from bugarach import call_measure

    assert st.MERGE_GAP_SEC == {s: g for s, (g, _) in call_measure.DEFAULTS.items()}


def test_the_widths_are_whole_frames_at_a_tenth_of_a_second():
    """Tony, 2026-10-07: the frame interval for internal work is 0.1 s."""
    frames = np.asarray(st.WIDTHS_SEC) / 0.1
    assert np.allclose(frames, np.round(frames)) and np.round(frames).min() >= 3


def test_stream_and_the_floor_must_be_named():
    trains, dur = _background(4)
    with pytest.raises(TypeError):
        stack_detect(trains, (0.0, dur), min_rois=5)
    with pytest.raises(TypeError):
        stack_detect(trains, (0.0, dur), stream="fast")


def test_each_stream_merges_at_its_own_gap():
    """Two tight towers 3 s apart: two calls at fast's 0.5 s gap, one at slow's 2.5 s. (Closer
    than the 2 s reference window, the window itself spans both and they are one call whatever
    the gap; that limit is the next test.)"""
    trains, dur = _background(13, rate_hz=0.004)
    two = _plant(_plant(trains, 900.0, range(6), 0.1, seed=1), 903.0, range(6, 12), 0.1, seed=2)
    kw = dict(widths_sec=(0.3, 2.0), alpha=1e-4, min_rois=5)
    assert _near(stack_detect(two, (0.0, dur), stream="fast", **kw), 901.5, 5.0).size == 2
    assert _near(stack_detect(two, (0.0, dur), stream="slow", **kw), 901.5, 5.0).size == 1


def test_towers_closer_than_the_reference_window_are_one_call_whatever_the_gap():
    """A known limit, kept visible: the 2 s window sliding across two towers 1.5 s apart holds
    both at once, so its pieces never drop below the floor between them."""
    trains, dur = _background(13, rate_hz=0.004)
    two = _plant(_plant(trains, 900.0, range(6), 0.1, seed=1), 901.5, range(6, 12), 0.1, seed=2)
    b = stack_detect(two, (0.0, dur), stream="fast", widths_sec=(0.3, 2.0), alpha=1e-4,
                     min_rois=5, merge_gap_sec=0.0)
    assert _near(b, 900.5).size == 1


def test_widths_under_the_frame_interval_are_dropped():
    trains, dur = _background(4, rate_hz=0.02)
    b = stack_detect(trains, (0.0, dur), stream="fast", min_rois=5, frame_interval_sec=0.4,
                     alpha=1e-4)
    assert b.opts["widths_sec"] == (0.5, 1.0, 2.0)


# ---------------------------------------------------------------- the calibration

def test_it_calls_no_more_often_than_count_sliding_on_rigid_shifts():
    trains, dur = _background(7, rate_hz=0.02)
    b = stack_detect(trains, (0.0, dur), stream="fast", min_rois=6, null_draws=40)
    assert b.null["draws"] == 40
    assert 0 < b.null["stack_calls"] <= b.null["ref_calls"]
    assert 0 < b.alpha <= 1
    assert np.all(b.p_value <= b.alpha)


def test_on_independent_background_it_calls_about_as_often_as_count_sliding():
    from bugarach.detectors import count_sliding_detect

    n_stack = n_count = 0
    for seed in range(3):
        trains, dur = _background(20 + seed, rate_hz=0.02)
        n_stack += stack_detect(trains, (0.0, dur), stream="fast", min_rois=6,
                                null_draws=40).n_events
        n_count += count_sliding_detect(trains, (0.0, dur), win_sec=2.0, min_rois=6,
                                        merge_gap_sec=0.5).n_events
    assert n_stack <= 2 * n_count + 3


def test_it_is_deterministic():
    trains, dur = _background(8, rate_hz=0.02)
    a = stack_detect(trains, (0.0, dur), stream="slow", min_rois=6, null_draws=20)
    b = stack_detect(trains, (0.0, dur), stream="slow", min_rois=6, null_draws=20)
    assert a.alpha == b.alpha and np.array_equal(a.onset_sec, b.onset_sec)


# ---------------------------------------------------------------- several widths

def test_a_tight_group_under_the_floor_is_called_at_a_narrow_width():
    """Five ROIs within 0.2 s where the floor at 2 s is seven: the floor applies at the 2 s
    reference only, so a narrow width can call it on its tail probability. That is what the
    narrow widths are for, and what count (sliding) cannot do."""
    from bugarach.detectors import count_sliding_detect

    trains, dur = _background(9, rate_hz=0.004)
    tight = _plant(trains, 900.0, range(5), 0.2)
    assert _near(count_sliding_detect(tight, (0.0, dur), win_sec=2.0, min_rois=7,
                                      merge_gap_sec=0.5), 900.0).size == 0
    b = stack_detect(tight, (0.0, dur), stream="fast", min_rois=7, null_draws=40)
    hit = _near(b, 900.0)
    assert hit.size == 1
    assert b.stability_sec[hit[0]] == 0.3
    assert b.nrois[hit[0]] == 5


def test_the_same_cells_tight_and_spread_out_win_at_different_widths():
    trains, dur = _background(9, rate_hz=0.004)
    tight = _plant(trains, 900.0, range(5), 0.2)
    loose = [np.sort(np.r_[v, 900.0 + 0.45 * i]) if i < 5 else v for i, v in enumerate(trains)]
    kw = dict(stream="fast", min_rois=3, alpha=1e-4)
    b = stack_detect(tight, (0.0, dur), **kw)
    c = stack_detect(loose, (0.0, dur), **kw)
    hb, hc = _near(b, 900.0), _near(c, 900.0)
    assert hb.size == 1 and hc.size == 1
    assert b.stability_sec[hb[0]] == 0.3 and c.stability_sec[hc[0]] == 2.0
    assert c.p_value[hc[0]] > b.p_value[hb[0]], "tight is less likely than loose"


def test_the_null_follows_the_local_rate():
    """The same planted tower is less surprising where the background is busy, because the
    null is drawn from the context around the window rather than the whole recording."""
    r = np.random.RandomState(12)
    dur, n = 1800.0, 30
    trains = [np.sort(np.r_[r.uniform(0, 900, r.poisson(0.004 * 900)),
                            r.uniform(900, dur, r.poisson(0.05 * 900))]) for _ in range(n)]
    planted = _plant(_plant(trains, 450.0, range(6), 0.4, seed=1), 1350.0, range(6), 0.4, seed=1)
    b = stack_detect(planted, (0.0, dur), stream="fast", widths_sec=(1.0,), ref_win_sec=1.0,
                     min_rois=1, alpha=1e-4)
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
    kw = dict(stream="fast", min_rois=5)
    with pytest.raises(ValueError, match="stream"):
        stack_detect(trains, (0.0, dur), stream="medium", min_rois=5)
    with pytest.raises(ValueError, match="null_context_mode"):
        stack_detect(trains, (0.0, dur), null_context_mode="global", **kw)
    with pytest.raises(ValueError, match="guard_sec"):
        stack_detect(trains, (0.0, dur), null_context_mode="symmetric", guard_sec=2.0, **kw)
    with pytest.raises(ValueError, match="frame interval"):
        stack_detect(trains, (0.0, dur), widths_sec=(0.3,), frame_interval_sec=0.5, **kw)
    with pytest.raises(ValueError, match="ref_win_sec"):
        stack_detect(trains, (0.0, dur), widths_sec=(0.3, 0.5), **kw)
    with pytest.raises(ValueError, match="alpha"):
        stack_detect(trains, (0.0, dur), alpha=0.0, **kw)
    with pytest.raises(ValueError, match="min_rois_narrow"):
        stack_detect(trains, (0.0, dur), min_rois_narrow=1, **kw)
    with pytest.raises(ValueError, match="too short"):
        stack_detect(trains, (0.0, 30.0), **kw)


def test_it_has_a_name_a_person_reads():
    assert DISPLAY_NAMES["stack"] == "stack"
