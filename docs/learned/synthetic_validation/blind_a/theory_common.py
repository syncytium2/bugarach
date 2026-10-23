"""Shared helpers: load the Aim 1a record, group rows, and the window-capture integrals."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
REC = HERE.parent / "docs/learned/synthetic_validation/aim1_one_source.json"
DT = 0.1
N, T = 33, 2700.0


def load():
    return json.loads(REC.read_text())["rows"]


def kpart(f, n=N):
    return max(1, int(np.floor(f * n + 0.5)))


def bin_probs(w, sigma, n_phase=400, dt=DT):
    """For an event at uniform phase within a w-second window grid, the probability vector over
    windows of ONE participant's (quantized-to-dt) onset, for each phase. Returns (n_phase, n_bins)."""
    wf = int(round(w / dt))
    half = int(np.ceil((6 * sigma + w) / dt)) + 2
    out = []
    for u in (np.arange(n_phase) + 0.5) / n_phase * w:      # event time within its window
        j = np.arange(-half, half + 1) + int(round(u / dt))   # frame indices
        if sigma > 0:
            q = norm.cdf(((j + 0.5) * dt - u) / sigma) - norm.cdf(((j - 0.5) * dt - u) / sigma)
        else:
            q = (j == int(np.floor(u / dt + 0.5))).astype(float)
        b = np.floor_divide(j, wf)
        bb = b - b.min()
        out.append(np.bincount(bb, weights=q))
    L = max(len(o) for o in out)
    return np.array([np.pad(o, (0, L - len(o))) for o in out])


def capture(w, sigma):
    """P2 = P(two participants share a window), P3 = P(three do)."""
    p = bin_probs(w, sigma)
    return float((p ** 2).sum(1).mean()), float((p ** 3).sum(1).mean())
