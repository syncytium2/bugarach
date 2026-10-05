"""Step B pilot: do nets separate from the coded reference on the SLOW bench, as they did on fast?

Same protocol on both benches (bugarach.bench, bugarach.bench_slow):
- nets: chorus_norm and tube at goal 2's UNTUNED configuration (tune_learned_vs_coact.UNTUNED,
  crop 4096, batch 3, n_train 10), training seeds 0-2, on the GPU; fitted on the bench's
  seeds 1000-1023 (both backgrounds) through fold_maker, which keeps a threshold block apart;
  each net decodes at its own threshold and its default merge gap.
- coded: CoactDetect, LoCo, SPIKE-synch at that bench's OPERATING_POINTS.
- scored on fresh seeds 4000-4023 per background (3000-3047 stay untouched for a final run),
  plus calls/hour on the bench's no-coordination recording at seeds 4000-4011.
"""
import importlib
import json
import sys
import time

import numpy as np

from bugarach.bench import pool_scores
from bugarach.learn.train import fold_maker, train
from bugarach.score import score_stream

UNTUNED = {"chorus_norm": dict(lr=1e-2, steps=900, roi_width=4, roi_depth=4, top_m=4),
           "tube": dict(lr=1e-2, steps=900, n_scales=4, width=8, max_ratio=40)}
FIT = tuple(range(1000, 1024))
TEST = tuple(range(4000, 4024))
NULLS = tuple(range(4000, 4012))
REG = ("baseline_quiet", "baseline_busy")
BUSY = 100_000


def f1_both(b, runner):
    f = []
    for r in REG:
        sc = []
        for s in TEST:
            sl, gt = b.make_recording(r, s)
            sc.append(score_stream(gt, runner(sl)))
        f.append(pool_scores(sc, detector="x", regime=r).f1)
    return f


def null_rate(b, runner):
    n, h = 0, 0.0
    for s in NULLS:
        sl, gt = b.make_null_recording(s + 50_000)
        n += score_stream(gt, runner(sl)).n_detected
        h += gt.params["duration_sec"] / 3600
    return n / h


def main(which, out):
    b = importlib.import_module(which)
    rec = lambda k: b.make_recording(REG[1] if k >= BUSY else REG[0], k % BUSY)  # noqa: E731
    ids = [x for s in FIT for x in (s, s + BUSY)]
    mk, n_fit, n_val = fold_maker(rec, ids)
    res = {"bench": which, "coded": {}, "nets": {}}
    for det in ("coact", "loco", "sync"):
        f = f1_both(b, lambda sl: b.run_detector(det, sl))
        res["coded"][det] = dict(f1=f, mean=float(np.mean(f)),
                                 null_per_hour=null_rate(b, lambda sl: b.run_detector(det, sl)))
        print(which, det, res["coded"][det], flush=True)
    for model, conf in UNTUNED.items():
        res["nets"][model] = []
        for seed in (0, 1, 2):
            t0 = time.time()
            c = dict(conf)
            tr = train(model, mk, n_train=10, steps=c.pop("steps"), crop=4096, batch=3,
                       lr=c.pop("lr"), seed=seed, device="cuda", **c)
            run = lambda sl: tr.predict(sl)[0]  # noqa: E731
            f = f1_both(b, run)
            row = dict(seed=seed, f1=f, mean=float(np.mean(f)), threshold=float(tr.threshold),
                       null_per_hour=null_rate(b, run), sec=round(time.time() - t0))
            res["nets"][model].append(row)
            print(which, model, row, flush=True)
            json.dump(res, open(out, "w"), indent=1)
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
