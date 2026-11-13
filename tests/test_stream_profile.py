"""A stream profile owns no number: every field is the bench module's own constant (ADR-0020).

The profile is the seam between the three benches and the synthetic-validation scripts. If it
ever carried a value of its own, a stream would have two answers to "what is the jitter", which
is the state this module was written to end.
"""
from __future__ import annotations

import importlib
import re
from pathlib import Path

import pytest

from bugarach import stream_profile as sp

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("stream", sp.STREAMS)
def test_every_field_is_the_modules_own(stream):
    p = sp.profile(stream)
    m = importlib.import_module(sp.MODULES[stream])
    assert p.module is m
    assert m.MEASURED_STREAM == stream, "a profile must not label one stream's bench as another's"
    assert p.recording() == m.BENCH_RECORDING
    assert p.regimes == m.REGIMES
    assert p.measured == m.measured_constants()
    assert p.measured_record == m.MEASURED_RECORD
    assert p.detectors == tuple(m.DETECTORS)
    assert p.operating_points == m.OPERATING_POINTS
    assert p.budgets["probe_per_min"] == m.MAX_PROBE_PER_MIN
    assert p.budgets["false_positives_per_hour"] == m.MAX_FALSE_POSITIVES_PER_HOUR
    assert p.budgets["precision_drop"] == m.MAX_PRECISION_DROP


@pytest.mark.parametrize("stream", sp.STREAMS)
def test_the_copies_cannot_reach_back_into_the_module(stream):
    p = sp.profile(stream)
    m = p.module
    before = dict(m.BENCH_RECORDING), {k: dict(v) for k, v in m.REGIMES.items()}
    p.recording()["jitter_sec"] = 99.0
    p.regimes["baseline_quiet"]["bg_rate_hz"] = 99.0
    assert (dict(m.BENCH_RECORDING), {k: dict(v) for k, v in m.REGIMES.items()}) == before


@pytest.mark.parametrize("stream", sp.STREAMS)
def test_the_source_is_the_recording_in_the_goal_pages_symbols(stream):
    p = sp.profile(stream)
    spec = p.module.BENCH_RECORDING
    for regime in p.module.REGIMES:
        s = p.source(regime)
        assert s.n_cells == spec["n_roi"]
        assert s.participants == tuple(f * spec["n_roi"] for f in spec["participation"])
        assert s.jitter_sec == spec["jitter_sec"]
        assert s.bg_rate_hz == p.module.REGIMES[regime]["bg_rate_hz"]
        assert s.n_events == sum(spec["n_per_level"])
        assert s.events_per_sec == pytest.approx(s.n_events / spec["duration_sec"])


@pytest.mark.parametrize("stream", sp.STREAMS)
def test_without_decoys_changes_the_decoy_count_and_nothing_else(stream):
    p = sp.profile(stream)
    with_, without = p.recording(), p.recording(decoys=False)
    assert without["n_distractors"] == 0
    assert {k: v for k, v in without.items() if k != "n_distractors"} == \
           {k: v for k, v in with_.items() if k != "n_distractors"}
    assert p.decoys == p.module.BENCH_RECORDING["n_distractors"]


def test_simulate_is_the_modules_maker():
    p = sp.profile("slow")
    a, gt_a = p.simulate("baseline_quiet", 3, duration_sec=600.0)
    b, gt_b = p.module.make_recording("baseline_quiet", 3, duration_sec=600.0)
    assert [e.time for e in gt_a.events] == [e.time for e in gt_b.events]
    ta = next(iter(a.streams.values())).t50rise
    tb = next(iter(b.streams.values())).t50rise
    assert all((x == y).all() for x, y in zip(ta, tb))


def test_an_unknown_stream_or_regime_is_refused():
    with pytest.raises(ValueError, match="no bench for stream"):
        sp.profile("medium")
    with pytest.raises(ValueError, match="no regime"):
        sp.profile("fast").source("treatment")


def test_the_three_streams_are_three_different_benches():
    ps = sp.profiles()
    assert tuple(ps) == sp.STREAMS
    assert len({p.module.__name__ for p in ps.values()}) == 3
    assert len({p.source().jitter_sec for p in ps.values()}) == 3


def test_the_module_types_no_bench_number():
    """The seam holds no measured value: a decimal literal here is a second copy of something."""
    code = (ROOT / "src" / "bugarach" / "stream_profile.py").read_text(encoding="utf-8")
    body = re.sub(r'"""[\s\S]*?"""', "", code)       # docstrings may name dates and ADRs
    assert not re.findall(r"(?<![\w.])\d+\.\d+", body), "a typed number in the profile seam"
