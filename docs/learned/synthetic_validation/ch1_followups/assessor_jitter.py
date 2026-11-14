"""Round 2, task 3 (murderboard 2026-10-29 round 2, roles 4, 7 and 11): why the assessor's jitter
reading goes flat.

The assessor (bugarach.assess.assess_coactivity, its `_clusters`) bins onsets in 1 s bins, takes
runs of bins with at least K distinct cells (merged when at most 2 bins apart) as clusters, puts
each cluster's centre at the mean of its bin centres, gathers EVERY cell's nearest onset within
+-1.5 s of the centre, keeps the cluster if at least K cells were gathered, and reports jit_obs =
the median over all kept clusters (chance clusters included) of the gathered onsets' SD (ddof 1).

The existing records cannot answer this: aim1_one_source.json's background-only arm stores only
clusters per minute, and its event-bearing rows store only each recording's jit_obs. So:

1. Background-only recordings, new: simulate_coordination exactly as aim1_one_source.chance_cell
   calls it (33 cells, 45 min, 0.1 s frame, no events), 40 per background (seeds 950000 + 1000 b
   + i, disjoint from chance_cell's). Every cluster's SD is kept.
2. The 240 Aim 1a recordings, regenerated through aim1_one_source's own seed path (as
   correlogram_vs_joint.py does; the onset counts are checked against the record). Each cluster is
   labelled an EVENT cluster when at least half of its gathered onsets are planted onsets (an
   onset equal to some PlantedEvent.onsets entry of that cell), else a CHANCE cluster.

Clusters are found by the shipped `_coact_count` and `_clusters`; a copy of `_clusters`' loop
here also returns each cluster's gathered onsets and centre (needed for the label), and its SDs
are asserted equal to `_clusters`' own, cluster by cluster. jit_obs is checked against
`assess_coactivity` (20 surrogates; jit_obs does not depend on them) on the first recordings.

Prediction of the chance share: chance clusters per minute c = 60 q (1 - q)^2 with q =
P(Binomial(33, 1 - exp(-b)) >= K) (theory.chance_clusters_per_min, 1 s bins, merge_bins 2), and
planted events per minute e = E / 45, every event assumed to give exactly one cluster:
chance share = c / (c + e).

Mixture (deliberately simple): the reading is predicted as the median of a two-part mixture,
  weight c / (c + e): the SDs of chance clusters, taken from the background-only recordings
                      at that b and K (empirical);
  weight e / (c + e): the SD (ddof 1) of an event cluster's gathered onsets, simulated as the k
                      participants' onsets N(0, sigma^2) kept if within +-1.5 s of the event
                      time (truncated Gaussian), plus one onset uniform on +-1.5 s from each of
                      the 33 - k other cells with probability 1 - exp(-3 b) (background cells
                      caught by the gather), rounded to the 0.1 s frame; kept only if at least K
                      onsets (20000 draws).
It is compared per condition (median over the 5 seeds' jit_obs) and pooled the way Figure 1.1 D/H
pools (events of 10+ cells: the median over the 20 recordings; for the mixture, all four
conditions' mixtures pooled with equal weight).

    PYTHONPATH=src python docs/learned/synthetic_validation/ch1_followups/assessor_jitter.py --workers 44
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SV = HERE.parent
ROOT = SV.parents[2]
for p in (SV, ROOT / "tools", ROOT / "src"):
    sys.path.insert(0, str(p))
import aim1_one_source as a1  # noqa: E402
import theory  # noqa: E402

KS = a1.KS
BW, MERGE, WM = 1.0, 2, 1.5
N_BG = 40


def clusters_detail(trains, counts, K, bin_width, n_bins, merge_bins, wm):
    """`assess._clusters`' loop, also returning each cluster's centre, gathered onsets and cells."""
    hit = np.flatnonzero(counts >= K)
    out = []
    if hit.size == 0:
        return out
    groups, cur = [], [int(hit[0])]
    for q in range(1, hit.size):
        if hit[q] - hit[q - 1] <= merge_bins:
            cur.append(int(hit[q]))
        else:
            groups.append(cur)
            cur = [int(hit[q])]
    groups.append(cur)
    for g in groups:
        tc = float(np.mean((np.asarray(g, float) + 0.5) * bin_width))
        gathered, who = [], []
        for r, v in enumerate(trains):
            if v.size == 0:
                continue
            near = v[np.abs(v - tc) <= wm]
            if near.size == 0:
                continue
            gathered.append(float(near[np.argmin(np.abs(near - tc))]))
            who.append(r)
        if len(gathered) >= K:
            oo = np.asarray(gathered)
            out.append(dict(tc=tc, onsets=oo, cells=who,
                            sd=float(np.std(oo, ddof=1)) if oo.size >= 2 else float("nan")))
    return out


def analyse(s, gt, check_assess=False):
    """Per K: every cluster's SD, size and label (event / chance), and jit_obs."""
    from bugarach.assess import _clusters, _coact_count, assess_coactivity
    st = next(iter(s.streams.values()))
    T = a1.DURATION
    trains = []
    for r in range(st.n_rois):
        v = np.asarray(st.t50rise[r], float).ravel()
        trains.append(v[np.isfinite(v) & (v >= 0.0) & (v <= T)])
    n_bins = int(np.ceil(T / BW))
    obs = _coact_count(trains, T, BW, n_bins)
    planted = defaultdict(set)
    for e in (gt.events if gt is not None else ()):
        for roi, t in zip(e.rois, e.onsets):
            planted[roi].add(round(float(t), 6))
    res = {}
    for K in KS:
        det = clusters_detail(trains, obs, K, BW, n_bins, MERGE, WM)
        sds_ref = _clusters(trains, obs, K, BW, n_bins, MERGE, WM)[0]
        assert len(sds_ref) == len(det) and np.allclose(sds_ref, [d["sd"] for d in det],
                                                         equal_nan=True), "copy differs"
        lab = []
        for d in det:
            n_pl = sum(round(t, 6) in planted[c] for t, c in zip(d["onsets"], d["cells"]))
            lab.append(bool(n_pl >= 0.5 * len(d["cells"])))
        res[str(K)] = dict(sd=[d["sd"] for d in det], n=[len(d["cells"]) for d in det],
                           event=lab, jit_obs=float(np.median(sds_ref)) if sds_ref else float("nan"))
    if check_assess:
        recs = assess_coactivity(s, window=(0.0, T), min_rois=KS, n_surrogates=20)
        for r in recs:
            a, b = r.jit_obs, res[str(r.min_rois)]["jit_obs"]
            assert (np.isnan(a) and np.isnan(b)) or abs(a - b) < 1e-12, (a, b)
    return res


def bg_job(args):
    bg, i = args
    from bugarach.simulate import simulate_coordination
    s, _ = simulate_coordination(duration_sec=a1.DURATION, n_roi=a1.N_ROI, bg_rate_hz=bg,
                                 participation=(0.3,), n_per_level=(0,), grid_sec=0.1,
                                 seed=950000 + 1000 * int(round(bg * 1000)) + i)
    return dict(bg=bg, i=i, res=analyse(s, None, check_assess=(i < 2)))


def ev_job(args):
    idx, (jit, part, n_ev, bg, seed) = args
    from bugarach.simulate import simulate_coordination
    s, gt = simulate_coordination(
        duration_sec=a1.DURATION, n_roi=a1.N_ROI, bg_rate_hz=bg, participation=(part,),
        n_per_level=(n_ev,), jitter_sec=jit, min_sep_sec=a1.MIN_SEP, grid_sec=0.1,
        seed=1000 + 100 * idx + seed)
    st = next(iter(s.streams.values()))
    import measure_coordination_rates as mcr   # onsets counted as aim1_one_source counts them
    n_on = int(sum(len(mcr._frames(np.asarray(t), 0.0, a1.DURATION)) for t in st.t50rise))
    return dict(cell=idx, seed=seed, jit=jit, part=part, n_ev=n_ev, bg=bg,
                k=int(max(1, np.floor(part * a1.N_ROI + 0.5))), n_onsets=n_on,
                res=analyse(s, gt, check_assess=(idx < 2 and seed == 0)))


def event_sd_model(k, sigma, bg, K, rng, n=20000):
    """SDs of model event clusters: truncated-Gaussian participants plus uniform background cells."""
    out = []
    p_bg = 1 - np.exp(-2 * WM * bg)
    for _ in range(n):
        x = rng.normal(0, sigma, k)
        x = x[np.abs(x) <= WM]
        nb = rng.binomial(a1.N_ROI - k, p_bg)
        x = np.concatenate([x, rng.uniform(-WM, WM, nb)])
        x = np.floor(x / 0.1 + 0.5) * 0.1
        if x.size >= K:
            out.append(float(np.std(x, ddof=1)))
    return np.array(out)


def mixture_median(chance_sds, event_sds, w_chance, rng, n=40000):
    nc = rng.binomial(n, w_chance)
    a = rng.choice(chance_sds, nc) if (nc and len(chance_sds)) else np.zeros(0)
    b = rng.choice(event_sds, n - nc) if (n - nc and len(event_sds)) else np.zeros(0)
    return float(np.median(np.concatenate([a, b])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=44)
    ap.add_argument("--from-record", action="store_true")
    a = ap.parse_args()
    path = HERE / "assessor_jitter.json"
    if a.from_record:
        rec = json.loads(path.read_text())
    else:
        t0 = time.time()
        cells = list(itertools.product(a1.JITTERS, a1.PARTS, a1.N_EVENTS, a1.BG_RATES))
        grid = [(i, (*c, s)) for i, c in enumerate(cells) for s in a1.SEEDS]
        with ProcessPoolExecutor(a.workers) as ex:
            bgs = list(ex.map(bg_job, [(b, i) for b in a1.BG_RATES for i in range(N_BG)]))
            evs = list(ex.map(ev_job, grid))
        print(f"{len(bgs)} background-only + {len(evs)} event recordings in "
              f"{time.time() - t0:.0f} s", file=sys.stderr)
        rec = dict(bg=bgs, ev=evs)
        path.write_text(json.dumps(rec, default=float))
    bgs, evs = rec["bg"], rec["ev"]
    orig = json.loads((SV / "aim1_one_source.json").read_text())
    by = {(r["cell"], r["seed"]): r for r in orig["rows"]}
    mism = sum(e["n_onsets"] != by[(e["cell"], e["seed"])]["true"]["n_onsets"] for e in evs)
    jdiff = max(abs(e["res"][str(K)]["jit_obs"] - by[(e["cell"], e["seed"])]["assess"][str(K)]["jit"])
                for e in evs for K in KS
                if np.isfinite(e["res"][str(K)]["jit_obs"]))
    print(f"regeneration: onset count differs from aim1_one_source.json in {mism} of {len(evs)}; "
          f"largest |jit_obs - record's jit| {jdiff:.2e} s")

    rng = np.random.default_rng(12345)
    print("\n(i)-(ii) chance clusters. predicted c = 60 q (1-q)^2 per min; measured on 40 "
          "background-only recordings per b. SD = per-cluster onset SD (s)")
    chance_sd = {}
    out_bg = []
    for bg in a1.BG_RATES:
        for K in KS:
            rows = [x["res"][str(K)] for x in bgs if x["bg"] == bg]
            sds = np.array([v for r in rows for v in r["sd"]])
            chance_sd[(bg, K)] = sds
            c_pred = theory.chance_clusters_per_min(a1.N_ROI, bg, K)
            c_meas = np.mean([len(r["sd"]) for r in rows]) / (a1.DURATION / 60)
            jo = [r["jit_obs"] for r in rows if np.isfinite(r["jit_obs"])]
            sz = np.array([v for r in rows for v in r["n"]])
            out_bg.append(dict(bg=bg, K=K, c_pred=c_pred, c_meas=float(c_meas),
                               n_clusters=int(sds.size),
                               cluster_sd_median=float(np.median(sds)) if sds.size else None,
                               cluster_sd_q=[float(x) for x in np.percentile(sds, [25, 75])] if sds.size else None,
                               jit_obs_median=float(np.median(jo)) if jo else None,
                               recordings_with_clusters=len(jo),
                               cluster_size_median=float(np.median(sz)) if sz.size else None))
            print(f"  b {bg} K {K}: chance clusters/min predicted {c_pred:.3f}, measured {c_meas:.3f} "
                  f"({sds.size} clusters); per-cluster SD median "
                  + (f"{np.median(sds):.3f} [{np.percentile(sds, 25):.3f}, {np.percentile(sds, 75):.3f}]"
                     if sds.size else "-")
                  + f"; jit_obs (background only) median over recordings "
                  + (f"{np.median(jo):.3f} s ({len(jo)} of {len(rows)} recordings with a cluster)"
                     if jo else "- (no clusters)")
                  + (f"; gathered cells median {np.median(sz):.0f}" if sz.size else ""))

    print("\n(i) chance share among event-bearing recordings' clusters: predicted c/(c+e), "
          "e = E/45 per min, every event one cluster | measured (label: >= half the gathered "
          "onsets planted); events of 10+ cells, by planted jitter")
    print("\n(iii) jitter reading (s): measured = median jit_obs; mixture = median of the "
          "two-part mixture above; also measured median SD of event-labelled clusters vs the "
          "model's. Events of 10+ cells.")
    hdr = (f"  {'b':>5} {'K':>2} {'sigma':>5} | {'share pred':>10} {'meas':>5} | "
           f"{'reading meas':>12} {'mixture':>7} | {'event-cl. SD meas':>17} {'model':>6} | "
           f"{'chance-cl. SD meas':>18}")
    print(hdr)
    out_ev, out_cond = [], []
    for bg in a1.BG_RATES:
        for K in KS:
            c = theory.chance_clusters_per_min(a1.N_ROI, bg, K)
            for sig in a1.JITTERS:
                sel = [e for e in evs if e["bg"] == bg and e["jit"] == sig and e["k"] >= 10]
                pooled_mix, share_p = [], []
                for (part, n_ev) in itertools.product(a1.PARTS, a1.N_EVENTS):
                    ss = [e for e in sel if e["part"] == part and e["n_ev"] == n_ev]
                    if not ss:
                        continue
                    k = ss[0]["k"]
                    e_rate = n_ev / (a1.DURATION / 60)
                    w = c / (c + e_rate)
                    msd = event_sd_model(k, sig, bg, K, rng)
                    mix = mixture_median(chance_sd[(bg, K)], msd, w, rng)
                    meas = float(np.nanmedian([x["res"][str(K)]["jit_obs"] for x in ss]))
                    lab = [v for x in ss for v in x["res"][str(K)]["event"]]
                    out_cond.append(dict(bg=bg, K=K, sigma=sig, k=k, n_events=n_ev,
                                         share_pred=w, share_meas=float(1 - np.mean(lab)) if lab else None,
                                         reading_meas=meas, mixture=mix,
                                         model_event_sd_median=float(np.median(msd))))
                    share_p.append(w)
                    nc = rng.binomial(10000, w)
                    pooled_mix.append(np.concatenate([
                        rng.choice(chance_sd[(bg, K)], nc) if nc and chance_sd[(bg, K)].size else np.zeros(0),
                        rng.choice(msd, 10000 - nc)]))
                allc = [(v, ev) for x in sel for v, ev in zip(x["res"][str(K)]["sd"], x["res"][str(K)]["event"])]
                share_m = 1 - np.mean([ev for _, ev in allc]) if allc else float("nan")
                ev_sd = [v for v, ev in allc if ev]
                ch_sd = [v for v, ev in allc if not ev]
                reading = float(np.nanmedian([x["res"][str(K)]["jit_obs"] for x in sel]))
                mixp = float(np.median(np.concatenate(pooled_mix)))
                model_ev = float(np.median(np.concatenate(
                    [event_sd_model(k_, sig, bg, K, rng, 5000) for k_ in (10, 20)])))
                row = dict(bg=bg, K=K, sigma=sig, share_pred=float(np.mean(share_p)),
                           share_meas=float(share_m), reading=reading, mixture=mixp,
                           event_sd_meas=float(np.median(ev_sd)) if ev_sd else None,
                           event_sd_model=model_ev,
                           chance_sd_meas=float(np.median(ch_sd)) if ch_sd else None,
                           n_clusters=len(allc))
                out_ev.append(row)
                print(f"  {bg:>5} {K:>2} {sig:>5} | {row['share_pred']:>10.2f} {share_m:>5.2f} | "
                      f"{reading:>12.3f} {mixp:>7.3f} | "
                      f"{(row['event_sd_meas'] or float('nan')):>17.3f} {model_ev:>6.3f} | "
                      f"{(row['chance_sd_meas'] or float('nan')):>18.3f}")
    print("\nper condition (k, E): share pred / meas, reading meas / mixture")
    for r in out_cond:
        print(f"  b {r['bg']} K {r['K']} sigma {r['sigma']:<4} k {r['k']:2d} E {r['n_events']:2d}: "
              f"share {r['share_pred']:.2f} / {r['share_meas'] if r['share_meas'] is not None else float('nan'):.2f}; "
              f"reading {r['reading_meas']:.3f} / {r['mixture']:.3f}")
    rec["summary"] = dict(background=out_bg, pooled=out_ev, per_condition=out_cond,
                          regeneration_mismatches=int(mism))
    path.write_text(json.dumps(rec, default=float))


if __name__ == "__main__":
    main()
