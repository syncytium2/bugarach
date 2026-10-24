"""Aim 0, membership: assembled vs random participation as the number of assemblies grows.

Goal page: docs/goals/synthetic-validation.md, "Aim 0, membership". Synthetic only. Revised
after the murderboard of 2026-10-23/24, all four rounds (docs/reviews/synthetic-validation-aim0_2026-10-23.md).

Model. E coordinated events, each recruiting k of N cells (ROIs). Random participation: a fresh
k-set per event. Assembled: M fixed k-sets, drawn at random (so they may overlap), each event
picking one with equal probability. Readout is perfect: every member is seen and no background
cell joins. These are the assumptions; the result below holds under them only.

Statistic: the variance of the pair co-participation counts across cell pairs,
`bugarach.assembly.stat_dispersion` (called, not re-implemented). Its mean ratio to random
participation is predicted to be

    1 + (E - 1) * sum_m p_m^2        (= 1 + (E - 1)/M when the M assemblies are used equally)

because two events share an assembly with probability sum_m p_m^2. This has the form of the
survey-sampling design effect 1 + (m - 1) rho (Kish 1965; analogy, not checked against the book).
At fixed E it falls to 1 as 1/M; what sets it is the reuse E/M.

Detection is the package's own decision: for each simulated recording, both nulls
(`pvalues_margin`, `pvalues_uniform`) and both statistics, read by `AssemblyResult.verdict()`.
The power is the share of recordings called anything but "no-assembly"; the word breakdown is
kept because at M = 1 (a single saturated assembly) the margin null is blind by construction and
the verdict is "uniform-only" (see the `bugarach.assembly` module docstring).

    PYTHONPATH=src python docs/learned/synthetic_validation/membership_limit.py
"""
import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from bugarach.assembly import (AssemblyResult, membership_matrix, pvalues_margin,
                               pvalues_uniform, stat_dispersion)

HERE = Path(__file__).resolve().parent
N, k, E = 33, 10, 45
REPS_MEAN = 400          # recordings per point for the mean ratio
REPS_VERDICT = 60        # recordings per point for the package verdict
N_SURR = 200             # surrogates per null per recording
ALPHA = 0.05
MS = (1, 3, 10, 45, 150, 1000, 10000)


def sets_for(M, rng):
    if M is None:
        return [rng.choice(N, k, replace=False) for _ in range(E)]
    A = [rng.choice(N, k, replace=False) for _ in range(M)]
    return [A[i] for i in rng.integers(0, M, E)]


def verdict_one(args):
    M, seed = args
    rng = np.random.default_rng(seed)
    X = membership_matrix(sets_for(M, rng), N)
    rs = np.random.RandomState(seed)
    md, me = pvalues_margin(rs, X, N_SURR)
    ud, ue = pvalues_uniform(rs, X, N_SURR)
    r = AssemblyResult(min_rois=k, n_events=E, n_roi=N, defined=True,
                       p_margin_disp=md, p_margin_eig=me, p_uniform_disp=ud, p_uniform_eig=ue)
    return M, r.verdict(ALPHA)


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    rand = np.array([stat_dispersion(membership_matrix(sets_for(None, rng), N))
                     for _ in range(REPS_MEAN)])
    base = rand.mean()
    rows = []
    jobs = [(M, 10_000 * i + r) for i, M in enumerate((None,) + MS) for r in range(REPS_VERDICT)]
    with ProcessPoolExecutor(24) as ex:
        verdicts = list(ex.map(verdict_one, jobs))
    words = ("no-assembly", "uniform-only", "margin-only", "structure-beyond-rate")
    def tally(M):
        v = [w for m, w in verdicts if m == M]
        return {w: v.count(w) for w in words}, len(v)
    t0, n0 = tally(None)
    print(f"{N} cells, {k} per event, {E} events; verdict at alpha {ALPHA}, {N_SURR} surrogates per null")
    print(f"  random participation: {n0 - t0['no-assembly']}/{n0} flagged (the false-positive rate); {t0}")
    print("  assemblies M | reuse E/M | ratio measured (mean) | predicted 1+(E-1)/M | "
          "flagged by verdict | words")
    for M in MS:
        v = [stat_dispersion(membership_matrix(sets_for(M, rng), N)) for _ in range(REPS_MEAN)]
        r = np.array(v) / base
        t, n = tally(M)
        pred = 1 + (E - 1) / M
        flagged = (n - t["no-assembly"]) / n
        rows.append(dict(M=M, reuse=E / M, measured=float(r.mean()), predicted=pred,
                         flagged=flagged, verdicts=t, n=n))
        print(f"  {M:12d} | {E / M:9.3f} | {r.mean():21.2f} | {pred:19.2f} | {flagged:6.0%} | {t}")
    (HERE / "membership_limit.json").write_text(json.dumps(
        dict(N=N, k=k, E=E, reps_mean=REPS_MEAN, reps_verdict=REPS_VERDICT, n_surr=N_SURR,
             alpha=ALPHA, random_flagged=(n0 - t0["no-assembly"]) / n0, random_verdicts=t0,
             rows=rows), indent=1))
