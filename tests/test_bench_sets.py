"""A bench set is its stream's bench with one record's values, and nothing else moves.

``bugarach.bench_sets`` (Tony, 2026-11-12: one synthetic set for both groups and one per group).
No data needed: the records are in the repository and every recording here is simulated.
"""
from __future__ import annotations

import copy
import subprocess
import sys

import pytest

from bugarach import bench, bench_combined, bench_sets, bench_slow
from bugarach import stream_profile as sp

NAMES = bench_sets.names()
STREAM_MODULES = {"fast": bench, "slow": bench_slow, "combined": bench_combined}


def test_there_is_a_set_for_every_stream():
    assert {bench_sets.stream_of(n) for n in NAMES} == set(STREAM_MODULES)


@pytest.mark.parametrize("name", NAMES)
def test_a_set_carries_its_records_values(name):
    rec, m = bench_sets.record(name), bench_sets.load(name)
    v = rec["values"]
    r = m.BENCH_RECORDING
    assert r["n_roi"] == round(v["n_roi"]["measured"])
    assert r["participation"][1] == pytest.approx(v["participation"]["measured"])
    assert r["jitter_sec"] == pytest.approx(v["jitter_sec"]["measured"])
    assert m.REGIMES["baseline_quiet"]["bg_rate_hz"] == pytest.approx(
        v["regime_quiet_hz"]["measured"])
    assert m.REGIMES["baseline_busy"]["bg_rate_hz"] == pytest.approx(
        v["regime_busy_hz"]["measured"])
    assert m.NULL_RECORDING["bg_rate_hz"] == m.REGIMES["baseline_quiet"]["bg_rate_hz"]
    assert m.ELEVATED_RATE_RECORDING["hot_rate_hz"] == pytest.approx(rec["elevated_rate_hz"])
    assert m.MEASURED_STREAM == rec["stream"]
    # What the module says it measured is what the record says, key for key.
    for key, value in m.measured_constants().items():
        assert value == pytest.approx(v[key]["measured"]), key
    # The derived recordings moved with it.
    for other in (m.CROWDED_RECORDING, m.TAIL_RECORDING):
        assert other["n_roi"] == r["n_roi"] and other["jitter_sec"] == r["jitter_sec"]


@pytest.mark.parametrize("name", NAMES)
def test_the_outer_participation_levels_keep_the_stream_benchs_ratios(name):
    m = bench_sets.load(name)
    base = STREAM_MODULES[m.MEASURED_STREAM].BENCH_RECORDING["participation"]
    got = m.BENCH_RECORDING["participation"]
    for i in (0, 2):
        want = min(bench_sets.MAX_PARTICIPATION, got[1] * base[i] / base[1])
        assert got[i] == pytest.approx(want)


def test_building_the_sets_does_not_move_a_stream_bench():
    before = {k: (copy.deepcopy(m.BENCH_RECORDING), copy.deepcopy(m.REGIMES),
                  copy.deepcopy(m.ELEVATED_RATE_RECORDING), m.MEASURED_RATE_SHAPE)
              for k, m in STREAM_MODULES.items()}
    for name in NAMES:
        bench_sets.load(name).make_recording("baseline_quiet", 1)
    after = {k: (m.BENCH_RECORDING, m.REGIMES, m.ELEVATED_RATE_RECORDING, m.MEASURED_RATE_SHAPE)
             for k, m in STREAM_MODULES.items()}
    assert before == after


@pytest.mark.parametrize("name", NAMES)
def test_a_set_plants_its_own_gaps_and_count_and_no_decoys(name):
    rec, m = bench_sets.record(name), bench_sets.load(name)
    old = bench.spacing()
    try:
        bench.use_spacing("realistic")
        _, gt = m.make_recording("baseline_busy", 3)
        want = round(rec["events"]["events_per_hour"] * m.BENCH_RECORDING["duration_sec"] / 3600)
        assert len(gt.events) == want
        assert len(gt.distractors) == 0                       # ADR-0019
        assert gt.params["gap_source"]["source"] == f"{name}.json"
        bench.use_spacing("bench")
        _, gt = m.make_recording("baseline_busy", 3)
        assert len(gt.events) == sum(m.BENCH_RECORDING["n_per_level"])
    finally:
        bench.use_spacing(old)


def test_a_set_is_reached_by_name_in_a_new_process():
    """The search passes its bench to workers by module name; Windows spawns them."""
    name = NAMES[0]
    code = ("import importlib; m = importlib.import_module("
            f"'bugarach.bench_sets.{name}'); print(m.SET, m.BENCH_RECORDING['n_roi'])")
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert out.stdout.split()[0] == name


def test_the_stream_profile_takes_a_set_by_name():
    name = next(n for n in NAMES if bench_sets.stream_of(n) == "fast")
    p = sp.profile(name)
    assert p.module is bench_sets.load(name)
    assert p.decoys == 0
    assert p.source().jitter_sec == pytest.approx(
        bench_sets.record(name)["values"]["jitter_sec"]["measured"])


def test_an_unknown_set_is_refused_by_name():
    with pytest.raises(ModuleNotFoundError, match="no bench set"):
        bench_sets.load("fast_nobody")
