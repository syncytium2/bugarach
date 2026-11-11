"""Aim 0: what the measuring tools should return, predicted from the planted parameters.

Goal page: docs/goals/synthetic-validation.md, "Aim 0". Synthetic only. Revised after the
murderboard of 2026-10-23/24, all four rounds (docs/reviews/synthetic-validation-aim0_2026-10-23.md).

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

   Sections 2 and 3 for any event train: `train=` on `predicted_excess_cumulants`,
   `predict_solve` and `fit_joint` takes an `event_train.EventTrain` (beside this file;
   derivation in separation/real_intervals/derivation.md). It replaces the at-most-one-event term
   with the train's pair correlation and carries the surrogate's dependence on the train, its
   leakage and, with `n_events`, the fixed-count term. Without `train` everything here is the
   hard-core, independent-surrogate form above, unchanged. On real recordings use
   `train=EventTrain.palm(gaps, lam)` (untested on real data; see its docstring).

4. Chance clusters at K (bugarach.assess). In 1 s bins, a bin reaches K cells with
   q = P(Binomial(N, 1 - exp(-b)) >= K); a cluster starts on a bin at or over K whose two
   preceding bins are below it (merge_bins = 2), about (60 / bin) q (1 - q)^2 per minute.
   Tested on background-only recordings. Planted events are not predicted: whether an event
   reaches K depends on k, sigma and the bin, and no detection term is modelled here.

    PYTHONPATH=src python docs/learned/synthetic_validation/theory.py   # checks Aim 1a
    ... theory.py --train empirical      # the same under the general form: theory_check_empirical.json
    ... theory.py --check-real           # real-gap simulation, page vs general: theory_check_real.json
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
sys.path.insert(0, str(HERE))
import event_train as et  # noqa: E402
from event_train import EventTrain  # noqa: E402,F401

DT = mcr.DT
WINDOWS = tuple(float(w) for w in mcr.WINDOWS)
SIGMA_BOUNDS = (0.005, 5.0)       # s; the joint fit's search range, reported when it binds


def s_eff(sigma: float, dt: float = DT) -> float:
    """The jitter SD window sharing sees. Rounding onsets to the frame adds nothing in
    expectation: event times are continuous and the windows sit on the frame grid, so under a
    uniform phase E|round(a) - round(b)| = |a - b| (murderboard round 2, role 6, by simulation:
    g_2 0.9441 measured, 0.9436 unrounded, 0.9349 with an added dt^2/12). An earlier version added
    dt^2/12 here and biased the joint fit low at 0.05 s: about 18 % on the shared-seed record, and
    8 % at 0.01 Hz and 35 % at 0.05 Hz on the reseeded one (review agents' reruns, not kept here).
    It is dropped."""
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


def predicted_excess_cumulants(k: float, sigma: float, w: float, lam: float, n_cells: int,
                               train: EventTrain | None = None, n_events: float | None = None):
    """The (f2, f3) the tool's surrogate-corrected cumulants should equal, exactly as derived.

    ``train`` None: the hard-core form of section 2. An `EventTrain`: the general form, with the
    tool's surrogate; ``n_events`` conditions it on the recording's event count (`fixed_count`;
    leave it None for a `from_times` train, which is already conditioned)."""
    if train is not None:
        t = train if n_events is None else train.fixed_count(n_events)
        return et.cumulants_from(et.coefficients(w, sigma, n_cells, t), k, lam)
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


def predict_solve(k, sigma, w, lam, n_cells, poisson=False, train=None, n_events=None):
    """What the tool's fixed-model solve() returns, as ratios to the planted values."""
    f2, f3 = (poisson_cumulants(k, sigma, w, lam) if poisson
              else predicted_excess_cumulants(k, sigma, w, lam, n_cells, train, n_events))
    s = mcr.solve(f2, f3, n_cells, w, "fixed")
    return dict(k=s["k"] / k, lam=s["lam"] / lam, share=s["share"] / (lam * k / n_cells))


def fit_joint(cum: dict, n_cells: int, train: EventTrain | None = None,
              n_events: float | None = None, sigma_grid=None):
    """Fit (sigma, k, lambda) to the six excess cumulants across windows.

    cum: {window_sec: {"f2": .., "f3": ..}}. Residuals are scaled by each order's mean absolute
    value so f2 and f3 weigh alike. Returns a dict with the estimates and whether sigma hit a
    bound, or None when the cumulants carry no usable signal (f2 <= 0 at every window).

    ``train``: fit the general form for that event train instead of the hard core (``n_events``
    as in `predicted_excess_cumulants`). Its coefficients depend on sigma only, so they are
    tabulated once per train on a log-sigma grid (``sigma_grid``, default
    `event_train.SIGMA_GRID`, which spans SIGMA_BOUNDS; outside a narrower grid they are held at
    its ends) and interpolated, and the fit stays fast."""
    ws = np.array(sorted(float(w) for w in cum))
    f2 = np.array([cum[str(w)]["f2"] if str(w) in cum else cum[w]["f2"] for w in ws])
    f3 = np.array([cum[str(w)]["f3"] if str(w) in cum else cum[w]["f3"] for w in ws])
    if not np.any(f2 > 0):
        return None
    s2 = max(np.mean(np.abs(f2)), 1e-12)
    s3 = max(np.mean(np.abs(f3)), 1e-12)

    if train is None:
        model = lambda k, sig, w, lam: predicted_excess_cumulants(k, sig, w, lam, n_cells)  # noqa: E731
    else:
        grid = et.SIGMA_GRID if sigma_grid is None else np.asarray(sigma_grid, float)
        t = train if n_events is None else train.fixed_count(n_events)
        tab = et.coefficient_table(t, n_cells, ws, grid)
        model = lambda k, sig, w, lam: et.cumulants_from(et.interpolated(tab, w, sig, grid), k, lam)  # noqa: E731

    def resid(x):
        sig, k, lam = np.exp(x[0]), 2 + np.exp(x[1]), np.exp(x[2])
        pr = np.array([model(k, sig, w, lam) for w in ws])
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


TRAINS = ("hardcore-dependent", "analytic", "empirical")
N_DRAW = 20000      # generator draws behind the empirical pair correlation (as in the derivation)


def generator_train(spec: str, m: int, T: float, min_sep: float = 20.0, margin: float = 5.0,
                    n_draw: int = N_DRAW) -> EventTrain:
    """The Aim 1a generator's event train at m events per recording, as an `EventTrain` already
    conditioned on the count (so pass no ``n_events`` with it).

    ``hardcore-dependent``: the page's 20 s hard core, uncorrelated beyond, with the tool's
    surrogate (dependence and leakage). ``analytic``: `_place_renewal`'s law at interval_cv 1,
    min_sep + Exp(excess) with excess = (T - 2 margin) / (m + 1) - min_sep, plus the fixed-count
    term; it ignores the overrun rescaling. ``empirical``: the pair correlation of ``n_draw``
    draws of `_place_renewal` itself (seeds 0 .. n_draw-1, circular lags). The run record does
    not store the planted event times, so, as in the derivation (section 7.1), the generator is
    redrawn with the same m, span and floor; the draws are the derivation's."""
    if spec == "hardcore-dependent":
        return EventTrain.hard_core(min_sep)
    if spec == "analytic":
        e = (T - 2 * margin) / (m + 1) - min_sep
        dens = lambda t: np.where(t >= min_sep, np.exp(-(t - min_sep) / e) / e, 0.0)  # noqa: E731
        return EventTrain.renewal(density=dens, mean=min_sep + e, cv2=(e / (min_sep + e)) ** 2,
                                  name=f"generator m={m}").fixed_count(m)
    if spec == "empirical":
        from bugarach.simulate import _place_renewal
        draws = [_place_renewal(np.random.RandomState(i), m, margin, T - margin, min_sep, None, 1.0)
                 for i in range(n_draw)]
        return EventTrain.from_times(draws, T, name=f"generator m={m} (empirical)")
    raise ValueError(f"train {spec!r}: one of {TRAINS}")


def check(path=HERE / "aim1_one_source.json", train: str | None = None) -> dict:
    """Every prediction against the Aim 1a run record, per condition. Writes theory_check.json.

    ``train`` (one of TRAINS): the same under the general form for that event train, written to
    theory_check_<train>.json instead. Each row then also keeps the page's prediction ("page")
    and solve() on the condition's mean f2, f3 ("pooled")."""
    rec = json.loads(Path(path).read_text())
    rows, N, T = rec["rows"], rec["n_roi"], rec["duration_sec"]
    out = dict(what="Aim 0 predictions against Aim 1a, per condition (k, sigma, events, bg, w); "
                    "each measured value is a median over the condition's 5 recordings, "
                    "NaN estimates (solve refused) excluded and counted",
               coord_rates=[], joint_fit=[], chance=[])
    trains = {}
    if train is not None:
        out["train"] = train
        out["what"] += f"; predictions ('exact') under the general form, event train {train!r}"

    cond = defaultdict(list)
    for r in rows:
        t = r["true"]
        cond[(t["bg_rate"], t["jitter"], int(round(t["k"])), t["n_events"])].append(r)

    for (bg, s, k, ne), rs in sorted(cond.items()):
        lam = ne / T
        tr = None
        if train is not None:
            if ne not in trains:
                trains[ne] = generator_train(train, ne, T, rec["min_sep_sec"])
            tr = trains[ne]
        for w in (str(x) for x in mcr.WINDOWS):
            e = predict_solve(k, s, float(w), lam, N, train=tr)
            p = predict_solve(k, s, float(w), lam, N, poisson=True)
            vals = {q: [x["coord_rates"][w][q] / x["true"][q] for x in rs] for q in ("k", "lam", "share")}
            m = {q: float(np.nanmedian(v)) if np.any(np.isfinite(v)) else float("nan")
                 for q, v in vals.items()}
            sd = {q: float(np.nanstd(v)) for q, v in vals.items()}
            row = dict(bg=bg, sigma=s, k=k, n_events=ne, w=float(w),
                       exact=e, poisson=p, meas=m, meas_sd=sd,
                       n_nan=int(np.sum(~np.isfinite(vals["k"]))), n=len(rs))
            if tr is not None:
                row["page"] = predict_solve(k, s, float(w), lam, N)
                f2m = float(np.mean([x["cum"][w]["f2"] for x in rs]))
                f3m = float(np.mean([x["cum"][w]["f3"] for x in rs]))
                sv = mcr.solve(f2m, f3m, N, float(w), "fixed")
                row["pooled"] = dict(k=sv["k"] / k, lam=sv["lam"] / lam,
                                     share=sv["share"] / (lam * k / N))
            out["coord_rates"].append(row)
        fits = [fit_joint(x["cum"], N, train=tr) for x in rs]
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
    name = "theory_check.json" if train is None else f"theory_check_{train}.json"
    (HERE / name).write_text(json.dumps(out, indent=1))
    return out


def general_summary(out: dict) -> None:
    """For a general-form record: the residuals under the page's form and the general one side by
    side, as derivation.md section 7.2 tabulates them (events of 10+ cells)."""
    cr = out["coord_rates"]
    print(f"\ngeneral form, event train {out['train']!r}, against the page's form; events of 10+ "
          "cells; residual = condition median of measured / planted minus predicted / planted")
    print(f"  {'bg':>5} {'qty':>5} {'prediction':>10} {'median res':>10} {'median |res|':>12} "
          f"{'meas > pred':>11} {'sign p':>7} | pooled f2, f3: median res, above")
    for bg in (0.01, 0.05):
        for q in ("lam", "k", "share"):
            sel = [r for r in cr if r["bg"] == bg and r["k"] >= 10 and np.isfinite(r["meas"][q])]
            for lab, key in (("page", "page"), ("general", "exact")):
                res = np.array([r["meas"][q] - r[key][q] for r in sel])
                pres = np.array([r["pooled"][q] - r[key][q] for r in sel
                                 if np.isfinite(r["pooled"][q])])
                above = int(np.sum(res > 0))
                pv = stats.binomtest(above, res.size).pvalue
                print(f"  {bg:>5} {q:>5} {lab:>10} {np.median(res):+10.4f} "
                      f"{np.median(np.abs(res)):12.4f} {above:>5} of {res.size:<3} {pv:7.3f} | "
                      f"{np.median(pres):+.4f}, {int(np.sum(pres > 0))} of {pres.size}")


# ------------------------------------------------------------------ real-gap check

GAPS = ROOT / "docs" / "learned" / "runs" / "2026-09-25-real-intervals" / "gaps.csv"
REAL = dict(stream="fast", sigma=0.105, ks=(7, 13), bg=0.0096, n_cells=33, T=2700.0, margin=5.0)


def load_gaps(stream: str = "fast") -> np.ndarray:
    import csv
    with open(GAPS, newline="") as fh:
        return np.array([float(r["gap_sec"]) for r in csv.DictReader(fh) if r["stream"] == stream])


def _realgap_recording(args):
    """One recording whose events follow a stationary renewal train with gaps resampled from
    ``gaps``, planted through `simulate_coordination` itself (its placement replaced by these
    times) and measured with the shipped tool. As in derivation.md section 7.3."""
    k, seed, gaps = args
    from bugarach import simulate as sim
    c = REAL
    T, lo, hi = c["T"], c["margin"], c["T"] - c["margin"]
    rng_t = np.random.RandomState(700000 + seed)
    t, times = lo - 4000.0, []
    while t < hi:                       # the long run-in makes the train stationary on [lo, hi)
        t += gaps[rng_t.randint(0, gaps.size)]
        if lo <= t < hi:
            times.append(t)
    times = np.array(times)
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


def check_real(n_rec: int = 40, jobs: int | None = None) -> dict:
    """Real fast-stream gaps, simulated and measured with the shipped tool: the page's form
    against the general form, and the joint fit under each. Measured is solve() on the
    recordings' mean f2, f3, with a bootstrap SE. Two general trains: the renewal train of the gap
    law itself (lam = 1 / mean gap), and `EventTrain.palm` built as it would be on real data, from
    the planted times' own gaps and event rate. Writes theory_check_real.json."""
    import os
    from concurrent.futures import ProcessPoolExecutor
    c = REAL
    N, T, s = c["n_cells"], c["T"], c["sigma"]
    gaps = load_gaps(c["stream"])
    lam_f = 1.0 / gaps.mean()
    jobs = jobs or max(1, min(12, (os.cpu_count() or 2) - 1))
    args = [(k, 1000 * k + i, gaps) for k in c["ks"] for i in range(n_rec)]
    with ProcessPoolExecutor(jobs) as ex:
        rows = list(ex.map(_realgap_recording, args))
    m_bar = lam_f * (T - 2 * c["margin"])
    renewal = EventTrain.renewal(intervals=gaps, name=f"{c['stream']} gaps")
    planted_gaps = np.concatenate([np.diff(r["times"]) for r in rows])
    m_meas = float(np.mean([len(r["times"]) for r in rows]))
    lam_meas = m_meas / T
    palm = EventTrain.palm(planted_gaps, lam_meas, name="planted gaps")
    out = dict(what="real fast-stream gaps (gaps.csv) as stationary renewal trains, planted with "
                    "simulate_coordination and measured with measure_coordination_rates; ratios "
                    "to planted; measured = solve() on the mean f2, f3 over recordings "
                    "(bootstrap SE)",
               setup=dict(c, n_rec=n_rec, lam_f=lam_f, lam_planted=lam_meas,
                          share_gaps_under_4s=float(np.mean(gaps < 4.0))),
               windows=[], joint_fit=[])
    qs = ("k", "lam", "share")
    for k in c["ks"]:
        rs = [r for r in rows if r["k"] == k]
        lam_i = np.array([r["true"]["lam"] for r in rs])
        for w in mcr.WINDOWS:
            f2 = np.array([r["cum"][str(w)]["f2"] for r in rs])
            f3 = np.array([r["cum"][str(w)]["f3"] for r in rs])

            def ratio(a2, a3, lam):
                v = mcr.solve(a2, a3, N, w, "fixed")
                return dict(k=v["k"] / k, lam=v["lam"] / lam, share=v["share"] / (lam * k / N))

            meas = ratio(f2.mean(), f3.mean(), lam_i.mean())
            bs = np.random.RandomState(1)
            boot = []
            for _ in range(400):
                ii = bs.randint(0, len(rs), len(rs))
                v = ratio(f2[ii].mean(), f3[ii].mean(), lam_i[ii].mean())
                boot.append([v[q] for q in qs])
            se = dict(zip(qs, np.nanstd(np.array(boot), axis=0).tolist()))
            pred = dict(page=predict_solve(k, s, w, lam_f, N),
                        general=predict_solve(k, s, w, lam_f, N, train=renewal, n_events=m_bar),
                        palm=predict_solve(k, s, w, lam_meas, N, train=palm, n_events=m_meas))
            out["windows"].append(dict(k=k, w=w, measured=meas, measured_se=se, predicted=pred))
        fits = {}
        for lab, tr, ne in (("page", None, None), ("general", renewal, m_bar),
                            ("palm", palm, m_meas)):
            fs = [fit_joint(r["cum"], N, train=tr, n_events=ne) for r in rs]
            ok = [(f, r["true"]["lam"]) for f, r in zip(fs, rs) if f is not None]
            fits[lab] = dict(n_usable=len(ok), n_at_bound=int(sum(f["at_bound"] for f, _ in ok)),
                             sigma_ratio_q=_q([f["sigma"] / s for f, _ in ok]),
                             k_ratio_q=_q([f["k"] / k for f, _ in ok]),
                             lam_ratio_q=_q([f["lam"] / lt for f, lt in ok]))
        out["joint_fit"].append(dict(k=k, n=len(rs), **fits))
    (HERE / "theory_check_real.json").write_text(json.dumps(out, indent=1))
    return out


def real_summary(out: dict) -> None:
    """The numbers of a check_real() record."""
    c = out["setup"]
    print(f"real {c['stream']}-stream gaps: {c['n_rec']} recordings per k, sigma {c['sigma']} s, "
          f"lam = 1 / mean gap = {c['lam_f']:.5f} Hz (planted {c['lam_planted']:.5f} Hz); "
          f"{100 * c['share_gaps_under_4s']:.1f} % of gaps under 4 s")
    print("  ratio to planted: measured (SE) | page | general (renewal) | palm (planted gaps)")
    for r in out["windows"]:
        for q, lab in (("lam", "rate"), ("k", "participants")):
            m, se, p = r["measured"][q], r["measured_se"][q], r["predicted"]
            print(f"  k {r['k']:2d} w {r['w']:g} s {lab:12s}: {m:.3f} ({se:.3f}) | page "
                  f"{p['page'][q]:.3f} | general {p['general'][q]:.3f} | palm {p['palm'][q]:.3f}")
    print("  joint fit across windows, fitted / planted, median [IQR] over recordings")
    for r in out["joint_fit"]:
        for lab in ("page", "general", "palm"):
            f = r[lab]
            print(f"  k {r['k']:2d} {lab:7s}: " + "; ".join(
                f"{q} {f[q + '_ratio_q'][1]:.2f} [{f[q + '_ratio_q'][0]:.2f}, "
                f"{f[q + '_ratio_q'][2]:.2f}]" for q in ("sigma", "k", "lam"))
                + f" (usable {f['n_usable']}/{r['n']}, at the sigma bound {f['n_at_bound']})")


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
        # the three windows reuse each condition's recordings: one sign per condition
        byc = defaultdict(list)
        for r in rs:
            byc[(r["sigma"], r["k"], r["n_events"])].append(r["meas"]["k"] - r["exact"]["k"])
        below = sum(np.mean(v) < 0 for v in byc.values())
        print(f"    per condition (mean over windows): measured below predicted in {below} of "
              f"{len(byc)} (sign test p = {stats.binomtest(below, len(byc)).pvalue:.2f})")
        per_s = {s_: np.median([abs(r["meas"]["k"] - r["exact"]["k"]) for r in rs if r["sigma"] == s_])
                 for s_ in sorted({r["sigma"] for r in rs})}
        print("    median |residual| by jitter: " + ", ".join(f"{k_:g} s {v:.3f}" for k_, v in per_s.items()))
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
    print("\nAim 1a. Assessor jitter (s), median over recordings pooled over participation and event "
          "count, events of 10+ cells, wherever it observed clusters (n with a value / n)")
    for bg in (0.01, 0.05):
        for K in rec["ks"]:
            parts = []
            for s in jits:
                v = [r["assess"][str(K)]["jit"] for r in rows if r["true"]["bg_rate"] == bg
                     and r["true"]["jitter"] == s and r["true"]["k"] >= 10]
                d = [r["assess"][str(K)]["jit"] for r in rows if r["true"]["bg_rate"] == bg
                     and r["true"]["jitter"] == s and r["true"]["k"] >= 10
                     and r["assess"][str(K)]["jit"] is not None
                     and np.isfinite(r["assess"][str(K)]["jit"])]
                parts.append(f"{s:g}: {np.median(d):.2f} ({len(d)}/{len(v)})" if d else f"{s:g}: -")
            print(f"  bg {bg} K {K}: " + "; ".join(parts))
    print("assessor cluster rate / planted event rate at K = 6, condition medians (0.01 Hz)")
    for k in (5, 10):
        for s in jits:
            v = [float(np.median([r["assess"]["6"]["per_min"] / r["true"]["per_min"] for r in rs]))
                 for (bg, s_, k_, ne), rs in cond.items() if bg == 0.01 and s_ == s and k_ == k]
            print(f"  {k}-cell, sigma {s:g}: {min(v):.2f}-{max(v):.2f}")
    from bugarach.event_floor import FA_PER_HOUR, floor_of
    print("ADR-0008's budget applied to the assessor's predicted chance clusters: smallest K at "
          f"or below {FA_PER_HOUR:g} per hour")
    for bg in (0.01, 0.05):
        per_hour = [0.0] + [chance_clusters_per_min(N, bg, K) * 60 for K in range(1, N + 1)]
        K = floor_of(per_hour, FA_PER_HOUR)
        print(f"  bg {bg}: K = {K} ({per_hour[K]:.2f} per hour)")
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
    if "--check-real" in sys.argv:       # real-gap simulation; writes theory_check_real.json
        if "--from-record" in sys.argv:
            real_summary(json.loads((HERE / "theory_check_real.json").read_text()))
        else:
            real_summary(check_real())
    elif "--train" in sys.argv:          # the general form; writes theory_check_<train>.json
        spec = sys.argv[sys.argv.index("--train") + 1]
        if spec not in TRAINS:
            raise SystemExit(f"--train: one of {', '.join(TRAINS)}")
        if "--from-record" in sys.argv:
            res = json.loads((HERE / f"theory_check_{spec}.json").read_text())
        else:
            res = check(train=spec)
        summary(res)
        general_summary(res)
    else:
        if "--from-record" in sys.argv:      # summarize theory_check.json without rerunning check()
            summary(json.loads((HERE / "theory_check.json").read_text()))
        else:
            summary(check())
        aim1_summary()
