"""The order the four experimental groups are shown in, everywhere a person reads them.

Tony, 2026-09-23: *"please always use DI OVX Male ORX as the ordering"*. Figures, tables, pages
and prose list the groups in :data:`GROUP_ORDER`. Before this there were four orders in the tree:
alphabetical from ``sorted()``, two different hand-typed tuples, and a report whose prose
introduced them as ORX, OVX, DI, MALE.

This is a display order. It says nothing about the groups, and measurement code whose results
depend on iteration order (a shared random generator consumed group by group, for instance)
keeps whatever order it was measured in, so no number moves for a change of layout.
"""
from __future__ import annotations

from collections.abc import Iterable

GROUP_ORDER: tuple[str, ...] = ("DI", "OVX", "MALE", "ORX")


def group_key(group: str) -> tuple[int, str]:
    """Sort key: the four groups in :data:`GROUP_ORDER`, then any other label alphabetically.

    Case-insensitive on the four, because exports have spelled MALE both ways.
    """
    g = str(group)
    up = g.upper()
    return (GROUP_ORDER.index(up), "") if up in GROUP_ORDER else (len(GROUP_ORDER), g)


def in_group_order(groups: Iterable[str]) -> list[str]:
    """``groups`` de-duplicated and in display order."""
    return sorted(set(groups), key=group_key)
