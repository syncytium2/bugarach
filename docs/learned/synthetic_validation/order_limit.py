"""Aim 0, order: a synfire-style order indicator, its closed forms, and what they do not cover.

Goal page: docs/goals/synthetic-validation.md, "Aim 0, membership and order". Synthetic only.
Revised after the murderboard of 2026-10-23 (docs/reviews/synthetic-validation-aim0_2026-10-23.md).

Model. Each source s has a latency template delta_si ~ N(0, s^2) over cells; an event from s
puts cell i at t0 + delta_si + N(0, sigma^2). Membership is random (k of N cells). Readout is
perfect: each event's participants and onsets are known, there is no background, and no
coincidence window is involved.

Statistic. For each pair, D_ij = sum over co-participations of sign(t_j - t_i). Cells are put
in an order, and F = sum over ordered pairs (i before j) of D_ij / sum of co-participations: net
agreement (agreeing minus disagreeing) as a share of all pair co-participations, 0 with no
order and 1 for a perfect sequence. The order is chosen two ways:

  * the SCORE sort: each cell's net lead count (a Borda / Copeland count), O(N^2), no search;
  * a LOCAL SEARCH from it (insertion moves until none improves F), standing in for the
    simulated annealing of tools/synfire_scan.py, which can only do as well or better.

This differs from SPIKE-order / the Synfire Indicator (Kreuz, Satuvuori, Pofahl & Mulansky 2017,
New J Phys 19:043028) in three ways: coincidences come from known events rather than ISI-adaptive
windows; the sort; and the normalisation, which there is by all spikes, coincident or not
(eq. 14), so background and non-participating spikes shrink it by a factor that varies with
participation and rate (murderboard role 6 measured 0.28 at 10 of 33 cells with no background,
less with it). None of the numbers below is PySpike's.

Predictions, tau = s / sigma:
  one template:   F = (2/pi) arctan(tau): the population Kendall tau between template and observed
                  latencies under a bivariate normal (Greiner's relation; Kruskal 1958).
  M templates:    the signal term F_M ~ sqrt(2/pi) * sqrt((2/pi) arcsin(tau^2 / (1 + tau^2))) / sqrt(M).
                  A finite run adds the no-order bias in quadrature: F ~ sqrt(F_M^2 + F_0^2).
  no order:       F_0 ~ c / sqrt(n_bar), n_bar = mean co-participations per pair. The 1/sqrt
                  scaling is the prediction; c is FITTED here, depends on N and k, and is larger
                  under a search than under the score sort. Kreuz et al. 2017 (sec. 3.1) already
                  note that the sorted indicator on order-free trains is a finite-size effect that
                  falls with the number of spikes.

    python docs/learned/synthetic_validation/order_limit.py
"""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent


def pair_matrices(events, N):
    n = np.zeros((N, N)); d = np.zeros((N, N))
    for cells, t in events:
        o = np.sign(t[None, :] - t[:, None])          # +1 where the row cell leads the column cell
        n[np.ix_(cells, cells)] += 1 - np.eye(len(cells))
        d[np.ix_(cells, cells)] += o
    return n, d


def f_of(order, n, d):
    iu = np.triu_indices(len(order), 1)
    return d[np.ix_(order, order)][iu].sum() / n[iu].sum()


def score_order(d):
    return np.argsort(-d.sum(1))


def local_search(order, d, max_pass=50):
    """Insertion moves: take a cell out and put it where it adds most, until nothing improves."""
    order = list(order)
    for _ in range(max_pass):
        improved = False
        for i in range(len(order)):
            c = order.pop(i)
            rest = np.array(order)
            # gain of inserting c at position p: sum_{j before p} d[j,c]... as leader over the rest
            lead = d[c, rest]                 # c before j adds d[c, j]
            follow = d[rest, c]               # j before c adds d[j, c]
            # value at position p = sum_{j<p} follow_j + sum_{j>=p} lead_j
            cf = np.concatenate([[0.0], np.cumsum(follow)])
            cl = np.concatenate([np.cumsum(lead[::-1])[::-1], [0.0]])
            p = int(np.argmax(cf + cl))
            order.insert(p, c)
            if p != i:
                improved = True
        if not improved:
            break
    return np.array(order)


def indicators(events, N):
    n, d = pair_matrices(events, N)
    o = score_order(d)
    return f_of(o, n, d), f_of(local_search(o, d), n, d), n


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


def nbar(N, k, E):
    return E * k * (k - 1) / (N * (N - 1))


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    N, k, sigma, REPS = 33, 10, 0.2, 40
    rec = dict(N=N, k=k, sigma_sec=sigma, one=[], none=[], many=[], c_by_field=[])
    print(f"one template, {N} cells, {k} per event, 200 events: F (score sort) vs (2/pi) arctan(s/sigma)")
    for s in (0.05, 0.1, 0.2, 0.5, 1.0):
        f = np.mean([indicators(simulate(N, k, 200, 1, s, sigma, rng), N)[0] for _ in range(REPS)])
        rec["one"].append(dict(tau=s / sigma, measured=f, predicted=pred_one(s / sigma)))
        print(f"  tau {s / sigma:5.2f}: measured {f:.3f}  predicted {pred_one(s / sigma):.3f}")
    print("\nno order: F * sqrt(n_bar) under the score sort and under the local search")
    for E in (25, 50, 100, 200, 400, 800):
        v = np.array([indicators(simulate(N, k, E, 1, 0.0, sigma, rng), N)[:2] for _ in range(REPS)])
        nb = nbar(N, k, E)
        rec["none"].append(dict(E=E, n_bar=nb, c_score=v[:, 0].mean() * np.sqrt(nb),
                                c_search=v[:, 1].mean() * np.sqrt(nb)))
        print(f"  {E:4d} events (n_bar {nb:5.1f}): c score {v[:, 0].mean() * np.sqrt(nb):.3f}, "
              f"c search {v[:, 1].mean() * np.sqrt(nb):.3f}")
    print("\nthe no-order constant c depends on the field: 400 events")
    for NN, kk in ((15, 5), (33, 5), (33, 10), (33, 20), (100, 10), (100, 30)):
        v = np.array([indicators(simulate(NN, kk, 400, 1, 0.0, sigma, rng), NN)[:2] for _ in range(20)])
        nb = nbar(NN, kk, 400)
        rec["c_by_field"].append(dict(N=NN, k=kk, c_score=v[:, 0].mean() * np.sqrt(nb),
                                      c_search=v[:, 1].mean() * np.sqrt(nb)))
        print(f"  {NN:3d} cells, {kk:2d} per event: c score {v[:, 0].mean() * np.sqrt(nb):.3f}, "
              f"c search {v[:, 1].mean() * np.sqrt(nb):.3f}")
    print("\nM templates, tau = 2.5, 2000 events: F (score sort) vs sqrt(F_M^2 + F_0^2), "
          "F_0 measured on the same run size")
    E = 2000
    f0 = np.mean([indicators(simulate(N, k, E, 1, 0.0, sigma, rng), N)[0] for _ in range(REPS)])
    for M in (1, 2, 4, 8, 16, 64, 256):
        f = np.mean([indicators(simulate(N, k, E, M, 0.5, sigma, rng), N)[0] for _ in range(REPS // 2)])
        fm = pred_one(2.5) if M == 1 else pred_many(2.5, M)
        p = fm if M == 1 else float(np.hypot(fm, f0))
        rec["many"].append(dict(M=M, measured=f, F_M=fm, F_0=f0, predicted=p))
        print(f"  M {M:4d}: measured {f:.3f}   F_M {fm:.3f}   predicted {p:.3f}")
    (HERE / "order_limit.json").write_text(json.dumps(rec, indent=1, default=float))
