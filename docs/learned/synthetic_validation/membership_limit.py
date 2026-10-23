"""Aim 0, membership: assembled vs random participation as the number of assemblies grows.

Goal page: docs/goals/synthetic-validation.md, "Aim 0, membership and order". Synthetic only.
E events, each recruits k of N cells. Random: a fresh k-set per event. Assembled: M fixed k-sets,
each event picks one uniformly. Statistic: dispersion of pair co-occurrence counts across pairs,
D = var(n_ij) / mean(n_ij), against the random baseline. Prediction: D_asm / D_rand = 1 + (E-1)/M."""
import numpy as np
N, k, E, REPS = 33, 10, 45, 400
iu = np.triu_indices(N, 1)
def D(sets):
    X = np.zeros((len(sets), N))
    for e, s in enumerate(sets): X[e, s] = 1
    n = (X.T @ X)[iu]; return n.var() / n.mean()
rng = np.random.default_rng(0)
rand = np.mean([D([rng.choice(N, k, replace=False) for _ in range(E)]) for _ in range(REPS)])
print(f"N={N} cells, k={k} per event, E={E} events; random-membership D = {rand:.3f}")
print("  M assemblies | events per assembly | D_asm/D_rand measured | predicted 1+(E-1)/M")
for M in (1, 3, 10, 45, 150, 1000, 10000):
    v = []
    for _ in range(REPS):
        A = [rng.choice(N, k, replace=False) for _ in range(M)]
        v.append(D([A[i] for i in rng.integers(0, M, E)]))
    print(f"  {M:12d} | {E/M:19.2f} | {np.mean(v)/rand:21.2f} | {1+(E-1)/M:8.2f}")
