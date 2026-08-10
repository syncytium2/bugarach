"""Peak-gated event selection — port of interface2's ``if2_peak_gate`` and the
subset of ``findpeaksTD`` it uses (local maxima + topographic prominence +
half-prominence extents; no height/threshold/distance/NPeaks options).

The extent machinery is a faithful port of MATLAB's
``signal.internal.findpeaks.findExtents`` stack algorithm, whose semantics
matter on real statistic traces (verified against MATLAB reference output in
tests/fixtures/ref_peak_gate.json):

- A flat-topped peak is reported at its LEFT edge; a rising staircase's
  shoulders are not peaks (they are not local maxima).
- NaN acts as a border: it resets the base scan, so a peak's prominence base
  never crosses a NaN.
- The prominence BASE extends to the nearest strictly-taller sample (through
  equal-height peaks); the SADDLE stops at the nearest equal-or-taller peak.
- The prominence gate is INCLUSIVE (prominence exactly P is kept).
- Half-prominence edges are linearly interpolated crossings of the reference
  line at ``peak - prominence/2``, walking outward from the peak but bounded
  by the SADDLE: if the line is not crossed before the saddle (typical
  between equal-height peaks), the edge clamps to the saddle sample.
- min-distance thinning is greedy tallest-first with a STABLE sort (equal
  peaks: the earlier one wins) and keeps peaks ``>= D`` samples apart.

All indices and fractional positions here are 0-BASED (MATLAB's are 1-based);
a caller converting to seconds uses ``t0 + idx * dt`` — identical values to
MATLAB's ``t0 + (idx - 1) * dt``.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class PeakGateResult:
    """K qualifying peaks, ascending in sample order (all arrays length K)."""

    idx: np.ndarray            # int, 0-based sample index of each peak
    val: np.ndarray            # S at the peak (read from the original trace)
    prominence: np.ndarray
    width_samples: np.ndarray  # half-prominence width (may be fractional)
    left_x: np.ndarray         # 0-based fractional position of the left edge
    right_x: np.ndarray        # 0-based fractional position of the right edge


def _skeleton(y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(peaks, inflections), 0-based, MATLAB findpeaks-style: NaN bookends,
    adjacent equal values collapse to their first sample (plateaus report
    their left edge), peaks where the derivative sign transitions + -> -,
    inflections at every sign change (peaks, valleys, NaN boundaries)."""
    yb = np.concatenate(([np.nan], y, [np.nan]))
    finite = ~np.isnan(yb)
    with np.errstate(invalid="ignore"):
        neq = (yb[:-1] != yb[1:]) & (finite[:-1] | finite[1:])
    i_temp = np.concatenate(([0], np.flatnonzero(neq) + 1))
    s = np.sign(np.diff(yb[i_temp]))
    with np.errstate(invalid="ignore"):
        i_max = np.flatnonzero(np.diff(s) < 0) + 1
    with np.errstate(invalid="ignore"):
        # NaN != NaN is True for both MATLAB and numpy — NaN runs transition
        i_any = np.flatnonzero(s[:-1] != s[1:]) + 1
    return i_temp[i_max] - 1, i_temp[i_any] - 1  # strip the leading bookend


def _left_bases(
    y: np.ndarray, i_peak: np.ndarray, i_inflect: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Per-peak (base_idx, saddle_idx) on the traversal side implied by the
    ordering of i_peak/i_inflect (pass reversed views for the right side).
    Port of findExtents>getLeftBase: a monotone stack of previously seen
    peaks merges valley minima; NaN resets the stack (border). The BASE
    valley extends past equal-height peaks, the SADDLE stops at them."""
    i_base = np.zeros(i_peak.size, dtype=int)
    i_saddle = np.zeros(i_peak.size, dtype=int)
    stack: list[tuple[float, float, int]] = []  # (peak_val, valley_val, valley_idx)
    v, iv = np.nan, 0
    i = k = 0
    while k < i_peak.size:
        while i_inflect[i] != i_peak[k]:
            v, iv = y[i_inflect[i]], i_inflect[i]
            if np.isnan(v):
                stack.clear()  # border seen, start over
            else:
                while stack and stack[-1][1] > v:
                    stack.pop()
            i += 1
        p = y[i_inflect[i]]
        while stack and stack[-1][0] < p:  # merge valleys of smaller peaks
            _, sv, si = stack.pop()
            if sv < v:
                v, iv = sv, si
        i_saddle[k] = iv                   # before crossing equal-height peaks
        while stack and stack[-1][0] <= p:  # extend base through equal peaks
            _, sv, si = stack.pop()
            if sv < v:
                v, iv = sv, si
        stack.append((p, v, iv))
        i_base[k] = iv
        i += 1
        k += 1
    return i_base, i_saddle


def _interp_edge(xa: int, xb: int, ya: float, yb: float, ref: float) -> float:
    """Fractional crossing of ref on the segment (xa, ya)-(xb, yb); ya <= ref."""
    if yb == ya:
        return float(xa)
    return xa + (xb - xa) * (ref - ya) / (yb - ya)


def find_peaks_halfprom(
    S: np.ndarray, min_prominence: float = 0.0
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Local maxima with topographic prominence and half-prominence extents.

    Returns (idx, prominence, left_x, right_x); the prominence gate keeps
    peaks with ``prominence >= min_prominence`` (inclusive, matching MATLAB).
    """
    S = np.asarray(S, dtype=float).ravel()
    peaks, inflect = _skeleton(S)
    if peaks.size == 0:
        z = np.empty(0)
        return np.empty(0, dtype=int), z.copy(), z.copy(), z.copy()

    lbase, lsaddle = _left_bases(S, peaks, inflect)
    rbase_r, rsaddle_r = _left_bases(S, peaks[::-1], inflect[::-1])
    rbase, rsaddle = rbase_r[::-1], rsaddle_r[::-1]

    prom_all = S[peaks] - np.maximum(S[lbase], S[rbase])
    keep = prom_all >= min_prominence
    peaks, prom = peaks[keep], prom_all[keep]
    lsad, rsad = lsaddle[keep], rsaddle[keep]

    lx = np.empty(peaks.size)
    rx = np.empty(peaks.size)
    for i, p in enumerate(peaks):
        ref = S[p] - 0.5 * prom[i]
        j = p
        while j >= lsad[i] and S[j] > ref:
            j -= 1
        lx[i] = float(lsad[i]) if j < lsad[i] else _interp_edge(j, j + 1, S[j], S[j + 1], ref)
        j = p
        while j <= rsad[i] and S[j] > ref:
            j += 1
        rx[i] = float(rsad[i]) if j > rsad[i] else _interp_edge(j, j - 1, S[j], S[j - 1], ref)
    return peaks, prom, lx, rx


def peak_gate(
    S,
    thr,
    *,
    prominence: float = 0.0,
    min_distance: int = 1,
    floor: float = -np.inf,
    strict_above: bool = True,
) -> PeakGateResult:
    """Peak-gated event selection on a coordination statistic trace.

    ``thr`` is a scalar or a per-sample vector (rolling theta(t)); a peak i
    qualifies iff ``S[i] > thr[i]`` (``>=`` when strict_above=False) and
    ``S[i] >= floor``. Survivors are thinned greedily tallest-first to
    ``>= min_distance`` samples apart, then emitted ascending in time.
    """
    S = np.asarray(S, dtype=float).ravel()
    n = S.size
    D = max(1, int(np.floor(min_distance + 0.5)))
    if n < 3 or not np.any(np.isfinite(S)):
        return _empty_result()

    thrv = np.asarray(thr, dtype=float).ravel()
    if thrv.size == 1:
        thrv = np.full(n, thrv[0])
    elif thrv.size != n:
        raise ValueError(f"thr must be scalar or length {n} (got {thrv.size})")

    idx, prom, lx, rx = find_peaks_halfprom(S, min_prominence=prominence)
    if idx.size == 0:
        return _empty_result()
    val = S[idx]

    th_at = thrv[idx]
    above = val > th_at if strict_above else val >= th_at
    keep = above & (val >= floor)
    idx, val, prom, lx, rx = idx[keep], val[keep], prom[keep], lx[keep], rx[keep]
    if idx.size == 0:
        return _empty_result()

    if D > 1 and idx.size > 1:
        order = np.argsort(-val, kind="stable")  # tallest first, earlier wins ties
        chosen = np.zeros(idx.size, dtype=bool)
        chosen_idx: list[int] = []
        for o in order:
            if not chosen_idx or all(abs(c - idx[o]) >= D for c in chosen_idx):
                chosen[o] = True
                chosen_idx.append(idx[o])
        idx, val, prom, lx, rx = idx[chosen], val[chosen], prom[chosen], lx[chosen], rx[chosen]

    order = np.argsort(idx, kind="stable")
    return PeakGateResult(
        idx=idx[order],
        val=val[order],
        prominence=prom[order],
        width_samples=(rx - lx)[order],
        left_x=lx[order],
        right_x=rx[order],
    )


def _empty_result() -> PeakGateResult:
    z = np.empty(0)
    return PeakGateResult(np.empty(0, dtype=int), z.copy(), z.copy(), z.copy(), z.copy(), z.copy())
