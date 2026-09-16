#!/usr/bin/env python3
"""Why does chorus not train? Fold 0 of the home bake-off, instrumented.

    PYTHONPATH=src python tools/diagnose_chorus_training.py

Prints, for chorus at initialisation and after 900 steps at learning rates 1e-2 and
1e-3, with `line` at 1e-2 beside it: the gradient norm reaching each block, the loss
every 50 steps, and whether the per-cell votes and the pooled channels depend on the
input at all. Output of the 2026-09-16 run is in
docs/learned/field_size_candidates/why_chorus.txt. Exploratory; writes nothing.
"""
import json
import sys
import time

import numpy as np
import torch

sys.path.insert(0, "tools")
from fair_bakeoff import _make_recording  # noqa: E402

from bugarach.bench import fold_split  # noqa: E402
from bugarach.learn import train as T  # noqa: E402
from bugarach.learn.encode import encode  # noqa: E402

spec = json.load(open("docs/learned/generator_spec.json"))["generator"]
split = fold_split(n_folds=4, seeds_per_fold=6)
cache = {}


def rec(s):
    if s not in cache:
        cache[s] = _make_recording(spec, s)
    return cache[s]


mk, n_fit, _ = T.fold_maker(rec, list(split.train(0)))

# one validation recording, encoded the way pick_threshold sees it
sl, gt = mk(T.VAL_SEED_BLOCK)
enc, y = T._recording(mk, T.VAL_SEED_BLOCK, 0.1, None)[:2]
x = torch.from_numpy(enc.raster).unsqueeze(0)
ev = y > 0


def inspect(tag, model):
    model.eval()
    with torch.no_grad():
        logit = model(x)[0].numpy()
        p = 1 / (1 + np.exp(-logit))
        out = {"p_max": float(p.max()), "p_q999": float(np.quantile(p, 0.999)),
               "p_mean_at_events": float(p[ev].mean()), "p_mean_elsewhere": float(p[~ev].mean()),
               "logit_sd_over_time": float(logit.std())}
        if hasattr(model, "roi"):
            b, n, t = x.shape
            h = torch.sigmoid(model.roi(x.reshape(b * n, 1, t))).reshape(b, n, -1, t)[0]
            active = x[0].bool().unsqueeze(1).expand_as(h)
            out["vote_mean"] = float(h.mean())
            out["vote_sd_over_cells_and_time"] = float(h.std())
            out["share_votes_saturated"] = float(((h < 0.01) | (h > 0.99)).float().mean())
            out["vote_mean_on_onset_frames"] = float(h[active].mean()) if active.any() else None
            pooled_mean = h.mean(0)
            out["pooled_mean_sd_over_time"] = float(pooled_mean.std(1).mean())
            out["pooled_mean_at_events_minus_elsewhere"] = float(
                (pooled_mean[:, ev].mean(1) - pooled_mean[:, ~ev].mean(1)).abs().max())
    print(tag, json.dumps({k: (round(v, 5) if isinstance(v, float) else v) for k, v in out.items()}))


def grad_split(name, lr):
    torch.manual_seed(0)
    m = T.ARCHITECTURES[name].make()
    data = [T._recording(mk, T.TRAIN_SEED_BLOCK + i, 0.1, None)[:2] for i in range(min(10, n_fit))]
    enc0, y0 = data[0]
    pi = np.flatnonzero(y0 > 0)
    a = int(np.clip(pi[0] - 2048, 0, enc0.n_frame - 4096))
    xb = torch.from_numpy(np.ascontiguousarray(enc0.raster[:, a:a + 4096])).unsqueeze(0)
    yb = torch.from_numpy(np.ascontiguousarray(y0[a:a + 4096])).unsqueeze(0)
    pos = float(np.mean([yy.mean() for _, yy in data]))
    lossf = torch.nn.BCEWithLogitsLoss(pos_weight=torch.tensor([(1 - pos) / pos]))
    loss = lossf(m(xb), yb)
    loss.backward()
    groups = {}
    for pname, p in m.named_parameters():
        g = pname.split(".")[0]
        groups.setdefault(g, 0.0)
        groups[g] += float(p.grad.norm() ** 2)
    print(f"{name} init gradient norm by block:", {k: f"{v ** 0.5:.2e}" for k, v in groups.items()})
    if hasattr(m, "roi"):
        inspect(f"{name} at init", m)


grad_split("chorus", 1e-2)
grad_split("line", 1e-2)

for name, lr in (("chorus", 1e-2), ("chorus", 1e-3), ("line", 1e-2)):
    t0 = time.time()
    tr = T.train(name, mk, n_train=min(10, n_fit), steps=900, crop=4096, batch=3, lr=lr, seed=0)
    print(f"\n{name} lr={lr:g}  {time.time() - t0:.0f} s  threshold {tr.threshold:.4f}")
    print("  loss every 50 steps:", [round(l, 3) for _, l in tr.history])
    inspect(f"  {name} lr={lr:g} trained", tr.model)
