"""Parity tests for CoactDetect (detect_local_coincidence port) against
MATLAB reference output, including the seeded surrogate null — MATLAB's
rng(seed) twister and numpy's RandomState(seed) produce identical streams.
"""

import json
from pathlib import Path

import numpy as np
import pytest
from conftest import as1d, assert_close_naninf

from bugarach.detectors.coact import coact_detect
from bugarach.detectors.rate import recording_extent
from bugarach.store import load_slice

FIXTURES = Path(__file__).parent / "fixtures"
REF = json.loads((FIXTURES / "ref_coact_synth.json").read_text())
SLICE = load_slice(FIXTURES / "synth_fastcal_s1.mat")


def _detect(stream_name, params):
    ext = recording_extent(SLICE)
    trains = getattr(SLICE, stream_name).t50rise  # raw cells; clipped internally
    kw = dict(int_win_sec=params["int_win_sec"],
              context_win_sec=params["context_win_sec"],
              min_rois=params["min_rois"],
              n_surrogates=params["n_surrogates"],
              alpha=params["alpha"], merge_gap_sec=3.0)
    if params["mode"] == "peak":
        kw.update(detection_mode="peak", peak_prominence=params["P"],
                  peak_min_distance_sec=params["D"])
    return coact_detect(trains, ext, **kw)


@pytest.mark.parametrize("stream", ["fast", "slow"])
@pytest.mark.parametrize("ci", [1, 2, 3, 4])
def test_coact_parity(stream, ci):
    ref = REF[stream][f"case{ci}"]
    det = _detect(stream, ref["params"])
    for ours, key in (
        (det.onset_sec, "onset_sec"), (det.width_sec, "width_sec"),
        (det.nrois, "nrois"), (det.z, "z"), (det.p, "p"),
        (det.peak_sec, "peak_sec"), (det.t50rise, "t50rise"),
        (det.t50fall, "t50fall"),
    ):
        assert_close_naninf(ours, as1d(ref[key]),
                            err_msg=f"{stream} case{ci} {key}")
    # candidate-bin profiles (surrogate-null z / p / mean; MATLAB 1-based bins)
    cand_ref = as1d(ref["cand"]).astype(int) - 1
    cand_ours = np.flatnonzero(~np.isnan(det.nullmean_prof))
    np.testing.assert_array_equal(cand_ours, cand_ref,
                                  err_msg=f"{stream} case{ci} cand")
    for prof, key in ((det.z_prof, "z_cand"), (det.pval_prof, "pval_cand"),
                      (det.nullmean_prof, "nullmean_cand")):
        assert_close_naninf(prof[cand_ref], as1d(ref[key]),
                            err_msg=f"{stream} case{ci} {key}")


@pytest.mark.parametrize("stream", ["fast", "slow"])
def test_coact_profile_parity(stream):
    ref = REF[stream]["case1"]
    det = _detect(stream, ref["params"])
    assert det.ctr.size == ref["nb"]
    assert det.ctr[0] == pytest.approx(ref["ctr_first"], rel=1e-9)
    assert det.ctr[-1] == pytest.approx(ref["ctr_last"], rel=1e-9)
    np.testing.assert_allclose(det.obs, as1d(ref["obs"]), rtol=0, atol=0,
                               err_msg=f"{stream} obs")
    assert det.signal.kind == "local_coincidence"


def test_planted_coincidence_detected():
    rng = np.random.RandomState(7)
    trains = [np.sort(np.concatenate((rng.uniform(0, 200, 8), [100.0 + 0.01 * r])))
              for r in range(8)]
    det = coact_detect(trains, (0.0, 200.0), int_win_sec=1.0, alpha=0.01,
                       n_surrogates=100)
    assert det.n_events >= 1
    hits = (det.onset_sec <= 100.5) & (det.onset_sec + det.width_sec >= 100.0)
    assert hits.any(), "planted synchronous event at t=100 not detected"
    assert det.width_kind == "episode_span"


def test_same_seed_is_reproducible():
    trains = [np.array([10.0, 50.0, 50.1]), np.array([50.05, 90.0]),
              np.array([49.9, 50.2, 120.0])]
    a = coact_detect(trains, (0.0, 150.0), n_surrogates=50)
    b = coact_detect(trains, (0.0, 150.0), n_surrogates=50)
    np.testing.assert_array_equal(a.onset_sec, b.onset_sec)
    np.testing.assert_array_equal(a.pval_prof, b.pval_prof)


def test_bad_detection_mode_raises():
    with pytest.raises(ValueError):
        coact_detect([np.array([1.0])], (0.0, 10.0), detection_mode="bogus")
