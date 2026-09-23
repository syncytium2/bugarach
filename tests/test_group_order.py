"""The groups are shown DI, OVX, MALE, ORX everywhere (Tony, 2026-09-23).

On the day the rule was given the tree held four orders: alphabetical from ``sorted()``, two
hand-typed tuples that disagreed with each other, and a report whose comment said the prose
introduces them ORX, OVX, DI, MALE. This keeps the order in one place.
"""
from __future__ import annotations

import itertools
import re
from pathlib import Path

from bugarach.groups import GROUP_ORDER, group_key, in_group_order

REPO = Path(__file__).resolve().parents[1]


def test_the_order_is_the_one_tony_gave():
    assert GROUP_ORDER == ("DI", "OVX", "MALE", "ORX")


def test_sorting_puts_the_four_first_and_anything_else_after():
    got = in_group_order(["ORX", "UNGROUPED", "MALE", "DI", "OVX", "ORX", "NA"])
    assert got == ["DI", "OVX", "MALE", "ORX", "NA", "UNGROUPED"]
    assert group_key("Male") == group_key("MALE")


def _literal_orders(text: str):
    """Every quoted run of all four group names, in the order it is written."""
    names = "|".join(GROUP_ORDER)
    rx = re.compile(r"""["'](%s)["']\s*,\s*["'](%s)["']\s*,\s*["'](%s)["']\s*,\s*["'](%s)["']"""
                    % ((names,) * 4))
    return [m.groups() for m in rx.finditer(text)]


def test_no_code_types_its_own_group_order():
    wrong = []
    for path in itertools.chain((REPO / "src").rglob("*.py"), (REPO / "tools").glob("*.py")):
        if path.name == "groups.py":
            continue
        for order in _literal_orders(path.read_text(encoding="utf-8", errors="ignore")):
            if len(set(order)) == 4 and tuple(order) != GROUP_ORDER:
                wrong.append(f"{path.relative_to(REPO)}: {order}")
    assert not wrong, ("group order typed by hand and not DI, OVX, MALE, ORX — import "
                       f"bugarach.groups.GROUP_ORDER instead: {wrong}")
