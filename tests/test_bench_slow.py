"""The slow bench scores SLOW recordings, and nothing in it quietly reaches the fast bench.

``HANDOFF-slow-bench.md`` step 2's trap: re-exporting a ``bench`` function that reads a
module constant scores fast recordings under a slow label, and nothing looks wrong. These
tests fail if a copied name IS the ``bench`` object, and build real slow recordings to check
that what comes out is slow — rates, widths, and the budgets the choosing reads.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from bugarach import bench, bench_slow
from bugarach.simulate import MEASURED_WIDTH_QUANTILES as FAST_WIDTHS

REPO = Path(__file__).resolve().parents[1]

COPIED = ("BENCH_RECORDING", "REGIMES", "NULL_RECORDING", "CROWDED_RECORDING",
          "TAIL_RECORDING", "OPERATING_POINTS", "FULL_GRIDS", "MAX_PROBE_PER_MIN",
          "MAX_FALSE_POSITIVES_PER_HOUR", "MAX_PRECISION_DROP", "MEASURED_RECORD",
          "make_recording", "make_crowded_recording", "make_tail_recording",
          "make_null_recording", "run_detector", "false_positives_per_hour", "evaluate",
          "sweep", "pick_operating_point")


@pytest.mark.parametrize("name", COPIED)
def test_a_stream_dependent_name_is_the_slow_modules_own(name):
    assert getattr(bench_slow, name) is not getattr(bench, name), (
        f"bench_slow.{name} is bench.{name}: a slow run would read fast values")


def test_the_fast_bench_is_untouched_by_the_copy():
    before = dict(bench.OPERATING_POINTS)
    bench_slow.OPERATING_POINTS["__probe__"] = None
    try:
        assert bench.OPERATING_POINTS == before
    finally:
        del bench_slow.OPERATING_POINTS["__probe__"]


def test_the_shared_result_class_reads_a_hot_window_the_slow_bench_also_uses():
    # BenchResult.hot_fa_per_min reads bench.BENCH_RECORDING["hot_window"].
    assert bench_slow.BENCH_RECORDING["hot_window"] == bench.BENCH_RECORDING["hot_window"]


def test_a_slow_recording_runs_at_the_slow_background():
    s, gt = bench_slow.make_null_recording(1)
    n = sum(len(t) for t in s.streams[bench_slow.STREAM].locs)
    rate = n / bench_slow.BENCH_RECORDING["duration_sec"] / bench_slow.BENCH_RECORDING["n_roi"]
    slow_q = bench_slow.NULL_RECORDING["bg_rate_hz"]
    fast_q = bench.NULL_RECORDING["bg_rate_hz"]
    assert abs(rate - slow_q) < abs(rate - fast_q), (rate, slow_q, fast_q)
    assert gt.params["n_roi"] == bench_slow.BENCH_RECORDING["n_roi"]


def test_a_slow_recording_carries_slow_widths():
    s, gt = bench_slow.make_recording("baseline_busy", 2)
    w = np.concatenate([np.asarray(x, float) for x in s.streams[bench_slow.STREAM].width])
    assert gt.params["width_quantiles"] == tuple(bench_slow.MEASURED_WIDTH_QUANTILES)
    # Slow median 2.0 s against fast 0.9 s: the draw sits with the slow table.
    assert abs(np.median(w) - 2.0) < abs(np.median(w) - float(np.median(FAST_WIDTHS)))


def test_the_default_simulator_still_draws_fast_widths():
    s, gt = bench.make_recording("baseline_quiet", 3)
    assert gt.params["width_quantiles"] is None


def test_the_measured_constants_agree_with_the_slow_record():
    rec = json.loads((REPO / bench_slow.MEASURED_RECORD).read_text(encoding="utf-8"))
    assert rec["stream"] == bench_slow.MEASURED_STREAM == "slow"
    for k, v in bench_slow.measured_constants().items():
        row = rec["values"][k]
        assert row["lo"] <= v <= row["hi"], f"{k} = {v} outside {row['lo']:.4f}-{row['hi']:.4f}"
    assert list(bench_slow.MEASURED_WIDTH_QUANTILES) == rec["width_quantiles"]


def test_the_slow_budgets_are_the_measured_ones():
    rec = json.loads((REPO / bench_slow.BUDGETS_RECORD).read_text(encoding="utf-8"))
    rows = rec["rows"]["bugarach.bench_slow"]
    assert set(rows) == set(bench_slow.DETECTORS)
    for d, r in rows.items():
        assert bench_slow.MAX_PROBE_PER_MIN[d] == r["ceiling_probe"], d
        assert bench_slow.MAX_FALSE_POSITIVES_PER_HOUR[d] == r["ceiling_null"], d
        assert bench_slow.MAX_PRECISION_DROP[d] == r["ceiling_swing"], d
        # The starting settings pass the budgets measured at them, or the search cannot start.
        assert r["probe_per_min"] <= r["ceiling_probe"]
        assert r["null_per_hour"] <= r["ceiling_null"]
        assert r["precision_swing"] <= r["ceiling_swing"]


@pytest.mark.parametrize("det", ["loco", "coact"])
def test_the_adopted_slow_settings_pass_the_slow_budgets(det):
    op = bench_slow.OPERATING_POINTS[det]
    assert op.source.startswith("SLOW, adopted")
    assert op is not bench.OPERATING_POINTS[det]
    seeds = tuple(range(49, 61))
    for regime in bench_slow.REGIMES:
        r = bench_slow.evaluate(det, regime, seeds)
        assert r.hot_fa_per_min <= bench_slow.MAX_PROBE_PER_MIN[det], (regime, r.hot_fa_per_min)
    assert (bench_slow.false_positives_per_hour(det, seeds=seeds)
            <= bench_slow.MAX_FALSE_POSITIVES_PER_HOUR[det])


def test_the_fast_operating_points_are_unchanged_by_the_slow_adoption():
    assert bench.OPERATING_POINTS["loco"].params.get("window_mode", "binned") != "sliding"
    assert bench.OPERATING_POINTS["coact"].params.get("min_rois", 3) == 3


def test_choosing_on_the_slow_bench_refuses_a_detector_with_no_slow_budget():
    r = bench.BenchResult(detector="not_a_detector", regime="baseline_quiet")
    with pytest.raises(ValueError, match="measure_slow_budgets"):
        bench_slow.pick_operating_point([r, r])
