#!/usr/bin/env python3
"""Every number the rigid-shift report quotes, computed from the run's files into one file.

    python tools/summarize_tube_self_supervised.py --run docs/learned/tube_self_supervised

Reads the stage outputs under ``--run`` (the layout
``docs/pipelines/learned-model-evaluation.md`` gives) and writes ``summary.json`` beside them.
Exploratory.

**Why this exists.** The report's second murderboard found the machine-written tables right cell
for cell and all fifty-one defects in the hand-typed prose around them: ranges quoted tighter than
the record, a chance row copied into the wrong column, a count that no file stored. The pipeline's
gate is *"if a number is in the prose, it is in a file"*. This is that file, so a reviewer checks a
sentence against one key rather than re-deriving it.

What it computes, by stage:

* **bake-off** (``bakeoff_seed*/bakeoff.json``): per detector, F1 per fold per training seed; the
  fold means over seeds; mean and sample SD over the four fold means; the SD across seeds within a
  fold; recall, precision, probe firings and fit seconds. Paired per-fold differences for the
  comparisons the report makes, each with its ``t`` on three degrees of freedom and the mean
  without the fold that contributes most — computed on the seed-averaged folds, and per seed.
* **training** (``training/results.jsonl``): per arm, displacement and model, F1 at every
  threshold with the population SD over fits, how many fits scored no true positive, how many
  ended at chance loss, how often a threshold sat on its grid's edge or floor, detection widths
  and coverage, and every paired check with its tie share.
* **aggregate leak**, **controls**, **real recordings** and **plant probe**: the cells the report
  reads, including the window-edge shares of every real-recording detector.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

LN2 = math.log(2.0)
COMPARISONS = (("line", "line_length"), ("line", "coact"), ("line_length", "coact"),
               ("line_bound", "line"), ("line_bound", "coact"), ("line", "tube"),
               ("tube", "coact"), ("coact", "loco"))
EDGE_SEC = (5.0, 12.8)


def finite(x):
    return x is not None and isinstance(x, (int, float)) and math.isfinite(x)


def f1_or_zero(x):
    return float(x) if finite(x) else 0.0


def paired(a, b):
    """Paired differences a - b over folds: each, mean, t on n-1 df, and without the largest."""
    d = np.asarray(a, float) - np.asarray(b, float)
    n = d.size
    sd = float(d.std(ddof=1)) if n > 1 else float("nan")
    t = float(d.mean() / (sd / math.sqrt(n))) if n > 1 and sd > 0 else float("nan")
    drop = int(np.argmax(d))
    rest = np.delete(d, drop)
    return {"differences": d.tolist(), "mean": float(d.mean()), "sd": sd, "t": t, "df": n - 1,
            "n_positive": int((d > 0).sum()), "largest_fold": drop,
            "mean_without_largest": float(rest.mean()) if rest.size else None}


# -- bake-off -----------------------------------------------------------------------------------

def bakeoff(run: Path) -> dict:
    dirs = sorted(d for d in run.glob("bakeoff_seed*") if d.is_dir())
    if not dirs:
        return {}
    per = defaultdict(lambda: defaultdict(dict))       # det -> seed -> fold -> row
    meta = {}
    for d in dirs:
        # `fair_bakeoff.py` writes `bakeoff.json` for seed 0 and `bakeoff_seed<N>.json` otherwise.
        (f,) = sorted(d.glob("bakeoff*.json"))
        b = json.loads(f.read_text())
        seed = int(b["train_seed"])
        meta[seed] = {"git_commit": b["provenance"].get("git_commit"),
                      "git_dirty": b["provenance"].get("git_dirty"),
                      "code_version": b["provenance"].get("code_version")}
        for group in ("hand_written", "learned"):
            for det, row in b[group].items():
                for pf in row["per_fold"]:
                    per[det][seed][pf["fold"]] = {**pf, "family": group}
    seeds = sorted(meta)
    out = {"seeds": seeds, "provenance": meta, "detectors": {}, "paired": {}, "paired_per_seed": {}}
    fold_means = {}
    for det, by_seed in per.items():
        folds = sorted(next(iter(by_seed.values())))
        grid = np.array([[f1_or_zero(by_seed[s][f]["f1"]) for f in folds] for s in seeds])
        fm = grid.mean(axis=0)
        fold_means[det] = fm
        def avg(key):
            v = [by_seed[s][f].get(key) for s in seeds for f in folds]
            v = [x for x in v if finite(x)]
            return float(np.mean(v)) if v else None
        ts_ = [float(np.mean([by_seed[s][f]["train_sec"] for f in folds]))
               if all(finite(by_seed[s][f].get("train_sec")) for f in folds) else None
               for s in seeds]
        out["detectors"][det] = {
            "family": by_seed[seeds[0]][folds[0]]["family"],
            "f1_by_seed_fold": grid.tolist(), "f1_fold_means": fm.tolist(),
            "f1_mean": float(fm.mean()), "f1_sd_over_folds": float(fm.std(ddof=1)),
            "f1_fold_range": [float(fm.min()), float(fm.max())],
            "f1_seed_sd_within_fold_mean": float(grid.std(axis=0, ddof=1).mean())
            if len(seeds) > 1 else None,
            "f1_seed_means": grid.mean(axis=1).tolist(),
            "recall": avg("recall"), "precision": avg("precision"), "probe_firings": avg("hot_fa"),
            "train_sec_mean_by_seed": ts_ if any(finite(x) for x in ts_) else None,
            "n_params": by_seed[seeds[0]][folds[0]].get("n_params")}
    for a, b in COMPARISONS:
        if a in fold_means and b in fold_means:
            key = f"{a} - {b}"
            out["paired"][key] = paired(fold_means[a], fold_means[b])
            g = out["detectors"]
            out["paired_per_seed"][key] = [
                paired(np.asarray(g[a]["f1_by_seed_fold"])[i], np.asarray(g[b]["f1_by_seed_fold"])[i])
                for i in range(len(seeds))]
    return out


# -- training -----------------------------------------------------------------------------------

def training(run: Path) -> dict:
    p = run / "training" / "results.jsonl"
    if not p.exists():
        return {}
    R = [json.loads(line) for line in open(p)]
    cells = defaultdict(list)
    for r in R:
        J = None if r["arm"] in ("supervised", "untrained") else r["J_sec"]
        cells[(r["arm"], J, r["model"])].append(r)
    out = {"n_rows": len(R), "cells": {}}
    for (arm, J, model), rows in sorted(cells.items(), key=lambda kv: str(kv[0])):
        c = {"arm": arm, "J_sec": J, "model": model, "n_fits": len(rows), "scores": {},
             "checks": {}}
        keys = sorted({k for r in rows for k in r["scores"]})
        for k in keys:
            got = [r["scores"].get(k, {}) for r in rows]
            f1 = [f1_or_zero(g.get("f1")) for g in got]
            c["scores"][k] = {
                "f1_mean": float(np.mean(f1)), "f1_pop_sd": float(np.std(f1)),
                "n_no_true_positive": int(sum(not finite(g.get("f1")) or not g.get("n_hit")
                                              for g in got)),
                "detections_mean": float(np.mean([g.get("n_detected") or 0 for g in got])),
                "hits_mean": float(np.mean([g.get("n_hit") or 0 for g in got])),
                "n_planted_per_fit": sorted({g.get("n_planted") for g in got if g.get("n_planted")}),
                "width_sec_median": _med(g.get("width_sec_median") for g in got),
                "coverage_share_median": _med(g.get("coverage_share") for g in got),
                "at_grid_floor_count": int(sum(sum(bool(x) for x in (g.get("at_grid_floor") or []))
                                               for g in got))}
        edge = [r.get("oracle_report", {}).get("at_edge") for r in rows]
        c["oracle_at_edge_fits"] = int(sum(bool(x) for x in edge))
        hist_final = [r["history"][-1][1] for r in rows if r.get("history") and len(r["history"][-1]) >= 3]
        if hist_final:
            c["final_loss"] = {"n_at_or_above_ln2": int(sum(x >= LN2 for x in hist_final)),
                               "n_at_or_above_0.6": int(sum(x >= 0.6 for x in hist_final)),
                               "min": float(min(hist_final)), "max": float(max(hist_final))}
        for r in rows:
            for k, v in (r.get("checks") or {}).items():
                c["checks"].setdefault(k, {"share": [], "tie": []})
                if v.get("share_real_higher") is not None:
                    c["checks"][k]["share"].append(v["share_real_higher"])
                    c["checks"][k]["tie"].append(v.get("tie_share"))
        for k, v in c["checks"].items():
            s = np.asarray(v["share"], float)
            t = np.asarray([x for x in v["tie"] if x is not None], float)
            c["checks"][k] = {"share_mean": float(s.mean()), "share_min": float(s.min()),
                              "share_max": float(s.max()), "tie_share_min": float(t.min()),
                              "tie_share_max": float(t.max()), "n": int(s.size)}
        widths = [r.get("fitted_parameters") for r in rows if r.get("fitted_parameters")]
        if widths:
            c["fitted_parameters_by_fit"] = widths
        out["cells"][f"{arm}|{J}|{model}"] = c
    # The comparisons the report's prose makes about the untrained arm, computed here so the
    # sentences quote them: where the best untrained model sits among the trained cells, and
    # which cells reach their truth-reading score by covering most of each recording.
    cells = out["cells"].values()
    for key in ("oracle", "label_free_2", "label_free_1", "label_free_0.5"):
        untrained = {c["model"]: c["scores"][key]["f1_mean"] for c in cells
                     if c["arm"] == "untrained" and key in c["scores"]}
        trained = {f"{c['arm']}|{c['J_sec']:g}|{c['model']}": c["scores"][key]["f1_mean"]
                   for c in cells if c["arm"] in ("ssl_sim", "ssl_real") and key in c["scores"]}
        best = max(untrained, key=untrained.get)
        out.setdefault("untrained_vs_trained", {})[key] = {
            "best_untrained_model": best, "best_untrained_f1": untrained[best],
            "n_trained_cells": len(trained),
            "n_trained_cells_below_best_untrained": sum(v < untrained[best] for v in trained.values()),
            "trained_f1_range": [min(trained.values()), max(trained.values())],
            "untrained_f1_range": [min(untrained.values()), max(untrained.values())]}
    out["oracle_at_edge_fits_total"] = int(sum(c["oracle_at_edge_fits"] for c in cells))
    out["oracle_at_edge_models"] = sorted({c["model"] for c in cells if c["oracle_at_edge_fits"]})
    out["cells_covering_over_half_at_truth_reading"] = sorted(
        k for k, c in out["cells"].items()
        if (c["scores"].get("oracle", {}).get("coverage_share_median") or 0) > 0.5)
    return out


def _med(values):
    v = [x for vs in values if vs for x in vs if finite(x)]
    return float(np.median(v)) if v else None


# -- the other stages ---------------------------------------------------------------------------

def aggregate(run: Path) -> dict:
    p = run / "aggregate_leak" / "results.json"
    if not p.exists():
        return {}
    R = json.loads(p.read_text())
    out = {"init": [], "fitted": defaultdict(list)}
    for r in R:
        cell = {"stream": r["stream"], "J_sec": r["J_sec"], "kind": r["kind"]}
        for k in ("real_vs_rigid_shift", "real_vs_shared_offset", "unplanted_vs_rigid_shift",
                  "planted_vs_rigid_shift"):
            if k in r:
                cell[k] = {s: r[k][s] for s in r[k] if s in ("all", "trace")}
                if k == "real_vs_rigid_shift":
                    cell["real_vs_rigid_shift_per_channel"] = {
                        s: r[k][s]["accuracy"] for s in r[k] if s not in ("all", "trace")}
        if r["bank"] == "init":
            out["init"].append(cell)
        else:
            out["fitted"][r["model"]].append({"held_fold": r["held_fold"], **cell})
    for model, cells in out["fitted"].items():
        rng = defaultdict(list)
        for c in cells:
            for k in ("real_vs_rigid_shift", "real_vs_shared_offset", "unplanted_vs_rigid_shift",
                      "planted_vs_rigid_shift"):
                if k in c:
                    rng[(k, c["J_sec"])].append(c[k]["all"]["accuracy"])
        out[f"fitted_{model}_all_accuracy_range_over_folds"] = {
            f"{k}|{J:g}": [min(v), max(v)] for (k, J), v in sorted(rng.items())}
    out["fitted"] = dict(out["fitted"])
    return out


def controls(run: Path) -> dict:
    p = run / "controls_lab" / "results.json"
    if not p.exists():
        return {}
    R = json.loads(p.read_text())["leak"]
    return {f"{r['stream']}|{r['J_sec']:g}": {
        k: {"accuracy": r[k]["accuracy_fold_seed_mean"], "range": r[k]["accuracy_fold_seed_range"],
            "by_mouse": r[k]["by_mouse"], "dropped_share": r[k]["dropped_share"]}
        for k in ("rigid_shift", "shared_shift", "uniform_dither")} for r in R}


def real(run: Path, with_edges: bool) -> dict:
    p = run / "real_compare" / "summary.json"
    if not p.exists():
        return {}
    s = json.loads(p.read_text())
    out = {"stats": s["stats"], "agreement": s["agreement"]}
    if with_edges:
        os.environ.setdefault("LOOK_ROLE", "steps_excluded")
        import look_rigid_shift as lr
        recs, _ = lr.load("fast", None)
        win = {r.recording_id: (r.window[0] * r.dt, r.window[1] * r.dt) for r in recs}
        ev = json.loads((run / "real_compare" / "events.json").read_text())
        edges = {}
        for det, runs in ev.items():
            n = 0
            near = {e: 0 for e in EDGE_SEC}
            span = 0.0
            for one in runs:
                for rid, evs in one.items():
                    a, b = win[rid]
                    span += b - a
                    for on, _ in evs:
                        n += 1
                        for e in EDGE_SEC:
                            near[e] += min(on - a, b - on) < e
            edges[det] = {f"within_{e:g}s": near[e] / max(1, n) for e in EDGE_SEC}
            edges[det]["n_events"] = n
            edges[det]["uniform_expectation"] = {
                f"within_{e:g}s": float(np.mean([2 * e / (b - a) for a, b in win.values()]))
                for e in EDGE_SEC}
        out["edge_shares"] = edges
    return out


def probe(run: Path) -> dict:
    p = run / "probe" / "line_vs_fuzz.json"
    if not p.exists():
        return {}
    sc = json.loads(p.read_text())["scores"]
    out = {}
    for m, r in sc.items():
        if m.startswith("no labels"):
            continue
        Ks = sorted({int(k.split("_")[1]) for k in r if k.startswith("line_") and not k.endswith("sd")})
        out[m] = {plant: {K: {"ratio": r[f"line_{K}"] / r[f"{plant}_{K}"],
                              "numerator": r[f"line_{K}"], "denominator": r[f"{plant}_{K}"],
                              "denominator_sd": r[f"{plant}_{K}_sd"],
                              "denominator_within_1sd_of_zero":
                                  abs(r[f"{plant}_{K}"]) < r[f"{plant}_{K}_sd"]}
                          for K in Ks}
                  for plant in ("burst", "fuzz", "wave")}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--no-edges", action="store_true",
                    help="skip the window-edge shares, which read the export folder")
    a = ap.parse_args(argv)
    run = Path(a.run)
    from bugarach import provenance
    summary = {"produced_by": "tools/summarize_tube_self_supervised.py",
               "provenance": provenance.stamp(produced_by="tools/summarize_tube_self_supervised.py"),
               "bakeoff": bakeoff(run), "training": training(run), "aggregate_leak": aggregate(run),
               "controls_lab": controls(run), "real_compare": real(run, not a.no_edges),
               "probe": probe(run)}
    (run / "summary.json").write_text(json.dumps(summary, indent=1, default=float))
    print(run / "summary.json")


if __name__ == "__main__":
    main()
