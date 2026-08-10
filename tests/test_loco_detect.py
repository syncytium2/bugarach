"""Parity tests for LoCo (detect_loco port) against MATLAB reference output —
both streams off one RNG stream per call, rolling threshold envelope included
(exercises MATLAB prctile semantics and maxlt/symmetric context modes).
"""

import json
from pathlib import Path

import numpy as np
import pytest
from conftest import as1d, assert_close_naninf

from bugarach.detectors.loco import loco_detect, region_windows
from bugarach.store import Region, Slice, Stream, load_slice

FIXTURES = Path(__file__).parent / "fixtures"
REF = json.loads((FIXTURES / "ref_loco_synth.json").read_text())
SLICE = load_slice(FIXTURES / "synth_fastcal_s1.mat")


def as_strs(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def as_bools(v):
    if v is None:
        return np.empty(0, dtype=bool)
    return np.atleast_1d(np.asarray(v, dtype=bool))


def _detect(params):
    kw = dict(
        bin_width_sec=tuple(params["bin"]), context_win_sec=tuple(params["ctx"]),
        threshold_pctile=params["pctile"], min_rois=3,
        n_surrogates=params["nsur"], thr_step_sec=tuple(params["tstep"]),
        merge_gap_sec=tuple(params["mgap"]), null_context_mode=params["nullmode"],
        rng_seed=20260706,
    )
    if params["mode"] == "peak":
        kw.update(detection_mode="peak", peak_prominence=params["P"],
                  peak_min_distance_sec=params["D"])
    return loco_detect(SLICE, **kw)


@pytest.mark.parametrize("ci", [1, 2, 3, 4])
def test_loco_parity(ci):
    ref = REF[f"case{ci}"]
    det = _detect(ref["params"])
    assert det.ext == pytest.approx(tuple(as1d(ref["ext"])), rel=1e-9)
    for stream_name, ours in (("FAST", det.fast), ("SLOW", det.slow)):
        r = ref[stream_name]
        tag = f"case{ci} {stream_name}"
        for a, key in (
            (ours.onset_sec, "onset_sec"), (ours.width_sec, "width_sec"),
            (ours.magnitude, "magnitude"), (ours.mag_total, "mag_total"),
            (ours.threshold, "threshold"), (ours.peak_sec, "peak_sec"),
            (ours.t50rise, "t50rise"), (ours.t50fall, "t50fall"),
        ):
            assert_close_naninf(a, as1d(r[key]), err_msg=f"{tag} {key}")
        assert ours.region == as_strs(r["region"]), f"{tag} region"
        np.testing.assert_array_equal(ours.in_stats_window,
                                      as_bools(r["in_stats_window"]),
                                      err_msg=f"{tag} in_stats_window")
        np.testing.assert_array_equal(ours.meets_floor,
                                      as_bools(r["meets_floor"]),
                                      err_msg=f"{tag} meets_floor")
        # rolling threshold envelope + coactivity trace
        sig = ours.signal
        assert sig.t.size == r["nb"], tag
        assert sig.t[0] == pytest.approx(r["t_first"], rel=1e-9)
        assert sig.t[-1] == pytest.approx(r["t_last"], rel=1e-9)
        np.testing.assert_allclose(sig.y, as1d(r["Sobs"]), rtol=0, atol=0,
                                   err_msg=f"{tag} Sobs")
        assert_close_naninf(sig.threshold, as1d(r["thrBin"]),
                            err_msg=f"{tag} thrBin")


def test_region_windows_parity():
    ref_rw = REF["case1"]["rw"]
    ref_rw = ref_rw if isinstance(ref_rw, list) else [ref_rw]
    rw = region_windows(SLICE, REF["case1"]["ext"][1])
    assert len(rw) == len(ref_rw)
    for ours, ref in zip(rw, ref_rw):
        assert ours.label == ref["label"]
        for f in ("raw_start", "raw_end", "win_start", "win_end"):
            assert getattr(ours, f) == pytest.approx(ref[f], rel=1e-9), f
        assert ours.meets_floor == bool(ref["meets_floor"])
        assert ours.is_baseline == bool(ref["is_baseline"])
        assert ours.is_hik == bool(ref["is_hik"])


def _mini_slice(regions):
    st = Stream(locs=[np.array([1.0]), np.array([2.0])],
                amp=[np.empty(1)] * 2, width=[np.empty(1)] * 2,
                t50rise=[np.array([1.0]), np.array([2.0])])
    return Slice(slice_id="mini", fast=st, slow=st, regions=regions)


def test_region_guards_halt():
    with pytest.raises(ValueError, match="expected 0"):
        region_windows(_mini_slice([Region("b", "r1", 5.0, 100.0)]), 100.0)
    with pytest.raises(ValueError, match="gap/overlap"):
        region_windows(_mini_slice([Region("b", "r1", 0.0, 50.0),
                                    Region("t", "r2", 60.0, 100.0)]), 100.0)


def test_hik_region_exempt_from_floor():
    rw = region_windows(_mini_slice([Region("baseline", "r1", 0.0, 1000.0),
                                     Region("HiK", "r2", 1000.0, 1100.0)]), 1100.0)
    assert rw[1].is_hik and rw[1].meets_floor and rw[1].win_dur == 100.0
    assert rw[0].is_baseline and not rw[0].is_hik


def test_bad_params_raise():
    with pytest.raises(ValueError):
        loco_detect(SLICE, null_context_mode="bogus")
    with pytest.raises(ValueError):
        loco_detect(SLICE, detection_mode="bogus")
    with pytest.raises(ValueError):
        loco_detect(SLICE, bin_width_sec=(1.0, 2.0, 3.0))
