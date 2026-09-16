"""The numpy rigid shift that produced every surrogate in the label-free run agrees with the
tested, Elephant-backed ``bugarach.surrogates.rigid_shift``.

``tools/tube_self_supervised.rigid_frames`` draws one offset per ROI from one generator, where
``rigid_shift`` seeds Elephant per ROI, so the two cannot agree draw for draw. What they must
share is the construction: every onset of an ROI moved by the same whole number of frames,
onsets leaving the window dropped, and the same distribution of that number. A murderboard
reviewer found the tested path and the path that ran were disjoint (2026-09-16); this closes it.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("elephant")

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

import tube_self_supervised as ts  # noqa: E402
from bugarach import surrogates as sg  # noqa: E402

L = 2000
J = 37.5
N_DRAWS = 3000


def _displacements_numpy():
    rng = np.random.RandomState(0)
    out = []
    for _ in range(N_DRAWS):
        (k,) = ts.rigid_frames([np.array([1000])], L, J, rng)
        out.append(int(k[0]) - 1000)
    return np.asarray(out)


def _displacements_elephant():
    out = []
    for i in range(N_DRAWS):
        res = sg.generate("rigid_shift", [np.array([1000])], (0, L), ("rigid-frames-test", i), J=J)
        out.append(int(res.trains[0][0]) - 1000)
    return np.asarray(out)


def test_every_onset_of_an_roi_moves_by_one_whole_frame_offset_and_leavers_are_dropped():
    rng = np.random.RandomState(1)
    train = np.array([3, 400, 401, 1000, 1990])
    anchor = 1000                                   # never within J of an edge
    dropped = 0
    for _ in range(500):
        (k,) = ts.rigid_frames([train], L, J, rng)
        # The anchor is always kept and no other onset lands within J + 1 of it,
        # so it names the offset.
        off = [x - anchor for x in k if abs(x - anchor) <= J + 1]
        assert len(off) == 1
        expect = train + off[0]
        expect = expect[(expect >= 0) & (expect < L)]
        assert np.array_equal(k, expect)
        dropped += train.size - k.size
    assert dropped > 0, "an onset 3 frames from the edge must sometimes leave the window"


def test_the_offset_distribution_matches_elephant_rigid_shift():
    a, b = np.sort(_displacements_numpy()), np.sort(_displacements_elephant())
    assert abs(a.mean() - b.mean()) < 1.5 and abs(a.std() - b.std()) < 1.5
    assert a.min() >= -round(J) - 1 and a.max() <= round(J) + 1
    assert b.min() >= -round(J) - 1 and b.max() <= round(J) + 1
    grid = np.arange(-40, 41)
    ks = np.max(np.abs(np.searchsorted(a, grid, "right") - np.searchsorted(b, grid, "right")))
    # Two-sample KS at n = m = 3000: the 0.001 critical value is 1.95 * sqrt(2/3000) = 0.050.
    assert ks / N_DRAWS < 0.05, ks / N_DRAWS
