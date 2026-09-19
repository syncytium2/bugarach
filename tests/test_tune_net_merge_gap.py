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


def test_the_gap_grid_reaches_every_gap_a_coded_detector_was_allowed():
    run_meta = json.loads((RUN / "meta.json").read_text())["declaration"]
    coded_tops = [dict(ax)["merge_gap_sec"][-1] for det, ax in run_meta["hand_axes"].items()
                  if "merge_gap_sec" in dict(ax)]
    assert max(coded_tops) <= G.GAPS_SEC[-1]
    assert G.AS_RUN_SEC in G.GAPS_SEC
