"""Smoke tests for the Panel viewer: builds headlessly against the canonical
two-stream fixture AND a foreign single-stream region-less slice, and the
compute plumbing produces signal rows for every enabled detector."""

from pathlib import Path

import numpy as np
import pytest

pn = pytest.importorskip("panel")
pytest.importorskip("holoviews")

from bugarach.detectors.rate import recording_extent  # noqa: E402
from bugarach.io import slice_from_events  # noqa: E402
from bugarach.store import load_slice  # noqa: E402
from bugarach.ui.app import PARAM_SPECS, _compute, build_viewer  # noqa: E402

FIXTURE = Path(__file__).parent / "fixtures" / "synth_fastcal_s1.mat"


def _foreign_slice():
    rng = np.random.RandomState(4)
    events = [np.sort(rng.uniform(0, 120, 15)) for _ in range(5)]
    return slice_from_events(events, slice_id="foreign")


def test_viewer_builds_on_two_stream_store():
    s = load_slice(FIXTURE)
    app = build_viewer({s.slice_id: s})
    assert app is not None  # FastListTemplate assembled without serving


def test_viewer_builds_on_single_stream_slice():
    s = _foreign_slice()
    app = build_viewer({"foreign": s})
    assert app is not None


@pytest.mark.parametrize("det", list(PARAM_SPECS))
def test_compute_runs_every_detector_generically(det):
    s = _foreign_slice()
    ext = recording_extent(s)
    params = {p: default for p, _, default, _, _ in PARAM_SPECS[det]}
    # shrink the expensive surrogate counts for the smoke test
    for key in ("n_surrogates",):
        if key in params:
            params[key] = 10
    out = _compute(det, s, ext, params)
    assert set(out) == {"events"}
    t, y, (onsets, widths), extra = out["events"]
    assert t.size == y.size and t.size > 0
    assert np.size(onsets) == np.size(widths)
