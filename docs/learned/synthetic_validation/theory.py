"""Aim 0: what the measuring tools should return, predicted from the planted parameters.

Goal page: docs/goals/synthetic-validation.md, "Aim 0". Synthetic only.

The generator is a superposition: independent background onsets per cell, plus coordinated
events, each joined by k cells whose onsets carry independent Gaussian jitter (SD sigma).

1. Window sharing. The chance that n onsets of one event fall in the same window of width w,
   with the window's phase uniform, is

       g_n(w, sigma) = E[max(0, 1 - R_n / w)] = (1/w) * integral_0^w F_R(r) dr,

   where R_n is the range of n independent N(0, sigma^2) onsets and
   F_R(r) = n * integral phi(x) [Phi(x + r) - Phi(x)]^(n-1) dx (onsets in units of sigma).

2. The coordination-rates tool (tools/measure_coordination_rates.py). Its factorial cumulants
   of the population count are additive over independent processes, and the shift surrogates
   remove the background's, so per window

       f2 = lambda * w * k(k-1) * g_2,     f3 = lambda * w * k(k-1)(k-2) * g_3.

   Its "fixed" solve assumes g_2 = g_3 = 1. So it returns

       k_hat     = (k - 2) * g_3/g_2 + 2
       lam_hat   = lambda * k(k-1) g_2 / (k_hat (k_hat - 1))
       share_hat = share * (k - 1) g_2 / (k_hat - 1)

3. Jitter from the window dependence. f2(w)/w = lambda k(k-1) g_2(w, sigma): only g_2 depends
   on w, so fitting f2(w)/w across the tool's windows (1, 2, 4 s) to A * g_2(w, sigma) gives
   sigma with no event definition and no K.

4. Chance clusters at K (bugarach.assess). In 1 s bins with N cells at background rate b,
   a bin reaches K with q = P(Binomial(N, 1 - exp(-b)) >= K); runs closer than 3 bins merge,
   so chance clusters start at about (60 / bin) * q (1 - q)^2 per minute.

Assumptions: events do not overlap within a window (min_sep 20 s here); background is
Poisson with equal rates (bg_rate_shape and bursts off, as in Aim 1a); frames (0.1 s) and the
tool's two window offsets are treated as a uniform phase.

    PYTHONPATH=src python docs/learned/synthetic_validation/theory.py   # checks Aim 1a
"""

from __future__ import annotations

import functools
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import integrate, optimize, stats

HERE = Path(__file__).resolve().parent


@functools.lru_cache(maxsize=None)
def _range_cdf(n: int, r: float) -> float:
    """P(range of n iid standard normals <= r)."""
    if r <= 0:
        return 0.0
    f = lambda x: stats.norm.pdf(x) * (stats.norm.cdf(x + r) - stats.norm.cdf(x)) ** (n - 1)
    return float(n * integrate.quad(f, -9, 9, limit=200)[0])


def g2_closed(w: float, sigma: float) -> float:
    """g_2 in closed form: the two onsets differ by D ~ N(0, 2 sigma^2), and
    E[(1 - |D|/w)+] = P(|D| < w) - E[|D|; |D| < w] / w, with a = w / (sigma sqrt 2)."""
    if sigma <= 0:
        return 1.0
    s = sigma * np.sqrt(2.0)
    a = w / s
    return float((2 * stats.norm.cdf(a) - 1) - 2 * s / w * (stats.norm.pdf(0) - stats.norm.pdf(a)))


@functools.lru_cache(maxsize=None)
def g(n: int, w: float, sigma: float) -> float:
    """Chance that n onsets of one event share a window of width w (uniform phase)."""
    if sigma <= 0:
        return 1.0
    if n == 2:
        return g2_closed(w, sigma)
    u = w / sigma                       # the window in units of sigma
    val = integrate.quad(lambda r: _range_cdf(n, r), 0, u, limit=200)[0]
    return float(val / u)


def coord_rates_prediction(k: float, sigma: float, w: float) -> dict:
    """What the coordination-rates tool's fixed solve returns, as ratios to the truth."""
    g2, g3 = g(2, w, sigma), g(3, w, sigma)
    kh = (k - 2) * g3 / g2 + 2
    return dict(g2=g2, g3=g3, k=kh / k, lam=k * (k - 1) * g2 / (kh * (kh - 1)),
                share=(k - 1) * g2 / (kh - 1))


def coord_rates_exact(k: int, sigma: float, w: float, lam: float, n_cells: int) -> dict:
    """As `coord_rates_prediction`, plus the term the Poisson picture leaves out.

    Events here are at least min_sep apart, so a window holds at most one. Then the
    coordinated count's factorial moments are exactly m_r = lam w (k)_r g_r, and its factorial
    cumulants carry products of lower moments that a Poisson event train would cancel. The
    shift surrogate keeps each cell's own train (rate lam k / N, at most one onset per window)
    and so removes only its within-cell share. The excess the tool measures is

        f2 = p (k)_2 g_2 - (p k)^2 (1 - 1/N)
        f3 = p (k)_3 g_3 - 3 p^2 k (k)_2 g_2 + 2 (p k)^3 (1 - 1/N^2),     p = lam w.
    """
    g2, g3 = g(2, w, sigma), g(3, w, sigma)
    p = lam * w
    f2 = p * k * (k - 1) * g2 - (p * k) ** 2 * (1 - 1 / n_cells)
    f3 = (p * k * (k - 1) * (k - 2) * g3 - 3 * p ** 2 * k * k * (k - 1) * g2
          + 2 * (p * k) ** 3 * (1 - 1 / n_cells ** 2))
    kh = f3 / f2 + 2
    lh = f2 / (w * kh * (kh - 1))
    return dict(k=kh / k, lam=lh / lam, share=(lh * kh) / (lam * k))


def jitter_from_windows(f2_by_w: dict) -> float:
    """sigma (s) that best fits f2(w)/w = A * g_2(w, sigma) across windows; nan if unusable."""
    ws = np.array(sorted(f2_by_w))
    y = np.array([f2_by_w[w] / w for w in ws])
    if not np.all(np.isfinite(y)) or np.any(y <= 0):
        return float("nan")

    def loss(ls):
        s = float(np.exp(ls))
        gg = np.array([g2_closed(float(w), s) for w in ws])
        a = (gg @ y) / (gg @ gg)        # least-squares amplitude
        return float(np.sum((np.log(y) - np.log(a * gg)) ** 2))

    grid = np.log(np.geomspace(0.01, 5, 40))
    ls0 = grid[int(np.argmin([loss(v) for v in grid]))]
    res = optimize.minimize_scalar(loss, bounds=(ls0 - 0.3, ls0 + 0.3), method="bounded")
    return float(np.exp(res.x))


def chance_clusters_per_min(n_cells: int, bg_hz: float, K: int, bin_sec: float = 1.0,
                            merge_bins: int = 2) -> float:
    """Clusters per minute that background alone produces at threshold K."""
    p = 1 - np.exp(-bg_hz * bin_sec)
    q = float(stats.binom.sf(K - 1, n_cells, p))
    return 60.0 / bin_sec * q * (1 - q) ** merge_bins


def f2_of(est: dict, w: float) -> float:
    """Recover the tool's f2 from its fixed-model (k, lam): lam = f2 / (w k (k-1))."""
    k, lam = est["k"], est["lam"]
    return lam * w * k * (k - 1) if np.isfinite(k) and np.isfinite(lam) else float("nan")


def check(path=HERE / "aim1_one_source.json") -> dict:
    """Every prediction against the Aim 1a run record. Prints tables, returns the record."""
    rec = json.loads(Path(path).read_text())
    rows, N = rec["rows"], rec["n_roi"]
    out = dict(what="Aim 0 predictions against Aim 1a", coord_rates=[], jitter=[], chance=[])

    cells = defaultdict(list)
    for r in rows:
        t = r["true"]
        cells[(t["bg_rate"], t["jitter"], round(t["k"]), t["n_events"])].append(r)
    print("coordination rates: recovered / planted; Poisson picture, exact, measured median")
    print(" bg    sigma  k ev  w |   k: pois exact meas | rate: pois exact meas |"
          " share: pois exact meas")
    for (bg, s, k, ne), rs in sorted(cells.items()):
        lam = ne / rec["duration_sec"]
        for w in ("1.0", "2.0", "4.0"):
            p = coord_rates_prediction(k, s, float(w))
            e = coord_rates_exact(k, s, float(w), lam, N)
            m = {q: float(np.nanmedian([x["coord_rates"][w][q] / x["true"][q] for x in rs]))
                 for q in ("k", "lam", "share")}
            out["coord_rates"].append(dict(bg=bg, sigma=s, k=k, n_events=ne, w=float(w),
                                           poisson=p, exact=e, meas=m))
            print(f"{bg:4.2f} {s:5.2f} {k:3d} {ne:2d} {w:>3} |"
                  + "|".join(f" {p[q]:5.2f} {e[q]:5.2f} {m[q]:5.2f} " for q in ("k", "lam", "share")))

    print("\njitter from the window dependence of f2 (median over recordings)")
    by = defaultdict(list)
    for r in rows:
        t = r["true"]
        f2 = {float(w): f2_of(r["coord_rates"][w], float(w)) for w in ("1.0", "2.0", "4.0")}
        est = jitter_from_windows(f2)
        r["theory_jitter"] = est
        by[(t["bg_rate"], t["jitter"])].append(est)
    for (bg, s), v in sorted(by.items()):
        v = np.array(v, float)
        out["jitter"].append(dict(bg=bg, sigma=s, median=float(np.nanmedian(v)),
                                  q25=float(np.nanpercentile(v, 25)),
                                  q75=float(np.nanpercentile(v, 75)),
                                  n_usable=int(np.isfinite(v).sum()), n=int(v.size)))
        print(f" bg {bg:4.2f} planted {s:4.2f} s -> {np.nanmedian(v):5.2f} s"
              f"  (IQR {np.nanpercentile(v, 25):.2f}-{np.nanpercentile(v, 75):.2f};"
              f" {np.isfinite(v).sum()}/{v.size} usable)")

    print("\nassessment clusters per min at K: chance (predicted) + planted vs measured median")
    by = defaultdict(list)
    for r in rows:
        t = r["true"]
        for K in rec["ks"]:
            by[(t["bg_rate"], K, t["n_events"])].append(r["assess"][str(K)]["per_min"])
    for (bg, K, ne), v in sorted(by.items()):
        planted = 60.0 * ne / rec["duration_sec"]
        ch = chance_clusters_per_min(N, bg, K)
        out["chance"].append(dict(bg=bg, K=K, n_events=ne, chance=ch, planted=planted,
                                  meas=float(np.nanmedian(v))))
        print(f" bg {bg:4.2f} K {K} events {ne:2d}: chance {ch:6.2f} + planted {planted:4.2f}"
              f" = {ch + planted:6.2f}  measured {np.nanmedian(v):6.2f}")
    (HERE / "theory_check.json").write_text(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    check()
