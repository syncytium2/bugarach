"""A jitter estimate the theory suggests, tested blind on aim1_one_source.json (no new simulation).

f2(w)/w = lam k(k-1) P2(sigma, w) - lam^2 k^2 w (hard-core term), so the pair excess per second at two
windows fixes sigma through P2(sigma, w1)/P2(sigma, w2) alone (lam and k cancel):
    rho = [f2(w1)/w1 + c w1] / [f2(w2)/w2 + c w2],  c = (lam k)^2 estimated from the 4 s solve,
    sigma_hat solves P2(sigma, w1)/P2(sigma, w2) = rho;  P2 = E[(1 - |d|/w)+], d = difference of two
    quantised N(0, sigma^2) onsets (closed form below, with 0.1 s quantisation as extra variance 0.1^2/6).
f2 is recovered from the record: f2 = lam w k(k-1) (solve's fixed model, exact inverse).
"""
import json
from pathlib import Path

import numpy as np
from scipy import optimize, stats

HERE = Path(__file__).resolve().parent
REC = HERE.parent / "docs/learned/synthetic_validation/aim1_one_source.json"


def P2(sigma, w):
    s = np.sqrt(2 * sigma**2 + 0.1**2 / 6)        # SD of the onset difference, quantisation included
    a = w / s
    return (2 * stats.norm.cdf(a) - 1) - (2 / a) * (1 - np.exp(-a * a / 2)) / np.sqrt(2 * np.pi)


def inv(rho, w1, w2):
    f = lambda ls: P2(np.exp(ls), w1) / P2(np.exp(ls), w2) - rho
    lo, hi = np.log(0.005), np.log(20)
    if f(lo) * f(hi) > 0:
        return np.nan if rho > 1 else np.inf
    return float(np.exp(optimize.brentq(f, lo, hi)))


def main():
    rec = json.loads(REC.read_text())
    res = {}
    for r in rec["rows"]:
        t = r["true"]
        cr = r["coord_rates"]
        f2 = {}
        ok = True
        for w in ("1.0", "2.0", "4.0"):
            k, lam = cr[w]["k"], cr[w]["lam"]
            if not (np.isfinite(k) and np.isfinite(lam)):
                ok = False
                break
            f2[float(w)] = lam * float(w) * k * (k - 1)
        if not ok:
            est = {p: np.nan for p in ("12", "14", "24")}
        else:
            c = (cr["4.0"]["lam"] * cr["4.0"]["k"]) ** 2
            est = {}
            for nm, (w1, w2) in {"12": (1.0, 2.0), "14": (1.0, 4.0), "24": (2.0, 4.0)}.items():
                rho = (f2[w1] / w1 + c * w1) / (f2[w2] / w2 + c * w2)
                est[nm] = inv(rho, w1, w2)
        res.setdefault((t["jitter"], t["bg_rate"]), []).append((est, t["k"], t["n_events"]))
    print("Jitter from the window ratio of the pair excess (blind), sigma_hat / sigma: median [IQR] over 60 recordings per cell")
    print("(assess jit_obs / sigma beside it, for comparison)")
    for (sig, b), v in sorted(res.items()):
        line = f"sigma={sig:4.2f} b={b:4.2f}: "
        for nm in ("12", "14"):
            x = np.array([e[nm] for e, _, _ in v], float) / sig
            fin = np.isfinite(x)
            q = np.nanpercentile(np.where(fin, x, np.nan), [25, 50, 75])
            line += f"w{nm[0]}/{nm[1]}: {q[1]:.2f} [{q[0]:.2f},{q[2]:.2f}] (undef {int((~fin).sum())})  "
        aj = [r["assess"]["4"]["jit"] / sig for r in rec["rows"] if r["true"]["jitter"] == sig and r["true"]["bg_rate"] == b]
        line += f"| assess K=4: {np.nanmedian(aj):.2f}"
        print(line)
    # by k at b = 0.05, w 1/4
    print("\nw1/4 estimator by participants k (both backgrounds pooled): median sigma_hat/sigma")
    for k in (5, 10, 20):
        row = []
        for sig in (0.05, 0.2, 0.5, 1.0):
            x = [e["14"] / sig for b in (0.01, 0.05) for e, kk, _ in res[(sig, b)] if kk == k]
            row.append(f"sigma {sig}: {np.nanmedian(x):.2f}")
        print(f"  k={k}: " + "; ".join(row))


if __name__ == "__main__":
    main()
