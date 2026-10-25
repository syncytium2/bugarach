"""Two coordinated events Δ apart: the chance the assessor (and the count detector) reports two.

Derivation: derivation.md beside this file. Run from the bugarach checkout:

    PYTHONPATH=src python <this file> [--pairs 400] [--workers 40] [--quick]

Writes split_output.txt, synth_recovery_plot_assessor-split-against-separation_20261025.png and split_results.json beside this file.

The prediction is an exact recursion over bins (`dp_groups`). Given which cells have an event
onset in a bin, the bins are independent (background is independent Poisson per cell), so a
bin fires with phi(X) = P(X + Bin(N - X, p_b) >= K), X the number of distinct cells with an
event onset there. X itself comes from a sequential (bin-by-bin) multinomial placement of the
two events' onsets, tracked by three counters: cells with only an A onset still to land, cells
with only a B onset still to land, and shared cells with both still to land. The fire pattern
drives a 10-state automaton that counts merged groups (merge when at most one sub-K bin lies
between fire bins). The gather is shown in derivation.md never to remove a group at the
defaults, so groups are clusters. Phase of the bin grid: midpoint quadrature over one bin.
Membership overlap: hypergeometric, mixed into the initial state.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy import stats
from scipy.special import gammaln

HERE = Path(__file__).resolve().parent
N_CELLS = 33
DT = 0.1                         # frame (s); onsets rounded half away from zero
SIGMAS = (0.105, 0.5)
KS = (7, 13)
BGS = (0.0096, 0.05)
DELTAS_SIM = (0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 8.0)
DELTAS_CURVE = tuple(np.round(np.r_[np.arange(0.0, 6.0, 0.125), np.arange(6.0, 10.01, 0.5)], 3))
THRESHOLDS = (5, 6, 8, 12)       # assessor's 1/h chance K (5, 8) and ADR-0008 floor (6, 12)
COMBOS = tuple((b, K) for b in BGS for K in THRESHOLDS)
TOOLS = {"assessor": 1.0, "count": 2.0}   # bin width (s); both split on >= 2 sub-K bins
N_PHASE = 32
PAD_SIG = 7.0                    # region: clouds' +-7 sigma, plus PAD_BINS bins each side
PAD_BINS = 3

# automaton: 0 = no group yet; 1 + 3 (g - 1) + d, g = groups so far (3 = 3 or more),
# d = sub-K bins since the last fire bin (2 = two or more: the group is closed)
FIRE_TO = np.zeros(10, int)
NOFIRE_TO = np.zeros(10, int)
for s in range(10):
    if s == 0:
        FIRE_TO[s], NOFIRE_TO[s] = 1, 0
        continue
    g, d = (s - 1) // 3 + 1, (s - 1) % 3
    FIRE_TO[s] = 1 + 3 * ((g if d <= 1 else min(g + 1, 3)) - 1)
    NOFIRE_TO[s] = 1 + 3 * (g - 1) + min(d + 1, 2)


def phi_table(bin_sec: float, xcap: int) -> np.ndarray:
    """phi[x, c]: chance a bin fires given x distinct cells have an event onset in it."""
    out = np.ones((xcap + 1, len(COMBOS)))
    for c, (b, K) in enumerate(COMBOS):
        pb = 1.0 - math.exp(-b * bin_sec)
        for x in range(min(K, xcap + 1)):
            out[x, c] = stats.binom.sf(K - x - 1, N_CELLS - x, pb)
    return out


def bin_probs(c: float, sigma: float, j0: int, j1: int, w: float) -> np.ndarray:
    """P(onset of an event centred at c lands in bin j), j = j0..j1, after frame rounding:
    round(t) is in [j w, (j+1) w) iff t is in [j w - DT/2, (j+1) w - DT/2). Tails folded in."""
    e = np.arange(j0, j1 + 2) * w - DT / 2
    cdf = stats.norm.cdf((e - c) / sigma)
    cdf[0], cdf[-1] = 0.0, 1.0
    return np.diff(cdf)


def hazards(p: np.ndarray) -> np.ndarray:
    R = np.cumsum(p[::-1])[::-1]
    with np.errstate(divide="ignore", invalid="ignore"):
        h = np.where(R > 1e-300, p / R, 0.0)
    return np.clip(h, 0.0, 1.0)


def _shift_add(dst, src, sh, xcap):
    """dst[min(x + sh, xcap)] += src[x] along axis 0."""
    if sh == 0:
        dst += src
    elif sh >= xcap:
        dst[xcap] += src.sum(0)
    else:
        dst[sh:xcap] += src[:xcap - sh]
        dst[xcap] += src[xcap - sh:].sum(0)


def _multinom(g, xa, xb, xab, hA, hB):
    st = g - xa - xb - xab
    ps = ((1 - hA) * (1 - hB), hA * (1 - hB), (1 - hA) * hB, hA * hB)
    ns = (st, xa, xb, xab)
    lp = gammaln(g + 1) - sum(gammaln(n + 1) for n in ns)
    for n, p in zip(ns, ps):
        if n:
            if p <= 0:
                return 0.0
            lp += n * math.log(p)
    return math.exp(lp)


def dp_groups(pA, pB, k, m_w, phi, tol=1e-15):
    """Exact P(groups = 0, 1, 2, >=3) per combo, for onset bin distributions pA, pB.

    m_w: {m: weight} for the number of shared cells. phi: (xcap + 1, C)."""
    xcap = phi.shape[0] - 1
    C = phi.shape[1]
    mmax = max(m_w)
    S = np.zeros((k + 1, k + 1, mmax + 1, 10, C))
    for m, wgt in m_w.items():
        S[k - m, k - m, m, 0, :] += wgt
    hAs, hBs = hazards(pA), hazards(pB)
    for hA, hB in zip(hAs, hBs):
        Z = np.zeros((xcap + 1,) + S.shape)
        if hA < tol and hB < tol:
            Z[0] = S
        else:
            # A-pending cells
            if hA < tol:
                Z[0] = S
            else:
                for n in range(k + 1):
                    src = S[n]
                    if not src.any():
                        continue
                    pm = stats.binom.pmf(np.arange(n + 1), n, hA)
                    for i in range(n + 1):
                        if pm[i] > tol:
                            Z[min(i, xcap), n - i] += pm[i] * src
            # B-pending cells
            if hB >= tol:
                Z2 = np.zeros_like(Z)
                for n in range(k + 1):
                    src = Z[:, :, n]
                    if not src.any():
                        continue
                    pm = stats.binom.pmf(np.arange(n + 1), n, hB)
                    for i in range(n + 1):
                        if pm[i] > tol:
                            _shift_add(Z2[:, :, n - i], pm[i] * src, i, xcap)
                Z = Z2
            # shared cells with both onsets pending
            Z3 = np.zeros_like(Z)
            for g in range(mmax + 1):
                src = Z[:, :, :, g]
                if not src.any():
                    continue
                for xa in range(g + 1):
                    for xb in range(g + 1 - xa):
                        for xab in range(g + 1 - xa - xb):
                            pr = _multinom(g, xa, xb, xab, hA, hB)
                            if pr <= tol:
                                continue
                            t = xa + xb + xab
                            s2 = src[:, :k + 1 - xb, :k + 1 - xa]
                            _shift_add(Z3[:, xb:, xa:, g - t], pr * s2, t, xcap)
            Z = Z3
        ph = phi.reshape((xcap + 1,) + (1,) * 4 + (C,))
        F = (Z * ph).sum(0)
        NF = Z.sum(0) - F
        S = np.zeros_like(S)
        for s in range(10):
            S[..., FIRE_TO[s], :] += F[..., s, :]
            S[..., NOFIRE_TO[s], :] += NF[..., s, :]
    auto = S.sum((0, 1, 2))                         # (10, C)
    out = np.zeros((4, C))
    out[0] = auto[0]
    for g in (1, 2, 3):
        out[g] = auto[1 + 3 * (g - 1):1 + 3 * g].sum(0)
    return out


def m_weights(k):
    rv = stats.hypergeom(N_CELLS, k, k)
    w = {m: float(rv.pmf(m)) for m in range(k + 1) if rv.pmf(m) > 1e-12}
    s = sum(w.values())
    return {m: v / s for m, v in w.items()}


def predict_one(args):
    """P(groups) per combo for one (tool, sigma, k, delta), averaged over the bin phase."""
    tool, sigma, k, delta = args
    w = TOOLS[tool]
    xcap = max(THRESHOLDS)
    phi = phi_table(w, xcap)
    mw = m_weights(k)
    acc = np.zeros((4, len(COMBOS)))
    for u in (np.arange(N_PHASE) + 0.5) / N_PHASE * w:
        cA, cB = u, u + delta
        j0 = int(math.floor((cA - PAD_SIG * sigma) / w)) - PAD_BINS
        j1 = int(math.floor((cB + PAD_SIG * sigma) / w)) + PAD_BINS
        pA = bin_probs(cA, sigma, j0, j1, w)
        pB = bin_probs(cB, sigma, j0, j1, w)
        acc += dp_groups(pA, pB, k, mw, phi)
    return args, acc / N_PHASE


# ------------------------------------------------------------------------ simulation
def _mround(x):
    return np.floor(x / DT + 0.5) * DT          # matlab_round, as the generator applies it


def simulate_point(args):
    """One recording of n_pairs planted pairs; per pair, clusters from both tools at every K."""
    sigma, k, b, delta, n_pairs, seed = args
    from bugarach.assess import _coact_count, _clusters
    from bugarach.detectors.count import count_detect
    rng = np.random.RandomState(seed)
    spacing = 40.0
    T = 20.0 + spacing * n_pairs + 20.0
    centres = 20.0 + spacing * np.arange(n_pairs) + rng.uniform(0.0, 2.0, n_pairs)
    trains = [list(rng.uniform(0.0, T, rng.poisson(b * T))) for _ in range(N_CELLS)]
    real_sep, n_shared = np.zeros(n_pairs), np.zeros(n_pairs, int)
    for i, c in enumerate(centres):
        meds = []
        mem = []
        for t in (c, c + delta):
            rois = np.sort(rng.choice(N_CELLS, size=k, replace=False))
            got = []
            for r in rois:
                on = min(max(t + sigma * rng.randn(), 0.0), T)
                trains[r].append(on)
                got.append(on)
            meds.append(float(np.median(_mround(np.asarray(got)))))
            mem.append(set(rois.tolist()))
        real_sep[i] = meds[1] - meds[0]
        n_shared[i] = len(mem[0] & mem[1])
    trains = [np.sort(_mround(np.asarray(v, float))) for v in trains]
    def assign(starts, ends, w):
        """Per pair, the number of groups whose [start, end) overlaps its region: exactly the
        bins the prediction recurses over (predict_one), so chance groups are counted alike."""
        lo = (np.floor((centres - PAD_SIG * sigma) / w) - PAD_BINS) * w
        hi = (np.floor((centres + delta + PAD_SIG * sigma) / w) + PAD_BINS + 1) * w
        cnt = np.zeros(n_pairs, int)
        stray = 0
        for s_, e_ in zip(starts, ends):
            hit = np.flatnonzero((s_ < hi) & (e_ > lo))
            if hit.size:
                cnt[hit] += 1
            else:
                stray += 1
        return cnt, stray

    res = {}
    n_bins = int(np.ceil(T / 1.0))
    obs = _coact_count(trains, T, 1.0, n_bins)
    for K in THRESHOLDS:
        fire = np.flatnonzero(obs >= K)
        groups = []
        if fire.size:
            cur = [fire[0]]
            for f in fire[1:]:
                if f - cur[-1] <= 2:
                    cur.append(f)
                else:
                    groups.append(cur)
                    cur = [f]
            groups.append(cur)
        sds, _, _, _ = _clusters(trains, obs, K, 1.0, n_bins, 2, 1.5)
        cnt, stray = assign([g[0] * 1.0 for g in groups], [g[-1] + 1.0 for g in groups],
                            TOOLS["assessor"])
        res[("assessor", K)] = dict(n_clusters=cnt.tolist(), stray=stray,
                                    n_groups=len(groups), n_clusters_tool=len(sds))
        cd = count_detect(trains, (0.0, T), bin_sec=2.0, min_rois=K, k_offset=0,
                          merge_gap_sec=3.0)
        cnt, stray = assign(cd.onset_sec, cd.onset_sec + cd.width_sec, TOOLS["count"])
        res[("count", K)] = dict(n_clusters=cnt.tolist(), stray=stray,
                                 n_groups=int(cd.n_events), n_clusters_tool=int(cd.n_events))
    return args, dict(T=T, real_sep=real_sep.tolist(), n_shared=n_shared.tolist(), res=res)


def full_assess_check(args):
    """The shipped assess_coactivity on one simulated recording: its cluster total against the
    per-pair counts (a check that the replica above is the tool)."""
    sigma, k, b, delta, n_pairs, seed = args
    from bugarach.assess import assess_coactivity
    from bugarach.io import slice_from_events
    # rebuild the identical recording
    rng = np.random.RandomState(seed)
    spacing = 40.0
    T = 20.0 + spacing * n_pairs + 20.0
    centres = 20.0 + spacing * np.arange(n_pairs) + rng.uniform(0.0, 2.0, n_pairs)
    trains = [list(rng.uniform(0.0, T, rng.poisson(b * T))) for _ in range(N_CELLS)]
    for c in centres:
        for t in (c, c + delta):
            rois = np.sort(rng.choice(N_CELLS, size=k, replace=False))
            for r in rois:
                trains[r].append(min(max(t + sigma * rng.randn(), 0.0), T))
    trains = [np.sort(_mround(np.asarray(v, float))) for v in trains]
    s = slice_from_events({"events": trains}, dt=DT, slice_id="sep")
    out = assess_coactivity(s, window=(0.0, T), min_rois=THRESHOLDS, n_surrogates=2,
                            region_min_sec=0.0)
    return args, {a.min_rois: a.n_clusters_obs for a in out}


# ------------------------------------------------------------------------ reporting
def z_and_p(x, n, p):
    se = math.sqrt(max(p * (1 - p), 1e-12) / n)
    z = (x / n - p) / se
    pv = stats.binomtest(int(x), int(n), min(max(p, 1e-12), 1 - 1e-12)).pvalue
    return z, pv


def delta50(ds, ps):
    """First separation where P(two) crosses 0.5 upward (linear interpolation), or None."""
    for i in range(1, len(ds)):
        if ps[i - 1] < 0.5 <= ps[i]:
            return ds[i - 1] + (0.5 - ps[i - 1]) * (ds[i] - ds[i - 1]) / (ps[i] - ps[i - 1])
    return None if ps[0] < 0.5 else ds[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", type=int, default=400)
    ap.add_argument("--workers", type=int, default=40)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--plot-only", action="store_true", help="redraw synth_recovery_plot_assessor-split-against-separation_20261025.png from split_results.json")
    ap.add_argument("--resim", action="store_true",
                    help="reuse the predictions in split_results.json; rerun the simulation")
    a = ap.parse_args()
    if a.plot_only:
        plot(json.loads((HERE / "split_results.json").read_text()))
        return
    t0 = time.time()
    curve = DELTAS_CURVE if not a.quick else DELTAS_SIM
    jobs = [(tool, s, k, d) for tool in TOOLS for s in SIGMAS for k in KS for d in curve]
    sims = [(s, k, b, d, a.pairs, 1000 + i) for i, (s, k, b, d) in enumerate(
        (s, k, b, d) for s in SIGMAS for k in KS for b in BGS for d in DELTAS_SIM)]
    with Pool(a.workers) as pool:
        if a.resim:
            old = json.loads((HERE / "split_results.json").read_text())
            pred = {(c["tool"], c["sigma"], c["k"], c["delta"]): np.asarray(c["p"])
                    for c in old["curve"]}
        else:
            pred = dict(pool.map(predict_one, jobs, chunksize=1))
        sim = dict(pool.map(simulate_point, sims, chunksize=1))
        chk = dict(pool.map(full_assess_check, sims[::9], chunksize=1))
    print(f"computed in {time.time() - t0:.0f} s", file=sys.stderr)
    report(pred, sim, chk, a.pairs)
    plot(json.loads((HERE / "split_results.json").read_text()))


def report(pred, sim, chk, n_pairs):
    lines = []
    P = lines.append
    sys.path.insert(0, str(Path.cwd() / "docs" / "learned" / "synthetic_validation"))
    try:
        from theory import chance_clusters_per_min
        P("Assessor chance clusters per hour at N = 33 (theory.chance_clusters_per_min):")
        for b in BGS:
            P("  b = %g Hz: " % b + ", ".join(
                f"K={K}: {60 * chance_clusters_per_min(N_CELLS, b, K):.3g}" for K in range(3, 13)))
    except Exception as e:  # pragma: no cover
        P(f"(theory.py not importable: {e})")
    P("ADR-0008 event floor (bugarach.event_floor.window_floor, 2 h Poisson background, "
      "1000 draws, 2 seeds): 6 cells at 0.0096 Hz, 12 at 0.05 Hz.")
    P("")
    # gather check
    bad = [(key, r["n_groups"], r["n_clusters_tool"]) for v in sim.values()
           for key, r in v["res"].items() if r["n_groups"] != r["n_clusters_tool"]]
    P(f"Gather check: merged groups vs _clusters output differ in {len(bad)} of "
      f"{sum(len(v['res']) for v in sim.values())} recording-thresholds. {bad[:5]}")
    for args, d in chk.items():
        s, k, b, de, n, seed = args
        mine = {K: sum(sim[args]["res"][("assessor", K)]["n_clusters"])
                + sim[args]["res"][("assessor", K)]["stray"] for K in THRESHOLDS}
        P(f"  assess_coactivity on sigma {s} k {k} b {b} delta {de}: n_clusters_obs {d} "
          f"vs replica {mine}")
    P("")
    rows = []
    combos = {c: i for i, c in enumerate(COMBOS)}
    P("Comparison: P(two clusters) and P(at least one), predicted vs measured, n pairs each.")
    P("z = (measured - predicted) / sqrt(p (1 - p) / n); p_binom is the exact two-sided test.")
    hdr = (f"{'tool':8s} {'sig':>5s} {'k':>3s} {'b':>6s} {'K':>3s} {'Delta':>5s} | "
           f"{'P2 pred':>7s} {'P2 meas':>7s} {'z':>6s} {'p_bin':>6s} | "
           f"{'P>=1 pr':>7s} {'P>=1 ms':>7s} {'z':>6s} | {'P>=3 pr':>7s} {'ms':>6s}")
    for tool in TOOLS:
        for (b, K) in COMBOS:
            P("")
            P(hdr)
            for s in SIGMAS:
                for k in KS:
                    for d in DELTAS_SIM:
                        args = next(x for x in sim if x[:4] == (s, k, b, d))
                        cnt = np.asarray(sim[args]["res"][(tool, K)]["n_clusters"])
                        n = cnt.size
                        pr = pred[(tool, s, k, d)][:, combos[(b, K)]]
                        p2, p1, p3 = pr[2], 1 - pr[0], pr[3]
                        x2, x1, x3 = (cnt == 2).sum(), (cnt >= 1).sum(), (cnt >= 3).sum()
                        z2, pv2 = z_and_p(x2, n, p2)
                        z1, _ = z_and_p(x1, n, p1)
                        rows.append(dict(tool=tool, sigma=s, k=k, b=b, K=K, delta=d, n=int(n),
                                         p2_pred=p2, p2_meas=x2 / n, z2=z2, p2_binom=pv2,
                                         p1_pred=p1, p1_meas=x1 / n, z1=z1, p3_pred=p3,
                                         p3_meas=x3 / n))
                        P(f"{tool:8s} {s:5.3f} {k:3d} {b:6.4f} {K:3d} {d:5.2f} | "
                          f"{p2:7.3f} {x2 / n:7.3f} {z2:6.2f} {pv2:6.3f} | "
                          f"{p1:7.3f} {x1 / n:7.3f} {z1:6.2f} | {p3:7.4f} {x3 / n:6.3f}")
    zs = np.array([r["z2"] for r in rows if 0.01 < r["p2_pred"] < 0.99])
    P("")
    P(f"P(two) z over points with 0.01 < p < 0.99: n = {zs.size}, mean {zs.mean():+.2f}, "
      f"SD {zs.std():.2f}, |z| > 2 in {(np.abs(zs) > 2).sum()}, |z| > 3 in "
      f"{(np.abs(zs) > 3).sum()}")
    pv = np.array([r["p2_binom"] for r in rows])
    P(f"exact binomial p < 0.01 in {(pv < 0.01).sum()} of {pv.size} points "
      f"(about {0.01 * pv.size:.1f} expected by chance)")
    P("")
    P("Separation at which predicted P(two) first reaches 0.5 (s; '-' never within 0-10 s)")
    d50 = {}
    for tool in TOOLS:
        for (b, K) in COMBOS:
            for s in SIGMAS:
                for k in KS:
                    ds = [d for d in sorted({x[3] for x in pred if x[:3] == (tool, s, k)})]
                    ps = [pred[(tool, s, k, d)][2, combos[(b, K)]] for d in ds]
                    v = delta50(ds, ps)
                    d50[(tool, b, K, s, k)] = v
                    P(f"  {tool:8s} b {b:6.4f} K {K:2d} sigma {s:5.3f} k {k:2d}: "
                      + ("-" if v is None else f"{v:.2f}") + f"   (max P2 {max(ps):.3f})")
    P("")
    # realized separation
    P("Split rate against REALIZED separation (median B onset - median A onset), pooled over "
      "planned Delta, per tool, sigma, k, b, K. Bins of realized separation (s).")
    edges = np.array([-10, 0.125, 0.375, 0.75, 1.25, 1.75, 2.5, 3.5, 4.5, 6.5, 20])
    real = []
    for tool in TOOLS:
        for (b, K) in COMBOS:
            for s in SIGMAS:
                for k in KS:
                    rs, cs = [], []
                    for args, v in sim.items():
                        if args[:3] == (s, k, b):
                            rs += v["real_sep"]
                            cs += v["res"][(tool, K)]["n_clusters"]
                    rs, cs = np.asarray(rs), np.asarray(cs)
                    idx = np.digitize(rs, edges) - 1
                    cells = []
                    for i in range(len(edges) - 1):
                        sel = idx == i
                        if sel.sum():
                            cells.append(dict(lo=float(edges[i]), hi=float(edges[i + 1]),
                                              mean_real=float(rs[sel].mean()),
                                              n=int(sel.sum()),
                                              p2=float((cs[sel] == 2).mean())))
                    real.append(dict(tool=tool, b=b, K=K, sigma=s, k=k, cells=cells))
                    P(f"  {tool:8s} b {b:6.4f} K {K:2d} sigma {s:5.3f} k {k:2d}: " + "; ".join(
                        f"{c['mean_real']:.2f}s {c['p2']:.2f} (n={c['n']})" for c in cells))
    P("")
    P("Realized separation spread per planned Delta (sigma, Delta: median [5th-95th pct])")
    for s in SIGMAS:
        for d in DELTAS_SIM:
            rs = np.concatenate([np.asarray(v["real_sep"]) for a_, v in sim.items()
                                 if a_[0] == s and a_[3] == d])
            P(f"  sigma {s:5.3f} Delta {d:4.2f}: {np.median(rs):.2f} "
              f"[{np.percentile(rs, 5):.2f}, {np.percentile(rs, 95):.2f}]; "
              f"realized <= 0 in {np.mean(rs <= 0):.3f}")
    strays = {}
    for args, v in sim.items():
        for key, r in v["res"].items():
            strays.setdefault(key + (args[2],), [0, 0.0])
            strays[key + (args[2],)][0] += r["stray"]
            strays[key + (args[2],)][1] += v["T"] / 3600
    P("")
    P("Chance clusters outside every pair's region, per hour (tool, K, b):")
    for key, (n, h) in sorted(strays.items()):
        P(f"  {key}: {n} in {h:.1f} h = {n / h:.2f}/h")
    (HERE / "split_output.txt").write_text("\n".join(lines) + "\n")
    (HERE / "split_results.json").write_text(json.dumps(dict(
        rows=rows, real=real,
        curve=[dict(tool=t, sigma=s, k=k, delta=d,
                    p=pred[(t, s, k, d)].tolist()) for (t, s, k, d) in pred],
        combos=COMBOS, d50=[dict(tool=t, b=b, K=K, sigma=s, k=k, d50=v)
                            for (t, b, K, s, k), v in d50.items()]), indent=1))
    print("\n".join(lines))


# Which K each tool is plotted at: the assessor at its own one-per-hour chance K (5, 8), the count
# detector at its shipped setting, the ADR-0008 floor plus k_offset 0 (6, 12).
PLOT_K = {("assessor", 0.0096): 5, ("assessor", 0.05): 8, ("count", 0.0096): 6, ("count", 0.05): 12}
# colour per (tool, k); marker and line also separate the tools, so no pair rests on colour alone
STYLE = {("assessor", 7): ("#2a78d6", "o", "-"), ("assessor", 13): ("#eb6834", "o", "-"),
         ("count", 7): ("#1baf7a", "s", "--"), ("count", 13): ("#6250d6", "s", "--")}


def plot(res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    plt.rcParams.update({"font.size": 11})
    combos = [tuple(c) for c in res["combos"]]
    fig, axes = plt.subplots(2, 4, figsize=(17, 9.6), sharex=True, sharey=True)
    panels = [(s, b) for s in SIGMAS for b in BGS]
    off = {("assessor", 7): -0.09, ("assessor", 13): -0.03, ("count", 7): 0.03, ("count", 13): 0.09}
    for col, (s, b) in enumerate(panels):
        for row in (0, 1):
            ax = axes[row, col]
            ax.axvline(2 * s, color="0.55", ls=":", lw=1.2)
            ax.axvline(3.8, color="#c0392b", ls="-.", lw=1.0)
            for (tool, k), (colr, mk, ls) in STYLE.items():
                K = PLOT_K[(tool, b)]
                ci = combos.index((b, K))
                cv = sorted((c for c in res["curve"] if c["tool"] == tool and c["sigma"] == s
                             and c["k"] == k), key=lambda c: c["delta"])
                ax.plot([c["delta"] for c in cv], [c["p"][2][ci] for c in cv], color=colr, ls=ls,
                        lw=1.6, alpha=1.0 if row == 0 else 0.35)
                if row == 0:
                    pts = [r for r in res["rows"] if r["tool"] == tool and r["sigma"] == s
                           and r["k"] == k and r["b"] == b and r["K"] == K]
                    x = np.array([r["delta"] for r in pts]) + off[(tool, k)]
                    y = np.array([r["p2_meas"] for r in pts])
                    n = np.array([r["n"] for r in pts])
                else:
                    rr = next(r for r in res["real"] if r["tool"] == tool and r["sigma"] == s
                              and r["k"] == k and r["b"] == b and r["K"] == K)
                    cells = [c for c in rr["cells"] if c["n"] >= 20]
                    x = np.array([c["mean_real"] for c in cells]) + off[(tool, k)]
                    y = np.array([c["p2"] for c in cells])
                    n = np.array([c["n"] for c in cells])
                se = np.sqrt(np.maximum(y * (1 - y), 0.25 / n) / n)
                ax.errorbar(x, y, yerr=se, fmt=mk, color=colr, ms=5, capsize=2, lw=1,
                            mfc=colr if row == 0 else "white")
            ax.set_xlim(-0.3, 8.7)
            ax.set_ylim(-0.03, 1.03)
            ax.grid(alpha=0.25)
            letter = "ABCDEFGH"[row * 4 + col]
            ax.text(0.03, 0.95, letter, transform=ax.transAxes, fontweight="bold", fontsize=14,
                    va="top")
            ax.set_title(f"jitter SD {s:g} s, background {b:g} Hz per cell", fontsize=10,
                         loc="right")
            if row == 1:
                ax.set_xlabel("realized separation, median onset B minus A (s)")
            else:
                ax.set_xlabel("planned separation, centre to centre (s)")
            if col == 0:
                ax.set_ylabel("P(pair reported as two clusters)")
    h = []
    for (tool, k), (colr, mk, ls) in STYLE.items():
        lab = (f"assessor, {k} of 33 cells per event; K = 5 cells at 0.0096 Hz, 8 at 0.05 Hz"
               if tool == "assessor" else
               f"count detector, {k} of 33 cells per event; K = ADR-0008 floor, 6 cells at "
               f"0.0096 Hz, 12 at 0.05 Hz")
        h.append(Line2D([], [], color=colr, ls=ls, marker=mk, label=lab))
    h += [Line2D([], [], color="0.3", ls="-", label="line: exact prediction at planned separation "
                 "(faint in E-H)"),
          Line2D([], [], color="0.3", ls="none", marker="o", label="filled: simulated, 400 pairs, "
                 "+-1 binomial SE"),
          Line2D([], [], color="0.3", ls="none", marker="o", mfc="white",
                 label="open: simulated, binned by realized separation (bins of >= 20 pairs)"),
          Line2D([], [], color="0.55", ls=":", label="2 x jitter SD: onset clouds unimodal below"),
          Line2D([], [], color="#c0392b", ls="-.", label="3.8 s: 5th percentile of real fast-stream gaps")]
    fig.legend(handles=h, loc="lower center", ncol=2, fontsize=9.5, frameon=False,
               bbox_to_anchor=(0.5, -0.005))
    fig.tight_layout(rect=(0, 0.15, 1, 1))
    fig.savefig(HERE / "synth_recovery_plot_assessor-split-against-separation_20261025.png", dpi=150)


if __name__ == "__main__":
    main()
