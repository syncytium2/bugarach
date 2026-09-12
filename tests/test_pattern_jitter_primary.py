"""The pattern-jitter primary against its clean-room spec (revision 1).

Every vector is parsed from ``docs/clean_room/pattern_jitter_spec.md`` itself, so a
spec revision reaches these tests without anyone copying numbers by hand. The
reference for the support sets and for the random cross-checks is a brute force
over the spec's onset-by-onset definition (equations 2.2 and 4.2 as it states
them), deliberately independent of the pattern-level count table the
implementation uses. The adversary's independent implementation, its vectors, the
differential fuzzer and the mutant check live in
``docs/clean_room/harness/pattern_jitter/`` and are wired in by
``tests/test_pattern_jitter.py``; this file is the primary's own suite only.

Synthetic inputs only: no recording is read here.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import numpy as np
import pytest
from scipy.stats import chi2

from bugarach.pattern_jitter import pattern_jitter, pattern_jitter_count

SPEC = Path(__file__).resolve().parent.parent / "docs" / "clean_room" / "pattern_jitter_spec.md"


# --------------------------------------------------------------------------- spec parsing


def _json_blocks():
    return [json.loads(b) for b in re.findall(r"```json\n(.*?)```", SPEC.read_text(), re.S)]


def _block_with(key):
    """The spec's JSON block whose entries carry ``key`` (support: 'support', ...)."""
    for block in _json_blocks():
        if block and all(key in v for v in block):
            return block
    raise AssertionError(f"no JSON block in the spec has entries keyed {key!r}")


SUPPORT = _block_with("support")
SCRIPTED = _block_with("u")
SEEDED = _block_with("seed")
ERRORS = next(b for b in _json_blocks() if b and all("L" in v and "support" not in v for v in b))
BASE = {v["name"]: v for v in SUPPORT}


def test_spec_is_revision_1():
    """These tests were written against revision 1; a new revision means re-read it."""
    head = SPEC.read_text().splitlines()[2]
    assert head.startswith("**Revision 1**"), (
        "the pattern-jitter spec names a new revision: re-read it top to bottom, "
        "then update the implementation and this test"
    )


def test_spec_blocks_parsed():
    assert len(SUPPORT) == 17
    assert len(SCRIPTED) == 28
    assert len(SEEDED) == 9
    assert len(ERRORS) == 10


# --------------------------------------------------------------------------- helpers


class ScriptedRng:
    """A stub whose ``random_sample()`` returns listed values, and fails on one call too many."""

    def __init__(self, values):
        self.values = list(values)
        self.calls = 0

    def random_sample(self):  # no parameters: a call with arguments is a TypeError
        if self.calls >= len(self.values):
            raise AssertionError(f"rng called {self.calls + 1} times; only {len(self.values)} scripted")
        v = self.values[self.calls]
        self.calls += 1
        return v

    @property
    def exhausted(self):
        return self.calls == len(self.values)


class ForbiddenRng:
    def random_sample(self):
        raise AssertionError("rng must not be called")


class CountingRng:
    """Wraps a RandomState and counts calls."""

    def __init__(self, seed):
        self.inner = np.random.RandomState(seed)
        self.calls = 0

    def random_sample(self):
        self.calls += 1
        return self.inner.random_sample()


def _heads(x, R):
    """Index of the first onset of each onset's pattern, per the spec's definition."""
    head, cur = [], 0
    for i in range(len(x)):
        if i > 0 and x[i] - x[i - 1] > R:
            cur = i
        head.append(cur)
    return head


def _n_patterns(x, R):
    return len(set(_heads(x, R)))


def brute_support(x, window, L, R):
    """All valid resamplings, lexicographic, from the onset-by-onset definition.

    y[0] and y[n-1] fixed; each other onset in its pattern start's block shifted by
    its offset (equation 4.2, partition anchored at ``start``); every interval of
    R or less reproduced exactly and every longer one kept longer than R (2.2).
    """
    x = [int(v) for v in x]
    n = len(x)
    if n == 0:
        return [[]]
    start = window[0]
    head = _heads(x, R)
    choices = []
    for i in range(n):
        if i == 0 or i == n - 1:
            choices.append([x[i]])
        else:
            a = head[i]
            bs = start + L * ((x[a] - start) // L)
            off = x[i] - x[a]
            choices.append(range(bs + off, bs + off + L))
    out = []

    def rec(i, y):
        if i == n:
            out.append(list(y))
            return
        for v in choices[i]:
            if i > 0:
                dx, dy = x[i] - x[i - 1], v - y[-1]
                if dx <= R:
                    if dy != dx:
                        continue
                elif not dy > R:
                    continue
            y.append(v)
            rec(i + 1, y)
            y.pop()

    rec(0, [])
    return out


def check_invariants(x, window, L, R, y):
    """The spec's 'Properties every output has', on one draw."""
    x = np.asarray(x, dtype=np.int64)
    assert isinstance(y, np.ndarray) and y.dtype == np.int64 and y.ndim == 1
    assert y.shape == x.shape
    if x.size == 0:
        return
    assert y[0] == x[0] and y[-1] == x[-1]
    assert np.all(np.diff(y) >= 0)
    dx, dy = np.diff(x), np.diff(y)
    short = dx <= R
    assert np.array_equal(dy[short], dx[short]), "an interval of R or less changed"
    assert np.all(dy[~short] > R), "an interval longer than R was shortened to R or less"
    assert window[0] <= y.min() and y.max() < window[1]
    start = window[0]
    head = _heads(x.tolist(), R)
    heads = sorted(set(head))
    for p, h in enumerate(heads[1:-1], start=1):
        bs = start + L * ((int(x[h]) - start) // L)
        assert bs <= y[h] < bs + L, f"free pattern {p} left its block"
    if L == 1 or len(heads) <= 2:
        assert np.array_equal(y, x)


def random_input(rs, n_max=7, span=24):
    """A small random valid input with duplicates, exact-R intervals and start > 0 forced often."""
    n = int(rs.randint(0, n_max + 1))
    start = int(rs.randint(0, 6))
    L = int(rs.randint(1, 7))
    R = int(rs.randint(0, 4))
    end = start + int(rs.randint(max(n, 1), span + 1))
    if n == 0:
        return [], (start, end), L, R
    shape = rs.randint(4)
    if shape == 0:  # intervals drawn around R, R + 1 and zero
        steps = rs.choice([0, R, R + 1, R + 2, L, L + R + 1], size=n - 1)
        x = np.concatenate([[0], np.cumsum(steps)]) + start
        x = x[x < end]
        if x.size == 0:
            x = np.array([start])
    else:
        x = np.sort(rs.randint(start, end, size=n))
    return [int(v) for v in x], (start, end), L, R


# --------------------------------------------------------------------------- support vectors


@pytest.mark.parametrize("v", SUPPORT, ids=[v["name"] for v in SUPPORT])
def test_support_count(v):
    got = pattern_jitter_count(v["train"], tuple(v["window"]), v["L"], v["R"])
    assert type(got) is int
    assert got == v["count"] == len(v["support"])


@pytest.mark.parametrize("v", SUPPORT, ids=[v["name"] for v in SUPPORT])
def test_support_matches_brute_force(v):
    """The oracle reproduces the spec's hand-derived sets, so it can be trusted below."""
    assert brute_support(v["train"], tuple(v["window"]), v["L"], v["R"]) == v["support"]


@pytest.mark.parametrize("v", [v for v in SUPPORT if "marginals" in v],
                         ids=[v["name"] for v in SUPPORT if "marginals" in v])
def test_support_marginals(v):
    heads = sorted(set(_heads(v["train"], v["R"])))
    for p, want in v["marginals"].items():
        h = heads[int(p)]
        got = Counter(str(y[h]) for y in v["support"])
        assert dict(got) == want


@pytest.mark.parametrize("v", SUPPORT, ids=[v["name"] for v in SUPPORT])
def test_support_draws_are_members_and_uniform(v):
    """Every draw is a member; frequencies pass a chi-square at alpha = 1e-4 (seeded, so fixed)."""
    window = tuple(v["window"])
    support = [tuple(s) for s in v["support"]]
    count = v["count"]
    draws = 400 * count if count > 1 else 20
    rs = np.random.RandomState(20260911)
    seen = Counter()
    for _ in range(draws):
        y = pattern_jitter(v["train"], window, v["L"], v["R"], rs)
        check_invariants(v["train"], window, v["L"], v["R"], y)
        seen[tuple(y.tolist())] += 1
    assert set(seen) <= set(support)
    if count > 1:
        assert set(seen) == set(support), "a member of the support was never drawn"
        expected = draws / count
        stat = sum((seen[s] - expected) ** 2 / expected for s in support)
        assert stat < chi2.ppf(1 - 1e-4, count - 1), f"chi-square {stat:.1f} on {count - 1} df"


# --------------------------------------------------------------------------- scripted vectors


@pytest.mark.parametrize("v", SCRIPTED, ids=[v["name"] for v in SCRIPTED])
def test_scripted(v):
    b = BASE[v["base"]]
    rng = ScriptedRng(v["u"])
    y = pattern_jitter(b["train"], tuple(b["window"]), b["L"], b["R"], rng)
    assert y.tolist() == v["expected"]
    assert rng.exhausted, f"rng called {rng.calls} times, {len(v['u'])} scripted"


def test_scripted_values_are_on_the_2_53_grid():
    for v in SCRIPTED:
        for u in v["u"]:
            assert float(u) * 2**53 == int(float(u) * 2**53)


# --------------------------------------------------------------------------- seeded vectors


@pytest.mark.parametrize("v", SEEDED, ids=[v["name"] for v in SEEDED])
def test_seeded(v):
    b = BASE[v["base"]]
    rng = np.random.RandomState(v["seed"])
    y = pattern_jitter(b["train"], tuple(b["window"]), b["L"], b["R"], rng)
    assert y.tolist() == v["expected"]
    fresh = np.random.RandomState(v["seed"]).random_sample(v["draws"] + 1)
    assert rng.random_sample() == fresh[-1], "rng advanced by the wrong number of draws"


def test_seeded_first_values_as_the_spec_states():
    assert np.random.RandomState(0).random_sample(3).tolist() == [
        0.5488135039273248, 0.7151893663724195, 0.6027633760716439]
    assert np.random.RandomState(1).random_sample(3).tolist() == [
        0.417022004702574, 0.7203244934421581, 0.00011437481734488664]
    assert np.random.RandomState(2).random_sample(3).tolist() == [
        0.43599490214200376, 0.025926231827891333, 0.5496624778787091]


# --------------------------------------------------------------------------- overflow vector

OVERFLOW = dict(train=[10 * j for j in range(311)], window=(0, 3101), L=10, R=0)


def test_overflow_count_is_exact():
    z = pattern_jitter_count(**OVERFLOW)
    assert type(z) is int and z == 10**309
    with pytest.raises(OverflowError):
        float(z)


@pytest.mark.parametrize("u,offset", [(0.5, 5), (0.0, 0), (0.9999999999999999, 9)],
                         ids=["half", "zero", "top"])
def test_overflow_scripted(u, offset):
    rng = ScriptedRng([u] * 309)
    y = pattern_jitter(OVERFLOW["train"], OVERFLOW["window"], OVERFLOW["L"], OVERFLOW["R"], rng)
    want = [0] + [10 * j + offset for j in range(1, 310)] + [3100]
    assert y.tolist() == want
    assert rng.exhausted


# --------------------------------------------------------------------------- error vectors


def _error_train(v):
    if v["name"] == "float_train":
        return np.array(v["train"], dtype=np.float64)
    if v["name"] == "two_dimensional":
        return np.array(v["train"], dtype=np.int64)
    return np.array(v["train"], dtype=np.int64) if v["train"] else np.array([])


@pytest.mark.parametrize("v", ERRORS, ids=[v["name"] for v in ERRORS])
def test_error_vectors(v):
    train, window = _error_train(v), tuple(v["window"])
    with pytest.raises(ValueError):
        pattern_jitter(train, window, v["L"], v["R"], ForbiddenRng())
    with pytest.raises(ValueError):
        pattern_jitter_count(train, window, v["L"], v["R"])


@pytest.mark.parametrize("L,R", [(True, 0), (3, False), (np.float64(3.0), 0), (3, np.float32(1.0)),
                                 ("3", 0), (None, 0)])
def test_non_integer_parameters_rejected(L, R):
    with pytest.raises(ValueError):
        pattern_jitter([0, 4, 9], (0, 10), L, R, ForbiddenRng())
    with pytest.raises(ValueError):
        pattern_jitter_count([0, 4, 9], (0, 10), L, R)


def test_bool_train_rejected():
    with pytest.raises(ValueError):
        pattern_jitter(np.array([False, True]), (0, 10), 3, 0, ForbiddenRng())


# --------------------------------------------------------------------------- interface details


def test_empty_float_train_is_valid():
    empty = np.array([])
    assert empty.dtype == np.float64
    y = pattern_jitter(empty, (0, 10), 3, 0, ForbiddenRng())
    assert y.dtype == np.int64 and y.size == 0
    assert pattern_jitter_count(empty, (0, 10), 3, 0) == 1


def test_numpy_integer_parameters_and_dtypes_accepted():
    for dt in (np.int32, np.int64, np.uint16, np.uint64):
        x = np.array([0, 4, 9], dtype=dt)
        assert pattern_jitter_count(x, (np.int64(0), np.int64(10)), np.int64(5), np.uint8(0)) == 4
        y = pattern_jitter(x, (0, 10), np.int32(5), np.int64(0), ScriptedRng([0.5]))
        assert y.dtype == np.int64 and y.tolist() == [0, 3, 9]


def test_returns_a_new_array_and_leaves_input_alone():
    for x in (np.array([2, 7], dtype=np.int64), np.array([0, 4, 9], dtype=np.int64),
              np.array([4], dtype=np.int64)):
        before = x.copy()
        y = pattern_jitter(x, (0, 10), 5, 0, np.random.RandomState(0))
        assert y is not x and not np.shares_memory(x, y)
        assert np.array_equal(x, before)
        y[...] = -1
        assert np.array_equal(x, before)


def test_count_is_one_exactly_when_frozen():
    assert pattern_jitter_count([0, 2, 4, 6, 8], (0, 10), 3, 1) == 1
    assert pattern_jitter_count([0, 4, 9], (0, 10), 5, 0) == 4


# --------------------------------------------------------------------------- random cross-checks


def test_random_small_inputs_against_brute_force():
    """Counts, membership, invariants and rng consumption on 1500 random small inputs."""
    rs = np.random.RandomState(7)
    for _ in range(1500):
        x, window, L, R = random_input(rs)
        support = brute_support(x, window, L, R)
        assert pattern_jitter_count(x, window, L, R) == len(support), (x, window, L, R)
        members = {tuple(s) for s in support}
        n_free = max(_n_patterns(x, R) - 2, 0) if x else 0
        for seed in range(3):
            rng = CountingRng(seed)
            y = pattern_jitter(x, window, L, R, rng)
            assert tuple(y.tolist()) in members, (x, window, L, R, y)
            check_invariants(x, window, L, R, y)
            assert rng.calls == n_free


def test_scripted_extremes_hit_first_and_last_members():
    """u = 0 gives the lexicographically first member and u = 1 - 2**-53 the last.

    Candidates are taken in ascending order and zero-weight ones are never chosen,
    so the lowest u walks the least valid start of every free pattern, the highest
    the greatest -- on every input, which the brute force can confirm.
    """
    rs = np.random.RandomState(11)
    for _ in range(600):
        x, window, L, R = random_input(rs)
        support = brute_support(x, window, L, R)
        n_free = max(_n_patterns(x, R) - 2, 0) if x else 0
        lo = pattern_jitter(x, window, L, R, ScriptedRng([0.0] * n_free))
        hi = pattern_jitter(x, window, L, R, ScriptedRng([1 - 2**-53] * n_free))
        assert lo.tolist() == support[0]
        assert hi.tolist() == support[-1]


def test_long_trains_hold_invariants_and_counts_pass_2_64():
    rs = np.random.RandomState(3)
    big = 0
    for _ in range(40):
        n = int(rs.randint(50, 400))
        start = int(rs.randint(0, 50))
        R = int(rs.randint(0, 5))
        L = int(rs.randint(1, 40))
        steps = rs.choice([0, 1, R, R + 1, R + 3, 2 * L, 5 * L], size=n - 1)
        x = (np.concatenate([[0], np.cumsum(steps)]) + start).astype(np.int64)
        window = (start, int(x[-1]) + 1 + int(rs.randint(0, 10)))
        z = pattern_jitter_count(x, window, L, R)
        big = max(big, z)
        rng = CountingRng(int(rs.randint(1 << 30)))
        y = pattern_jitter(x, window, L, R, rng)
        check_invariants(x, window, L, R, y)
        assert rng.calls == max(_n_patterns(x.tolist(), R) - 2, 0)
    assert big > 2**64, "no long train exceeded 2**64 resamplings; the generator is too tame"


def test_same_seed_same_output_and_cache_is_transparent():
    x = [0, 3, 5, 5, 9, 14, 15, 22, 30]
    window = (0, 31)
    a = [pattern_jitter(x, window, 4, 1, np.random.RandomState(s)).tolist() for s in range(20)]
    # other inputs in between must not disturb cached tables
    for R in (0, 2, 3):
        pattern_jitter_count(x, window, 4, R)
        pattern_jitter(x, (0, 40), 4, R, np.random.RandomState(0))
    b = [pattern_jitter(x, window, 4, 1, np.random.RandomState(s)).tolist() for s in range(20)]
    assert a == b
