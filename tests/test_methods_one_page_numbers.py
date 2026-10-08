"""The one-page methods quote numbers the code owns; this keeps them from drifting apart.

`docs/methods/one_page/methods_one_page.html` is written by hand, and the approach it describes
is still moving (Tony, 2026-09-25: "assume this will change again"). Every number below is read
from the constant that sets it and must appear on the page exactly as written, so a moved
constant turns the suite red instead of leaving the methods quietly wrong. The murderboard of
2026-09-25 (role 7) asked for this; the page's own review record is
`docs/reviews/methods_one_page_2026-09-25.md`.
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
PAGE = REPO / "docs" / "methods" / "one_page" / "methods_one_page.html"
sys.path.insert(0, str(REPO / "tools"))


@pytest.fixture(scope="module")
def text() -> str:
    body = PAGE.read_text(encoding="utf-8").split("<body>")[1]
    plain = html.unescape(re.sub(r"<[^>]+>", "", body))
    return re.sub(r"\s+", " ", plain.replace(" ", " "))


def _g(x: float) -> str:
    """A constant as the page writes it: no trailing zeros."""
    return f"{x:g}"


def test_the_event_floor_constants(text):
    from bugarach import event_floor as ef

    assert f"within {_g(ef.WINDOW_SEC)} s" in text
    assert f"[−{_g(ef.J_SEC)} s, {_g(ef.J_SEC)} s)" in text
    assert f"{ef.MIN_DRAWS:,} draws" in text
    assert ef.FA_PER_HOUR == 1.0 and "at most once per hour" in text
    assert f"never fewer than {ef.MINIMUM_ROIS} ROIs" in text


def test_the_simulation_parameters(text):
    from bugarach import bench, bench_combined, bench_slow

    mods = {"fast": bench, "slow": bench_slow, "combined": bench_combined}
    for stream, m in mods.items():
        rec = m.BENCH_RECORDING
        assert f"{stream} {rec['jitter_sec']:.3f} s" in text, stream
        mid = rec["participation"][1]
        assert f"{stream} {mid:.2f}" in text, stream
        assert rec["n_roi"] == 32
        assert rec["duration_sec"] == 45 * 60
        assert rec["n_distractors"] == 6
    assert "32 ROIs" in text and "lasts 45 min" in text and "six decoys" in text
    counts = [sum(bench.realistic_counts(s, 3, 2700.0)) for s in mods]
    assert "(fast {} events, slow {}, combined {})".format(*counts) in text


def test_the_measured_intervals(text):
    rec = json.loads((REPO / "docs/learned/runs/2026-09-25-real-intervals/summary.json")
                     .read_text(encoding="utf-8"))["summary"]
    for stream in ("fast", "slow", "combined"):
        a = rec[stream]["all"]
        assert f"{a['p50']:.1f} s ({stream})" in text, stream
    rates = ", ".join(f"{rec[s]['all']['events_per_hour']:.1f}" for s in ("fast", "slow"))
    assert f"{rates} and {rec['combined']['all']['events_per_hour']:.1f} events per hour" in text


def test_the_scoring_budgets(text):
    from bugarach import bench, bench_combined, bench_slow, score

    assert f"within {_g(score.TOL_SEC)} s" in text
    fp = [m.MAX_FALSE_POSITIVES_PER_HOUR["coact"] for m in (bench, bench_slow, bench_combined)]
    assert "(fast {}, slow {}, combined {})".format(*map(_g, fp)) in text
    probe = {m.MAX_PROBE_PER_MIN["coact"] for m in (bench, bench_slow, bench_combined)}
    assert probe == {1.0} and "1 call per minute" in text
    drop = {m.MAX_PRECISION_DROP["coact"] for m in (bench, bench_slow, bench_combined)}
    assert drop == {0.10} and "at most 0.10" in text


def test_the_search_limits(text):
    import search_all_settings as s
    from bugarach import bench

    assert s.ALPHA_CAP == 6e-16 and "6×10−16" in text
    assert f"contexts {_g(s.CONTEXT_MIN_SEC)}–{_g(s.CONTEXT_MAX_SEC)} s" in text
    assert bench.GUARD_MAX_CONTEXT_FRACTION == 0.25 and "a quarter of the context" in text


def test_the_benchmark_bootstrap(text):
    import score_bench_candidates as sc

    assert f"{sc.BOOTSTRAP:,} resamples" in text


def test_the_call_measure_lengths(text):
    from bugarach import call_measure as cm

    (fg, fa), (sg, sa) = cm.DEFAULTS["fast"], cm.DEFAULTS["slow"]
    assert cm.DEFAULTS["combined"] == cm.DEFAULTS["slow"]
    assert f"±{_g(fa)} s (fast) or ±{_g(sa)} s (slow, combined)" in text
    assert f"over {_g(fg)} s (fast) or {_g(sg)} s (slow, combined) apart" in text
