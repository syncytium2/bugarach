"""Round 3, task 2 (blind review role 4): the assessor's chance clusters on an over-dispersed
background.

docs/generator.md reports baseline ROIs over-dispersed in time (variance/mean 1.81/2.60/3.87/5.68
at 30/60/120/300 s) and gives the generator's fitted two-scale mode, bg_burst_shape=(1.547, 1.388)
with bg_burst_bin_sec=(300.0, 60.0): each ROI's rate is multiplied, per 300 s bin and per 60 s
bin, by independent Gamma(shape, 1/shape) draws (mean 1), drawn PER ROI. Those values are used
here as simulation parameters only.

Background-only recordings, simulate_coordination as aim1_one_source.chance_cell calls it
(33 cells, 2700 s, 0.1 s frame, no events, b = 0.0096 Hz mean rate), 400 per arm (100 were
asked for; 400 cost seconds and give K = 5, 6 a usable count):
  flat     : homogeneous Poisson (the default, the chapter's model);
  bursty   : bg_burst_shape=(1.547, 1.388), bg_burst_bin_sec=(300, 60);
  bursty+rate: the same plus bg_rate_shape = bench.MEASURED_RATE_SHAPE (Gamma heterogeneity of
             the ROIs' own rates, mean kept at b) -- an extra arm, not asked for, because the flat
             formula assumes equal rates as well as Poisson.
Clusters are the shipped bugarach.assess `_coact_count` + `_clusters` (1 s bins, merge 2, gather
+-1.5 s, kept if >= K cells), as assessor_jitter.py uses them, at K = 3, 4, 5, 6. Prediction:
60 q (1 - q)^2 per minute (theory.chance_clusters_per_min), x 60 per hour.

Also: each arm's per-ROI variance/mean of counts in 30/60/120/300 s windows (pooled over ROIs with
>= 1 event, as a check that the mode is on), and the background rate b at which the smallest K
with under 1 chance cluster per hour changes from 4 to 5 (and 3 to 4) under the flat formula.

Seeds 7_100_000 + 1000 arm + i.

    PYTHONPATH=src python docs/learned/synthetic_validation/ch1_followups/chance_bursty.py --workers 40
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from scipy import optimize, stats

HERE = Path(__file__).resolve().parent
SV = HERE.parent
sys.path.insert(0, str(SV))
import theory  # noqa: E402

N, T, B, N_REC = 33, 2700.0, 0.0096, 400
KS = (3, 4, 5, 6)
BW, MERGE, WM = 1.0, 2, 1.5
SCALES = (30, 60, 120, 300)


def arms():
    from bugarach.bench import MEASURED_RATE_SHAPE
    return {"flat": {}, "bursty": dict(bg_burst_shape=(1.547, 1.388), bg_burst_bin_sec=(300.0, 60.0)),
            "bursty+rate": dict(bg_burst_shape=(1.547, 1.388), bg_burst_bin_sec=(300.0, 60.0),
                                bg_rate_shape=MEASURED_RATE_SHAPE, bg_rate_stat="mean")}


def job(args):
    ai, arm, i = args
    from bugarach.assess import _clusters, _coact_count
    from bugarach.simulate import simulate_coordination
    s, _ = simulate_coordination(duration_sec=T, n_roi=N, bg_rate_hz=B, participation=(0.3,),
                                 n_per_level=(0,), grid_sec=0.1, seed=7_100_000 + 1000 * ai + i,
                                 **arms()[arm])
    st = next(iter(s.streams.values()))
    trains = []
    for r in range(st.n_rois):
        v = np.asarray(st.t50rise[r], float).ravel()
        trains.append(v[np.isfinite(v) & (v >= 0.0) & (v <= T)])
    n_bins = int(np.ceil(T / BW))
    obs = _coact_count(trains, T, BW, n_bins)
    n_cl = {str(K): len(_clusters(trains, obs, K, BW, n_bins, MERGE, WM)[0]) for K in KS}
    disp = {}
    for w in SCALES:
        nb = int(T // w)
        c = np.array([np.histogram(v, bins=nb, range=(0, nb * w))[0] for v in trains], float)
        c = c[c.sum(1) > 0]
        m, var = c.mean(1), c.var(1, ddof=1)
        disp[str(w)] = [float(var.sum()), float(m.sum())]   # pooled: sum var / sum mean
    return dict(arm=arm, i=i, n_onsets=int(sum(v.size for v in trains)), clusters=n_cl, disp=disp)


def flip_b(K):
    """b at which the flat formula gives exactly 1 chance cluster per hour at threshold K."""
    f = lambda lb: 60 * theory.chance_clusters_per_min(N, np.exp(lb), K) - 1.0  # noqa: E731
    g = np.log(np.geomspace(1e-4, 0.2, 400))
    v = np.array([f(x) for x in g])
    j = int(np.flatnonzero((v[:-1] < 0) & (v[1:] >= 0))[0])     # first upward crossing
    return float(np.exp(optimize.brentq(f, g[j], g[j + 1])))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=40)
    a = ap.parse_args()
    t0 = time.time()
    names = list(arms())
    with ProcessPoolExecutor(a.workers) as ex:
        rows = list(ex.map(job, [(ai, arm, i) for ai, arm in enumerate(names) for i in range(N_REC)]))
    rt = time.time() - t0
    print(f"{rt:.0f} s", file=sys.stderr)
    rec = dict(N=N, T=T, b=B, n_rec=N_REC, Ks=KS, arms={k: {kk: list(vv) if isinstance(vv, tuple) else vv
                                                              for kk, vv in v.items()} for k, v in arms().items()},
               rows=rows, runtime_sec=rt, summary={})
    print(f"background only, {N} cells, {T:.0f} s, mean b {B} Hz, {N_REC} recordings per arm; shipped "
          "_coact_count/_clusters (1 s bins, merge 2, kept if >= K gathered)")
    print("per-ROI variance/mean of counts (pooled over ROIs with >= 1 onset), 30/60/120/300 s "
          "(generator.md: real 1.81/2.60/3.87/5.68; two-scale 1.87/2.76/3.04/4.44):")
    for arm in names:
        rs = [r for r in rows if r["arm"] == arm]
        d = [sum(r["disp"][str(w)][0] for r in rs) / sum(r["disp"][str(w)][1] for r in rs) for w in SCALES]
        on = np.mean([r["n_onsets"] for r in rs]) / (N * T)
        print(f"  {arm:12s}: " + " / ".join(f"{x:.2f}" for x in d) + f"   (mean rate {on:.4f} Hz)")
        rec["summary"][arm] = dict(dispersion=d, mean_rate=float(on))
    print("\nchance clusters per hour: mean over recordings [exact Poisson 95 % CI of the pooled "
          "count] (recordings with >= 1 cluster) | flat prediction 60 x 60 q (1-q)^2")
    for K in KS:
        pred = 60 * theory.chance_clusters_per_min(N, B, K)
        line = f"  K {K}: flat prediction {pred:8.4f} |"
        for arm in names:
            c = np.array([r["clusters"][str(K)] for r in rows if r["arm"] == arm])
            tot, hours = int(c.sum()), N_REC * T / 3600
            lo = stats.chi2.ppf(0.025, 2 * tot) / 2 / hours if tot else 0.0
            hi = stats.chi2.ppf(0.975, 2 * tot + 2) / 2 / hours
            rec["summary"][arm][f"K{K}"] = dict(per_hour=tot / hours, ci=[lo, hi], total=tot,
                                                recs_with=int(np.sum(c > 0)),
                                                var_over_mean=float(c.var(ddof=1) / c.mean()) if tot else None,
                                                predicted_flat=pred)
            line += (f" {arm} {tot / hours:8.4f} [{lo:.4f}, {hi:.4f}] ({int(np.sum(c > 0))});")
        print(line)
    for K in (3, 4, 5):
        fb = flip_b(K)
        rec["summary"][f"b_flip_K{K}"] = fb
        print(f"flat formula: 1 chance cluster per hour at K = {K} when b = {fb:.5f} Hz "
              f"(above it, K = {K} gives more than 1 per hour, so the smallest K under 1/hour becomes {K + 1})")
    (HERE / "chance_bursty.json").write_text(json.dumps(rec, indent=1))
