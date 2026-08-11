"""Independent (adversary) implementation of find_peaks_halfprom.

Implemented solely from the behavioral specification
docs/clean_room/find_peaks_halfprom_spec.md (Revision 2). No
MATLAB/Octave/SciPy source or any other peak-finding implementation was
consulted.

Interpretation notes (where the spec left slack):

- "First local maximum whose value is >= V" for saddle truncation is taken
  to mean the such maximum NEAREST the peak in the walking direction
  (largest position on the left side, smallest on the right), consistent
  with the walk metaphor ("the truncated interval ends just before that
  maximum's position").
- A truncating maximum's "position" is its collapsed position (the FIRST
  index of its plateau run).  On the left side the truncated interval
  therefore still contains the tail samples of that plateau.
- Rev 2 saddle rule: runs of equal adjacent values are collapsed WITHIN the
  (possibly truncated) interval.  A run cut mid-run by an interval boundary
  (the truncating maximum's plateau tail on the left, or the peak's own
  plateau at p+1 on the right) contributes a candidate positioned at its
  leftmost sample INSIDE the interval.  This choice is observationally
  unreachable as a saddle: only value-V runs can be cut (interval endpoints
  at lb/rb sit against strictly greater samples), and the interval always
  contains a value strictly below V, so a cut run never holds the minimum.
"""

import numpy as np


def find_peaks_halfprom(S, min_prominence=0.0):
    """-> (idx, prominence, left_x, right_x), four 1-D numpy arrays"""
    S = np.asarray(S, dtype=float).ravel()
    n = S.size

    idx_out = []
    prom_out = []
    lx_out = []
    rx_out = []

    if n:
        good = ~np.isnan(S)
        start = 0
        while start < n:
            if not good[start]:
                start += 1
                continue
            stop = start
            while stop < n and good[stop]:
                stop += 1
            _segment_peaks(S, start, stop, min_prominence,
                           idx_out, prom_out, lx_out, rx_out)
            start = stop

    return (np.asarray(idx_out, dtype=np.int64),
            np.asarray(prom_out, dtype=float),
            np.asarray(lx_out, dtype=float),
            np.asarray(rx_out, dtype=float))


def _segment_peaks(S, s, e, min_prominence, idx_out, prom_out, lx_out, rx_out):
    """Process one maximal NaN-free run S[s:e] (all samples finite)."""
    # Collapse each run of equal adjacent values to its FIRST index.
    pos = [s]
    for k in range(s + 1, e):
        if S[k] != S[k - 1]:
            pos.append(k)

    # Local maxima among collapsed points; both neighbors must exist.
    maxima = []
    for t in range(1, len(pos) - 1):
        v = S[pos[t]]
        if v > S[pos[t - 1]] and v > S[pos[t + 1]]:
            maxima.append(pos[t])

    for p in maxima:
        V = S[p]

        # ---- Base intervals: walk outward through samples <= V ----------
        i = p - 1
        while i >= s and S[i] <= V:
            i -= 1
        lb = i + 1                        # left base interval = [lb, p-1]

        i = p + 1
        while i < e and S[i] <= V:
            i += 1
        rb = i - 1                        # right base interval = [p+1, rb]

        left_base = S[lb:p].min() if lb <= p - 1 else V
        right_base = S[p + 1:rb + 1].min() if p + 1 <= rb else V
        prom = V - max(left_base, right_base)

        if prom < min_prominence:         # inclusive gate: keep prom == gate
            continue

        # ---- Saddles ----------------------------------------------------
        # Left: truncate the base interval just before the nearest local
        # maximum with value >= V (only equal-height maxima can occur).
        lo = lb
        for q in reversed(maxima):        # descending => nearest-first
            if q <= p - 1 and q >= lb and S[q] >= V:
                lo = q + 1
                break
        # Rev 2: collapse equal-adjacent runs within [lo, p-1]; each run's
        # candidate position is its FIRST (leftmost) index in the interval.
        # Ties between DISTINCT runs resolve to the run nearest the peak
        # (largest run position on the left side) -> '<=' keeps later runs.
        sadl = lo
        for k in range(lo + 1, p):
            if S[k] != S[k - 1] and S[k] <= S[sadl]:
                sadl = k

        hi = rb
        for q in maxima:                  # ascending => nearest-first
            if q >= p + 1 and q <= rb and S[q] >= V:
                hi = q - 1
                break
        # Same run collapse within [p+1, hi]; positions are still each run's
        # LEFTMOST index, and the nearest run on the right is the one with
        # the smallest position -> strict '<' keeps earlier runs on ties.
        sadr = p + 1
        for k in range(p + 2, hi + 1):
            if S[k] != S[k - 1] and S[k] < S[sadr]:
                sadr = k

        # ---- Half-prominence extents ------------------------------------
        ref = V - prom / 2.0

        lx = None
        j = p - 1
        while j >= sadl:
            if S[j] <= ref:
                lx = j + (ref - S[j]) / (S[j + 1] - S[j])
                break
            j -= 1
        if lx is None:
            lx = float(sadl)              # clamp: everything > ref down to saddle

        rx = None
        j = p + 1
        while j <= sadr:
            if S[j] <= ref:
                rx = j - (ref - S[j]) / (S[j - 1] - S[j])
                break
            j += 1
        if rx is None:
            rx = float(sadr)

        idx_out.append(p)
        prom_out.append(prom)
        lx_out.append(lx)
        rx_out.append(rx)
