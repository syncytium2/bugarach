"""Parity tests for the rate+context detector and peak-gate kernel against
MATLAB reference output (interface2 RateDetect / if2_peak_gate, R2025b).

Reference JSONs are generated from the committed synthetic fixture; the
generator replicates explore_sce's exact wiring (t50rise trains, extent from
regions + locs, rate_win=1 / context_win=60 on the RateViewer 0.1 s grid).
"""

import json
from pathlib import Path

import numpy as np
import pytest

from bugarach.detectors.peaks import peak_gate
from bugarach.detectors.rate import (
    event_rate_context,
    rate_detect,
    recording_extent,
    stream_trains,
)
from bugarach.store import load_slice

FIXTURES = Path(__file__).parent / "fixtures"
RTOL = 1e-9
ATOL = 1e-9


def as1d(v):
    """MATLAB jsonencode collapses 1-element arrays to scalars, empties to [],
    and NaN to null — normalize back to a 1-D float array."""
    if v is None:
        return np.empty(0)
    if not isinstance(v, list):
        v = [v]
    return np.array([np.nan if x is None else x for x in v], dtype=float)


def as2d(v):
    """Normalize a jsonencode'd Kx2 matrix ([] / flat pair / nested lists)."""
    if v is None or v == []:
        return np.empty((0, 2))
    a = np.array(v, dtype=float)
    return a.reshape(1, 2) if a.ndim == 1 else a


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
    kw = dict(excess_threshold_hz=params["thr"])
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
    det = rate_detect([np.empty(0), np.empty(0)], (0.0, 100.0))
    assert det.n_events == 0
    assert det.signal.t.size == 0
    assert det.signal.hilite.shape == (0, 2)


def test_context_window_clips_to_short_recording():
    trains = [np.array([1.0, 2.0, 3.0]), np.array([1.5, 2.5])]
    _, _, _, ctx_actual = event_rate_context(trains, (0.0, 10.0), 1.0, 60.0)
    assert ctx_actual == pytest.approx(9.0)  # 0.9 x duration


def test_grid_dt_is_parameterized():
    trains = [np.arange(0.0, 100.0, 0.5), np.arange(0.25, 100.0, 0.5)]
    det_10hz = rate_detect(trains, (0.0, 100.0))
    det_20hz = rate_detect(trains, (0.0, 100.0), grid_dt=0.05)
    assert det_20hz.signal.t.size == 2 * det_10hz.signal.t.size - 1
    assert det_20hz.settings["dt_grid"] == 0.05
    np.testing.assert_allclose(np.diff(det_20hz.signal.t), 0.05)


def test_threshold_too_high_yields_no_events():
    trains = [np.array([1.0, 1.1, 1.2]), np.array([1.05, 1.15])]
    det = rate_detect(trains, (0.0, 100.0), excess_threshold_hz=1e6)
    assert det.n_events == 0
