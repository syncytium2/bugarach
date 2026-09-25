#!/usr/bin/env python3
"""Score tuned CoactDetect settings and trained chorus checkpoints on bench seeds nothing chose on.

    python tools/score_bench_candidates.py --phase2 <folder> --out <folder> [--workers 20]

**Why.** The overnight run of 2026-09-24 tuned CoactDetect (``tools/search_all_settings.py``) and
trained two chorus nets (``tools/train_learned_on_bench.py``) on each of the fast, slow and combined
benches. Each tool scores on its own held-out seeds, and chorus's best seed is *chosen* on them, so
its F1 there is a selection score. This tool scores every candidate on **fresh** seeds
(:data:`SEEDS`, both backgrounds) so the two families are compared on recordings neither selection
saw, and it reports F1 **both ways** (ADR-0006): as scored, and with calls on decoys left out of
precision.

**Candidates per bench.**

* CoactDetect at the bench's shipped operating point, and at the search's proposal: the held-out
  candidate with the highest mean F1 whose gain over the shipped point has a 95% bootstrap interval
  above zero (the repository's retune rule), or the shipped point when none has. **Proposals are
  not written into the bench**; adopting one is Tony's.
* Every chorus seed that was trained, and which seed the training tool's own rule picks (highest
  mean held-out F1 among seeds at or under CoactDetect's empty-recording budget).

**Collapse** (``docs/todo/2026-09-19-chorus-norm-does-not-train-at-lr-0.03.md``): a fit that makes
exactly one call on every recording. Flagged per seed with the count of recordings where it made
one call, and kept in the table: dropping a collapsed fit would select on the outcome.

The run is stamped with the bench it measured; the bench is simulated, so there is no dataset.
"""
from __future__ import annotations

import argparse
import importlib
import json
import math
import multiprocessing as mp
import re
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

BENCHES = {"fast": "bugarach.bench", "slow": "bugarach.bench_slow",
           "combined": "bugarach.bench_combined"}
REG = ("baseline_quiet", "baseline_busy")
SEEDS = tuple(range(6000, 6024))
NULLS = tuple(range(6000, 6012))
MODELS = ("chorus_norm", "chorus_gain_norm")
_MODEL_CACHE: dict = {}


def proposal(search: dict, det: str = "coact") -> tuple[str, dict, dict]:
    """``(name, params, held-out row)``: the search's best held-out candidate for ``det`` whose
    gain interval is above zero, else the shipped point."""
    ho = search["held_out"][det]
    best = ("shipped", ho["shipped"])
    for name, row in ho.items():
        g = row.get("gain_vs_shipped") or {}
        if name != "shipped" and g.get("lo") is not None and g["lo"] > 0 \
                and row["mean_f1"] > best[1]["mean_f1"]:
            best = (name, row)
    return best[0], dict(best[1]["params"]), best[1]


def train_rows(log: Path) -> list[dict]:
    rows = []
    for line in log.read_text(encoding="utf-8").splitlines():
        if line.startswith("{") and '"seed"' in line:
            rows.append(json.loads(line))
    return rows


def picked(rows: list[dict], budget: float) -> dict | None:
    ok = [r for r in rows if r["null_per_hour"] <= budget] or rows
    return max(ok, key=lambda r: r["mean"]) if ok else None


CODED = ("coact", "loco", "sce", "rate", "sync", "cicada")


def _runner(kind: str, spec):
    if kind in CODED:
        def run(b, sl):
            return b.run_detector(kind, sl, **spec)
        return run
    path = Path(spec)
    if path not in _MODEL_CACHE:
        from bugarach.learn.checkpoint import load
        _MODEL_CACHE[path] = load(path)
    tr = _MODEL_CACHE[path]
    return lambda b, sl: tr.predict(sl)[0]


def job(args):
    bench, kind, name, spec, regime, seed = args
    from bugarach.score import score_stream
    b = importlib.import_module(BENCHES[bench])
    run = _runner(kind, spec)
    if regime == "null":
        sl, gt = b.make_null_recording(seed + b.NULL_SEED_OFFSET)
        det = run(b, sl)
        sc = score_stream(gt, det)
        return (bench, kind, name, regime, seed), dict(
            n_detected=sc.n_detected, hours=gt.params["duration_sec"] / 3600.0)
    if regime.startswith("elevated:"):
        # ADR-0009's elevated-rate recording; the maker adds ELEVATED_SEED_OFFSET itself.
        sl, gt = b.make_elevated_rate_recording(regime.split(":", 1)[1], seed)
        sc = score_stream(gt, run(b, sl))
        h0, h1 = gt.params["hot_window"]
        return (bench, kind, name, regime, seed), dict(
            calls_in=sc.hot_fa, calls_out=sc.n_detected - sc.hot_fa, minutes_in=(h1 - h0) / 60.0,
            hours_out=(gt.params["duration_sec"] - (h1 - h0)) / 3600.0)
    sl, gt = b.make_recording(regime, seed)
    sc = score_stream(gt, run(b, sl))
    return (bench, kind, name, regime, seed), sc


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--phase2", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--detectors", nargs="+", default=["coact"], choices=CODED,
                    help="coded detectors to score, shipped and proposal (default coact)")
    ap.add_argument("--search", default="search-coact-{bench}",
                    help="each bench's search folder under --phase2, {bench} filled in")
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)

    from bugarach.bench import pool_scores

    cands, meta = [], {}
    for bench, mod in BENCHES.items():
        b = importlib.import_module(mod)
        budget = float(b.MAX_FALSE_POSITIVES_PER_HOUR["coact"])
        search = json.loads((a.phase2 / a.search.format(bench=bench) / "search.json").read_text())
        meta[bench] = dict(budget_null_per_hour=budget,
                           search_elapsed_min=search.get("elapsed_min"), chorus={}, detectors={})
        for det in a.detectors:
            pname, pparams, prow = proposal(search, det)
            shipped = dict(b.OPERATING_POINTS[det].params)
            meta[bench]["detectors"][det] = dict(
                shipped=shipped, proposal=dict(name=pname, params=pparams, search_row=prow),
                budget_null_per_hour=float(b.MAX_FALSE_POSITIVES_PER_HOUR[det]))
            if det == "coact":      # the keys detect_with_floors.py reads
                meta[bench]["coact_shipped"] = shipped
                meta[bench]["coact_proposal"] = dict(name=pname, params=pparams,
                                                     search_row=prow)
            cands.append((bench, det, "shipped", shipped))
            if pname != "shipped":
                cands.append((bench, det, "proposal", pparams))
        for m in MODELS:
            log = a.phase2 / f"train-{m}-{bench}.log"
            if not log.exists():
                continue
            rows = train_rows(log)
            pick = picked(rows, budget)
            meta[bench]["chorus"][m] = dict(train_rows=rows,
                                            picked=pick["path"] if pick else None)
            for r in rows:
                cands.append((bench, "chorus", r["path"],
                              str(a.phase2 / f"models-{bench}" / r["path"])))

    jobs = [(bench, kind, name, spec, reg, s) for bench, kind, name, spec in cands
            for reg in REG for s in SEEDS]
    jobs += [(bench, kind, name, spec, "null", s) for bench, kind, name, spec in cands
             for s in NULLS]
    jobs += [(bench, kind, name, spec, f"elevated:{reg}", s) for bench, kind, name, spec in cands
             for reg in REG for s in NULLS]
    with mp.Pool(a.workers) as pool:
        got = dict(pool.map(job, jobs, chunksize=4))

    results = {}
    for bench, kind, name, spec in cands:
        row = {}
        one_call = 0
        for reg in REG:
            scores = [got[(bench, kind, name, reg, s)] for s in SEEDS]
            one_call += sum(sc.n_detected == 1 for sc in scores)
            r = pool_scores(scores, detector=kind, regime=reg, seeds=SEEDS)
            el = [got[(bench, kind, name, f"elevated:{reg}", s)] for s in NULLS]
            row[reg] = dict(f1=r.f1, f1_without_decoys=r.f1_without_decoys, recall=r.recall,
                            precision=r.precision,
                            precision_without_decoys=r.precision_without_decoys,
                            decoy_calls=r.decoy_calls, n_planted=r.n_planted, n_hit=r.n_hit,
                            n_detected=r.n_detected,
                            probe_calls_per_min=(sum(e["calls_in"] for e in el)
                                                 / sum(e["minutes_in"] for e in el)),
                            elevated_calls_per_hour_outside=(sum(e["calls_out"] for e in el)
                                                             / sum(e["hours_out"] for e in el)),
                            recall_by_participation={f"{f:g}": r.recall_at(f)
                                                     for f in sorted(r.by_frac)})
        nulls = [got[(bench, kind, name, "null", s)] for s in NULLS]
        row["null_calls_per_hour"] = (sum(n["n_detected"] for n in nulls)
                                      / sum(n["hours"] for n in nulls))
        row["mean_f1"] = float(np.mean([row[r]["f1"] for r in REG]))
        row["mean_f1_without_decoys"] = float(np.mean([row[r]["f1_without_decoys"] for r in REG]))
        row["recordings_with_one_call"] = int(one_call)
        row["collapsed"] = bool(one_call == len(REG) * len(SEEDS))
        results.setdefault(bench, {})[f"{kind}:{name}"] = row
        print(f"{bench:8s} {kind:6s} {name:34s} F1 {row['mean_f1']:.3f} "
              f"(without decoys {row['mean_f1_without_decoys']:.3f}), "
              f"{row['null_calls_per_hour']:.2f} calls/h on the empty recording"
              + ("  COLLAPSED" if row["collapsed"] else ""), flush=True)
    from bugarach.bench import ELEVATED_SEED_OFFSET, NULL_SEED_OFFSET
    rec = dict(seeds=[SEEDS[0], SEEDS[-1]],
               null_seeds=[NULLS[0] + NULL_SEED_OFFSET, NULLS[-1] + NULL_SEED_OFFSET],
               elevated_rate_seeds=[NULLS[0] + ELEVATED_SEED_OFFSET,
                                    NULLS[-1] + ELEVATED_SEED_OFFSET],
               benches=meta, results=results,
               note="floor: pre-ADR-0008 (min_rois >= 3 in the search; chorus has no floor)")
    (a.out / "candidates.json").write_text(json.dumps(rec, indent=1, default=float) + "\n")
    print(f"wrote {a.out / 'candidates.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
