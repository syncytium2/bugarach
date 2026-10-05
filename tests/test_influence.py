"""``bugarach.influence``: leave-one-out, the gap-against-leave-one-out test, the mouse bootstrap.

Synthetic items only; every expected value is worked out by hand in the test.
"""
from __future__ import annotations

import numpy as np
import pytest

from bugarach import influence


def pooled(items):
    """A pooled ratio, the shape every group number here has: sum of numerators over sum of
    denominators, so an item weighs by its denominator."""
    return sum(o for _, o, _ in items) / sum(e for _, _, e in items) if items else float("nan")


def ident(it):
    return it[0]


def test_the_heavy_item_is_the_most_influential_and_bounds_the_range():
    # Four items at ratio 1 with weight 1, and one at ratio 5 with weight 4: pooled (4 + 20) / 8 = 3.
    items = [("a", 1, 1), ("b", 1, 1), ("c", 1, 1), ("d", 1, 1), ("heavy", 20, 4)]
    loo = influence.leave_one_out(items, pooled, ident)
    assert loo["value"] == pytest.approx(3.0)
    assert loo["most_influential"] == "heavy"
    assert loo["without"] == pytest.approx(1.0)
    assert loo["delta"] == pytest.approx(-2.0)
    # Dropping a light item: (3 + 20) / 7.
    assert loo["hi"] == pytest.approx(23 / 7)
    assert loo["lo"] == pytest.approx(1.0)
    assert loo["n"] == 5 and loo["unmeasurable_drops"] == 0


def test_fewer_than_two_items_have_no_leave_one_out():
    assert influence.leave_one_out([("a", 1, 1)], pooled, ident) is None


def test_a_gap_outlives_only_when_wider_than_both_ranges():
    a = dict(value=3.0, lo=2.9, hi=3.1)
    b = dict(value=1.0, lo=0.8, hi=1.2)
    p = influence.gap_outlives_leave_one_out(a, b)
    assert p["gap"] == pytest.approx(2.0)
    assert p["outlives"] and not p["ranges_overlap"]
    # One group whose range is wider than the gap: one recording can close it from that side.
    wide = dict(value=3.0, lo=0.9, hi=3.2)
    p = influence.gap_outlives_leave_one_out(wide, b)
    assert not p["outlives"] and p["ranges_overlap"]
    # The width counts the full-group value even when every drop sits on one side of it.
    one_sided = dict(value=3.0, lo=1.5, hi=1.6)
    assert influence.loo_width(one_sided) == pytest.approx(1.5)


def test_pairs_follow_the_order_given():
    loo = {g: dict(value=v, lo=v, hi=v) for g, v in (("ORX", 1.0), ("DI", 2.0), ("MALE", 3.0))}
    out = influence.pairwise(loo, ["DI", "OVX", "MALE", "ORX"])
    assert list(out) == ["DI - MALE", "DI - ORX", "MALE - ORX"]


def test_without_most_influential_drops_the_biggest_mover_across_groups():
    by = {"DI": [("a", 1, 1), ("b", 1, 1), ("heavy", 20, 4)],
          "ORX": [("c", 2, 1), ("d", 2, 1), ("e", 3, 1)]}
    loo = {g: influence.leave_one_out(v, pooled, ident) for g, v in by.items()}
    w = influence.without_most_influential(by, pooled, ident, loo)
    assert w["dropped"] == "heavy" and w["group"] == "DI"
    assert w["values"]["DI"] == pytest.approx(1.0)
    assert w["values"]["ORX"] == pytest.approx(7 / 3)


def test_a_drawn_mouse_brings_all_of_its_recordings():
    items = [("m1", "r1"), ("m1", "r2"), ("m1", "r3"), ("m2", "r4"), ("m3", "r5")]
    draws = influence.mouse_bootstrap(items, lambda its: [r for _, r in its],
                                      lambda it: it[0], 200, np.random.RandomState(0))
    for d in draws:
        n1 = sum(r in ("r1", "r2", "r3") for r in d)
        assert n1 % 3 == 0
        assert len(d) == n1 + d.count("r4") + d.count("r5")
        assert d.count("r1") == d.count("r2") == d.count("r3")
