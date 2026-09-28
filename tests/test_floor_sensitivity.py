"""tools/measure_floor_sensitivity.py: its current setting IS ADR-0008's floor, each variant moves
only the setting it names, and calls-kept counts overlaps. Synthetic trains only."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import measure_floor_sensitivity as M  # noqa: E402
from bugarach import event_floor as ef  # noqa: E402


def trains(seed=3, n=12, frames=6000, rate=0.002):
    rs = np.random.default_rng(seed)
    out = [np.sort(rs.choice(frames, size=rs.poisson(rate * frames), replace=False)) for _ in range(n)]
    for t0 in (1000, 2500, 4000):           # three planted co-activations of 8 ROIs
        for r in range(8):
            out[r] = np.sort(np.append(out[r], t0 + r % 3))
    return out, frames


def test_the_current_setting_is_adr_0008s_floor():
    tr, L = trains()
    fl = M.floors_of(tr, L, 0.1, ("t", 1), draws=40)
    ref = ef.window_floor(tr, L, 0.1, key=("t", 1), draws=40)
    assert fl[("current", "ADR-0008")] == (ref.floor, ref.chance_floor)


def test_every_setting_is_varied_alone():
    names = {(n, v): (c, b, m) for n, v, c, b, m in M.SETTINGS}
    cur = names[("current", "ADR-0008")]
    for (n, v), (c, b, m) in names.items():
        changed = sum(x != y for x, y in zip((c[0], c[1], b, m), (cur[0][0], cur[0][1], cur[1], cur[2])))
        assert changed == (0 if n == "current" else 1), (n, v)


def test_the_budget_and_minimum_read_the_current_curve():
    tr, L = trains()
    fl = M.floors_of(tr, L, 0.1, ("t", 2), draws=40)
    cur = fl[("current", "ADR-0008")]
    assert fl[("fa_per_hour", 0.5)][0] >= cur[0] >= fl[("fa_per_hour", 2.0)][0]
    assert fl[("minimum", 4)] == (max(4, cur[1]), cur[1])
    assert fl[("minimum", 2)] == (max(2, cur[1]), cur[1])


def test_kept_counts_current_calls_a_new_call_overlaps():
    cur = (np.array([10.0, 50.0, 90.0]), np.array([2.0, 2.0, 2.0]))
    new = (np.array([11.0, 200.0]), np.array([1.0, 1.0]))
    assert M.kept(cur, new) == 1
    assert M.kept(cur, cur) == 3
