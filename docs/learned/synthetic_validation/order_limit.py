"""Aim 0, order: a synfire-style indicator predicted, not optimised (Tony, 2026-10-23).

Model. Each source s has a latency template delta_si ~ N(0, s^2) over cells; an event from s
puts cell i at t0 + delta_si + N(0, sigma^2). Membership is random (k of N), so this isolates
order. Perfect readout: each event's participants and onsets are known.

Statistic, in the spirit of SPIKE-order (Kreuz et al. 2017): D_ij = mean over co-participations
of sign(t_j - t_i); cells sorted from leader to follower; F = sum over ordered pairs of
n_ij D_ij / sum n_ij. Here the sort is the score s_i = sum_j n_ij D_ij (a Borda count), which
is O(N^2) and deterministic, instead of simulated annealing over N! orders.

Predictions, with tau = s / sigma:
  one template:            F = (2/pi) arctan(tau)
  M independent templates: F ~ sqrt(2/pi) * sqrt((2/pi) arcsin(tau^2/(1+tau^2))) / sqrt(M)
  no order (any M):        F ~ c / sqrt(n_bar), n_bar = mean co-participations per pair
                           (the optimisation's own bias; it is why the indicator falls with
                           event count in the real recordings)

    python docs/learned/synthetic_validation/order_limit.py
"""
import numpy as np


def indicator(events, N):
    """events: list of (cells, onsets). Returns F under the score sort."""
    n = np.zeros((N, N)); d = np.zeros((N, N))
    for cells, t in events:
        o = np.sign(t[None, :] - t[:, None])          # +1 where row leads column
        n[np.ix_(cells, cells)] += 1 - np.eye(len(cells))
        d[np.ix_(cells, cells)] += o
    order = np.argsort(-d.sum(1))                       # leaders first
    iu = np.triu_indices(N, 1)
    dd = d[np.ix_(order, order)][iu]
    return dd.sum() / n[iu].sum()


def simulate(N, k, E, M, s, sigma, rng):
    tmpl = rng.normal(0, s, (M, N)) if s > 0 else np.zeros((M, N))
    ev = []
    for _ in range(E):
        src = rng.integers(M); cells = rng.choice(N, k, replace=False)
        ev.append((cells, tmpl[src, cells] + rng.normal(0, sigma, k)))
    return ev


def pred_one(tau):
    return 2 / np.pi * np.arctan(tau)


def pred_many(tau, M):
    return np.sqrt(2 / np.pi) * np.sqrt(2 / np.pi * np.arcsin(tau ** 2 / (1 + tau ** 2))) / np.sqrt(M)


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    N, k, sigma, REPS = 33, 10, 0.2, 60
    print("one template, E = 200 events: F measured vs (2/pi) arctan(s/sigma)")
    for s in (0.05, 0.1, 0.2, 0.5, 1.0):
        f = np.mean([indicator(simulate(N, k, 200, 1, s, sigma, rng), N) for _ in range(REPS)])
        print(f"  s/sigma {s / sigma:5.2f}: {f:.3f}  predicted {pred_one(s / sigma):.3f}")
    print("\nno order (s = 0): the optimisation's bias against co-participations per pair")
    for E in (25, 50, 100, 200, 400, 800):
        f = np.mean([indicator(simulate(N, k, E, 1, 0.0, sigma, rng), N) for _ in range(REPS)])
        nbar = E * k * (k - 1) / (N * (N - 1))
        print(f"  E {E:4d} (n_bar {nbar:5.1f}): F {f:.3f}   F * sqrt(n_bar) = {f * np.sqrt(nbar):.3f}")
    print("\nM templates, s/sigma = 2.5, E = 2000 events: F measured vs prediction (+ no-order bias)")
    E = 2000; nbar = E * k * (k - 1) / (N * (N - 1))
    bias = np.mean([indicator(simulate(N, k, E, 1, 0.0, sigma, rng), N) for _ in range(REPS)])
    for M in (1, 2, 4, 8, 16, 64, 256):
        f = np.mean([indicator(simulate(N, k, E, M, 0.5, sigma, rng), N) for _ in range(REPS // 2)])
        p = pred_one(2.5) if M == 1 else np.hypot(pred_many(2.5, M), bias)
        print(f"  M {M:4d}: F {f:.3f}   predicted {p:.3f}")
