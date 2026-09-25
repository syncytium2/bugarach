"""ADR-0010's search rulings in tools/search_all_settings.py, and its training switch in
tools/train_learned_on_bench.py: nothing changes unless the realistic bench is named, and when it
is, each ruling does what the record says.

The detectors are not run for the search rulings: the evaluator is injected, as in
``tests/test_search_all_settings.py``.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import search_all_settings as S  # noqa: E402
import train_learned_on_bench as T  # noqa: E402


@pytest.fixture
def off(monkeypatch):
    from bugarach import bench
    monkeypatch.delenv(bench.SPACING_ENV, raising=False)
    assert not S.realistic()


@pytest.fixture
def on(monkeypatch):
    from bugarach import bench
    monkeypatch.setenv(bench.SPACING_ENV, "realistic")
    assert S.realistic()


def _fake(f):
    return (lambda points: None,
            lambda d, p: dict(mean_f1=f(p), params=dict(p)),
            lambda d, s: True)


# ------------------------------------------------------------------ nothing changes unless named

def test_without_the_realistic_bench_every_old_rule_stands(off):
    # Extensions as before: contexts halve past 20 s, alpha divides by 3, no value cap.
    assert S.extend("context_win_sec", [20.0, 60.0, 120.0], low_end=True) == 10.0
    assert S.extend("context_win_sec", [20.0, 60.0, 120.0], low_end=False) == 240.0
    assert S.extend("alpha", [1e-4, 1e-3], low_end=True) == pytest.approx(1e-4 / 3)
    # The context-versus-spacing rule still refuses a context wider than the planted spacing.
    p = dict(S._bench.OPERATING_POINTS["coact"].params, context_win_sec=240.0)
    assert not S.valid("coact", p)
    # And a candidate at a zero guard is only "limit", with no ruling-5 finding attached.
    br = S.bracketing("coact", {"guard_sec": 0.0, "alpha": 1e-4},
                      {"guard_sec": [0.0, 2.0, 4.0], "alpha": [1e-5, 1e-4, 1e-3]},
                      {"guard_sec": [0.0, 2.0, 4.0]}, 6)
    assert "findings" not in br and br["only_at_limits"] is True


def test_the_spacing_is_the_one_switch(monkeypatch):
    """#828's BUGARACH_REALISTIC and a bench module's REALISTIC attribute are retired: the spacing
    alone names the rulings, and the ORX spacing runs under them too."""
    from bugarach import bench
    monkeypatch.delenv(bench.SPACING_ENV, raising=False)
    monkeypatch.setenv("BUGARACH_REALISTIC", "1")
    monkeypatch.setattr(S._bench, "REALISTIC", True, raising=False)
    assert not S.realistic()
    monkeypatch.setenv(bench.SPACING_ENV, "orx")
    assert S.realistic()


# ------------------------------------------------------------------ ruling 7: contexts, LoCo

def test_contexts_stay_between_20_and_120_seconds(on):
    assert S.extend("context_win_sec", [20.0, 60.0, 120.0], low_end=True) is None
    assert S.extend("context_win_sec", [30.0, 60.0], low_end=True) == 20.0
    assert S.extend("context_win", [30.0, 60.0], low_end=True) == 20.0
    assert S.extend("context_win_sec", [20.0, 120.0], low_end=False) is None
    assert S.extend("context_win_sec", [20.0, 90.0], low_end=False) == 120.0
    space = S.realistic_space({"loco": {"context_win_sec": [5.0, 10.0, 20.0, 120.0, 240.0],
                                        "threshold_pctile": [97.0, 99.5],
                                        "merge_gap_sec": [1.0, 2.0]}})
    assert space["loco"]["context_win_sec"] == [20.0, 120.0]
    assert "threshold_pctile" not in space["loco"], "ruling 7: LoCo's threshold leaves"
    assert S.realistic_pairs({"loco": ("threshold_pctile", "context_win_sec"),
                              "coact": ("alpha", "context_win_sec")},
                             {"loco": space["loco"],
                              "coact": {"alpha": [1e-4], "context_win_sec": [60.0]}}) \
        == {"coact": ("alpha", "context_win_sec")}


def test_a_long_context_is_valid_on_the_realistic_bench(on):
    """ADR-0010 part 4 retires the context-versus-spacing rule; 120 s is still the ceiling,
    held by the grid, not by this rule."""
    p = dict(S._bench.OPERATING_POINTS["coact"].params, context_win_sec=120.0, guard_sec=0.0)
    assert S.valid("coact", p)


# ------------------------------------------------------------------ ruling 6: alpha's cap

def test_alpha_extends_tenfold_to_about_8_sd_and_no_further(on):
    assert S.ALPHA_CAP == pytest.approx(0.5 * math.erfc(8 / math.sqrt(2)), rel=0.05)
    assert S.extend("alpha", [1e-4, 1e-3], low_end=True) == pytest.approx(1e-5)
    assert S.extend("alpha", [1e-15, 1e-4], low_end=True) == pytest.approx(S.ALPHA_CAP)
    assert S.extend("alpha", [S.ALPHA_CAP, 1e-4], low_end=True) is None


def test_alpha_runs_to_its_cap_past_the_extension_count_and_is_a_finding(on):
    """A score that keeps rising as alpha falls: the search walks alpha down past
    ``max_extensions`` to the value cap, and the result says so as a finding, not a tuned
    value (rulings 5 and 6)."""
    ev, summ, adm = _fake(lambda p: -math.log10(p["alpha"]))
    space = {"coact": {"alpha": [1e-4, 1e-3]}}
    state, _, grown = S.coordinate_rounds(["coact"], {"coact": {"alpha": 1e-4}}, space,
                                          ev, summ, adm, log=lambda *_: None, max_extensions=2)
    assert state["coact"]["alpha"] == pytest.approx(S.ALPHA_CAP)
    br = S.bracketing("coact", state["coact"], grown["coact"], space["coact"], 2)
    assert br["unbracketed_axes"]["alpha"]["reason"] == "cap"
    assert br["findings"] == [dict(setting="alpha", value=state["coact"]["alpha"], kind="cap")]
    assert br["bracketed"] is False and br["adoptable_blocked"] is True


def test_without_the_realistic_bench_alpha_still_stops_at_the_count(off):
    ev, summ, adm = _fake(lambda p: -math.log10(p["alpha"]))
    state, _, _ = S.coordinate_rounds(["coact"], {"coact": {"alpha": 1e-4}},
                                      {"coact": {"alpha": [1e-4, 1e-3]}}, ev, summ, adm,
                                      log=lambda *_: None, max_extensions=2)
    assert state["coact"]["alpha"] == pytest.approx(1e-4 / 9)


# ------------------------------------------------------------------ ruling 5: off-limits

@pytest.mark.parametrize("det,setting,value,grid", [
    ("coact", "guard_sec", 0.0, [0.0, 2.0, 4.0]),
    ("sync", "C_min", 0.0, [0.0, 0.01, 0.03]),
    ("rate", "merge_gap_s", 0.0, [0.0, 4.0, 8.0]),
    ("cicada", "n_synchronous_frames", 1, [1, 2, 5]),
])
def test_a_best_value_at_its_off_limit_is_a_finding_and_never_adoptable(on, det, setting,
                                                                         value, grid):
    br = S.bracketing(det, {setting: value}, {setting: grid}, {setting: grid}, 6)
    assert br["findings"] == [dict(setting=setting, value=value, kind="off_limit")]
    assert br["bracketed"] is False and br["adoptable_blocked"] is True
    # The looser reading ("a limit counts as a bracket") cannot rescue it either.
    assert br["only_at_limits"] is False


def test_no_merge_is_an_off_limit_although_the_grid_ends_never_see_it(on):
    br = S.bracketing("sce", {"merge_gap_sec": float("nan"), "bin_width_sec": 2.0},
                      {"merge_gap_sec": [5.0, 10.0], "bin_width_sec": [1.0, 2.0, 5.0]},
                      {"merge_gap_sec": [5.0, 10.0], "bin_width_sec": [1.0, 2.0, 5.0]}, 6)
    assert [f["setting"] for f in br["findings"]] == ["merge_gap_sec"]
    assert br["bracketed"] is False


def test_an_interior_value_is_still_bracketed(on):
    br = S.bracketing("coact", {"guard_sec": 2.0}, {"guard_sec": [0.0, 2.0, 4.0]},
                      {"guard_sec": [0.0, 2.0, 4.0]}, 6)
    assert br["bracketed"] is True and br["findings"] == []


def test_one_step_off_is_inward():
    assert S.step_off("guard_sec", 0.0, [0.0, 2.0, 4.0]) == 2.0
    assert S.step_off("alpha", S.ALPHA_CAP, [S.ALPHA_CAP, 1e-15, 1e-4]) == 1e-15
    assert S.step_off("context_win_sec", 120.0, [20.0, 60.0, 120.0]) == 60.0
    assert S.step_off("merge_gap_sec", float("nan"), [10.0, 5.0]) == 5.0
    assert S.step_off("guard_sec", 0.0, [0.0]) is None


def test_ruling_5_check_reports_whether_calls_change_one_step_off(monkeypatch):
    """A planted case: the calls at the limit and one step off are compared per recording, and
    the record says how many recordings changed."""
    same = {("baseline_quiet", 1): True, ("baseline_busy", 1): False}

    class Pool:
        def imap_unordered(self, fn, jobs, chunksize=1):
            for det, a, b, regime, seed in jobs:
                assert dict(a)["guard_sec"] == 0.0 and dict(b)["guard_sec"] == 2.0
                yield dict(n_a=3, n_b=3 if same.get((regime, seed), True) else 2,
                           same=same.get((regime, seed), True))

    monkeypatch.setattr(S, "N_STEP_OFF_SEEDS", 1)
    params = dict(S._bench.OPERATING_POINTS["coact"].params, guard_sec=0.0,
                  context_win_sec=60.0)
    rows = S.ruling_5_checks(Pool(), "coact", params,
                             [dict(setting="guard_sec", value=0.0, kind="off_limit")],
                             {"guard_sec": [0.0, 2.0, 4.0]}, [1, 2], log=lambda *_: None)
    assert rows[0]["step_value"] == 2.0 and rows[0]["recordings"] == 2
    assert rows[0]["recordings_changed"] == 1 and rows[0]["changed"] is True
    assert rows[0]["calls_at_limit"] == 6 and rows[0]["calls_one_step_off"] == 5


def test_a_ruling_5_check_that_compared_nothing_says_so(monkeypatch):
    """Every comparison refused is not "no change": `changed` stays None, the refusal named."""
    class Pool:
        def imap_unordered(self, fn, jobs, chunksize=1):
            for _ in jobs:
                yield dict(refused="ValueError: a guard needs the max-left null")

    monkeypatch.setattr(S, "N_STEP_OFF_SEEDS", 1)
    params = dict(S._bench.OPERATING_POINTS["coact"].params, guard_sec=0.0,
                  context_win_sec=60.0)
    row = S.ruling_5_checks(Pool(), "coact", params,
                            [dict(setting="guard_sec", value=0.0, kind="off_limit")],
                            {"guard_sec": [0.0, 2.0]}, [1], log=lambda *_: None)[0]
    assert row["changed"] is None and row["recordings_compared"] == 0
    assert row["refused"] == ["ValueError: a guard needs the max-left null"]


# ------------------------------------------------------------------ ruling 8: the guard cap

def test_the_guard_cap_holds_on_every_search_path_for_every_detector_with_a_guard(on):
    """A guard over a quarter of its context is refused by `valid` (rounds, pairs, full grid)
    and by `choose_settings`' default rule, on all three benches."""
    import importlib

    for mod in ("bugarach.bench", "bugarach.bench_slow", "bugarach.bench_combined"):
        b = importlib.import_module(mod)
        for det, axes in b.FULL_GRIDS.items():
            if "guard_sec" not in axes:
                continue
            ctx = "context_win" if "context_win" in b.OPERATING_POINTS[det].params \
                or "context_win" in axes else "context_win_sec"
            p = dict(b.OPERATING_POINTS[det].params, **{ctx: 20.0, "guard_sec": 8.0})
            assert not b.settings_are_valid(det, p), (mod, det)
            ok = dict(p, guard_sec=4.0)
            assert b.settings_are_valid(det, ok) or det == "loco", (mod, det)


# ------------------------------------------------------------------ training

def test_training_is_unchanged_unless_the_realistic_bench_is_named():
    from bugarach import bench

    assert T.seed_sets("fast", False) == (T.FIT, T.TEST, T.NULLS)
    assert T.seed_sets("slow", True) == (T.FIT, T.TEST, T.NULLS)
    rec = T.training_recording(bench, False)
    s1, g1 = rec(1000)
    s2, g2 = bench.make_recording("baseline_quiet", 1000)
    assert [e.time for e in g1.events] == [e.time for e in g2.events]
    assert T.config("chorus_norm") == T.CONFIGS["chorus_norm"]


def test_fast_seeds_double_on_the_realistic_bench():
    fit, test, nulls = T.seed_sets("fast", True)
    assert len(fit) == 2 * len(T.FIT) and len(test) == 2 * len(T.TEST)
    assert len(nulls) == 2 * len(T.NULLS)


def test_every_panel_model_trains_with_its_base_configuration():
    from bugarach.learn.nets import ARCHITECTURES

    for m in T.MODELS:
        assert m in ARCHITECTURES, m
        ARCHITECTURES[m].make(**T.config(m))
    assert T.config("chorus_gain_norm_part") == T.CONFIGS["chorus_gain_norm"]
    assert T.config("tube_part") == {}


def test_realistic_training_recordings_carry_the_boundary_events():
    from bugarach import bench

    s, gt = T.training_recording(bench, True)(1000)
    bp = gt.params["boundary_planting"]
    assert [c - bp["planned_floor"] for c in bp["counts"]] == [-1, 0, 1]
