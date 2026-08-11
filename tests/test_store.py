import os
from pathlib import Path

import numpy as np
import pytest

from bugarach.store import load_slice

FIXTURE = Path(__file__).parent / "fixtures" / "synth_fastcal_s1.mat"
# real-store smoke test runs only where BUGARACH_DATA_ROOT points at an
# event_store_onset directory; no default — real data stays machine-local
_root = os.environ.get("BUGARACH_DATA_ROOT")
REAL_STORE = Path(_root) if _root else None


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


def test_streams_mapping_is_generic():
    s = load_slice(FIXTURE)
    assert list(s.streams) == ["fast", "slow"]  # insertion-ordered
    assert s.streams["fast"] is s.fast
    assert s.streams["slow"] is s.slow
    for name, stream in s.streams.items():
        assert stream.n_rois == s.fast.n_rois, name


@pytest.mark.skipif(REAL_STORE is None or not REAL_STORE.exists(),
                    reason="BUGARACH_DATA_ROOT not set")
def test_real_v7_slices():
    mats = sorted(REAL_STORE.glob("*.mat"))
    assert mats, "data root contains no slices"
    s = load_slice(mats[0])
    _check_slice(s)
    assert s.slice_id == mats[0].stem
    assert s.regions, "real slices carry region annotations"
    assert all(r.name for r in s.regions)
