"""Inverted coordination-rates estimator: fit (sigma, k, lambda) to excess (f2, f3) at several windows
using the analytic window-capture model, instead of solve()'s per-window 'every pair shares a window'.

    f2(w) = lam w [k(k-1) P2(w,s) - lam w k^2]
    f3(w) = lam w [k(k-1)(k-2) P3(w,s) - 3 lam w k^2 (k-1) P2(w,s) + 2 (lam w)^2 k^3]

Residuals weighted by the Charlier-polynomial background SE (Var f2 = 1.5 mu^2/n, Var f3 = 3.75 mu^3/n,
mu = N rbar w, n = T/w; rbar = observed mean rate per cell) plus a 5 % model floor.
Run on (a) fresh_cr.json (independent backgrounds, windows 0.5-8 s or 1,2,4 s), (b) the Aim 1a record.
"""
from __future__ import annotations

import itertools
import json

import numpy as np
from scipy.optimize import least_squares

from theory_common import HERE, N, T, capture, load

SG = np.exp(np.linspace(np.log(0.01), np.log(4.0), 45))
_TAB: dict = {}


def tab(w):
    if w not in _TAB:
        _TAB[w] = np.array([capture(w, s) for s in SG])
    return _TAB[w]


def P(w, s):
    t = tab(w); ls = np.log(np.clip(s, SG[0], SG[-1]))
    return np.interp(ls, np.log(SG), t[:, 0]), np.interp(ls, np.log(SG), t[:, 1])


def model(theta, ws):
    s, k, lam = np.exp(theta[0]), 2 + np.exp(theta[1]), np.exp(theta[2])
    out = []
    for w in ws:
        p2, p3 = P(w, s); lw = lam * w
        out += [lw * (k * (k - 1) * p2 - lw * k * k),
                lw * (k * (k - 1) * (k - 2) * p3 - 3 * lw * k * k * (k - 1) * p2 + 2 * lw * lw * k ** 3)]
    return np.array(out)


def fit(f, ws, rbar):
    y = np.array([v for w in ws for v in f[w]])
    se = []
    for w in ws:
        mu, n = N * rbar * w, T / w
        se += [np.sqrt(1.5 * mu ** 2 / n), np.sqrt(3.75 * mu ** 3 / n)]
    se = np.sqrt(np.array(se) ** 2 + (0.05 * np.abs(y)) ** 2)
    best = None
    for s0, k0 in itertools.product((0.05, 0.3, 1.0), (5.0, 15.0)):
        f2 = max(f[ws[0]][0], 1e-3)
        th0 = [np.log(s0), np.log(k0 - 2), np.log(f2 / (ws[0] * k0 * (k0 - 1)))]
        r = least_squares(lambda th: (model(th, ws) - y) / se, th0,
                          bounds=([np.log(0.01), np.log(0.05), -15], [np.log(4.0), np.log(60), 0]))
        if best is None or r.cost < best.cost:
            best = r
    th = best.x
    return np.exp(th[0]), 2 + np.exp(th[1]), np.exp(th[2])


def summarize(recs, label):
    print(f"\n{label}: median recovered/planted (IQR) by background and jitter, pooled over part, m, seeds")
    print(" b     sigma |  sigma_hat/sigma      |  k_hat/k              |  rate_hat/rate         | naive k(1s)  naive rate(1s)")
    for b, sg in itertools.product((0.01, 0.05), (0.05, 0.2, 0.5, 1.0)):
        R = np.array([r["fit"] for r in recs if r["bg"] == b and r["jit"] == sg])
        nv = np.array([r["naive"] for r in recs if r["bg"] == b and r["jit"] == sg])
        q = lambda x: f"{np.nanmedian(x):5.2f} ({np.nanpercentile(x,25):4.2f}-{np.nanpercentile(x,75):4.2f})"  # noqa: E731
        print(f"{b:.2f} {sg:5.2f} | {q(R[:,0])} | {q(R[:,1])} | {q(R[:,2])} | {np.nanmedian(nv[:,0]):5.2f} {np.nanmedian(nv[:,1]):5.2f}")


def naive(f2, f3, k, lam, w=1.0):
    if not (f2 > 0 and f3 > 0):
        return (np.nan, np.nan)
    kk = f3 / f2 + 2
    return kk / k, f2 / (w * kk * (kk - 1)) / lam


def main():
    import sys
    fresh = json.loads((HERE / "fresh_cr.json").read_text())
    for ws, lab in (((1.0, 2.0, 4.0), "fresh runs, windows 1,2,4 s (the tool's own)"),
                    ((0.5, 1.0, 2.0, 4.0, 8.0), "fresh runs, windows 0.5-8 s")):
        recs = []
        for r in fresh:
            f = {w: tuple(r["cum"][str(w)]) for w in ws}
            rbar = 0.0 + r["bg"] + r["m"] * r["k"] / (N * T)
            s, k, lam = fit(f, ws, rbar)
            lam0 = r["m"] / T
            recs.append(dict(bg=r["bg"], jit=r["jit"], fit=(s / r["jit"], k / r["k"], lam / lam0),
                             naive=naive(*r["cum"]["1.0"], r["k"], lam0)))
        summarize(recs, lab)
    # the Aim 1a record: reconstruct f2, f3 from the stored fixed-model (k, lam)
    recs = []
    for r in load():
        f = {}
        for w in (1.0, 2.0, 4.0):
            c = r["coord_rates"][str(w)]
            if not np.isfinite(c["k"]):
                f = None; break
            f2 = c["lam"] * w * c["k"] * (c["k"] - 1); f[w] = (f2, (c["k"] - 2) * f2)
        t = r["true"]
        if f is None:
            recs.append(dict(bg=t["bg_rate"], jit=t["jitter"], fit=(np.nan,) * 3, naive=(np.nan,) * 2)); continue
        s, k, lam = fit(f, (1.0, 2.0, 4.0), t["n_onsets"] / (N * T))
        recs.append(dict(bg=t["bg_rate"], jit=t["jitter"], fit=(s / t["jitter"], k / t["k"], lam / t["lam"]),
                         naive=naive(*f[1.0], t["k"], t["lam"])))
    summarize(recs, "Aim 1a record (shared backgrounds), windows 1,2,4 s")


if __name__ == "__main__":
    main()
