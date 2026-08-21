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


def test_raster_only_viewer_builds_and_computes_nothing(monkeypatch):
    """The first look at a folder somebody just sent you: recordings, no
    claims about them. Nothing is computed, which is also why it opens."""
    import bugarach.ui.app as app_mod

    def boom(*a, **k):                      # any detector call is a failure
        raise AssertionError("raster-only must not run a detector")

    monkeypatch.setattr(app_mod, "_compute", boom)
    app = build_viewer({"a": _foreign_slice()}, raster_only=True)
    assert app is not None


def test_export_folder_is_read_as_one_thing_not_swept_for_files(tmp_path):
    """`slices.csv` and `regions.csv` are not recordings. Without this a
    folder of 2 recordings opens as 4, two of them nonsense."""
    from bugarach.cli import _is_export_folder
    from bugarach.io import load_folder

    d = tmp_path / "export"
    d.mkdir()
    (d / "s1.csv").write_text("roi,time_sec,stream\n1,1.0,fast\n2,NA,fast\n")
    (d / "s2.csv").write_text("roi,time_sec\n1,4.0\n")
    (d / "slices.csv").write_text("slice_id,frame_interval_sec\ns1,0.05\ns2,0.1\n")
    (d / "regions.csv").write_text(
        "slice_id,region_idx,label,start_sec,end_sec\ns1,1,baseline,0,60\n")

    assert _is_export_folder(d)
    assert not _is_export_folder(tmp_path)          # a bare dir is not one
    ids = [s.slice_id for s in load_folder(d)]
    assert ids == ["s1", "s2"]

    app = build_viewer({s.slice_id: s for s in load_folder(d)},
                       raster_only=True)
    assert app is not None
