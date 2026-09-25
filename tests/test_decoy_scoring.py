"""ADR-0006: F1 reported both as scored and with calls on decoys left out of precision."""
from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pytest

from bugarach import bench
from bugarach.score import score_stream


# Pre-ADR-0008 by construction: these pin measurements taken before the floor, or exercise detector
# mechanics it has nothing to do with. The floor's own tests are tests/test_bench_floor.py.
pytestmark = pytest.mark.usefixtures("pre_adr_0008_bench")


def _calls(times):
    t = np.asarray(sorted(times), float)
    return SimpleNamespace(onset_sec=t, width_sec=np.zeros(t.size))


def test_a_call_on_every_decoy_and_every_event_leaves_precision_one_without_decoys():
    s, gt = bench.make_recording("baseline_quiet", 1)
    hot = gt.params["hot_window"]
    decoys = [d.time for d in gt.distractors if not hot[0] <= d.time <= hot[1]]
    assert decoys, "the bench plants decoys outside the probe"
    sc = score_stream(gt, _calls(list(gt.times) + decoys))
    assert sc.n_hit == len(gt.events)
    assert sc.decoy_calls == len(decoys)
    r = bench.pool_scores([sc], detector="x", regime="baseline_quiet")
    assert r.decoy_calls == len(decoys)
    assert r.precision == pytest.approx(len(gt.events) / (len(gt.events) + len(decoys)))
    assert r.precision_without_decoys == pytest.approx(1.0)
    assert r.f1_without_decoys == pytest.approx(1.0)
    assert r.f1 < r.f1_without_decoys


def test_a_call_on_nothing_is_still_a_false_alarm_both_ways():
    s, gt = bench.make_recording("baseline_quiet", 2)
    near = [d.time for d in gt.distractors] + list(gt.times) + list(gt.params["hot_window"])
    t = next(x for x in np.arange(30.0, 2600.0, 7.0)
             if min(abs(x - y) for y in near) > 30 and not
             gt.params["hot_window"][0] <= x <= gt.params["hot_window"][1])
    sc = score_stream(gt, _calls(list(gt.times) + [t]))
    assert sc.decoy_calls == 0
    r = bench.pool_scores([sc], detector="x", regime="baseline_quiet")
    assert r.precision == r.precision_without_decoys < 1.0
