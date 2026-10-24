"""Aim 0: what the measuring tools should return, predicted from the planted parameters.

Goal page: docs/goals/synthetic-validation.md, "Aim 0". Synthetic only. Revised after the
murderboard of 2026-10-23 (docs/reviews/synthetic-validation-aim0_2026-10-23.md).

The generator is a cluster process of the Neyman-Scott / Thomas type (Gaussian offspring), but
with a fixed number of parents held at least `min_sep` apart rather than Poisson parents:
independent Poisson background onsets per cell, plus coordinated events, each joined by k cells whose onsets carry
independent Gaussian jitter (SD sigma) and are then rounded to the 0.1 s frame. Symbols:
N cells, k participants per event (cells), sigma jitter SD (s), w window (s), lambda event rate
(per s), b background rate (Hz per cell), K the assessor's threshold (cells, an absolute count).

1. Window sharing. The chance that n onsets of one event fall in one window of width w, with the
   window's phase uniform, is g_n(w, s) = E[max(0, 1 - R_n / w)], R_n the range of n onsets.
   Rounding onsets to the frame changes nothing in expectation (see `s_eff`). g_2 has a closed
   form (two onsets differ by N(0, 2 s^2)); g_3 is a one-dimensional integral. Grun et al.
   1999 (J Neurosci Methods 94:67) derived the uniform-jitter, two-onset case ("fission
   probability") and read the temporal scatter from how detection changes with the analysis
   width; Pazienti et al. 2008 (Brain Res 1225:39; abstract read) estimated synchronization
   precision from how detection decays with the dither width, at one fixed window. Louis & Grun
   2009 (BMC Neurosci 10(Suppl 1):P253) and Louis, Borgelt & Grun 2010 (Neural Netw 23:705;
   abstract read) fitted group size and jitter together from the population complexity
   distribution across bin widths: the precedent for section 3.

2. The coordination-rates tool (tools/measure_coordination_rates.py). Its route is the cumulant
   route of CuBIC (Staude, Rotter & Grun 2010, J Comput Neurosci 29:327) on the multiple-
   interaction model of Kuhn, Aertsen & Rotter 2003; the tool uses factorial rather than ordinary
   cumulants of the population count, which add over independent processes. With at most one
   event per window, the coordinated count's factorial moments are m_r = p (k)_r g_r with
   p = lambda w, and the shift surrogate keeps each cell's own train (rate lambda k / N), so the
   excess the tool measures is

       f2 = p (k)_2 g_2 - (p k)^2 (1 - 1/N)
       f3 = p (k)_3 g_3 - 3 p^2 k (k)_2 g_2 + 2 (p k)^3 (1 - 1/N^2).

   The predictions are passed through the tool's own `solve()`, so a prediction and a
   measurement are the same estimator (including its refusal when f2 or f3 <= 0). Omitted: the
   surrogate's offsets (multiples of 2w, spanning minutes) are not independent of the renewal
   event train; a review agent's test put it at about 1 % of f2, of the sign and size of the
   rate residual (murderboard, blind round 2, role 6; not kept here).

3. Jitter, participants and rate, fitted together across the tool's windows (1, 2, 4 s): the
   six excess cumulants against the exact forms above, for (sigma, k, lambda). The joint fit
   follows blind pass A's route, re-specified (blind_README.md lists the differences); it
   replaces a one-parameter fit of f2(w)/w that ignored the at-most-one-event term. The pair-only
   analogue in spatial statistics is minimum-contrast fitting of a Thomas process to its
   K-function (Diggle, Besag & Gleaves 1976; Waagepetersen 2007).

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
    """The jitter SD window sharing sees. Rounding onsets to the frame adds nothing in
    expectation: event times are continuous and the windows sit on the frame grid, so under a
    uniform phase E|round(a) - round(b)| = |a - b| (murderboard round 2, role 6, by simulation:
    g_2 0.9441 measured, 0.9436 unrounded, 0.9349 with an added dt^2/12). An earlier version added
    dt^2/12 here and biased the joint fit about 18 % low at 0.05 s; it is dropped."""
    return float(sigma)


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


def predicted_excess_cumulants(k: float, sigma: float, w: float, lam: float, n_cells: int):
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
              else predicted_excess_cumulants(k, sigma, w, lam, n_cells))
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
        pr = np.array([predicted_excess_cumulants(k, sig, w, lam, n_cells) for w in ws])
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


def _assessor_defaults():
    """The assessor's bin and merge rule, read from its signature so the prediction follows it."""
    import inspect
    from bugarach.assess import assess_coactivity
    sig = inspect.signature(assess_coactivity).parameters
    bw = sig["bin_width_sec"].default
    return (1.0 if bw is None else float(bw)), int(sig["merge_bins"].default)


def chance_clusters_per_min(n_cells: int, bg_hz: float, K: int, bin_sec: float | None = None,
                            merge_bins: int | None = None) -> float:
    """Clusters per minute that background alone produces at threshold K (cells), for a field of
    equal rates (Aim 1a's). A field of unequal rates needs the Poisson-binomial tail instead
    (`tools/measure_chance_floor.poisson_binomial_sf`)."""
    if bin_sec is None or merge_bins is None:
        b0, m0 = _assessor_defaults()
        bin_sec = b0 if bin_sec is None else bin_sec
        merge_bins = m0 if merge_bins is None else merge_bins
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
        for w in (str(x) for x in mcr.WINDOWS):
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
        pred = chance_clusters_per_min(N, bg, K)
        counts = np.round(np.array(v) * T / 60.0).astype(int)   # clusters per recording
        tot, exp_tot = int(counts.sum()), pred * T / 60.0 * len(v)
        lo = stats.chi2.ppf(0.025, 2 * tot) / 2 if tot > 0 else 0.0     # exact Poisson 95 % CI
        hi = stats.chi2.ppf(0.975, 2 * tot + 2) / 2
        p_two = (float(min(1.0, 2 * min(stats.poisson.cdf(tot, exp_tot),
                                         stats.poisson.sf(tot - 1, exp_tot))))
                 if exp_tot > 0 else float("nan"))
        scale = 60.0 / (T * len(v))
        out["chance"].append(dict(bg=bg, K=K, predicted=pred,
                                  measured_median=float(np.median(v)), measured_q=_q(v), n=len(v),
                                  pooled_count=tot, expected_count=exp_tot,
                                  pooled_rate=tot * scale, pooled_rate_ci=[lo * scale, hi * scale],
                                  p_poisson=p_two))
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
    # The SE of a median of n = 5, from an SD of the same 5 values (ddof 0), is heavy-tailed:
    # calibrate |z| > 2 by simulating that statistic under a normal null.
    x = np.random.default_rng(0).standard_normal((400_000, 5))
    p2 = float(np.mean(np.abs(np.median(x, 1) / (1.2533 * x.std(1) / np.sqrt(5))) > 2))
    print(f"\nparticipants, k >= 10: |z| > 2 of (median - prediction) / (1.2533 SD / sqrt(n)); "
          f"null rate {p2:.3f} at n = 5 (simulated). The three windows reuse the same recordings.")
    for bg in (0.01, 0.05):
        rs = [r for r in cr if r["bg"] == bg and r["k"] >= 10 and np.isfinite(r["meas"]["k"])]
        z = [(r["meas"]["k"] - r["exact"]["k"]) / (1.2533 * max(r["meas_sd"]["k"], 1e-9)
                                                  / np.sqrt(r["n"] - r["n_nan"])) for r in rs]
        nz = sum(abs(v) > 2 for v in z)
        above = sum(r["meas"]["k"] > r["exact"]["k"] for r in rs)
        signed = np.median([r["meas"]["k"] - r["exact"]["k"] for r in rs])
        print(f"  bg {bg}: {nz} of {len(z)} condition-windows beyond 2 SE (about {p2 * len(z):.1f} "
              f"expected; binomial P(>= {nz}) = {stats.binom.sf(nz - 1, len(z), p2):.2f}); "
              f"measured above predicted in {above} of {len(rs)} (sign test p = "
              f"{stats.binomtest(above, len(rs)).pvalue:.3f}); median signed residual {signed:+.3f}")
        for q in ("lam", "share"):
            above = sum(r["meas"][q] > r["exact"][q] for r in rs if np.isfinite(r["meas"][q]))
            print(f"    {q}: measured above predicted in {above} of {len(rs)}")
    print("\nper-condition range (median ratio to planted), k >= 10 (and 5-cell)")
    for bg in (0.01, 0.05):
        for w in (str(x) for x in mcr.WINDOWS):
            for q in ("k", "share"):
                v = [r["meas"][q] for r in cr if r["bg"] == bg and r["k"] >= 10 and str(r["w"]) == w]
                v5 = [r["meas"][q] for r in cr if r["bg"] == bg and r["k"] == 5 and str(r["w"]) == w]
                print(f"  bg {bg} w {w} {q:5s}: {min(v):.2f}-{max(v):.2f} "
                      f"(5-cell: {np.nanmin(v5):.2f}-{np.nanmax(v5):.2f})")
    for bg in (0.01, 0.05):
        r5 = [r for r in cr if r["bg"] == bg and r["k"] == 5]
        wr = max((r for r in r5 if np.isfinite(r["meas"]["k"])), key=lambda r: r["meas"]["k"])
        wl = max((r for r in r5 if np.isfinite(r["meas"]["lam"])), key=lambda r: r["meas"]["lam"])
        print(f"  5-cell, bg {bg}: worst measured ratio to planted: participants {wr['meas']['k']:.2f} "
              f"(w {wr['w']:g} s, sigma {wr['sigma']:g} s), rate {wl['meas']['lam']:.2f}")
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
    jf = [r for r in out["joint_fit"] if r["k"] >= 10]
    for bg in (0.01, 0.05):
        rr = [r for r in jf if r["bg"] == bg and r["sigma"] >= 0.2]
        print(f"  per-condition, k>=10, sigma>=0.2, bg {bg}: sigma ratio "
              f"{min(r['sigma_q'][1] / r['sigma'] for r in rr):.2f}-"
              f"{max(r['sigma_q'][1] / r['sigma'] for r in rr):.2f}; "
              f"k {min(r['k_ratio_q'][1] for r in rr):.2f}-{max(r['k_ratio_q'][1] for r in rr):.2f}; "
              f"rate {min(r['lam_ratio_q'][1] for r in rr):.2f}-{max(r['lam_ratio_q'][1] for r in rr):.2f}")
        r5 = [r for r in out["joint_fit"] if r["bg"] == bg and r["k"] == 5]
        print(f"  5-cell, bg {bg}: sigma ratio {min(r['sigma_q'][1] / r['sigma'] for r in r5):.2f}-"
              f"{max(r['sigma_q'][1] / r['sigma'] for r in r5):.2f}")
    print("\nchance clusters, background only: pooled rate, exact Poisson 95 % CI")
    for c in out["chance"]:
        print(f"  bg {c['bg']} K {c['K']}: predicted {c['predicted']:.4f}/min; pooled {c['pooled_count']} "
              f"clusters against {c['expected_count']:.1f} expected = {c['pooled_rate']:.4f}/min "
              f"[{c['pooled_rate_ci'][0]:.4f}-{c['pooled_rate_ci'][1]:.4f}], p = {c['p_poisson']:.3f}")

def aim1_summary(path=HERE / "aim1_one_source.json") -> None:
    """The Aim 1a numbers the goal page quotes, recomputed from the run record."""
    rec = json.loads(Path(path).read_text())
    rows, N = rec["rows"], rec["n_roi"]
    cond = defaultdict(list)
    for r in rows:
        t = r["true"]
        cond[(t["bg_rate"], t["jitter"], int(round(t["k"])), t["n_events"])].append(r)
    jits = sorted({k[1] for k in cond})
    print("\nAim 1a. Assessor jitter (s), median over recordings, events of 10+ cells, where the "
          "assessor marks it defined (n defined / n)")
    for bg in (0.01, 0.05):
        for K in rec["ks"]:
            parts = []
            for s in jits:
                v = [r["assess"][str(K)]["jit"] for r in rows if r["true"]["bg_rate"] == bg
                     and r["true"]["jitter"] == s and r["true"]["k"] >= 10]
                d = [r["assess"][str(K)]["jit"] for r in rows if r["true"]["bg_rate"] == bg
                     and r["true"]["jitter"] == s and r["true"]["k"] >= 10
                     and r["assess"][str(K)]["jit_defined"]]
                parts.append(f"{s:g}: {np.median(d):.2f} ({len(d)}/{len(v)})" if d else f"{s:g}: -")
            print(f"  bg {bg} K {K}: " + "; ".join(parts))
    print("assessor rate / planted at K = 6, condition medians (0.01 Hz)")
    for k in (5, 10):
        for s in jits:
            v = [float(np.median([r["assess"]["6"]["per_min"] / r["true"]["per_min"] for r in rs]))
                 for (bg, s_, k_, ne), rs in cond.items() if bg == 0.01 and s_ == s and k_ == k]
            print(f"  {k}-cell, sigma {s:g}: {min(v):.2f}-{max(v):.2f}")
    print("smallest K with chance clusters at or below one per hour (the assessor's own rule)")
    for bg in (0.01, 0.05):
        K = next(K for K in range(2, N) if chance_clusters_per_min(N, bg, K) <= 1 / 60)
        print(f"  bg {bg}: K = {K} ({chance_clusters_per_min(N, bg, K) * 60:.2f} per hour)")
    print("coordination-rates tool at 1 s jitter, events of 10+ cells: per-condition medians / planted")
    for bg in (0.01, 0.05):
        for w, q in (("1.0", "k"), ("4.0", "k"), ("1.0", "lam")):
            v = [float(np.nanmedian([r["coord_rates"][w][q] / r["true"][q] for r in rs]))
                 for (bg_, s, k, ne), rs in cond.items() if bg_ == bg and s == 1.0 and k >= 10]
            print(f"  bg {bg} w {w} {q}: {min(v):.2f}-{max(v):.2f}")
        v = [float(np.nanmedian([r["coord_rates"]["4.0"]["k"] / r["true"]["k"] for r in rs]))
             for (bg_, s, k, ne), rs in cond.items() if bg_ == bg and k >= 10]
        print(f"  bg {bg} w 4.0 k, every jitter: {min(v):.2f}-{max(v):.2f}")


if __name__ == "__main__":
    if "--from-record" in sys.argv:      # summarize theory_check.json without rerunning check()
        summary(json.loads((HERE / "theory_check.json").read_text()))
    else:
        summary(check())
    aim1_summary()
