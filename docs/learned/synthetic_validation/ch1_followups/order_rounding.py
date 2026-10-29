"""Round 2, task 4 (murderboard 2026-10-29 round 2, roles 6 and 7): frame rounding in the order test.

order_limit.simulate has no frame grid. Here each event gets a continuous time t0 (uniform on
100-200 s, so its phase against the 0.1 s frame is uniform), its onsets t0 + template offset +
N(0, sigma^2) are rounded to the 0.1 s frame by the production quantizer
`bugarach.simulate._quantize` (matlab_round, half away from zero), and F is scored on the
rounded onsets and, for the same draw, on the unrounded ones (paired).

Ties. Two cells of one event on the same frame tie. order_limit.pair_matrices scores a pair by
sign(t_j - t_i), so a tie adds 0 to D (neither cell leads) and still adds 1 to the pair's
co-participation count n, the denominator of F. A tie therefore pulls F toward 0. This is the
tie rule used for every number below; the share of tied pairs is printed.

Power: order_limit's score sort, 33 cells, 13 cells per event, E = 3 and 5, one template,
r = delta / sigma = 2.5, sigma = 0.105 s and 0.2 s. Each test is against an order-free null of
the same size built the same way (rounded null for the rounded test): Table 1.2's method (F
above the 95th percentile of 300 null draws) and the exact-size randomized 5 % test on a
3000-recording null (as order_power.py). 2000 recordings per signal point.

Mean F change: delta = sigma = 0.1 s (r = 1), 33 cells, 10 per event, 200 events per recording
(as order_limit.py's one-template run), 200 recordings; also r = 2.5 at sigma 0.105 s. This
replaces the unkept "about 9 %" of order_limit.py's docstring and the chapter's limitation 4.

    PYTHONPATH=src python docs/learned/synthetic_validation/ch1_followups/order_rounding.py --workers 40
"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SV = HERE.parent
sys.path.insert(0, str(SV))
sys.path.insert(0, str(SV.parents[2] / "src"))
import order_limit as ol  # noqa: E402

N, GRID = 33, 0.1
NULL_SMALL, NULL_BIG, REPS = 300, 3000, 2000


def draw(k, E, M, s, sigma, rng):
    """order_limit.simulate's events, with a continuous event time added (onsets absolute)."""
    ev = ol.simulate(N, k, E, M, s, sigma, rng)
    return [(cells, rng.uniform(100.0, 200.0) + t) for cells, t in ev]


def rounded(ev):
    from bugarach.simulate import _quantize
    return [(cells, np.array(_quantize(t, GRID))) for cells, t in ev]


def f_and_ties(ev):
    n, d = ol.pair_matrices(ev, N)
    F = ol.f_of(ol.score_order(d), n, d)
    ties = sum(int(np.sum(np.triu(t[None, :] == t[:, None], 1))) for _, t in ev)
    pairs = sum(len(c) * (len(c) - 1) // 2 for c, _ in ev)
    return F, ties / pairs


def batch(args):
    """F unrounded and rounded for `reps` paired draws."""
    k, E, M, r, sigma, reps, seed = args
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(reps):
        ev = draw(k, E, M, r * sigma, sigma, rng)
        f0, _ = f_and_ties(ev)
        f1, tie = f_and_ties(rounded(ev))
        out.append((f0, f1, tie))
    return out


def run_many(ex, k, E, M, r, sigma, reps, seed, chunk=50):
    jobs = [(k, E, M, r, sigma, min(chunk, reps - i), seed * 1000 + i // chunk)
            for i in range(0, reps, chunk)]
    return np.array([row for part in ex.map(batch, jobs) for row in part])


def exact_power(null, sig):
    nr, vr = np.round(null, 9), np.round(sig, 9)
    c = next(v for v in np.unique(nr) if np.mean(nr > v) <= 0.05)
    gamma = (0.05 - np.mean(nr > c)) / np.mean(nr == c)
    return float(np.mean(vr > c) + gamma * np.mean(vr == c))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=40)
    a = ap.parse_args()
    rec = dict(what="order test with onsets rounded to the 0.1 s frame (bugarach.simulate._quantize); "
                    "ties score 0 in D and count in n", N=N, grid=GRID, power=[], mean_f=[])
    with ProcessPoolExecutor(a.workers) as ex:
        print("power, one template, r = 2.5, 13 cells per event, 33 cells, score sort; "
              f"{REPS} recordings per point. Table 1.2's method (300-draw null) | exact 5 % "
              f"(randomized, {NULL_BIG}-draw null)")
        for si, sigma in enumerate((0.105, 0.2)):
            for E in (3, 5):
                base = 100 * si + E
                small = run_many(ex, 13, E, 1, 0.0, sigma, NULL_SMALL, 1 + base)
                big = run_many(ex, 13, E, 1, 0.0, sigma, NULL_BIG, 2 + base)
                sig = run_many(ex, 13, E, 1, 2.5, sigma, REPS, 3 + base)
                row = dict(sigma=sigma, E=E, k=13, r=2.5, M=1)
                for j, lab in ((0, "unrounded"), (1, "rounded")):
                    thr = float(np.percentile(small[:, j], 95))
                    row[lab] = dict(table_1_2=float(np.mean(sig[:, j] > thr)),
                                    table_1_2_size=float(np.mean(small[:, j] > thr)),
                                    exact=exact_power(big[:, j], sig[:, j]),
                                    mean_F=float(sig[:, j].mean()),
                                    null_mean_F=float(big[:, j].mean()))
                row["tied_pair_share_signal"] = float(sig[:, 2].mean())
                row["tied_pair_share_null"] = float(big[:, 2].mean())
                rec["power"].append(row)
                u, rd = row["unrounded"], row["rounded"]
                print(f"  sigma {sigma:.3f} s, E {E}: unrounded {u['table_1_2']:.3f} | "
                      f"{u['exact']:.3f}   rounded {rd['table_1_2']:.3f} | {rd['exact']:.3f}   "
                      f"(mean F {u['mean_F']:.3f} -> {rd['mean_F']:.3f}; null mean F "
                      f"{u['null_mean_F']:.3f} -> {rd['null_mean_F']:.3f}; tied pairs "
                      f"{100 * row['tied_pair_share_signal']:.1f} % signal, "
                      f"{100 * row['tied_pair_share_null']:.1f} % null)")
        print("\nmean F with many events: 33 cells, 10 per event, 200 events, one template, "
              "200 recordings (paired draws)")
        for i, (sigma, r) in enumerate(((0.1, 1.0), (0.105, 2.5), (0.2, 1.0), (0.2, 2.5))):
            v = run_many(ex, 10, 200, 1, r, sigma, 200, 50 + i, chunk=5)
            d = v[:, 1] / v[:, 0] - 1
            row = dict(sigma=sigma, delta=r * sigma, r=r, k=10, E=200, n=len(v),
                       mean_F_unrounded=float(v[:, 0].mean()), mean_F_rounded=float(v[:, 1].mean()),
                       mean_rel_change=float(d.mean()), sd_rel_change=float(d.std(ddof=1)),
                       tied_pair_share=float(v[:, 2].mean()),
                       predicted_unrounded=float(ol.pred_one(r)))
            rec["mean_f"].append(row)
            print(f"  delta {r * sigma:.3f} s, sigma {sigma:.3f} s (r = {r:g}): F {row['mean_F_unrounded']:.4f}"
                  f" -> {row['mean_F_rounded']:.4f}, change {100 * row['mean_rel_change']:+.2f} % "
                  f"(SE {100 * row['sd_rel_change'] / np.sqrt(len(v)):.2f} %); (2/pi) arctan r = "
                  f"{row['predicted_unrounded']:.4f}; tied pairs {100 * row['tied_pair_share']:.1f} %")
    (HERE / "order_rounding.json").write_text(json.dumps(rec, indent=1))
