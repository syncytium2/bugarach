"""Parity tests for the SPIKE-synchronization detector against cSPIKE-derived
MATLAB reference output (adaptive profile, binning, SpikyDetect3 hysteresis /
peak modes, artifact flagging), plus a cross-validation of the per-spike
profile against PySpike's merged multivariate profile.
"""

import json
from pathlib import Path

import numpy as np
import pytest
from conftest import as1d, assert_close_naninf

from bugarach.detectors.rate import recording_extent
from bugarach.detectors.sync import adaptive_profile, sync_detect
from bugarach.store import load_slice

FIXTURES = Path(__file__).parent / "fixtures"
REF = json.loads((FIXTURES / "ref_sync_synth.json").read_text())
SLICE = load_slice(FIXTURES / "synth_fastcal_s1.mat")
EXT = recording_extent(SLICE)
TAU = {"fast": 0.25, "slow": 0.5}
GAP = {"fast": 0.5, "slow": 2.0}


@pytest.mark.parametrize("stream,tau_key,tau", [
    ("fast", "tau250", 0.25), ("slow", "tau500", 0.5),
    ("fast", "tau1000000000", 1e6), ("slow", "tau1000000000", 1e6),
])
def test_profile_parity_vs_cspike(stream, tau_key, tau):
    p = REF[stream]["profiles"][tau_key]
    rx, ry = as1d(p["x"]), as1d(p["y"])
    x, y = adaptive_profile(getattr(SLICE, stream).t50rise, EXT, tau)
    assert x.size == rx.size
    o1 = np.lexsort((y, x))
    o2 = np.lexsort((ry, rx))
    np.testing.assert_allclose(x[o1], rx[o2], rtol=1e-9, atol=1e-9)
    np.testing.assert_allclose(y[o1], ry[o2], rtol=1e-9, atol=1e-9)


def _detect(stream, params):
    tau = TAU[stream] if isinstance(params["tau"], str) else params["tau"]
    kw = dict(tau_max=tau, max_gap=GAP[stream], C_threshold=params["Cthr"],
              C_min=params["Cmin"], min_n=params["minn"], dt=0.1,
              synchrony_statistic=params["stat"])
    if params["mode"] == "peak":
        kw.update(detection_mode="peak", peak_prominence=params["P"],
                  peak_min_distance_sec=params["D"])
    return sync_detect(getattr(SLICE, stream).t50rise, EXT, **kw)


@pytest.mark.parametrize("stream", ["fast", "slow"])
@pytest.mark.parametrize("ci", [1, 2, 3, 4])
def test_sync_parity(stream, ci):
    ref = REF[stream][f"case{ci}"]
    det = _detect(stream, ref["params"])
    tag = f"{stream} case{ci}"
    for ours, key in (
        (det.locs, "locs"), (det.widths, "widths"), (det.amps, "amps"),
        (det.locs, "onsets"), (det.ends, "ends"),
        (det.peak_C, "peak_C"), (det.plat90, "plat90"),
        (det.n_participating_rois, "n_part"),
    ):
        assert_close_naninf(ours, as1d(ref[key]), err_msg=f"{tag} {key}")
    np.testing.assert_array_equal(
        det.is_artifact,
        np.atleast_1d(np.asarray(ref["is_artifact"] if ref["is_artifact"]
                                 is not None else [], dtype=bool))
        if not isinstance(ref["is_artifact"], list)
        else np.asarray(ref["is_artifact"], dtype=bool),
        err_msg=f"{tag} is_artifact")
    # binned synchrony trace
    assert det.Cy.size == ref["C_n"], tag
    assert det.Cx[0] == pytest.approx(ref["Cx_first"], rel=1e-9)
    assert det.Cx[-1] == pytest.approx(ref["Cx_last"], rel=1e-9)
    np.testing.assert_allclose(det.Cy[::ref["stride"]], as1d(ref["Cy_sub"]),
                               rtol=1e-9, atol=1e-9, err_msg=f"{tag} Cy")
    assert np.sum(det.Cy) == pytest.approx(ref["Cy_sum"], rel=1e-8)
    assert det.Cy.max() == pytest.approx(ref["Cy_max"], rel=1e-9)


def test_profile_cross_validates_against_pyspike_uncapped():
    # NOTE: PySpike 0.9.0's max_tau is BROKEN for finite caps — its get_tau
    # applies the cap only as the default for missing edge-neighbors, so
    # spikes seconds apart "coincide" whenever all four surrounding ISIs
    # exist (verified: [40.4, 77.3, 534.4] vs [58.8, 85.0, 300.0] at
    # max_tau=0.25 marks 77.3/85.0 coincident). cSPIKE caps correctly and
    # our port is bit-exact against cSPIKE, so the cross-validation runs in
    # the UNCAPPED regime, where the two definitions coincide.
    pyspike = pytest.importorskip("pyspike")
    trains = [np.unique(v[np.isfinite(v) & (v >= EXT[0]) & (v <= EXT[1])])
              for v in SLICE.fast.t50rise]
    sts = [pyspike.SpikeTrain(v, EXT) for v in trains]
    prof = pyspike.spike_sync_profile(sts, max_tau=1e6)
    x, y = adaptive_profile(SLICE.fast.t50rise, EXT, 1e6)
    n1 = len(trains) - 1
    # PySpike merges same-time spikes: per unique time, its y is the summed
    # coincidence count and mp the summed pair multiplicity — our per-spike
    # C values must reproduce y/mp as their mean at every unique time.
    checked = 0
    for t, ys, mp in zip(prof.x[1:-1], prof.y[1:-1], prof.mp[1:-1]):
        sel = x == t
        if not sel.any():
            continue
        np.testing.assert_allclose(y[sel].sum() * n1, ys, rtol=1e-9, atol=1e-9,
                                   err_msg=f"t={t}")
        assert mp == n1 * sel.sum()
        checked += 1
    assert checked > 2000  # essentially every spike cross-checked


def test_pyspike_max_tau_is_still_inert():
    # The reason the cross-check above must run uncapped, pinned so it cannot
    # rot: PySpike's max_tau is a default for missing edge-neighbor ISIs, never
    # a bound on the window, so a finite cap changes nothing except through the
    # spikes at each train's edge. This test asserts the BUG, and is meant to
    # fail the day upstream fixes it — at which point the cross-check can be
    # extended to the capped regime and every warning about this comes down.
    # The full list of places to update, and the upstream report itself, live in
    # docs/todo/2026-08-11-file-pyspike-max-tau-issue.md — keep it the one
    # inventory, so a copy here cannot go stale behind it.
    # Regression landed in 0.8.0 (0.7.0 still capped).
    pyspike = pytest.importorskip("pyspike")
    rng = np.random.default_rng(0)
    edges = (0.0, 600.0)
    a, b = (pyspike.SpikeTrain(np.sort(rng.uniform(*edges, 60)), edges)
            for _ in range(2))                       # mean ISI ~10 s
    capped = [pyspike.spike_sync(a, b, max_tau=t) for t in (1.0, 0.25, 1e-6)]
    assert capped[0] == capped[1] == capped[2], \
        f"PySpike's max_tau appears to bound the window again: {capped}"
    # A 1 us window on 10 s ISIs should score 0; it scores the uncapped answer.
    assert capped[-1] > 0.3

    # The hand-checkable case quoted in the upstream report: 7.7 s apart,
    # coincident under a 0.25 s cap.
    a2 = pyspike.SpikeTrain([40.4, 77.3, 534.4], edges)
    b2 = pyspike.SpikeTrain([58.8, 85.0, 300.0], edges)
    x, y = pyspike.spike_sync_profile(a2, b2, max_tau=0.25).get_plottable_data()
    assert dict(zip(np.round(x, 1), y))[77.3] == 1.0


def test_bad_params_raise():
    with pytest.raises(ValueError):
        sync_detect([np.array([1.0])], (0.0, 10.0), tau_max=0.25,
                    max_gap=0.5, detection_mode="bogus")
    with pytest.raises(ValueError):
        sync_detect([np.array([1.0])], (0.0, 10.0), tau_max=0.25,
                    max_gap=0.5, synchrony_statistic="bogus")


def test_planted_synchrony_detected():
    rng = np.random.RandomState(3)
    trains = [np.sort(np.concatenate((rng.uniform(0, 300, 12),
                                      [150.0 + 0.02 * r])))
              for r in range(6)]
    # min_n=1: Cn is the same-time group size of a bin's LAST event (faithful
    # binning quirk), so a burst of distinct-time spikes in one bin has Cn=1
    det = sync_detect(trains, (0.0, 300.0), tau_max=0.25, max_gap=0.5,
                      C_threshold=0.5, C_min=0.3, min_n=1)
    hits = (det.locs <= 150.1) & (det.ends >= 149.9)
    assert hits.any(), "planted synchronous burst at t=150 not detected"
