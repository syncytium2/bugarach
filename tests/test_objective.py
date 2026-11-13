"""The tuning objective proposes the highest recall under the false-call cap, and nothing else.

``bugarach.objective`` (Tony, 2026-11-13, on recall under a false-call cap: "you may build it
along with a documented rationale"; the rationale is ``docs/scoring_objective.md``).
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from bugarach import negatives as ng
from bugarach import objective as ob


def _cand(label, recall, calls, hours=10.0, n=100):
    return ob.Candidate(setting={"name": label}, recall=recall, n_scored=n,
                        false=ob.FalseCalls(calls, hours), label=label)


def test_false_calls_are_counted_inside_the_negatives_valid_window():
    neg = ng.rate_matched_negative([np.array([100.0, 500.0])], 3600.0, seed=1)
    lo, hi = neg.valid_window
    fc = ob.false_calls([lo - 1.0, lo + 1.0, 1800.0, hi + 1.0], neg)
    assert fc.calls == 2
    assert fc.hours == pytest.approx((hi - lo) / 3600.0)
    both = fc + ob.false_calls([], neg)
    assert both.calls == 2 and both.hours == pytest.approx(2 * fc.hours)
    assert both.per_hour == pytest.approx(fc.per_hour / 2)


def test_the_highest_recall_under_the_cap_is_proposed_and_a_better_one_over_it_is_not():
    loose = _cand("loose", 0.99, calls=40)       # 4 per hour
    mid = _cand("mid", 0.90, calls=10)           # 1 per hour, at the cap
    tight = _cand("tight", 0.70, calls=0)
    choice = ob.choose([loose, mid, tight], cap_per_hour=1.0)
    assert choice.proposed is mid
    assert choice.over_the_cap == (loose,)
    assert choice.admissible == (mid, tight)
    assert choice.resolved


def test_a_tie_in_recall_goes_to_fewer_false_calls_and_then_to_the_earlier_candidate():
    a = _cand("a", 0.9, calls=8)
    b = _cand("b", 0.9, calls=2)
    c = _cand("c", 0.9, calls=2)
    assert ob.choose([a, b, c], 1.0).proposed is b
    assert ob.choose([c, b, a], 1.0).proposed is c


def test_nothing_is_proposed_when_every_setting_is_over_the_cap():
    choice = ob.choose([_cand("x", 0.99, calls=40), _cand("y", 0.95, calls=30)], 1.0)
    assert choice.proposed is None and len(choice.over_the_cap) == 2
    assert "cap stands" in choice.notes[0]


def test_too_few_hours_of_negative_is_reported_and_does_not_block_the_proposal():
    assert ob.hours_to_resolve(1.0) == pytest.approx(3.0)
    assert ob.hours_to_resolve(0.25) == pytest.approx(12.0)
    choice = ob.choose([_cand("short", 0.9, calls=0, hours=1.0)], 1.0)
    assert choice.proposed is not None and not choice.resolved
    assert "3.00 hours are needed" in choice.notes[0]


def test_a_candidate_with_no_negative_or_no_scored_event_is_refused():
    with pytest.raises(ValueError, match="no hours of negative"):
        ob.choose([_cand("none", 0.9, calls=0, hours=0.0)], 1.0)
    with pytest.raises(ValueError, match="no scored planted event"):
        ob.choose([_cand("empty", math.nan, calls=0, n=0)], 1.0)
    with pytest.raises(ValueError, match="positive number of calls per hour"):
        ob.choose([_cand("a", 0.9, calls=0)], 0.0)


def test_the_operating_curve_keeps_only_settings_that_buy_recall_with_false_calls():
    cands = [_cand("a", 0.70, 0), _cand("b", 0.60, 5), _cand("c", 0.90, 10),
             _cand("d", 0.90, 20), _cand("e", 0.99, 40)]
    assert ob.operating_curve(cands) == [(0.0, 0.70), (1.0, 0.90), (4.0, 0.99)]
