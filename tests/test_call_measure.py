"""One yardstick for every detector's calls (bugarach.call_measure, tools/measure_calls.py).

Width is the earliest to the last onset in the coordinated event; amplitude is proportional to
the cells taking part and inversely proportional to the interval between their onsets (Tony,
2026-09-21). Every expected value below is worked by hand from the construction.
"""
import importlib.util
import math
from pathlib import Path

import numpy as np
import pytest

from bugarach import call_measure as cm
from bugarach.store import Stream

ROOT = Path(__file__).resolve().parent.parent
FAST = dict(gap_sec=0.5, half_aperture_sec=1.0, min_interval_sec=0.1)


def stream(onsets_by_roi, amps_by_roi=None, widths_by_roi=None, width_def="rule"):
    locs = [np.asarray(o, dtype=float) for o in onsets_by_roi]
    amp = [np.asarray(a, dtype=float) for a in (amps_by_roi or [[1.0] * len(o) for o in locs])]
    wid = [np.asarray(w, dtype=float) for w in (widths_by_roi or [[0.9] * len(o) for o in locs])]
    return Stream(locs=locs, amp=amp, width=wid, t50rise=locs, width_def=width_def)


def test_width_is_earliest_to_last_onset_in_the_coordinated_event():
    s = stream([[10.0], [10.1], [10.3], [10.4]])
    m = cm.measure_call(s, 10.2, **FAST)
    assert m.core_span_sec == pytest.approx(0.4)
    assert m.core_n_roi == 4 and m.core_first_sec == pytest.approx(10.0)


def test_a_straggler_does_not_stretch_the_width():
    """10.9 is inside the ±1 s aperture but 0.5 s past the group, so it is not in the event."""
    s = stream([[10.0], [10.1], [10.2], [10.9]])
    m = cm.measure_call(s, 10.2, **FAST)
    assert m.core_span_sec == pytest.approx(0.2) and m.core_n_roi == 3
    assert m.span_sec == pytest.approx(0.9) and m.n_roi == 4     # still reported, separately


def test_amplitude_is_cells_over_the_mean_interval():
    # 4 cells, onsets 0.1 s apart: interval 0.1, amplitude 4 / 0.1 = 40 cells per second.
    m = cm.measure_call(stream([[5.0], [5.1], [5.2], [5.3]]), 5.15, **FAST)
    assert m.mean_interval_sec == pytest.approx(0.1)
    assert m.amplitude == pytest.approx(40.0)


def test_amplitude_doubles_with_twice_the_cells_at_the_same_spacing():
    four = cm.measure_call(stream([[5.0], [5.2], [5.4], [5.6]]), 5.3, **FAST)
    eight = cm.measure_call(stream([[5.0], [5.2], [5.4], [5.6]] * 2), 5.3, **FAST)
    # Eight cells, onsets pairwise coincident: 8 onsets over 0.6 s -> interval 0.6/7.
    assert four.amplitude == pytest.approx(4 / 0.2)
    assert eight.amplitude == pytest.approx(8 / max(0.6 / 7, 0.1))


def test_amplitude_doubles_when_the_same_cells_are_twice_as_tight():
    loose = cm.measure_call(stream([[5.0], [5.4], [5.8]]), 5.4, gap_sec=0.5,
                            half_aperture_sec=1.0, min_interval_sec=0.05)
    tight = cm.measure_call(stream([[5.0], [5.2], [5.4]]), 5.2, gap_sec=0.5,
                            half_aperture_sec=1.0, min_interval_sec=0.05)
    assert tight.amplitude == pytest.approx(2 * loose.amplitude)


def test_onsets_in_one_frame_are_floored_at_the_frame_interval():
    m = cm.measure_call(stream([[7.0], [7.0], [7.0]]), 7.0, **FAST)
    assert m.core_span_sec == 0.0
    assert m.mean_interval_sec == pytest.approx(0.1) and m.amplitude == pytest.approx(30.0)


def test_one_cell_is_not_coordination():
    m = cm.measure_call(stream([[3.0, 3.1, 3.2], [], []]), 3.1, **FAST)
    assert m.core_n_roi == 1 and math.isnan(m.amplitude)


def test_an_empty_aperture_measures_nothing():
    m = cm.measure_call(stream([[1.0], [50.0]]), 25.0, **FAST)
    assert m.n_events == 0 and math.isnan(m.core_span_sec) and math.isnan(m.amplitude)


def test_the_core_is_chosen_by_cells_not_by_events():
    """One cell firing four times is not four cells."""
    # 20.3 -> 20.9 is 0.6 s, past the 0.5 s gap (a gap of exactly 0.5 does not split).
    s = stream([[20.0, 20.1, 20.2, 20.3], [20.9], [21.0], [21.1]])
    m = cm.measure_call(s, 20.5, **FAST)
    assert m.core_n_roi == 3 and m.core_first_sec == pytest.approx(20.9)


def test_a_wide_call_is_searched_across_its_own_window():
    """A 10 s bin whose cluster sits 4 s from its centre: the aperture alone misses it."""
    s = stream([[14.0], [14.1], [14.2], [10.0]])
    narrow = cm.measure_call(s, 10.0, **FAST)
    wide = cm.measure_call(s, 10.0, **FAST, window=(5.0, 15.0))
    assert narrow.core_n_roi == 1
    assert wide.core_n_roi == 3 and wide.core_span_sec == pytest.approx(0.2)


def test_the_measure_does_not_depend_on_the_detectors_width():
    s = stream([[10.0], [10.1], [10.3], [10.4]])
    a = cm.measure_call(s, cm.call_center(9.9, 0.6), **FAST)      # a wide window
    b = cm.measure_call(s, cm.call_center(10.1, 0.2), **FAST)     # a narrow one
    assert a.row() == b.row()


def test_member_amp_and_width_are_the_member_events_own():
    s = stream([[10.0], [10.1], [10.2]], amps_by_roi=[[2.0], [4.0], [9.0]],
               widths_by_roi=[[0.5], [1.0], [1.5]])
    m = cm.measure_call(s, 10.1, **FAST)
    assert m.member_amp_median == pytest.approx(4.0)
    assert m.member_width_median == pytest.approx(1.0)


def test_a_width_without_its_rule_is_not_read():
    s = stream([[10.0], [10.1]], width_def=None)
    assert math.isnan(cm.measure_call(s, 10.05, **FAST).member_width_median)


def test_nonpositive_lengths_are_refused():
    with pytest.raises(ValueError):
        cm.measure_call(stream([[1.0]]), 1.0, gap_sec=0, half_aperture_sec=1, min_interval_sec=0.1)


def test_slow_gets_its_own_lengths():
    assert cm.defaults_for("slow") == (2.5, 5.0) and cm.defaults_for("FAST") == (0.5, 1.0)


def _tool():
    spec = importlib.util.spec_from_file_location("measure_calls", ROOT / "tools" / "measure_calls.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class _Slice:
    def __init__(self, streams, dt=0.1):
        self.streams, self.dt = streams, dt


def test_the_tool_keeps_every_detection_column_and_adds_the_measure(tmp_path):
    mc = _tool()
    rows = [{"slice_id": "s1", "stream": "fast", "detector": "coact", "region_idx": 1,
             "region_label": "baseline", "onset_sec": 10.0, "width_sec": 0.4, "n_roi": 4}]
    out = mc.measure_rows(rows, {"s1": _Slice({"fast": stream([[10.0], [10.1], [10.3], [10.4]])})})
    assert out[0]["region_label"] == "baseline" and out[0]["detector"] == "coact"
    assert out[0]["core_span_sec"] == pytest.approx(0.4)
    assert out[0]["gap_sec"] == 0.5 and out[0]["min_interval_sec"] == 0.1
    path = mc.write(out, tmp_path / "calls_measured.csv")
    assert "amplitude" in path.read_text(encoding="utf-8").splitlines()[0]


def test_the_tool_refuses_a_detection_the_folder_does_not_carry():
    mc = _tool()
    rows = [{"slice_id": "missing", "stream": "fast", "onset_sec": 1.0, "width_sec": 0.1}]
    with pytest.raises(SystemExit, match="does not carry"):
        mc.measure_rows(rows, {})
