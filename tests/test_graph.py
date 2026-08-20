"""STTC and modularity, checked against the MATLAB the port replaced.

**Why a fixture and not a bare unit test.** `src/bugarach/graph.py` exists to take the
modularity half of the assembly negative off an unmaintained interface2 pipeline
(`docs/todo/2026-08-19-the-connectivity-pipeline-has-no-owner.md`). A port is only worth
having if it demonstrably computes the same thing, so `tests/fixtures/ref_sttc_matlab.json`
carries real windows, real trains and MATLAB's own coefficients, and these lock the port
against them on CI, with no store and no MATLAB.

The coefficient was written from Cutts & Eglen (2014) with `if2_sttc.m` deliberately
unread, so this comparison is a genuine independent check of it rather than a diff of two
transcriptions.
"""

import json
from pathlib import Path

import numpy as np
import pytest

from bugarach.graph import (jitter_trains, louvain, modularity,
                            modularity_vs_null, sttc, sttc_matrix)

FIX = Path(__file__).parent / "fixtures" / "ref_sttc_matlab.json"
CASES = json.loads(FIX.read_text())


@pytest.mark.parametrize("case", CASES, ids=[c["slice"] for c in CASES])
def test_sttc_reproduces_matlab_pairwise(case):
    """Every pair, to floating point. This is the whole warrant for the port."""
    trains = [np.asarray(t, dtype=float) for t in case["trains"]]
    S, _ = sttc_matrix(trains, case["dt"], case["t0"], case["t1"])
    n = len(trains)
    got = [S[i, j] for i in range(n) for j in range(i + 1, n)]
    want = case["sttc_upper"]
    assert len(got) == len(want)
    for g, w in zip(got, want):
        if np.isnan(w):
            assert np.isnan(g)
        else:
            assert g == pytest.approx(w, abs=1e-9), (g, w)


def test_sttc_is_undefined_not_zero_for_an_empty_train():
    """A cell that never fired has no coupling to report.

    Returning 0.0 would drag `meanSTTC` toward zero for a reason that is not about
    coupling — and it is the same undefined-as-negative confusion that made the
    reference pipeline understate its own rates.
    """
    a = np.array([1.0, 2.0, 3.0])
    assert np.isnan(sttc(a, np.array([]), 0.5, 0.0, 10.0))
    assert np.isnan(sttc(np.array([]), a, 0.5, 0.0, 10.0))


def test_sttc_of_a_train_with_itself_is_one():
    """The tiling coefficient's own sanity check: perfect agreement scores 1."""
    a = np.array([1.0, 5.0, 9.0, 30.0])
    assert sttc(a, a, 0.5, 0.0, 60.0) == pytest.approx(1.0, abs=1e-12)


def test_sttc_is_symmetric():
    rng = np.random.RandomState(3)
    a = np.sort(rng.uniform(0, 100, 40))
    b = np.sort(rng.uniform(0, 100, 25))
    assert sttc(a, b, 1.0, 0, 100) == pytest.approx(sttc(b, a, 1.0, 0, 100), abs=1e-12)


def test_modularity_of_two_disconnected_cliques_is_high():
    """A graph with an obvious answer, so a broken optimizer cannot pass quietly."""
    W = np.zeros((8, 8))
    W[:4, :4] = 1.0
    W[4:, 4:] = 1.0
    np.fill_diagonal(W, 0.0)
    labels, q = louvain(W, n_restarts=5, seed=1)
    assert q == pytest.approx(0.5, abs=0.01)
    assert len(set(labels[:4])) == 1 and len(set(labels[4:])) == 1
    assert labels[0] != labels[4]


def test_modularity_matches_hand_computation():
    """Q by the definition, against Q by the function, on a graph small enough to check."""
    W = np.array([[0., 1., 0.],
                  [1., 0., 1.],
                  [0., 1., 0.]])
    labels = np.array([0, 0, 1])
    k = W.sum(axis=1)
    two_m = k.sum()
    same = labels[:, None] == labels[None, :]
    want = (np.sum(W[same]) - np.sum(np.outer(k, k)[same]) / two_m) / two_m
    assert modularity(W, labels) == pytest.approx(want, abs=1e-12)


def test_louvain_returns_nan_on_a_graph_with_no_edges():
    """Undefined, so the caller reports an exclusion rather than a zero."""
    _, q = louvain(np.zeros((5, 5)))
    assert np.isnan(q)


def test_jitter_preserves_event_counts_and_stays_in_window():
    """The null's whole point: same cells, same counts, same window, different timing.

    If jitter changed any of those, the surrogate graph would differ from the observed
    one in node count or sparsity and the comparison would stop being about timing.
    """
    rng = np.random.RandomState(5)
    trains = [np.sort(rng.uniform(10, 90, n)) for n in (5, 20, 1)]
    out = jitter_trains(trains, 20.0, 10.0, 90.0, rng)
    for a, b in zip(trains, out):
        assert a.size == b.size
        assert b.min() >= 10.0 and b.max() < 90.0


def test_undefined_recording_is_not_a_negative():
    """Too few active cells -> `defined=False`, and `above_null` must not read as a result.

    This is the defect found in the reference outputs: `Q_obs > q_hi` is false for a
    missing value, so an untestable recording was written out as a 0 and counted as
    tested-and-not-modular. The port must refuse to make that claim.
    """
    res = modularity_vs_null([np.array([1.0]), np.array([])], t0=0, t1=100,
                             n_surrogates=5, n_restarts=2)
    assert res.defined is False
    assert res.above_null is False       # false, but `defined` is what a caller reads


def test_a_planted_module_is_found_and_a_uniform_field_is_not():
    """The positive control and the negative control, in one test.

    Without the first, a test that never fires proves nothing; without the second, an
    instrument that always fires would pass.
    """
    rng = np.random.RandomState(11)
    T0, T1 = 0.0, 600.0

    # two groups whose members fire together, groups independent of each other
    planted = []
    for g in range(2):
        base = np.sort(rng.uniform(T0, T1, 60))
        for _ in range(5):
            planted.append(np.sort(base + rng.normal(0, 0.3, base.size)))
    got = modularity_vs_null(planted, t0=T0, t1=T1, n_surrogates=40, n_restarts=5, seed=2)
    assert got.defined and got.above_null, got

    # no structure: every cell independent
    flat = [np.sort(rng.uniform(T0, T1, 60)) for _ in range(10)]
    none = modularity_vs_null(flat, t0=T0, t1=T1, n_surrogates=40, n_restarts=5, seed=2)
    assert none.defined and not none.above_null, none


# ---- the producer's ROI selection -------------------------------------------

def test_dead_roi_verdicts_load_and_a_missing_slice_keeps_everything(tmp_path):
    """A slice with no verdict keeps every ROI — the spec, not a silent pass.

    The R team's rule only judges slices whose second treatment is senktide or TTX;
    18 of 85 are ineligible and get no verdict at all. Treating "absent from the
    roster" as "reject everything" would empty them, and treating it as an error
    would refuse to score them.
    """
    from bugarach.assembly import load_dead_roi_keep
    f = tmp_path / "verdicts.csv"
    f.write_text("# a comment the loader must skip\n"
                 "slice_id,roi_index,keep\n"
                 "s1,1,1\ns1,2,0\ns1,3,1\n")
    got = load_dead_roi_keep(f)
    assert got == {"s1": [True, False, True]}
    assert got.get("not_in_roster") is None      # caller keeps everything
    assert load_dead_roi_keep(None) == {}
