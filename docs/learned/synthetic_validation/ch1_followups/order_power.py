"""Task 6 (murderboard 2026-10-29, roles 4 and 6): power to detect order at small event counts.

Same method as order_limit.py's power table (Table 1.2): the share of recordings with M latency
templates whose score-sort indicator F exceeds the 95th percentile of order-free recordings of
the same size (one-sided 5 %), 300 recordings on each side. order_limit.py's own `simulate`,
`indicators` (score sort) are imported, not copied. Perfect readout, no background, as there.

Grid: E = 1, 2, 3, 5 events per recording; 7 and 13 cells per event; 33 cells; M = 1 and 2
templates; r = delta / sigma = 1, 2.5, 5 (sigma 0.2 s as in order_limit.py, delta = r sigma).
The null is shared across r (it has no template). Each grid point has its own seed.

F is discrete at these sizes (a multiple of 2 / total pair co-participations), so "F above the
95th percentile of 300 null draws" has a realized size below 5 % that depends on which lattice
value the percentile lands on, and float ties at that value compare arbitrarily. Three powers
are printed: Table 1.2's method as is; the same against a 3000-recording null; and an exact-size
randomized test on the 3000-recording null. A last block repeats Table 1.2's method six times
(seeds 100-105) at its 7-cell, 5-event, r = 2.5, one-template entry, to show its spread.

    python docs/learned/synthetic_validation/ch1_followups/order_power.py
"""
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import order_limit as ol  # noqa: E402

N, SIGMA, REPS = 33, 0.2, 300
ES, KS, MS, RS = (1, 2, 3, 5), (7, 13), (1, 2), (1.0, 2.5, 5.0)


def point(args):
    k, E = args
    rng = np.random.default_rng(10_000 * k + E)
    null = np.array([ol.indicators(ol.simulate(N, k, E, 1, 0.0, SIGMA, rng), N)[0]
                     for _ in range(REPS)])
    thr = float(np.percentile(null, 95))
    # F is discrete at these sizes, so the 95th percentile of 300 null draws lands on a lattice
    # value and the realized size (null share strictly above it) is below 5 % and varies with the
    # draw. A 3000-recording null (its own seed) gives a steadier threshold; both are reported.
    rng_big = np.random.default_rng(20_000 * k + E)
    big = np.array([ol.indicators(ol.simulate(N, k, E, 1, 0.0, SIGMA, rng_big), N)[0]
                    for _ in range(10 * REPS)])
    thr_big = float(np.percentile(big, 95))
    # Exact-size (randomized) test on the 3000-recording null, F rounded to 1e-9 so that equal
    # lattice values compare equal: reject when F > c, and with probability gamma when F == c,
    # where P0(F > c) + gamma P0(F == c) = 0.05. Its power is P1(F > c) + gamma P1(F == c).
    bigr = np.round(big, 9)
    vals = np.unique(bigr)
    c = next(v for v in vals if np.mean(bigr > v) <= 0.05)
    gamma = (0.05 - np.mean(bigr > c)) / np.mean(bigr == c)
    row = dict(k=k, E=E, n_bar=ol.nbar(N, k, E), null_mean=float(null.mean()),
               null_sd=float(null.std()), threshold=thr,
               size=float(np.mean(null > thr)), null_share_at_threshold=float(np.mean(null >= thr)),
               threshold_3000=thr_big, size_3000=float(np.mean(big > thr_big)),
               randomized_c=float(c), randomized_gamma=float(gamma),
               power={}, power_3000={}, power_randomized={})
    for r in RS:
        for M in MS:
            v = np.array([ol.indicators(ol.simulate(N, k, E, M, r * SIGMA, SIGMA, rng), N)[0]
                          for _ in range(REPS)])
            row["power"][f"r={r:g},M={M}"] = float(np.mean(v > thr))
            row["power_3000"][f"r={r:g},M={M}"] = float(np.mean(v > thr_big))
            vr = np.round(v, 9)
            row["power_randomized"][f"r={r:g},M={M}"] = float(np.mean(vr > c) + gamma * np.mean(vr == c))
    return row


if __name__ == "__main__":
    with ProcessPoolExecutor(8) as ex:
        rows = list(ex.map(point, [(k, E) for k in KS for E in ES]))
    print(f"power against an order-free null (one-sided 5 %, F > 95th percentile of {REPS} "
          f"null recordings), {REPS} recordings per point, {N} cells, score sort")
    for row in rows:
        print(f"  {row['k']:2d} cells/event, E {row['E']}: null F {row['null_mean']:.3f} +- "
              f"{row['null_sd']:.3f}; threshold {row['threshold']:.3f}, realized size "
              f"{row['size']:.3f} | " + " ".join(f"{key}: {p:.2f}" for key, p in row["power"].items()))
        print(f"      3000-recording null: threshold {row['threshold_3000']:.3f}, realized size "
              f"{row['size_3000']:.3f} | "
              + " ".join(f"{key}: {p:.2f}" for key, p in row["power_3000"].items()))
        print(f"      exact 5 % (randomized at F = {row['randomized_c']:.3f}, gamma "
              f"{row['randomized_gamma']:.2f}) | "
              + " ".join(f"{key}: {p:.2f}" for key, p in row["power_randomized"].items()))
    print("\nTable 1.2's method repeated: 7 cells/event, 5 events, r = 2.5, one template "
          "(order_limit.json has 0.43 there)")
    rep = []
    for seed in range(100, 106):
        rng = np.random.default_rng(seed)
        null = np.array([ol.indicators(ol.simulate(N, 7, 5, 1, 0.0, SIGMA, rng), N)[0]
                         for _ in range(REPS)])
        thr = float(np.percentile(null, 95))
        v = np.array([ol.indicators(ol.simulate(N, 7, 5, 1, 2.5 * SIGMA, SIGMA, rng), N)[0]
                      for _ in range(REPS)])
        rep.append(dict(seed=seed, threshold=thr, size=float(np.mean(null > thr)),
                        power=float(np.mean(v > thr))))
        print(f"  seed {seed}: threshold {thr:.4f}, realized size {rep[-1]['size']:.3f}, "
              f"power {rep[-1]['power']:.2f}")
    (HERE / "order_power.json").write_text(json.dumps(
        dict(what="order detection power at small event counts; order_limit.py's simulate and "
                  "score sort", N=N, sigma_sec=SIGMA, reps=REPS, Es=ES, ks=KS, Ms=MS, rs=RS,
             rows=rows, table_1_2_repeats=rep), indent=1))
