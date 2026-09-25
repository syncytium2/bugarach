"""``tools/measure_real_intervals.py``: events are runs at or above the floor, timed at their peak,
and events closer than one co-activity window merge (ADR-0010 part 2, step 1)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import measure_real_intervals as mri  # noqa: E402

DT, WF = 0.1, 20          # a 2 s window at 0.1 s frames


def test_each_run_at_or_above_the_floor_is_one_event_at_its_peak():
    c = np.zeros(1000, int)
    c[100:110] = [5, 6, 8, 7, 6, 5, 5, 5, 5, 5]      # peak at 102
    c[600:605] = 9                                     # tie: the first, 600
    ev = mri.events_of(c, floor=5, dt=DT, wf=WF, lo=10.0)
    assert [t for t, _ in ev] == pytest.approx([10.0 + (102 + 10) * DT, 10.0 + (600 + 10) * DT])
    assert [k for _, k in ev] == [8, 9]


def test_events_closer_than_two_seconds_merge_keeping_the_higher():
    c = np.zeros(1000, int)
    c[100] = 6
    c[112] = 9            # 1.2 s later: merged, the higher kept
    c[400] = 7            # 30 s later: separate
    ev = mri.events_of(c, floor=5, dt=DT, wf=WF, lo=0.0)
    assert [k for _, k in ev] == [9, 7]
    assert ev[1][0] - ev[0][0] > 2.0


def test_nothing_above_the_floor_is_no_event():
    assert mri.events_of(np.full(100, 4), floor=5, dt=DT, wf=WF, lo=0.0) == []


def test_describe_reports_shares_and_rate():
    d = mri.describe(np.array([1.0, 5.0, 50.0, 200.0]), hours=0.5, n_events=5)
    assert d["n_gaps"] == 4 and d["events_per_hour"] == 10.0
    assert d["share_under_10_sec"] == 0.5 and d["share_under_120_sec"] == 0.75
