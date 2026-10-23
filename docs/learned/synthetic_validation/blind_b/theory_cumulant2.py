"""Cumulant tool: first-principles prediction (mean + noise), tested against aim1_one_source.json.

MEAN (k fixed participants, Gaussian jitter sigma, onsets quantised to 0.1 s, events >= 20 s apart so a
tile holds at most one event, background independent Poisson, surrogate removes only per-cell terms):
  p = n_ev w / T (events per tile), m = p k (signal onsets per tile)
  f2 = p k(k-1) P2 - m^2 (1 - 1/N)
  f3 = p k(k-1)(k-2) P3 - 3 m p k(k-1) P2 + 2 m^3
  P_r = E[(1 - R_r/w)_+]  (R_r = range of r onsets of one event), averaged over the two tilings.
The m-terms are the 'hard-core' bias: the estimator's chance subtraction assumes events may share a tile;
the generator forbids it (min_sep 20 s >> w).
NOISE (delta method on sample factorial cumulants, tiles independent; B ~ Poisson(mu = N b w)):
  Var f2 ~ [2mu^2 a2 + 4mu E S^2 a1] / n + n_ev Var(C2) / n^2
  Var f3 ~ [6mu^3 a3 + 18mu^2 E S^2 a2 + 9mu E S_(2)^2 a1] / n + n_ev Var(C3) / n^2
  Cov    ~ [6mu E[S S_(2)] a1] / n + n_ev Cov(C2, C3) / n^2,   C_r = one event's tile-summed c_(r);  a_j = (1+2^-j)/2 (two half-offset tilings), x1.05 (20 surrogates)
S = signal onsets in a tile; its moments from a one-event Monte Carlo.
"""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REC = HERE.parent / "docs/learned/synthetic_validation/aim1_one_source.json"
DT = 0.1


def event_mc(sigma, w, k, n_mc=100_000, seed=1):
    rng = np.random.default_rng(seed)
    wf = int(round(w / DT))
    x = np.round((sigma * rng.standard_normal((n_mc, k)) + rng.uniform(0, wf * DT, (n_mc, 1))) / DT)
    tilings = []
    for off in (0, wf // 2):
        win = np.floor((x - off) / wf).astype(int)
        win -= win.min(axis=1, keepdims=True)
        c = np.zeros((n_mc, win.max() + 1))
        np.add.at(c, (np.repeat(np.arange(n_mc), k), win.ravel()), 1)
        tilings.append(c)
    f = {1: lambda c: c, 2: lambda c: c * (c - 1), 3: lambda c: c * (c - 1) * (c - 2)}

    def tile_sum(a, b=None):
        if b is None:
            return 0.5 * sum(f[a](c).sum(1) for c in tilings)
        return 0.5 * sum((f[a](c) * f[b](c)).sum(1) for c in tilings)
    C2, C3 = tile_sum(2), tile_sum(3)
    return dict(EC2=C2.mean(), EC3=C3.mean(), vC2=C2.var(), vC3=C3.var(), cC23=np.cov(C2, C3)[0, 1],
                S11=tile_sum(1, 1).mean(),
                S22=tile_sum(2, 2).mean(), S33=tile_sum(3, 3).mean(), S12=tile_sum(1, 2).mean(),
                S23=tile_sum(2, 3).mean())


def predict(sigma, w, k, N, n_ev, T, b):
    e = event_mc(sigma, w, k)
    n = T / w
    p = n_ev / n
    m = p * k
    f2 = p * e["EC2"] - m * m * (1 - 1 / N)
    f3 = p * e["EC3"] - 3 * m * p * e["EC2"] + 2 * m ** 3
    mu = N * b * w

    def a(j):
        return (1 + 2.0 ** -j) / 2
    VS, VS2, VS3, ES12, C23 = (p * e[q] for q in ("S11", "S22", "S33", "S12", "S23"))
    # the generator plants exactly n_ev events, so the signal-only term is the between-event variance
    V2 = (2 * mu**2 * a(2) + 4 * mu * VS * a(1)) / n * 1.05 + n_ev * e["vC2"] / n**2
    V3 = (6 * mu**3 * a(3) + 18 * mu**2 * VS * a(2) + 9 * mu * VS2 * a(1)) / n * 1.05 + n_ev * e["vC3"] / n**2
    C = (6 * mu * ES12 * a(1)) / n * 1.05 + n_ev * e["cC23"] / n**2
    r = f3 / f2
    kh = r + 2
    lh = f2 / (w * kh * (kh - 1))
    sdk = abs(r) * np.sqrt(max(V3 / f3**2 + V2 / f2**2 - 2 * C / (f2 * f3), 0))
    return dict(k=kh, lam=lh, share=lh * kh / N, f2=f2, f3=f3, sd2=np.sqrt(V2), sd3=np.sqrt(V3), sdk=sdk)


def main():
    rec = json.loads(REC.read_text())
    N, T = rec["n_roi"], rec["duration_sec"]
    cells = {}
    for r in rec["rows"]:
        t = r["true"]
        cells.setdefault((t["jitter"], int(t["k"]), t["n_events"], t["bg_rate"]), []).append(r)
    rows = []
    for w in (1.0, 2.0, 4.0):
        for key, rs in sorted(cells.items()):
            sig, k, n_ev, b = key
            p = predict(sig, w, k, N, n_ev, T, b)
            tr = rs[0]["true"]
            ko = np.array([x["coord_rates"][str(w)]["k"] for x in rs], float)
            lo = np.array([x["coord_rates"][str(w)]["lam"] for x in rs], float)
            so = np.array([x["coord_rates"][str(w)]["share"] for x in rs], float)
            rows.append(dict(w=w, sig=sig, k=k, n_ev=n_ev, b=b, kp=p["k"] / k, ko=ko / k,
                             lp=p["lam"] / tr["lam"], lo=lo / tr["lam"], sp=p["share"] / tr["share"],
                             so=so / tr["share"], sdk=p["sdk"] / k, snr3=p["f3"] / p["sd3"],
                             snr2=p["f2"] / p["sd2"]))
    print("T1  k_hat/k, lam_hat/lam, share_hat/share: predicted (mean over n_ev x b) | observed median of 20 recordings")
    print(f"{'w':>3} {'sig':>4} {'k':>3} | {'k pr':>5} {'k ob':>5} | {'lam pr':>6} {'lam ob':>6} | {'sh pr':>5} {'sh ob':>5}")
    allv = {"k": [], "lam": [], "share": []}
    for w in (1.0, 2.0, 4.0):
        for sig in (0.05, 0.2, 0.5, 1.0):
            for k in (5, 10, 20):
                sel = [o for o in rows if o["w"] == w and o["sig"] == sig and o["k"] == k]
                kp, lp, sp = (np.mean([o[q] for o in sel]) for q in ("kp", "lp", "sp"))
                ko, lo, so = (np.nanmedian(np.concatenate([o[q] for o in sel])) for q in ("ko", "lo", "so"))
                allv["k"].append(np.log(ko / kp)); allv["lam"].append(np.log(lo / lp)); allv["share"].append(np.log(so / sp))
                print(f"{w:3.0f} {sig:4.2f} {k:3d} | {kp:5.2f} {ko:5.2f} | {lp:6.2f} {lo:6.2f} | {sp:5.2f} {so:5.2f}")
    for nm, v in allv.items():
        v = np.array(v)
        print(f"  {nm}: obs/pred geo-mean {np.exp(np.nanmean(v)):.3f}; median |error| {100*(np.exp(np.nanmedian(np.abs(v)))-1):.1f}%; max {100*(np.exp(np.nanmax(np.abs(v)))-1):.0f}%")
    print("\nT1b  same, b = 0.01 cells only (low noise)")
    for nm, q, qp in (("k", "ko", "kp"), ("lam", "lo", "lp"), ("share", "so", "sp")):
        v = [np.log(np.nanmedian(o[q]) / o[qp]) for o in rows if o["b"] == 0.01]
        v = np.array(v)
        print(f"  {nm}: per-cell (5-seed median) obs/pred geo-mean {np.exp(np.nanmean(v)):.3f}; median |error| {100*(np.exp(np.nanmedian(np.abs(v)))-1):.1f}%; 90th pct {100*(np.exp(np.nanpercentile(np.abs(v),90))-1):.0f}%")
    print("\nT2  noise: predicted SD(k_hat/k) vs observed (5 seeds, IQR/1.349); snr3 = f3/SD(f3)")
    print(f"{'w':>3} {'sig':>4} {'k':>3} {'nev':>3} {'b':>4} | {'snr3':>6} {'sd pr':>6} {'sd ob':>6} {'nan':>3}")
    pr, ob = [], []
    for o in rows:
        fin = np.isfinite(o["ko"])
        sdo = np.subtract(*np.nanpercentile(o["ko"], [75, 25])) / 1.349 if fin.sum() >= 4 else np.nan
        if np.isfinite(sdo):
            pr.append(o["sdk"]); ob.append(sdo)
        if o["sig"] in (0.05, 1.0) and o["w"] in (1.0, 4.0):
            print(f"{o['w']:3.0f} {o['sig']:4.2f} {o['k']:3d} {o['n_ev']:3d} {o['b']:4.2f} | {o['snr3']:6.1f} {o['sdk']:6.3f} {sdo:6.3f} {int((~fin).sum()):3d}")
    pr, ob = np.array(pr), np.array(ob)
    print(f"  all {len(pr)} cells: median obs/pred SD {np.median(ob/pr):.2f}; corr of logs {np.corrcoef(np.log(pr), np.log(ob + 1e-4))[0, 1]:.2f}")
    s3 = np.array([o["snr3"] for o in rows]); nn = np.array([np.isnan(o["ko"]).sum() for o in rows])
    for lo_, hi_ in ((0, 1), (1, 2), (2, 4), (4, 1e9)):
        msk = (s3 >= lo_) & (s3 < hi_)
        print(f"  snr3 in [{lo_},{hi_}): {msk.sum()} cells, NaN fraction {nn[msk].sum() / (5 * max(msk.sum(), 1)):.2f}")
    json.dump([{kk: (vv.tolist() if isinstance(vv, np.ndarray) else vv) for kk, vv in o.items()} for o in rows],
              open(HERE / "theory_cumulant2_out.json", "w"))


if __name__ == "__main__":
    main()
