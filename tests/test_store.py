import os
from pathlib import Path

import numpy as np
import pytest

from bugarach.store import load_slice

FIXTURE = Path(__file__).parent / "fixtures" / "synth_fastcal_s1.mat"
REAL_STORE = Path(
    os.environ.get("BUGARACH_DATA_ROOT")
    or Path.home()
    / "University of Michigan Dropbox/Richard DeFazio/data/"
      "processed_archive/event_store_onset_revised_2v"
)


def _check_slice(s):
    assert s.fast.n_rois > 0
    assert s.slow.n_rois == s.fast.n_rois
    for stream in (s.fast, s.slow):
        assert len(stream.amp) == stream.n_rois
        assert len(stream.width) == stream.n_rois
        assert len(stream.t50rise) == stream.n_rois
        for locs in stream.locs:
            assert locs.ndim == 1
            if locs.size:
                assert np.all(locs >= 0)
                assert np.all(np.diff(locs) >= 0), "onsets must be sorted"
    for r in s.regions:
        assert r.end_sec > r.start_sec


def test_synthetic_v73_fixture():
    s = load_slice(FIXTURE)
    _check_slice(s)
    assert s.slice_id  # falls back to filename stem for MCOS strings
    assert s.fast.n_rois == 30
    assert s.fast.n_events > 0


@pytest.mark.skipif(not REAL_STORE.exists(), reason="interface2 data root not present")
def test_real_v7_slice():
    s = load_slice(REAL_STORE / "20240708_13.mat")
    _check_slice(s)
    assert s.slice_id == "20240708_13"
    assert s.fast.n_rois == 34
    assert s.regions, "real slices carry region annotations"
    assert all(r.name for r in s.regions)
