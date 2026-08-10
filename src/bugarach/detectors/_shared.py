"""MATLAB-semantics helpers shared by the detector ports.

CoactDetect and LoCo share the circular-shift surrogate machinery; every
detector shares MATLAB's colon/round conventions. Each helper here replicates
the exact MATLAB behavior the ports were parity-tested against — do not
"fix" them toward numpy conventions.
"""

from __future__ import annotations

import numpy as np


def matlab_colon(lo: float, step: float, hi: float) -> np.ndarray:
    """lo:step:hi with MATLAB's exact element values: the first half is
    computed forward (lo + k*step), the second half BACKWARD from the
    endpoint (Cleve Moler's two-ended colonop — verified element-for-element
    against MATLAB R2025b). The endpoint snaps to hi when (hi-lo) is a
    multiple of step within roundoff. A plain forward grid differs from
    MATLAB in the last ulp for ~1/4 of the elements, which flips
    strict/abs-comparison bin assignments downstream."""
    q = (hi - lo) / step
    n = int(np.floor(q * (1.0 + 4.0 * np.finfo(float).eps))) + 1
    if n < 1:
        return np.empty(0)
    k = np.arange(n)
    fwd = lo + k * step
    tol = 4.0 * np.spacing(max(abs(lo), abs(hi)))
    end_val = hi if abs(fwd[-1] - hi) <= tol else fwd[-1]
    bwd = end_val - (n - 1 - k) * step
    mid = n // 2
    return np.concatenate((fwd[:mid], bwd[mid:]))


def matlab_round(x: float) -> int:
    """MATLAB round: half away from zero (for non-negative x)."""
    return int(np.floor(x + 0.5))


def matlab_prctile(x: np.ndarray, p: float) -> float:
    """MATLAB prctile: sorted sample i sits at percentile 100*(i-0.5)/n,
    linear interpolation between, clamped at the extremes. This differs from
    every numpy.percentile interpolation mode."""
    x = np.sort(np.asarray(x, dtype=float).ravel())
    n = x.size
    if n == 0:
        return np.nan
    q = (np.arange(1, n + 1) - 0.5) * (100.0 / n)
    return float(np.interp(p, q, x))


def discretize(v: np.ndarray, edges: np.ndarray) -> np.ndarray:
    """MATLAB discretize: bin i covers [edges[i], edges[i+1]), the last bin is
    closed on the right; values outside [edges[0], edges[-1]] get -1 (MATLAB
    NaN). Returns 0-based bin indices."""
    v = np.asarray(v, dtype=float)
    idx = np.searchsorted(edges, v, side="right") - 1
    idx[v == edges[-1]] = edges.size - 2
    idx[(v < edges[0]) | (v > edges[-1])] = -1
    return idx


def distinct_coact(evs: list[np.ndarray], edges: np.ndarray) -> np.ndarray:
    """Distinct active ROIs per bin (one count per ROI per bin), discretize
    binning — LoCo's coactivity statistic (detect_loco>local_coact)."""
    nb = edges.size - 1
    c = np.zeros(nb)
    for v in evs:
        if v.size == 0:
            continue
        idx = discretize(v, edges)
        idx = idx[idx >= 0]
        if idx.size:
            c[np.unique(idx)] += 1
    return c


def clip_sorted(trains: list[np.ndarray], lo: float, hi: float) -> list[np.ndarray]:
    """Per-ROI finite onsets within [lo, hi], sorted (shared train prep)."""
    out = []
    for v in trains:
        v = np.asarray(v, dtype=float).ravel()
        v = v[np.isfinite(v)]
        out.append(np.sort(v[(v >= lo) & (v <= hi)]))
    return out
