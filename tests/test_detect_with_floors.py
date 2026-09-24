"""The pieces of ``tools/detect_with_floors.py`` that decide what a floored call is."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import detect_with_floors as d  # noqa: E402


def test_participants_are_rois_with_an_onset_in_the_call_widened_to_two_seconds():
    trains = [np.array([10.0]), np.array([11.5]), np.array([13.0]), np.array([]),
              np.array([9.0, 10.2])]
    # A zero-width call at 10 s covers [10, 12]: ROIs 0, 1 and 4.
    assert d.participants(trains, 10.0, 0.0, 2.0) == 3
    # A 3.5 s call covers [10, 13.5]: ROI 2 joins.
    assert d.participants(trains, 10.0, 3.5, 2.0) == 4


def test_baseline_is_read_from_the_label():
    assert d.is_baseline("baseline") and d.is_baseline(" Baseline 2")
    assert not d.is_baseline("senktide") and not d.is_baseline(None)


def test_the_summary_lists_groups_in_house_order_and_counts_recordings():
    rows = [dict(slice_id=f"r{i}", group=g, window_kind="baseline", stream="fast",
                 detector="coact", variant="own_floor", calls_per_hour=float(i), own_floor=5)
            for i, g in enumerate(["ORX", "DI", "DI", "MALE", "OVX"])]
    s = d.summarise(rows, ["DI", "OVX", "MALE", "ORX"])
    assert list(s) == ["DI", "OVX", "MALE", "ORX", "all"]
    cell = s["DI"]["baseline|fast|coact|own_floor"]
    assert cell["recordings"] == 2 and cell["median_calls_per_hour"] == 1.5
    assert s["all"]["baseline|fast|coact|own_floor"]["recordings"] == 5
