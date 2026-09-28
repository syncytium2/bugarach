"""count (sliding)'s local-rate threshold (opt-in, 2026-09-28): off by default, K(t) from each
ROI's own rate around t, never below 3, and a rate rise alone is not a call."""
from __future__ import annotations

import numpy as np
import pytest

from bugarach.detectors import count_sliding_detect
from bugarach.detectors import sliding as sl
from bugarach.detectors.count import LOCAL_MINIMUM, local_thresholds


def quiet_with_one_event(seed=1, n=20, dur=600.0):
    """Sparse background (one onset per ROI per ~60 s) and one 8-ROI coincidence at 300 s."""
    rs = np.random.default_rng(seed)
    tr = [np.sort(rs.uniform(0, dur, rs.poisson(dur / 60))) for _ in range(n)]
    for r in range(8):
        tr[r] = np.sort(np.append(tr[r], 300.0 + 0.1 * r))
    return tr, (0.0, dur)


def busy_stretch(seed=2, n=20, dur=600.0):
    """Every ROI's rate jumps tenfold, independently, for 120 s: co-activity from rate alone."""
    rs = np.random.default_rng(seed)
    tr = []
    for _ in range(n):
        base = rs.uniform(0, dur, rs.poisson(dur / 60))
        burst = rs.uniform(240, 360, rs.poisson(120 / 6))
        tr.append(np.sort(np.concatenate([base, burst])))
    return tr, (0.0, dur)


def test_off_by_default_the_threshold_is_the_floor():
    tr, rng = quiet_with_one_event()
    d = count_sliding_detect(tr, rng, min_rois=5)
    assert d.threshold == 5 and d.opts["local_rate_sec"] is None
    assert np.all(d.signal.ref == 5)


def test_the_local_threshold_is_never_below_three_and_infinite_where_nothing_reaches_it():
    tr, (a, b) = quiet_with_one_event()
    ev = [np.asarray(t, float) for t in tr]
    starts, ends, S = sl.pieces(ev, 2.0, a, b)
    K = local_thresholds(ev, starts, S, 2.0, (a, b), 30.0, (99.99,))[99.99]
    assert np.all(K[S >= LOCAL_MINIMUM] >= LOCAL_MINIMUM)
    assert np.all(np.isinf(K[S < LOCAL_MINIMUM]))


def test_a_real_coincidence_in_a_quiet_stretch_is_called():
    tr, rng = quiet_with_one_event()
    d = count_sliding_detect(tr, rng, local_rate_sec=30.0, local_pctile=99.99)
    assert any(abs(o - 300.0) < 2.0 for o in d.onset_sec)


def test_a_rate_rise_alone_is_not_a_call():
    """Ten times the rate in every ROI at once, independently: a fixed threshold of 3 turns the
    whole stretch into one long call; the local-rate threshold rises with the rate and calls none
    of it."""
    tr, rng = busy_stretch()
    fixed = count_sliding_detect(tr, rng, min_rois=3)
    local = count_sliding_detect(tr, rng, local_rate_sec=30.0, local_pctile=99.99)
    in_burst = lambda d: [(o, w) for o, w in zip(d.onset_sec, d.width_sec)  # noqa: E731
                          if 230 <= o <= 360]
    assert any(w > 100 for _, w in in_burst(fixed)), "the fixed threshold spans the rate rise"
    assert in_burst(local) == []
    assert local.opts["threshold_rule"].startswith("local rate")


def test_the_floor_is_not_used_in_local_mode():
    tr, rng = quiet_with_one_event()
    a = count_sliding_detect(tr, rng, local_rate_sec=30.0, min_rois=3)
    b = count_sliding_detect(tr, rng, local_rate_sec=30.0, min_rois=15)
    assert a.onset_sec.tolist() == b.onset_sec.tolist()


def test_bad_settings_are_refused():
    tr, rng = quiet_with_one_event()
    with pytest.raises(ValueError):
        count_sliding_detect(tr, rng, local_rate_sec=0.0)
    with pytest.raises(ValueError):
        count_sliding_detect(tr, rng, local_rate_sec=30.0, local_pctile=100.0)
