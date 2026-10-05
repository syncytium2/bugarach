#!/usr/bin/env python3
"""Two checks the final-parameters report's review asked for, recorded rather than quoted.

    python tools/final_parameters_review_checks.py --night <darkroom>/bugarach/2026-09-25-final-parameters \
        --out <that folder>/064/phase3-3x3/review_checks.json [--workers 44]

1. **The paired fresh-seed gain** of each strictly adoptable proposal: proposal minus shipped, on
   the same fresh recordings (seeds 6000–6023 per background), mean F1 over the two backgrounds,
   with a 95% interval from 2,000 paired resamples of recordings (the same resample index for both
   versions). The report's fresh intervals were per version; this is the interval on the gain.
2. **Fast CoactDetect's close-events loss against the point fast ships.** The search scored the
   held-out close-events recordings (seeds 49–60, both backgrounds) against the shipped values in
   their sliding form. This scores the binned operating point ``bench.OPERATING_POINTS`` declares
   and the proposal on the same recordings, and reports proposal minus shipped.

Floor: ADR-0008 per-window floor, bench per ADR-0009 (the bench modules apply it).
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

MODS = {"fast": "bugarach.bench", "slow": "bugarach.bench_slow",
        "combined": "bugarach.bench_combined"}
REG = ("baseline_quiet", "baseline_busy")
FRESH = tuple(range(6000, 6024))
TAIL = tuple(range(49, 61))
ADOPTABLE = (("fast", "sce"), ("combined", "sce"), ("combined", "rate"), ("combined", "sync"))


def score(args):
    stream, det, params, kind, regime, seed = args
    from bugarach.score import score_stream
    b = importlib.import_module(MODS[stream])
    if kind == "tail":
        s, gt = b.make_tail_recording(regime, seed)
    else:
        s, gt = b.make_recording(regime, seed)
    return args[3:], stream, det, json.dumps(params, sort_keys=True, default=str), \
        score_stream(gt, b.run_detector(det, s, **params))


def mean_f1(pool_scores, by_reg, idx):
    f = []
    for reg in REG:
        r = pool_scores([by_reg[reg][i] for i in idx[reg]], detector="x", regime=reg)
        f.append(r.f1)
    return float(np.mean(f))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--night", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=44)
    a = ap.parse_args(argv)
    from bugarach.bench import FLOOR_LABEL, pool_scores

    cand = {"fast": json.loads((a.night / "064/phase3/candidates.json").read_text(encoding="utf-8"))}
    cand["combined"] = json.loads((a.night / "065/phase3/candidates.json").read_text(encoding="utf-8"))
    versions = []
    for stream, det in ADOPTABLE:
        M = cand[stream]["benches"][stream]["detectors"][det]
        versions.append((stream, det, "shipped", dict(M["shipped"])))
        versions.append((stream, det, "proposal", dict(M["proposal"]["params"])))
    fast_coact = cand["fast"]["benches"]["fast"]["detectors"]["coact"]
    tail_versions = [("fast", "coact", "shipped (binned, as bench.py ships it)",
                      dict(importlib.import_module(MODS["fast"]).OPERATING_POINTS["coact"].params)),
                     ("fast", "coact", "proposal", dict(fast_coact["proposal"]["params"]))]
    jobs = [(s, d, p, "fresh", reg, seed) for s, d, _, p in versions for reg in REG for seed in FRESH]
    jobs += [(s, d, p, "tail", reg, seed) for s, d, _, p in tail_versions for reg in REG
             for seed in TAIL]
    with Pool(a.workers) as pool:
        got = pool.map(score, jobs, chunksize=2)
    table = {}
    for (kind, reg, seed), stream, det, key, sc in got:
        table.setdefault((stream, det, key, kind), {}).setdefault(reg, {})[seed] = sc

    def series(stream, det, params, kind, seeds):
        key = json.dumps(params, sort_keys=True, default=str)
        t = table[(stream, det, key, kind)]
        return {reg: [t[reg][s] for s in seeds] for reg in REG}

    rng = np.random.RandomState(20260925)
    n = len(FRESH)
    boots = [{reg: rng.randint(0, n, n) for reg in REG} for _ in range(2000)]
    full = {reg: np.arange(n) for reg in REG}
    paired = []
    for stream, det in ADOPTABLE:
        sh = series(stream, det, next(p for s, d, v, p in versions
                                      if (s, d, v) == (stream, det, "shipped")), "fresh", FRESH)
        pr = series(stream, det, next(p for s, d, v, p in versions
                                      if (s, d, v) == (stream, det, "proposal")), "fresh", FRESH)
        g = [mean_f1(pool_scores, pr, i) - mean_f1(pool_scores, sh, i) for i in boots]
        paired.append(dict(stream=stream, detector=det,
                           gain=mean_f1(pool_scores, pr, full) - mean_f1(pool_scores, sh, full),
                           ci=[float(np.percentile(g, 2.5)), float(np.percentile(g, 97.5))],
                           shipped_f1=mean_f1(pool_scores, sh, full),
                           proposal_f1=mean_f1(pool_scores, pr, full)))
        print(f"{stream} {det}: paired fresh gain {paired[-1]['gain']:+.4f} "
              f"[{paired[-1]['ci'][0]:+.4f}, {paired[-1]['ci'][1]:+.4f}]", flush=True)
    tl = {v: series("fast", "coact", p, "tail", TAIL) for _, _, v, p in tail_versions}
    tidx = {reg: np.arange(len(TAIL)) for reg in REG}
    crowd = {v: mean_f1(pool_scores, s, tidx) for v, s in tl.items()}
    names = list(crowd)
    close = dict(seeds=[TAIL[0], TAIL[-1]], backgrounds=list(REG), mean_f1=crowd,
                 loss=crowd[names[0]] - crowd[names[1]], allowance=0.02)
    print(f"fast coact close-events: {crowd}, loss {close['loss']:.4f}", flush=True)
    a.out.write_text(json.dumps(dict(
        floor=FLOOR_LABEL, tool="tools/final_parameters_review_checks.py",
        paired_fresh_gain=dict(seeds=[FRESH[0], FRESH[-1]], resamples=2000, rows=paired),
        fast_coact_close_events_vs_binned_shipped=close), indent=1, default=float) + "\n",
        encoding="utf-8")
    print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
