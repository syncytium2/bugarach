#!/usr/bin/env python3
"""The evidence behind the fair comparison's report, regenerated from the run's own files.

    python tools/fair_comparison_evidence.py fold-draws --fits %USERPROFILE%/runs/fair-comparison-2026-09-18/fits
    python tools/fair_comparison_evidence.py merge-gap  --fits %USERPROFILE%/runs/fair-comparison-2026-09-18/fits
    python tools/fair_comparison_evidence.py breakdown  --fits %USERPROFILE%/runs/fair-comparison-2026-09-18/fits
    python tools/fair_comparison_evidence.py replicate  --source <darkroom>/bugarach/2026-09-18-replicate-run-status/results

All four write into ``--run`` (default ``docs/learned/tuned_vs_coact/fair_comparison_2026_09_18/``).
The per-fit and per-score files (``--fits``, and ``scores/`` beside it) are too large for git; they
are archived in the darkroom as ``results/fits.tar.gz`` and ``results/scores.tar.gz``.

``breakdown``. Held-out recall per participation level and background, and distractor calls,
read from the run's own score rows at the operating point each choice was scored at. A pooled F1
can hide two sides winning in different places; this is where they differ.

``fold-draws`` (Figure 4). Which recordings each outer refit fitted and picked its threshold on, at
training seed 0: **as run**, read from the run's own fit records, and **before the fix**, by calling
``bugarach.learn.train.fold_maker`` on the order the tuning tool used until 2026-09-18 (each training
seed in turn, quiet then busy) and drawing exactly as ``train`` and ``pick_threshold`` draw.

``merge-gap``. The merge gap is how close two calls may be before they are merged into one. The
coded detectors' searches tuned it; the nets' was fixed at 20 frames (2 s), the default
``pick_threshold`` returns unchanged. So each side is re-scored with ONLY that setting changed:
every coded choice (CoactDetect, binned SCE, LoCo) at each gap in ``CODED_GAPS``, and every chosen
net refit re-decoded from its saved model at each gap in ``NET_GAPS``, keeping its threshold. Both
are scored on the held-out fold exactly as the run scores it (each background's pooled F1,
averaged). Each side first reproduces the run's own number at its own gap, and the file records how
closely. Nothing is re-chosen: a threshold picked at 2 s is kept at 8 s, and a coded choice made at
8 s is kept at 2 s, so the result bounds what tuning the gap could do rather than measuring it.

The nets' modules (``chorus_norm``, ``chorus_gain_norm``) are registered only on branch
``tune-bench-comparison``: run ``merge-gap`` with that worktree's ``src`` first on ``PYTHONPATH``.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO / "src") not in sys.path:
    sys.path.append(str(REPO / "src"))

DEFAULT_RUN = REPO / "docs" / "learned" / "tuned_vs_coact" / "fair_comparison_2026_09_18"
REGIMES = {"quiet": "baseline_quiet", "busy": "baseline_busy"}
CODED_GAPS = (0.0, 2.0, 4.0, 8.0, 16.0, 30.0)     # seconds
NET_GAPS = (2.0, 4.0, 8.0, 16.0)                   # seconds; the run's is 2
GAP_KEY = {"coact": "merge_gap_sec", "sce": "merge_gap_sec", "loco": "merge_gap_sec"}
NETS = ("chorus_norm", "chorus_gain_norm", "line_length", "tube")
SELECTIONS = ("ungated", "gated")


def _seeds_of_fold(decl, h):
    spf = decl["seeds_per_fold"]
    return decl["recording_seeds"][h * spf:(h + 1) * spf]


def _training_folds(decl, h):
    return [f for f in range(decl["folds"]) if f != h]


# ---- fold draws ---------------------------------------------------------------------------------

def fold_draws(run: Path, fits: Path, seed: int = 0) -> dict:
    from bugarach.learn.train import TRAIN_SEED_BLOCK, VAL_SEED_BLOCK, fold_maker

    decl = json.loads((run / "meta.json").read_text())["declaration"]
    # How many recordings a fit trains on, as the run's own configuration records declare it.
    n_train = {json.loads(p.read_text())["training"]["n_train"]
               for p in (run / "configs" / "chorus_norm").glob("*.json")}
    assert len(n_train) == 1, n_train
    n_train = n_train.pop()
    seeds = decl["recording_seeds"]
    fold_of = {s: i // decl["seeds_per_fold"] for i, s in enumerate(seeds)}

    def draw(recs):
        mk, _, _ = fold_maker(lambda r: r, recs)
        fitted = sorted({mk(TRAIN_SEED_BLOCK + seed * 1000 + i) for i in range(n_train)})
        picked = sorted({mk(VAL_SEED_BLOCK + seed * 1000 + i) for i in range(4)})
        return dict(fitted=fitted, threshold=picked)

    before = {}
    for h in range(decl["folds"]):
        train = sorted(s for s in seeds if fold_of[s] != h)
        before[str(h)] = draw([f"{b}:{s}" for s in train for b in REGIMES])

    as_run = {}
    for p in sorted((fits / "chorus_norm").rglob(f"seed{seed}__*.run.json")):
        r = json.loads(p.read_text())
        if r["role"] != "outer":
            continue
        h = [f for f in range(decl["folds"]) if f not in r["train_folds"]][0]
        as_run.setdefault(str(h), dict(fitted=r["fitted_recordings"],
                                       threshold=r["threshold_recordings"],
                                       train_folds=r["train_folds"]))
    doc = dict(
        what="fitting and threshold recordings of each outer refit at training seed "
             f"{seed}: as run (chorus_norm's refits, read from their fit records) and as the "
             "order used before the 2026-09-18 fix would have drawn them on the same split "
             "(bugarach.learn.train.fold_maker over each training seed in turn, quiet then busy)",
        generator="tools/fair_comparison_evidence.py fold-draws",
        seed=seed, n_train=n_train, seeds_per_fold=decl["seeds_per_fold"],
        fold_of={str(k): v for k, v in fold_of.items()}, as_run=as_run, before_fix=before)
    return doc


# ---- merge gap ----------------------------------------------------------------------------------

_REC: dict = {}


def _recording(rid):
    from bugarach import bench
    if rid not in _REC:
        b, s = rid.split(":")
        _REC[rid] = bench.make_recording(REGIMES[b], int(s))
    return _REC[rid]


def _objective(scored):
    """Each background's pooled F1, averaged; a NaN F1 counts as 0 (the run's rule)."""
    from bugarach.bench import pool_scores
    f1 = []
    for b in REGIMES:
        rows = [sc for rid, sc in scored if rid.startswith(b + ":")]
        v = pool_scores(rows, detector="x", regime="tuning").f1
        f1.append(float(v) if np.isfinite(v) else 0.0)
    return float(np.mean(f1))


def _held_out(decl, h):
    return [f"{b}:{s}" for s in _seeds_of_fold(decl, h) for b in REGIMES]


def coded_gaps(run: Path) -> dict:
    from bugarach import bench
    from bugarach.score import score_stream

    decl = json.loads((run / "meta.json").read_text())["declaration"]
    results = json.loads((run / "results.json").read_text())
    out = {}
    for d, key in GAP_KEY.items():
        out[d] = []
        for row in results["hand"][d]:
            h = row["outer_fold"]
            for w in SELECTIONS:
                chosen = dict(row[w]["chosen_params"])
                rec = dict(outer_fold=h, selection=w, chosen_gap=chosen.get(key),
                           run_f1=row[w]["f1"], f1_by_gap={})
                for g in sorted(set(CODED_GAPS) | {float(chosen.get(key))}):
                    p = dict(chosen, **{key: float(g)})
                    scored = [(rid, score_stream(_recording(rid)[1],
                                                 bench.run_detector(d, _recording(rid)[0], **p)))
                              for rid in _held_out(decl, h)]
                    rec["f1_by_gap"][f"{g:g}"] = _objective(scored)
                rec["reproduces_run"] = abs(rec["f1_by_gap"][f"{float(chosen.get(key)):g}"]
                                            - row[w]["f1"])
                out[d].append(rec)
                print(d, h, w, {k: round(v, 4) for k, v in rec["f1_by_gap"].items()},
                      "repro", f"{rec['reproduces_run']:.2g}", flush=True)
    return out


def net_gaps(run: Path, fits: Path) -> dict:
    from bugarach.learn import checkpoint
    from bugarach.learn.encode import decode, encode
    from bugarach.learn.train import THRESHOLD_GRID, probabilities
    from bugarach.score import score_stream

    decl = json.loads((run / "meta.json").read_text())["declaration"]
    results = json.loads((run / "results.json").read_text())
    grid = [float(t) for t in THRESHOLD_GRID]
    records = {}
    for p in fits.rglob("*.run.json"):
        r = json.loads(p.read_text())
        if r["role"] == "outer":
            records[(p.parts[-3], p.parts[-2], int(p.name.split("seed")[1].split("__")[0]),
                     tuple(r["train_folds"]))] = fits.parent / r["fit"]
    out = {}
    cache: dict = {}
    for m in NETS:
        out[m] = []
        for row in results["learned"][m]:
            h = row["outer_fold"]
            for w in SELECTIONS:
                x = row[w]
                rec = dict(outer_fold=h, selection=w, config_key=x["config_key"],
                           run_f1_mean=x["f1_mean"], per_seed=[])
                for s in x["per_seed"]:
                    key = (m, x["config_key"], s["seed"], tuple(_training_folds(decl, h)))
                    ck = records[key]
                    thr = grid[s["threshold_index"]]
                    ent = dict(seed=s["seed"], run_f1=s["f1"], threshold=thr, f1_by_gap={})
                    for g in NET_GAPS:
                        ck_key = (str(ck), thr, g)
                        if ck_key not in cache:
                            tr = checkpoint.load(ck)
                            scored = []
                            for rid in _held_out(decl, h):
                                sl, gt = _recording(rid)
                                enc = encode(sl, dt=tr.dt)
                                prob = probabilities(tr.model, enc.raster)
                                det = decode(prob, threshold=thr,
                                             merge_gap_frames=int(round(g / tr.dt))).to_seconds(enc)
                                scored.append((rid, score_stream(gt, det)))
                            cache[ck_key] = _objective(scored)
                        ent["f1_by_gap"][f"{g:g}"] = cache[ck_key]
                    ent["reproduces_run"] = abs(ent["f1_by_gap"]["2"] - s["f1"])
                    rec["per_seed"].append(ent)
                rec["f1_mean_by_gap"] = {f"{g:g}": float(np.mean([e["f1_by_gap"][f"{g:g}"]
                                                                  for e in rec["per_seed"]]))
                                         for g in NET_GAPS}
                out[m].append(rec)
                print(m, h, w, {k: round(v, 4) for k, v in rec["f1_mean_by_gap"].items()},
                      "run", round(x["f1_mean"], 4),
                      "max repro", f"{max(e['reproduces_run'] for e in rec['per_seed']):.2g}",
                      flush=True)
    return out


# ---- where the difference is: recall by participation and background -------------------------

def breakdown(run: Path, fits: Path, detectors=("coact",), nets=("chorus_norm", "chorus_gain_norm")) -> dict:
    """Held-out recall per participation level and background, and distractor calls, per outer fold.

    A pooled F1 can hide two sides winning in different places, so this reads the run's own
    per-recording score rows, at the operating point each choice was scored at: the coded choice's
    one row per recording, and each net refit's row at its ``threshold_index``, pooled over the
    five refits. Counts are summed before dividing (hits over planted), as the scorer pools.
    Nothing is re-scored."""
    decl = json.loads((run / "meta.json").read_text())["declaration"]
    results = json.loads((run / "results.json").read_text())
    scores = fits.parent / "scores"
    records = {}
    for p in fits.rglob("*.run.json"):
        r = json.loads(p.read_text())
        if r["role"] == "outer":
            records[(p.parts[-3], p.parts[-2], int(p.name.split("seed")[1].split("__")[0]),
                     tuple(r["train_folds"]))] = Path(r["fit"]).stem

    def tally(rows):
        t = {}
        for rid, row in rows:
            b = rid.split(":")[0]
            c = t.setdefault(b, dict(planted={}, hit={}, distractor_hits=0, n_distractors=0,
                                     n_fa=0, n_detected=0, hot_fa=0))
            for frac, (n, k) in row["by_frac"].items():
                c["planted"][frac] = c["planted"].get(frac, 0) + n
                c["hit"][frac] = c["hit"].get(frac, 0) + k
            c["distractor_hits"] += row["distractor_hits"]
            c["n_distractors"] += decl["bench_recording"]["n_distractors"]
            for k in ("n_fa", "n_detected", "hot_fa"):
                c[k] += row[k]
        for c in t.values():
            c["recall_by_participation"] = {f: c["hit"][f] / c["planted"][f] for f in c["planted"]}
            c["distractor_hit_rate"] = c["distractor_hits"] / c["n_distractors"]
            c["distractor_share_of_false_calls"] = (c["distractor_hits"] / (c["n_fa"] - c["hot_fa"])
                                                    if c["n_fa"] > c["hot_fa"] else None)
        return t

    out = dict(
        what="held-out recall per participation level and background, and distractor calls, at "
             "each choice's scored operating point; nets pooled over their refits",
        generator="tools/fair_comparison_evidence.py breakdown", detectors={}, nets={})
    for d in detectors:
        out["detectors"][d] = []
        for row in results["hand"][d]:
            h = row["outer_fold"]
            for w in SELECTIONS:
                doc = json.loads((scores / d / f"outer{h}__{w}.json").read_text())
                out["detectors"][d].append(dict(
                    outer_fold=h, selection=w, f1_by_background=row[w]["f1_by_background"],
                    by_background=tally(doc["rows"].items())))
    for m in nets:
        out["nets"][m] = []
        for row in results["learned"][m]:
            h = row["outer_fold"]
            for w in SELECTIONS:
                x = row[w]
                rows = []
                for s in x["per_seed"]:
                    stem = records[(m, x["config_key"], s["seed"], tuple(_training_folds(decl, h)))]
                    doc = json.loads((scores / m / x["config_key"] / f"{stem}__fold{h}.json").read_text())
                    rows += [(rid, per_thr[s["threshold_index"]]) for rid, per_thr in doc["rows"].items()]
                fb = {b: float(np.mean([s["f1_by_background"][b] for s in x["per_seed"]]))
                      for b in REGIMES}
                out["nets"][m].append(dict(outer_fold=h, selection=w, f1_by_background=fb,
                                           by_background=tally(rows)))
    return out


def replicate(source: Path) -> dict:
    """The replicate's headline numbers, copied from WSMIP065's results so the report can show both
    draws. WSMIP065's own report is the authority on the replicate; this is a citation, not a copy
    of its analysis."""
    r = json.loads((source / "results.json").read_text())
    m = json.loads((source / "meta.json").read_text())
    d = m["declaration"]
    return dict(
        what="the replicate's held-out F1 per outer fold and its paired comparisons, copied from "
             "WSMIP065's results so this report can show both draws; WSMIP065's own report is the "
             "authority on the replicate",
        generator="tools/fair_comparison_evidence.py replicate",
        source="<darkroom>/bugarach/2026-09-18-replicate-run-status/results/results.json and meta.json",
        code="branch replicate-run @ " + str(m["started"]["git"]["commit"])[:7]
             + " (this run's code plus --replicate)",
        replicate=d.get("replicate"),
        recording_seeds=[d["recording_seeds"][0], d["recording_seeds"][-1]],
        seeds_per_fold=d["seeds_per_fold"],
        fold_check_distinct=d.get("fold_check", {}).get("distinct"),
        coded_window_mode=d.get("coded_window_mode"),
        learned={mm: {w: [row[w]["f1_mean"] for row in rows] for w in ("untuned",) + SELECTIONS}
                 for mm, rows in r["learned"].items()},
        hand={dd: {w: [row[w]["f1"] for row in rows] for w in SELECTIONS}
              for dd, rows in r["hand"].items()},
        comparisons=r["comparisons"],
        refits=_refit_health(r))


#: A refit under this held-out F1 is set aside in the "without" means. The flags the run records
#: depend on the threshold a model is scored at (one failed model carries the failed-training
#: signature at one selection's threshold and makes no calls at the other's), so one cut on F1,
#: applied to both draws alike, is the rule; the flags describe what each set-aside refit did.
LOW_F1 = 0.2


def _refit_health(r: dict) -> dict:
    """Per net, selection and outer fold: the refits' F1, which fall under ``LOW_F1`` and what they
    did (the failed-training signature, or no calls at all), and the fold mean with and without
    them. Applied to this run and to the replicate alike, so both draws are read the same way."""
    out = {}
    for mm, rows in r["learned"].items():
        out[mm] = {}
        for w in ("untuned",) + SELECTIONS:
            out[mm][w] = []
            for row in rows:
                ps = row[w]["per_seed"]
                kept = [s["f1"] for s in ps if s["f1"] >= LOW_F1]
                out[mm][w].append(dict(
                    f1=[s["f1"] for s in ps],
                    low=[s["seed"] for s in ps if s["f1"] < LOW_F1],
                    failed_signature=[s["seed"] for s in ps if s.get("failed_training_signature")],
                    no_calls=[s["seed"] for s in ps if s.get("f1_was_nan")],
                    mean=float(np.mean([s["f1"] for s in ps])),
                    mean_without_low=float(np.mean(kept)) if kept else None))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("what", choices=("fold-draws", "merge-gap", "replicate", "breakdown"))
    ap.add_argument("--run", type=Path, default=DEFAULT_RUN)
    ap.add_argument("--fits", type=Path, default=None,
                    help="the run's fits/ folder (the darkroom's results/fits.tar.gz, unpacked)")
    ap.add_argument("--source", type=Path, default=None,
                    help="replicate: the replicate's results folder in the darkroom")
    a = ap.parse_args(argv)
    if a.what == "replicate":
        doc = replicate(a.source)
        (a.run / "replicate_summary.json").write_text(json.dumps(doc, indent=1) + "\n")
        print(a.run / "replicate_summary.json")
        return 0
    if a.fits is None:
        ap.error("--fits is required for fold-draws, merge-gap and breakdown")
    if a.what == "breakdown":
        doc = breakdown(a.run, a.fits)
        (a.run / "breakdown.json").write_text(json.dumps(doc, indent=1) + "\n")
        print(a.run / "breakdown.json")
        return 0
    if a.what == "fold-draws":
        doc = fold_draws(a.run, a.fits)
        (a.run / "fold_draws.json").write_text(json.dumps(doc, indent=1) + "\n")
        print(a.run / "fold_draws.json")
        return 0
    doc = dict(
        what="held-out F1 with ONLY the merge gap changed, both sides; nothing re-chosen",
        generator="tools/fair_comparison_evidence.py merge-gap",
        coded_gaps_sec=list(CODED_GAPS), net_gaps_sec=list(NET_GAPS),
        net_gap_as_run_sec=2.0,
        coded=coded_gaps(a.run), nets=net_gaps(a.run, a.fits))
    (a.run / "merge_gap.json").write_text(json.dumps(doc, indent=1, default=float) + "\n")
    print(a.run / "merge_gap.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
