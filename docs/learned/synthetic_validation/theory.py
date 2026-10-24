"""Aim 0: what the measuring tools should return, predicted from the planted parameters.

Goal page: docs/goals/synthetic-validation.md, "Aim 0". Synthetic only. Revised after the
murderboard of 2026-10-23 (docs/reviews/synthetic-validation-aim0_2026-10-23.md).

The generator is a Neyman-Scott cluster process: independent Poisson background onsets per cell,
plus coordinated events at least `min_sep` apart, each joined by k cells whose onsets carry
independent Gaussian jitter (SD sigma) and are then rounded to the 0.1 s frame. Symbols:
N cells, k participants per event (cells), sigma jitter SD (s), w window (s), lambda event rate
(per s), b background rate (Hz per cell), K the assessor's threshold (cells, an absolute count).

1. Window sharing. The chance that n onsets of one event fall in one window of width w, with the
   window's phase uniform, is g_n(w, s) = E[max(0, 1 - R_n / w)], R_n the range of n onsets.
   Rounding to a frame of dt adds a uniform error of variance dt^2/12 per onset, so s is taken
   as sqrt(sigma^2 + dt^2/12). g_2 has a closed form (two onsets differ by N(0, 2 s^2)); g_3 is
   a one-dimensional integral. This is the Gaussian, continuous form of the bin-border loss in
   Grun et al. 1999 (J Neurosci Methods 94:67), whose uniform-jitter "fission probability" is
   the same quantity.

2. The coordination-rates tool (tools/measure_coordination_rates.py). Its route is CuBIC's
   (Staude, Rotter & Grun, J Comput Neurosci 29:327) and Ehm, Staude & Rotter 2007: factorial
   cumulants of the population count, which add over independent processes. With at most one
   event per window, the coordinated count's factorial moments are m_r = p (k)_r g_r with
   p = lambda w, and the shift surrogate keeps each cell's own train (rate lambda k / N), so the
   excess the tool measures is

       f2 = p (k)_2 g_2 - (p k)^2 (1 - 1/N)
       f3 = p (k)_3 g_3 - 3 p^2 k (k)_2 g_2 + 2 (p k)^3 (1 - 1/N^2).

   The predictions are passed through the tool's own `solve()`, so a prediction and a
   measurement are the same estimator (including its refusal when f2 or f3 <= 0). Omitted: the
   surrogate's offsets (multiples of 2w, spanning minutes) are not independent of the renewal
   event train; that term is about 1 % of f2 here (murderboard role 6).

3. Jitter, participants and rate, fitted together across the tool's windows (1, 2, 4 s): the
   six excess cumulants against the exact forms above, for (sigma, k, lambda). This replaces a
   one-parameter fit of f2(w)/w that ignored the at-most-one-event term (blind pass A's route;
   see blind_README.md).

4. Chance clusters at K (bugarach.assess). In 1 s bins, a bin reaches K cells with
   q = P(Binomial(N, 1 - exp(-b)) >= K); a cluster starts on a bin at or over K whose two
   preceding bins are below it (merge_bins = 2), about (60 / bin) q (1 - q)^2 per minute.
   Tested on background-only recordings. Planted events are not predicted: whether an event
   reaches K depends on k, sigma and the bin, and no detection term is modelled here.

    PYTHONPATH=src python docs/learned/synthetic_validation/theory.py   # checks Aim 1a
"""

from __future__ import annotations

import functools
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import integrate, optimize, stats

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import measure_coordination_rates as mcr  # noqa: E402

DT = mcr.DT
WINDOWS = tuple(float(w) for w in mcr.WINDOWS)
SIGMA_BOUNDS = (0.005, 5.0)       # s; the joint fit's search range, reported when it binds


def s_eff(sigma: float, dt: float = DT) -> float:
    """Jitter SD after rounding each onset to the frame."""
    return float(np.sqrt(sigma ** 2 + dt ** 2 / 12.0))


@functools.lru_cache(maxsize=None)
def _range_cdf(n: int, r: float) -> float:
    """P(range of n iid standard normals <= r)."""
    if r <= 0:
        return 0.0
    f = lambda x: stats.norm.pdf(x) * (stats.norm.cdf(x + r) - stats.norm.cdf(x)) ** (n - 1)
    return float(n * integrate.quad(f, -9, 9, limit=200)[0])


def g2_closed(w: float, s: float) -> float:
    """g_2 for onsets of SD s: P(|D| < w) - E[|D|; |D| < w] / w, D ~ N(0, 2 s^2)."""
    if s <= 0:
        return 1.0
    sd = s * np.sqrt(2.0)
    a = w / sd
    return float((2 * stats.norm.cdf(a) - 1) - 2 * sd / w * (stats.norm.pdf(0) - stats.norm.pdf(a)))


@functools.lru_cache(maxsize=None)
def _g3_table():
    """g_3 depends only on u = w / s: tabulate it once on a log grid and interpolate."""
    us = np.geomspace(1e-3, 1e4, 500)
    cdf = np.array([_range_cdf(3, r) for r in np.geomspace(1e-4, 40, 2000)])
    rr = np.geomspace(1e-4, 40, 2000)
    # integral_0^u F(r) dr, with F ~ 0 below 1e-4 and F = 1 above 40
    cum = np.concatenate([[0.0], np.cumsum(0.5 * (cdf[1:] + cdf[:-1]) * np.diff(rr))])
    vals = []
    for u in us:
        if u <= rr[-1]:
            vals.append(np.interp(u, rr, cum) / u)
        else:
            vals.append((cum[-1] + (u - rr[-1])) / u)
    return np.log(us), np.array(vals)


def _g3(w: float, s: float) -> float:
    lu, v = _g3_table()
    return float(np.interp(np.log(w / s), lu, v))


def g(n: int, w: float, sigma: float) -> float:
    """Chance that n onsets of one event share a window of width w (frame rounding included)."""
    s = s_eff(sigma)
    if n == 2:
        return g2_closed(w, s)
    if n == 3:
        return _g3(float(w), s)
    raise ValueError(n)


def excess_cumulants(k: float, sigma: float, w: float, lam: float, n_cells: int):
    """The (f2, f3) the tool's surrogate-corrected cumulants should equal, exactly as derived."""
    p = lam * w
    g2, g3 = g(2, w, sigma), g(3, w, sigma)
    f2 = p * k * (k - 1) * g2 - (p * k) ** 2 * (1 - 1 / n_cells)
    f3 = (p * k * (k - 1) * (k - 2) * g3 - 3 * p ** 2 * k * k * (k - 1) * g2
          + 2 * (p * k) ** 3 * (1 - 1 / n_cells ** 2))
    return f2, f3


def poisson_cumulants(k, sigma, w, lam):
    """The same without the at-most-one-event terms (a Poisson event train): kept to show why
    those terms are needed."""
    p = lam * w
    return p * k * (k - 1) * g(2, w, sigma), p * k * (k - 1) * (k - 2) * g(3, w, sigma)


def predict_solve(k, sigma, w, lam, n_cells, poisson=False):
    """What the tool's fixed-model solve() returns, as ratios to the planted values."""
    f2, f3 = (poisson_cumulants(k, sigma, w, lam) if poisson
              else excess_cumulants(k, sigma, w, lam, n_cells))
    s = mcr.solve(f2, f3, n_cells, w, "fixed")
    return dict(k=s["k"] / k, lam=s["lam"] / lam, share=s["share"] / (lam * k / n_cells))


def fit_joint(cum: dict, n_cells: int):
    """Fit (sigma, k, lambda) to the six excess cumulants across windows.

    cum: {window_sec: {"f2": .., "f3": ..}}. Residuals are scaled by each order's mean absolute
    value so f2 and f3 weigh alike. Returns a dict with the estimates and whether sigma hit a
    bound, or None when the cumulants carry no usable signal (f2 <= 0 at every window)."""
    ws = np.array(sorted(float(w) for w in cum))
    f2 = np.array([cum[str(w)]["f2"] if str(w) in cum else cum[w]["f2"] for w in ws])
    f3 = np.array([cum[str(w)]["f3"] if str(w) in cum else cum[w]["f3"] for w in ws])
    if not np.any(f2 > 0):
        return None
    s2 = max(np.mean(np.abs(f2)), 1e-12)
    s3 = max(np.mean(np.abs(f3)), 1e-12)

    def resid(x):
        sig, k, lam = np.exp(x[0]), 2 + np.exp(x[1]), np.exp(x[2])
        pr = np.array([excess_cumulants(k, sig, w, lam, n_cells) for w in ws])
        return np.concatenate([(pr[:, 0] - f2) / s2, (pr[:, 1] - f3) / s3])

    best = None
    lo = [np.log(SIGMA_BOUNDS[0]), np.log(1e-3), np.log(1e-6)]
    hi = [np.log(SIGMA_BOUNDS[1]), np.log(n_cells - 2), np.log(1.0)]
    for sig0 in (0.05, 0.2, 0.6, 1.5):
        for k0 in (4.0, 12.0):
            w0 = ws[-1]
            lam0 = max(f2[-1], 1e-6) / (w0 * k0 * (k0 - 1))
            x0 = [np.log(sig0), np.log(k0 - 2), np.log(min(max(lam0, 1e-5), 0.5))]
            try:
                r = optimize.least_squares(resid, x0, bounds=(lo, hi))
            except ValueError:
                continue
            if best is None or r.cost < best.cost:
                best = r
    if best is None:
        return None
    sig = float(np.exp(best.x[0]))
    return dict(sigma=sig, k=float(2 + np.exp(best.x[1])), lam=float(np.exp(best.x[2])),
                at_bound=bool(sig <= SIGMA_BOUNDS[0] * 1.02 or sig >= SIGMA_BOUNDS[1] / 1.02))


def chance_clusters_per_min(n_cells: int, bg_hz: float, K: int, bin_sec: float = 1.0,
                            merge_bins: int = 2) -> float:
    """Clusters per minute that background alone produces at threshold K (cells)."""
    p = 1 - np.exp(-bg_hz * bin_sec)
    q = float(stats.binom.sf(K - 1, n_cells, p))
    return 60.0 / bin_sec * q * (1 - q) ** merge_bins


def _q(v, qs=(25, 50, 75)):
    v = np.asarray([x for x in v if x is not None and np.isfinite(x)], float)
    return [float(np.percentile(v, q)) for q in qs] if v.size else [float("nan")] * len(qs)


def check(path=HERE / "aim1_one_source.json") -> dict:
    """Every prediction against the Aim 1a run record, per condition. Writes theory_check.json."""
    rec = json.loads(Path(path).read_text())
    rows, N, T = rec["rows"], rec["n_roi"], rec["duration_sec"]
    out = dict(what="Aim 0 predictions against Aim 1a, per condition (k, sigma, events, bg, w); "
                    "each measured value is a median over the condition's 5 recordings, "
                    "NaN estimates (solve refused) excluded and counted",
               coord_rates=[], joint_fit=[], chance=[])

    cond = defaultdict(list)
    for r in rows:
        t = r["true"]
        cond[(t["bg_rate"], t["jitter"], int(round(t["k"])), t["n_events"])].append(r)

    for (bg, s, k, ne), rs in sorted(cond.items()):
        lam = ne / T
        for w in ("1.0", "2.0", "4.0"):
            e = predict_solve(k, s, float(w), lam, N)
            p = predict_solve(k, s, float(w), lam, N, poisson=True)
            vals = {q: [x["coord_rates"][w][q] / x["true"][q] for x in rs] for q in ("k", "lam", "share")}
            m = {q: float(np.nanmedian(v)) if np.any(np.isfinite(v)) else float("nan")
                 for q, v in vals.items()}
            sd = {q: float(np.nanstd(v)) for q, v in vals.items()}
            out["coord_rates"].append(dict(bg=bg, sigma=s, k=k, n_events=ne, w=float(w),
                                           exact=e, poisson=p, meas=m, meas_sd=sd,
                                           n_nan=int(np.sum(~np.isfinite(vals["k"]))), n=len(rs)))
        fits = [fit_joint(x["cum"], N) for x in rs]
        ok = [f for f in fits if f is not None]
        out["joint_fit"].append(dict(
            bg=bg, sigma=s, k=k, n_events=ne, n=len(rs), n_usable=len(ok),
            n_at_bound=int(sum(f["at_bound"] for f in ok)),
            sigma_q=_q([f["sigma"] for f in ok]),
            k_ratio_q=_q([f["k"] / k for f in ok]),
            lam_ratio_q=_q([f["lam"] / lam for f in ok])))

    by = defaultdict(list)
    for c in rec.get("chance_arm", []):
        for K, v in c["per_min"].items():
            by[(c["bg_rate"], int(K))].append(v)
    for (bg, K), v in sorted(by.items()):
        out["chance"].append(dict(bg=bg, K=K, predicted=chance_clusters_per_min(N, bg, K),
                                  measured_median=float(np.median(v)),
                                  measured_q=_q(v), n=len(v)))
    (HERE / "theory_check.json").write_text(json.dumps(out, indent=1))
    return out


def summary(out: dict) -> None:
    """The numbers the goal page quotes, recomputed from a check() record."""
    cr = out["coord_rates"]
    for bg in (0.01, 0.05):
        for kmin in (5, 10):
            for q in ("k", "lam", "share"):
                d = [abs(r["meas"][q] - r["exact"][q]) for r in cr
                     if r["bg"] == bg and r["k"] >= kmin and np.isfinite(r["meas"][q])]
                dp = [abs(r["meas"][q] - r["poisson"][q]) for r in cr
                      if r["bg"] == bg and r["k"] >= kmin and np.isfinite(r["meas"][q])]
                print(f"bg {bg} k>={kmin:2d} {q:5s}: |meas - exact| median {np.median(d):.3f} "
                      f"worst {np.max(d):.3f} (n={len(d)}); Poisson median {np.median(dp):.3f}")
    nan = sum(r["n_nan"] for r in cr)
    print(f"solve() refused (NaN) in {nan} of {sum(r['n'] for r in cr)} recording-windows")
    print("\njoint fit: sigma median [IQR] by background and planted sigma, k >= 10 vs k = 5")
    for bg in (0.01, 0.05):
        for s in (0.05, 0.2, 0.5, 1.0):
            for lab, sel in (("k>=10", lambda r: r["k"] >= 10), ("k=5", lambda r: r["k"] == 5)):
                rs = [r for r in out["joint_fit"] if r["bg"] == bg and r["sigma"] == s and sel(r)]
                med = np.median([r["sigma_q"][1] for r in rs])
                us = sum(r["n_usable"] for r in rs); n = sum(r["n"] for r in rs)
                ab = sum(r["n_at_bound"] for r in rs)
                kr = np.median([r["k_ratio_q"][1] for r in rs])
                lr = np.median([r["lam_ratio_q"][1] for r in rs])
                print(f"  bg {bg} sigma {s:4.2f} {lab:5s}: sigma {med:.3f} s; k ratio {kr:.2f}; "
                      f"rate ratio {lr:.2f}; usable {us}/{n}; at bound {ab}")
    print("\nchance clusters per min, background only (10 recordings each)")
    for c in out["chance"]:
        print(f"  bg {c['bg']} K {c['K']}: predicted {c['predicted']:.3f}, measured median "
              f"{c['measured_median']:.3f} [IQR {c['measured_q'][0]:.3f}-{c['measured_q'][2]:.3f}]")


if __name__ == "__main__":
    summary(check())
