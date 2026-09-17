"""A baseline window under 15 minutes is not measured, and the tool says which and why.

Tony, 2026-09-17: *"baselines shorter than 15 minutes should be ignored. they probably should
not have been exported."* Nothing in the declared folder is affected — its shortest baseline
is 17.0 minutes — so the only way to know this rule works is a folder built to break it.

The dropped window must be NAMED. A threshold that quietly shrinks the denominator is how a
measurement comes to be over a different population than its readout claims.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

from bugarach import bench
from bugarach.io import load_folder

TOOLS = Path(__file__).resolve().parents[1] / "tools"


@pytest.fixture(scope="module")
def compare():
    spec = importlib.util.spec_from_file_location("_csvb2", TOOLS / "compare_sliding_vs_binned.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["_csvb2"] = m
    spec.loader.exec_module(m)
    return m


def _folder(root: Path, baseline_sec: float) -> Path:
    """One recording whose baseline window is `baseline_sec` long."""
    root.mkdir(parents=True, exist_ok=True)
    rows = ["roi,time_sec"]
    for roi in range(1, 6):
        for t in np.arange(5.0, baseline_sec, 50.0):
            rows.append(f"{roi},{t:.2f}")
    (root / "rec_1.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (root / "slices.csv").write_text("slice_id,frame_interval_sec\nrec_1,0.1\n", encoding="utf-8")
    (root / "regions.csv").write_text(
        "slice_id,region_idx,label,start_sec,end_sec,analysis_start_sec,analysis_end_sec\n"
        f"rec_1,1,baseline,0,{baseline_sec:.1f},0,{baseline_sec:.1f}\n", encoding="utf-8")
    return root


def test_the_floor_is_fifteen_minutes():
    assert bench.MIN_BASELINE_SEC == 900.0


def test_a_short_baseline_is_dropped_and_named(tmp_path, compare):
    s = load_folder(_folder(tmp_path / "short", 840.0))[0]          # 14 minutes
    sl, why = compare._window_slice(s, "events")
    assert sl is None
    assert "840" in why and "900" in why and "MIN_BASELINE_SEC" in why


def test_a_baseline_at_the_floor_is_measured(tmp_path, compare):
    """The rule is *shorter than* 15 minutes, so 15 minutes exactly stays in."""
    s = load_folder(_folder(tmp_path / "exact", 900.0))[0]
    sl, dur = compare._window_slice(s, "events")
    assert sl is not None and dur == pytest.approx(900.0)


def test_the_declared_folders_shortest_baseline_is_recorded():
    """The claim the constant's docstring makes about today's folder, kept true.

    If a new export arrives with a shorter baseline, the docstring's "nothing is affected"
    stops being true, and this is where that shows up.
    """
    src = Path(bench.__file__).read_text(encoding="utf-8")
    i = src.index("MIN_BASELINE_SEC = ")
    block = src[i:i + 1600]
    assert "17.0 minutes" in block, (
        "the constant must say what the declared folder's shortest baseline is, or nobody "
        "can tell whether applying it changed a number")
