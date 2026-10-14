"""The coordinated fraction under treatment 1 — `tools/measure_coordination_under_treatment.py`.

What these pin: which windows are read (baseline and treatment 1, nothing after), that blank
windows are handled the way the docstring says (an every-ROI span cut from the timeline, a
some-ROI span dropping those ROIs from both windows), and that a planted rise in coordination
under treatment comes out as one. The statistic itself is `measure_coordination_rates.py`'s
and is tested there.
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

import measure_coordination_under_treatment as mct  # noqa: E402
from bugarach.store import Region  # noqa: E402


def test_cut_spans_close_up_the_timeline():
    spans = mct.kept_spans(0.0, 100.0, [(10.0, 20.0), (50.0, 55.0)])
    assert spans == [(0.0, 10.0), (20.0, 50.0), (55.0, 100.0)]
    # 25 s sits 15 s into the kept time once 10 s are cut before it; 60 s sits 45 s in.
    frames = mct.excised_frames([5.0, 15.0, 25.0, 60.0], spans)
    assert frames.tolist() == [50, 150, 450]   # 15 s fell in a cut and is gone


def test_both_spellings_of_the_blank_file_are_read(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / mct.BLANKS).write_text(
        "slice_id\twindow_rois\tstart_frame\tend_frame\tstart_sec\tend_sec\n"
        "r1\tALL\t1\t11\t0\t1\nr1\t6,8\t1\t1801\t0\t180\n", encoding="utf-8")
    (tmp_path / "b").mkdir()
    (tmp_path / "b" / mct.BLANKS).write_text(
        "slice_id\trois\tstart_sec\tend_sec\nr2\tALL\t158\t160\n", encoding="utf-8")
    assert mct.read_blanks(tmp_path / "a") == {"r1": [(None, 0.0, 1.0), ({"6", "8"}, 0.0, 180.0)]}
    assert mct.read_blanks(tmp_path / "b") == {"r2": [(None, 158.0, 160.0)]}
    assert mct.read_blanks(tmp_path / "missing") == {}


def test_treatment_one_is_the_first_period_after_baseline_and_its_analysis_window():
    s = SimpleNamespace(regions=[
        Region(name="high K+", slot=None, start_sec=2820, end_sec=3300),
        Region(name="baseline", slot=None, start_sec=0, end_sec=1200,
               analysis_start_sec=0, analysis_end_sec=1200),
        Region(name="APV+CNQX", slot=None, start_sec=1200, end_sec=2700,
               analysis_start_sec=1320, analysis_end_sec=2520),
        Region(name="gabazine", slot=None, start_sec=2700, end_sec=2820)])
    assert mct.treatment_one_window(s) == ("APV+CNQX", (1320.0, 2520.0))


# ------------------------------------------------------------------ end to end

N_ROI, END = 20, 2520.0


def _write(root: Path, n_rec: int = 3) -> Path:
    """Fast stream: twice as many shared moments in treatment 1 as in baseline."""
    root.mkdir(parents=True)
    rng = np.random.default_rng(7)
    slices = ["slice_id,frame_interval_sec,group_id,mouse_id"]
    regions = ["slice_id,region_idx,label,start_sec,end_sec,analysis_start_sec,analysis_end_sec"]
    blanks = ["slice_id\twindow_rois\tstart_sec\tend_sec"]
    for i in range(n_rec):
        sid = f"rec_{i + 1}"
        fast = [list(rng.uniform(0, END, rng.poisson(0.02 * END))) for _ in range(N_ROI)]
        for lo, hi, gap in ((0, 1200, 60.0), (1320, 2520, 20.0)):
            for t in np.arange(lo + 5, hi - 5, gap):
                for r in rng.choice(N_ROI, 8, replace=False):
                    fast[r].append(t + rng.normal(0, 0.1))
        slow = [list(rng.uniform(0, END, rng.poisson(0.01 * END))) for _ in range(N_ROI)]
        rows = ["roi,time_sec,stream"]
        for name, trains in (("fast", fast), ("slow", slow)):
            for r, v in enumerate(trains):
                rows += [f"{r + 1},{t:.2f},{name}" for t in sorted(v) if 0 <= t < END]
        (root / f"{sid}.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
        slices.append(f"{sid},0.1,MALE,{90 + i}")
        regions += [f"{sid},1,baseline,0,1200,0,1200",
                    f"{sid},2,APV+CNQX+GZ,1200,2520,1320,2520"]
    blanks += ["rec_1\tALL\t100\t110", "rec_1\t3\t0\t180"]
    (root / "slices.csv").write_text("\n".join(slices) + "\n", encoding="utf-8")
    (root / "regions.csv").write_text("\n".join(regions) + "\n", encoding="utf-8")
    (root / mct.BLANKS).write_text("\n".join(blanks) + "\n", encoding="utf-8")
    return root


@pytest.fixture(scope="module")
def measured(tmp_path_factory):
    folder = _write(tmp_path_factory.mktemp("pilot") / "f")
    from bugarach.io import load_folder
    n = len(load_folder(folder))
    return [mct._one((str(folder), i, 1)) for i in range(n)]


def test_blank_windows_are_cut_or_drop_their_rois(measured):
    r1 = next(r for r in measured if r["slice_id"] == "rec_1")
    assert r1["windows"]["baseline"]["cut_sec"] == pytest.approx(10.0)
    assert r1["windows"]["treatment_1"]["cut_sec"] == pytest.approx(0.0)
    assert r1["dropped_rois"] == ["3"]
    for cond in mct.CONDITIONS:      # the dropped ROI is gone from BOTH windows
        assert r1["windows"][cond]["streams"]["fast"]["N"] == N_ROI - 1
    other = next(r for r in measured if r["slice_id"] == "rec_2")
    assert other["dropped_rois"] == [] and other["windows"]["baseline"]["streams"]["fast"]["N"] == N_ROI


def test_a_planted_rise_in_coordination_reads_as_one(measured):
    head = mct.compare(measured, "fast", 1.0, "fixed")
    assert head["recordings"] == 3
    f = head["median_fraction"]
    assert f["treatment_1"] > f["baseline"] > 0
    assert head["median_ratio"] > 1.5
    assert head["treatment_at_or_above_baseline"] == 3


def test_a_window_too_sparse_to_measure_stays_out_of_the_headline(measured):
    """A treatment that cuts the event rate leaves windows below shape_usable's floors, and
    the fraction of almost nothing is not a measurement (the 2026 pilots, 2026-10-14)."""
    import copy
    recs = copy.deepcopy(measured)
    recs[0]["windows"]["treatment_1"]["streams"]["fast"]["shape_usable"] = False
    head = mct.compare(recs, "fast", 1.0, "fixed")
    assert head["recordings"] == 2 and head["all_recordings"]["recordings"] == 3
    assert recs[0]["slice_id"] not in head["usable_in_both"]
