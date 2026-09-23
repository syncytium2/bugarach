"""The ROI table by group and treatment: it is derived, not typed.

Tony asked for this table on 2026-09-22 and, on 2026-09-23, that it be
reproducible — the export folder moves under a table typed once. Three claims
that a reader of the table cannot check by looking:

* **Each recording is listed once, not once per stream.** The raster pages it
  borrows its membership from have one page per stream, so the obvious loop
  lists every recording twice with the same ROI count.
* **A recording is listed under its FIRST treatment only.** That rule has
  already been got wrong once in this tree, and it decides the column a
  recording lands in.
* **The table says which folder it came from.** Two copies built from different
  exports are otherwise indistinguishable, which is the failure this tool exists
  to prevent.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

pytest.importorskip("holoviews", reason="imports the figure tool; holoviews is the 'ui' extra")

import make_roi_table as mod  # noqa: E402

from test_group_raster_summary import EVENTS, REGIONS  # noqa: E402

#: s1/s2 (MALE) get TTX, s3 (DI) senktide, s4 only SB222200 — so s4 is listed
#: nowhere. ROI counts differ per recording so a mixed-up join is visible.
SLICES = (
    "slice_id,frame_interval_sec,date,mouse_id,group_id,n_roi_recorded\n"
    "s1,0.1,20240101,1,MALE,11\n"
    "s2,0.1,20240102,2,MALE,23\n"
    "s3,0.1,20240103,3,DI,17\n"
    "s4,0.1,20240104,4,MALE,99\n"
)

STAMP = {"role": "test", "name": "a_folder", "recordings": 4, "use": "input"}


def _folder(tmp_path: Path) -> Path:
    d = tmp_path / "steps_excluded"
    d.mkdir()
    (d / "slices.csv").write_text(SLICES)
    (d / "regions.csv").write_text(REGIONS)
    for sid in ("s1", "s2", "s3", "s4"):
        (d / f"{sid}.csv").write_text(EVENTS)
    return d


def test_each_recording_is_listed_once_with_the_producers_roi_count(tmp_path):
    """Once per recording — NOT once per stream, which is how the pages are keyed."""
    table, skipped = mod.measure(_folder(tmp_path), ("senktide", "TTX"))
    assert table[("MALE", "TTX")] == [("s1", 11), ("s2", 23)]
    assert table[("DI", "senktide")] == [("s3", 17)]
    # s4's only treatment is SB222200: on no page, in no column, and said out loud.
    assert ("MALE", "senktide") not in table
    assert any(x.startswith("s4 ") for x in skipped)


def test_the_groups_come_out_in_the_one_declared_order(tmp_path):
    """DI, OVX, MALE, ORX — `bugarach.groups`, not alphabetical (Tony, 2026-09-23)."""
    table, _ = mod.measure(_folder(tmp_path), ("senktide", "TTX"))
    assert mod.ordered_groups(table) == ["DI", "MALE"]


def test_the_written_table_names_the_folder_it_was_built_from(tmp_path):
    """A table that cannot say which export it describes cannot be checked."""
    table, skipped = mod.measure(_folder(tmp_path), ("senktide", "TTX"))
    dest = tmp_path / "out"
    mod.write(dest, table, ("senktide", "TTX"), STAMP, skipped)

    md = (dest / "roi_table.md").read_text(encoding="utf-8")
    assert "a_folder" in md
    assert "| **DI** | s3 | 17 |  |  |" in md
    assert "| **MALE** |  |  | s1 | 11 |" in md

    rows = list(csv.DictReader((dest / "roi_table.csv").open(encoding="utf-8")))
    assert [r["slice_id"] for r in rows] == ["s3", "s1", "s2"]
    assert [r["n_roi_recorded"] for r in rows] == ["17", "11", "23"]

    record = json.loads((dest / "roi_table.json").read_text(encoding="utf-8"))
    assert record["dataset"] == STAMP
    assert len(record["rows"]) == 3
    assert record["not_listed"]


def test_a_summary_line_counts_what_its_own_block_holds(tmp_path):
    """The per-group line is derived from the rows above it, never carried over."""
    table, skipped = mod.measure(_folder(tmp_path), ("senktide", "TTX"))
    md = mod.markdown(table, ("senktide", "TTX"), STAMP)
    assert "| *MALE summary* | *none* |  | *2 slices* | *median 17 ROIs* |" in md
    assert "| **All groups** | **1 slice** | **17-17 ROIs** | **2 slices** | **11-23 ROIs** |" in md
