"""Pattern jitter on integer frame indices (Harrison & Geman 2009, fixed partition).

Implemented solely from ``docs/clean_room/pattern_jitter_spec.md`` (revision 1);
no paper, published code or other resampling implementation was consulted. Where
the method's original description and the spec differ -- the partition anchored at
the generation window's start, the first and last onsets held fixed, the pinned
random-number protocol, exact integer arithmetic -- the spec is followed.

One ROI's onsets are split into rigid **patterns**: an onset whose interval from
its predecessor is ``R`` frames or less belongs to its predecessor's pattern. The
first and last patterns stay where they are; every other pattern's start is
re-placed inside the fixed ``L``-frame jitter block that held it, subject to each
pattern starting more than ``R`` frames after the previous pattern ends. Among all
such trains one is drawn uniformly, exactly: a backward pass counts completions in
Python integers (the counts overflow int64 and float64 on long trains), and a
forward pass draws each free pattern's start with one ``rng.random_sample()`` and
a strict integer comparison, so two implementations given the same ``rng`` return
identical trains.

``pattern_jitter_count`` returns the number of valid resamplings; ``1`` means the
train cannot move at all, as opposed to a draw that happened not to move it.
Converting the screen's jitter radius and dead time to ``L`` and ``R`` is the
caller's job (``bugarach.surrogates``).
"""

from __future__ import annotations

from bisect import bisect_right
from collections import OrderedDict
from itertools import accumulate

import numpy as np

__all__ = ["pattern_jitter", "pattern_jitter_count"]

_TWO53 = 1 << 53

# Count tables depend on (train, start, L, R) only, never on rng, so the screen's
# K draws of one ROI share a single backward pass. Small LRU; entries are immutable.
_CACHE: "OrderedDict[tuple, _Tables]" = OrderedDict()
_CACHE_MAX = 512


def _is_int(v) -> bool:
    """A Python int or numpy integer, and not a bool (numpy's bool is not np.integer)."""
    return isinstance(v, (int, np.integer)) and not isinstance(v, bool)


def _validate(train, window, L, R):
    """Check every argument; return (onsets as a list of Python ints, start)."""
    x = np.asarray(train)
    if x.ndim != 1:
        raise ValueError(f"train must be 1-D, got {x.ndim}-D")
    if x.size and x.dtype.kind not in "iu":
        raise ValueError(f"train must hold integer frame indices, got dtype {x.dtype}")
    if x.size > 1 and bool(np.any(x[1:] < x[:-1])):
        raise ValueError("train must be non-decreasing")
    try:
        start, end = window
    except (TypeError, ValueError):
        raise ValueError("window must be a (start, end) pair") from None
    if not (_is_int(start) and _is_int(end)):
        raise ValueError("window bounds must be integers")
    start, end = int(start), int(end)
    if start > end:
        raise ValueError(f"window start {start} is after its end {end}")
    for name, v in (("L", L), ("R", R)):
        if not _is_int(v):
            raise ValueError(f"{name} must be an integer, got {type(v).__name__}")
    if L < 1:
        raise ValueError(f"L must be >= 1, got {L}")
    if R < 0:
        raise ValueError(f"R must be >= 0, got {R}")
    onsets = [int(v) for v in x.tolist()] if x.size else []
    if onsets and (onsets[0] < start or onsets[-1] >= end):
        raise ValueError(f"every onset must lie in [{start}, {end})")
    return onsets, start


class _Tables:
    """The pattern structure and the backward pass's count tables for one input."""

    __slots__ = ("heads", "lengths", "gaps", "lo", "prefix", "count")

    def __init__(self, onsets, start, L, R):
        n = len(onsets)
        heads = [0]  # index of each pattern's first onset
        for i in range(1, n):
            if onsets[i] - onsets[i - 1] > R:
                heads.append(i)
        d = len(heads)
        ends = heads[1:] + [n]  # one past each pattern's last onset
        self.heads = heads
        self.lengths = [e - h for h, e in zip(heads, ends)]
        # G_p = span_p + R + 1: least distance from pattern p's start to pattern p+1's.
        self.gaps = [onsets[e - 1] - onsets[h] + R + 1 for h, e in zip(heads, ends)]

        # Allowed starts A_p as a contiguous range lo[p] .. lo[p] + size[p] - 1.
        lo, size = [], []
        for p, h in enumerate(heads):
            s = onsets[h]
            if p == 0 or p == d - 1:
                lo.append(s)
                size.append(1)
            else:
                lo.append(start + L * ((s - start) // L))
                size.append(L)
        self.lo = lo

        # Backward pass. prefix[p][j] = N_p(lo_p) + ... + N_p(lo_p + j - 1); only the
        # free patterns' prefixes are kept, since only they are sampled.
        prefix = [None] * d
        counts = [1]  # N_{d-1}
        for p in range(d - 2, -1, -1):
            nxt = counts
            # suffix[j] = sum of N_{p+1} over its entries j..end; suffix[len] = 0.
            suffix = list(accumulate(reversed(nxt)))[::-1] + [0]
            m = len(suffix)
            # N_p(lo_p + i) = suffix[j0 + i], clamped: below 0 means every entry of
            # A_{p+1} is reachable (suffix[0]); at or past m - 1 means none is (0).
            j0 = lo[p] + self.gaps[p] - lo[p + 1]
            sp = size[p]
            n_all = min(sp, max(0, -j0))
            a = max(j0, 0)
            b = min(j0 + sp, m)
            middle = suffix[a:b] if b > a else []
            n_none = sp - n_all - len(middle)
            counts = [suffix[0]] * n_all + middle + [0] * n_none
            if 0 < p < d - 1:
                prefix[p] = [0] + list(accumulate(counts))
        self.prefix = prefix
        self.count = counts[0] if n else 1


def _tables(onsets, start, L, R) -> _Tables:
    key = (tuple(onsets), start, int(L), int(R))
    hit = _CACHE.get(key)
    if hit is not None:
        _CACHE.move_to_end(key)
        return hit
    tab = _Tables(onsets, start, int(L), int(R))
    _CACHE[key] = tab
    if len(_CACHE) > _CACHE_MAX:
        _CACHE.popitem(last=False)
    return tab


def pattern_jitter_count(train, window, L, R) -> int:
    """Number of valid resamplings of ``train`` (an exact Python int, >= 1).

    ``1`` exactly when the input is its own only valid resampling.
    """
    onsets, start = _validate(train, window, L, R)
    if not onsets:
        return 1
    return _tables(onsets, start, L, R).count


def pattern_jitter(train, window, L, R, rng):
    """Draw one pattern-jittered copy of ``train`` uniformly from its valid resamplings.

    Parameters
    ----------
    train : 1-D array-like of int
        Non-decreasing frame indices of one ROI, all in ``[window[0], window[1])``.
    window : (int, int)
        Half-open generation window; its start anchors the ``L``-frame jitter blocks.
    L : int
        Jitter-block length in frames, ``>= 1``.
    R : int
        History length in frames, ``>= 0``: intervals of ``R`` or less are kept
        exactly, longer ones stay longer than ``R``.
    rng : object with ``random_sample()``
        In practice ``numpy.random.RandomState``. Called exactly once per free
        pattern, in pattern order, and never otherwise.

    Returns
    -------
    numpy.ndarray of int64
        A new array, the same length as ``train``; the input is not modified.
    """
    onsets, start = _validate(train, window, L, R)
    n = len(onsets)
    if n == 0:
        return np.empty(0, dtype=np.int64)
    tab = _tables(onsets, start, L, R)
    heads, gaps, lo, prefix = tab.heads, tab.gaps, tab.lo, tab.prefix
    d = len(heads)

    starts = [onsets[heads[0]]]  # W_0
    for p in range(1, d - 1):  # the free patterns, in order
        floor = starts[p - 1] + gaps[p - 1]
        P = prefix[p]
        size = len(P) - 1
        j0 = min(max(floor - lo[p], 0), size)  # first candidate >= floor
        total = P[size] - P[j0]  # T
        u = rng.random_sample()
        k = int(float(u) * _TWO53)
        if not 0 <= k < _TWO53:
            raise ValueError(f"rng.random_sample() returned {u!r}, outside [0, 1)")
        if total < 1:  # unreachable for a valid input; guards the invariant
            raise RuntimeError("pattern_jitter: no valid start for a free pattern")
        # Smallest r with 2**53 * C_r > k * T, C_r = P[j0 + r] - P[j0]. For an
        # integer C this is C > floor(k * T / 2**53), so bisect the prefix sums.
        threshold = P[j0] + ((k * total) >> 53)
        i = bisect_right(P, threshold, j0 + 1, size + 1)
        starts.append(lo[p] + i - 1)
    if d >= 2:
        starts.append(onsets[heads[d - 1]])

    x = np.array(onsets, dtype=np.int64)
    shifts = np.array([w - onsets[h] for w, h in zip(starts, heads)], dtype=np.int64)
    return x + np.repeat(shifts, tab.lengths)
