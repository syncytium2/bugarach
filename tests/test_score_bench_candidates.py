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


def test_searches_are_read_in_place_from_several_roots(tmp_path):
    """The full-panel night: fast searched on WSMIP064, slow and combined on WSMIP065."""
    _record(tmp_path / "064" / "search-fast" / "coact", "064-fast")
    _record(tmp_path / "065" / "search-slow" / "coact", "065-slow")
    roots = [tmp_path / "064", tmp_path / "065"]
    assert sbc.load_search(roots, "search-{bench}/{det}", "fast", "coact")["marker"] == "064-fast"
    assert sbc.load_search(roots, "search-{bench}/{det}", "slow", "coact")["marker"] == "065-slow"
    with pytest.raises(FileNotFoundError):
        sbc.load_search(roots, "search-{bench}/{det}", "combined", "coact")


def test_the_same_search_under_two_roots_is_an_error_not_a_choice(tmp_path):
    _record(tmp_path / "064" / "search-slow" / "coact", "064")
    _record(tmp_path / "065" / "search-slow" / "coact", "065")
    with pytest.raises(ValueError, match="more than one"):
        sbc.load_search([tmp_path / "064", tmp_path / "065"], "search-{bench}/{det}", "slow",
                        "coact")


def test_every_model_the_training_tool_trains_is_scored():
    import train_learned_on_bench as T

    assert sbc.MODELS is T.MODELS and len(sbc.MODELS) == 8


def _row(seed):
    return json.dumps(dict(seed=seed, path=f"m_slow_seed{seed}.json", mean=0.5, null_per_hour=0.0))


def test_a_log_opening_with_a_byte_order_mark_keeps_its_first_seed(tmp_path):
    """2026-09-26: every training log PowerShell wrote opened with a BOM, and seed 0 was lost."""
    log = tmp_path / "train-m-slow.log"
    log.write_text("\n".join([_row(0), _row(1), "best: m_slow_seed0.json mean F1 0.5"]) + "\n",
                   encoding="utf-8-sig")
    assert log.read_bytes()[:3] == b"\xef\xbb\xbf"
    assert [r["seed"] for r in sbc.train_rows(log)] == [0, 1]


def test_a_best_seed_missing_from_the_rows_is_an_error(tmp_path):
    log = tmp_path / "train-m-slow.log"
    log.write_text("\n".join(["noise" + _row(0), _row(1), "best: m_slow_seed0.json"]) + "\n",
                   encoding="utf-8")
    with pytest.raises(ValueError, match="not among the rows"):
        sbc.train_rows(log)


def test_a_run_with_no_seed_in_budget_has_no_pick():
    rows = [dict(path="a", mean=0.9, null_per_hour=3.0), dict(path="b", mean=0.5, null_per_hour=0.5)]
    assert sbc.picked(rows, 1.0)["path"] == "b"
    assert sbc.picked(rows, 0.1) is None


def test_phase2_repeats_and_every_root_reaches_the_scorer(tmp_path, monkeypatch):
    """Run main as far as it reads the searches, with two roots, and check each was consulted."""
    seen = []

    def spy(phase2, pattern, bench, det):
        seen.append(list(phase2))
        raise SystemExit(0)

    monkeypatch.setattr(sbc, "load_search", spy)
    with pytest.raises(SystemExit):
        sbc.main(["--phase2", str(tmp_path / "064"), "--phase2", str(tmp_path / "065"),
                  "--out", str(tmp_path / "o"), "--benches", "slow"])
    assert seen == [[tmp_path / "064", tmp_path / "065"]]


def test_an_unknown_bench_is_refused(tmp_path):
    with pytest.raises(SystemExit):
        sbc.main(["--phase2", str(tmp_path), "--out", str(tmp_path / "o"), "--benches", "medium"])
