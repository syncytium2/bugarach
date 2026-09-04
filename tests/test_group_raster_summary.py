"""The per-group raster summary: one PDF a group, and every flagged event red.

The figure's whole claim is that a red mark means *the producer confirmed a
whole-field brightness step here*. Two ways that claim can quietly fail, and both
are tested rather than eyeballed: the sidecar join can drop rows, which under-reports
the artifact while the page still looks finished; and the tool can be pointed at the
excluded folder, where there is nothing left to draw and a clean-looking page is a
lie about a corpus that was cleaned rather than born clean.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

pytest.importorskip("matplotlib", reason="figure tool; matplotlib is the 'figures' extra")

import make_group_raster_summary as mod  # noqa: E402


SLICES = (
    "slice_id,frame_interval_sec,date,mouse_id,group_id,n_roi_recorded\n"
    "s1,0.1,20240101,1,MALE,2\n"
    "s2,0.1,20240102,2,MALE,2\n"
    "s3,0.1,20240103,3,DI,2\n"
)
REGIONS = (
    "slice_id,region_idx,label,start_sec,end_sec,analysis_start_sec,analysis_end_sec\n"
    "s1,1,baseline,0,100,0,100\n"
    "s2,1,baseline,0,100,0,100\n"
    "s3,1,baseline,0,100,0,100\n"
)
EVENTS = (
    "roi,time_sec,stream,width_sec,width_def,peak_sec,amp\n"
    "1,10.000000,fast,1.0,halfprom_width_findpeaks_w,10.5,1.0\n"
    "1,50.000000,fast,1.0,halfprom_width_findpeaks_w,50.5,1.0\n"
    "2,10.100000,fast,1.0,halfprom_width_findpeaks_w,10.6,1.0\n"
    "1,10.050000,slow,1.0,rise_interval_peak_minus_t50rise,11.0,1.0\n"
    "2,80.000000,slow,1.0,rise_interval_peak_minus_t50rise,81.0,1.0\n"
)
#: Three of s1's five events sit on a step; s2 and s3 carry none. The manifest is
#: the ONLY place that says so — the flag columns never survive the loader.
MANIFEST = (
    "slice_id\troi\tstream\ttime_sec\tonset_sec\tfield_step_id\tregion\tin_analysis_window\n"
    "s1\t1\tfast\t10.000000\t10.000000\ts1@10.0\tbaseline\t1\n"
    "s1\t2\tfast\t10.100000\t10.100000\ts1@10.0\tbaseline\t1\n"
    "s1\t1\tslow\t10.050000\t10.050000\ts1@10.0\tbaseline\t1\n"
)


def _folder(tmp_path: Path, *, manifest: str | None = MANIFEST) -> Path:
    d = tmp_path / "flagged"
    d.mkdir()
    (d / "slices.csv").write_text(SLICES)
    (d / "regions.csv").write_text(REGIONS)
    for sid in ("s1", "s2", "s3"):
        (d / f"{sid}.csv").write_text(EVENTS)
    if manifest is not None:
        (d / mod.MANIFEST).write_text(manifest)
    return d


def test_one_pdf_per_group_and_every_flagged_event_is_drawn_red(tmp_path):
    folder = _folder(tmp_path)
    out = tmp_path / "out"

    written, drawn, expected = mod.draw(folder, out, rows_per_page=12, also=None)

    assert {p.name.split("__")[1] for p in written} == {"MALE.pdf", "DI.pdf"}
    assert all(p.stat().st_size > 0 for p in written)
    # The count that matters: the join reproduces the manifest exactly. A dropped
    # row costs a red mark, and a missing red mark reads as a clean recording.
    assert expected == 3
    assert drawn == expected


def test_a_row_is_a_slice_and_its_height_does_not_move_with_roi_count(tmp_path):
    """Constant row height is the request, so it is asserted, not left to the eye."""
    folder = _folder(tmp_path)
    pages = mod.build_pages(folder, rows_per_page=12)
    assert sorted(pages) == ["DI", "MALE"]
    assert [s.slice_id for s in pages["MALE"][0]] == ["s1", "s2"]
    # Row height is a constant of the module rather than a function of anything —
    # the ROI axis is normalised INTO the band, so it cannot leak into the layout.
    assert isinstance(mod.ROW_INCHES, float)
    assert "ROW_INCHES * len(chunk)" in (ROOT / "tools" / "make_group_raster_summary.py").read_text()


def test_it_refuses_a_folder_with_no_manifest(tmp_path):
    """The excluded folder has no red to draw, and drawing it anyway would lie."""
    folder = _folder(tmp_path, manifest=None)
    with pytest.raises(SystemExit) as e:
        mod.resolve_folder(str(folder))
    msg = str(e.value)
    assert mod.MANIFEST in msg
    assert "STEPS_EXCLUDED" in msg


def test_pagination_splits_rows_without_changing_the_row(tmp_path):
    folder = _folder(tmp_path)
    pages = mod.build_pages(folder, rows_per_page=1)
    assert [[s.slice_id for s in p] for p in pages["MALE"]] == [["s1"], ["s2"]]


@pytest.mark.parametrize("secs,want", [
    (0, "0s"), (45, "45s"), (60, "1m"), (150, "2m30s"), (3600, "60m"),
])
def test_the_time_axis_is_the_repos_time_axis(secs, want):
    """60-base ticks labelled 45s / 2m / 2m30s — never a raw second count."""
    assert mod._fmt_time(secs) == want


@pytest.mark.parametrize("span", [30, 120, 600, 4200, 20000])
def test_tick_step_stays_on_the_60_base_ladder(span):
    step = mod._tick_step(span)
    ladder = {m * (60.0 ** k) for k in range(-1, 4) for m in (1, 2, 5, 10, 15, 30)}
    assert step in ladder
    assert span / step <= 8


def test_the_tool_runs_end_to_end_and_reports_its_join(tmp_path):
    """Exit status is the alarm: a partial join must not exit 0."""
    folder = _folder(tmp_path)
    r = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "make_group_raster_summary.py"),
         "--folder", str(folder), "--out", str(tmp_path / "o")],
        capture_output=True, text=True,
        env={"PATH": "/usr/bin:/bin", "PYTHONPATH": str(ROOT / "src"),
             "HOME": str(tmp_path)},
    )
    assert r.returncode == 0, r.stderr
    assert "381" not in r.stdout          # the real corpus's number, not this fixture's
    assert "3 drawn / 3" in r.stdout
