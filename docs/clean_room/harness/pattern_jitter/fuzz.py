"""Seeded structured differential fuzzer for pattern_jitter (spec revision 1).

Both implementations are black boxes: this file imports them and never inspects their code.
An implementation is anything with ``sample(train, window, L, R, rng)`` and
``count(train, window, L, R)``; ``Impl`` wraps a pair of functions.

What a case is checked for, in order (``check_case``):

1. **Counts.** ``count`` agrees with the reference implementation (exact Python ints), and,
   where the brute-force enumerator finishes, with the size of the enumerated support.
2. **Seeded differential.** For each of a few seeds, both implementations get a fresh
   ``RandomState(seed)``: outputs must be identical, and the two generators must end in the
   same state (the next draw from each is compared), which is the spec's "same rng
   consumption". The number of draws must also be exactly the number of free patterns.
3. **Invariants** on every seeded output — the spec's *Properties every output has*.
4. **Exact distribution, by enumeration** (supports up to ``PROBE_MAX`` members). The support
   is enumerated by brute force over the spec's onset-by-onset definition (equations 2.2 and
   4.2), never from a count table. From it the fuzzer builds the tree of free-pattern starts:
   at each node the children, ascending, with their numbers of completions ``n_r`` summing to
   ``T``. The specified rule sends ``k = u * 2**53`` to child ``r`` exactly on the integer
   segment ``[ceil(2**53 C_{r-1} / T), ceil(2**53 C_r / T) - 1]``. The implementation is driven
   with a scripted rng at **both ends of every segment** (later draws scripted to 0) and must
   return exactly the support member the rule predicts, with exactly the specified number of
   draws. Assuming each choice is a non-decreasing step function of its own draw (true of the
   specified sampler), this pins the implementation's distribution **exactly**: every member's
   probability is the product of its segment widths over ``2**53``, which equals ``1/Z`` to
   within the rng's 2**-53 resolution. No tolerance is involved.
5. **Frequencies** (``frequency_pvalue``, ``marginal_pvalues``): the statistical fallback where
   enumeration is not feasible, and a check of the exact result on real ``RandomState`` draws.
   Chi-square goodness of fit against uniform over the enumerated support (small trains), or
   against the exact per-pattern marginals from the adversary's forward-backward counts (large
   trains), at a stated family-wise alpha, Bonferroni across patterns.

Reference ``None`` runs the black-box checks alone (3 to 5), which do not need a second
implementation — the mutant check uses both modes.
"""

import math

import numpy as np

TWO53 = 1 << 53
PROBE_MAX = 400          # largest support the exact-distribution probe walks
BRUTE_NODE_CAP = 200000  # brute-force search nodes before giving up on a case
N_SEEDS = 2              # seeded differential draws per case


class Impl:
    def __init__(self, name, sample, count):
        self.name, self.sample, self.count = name, sample, count


class StubRNG:
    """Scripted ``random_sample()``: listed values, then ``pad`` forever (or fail)."""

    def __init__(self, values, pad=None):
        self.values, self.pad, self.calls = list(values), pad, 0

    def random_sample(self, *args, **kwargs):
        if args or kwargs:
            raise AssertionError("random_sample() must be called with no arguments")
        if self.calls < len(self.values):
            v = self.values[self.calls]
        elif self.pad is not None:
            v = self.pad
        else:
            raise AssertionError("rng called more often than scripted")
        self.calls += 1
        return v


class NoCallRNG:
    def random_sample(self, *args, **kwargs):
        raise AssertionError("rng must not be called")


# ------------------------------------------------------------------ definition-level helpers

def pattern_heads(x, R):
    """Index of each pattern's first onset (spec: onset i starts one when x[i]-x[i-1] > R)."""
    return [i for i in range(len(x)) if i == 0 or x[i] - x[i - 1] > R]


def n_free(x, R):
    return max(len(pattern_heads(x, R)) - 2, 0)


def block_start(t, start, L):
    return start + L * ((t - start) // L)


def brute_support(train, window, L, R, node_cap=BRUTE_NODE_CAP):
    """Every valid resampling, from the onset-by-onset definition; None if the search is too
    big. Sorted lexicographically, as tuples."""
    x = [int(v) for v in train]
    n = len(x)
    if n == 0:
        return [()]
    if n == 1:
        return [(x[0],)]
    start = int(window[0])
    head = 0
    heads = []
    for i in range(n):
        if i == 0 or x[i] - x[i - 1] > R:
            head = i
        heads.append(head)
    opts = [None] * n
    for i in range(1, n - 1):
        a = heads[i]
        base = block_start(x[a], start, L) + (x[i] - x[a])
        opts[i] = range(base, base + L)
    opts[n - 1] = (x[n - 1],)
    out = []
    y = [x[0]] + [None] * (n - 1)
    nodes = [0]

    def ok(i, v):
        dx, dy = x[i] - x[i - 1], v - y[i - 1]
        return dy == dx if dx <= R else dy > R

    def dfs(i):
        nodes[0] += 1
        if nodes[0] > node_cap:
            raise OverflowError
        for v in opts[i]:
            if ok(i, v):
                y[i] = v
                if i == n - 1:
                    out.append(tuple(y))
                else:
                    dfs(i + 1)

    try:
        dfs(1)
    except OverflowError:
        return None
    return sorted(out)


def invariant_violations(x, y, window, L, R):
    """The spec's 'Properties every output has', as a list of failure strings."""
    bad = []
    x = [int(v) for v in x]
    if not isinstance(y, np.ndarray) or y.ndim != 1 or y.dtype != np.int64:
        return [f"output is not a 1-D int64 ndarray: {type(y)} {getattr(y, 'dtype', None)}"]
    if len(y) != len(x):
        return [f"length {len(y)} != {len(x)}"]
    n = len(x)
    if n == 0:
        return bad
    yl = [int(v) for v in y]
    if yl[0] != x[0] or yl[-1] != x[-1]:
        bad.append("first or last onset moved")
    for i in range(1, n):
        if yl[i] < yl[i - 1]:
            bad.append(f"decreases at {i}")
        dx, dy = x[i] - x[i - 1], yl[i] - yl[i - 1]
        if dx <= R and dy != dx:
            bad.append(f"interval {i} of {dx} <= R not kept (got {dy})")
        if dx > R and dy <= R:
            bad.append(f"interval {i} became {dy} <= R")
    if min(yl) < x[0] or max(yl) > x[-1]:
        bad.append("onset outside [x0, x_last]")
    heads = pattern_heads(x, R)
    for a in heads[1:-1]:
        bs = block_start(x[a], int(window[0]), L)
        if not bs <= yl[a] <= bs + L - 1:
            bad.append(f"free pattern at onset {a} left its block")
    if (L == 1 or len(heads) <= 2) and yl != x:
        bad.append("L == 1 or d <= 2 but output differs from input")
    return bad


# ------------------------------------------------------------------ the exact probe

def _seg(C_prev, C, T):
    lo = -(-TWO53 * C_prev // T)
    hi = -(-TWO53 * C // T) - 1
    return lo, hi


def probe_distribution(impl, train, window, L, R, support):
    """Drive impl at both ends of every rule segment; return a list of failure strings.
    The support must come from brute_support."""
    x = [int(v) for v in train]
    heads = pattern_heads(x, R)
    m = max(len(heads) - 2, 0)
    fails = []
    arr = np.asarray(x, dtype=np.int64)

    def run(ks):
        rng = StubRNG([k * 2.0 ** -53 for k in ks], pad=0.0)
        try:
            y = impl.sample(arr.copy(), window, L, R, rng)
        except Exception as e:  # noqa: BLE001 - any exception is a finding
            return None, rng.calls, repr(e)
        return tuple(int(v) for v in y), rng.calls, None

    if m == 0:
        got, calls, err = run([])
        if err or calls != 0 or [got] != support:
            fails.append(f"no free pattern: got {got} calls {calls} err {err}")
        return fails

    free = heads[1:-1]

    def lowest_completion(members):
        return members[0]  # members are sorted; lowest start at every later level

    def walk(level, prefix_ks, members):
        # members: support members consistent with the prefix; group by this level's start
        groups = {}
        for s in members:
            groups.setdefault(s[free[level]], []).append(s)
        keys = sorted(groups)
        T = len(members)
        C = 0
        for c in keys:
            grp = groups[c]
            lo, hi = _seg(C, C + len(grp), T)
            C += len(grp)
            if hi < lo:
                fails.append(f"empty segment at level {level} for start {c}")
                continue
            expected = lowest_completion(grp)
            for k in {lo, hi, (lo + hi) // 2}:
                got, calls, err = run(prefix_ks + [k])
                if err is not None:
                    fails.append(f"exception at ks={prefix_ks + [k]}: {err}")
                elif calls != m:
                    fails.append(f"{calls} draws, expected {m} (ks={prefix_ks + [k]})")
                elif got != expected:
                    fails.append(f"ks={prefix_ks + [k]}: got {got}, rule gives {expected}")
                if len(fails) > 5:
                    return
            if level + 1 < m:
                walk(level + 1, prefix_ks + [lo], grp)

    walk(0, [], support)
    return fails


# ------------------------------------------------------------------ frequency tests

def _chi2_sf(stat, dof):
    try:
        from scipy.stats import chi2
        return float(chi2.sf(stat, dof))
    except ImportError:  # Wilson-Hilferty approximation
        if dof <= 0:
            return 1.0
        z = ((stat / dof) ** (1 / 3) - (1 - 2 / (9 * dof))) / math.sqrt(2 / (9 * dof))
        return 0.5 * math.erfc(z / math.sqrt(2))


def _pooled_chi2(obs, exp):
    """Chi-square statistic after pooling cells with expected count below 5."""
    pairs = sorted(zip(exp, obs))
    O, E, co, ce = [], [], 0.0, 0.0
    for e, o in pairs:
        co += o
        ce += e
        if ce >= 5:
            O.append(co)
            E.append(ce)
            co = ce = 0.0
    if ce and E:
        O[-1] += co
        E[-1] += ce
    if len(E) < 2:
        return 0.0, 0
    return sum((o - e) ** 2 / e for o, e in zip(O, E)), len(E) - 1


def frequency_pvalue(impl, train, window, L, R, support, n_draws, seed):
    """Chi-square p-value of n_draws seeded outputs against uniform over the support.
    An output outside the support returns p = 0."""
    rng = np.random.RandomState(seed)
    idx = {s: i for i, s in enumerate(support)}
    obs = [0] * len(support)
    arr = np.asarray(train, dtype=np.int64)
    for _ in range(n_draws):
        y = tuple(int(v) for v in impl.sample(arr, window, L, R, rng))
        if y not in idx:
            return 0.0
        obs[idx[y]] += 1
    stat, dof = _pooled_chi2(obs, [n_draws / len(support)] * len(support))
    return _chi2_sf(stat, dof) if dof else 1.0


def marginal_pvalues(impl, train, window, L, R, marginals, n_draws, seed):
    """Per free pattern, chi-square p-value of the seeded starts against exact marginals
    ({p: {frame: completions}}). Returns {p: pvalue}."""
    x = [int(v) for v in train]
    heads = pattern_heads(x, R)
    rng = np.random.RandomState(seed)
    arr = np.asarray(x, dtype=np.int64)
    hits = {p: {} for p in marginals}
    for _ in range(n_draws):
        y = impl.sample(arr, window, L, R, rng)
        for p in marginals:
            v = int(y[heads[p]])
            hits[p][v] = hits[p].get(v, 0) + 1
    out = {}
    for p, marg in marginals.items():
        if len(marg) < 2:
            continue
        if set(hits[p]) - set(marg):
            out[p] = 0.0
            continue
        Z = sum(marg.values())
        keys = sorted(marg)
        exp = [n_draws * marg[k] / Z for k in keys]
        obs = [hits[p].get(k, 0) for k in keys]
        stat, dof = _pooled_chi2(obs, exp)
        out[p] = _chi2_sf(stat, dof) if dof else 1.0
    return out


# ------------------------------------------------------------------ generator

def _build(g, n, R, L, start_max=6, interval_fn=None):
    start = int(g.randint(0, start_max + 1))
    first = start + int(g.randint(0, L + 2))
    x = [first] if n else []
    for _ in range(n - 1):
        x.append(x[-1] + int(interval_fn()))
    end = (x[-1] + 1 + int(g.randint(0, L + 1))) if x else start + int(g.randint(0, 3))
    return x, (start, end)


def gen_case(g):
    """One (train, window, L, R, shape) from a numpy RandomState."""
    shape = g.choice(["tiny", "singletons", "patterns", "span_cross", "block_cut_end",
                      "L1", "one_pattern", "dense", "long"],
                     p=[0.10, 0.14, 0.18, 0.14, 0.10, 0.04, 0.05, 0.15, 0.10])
    R = int(g.randint(0, 4))
    L = int(g.randint(1, 8))
    if shape == "tiny":
        n = int(g.randint(0, 4))
        pool = [0, R, R + 1, R + 2, L, L + 1, 2 * L + R]
        x, win = _build(g, n, R, L, interval_fn=lambda: g.choice(pool))
    elif shape == "singletons":
        L = int(g.randint(2, 8))
        n = int(g.randint(3, 8))
        x, win = _build(g, n, R, L, interval_fn=lambda: R + 1 + g.randint(0, 2 * L))
    elif shape == "patterns":
        R = int(g.randint(1, 5))
        L = int(g.randint(2, 7))
        n = int(g.randint(4, 10))
        pool = [0, R, R + 1, R + 1, R + 2, R + L, 1]
        x, win = _build(g, n, R, L, interval_fn=lambda: g.choice(pool))
    elif shape == "span_cross":
        R = int(g.randint(2, 5))
        L = int(g.randint(2, 6))
        n = int(g.randint(4, 9))
        x, win = _build(g, n, R, L, interval_fn=lambda: (
            g.randint(1, R + 1) if g.rand() < 0.5 else R + 1 + g.randint(0, L + 1)))
    elif shape == "block_cut_end":
        L = int(g.randint(3, 8))
        n = int(g.randint(3, 7))
        x, (start, _e) = _build(g, n, R, L, start_max=9,
                                interval_fn=lambda: R + 1 + g.randint(0, L + 1))
        win = (start, x[-1] + 1)
    elif shape == "L1":
        L = 1
        n = int(g.randint(2, 8))
        x, win = _build(g, n, R, L, interval_fn=lambda: g.randint(0, 5))
    elif shape == "one_pattern":
        n = int(g.randint(2, 7))
        x, win = _build(g, n, R, L, interval_fn=lambda: g.randint(0, 5))
        if len(x) > 1:
            R = max(b - a for a, b in zip(x, x[1:])) + int(g.randint(0, 2))
    elif shape == "dense":
        R = int(g.randint(0, 3))
        L = int(g.randint(5, 13))
        n = int(g.randint(4, 8))
        x, win = _build(g, n, R, L, interval_fn=lambda: R + 1 + g.randint(0, 2))
    else:  # long
        R = int(g.randint(0, 3))
        L = int(g.randint(3, 21))
        n = int(g.randint(40, 160))
        x, win = _build(g, n, R, L, interval_fn=lambda: (
            g.randint(0, R + 1) if g.rand() < 0.15 else R + 1 + g.randint(0, 2 * L)))
    return x, win, L, R, str(shape)


# ------------------------------------------------------------------ one case, many cases

def _call(fn, *args):
    try:
        return fn(*args), None
    except Exception as e:  # noqa: BLE001
        return None, repr(e)


def check_case(impl, reference, x, win, L, R, case_seed=0):
    """All checks on one case; returns a list of (check, detail) failures."""
    fails = []
    arr = np.asarray(x, dtype=np.int64)
    m = n_free(x, R)

    c_impl, e_impl = _call(impl.count, arr.copy(), win, L, R)
    if e_impl:
        fails.append(("count", f"{impl.name} raised {e_impl}"))
    elif not isinstance(c_impl, int) or isinstance(c_impl, bool):
        fails.append(("count", f"count is {type(c_impl).__name__}, not int"))
    if reference is not None:
        c_ref, e_ref = _call(reference.count, arr.copy(), win, L, R)
        if (e_impl is None) != (e_ref is None) or c_impl != c_ref:
            fails.append(("count", f"{impl.name}={c_impl} {e_impl} vs ref={c_ref} {e_ref}"))

    for s in range(N_SEEDS):
        seed = (case_seed * 7919 + s) % (2 ** 32)
        ra = np.random.RandomState(seed)
        inp = arr.copy()
        ya, ea = _call(impl.sample, inp, win, L, R, ra)
        if ea:
            fails.append(("seeded", f"{impl.name} raised {ea}"))
            continue
        if not isinstance(ya, np.ndarray):
            fails.append(("seeded", f"output is {type(ya).__name__}, not ndarray"))
            continue
        if ya is inp or np.shares_memory(ya, inp) or not np.array_equal(inp, arr):
            fails.append(("seeded", "output aliases or modifies the input"))
        nxt_a = ra.random_sample()
        probe = np.random.RandomState(seed)
        for _ in range(m):
            probe.random_sample()
        if nxt_a != probe.random_sample():
            fails.append(("seeded", f"rng consumption is not {m} draws"))
        for v in invariant_violations(x, ya, win, L, R):
            fails.append(("invariant", v))
        if reference is not None:
            rb = np.random.RandomState(seed)
            yb, eb = _call(reference.sample, arr.copy(), win, L, R, rb)
            if eb or not np.array_equal(ya, yb):
                fails.append(("seeded", f"seed {seed}: {ya} vs ref {yb} {eb}"))
            elif nxt_a != rb.random_sample():
                fails.append(("seeded", f"seed {seed}: rng consumption differs"))

    if len(x) <= 14:
        support = brute_support(x, win, L, R)
        if support is not None:
            if e_impl is None and c_impl != len(support):
                fails.append(("support", f"count {c_impl} != enumerated {len(support)}"))
            if len(support) <= PROBE_MAX:
                for f in probe_distribution(impl, x, win, L, R, support):
                    fails.append(("probe", f))
    return fails


def compare(impl, reference, n_cases=300, seed=0):
    """Disagreement records over n_cases generated cases (empty list = agreement)."""
    g = np.random.RandomState(seed)
    out = []
    for i in range(n_cases):
        x, win, L, R, shape = gen_case(g)
        fails = check_case(impl, reference, x, win, L, R, case_seed=seed * 100003 + i)
        if fails:
            out.append({"case": i, "shape": shape, "train": x, "window": list(win),
                        "L": L, "R": R, "fails": fails[:6]})
    return out
