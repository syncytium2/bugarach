#!/usr/bin/env python3
"""Two questions the fitted kernels raised, put to the simulated data.

    python tools/ablate_tube.py --spec docs/learned/generator_spec.json \
        --out docs/learned

Drawing the trained operator (``make_architecture_figures.py``) turned up two
things a block diagram could not, and both were left untested:

1. **The four-scale bank collapsed.** Centres initialised a doubling apart at 1,
   2, 4 and 8 samples all trained into 4.0–6.6. A bank whose scales converge is
   one scale with redundant copies — so does it score any differently with one?
2. **A fitted surround ratio sat at 38 against a clamp of 40.** By this project's
   own rule about the threshold grid, a value at the end of its range is the
   search reporting the range was wrong. Where does it settle when the ceiling is
   raised, and does the transfer penalty move with it?

Both run through **the same fold procedure as the bake-off** — train on three
folds, score on the held-out fourth, all rotations — so the numbers are
comparable with `bakeoff.json` rather than to each other only. `fair_bakeoff`'s
own helpers are imported rather than reimplemented; a second scorer is how the two
halves of a comparison end up on different metrics.

⚠ **One training run per fold, one seed.** Same limitation as everything else
learned in this project: fold spread confounds data variation with training
variation, so a difference of a few hundredths here is not a result. This is
sized to catch a *design* difference, not a small one.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
import sys
import time
from pathlib import Path

VARIANTS = [
    # label, architecture overrides
    ("4 scales, clamp 40 (as published)", {}),
    ("1 scale,  clamp 40", {"n_scales": 1}),
    ("2 scales, clamp 40", {"n_scales": 2}),
    ("4 scales, clamp 200", {"max_ratio": 200.0}),
    ("1 scale,  clamp 200", {"n_scales": 1, "max_ratio": 200.0}),
]


def _fb():
    spec = importlib.util.spec_from_file_location(
        "_fb", Path(__file__).parent / "fair_bakeoff.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(spec: dict, *, folds: int, seeds_per_fold: int, steps: int) -> dict:
    from bugarach.bench import pool_scores
    from bugarach.learn.train import fold_maker, train
    from bugarach.score import score_stream

    fb = _fb()
    all_seeds = [1000 + i for i in range(folds * seeds_per_fold)]
    fold_of = {s: i // seeds_per_fold for i, s in enumerate(all_seeds)}
    cache: dict[int, tuple] = {}

    def rec(seed):
        if seed not in cache:
            cache[seed] = fb._make_recording(spec, seed)
        return cache[seed]

    out = {"spec": spec, "folds": folds, "seeds_per_fold": seeds_per_fold,
           "steps": steps, "variants": {}}

    for label, over in VARIANTS:
        per_fold = []
        for held in range(folds):
            tr_seeds = [s for s in all_seeds if fold_of[s] != held]
            te_seeds = [s for s in all_seeds if fold_of[s] == held]
            # `fold_maker`, not an index by seed-modulo-length — the latter hands
            # `pick_threshold` the recordings the fit just used, defeating a
            # separation it asserts. #356 fixed that in `fair_bakeoff.py` and
            # `lab.py` and MISSED this file, so every number in
            # `tube_ablation.json` before 2026-08-28 was fitted that way.
            mk, n_fit, _ = fold_maker(rec, tr_seeds)

            t0 = time.perf_counter()
            tr = train("tube", mk, n_train=min(10, n_fit), steps=steps,
                       crop=4096, batch=3, lr=1e-2, **over)
            train_sec = time.perf_counter() - t0

            te = [rec(sd) for sd in te_seeds]
            scs = [score_stream(gt, tr.predict(sl)[0]) for sl, gt in te]
            p = pool_scores(scs, detector="tube", regime="heldout", seeds=te_seeds)

            m = tr.model
            per_fold.append(dict(
                fold=held, f1=p.f1, recall=p.recall, precision=p.precision,
                threshold=float(tr.threshold), n_params=int(tr.n_params),
                train_sec=train_sec,
                centres=[math.exp(v) for v in m.log_center.tolist()],
                ratios=[math.exp(v) for v in m.log_ratio.tolist()],
            ))
            print(f"  {label:34s} fold {held}: F1 {p.f1:.3f}  "
                  f"centres {[round(c,1) for c in per_fold[-1]['centres']]}  "
                  f"ratios {[round(r) for r in per_fold[-1]['ratios']]}")

        f1s = [f["f1"] for f in per_fold]
        out["variants"][label] = {
            "label": label,
            "overrides": over, "per_fold": per_fold,
            "f1": fb._spread(f1s),
            "n_params": per_fold[0]["n_params"],
            "train_sec": fb._spread([f["train_sec"] for f in per_fold]),
        }
    # Slugged aliases: the report builder addresses stores with a narrow token
    # grammar ([A-Za-z0-9_.-]), so a label with spaces and parentheses cannot be
    # quoted from the page. Same objects, addressable names.
    # The lookups are hoisted out of the f-string ON PURPOSE. A backslash inside
    # a replacement field — the `\d` of `r'(\d+)'` — is a SyntaxError on 3.11 and
    # became legal only in 3.12. No test imports this module, so nothing ever
    # parsed it on the floor and the tree carried a tool that could not run on
    # the oldest Python it claims to support. Found by
    # `tests/test_syntax_floor.py`, which parses every file rather than only the
    # ones something happens to import.
    def slug(k: str) -> str:
        scale = re.search(r"(\d+) scale", k).group(1)
        clamp = re.search(r"clamp (\d+)", k).group(1)
        return f"s{scale}_c{clamp}"

    out["by_key"] = {slug(k): v for k, v in out["variants"].items()}
    return out


def report(res: dict) -> str:
    lines = ["", "TUBE ABLATION — same folds, same scorer as the bake-off", ""]
    lines.append(f"{'variant':36s} {'F1 mean':>8} {'sd':>6} {'range':>13} "
                 f"{'params':>7}  fitted ratios (max over folds)")
    for label, v in res["variants"].items():
        f1 = v["f1"]
        top = max(max(f["ratios"]) for f in v["per_fold"])
        clamp = v["overrides"].get("max_ratio", 40.0)
        flag = "  <- AT CLAMP" if top > 0.9 * clamp else ""
        lines.append(f"{label:36s} {f1['mean']:8.3f} {f1['sd']:6.3f} "
                     f"{f1['min']:.2f}-{f1['max']:.2f}   {v['n_params']:7d}  "
                     f"max {top:6.1f} of {clamp:g}{flag}")
    return "\n".join(lines)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--spec", type=Path, required=True)
    p.add_argument("--out", type=Path, default=None)
    p.add_argument("--folds", type=int, default=4)
    p.add_argument("--seeds-per-fold", type=int, default=2)
    p.add_argument("--steps", type=int, default=900)
    a = p.parse_args(argv)

    spec = json.loads(a.spec.read_text())["generator"]
    res = run(spec, folds=a.folds, seeds_per_fold=a.seeds_per_fold,
              steps=a.steps)
    print(report(res))
    if a.out:
        a.out.mkdir(parents=True, exist_ok=True)
        f = a.out / "tube_ablation.json"
        f.write_text(json.dumps(res, indent=1, sort_keys=True))
        print(f"\nwrote {f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
