"""``tools/score_bench_candidates.py`` reads a search per bench, or per detector, for the benches asked.

The final-parameters night (2026-09-25) searched slow and combined one detector per process
(``search_all_settings.py --only``), so each detector's record is its own folder, and phase 3 for
those two streams ran before fast's searches existed.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

import score_bench_candidates as sbc  # noqa: E402


def _record(folder: Path, marker: str) -> None:
    folder.mkdir(parents=True)
    (folder / "search.json").write_text(json.dumps({"marker": marker}), encoding="utf-8")


def test_a_search_per_bench_is_read_for_every_detector(tmp_path):
    _record(tmp_path / "search-coact-slow", "bench")
    for det in ("coact", "loco"):
        got = sbc.load_search(tmp_path, "search-coact-{bench}", "slow", det)
        assert got["marker"] == "bench"


def test_a_search_per_detector_is_read_from_its_own_folder(tmp_path):
    _record(tmp_path / "search-slow" / "coact", "slow-coact")
    _record(tmp_path / "search-slow" / "loco", "slow-loco")
    assert sbc.load_search(tmp_path, "search-{bench}/{det}", "slow", "coact")["marker"] == "slow-coact"
    assert sbc.load_search(tmp_path, "search-{bench}/{det}", "slow", "loco")["marker"] == "slow-loco"


def test_a_missing_search_is_an_error_not_a_skip(tmp_path):
    with pytest.raises(FileNotFoundError):
        sbc.load_search(tmp_path, "search-{bench}/{det}", "fast", "coact")


def test_an_unknown_bench_is_refused(tmp_path):
    with pytest.raises(SystemExit):
        sbc.main(["--phase2", str(tmp_path), "--out", str(tmp_path / "o"), "--benches", "medium"])
