"""Peak-gated event selection — port of interface2's ``if2_peak_gate`` plus
the peak-extent kernel it needs (local maxima + topographic prominence +
half-prominence extents).

The extent kernel reproduces MATLAB findpeaks' OBSERVABLE half-prominence
semantics, as pinned by MATLAB-generated reference fixtures
(tests/fixtures/ref_peak_gate.json and the detector parity suites):

- A flat-topped peak is reported at its LEFT edge; a rising staircase's
  shoulders are not peaks (they are not local maxima).
- NaN acts as a border: signals split into segments nothing crosses.
- The prominence BASE extends to the nearest strictly-taller sample
  (through equal-height peaks); the prominence gate is INCLUSIVE.
- Half-prominence edges are linearly interpolated crossings of the
  reference line at ``peak - prominence/2``, walking outward from the peak
  but bounded by the SADDLE — the minimum-valued run between the peak and
  the nearest equal-or-taller peak (run positions collapse to their first
  index; equal-depth run ties resolve nearest the peak) — clamping there
  when the line is never crossed (typical between equal-height peaks).

Provenance: the kernel is a CLEAN-ROOM implementation, written solely from
the behavioral specification in docs/clean_room/find_peaks_halfprom_spec.md
by an independent session with no access to MATLAB, this repository, or any
existing peak-finder source, and accepted after passing the full
MATLAB-parity suite plus a 20k-case fuzz against the reference behavior.

``peak_gate`` itself (threshold/floor gating + min-distance thinning) is a
port of interface2's if2_peak_gate: gating uses a scalar or per-sample
threshold with strict/non-strict comparison on the ORIGINAL trace values,
and thinning is greedy tallest-first with a STABLE sort (equal peaks: the
earlier one wins), keeping peaks ``>= D`` samples apart.

All indices and fractional positions are 0-BASED (MATLAB's are 1-based); a
caller converting to seconds uses ``t0 + idx * dt`` — identical values to
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


# ---------------------------------------------------------------------------
# Peak-extent kernel — clean-room implementation (see module docstring).
# Implemented solely from docs/clean_room/find_peaks_halfprom_spec.md.
# ---------------------------------------------------------------------------

def _collapsed_maxima(S, a, b):
    """Local maxima of the segment S[a:b] (no NaNs inside), as absolute indices.

    Runs of equal adjacent values collapse to their first index, so a
    flat-topped peak reports at the left edge of its plateau. Segment
    endpoints are never maxima.
    """
    pts = [a]
    for k in range(a + 1, b):
        if S[k] != S[k - 1]:
            pts.append(k)
    maxima = []
    for t in range(1, len(pts) - 1):
        v = S[pts[t]]
        if v > S[pts[t - 1]] and v > S[pts[t + 1]]:
            maxima.append(pts[t])
    return maxima


def _side(S, a, b, p, V, maxima, left):
    """Base value and saddle index for one side of the peak at p.

    The base interval walks away from p through samples <= V, stopping
    before the first sample > V, the segment edge, or (implicitly) a NaN.
    The base value is the interval's minimum. For the saddle, the interval
    is truncated just before the first equal-or-higher local maximum
    encountered walking outward, then equal-value runs collapse to their
    first (leftmost) index; the saddle is the position of the
    minimum-valued run, ties between distinct runs resolving to the run
    nearest the peak.
    """
    if left:
        i = p - 1
        while i >= a and S[i] <= V:
            i -= 1
        lo, hi = i + 1, p - 1
    else:
        i = p + 1
        while i < b and S[i] <= V:
            i += 1
        lo, hi = p + 1, i - 1
    if lo > hi:
        return V, p

    base = float(np.min(S[lo:hi + 1]))

    tlo, thi = lo, hi
    if left:
        for m in reversed(maxima):
            if lo <= m <= hi and S[m] >= V:
                tlo = m + 1
                break
    else:
        for m in maxima:
            if lo <= m <= hi and S[m] >= V:
                thi = m - 1
                break
    if tlo > thi:
        tlo, thi = lo, hi

    starts = [tlo] + [k for k in range(tlo + 1, thi + 1) if S[k] != S[k - 1]]
    mn = min(S[r] for r in starts)
    cands = [r for r in starts if S[r] == mn]
    saddle = max(cands) if left else min(cands)
    return base, saddle


def find_peaks_halfprom(
    S, min_prominence: float = 0.0
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """-> (idx, prominence, left_x, right_x), four 1-D numpy arrays.

    idx: 0-based sample index of each qualifying peak, ascending.
    prominence: peak height above the higher of its two base minima.
    left_x, right_x: fractional sample positions of the half-prominence
    extent, clamped at the side's saddle when no crossing occurs.
    A peak qualifies iff prominence >= min_prominence (inclusive). NaNs
    split the signal into segments that nothing crosses.
    """
    S = np.asarray(S, dtype=float).ravel()
    n = S.size
    idx_o, prom_o, lx_o, rx_o = [], [], [], []

    a = 0
    while a < n:
        if np.isnan(S[a]):
            a += 1
            continue
        b = a
        while b < n and not np.isnan(S[b]):
            b += 1

        maxima = _collapsed_maxima(S, a, b)
        for p in maxima:
            V = S[p]
            lbase, lsad = _side(S, a, b, p, V, maxima, True)
            rbase, rsad = _side(S, a, b, p, V, maxima, False)
            prom = V - max(lbase, rbase)
            if prom < min_prominence:
                continue
            ref = V - prom / 2.0

            lx = None
            j = p - 1
            while j >= lsad:
                if S[j] <= ref:
                    if S[j] == ref:
                        lx = float(j)
                    else:
                        lx = j + (ref - S[j]) / (S[j + 1] - S[j])
                    break
                j -= 1
            if lx is None:
                lx = float(lsad)

            rx = None
            j = p + 1
            while j <= rsad:
                if S[j] <= ref:
                    if S[j] == ref:
                        rx = float(j)
                    else:
                        rx = j - (ref - S[j]) / (S[j - 1] - S[j])
                    break
                j += 1
            if rx is None:
                rx = float(rsad)

            idx_o.append(p)
            prom_o.append(prom)
            lx_o.append(lx)
            rx_o.append(rx)
        a = b

    return (np.asarray(idx_o, dtype=np.int64),
            np.asarray(prom_o, dtype=float),
            np.asarray(lx_o, dtype=float),
            np.asarray(rx_o, dtype=float))


# ---------------------------------------------------------------------------
# if2_peak_gate port (interface2's own code)
# ---------------------------------------------------------------------------

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
