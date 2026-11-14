"""Round 3, task 3 (blind review role 4): the order test with frame rounding at the cells the
chapter uses.

Extends order_rounding.py (whose draw / rounded / f_and_ties / exact_power are imported): onsets
t0 + template offset + N(0, sigma^2), t0 uniform on 100-200 s, rounded with the production
quantizer bugarach.simulate._quantize(..., 0.1); F scored with and without rounding on the same
draw (paired); ties add 0 to D and 1 to n.

Grid: sigma 0.105 and 0.131 s; 7 and 13 of 33 cells per event; r = delta / sigma = 1 and 2.5;
M = 1 and 2 templates; E = 2, 3, 5. 1000 signal recordings per point; a 2000-recording
order-free null per (sigma, k, E), scored both ways (the rounded test uses the rounded null).
Power is the exact-size randomized 5 % test (order_rounding.exact_power).

Null mean F. The exact no-order mean (kendall_w/derivation.md, `F_exact`) assumes untied
onsets (A2). With ties the same reduction still holds: the denominator sum n_ij = E C(k,2) is
not random, the label-swap argument still gives tied scores zero weight, and within a shared
event x = sign(t2 - t1) is still the sign of y = u1 - u2 (u_i = cells i leads minus cells that
lead i, ties counting 0), with x = y = 0 on a tie. So

    E[F] = E[ x sign(y + S) ],   S = sum of E - 1 i.i.d. per-event contributions Y,

where Y = u1 - u2 if both cells join (prob p2), u1 or -u2 if one does (2 p1), else 0. The laws of
(x, y) and of u now depend on sigma / frame and are no longer the rank lattice; here they are
estimated from 400 000 quantized model events per (sigma, k) and then convolved exactly
("tie-corrected mean"). The same machinery on unrounded events must reproduce F_exact.

    PYTHONPATH=src python docs/learned/synthetic_validation/ch1_followups/order_rounding_cells.py --workers 40
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SV = HERE.parent
sys.path.insert(0, str(SV))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SV / "kendall_w"))
sys.path.insert(0, str(SV.parents[2] / "src"))
import order_rounding as orr  # noqa: E402
from kendall_w import F_exact  # noqa: E402

N, GRID = 33, 0.1
SIGMAS, KS, RS, MS, ES = (0.105, 0.131), (7, 13), (1.0, 2.5), (1, 2), (2, 3, 5)
REPS, NULL = 1000, 2000
N_EVENT_MC = 400_000


def tie_pmfs(sigma, k, rounded, n=N_EVENT_MC, seed=0):
    """Per-event laws for one cell pair under the null: (x, y) when both join, u when one does."""
    rng = np.random.default_rng(seed)
    xs, ys, us = [], [], []
    for _ in range(n // 50_000):                        # chunks keep the sign cube small
        t = rng.uniform(100.0, 200.0, (50_000, 1)) + rng.normal(0, sigma, (50_000, k))
        if rounded:
            t = np.floor(t / GRID + 0.5) * GRID         # matlab_round (onsets > 0), as _quantize
        sg = np.sign(t[:, None, :] - t[:, :, None])    # [e, i, m] = sign(t_m - t_i): i leads m
        u = sg.sum(2).astype(int)                       # leads minus led, per cell
        xs.append(sg[:, 0, 1].astype(int))              # sign(t_1 - t_0): cell 0 leads cell 1
        ys.append(u[:, 0] - u[:, 1])
        us.append(u.ravel())
    x, y, u = np.concatenate(xs), np.concatenate(ys), np.concatenate(us)
    assert np.all(np.sign(y) == x), "x must be the sign of y"
    return x, y, u, float(np.mean(x == 0))


def mean_F_from_pmfs(x, y, u, k, E):
    p2 = k * (k - 1) / (N * (N - 1))
    p1 = k * (N - k) / (N * (N - 1))
    L = 2 * (k - 1)
    q = np.zeros(2 * L + 1)
    q[L] += 1 - p2 - 2 * p1
    np.add.at(q, L + y, p2 / y.size)
    np.add.at(q, L + u, p1 / u.size)
    np.add.at(q, L - u, p1 / u.size)
    S = np.array([1.0])
    for _ in range(E - 1):
        S = np.convolve(S, q)
    off = (S.size - 1) // 2
    cdf = np.concatenate([[0.0], np.cumsum(S)])

    def P(a, b):
        a, b = max(a, -off), min(b, off)
        return cdf[b + off + 1] - cdf[a + off] if b >= a else 0.0

    tot = 0.0
    vals, cnt = np.unique(np.stack([x, y], 1), axis=0, return_counts=True)
    for (xx, yy), c in zip(vals, cnt):
        if xx == 0:
            continue
        # E sign(yy + S) = P(S > -yy) - P(S < -yy)
        tot += c / x.size * xx * (P(-yy + 1, off) - P(-off, -yy - 1))
    return float(tot)


def tie_job(args):
    sigma, k, rounded = args
    x, y, u, tie = tie_pmfs(sigma, k, rounded, seed=int(1000 * sigma) * 100 + k + 50 * rounded)
    return sigma, k, rounded, tie, {E: mean_F_from_pmfs(x, y, u, k, E) for E in ES}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=40)
    a = ap.parse_args()
    t0 = time.time()
    rec = dict(N=N, grid=GRID, reps=REPS, null_reps=NULL, points=[], nulls=[], tie_corrected=[])
    with ProcessPoolExecutor(a.workers) as ex:
        tie = {(s, k, r): (tt, m) for s, k, r, tt, m in
               ex.map(tie_job, list(itertools.product(SIGMAS, KS, (False, True))))}
        nulls = {}
        for si, s in enumerate(SIGMAS):
            for k in KS:
                for E in ES:
                    nulls[(s, k, E)] = orr.run_many(ex, k, E, 1, 0.0, s, NULL, 7_000 + 100 * si + 10 * k + E)
        sig = {}
        for si, s in enumerate(SIGMAS):
            for k, r, M, E in itertools.product(KS, RS, MS, ES):
                sig[(s, k, r, M, E)] = orr.run_many(
                    ex, k, E, M, r, s, REPS, 8_000 + 1000 * si + 100 * k + 10 * int(2 * r) + 5 * M + E)
    rt = time.time() - t0
    print(f"{rt:.0f} s", file=sys.stderr)
    print(f"order test with onsets on the 0.1 s frame; {N} cells, score sort; {REPS} recordings per "
          f"signal point, {NULL}-recording null per (sigma, k, E), each rounded or not as its test; "
          "exact-size randomized 5 % test")
    print("\nnull mean F: simulated unrounded (SE) | F_exact (untied) || simulated rounded (SE) | "
          "tie-corrected exact mean | tied pairs in null")
    for (s, k, E), nv in nulls.items():
        se = nv[:, :2].std(0, ddof=1) / np.sqrt(len(nv))
        tc_u, tc_r = tie[(s, k, False)][1][E], tie[(s, k, True)][1][E]
        row = dict(sigma=s, k=k, E=E, null_mean_unrounded=float(nv[:, 0].mean()),
                   null_mean_rounded=float(nv[:, 1].mean()), se=se.tolist(),
                   F_exact=F_exact(N, k, E), machinery_unrounded=tc_u, tie_corrected=tc_r,
                   tied_share_null=float(nv[:, 2].mean()), tied_share_model=tie[(s, k, True)][0])
        rec["nulls"].append(row)
        print(f"  sigma {s:.3f} k {k:2d} E {E}: {row['null_mean_unrounded']:.4f} ({se[0]:.4f}) | "
              f"{row['F_exact']:.4f} [machinery on untied events {tc_u:.4f}] || "
              f"{row['null_mean_rounded']:.4f} ({se[1]:.4f}) | {tc_r:.4f} | {100 * row['tied_share_null']:.1f} %")
    print("\npower (exact 5 %) unrounded -> rounded | signal mean F unrounded -> rounded (shift) | "
          "null mean F unrounded -> rounded (shift) | tied pairs signal")
    for (s, k, r, M, E), v in sig.items():
        nv = nulls[(s, k, E)]
        row = dict(sigma=s, k=k, r=r, M=M, E=E,
                   power_unrounded=orr.exact_power(nv[:, 0], v[:, 0]),
                   power_rounded=orr.exact_power(nv[:, 1], v[:, 1]),
                   mean_F_unrounded=float(v[:, 0].mean()), mean_F_rounded=float(v[:, 1].mean()),
                   null_mean_unrounded=float(nv[:, 0].mean()), null_mean_rounded=float(nv[:, 1].mean()),
                   tied_share_signal=float(v[:, 2].mean()))
        rec["points"].append(row)
        print(f"  sigma {s:.3f} k {k:2d} r {r:g} M {M} E {E}: {row['power_unrounded']:.3f} -> "
              f"{row['power_rounded']:.3f} | {row['mean_F_unrounded']:.3f} -> {row['mean_F_rounded']:.3f} "
              f"({row['mean_F_rounded'] - row['mean_F_unrounded']:+.3f}) | {row['null_mean_unrounded']:.3f} -> "
              f"{row['null_mean_rounded']:.3f} ({row['null_mean_rounded'] - row['null_mean_unrounded']:+.3f}) | "
              f"{100 * row['tied_share_signal']:.1f} %")
    rec["runtime_sec"] = rt
    (HERE / "order_rounding_cells.json").write_text(json.dumps(rec, indent=1))
