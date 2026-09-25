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

**On the realistic bench (ADR-0010, ``--realistic``)**, for every model in :data:`MODELS`: each
training recording also plants one event at each of its floor − 1, floor and floor + 1
(``learn.participation.boundary_recording``, #824); events under the floor are labelled no-event for
training (``floor_labels``), and stay "don't care" for scoring (ADR-0009 decision 2); fast's fit,
test and no-coordination seeds are doubled (ruling 2). The ``*_part`` variants also carry their
registered count, floor input and membership loss. Without the switch nothing changes.
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
MODELS = ("chorus_norm", "chorus_gain_norm", "line", "tube",
          "chorus_norm_part", "chorus_gain_norm_part", "line_part", "tube_part")
"""The panel ADR-0010 part 1 trains: the four learned families, and #824's participation variant
of each. A ``*_part`` variant takes its base's configuration; line and tube take the registry's."""
FIT = tuple(range(1000, 1024))
TEST = tuple(range(4000, 4024))
NULLS = tuple(range(4000, 4012))
REG = ("baseline_quiet", "baseline_busy")
BUSY = 100_000


def config(model: str) -> dict:
    """The constructor settings a model is trained with: its own entry in :data:`CONFIGS`, or its
    base's for a ``*_part`` variant, or none (the registry's defaults)."""
    return dict(CONFIGS.get(model) or CONFIGS.get(model.removesuffix("_part")) or {})


def seed_sets(bench: str, realistic: bool):
    """(fit, test, nulls) seeds. ADR-0010 ruling 2: on the realistic bench fast plants about 7
    events per recording instead of 15, so its seed counts are doubled to hold the number of
    scored events. The factor is ``bench.seed_factor``'s, the one place that decides it."""
    from bugarach.bench import seed_factor

    f = seed_factor(bench, "realistic" if realistic else "bench")
    return tuple(tuple(range(s[0], s[0] + len(s) * f)) for s in (FIT, TEST, NULLS))


def training_recording(b, realistic: bool):
    """``k -> (slice, gt)`` for training. On the realistic bench every training recording also
    plants events at its floor − 1, floor and floor + 1 (#824, ADR-0010 part 5); the scored
    recordings are never built this way."""
    if not realistic:
        return lambda k: b.make_recording(REG[1] if k >= BUSY else REG[0], k % BUSY)
    from bugarach.learn.participation import boundary_recording

    return lambda k: boundary_recording(b.make_recording, REG[1] if k >= BUSY else REG[0],
                                        k % BUSY)


def held_out(b, run, test=TEST, nulls=NULLS) -> dict:
    from bugarach.bench import pool_scores
    from bugarach.score import score_stream

    f1 = []
    for r in REG:
        sc = []
        for s in test:
            sl, gt = b.make_recording(r, s)
            sc.append(score_stream(gt, run(sl)))
        f1.append(pool_scores(sc, detector="x", regime=r).f1)
    n, h = 0, 0.0
    for s in nulls:
        sl, gt = b.make_null_recording(s + 50_000)
        n += score_stream(gt, run(sl)).n_detected
        h += gt.params["duration_sec"] / 3600
    return dict(f1=f1, mean=float(np.mean(f1)), null_per_hour=n / h)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bench", choices=sorted(BENCHES), required=True)
    ap.add_argument("--model", choices=sorted(MODELS), default="chorus_gain_norm")
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    ap.add_argument("--device", default=None, help="cuda, or omit for CPU (about 200 s a fit)")
    ap.add_argument("--steps", type=int, default=900)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--spacing", choices=("bench", "realistic", "orx"), default=None,
                    help="how the bench spaces its planted events (bench.SPACINGS; default "
                         "'bench', unchanged). 'realistic' (or 'orx') trains on the realistic "
                         "recordings with boundary planting and floor labels, fast's seeds "
                         "doubled (ADR-0010)")
    ap.add_argument("--realistic", action="store_true",
                    help="the same as --spacing realistic: realistic recordings with boundary "
                         "planting (events at floor - 1, floor, floor + 1; under the floor "
                         "labelled no-event for training only, don't-care for scoring), fast's "
                         "seeds doubled. Refused with --spacing bench")
    a = ap.parse_args(argv)

    from bugarach import bench as _b
    try:
        a.spacing = _b.spacing_from_args(a.spacing, a.realistic)
    except ValueError as e:
        ap.error(str(e))
    # One source of truth: the spacing. It plants the realistic recordings (bench.make_recording
    # reads it), and it is what switches on boundary planting and the doubled seeds below.
    _b.use_spacing(a.spacing)
    a.realistic = a.spacing != "bench"
    from bugarach.learn.checkpoint import save
    from bugarach.learn.train import fold_maker, train

    name = BENCHES[a.bench]
    b = importlib.import_module(name)
    fit, test, nulls = seed_sets(a.bench, a.realistic)
    rec = training_recording(b, a.realistic)
    mk, n_fit, n_val = fold_maker(rec, [x for s in fit for x in (s, s + BUSY)])
    budget = b.MAX_FALSE_POSITIVES_PER_HOUR["coact"]
    # ADR-0010 part 5: every model trained under it labels under-floor events no-event in
    # training. Unset otherwise, so each model keeps its registered default.
    extra = dict(floor_labels=True) if a.realistic else {}
    a.out.mkdir(parents=True, exist_ok=True)
    rows = []
    for seed in a.seeds:
        t0 = time.time()
        tr = train(a.model, mk, n_train=10, steps=a.steps, crop=4096, batch=3, lr=1e-2,
                   seed=seed, device=a.device, **extra, **config(a.model))
        path = a.out / f"{a.model}_{a.bench}_seed{seed}.json"
        how = ("participation.boundary_recording over " if a.realistic else "")
        save(tr, path, trained_on=f"{how}{name}.make_recording seeds {fit[0]}-{fit[-1]}, "
                                  f"quiet+busy, spacing {a.spacing}", train_seed=seed,
             steps=a.steps, n_fit=10, n_threshold_val=n_val,
             note=f"tools/train_learned_on_bench.py --bench {a.bench} --spacing {a.spacing}")
        row = dict(seed=seed, path=path.name, threshold=float(tr.threshold),
                   **held_out(b, lambda sl: tr.predict(sl)[0], test, nulls),
                   sec=round(time.time() - t0))
        rows.append(row)
        print(json.dumps(row), flush=True)

    ok = [r for r in rows if r["null_per_hour"] <= budget] or rows
    best = max(ok, key=lambda r: r["mean"])
    shutil.copyfile(a.out / best["path"], a.out / "best.json")
    summary = dict(bench=name, model=a.model, config=config(a.model),
                   spacing=a.spacing,
                   **(dict(realistic=True, floor_labels=True,
                           boundary_planting="floor - 1, floor, floor + 1; one event each")
                      if a.realistic else {}),
                   fit_seeds=[fit[0], fit[-1]], test_seeds=[test[0], test[-1]],
                   null_budget_per_hour=budget,
                   best_within_budget=best["null_per_hour"] <= budget,
                   best=best["path"], rows=rows,
                   caveat="best is chosen on the held-out seeds; its F1 is a selection score")
    (a.out / "summary.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    print(f"best: {best['path']} mean F1 {best['mean']:.3f}, {best['null_per_hour']:.2f} calls/h "
          f"on the no-coordination test (budget {budget:g})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
