"""The performance table: what it reports, what it gates, and what it must not do.

The last assertion in this file is the one that matters most — that no ordering
API creeps back in. The tiers were removed because the question they answered was
not being asked and, tested, could not be answered; a future session reaching for
`rank()` should find it missing and read why.
"""

import json
from pathlib import Path

import pytest

from bugarach import performance as perf
from bugarach.performance import (
    MIN_X_REALTIME, FoldScore, fold_scores_from_bakeoff, performance_table,
)

BAKEOFF = Path(__file__).resolve().parents[1] / "docs" / "learned" / "bakeoff.json"


def _scores(spec, *, probe=None, xrt=100.0, distractor=0.0, seeds_per_fold=3):
    probe = probe or {}
    out = []
    for det, f1s in spec.items():
        for i, f1 in enumerate(f1s):
            out.append(FoldScore(
                detector=det, fold=i, f1=f1,
                seeds=tuple(range(i * seeds_per_fold, (i + 1) * seeds_per_fold)),
                hot_fa_per_min=probe.get(det, 0.0),
                detect_x_realtime=xrt, distractor_rate=distractor,
                recall=0.5, precision=0.5))
    return out


# --- what the table reports ---

def test_every_detector_gets_a_row():
    t = performance_table(_scores({"a": [0.6] * 4, "b": [0.5] * 4}))
    assert {r.detector for r in t.rows} == {"a", "b"}
    assert t.n_folds == 4


def test_the_fold_range_is_the_observed_min_and_max():
    """Not an interval estimate, and deliberately not dressed as one — it is there
    so a reader can see an overlap without anyone deciding whether it counts."""
    t = performance_table(_scores({"a": [0.60, 0.70, 0.65, 0.55]}))
    r = t.row("a")
    assert r.f1_lo == pytest.approx(0.55)
    assert r.f1_hi == pytest.approx(0.70)
    assert r.f1 == pytest.approx(0.625)


def test_detectors_need_not_share_folds():
    """A real consequence of dropping the ordering: the paired-fold requirement
    existed only to make comparisons legitimate, and there are no comparisons."""
    scores = _scores({"a": [0.6] * 4}) + [
        FoldScore(detector="b", fold=99, f1=0.5, seeds=(500,))]
    t = performance_table(scores)
    assert t.row("b") is not None


def test_render_leads_with_the_seed_and_fold_count():
    """An F1 quoted without them is the defect this project has already paid for."""
    out = performance_table(_scores({"a": [0.6] * 4})).render()
    assert "12 seeds, 4 folds" in out
    assert "no ordering claimed" in out


def test_render_says_the_distractor_column_is_not_gated():
    out = performance_table(_scores({"a": [0.6] * 4})).render()
    assert "REPORTED, NOT GATED" in out


# --- gates: a requirement, not a comparison ---

def test_probe_gate_marks_but_does_not_remove():
    """The difference from the tiers it replaced: a failing detector stays in the
    table with its verdict beside it, because the table's job is to report."""
    t = performance_table(_scores({"rate": [0.9] * 4, "coact": [0.9] * 4},
                                  probe={"rate": 9.0, "coact": 0.1}))
    assert t.row("rate") is not None, "a gated detector must still be reported"
    assert t.row("rate").gate == "FAIL"
    assert t.row("coact").gate == "pass"


def test_no_declared_ceiling_reads_none_not_pass():
    """`none` means nobody has set a ceiling, which is not the same statement as
    passing one — the learned models sit here while one of them fires above the
    ceiling a hand-written detector failed on."""
    t = performance_table(_scores({"tube": [0.9] * 4}, probe={"tube": 99.0}))
    assert t.row("tube").gate == "none"
    assert t.row("tube").probe_ceiling is None


def test_unset_probe_gate_uses_the_benchs_own_ceilings():
    from bugarach.bench import MAX_PROBE_PER_MIN
    over = MAX_PROBE_PER_MIN["coact"] + 1.0
    t = performance_table(_scores({"coact": [0.9] * 4}, probe={"coact": over}))
    assert t.row("coact").gate == "FAIL"


def test_probe_gate_can_be_disabled_explicitly():
    t = performance_table(_scores({"coact": [0.9] * 4}, probe={"coact": 99.0}),
                          max_probe_per_min=None)
    assert t.row("coact").gate == "none"


def test_realtime_gate_fails_a_detector_that_cannot_keep_up():
    slow = _scores({"a": [0.9] * 4}, xrt=MIN_X_REALTIME / 2)
    assert performance_table(slow).row("a").gate == "FAIL"


def test_distractor_gate_is_disarmed_by_default():
    """Firing on every planted distractor does not fail anything today.

    Uses a detector that HAS a probe ceiling, so `pass` is reachable and the
    assertion is about the distractor axis rather than about a missing ceiling.
    """
    t = performance_table(_scores({"coact": [0.9] * 4}, probe={"coact": 0.0},
                                  distractor=1.0))
    assert t.row("coact").gate == "pass"
    assert t.row("coact").distractor_rate == 1.0


def test_distractor_gate_works_once_armed():
    t = performance_table(_scores({"a": [0.9] * 4}, distractor=0.9),
                          max_distractor_rate=0.5)
    assert t.row("a").gate == "FAIL"


# --- reading the bake-off ---

@pytest.mark.skipif(not BAKEOFF.exists(), reason="bake-off not in the tree")
def test_bakeoff_conversions_come_from_the_files_own_spec():
    raw = json.loads(BAKEOFF.read_text())
    spec, per_fold = raw["spec"], raw["seeds_per_fold"]
    minutes = (spec["hot_window"][1] - spec["hot_window"][0]) / 60.0 * per_fold
    opportunities = spec["n_distractors"] * per_fold

    one = next(s for s in fold_scores_from_bakeoff(raw)
               if s.detector == "coact" and s.fold == 0)
    src = next(p for p in raw["hand_written"]["coact"]["per_fold"] if p["fold"] == 0)
    assert one.hot_fa_per_min == pytest.approx(src["hot_fa"] / minutes)
    assert one.distractor_rate == pytest.approx(src["distractor_hits"] / opportunities)


@pytest.mark.skipif(not BAKEOFF.exists(), reason="bake-off not in the tree")
def test_the_shipped_bakeoff_fails_one_gate_and_declares_none_for_the_learned():
    """Two facts about the shipped file, both reported rather than acted on.

    rate+context ships a setting firing over its own ceiling because the bake-off
    picks knobs by raw argmax with no probe gate. And the learned models have no
    ceilings at all, so the table cannot say anything about them on that axis.
    """
    t = performance_table(fold_scores_from_bakeoff(BAKEOFF))
    assert t.row("rate").gate == "FAIL"
    assert t.row("tube").gate == "none"
    assert t.row("tube").probe_per_min > t.row("rate").probe_ceiling, (
        "tube fires above the ceiling rate+context failed on, and is ungated")


@pytest.mark.skipif(not BAKEOFF.exists(), reason="bake-off not in the tree")
def test_the_top_four_overlap_and_the_table_shows_it_rather_than_resolving_it():
    """The whole reason there is no ordering: these four are not separable here."""
    t = performance_table(fold_scores_from_bakeoff(BAKEOFF))
    top = {r.detector: r for r in t.rows[:4]}
    assert set(top) == {"tube", "tube_guard", "coact", "loco"}
    lo = max(r.f1_lo for r in top.values())
    hi = min(r.f1_hi for r in top.values())
    assert lo < hi, "the four fold ranges must genuinely overlap"


# --- the guard ---

def test_no_ordering_api_comes_back():
    """Tiers, a beats-relation and a tie margin were removed on 2026-08-30.

    They answered a question nobody was asking, and when tested they could not
    answer it: tier membership moved with the seed block while the argmax stood
    still. A session reaching for them should find them gone and read the module
    docstring, which also records why the standard statistical route
    (Friedman + Nemenyi) is the wrong fit for a bench that ships deliberate
    controls.
    """
    banned = {"rank", "tiers", "tier_of", "TIE_MARGIN", "MIN_SEEDS", "TooThin"}
    assert banned.isdisjoint(perf.__all__)
    for name in banned:
        assert not hasattr(perf, name), f"{name} is back in bugarach.performance"
