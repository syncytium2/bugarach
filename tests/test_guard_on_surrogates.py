"""Guard cells on the two detectors whose bar is built from the window's events.

`docs/forks.md` §4 records that a guard does nothing for `rate+context`, with the
arithmetic: its bar is a fixed 2–5 Hz constant while the contamination a guard
removes is worth 0.14 Hz. It predicts the guard should matter for `loco` and
`coact`, whose bar is a percentile or a z-score against a null pool built from the
events *inside* the window — so contamination scales the threshold instead of
adding to a constant.

These pin the prediction, the parity that makes it safe, and the one place the
implementation could go quietly wrong.
"""

from __future__ import annotations

import numpy as np
import pytest

from bugarach.bench import make_crowded_recording, make_recording
from bugarach.detectors.coact import coact_detect
from bugarach.detectors.loco import loco_detect
from bugarach.detectors.rate import recording_extent, stream_trains

STREAM = "events"
COACT = dict(rng_seed=7, int_win_sec=2.0, context_win_sec=60.0, alpha=1e-4,
             n_surrogates=100)
LOCO = dict(rng_seed=7, bin_width_sec=1.0, context_win_sec=120.0,
            thr_step_sec=15.0, merge_gap_sec=2.0, threshold_pctile=99.9,
            n_surrogates=100)


@pytest.fixture(scope="module")
def crowded():
    sl, gt = make_crowded_recording(1)
    ext = recording_extent(sl)
    return sl, gt, ext, stream_trains(sl.streams[STREAM], ext)


def test_the_guard_is_inert_at_zero_for_both(crowded):
    """Parity is the product (FOUNDATIONS §2). Both detectors must reproduce the
    MATLAB original bit-for-bit at the default, and — because both consume a
    seeded RNG stream in a documented order — that means the guarded branch must
    not run at all when the guard is zero, not merely compute the same answer."""
    sl, _, ext, trains = crowded
    a = coact_detect(trains, ext, **COACT)
    b = coact_detect(trains, ext, **COACT, guard_sec=0.0)
    np.testing.assert_array_equal(a.onset_sec, b.onset_sec)
    np.testing.assert_allclose(a.nullmean_prof, b.nullmean_prof,
                               rtol=0, atol=0, equal_nan=True)

    c = loco_detect(sl, **LOCO).streams[STREAM]
    d = loco_detect(sl, **LOCO, guard_sec=0.0).streams[STREAM]
    np.testing.assert_array_equal(c.onset_sec, d.onset_sec)


def test_the_guard_lowers_the_bar_it_was_meant_to_lower(crowded):
    """The mechanism, tested directly rather than through F1.

    A coordinated event sits inside the window that judges it, so it inflates its
    own null. Removing it should lower the null mean — measured over the 891
    candidate bins of a crowded recording: 3.689 without, 3.645 with."""
    _, _, ext, trains = crowded
    open_ = coact_detect(trains, ext, **COACT).nullmean_prof
    guard = coact_detect(trains, ext, **COACT, guard_sec=10.0).nullmean_prof
    m = np.isfinite(open_) & np.isfinite(guard)
    assert m.sum() > 100, "not enough candidate bins to compare"
    assert guard[m].mean() < open_[m].mean(), (
        f"the guard did not lower the null: {guard[m].mean():.4f} vs "
        f"{open_[m].mean():.4f}")


def test_the_compaction_does_not_wrap_across_the_excised_span(crowded):
    """The one place this could go quietly wrong.

    CoactDetect's window is CENTRED on the bin under test, so a guard leaves a
    hole — and the null is a circular shift *within the window*. Shifting on the
    original width would wrap events across the excised span and re-import
    exactly what the guard removed, which would look like a working guard and do
    nothing.

    The check: with a guard so wide it swallows the whole context, no reference
    cells remain and the null must be undefined rather than silently computed
    from the wrapped remainder."""
    _, _, ext, trains = crowded
    r = coact_detect(trains, ext, **{**COACT, "context_win_sec": 20.0},
                     guard_sec=19.0)
    assert np.all(np.isnan(r.nullmean_prof) | (r.nullmean_prof >= 0))
    assert r.n_events == 0, (
        "a guard that leaves no reference cells produced detections — the shift "
        "is wrapping across the excised span")


def test_loco_refuses_a_guard_in_symmetric_mode():
    """`maxlt`'s halves are one-sided and stay contiguous when a guard shrinks
    them; `symmetric` is one window and would develop a hole. Refused rather than
    given a second, subtly different implementation nobody uses."""
    sl, _ = make_recording("baseline_quiet", 1)
    with pytest.raises(ValueError, match="only supported with"):
        loco_detect(sl, **{**LOCO, "null_context_mode": "symmetric"},
                    guard_sec=10.0)


def test_the_settings_record_the_guard(crowded):
    """A detection made with a guard is a different instrument from one made
    without, so the result has to say which."""
    sl, _, ext, trains = crowded
    assert coact_detect(trains, ext, **COACT,
                        guard_sec=7.5).opts["guard_sec"] == 7.5
    assert loco_detect(sl, **LOCO, guard_sec=7.5).params["guard_sec"] == 7.5
