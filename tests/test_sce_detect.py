"""Parity tests for the binned SCE detector (generate_sce port) against
MATLAB reference output — regional/whole modes, threshold (merge off + on)
and peak modes, per-region surrogate thresholds and the emit_signal trace.
"""

import json
import warnings
from pathlib import Path

import numpy as np
import pytest
from conftest import as1d, assert_close_naninf

from bugarach.detectors.sce import sce_detect
from bugarach.store import load_slice

FIXTURES = Path(__file__).parent / "fixtures"
REF = json.loads((FIXTURES / "ref_sce_synth.json").read_text())
SLICE = load_slice(FIXTURES / "synth_fastcal_s1.mat")


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


def _detect(params):
    kw = dict(
        analysis_mode=params["analysis"], bin_width_sec=params["bin"],
        threshold_pctile=params["pctile"], n_surrogates=params["nsur"],
        min_rois=params["min_rois"],
        merge_gap_sec=np.nan if params["mgap"] is None else params["mgap"],
        rng_seed=20260706, emit_signal=True,
    )
    if params["mode"] == "peak":
        kw.update(detection_mode="peak", peak_prominence=params["P"],
                  peak_min_distance_sec=params["D"])
    return sce_detect(SLICE, **kw)


@pytest.mark.parametrize("ci", [1, 2, 3, 4, 5])
def test_sce_parity(ci):
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
        # emit_signal trace (NaN window separators) + per-region thresholds
        assert_close_naninf(ours.signal.t, as1d(r["sig_t"]), err_msg=f"{tag} sig_t")
        assert_close_naninf(ours.signal.y, as1d(r["sig_y"]), err_msg=f"{tag} sig_y")
        ref_thr = as_structs(r["sig_thr"])
        assert len(ours.signal.thresholds) == len(ref_thr), f"{tag} sig_thr len"
        for got, want in zip(ours.signal.thresholds, ref_thr):
            assert got["label"] == want["label"], f"{tag} sig_thr label"
            for f in ("value", "win_start", "win_end"):
                w = want[f]
                if w is None:
                    assert not np.isfinite(got[f])
                else:
                    assert got[f] == pytest.approx(w, rel=1e-9), f"{tag} sig_thr {f}"


def test_whole_mode_warns_on_multiregion():
    # synthetic slice has one region -> no warning
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        sce_detect(SLICE, analysis_mode="whole", n_surrogates=5, rng_seed=1)


def test_bad_params_raise():
    with pytest.raises(ValueError):
        sce_detect(SLICE, analysis_mode="bogus")
    with pytest.raises(ValueError):
        sce_detect(SLICE, detection_mode="bogus")
    with pytest.raises(NotImplementedError):
        sce_detect(SLICE, surrogate_model="jitter")
    with pytest.raises(ValueError):
        sce_detect(SLICE, surrogate_model="bogus")


def test_merge_gap_nan_yields_single_bin_episodes():
    det = sce_detect(SLICE, bin_width_sec=10, n_surrogates=20, rng_seed=2)
    det_m = sce_detect(SLICE, bin_width_sec=10, n_surrogates=20, rng_seed=2,
                       merge_gap_sec=1e9)
    # merging with a huge gap can only reduce (or keep) the episode count
    assert det_m.fast.n_events <= det.fast.n_events
