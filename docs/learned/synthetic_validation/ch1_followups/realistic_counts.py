"""Round 2, tasks 1 and 2 (murderboard 2026-10-29 round 2, roles 4 and 6): Task 4 of round 1
(lab_values.py) rerun at the tabulated event counts, and the joint fit without knowing the train.

Why. lab_values.py planted the gap lists as renewal trains at lam = 1 / mean gap, which put 25.5
(fast) and 53.6 (slow) events in a 45-minute recording. The interval run's README
(runs/2026-09-25-real-intervals) tabulates 9.7 and 22.0 events per hour, about 7.3 and 16.5 per
45 minutes. This reruns the same check at those counts.

How the count is lowered: INDEPENDENT THINNING. The train is first drawn exactly as
theory._realgap_recording draws it (a stationary renewal train with gaps resampled from the list,
after a 4000 s run-in), then each event is kept with probability p = target rate x mean gap
(fast 9.7/h x 100.58 s = 0.271; slow 22.0/h x 51.35 s = 0.314), with its own random stream.
Independent thinning keeps the pair correlation g_E(tau) of the train exactly (rho_2 and lam^2
both scale by p^2), so the close pairs the list holds stay close pairs, and the "true" train the
general form is given is still EventTrain.renewal(intervals=gaps); only lam is lower. The
thinned train is again a renewal train (each interval is a geometric sum of list gaps), with
CV^2 = p CV^2_list + (1 - p); that CV^2 is what the fixed-count term uses (`fixed_count`). Nothing
else changes from lab_values.py: sigma 0.105 s (fast) / 0.131 s (slow), k = 7 and 13 of 33 cells,
b = 0.0096 Hz, 45 min, 0.1 s frame, simulate_coordination with its placement replaced by these
times, the shipped measure_coordination_rates, 40 recordings per (list, k). New seeds (generator
800000 + seed, train 700000 + seed, thinning 600000 + seed, surrogate 900000 + seed, with seed =
1000 k + 200 + i fast, 1000 k + 700 + i slow): disjoint from lab_values.py's.

Task 1 output: per window, the tool's measured reading (solve() on the mean f2, f3 over the 40
recordings, and the per-recording median) beside the hard-core (page) and general predictions,
and the joint fit per recording under the true train (general form, the thinned renewal train
with n_events = expected count) and the page's hard-core form.

Task 2 output: the same recordings fitted as an analyst who does not know the train would:
(a) a Poisson train (EventTrain.poisson(), with and without the fixed-count term at the expected
count), (b) the 20 s hard core, both as theory.py's hard-core form (train=None; the "page" row,
the form theory.check runs) and as EventTrain.hard_core(20) through the general machinery (the
tool's own surrogate).

    PYTHONPATH=src python docs/learned/synthetic_validation/ch1_followups/realistic_counts.py --workers 44
    ... realistic_counts.py --from-record      # reprint from realistic_counts.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SV = HERE.parent
sys.path.insert(0, str(SV))
import theory  # noqa: E402
from event_train import EventTrain  # noqa: E402

STREAMS = {"fast": dict(sigma=0.105, per_hour=9.7, seed_offset=200),
           "slow": dict(sigma=0.131, per_hour=22.0, seed_offset=700)}
N_REC = 40
FORMS = ("true", "page", "poisson", "poisson_fixed", "hardcore20")
FORM_LABEL = {"true": "true train (thinned renewal, general form, fixed count)",
              "page": "20 s hard core, theory.py's form (train=None)",
              "poisson": "Poisson train, general form, no fixed count",
              "poisson_fixed": "Poisson train, general form, fixed count at the expected count",
              "hardcore20": "20 s hard core, general form (tool's surrogate)"}


def recording(args):
    """theory._realgap_recording with the train thinned to probability p before planting."""
    stream, k, seed, gaps, p = args
    import measure_coordination_rates as mcr
    from bugarach import simulate as sim
    c = dict(theory.REAL, stream=stream, sigma=STREAMS[stream]["sigma"])
    T, lo, hi = c["T"], c["margin"], c["T"] - c["margin"]
    rng_t = np.random.RandomState(700000 + seed)
    t, times = lo - 4000.0, []
    while t < hi:
        t += gaps[rng_t.randint(0, gaps.size)]
        if lo <= t < hi:
            times.append(t)
    times = np.array(times)
    keep = np.random.RandomState(600000 + seed).random_sample(times.size) < p
    times = times[keep]
    orig = sim._place_renewal
    sim._place_renewal = lambda rng, m, lo_, hi_, ms, ex, cv: times.copy()  # noqa: E731
    try:
        s, gt = sim.simulate_coordination(
            duration_sec=T, n_roi=c["n_cells"], bg_rate_hz=c["bg"],
            participation=(k / c["n_cells"],), n_per_level=(times.size,), jitter_sec=c["sigma"],
            min_sep_sec=0.0, grid_sec=0.1, seed=800000 + seed)
    finally:
        sim._place_renewal = orig
    st = next(iter(s.streams.values()))
    L = int(round(T / mcr.DT))
    trains = [np.minimum(mcr._frames(np.asarray(tr), 0.0, T), L - 1) for tr in st.t50rise]
    m = mcr.measure(trains, L, np.random.RandomState(900000 + seed))
    cum = {w: dict(f2=float(v["f2"]), f3=float(v["f3"])) for w, v in m["cum"].items()}
    ev = np.array(sorted(e.time for e in gt.events))
    return dict(k=k, seed=seed, true=mcr.truth(gt, c["n_cells"], T), cum=cum, times=ev.tolist())


def thinned_train(gaps, p, name):
    """The renewal train of the gap list, thinned with probability p: same g_E, CV^2 thinned."""
    r = EventTrain.renewal(intervals=gaps, name=name)
    return EventTrain(r.tau, r.g, name + f", thinned p={p:.3f}", lam_f=p * r.lam_f,
                      cv2=p * r.cv2 + (1 - p), kind="renewal")


def train_for(form, gaps, p, m_bar, stream):
    if form == "true":
        return thinned_train(gaps, p, f"{stream} gaps"), m_bar
    if form == "page":
        return None, None
    if form == "poisson":
        return EventTrain.poisson(), None
    if form == "poisson_fixed":
        return EventTrain.poisson(), m_bar
    if form == "hardcore20":
        return EventTrain.hard_core(20.0), None
    raise ValueError(form)


def fit_block(args):
    """All recordings of one (stream, k, form): the train's coefficient table is built once."""
    stream, k, form, gaps, p, m_bar, cums = args
    tr, ne = train_for(form, gaps, p, m_bar, stream)
    N = theory.REAL["n_cells"]
    out = []
    for cum in cums:
        f = theory.fit_joint(cum, N, train=tr, n_events=ne)
        out.append(None if f is None else dict(sigma=f["sigma"], k=f["k"], lam=f["lam"]))
    return stream, k, form, out


def q3(v):
    v = np.asarray([x for x in v if x is not None and np.isfinite(x)], float)
    return [float(x) for x in np.percentile(v, [25, 50, 75])] if v.size else [float("nan")] * 3


def run(ex):
    res = {}
    jobs, meta = [], {}
    for stream, cfg in STREAMS.items():
        gaps = theory.load_gaps(stream)
        p = cfg["per_hour"] / 3600.0 * gaps.mean()
        args = [(stream, k, 1000 * k + cfg["seed_offset"] + i, gaps, p)
                for k in theory.REAL["ks"] for i in range(N_REC)]
        meta[stream] = (gaps, p, args)
        jobs.append(ex.map(recording, args))
    for (stream, (gaps, p, args)), it in zip(meta.items(), jobs):
        rows = list(it)
        T, margin = theory.REAL["T"], theory.REAL["margin"]
        lam_target = p / gaps.mean()
        m_bar = lam_target * (T - 2 * margin)
        res[stream] = dict(stream=stream, sigma=STREAMS[stream]["sigma"],
                           ks=list(theory.REAL["ks"]), bg=theory.REAL["bg"],
                           n_cells=theory.REAL["n_cells"], T=T, n_rec=N_REC,
                           mean_gap=float(gaps.mean()), p_thin=float(p),
                           lam_target=float(lam_target), m_bar=float(m_bar),
                           events_per_recording=[len(r["times"]) for r in rows
                                                 if r["k"] == theory.REAL["ks"][0]]
                           + [len(r["times"]) for r in rows if r["k"] == theory.REAL["ks"][1]],
                           rows=rows)
    fjobs = []
    for stream, r in res.items():
        gaps, p, _ = meta[stream]
        for k in r["ks"]:
            cums = [x["cum"] for x in r["rows"] if x["k"] == k]
            for form in FORMS:
                fjobs.append((stream, k, form, gaps, p, r["m_bar"], cums))
    for stream, k, form, out in ex.map(fit_block, fjobs):
        res[stream].setdefault("fits", {}).setdefault(str(k), {})[form] = out
    for stream, r in res.items():
        gaps, p, _ = meta[stream]
        N, s = r["n_cells"], r["sigma"]
        true_tr = thinned_train(gaps, p, f"{stream} gaps")
        r["windows"] = []
        for k in r["ks"]:
            rs = [x for x in r["rows"] if x["k"] == k]
            lam_i = np.array([x["true"]["lam"] for x in rs])
            for w in theory.mcr.WINDOWS:
                f2 = np.array([x["cum"][str(w)]["f2"] for x in rs])
                f3 = np.array([x["cum"][str(w)]["f3"] for x in rs])
                v = theory.mcr.solve(f2.mean(), f3.mean(), N, w, "fixed")
                per = [theory.mcr.solve(a, b, N, w, "fixed") for a, b in zip(f2, f3)]
                pk = [pp["k"] / k for pp in per]
                pl = [pp["lam"] / li if li > 0 else np.nan for pp, li in zip(per, lam_i)]
                pred = dict(page=theory.predict_solve(k, s, w, r["lam_target"], N),
                            general=theory.predict_solve(k, s, w, r["lam_target"], N,
                                                         train=true_tr, n_events=r["m_bar"]))
                r["windows"].append(dict(
                    k=k, w=w, pooled=dict(k=v["k"] / k, lam=v["lam"] / lam_i.mean()),
                    per_recording_k_q=q3(pk), per_recording_lam_q=q3(pl),
                    per_recording_refused=int(np.sum(~np.isfinite(pk))), predicted=pred))
    return res


def summarize(r):
    s, N = r["sigma"], r["n_cells"]
    ev = np.array(r["events_per_recording"])
    print(f"\n=== {r['stream']} gap list (mean gap {r['mean_gap']:.2f} s), thinned with p = "
          f"{r['p_thin']:.3f} to {3600 * r['lam_target']:.1f} events per hour = "
          f"{r['m_bar']:.2f} expected per recording; sigma {s} s, b {r['bg']} Hz/cell, {N} cells, "
          f"{r['T']:.0f} s, {r['n_rec']} recordings per k")
    print(f"  planted events per recording: mean {ev.mean():.2f}, median {np.median(ev):.0f}, "
          f"range {ev.min()}-{ev.max()}, recordings with < 3 events: {int(np.sum(ev < 3))} of {ev.size}")
    print("  coordination-rates tool, ratio to planted. measured: solve() on the mean f2, f3 "
          "(bootstrap SE) | "
          "per-recording solve() median [IQR] (refused) || predicted page (hard core) | general")
    for w in r["windows"]:
        # bootstrap SE of the pooled reading (400 resamples of the 40 recordings, as check_real)
        rs = [x for x in r["rows"] if x["k"] == w["k"]]
        f2 = np.array([x["cum"][str(w["w"])]["f2"] for x in rs])
        f3 = np.array([x["cum"][str(w["w"])]["f3"] for x in rs])
        li = np.array([x["true"]["lam"] for x in rs])
        bs, boot = np.random.RandomState(1), []
        for _ in range(400):
            ii = bs.randint(0, len(rs), len(rs))
            v = theory.mcr.solve(f2[ii].mean(), f3[ii].mean(), N, w["w"], "fixed")
            boot.append([v["lam"] / li[ii].mean(), v["k"] / w["k"]])
        w["pooled_se"] = dict(zip(("lam", "k"), np.nanstd(np.array(boot), axis=0).tolist()))
        for qk, lab in (("lam", "rate"), ("k", "participants")):
            pq = w[f"per_recording_{qk}_q"]
            p = w["predicted"]
            print(f"  k {w['k']:2d} w {w['w']:g} s {lab:12s}: {w['pooled'][qk]:.3f} "
                  f"(SE {w['pooled_se'][qk]:.3f}) | "
                  f"{pq[1]:.2f} [{pq[0]:.2f}, {pq[2]:.2f}] ({w['per_recording_refused']}) || "
                  f"{p['page'][qk]:.3f} | {p['general'][qk]:.3f}")
    print("  joint fit per recording, fitted / planted: median [IQR]; bounds = within 2 % of the "
          "fit's limits (sigma 0.005 / 5 s; k 2.001 / 33; lam 1e-6 / 1 Hz); 'in band' = within "
          "0.8-1.25 of planted; rate is against each recording's own planted rate")
    summ = []
    for k in r["ks"]:
        rs = [x for x in r["rows"] if x["k"] == k]
        for form in FORMS:
            fs = r["fits"][str(k)][form]
            ok = [(f, x) for f, x in zip(fs, rs) if f is not None]
            sr = [f["sigma"] / s for f, _ in ok]
            kr = [f["k"] / k for f, _ in ok]
            lr = [f["lam"] / x["true"]["lam"] for f, x in ok if x["true"]["lam"] > 0]
            sb_lo = sum(f["sigma"] <= 0.005 * 1.02 for f, _ in ok)
            sb_hi = sum(f["sigma"] >= 5.0 / 1.02 for f, _ in ok)
            kb = sum(f["k"] <= 2.001 * 1.02 or f["k"] >= N / 1.02 for f, _ in ok)
            lb = sum(f["lam"] <= 1e-6 * 1.02 or f["lam"] >= 1 / 1.02 for f, _ in ok)
            band = lambda v: int(sum(0.8 <= x <= 1.25 for x in v))  # noqa: E731
            a = dict(k=k, form=form, usable=len(ok), n=len(fs), sigma_q=q3(sr), k_q=q3(kr),
                     lam_q=q3(lr), sigma_lo=int(sb_lo), sigma_hi=int(sb_hi), k_bound=int(kb),
                     lam_bound=int(lb), sigma_band=band(sr), k_band=band(kr), lam_band=band(lr))
            summ.append(a)
            print(f"  k {k:2d} {form:13s}: sigma {a['sigma_q'][1]:.2f} [{a['sigma_q'][0]:.2f}, "
                  f"{a['sigma_q'][2]:.2f}] (bound lo {sb_lo}, hi {sb_hi}; band {a['sigma_band']}) | "
                  f"k {a['k_q'][1]:.2f} [{a['k_q'][0]:.2f}, {a['k_q'][2]:.2f}] (bound {kb}; band "
                  f"{a['k_band']}) | lam {a['lam_q'][1]:.2f} [{a['lam_q'][0]:.2f}, "
                  f"{a['lam_q'][2]:.2f}] (bound {lb}; band {a['lam_band']}/{len(lr)}) | usable "
                  f"{len(ok)}/{len(fs)}")
    r["fit_summary"] = summ


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=40)
    ap.add_argument("--from-record", action="store_true")
    a = ap.parse_args()
    path = HERE / "realistic_counts.json"
    if a.from_record:
        res = json.loads(path.read_text())
    else:
        t0 = time.time()
        with ProcessPoolExecutor(a.workers) as ex:
            res = run(ex)
        print(f"{time.time() - t0:.0f} s", file=sys.stderr)
    print("forms: " + "; ".join(f"{k} = {v}" for k, v in FORM_LABEL.items()))
    for r in res.values():
        summarize(r)
    path.write_text(json.dumps(res, indent=1, default=float))
