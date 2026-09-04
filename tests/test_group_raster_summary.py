"""Per-group, per-treatment rasters: the alignment, the join, and the two inks.

Four claims this figure makes that a reader cannot check by looking, so they are
checked here:

* **t = 0 is the end of that recording's own baseline.** Rows are meant to be read
  down the page against each other, and the alignment is the only thing making
  that legitimate.
* **A red mark means the producer confirmed a field step there.** The join can
  drop rows, and a dropped row costs a mark while the page still looks finished.
* **Row height does not scale with ROI count.** It is constant only if each
  raster carries its own y-dimension — sharing one name links the ranges and
  silently draws every recording against the largest ROI count on the page.
* **A recording on no page is said out loud.** Eight pages look like the corpus.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

pytest.importorskip("holoviews", reason="figure tool; holoviews is the 'ui' extra")

import make_group_raster_summary as mod  # noqa: E402

SLICES = (
    "slice_id,frame_interval_sec,date,mouse_id,group_id,n_roi_recorded\n"
    "s1,0.1,20240101,1,MALE,2\n"
    "s2,0.1,20240102,2,MALE,2\n"
    "s3,0.1,20240103,3,DI,2\n"
    "s4,0.1,20240104,4,MALE,2\n"
)
#: s1/s2 get TTX, s3 senktide, s4 only SB222200 — so s4 lands on no page and the
#: run has to say so rather than leaving it out quietly.
REGIONS = (
    "slice_id,region_idx,label,start_sec,end_sec,analysis_start_sec,analysis_end_sec\n"
    "s1,1,baseline,0,60,0,60\n"
    "s1,2,TTX,60,120,60,120\n"
    "s2,1,baseline,0,30,0,30\n"
    "s2,2,TTX,30,120,30,120\n"
    "s3,1,baseline,0,60,0,60\n"
    "s3,2,senktide,60,120,60,120\n"
    "s4,1,baseline,0,60,0,60\n"
    "s4,2,SB222200,60,120,60,120\n"
)
EVENTS = (
    "roi,time_sec,stream,width_sec,width_def,peak_sec,amp\n"
    "1,10.000000,fast,1.0,halfprom_width_findpeaks_w,10.5,1.0\n"
    "1,70.000000,fast,1.0,halfprom_width_findpeaks_w,70.5,1.0\n"
    "2,10.100000,fast,1.0,halfprom_width_findpeaks_w,10.6,1.0\n"
    "1,10.050000,slow,1.0,rise_interval_peak_minus_t50rise,11.0,1.0\n"
    "2,80.000000,slow,1.0,rise_interval_peak_minus_t50rise,81.0,1.0\n"
)
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
    for sid in ("s1", "s2", "s3", "s4"):
        (d / f"{sid}.csv").write_text(EVENTS)
    if manifest is not None:
        (d / mod.MANIFEST).write_text(manifest)
    return d


def test_one_page_per_group_and_treatment(tmp_path):
    pages, _, skipped = mod.measure(_folder(tmp_path), ("TTX", "senktide"))
    assert sorted(pages) == [("DI", "senktide"), ("MALE", "TTX")]
    assert [s.slice_id for s, _ in pages[("MALE", "TTX")]["members"]] == ["s1", "s2"]
    # s4's only treatment is SB222200, so it is on no page — and named for it.
    assert any(x.startswith("s4 ") for x in skipped)


def test_time_is_re_zeroed_at_each_recordings_own_baseline_end(tmp_path):
    """Different baselines, one origin — which is the whole reason to align."""
    pages, _, _ = mod.measure(_folder(tmp_path), ("TTX",))
    members = dict((sl.slice_id, a) for sl, a in pages[("MALE", "TTX")]["members"])
    assert members["s1"] == 60.0 and members["s2"] == 30.0

    sl = next(s for s, _ in pages[("MALE", "TTX")]["members"] if s.slice_id == "s2")
    shifted = mod._shift_stream(sl.streams["fast"], 30.0)
    # the 70 s event sits 40 s into treatment on s2, and 10 s into it on s1
    assert 40.0 in np.concatenate([np.asarray(v) for v in shifted.t50rise])
    # nothing but the times moved
    assert shifted.width_def == sl.streams["fast"].width_def
    assert shifted.n_rois == sl.streams["fast"].n_rois


def test_every_flagged_event_is_drawn_in_the_second_ink(tmp_path):
    folder = _folder(tmp_path)
    pages, manifest, _ = mod.measure(folder, ("TTX",))
    spec = pages[("MALE", "TTX")]
    _, red = mod.build_page(spec["members"], ext=spec["ext"], manifest=manifest,
                            width=600)
    assert red == 3 == sum(len(v) for v in manifest.values())


def test_each_raster_carries_its_own_y_dimension(tmp_path):
    """Shared names link y-ranges, which is how constant row height stops being
    constant in the only sense that matters — the ink inside it."""
    folder = _folder(tmp_path)
    pages, manifest, _ = mod.measure(folder, ("TTX",))
    spec = pages[("MALE", "TTX")]
    blocks, _ = mod.build_page(spec["members"], ext=spec["ext"], manifest=manifest,
                               width=600)
    # One name PER PANEL is expected and required — the invisible `_base` point
    # shares it deliberately, so that the panel has a y-dimension at all. What
    # must not repeat is the name ACROSS panels.
    per_panel = []
    for _, panels in blocks:
        for p in panels:
            names = {d.name for el in p for d in el.vdims}
            assert len(names) == 1, f"panel mixes y-dimensions: {names}"
            per_panel.append(names.pop())
    assert len(set(per_panel)) == len(per_panel), f"y-dimension reused: {per_panel}"


def test_only_the_last_panel_keeps_an_x_axis(tmp_path):
    """One x-axis per linked group, bottom row only (CLAUDE.md)."""
    folder = _folder(tmp_path)
    pages, manifest, _ = mod.measure(folder, ("TTX",))
    spec = pages[("MALE", "TTX")]
    blocks, _ = mod.build_page(spec["members"], ext=spec["ext"], manifest=manifest,
                               width=600)
    flat = [p for _, panels in blocks for p in panels]
    assert all(p.opts.get("plot").kwargs.get("xaxis") is None for p in flat[:-1])
    # The bottom row never sets `xaxis` at all — it keeps holoviews' default,
    # which is to draw one. Absent and None are different states here.
    assert "xaxis" not in flat[-1].opts.get("plot").kwargs


def test_it_refuses_a_folder_with_no_manifest(tmp_path):
    """The excluded folder has no red to draw, and drawing it anyway would lie."""
    with pytest.raises(SystemExit) as e:
        mod.resolve_folder(str(_folder(tmp_path, manifest=None)))
    msg = str(e.value)
    assert mod.MANIFEST in msg and "STEPS_EXCLUDED" in msg


def test_a_recording_with_no_baseline_is_skipped_not_drawn_at_zero(tmp_path):
    """No anchor means no honest x — dropping it beats aligning it on nothing."""
    d = _folder(tmp_path)
    (d / "regions.csv").write_text(
        "slice_id,region_idx,label,start_sec,end_sec,"
        "analysis_start_sec,analysis_end_sec\n"
        "s1,1,TTX,0,120,0,120\n")
    pages, _, skipped = mod.measure(d, ("TTX",))
    assert pages == {} or ("MALE", "TTX") not in pages
    assert any("no baseline region" in s for s in skipped)
