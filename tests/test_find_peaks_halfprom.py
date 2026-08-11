"""Clean-room validation for find_peaks_halfprom (spec rev 2).

Runs the spec's own vectors (parsed from the spec markdown), the adversary's
hand-derived vectors, and a seeded differential fuzz pass between the
deliverable and the independent adversary implementation. See
docs/clean_room/WORKFLOW.md for the process these artifacts come from.
"""

import importlib.util
import json
import re
from pathlib import Path

import numpy as np
import pytest

from bugarach.detectors.peaks import find_peaks_halfprom as primary

REPO = Path(__file__).parent.parent
SPEC = REPO / "docs" / "clean_room" / "find_peaks_halfprom_spec.md"
HARNESS = REPO / "docs" / "clean_room" / "harness" / "find_peaks_halfprom"
ATOL = 1e-9


def _load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


adversary = _load_module(HARNESS / "adversary_impl.py", "fph_adversary").find_peaks_halfprom
fuzz = _load_module(HARNESS / "fuzz.py", "fph_fuzz")


def _spec_vectors():
    m = re.search(r"```json\n(.*?)```", SPEC.read_text(), re.S)
    return json.loads(m.group(1))


def _adversary_vectors():
    return json.loads((HARNESS / "adversary_vectors.json").read_text())


def _check(fn, v):
    S = [np.nan if x is None else x for x in v["S"]]
    idx, prom, lx, rx = fn(S, v["min_prominence"])
    assert idx.dtype.kind == "i"
    assert list(idx) == v["idx"]
    np.testing.assert_allclose(prom, v["prominence"], rtol=0, atol=ATOL)
    np.testing.assert_allclose(lx, v["left_x"], rtol=0, atol=ATOL)
    np.testing.assert_allclose(rx, v["right_x"], rtol=0, atol=ATOL)


@pytest.mark.parametrize("impl", [primary, adversary], ids=["primary", "adversary"])
@pytest.mark.parametrize("v", _spec_vectors(), ids=lambda v: v["name"])
def test_spec_vectors(impl, v):
    _check(impl, v)


@pytest.mark.parametrize("impl", [primary, adversary], ids=["primary", "adversary"])
@pytest.mark.parametrize("v", _adversary_vectors(), ids=lambda v: v["name"])
def test_adversary_vectors(impl, v):
    _check(impl, v)


@pytest.mark.parametrize("bad", [[], [np.nan, np.nan], [1.0], [1.0, 2.0]],
                         ids=["empty", "all_nan", "one_sample", "two_samples"])
def test_degenerate_inputs(bad):
    idx, prom, lx, rx = primary(bad)
    assert idx.dtype.kind == "i"
    assert len(idx) == len(prom) == len(lx) == len(rx) == 0


@pytest.mark.parametrize("seed", [0, 1])
def test_differential_fuzz(seed):
    disagreements = fuzz.compare(primary, adversary, n_cases=300, seed=seed)
    assert disagreements == []
