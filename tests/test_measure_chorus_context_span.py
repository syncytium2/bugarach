"""The piece arithmetic and the between-mode matching behind ``tools/measure_chorus_context_span.py``."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import measure_chorus_context_span as m  # noqa: E402


def test_pieces_are_consecutive_and_the_last_is_what_remains():
    ps = m.pieces(3.2, 2700.0)
    assert ps[0] == (3.2, pytest.approx(412.8))
    assert all(b == pytest.approx(a2) for (_, b), (a2, _) in zip(ps, ps[1:]))
    assert all(b - a == pytest.approx(409.6) for a, b in ps[:-1])
    assert ps[-1][1] == 2700.0 and ps[-1][1] - ps[-1][0] < 409.6
    assert len(ps) == 7


def test_a_span_shorter_than_one_piece_is_one_piece_and_has_no_edges():
    assert m.pieces(0.0, 300.0) == [(0.0, 300.0)]
    assert m.edges_of((0.0, 300.0)).size == 0
    assert m.away(np.array([1.0, 299.0]), m.edges_of((0.0, 300.0))).all()


def test_away_leaves_out_within_edge_sec_of_an_internal_edge_only():
    edges = m.edges_of((0.0, 1000.0))  # 409.6 and 819.2; 0 and 1000 are not piece edges
    assert edges == pytest.approx([409.6, 819.2])
    t = np.array([1.0, 380.0, 409.6 + m.EDGE_SEC + 0.1, 800.0, 999.0])
    assert m.away(t, edges).tolist() == [True, False, True, False, True]


def test_match_share_is_one_to_one_within_tolerance():
    # 10.0 matches 10.5 (closest), 11.0 has no partner left; 50 is too far from 53.
    assert m.match_share([10.0, 11.0, 50.0], [10.5, 53.0], 2.5) == (1, 3, 2)
    assert m.match_share([], [1.0], 2.5) == (0, 0, 1)
