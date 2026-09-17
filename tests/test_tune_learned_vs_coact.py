"""The tuning tool's guarantees, on one ``--quick`` run of ``tube`` and CoactDetect.

``tools/tune_learned_vs_coact.py`` runs overnight with nobody watching, and a defect in it
would cost the night and possibly the comparison. Each test is one requirement from
``HANDOFF-workstation-tuning.md`` (*Gate 2*) or from the storage rule the Mac unsupervised
session carried from Tony on 2026-09-16 (tuned parameters stored persistently, rationally and
separably). The run is made once, by the command line, because the tool's workers are spawned
processes that must import it as a script.
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
                          "--models", "tube", "--detectors", "coact"],
                         capture_output=True, text=True, env=env, cwd=REPO, timeout=600)
    assert res.returncode == 0, res.stdout + res.stderr
    return res.stdout


@pytest.fixture(scope="module")
def run(tmp_path_factory):
    out = tmp_path_factory.mktemp("tune") / "run"
    first = _run_cli(out)
    plan = T.Plan(quick=True, models=("tube",), detectors=("coact",))
    return dict(out=out, plan=plan, first=first)


def _json(p):
    return json.loads(Path(p).read_text())


def test_no_held_out_recording_or_its_twin_reaches_a_fit_a_threshold_a_budget_or_a_selection(run):
    out, plan = run["out"], run["plan"]
    offset = T.NULL_SEED_OFFSET
    for rp in (out / "fits").rglob("*.run.json"):
        r = _json(rp)
        assert set(r["fitted_recordings"]) <= set(r["recording_seeds"])
        assert set(r["threshold_recordings"]) <= set(r["recording_seeds"])
        stem = rp.name[: -len(".run.json")]
        for sp in (out / "scores" / rp.parent.relative_to(out / "fits")).glob(f"{stem}__fold*.json"):
            scored = {int(s) for s in _json(sp)["rows"]}
            assert scored and not scored & set(r["recording_seeds"]), sp
    meta = _json(out / "meta.json")
    for h in plan.folds():
        test = set(plan.split.test(h))
        b = meta["budgets"][str(h)]
        assert not set(b["recording_seeds"]) & test
        assert not {s - offset for s in b["twin_seeds"]} & test
        for w in T.SELECTIONS:
            for name in ("tube", "coact"):
                pooled = _json(T.selection_path(out, w, h, name))["pooled"]
                used = set(pooled["recording_seeds"]) | set(pooled.get("fitted_on", []))
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
    fold0 = plan.fold_seeds([0])
    readers = [h for h in plan.folds()
               if set(fold0) <= set(_json(T.selection_path(out, "ungated", h, "tube"))["pooled"]["fitted_on"])]
    assert readers == [1, 2]


def test_decoding_at_the_fits_own_threshold_reproduces_trained_predict(run):
    from bugarach.learn import checkpoint

    ck = next(p for p in (run["out"] / "fits").rglob("*.json") if not p.name.endswith(".run.json"))
    tr = checkpoint.load(ck)
    sl, _ = T._make_recording(run["plan"].spec, 1000)
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
    seeds = list(plan.split.seeds)
    live = []
    for s in seeds:
        sl, gt = T._make_recording(plan.spec, s)
        live.append(score_stream(gt, run_detector("coact", sl, **conf["params"])))
    a = pool_scores(live, detector="coact", regime="tuning")
    b = T.pooled([doc["rows"][str(s)] for s in seeds], "coact")
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
    recs = plan.fold_seeds(plan.training_folds(h))
    stored = _json(T.score_path(out, "tube", sel["config_key"], seed, recs, h))
    code = (
        "import json, sys\n"
        "sys.path.insert(0, 'tools')\n"
        "from fair_bakeoff import _make_recording\n"
        "from bugarach.learn import checkpoint\n"
        "from bugarach.score import score_stream\n"
        f"spec = json.loads(open({str(REPO / T.SPEC_PATH)!r}).read())['generator']\n"
        f"tr = checkpoint.load({str(chosen)!r})\n"
        "rows = {}\n"
        f"for s in {list(plan.split.test(h))!r}:\n"
        "    sl, gt = _make_recording(spec, s)\n"
        "    sc = score_stream(gt, tr.predict(sl)[0])\n"
        "    rows[str(s)] = dict(n_planted=sc.n_planted, n_detected=sc.n_detected, n_hit=sc.n_hit,\n"
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
