"""The replicate report's arithmetic, on synthetic runs — the page's numbers come from these helpers,
so each is checked against a hand-computed answer, including the cases the page exists to flag."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

TOOL = Path(__file__).resolve().parents[1] / "tools" / "make_replicate_report.py"


@pytest.fixture(scope="module")
def R():
    spec = importlib.util.spec_from_file_location("make_replicate_report", TOOL)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["make_replicate_report"] = mod
    spec.loader.exec_module(mod)
    return mod


def _seed(f1, *, failed=False, nan=False, seed=0):
    return dict(seed=seed, f1=f1, failed_training_signature=failed, f1_was_nan=nan)


def _learned(per_seed, key="k"):
    return dict(config_key=key, per_seed=per_seed, n_seeds=len(per_seed),
                f1_mean=sum(s["f1"] for s in per_seed) / len(per_seed))


def _run(tmp_path, name, *, seeds, cicada_refused=False, over=0):
    """A run with every net and coded detector over 4 outer folds, laid out as the tuner writes it.
    tube's F1-alone selection carries one failed refit and its budgeted one a refit that called
    nothing; every other net is clean."""
    folder = tmp_path / name
    learned = {}
    for net in ("chorus_norm", "chorus_gain_norm", "line_length", "tube"):
        folds = []
        for h in range(4):
            bad = net == "tube"
            ung = [_seed(0.125, failed=bad, seed=0), _seed(0.8, seed=1)] if bad else \
                  [_seed(0.7), _seed(0.7, seed=1)]
            gat = [_seed(0.0, nan=bad, seed=0), _seed(0.6, seed=1)] if bad else \
                  [_seed(0.6), _seed(0.6, seed=1)]
            g = _learned(gat)
            g["seeds_over_budget"] = over
            folds.append(dict(outer_fold=h, untuned=_learned([_seed(0.6), _seed(0.7, seed=1)]),
                              ungated=_learned(ung), gated=g))
        learned[net] = folds
    hand = {d: [dict(outer_fold=h,
                     ungated=dict(f1=0.5 + 0.1 * h, edge_flags={"merge_gap_sec": "high"}),
                     gated=dict(f1=0.4, edge_flags={}, over_budget=(d == "cicada")))
                for h in range(4)] for d in ("rate", "coact", "loco", "sce", "cicada", "sync")}
    folder.mkdir()
    (folder / "results.json").write_text(json.dumps(dict(learned=learned, hand=hand)))
    (folder / "meta.json").write_text(json.dumps(dict(declaration=dict(
        recording_seeds=seeds, replicate=seeds[0] // 1000 - 1, draw_seed=20260916, folds=4))))
    for h in range(4):
        sel = folder / "selections" / "gated" / f"outer{h}"
        sel.mkdir(parents=True)
        for d in hand:
            refused = d == "cicada" and cicada_refused
            n = 16 if refused else 30
            (sel / f"{d}.json").write_text(json.dumps(dict(n_scored=n,
                                                           n_refused=n if refused else 9)))
    return folder


def test_signs_and_powers_are_written_the_way_a_reader_writes_them(R):
    assert R.sgn(0.0123) == "+0.012"
    assert R.sgn(-0.0123) == "−0.012"          # a real minus sign, not a hyphen
    assert R.sgn(-0.0004) == "0.000"           # no "−0.000"
    assert R.sci(1e-5) == "10⁻⁵"
    assert R.sci(3e-5) == "3e-05"              # not a power of ten: left as it is


def test_a_fold_is_read_as_the_run_wrote_it(R, tmp_path):
    run = R.load_run(_run(tmp_path, "a", seeds=list(range(1000, 1048))))
    t = R.table(run)
    assert t[("tube", "untuned")] == [pytest.approx(0.65)] * 4
    assert t[("tube", "ungated")] == [pytest.approx((0.125 + 0.8) / 2)] * 4
    assert t[("coact", "ungated")] == pytest.approx([0.5, 0.6, 0.7, 0.8])
    # the tuner's no-admissible entry has no per_seed and no f1: it counts as 0.0, as the tuner does
    assert R.fold_f1(dict(config_key=None, f1_mean=0.0, note="no admissible configuration")) == 0.0


def test_flags_come_from_the_runs_own_seed_records(R, tmp_path):
    run = R.load_run(_run(tmp_path, "a", seeds=list(range(1000, 1048))))
    failed = R.seed_flags(run, "tube", "ungated")
    nothing = R.seed_flags(run, "tube", "gated")
    assert len(failed) == 4 and all(s["failed"] and s["f1"] == 0.125 for s in failed)
    assert len(nothing) == 4 and all(s["nothing"] for s in nothing)
    assert R.seed_flags(run, "chorus_norm", "ungated") == []


def test_one_rule_marks_the_table_and_the_between_draw_spread(R, tmp_path):
    run = R.load_run(_run(tmp_path, "a", seeds=list(range(1000, 1048)), cicada_refused=True))
    assert R.flagged(run, ("tube", "ungated")) and R.flagged(run, ("tube", "gated"))
    assert not R.flagged(run, ("tube", "untuned"))
    assert R.flagged(run, ("cicada", "gated")) and not R.flagged(run, ("cicada", "ungated"))
    assert not R.flagged(run, ("coact", "gated"))


def test_only_the_recordings_differ_between_two_draws(R, tmp_path):
    a = R.load_run(_run(tmp_path, "a", seeds=list(range(1000, 1048))))
    b = R.load_run(_run(tmp_path, "b", seeds=list(range(2000, 2048))))
    assert R.declaration_difference(a, b) == ["recording_seeds", "replicate"]


def test_a_search_that_refused_every_candidate_is_found_and_one_that_did_not_is_not(R, tmp_path):
    run = R.load_run(_run(tmp_path, "a", seeds=list(range(1000, 1048)), cicada_refused=True))
    got = R.refused_everything(run)
    assert set(got) == {("cicada", h) for h in range(4)}
    assert got[("cicada", 0)] == (16, 16)
    clean = R.load_run(_run(tmp_path, "b", seeds=list(range(2000, 2048))))
    assert R.refused_everything(clean) == {}


def test_held_out_compliance_is_what_the_run_wrote(R, tmp_path):
    run = R.load_run(_run(tmp_path, "a", seeds=list(range(1000, 1048)), over=1))
    c = R.held_out_compliance(run)
    assert c["tube"] == (4, 8, "refit seeds")           # 1 of 2 refits over, in each of 4 folds
    assert c["cicada"] == (4, 4, "folds") and c["coact"] == (0, 4, "folds")


def _merge_gap(net_f1, coact_f1, *, repro=0.0, chosen=8.0):
    """A matched-merge file as `fair_comparison_evidence.py merge-gap` writes it: one fold, both
    selections, every net at `net_f1(gap)` and CoactDetect at `coact_f1(gap)`."""
    gaps = ("2", "4", "8", "16")
    coded = [dict(outer_fold=0, selection=s, chosen_gap=chosen, run_f1=coact_f1("8"),
                  f1_by_gap={g: coact_f1(g) for g in ("0", "30") + gaps}, reproduces_run=0.0)
             for s in ("ungated", "gated")]
    nets = {n: [dict(outer_fold=0, selection=s, run_f1_mean=net_f1("2"),
                     f1_mean_by_gap={g: net_f1(g) for g in gaps},
                     per_seed=[dict(seed=0, reproduces_run=repro)])
                for s in ("ungated", "gated")]
            for n in ("chorus_norm", "chorus_gain_norm", "line_length", "tube")}
    return dict(net_gap_as_run_sec=2.0, coded=dict(coact=coded), nets=nets)


def _comparisons(per_fold):
    return {"results": {"comparisons": {s: {f"{n} - coact": dict(per_fold=per_fold)
                                            for n in ("chorus_norm", "chorus_gain_norm",
                                                      "line_length", "tube")}
                                        for s in ("ungated", "gated")}}}


def test_the_matched_merge_is_net_minus_coact_at_the_same_gap(R):
    net = {"2": 0.70, "4": 0.71, "8": 0.72, "16": 0.73}
    coact = {"0": 0.60, "2": 0.71, "4": 0.72, "8": 0.75, "16": 0.77, "30": 0.80}
    g = R.matched_gaps(_merge_gap(net.get, coact.get), _comparisons([0.70 - 0.75]))
    row = g[("chorus_norm", "gated")]
    assert row["run"][0] == pytest.approx(0.70 - 0.75)    # as run: the net at 2 s, CoactDetect at 8 s
    assert row[2][0] == pytest.approx(0.70 - 0.71)        # both at 2 s
    assert row[8][0] == pytest.approx(0.72 - 0.75)        # both at 8 s
    assert g["worst"] == 0.0 and g["inexact"] == set()


def test_a_matched_merge_file_that_is_not_the_same_comparison_is_refused(R):
    net = {"2": 0.70, "4": 0.71, "8": 0.72, "16": 0.73}.get
    coact = {"0": 0.6, "2": 0.71, "4": 0.72, "8": 0.75, "16": 0.77, "30": 0.8}.get
    with pytest.raises(AssertionError):                   # the re-decode does not reproduce the run
        R.matched_gaps(_merge_gap(net, coact, repro=0.01), _comparisons([-0.05]))
    with pytest.raises(AssertionError):                   # its as-run gap is not the run's own
        R.matched_gaps(_merge_gap(net, coact), _comparisons([-0.04]))
    with pytest.raises(AssertionError):                   # CoactDetect is not at the 8 s the page states
        R.matched_gaps(_merge_gap(net, coact, chosen=5.0), _comparisons([-0.05]))
    small = R.matched_gaps(_merge_gap(net, coact, repro=0.0007), _comparisons([0.70 - 0.75]))
    assert small["worst"] == pytest.approx(0.0007) and len(small["inexact"]) == 8


def _row(hit, planted, detected, fa, dense, tol=2.5):
    return dict(n_planted=planted, n_detected=detected, n_hit=hit, n_fa=fa, hot_fa=dense,
                distractor_hits=0, by_frac={"0.3": [planted, hit]}, tol_sec=tol)


def test_rows_pool_through_the_bench_and_precision_leaves_the_dense_stretch_out(R):
    from bugarach.bench import BenchResult
    t = R.pooled([_row(12, 15, 20, 8, 3), _row(12, 15, 20, 8, 3)])
    r, p, f1 = R.prf(t)
    ref = BenchResult(detector="x", regime="y", n_planted=30, n_detected=40, n_hit=24, n_fa=16,
                      hot_fa=6)
    assert (r, p, f1) == pytest.approx((ref.recall, ref.precision, ref.f1))
    assert p == pytest.approx(24 / 34)                    # the dense stretch is out of precision
    assert R.outside_fa(t) == pytest.approx(5.0)          # (16 - 6) calls over 2 recordings
    assert R.outside_fa(t) * t["n"] + t["dense"] == t["fa"]
    with pytest.raises(ValueError):                       # the bench refuses mixed tolerances
        R.pooled([_row(1, 1, 1, 0, 0, tol=2.5), _row(1, 1, 1, 0, 0, tol=1.0)])


def test_a_crowded_refusal_flags_the_entry_it_names_and_no_other(R, tmp_path):
    run = R.load_run(_run(tmp_path, "a", seeds=list(range(1000, 1048))))
    run["crowded"] = R.crowded_refused(dict(choices=[
        dict(detector="sce", selection="ungated", outer_fold=2, passes_veto=False),
        dict(detector="coact", selection="ungated", outer_fold=2, passes_veto=True)]))
    assert R.flagged(run, ("sce", "ungated")) and not R.flagged(run, ("sce", "gated"))
    assert not R.flagged(run, ("coact", "ungated"))


def test_a_value_off_the_axis_is_drawn_as_an_edge_triangle_not_a_dot(R):
    s = R.Svg(100, 50, "x")
    s.dot(-20, 10, 0, 100, 3, fill="red")
    s.dot(50, 10, 0, 100, 3, fill="red")
    marks = "".join(s.parts)                              # the drawing, without its shared defs
    assert marks.count("<path") == 1 and marks.count("<circle") == 1


def test_each_drawing_carries_its_own_ids_and_escapes_what_it_is_given(R):
    s1, s2 = R.Svg(100, 50, "a <b> & c"), R.Svg(100, 50, "second")
    s1.text(1, 2, "x < y & z")
    s1.rect(0, 0, 5, 5, fill="url(#hatch)")
    out1, out2 = s1.render(), s2.render()
    assert "x &lt; y &amp; z" in out1 and 'aria-label="a &lt;b&gt; &amp; c"' in out1
    assert f'url(#{s1.id}-hatch)' in out1 and s1.id != s2.id
    assert f'id="{s1.id}-hatch"' in out1 and f'id="{s1.id}-hatch"' not in out2
