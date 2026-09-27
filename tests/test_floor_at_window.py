"""The floor-at-window experiment (2026-09-27): off by default, and only count (sliding) moves.

ADR-0008's floor is counted in a 2 s co-activity window (`event_floor.WINDOW_SEC`). Behind
`BUGARACH_FLOOR_AT_WINDOW=on`, count (sliding) gets its floor counted in its own `win_sec`
instead. These pin that the default path is unchanged, that the flag moves exactly the detector
it names, and that a floor at 2 s is the ADR-0008 floor itself.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

from bugarach import bench
from bugarach import event_floor as ef

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def rec():
    s, _ = bench.make_recording("baseline_quiet", 1)
    return s


def test_it_is_off_by_default(monkeypatch):
    monkeypatch.delenv(bench.FLOOR_AT_WINDOW_ENV, raising=False)
    assert not bench.floor_at_window()
    assert ef.WINDOW_SEC == 2.0, "ADR-0008's window is unchanged by this experiment"


def test_the_default_path_is_the_adr_0008_floor(monkeypatch, rec):
    monkeypatch.delenv(bench.FLOOR_AT_WINDOW_ENV, raising=False)
    adr = bench.recording_floor(rec, bench.STREAM).floor
    p = bench.floored_params("count_sliding", rec, dict(win_sec=0.5, k_offset=0,
                                                        merge_gap_sec=3.0), {}, bench.STREAM, None)
    assert p["min_rois"] == adr


def test_a_floor_at_two_seconds_is_the_default_floor(rec):
    assert bench.recording_floor(rec, bench.STREAM, window_sec=2.0) == \
        bench.recording_floor(rec, bench.STREAM)


def test_on_it_moves_count_sliding_to_its_own_window_and_nothing_else(monkeypatch, rec):
    monkeypatch.setenv(bench.FLOOR_AT_WINDOW_ENV, "on")
    at_half = bench.recording_floor(rec, bench.STREAM, window_sec=0.5)
    assert at_half.window_sec == 0.5
    p = bench.floored_params("count_sliding", rec, dict(win_sec=0.5, k_offset=0,
                                                        merge_gap_sec=3.0), {}, bench.STREAM, None)
    assert p["min_rois"] == at_half.floor
    adr = bench.recording_floor(rec, bench.STREAM).floor
    for det in ("count", "coact"):
        q = bench.floored_params(det, rec, dict(bench.OPERATING_POINTS[det].params), {},
                                 bench.STREAM, None)
        assert q["min_rois"] == adr, f"{det} must keep ADR-0008's floor under the experiment"


def test_a_shorter_window_never_needs_more_cells(rec):
    """Fewer onsets fit in a shorter window, so chance reaches no higher a count there."""
    floors = [bench.recording_floor(rec, bench.STREAM, window_sec=w).floor for w in (0.5, 1, 2)]
    assert floors == sorted(floors)


def test_the_tool_counts_what_moves():
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        import measure_floor_at_window as m
    finally:
        sys.path.pop(0)
    rows = [dict(stream="fast", unit="a", window_sec=w, floor=f)
            for w, f in ((0.5, 4), (1.0, 5), (2.0, 6))]
    rows += [dict(stream="fast", unit="b", window_sec=w, floor=f)
             for w, f in ((0.5, 5), (1.0, 5), (2.0, 5))]
    s = m.summarise(rows)["fast"]
    assert s["0.5"]["moved"] == 1 and s["0.5"]["change_vs_2s"] == {"-2": 1, "0": 1}
    assert s["2"]["moved"] == 0 and s["2"]["median"] == 5.5
