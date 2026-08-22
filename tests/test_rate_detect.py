"""Parity tests for the rate+context detector and peak-gate kernel against
MATLAB reference output (interface2 RateDetect / if2_peak_gate, R2025b).

Reference JSONs are generated from the committed synthetic fixture; the
generator replicates explore_sce's exact wiring (t50rise trains, extent from
regions + locs, rate_win=1 / context_win=60 on the RateViewer 0.1 s grid).
"""

import json
import warnings
from pathlib import Path

import numpy as np
import pytest
from conftest import as1d, as2d

from bugarach.detectors.peaks import peak_gate
from bugarach.detectors.rate import (
    GridDtNotSetWarning,
    event_rate_context,
    rate_detect,
    recording_extent,
    stream_trains,
)
from bugarach.store import load_slice

FIXTURES = Path(__file__).parent / "fixtures"
RTOL = 1e-9
ATOL = 1e-9


# ---------------------------------------------------------------- peak gate

PEAK_REF = json.loads((FIXTURES / "ref_peak_gate.json").read_text())["cases"]


@pytest.mark.parametrize("case", PEAK_REF, ids=[c["name"] for c in PEAK_REF])
def test_peak_gate_parity(case):
    S = as1d(case["S"])
    thr = as1d(case["thr"])
    thr = thr[0] if thr.size == 1 else thr
    opts = case.get("opts") or {}
    pk = peak_gate(
        S, thr,
        prominence=opts.get("prominence", 0.0),
        min_distance=opts.get("min_distance", 1),
        floor=opts.get("floor", -np.inf),
        strict_above=opts.get("strict_above", True),
    )
    # MATLAB indices/positions are 1-based; the port is 0-based
    np.testing.assert_array_equal(pk.idx, as1d(case["idx"]).astype(int) - 1)
    for ours, ref, shift in (
        (pk.val, "val", 0), (pk.prominence, "prominence", 0),
        (pk.width_samples, "width_samples", 0),
        (pk.left_x, "left_x", 1), (pk.right_x, "right_x", 1),
    ):
        np.testing.assert_allclose(ours, as1d(case[ref]) - shift,
                                   rtol=RTOL, atol=ATOL, err_msg=ref)


# ---------------------------------------------------------------- rate detect

RATE_REF = json.loads((FIXTURES / "ref_ratedetect_synth.json").read_text())
SLICE = load_slice(FIXTURES / "synth_fastcal_s1.mat")


def _detect(stream_name, params):
    ext = recording_extent(SLICE)
    trains = stream_trains(getattr(SLICE, stream_name), ext)
    # the MATLAB reference runs on its hardcoded 0.1 s grid — pass explicitly
    kw = dict(excess_threshold_hz=params["thr"], grid_dt=0.1)
    if params["mode"] == "peak":
        kw.update(detection_mode="peak", peak_prominence=params["P"],
                  peak_min_distance_sec=params["D"])
    else:
        kw.update(merge_gap_s=params["gap"])
    return rate_detect(trains, ext, **kw)


def test_recording_extent_parity():
    assert recording_extent(SLICE) == pytest.approx(tuple(RATE_REF["ext"]), rel=RTOL)


@pytest.mark.parametrize("stream", ["fast", "slow"])
@pytest.mark.parametrize("ci", [1, 2, 3, 4, 5])
def test_rate_detect_parity(stream, ci):
    ref = RATE_REF[stream][f"case{ci}"]
    det = _detect(stream, ref["params"])
    for ours, key in (
        (det.locs, "locs"), (det.widths, "widths"), (det.amps, "amps"),
        (det.intra_event_freq_max, "freq_max"),
        (det.intra_event_freq_mean, "freq_mean"),
    ):
        np.testing.assert_allclose(ours, as1d(ref[key]), rtol=RTOL, atol=ATOL,
                                   err_msg=f"{stream} case{ci} {key}")
    np.testing.assert_allclose(det.signal.hilite, as2d(ref["hilite"]),
                               rtol=RTOL, atol=ATOL,
                               err_msg=f"{stream} case{ci} hilite")


@pytest.mark.parametrize("stream", ["fast", "slow"])
def test_rate_signal_parity(stream):
    ref = RATE_REF[stream]["case1"]
    det = _detect(stream, ref["params"])
    sig = det.signal
    assert sig.t.size == ref["signal_M"]
    assert sig.t[0] == pytest.approx(ref["t_first"], rel=RTOL)
    assert sig.t[-1] == pytest.approx(ref["t_last"], rel=RTOL)
    stride = ref["stride"]
    np.testing.assert_allclose(sig.y[::stride], as1d(ref["y_sub"]), rtol=RTOL, atol=ATOL)
    np.testing.assert_allclose(sig.ref[::stride], as1d(ref["ref_sub"]), rtol=RTOL, atol=ATOL)
    assert np.sum(sig.y) == pytest.approx(ref["y_sum"], rel=1e-8)
    assert np.sum(sig.ref) == pytest.approx(ref["ref_sum"], rel=1e-8)
    assert sig.y.max() == pytest.approx(ref["y_max"], rel=RTOL)
    assert sig.ref.max() == pytest.approx(ref["ref_max"], rel=RTOL)


# ---------------------------------------------------------------- unit tests

def test_empty_stream_yields_no_events():
    det = rate_detect([np.empty(0), np.empty(0)], (0.0, 100.0), grid_dt=0.1)
    assert det.n_events == 0
    assert det.signal.t.size == 0
    assert det.signal.hilite.shape == (0, 2)


def test_context_window_clips_to_short_recording():
    trains = [np.array([1.0, 2.0, 3.0]), np.array([1.5, 2.5])]
    _, _, _, ctx_actual = event_rate_context(trains, (0.0, 10.0), 1.0, 60.0,
                                             grid_dt=0.1)
    assert ctx_actual == pytest.approx(9.0)  # 0.9 x duration


def test_grid_dt_is_parameterized():
    trains = [np.arange(0.0, 100.0, 0.5), np.arange(0.25, 100.0, 0.5)]
    det_10hz = rate_detect(trains, (0.0, 100.0), grid_dt=0.1)
    det_20hz = rate_detect(trains, (0.0, 100.0), grid_dt=0.05)
    assert det_20hz.signal.t.size == 2 * det_10hz.signal.t.size - 1
    assert det_20hz.settings["dt_grid"] == 0.05
    np.testing.assert_allclose(np.diff(det_20hz.signal.t), 0.05)


def test_omitted_grid_dt_warns_and_falls_back():
    trains = [np.array([1.0, 2.0]), np.array([1.5])]
    with pytest.warns(GridDtNotSetWarning, match="sampling interval"):
        det = rate_detect(trains, (0.0, 100.0))
    assert det.settings["dt_grid"] == 0.1


def test_explicit_grid_dt_does_not_warn():
    trains = [np.array([1.0, 2.0]), np.array([1.5])]
    with warnings.catch_warnings():
        warnings.simplefilter("error", GridDtNotSetWarning)
        rate_detect(trains, (0.0, 100.0), grid_dt=0.1)


def test_threshold_too_high_yields_no_events():
    trains = [np.array([1.0, 1.1, 1.2]), np.array([1.05, 1.15])]
    det = rate_detect(trains, (0.0, 100.0), excess_threshold_hz=1e6, grid_dt=0.1)
    assert det.n_events == 0


# --- the CFAR options: guard cells, and a multiplicative bar -----------------
#
# Both default to the MATLAB original's behaviour, so parity is untouched and
# every test above still describes the shipped detector. The argument is in
# `docs/detector_history.md` §5.1 and §5.2; these are the assertions.

def test_the_guard_is_inert_at_its_default():
    """Parity is the product (FOUNDATIONS §2), so the guard must be inert at its
    default — and inert *by construction*, not because a subtraction happened to
    cancel. A guard band of width zero still covers the centre bin, so the zero
    case has to return before the arithmetic rather than through it."""
    rng = np.random.RandomState(0)
    trains = [np.sort(rng.uniform(0, 300, 40)) for _ in range(12)]
    base = event_rate_context(trains, (0.0, 300.0), 1.0, 60.0, 0.1)
    zero = event_rate_context(trains, (0.0, 300.0), 1.0, 60.0, 0.1, guard_sec=0.0)
    for a, b in zip(base, zero):
        np.testing.assert_array_equal(np.asarray(a), np.asarray(b))


def test_a_guard_removes_the_events_under_it_from_the_context():
    """The whole point of a guard: a burst at t must not sit in the background
    estimate that judges t."""
    burst = np.arange(149.0, 151.0, 0.02)          # a dense 2 s burst at t=150
    trains = [burst.copy() for _ in range(5)]
    _, _, ctx_open, _ = event_rate_context(trains, (0.0, 300.0), 1.0, 60.0, 0.1)
    _, _, ctx_guard, _ = event_rate_context(trains, (0.0, 300.0), 1.0, 60.0, 0.1,
                                            guard_sec=4.0)
    at = 1500                                       # grid index of t = 150 s
    assert ctx_open[at] > 0, "the burst should be in the unguarded context"
    assert ctx_guard[at] < ctx_open[at], (
        "the guard did not remove the burst from its own context")
    assert ctx_guard[at] == pytest.approx(0.0, abs=1e-9), (
        "the only events are inside the guard, so the background is empty")


def test_a_guard_wider_than_the_context_is_refused():
    trains = [np.array([1.0, 2.0]), np.array([1.5])]
    with pytest.raises(ValueError, match="leave nothing to estimate"):
        event_rate_context(trains, (0.0, 300.0), 1.0, 60.0, 0.1, guard_sec=60.0)


def test_the_additive_bar_demands_a_different_ratio_at_each_background():
    """The defect §5.2 names, measured on one recording containing both
    backgrounds so no cross-run difference can explain it.

    A fixed offset means the RATIO the detector demands is `1 + excess/context`
    — large where the tissue is quiet, approaching 1 where it is busy. That is a
    rolling reference window with no constant-false-alarm property."""
    rng = np.random.RandomState(3)
    quiet = [np.sort(rng.uniform(0, 150, 30)) for _ in range(10)]
    busy = [np.sort(rng.uniform(150, 300, 240)) for _ in range(10)]
    trains = [np.concatenate([q, b]) for q, b in zip(quiet, busy)]

    _, _, ctx_y, _ = event_rate_context(trains, (0.0, 300.0), 1.0, 60.0, 0.1)
    lo, hi = 500, 2500                              # well inside each half
    assert ctx_y[hi] > 4 * ctx_y[lo], "the two halves must differ in background"

    # what a 2 Hz offset actually demands, as a multiple of the local background
    demanded_quiet = 1 + 2.0 / ctx_y[lo]
    demanded_busy = 1 + 2.0 / ctx_y[hi]
    assert demanded_quiet > 1.5, (
        f"in the quiet half the same offset demands {demanded_quiet:.2f}x the "
        "background — nearly double, a strict bar")
    assert demanded_busy < 1.25, (
        f"in the busy half it demands only {demanded_busy:.2f}x — a lax one. "
        "One constant, two different detectors: that is the defect, and a "
        "multiplicative bar does not have it")


def test_multiplicative_mode_folds_the_bar_into_the_trace():
    """`rate >= alpha*context` implemented as `rate - alpha*context >= 0`, so the
    hilite spans and the peak path stay one code path."""
    rng = np.random.RandomState(3)
    trains = [np.sort(rng.uniform(0, 300, 120)) for _ in range(10)]
    det = rate_detect(trains, (0.0, 300.0), grid_dt=0.1,
                      threshold_mode="multiplicative", threshold_alpha=2.0)
    assert det.settings["threshold_mode"] == "multiplicative"
    assert det.settings["threshold_alpha"] == 2.0
    assert det.settings["excess_threshold_hz"] == 0.0


def test_multiplicative_mode_is_not_the_default():
    trains = [np.array([1.0, 2.0]), np.array([1.5])]
    det = rate_detect(trains, (0.0, 100.0), grid_dt=0.1)
    assert det.settings["threshold_mode"] == "additive"
    assert det.settings["threshold_alpha"] is None, (
        "alpha is meaningless in additive mode and must not be recorded as "
        "though it had been used")


def test_an_unknown_threshold_mode_is_refused():
    trains = [np.array([1.0, 2.0]), np.array([1.5])]
    with pytest.raises(ValueError, match="additive"):
        rate_detect(trains, (0.0, 100.0), grid_dt=0.1, threshold_mode="ratio")


def test_the_settings_record_which_mechanism_produced_the_detection():
    """A detection made with a guard is not the same instrument as one made
    without, so the result has to say which it was."""
    trains = [np.sort(np.random.RandomState(1).uniform(0, 300, 60))
              for _ in range(8)]
    det = rate_detect(trains, (0.0, 300.0), grid_dt=0.1, guard_sec=5.0)
    assert det.settings["guard_sec"] == 5.0
