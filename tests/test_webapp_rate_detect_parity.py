"""The browser's RateDetect against `bugarach.detectors.rate`, exactly.

RateDetect draws **no random numbers**. It is a pure function of the event times,
so the browser port is either bit-identical to the Python or it is wrong — there
is no sampling error to hide a bug in. Everything here is compared at 1e-9, the
same bar the Python port holds against MATLAB.

That is a stronger guarantee than the assessment port carries, and it is why
these two detectors went first: a mistake cannot pass as Monte Carlo noise.

**CI runs this**, since 2026-08-19 — the runner installs chromium and
sets `BUGARACH_REQUIRE_BROWSER=1`, so a browser that goes missing fails
`test_browser_available.py` loudly rather than letting this skip quietly.
Without a browser locally it still skips.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from bugarach.detectors.rate import event_rate, event_rate_context, rate_detect
from bugarach.simulate import simulate_coordination

ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "docs" / "site" / "raster_viewer.html"

DURATION = 1800.0
GRID_DT = 0.1
# the operating point the bench ships for this detector
PARAMS = dict(excess_threshold_hz=5.0, context_win=60.0, rate_win=1.0)


@pytest.fixture(scope="module")
def trains():
    s, _ = simulate_coordination(duration_sec=DURATION, n_roi=30,
                                 bg_rate_hz=0.03, n_per_level=(5, 5, 5),
                                 min_sep_sec=60.0, seed=3)
    return [np.asarray(v, dtype=float) for v in s.streams["events"].locs]


@pytest.fixture(scope="module")
def js(trains):
    pw = pytest.importorskip("playwright.sync_api",
                             reason="the browser detector needs playwright")
    from playwright.sync_api import sync_playwright

    payload = {"trains": [list(map(float, v)) for v in trains],
               "tRange": [0.0, DURATION], "dt": GRID_DT,
               "thr": PARAMS["excess_threshold_hz"],
               "rateWin": PARAMS["rate_win"], "ctxWin": PARAMS["context_win"]}
    script = """(cfg) => {
      const r = rateDetect(cfg.trains, cfg.tRange, {
        excessThresholdHz: cfg.thr, rateWin: cfg.rateWin,
        contextWin: cfg.ctxWin, gridDt: cfg.dt});
      const er = eventRate(cfg.trains, cfg.tRange, cfg.rateWin, cfg.dt);
      return {starts: r.starts, ends: r.ends, freqMax: r.freqMax,
              freqMean: r.freqMean, ctxActual: r.ctxActual,
              nEvents: r.nEvents,
              rateX: Array.from(er.rateX), rateY: Array.from(er.rateY),
              colon: Array.from(matlabColon(0, cfg.dt, 10))};
    }"""
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception as e:                        # noqa: BLE001
            pytest.skip(f"no chromium available: {type(e).__name__}")
        try:
            page = browser.new_page()
            errs: list[str] = []
            page.on("pageerror", lambda e: errs.append(str(e)))
            page.goto(VIEWER.as_uri())
            out = page.evaluate(script, payload)
            assert not errs, errs
            return out
        finally:
            browser.close()


def test_the_matlab_colon_grid_matches_element_for_element(js):
    """The two-ended colon is the reason the grids agree at all. A plain forward
    grid differs in the last ulp for about a quarter of the elements, which is
    enough to move an event between bins."""
    from bugarach.detectors._shared import matlab_colon

    py = matlab_colon(0.0, GRID_DT, 10.0)
    got = np.asarray(js["colon"], dtype=float)
    assert got.shape == py.shape
    assert np.array_equal(got, py), "the browser grid is not MATLAB's colon"


def test_the_rate_trace_matches_exactly(js, trains):
    px, py = event_rate(trains, (0.0, DURATION), PARAMS["rate_win"], GRID_DT)
    jx = np.asarray(js["rateX"], dtype=float)
    jy = np.asarray(js["rateY"], dtype=float)
    assert jx.shape == px.shape
    assert np.max(np.abs(jx - px)) == 0.0, "grid differs"
    assert np.max(np.abs(jy - py)) < 1e-9, "rate differs"


def test_the_context_clip_is_the_same_value(js, trains):
    *_, ctx_actual = event_rate_context(trains, (0.0, DURATION),
                                        PARAMS["rate_win"],
                                        PARAMS["context_win"], GRID_DT)
    assert abs(js["ctxActual"] - ctx_actual) < 1e-12


def test_the_same_events_are_detected(js, trains):
    det = rate_detect(trains, (0.0, DURATION), grid_dt=GRID_DT, **PARAMS)
    # a comparison of two empty lists passes without comparing anything, so the
    # fixture has to actually detect something for this file to mean what it says
    assert det.locs.size >= 5, (
        f"the fixture only produced {det.locs.size} detections — every "
        f"comparison in this file would be near-vacuous")
    assert js["nEvents"] == det.locs.size, (
        f"browser found {js['nEvents']}, python found {det.locs.size}")


@pytest.mark.parametrize("field", ["starts", "ends", "freqMax", "freqMean"])
def test_every_event_field_matches_to_1e9(js, trains, field):
    det = rate_detect(trains, (0.0, DURATION), grid_dt=GRID_DT, **PARAMS)
    py = {"starts": det.locs,
          "ends": det.locs + det.widths,
          "freqMax": det.intra_event_freq_max,
          "freqMean": det.intra_event_freq_mean}[field]
    got = np.asarray(js[field], dtype=float)
    assert got.shape == np.shape(py), f"{field}: {got.shape} vs {np.shape(py)}"
    if got.size:
        assert np.max(np.abs(got - py)) < 1e-9, (
            f"{field}: worst |diff| {np.max(np.abs(got - py)):.3e}")
