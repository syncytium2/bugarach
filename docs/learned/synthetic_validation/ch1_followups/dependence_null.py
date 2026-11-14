"""Round 3, task 5 (blind review role 4): window-dependence-aware nulls for the chapter's
condition-window counts.

The chapter counts, over 48 condition-windows (16 conditions with 10- or 20-cell events x 3
windows, one background), how many sit beyond 2 SE of the prediction (SE = 1.2533 SD / sqrt(n),
SD with ddof 0, as theory.check / like_for_like) and how many have measured above predicted. It
reads those counts against independent windows: Binomial(48, 0.118) and Binomial(48, 1/2). The
three windows of a condition reuse the same 5 recordings, so they are positively dependent and
those binomials are too narrow.

Here the null "the prediction is exact" keeps that dependence. Per-recording values (measured /
planted, solve() per recording, all three windows of one recording kept together) come from the
run records; predictions from the matching theory_check record. Two resampling nulls, 20 000
replicate experiments each:

  MVN  : each condition's 3-window vector ~ Normal(prediction, the condition's own sample
         covariance over its recordings); 5 recordings drawn per condition.
  BOOT : every recording's vector is standardized within its condition ((x - condition mean) /
         condition SD (ddof 1), per window); the 80 standardized vectors of one (record,
         background, quantity) are pooled, and each condition draws 5 distinct ones (without
         replacement: duplicates would shrink the SD and inflate |z|), rescaled by its own SD and
         centred on the prediction. This keeps the cross-window correlation and the empirical
         shape, not just the covariance. Its limit: a vector standardized within 5 recordings
         cannot exceed (n - 1)/sqrt(n) = 1.79 SD, so the pooled shape has LIGHTER tails than the
         population, and centring on the condition mean, not the median, matters when the
         per-recording values are skewed.

Each replicate is scored exactly as the record was (median of 5, ddof-0 SD, |z| > 2; median >
prediction). Reported: the observed count, its P under the binomial (independent windows) and
under each null, and each null's mean and SD of the count beside the binomial's. Also the
one-sign-per-condition version (window-averaged residual, 16 conditions), which is already
independent across conditions and is checked here only as a control.

    PYTHONPATH=src python docs/learned/synthetic_validation/ch1_followups/dependence_null.py
"""
from __future__ import annotations

import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
SV = HERE.parent
WS = ("1.0", "2.0", "4.0")
N_REP = 20000
RECORDS = {
    "original": (SV / "aim1_one_source.json", {"hard-core": SV / "theory_check.json",
                                               "general": SV / "theory_check_empirical.json"}),
    "held-out": (HERE / "aim1_one_source_heldout.json", {"hard-core": HERE / "theory_check_heldout.json",
                                                         "general": HERE / "theory_check_heldout_empirical.json"}),
}
P2SE = 0.1183   # like_for_like.null_rate()


def score(x, pred):
    """x: (reps, conditions, n, 3) values; pred: (conditions, 3). Counts per replicate."""
    med = np.median(x, axis=2)
    sd = x.std(axis=2)
    n = x.shape[2]
    z = (med - pred) / (1.2533 * np.maximum(sd, 1e-9) / np.sqrt(n))
    beyond = (np.abs(z) > 2).sum(axis=(1, 2))
    above = (med > pred).sum(axis=(1, 2))
    cond_below = ((med - pred).mean(axis=2) < 0).sum(axis=1)
    return beyond, above, cond_below


def one(rec_rows, check_rows, bg, q, rng):
    cond = defaultdict(list)
    for r in rec_rows:
        t = r["true"]
        if t["bg_rate"] != bg or int(round(t["k"])) < 10:
            continue
        v = np.array([r["coord_rates"][w][q] / t[q] for w in WS])
        cond[(t["jitter"], int(round(t["k"])), t["n_events"])].append(v)
    pred = {}
    for c in check_rows:
        if c["bg"] == bg and c["k"] >= 10:
            pred.setdefault((c["sigma"], c["k"], c["n_events"]), {})[f"{c['w']:.1f}"] = c["exact"][q]
    keys = sorted(cond)
    P = np.array([[pred[kk][w] for w in WS] for kk in keys])
    X = [np.array(cond[kk]) for kk in keys]
    n_nan = sum(int(np.sum(~np.all(np.isfinite(x), 1))) for x in X)
    X = [x[np.all(np.isfinite(x), 1)] for x in X]
    n = 5
    # observed, scored as the record was (nan-dropped recordings; all have 5 here when n_nan = 0)
    med = np.array([np.median(x, 0) for x in X])
    sd = np.array([x.std(0) for x in X])
    nn = np.array([len(x) for x in X])[:, None]
    z = (med - P) / (1.2533 * np.maximum(sd, 1e-9) / np.sqrt(nn))
    obs = dict(beyond=int(np.sum(np.abs(z) > 2)), above=int(np.sum(med > P)),
               cond_below=int(np.sum((med - P).mean(1) < 0)))
    C = len(keys)
    # MVN null
    xm = np.empty((N_REP, C, n, 3))
    for j, x in enumerate(X):
        cov = np.cov(x.T, ddof=1)
        xm[:, j] = rng.multivariate_normal(P[j], cov, size=(N_REP, n), method="eigh")
    # pooled standardized bootstrap
    mu = [x.mean(0) for x in X]
    sdc = [x.std(0, ddof=1) for x in X]
    Z = np.concatenate([(x - m) / np.maximum(s, 1e-12) for x, m, s in zip(X, mu, sdc)])
    xb = np.empty((N_REP, C, n, 3))
    for j in range(C):
        idx = rng.random((N_REP, len(Z))).argsort(1)[:, :n]     # 5 distinct vectors
        xb[:, j] = P[j] + sdc[j] * Z[idx]
    corr = np.mean([np.corrcoef(x.T)[np.triu_indices(3, 1)] for x in X if len(x) > 2], axis=0)
    out = dict(n_condition_windows=3 * C, n_conditions=C, n_nan_recordings=n_nan, observed=obs,
               mean_window_corr=corr.tolist(), nulls={})
    for lab, xx in (("MVN", xm), ("BOOT", xb)):
        b, a, cb = score(xx, P)
        out["nulls"][lab] = dict(
            beyond_mean=float(b.mean()), beyond_sd=float(b.std()),
            p_beyond=float(np.mean(b >= obs["beyond"])),
            above_mean=float(a.mean()), above_sd=float(a.std()),
            p_above_two=float(min(1.0, 2 * min(np.mean(a >= obs["above"]), np.mean(a <= obs["above"])))),
            cond_below_sd=float(cb.std()),
            p_cond_two=float(min(1.0, 2 * min(np.mean(cb >= obs["cond_below"]), np.mean(cb <= obs["cond_below"])))))
    N = 3 * C
    out["binomial"] = dict(beyond_mean=P2SE * N, beyond_sd=float(np.sqrt(N * P2SE * (1 - P2SE))),
                           p_beyond=float(stats.binom.sf(obs["beyond"] - 1, N, P2SE)),
                           above_sd=float(np.sqrt(N) / 2),
                           p_above_two=float(stats.binomtest(obs["above"], N).pvalue),
                           p_cond_two=float(stats.binomtest(obs["cond_below"], C).pvalue))
    return out


if __name__ == "__main__":
    t0 = time.time()
    rng = np.random.default_rng(20261029)
    res = {}
    print(f"null 'prediction exact', {N_REP} replicate experiments; events of 10+ cells; 48 "
          "condition-windows = 16 conditions x 3 windows")
    print("record   form      bg   qty | >2SE obs | binomial mean+-SD P | MVN mean+-SD P | BOOT mean+-SD P "
          "|| above obs | binomial SD P | MVN SD P | BOOT SD P || cond below obs: binom P | MVN P | BOOT P "
          "|| mean corr (1-2, 1-4, 2-4 s)")
    for rname, (rp, forms) in RECORDS.items():
        rows = json.loads(rp.read_text())["rows"]
        for form, cp in forms.items():
            chk = json.loads(cp.read_text())["coord_rates"]
            for bg in (0.01, 0.05):
                for q in ("k", "lam"):
                    o = one(rows, chk, bg, q, rng)
                    res[f"{rname},{form},{bg},{q}"] = o
                    ob, bi, m, b = o["observed"], o["binomial"], o["nulls"]["MVN"], o["nulls"]["BOOT"]
                    print(f"{rname:8s} {form:9s} {bg:4} {q:4s}| {ob['beyond']:3d} | {bi['beyond_mean']:.1f}+-"
                          f"{bi['beyond_sd']:.1f} {bi['p_beyond']:.4f} | {m['beyond_mean']:.1f}+-{m['beyond_sd']:.1f} "
                          f"{m['p_beyond']:.4f} | {b['beyond_mean']:.1f}+-{b['beyond_sd']:.1f} {b['p_beyond']:.4f} "
                          f"|| {ob['above']:3d} | {bi['above_sd']:.1f} {bi['p_above_two']:.4f} | "
                          f"{m['above_sd']:.1f} {m['p_above_two']:.4f} | {b['above_sd']:.1f} {b['p_above_two']:.4f} "
                          f"|| {ob['cond_below']:2d}: {bi['p_cond_two']:.3f} | {m['p_cond_two']:.3f} | "
                          f"{b['p_cond_two']:.3f} || " + ", ".join(f"{c:.2f}" for c in o["mean_window_corr"])
                          + (f"  [{o['n_nan_recordings']} NaN recordings dropped]" if o["n_nan_recordings"] else ""))
    res["runtime_sec"] = time.time() - t0
    print(f"{res['runtime_sec']:.0f} s", file=sys.stderr)
    (HERE / "dependence_null.json").write_text(json.dumps(res, indent=1))
