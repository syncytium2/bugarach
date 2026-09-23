#!/usr/bin/env python3
"""Train a learned detector on a bench module and save checkpoints ``bugarach detect --model`` runs.

    python tools/train_learned_on_bench.py --bench combined --model chorus_gain_norm \
        --seeds 0 1 2 3 4 --device cuda --out <claimed folder>/models

**Why.** The chorus lane on the real cohort rasters is a ``chorus_gain_norm`` checkpoint fitted on
the FAST bench (``docs/learned/tuned_vs_coact/replicate1/chosen/gated/outer0/chorus_gain_norm/
seed2.json``). Nothing on ``main`` trained one on another bench and kept it: the slow pilot
(``docs/learned/runs/2026-09-21-slow-pilot/slow_pilot.py``) scored its fits and saved none. This is
that pilot's protocol with :func:`bugarach.learn.checkpoint.save` at the end, so a slow or combined
stream gets a model of its own (Tony, 2026-09-22: combined, "just like fast and slow").

**Protocol, unchanged from the pilot and from the checkpoint above:** the configuration that
checkpoint was built with (:data:`CONFIGS`), 900 steps, crop 4096, batch 3, ``n_train`` 10; fitted
on the bench's seeds 1000–1023 on both backgrounds through ``fold_maker``, which keeps a threshold
block apart; scored on fresh seeds 4000–4023 per background, plus calls/hour on the bench's
no-coordination recording.

**About a sixth of chorus_gain_norm fits collapse** to F1 near 0.125
(``docs/goals/learned-model-family.md``). So several seeds are trained. ``best.json`` is the
seed with the highest mean held-out F1 among those at or under the bench's false-alarm budget
for CoactDetect, the anchor (``MAX_FALSE_POSITIVES_PER_HOUR['coact']``). Choosing on held-out
seeds 4000–4023 makes that F1 a selection score, not an unbiased estimate: say so wherever it
is quoted.
"""
from __future__ import annotations

import argparse
import importlib
import json
import shutil
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
if str(REPO / "src") not in sys.path:
    sys.path.insert(0, str(REPO / "src"))

BENCHES = {"fast": "bugarach.bench", "slow": "bugarach.bench_slow",
           "combined": "bugarach.bench_combined"}
CONFIGS = {
    "chorus_gain_norm": dict(roi_width=4, roi_depth=4, head_width=8, head_depth=8, top_m=4,
                             norm=True, vote_gain=8),
    "chorus_norm": dict(roi_width=4, roi_depth=4, top_m=4),
}
"""As built in the real-data checkpoint (chorus_gain_norm) and the pilot (chorus_norm)."""
FIT = tuple(range(1000, 1024))
TEST = tuple(range(4000, 4024))
NULLS = tuple(range(4000, 4012))
REG = ("baseline_quiet", "baseline_busy")
BUSY = 100_000


def held_out(b, run) -> dict:
    from bugarach.bench import pool_scores
    from bugarach.score import score_stream

    f1 = []
    for r in REG:
        sc = []
        for s in TEST:
            sl, gt = b.make_recording(r, s)
            sc.append(score_stream(gt, run(sl)))
        f1.append(pool_scores(sc, detector="x", regime=r).f1)
    n, h = 0, 0.0
    for s in NULLS:
        sl, gt = b.make_null_recording(s + 50_000)
        n += score_stream(gt, run(sl)).n_detected
        h += gt.params["duration_sec"] / 3600
    return dict(f1=f1, mean=float(np.mean(f1)), null_per_hour=n / h)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bench", choices=sorted(BENCHES), required=True)
    ap.add_argument("--model", choices=sorted(CONFIGS), default="chorus_gain_norm")
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    ap.add_argument("--device", default=None, help="cuda, or omit for CPU (about 200 s a fit)")
    ap.add_argument("--steps", type=int, default=900)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)

    from bugarach.learn.checkpoint import save
    from bugarach.learn.train import fold_maker, train

    name = BENCHES[a.bench]
    b = importlib.import_module(name)
    rec = lambda k: b.make_recording(REG[1] if k >= BUSY else REG[0], k % BUSY)  # noqa: E731
    mk, n_fit, n_val = fold_maker(rec, [x for s in FIT for x in (s, s + BUSY)])
    budget = b.MAX_FALSE_POSITIVES_PER_HOUR["coact"]
    a.out.mkdir(parents=True, exist_ok=True)
    rows = []
    for seed in a.seeds:
        t0 = time.time()
        tr = train(a.model, mk, n_train=10, steps=a.steps, crop=4096, batch=3, lr=1e-2,
                   seed=seed, device=a.device, **CONFIGS[a.model])
        path = a.out / f"{a.model}_{a.bench}_seed{seed}.json"
        save(tr, path, trained_on=f"{name}.make_recording seeds {FIT[0]}-{FIT[-1]}, quiet+busy",
             train_seed=seed, steps=a.steps, n_fit=10, n_threshold_val=n_val,
             note=f"tools/train_learned_on_bench.py --bench {a.bench}")
        row = dict(seed=seed, path=path.name, threshold=float(tr.threshold),
                   **held_out(b, lambda sl: tr.predict(sl)[0]), sec=round(time.time() - t0))
        rows.append(row)
        print(json.dumps(row), flush=True)

    ok = [r for r in rows if r["null_per_hour"] <= budget] or rows
    best = max(ok, key=lambda r: r["mean"])
    shutil.copyfile(a.out / best["path"], a.out / "best.json")
    summary = dict(bench=name, model=a.model, config=CONFIGS[a.model], fit_seeds=[FIT[0], FIT[-1]],
                   test_seeds=[TEST[0], TEST[-1]], null_budget_per_hour=budget,
                   best_within_budget=best["null_per_hour"] <= budget,
                   best=best["path"], rows=rows,
                   caveat="best is chosen on the held-out seeds; its F1 is a selection score")
    (a.out / "summary.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    print(f"best: {best['path']} mean F1 {best['mean']:.3f}, {best['null_per_hour']:.2f} calls/h "
          f"on the no-coordination test (budget {budget:g})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
