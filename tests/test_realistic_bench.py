"""The realistic bench (ADR-0010 part 2, rulings 1 and 2): off unless named, byte-identical
otherwise, planted gaps and counts from the committed measurement, fast's seeds doubled, floors on
every recording, and the close-events rules retired only there.

The old benches' byte-identity is pinned by ``tests/test_real_intervals_off_by_default.py``
(60 recording hashes); the tests here check that nothing in this change turns the spacing on.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

from bugarach import bench, bench_combined, bench_slow

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

BENCHES = [(bench, "fast"), (bench_slow, "slow"), (bench_combined, "combined")]


@pytest.fixture
def spacing(monkeypatch):
    def use(name):
        monkeypatch.setenv(bench.SPACING_ENV, name)
    monkeypatch.delenv(bench.SPACING_ENV, raising=False)
    return use


def test_the_spacing_is_the_old_one_unless_named(spacing):
    assert bench.spacing() == "bench"
    for b, s in BENCHES:
        assert bench.spacing_overrides(s, b.BENCH_RECORDING) == {}
        _, gt = b.make_recording("baseline_quiet", 1)
        assert "gap_source" not in gt.params
        assert gt.params["n_per_level"] == b.BENCH_RECORDING["n_per_level"]
        assert np.diff(np.sort(gt.times)).min() >= b.BENCH_RECORDING["min_sep_sec"]


def test_an_unknown_spacing_is_refused(spacing):
    spacing("dense")
    with pytest.raises(ValueError, match="not one of"):
        bench.spacing()
    with pytest.raises(ValueError):
        bench.use_spacing("dense")


@pytest.mark.parametrize("b,stream", BENCHES, ids=[s for _, s in BENCHES])
def test_the_realistic_bench_draws_gaps_and_counts_from_the_committed_measurement(spacing, b,
                                                                                    stream):
    spacing("realistic")
    _, gt = b.make_recording("baseline_busy", 2)
    src = gt.params["gap_source"]
    assert src["pool"] == "pooled" and src["source"] == "gaps_for_generator.json"
    assert gt.params["gap_mix"] == 0.0 and gt.params["n_gaps_old_rule"] == 0
    expected = {"fast": 7, "slow": 17, "combined": 19}[stream]    # measured events per hour x 0.75 h
    assert len(gt.events) == sum(gt.params["n_per_level"]) == expected
    assert gt.params["duration_sec"] == b.BENCH_RECORDING["duration_sec"] == 2700.0
    # Every gap is one of the measured gaps (the generator resamples them, never rescales).
    from bugarach.real_intervals import load_gaps
    pool = set(np.round(load_gaps(stream, path=bench.INTERVALS_RUN / "gaps_for_generator.json")
                        .gaps_sec, 6))
    got = np.round(np.diff(np.sort(gt.times)), 6)
    assert all(g in pool for g in got)


def test_the_orx_bench_draws_from_orx_gaps(spacing):
    spacing("orx")
    _, gt = bench_slow.make_recording("baseline_quiet", 1)
    assert gt.params["gap_source"]["pool"] == "ORX"


@pytest.mark.parametrize("b,stream", BENCHES, ids=[s for _, s in BENCHES])
def test_every_realistic_recording_carries_its_floor(spacing, b, stream):
    if not bench.floor_enabled():
        pytest.skip("floor switched off for this run")
    spacing("realistic")
    s, gt = b.make_recording("baseline_quiet", 1)
    assert gt.params["event_floor"] == bench.recording_floor(s, b.STREAM).floor >= 3


def test_seeds_are_doubled_on_fast_only_and_only_under_a_realistic_spacing(spacing):
    import score_bench_candidates as sbc

    assert [bench.seed_factor(s) for s in ("fast", "slow", "combined")] == [1, 1, 1]
    assert len(sbc.seeds_for("fast")) == 24 and len(sbc.nulls_for("fast")) == 12
    for name in ("realistic", "orx"):
        spacing(name)
        assert [bench.seed_factor(s) for s in ("fast", "slow", "combined")] == [2, 1, 1]
        assert sbc.seeds_for("fast") == tuple(range(6000, 6048))
        assert sbc.nulls_for("fast") == tuple(range(6000, 6024))
        assert sbc.seeds_for("slow") == tuple(range(6000, 6024))


def test_the_search_doubles_fast_seeds_and_drops_the_crowded_veto_under_realistic(spacing,
                                                                                 monkeypatch,
                                                                                 tmp_path):
    import search_all_settings as sas

    captured = {}

    def stop(*a, **k):                 # stop main just after its argument handling
        raise SystemExit(0)

    monkeypatch.setattr(sas, "shipped_value", lambda d, k: stop())
    for argv, seeds, veto in ((["--bench", "fast"], 48, True),
                              (["--bench", "fast", "--spacing", "realistic"], 96, False),
                              (["--bench", "slow", "--spacing", "realistic"], 48, False)):
        orig = sas.argparse.ArgumentParser.parse_args

        def spy(self, args=None, namespace=None, _orig=orig):
            ns = _orig(self, args, namespace)
            captured["ns"] = ns
            return ns
        monkeypatch.setattr(sas.argparse.ArgumentParser, "parse_args", spy)
        with pytest.raises(SystemExit):
            sas.main(argv + ["--out", str(tmp_path / "search")])
        ns = captured["ns"]
        assert ns.seeds == seeds and (not ns.no_crowded_veto) == veto
        monkeypatch.delenv(bench.SPACING_ENV, raising=False)
    sas.use_bench("fast")


def test_the_context_rule_is_retired_only_under_a_realistic_spacing(spacing):
    wide = {"context_win_sec": 240.0}
    assert not bench.context_fits_the_null(wide, 120.0)
    spacing("realistic")
    assert bench.context_fits_the_null(wide, 120.0)


def test_the_paired_difference_is_seed_by_seed():
    import score_bench_candidates as sbc

    ref = np.array([0.5, 0.6, 0.7, np.nan])
    f1 = np.array([0.6, 0.7, 0.8, 0.9])
    d = sbc.paired_difference(f1, ref)
    assert d["mid"] == pytest.approx(0.1) and d["lo"] == pytest.approx(0.1)
    assert d["hi"] == pytest.approx(0.1) and d["n_seeds"] == 3 and d["n_dropped"] == 1
    assert sbc.paired_difference(np.array([np.nan]), np.array([0.5]))["mid"] is None


def test_the_call_measure_check_bins_by_the_nearest_neighbour():
    import check_call_measure as ccm

    assert [ccm.gap_bin(g) for g in (3.0, 10.0, 29.9, 30.0, float("inf"))] == [
        "under 10 s", "10 to 30 s", "10 to 30 s", "over 30 s", "over 30 s"]
    rows = [dict(stream="fast", gap_bin="under 10 s", error=e) for e in (0, 0, 1, 3)]
    s = ccm.summarise(rows)["fast"]["under 10 s"]
    assert s["events"] == 4 and s["share_exact"] == 0.5 and s["share_within_1"] == 0.75
