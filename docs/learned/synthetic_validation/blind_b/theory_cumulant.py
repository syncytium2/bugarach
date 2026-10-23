"""Analytic prediction for measure_coordination_rates (factorial-cumulant tool) vs aim1_one_source.json.

Model: events at rate lam, each with exactly k participants, onsets N(t, sigma^2) quantised to
0.1 s; windows of w tile time with uniform phase.  Excess factorial cumulants per window:
    f2 = lam w k(k-1) P2,   f3 = lam w k(k-1)(k-2) P3,
    P_m = E[(1 - R_m / w)_+],  R_m = range of m onsets of one event (quantised).
Background (independent Poisson) contributes zero in expectation.  Then solve('fixed'):
    k_hat = (k-2) P3/P2 + 2,  lam_hat = f2/(w k_hat(k_hat-1)),  share_hat = lam_hat k_hat / N.
Noise (leading order, Poisson background mu = N b w per window, n = T/w windows):
    SD(f2) ~ sqrt((2 mu^2 + 4 mu E[S^2]) / n),  SD(f3) ~ sqrt((6 mu^3 + 18 mu^2 E[S^2]) / n)
with E[S^2] ~ lam w k^2 (signal onsets per window).  Times sqrt(1 + 1/20) for the surrogate mean.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REC = HERE.parent / "docs/learned/synthetic_validation/aim1_one_source.json"
DT = 0.1


def P_m(sigma, w, m, n_mc=400_000, seed=0):
    """E[(1 - R/w)+] for m quantised N(0, sigma) onsets, window phase uniform (Monte Carlo)."""
    rng = np.random.default_rng(seed)
    x = sigma * rng.standard_normal((n_mc, m)) + rng.uniform(0, DT, (n_mc, 1))
    xq = np.round(x / DT)                       # frames
    wf = int(round(w / DT))
    ph = rng.integers(0, wf, (n_mc, 1))          # window phase in frames
    win = np.floor((xq + ph) / wf)
    same = (win == win[:, :1]).all(axis=1)       # all m in the same tile
    return same.mean()


def predict(sigma, w, k, N, n_ev, T, b):
    P2, P3 = P_m(sigma, w, 2), P_m(sigma, w, 3)
    lam = n_ev / T
    f2 = lam * w * k * (k - 1) * P2
    f3 = lam * w * k * (k - 1) * (k - 2) * P3
    kh = f3 / f2 + 2
    lh = f2 / (w * kh * (kh - 1))
    sh = lh * kh / N
    mu = N * b * w
    n = T / w
    ES2 = lam * w * k * k
    sd2 = np.sqrt((2 * mu**2 + 4 * mu * ES2) / n * 1.05)
    sd3 = np.sqrt((6 * mu**3 + 18 * mu**2 * ES2) / n * 1.05)
    return dict(P2=P2, P3=P3, k=kh, lam=lh, share=sh, f2=f2, f3=f3, sd2=sd2, sd3=sd3)


def main():
    rec = json.loads(REC.read_text())
    N, T = rec["n_roi"], rec["duration_sec"]
    rows = rec["rows"]
    cells = {}
    for r in rows:
        t = r["true"]
        key = (t["jitter"], int(t["k"]), t["n_events"], t["bg_rate"])
        cells.setdefault(key, []).append(r)
    cache = {}
    out = []
    for w in ("1.0", "2.0", "4.0"):
        for key, rs in sorted(cells.items()):
            sig, k, n_ev, b = key
            if (sig, float(w), k, n_ev, b) not in cache:
                cache[(sig, float(w), k, n_ev, b)] = predict(sig, float(w), k, N, n_ev, T, b)
            p = cache[(sig, float(w), k, n_ev, b)]
            obs = {q: np.array([x["coord_rates"][w][q] for x in rs], float) for q in ("k", "lam", "share")}
            f2o = obs["lam"] * float(w) * obs["k"] * (obs["k"] - 1)
            f3o = (obs["k"] - 2) * f2o
            tr = rs[0]["true"]
            out.append(dict(w=float(w), sigma=sig, k=k, n_ev=n_ev, b=b,
                            k_pred=p["k"] / k, k_obs=float(np.nanmedian(obs["k"])) / k,
                            lam_pred=p["lam"] / tr["lam"], lam_obs=float(np.nanmedian(obs["lam"])) / tr["lam"],
                            sh_pred=p["share"] / tr["share"], sh_obs=float(np.nanmedian(obs["share"])) / tr["share"],
                            n_nan=int(np.isnan(obs["k"]).sum()),
                            f2_pred=p["f2"], f2_obs=float(np.nanmedian(f2o)),
                            f3_pred=p["f3"], f3_obs=float(np.nanmedian(f3o)),
                            snr2=p["f2"] / p["sd2"], snr3=p["f3"] / p["sd3"],
                            k_iqr=float(np.subtract(*np.nanpercentile(obs["k"], [75, 25]))) / k))
    json.dump(out, open(HERE / "theory_cumulant_out.json", "w"), indent=1)

    # Table A: pooled over n_ev and bg (they should not matter for the mean): pred vs obs by sigma, w, k
    print("Table A: participants k_hat/k, rate lam_hat/lam, share_hat/share ; pred | obs (median over 20 recs)")
    print(f"{'w':>4} {'sig':>5} {'k':>3} | {'k pr':>5} {'k ob':>5} | {'lam pr':>6} {'lam ob':>6} | {'sh pr':>5} {'sh ob':>5}")
    for w in (1.0, 2.0, 4.0):
        for sig in (0.05, 0.2, 0.5, 1.0):
            for k in (5, 10, 20):
                sel = [o for o in out if o["w"] == w and o["sigma"] == sig and o["k"] == k]
                # observed: median over all 20 recordings
                rs = [x for key, v in cells.items() if key[0] == sig and key[1] == k for x in v]
                ko = np.nanmedian([x["coord_rates"][str(w)]["k"] for x in rs]) / k
                lo = np.nanmedian([x["coord_rates"][str(w)]["lam"] / x["true"]["lam"] for x in rs])
                so = np.nanmedian([x["coord_rates"][str(w)]["share"] / x["true"]["share"] for x in rs])
                print(f"{w:4.0f} {sig:5.2f} {k:3d} | {sel[0]['k_pred']:5.2f} {ko:5.2f} | "
                      f"{sel[0]['lam_pred']:6.2f} {lo:6.2f} | {sel[0]['sh_pred']:5.2f} {so:5.2f}")
    # Table B: f2, f3 absolute pred vs obs, and SNR vs observed spread / NaN count
    print("\nTable B: noise. snr2, snr3 predicted; observed IQR of k_hat/k and NaN count of 5 seeds")
    print(f"{'w':>4} {'sig':>5} {'k':>3} {'nev':>3} {'b':>5} | {'f2 pr/ob':>8} {'f3 pr/ob':>8} | {'snr2':>6} {'snr3':>6} | {'kIQR':>5} {'nan':>3}")
    for o in out:
        if o["sigma"] in (0.05, 1.0):
            print(f"{o['w']:4.0f} {o['sigma']:5.2f} {o['k']:3d} {o['n_ev']:3d} {o['b']:5.2f} | "
                  f"{o['f2_pred']/o['f2_obs']:8.2f} {o['f3_pred']/o['f3_obs'] if o['f3_obs']>0 else float('nan'):8.2f} | "
                  f"{o['snr2']:6.1f} {o['snr3']:6.1f} | {o['k_iqr']:5.2f} {o['n_nan']:3d}")


if __name__ == "__main__":
    main()
