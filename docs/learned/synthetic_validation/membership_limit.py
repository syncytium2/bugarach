"""Aim 0, membership: assembled vs random participation as the number of assemblies grows.

Goal page: docs/goals/synthetic-validation.md, "Aim 0, membership and order". Synthetic only.
Revised after the murderboard of 2026-10-23 (docs/reviews/synthetic-validation-aim0_2026-10-23.md).

Model. E coordinated events, each recruiting k of N cells. Random participation: a fresh k-set
per event. Assembled: M fixed k-sets (drawn at random, so they may overlap), each event picking
one uniformly. Readout is perfect: every member is seen and no background cell joins.

Statistic: the variance of the pair co-participation counts across cell pairs, which is
`bugarach.assembly.stat_dispersion` (called here, not re-implemented). Its ratio to random
participation is predicted to be

    1 + (E - 1) / M

because two events share an assembly with probability 1/M; it is the survey-sampling design
effect 1 + (m - 1) rho with intraclass correlation rho = 1/M (Kish 1965; not re-checked here).
At fixed E it falls to 1 as 1/M; what sets it is the reuse E/M.

The mean is not the whole answer for one recording, so the script also reports how often a single
recording's ratio exceeds the 95th percentile of random participation (5 % is chance).
For tools/assembly_power.py's model (one assembly recruited in a `strength` fraction of events)
M = 1 corresponds to strength 1.

    PYTHONPATH=src python docs/learned/synthetic_validation/membership_limit.py
"""
import json
from pathlib import Path

import numpy as np

from bugarach.assembly import membership_matrix, stat_dispersion

HERE = Path(__file__).resolve().parent
N, k, E, REPS = 33, 10, 45, 400


def disp(sets):
    return stat_dispersion(membership_matrix(sets, N))


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    rand = np.array([disp([rng.choice(N, k, replace=False) for _ in range(E)]) for _ in range(REPS)])
    base = rand.mean()
    p95 = np.percentile(rand / base, 95)
    sd_rand = (rand / base).std()
    print(f"{N} cells, {k} per event, {E} events. Random participation: ratio SD {sd_rand:.3f} "
          f"per recording, 95th percentile {p95:.3f}")
    print("  assemblies M | reuse E/M | ratio measured (mean) | predicted 1+(E-1)/M | "
          "recordings above the random 95th percentile")
    rows = []
    for M in (1, 3, 10, 45, 150, 1000, 10000):
        v = []
        for _ in range(REPS):
            A = [rng.choice(N, k, replace=False) for _ in range(M)]
            v.append(disp([A[i] for i in rng.integers(0, M, E)]))
        r = np.array(v) / base
        pred = 1 + (E - 1) / M
        rows.append(dict(M=M, reuse=E / M, measured=float(r.mean()), predicted=pred,
                         detected=float(np.mean(r > p95))))
        print(f"  {M:12d} | {E / M:9.2f} | {r.mean():21.2f} | {pred:19.2f} | {np.mean(r > p95):6.0%}")
    (HERE / "membership_limit.json").write_text(json.dumps(
        dict(N=N, k=k, E=E, reps=REPS, random_sd=float(sd_rand), random_p95=float(p95), rows=rows),
        indent=1))
