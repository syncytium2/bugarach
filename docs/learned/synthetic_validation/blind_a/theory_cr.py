"""Analytic prediction for measure_coordination_rates (+ solve, fixed model) on Aim 1a, vs the record.

Mean:  f2 = lam*w*[k(k-1)P2 - lam*w*k^2],  f3 = lam*w*[k(k-1)(k-2)P3 - 3 lam w k^2 (k-1) P2 + 2 (lam w)^2 k^3]
       (P2, P3 = probability two / three jittered, frame-quantized onsets of one event share a window).
Noise: Poisson background via Charlier polynomials: Var f2 = 2 mu^2/n, Var f3 = 6 mu^3/n per offset
       (two half-shifted offsets averaged: x0.75, x0.625), mu = N b w, n = T/w; plus event-by-event
       variability and event x background cross terms, from a cheap single-event Monte Carlo.
Prediction of the estimator's distribution: draw (f2, f3) ~ Gaussian(mean, cov), push through solve().
"""
from __future__ import annotations

import itertools
import sys

import numpy as np

from theory_common import DT, N, T, capture, kpart, load

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "tools"))
from measure_coordination_rates import solve  # noqa: E402

JITS, PARTS, NEVS, BGS, WS = (0.05, 0.2, 0.5, 1.0), (0.15, 0.3, 0.6), (15, 45), (0.01, 0.05), (1.0, 2.0, 4.0)


def event_mc(w, sigma, k, n=4000, seed=0):
    """Per-event window-count statistics, averaged over the tool's two offsets."""
    rs = np.random.RandomState(seed)
    wf = int(round(w / DT))
    t0 = rs.random_sample(n) * 1000 * w + 50 * w
    fr = np.floor((t0[:, None] + sigma * rs.randn(n, k)) / DT + 0.5).astype(int)
    out = {}
    for off in (0, wf // 2):
        b = (fr - off) // wf
        b = b - b.min(1, keepdims=True)
        Y = np.zeros((n, b.max() + 1))
        np.add.at(Y, (np.repeat(np.arange(n), k), b.ravel()), 1)
        for name, v in dict(S2=(Y * (Y - 1)).sum(1), S3=(Y * (Y - 1) * (Y - 2)).sum(1),
                            Q1=(Y ** 2).sum(1), Q2=((Y * (Y - 1)) ** 2).sum(1),
                            Q12=(Y * Y * (Y - 1)).sum(1)).items():
            out.setdefault(name, []).append(v)
    return {kk: np.mean(v, axis=0) for kk, v in out.items()}


def predict(sigma, f, m, b, w, ndraw=20000, seed=1):
    k = kpart(f)
    lam = m / T
    P2, P3 = capture(w, sigma)
    lw = lam * w
    f2 = lw * (k * (k - 1) * P2 - lw * k * k)
    f3 = lw * (k * (k - 1) * (k - 2) * P3 - 3 * lw * k * k * (k - 1) * P2 + 2 * lw * lw * k ** 3)
    n = T / w
    mu = N * b * w + lw * k
    ev = event_mc(w, sigma, k)
    v2 = 0.75 * 2 * mu ** 2 * n + m * (ev["S2"].var() + 4 * mu * ev["Q1"].mean())
    v3 = 0.625 * 6 * mu ** 3 * n + m * (ev["S3"].var() + 18 * mu ** 2 * ev["Q1"].mean()
                                       + 9 * mu * ev["Q2"].mean())
    c23 = m * (np.cov(ev["S2"], ev["S3"])[0, 1] + 6 * mu * ev["Q12"].mean())
    cov = np.array([[v2, c23], [c23, v3]]) / n ** 2 * 1.05          # x1.05: 20 surrogates
    rs = np.random.RandomState(seed)
    d = rs.multivariate_normal([f2, f3], cov, size=ndraw)
    sol = [solve(a, c, N, w, "fixed") for a, c in d]
    kk = np.array([s["k"] for s in sol]) / k
    ll = np.array([s["lam"] for s in sol]) / lam
    sh = np.array([s["share"] for s in sol]) / (lam * k / N)
    noiseless = solve(f2, f3, N, w, "fixed")
    return dict(k=k, P2=P2, P3=P3, f2=f2, f3=f3, sd2=np.sqrt(cov[0, 0]), sd3=np.sqrt(cov[1, 1]),
                k0=noiseless["k"] / k, lam0=noiseless["lam"] / lam,
                share0=noiseless["share"] / (lam * k / N),
                kmed=np.nanmedian(kk), lmed=np.nanmedian(ll), smed=np.nanmedian(sh),
                kiqr=np.subtract(*np.nanpercentile(kk, [75, 25])),
                nanfrac=float(np.isnan(kk).mean()))


def main():
    rows = load()
    out = []
    for sg, f, m, b, w in itertools.product(JITS, PARTS, NEVS, BGS, WS):
        rr = [r for r in rows if (r["true"]["jitter"], r["true"]["part_frac"], r["true"]["n_events"],
                                  r["true"]["bg_rate"]) == (sg, f, m, b)]
        t = rr[0]["true"]
        obs = [r["coord_rates"][str(w)] for r in rr]
        ok = [o for o in obs if np.isfinite(o["k"])]
        ko = np.array([o["k"] for o in ok]) / t["k"]
        lo = np.array([o["lam"] for o in ok]) / t["lam"]
        so = np.array([o["share"] for o in ok]) / t["share"]
        p = predict(sg, f, m, b, w)
        out.append(dict(sg=sg, f=f, m=m, b=b, w=w, nobs=len(ok), ko=ko, lo=lo, so=so, **p))
    np.save(__import__("pathlib").Path(__file__).with_suffix(".npy"), out, allow_pickle=True)

    # ---- table 1: noiseless prediction vs observed median, averaged the way Figure 1 pools
    print("Noiseless mean-field prediction (pooled as Figure 1: median over part, m, seeds)")
    print(" b     w   sigma | k: pred  pred(noisy) obs | lam: pred noisy obs | share: pred noisy obs")
    for b, w, sg in itertools.product(BGS, WS, JITS):
        sel = [o for o in out if (o["b"], o["w"], o["sg"]) == (b, w, sg)]
        ko = np.concatenate([o["ko"] for o in sel]); lo = np.concatenate([o["lo"] for o in sel])
        so = np.concatenate([o["so"] for o in sel])
        f = lambda key: np.median([o[key] for o in sel])  # noqa: E731
        print(f"{b:.2f} {w:3.0f} {sg:5.2f} | {f('k0'):5.2f} {f('kmed'):5.2f} {np.median(ko):5.2f} |"
              f" {f('lam0'):5.2f} {f('lmed'):5.2f} {np.median(lo):5.2f} |"
              f" {f('share0'):5.2f} {f('smed'):5.2f} {np.median(so):5.2f}")


if __name__ == "__main__":
    main()
