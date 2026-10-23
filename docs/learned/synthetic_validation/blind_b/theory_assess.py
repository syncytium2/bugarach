"""assess_coactivity at K: predicted cluster rate, participants and jitter vs aim1_one_source.json.

Closed form (background only, 1 s bins, merge_bins = 2, ROI active in a bin with q = 1 - exp(-b)):
    pi_K = P(Binom(N, q) >= K)                        fraction of bins at or above K
    R_false(K) = 60 * pi_K * (1 - pi_K)^2  per min    (a cluster starts where the two previous bins are below K)
Every false cluster passes the gather test (its own bin's ROIs are within 1.5 s of its centre).
    clusters/min = R_false + (n_ev/T_min) * D,  D = expected clusters one event adds (one-event Monte Carlo)
'Small-jitter' closed forms for a detected event, sigma << 1 s:
    D ~ P(k + Binom(N-k, q) >= K)
    gathered participants ~ k + (N - k)(1 - exp(-3b))  (any onset within +-1.5 s of the centre)
The observed median over clusters is the median of the MIXTURE of false and event clusters, weights
R_false : event rate. Its components (gathered count, onset SD) come from a short-strip Monte Carlo that
calls assess._clusters itself on one event (or none) plus background: no recording is simulated.
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
from bugarach.assess import _clusters, _coact_count  # noqa: E402

REC = HERE.parent / "docs/learned/synthetic_validation/aim1_one_source.json"
N, T = 33, 2700.0
DT = 0.1
STRIP = 40.0     # s; one event in the middle, background throughout


def pi_K(K, b, N=N):
    q = 1 - np.exp(-b * 1.0)
    return stats.binom.sf(K - 1, N, q)


def r_false(K, b):
    p = pi_K(K, b)
    return 60.0 * p * (1 - p) ** 2


def strip(rng, b, k, sigma):
    """One strip: background Poisson b on N ROIs, plus (k > 0) one event at the centre (random phase)."""
    trains = []
    t0 = STRIP / 2 + rng.uniform(0, 1)
    rois = set(rng.choice(N, size=k, replace=False).tolist()) if k else set()
    for r in range(N):
        v = rng.uniform(0, STRIP, rng.poisson(b * STRIP))
        if r in rois:
            v = np.append(v, t0 + sigma * rng.standard_normal())
        v = np.round(v / DT) * DT
        trains.append(np.sort(v[(v >= 0) & (v <= STRIP)]))
    return trains, t0


def strip_stats(b, k, sigma, K, n_mc, seed):
    rng = np.random.default_rng(seed)
    nb = int(STRIP)
    parts, sds, n_cl = [], [], []
    for _ in range(n_mc):
        tr, t0 = strip(rng, b, k, sigma)
        c = _coact_count(tr, STRIP, 1.0, nb)
        sd, pr, _, _, mem = _clusters(tr, c, K, 1.0, nb, 2, 1.5, with_members=True)
        # clusters whose span lies in the middle 20 s (edges excluded so the strip boundary does not bias)
        over = np.flatnonzero(c >= K)
        # recompute centres the way _clusters groups them
        groups, cur = [], []
        for f in over:
            if cur and f - cur[-1] > 2:
                groups.append(cur); cur = []
            cur.append(f)
        if cur:
            groups.append(cur)
        cents = [np.mean((np.asarray(g) + 0.5)) for g in groups]
        # _clusters drops groups failing the gather test; align by recomputing the test
        kept = []
        for g, tc in zip(groups, cents):
            got = sum(1 for v in tr if v.size and np.any(np.abs(v - tc) <= 1.5))
            if got >= K:
                kept.append(tc)
        assert len(kept) == len(sd)
        m = [i for i, tc in enumerate(kept) if 10 <= tc < 30]
        n_cl.append(len(m))
        parts += [pr[i] for i in m]
        sds += [sd[i] for i in m]
    return np.array(parts), np.array(sds), float(np.mean(n_cl))


def mixture_median(vals_f, w_f, vals_e, w_e):
    v = np.concatenate([vals_f, vals_e])
    wt = np.concatenate([np.full(len(vals_f), w_f / max(len(vals_f), 1)), np.full(len(vals_e), w_e / max(len(vals_e), 1))])
    o = np.argsort(v)
    cw = np.cumsum(wt[o]) / wt.sum()
    return float(v[o][np.searchsorted(cw, 0.5)])


def main():
    rec = json.loads(REC.read_text())
    cells = {}
    for r in rec["rows"]:
        t = r["true"]
        cells.setdefault((t["jitter"], int(t["k"]), t["n_events"], t["bg_rate"]), []).append(r)
    print("Closed form, background only: fraction of 1 s bins >= K and false clusters per minute")
    for b in (0.01, 0.05):
        print(f"  b={b}: " + "  ".join(f"K={K}: pi={pi_K(K, b):.2e} R={r_false(K, b):.3f}/min" for K in (3, 4, 6)))
    # false-cluster component distributions (background only strips): rate per 20 s middle span
    bgc = {}
    for b in (0.01, 0.05):
        for K in (3, 4, 6):
            pr, sd, ncl = strip_stats(b, 0, 0.0, K, 4000 if b == 0.05 else 20000, 11)
            bgc[(b, K)] = (pr, sd, ncl * 3.0)   # clusters per minute (20 s span)
            print(f"  strip MC check b={b} K={K}: false clusters/min {ncl*3:.3f} vs closed form {r_false(K, b):.3f}")
    out = []
    print("\nPer cell (median over 5 seeds observed): clusters/min, participants, jitter; pred | obs")
    print(f"{'sig':>4} {'k':>3} {'nev':>3} {'b':>4} {'K':>2} | {'cpm pr':>7} {'cpm ob':>7} | {'part pr':>7} {'ob':>5} | {'jit pr':>6} {'ob':>5}")
    for key, rs in sorted(cells.items()):
        sig, k, n_ev, b = key
        for K in (3, 4, 6):
            pr_e, sd_e, ncl_e = strip_stats(b, k, sig, K, 600, 3)
            pr_f, sd_f, rf = bgc[(b, K)]
            # event-added clusters per event: clusters in event strips minus the false ones expected in 20 s
            D = ncl_e - rf / 3.0
            lam = n_ev / (T / 60)
            cpm = rf + lam * D
            # mixture: event strips' clusters already include their share of false clusters at rate rf/3 per strip
            # weight per minute: event strips contribute lam * ncl_e, the rest of the time contributes rf*(1 - lam*20/60)
            w_e, w_f = lam * ncl_e, max(rf * (1 - lam / 3.0), 0)
            part = mixture_median(pr_f, w_f, pr_e, w_e) if (len(pr_e) + len(pr_f)) else np.nan
            jit = mixture_median(sd_f, w_f, sd_e, w_e) if (len(sd_e) + len(sd_f)) else np.nan
            ob = [x["assess"][str(K)] for x in rs]
            o_cpm = float(np.median([x["per_min"] for x in ob]))
            o_part = float(np.nanmedian([x["part"] for x in ob]))
            o_jit = float(np.nanmedian([x["jit"] for x in ob]))
            out.append(dict(sig=sig, k=k, n_ev=n_ev, b=b, K=K, cpm_p=cpm, cpm_o=o_cpm, part_p=part, part_o=o_part,
                            jit_p=jit, jit_o=o_jit, D=D, true_cpm=lam))
            print(f"{sig:4.2f} {k:3d} {n_ev:3d} {b:4.2f} {K:2d} | {cpm:7.3f} {o_cpm:7.3f} | {part:7.1f} {o_part:5.1f} | {jit:6.3f} {o_jit:5.3f}", flush=True)
    json.dump(out, open(HERE / "theory_assess_out.json", "w"), indent=0)
    for nm in ("cpm", "part", "jit"):
        p = np.array([o[nm + "_p"] for o in out]); o_ = np.array([o[nm + "_o"] for o in out])
        ok = np.isfinite(p) & np.isfinite(o_) & (p > 0) & (o_ > 0)
        lr = np.log(o_[ok] / p[ok])
        print(f"{nm}: {ok.sum()} cells, obs/pred geo-mean {np.exp(lr.mean()):.3f}, median |err| {100*(np.exp(np.median(np.abs(lr)))-1):.0f}%, "
              f"90th pct {100*(np.exp(np.percentile(np.abs(lr), 90))-1):.0f}%, corr(log) {np.corrcoef(np.log(p[ok]), np.log(o_[ok]))[0,1]:.3f}")


if __name__ == "__main__":
    main()
