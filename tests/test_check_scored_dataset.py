"""The startup check that flags results scored on anything but the default dataset.

Tony, 2026-09-21: *"benchmarks derived from an older data set should be flagged."*
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "check_scored_dataset", ROOT / "tools" / "check_scored_dataset.py")
csd = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(csd)

DEFAULT = "2099-01-01_the_default"
EVALS = frozenset({"another_lab"})


def _write(tmp_path, name, doc):
    p = tmp_path / name
    p.write_text(json.dumps(doc), encoding="utf-8")
    return p


def test_each_shape_of_provenance_is_classified(tmp_path):
    cases = {
        "stamped.json": ({"dataset": {"name": DEFAULT, "role": "x"}}, "current"),
        "older.json": ({"dataset": {"name": "2000-01-01_older"}}, "older"),
        "legacy_folder.json": ({"folder": "2000-01-01_older"}, "older"),
        "legacy_folder_current.json": ({"folder": DEFAULT}, "current"),
        "store.json": ({"store": "event_store_whatever"}, "store"),
        "nested_store.json": ({"provenance": {"store": "event_store_x"}}, "store"),
        "eval.json": ({"store": "another_lab"}, "eval"),
        "silent.json": ({"f1": 0.5}, "unstamped"),
        "a_list.json": ([1, 2, 3], "unstamped"),
    }
    for name, (doc, want) in cases.items():
        got, _ = csd.classify(_write(tmp_path, name, doc), DEFAULT, EVALS)
        assert got == want, f"{name}: {got} != {want}"


def test_a_stamp_from_the_resolver_reads_as_current(tmp_path):
    from bugarach import dataset
    p = _write(tmp_path, "r.json", {"dataset": dataset.stamp(), "f1": 0.9})
    assert csd.classify(p, dataset.current_name("default"))[0] == "current"


def test_figure_specs_are_not_results(tmp_path):
    _write(tmp_path, "architecture.spec.json", {})
    _write(tmp_path, "real.json", {})
    assert [p.name for p in csd.results(tmp_path)] == ["real.json"]


def test_the_briefing_line_is_one_line_and_never_fails_the_hook():
    out = subprocess.run([sys.executable, str(ROOT / "tools" / "check_scored_dataset.py"),
                          "--brief"], capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr
    assert len(out.stdout.strip().splitlines()) == 1, out.stdout
    assert "results on it" in out.stdout
    assert len(out.stdout.strip()) <= 30, "it is appended to a budgeted briefing line"
