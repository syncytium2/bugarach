"""The browser's fold split and pooled scorer against `bugarach.bench`.

Held-out scoring is what turns the page's tuning step from a demonstration into
a measurement. Today it sweeps one detector's one knob on one recording and
scores it against that recording's own planted events, so every number on screen
is in-sample and nothing distinguishes that from performance on new ground
truth. `docs/site/scoring.js` ports the two pieces that close the gap — the
deterministic fold split, and `bench.pool_scores` — and this file is the reason
to believe the browser's arithmetic is the Python's rather than a second one
that happens to agree today.

**What is under test here is the pooling, not the matching.** The per-recording
scorer already has its parity check in `test_webapp_tune_parity.py`. So the
per-recording counts are produced here by the real `score_detections` and then
handed to both languages, which have to reach the same pooled result from them.
That keeps this file pointed at the thing this lane ported.

Neither function draws a random number, so the bar is exactness, not a
distribution: 1e-9, the same one the browser detectors hold. The cases that
carry the weight are the degenerate ones, because they are where the two
plausible ways to pool stop agreeing:

* **a recording with no detections** — precision is undefined for it, and the
  pooled precision must still come from the summed counts. Average the
  per-recording ratios instead and this recording either poisons the result or
  silently drops out of it, depending on which plausible guard you wrote.
* **no planted events at all** — recall undefined, and F1 with it.
* **a false alarm inside the promiscuity probe** — the one case that proves the
  browser is not computing hits over detections. `nScored` excludes the probe,
  so pooled precision and `nHit / nDetected` diverge here and nowhere else.
* **a detection matching two truths, and a truth matched by two detections** —
  greedy one-to-one matching, where the second detection becomes a duplicate
  false alarm rather than a second hit.

Unlike the other `test_webapp_*_parity.py` files this one needs **node**, not a
browser: `scoring.js` is pure functions with no DOM, so there is nothing for a
page to do. That is deliberate — it means this parity check runs in CI today,
where the browser-driven ones skip for want of a chromium the runner has not
installed.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest

from bugarach.bench import fold_split, pool_scores
from bugarach.score import score_detections
from bugarach.simulate import GroundTruth, PlantedEvent

ROOT = Path(__file__).resolve().parents[1]
SCORING_JS = ROOT / "docs" / "site" / "scoring.js"
VIEWER = ROOT / "docs" / "site" / "raster_viewer.html"

NODE = shutil.which("node")
needs_node = pytest.mark.skipif(
    NODE is None, reason="the browser scorer is run with node; none on PATH")

# Read stdin, run whichever entry point was asked for, print the answer. Kept to
# one driver so every case crosses the boundary the same way.
DRIVER = r"""
const fs = require("fs");
const { foldSplit, poolScores } = require(process.argv[1]);
const req = JSON.parse(fs.readFileSync(0, "utf8"));

// JSON has no NaN, and `JSON.stringify` turns one into `null` without saying
// so. Map it deliberately instead, so an accidental null and an intended NaN
// cannot be confused on the Python side.
const num = (x) => (Number.isFinite(x) ? x : null);

function pooled(c) {
  const r = poolScores(c.scores.map(s => ({...s, byFrac: new Map(s.byFrac)})),
                       {detector: c.detector, regime: c.regime,
                        seeds: c.seeds, knobValue: c.knobValue,
                        tolSec: c.tolSec});
  return {
    detector: r.detector, regime: r.regime, knobValue: r.knobValue,
    nPlanted: r.nPlanted, nDetected: r.nDetected, nHit: r.nHit, nFa: r.nFa,
    hotFa: r.hotFa, distractorHits: r.distractorHits, nScored: r.nScored,
    seeds: r.seeds, tolSec: num(r.tolSec),
    recall: num(r.recall), precision: num(r.precision), f1: num(r.f1),
    byFrac: [...r.byFrac.entries()].sort((a, b) => a[0] - b[0]),
    recallAt: [...r.byFrac.keys()].sort((a, b) => a - b)
               .map(f => [f, num(r.recallAt(f))]),
    hotFaPerMin: num(r.hotFaPerMin(c.hotWindow || null)),
  };
}

function split(c) {
  const s = foldSplit(c);
  return {
    seeds: s.seeds, nFolds: s.nFolds, seedsPerFold: s.seedsPerFold,
    baseSeed: s.baseSeed,
    foldOf: s.seeds.map(x => s.foldOf(x)),
    train: [...Array(s.nFolds).keys()].map(h => s.train(h)),
    test: [...Array(s.nFolds).keys()].map(h => s.test(h)),
  };
}

const run = {pooled, split};
const out = req.cases.map(c => {
  // A refusal is a result: the two languages have to refuse the same inputs,
  // so it is reported rather than allowed to kill the process.
  try { return {ok: true, value: run[c.op](c.arg)}; }
  catch (e) { return {ok: false, error: String(e.message)}; }
});
process.stdout.write(JSON.stringify(out));
"""


def _js(cases: list[dict]) -> list[dict]:
    """Run every case through node in one go."""
    r = subprocess.run([NODE, "-e", DRIVER, str(SCORING_JS)],
                       input=json.dumps({"cases": cases}),
                       capture_output=True, text=True)
    assert r.returncode == 0, f"node failed:\n{r.stderr}"
    return json.loads(r.stdout)


def _close(got, want, what: str) -> None:
    """`None` from the browser is NaN from Python — compare them as the same
    thing, and demand exactness of everything else."""
    if got is None:
        assert want is None or not np.isfinite(want), f"{what}: JS NaN, Python {want}"
        return
    assert want is not None and np.isfinite(want), f"{what}: JS {got}, Python NaN"
    assert abs(got - want) <= 1e-9, f"{what}: JS {got} vs Python {want}"


# ---------------------------------------------------------------------------
# the vectors: per-recording scores, produced by the real scorer
# ---------------------------------------------------------------------------

def _gt(times, fracs, *, hot_window=None, distractors=()) -> GroundTruth:
    ev = [PlantedEvent(time=float(t), frac=float(f), n_part=0, rois=(),
                       jitter_sec=0.0) for t, f in zip(times, fracs)]
    ds = [PlantedEvent(time=float(t), frac=0.18, n_part=0, rois=(),
                       jitter_sec=0.0, kind="distractor") for t in distractors]
    params = {} if hot_window is None else {"hot_window": tuple(hot_window)}
    return GroundTruth(events=ev, distractors=ds, params=params)


# One recording each, named for the thing it puts under the pooler.
RECORDINGS = {
    # ordinary: most events found, one missed, one detection at nothing
    "ordinary": dict(times=[10.0, 40.0, 70.0, 100.0], fracs=[0.3, 0.3, 0.18, 0.1],
                     onsets=[10.4, 40.2, 70.9, 55.0], widths=[0, 0, 0, 0]),
    # every detection a hit, and every event found
    "perfect": dict(times=[5.0, 25.0], fracs=[0.3, 0.1],
                    onsets=[5.0, 25.0], widths=[0, 0]),
    # nothing fired: precision undefined for this recording alone
    "no_detections": dict(times=[12.0, 33.0], fracs=[0.3, 0.18],
                          onsets=[], widths=[]),
    # nothing planted: recall undefined, and every detection is a false alarm
    "no_events": dict(times=[], fracs=[],
                      onsets=[8.0, 18.0], widths=[0, 0]),
    # two detections on one event — the second is a duplicate, not a second hit;
    # and one wide detection spanning two events can still only claim one
    "crowded": dict(times=[20.0, 20.6, 60.0], fracs=[0.3, 0.3, 0.18],
                    onsets=[20.1, 20.2, 59.5], widths=[0, 0, 2.0]),
    # false alarms inside the promiscuity probe, where nothing was planted:
    # the only case where pooled precision and nHit/nDetected part company
    "probe": dict(times=[10.0], fracs=[0.3],
                  onsets=[10.1, 1250.0, 1300.0, 1400.0],
                  widths=[0, 0, 0, 0], hot_window=(1200.0, 1500.0)),
    # a detection landing on a correlated population burst: counted, and still
    # a false alarm, because it matched no planted event
    "distractor": dict(times=[30.0], fracs=[0.3], onsets=[30.2, 90.0],
                       widths=[0, 0], distractors=(90.1,)),
}


def _score(name: str, tol: float = 1.5):
    """One recording's `Score`, from the scorer this project actually uses."""
    v = RECORDINGS[name]
    gt = _gt(v["times"], v["fracs"], hot_window=v.get("hot_window"),
             distractors=v.get("distractors", ()))
    return score_detections(gt, np.array(v["onsets"], dtype=float),
                            widths=np.array(v["widths"], dtype=float),
                            tol_sec=tol)


def _as_js(sc) -> dict:
    """A `Score` in the shape the page's `scoreDetections` returns."""
    return dict(nPlanted=sc.n_planted, nDetected=sc.n_detected, nHit=sc.n_hit,
                nFa=sc.n_fa, hotFa=sc.hot_fa, distractorHits=sc.distractor_hits,
                byFrac=[[float(f), [n, h]] for f, (n, h) in sorted(sc.by_frac.items())],
                tolSec=sc.tol_sec)


# The pools, each one a list of recordings scored together.
POOLS = {
    "the ordinary case": ["ordinary", "perfect"],
    "one recording fired at nothing": ["ordinary", "no_detections"],
    "nothing fired anywhere": ["no_detections", "no_detections"],
    "nothing was planted anywhere": ["no_events", "no_events"],
    "planted in one, not the other": ["ordinary", "no_events"],
    "everything found": ["perfect", "perfect"],
    "duplicates and a span over two truths": ["crowded", "ordinary"],
    "the promiscuity probe": ["probe", "ordinary"],
    "a burst that is not an event": ["distractor", "perfect"],
    "every degenerate case at once": list(RECORDINGS),
    "an empty pool": [],
}


@needs_node
@pytest.mark.parametrize("name", list(POOLS))
def test_pooling_matches_python(name):
    """The pooled result, both languages, from identical per-recording counts."""
    names = POOLS[name]
    scores = [_score(n) for n in names]
    seeds = [1000 + i for i in range(len(names))]

    py = pool_scores(scores, detector="loco", regime="heldout", seeds=seeds,
                     knob_value=2.5)
    hot = (1200.0, 1500.0)
    [res] = _js([{"op": "pooled", "arg": {
        "scores": [_as_js(s) for s in scores], "detector": "loco",
        "regime": "heldout", "seeds": seeds, "knobValue": 2.5,
        "tolSec": 1.5, "hotWindow": list(hot)}}])
    assert res["ok"], res.get("error")
    js = res["value"]

    for k, want in [("detector", "loco"), ("regime", "heldout"),
                    ("knobValue", 2.5)]:
        assert js[k] == want, f"{name}: {k}"
    assert js["seeds"] == seeds, name

    # counts first — the ratios are only as good as these
    for k, want in [("nPlanted", py.n_planted), ("nDetected", py.n_detected),
                    ("nHit", py.n_hit), ("nFa", py.n_fa),
                    ("hotFa", py.hot_fa),
                    ("distractorHits", py.distractor_hits),
                    ("nScored", py.n_scored)]:
        assert js[k] == want, f"{name}: {k} — JS {js[k]} vs Python {want}"

    _close(js["recall"], py.recall, f"{name}: recall")
    _close(js["precision"], py.precision, f"{name}: precision")
    _close(js["f1"], py.f1, f"{name}: f1")
    _close(js["tolSec"], py.tol_sec, f"{name}: tolSec")

    assert [f for f, _ in js["byFrac"]] == sorted(py.by_frac), f"{name}: byFrac keys"
    for f, (n, h) in js["byFrac"]:
        assert (n, h) == py.by_frac[f], f"{name}: byFrac[{f}]"
    for f, r in js["recallAt"]:
        _close(r, py.recall_at(f), f"{name}: recallAt({f})")

    # the probe's own rate, gated apart from precision
    want_hot = py.hot_fa / ((hot[1] - hot[0]) / 60.0 * max(1, len(seeds)))
    _close(js["hotFaPerMin"], want_hot, f"{name}: hotFaPerMin")


@needs_node
def test_the_probe_is_what_makes_pooling_differ_from_hits_over_detections():
    """The vector that would catch a browser computing its own precision.

    Everywhere else `nHit / nDetected` and the pooled precision agree, so a page
    doing its own arithmetic would pass every other case in this file. Here the
    promiscuity probe's firings leave the denominator and the two answers part
    company — which is the whole reason `nScored` exists.
    """
    scores = [_score("probe"), _score("ordinary")]
    py = pool_scores(scores, detector="cicada", regime="heldout", seeds=[1, 2])

    naive = py.n_hit / py.n_detected
    assert py.n_scored < py.n_detected, "the probe vector planted no hot-window FA"
    assert abs(py.precision - naive) > 0.05, (
        "this vector no longer separates pooled precision from hits/detections, "
        "so it has stopped guarding the thing it was written for")

    [res] = _js([{"op": "pooled", "arg": {
        "scores": [_as_js(s) for s in scores], "detector": "cicada",
        "regime": "heldout", "seeds": [1, 2], "knobValue": None,
        "tolSec": 1.5}}])
    assert res["ok"], res.get("error")
    _close(res["value"]["precision"], py.precision, "probe precision")


@needs_node
def test_pooled_precision_is_not_the_mean_of_per_recording_precisions():
    """Pooled counts, not the mean of ratios — the trap this port had to avoid.

    A recording that plants fewer events must not carry the same weight as a
    fuller one. The two ways of pooling are a few characters apart and both look
    reasonable on screen, so the guard is a vector where they visibly disagree.
    """
    scores = [_score("ordinary"), _score("perfect")]
    py = pool_scores(scores, detector="loco", regime="heldout", seeds=[1, 2])
    mean_of_ratios = float(np.mean([s.recall for s in scores]))
    assert abs(py.recall - mean_of_ratios) > 1e-3, (
        "these recordings no longer separate pooled recall from the mean of "
        "per-recording recalls")

    [res] = _js([{"op": "pooled", "arg": {
        "scores": [_as_js(s) for s in scores], "detector": "loco",
        "regime": "heldout", "seeds": [1, 2], "knobValue": None,
        "tolSec": 1.5}}])
    _close(res["value"]["recall"], py.recall, "pooled recall")


@needs_node
def test_scores_at_different_tolerances_are_refused_by_both():
    """Counts add whatever they were counted against, so pooling across
    tolerances yields a plausible number whose matching rule is a blend of two.
    Neither language is allowed to return it."""
    scores = [_score("ordinary", tol=1.5), _score("perfect", tol=3.0)]
    with pytest.raises(ValueError, match="different tolerances"):
        pool_scores(scores, detector="loco", regime="heldout")

    [res] = _js([{"op": "pooled", "arg": {
        "scores": [_as_js(s) for s in scores], "detector": "loco",
        "regime": "heldout", "seeds": [], "knobValue": None, "tolSec": None}}])
    assert not res["ok"], "the browser pooled two different matching rules"
    assert "different tolerances" in res["error"], res["error"]


@needs_node
def test_a_pooled_score_carries_the_tolerance_it_was_measured_at():
    """The tolerance is the number's units. A hit is counted at a 1.5 s edge gap
    against a median realized event 0.80 s wide, so this F1 cannot tell landing
    on an event from landing a second away from it — the ranking survives that,
    a bare number implying timing accuracy does not. Both languages carry it,
    and the browser refuses to pool a score that arrives without one."""
    for tol in (1.5, 3.0):
        py = pool_scores([_score("ordinary", tol=tol)], detector="loco",
                         regime="heldout")
        assert py.tol_sec == tol
        assert f"@{tol:g}s" in py.summary(), "F1 printed without its tolerance"

    bare = _as_js(_score("ordinary"))
    bare.pop("tolSec")
    [res] = _js([{"op": "pooled", "arg": {
        "scores": [bare], "detector": "loco", "regime": "heldout",
        "seeds": [], "knobValue": None, "tolSec": None}}])
    assert not res["ok"], "the browser pooled a score with no tolerance"
    assert "tolerance" in res["error"], res["error"]


# ---------------------------------------------------------------------------
# the fold split
# ---------------------------------------------------------------------------

SPLITS = [
    dict(nFolds=4, seedsPerFold=3, baseSeed=1000),   # what fair_bakeoff runs
    dict(nFolds=2, seedsPerFold=1, baseSeed=0),      # the smallest legal split
    dict(nFolds=5, seedsPerFold=7, baseSeed=424242),
    dict(nFolds=3, seedsPerFold=4, baseSeed=-10),    # a base below zero still deals
]


@needs_node
@pytest.mark.parametrize("cfg", SPLITS, ids=lambda c: f"{c['nFolds']}x{c['seedsPerFold']}")
def test_fold_split_matches_python(cfg):
    """Same data set, same folds, same held-out set — with no random source in it,
    so the browser reproduces a split the command line made."""
    py = fold_split(n_folds=cfg["nFolds"], seeds_per_fold=cfg["seedsPerFold"],
                    base_seed=cfg["baseSeed"])
    [res] = _js([{"op": "split", "arg": cfg}])
    assert res["ok"], res.get("error")
    js = res["value"]

    assert js["seeds"] == list(py.seeds)
    assert js["foldOf"] == [py.fold_of(s) for s in py.seeds]
    for held in range(py.n_folds):
        assert js["train"][held] == list(py.train(held)), f"train({held})"
        assert js["test"][held] == list(py.test(held)), f"test({held})"
        # the property the whole split exists for
        assert not set(js["train"][held]) & set(js["test"][held])
    assert sorted(sum(js["test"], [])) == list(py.seeds), "the folds lost a recording"


@needs_node
@pytest.mark.parametrize("cfg", [dict(nFolds=1, seedsPerFold=3, baseSeed=1000),
                                 dict(nFolds=0, seedsPerFold=3, baseSeed=1000),
                                 dict(nFolds=4, seedsPerFold=0, baseSeed=1000)])
def test_a_split_with_nothing_to_fit_on_is_refused_by_both(cfg):
    """One fold means a held-out score with no training set behind it, which is
    the exact claim the split exists to make true. Refused, not degraded."""
    with pytest.raises(ValueError):
        fold_split(n_folds=cfg["nFolds"], seeds_per_fold=cfg["seedsPerFold"],
                   base_seed=cfg["baseSeed"])
    [res] = _js([{"op": "split", "arg": cfg}])
    assert not res["ok"], f"the browser accepted {cfg}"


def test_fair_bakeoff_uses_the_shared_split():
    """The data-set division the browser reproduces has to be the one the command
    line ran, so the tool imports it rather than keeping its own copy."""
    src = (ROOT / "tools" / "fair_bakeoff.py").read_text(encoding="utf-8")
    assert "fold_split" in src, "fair_bakeoff no longer uses the shared split"
    assert "// seeds_per_fold" not in src, "the inline split came back"


# ---------------------------------------------------------------------------
# the splice
# ---------------------------------------------------------------------------

MARKERS = ("BEGIN bugarach-scoring", "END bugarach-scoring")


def _block(text: str) -> str | None:
    """The spliced region, marker lines included, or None if it is not there."""
    lines = text.splitlines()
    starts = [i for i, ln in enumerate(lines) if MARKERS[0] in ln]
    ends = [i for i, ln in enumerate(lines) if MARKERS[1] in ln]
    if not starts or not ends:
        return None
    assert len(starts) == 1 and len(ends) == 1, "the splice markers are duplicated"
    return "\n".join(lines[starts[0]:ends[0] + 1])


def test_the_scorer_has_splice_markers():
    """Without them the guard below can never arm, and would sit here looking
    like coverage while checking nothing."""
    assert _block(SCORING_JS.read_text(encoding="utf-8")) is not None


def test_the_page_has_not_forked_the_scorer():
    """Arms itself the moment the UI phase pastes this into the viewer.

    The viewer is one self-contained file with no `import(` in it — the build
    refuses to publish one that has any — so the scorer cannot be loaded from
    here at runtime and has to be pasted in. That leaves two copies of one
    scorer, which is precisely the failure the module was written to prevent,
    and it is not a failure anyone catches by reading. So the check exists
    before the splice does and starts enforcing without anyone remembering to
    switch it on.
    """
    page = _block(VIEWER.read_text(encoding="utf-8"))
    if page is None:
        pytest.skip("the scorer is not spliced into the viewer yet")
    assert page == _block(SCORING_JS.read_text(encoding="utf-8")), (
        "docs/site/raster_viewer.html and docs/site/scoring.js hold different "
        "scorers. Edit scoring.js and re-splice; do not repair the page copy.")
