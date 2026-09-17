"""The sliding-vs-binned comparison measures the analysis window, and its arithmetic is right.

The comparison itself runs on real recordings and its output stays in the darkroom
(FOUNDATIONS §5). What can be tested anywhere is the part that decides *what is measured*:
the baseline analysis window rather than the raw period, one stream, no regions left on to
drag the detectors across the treatments — and the two matched fractions, which answer
different questions and are easy to transpose.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

from bugarach.io import load_folder

TOOLS = Path(__file__).resolve().parents[1] / "tools"


@pytest.fixture(scope="module")
def tool():
    spec = importlib.util.spec_from_file_location("_csvb", TOOLS / "compare_sliding_vs_binned.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["_csvb"] = m
    spec.loader.exec_module(m)
    return m


def _folder(root: Path) -> Path:
    """One recording: a baseline period of 0–1800 s scored over 600–1800 s, then a treatment.

    Each ROI fires once every 100 s, so counting the events in a window is counting the
    window.
    """
    root.mkdir(parents=True, exist_ok=True)
    rows = ["roi,time_sec"]
    for roi in range(1, 6):
        for t in np.arange(10.0, 3000.0, 100.0):
            rows.append(f"{roi},{t:.2f}")
    (root / "rec_1.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (root / "slices.csv").write_text("slice_id,frame_interval_sec\nrec_1,0.1\n", encoding="utf-8")
    (root / "regions.csv").write_text(
        "slice_id,region_idx,label,start_sec,end_sec,analysis_start_sec,analysis_end_sec\n"
        "rec_1,1,baseline,0,1800,600,1800\n"
        "rec_1,2,TTX,1800,3000,1860,3000\n", encoding="utf-8")
    return root


def test_it_measures_the_analysis_window_and_not_the_period_or_the_treatment(tmp_path, tool):
    s = load_folder(_folder(tmp_path / "f"))[0]
    sl, dur = tool._window_slice(s, "events")
    assert dur == pytest.approx(1200.0), "the analysis window, not the 1800 s period"
    assert sl.regions == [], (
        "the regions must come off, or every detector runs over the treatment too "
        "(FOUNDATIONS §9)")
    stream = sl.streams[list(sl.streams)[0]]
    times = np.concatenate([np.asarray(t, float) for t in (stream.t50rise or stream.locs)])
    assert times.size and times.min() >= 0.0 and times.max() < 1200.0, (
        "events must be re-zeroed into the window, and nothing from the treatment may survive")
    # 600-1800 s at one event per ROI per 100 s: 12 per ROI, 5 ROIs.
    assert times.size == 60


def test_a_recording_with_no_baseline_is_skipped_with_a_reason(tmp_path, tool):
    folder = _folder(tmp_path / "g")
    (folder / "regions.csv").write_text(
        "slice_id,region_idx,label,start_sec,end_sec\nrec_1,1,TTX,0,1800\n", encoding="utf-8")
    s = load_folder(folder)[0]
    sl, why = tool._window_slice(s, "events")
    assert sl is None and "baseline" in why.lower()


def test_recovered_and_new_are_not_the_same_question(tool):
    binned = np.array([10.0, 20.0, 30.0])
    sliding = np.array([10.2, 20.1, 30.1, 40.0, 50.0])
    # Every binned call has a sliding call near it...
    assert tool._matched(binned, sliding, 0.5) == pytest.approx(1.0)
    # ...while two of the five sliding calls are new.
    assert 1.0 - tool._matched(sliding, binned, 0.5) == pytest.approx(0.4)
    # A tolerance too tight to bridge the offset matches nothing.
    assert tool._matched(binned, sliding, 0.05) == pytest.approx(0.0)


def test_no_calls_is_undefined_rather_than_perfect(tool):
    """A recording where the binned mode called nothing has no fraction to report, and
    reporting 1.0 there would say the sliding mode reproduced everything."""
    assert np.isnan(tool._matched(np.array([]), np.array([1.0]), 0.5))
    assert tool._matched(np.array([1.0]), np.array([]), 0.5) == 0.0
