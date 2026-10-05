"""The fixed definitions behind ``tools/measure_rate_stretches.py``, on synthetic trains."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import measure_rate_stretches as m  # noqa: E402


def test_population_rate_is_onsets_per_roi_per_second():
    # Two ROIs; ROI 0 has 6 onsets in [0, 60), ROI 1 none: (6 / 60 + 0) / 2 = 0.05 Hz.
    trains = [np.arange(0, 60, 10.0), np.array([])]
    starts, pop, per = m.rates(trains, 0.0, 120.0, 60.0)
    assert starts[0] == 0 and pop[0] == pytest.approx(0.05)
    assert per[0, 0] == pytest.approx(0.1) and per[1, 0] == 0


def test_breadth_is_the_share_of_rois_above_their_own_median():
    per = np.array([[0, 0, 5.0], [1, 1, 3.0], [2, 2, 2.0]])
    assert m.breadth(per).tolist() == pytest.approx([0.0, 0.0, 2 / 3])


def test_a_stretch_needs_two_minutes_at_or_above_k():
    starts = np.arange(0, 600, 10.0)
    elev = np.ones(starts.size)
    elev[10:18] = 4.0             # 8 positions: 70 s of starts + 60 s window = 130 s
    elev[30:33] = 4.0             # 3 positions: 20 + 60 = 80 s, too short
    brd = np.full(starts.size, 0.9)
    got = m.stretches(starts, elev, elev * 2, brd, 60.0, 3.0)
    assert len(got) == 1
    s = got[0]
    assert (s["start"], s["duration"], s["peak_elevation"]) == (100.0, 130.0, 4.0)
    assert s["peak_elevation_vs_baseline"] == 8.0 and s["median_breadth"] == 0.9
    assert m.stretches(starts, elev, elev, brd, 60.0, 5.0) == []


def test_the_bench_stretch_reads_as_a_broad_high_stretch():
    """Every ROI raised together for 300 s: breadth near 1, elevation far above 5."""
    rng = np.random.RandomState(0)
    trains = []
    for _ in range(30):
        bg = rng.uniform(0, 2700, rng.poisson(0.005 * 2700))
        hot = rng.uniform(1200, 1500, rng.poisson(0.13 * 300))
        trains.append(np.sort(np.concatenate([bg, hot])))
    w = m.measure_window(trains, 0.0, 2700.0, None)["60.0"]
    st = w["stretches"]["5.0"]
    assert len(st) == 1 and st[0]["median_breadth"] > 0.9 and st[0]["peak_elevation"] > 10
    assert 1100 <= st[0]["start"] <= 1200 and st[0]["duration"] >= 300


def test_cutting_out_stretches_keeps_the_rest_in_order():
    assert m.cut_out([], 0.0, 100.0, [(20.0, 30.0), (60.0, 70.0)]) == [
        (0.0, 20.0), (30.0, 60.0), (70.0, 100.0)]
    assert m.cut_out([], 0.0, 100.0, []) == [(0.0, 100.0)]


def test_window_types_come_from_the_folder_label():
    assert [m.window_type(x) for x in ("baseline", "TTX", "senktide", "high K+", "wash", "x")] \
        == ["baseline", "TTX", "senktide", "high K+", "wash", "other"]
