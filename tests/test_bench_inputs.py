"""ADR-0012's bench-inputs folder: the switch that builds the bench from it, and the extraction."""
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from bugarach import bench  # noqa: E402

import extract_bench_inputs as ex  # noqa: E402


@pytest.fixture
def realistic(monkeypatch):
    monkeypatch.setenv(bench.SPACING_ENV, "realistic")
    monkeypatch.delenv(bench.INPUTS_ENV, raising=False)


def test_unset_the_bench_reads_its_committed_inputs_and_its_own_constants(realistic):
    o = bench.spacing_overrides("fast", bench.BENCH_RECORDING)
    assert bench.inputs_run() == bench.INTERVALS_RUN
    assert "participation" not in o and "jitter_sec" not in o
    assert o["n_per_level"] == bench.realistic_counts("fast", 3, bench.BENCH_RECORDING["duration_sec"])


def test_a_folder_supplies_gaps_counts_participation_and_jitter(realistic, monkeypatch, tmp_path):
    for f in ("summary.json", "gaps_for_generator.json"):
        shutil.copy(bench.INTERVALS_RUN / f, tmp_path / f)
    rec = json.loads((tmp_path / "summary.json").read_text())
    rec["summary"]["fast"]["all"]["events_per_hour"] = 20.0          # 15 events in 45 minutes
    (tmp_path / "summary.json").write_text(json.dumps(rec))
    (tmp_path / "bench_inputs.json").write_text(json.dumps(
        {"streams": {"fast": {"participation": [0.5, 0.3, 0.15], "jitter_sec": 0.33}}}))
    monkeypatch.setenv(bench.INPUTS_ENV, str(tmp_path))
    o = bench.spacing_overrides("fast", bench.BENCH_RECORDING)
    assert o["participation"] == (0.5, 0.3, 0.15) and o["jitter_sec"] == 0.33
    assert sum(o["n_per_level"]) == 15
    # A stream the file does not name keeps the bench's own participation and jitter.
    assert "participation" not in bench.spacing_overrides("slow", bench.BENCH_RECORDING)


def test_the_bench_spacing_is_untouched_by_the_folder(monkeypatch, tmp_path):
    monkeypatch.setenv(bench.SPACING_ENV, "bench")
    monkeypatch.setenv(bench.INPUTS_ENV, str(tmp_path))
    assert bench.spacing_overrides("fast", bench.BENCH_RECORDING) == {}


def test_gaps_run_call_start_to_call_start_within_a_window():
    calls = [dict(slice_id="a", region_idx=1, stream="fast", onset_sec=t) for t in (50.0, 10.0, 30.0)]
    calls.append(dict(slice_id="a", region_idx=2, stream="fast", onset_sec=100.0))
    assert sorted(g["gap_sec"] for g in ex.gaps_of(calls)) == [20.0, 20.0]


def test_spread_is_the_sd_of_first_onsets_inside_the_call():
    trains = [np.array([10.0, 10.5]), np.array([11.0]), np.array([30.0])]
    assert ex.spread_of(trains, 10.0, 1.0) == pytest.approx(np.std([10.0, 11.0]))
    assert ex.spread_of(trains, 30.0, 0.0) is None            # one participant has no spread


def test_outer_levels_keep_the_benchs_ratios_and_are_capped():
    cur = bench.BENCH_RECORDING["participation"]
    got = ex.levels("fast", cur[1])
    assert got == pytest.approx([round(x, 4) for x in cur])
    assert max(ex.levels("fast", 0.9)) == 0.95
