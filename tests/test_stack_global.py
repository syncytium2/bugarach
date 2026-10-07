"""stack_global: stack's first form, kept as it was (Tony, 2026-10-07).

Four parts:
- it is the code that ran at 8646eb4: exactly that commit's output on five recordings, four of
  which go through the rigid-shift calibration (``tests/fixtures/stack_global_8646eb4.json``);
- it stands alone: it imports nothing from ``bugarach``;
- one width alone is count (sliding), call for call, checked from outside the module;
- the several-width form does what it says: it is matched to count (sliding) on rigid shifts, it
  finds a tight tower the wide window alone misses, and it names the width that won.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import numpy as np
import pytest

from bugarach.detectors import DISPLAY_NAMES, count_sliding_detect, stack_global_detect
from bugarach.detectors import stack_global as sg

FIXTURE = Path(__file__).parent / "fixtures" / "stack_global_8646eb4.json"


def _background(seed: int, n_roi: int = 30, rate_hz: float = 0.01, dur: float = 1800.0):
    r = np.random.RandomState(seed)
    return [np.sort(r.uniform(0.0, dur, r.poisson(rate_hz * dur))) for _ in range(n_roi)], dur


def _plant(trains, t: float, rois, spread: float, seed: int = 0):
    r = np.random.RandomState(seed)
    return [np.sort(np.r_[v, t + r.uniform(0.0, spread)]) if i in rois else v
            for i, v in enumerate(trains)]


# ---------------------------------------------------------------- it is the 8646eb4 code

@pytest.mark.parametrize("case", range(5))
def test_it_reproduces_8646eb4_exactly(case):
    c = json.loads(FIXTURE.read_text())["cases"][case]
    kw = {k: tuple(v) if isinstance(v, list) else v for k, v in c["kwargs"].items()}
    d = stack_global_detect([np.asarray(v) for v in c["trains"]], tuple(c["t_range"]), **kw)
    e = c["expected"]
    for name in ("onset_sec", "width_sec", "nrois", "strength", "stability_sec", "p_value"):
        assert np.array_equal(getattr(d, name), np.asarray(e[name], float)), name
    assert d.alpha == e["alpha"]
    assert d.threshold == e["threshold"]
    assert {f"{w}": k for w, k in d.thresholds.items()} == e["thresholds"]
    assert d.null == e["null"]


def test_the_fixture_exercises_the_calibration():
    cases = json.loads(FIXTURE.read_text())["cases"]
    assert sum(c["expected"]["null"]["draws"] > 0 for c in cases) == 4
    assert all(len(c["expected"]["onset_sec"]) > 0 for c in cases)


# ---------------------------------------------------------------- it stands alone

def test_the_module_imports_nothing_from_the_package():
    tree = ast.parse(Path(sg.__file__).read_text())
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
            assert name.split(".")[0] in allowed, f"stack_global.py imports {name}"


# ---------------------------------------------------------------- one width is count_sliding

@pytest.mark.parametrize("seed", [1, 2, 3])
@pytest.mark.parametrize("win, gap, K", [(2.0, 3.0, 3), (0.5, 0.0, 2), (1.0, 8.0, 4)])
def test_one_width_alone_is_count_sliding(seed, win, gap, K):
    trains, dur = _background(seed, rate_hz=0.02)
    trains = _plant(trains, 600.0, range(8), 0.3)
    a = count_sliding_detect(trains, (0.0, dur), win_sec=win, min_rois=K, merge_gap_sec=gap)
    b = stack_global_detect(trains, (0.0, dur), widths_sec=(win,), ref_win_sec=win, min_rois=K,
                            merge_gap_sec=gap)
    assert a.n_events > 0
    assert np.array_equal(a.onset_sec, b.onset_sec)
    assert np.array_equal(a.width_sec, b.width_sec)
    assert np.array_equal(a.nrois, b.nrois)
    assert b.threshold == a.threshold == K
    assert np.all(b.stability_sec == win)
    assert b.null["draws"] == 0, "one width needs no calibration, so it must draw nothing"


# ---------------------------------------------------------------- several widths

def test_it_is_matched_to_count_sliding_on_rigid_shifts_and_never_looser_at_the_reference():
    trains, dur = _background(7, rate_hz=0.02)
    b = stack_global_detect(trains, (0.0, dur), min_rois=4)
    assert b.null["draws"] == 200
    assert b.null["stack_calls"] <= b.null["ref_calls"]
    assert b.thresholds[2.0] >= 4, "the reference width must not call under the floor"
    counts = [b.thresholds[w] for w in sorted(b.thresholds)]
    assert counts == sorted(counts), "a narrower window cannot need more ROIs than a wider one"


def test_it_is_deterministic():
    trains, dur = _background(8, rate_hz=0.02)
    a = stack_global_detect(trains, (0.0, dur), min_rois=4)
    b = stack_global_detect(trains, (0.0, dur), min_rois=4)
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
    b = stack_global_detect(tight, (0.0, dur), min_rois=K)
    assert b.thresholds[0.25] <= 5 < b.thresholds[2.0]
    hit = near(b)
    assert hit.size == 1
    assert b.stability_sec[hit[0]] == 0.25, "the winning width is the tower's stability"
    assert b.nrois[hit[0]] == 5
    assert near(stack_global_detect(loose, (0.0, dur), min_rois=K)).size == 0


# ---------------------------------------------------------------- refusals and the name

def test_refusals():
    trains, dur = _background(11)
    with pytest.raises(ValueError, match="ref_win_sec"):
        stack_global_detect(trains, (0.0, dur), widths_sec=(0.25, 0.5), ref_win_sec=2.0)
    with pytest.raises(ValueError, match="k_offset"):
        stack_global_detect(trains, (0.0, dur), k_offset=-1)
    with pytest.raises(ValueError, match="too short"):
        stack_global_detect(trains, (0.0, 30.0))


def test_it_has_a_name_a_person_reads():
    assert DISPLAY_NAMES["stack_global"] == "stack (global)"
