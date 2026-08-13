"""Every detector runs on a single-stream slice with nothing but its own
defaults.

FOUNDATIONS §3 says streams are generic and that most outside labs record one,
which makes the single-stream slice the shape a stranger's data arrives in. Two
detectors could not run on it: LoCo and CICADA carried their tuned optima as
literal (FAST, SLOW) pairs, and a pair is neither a scalar nor a
one-element-in-stream-order sequence, so broadcasting refused it. The refusal
named a parameter, so the first reading was "my data is malformed".

The defect was old. What kept it invisible is that every detector test ran
against the committed two-stream fixture — so the absence of the test below is
the actual bug, and the parametrization over all six detectors is the fix.
Flattening the defaults to scalars was the wrong repair: it would have silently
changed SLOW on every canonical store and broken the parity claim, which is why
two-stream resolution is pinned here as well.
"""

import numpy as np
import pytest

from bugarach.detectors.cicada import cicada_detect
from bugarach.detectors.coact import coact_detect
from bugarach.detectors.loco import loco_detect, per_stream_param
from bugarach.detectors.rate import rate_detect, recording_extent, stream_trains
from bugarach.detectors.sce import sce_detect
from bugarach.detectors.sync import sync_detect
from bugarach.io import slice_from_events


def _events(seed, n_roi=6, n=40, dur=600.0):
    rng = np.random.RandomState(seed)
    # a planted burst so the detectors have something to find, not just noise
    return [np.sort(np.concatenate([rng.uniform(0, dur, n),
                                    300.0 + rng.uniform(0, 1.0, 3)]))
            for _ in range(n_roi)]


def _single_stream():
    """A foreign recording: one stream, no region annotations."""
    return slice_from_events(_events(4), slice_id="foreign")


def _two_stream():
    return slice_from_events({"fast": _events(4), "slow": _events(5)},
                             slice_id="canonical")


# --- the detectors, single stream, pure defaults ----------------------------
#
# Two call shapes: three detectors take a Slice and run every stream in it, the
# rest take one stream's trains plus the extent. Spike-sync is the one detector
# with no defaults to test — see its own case below.

SLICE_DETECTORS = {"loco": loco_detect, "cicada": cicada_detect, "sce": sce_detect}
TRAIN_DETECTORS = {"rate": rate_detect, "coact": coact_detect}


@pytest.mark.parametrize("name", sorted(SLICE_DETECTORS))
def test_slice_detector_runs_on_one_stream_with_defaults(name):
    det = SLICE_DETECTORS[name](_single_stream())
    assert set(det.streams) == {"events"}


@pytest.mark.parametrize("name", sorted(TRAIN_DETECTORS))
def test_train_detector_runs_on_one_stream_with_defaults(name):
    s = _single_stream()
    ext = recording_extent(s)
    out = TRAIN_DETECTORS[name](stream_trains(s.streams["events"], ext), ext)
    assert out is not None


def test_spike_sync_is_the_deliberate_exception():
    """The sixth detector is absent from the sweep above on purpose, and this
    pins why: ``sync_detect`` has no default coincidence window. tau is a
    physical timescale of the recording, not a tuned knob with a
    regime-optimum, so the port makes the caller name it rather than guessing
    (the viewer supplies FAST 0.25 / SLOW 0.5). If tau_max and max_gap ever
    acquire defaults, this test fails — and spike-sync joins the sweep instead
    of quietly sitting out of it.
    """
    s = _single_stream()
    ext = recording_extent(s)
    trains = stream_trains(s.streams["events"], ext)
    with pytest.raises(TypeError, match="tau_max"):
        sync_detect(trains, ext)
    assert sync_detect(trains, ext, tau_max=0.25, max_gap=0.5) is not None


# --- what the defaults resolve to -------------------------------------------

def test_one_stream_gets_the_fast_element_not_the_pair():
    s = _single_stream()
    kw = dict(rng_seed=7, n_surrogates=10)
    implicit = loco_detect(s, **kw)
    explicit = loco_detect(s, bin_width_sec=1.0, context_win_sec=120.0,
                           thr_step_sec=15.0, merge_gap_sec=2.0, **kw)
    assert np.array_equal(implicit.streams["events"].onset_sec,
                          explicit.streams["events"].onset_sec)


def test_cicada_one_stream_gets_the_fast_element():
    s = _single_stream()
    kw = dict(rng_seed=7, n_surrogates=10)
    implicit = cicada_detect(s, **kw)
    explicit = cicada_detect(s, sce_percentile=99.99, active_duration_sec=1.0, **kw)
    assert np.array_equal(implicit.streams["events"].onset_sec,
                          explicit.streams["events"].onset_sec)


def test_two_stream_defaults_are_still_the_calibrated_pair():
    """The parity claim: nothing about the canonical store moved."""
    s = _two_stream()
    kw = dict(rng_seed=7, n_surrogates=10)
    implicit = loco_detect(s, **kw)
    explicit = loco_detect(s, bin_width_sec=(1.0, 2.0), context_win_sec=(120.0, 60.0),
                           thr_step_sec=(15.0, 30.0), merge_gap_sec=(2.0, 4.0), **kw)
    for stream in ("fast", "slow"):
        assert np.array_equal(implicit.streams[stream].onset_sec,
                              explicit.streams[stream].onset_sec)


def test_slow_is_not_silently_flattened_to_fast():
    """Guards the repair that was explicitly rejected: had the defaults been
    flattened to scalars, SLOW would now run with FAST's settings."""
    s = _two_stream()
    kw = dict(rng_seed=7, n_surrogates=10)
    calibrated = loco_detect(s, **kw)
    flattened = loco_detect(s, bin_width_sec=1.0, context_win_sec=120.0,
                            thr_step_sec=15.0, merge_gap_sec=2.0, **kw)
    assert not np.array_equal(calibrated.streams["slow"].onset_sec,
                              flattened.streams["slow"].onset_sec)


# --- the broadcasting rule itself -------------------------------------------

def test_pair_resolves_by_stream_count():
    assert per_stream_param(None, ["fast", "slow"], "p", (1.0, 2.0)) == \
        {"fast": 1.0, "slow": 2.0}
    assert per_stream_param(None, ["events"], "p", (1.0, 2.0)) == {"events": 1.0}


def test_odd_stream_counts_fall_back_to_fast():
    names = ["a", "b", "c"]
    assert per_stream_param(None, names, "p", (1.0, 2.0)) == \
        {"a": 1.0, "b": 1.0, "c": 1.0}


def test_an_explicit_pair_on_one_stream_says_what_is_wrong():
    with pytest.raises(ValueError, match="two-stream store"):
        per_stream_param((1.0, 2.0), ["events"], "bin_width_sec", (1.0, 2.0))


def test_none_without_a_calibrated_default_is_an_error():
    with pytest.raises(ValueError, match="no calibrated default"):
        per_stream_param(None, ["events"], "p")
