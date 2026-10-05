"""The call-to-call matcher behind tools/agreement_on_real.py: the scorer's rule, span to span."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import agreement_on_real as ag  # noqa: E402


def test_overlapping_spans_match_and_the_tolerance_is_inclusive():
    # 10–11 s against 12–13 s: 1 s apart; 20 s against 22.5 s: exactly the tolerance.
    pairs = ag.match_calls([10.0, 20.0], [1.0, 0.0], [12.0, 20.0 + ag.TOL_SEC], [1.0, 0.0])
    assert sorted(pairs) == [(0, 0), (1, 1)]


def test_matching_is_one_to_one_and_closest_first():
    # One call of A between two of B: it takes the nearer, and the other is left alone.
    pairs = ag.match_calls([100.0], [0.0], [98.5, 100.4], [0.0, 0.0])
    assert pairs == [(0, 1)]


def test_indices_refer_to_the_inputs_as_given_not_sorted():
    # Unsorted input: the pair indices must still point at the caller's rows.
    pairs = ag.match_calls([50.0, 10.0], [0.0, 0.0], [10.5, 300.0], [0.0, 0.0])
    assert pairs == [(1, 0)]


def test_calls_beyond_the_tolerance_do_not_match():
    assert ag.match_calls([0.0], [1.0], [1.0 + ag.TOL_SEC + 0.01], [0.0]) == []
    assert ag.match_calls([], [], [1.0], [0.0]) == []
