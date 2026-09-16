#!/usr/bin/env python3
"""Can a model tell a long line from a short one, and either from fuzz? Exploratory.

    python tools/probe_line_vs_fuzz.py --checkpoints <dir> --out <folder>

Tony, 2026-09-15, on the tube models trained against rigid shift: *"i wonder if we need an
orientation detector rather than a center-surround. something that fires looking at the raster as
a 1d line at each time window. when most rois fire it looks like a vertical line. two rois aren't
enough and noise/high background looks like fuzz"*.

This probe measures whether the models already here can make those distinctions. On a quiet
synthetic field it plants, one at a time:

* **line K** — K distinct ROIs, one onset each, inside one frame: the vertical line;
* **burst K** — K/4 ROIs firing 4 times each inside 0.4 s: the same ink, a quarter of the line;
* **fuzz K** — K distinct ROIs spread uniformly over 3 s: the same ROIs, no line;
* **wave K** — K distinct ROIs recruited one frame apart: the same ROIs, ordered rather than
  scattered. To a model that is permutation-invariant over ROIs this is fuzz with a different
  cover story, and that is the point of including it — the tilt a person sees in a raster is a
  fact about the row order, which no order-free detector reads.

A detector of coordination should rank line above burst and above fuzz at equal ink. Each model's
score is the maximum of its per-frame output within ±2 s of the plant, minus the same maximum on
the identical field with nothing planted, so a model's own scale cancels.

Models: every checkpoint in ``--checkpoints`` (the self-supervised fits), plus a supervised
``tube`` and ``tube_guard`` fitted here the way the bake-off fits them, and the untrained
architectures. Nothing is fitted to this probe.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import tube_self_supervised as ts                            # noqa: E402

TAG = "line-vs-fuzz-2026-09-15"
N_ROI, N_FRAMES, DT = 32, 6000, 0.1
BG_HZ = 0.0097
K_VALUES = (4, 8, 16)
BURST_FRAMES = 4
FUZZ_SEC = 3.0
N_FIELDS = 12
PAD_SEC = 2.0


def seed31(*key):
    from bugarach import surrogate_stats as ss
    return int(ss.seed_of((TAG,) + tuple(key)) & 0x7FFFFFFF)


def field(seed):
    """A quiet Poisson background, and the frame the plant goes in."""
    rng = np.random.RandomState(seed)
    x = (rng.rand(N_ROI, N_FRAMES) < BG_HZ * DT).astype(np.float32)
    return x, N_FRAMES // 2, rng


def plant(x, t0, kind, K, rng):
    x = x.copy()
    rois = rng.choice(N_ROI, size=min(K, N_ROI), replace=False)
    if kind == "line":
        x[rois, t0] = 1.0
    elif kind == "burst":
        n = max(1, K // 4)
        for r in rois[:n]:
            for j in range(4):
                x[r, t0 + j * (BURST_FRAMES // 4 + 1)] = 1.0
    elif kind == "fuzz":
        span = int(FUZZ_SEC / DT)
        for r in rois:
            x[r, t0 + rng.randint(-span // 2, span // 2)] = 1.0
    elif kind == "wave":
        for i, r in enumerate(rois):
            x[r, t0 - len(rois) // 2 + i] = 1.0
    else:                                                     # pragma: no cover
        raise ValueError(kind)
    return x


def peak(model, x, t0):
    z = ts.probs(model, x)
    a, b = t0 - int(PAD_SEC / DT), t0 + int(PAD_SEC / DT)
    return float(np.max(z[a:b]))


def score_model(model):
    out = {}
    for kind in ("line", "burst", "fuzz", "wave"):
        for K in K_VALUES:
            gaps = []
            for i in range(N_FIELDS):
                x, t0, rng = field(seed31("field", i))
                base = peak(model, x, t0)
                gaps.append(peak(model, plant(x, t0, kind, K, rng), t0) - base)
            out[f"{kind}_{K}"] = float(np.mean(gaps))
            out[f"{kind}_{K}_sd"] = float(np.std(gaps))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--checkpoints", default=None)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    import torch
    from bugarach.learn.nets import ARCHITECTURES
    from bugarach.learn.train import fold_maker, pin_threads, train
    from bugarach.bench import fold_split
    import fair_bakeoff as fb
    pin_threads()
    models = {}
    for name in ts.MODELS:
        torch.manual_seed(0)
        models[f"untrained {name}"] = ARCHITECTURES[name].make().eval()
        mk, n_fit, _ = fold_maker(ts.sim_recording, list(fold_split(
            n_folds=ts.N_FOLDS, seeds_per_fold=ts.SEEDS_PER_FOLD).seeds))
        tr = train(name, mk, n_train=min(10, n_fit), steps=900, crop=ts.CROP, batch=ts.BATCH,
                   lr=fb.LR[name], seed=0)
        models[f"supervised {name}"] = tr.model.eval()
    if a.checkpoints:
        from bugarach.learn import checkpoint
        for p in sorted(Path(a.checkpoints).glob("*.json")):
            models[f"no labels {p.stem}"] = checkpoint.load(p).model.eval()
    out = {}
    t0 = time.time()
    for label, m in models.items():
        out[label] = score_model(m)
        r = out[label]
        print(f"{label:36s} " + "  ".join(
            f"{k}: {r[k]:+.2f}" for k in ("line_16", "burst_16", "fuzz_16", "wave_16")),
            flush=True)
    dest = Path(a.out)
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "line_vs_fuzz.json").write_text(json.dumps(
        {"meta": {"tag": TAG, "n_roi": N_ROI, "n_frames": N_FRAMES, "dt": DT, "bg_hz": BG_HZ,
                  "K": K_VALUES, "n_fields": N_FIELDS, "seconds": time.time() - t0},
         "scores": out}, indent=2))
    print("done", dest)


if __name__ == "__main__":
    main()
