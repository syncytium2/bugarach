"""Adversary implementation of pattern_jitter, written from
docs/clean_room/pattern_jitter_spec.md (revision 1) ALONE.

The primary, src/bugarach/pattern_jitter.py, was never read by the author of this file. It
exists so the differential fuzzer (fuzz.py) has an independent second implementation to hold
the primary against, per docs/clean_room/WORKFLOW.md.

The module also exposes the pieces the harness needs beyond the two public functions: the
pattern decomposition, the count tables and exact marginals (for the large-train distribution
test), and a ``Variant`` class whose flags switch on deliberate defects, used by mutants.py.
Only numpy and the standard library are used.
"""

import numbers

import numpy as np

TWO53 = 1 << 53


def _is_int(v):
    if isinstance(v, (bool, np.bool_)):
        return False
    return isinstance(v, (numbers.Integral, np.integer))


def validate(train, window, L, R):
    """Return (list of python-int onsets, start, end, L, R) or raise ValueError."""
    x = np.asarray(train)
    if x.ndim != 1:
        raise ValueError("train must be 1-D")
    if x.size and x.dtype.kind not in "iu":
        raise ValueError("train must hold integers")
    if not _is_int(L) or not _is_int(R):
        raise ValueError("L and R must be integers")
    L, R = int(L), int(R)
    if L < 1:
        raise ValueError("L must be >= 1")
    if R < 0:
        raise ValueError("R must be >= 0")
    start, end = window
    start, end = int(start), int(end)
    if start > end:
        raise ValueError("window start after end")
    xs = [int(v) for v in x.tolist()]
    for i in range(1, len(xs)):
        if xs[i] < xs[i - 1]:
            raise ValueError("train decreases")
    for v in xs:
        if v < start or v >= end:
            raise ValueError("onset outside window")
    return xs, start, end, L, R


class Variant:
    """The adversary's sampler. With every flag off it is the specified algorithm; each flag
    switches on one deliberate defect (see mutants.py)."""

    FLAGS = (
        "split_at_R",          # a new pattern starts when the interval is >= R (not > R)
        "gap_minus_one",       # G = span + R: 'at least R' read for 'longer than R'
        "gap_no_span",         # G = R + 1, the span forgotten
        "gap_next_span",       # G uses the NEXT pattern's span (indexing slip)
        "centred",             # window centred on the original start
        "anchor_zero",         # partition anchored at frame 0, not at start
        "block_plus_one",      # a block holds L + 1 frames
        "clip_to_block",       # later onsets of a pattern clipped into the start's block
        "last_free",           # the last pattern is free too
        "first_free",          # the first pattern is free too
        "uniform_open",        # uniform over open candidates with a completion, not weighted
        "select_ge",           # >= in the selection rule
        "skip_single_draw",    # no draw when the candidate list has one member
        "float_rule",          # float counts, pick first C_r/T > u
        "descending",          # candidates walked in descending order
        "R_plus_one",          # history length R + 1 used throughout
    )

    def __init__(self, **flags):
        bad = set(flags) - set(self.FLAGS)
        if bad:
            raise TypeError(f"unknown flags {bad}")
        self.f = {k: bool(flags.get(k, False)) for k in self.FLAGS}

    # -- structure ---------------------------------------------------------------------------
    def patterns(self, xs, R):
        """List of (a, b) inclusive onset index ranges, one per pattern, in time order."""
        if self.f["R_plus_one"]:
            R = R + 1
        pats = []
        for i, v in enumerate(xs):
            gap = v - xs[i - 1] if i else None
            new = i == 0 or (gap >= R if self.f["split_at_R"] else gap > R)
            if new:
                pats.append([i, i])
            else:
                pats[-1][1] = i
        return [tuple(p) for p in pats]

    def structure(self, xs, start, L, R):
        """(pats, starts, G, allowed) where allowed[p] = (lo, hi) inclusive frame range."""
        pats = self.patterns(xs, R)
        Rg = R + 1 if self.f["R_plus_one"] else R
        d = len(pats)
        starts = [xs[a] for a, _ in pats]
        spans = [xs[b] - xs[a] for a, b in pats]
        G = []
        for p in range(d - 1):
            if self.f["gap_no_span"]:
                g = Rg + 1
            elif self.f["gap_next_span"]:
                g = spans[p + 1] + Rg + 1
            else:
                g = spans[p] + Rg + 1
            if self.f["gap_minus_one"]:
                g -= 1
            G.append(g)
        allowed = []
        for p in range(d):
            s = starts[p]
            fixed = (p == 0 and not self.f["first_free"]) or (
                p == d - 1 and not self.f["last_free"])
            if fixed:
                allowed.append((s, s))
                continue
            width = L + 1 if self.f["block_plus_one"] else L
            if self.f["centred"]:
                lo = s - L // 2
            elif self.f["anchor_zero"]:
                lo = L * (s // L)
            else:
                lo = start + L * ((s - start) // L)
            allowed.append((lo, lo + width - 1))
        return pats, starts, G, allowed

    # -- counting ----------------------------------------------------------------------------
    def tables(self, xs, start, L, R):
        """Count tables: tabs[p] is a dict frame -> N_p(frame), over allowed[p]."""
        pats, starts, G, allowed = self.structure(xs, start, L, R)
        d = len(pats)
        tabs = [None] * d
        if d == 0:
            return pats, starts, G, allowed, tabs
        lo, hi = allowed[d - 1]
        tabs[d - 1] = {w: 1 for w in range(lo, hi + 1)}
        for p in range(d - 2, -1, -1):
            nlo, nhi = allowed[p + 1]
            nxt = tabs[p + 1]
            # tail[v] = sum of N_{p+1}(v') for v' >= v within the next allowed range
            tail = {}
            acc = 0
            for v in range(nhi, nlo - 1, -1):
                acc += nxt[v]
                tail[v] = acc
            lo, hi = allowed[p]
            cur = {}
            for w in range(lo, hi + 1):
                need = max(w + G[p], nlo)
                cur[w] = tail[need] if need <= nhi else 0
            tabs[p] = cur
        return pats, starts, G, allowed, tabs

    def count(self, train, window, L, R):
        xs, start, _end, L, R = validate(train, window, L, R)
        if not xs:
            return 1
        _pats, starts, _G, allowed, tabs = self.tables(xs, start, L, R)
        if self.f["first_free"]:
            return sum(tabs[0].values())
        return tabs[0][starts[0]]

    # -- sampling ----------------------------------------------------------------------------
    def sample(self, train, window, L, R, rng):
        xs, start, _end, L, R = validate(train, window, L, R)
        if not xs:
            return np.zeros(0, dtype=np.int64)
        pats, starts, G, allowed, tabs = self.tables(xs, start, L, R)
        d = len(pats)
        W = [None] * d
        first_p = 0 if self.f["first_free"] else 1
        last_p = d - 1 if self.f["last_free"] else d - 2
        W[0] = starts[0]
        for p in range(first_p, last_p + 1):
            if p == 0:
                lo_need = allowed[0][0]
            else:
                lo_need = W[p - 1] + G[p - 1]
            alo, ahi = allowed[p]
            cands = [c for c in range(max(alo, lo_need), ahi + 1)]
            if self.f["descending"]:
                cands = cands[::-1]
            weights = [tabs[p][c] for c in cands]
            if self.f["skip_single_draw"] and len(cands) == 1:
                W[p] = cands[0]
                continue
            u = rng.random_sample()
            W[p] = self._pick(cands, weights, u)
        if d >= 2 and not self.f["last_free"]:
            W[d - 1] = starts[d - 1]
        y = np.empty(len(xs), dtype=np.int64)
        for p, (a, b) in enumerate(pats):
            blk_hi = allowed[p][1]
            for i in range(a, b + 1):
                v = W[p] + (xs[i] - xs[a])
                if self.f["clip_to_block"] and 0 < p < d - 1:
                    v = min(v, blk_hi)
                y[i] = v
        return y

    def _pick(self, cands, weights, u):
        if self.f["uniform_open"]:
            live = [c for c, w in zip(cands, weights) if w > 0]
            k = int(u * TWO53)
            return live[(k * len(live)) >> 53]
        if self.f["float_rule"]:
            T = float(sum(weights))
            acc = 0.0
            for c, w in zip(cands, weights):
                acc += float(w)
                if acc / T > u:
                    return c
            return cands[-1]
        T = sum(weights)
        k = int(u * TWO53)
        C = 0
        for c, w in zip(cands, weights):
            C += w
            if (C * TWO53 >= k * T) if self.f["select_ge"] else (C * TWO53 > k * T):
                return c
        raise AssertionError("no candidate selected; total weight was zero")

    # -- exact marginals (uniform over the support) --------------------------------------------
    def marginals(self, train, window, L, R):
        """{pattern p: {frame: number of valid resamplings with W_p = frame}} for free p,
        from a forward count F times the backward count N."""
        xs, start, _end, L, R = validate(train, window, L, R)
        if not xs:
            return {}
        pats, starts, G, allowed, tabs = self.tables(xs, start, L, R)
        d = len(pats)
        F = [None] * d
        F[0] = {starts[0]: 1}
        for p in range(1, d):
            lo, hi = allowed[p]
            prev = sorted(F[p - 1].items())
            cur = {}
            for w in range(lo, hi + 1):
                cur[w] = sum(c for v, c in prev if v + G[p - 1] <= w)
            F[p] = cur
        return {p: {w: F[p][w] * tabs[p][w] for w in F[p] if F[p][w] * tabs[p][w]}
                for p in range(1, d - 1)}


_CORRECT = Variant()


def pattern_jitter(train, window, L, R, rng):
    """-> 1-D numpy int64 array, same length as train (spec revision 1)."""
    return _CORRECT.sample(train, window, L, R, rng)


def pattern_jitter_count(train, window, L, R):
    """-> Python int: the number of valid resamplings of train (spec revision 1)."""
    return _CORRECT.count(train, window, L, R)


def pattern_marginals(train, window, L, R):
    return _CORRECT.marginals(train, window, L, R)


def pattern_bounds(train, R):
    """First-onset index of each pattern (definition only; used by the fuzzer's probes)."""
    xs = [int(v) for v in np.asarray(train).tolist()]
    return [a for a, _ in _CORRECT.patterns(xs, int(R))]
