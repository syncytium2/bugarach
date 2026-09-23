"""How much one recording carries a group's number, and whether a group difference outlives it.

A group's number in this project is usually read off **pooled** counts — pairs, variances,
factorial cumulants summed over the group's recordings and then divided — so a recording weighs
by what it brings, and one dense recording can carry a whole group. On 2026-09-22 that was the
answer for slow jitter (one ORX recording held the between-group difference); on 2026-09-23 the
same recording halved slow ORX's co-modulation, and the leave-one-out that showed it was done by
hand in a run record. This module is that check as code, so it goes with every rerun.

Nothing here filters. The export folder is the input and every recording in it stays in every
reported number; dropping one is a question asked of the number, never a cleaned result.

* :func:`leave_one_out` — the statistic with each item dropped in turn: the range it takes, and
  the single item that moves it most.
* :func:`gap_outlives_leave_one_out` — for two groups, whether the gap between them is wider than
  **both** groups' leave-one-out ranges. That is the orchestrator's criterion (2026-09-23), and it
  is deliberately blunt: a gap no wider than what one recording does to either group is a gap
  about a recording.
* :func:`without_most_influential` — every group's statistic with the one item that moved its own
  group most, across all groups, dropped.
* :func:`mouse_bootstrap` — the statistic over resamples of MICE, because recordings from one
  mouse are not independent draws (66 recordings, fewer mice).
"""
from __future__ import annotations

from collections.abc import Callable, Hashable, Mapping, Sequence
from typing import Any

import numpy as np


def leave_one_out(items: Sequence, stat: Callable[[list], float],
                  ident: Callable[[Any], Hashable]) -> dict | None:
    """``stat`` over ``items`` and over every ``items`` minus one.

    Returns ``value`` (all items), ``lo`` / ``hi`` (the range over the drops, which is what a
    single item can do to the number), ``most_influential`` (the identity of the item whose drop
    moves the value furthest), ``without`` (the value without it) and ``delta`` (``without −
    value``). Drops whose statistic is not finite are ignored for the range and the argmax;
    ``unmeasurable_drops`` counts them. ``None`` for fewer than two items.
    """
    items = list(items)
    if len(items) < 2:
        return None
    base = float(stat(items))
    drops = []
    for j, it in enumerate(items):
        v = float(stat(items[:j] + items[j + 1:]))
        drops.append((ident(it), v))
    finite = [(i, v) for i, v in drops if np.isfinite(v)]
    if not finite:
        return dict(value=base, lo=float("nan"), hi=float("nan"), most_influential=None,
                    without=float("nan"), delta=float("nan"), n=len(items),
                    unmeasurable_drops=len(drops))
    vals = np.array([v for _, v in finite])
    who, w = max(finite, key=lambda t: abs(t[1] - base) if np.isfinite(base) else 0.0)
    return dict(value=base, lo=float(vals.min()), hi=float(vals.max()),
                most_influential=who, without=float(w), delta=float(w - base), n=len(items),
                unmeasurable_drops=len(drops) - len(finite))


def loo_width(loo: Mapping) -> float:
    """How far one item can move the number: the whole leave-one-out range, which always holds
    the full-group value between its ends."""
    lo = min(loo["lo"], loo["value"])
    hi = max(loo["hi"], loo["value"])
    return float(hi - lo)


def gap_outlives_leave_one_out(a: Mapping, b: Mapping) -> dict:
    """Is the gap between two groups wider than both groups' leave-one-out ranges?

    ``a`` and ``b`` are :func:`leave_one_out` results. ``outlives`` is True only when
    ``|a − b|`` exceeds the width of **each** range — one recording cannot close it from either
    side. ``ranges_overlap`` is reported beside it: two ranges that overlap mean some single drop
    in each group could bring them level, which is a weaker test and never the headline.
    """
    gap = float(a["value"] - b["value"])
    wa, wb = loo_width(a), loo_width(b)
    ok = bool(np.isfinite(gap) and np.isfinite(wa) and np.isfinite(wb)
              and abs(gap) > wa and abs(gap) > wb)
    a_lo, a_hi = min(a["lo"], a["value"]), max(a["hi"], a["value"])
    b_lo, b_hi = min(b["lo"], b["value"]), max(b["hi"], b["value"])
    return dict(gap=gap, loo_width_first=wa, loo_width_second=wb, outlives=ok,
                ranges_overlap=bool(a_lo <= b_hi and b_lo <= a_hi))


def pairwise(loo_by_group: Mapping[str, Mapping], order: Sequence[str]) -> dict:
    """:func:`gap_outlives_leave_one_out` for every pair of groups, keyed ``"A - B"`` with A before
    B in ``order`` (pass ``bugarach.groups.in_group_order``'s result)."""
    names = [g for g in order if loo_by_group.get(g)]
    out = {}
    for i, g in enumerate(names):
        for h in names[i + 1:]:
            out[f"{g} - {h}"] = gap_outlives_leave_one_out(loo_by_group[g], loo_by_group[h])
    return out


def without_most_influential(items_by_group: Mapping[str, Sequence], stat: Callable[[list], float],
                             ident: Callable[[Any], Hashable],
                             loo_by_group: Mapping[str, Mapping]) -> dict | None:
    """Every group's statistic with the single most influential item dropped — the one whose
    leave-one-out delta is largest in absolute value over all groups. A between-group ordering
    that changes here was an ordering about one recording."""
    movers = [(abs(l["delta"]), l["most_influential"], g) for g, l in loo_by_group.items()
              if l and l["most_influential"] is not None and np.isfinite(l["delta"])]
    if not movers:
        return None
    _, who, whose = max(movers, key=lambda t: t[0])
    values = {g: float(stat([it for it in items if ident(it) != who]))
              for g, items in items_by_group.items()}
    return dict(dropped=who, group=whose, values=values)


def mouse_bootstrap(items: Sequence, stat: Callable[[list], Any], mouse: Callable[[Any], Hashable],
                    n_boot: int, rs: np.random.RandomState) -> list:
    """``stat`` over ``n_boot`` resamples of the items' MICE with replacement; a drawn mouse
    brings every one of its items. ``stat`` may return anything; the list is returned as is."""
    clusters: dict = {}
    for it in items:
        clusters.setdefault(mouse(it), []).append(it)
    groups = list(clusters.values())
    out = []
    for _ in range(n_boot):
        pick = rs.randint(0, len(groups), len(groups))
        out.append(stat([it for j in pick for it in groups[j]]))
    return out
