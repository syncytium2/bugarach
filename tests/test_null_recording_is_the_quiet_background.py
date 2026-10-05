"""The no-coordination recording runs at its bench's quiet background, and follows it when it moves.

It was a literal on the fast and slow benches, so #756 moved the quiet background (fast 0.0052 ->
0.0042 Hz, slow 0.0030 -> 0.0024 Hz) and left this recording behind; every calls-per-hour budget
was then measured on a background a quarter busier than the quiet end it stands for. Found while
tabulating the three benches, 2026-09-23.
"""
from __future__ import annotations

import pytest

from bugarach import bench, bench_combined, bench_slow


@pytest.mark.parametrize("b", [bench, bench_slow, bench_combined], ids=["fast", "slow", "combined"])
def test_the_null_recording_is_the_quiet_background(b):
    assert b.NULL_RECORDING["bg_rate_hz"] == b.REGIMES["baseline_quiet"]["bg_rate_hz"]
