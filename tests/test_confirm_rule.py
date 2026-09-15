"""The confirmatory rule, exercised on hand-built readings — no recording, no randomness in the rule.

Each test names the defect the prose version of this rule had, found by the pre-registration's
two review rounds, and proves the code does not have it: overlapping results, gates that could
not fail, outcomes that got worse as evidence improved, an exclusion that skipped exactly the
failures it existed to catch.
"""

from __future__ import annotations

import itertools
import random

import pytest

from bugarach.confirm import rule as R
from bugarach.confirm.rule import (CellVerdict, CountReading, DestructionAtK, Interval,
                                   LeakReading, Outcome, Verdict)

V = Verdict
ALL = list(Verdict)


# -- building blocks --------------------------------------------------------------------------

def test_precedence_is_void_fail_undecided_pass():
    assert R.most_cautious([V.PASS, V.UNDECIDED]) is V.UNDECIDED
    assert R.most_cautious([V.UNDECIDED, V.FAIL]) is V.FAIL
    assert R.most_cautious([V.FAIL, V.VOID]) is V.VOID
    with pytest.raises(ValueError):
        R.most_cautious([])


def test_an_interval_cannot_be_inverted():
    with pytest.raises(ValueError):
        Interval(0.6, 0.5)


def test_family_alpha_is_the_signed_bonferroni():
    assert R.FAMILY_ALPHA == pytest.approx(0.05 / 3)
    assert R.GROUP_ALPHA == pytest.approx(0.05 / 3 / 4)


# -- leak -------------------------------------------------------------------------------------

GOOD_POS = Interval(0.60, 0.75)


def _leak(lo, hi, pos=GOOD_POS, flags=0):
    return R.leak_verdict(LeakReading(Interval(lo, hi), pos, flags))


def test_leak_passes_only_when_the_upper_bound_is_below_the_margin():
    assert _leak(0.48, 0.549) is V.PASS
    assert _leak(0.48, 0.55) is V.UNDECIDED          # at the margin is not below it


def test_leak_fails_only_when_the_lower_bound_is_above_the_margin():
    assert _leak(0.551, 0.62) is V.FAIL
    assert _leak(0.55, 0.62) is V.UNDECIDED


def test_a_positive_control_on_the_margin_voids_the_cell():
    assert _leak(0.48, 0.52, pos=Interval(0.55, 0.70)) is V.VOID
    assert _leak(0.48, 0.52, pos=Interval(0.551, 0.70)) is V.PASS


def test_the_negative_control_voids_at_four_flags_not_three():
    assert _leak(0.48, 0.52, flags=3) is V.PASS
    assert _leak(0.48, 0.52, flags=4) is V.VOID
    with pytest.raises(ValueError):
        _leak(0.48, 0.52, flags=21)


def test_a_void_control_beats_a_decided_leak_failure():
    # Prose defect: a cell could be FAIL and VOID at once, with no precedence.
    assert _leak(0.60, 0.70, flags=5) is V.VOID


def test_there_is_no_can_pass_override():
    # Prose defect: one noisy draw could turn a passing candidate UNDECIDED. The reading has
    # no field for it, so it cannot.
    assert not hasattr(LeakReading, "can_pass")


# -- count ------------------------------------------------------------------------------------

CONTROL_OK = Interval(-0.050, -0.035)


def test_count_passes_inside_the_tolerance_and_fails_wholly_outside():
    assert R.count_verdict(CountReading(Interval(-0.019, 0.019), CONTROL_OK)) is V.PASS
    assert R.count_verdict(CountReading(Interval(-0.03, -0.021), CONTROL_OK)) is V.FAIL
    assert R.count_verdict(CountReading(Interval(0.021, 0.03), CONTROL_OK)) is V.FAIL
    assert R.count_verdict(CountReading(Interval(-0.03, 0.0), CONTROL_OK)) is V.UNDECIDED


def test_count_has_a_decided_failure():
    # Prose defect: count had a pass rule and no failure rule, so it could never fail.
    assert R.count_verdict(CountReading(Interval(-0.10, -0.05), CONTROL_OK)) is V.FAIL


def test_a_control_that_is_not_wholly_outside_voids_the_count_gate():
    # edge_thinning at 1.6 s loses about 1.3 %: inside the band, so it cannot show the gate works.
    straddling = Interval(-0.025, -0.012)
    assert R.count_verdict(CountReading(Interval(-0.001, 0.001), straddling)) is V.VOID
    inside = Interval(-0.015, -0.011)
    assert R.count_verdict(CountReading(Interval(-0.001, 0.001), inside)) is V.VOID


# -- destruction ------------------------------------------------------------------------------

def _k(k, lo, hi, before=5.0, graded=0.3, homogeneous=0.01, do_nothing=0.99):
    return DestructionAtK(k, before, Interval(lo, hi), graded, homogeneous, do_nothing)


def test_destruction_passes_when_every_gated_k_is_below_the_ceiling():
    rows = [_k(3, 0.05, 0.20), _k(4, 0.02, 0.15)]
    assert R.destruction_block_verdict(rows) is V.PASS


def test_destruction_has_a_decided_failure():
    # Prose defect: destruction had no failure rule.
    rows = [_k(3, 0.05, 0.20), _k(4, 0.30, 0.45)]
    assert R.destruction_block_verdict(rows) is V.FAIL


def test_destruction_straddling_the_ceiling_is_undecided():
    assert R.destruction_block_verdict([_k(3, 0.20, 0.30)]) is V.UNDECIDED


def test_a_k_where_the_event_survived_the_shift_is_scored_not_skipped():
    # Prose defect: the saturation exclusion ungated exactly the K where the shifted event still
    # sat in one bin. Here that K retains 0.9 of its coordination; it must fail, not vanish.
    rows = [_k(3, 0.85, 0.95), _k(6, 0.01, 0.05)]
    assert R.destruction_block_verdict(rows) is V.FAIL


def test_invisible_or_ungraded_k_are_not_gated():
    invisible = _k(8, 0.9, 0.95, before=0.4)
    ungraded = _k(6, 0.9, 0.95, graded=0.03)
    assert not R.gated(invisible) and not R.gated(ungraded)
    assert R.destruction_block_verdict([invisible, ungraded, _k(3, 0.0, 0.1)]) is V.PASS


def test_no_gated_k_voids_the_block():
    assert R.destruction_block_verdict([_k(8, 0.0, 0.1, before=0.2)]) is V.VOID


def test_broken_machinery_controls_void_the_block():
    assert R.destruction_block_verdict([_k(3, 0.0, 0.1, homogeneous=0.2)]) is V.VOID
    assert R.destruction_block_verdict([_k(3, 0.0, 0.1, do_nothing=0.8)]) is V.VOID


def test_every_participation_and_bin_block_must_pass():
    ok = [_k(3, 0.0, 0.1)]
    bad = [_k(3, 0.4, 0.5)]
    assert R.destruction_verdict({(0.2, 1.0): ok, (0.5, 1.0): ok}) is V.PASS
    assert R.destruction_verdict({(0.2, 1.0): ok, (0.5, 2.0): bad}) is V.FAIL


# -- streams ----------------------------------------------------------------------------------

def _cell(v: Verdict) -> CellVerdict:
    return CellVerdict(v, V.PASS, V.PASS) if v is not V.PASS else CellVerdict(V.PASS, V.PASS, V.PASS)


def test_stream_verdict_is_defined_for_every_combination_of_cells():
    for combo in itertools.product(ALL, repeat=3):
        v = R.stream_verdict([_cell(x) for x in combo])
        assert isinstance(v, Verdict)
        if V.PASS in combo:
            assert v is V.PASS
        elif all(x is V.FAIL for x in combo):
            assert v is V.FAIL
        else:
            assert v in (V.VOID, V.UNDECIDED)


def test_a_void_or_undecided_cell_never_makes_a_stream_fail():
    for combo in itertools.product(ALL, repeat=3):
        if any(x in (V.VOID, V.UNDECIDED) for x in combo):
            assert R.stream_verdict([_cell(x) for x in combo]) is not V.FAIL


# -- outcome ----------------------------------------------------------------------------------

def _stream(*vs):
    return [_cell(v) for v in vs]


def _run(fast, slow, cossart=(V.PASS, V.PASS, V.PASS), groups=None):
    return R.outcome({"fast": fast, "slow": slow}, list(cossart), groups)


def test_viable_needs_both_streams_cossart_and_no_excluded_group():
    r = _run(_stream(V.PASS, V.FAIL, V.FAIL), _stream(V.FAIL, V.PASS, V.FAIL))
    assert r.outcome is Outcome.VIABLE and r.passing_streams == ("fast", "slow")


def test_cossart_passes_if_it_passes_at_any_position_a_lab_stream_passed():
    fast = _stream(V.FAIL, V.PASS, V.FAIL)          # passes at position 1
    slow = _stream(V.FAIL, V.FAIL, V.PASS)          # passes at position 2
    r = _run(fast, slow, cossart=(V.FAIL, V.PASS, V.FAIL))
    assert r.outcome is Outcome.VIABLE and r.cossart is V.PASS
    r = _run(fast, slow, cossart=(V.FAIL, V.VOID, V.PASS))
    assert r.outcome is Outcome.VIABLE
    r = _run(fast, slow, cossart=(V.PASS, V.FAIL, V.UNDECIDED))   # position 0 never passed in the lab
    assert r.outcome is Outcome.NARROWED and r.cossart is V.UNDECIDED


def test_a_smaller_passing_displacement_cannot_move_cossart_onto_a_void_position():
    # Found by the property test below, not by any reader: the amendment's "smallest passing
    # position" let one more passing lab cell turn VIABLE into NARROWED.
    slow = _stream(V.FAIL, V.PASS, V.FAIL)
    coss = (V.VOID, V.PASS, V.FAIL)
    assert _run(_stream(V.FAIL, V.PASS, V.FAIL), slow, coss).outcome is Outcome.VIABLE
    assert _run(_stream(V.PASS, V.PASS, V.FAIL), slow, coss).outcome is Outcome.VIABLE


def test_a_passing_stream_is_always_reported():
    # Prose defect: PASS with UNDECIDED or VOID fell into "nothing is read", worse than PASS
    # with FAIL.
    for other in ALL:
        r = _run(_stream(V.PASS, V.PASS, V.PASS), _stream(other, other, other))
        assert r.outcome in (Outcome.VIABLE, Outcome.NARROWED)
        assert "fast" in r.passing_streams


def test_a_group_excluded_by_its_lower_bound_narrows():
    both = _stream(V.PASS, V.FAIL, V.FAIL)          # passes at position 0 only
    r = _run(both, both, groups={"fast": {"DI": {0: 0.56}, "ORX": {0: 0.50}}})
    assert r.outcome is Outcome.NARROWED and r.excluded_groups == ("DI",)
    r = _run(both, both, groups={"fast": {"DI": {0: 0.55}}})     # at the margin: not excluded
    assert r.outcome is Outcome.VIABLE


def test_a_group_is_excluded_only_if_it_leaks_at_every_passing_position():
    both = _stream(V.PASS, V.PASS, V.FAIL)
    r = _run(both, both, groups={"slow": {"DI": {0: 0.60, 1: 0.52}}})
    assert r.outcome is Outcome.VIABLE
    r = _run(both, both, groups={"slow": {"DI": {0: 0.60, 1: 0.58}}})
    assert r.outcome is Outcome.NARROWED and r.excluded_groups == ("DI",)
    with pytest.raises(ValueError):
        _run(both, both, groups={"slow": {"DI": {0: 0.60}}})     # no bound at position 1


def test_stopped_needs_both_streams_to_fail_on_leak_or_destruction():
    failing = [CellVerdict(V.FAIL, V.PASS, V.PASS)] * 3
    assert _run(failing, failing).outcome is Outcome.STOPPED


def test_a_displacement_that_only_lost_counts_does_not_stop_the_goal():
    only_count = CellVerdict(V.PASS, V.FAIL, V.PASS)
    leak_fail = CellVerdict(V.FAIL, V.PASS, V.PASS)
    r = _run([leak_fail, leak_fail, only_count], [leak_fail] * 3)
    assert r.outcome is Outcome.FAILED_ON_COUNT


def test_unresolved_names_the_streams_that_may_be_rerun():
    r = _run(_stream(V.VOID, V.FAIL, V.VOID), _stream(V.UNDECIDED, V.FAIL, V.FAIL))
    assert r.outcome is Outcome.UNRESOLVED and r.rerun == ("fast",)


RANK = {Outcome.STOPPED: 0, Outcome.FAILED_ON_COUNT: 1, Outcome.UNRESOLVED: 2,
        Outcome.NARROWED: 3, Outcome.VIABLE: 4}


def _random_cell(rng):
    return CellVerdict(rng.choice(ALL), rng.choice(ALL), rng.choice(ALL))


FAVOURABLE = (Outcome.NARROWED, Outcome.VIABLE)


def test_every_combination_lands_in_one_outcome_and_better_evidence_never_hurts():
    # The property the prose could not hold (PASS beside UNDECIDED read worse than PASS beside
    # FAIL). 20,000 seeded random runs, each checked against every single-gate change to PASS.
    #
    # Stated precisely, because the first draft of this test was wrong: turning a VOID or
    # UNDECIDED gate into PASS may *reveal* a failure it was hiding — UNRESOLVED becoming
    # STOPPED is an instrument resolving, not the rule punishing evidence. So:
    #  * a FAIL gate becoming PASS never lowers the outcome's rank;
    #  * any gate becoming PASS never takes a favourable outcome (NARROWED, VIABLE) down, and
    #    never takes FAILED_ON_COUNT to STOPPED.
    rng = random.Random(20260914)
    for _ in range(20_000):
        fast = [_random_cell(rng) for _ in range(3)]
        slow = [_random_cell(rng) for _ in range(3)]
        coss = [rng.choice(ALL) for _ in range(3)]
        # Sparse on purpose: bounds that leak often make VIABLE rare, and a test that rarely
        # starts from VIABLE cannot see a rule that knocks VIABLE down. A dense version of this
        # line let two reverted rules pass unnoticed (the mutation check in this file's history).
        groups = (None if rng.random() < 0.5 else
                  {s: {g: {p: (0.60 if rng.random() < 0.15 else 0.50) for p in range(3)}
                       for g in ("DI", "MALE", "ORX", "OVX")} for s in R.STREAMS})
        _run = lambda f, s, c, _g=groups: R.outcome({"fast": f, "slow": s}, list(c), _g)  # noqa: E731
        base = _run(fast, slow, coss).outcome
        assert base in RANK
        for s_name, cells in (("fast", fast), ("slow", slow)):
            for i, c in enumerate(cells):
                for gate in ("leak", "count", "destruction"):
                    before = getattr(c, gate)
                    new = list(cells)
                    new[i] = CellVerdict(**{**c.__dict__, gate: V.PASS})
                    f2, s2 = (new, slow) if s_name == "fast" else (fast, new)
                    after = _run(f2, s2, coss).outcome
                    ctx = (fast, slow, coss, s_name, i, gate)
                    if before is V.FAIL:
                        assert RANK[after] >= RANK[base], ctx
                    if base in FAVOURABLE:
                        assert after in FAVOURABLE and RANK[after] >= RANK[base], ctx
                    if base is Outcome.FAILED_ON_COUNT:
                        assert after is not Outcome.STOPPED, ctx
        for i in range(3):
            c2 = list(coss)
            c2[i] = V.PASS
            assert RANK[_run(fast, slow, c2).outcome] >= RANK[base]


def test_adding_a_passing_position_never_adds_a_group_exclusion():
    # Exhaustive over which positions pass and a leak/no-leak bound per position.
    for pass_mask in itertools.product((V.PASS, V.FAIL), repeat=3):
        if V.PASS not in pass_mask:
            continue
        for leaks in itertools.product((0.50, 0.60), repeat=3):
            by_pos = dict(enumerate(leaks))
            cells = _stream(*pass_mask)
            base = R.excluded_groups({"fast": cells}, ["fast"], {"fast": {"DI": by_pos}})
            for i in range(3):
                if pass_mask[i] is V.FAIL:
                    more = list(pass_mask)
                    more[i] = V.PASS
                    after = R.excluded_groups({"fast": _stream(*more)}, ["fast"],
                                              {"fast": {"DI": by_pos}})
                    assert set(after) <= set(base), (pass_mask, leaks, i)


def test_adding_a_passing_position_never_worsens_the_cossart_reading():
    for pass_mask in itertools.product((V.PASS, V.FAIL), repeat=3):
        if V.PASS not in pass_mask:
            continue
        for coss in itertools.product(ALL, repeat=3):
            base = R.cossart_reading({"fast": _stream(*pass_mask)}, ["fast"], coss)
            for i in range(3):
                if pass_mask[i] is V.FAIL:
                    more = list(pass_mask)
                    more[i] = V.PASS
                    after = R.cossart_reading({"fast": _stream(*more)}, ["fast"], coss)
                    assert after <= base, (pass_mask, coss, i)


def test_the_outcome_refuses_malformed_input():
    good = _stream(V.PASS, V.PASS, V.PASS)
    with pytest.raises(ValueError):
        R.outcome({"fast": good}, [V.PASS] * 3)
    with pytest.raises(ValueError):
        R.outcome({"fast": good, "slow": good}, [V.PASS] * 2)
    with pytest.raises(ValueError):
        R.stream_verdict(good[:2])
