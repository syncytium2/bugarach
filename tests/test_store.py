import os
from pathlib import Path

import numpy as np
import pytest

from bugarach.store import (FrameIntervalNotDeclaredError, Slice, Stream,
                            load_slice)

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
    s = load_slice(FIXTURE, dt=0.1)
    _check_slice(s)
    assert s.slice_id  # falls back to filename stem for MCOS strings
    assert s.fast.n_rois == 30
    assert s.fast.n_events > 0


def test_streams_mapping_is_generic():
    s = load_slice(FIXTURE, dt=0.1)
    assert list(s.streams) == ["fast", "slow"]  # insertion-ordered
    assert s.streams["fast"] is s.fast
    assert s.streams["slow"] is s.slow
    for name, stream in s.streams.items():
        assert stream.n_rois == s.fast.n_rois, name


# --- the sampling interval is a field, and nothing may invent one -----------
#
# FOUNDATIONS §6. These tests are the mechanized half of it: the rule used to
# be prose plus a warning nobody read, and three separate code paths defaulted
# to 0.1 s underneath it.

def _bare_stream(n=2):
    empty = [np.empty(0) for _ in range(n)]
    return Stream(locs=list(empty), amp=list(empty), width=list(empty),
                  t50rise=list(empty))


def test_a_slice_cannot_be_built_without_saying_what_its_interval_is():
    """Not "must have one" — must SAY. Silence and "we do not know" were the
    same state of the program, which is how the default survived for months."""
    with pytest.raises(TypeError, match="dt"):
        Slice(slice_id="s", streams={"fast": _bare_stream()})


def test_an_interval_that_is_not_seconds_is_refused_at_construction():
    for bad in (0.0, -0.05, float("nan"), float("inf"), "30fps"):
        with pytest.raises(FrameIntervalNotDeclaredError):
            Slice(slice_id="s", streams={"fast": _bare_stream()}, dt=bad)


def test_a_recording_that_states_no_interval_draws_and_does_not_measure():
    s = Slice(slice_id="s", streams={"fast": _bare_stream()}, dt=None)
    assert not s.has_dt
    with pytest.raises(FrameIntervalNotDeclaredError) as exc:
        s.require_dt("the rate grid")
    msg = str(exc.value)
    # the refusal has to be actionable, not merely correct
    assert "frame_interval_sec" in msg and "slices.csv" in msg
    assert "FOUNDATIONS §6" in msg


def test_a_declared_interval_reads_back_as_a_float_not_a_string():
    s = Slice(slice_id="s", streams={"fast": _bare_stream()}, dt="0.05")
    assert s.dt == 0.05 and s.require_dt() == 0.05
    assert isinstance(s.dt, float)


def test_the_store_reader_asks_for_the_interval_it_cannot_read():
    """The .mat store has no field for it — recorded in FOUNDATIONS §6 and
    filed upstream — so the reader asks rather than guessing on the lab's
    behalf. ``None`` is an answer; omitting the argument is not."""
    with pytest.raises(TypeError, match="dt"):
        load_slice(FIXTURE)
    assert load_slice(FIXTURE, dt=0.05).dt == 0.05
    assert not load_slice(FIXTURE, dt=None).has_dt


@pytest.mark.skipif(REAL_STORE is None or not REAL_STORE.exists(),
                    reason="BUGARACH_DATA_ROOT not set")
def test_real_v7_slices():
    mats = sorted(REAL_STORE.glob("*.mat"))
    assert mats, "data root contains no slices"
    s = load_slice(mats[0], dt=0.1)
    _check_slice(s)
    assert s.slice_id == mats[0].stem
    assert s.regions, "real slices carry region annotations"
    assert all(r.name for r in s.regions)
