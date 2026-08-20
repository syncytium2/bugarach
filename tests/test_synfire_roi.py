"""Silent ROIs are not evidence of order, and PySpike scores them as if they were.

These lock a *defect and its fix*, not an implementation choice. PySpike's
`spike_train_order` averages a per-pair ratio, and it scores a pair of trains that
are **both empty** as `(e=1, m=1)` — the value a perfectly ordered pair gets. So
handing the sorter every ROI in a recording, silent ones included, adds one
maximal-order term per silent pair: quadratic in the number of cells that never
fired, and entirely unrelated to whether anything fires in order.

On this corpus that is not a rounding error. `20240723_22` carries 17 events across
3 active ROIs and 21 silent ones — 210 silent pairs against 3 real ones — and scored
**0.353**, the top of the fast distribution, against **0.059** once the silent ROIs
are dropped. The recordings that moved most were the emptiest ones, so the upper tail
of the published indicator was measuring silence.

The first test pins PySpike's behaviour rather than ours: if a future release scores
empty pairs as undefined instead, the padding stops mattering and this fix can be
revisited. The rest pin the tool.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).parent.parent
sys.path.insert(0, str(REPO / "tools"))

spk = pytest.importorskip("pyspike", reason="synfire scan needs PySpike")
import synfire_scan as ss  # noqa: E402

WIN = (0.0, 100.0)


def _train(v):
    return spk.SpikeTrain(np.asarray(v, dtype=float), edges=list(WIN))


class _Stream:
    """The two attributes `_trains` reads off a real stream."""

    def __init__(self, locs):
        self.locs = locs
        self.n_rois = len(locs)


def test_pyspike_scores_two_empty_trains_as_a_perfectly_ordered_pair():
    """The upstream behaviour the fix exists for. Not our bug — our exposure to it."""
    from pyspike.spike_directionality import _spike_train_order_impl as impl

    e, m = impl(_train([]), _train([]), None, None, MRTS=0.0, RI=False)
    assert (e, m) == (1, 1), (
        "PySpike no longer scores an empty pair as maximally ordered; the reason "
        "silent ROIs are dropped below may no longer hold — re-derive before relying "
        "on this")

    # A real pair with no coincidences is scored as it should be: zero order, and it
    # still contributes to the denominator. Only the *empty* pair is anomalous.
    e, m = impl(_train([1.0]), _train([99.0]), None, None, MRTS=0.0, RI=False)
    assert e == 0 and m == 2


def test_silent_rois_inflate_the_indicator_when_they_are_kept():
    """The defect, on a recording small enough to check by hand.

    Three cells fire in a fixed order; twelve never fire. The order is identical in
    both cases, so any change in the indicator is the silence talking.
    """
    real = [[10, 20, 30, 40], [11, 21, 31, 41], [12, 22, 32, 42]]
    padded = real + [[] for _ in range(12)]

    f_real = spk.spike_train_order([_train(v) for v in real])
    f_padded = spk.spike_train_order([_train(v) for v in padded])

    assert f_real == pytest.approx(1.0), "three cells in strict order is a synfire chain"
    assert f_padded < f_real, "the 66 silent pairs move the average off the true value"


def test_trains_drops_silent_rois_by_default():
    stream = _Stream([[10.0, 20.0], [], [11.0, 21.0], [], []])
    trains = ss._trains(stream, WIN, stream.n_rois)
    assert len(trains) == 2, "silent ROIs must not reach the sorter"
    assert all(t.spikes.size for t in trains)


def test_keep_silent_restores_the_pre_fix_behaviour():
    """The escape hatch has to actually reproduce the old numbers, or it is a lie."""
    stream = _Stream([[10.0, 20.0], [], [11.0, 21.0], [], []])
    trains = ss._trains(stream, WIN, stream.n_rois, keep_silent=True)
    assert len(trains) == 5
    assert sum(1 for t in trains if t.spikes.size == 0) == 3


def test_events_outside_the_window_do_not_make_an_roi_active():
    """A cell that fired only outside the analysis window is silent *for this test*,
    and must be dropped like any other silent cell rather than entering as an empty
    train."""
    stream = _Stream([[10.0, 20.0], [999.0], [11.0, 21.0]])
    trains = ss._trains(stream, WIN, stream.n_rois)
    assert len(trains) == 2
