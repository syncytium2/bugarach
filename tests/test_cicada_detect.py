"""Parity tests for locust, the sliding-window detector ported from interface2's
``generate_sce_cicada`` — so what these assert is agreement with THAT, not with the
Cossart lab's CICADA (docs/detector_history.md §6.3).

Against MATLAB reference output — global/regional threshold scope,
fixed and per-event duration modes, randi-based surrogate rolls on the shared
RNG stream.

**Where case 2's durations come from, and why the test computes them.** MATLAB's
``explore_sce`` prep feeds CICADA a per-event rise interval, ``locs - t50rise``,
and reference case 2 was generated that way — so parity has to be checked
against exactly that array. It used to be reproduced by ``rise_durations()``
inside the detector, and that function is now refused: **bugarach does not
derive event durations**, because the duration is the producer's and arrives in
``width_sec`` (ADR-0002's 2026-08-28 addendum, FOUNDATIONS §7). Nothing about
parity changes. The subtraction moves out of the shipped library and into the
one place it belongs — a test whose stated job is reconstructing MATLAB's
*input* — and is then handed to the detector the way any producer's duration is
handed to it, through ``duration_field="width"``. Same array in, same raster,
same numbers; the derivation is no longer something the package can do to a
recording on its own.
"""

import dataclasses
import json
from pathlib import Path

import numpy as np
import pytest
from conftest import as1d, assert_close_naninf

from bugarach.detectors.cicada import (
    DurationIsNotOursToDerive,
    cicada_detect,
    rise_durations,
)
from bugarach.store import load_slice

FIXTURES = Path(__file__).parent / "fixtures"
REF = json.loads((FIXTURES / "ref_cicada_synth.json").read_text())
SLICE = load_slice(FIXTURES / "synth_fastcal_s1.mat", dt=0.1)


def as_strs(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def as_bools(v):
    if v is None:
        return np.empty(0, dtype=bool)
    return np.atleast_1d(np.asarray(v, dtype=bool))


def as_structs(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def _with_rise_interval_as_the_width(sl):
    """MATLAB's ``explore_sce`` input, rebuilt: the rise interval AS the width.

    This is the store case, where ``locs`` really is the peak — so the
    subtraction is the rise interval and reproduces what generated the
    reference. On an export folder it would be zero for every event, which is
    the second reason the detector no longer does this for anybody.
    """
    streams = {
        name: dataclasses.replace(
            st,
            width=[np.asarray(pk, dtype=float) - np.asarray(on, dtype=float)
                   for pk, on in zip(st.locs, st.t50rise)],
            width_def="rise_interval_peak_minus_t50rise")
        for name, st in sl.streams.items()}
    return dataclasses.replace(sl, streams=streams)


def _detect(params):
    sl = SLICE
    dfield = params["dfield"]
    if dfield == "rise_dur":
        sl, dfield = _with_rise_interval_as_the_width(SLICE), "width"
    return cicada_detect(
        sl,
        threshold_scope=params["scope"],
        n_synchronous_frames=params["nsync"],
        sce_percentile=params["pct"] if isinstance(params["pct"], (int, float))
        else tuple(params["pct"]),
        n_surrogates=params["nsur"],
        sce_min_distance_frames=params["mindist"],
        imaging_rate_hz=10.0,
        onset_field="t50rise",
        active_duration_mode=params["admode"],
        duration_field=dfield,
        active_duration_sec=tuple(params["adur"]),
        rng_seed=20260706,
        emit_signal=True,
    )


@pytest.mark.parametrize("ci", [1, 2, 3, 4])
def test_cicada_parity(ci):
    ref = REF[f"case{ci}"]
    det = _detect(ref["params"])
    assert det.ext == pytest.approx(tuple(as1d(ref["ext"])), rel=1e-9)
    for stream_name, ours in (("FAST", det.fast), ("SLOW", det.slow)):
        r = ref[stream_name]
        tag = f"case{ci} {stream_name}"
        for a, key in (
            (ours.onset_sec, "onset_sec"), (ours.width_sec, "width_sec"),
            (ours.magnitude, "magnitude"), (ours.mag_total, "mag_total"),
            (ours.threshold, "threshold"),
        ):
            assert_close_naninf(a, as1d(r[key]), err_msg=f"{tag} {key}")
        assert ours.region == as_strs(r["region"]), f"{tag} region"
        np.testing.assert_array_equal(ours.in_stats_window,
                                      as_bools(r["in_stats_window"]),
                                      err_msg=f"{tag} in_stats_window")
        np.testing.assert_array_equal(ours.meets_floor,
                                      as_bools(r["meets_floor"]),
                                      err_msg=f"{tag} meets_floor")
        sig = ours.signal
        assert sig.t.size == r["sig_n"], tag
        assert sig.t[0] == pytest.approx(r["sig_t_first"], rel=1e-9)
        assert sig.t[-1] == pytest.approx(r["sig_t_last"], rel=1e-9)
        np.testing.assert_allclose(sig.y[::r["stride"]], as1d(r["sig_y_sub"]),
                                   rtol=0, atol=0, err_msg=f"{tag} sig_y")
        assert np.sum(sig.y) == pytest.approx(r["sig_y_sum"], rel=1e-9)
        assert sig.y.max() == pytest.approx(r["sig_y_max"], rel=1e-9)
        ref_thr = as_structs(r["sig_thr"])
        assert len(sig.thresholds) == len(ref_thr), f"{tag} sig_thr len"
        for got, want in zip(sig.thresholds, ref_thr):
            assert got["label"] == want["label"]
            assert got["value"] == pytest.approx(want["value"], rel=1e-9)


def test_rise_durations_refuses_because_duration_is_not_ours_to_derive():
    """The rule, asserted where the violation would be written.

    This test used to check that the subtraction was correct. The subtraction
    was correct and that was never the question: bugarach is not the layer that
    decides what a duration is derived from, so the right number computed here
    is still the wrong thing to compute.
    """
    with pytest.raises(DurationIsNotOursToDerive) as e:
        rise_durations(SLICE.fast)
    msg = str(e.value)
    assert "width_sec" in msg and 'duration_field="width"' in msg, (
        "the refusal has to say what to do instead, or it is an obstacle "
        f"rather than a rule — got: {msg}")


def test_the_detector_refuses_the_rise_dur_field_too():
    """The refusal covers the route a caller actually takes to reach it.

    Removing the function but leaving `duration_field="rise_dur"` wired to it
    would have moved the derivation, not closed it.
    """
    with pytest.raises(DurationIsNotOursToDerive):
        cicada_detect(SLICE, active_duration_mode="per_event",
                      duration_field="rise_dur", n_surrogates=2, rng_seed=1)


def test_bad_params_raise():
    with pytest.raises(ValueError):
        cicada_detect(SLICE, threshold_scope="bogus")
    with pytest.raises(ValueError):
        cicada_detect(SLICE, active_duration_mode="bogus")
    with pytest.raises(ValueError, match="duration_field"):
        cicada_detect(SLICE, active_duration_mode="per_event",
                      duration_field="nonexistent", n_surrogates=2, rng_seed=1)


def test_the_imaging_rate_comes_off_the_recording_and_changes_nothing():
    """It used to default to 10.0 Hz — this lab's rate, stated as everybody's.

    Two halves, and the second is why this could land at all: unset, the rate
    is now ``1 / Slice.dt``, and on a recording declaring 0.1 s that is the
    same 10 Hz the fixture was measured at, event for event.
    """
    kw = dict(n_surrogates=10, rng_seed=7, n_synchronous_frames=2)
    derived = cicada_detect(SLICE, **kw)
    stated = cicada_detect(SLICE, imaging_rate_hz=10.0, **kw)
    np.testing.assert_array_equal(derived.fast.onset_sec, stated.fast.onset_sec)
    np.testing.assert_array_equal(derived.slow.threshold, stated.slow.threshold)
    # and the settings row records the rate that ran, not the argument
    assert derived.params["imaging_rate_hz"] == 10.0


def test_cicada_refuses_a_recording_that_never_stated_its_interval():
    """One boundary, one refusal. The detector has no number of its own to
    fall back on any more, so the recording's silence is what stops the run."""
    from dataclasses import replace

    from bugarach.store import FrameIntervalNotDeclaredError

    quiet = replace(SLICE, dt=None)
    with pytest.raises(FrameIntervalNotDeclaredError, match="frame_interval_sec"):
        cicada_detect(quiet, n_surrogates=2, rng_seed=1)


def test_same_seed_reproducible():
    kw = dict(n_surrogates=10, rng_seed=7, n_synchronous_frames=2)
    a = cicada_detect(SLICE, **kw)
    b = cicada_detect(SLICE, **kw)
    np.testing.assert_array_equal(a.fast.onset_sec, b.fast.onset_sec)
    np.testing.assert_array_equal(a.slow.threshold, b.slow.threshold)
