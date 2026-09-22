"""Scratch (step A): participation against the coactivity floor K, both streams, same instrument.

participation = median participants per cluster / median ROI count, over the default folder's
baseline analysis windows (remeasure_bench's definition), at K = 3..6, bin 1 s, with a
bootstrap over recordings.
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

KS = (3, 4, 5, 6)


def one(args):
    folder, i, stream = args
    from bugarach.assess import assess_coactivity
    from bugarach.assess_folder import NoBaselineRegion, generation_window
    from bugarach.io import load_folder

    s = load_folder(Path(folder))[i]
    try:
        w, _ = generation_window(s)
    except NoBaselineRegion:
        return None
    if w is None or w[1] - w[0] < 900 or stream not in s.streams:
        return None
    res = assess_coactivity(s, stream=stream, window=w, n_surrogates=1000, min_rois=KS)
    return {int(r.min_rois): dict(n_roi=int(r.n_roi), part=float(r.part_n_obs),
                                  ev=float(r.ev_rate_permin)) for r in res}


def summarise(recs, k):
    n = np.median([r[k]["n_roi"] for r in recs])
    p = np.array([r[k]["part"] for r in recs])
    return float(np.median(p[np.isfinite(p)]) / n), int(np.isfinite(p).sum())


if __name__ == "__main__":
    from bugarach import dataset
    from bugarach.io import load_folder

    folder = dataset.default()
    n = len(load_folder(folder))
    out = {}
    for stream in ("fast", "slow"):
        with ProcessPoolExecutor(12) as ex:
            recs = [r for r in ex.map(one, [(str(folder), i, stream) for i in range(n)]) if r]
        rng = np.random.RandomState(7)
        out[stream] = {}
        for k in KS:
            pt, n_with = summarise(recs, k)
            draws = [summarise([recs[j] for j in rng.randint(0, len(recs), len(recs))], k)[0]
                     for _ in range(200)]
            lo, hi = np.percentile(draws, [2.5, 97.5])
            out[stream][k] = dict(participation=pt, lo=float(lo), hi=float(hi), recordings_with_clusters=n_with)
            print(f"{stream:4s} K={k}: participation {pt:.3f} [{lo:.3f}, {hi:.3f}]  "
                  f"({n_with} of {len(recs)} recordings form a cluster)")
    Path(sys.argv[1]).write_text(json.dumps(out, indent=1))
