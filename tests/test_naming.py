"""Output filenames follow the estate scheme, so a page cannot leave the lab as `ALL_..._combined.html`.

On 2026-10-06 a page from `make_group_raster_summary.py` went outside the lab named
`ALL_APV+CNQX+GZ_combined.html`. `ALL` meant "every group, as separate rows", `combined` meant
a stream, and the name had no type, no window and no date. The scheme and its builder are
vendored from syncytium2/armory into `tools/naming/`. These tests check two things: the copy
still works here, and the raster tool's names come from it.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from naming import artifact_name  # noqa: E402


def test_the_vendored_builder_passes_its_own_selftest():
    out = subprocess.run([sys.executable, str(ROOT / "tools/naming/artifact_name.py"),
                          "--selftest"], capture_output=True, text=True)
    assert out.stdout.strip().splitlines()[-1] == "selftest: PASS", out.stdout + out.stderr


def test_tuesdays_name_is_refused():
    with pytest.raises(artifact_name.NameError_):
        artifact_name.check(artifact_name.load_codes(), "ALL_APV+CNQX+GZ_combined.html")


pytest.importorskip("holoviews", reason="figure tool; holoviews is the 'ui' extra")

import make_group_raster_summary as mod  # noqa: E402

MAIN = {"signal": "roi", "win": "long_window_20", "source": None}


def rec(group):
    return SimpleNamespace(meta={"group_id": group}), None


def test_a_group_page_is_named_by_its_fields():
    name = mod.page_filename(MAIN, "MALE", "TTX", "fast", [rec("MALE")], date="20261007")
    assert name == "raster_roi_fast_ttx_male_win20min_20261007.html"


def test_an_all_groups_page_names_the_groups_on_it_in_display_order():
    members = [rec("ORX"), rec("DI"), rec("MALE"), rec("DI")]
    facts = {"signal": "roi", "win": "win20min", "source": "pilot-20260811"}
    name = mod.page_filename(facts, mod.ALL_GROUPS, "APV+CNQX+GZ", "combined", members,
                             date="20261006")
    assert name == ("pilot-20260811_raster_roi_combined_apv+cnqx+gz_di-male-orx_"
                    "win20min_20261006.html")
    assert "all" not in name.split("_")


def test_a_label_with_no_code_is_refused_not_guessed():
    with pytest.raises(artifact_name.NameError_):
        mod.page_filename(MAIN, "UNGROUPED", "TTX", "fast", [rec(None)], date="20261007")
    with pytest.raises(artifact_name.NameError_):
        mod.page_filename(MAIN, "DI", "aspirin", "fast", [rec("DI")], date="20261007")


def test_facts_come_from_the_folders_table_and_a_flag_overrides(monkeypatch, tmp_path):
    from bugarach import dataset

    folder = tmp_path / "an_export"
    folder.mkdir()
    monkeypatch.setattr(dataset, "declared_exports", lambda: {
        "x": {"name": "an_export", "signal": "roi", "win": "win20min"}})
    assert mod.naming_facts(folder, {}) == {"signal": "roi", "win": "win20min", "source": None}
    assert mod.naming_facts(folder, {"signal": "pensub"})["signal"] == "pensub"


def test_an_undeclared_folder_must_say_everything_including_that_it_is_not_a_pilot(
        monkeypatch, tmp_path):
    from bugarach import dataset

    folder = tmp_path / "a_pilot_passed_by_path"
    folder.mkdir()
    monkeypatch.setattr(dataset, "declared_exports", lambda: {})
    with pytest.raises(SystemExit, match="source"):
        mod.naming_facts(folder, {"signal": "roi", "win": "win20min"})
    assert mod.naming_facts(folder, {"signal": "roi", "win": "win20min",
                                     "source": "none"})["source"] is None
