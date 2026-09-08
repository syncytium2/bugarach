"""The participation probe's two halves, each checked without fitting a model.

The probe answers *"how many ROIs were firing when this detector called?"*, so the
things worth pinning are the counting rules — every one of them is a place the
answer could be quietly wrong in the flattering direction:

* an ROI is counted ONCE however many onsets it contributed, because the question
  is how many cells fired together and a bursting cell is one cell;
* the pad widens the call's own span on BOTH sides, and it is timing tolerance, not
  participation tolerance — an ROI outside it is not a participant;
* a call matching no ROI at all counts as lone, not as missing data;
* the ladder holds the background fixed across k, so the only thing that changes
  between two points on one curve is how many cells fired in the planted frame.

The ladder's own arithmetic is checked against a stub model — a real fit takes
minutes and one training seed would make the assertion about that seed rather than
about the probe.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "src"))

import probe_participation as mod  # noqa: E402

SLICES = "slice_id,frame_interval_sec,group_id\ns1,0.1,MALE\n"
REGIONS = ("slice_id,region_idx,label,start_sec,end_sec,"
           "analysis_start_sec,analysis_end_sec\n"
           "s1,1,baseline,0,600,0,600\n")
#: ROI 1 bursts four times inside one 0.4 s window and no other ROI joins it; ROI 2
#: and 3 fire together at 200 s; ROI 4 fires at 300.6 s, just outside a 0.25 s pad
#: on a call ending at 300.0 s.
EVENTS = ("roi,time_sec,stream\n"
          "1,100.0,fast\n1,100.1,fast\n1,100.2,fast\n1,100.3,fast\n"
          "2,200.0,fast\n3,200.0,fast\n"
          "5,300.0,fast\n4,300.6,fast\n")
DETECTIONS = (
    "slice_id,stream,detector,mode,region_idx,region_label,onset_sec,width_sec\n"
    "s1,fast,burst_only,learned,1,baseline,100.0,0.4\n"
    "s1,fast,burst_only,learned,1,baseline,200.0,0.1\n"
    "s1,fast,edge,learned,1,baseline,300.0,0.0\n"
    "s1,fast,empty,learned,1,baseline,450.0,0.1\n"
)


def _folder(tmp_path: Path):
    folder = tmp_path / "folder"
    folder.mkdir()
    (folder / "slices.csv").write_text(SLICES)
    (folder / "regions.csv").write_text(REGIONS)
    (folder / "s1.csv").write_text(EVENTS)
    det = tmp_path / "detections.csv"
    det.write_text(DETECTIONS)
    return folder, det


def test_a_bursting_cell_is_one_cell(tmp_path):
    """Four onsets from ROI 1 inside the call span are one participant, so lone."""
    folder, det = _folder(tmp_path)
    per = mod.tally(det, folder, pad=0.25)
    assert per["burst_only"]["n"] == 2
    # the 100 s call sees only ROI 1; the 200 s call sees ROIs 2 and 3
    assert per["burst_only"]["lone"] == 1


def test_the_pad_is_timing_tolerance_and_has_an_edge(tmp_path):
    folder, det = _folder(tmp_path)
    # ROI 4 fires 0.6 s after the call, so at pad 0.25 only ROI 5 participates
    assert mod.tally(det, folder, pad=0.25)["edge"]["lone"] == 1
    # widen past it and the call is no longer lone — the count moved because the
    # tolerance moved, which is the only thing that may move it
    assert mod.tally(det, folder, pad=1.0)["edge"]["lone"] == 0


def test_a_call_matching_nothing_counts_as_lone(tmp_path):
    folder, det = _folder(tmp_path)
    per = mod.tally(det, folder, pad=0.25)
    assert per["empty"]["n"] == 1 and per["empty"]["lone"] == 1


class _Stub:
    """A model that scores the fraction of cells active in each frame.

    Not a coordination detector — a per-frame population rate — but it is the
    behaviour the ladder must be able to render: monotone in k, and unchanged by
    anything the probe is not varying.
    """

    n_params = 0
    threshold = 0.5
    dt = 0.1
    merge_gap_frames = 20
    model = None

    def __init__(self):
        self.model = lambda x: x.mean(dim=1)


def test_the_ladder_is_monotone_in_k_for_a_model_that_counts():
    pytest.importorskip("torch")
    rows = mod.ladder([("stub", _Stub())], n_roi=10, duration_sec=20.0, dt=0.1,
                      backgrounds=[0.0], k_max=4)
    scores = [r["score"] for r in sorted(rows, key=lambda r: r["k"])]
    assert scores == sorted(scores)
    assert scores[0] == pytest.approx(0.0)          # k=0 in a silent field
    assert scores[4] == pytest.approx(0.4)          # 4 of 10 cells


def test_the_ladder_varies_only_k_within_one_curve():
    """Same background draw for every k, so two points differ by the plant alone."""
    pytest.importorskip("torch")
    rows = mod.ladder([("stub", _Stub())], n_roi=8, duration_sec=20.0, dt=0.1,
                      backgrounds=[0.0, 0.05], k_max=3, seed=7)
    again = mod.ladder([("stub", _Stub())], n_roi=8, duration_sec=20.0, dt=0.1,
                       backgrounds=[0.0, 0.05], k_max=3, seed=7)
    assert [r["score"] for r in rows] == [r["score"] for r in again]
    # the planted frame is cleared before k cells are placed in it, so k is exactly
    # the number of participants there however busy the background is
    busy = {r["k"]: r["score"] for r in rows if r["bg_hz"] == 0.05}
    assert busy[3] >= busy[0]
    assert np.isfinite(list(busy.values())).all()


def test_detections_and_folder_go_together():
    with pytest.raises(SystemExit):
        mod.main(["--spec", "nope.json", "--detections", "d.csv"])
