"""Round 3, task 6 (blind review roles 6 and 7): the assessor's own jitter null.

bugarach.assess.assess_coactivity returns, per K, jit_obs (median SD of the observed clusters'
gathered onsets), jit_null (the same median over every cluster of every circular-shift
surrogate) and jit_excess = jit_obs - jit_null. The first experiment (aim1_one_source.py) ran 120
surrogates and kept only jit_obs. Here the 240 Aim 1a recordings are regenerated exactly as
assessor_jitter.py regenerates them (aim1_one_source's arguments and seed path,
1000 + 100 condition + seed) and assess_coactivity is run at its SHIPPED settings: window = the
whole 45 min, min_rois = (3, 4, 6), n_surrogates = its default (1000, read from the signature),
rng_seed default. jit_obs is checked against the record's assess.jit.

Reported per (b, K, sigma), events of 10+ cells pooled as Figure 1.1 D/H (20 recordings):
median jit_obs, jit_null, jit_excess, and recordings with jit_defined False; beside the
background-only chance-cluster SDs of assessor_jitter.json (its table (ii)).

    PYTHONPATH=src python docs/learned/synthetic_validation/ch1_followups/assessor_null.py --workers 44
"""
from __future__ import annotations

import argparse
import inspect
import itertools
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SV = HERE.parent
sys.path.insert(0, str(SV))
import aim1_one_source as a1  # noqa: E402


def job(args):
    idx, (jit, part, n_ev, bg, seed) = args
    from bugarach.assess import assess_coactivity
    from bugarach.simulate import simulate_coordination
    s, gt = simulate_coordination(
        duration_sec=a1.DURATION, n_roi=a1.N_ROI, bg_rate_hz=bg, participation=(part,),
        n_per_level=(n_ev,), jitter_sec=jit, min_sep_sec=a1.MIN_SEP, grid_sec=0.1,
        seed=1000 + 100 * idx + seed)
    recs = assess_coactivity(s, window=(0.0, a1.DURATION), min_rois=a1.KS)
    return dict(cell=idx, seed=seed, jit=jit, part=part, n_ev=n_ev, bg=bg,
                k=int(max(1, np.floor(part * a1.N_ROI + 0.5))),
                res={str(r.min_rois): dict(jit_obs=r.jit_obs, jit_null=r.jit_null,
                                           jit_excess=r.jit_excess, jit_defined=bool(r.jit_defined),
                                           clusters_permin=r.clusters_permin) for r in recs})


def med(v):
    v = np.asarray([x for x in v if np.isfinite(x)], float)
    return float(np.median(v)) if v.size else float("nan")


if __name__ == "__main__":
    from bugarach.assess import assess_coactivity
    shipped = inspect.signature(assess_coactivity).parameters["n_surrogates"].default
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=44)
    ap.add_argument("--from-record", action="store_true")
    a = ap.parse_args()
    path = HERE / "assessor_null.json"
    if a.from_record:
        rec = json.loads(path.read_text())
    else:
        cells = list(itertools.product(a1.JITTERS, a1.PARTS, a1.N_EVENTS, a1.BG_RATES))
        grid = [(i, (*c, s)) for i, c in enumerate(cells) for s in a1.SEEDS]
        # busiest first, so the pool's tail is short
        grid.sort(key=lambda g: -g[1][3])
        t0 = time.time()
        with ProcessPoolExecutor(a.workers) as ex:
            rows = list(ex.map(job, grid))
        rec = dict(n_surrogates=shipped, rows=rows, runtime_sec=time.time() - t0)
        print(f"{rec['runtime_sec']:.0f} s", file=sys.stderr)
    rows = rec["rows"]
    orig = {(r["cell"], r["seed"]): r for r in json.loads((SV / "aim1_one_source.json").read_text())["rows"]}
    diffs = [abs(r["res"][K]["jit_obs"] - orig[(r["cell"], r["seed"])]["assess"][K]["jit"])
             for r in rows for K in r["res"]
             if np.isfinite(r["res"][K]["jit_obs"]) and np.isfinite(orig[(r["cell"], r["seed"])]["assess"][K]["jit"])]
    print(f"assess_coactivity at shipped settings, n_surrogates = {rec['n_surrogates']} (signature default); "
          f"240 regenerated Aim 1a recordings; jit_obs vs record: max |diff| {max(diffs):.2e} over {len(diffs)}")
    bgsum = {(d["bg"], d["K"]): d for d in json.loads((HERE / "assessor_jitter.json").read_text())["summary"]["background"]}
    print("\nevents of 10+ cells pooled (20 recordings per cell): median jit_obs / jit_null / jit_excess (s) "
          "[recordings with jit_defined False]; background-only chance-cluster SD median (assessor_jitter)")
    summ = []
    for bg in a1.BG_RATES:
        for K in a1.KS:
            bs = bgsum.get((bg, K))
            line = f"  b {bg} K {K} (chance-cluster SD alone {bs['cluster_sd_median']:.3f}):" if bs else f"  b {bg} K {K}:"
            for s in a1.JITTERS:
                rs = [r for r in rows if r["bg"] == bg and r["jit"] == s and r["k"] >= 10]
                v = {q: med([r["res"][str(K)][q] for r in rs]) for q in ("jit_obs", "jit_null", "jit_excess")}
                nd = sum(not r["res"][str(K)]["jit_defined"] for r in rs)
                summ.append(dict(bg=bg, K=K, sigma=s, n=len(rs), undefined=nd, **v,
                                 chance_sd_bg_only=bs["cluster_sd_median"] if bs else None))
                line += f" | sigma {s}: {v['jit_obs']:.3f} / {v['jit_null']:.3f} / {v['jit_excess']:+.3f} [{nd}]"
            print(line)
    rec["summary"] = summ
    path.write_text(json.dumps(rec, indent=1, default=float))
