"""Figures 3 and 4 of the final-parameters night's morning report: the elevated-rate recording and
the bench floors re-measured (``tools/make_elevated_rate_figure.py``, ``make_bench_floor_figure.py``).

Both tools draw with matplotlib, which no ``pyproject.toml`` extra declares yet
(``docs/todo/2026-09-25-matplotlib-figure-tools-are-an-undeclared-dependency.md``), so these skip
where it is absent rather than fail.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("matplotlib")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import make_bench_floor_figure as fig4  # noqa: E402
import make_elevated_rate_figure as fig3  # noqa: E402


def _row(probe, out):
    return {bg: dict(probe_calls_per_min=probe, elevated_calls_per_hour_outside=out)
            for bg in ("baseline_quiet", "baseline_busy")}


def _candidates(tmp_path, name, stream, rows, picked=()):
    chorus = {m: dict(picked=p) for m, p in picked}
    p = tmp_path / name
    p.write_text(json.dumps(dict(results={stream: rows},
                                 benches={stream: dict(chorus=chorus)})), encoding="utf-8")
    return p


def test_only_the_picked_chorus_seed_is_drawn_and_a_later_file_wins(tmp_path):
    a = _candidates(tmp_path, "a.json", "slow", {
        "coact:shipped": _row(0.1, 0.0),
        "chorus:chorus_norm_slow_seed0.json": _row(9.0, 9.0),
        "chorus:chorus_norm_slow_seed3.json": _row(1.4, 0.0)},
        picked=[("chorus_norm", "chorus_norm_slow_seed3.json")])
    b = _candidates(tmp_path, "b.json", "slow", {"coact:shipped": _row(0.2, 0.5)})
    got = fig3.collect([a, b])["slow"]
    assert set(got) == {("coact", "shipped"), ("chorus_norm", "picked")}
    assert got[("chorus_norm", "picked")]["baseline_quiet"]["probe_calls_per_min"] == 1.4
    assert got[("coact", "shipped")]["baseline_quiet"]["probe_calls_per_min"] == 0.2


def test_figure_3_renders(tmp_path):
    a = _candidates(tmp_path, "a.json", "combined", {
        "rate:shipped": _row(2.5, 0.1), "rate:proposal": _row(1.3, 0.0)})
    png = fig3.draw(fig3.collect([a]), tmp_path / "f3.png")
    assert png.exists() and png.stat().st_size > 10_000


def test_figure_4_renders_from_a_probe_record(tmp_path):
    summary = {f"{b}/{bg}": dict(
        bench_floor_range=[5, 7], elevated_rate_floor_range=[16, 18],
        share_below_floor_mean=0.33, null_floor_range=[4, 5],
        below_floor_by_participants={"3": dict(planted=40, below_floor=40, share=1.0),
                                     "6": dict(planted=40, below_floor=0, share=0.0)})
        for b in ("fast", "slow", "combined") for bg in ("baseline_quiet", "baseline_busy")}
    png = fig4.draw(dict(summary=summary, expected={"fast": [5, 10]}), tmp_path / "f4.png")
    assert png.exists() and png.stat().st_size > 10_000
