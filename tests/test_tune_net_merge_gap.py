"""The nets' merge-gap re-selection keeps its own rules and reproduces the run it starts from.

The scoring needs the saved fits and branch ``tune-bench-comparison``'s tuning tool, neither of
which is here, so these tests read what the tool committed: every rule a reader relies on is
checked against that file and against the run's own ``results.json`` and selections beside it.
"""

from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
RUN = REPO / "docs" / "learned" / "tuned_vs_coact" / "fair_comparison_2026_09_18"
OUTPUTS = sorted(p.name for p in RUN.glob("*net_merge_gap.json"))


def _tool():
    spec = importlib.util.spec_from_file_location("tune_net_merge_gap_under_test",
                                                  REPO / "tools" / "tune_net_merge_gap.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


G = _tool()


@pytest.fixture(params=OUTPUTS)
def doc(request):
    return json.loads((RUN / request.param).read_text(encoding="utf-8"))


def test_both_draws_are_committed():
    assert OUTPUTS == ["net_merge_gap.json", "replicate_net_merge_gap.json"]


def test_every_fit_reproduces_the_run_at_two_seconds(doc):
    """pick_threshold at 20 frames returns each fit's own threshold, and the re-decoded rows and
    empty-recording counts at 2 s equal the run's score files, for every fit."""
    r = doc["reproduction"]
    assert r["fits"] > 0
    assert r["own_threshold_at_2s"] == r["fits"]
    assert r["rows_at_2s"] + r["rows_without_score_file"] == r["fits"]
    assert r["rows_without_score_file"] == 0
    assert r["empty_recordings_at_2s"] == r["fits"]


def test_the_starting_point_is_the_runs_own_choice(doc):
    for m, by_w in doc["nets"].items():
        for w, rows in by_w.items():
            for row in rows:
                assert row["as_run"]["gap_sec"] == doc["as_run_gap_sec"] == 2.0
                assert row["reproduces_run"]["inner_f1"] < 1e-12, (m, w, row["outer_fold"])
                assert row["reproduces_run"]["heldout_f1"] < 1e-12, (m, w, row["outer_fold"])


def test_a_move_gains_the_minimum_and_passes_the_crowded_check(doc):
    """Goal 1's move rule: leave the run's choice only for at least min_gain of inner F1, and never
    for a choice losing more than max_crowded_drop on the crowded recordings."""
    for m, by_w in doc["nets"].items():
        for w, rows in by_w.items():
            for row in rows:
                for v in ("config_kept", "config_rechosen"):
                    c = row[v]
                    assert c["gap_sec"] in doc["gaps_sec"]
                    if not c["moved"]:
                        assert c["gap_sec"] == 2.0 and c["config_key"] == row["as_run"]["config_key"]
                        assert c["inner_gain"] == 0
                        continue
                    assert c["inner_gain"] >= doc["min_gain"] - 1e-12, (m, w, v)
                    assert c["crowded_f1"] >= c["reference_crowded_f1"] - doc["max_crowded_drop"]
                    for refused in c["refused_by_crowded"]:
                        assert refused["crowded_f1"] < refused["reference_crowded_f1"] - doc["max_crowded_drop"]
                        assert refused["inner_f1"] >= c["inner_f1"]
                if row["config_kept"]["config_key"] != row["as_run"]["config_key"]:
                    pytest.fail(f"{m} {w} fold {row['outer_fold']}: the kept configuration changed")


def test_the_comparison_is_recomputed_from_the_folds_it_reports(doc):
    coact = doc["coact"]["f1"]
    for w, comp in doc["comparisons"].items():
        for name, c in comp.items():
            m, variant = name.split(" - ")[0].split(" ")
            nets = [(row[variant]["heldout"] or {}).get("f1_mean") for row in doc["nets"][m][w]]
            again = G._paired(nets, coact[w])
            assert again["per_fold"] == pytest.approx(c["per_fold"])
            assert again["folds_ahead"] == c["folds_ahead"]
            if c["t"] is not None:
                assert c["t_corrected"] == pytest.approx(c["t"] * math.sqrt(3 / 7))


def test_the_heldout_curve_agrees_with_the_chosen_gap(doc):
    """The curve holds the chosen threshold and moves only the gap, so it meets the chosen gap's
    held-out F1, and the as-run number only where the threshold did not move too."""
    for m, by_w in doc["nets"].items():
        for w, rows in by_w.items():
            for row in rows:
                c, a = row["config_kept"], row["as_run"]
                curve = c["heldout_f1_by_gap"]
                assert curve[f"{c['gap_sec']:g}"] == pytest.approx(c["heldout"]["f1_mean"])
                if c["threshold"] == a["threshold"]:
                    assert curve["2"] == pytest.approx(a["heldout"]["f1_mean"]), (m, w)
                elif not c["moved"]:
                    pytest.fail(f"{m} {w} fold {row['outer_fold']}: nothing moved, yet the "
                                "threshold differs from the run's")


def test_paired_statistics_by_hand():
    p = G._paired([0.8, 0.7, 0.9, 0.6], [0.7, 0.7, 0.8, 0.7])
    assert p["per_fold"] == pytest.approx([0.1, 0.0, 0.1, -0.1])
    assert p["mean"] == pytest.approx(0.025)
    assert p["folds_ahead"] == 2
    sd = math.sqrt(sum((x - 0.025) ** 2 for x in [0.1, 0.0, 0.1, -0.1]) / 3)
    assert p["t"] == pytest.approx(0.025 / (sd / 2))
    assert p["within_noise"] is False
    assert G._paired([0.5, 0.5], [0.495, 0.497])["within_noise"] is True


def test_the_gap_grid_spans_the_coded_range_and_holds_coactdetects_own_values():
    """What the grid actually promises. It is coarser than the union of the coded grids — the page
    says so — but it covers CoactDetect's values exactly and reaches the widest gap any of them had.
    The first draft's test only checked the top while the page claimed membership."""
    run_meta = json.loads((RUN / "meta.json").read_text())["declaration"]
    axes = {det: dict(ax) for det, ax in run_meta["hand_axes"].items()}
    coded = {g for ax in axes.values() for g in ax.get("merge_gap_sec", [])}
    assert max(coded) <= G.GAPS_SEC[-1] and min(coded) >= G.GAPS_SEC[0]
    assert set(axes["coact"]["merge_gap_sec"]) <= set(G.GAPS_SEC)
    assert not coded <= set(G.GAPS_SEC), "the grid now covers every coded value: say so on the page"
    assert G.AS_RUN_SEC in G.GAPS_SEC


def test_every_refit_carries_the_runs_own_failure_flags(doc):
    """A refit under LOW_F1 is a collapsed training or a refit that called nothing, and the run
    distinguishes them. The page may not call them all failed trainings."""
    seen = 0
    for m, by_w in doc["nets"].items():
        for w, rows in by_w.items():
            for row in rows:
                for v in ("as_run", "config_kept"):
                    held = row[v].get("heldout")
                    if held is None:
                        continue
                    for x in held["per_seed"]:
                        assert {"failed_training_signature", "f1_was_nan",
                                "threshold_at_grid_edge"} <= set(x), (m, w, v)
                        seen += 1
    assert seen > 0


def test_the_output_records_what_it_ran_on(doc):
    """The nets and the tuning tool live on another branch, so a reader cannot repeat this without
    the commit of both trees, the machine and the torch version."""
    p = doc["provenance"]
    assert p["host"] and p["torch"]
    assert p["this_tree"] and p["tuning_tree"], "a tree commit is missing"


def test_the_correction_is_derived_from_the_fold_count(doc):
    folds = {len(doc["comparisons"][w][k]["per_fold"]) for w in doc["comparisons"]
             for k in doc["comparisons"][w]}
    assert folds == {4}
    assert doc["nb_factor"] == pytest.approx(G.nb_factor(4))
    assert G.nb_factor(4) == pytest.approx(math.sqrt(3 / 7))
    assert G.nb_factor(5) != pytest.approx(G.nb_factor(4)), "the factor must move with the folds"
