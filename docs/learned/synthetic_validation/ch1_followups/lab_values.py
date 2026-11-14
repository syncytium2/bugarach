"""Task 4 (murderboard 2026-10-29, role 4): the joint fit and the coordination-rates prediction at
realistic parameter values, per recording. A synthetic check, not a statement about any recording.

Parameter values: sigma 0.105 s with renewal trains of the fast stream's gap list, and sigma
0.131 s with the slow stream's gap list (both from runs/2026-09-25-real-intervals/gaps.csv, via
theory.load_gaps); k = 7 and 13 of 33 cells; background 0.0096 Hz per cell; 45 min; 40
recordings per (stream, k). Event rate lam = 1 / mean gap, as theory.check_real.

This is theory.check_real() (theory.py --check-real) with three additions: every recording's joint
fit is kept (so the spread and the count at each of the fit's bounds can be given, not just
quartiles), the per-recording solve() is summarized beside the pooled one, and the slow list is
run too. Recordings come from theory._realgap_recording itself, with theory.REAL switched to the
slow values inside each worker for the slow arm. The fast arm uses check_real's seeds
(1000 k + i), so it reproduces theory_check_real.json; the slow arm uses 1000 k + 500 + i.

Fit bounds (theory.fit_joint): sigma 0.005-5 s (its own at_bound flag, within 2 %), k 2.001-33,
lam 1e-6-1 Hz; a k or lam "at bound" here is within 2 % of its limit.

    PYTHONPATH=src python docs/learned/synthetic_validation/ch1_followups/lab_values.py --workers 40
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

STREAMS = {"fast": dict(sigma=0.105, seed_offset=0), "slow": dict(sigma=0.131, seed_offset=500)}
N_REC = 40


def worker(args):
    stream, k, seed, gaps = args
    theory.REAL.update(stream=stream, sigma=STREAMS[stream]["sigma"])
    return theory._realgap_recording((k, seed, gaps))


def q3(v):
    v = np.asarray([x for x in v if x is not None and np.isfinite(x)], float)
    return [float(x) for x in np.percentile(v, [25, 50, 75])] if v.size else [float("nan")] * 3


def run_stream(stream, ex):
    c = dict(theory.REAL, stream=stream, sigma=STREAMS[stream]["sigma"])
    N, T, s = c["n_cells"], c["T"], c["sigma"]
    gaps = theory.load_gaps(stream)
    lam_f = 1.0 / gaps.mean()
    args = [(stream, k, 1000 * k + STREAMS[stream]["seed_offset"] + i, gaps)
            for k in c["ks"] for i in range(N_REC)]
    rows = list(ex.map(worker, args))
    m_bar = lam_f * (T - 2 * c["margin"])
    renewal = EventTrain.renewal(intervals=gaps, name=f"{stream} gaps")
    planted_gaps = np.concatenate([np.diff(r["times"]) for r in rows])
    m_meas = float(np.mean([len(r["times"]) for r in rows]))
    lam_meas = m_meas / T
    palm = EventTrain.palm(planted_gaps, lam_meas, name="planted gaps")
    out = dict(stream=stream, sigma=s, ks=list(c["ks"]), bg=c["bg"], n_cells=N, T=T, n_rec=N_REC,
               n_gaps=int(gaps.size), mean_gap=float(gaps.mean()), lam_f=lam_f,
               lam_planted=lam_meas, events_per_recording_mean=m_meas, windows=[], fits=[])
    for k in c["ks"]:
        rs = [r for r in rows if r["k"] == k]
        lam_i = np.array([r["true"]["lam"] for r in rs])
        for w in theory.mcr.WINDOWS:
            f2 = np.array([r["cum"][str(w)]["f2"] for r in rs])
            f3 = np.array([r["cum"][str(w)]["f3"] for r in rs])
            v = theory.mcr.solve(f2.mean(), f3.mean(), N, w, "fixed")
            per = [theory.mcr.solve(a, b, N, w, "fixed") for a, b in zip(f2, f3)]
            pk = [p["k"] / k for p in per]
            pl = [p["lam"] / li for p, li in zip(per, lam_i)]
            pred = dict(page=theory.predict_solve(k, s, w, lam_f, N),
                        general=theory.predict_solve(k, s, w, lam_f, N, train=renewal, n_events=m_bar),
                        palm=theory.predict_solve(k, s, w, lam_meas, N, train=palm, n_events=m_meas))
            out["windows"].append(dict(
                k=k, w=w, pooled=dict(k=v["k"] / k, lam=v["lam"] / lam_i.mean()),
                per_recording_k_q=q3(pk), per_recording_lam_q=q3(pl),
                per_recording_refused=int(np.sum(~np.isfinite(pk))), predicted=pred))
        for lab, tr, ne in (("page", None, None), ("general", renewal, m_bar), ("palm", palm, m_meas)):
            for r in rs:
                f = theory.fit_joint(r["cum"], N, train=tr, n_events=ne)
                out["fits"].append(dict(
                    k=k, form=lab, seed=r["seed"], lam_true=r["true"]["lam"],
                    sigma=f["sigma"] if f else None, k_fit=f["k"] if f else None,
                    lam=f["lam"] if f else None, sigma_at_bound=bool(f["at_bound"]) if f else None))
    return out


def summarize(out):
    s, N = out["sigma"], out["n_cells"]
    print(f"\n=== {out['stream']} gap list ({out['n_gaps']} gaps, mean {out['mean_gap']:.2f} s): "
          f"sigma {s} s, b {out['bg']} Hz/cell, {N} cells, {out['T']:.0f} s, {out['n_rec']} "
          f"recordings per k; lam = 1/mean gap = {out['lam_f']:.5f} Hz = {3600 * out['lam_f']:.1f} "
          f"per hour (planted {out['lam_planted']:.5f} Hz, {out['events_per_recording_mean']:.1f} "
          f"events per recording)")
    print("  coordination-rates tool, ratio to planted. measured: solve() on the mean f2, f3 | "
          "per-recording solve() median [IQR] (refused) || predicted page | general | palm")
    for r in out["windows"]:
        for q, lab in (("lam", "rate"), ("k", "participants")):
            pq = r[f"per_recording_{q}_q"]
            p = r["predicted"]
            print(f"  k {r['k']:2d} w {r['w']:g} s {lab:12s}: {r['pooled'][q]:.3f} | "
                  f"{pq[1]:.2f} [{pq[0]:.2f}, {pq[2]:.2f}] ({r['per_recording_refused']}) || "
                  f"{p['page'][q]:.3f} | {p['general'][q]:.3f} | {p['palm'][q]:.3f}")
    print("  joint fit per recording, fitted / planted: median [IQR]; at bound = within 2 % of the "
          "fit's limits (sigma 0.005 or 5 s; k 2.001 or 33; lam 1e-6 or 1 Hz)")
    summ = []
    for k in out["ks"]:
        for lab in ("page", "general", "palm"):
            fs = [f for f in out["fits"] if f["k"] == k and f["form"] == lab]
            ok = [f for f in fs if f["sigma"] is not None]
            sr = [f["sigma"] / s for f in ok]
            kr = [f["k_fit"] / k for f in ok]
            lr = [f["lam"] / f["lam_true"] for f in ok]
            sb_lo = sum(f["sigma"] <= 0.005 * 1.02 for f in ok)
            sb_hi = sum(f["sigma"] >= 5.0 / 1.02 for f in ok)
            kb_lo = sum(f["k_fit"] <= 2.001 * 1.02 for f in ok)
            kb_hi = sum(f["k_fit"] >= N / 1.02 for f in ok)
            lb = sum(f["lam"] <= 1e-6 * 1.02 or f["lam"] >= 1 / 1.02 for f in ok)
            within = sum(0.8 <= x <= 1.25 for x in sr)
            a, b, c = q3(sr); ka, kb, kc = q3(kr); la, lb_, lc = q3(lr)
            print(f"  k {k:2d} {lab:7s}: sigma {b:.2f} [{a:.2f}, {c:.2f}] (range {min(sr):.3f}-"
                  f"{max(sr):.2f}); k {kb:.2f} [{ka:.2f}, {kc:.2f}]; lam {lb_:.2f} [{la:.2f}, {lc:.2f}] "
                  f"| usable {len(ok)}/{len(fs)}; sigma at lower bound {sb_lo}, upper {sb_hi}; "
                  f"k at bound {kb_lo}+{kb_hi}; lam at bound {lb}; sigma within 0.8-1.25x: "
                  f"{within}/{len(ok)}")
            summ.append(dict(k=k, form=lab, usable=len(ok), n=len(fs), sigma_ratio_q=[a, b, c],
                             sigma_ratio_range=[float(min(sr)), float(max(sr))],
                             k_ratio_q=[ka, kb, kc], lam_ratio_q=[la, lb_, lc],
                             sigma_at_lower=int(sb_lo), sigma_at_upper=int(sb_hi),
                             k_at_bound=int(kb_lo + kb_hi), lam_at_bound=int(lb),
                             sigma_within_0_8_1_25=int(within)))
    out["fit_summary"] = summ


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=40)
    ap.add_argument("--from-record", action="store_true")
    a = ap.parse_args()
    path = HERE / "lab_values.json"
    if a.from_record:
        res = json.loads(path.read_text())
    else:
        res = {}
        with ProcessPoolExecutor(a.workers) as ex:
            for st in STREAMS:
                t0 = time.time()
                res[st] = run_stream(st, ex)
                print(f"{st}: {time.time() - t0:.0f} s", file=sys.stderr)
    for st in res.values():
        summarize(st)
    path.write_text(json.dumps(res, indent=1, default=float))
