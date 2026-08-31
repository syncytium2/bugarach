"""The ranking rule: tiers, gates, and the two halves of the tie test.

Every assertion here is about the *rule*, not about which detector is good —
that is the separation the module exists to enforce, and a test that pinned a
winner would undo it. The one test that reads the shipped bake-off checks that
the rule **refuses** it, which is a fact about the file's seed count and does not
move when a detector improves.
"""

import json
import random
from pathlib import Path

import pytest

from bugarach.rank import (
    MIN_SEEDS, TIE_MARGIN, FoldScore, Ranking, TooThin,
    fold_scores_from_bakeoff, rank, _beats,
)

BAKEOFF = Path(__file__).resolve().parents[1] / "docs" / "learned" / "bakeoff.json"


def _scores(spec, *, n_seeds=MIN_SEEDS, probe=None, xrt=100.0, distractor=0.0):
    """Build a flat FoldScore list from ``{detector: [f1 per fold]}``.

    Seeds are dealt out contiguously so the total distinct count clears
    :data:`MIN_SEEDS` unless a test is deliberately starving it.
    """
    probe = probe or {}
    n_folds = len(next(iter(spec.values())))
    per_fold = max(1, n_seeds // n_folds)
    out = []
    for det, f1s in spec.items():
        for i, f1 in enumerate(f1s):
            out.append(FoldScore(
                detector=det, fold=i, f1=f1,
                seeds=tuple(range(i * per_fold, (i + 1) * per_fold)),
                hot_fa_per_min=probe.get(det, 0.0),
                detect_x_realtime=xrt,
                distractor_rate=distractor,
            ))
    return out


# --- D4: a tie needs BOTH halves to fail, and each half catches its own case ---

def test_majority_without_margin_is_a_tie():
    """Wins 3 of 4 folds but leads by 0.013 — the coact/loco case, measured."""
    a = [0.711, 0.645, 0.606, 0.641]
    b = [0.696, 0.640, 0.567, 0.648]
    assert sum(x > y for x, y in zip(a, b)) == 3          # majority: yes
    assert 0 < (sum(a) - sum(b)) / 4 < TIE_MARGIN          # margin: no
    assert not _beats(a, b, TIE_MARGIN)


def test_margin_without_majority_is_a_tie():
    """Leads by 0.030 but wins only 2 of 4 folds — the tube/coact case, measured."""
    a = [0.692, 0.658, 0.744, 0.629]
    b = [0.711, 0.645, 0.606, 0.641]
    assert sum(x > y for x, y in zip(a, b)) == 2           # majority: no
    assert (sum(a) - sum(b)) / 4 > TIE_MARGIN              # margin: yes
    assert not _beats(a, b, TIE_MARGIN)


def test_both_halves_present_is_a_win():
    a = [0.627, 0.472, 0.568, 0.500]
    b = [0.422, 0.468, 0.559, 0.562]
    assert _beats(a, b, TIE_MARGIN)
    assert not _beats(b, a, TIE_MARGIN)


def test_beats_refuses_an_unpaired_comparison():
    with pytest.raises(ValueError, match="same folds"):
        _beats([0.6, 0.6, 0.6], [0.5, 0.5], TIE_MARGIN)


# --- the seed count is able to fail ---

def test_too_thin_refuses_rather_than_warning():
    scores = _scores({"a": [0.6] * 4, "b": [0.5] * 4}, n_seeds=8)
    with pytest.raises(TooThin) as e:
        rank(scores)
    assert "8 distinct seeds" in str(e.value)
    assert str(MIN_SEEDS) in str(e.value)


def test_min_seeds_is_the_only_thing_standing_in_the_way():
    scores = _scores({"a": [0.6] * 4, "b": [0.5] * 4}, n_seeds=8)
    r = rank(scores, min_seeds=8)
    assert r.tiers == (("a",), ("b",))


def test_unpaired_detectors_are_refused():
    scores = _scores({"a": [0.6] * 4}) + [
        FoldScore(detector="b", fold=9, f1=0.5, seeds=(99,))]
    with pytest.raises(ValueError, match="not paired"):
        rank(scores)


# --- tiers ---

def test_indistinguishable_detectors_share_a_tier():
    r = rank(_scores({"a": [0.70, 0.65, 0.60, 0.64],
                      "b": [0.69, 0.64, 0.61, 0.63]}))
    assert len(r.tiers) == 1
    assert set(r.tiers[0]) == {"a", "b"}


def test_a_real_gap_produces_two_tiers():
    r = rank(_scores({"a": [0.80, 0.82, 0.79, 0.81],
                      "b": [0.50, 0.52, 0.49, 0.51]}))
    assert r.tiers == (("a",), ("b",))
    assert r.tier_of("a") == 1 and r.tier_of("b") == 2


def test_beats_cannot_cycle_because_the_margin_forces_a_mean_order():
    """The margin is not only noise suppression — it is what makes tiers exist.

    ``beats`` requires a mean-F1 lead over the margin, so a cycle a>b>c>a would
    need ``0 > 3 * TIE_MARGIN``. Hence the relation is acyclic and the tier
    decomposition always terminates. Checked by search as well as by argument,
    because the argument is the kind that is easy to state and easy to get
    wrong.
    """
    rng = random.Random(7)
    for _ in range(20000):
        n = rng.choice([3, 4, 5])
        f = {k: [rng.uniform(0.0, 1.0) for _ in range(n)] for k in "abc"}
        cycle = (_beats(f["a"], f["b"], TIE_MARGIN)
                 and _beats(f["b"], f["c"], TIE_MARGIN)
                 and _beats(f["c"], f["a"], TIE_MARGIN))
        assert not cycle, f"beats cycled on {f}"


def test_majority_alone_would_cycle_which_is_why_it_was_not_chosen():
    """The rejected 'majority only' rule admits Condorcet cycles.

    Three detectors, each beating the next on a majority of folds, going round.
    A rule that produced this would have to break the cycle arbitrarily and
    would call the result a ranking.
    """
    a = [0.9, 0.5, 0.7]
    b = [0.7, 0.9, 0.5]
    c = [0.5, 0.7, 0.9]

    def majority(x, y):
        return sum(p > q for p, q in zip(x, y)) * 2 > len(x)

    assert majority(a, b) and majority(b, c) and majority(c, a)
    # The shipped rule declines all three rather than picking one.
    assert not _beats(a, b, TIE_MARGIN)
    assert not _beats(b, c, TIE_MARGIN)
    assert not _beats(c, a, TIE_MARGIN)
    r = rank(_scores({"a": a, "b": b, "c": c}))
    assert len(r.tiers) == 1 and set(r.tiers[0]) == {"a", "b", "c"}


def test_a_negative_margin_is_refused():
    """The only door to a cycle, so it is shut at the front."""
    with pytest.raises(ValueError, match="tie_margin"):
        rank(_scores({"a": [0.6] * 4, "b": [0.5] * 4}), tie_margin=-0.1)


# --- D2: the probe gates, and breaks ties inside a tier ---

def test_probe_gate_removes_and_explains():
    r = rank(_scores({"rate": [0.9] * 4, "coact": [0.9] * 4},
                     probe={"rate": 9.0, "coact": 0.1}))
    assert "rate" not in [d for t in r.tiers for d in t]
    assert r.tier_of("rate") is None
    assert "promiscuity probe" in r.gated["rate"]
    assert "ceiling" in r.gated["rate"]


def test_probe_gate_can_be_disabled_explicitly():
    scores = _scores({"rate": [0.9] * 4, "coact": [0.9] * 4},
                     probe={"rate": 9.0, "coact": 0.1})
    r = rank(scores, max_probe_per_min=None)
    assert r.gated == {}
    assert "rate" in [d for t in r.tiers for d in t]


def test_unset_probe_gate_uses_the_benchs_own_ceilings():
    """The ranking and the calibration must refuse the same behaviour."""
    from bugarach.bench import MAX_PROBE_PER_MIN
    over = MAX_PROBE_PER_MIN["coact"] + 1.0
    r = rank(_scores({"coact": [0.9] * 4, "loco": [0.9] * 4},
                     probe={"coact": over, "loco": 0.0}))
    assert "coact" in r.gated


def test_tiebreak_orders_within_a_tier_by_probe():
    r = rank(_scores({"noisy": [0.70, 0.65, 0.60, 0.64],
                      "quiet": [0.69, 0.64, 0.61, 0.63]},
                     probe={"noisy": 0.9, "quiet": 0.05}))
    assert len(r.tiers) == 1
    assert r.tiers[0] == ("quiet", "noisy")


def test_tiebreak_cannot_promote_across_tiers():
    """A silent detector does not out-rank a good one.

    The tiebreak reads only inside a settled tier, so 'never fires' has to earn
    its way into the tier on F1 before its zero probe rate counts for anything.
    """
    r = rank(_scores({"good": [0.80, 0.82, 0.79, 0.81],
                      "silent": [0.10, 0.11, 0.09, 0.10]},
                     probe={"good": 0.9, "silent": 0.0}))
    assert r.tiers == (("good",), ("silent",))


# --- D5: timing gates, never ranks ---

def test_realtime_gate_removes_a_detector_that_cannot_keep_up():
    scores = _scores({"a": [0.9] * 4, "b": [0.9] * 4})
    scores = [FoldScore(**{**s.__dict__, "detect_x_realtime": 0.4})
              if s.detector == "b" else s for s in scores]
    r = rank(scores)
    assert "realtime" in r.gated["b"]
    assert r.tier_of("b") is None


def test_timing_never_changes_the_order():
    """Same F1, wildly different speed: still one tier, and speed is not the
    tiebreak — the probe is."""
    fast = _scores({"a": [0.70, 0.65, 0.60, 0.64]}, xrt=900000.0)
    slow = _scores({"b": [0.69, 0.64, 0.61, 0.63]}, xrt=2.0)
    r = rank(fast + slow)
    assert len(r.tiers) == 1
    assert set(r.tiers[0]) == {"a", "b"}


# --- D3: the axis is wired, disarmed, and reported ---

def test_distractor_gate_is_disarmed_by_default():
    """Everything fires on nearly every distractor today; a live gate would
    empty the field. See the todo the module docstring names."""
    r = rank(_scores({"a": [0.9] * 4, "b": [0.9] * 4}, distractor=1.0))
    assert r.gated == {}
    assert r.distractor["a"] == 1.0


def test_distractor_gate_works_once_armed():
    r = rank(_scores({"a": [0.9] * 4, "b": [0.9] * 4}, distractor=0.9),
             max_distractor_rate=0.5)
    assert "distractors" in r.gated["a"]


# --- reading the bake-off ---

@pytest.mark.skipif(not BAKEOFF.exists(), reason="bake-off not in the tree")
def test_the_shipped_bakeoff_is_refused_for_being_too_thin():
    """A fact about the file's seed count, not about any detector.

    The bake-off runs 8 seeds in 4 folds. The rule needs 12. This is the gate
    firing on real data, and it is the reason a re-run at 24 is the next step.
    """
    scores = fold_scores_from_bakeoff(BAKEOFF)
    with pytest.raises(TooThin):
        rank(scores)


@pytest.mark.skipif(not BAKEOFF.exists(), reason="bake-off not in the tree")
def test_bakeoff_conversions_come_from_the_files_own_spec():
    raw = json.loads(BAKEOFF.read_text())
    spec = raw["spec"]
    per_fold = raw["seeds_per_fold"]
    minutes = (spec["hot_window"][1] - spec["hot_window"][0]) / 60.0 * per_fold
    opportunities = spec["n_distractors"] * per_fold

    scores = fold_scores_from_bakeoff(raw)
    one = next(s for s in scores if s.detector == "coact" and s.fold == 0)
    src = next(p for p in raw["hand_written"]["coact"]["per_fold"] if p["fold"] == 0)

    assert one.hot_fa_per_min == pytest.approx(src["hot_fa"] / minutes)
    assert one.distractor_rate == pytest.approx(
        src["distractor_hits"] / opportunities)
    assert len(one.seeds) == per_fold


@pytest.mark.skipif(not BAKEOFF.exists(), reason="bake-off not in the tree")
def test_the_four_f1_could_not_separate_land_in_one_tier():
    """The brief's finding, as an output rather than a caveat.

    Read at the bake-off's own seed count, which the rule otherwise refuses --
    that refusal has its own test above. What is asserted is only that the rule
    declines to order these four, which is what every measurement in the brief
    said F1 cannot do.
    """
    r = rank(fold_scores_from_bakeoff(BAKEOFF), min_seeds=8)
    assert r.tiers[0] == tuple(sorted(
        r.tiers[0], key=lambda d: (r.probe[d], d))), "tier not in tiebreak order"
    assert {"coact", "loco", "tube", "tube_guard"} <= set(r.tiers[0])


@pytest.mark.skipif(not BAKEOFF.exists(), reason="bake-off not in the tree")
def test_rate_is_gated_out_of_the_shipped_bakeoff():
    """Independent confirmation of the bake-off's calibration defect.

    ``fair_bakeoff.py`` picks each fold's knob by raw argmax with no probe gate,
    so rate ships a setting that fires over its own ceiling. The ranking refuses
    it from the shipped file without re-running anything.
    """
    r = rank(fold_scores_from_bakeoff(BAKEOFF), min_seeds=8)
    assert "rate" in r.gated
    assert "promiscuity probe" in r.gated["rate"]


def test_table_names_the_tie_rule_it_applied():
    r = rank(_scores({"a": [0.9] * 4, "b": [0.5] * 4}))
    out = r.table()
    assert "tie = majority of folds" in out
    assert "reported, not gated" in out, "the disarmed axis must say so in the table"
