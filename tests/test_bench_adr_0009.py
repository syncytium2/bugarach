"""ADR-0009 decision 1 on the fast, slow and combined benches: the elevated-rate test in a recording
of its own.

* no recording with planted events carries the stretch, and its length and event spacing did not
  move with it;
* the elevated-rate recording has the stretch and nothing planted, on its own seed range;
* the probe that gates selection is read off that recording, and a probe nobody ran fails the gates
  instead of reading zero and passing them.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pytest

from bugarach import bench, bench_combined, bench_slow

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

import search_all_settings as sas  # noqa: E402

BENCHES = [bench, bench_slow, bench_combined]
IDS = ["fast", "slow", "combined"]


@pytest.mark.parametrize("b", BENCHES, ids=IDS)
@pytest.mark.parametrize("which", ["BENCH_RECORDING", "CROWDED_RECORDING", "TAIL_RECORDING"])
def test_no_recording_with_planted_events_carries_the_stretch(b, which):
    spec = getattr(b, which)
    assert spec["hot_window"] is None, which
    assert spec["n_per_level"] != (0, 0, 0), which


@pytest.mark.parametrize("b", BENCHES, ids=IDS)
def test_the_planted_recordings_keep_their_length_and_spacing(b):
    assert b.BENCH_RECORDING["duration_sec"] == 2700.0
    assert b.BENCH_RECORDING["min_sep_sec"] == 120.0
    assert b.BENCH_RECORDING["n_per_level"] == (5, 5, 5)
    _, gt = b.make_recording("baseline_quiet", 1)
    assert gt.params["hot_window"] is None
    assert len(gt.events) == 15
    assert np.diff(np.sort(gt.times)).min() >= 120.0


@pytest.mark.parametrize("b", BENCHES, ids=IDS)
def test_the_span_that_held_the_stretch_now_carries_ordinary_background(b):
    """Same seed with and without the old stretch: the busy span is gone from the recording."""
    s, _ = b.make_recording("baseline_quiet", 3)
    counts = np.array([np.sum((np.asarray(t) >= 1200) & (np.asarray(t) < 1500))
                       for t in s.streams[b.STREAM].t50rise])
    rate = counts.sum() / 300.0 / len(counts)
    stretch = b.ELEVATED_RATE_RECORDING["hot_rate_hz"]
    assert rate < stretch / 2, (rate, stretch)


@pytest.mark.parametrize("b", BENCHES, ids=IDS)
@pytest.mark.parametrize("regime", ["baseline_quiet", "baseline_busy"])
def test_the_elevated_rate_recording_has_the_stretch_and_nothing_planted(b, regime):
    _, gt = b.make_elevated_rate_recording(regime, 1)
    assert not gt.events and not gt.distractors
    assert gt.params["hot_window"] == (1200.0, 1500.0)
    assert gt.params["hot_rate_hz"] == b.ELEVATED_RATE_RECORDING["hot_rate_hz"] > 0
    assert gt.params["duration_sec"] == b.BENCH_RECORDING["duration_sec"]
    assert gt.params["n_roi"] == b.BENCH_RECORDING["n_roi"]
    assert gt.params["bg_rate_hz"] == b.REGIMES[regime]["bg_rate_hz"]


@pytest.mark.parametrize("b", BENCHES, ids=IDS)
def test_the_elevated_rate_recording_is_drawn_on_its_own_seed_range(b):
    assert b.ELEVATED_SEED_OFFSET == 60_000 and b.NULL_SEED_OFFSET == 50_000
    _, gt = b.make_elevated_rate_recording("baseline_quiet", 6000)
    assert gt.params["seed"] == 66000
    # The ranges the night's runs use never meet: search 1-96, fresh 6000-6023, null 56000-56011.
    elevated = {s + b.ELEVATED_SEED_OFFSET for s in (*range(1, 97), *range(6000, 6012))}
    others = {*range(1, 97), *range(6000, 6024), *range(56000, 56012), *range(50001, 50097)}
    assert not elevated & others


def test_a_probe_nobody_ran_is_nan_not_zero():
    r = bench.BenchResult(detector="coact", regime="baseline_quiet", n_planted=10, n_hit=5,
                          n_detected=6)
    assert math.isnan(r.hot_fa_per_min) and math.isnan(r.elevated_out_per_hour)
    r = bench.evaluate("coact", "baseline_quiet", (1,), probe=False)
    assert r.probe is None and math.isnan(r.hot_fa_per_min)


def test_probe_counts_splits_calls_at_the_stretch():
    """A stub detector calling once inside the stretch and twice outside, on two seeds."""
    class Det:
        onset_sec = np.array([100.0, 1300.0, 2000.0])
        width_sec = np.array([0.5, 0.5, 0.5])

    got = bench.probe_counts(bench.make_elevated_rate_recording, lambda name, s, **kw: Det(),
                             "coact", "baseline_quiet", (1, 2))
    assert (got.calls_in, got.calls_out) == (2, 4)
    assert got.minutes_in == pytest.approx(10.0)
    assert got.hours_out == pytest.approx(2 * 2400 / 3600)
    assert got.per_min_in == pytest.approx(0.2)
    assert got.per_hour_out == pytest.approx(4 / (2 * 2400 / 3600))


@pytest.mark.parametrize("b", BENCHES, ids=IDS)
def test_evaluate_reads_the_probe_off_the_elevated_rate_recording(b):
    r = b.evaluate("coact", "baseline_quiet", (1,))
    direct = b.evaluate_elevated_rate("coact", "baseline_quiet", (1,))
    assert r.probe.seeds == (1,)
    assert (r.probe.calls_in, r.probe.calls_out) == (direct.calls_in, direct.calls_out)
    assert r.hot_fa_per_min == pytest.approx(direct.per_min_in)
    assert r.hot_fa == 0


def _summary(**over):
    s = dict(f1_quiet=0.7, f1_busy=0.7, mean_f1=0.7, precision_quiet=0.8, precision_busy=0.8,
             probe_quiet=0.0, probe_busy=0.0, null_per_hour=0.0,
             elevated_out_quiet=0.0, elevated_out_busy=0.0)
    s.update(over)
    return s


def test_the_search_admits_a_clean_candidate():
    assert sas.make_admissible()("coact", _summary())


@pytest.mark.parametrize("key", ["probe_quiet", "probe_busy", "elevated_out_quiet"])
def test_the_search_refuses_a_candidate_whose_elevated_rate_score_is_missing(key):
    assert not sas.make_admissible()("coact", _summary(**{key: float("nan")}))


def test_the_search_holds_calls_outside_the_stretch_to_the_empty_recording_budget():
    over = bench.MAX_FALSE_POSITIVES_PER_HOUR["coact"] + 1
    assert not sas.make_admissible()("coact", _summary(elevated_out_quiet=over))
    # Busy is reported beside it, not gated: the budget was measured at the quiet background.
    assert sas.make_admissible()("coact", _summary(elevated_out_busy=over))


def test_a_search_job_carries_the_elevated_rate_numbers():
    key, got = sas._job(("coact", (), (), "baseline_quiet", [1], False))
    direct = bench.evaluate_elevated_rate("coact", "baseline_quiet", (1,))
    assert got["probe_per_min"] == pytest.approx(direct.per_min_in)
    assert got["elevated_out_per_hour"] == pytest.approx(direct.per_hour_out)
