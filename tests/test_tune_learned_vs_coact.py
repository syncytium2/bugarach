"""The tuning tool's guarantees, on one ``--quick`` run of ``tube`` and CoactDetect on the bench.

``tools/tune_learned_vs_coact.py`` runs overnight with nobody watching, and a defect in it
would cost the night and possibly the comparison. Each test is one requirement from
``HANDOFF-workstation-tuning.md`` (*Gate 2*), from the storage rule the Mac unsupervised
session carried from Tony on 2026-09-16 (tuned parameters stored persistently, rationally and
separably), or from the four decisions for goal 2's next comparison on the bench
(``docs/goals/learned-model-family.md``, Tony, 2026-09-17). The run is made once, by the command
line, because the tool's workers are spawned processes that must import it as a script.
"""

from __future__ import annotations

import importlib.util
import itertools
import json
import os
import random
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parent.parent
TOOL = REPO / "tools" / "tune_learned_vs_coact.py"


def _load_tool():
    spec = importlib.util.spec_from_file_location("tune_learned_vs_coact_under_test", TOOL)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


T = _load_tool()


def _run_cli(out: Path) -> str:
    env = dict(os.environ, PYTHONPATH=str(REPO / "src"))
    res = subprocess.run([sys.executable, str(TOOL), "--out", str(out), "--jobs", "4", "--quick",
                          "--models", "tube", "--detectors", "coact", "--simulation", "bench"],
                         capture_output=True, text=True, env=env, cwd=REPO, timeout=600)
    assert res.returncode == 0, res.stdout + res.stderr
    return res.stdout


@pytest.fixture(scope="module")
def run(tmp_path_factory):
    out = tmp_path_factory.mktemp("tune") / "run"
    first = _run_cli(out)
    plan = T.Plan(quick=True, models=("tube",), detectors=("coact",), simulation="bench")
    return dict(out=out, plan=plan, first=first)


def _json(p):
    return json.loads(Path(p).read_text())


def _seeds(names):
    return {T.seed_of(n) for n in names}


def test_no_held_out_recording_or_its_twin_reaches_a_fit_a_threshold_a_budget_or_a_selection(run):
    out, plan = run["out"], run["plan"]
    offset = T.NULL_SEED_OFFSET
    for rp in (out / "fits").rglob("*.run.json"):
        r = _json(rp)
        assert set(r["fitted_recordings"]) <= set(r["recordings"])
        assert set(r["threshold_recordings"]) <= set(r["recordings"])
        stem = rp.name[: -len(".run.json")]
        for sp in (out / "scores" / rp.parent.relative_to(out / "fits")).glob(f"{stem}__fold*.json"):
            scored = _seeds(_json(sp)["rows"])
            assert scored and not scored & _seeds(r["recordings"]), sp
    meta = _json(out / "meta.json")
    for h in plan.folds():
        test = set(plan.split.test(h))
        b = meta["budgets"][str(h)]
        assert not set(b["recording_seeds"]) & test
        assert not {s - offset for s in b["twin_seeds"]} & test
        for w in T.SELECTIONS:
            for name in ("tube", "coact"):
                pooled = _json(T.selection_path(out, w, h, name))["pooled"]
                used = set(pooled["recording_seeds"]) | _seeds(pooled.get("fitted_on", []))
                assert not used & test, (w, h, name)
                assert all(s >= offset for s in pooled["twin_seeds"]), "twin seeds carry the offset"
                assert not {s - offset for s in pooled["twin_seeds"]} & test, (w, h, name)


def test_a_rerun_resumes_and_runs_nothing(run):
    assert "ran 0 jobs" in _run_cli(run["out"])


def test_the_draw_is_the_declared_procedure():
    for model in T.MODELS:
        axes = T.LEARNED_AXES[model]
        names = [a for a, _ in axes]
        every = [dict(zip(names, v)) for v in itertools.product(*[vals for _, vals in axes])]
        untuned = {k: float(v) for k, v in T.UNTUNED[model].items()}
        rest = [c for c in every if {k: float(v) for k, v in c.items()} != untuned]
        expected = random.Random(20260916).sample(rest, 23)
        got = T.draw(model)
        assert len(got) == 24 and got[:23] == expected and got[23] == T.UNTUNED[model]
        assert len({json.dumps(c, sort_keys=True) for c in got}) == 24


def test_an_inner_fit_reached_from_two_outer_folds_is_trained_once_and_scored_twice(run):
    out, plan = run["out"], run["plan"]
    inner = [r for r in (out / "fits").rglob("*.run.json") if _json(r)["role"] == "inner"]
    assert inner
    for rp in inner:
        stem = rp.name[: -len(".run.json")]
        folder = rp.parent
        assert len(list(folder.glob(f"{stem}.json"))) == 1
        scores = list((out / "scores" / folder.relative_to(out / "fits")).glob(f"{stem}__fold*.json"))
        assert len(scores) == 2, (stem, scores)
    fold0 = plan.fold_recordings([0])
    readers = [h for h in plan.folds()
               if set(fold0) <= set(_json(T.selection_path(out, "ungated", h, "tube"))["pooled"]["fitted_on"])]
    assert readers == [1, 2]


def test_decoding_at_the_fits_own_threshold_reproduces_trained_predict(run):
    from bugarach.learn import checkpoint

    ck = next(p for p in (run["out"] / "fits").rglob("*.json") if not p.name.endswith(".run.json"))
    tr = checkpoint.load(ck)
    sl, _ = T._planted(run["plan"].sim, "busy:1000")
    p, enc = T.probabilities(tr, sl)
    mine = T.decode_at(tr, p, enc, tr.threshold)
    theirs, _ = tr.predict(sl)
    assert np.array_equal(mine.onset_sec, theirs.onset_sec)
    assert np.array_equal(mine.width_sec, theirs.width_sec)


def test_pooling_stored_rows_equals_pooling_live_scores(run):
    from bugarach.bench import pool_scores, run_detector
    from bugarach.score import score_stream

    out, plan = run["out"], run["plan"]
    conf = plan.hand["coact"][0]
    doc = _json(T.hand_score_path(out, "coact", conf["config_key"]))
    names = plan.recordings(plan.split.seeds)
    live = []
    for rid in names:
        sl, gt = T._planted(plan.sim, rid)
        live.append(score_stream(gt, run_detector("coact", sl, **conf["params"])))
    a = pool_scores(live, detector="coact", regime="tuning")
    b = T.pooled([doc["rows"][rid] for rid in names], "coact")
    for field in ("n_planted", "n_detected", "n_hit", "n_fa", "hot_fa", "distractor_hits"):
        assert getattr(a, field) == getattr(b, field), field
    assert a.by_frac == b.by_frac
    assert (np.isnan(a.f1) and np.isnan(b.f1)) or a.f1 == b.f1


def test_eight_and_eight_point_zero_are_one_configuration():
    from bugarach.learn.checkpoint import config_key

    a = T.learned_config("chorus_gain_norm", dict(lr=1e-2, steps=900, roi_width=4, roi_depth=4,
                                                  top_m=4, vote_gain=8), index=0, is_untuned=False)
    b = T.learned_config("chorus_gain_norm", dict(lr=0.01, steps=900.0, roi_width=4.0,
                                                  roi_depth=4, top_m=4, vote_gain=8.0),
                         index=0, is_untuned=False)
    assert a["config_key"] == b["config_key"]
    assert config_key("tube", {"max_ratio": 40}) == config_key("tube", {"max_ratio": 40.0})


def test_every_checkpoint_is_the_configuration_its_key_declares(run):
    from bugarach.learn.checkpoint import canonical, config_key

    out = run["out"]
    choices = ("optimizer", "lr", "steps", "crop_frames", "batch", "n_train")
    checked = 0
    for root in (out / "fits", out / "chosen"):
        for p in root.rglob("*.json"):
            if p.name.endswith(".run.json"):
                continue
            doc = _json(p)
            conf = _json(T.config_path(out, doc["arch"], doc["config_key"]))
            assert canonical(doc["cfg"]) == canonical(conf["cfg"]), p
            assert {k: canonical(doc["training"][k]) for k in choices} == \
                {k: canonical(conf["training"][k]) for k in choices}, p
            assert config_key(doc["arch"], doc["cfg"], doc["training"]) == doc["config_key"], p
            if root.name == "fits":
                assert p.parent.name == doc["config_key"], p
            checked += 1
    assert checked > 0


def test_a_chosen_checkpoint_reloaded_in_a_fresh_process_reproduces_its_held_out_rows(run):
    out, plan = run["out"], run["plan"]
    h, seed = 0, 0
    sel = _json(T.selection_path(out, "gated", h, "tube"))
    assert sel["config_key"]
    chosen = T.chosen_path(out, "gated", h, "tube", seed)
    recs = plan.fold_recordings(plan.training_folds(h))
    stored = _json(T.score_path(out, "tube", sel["config_key"], seed, recs, h))
    code = (
        "import json\n"
        "from bugarach.bench import make_recording\n"
        "from bugarach.learn import checkpoint\n"
        "from bugarach.score import score_stream\n"
        f"regimes = {T.BENCH_REGIMES!r}\n"
        f"tr = checkpoint.load({str(chosen)!r})\n"
        "rows = {}\n"
        f"for rid in {plan.recordings(plan.split.test(h))!r}:\n"
        "    background, seed = rid.split(':')\n"
        "    sl, gt = make_recording(regimes[background], int(seed))\n"
        "    sc = score_stream(gt, tr.predict(sl)[0])\n"
        "    rows[rid] = dict(n_planted=sc.n_planted, n_detected=sc.n_detected, n_hit=sc.n_hit,\n"
        "                        n_fa=sc.n_fa, hot_fa=sc.hot_fa, distractor_hits=sc.distractor_hits)\n"
        "print(json.dumps(rows))\n")
    res = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=REPO,
                         env=dict(os.environ, PYTHONPATH=str(REPO / "src")), timeout=300)
    assert res.returncode == 0, res.stderr
    fresh = json.loads(res.stdout.strip().splitlines()[-1])
    ti = sel["threshold_index"]
    for s, row in fresh.items():
        want = {k: stored["rows"][s][ti][k] for k in row}
        assert row == want, (s, row, want)


def test_a_chosen_settings_file_round_trips_the_sliding_parameters(run):
    from bugarach.detect_folder import load_settings

    out, plan = run["out"], run["plan"]
    for w in T.SELECTIONS:
        sel = _json(T.selection_path(out, w, 0, "coact"))
        if sel["config_key"] is None:
            continue
        params, provenance = load_settings(T.chosen_path(out, w, 0, "coact"))
        declared = _json(T.config_path(out, "coact", sel["config_key"]))["params"]
        (got,) = params.values()
        assert got == declared
        assert got["window_mode"] == "sliding"
        (prov,) = provenance.values()
        assert prov["fitted_config_key"] == sel["config_key"]


# ---- goal 2's next comparison on the bench (Tony, 2026-09-17) ----------------------------------

def test_training_is_half_quiet_half_busy_and_the_threshold_pair_is_one_of_each():
    """Decision 2, checked at full size: quick mode fits on one recording and cannot show it."""
    from bugarach.learn.train import TRAIN_SEED_BLOCK, VAL_SEED_BLOCK, fold_maker

    plan = T.Plan(quick=False, models=("tube",), detectors=("coact",), simulation="bench")
    for train_folds in ([0, 1], [0, 1, 2]):                 # an inner fit, and an outer refit
        recs = plan.fold_recordings(train_folds)
        mk, n_fit, n_val = fold_maker(lambda r: (r, None), recs)
        picked = {mk(VAL_SEED_BLOCK + i)[0] for i in range(4)}
        assert sorted(T.regime_of(r) for r in picked) == ["busy", "quiet"], picked
        for seed in plan.refit_seeds:
            fitted = [mk(TRAIN_SEED_BLOCK + seed * 1000 + i)[0] for i in range(plan.n_train)]
            counts = {b: sum(T.regime_of(r) == b for r in fitted) for b in ("quiet", "busy")}
            assert counts == {"quiet": 5, "busy": 5}, (train_folds, seed, fitted)
            assert not set(fitted) & picked


def test_the_score_is_each_backgrounds_pooled_f1_averaged():
    """Decision 1: goal 1's rule. A model perfect on quiet and blind on busy scores one half."""
    def row(n_hit, n_detected):
        return dict(n_planted=10, n_detected=n_detected, n_hit=n_hit, n_fa=n_detected - n_hit,
                    hot_fa=0, distractor_hits=0, by_frac={}, tol_sec=None)
    items = [("quiet:1000", row(10, 10)), ("busy:1000", row(0, 0)),
             ("quiet:1001", row(10, 10)), ("busy:1001", row(0, 0))]
    assert T.objective(items) == pytest.approx(0.5)
    assert T.objective([("1000", row(10, 10)), ("1001", row(0, 0))]) == \
        pytest.approx(T.f1_or_zero(T.pooled([row(10, 10), row(0, 0)])))   # home: pooled, as before


def test_the_probe_budget_holds_at_every_background(run):
    """Decision 3: the bench's probe, per background; one background over budget refuses."""
    meta = _json(run["out"] / "meta.json")
    for h, b in meta["budgets"].items():
        assert set(b["probe_per_hour"]) == {"quiet", "busy"}
        assert b["gate_empty_recording"] == "null_quiet"
        ok = {k: v * 0.5 for k, v in b["probe_per_hour"].items()}
        assert T.within(b, ok, 0.0)
        assert not T.within(b, dict(ok, busy=b["probe_per_hour"]["busy"] * 2), 0.0)
        assert not T.within(b, ok, b["quiet_per_hour"] * 2)


def test_the_declaration_writes_out_the_backgrounds_the_empty_recordings_and_the_reference(run):
    """Decisions 1, 3 and 4 as the run recorded them, before any fit."""
    from bugarach import bench

    d = _json(run["out"] / "meta.json")["declaration"]
    assert d["simulation"] == "bench"
    assert {b: v["bg_rate_hz"] for b, v in d["backgrounds"].items()} == \
        {b: bench.REGIMES[r]["bg_rate_hz"] for b, r in T.BENCH_REGIMES.items()}
    assert d["gate_empty_recording"] == "null_quiet" and d["reported_only_empty_recordings"] == ["null_busy"]
    assert d["empty_recordings"]["null_quiet"]["bg_rate_hz"] == bench.NULL_RECORDING["bg_rate_hz"]
    assert d["reference"]["params"] == json.loads(json.dumps(bench.OPERATING_POINTS["coact"].params))
    score = next((run["out"] / "scores" / "tube").rglob("*__fold*.json"))
    assert {T.regime_of(r) for r in _json(score)["rows"]} == {"quiet", "busy"}


def test_a_home_spec_plan_still_names_recordings_by_seed():
    plan = T.Plan(quick=True, models=("tube",), detectors=("coact",), simulation="home")
    assert plan.recordings([1001, 1000]) == ["1000", "1001"]
    assert plan.gate_key == "0.54" and plan.regimes == ("home",)
