"""Clean-room validation for pattern_jitter (spec revision 1).

Wires docs/clean_room/pattern_jitter_spec.md's own vectors (parsed from the spec markdown),
the adversary's hand-derived vectors, a seeded differential fuzz pass between the deliverable
and the independent adversary implementation, the exact and statistical distribution checks,
and the mutant check into the normal suite, per docs/clean_room/WORKFLOW.md.

Synthetic inputs only. The primary is imported as a black box.
"""

import importlib.util
import json
import re
from pathlib import Path

import numpy as np
import pytest

from bugarach.pattern_jitter import pattern_jitter, pattern_jitter_count

REPO = Path(__file__).parent.parent
SPEC = REPO / "docs" / "clean_room" / "pattern_jitter_spec.md"
HARNESS = REPO / "docs" / "clean_room" / "harness" / "pattern_jitter"

# Family-wise false-alarm rate of each frequency test below (Bonferroni inside a test).
ALPHA = 1e-3


def _load(name):
    spec = importlib.util.spec_from_file_location(f"pj_harness_{name}", HARNESS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


adversary = _load("adversary")
fuzz = _load("fuzz")
mutants = _load("mutants")

PRIMARY = fuzz.Impl("primary", pattern_jitter, pattern_jitter_count)
ADVERSARY = fuzz.Impl("adversary", adversary.pattern_jitter, adversary.pattern_jitter_count)
IMPLS = [PRIMARY, ADVERSARY]
IDS = ["primary", "adversary"]


def _spec_blocks():
    blocks = re.findall(r"```json\n(.*?)```", SPEC.read_text(), re.S)
    assert len(blocks) == 4, "spec layout changed: re-read the spec for a revision header"
    return [json.loads(b) for b in blocks]


SPEC_SUPPORT, SPEC_SCRIPTED, SPEC_SEEDED, SPEC_ERRORS = _spec_blocks()
ADV = json.loads((HARNESS / "adversary_vectors.json").read_text())
SUPPORT = [("spec", v) for v in SPEC_SUPPORT] + [("adversary", v) for v in ADV["support"]]
BASES = {v["name"]: v for _, v in SUPPORT}
SCRIPTED = [("spec", v) for v in SPEC_SCRIPTED] + [("adversary", v) for v in ADV["scripted"]]
ERRORS = [("spec", v) for v in SPEC_ERRORS] + [("adversary", v) for v in ADV["errors"]]


def test_spec_is_revision_1():
    assert "**Revision 1**" in SPEC.read_text()[:400], (
        "the spec names a new revision: re-read it top to bottom and update both sides")


def _args(v):
    return np.asarray(v["train"], dtype=np.int64), tuple(v["window"]), v["L"], v["R"]


# ------------------------------------------------------------------ vectors

@pytest.mark.parametrize("impl", IMPLS, ids=IDS)
@pytest.mark.parametrize("src,v", SUPPORT, ids=lambda x: x if isinstance(x, str) else x["name"])
def test_support_vectors(impl, src, v):
    train, win, L, R = _args(v)
    c = impl.count(train, win, L, R)
    assert type(c) is int and c == v["count"]
    support = {tuple(s) for s in v["support"]}
    rng = np.random.RandomState(12345)
    for _ in range(50):
        assert tuple(int(t) for t in impl.sample(train, win, L, R, rng)) in support


@pytest.mark.parametrize("src,v", SUPPORT, ids=lambda x: x if isinstance(x, str) else x["name"])
def test_support_vectors_brute_force(src, v):
    """The harness's own enumerator reproduces every support set (a check of the harness)."""
    assert fuzz.brute_support(v["train"], v["window"], v["L"], v["R"]) == \
        [tuple(s) for s in v["support"]]


@pytest.mark.parametrize("impl", IMPLS, ids=IDS)
@pytest.mark.parametrize("src,v", SCRIPTED, ids=lambda x: x if isinstance(x, str) else x["name"])
def test_scripted_vectors(impl, src, v):
    train, win, L, R = _args(BASES[v["base"]])
    rng = fuzz.StubRNG(v["u"])
    y = impl.sample(train, win, L, R, rng)
    assert isinstance(y, np.ndarray) and y.dtype == np.int64
    assert list(y) == v["expected"]
    assert rng.calls == len(v["u"]), "rng not exhausted, or called too often"


@pytest.mark.parametrize("impl", IMPLS, ids=IDS)
@pytest.mark.parametrize("v", SPEC_SEEDED, ids=lambda v: v["name"])
def test_seeded_vectors(impl, v):
    train, win, L, R = _args(BASES[v["base"]])
    rng = np.random.RandomState(v["seed"])
    assert list(impl.sample(train, win, L, R, rng)) == v["expected"]
    ref = np.random.RandomState(v["seed"])
    for _ in range(v["draws"]):
        ref.random_sample()
    assert rng.random_sample() == ref.random_sample()


def _error_train(v):
    if v["name"] == "float_train":
        return np.asarray(v["train"], dtype=np.float64)
    if not v["train"]:
        return np.asarray([])
    return np.asarray(v["train"], dtype=np.int64)


@pytest.mark.parametrize("impl", IMPLS, ids=IDS)
@pytest.mark.parametrize("src,v", ERRORS, ids=lambda x: x if isinstance(x, str) else x["name"])
def test_error_vectors(impl, src, v):
    train = _error_train(v)
    with pytest.raises(ValueError):
        impl.sample(train, tuple(v["window"]), v["L"], v["R"], fuzz.NoCallRNG())
    with pytest.raises(ValueError):
        impl.count(train, tuple(v["window"]), v["L"], v["R"])


TYPE_ERRORS = {
    "numpy_float_L": (np.asarray([0, 4, 9]), (0, 10), np.float64(3.0), 0),
    "numpy_bool_R": (np.asarray([0, 4, 9]), (0, 10), 3, np.bool_(False)),
    "bool_dtype_train": (np.asarray([False, True]), (0, 10), 3, 0),
    "empty_two_dimensional": (np.empty((0, 2), dtype=np.int64), (0, 10), 3, 0),
    "object_dtype_train": (np.asarray([0, 4], dtype=object), (0, 10), 3, 0),
}


@pytest.mark.parametrize("impl", IMPLS, ids=IDS)
@pytest.mark.parametrize("name", sorted(TYPE_ERRORS))
def test_type_errors(impl, name):
    train, win, L, R = TYPE_ERRORS[name]
    with pytest.raises(ValueError):
        impl.sample(train, win, L, R, fuzz.NoCallRNG())
    with pytest.raises(ValueError):
        impl.count(train, win, L, R)


VALID_TYPES = {
    "uint64_train": (np.asarray([0, 4, 9], dtype=np.uint64), (0, 10), 5, 0, 4),
    "int32_train_numpy_L_R": (np.asarray([0, 4, 9], dtype=np.int32), (0, 10),
                              np.int64(5), np.int32(0), 4),
    "python_list_train": ([0, 4, 9], (0, 10), 5, 0, 4),
    "empty_float_train": (np.asarray([]), (3, 7), 2, 0, 1),
}


@pytest.mark.parametrize("impl", IMPLS, ids=IDS)
@pytest.mark.parametrize("name", sorted(VALID_TYPES))
def test_valid_types(impl, name):
    train, win, L, R, count = VALID_TYPES[name]
    assert impl.count(train, win, L, R) == count
    y = impl.sample(train, win, L, R, np.random.RandomState(0))
    assert isinstance(y, np.ndarray) and y.dtype == np.int64 and len(y) == len(train)


@pytest.mark.parametrize("impl", IMPLS, ids=IDS)
def test_input_not_modified_or_aliased(impl):
    train = np.asarray([0, 3, 5, 12], dtype=np.int64)
    keep = train.copy()
    y = impl.sample(train, (0, 15), 5, 1, np.random.RandomState(0))
    assert y is not train and not np.shares_memory(y, train)
    assert np.array_equal(train, keep)
    # d <= 2: the output equals the input but must still be a new array
    two = np.asarray([2, 7], dtype=np.int64)
    y2 = impl.sample(two, (0, 10), 5, 0, fuzz.NoCallRNG())
    assert y2 is not two and not np.shares_memory(y2, two)


# ------------------------------------------------------------------ large counts

OVERFLOW = (np.asarray([10 * j for j in range(311)], dtype=np.int64), (0, 3101), 10, 0)
FIVE30 = (np.asarray([5 * j for j in range(32)], dtype=np.int64), (0, 156), 5, 0)


@pytest.mark.parametrize("impl", IMPLS, ids=IDS)
@pytest.mark.parametrize("u,off", [(0.5, 5), (0.0, 0), (0.9999999999999999, 9)],
                         ids=["half", "zero", "top"])
def test_overflow_chain(impl, u, off):
    assert impl.count(*OVERFLOW) == 10 ** 309
    rng = fuzz.StubRNG([u] * 309)
    y = impl.sample(*OVERFLOW, rng)
    assert list(y) == [0] + [10 * j + off for j in range(1, 310)] + [3100]
    assert rng.calls == 309


@pytest.mark.parametrize("impl", IMPLS, ids=IDS)
@pytest.mark.parametrize("u", [0.5, 0.6])
def test_five_pow_thirty(impl, u):
    assert impl.count(*FIVE30) == 5 ** 30
    rng = fuzz.StubRNG([u] * 30)
    assert list(impl.sample(*FIVE30, rng)) == [0] + [5 * j + 2 for j in range(1, 31)] + [155]
    assert rng.calls == 30


# ------------------------------------------------------------------ distribution

@pytest.mark.parametrize("impl", IMPLS, ids=IDS)
@pytest.mark.parametrize("src,v", [s for s in SUPPORT if s[1]["count"] > 1],
                         ids=lambda x: x if isinstance(x, str) else x["name"])
def test_exact_distribution_on_vectors(impl, src, v):
    """The exact boundary probe (fuzz.probe_distribution) on every support vector."""
    support = [tuple(s) for s in v["support"]]
    assert fuzz.probe_distribution(impl, v["train"], v["window"], v["L"], v["R"], support) == []


@pytest.mark.parametrize("impl", IMPLS, ids=IDS)
def test_frequencies_uniform_on_vectors(impl):
    """Chi-square goodness of fit on real RandomState draws, Bonferroni over the vectors."""
    cases = [v for _, v in SUPPORT if v["count"] > 1]
    alpha_each = ALPHA / len(cases)
    for v in cases:
        support = [tuple(s) for s in v["support"]]
        p = fuzz.frequency_pvalue(impl, v["train"], v["window"], v["L"], v["R"],
                                  support, n_draws=400 * len(support), seed=7)
        assert p > alpha_each, f"{v['name']}: p = {p:.3g}"


@pytest.mark.parametrize("impl", IMPLS, ids=IDS)
def test_marginals_on_a_long_train(impl):
    """Where the support is too big to enumerate: seeded starts of every free pattern
    against the exact marginals from the adversary's forward-backward counts."""
    g = np.random.RandomState(3)
    x = [0]
    for _ in range(40):
        x.append(x[-1] + (int(g.randint(0, 2)) if g.rand() < 0.2 else 2 + int(g.randint(0, 9))))
    win, L, R = (0, x[-1] + 1), 6, 1
    marg = adversary.pattern_marginals(x, win, L, R)
    assert pattern_jitter_count(x, win, L, R) > 2 ** 64
    pv = fuzz.marginal_pvalues(impl, x, win, L, R, marg, n_draws=3000, seed=11)
    assert pv and min(pv.values()) > ALPHA / len(pv), pv


# ------------------------------------------------------------------ differential fuzz

@pytest.mark.parametrize("seed", [0, 1])
def test_differential_fuzz(seed):
    disagreements = fuzz.compare(PRIMARY, ADVERSARY, n_cases=300, seed=seed)
    assert disagreements == []


def test_differential_fuzz_roles_swapped():
    """The adversary under the black-box checks too, with the primary as the reference."""
    assert fuzz.compare(ADVERSARY, PRIMARY, n_cases=150, seed=5) == []


# ------------------------------------------------------------------ mutant check

@pytest.mark.parametrize("name", sorted(mutants.MUTANTS))
def test_fuzzer_catches_mutant(name):
    """WORKFLOW.md's sanity check: the fuzzer flags every deliberately broken variant on
    generated cases — differentially, and with the black-box checks alone."""
    bad = mutants.make(name)
    assert len(fuzz.compare(bad, mutants.reference(), n_cases=80, seed=0)) >= 3
    assert len(fuzz.compare(bad, None, n_cases=80, seed=0)) >= 3


@pytest.mark.parametrize("name", sorted(mutants.MUTANTS))
def test_named_vector_kills_mutant(name):
    """Each mutant is also killed by the vector the spec (or the adversary) names for it."""
    _flag, _what, vec = mutants.MUTANTS[name]
    bad = mutants.make(name)
    scripted = {v["name"]: v for _, v in SCRIPTED}
    try:
        if vec in scripted:
            v = scripted[vec]
            rng = fuzz.StubRNG(v["u"], pad=0.0)
            y = bad.sample(*_args(BASES[v["base"]]), rng)
            killed = list(y) != v["expected"] or rng.calls != len(v["u"])
        else:
            v = BASES[vec]
            support = [tuple(s) for s in v["support"]]
            killed = (bad.count(*_args(v)) != v["count"] or
                      fuzz.probe_distribution(bad, v["train"], v["window"], v["L"], v["R"],
                                              support) != [])
    except Exception:  # noqa: BLE001 - a crash on a valid input is a kill
        killed = True
    assert killed
