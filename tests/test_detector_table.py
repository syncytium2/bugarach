"""The one-table assembly: what it may combine, and what it must keep apart.

The whole risk in putting twelve detectors and two experiments on one page is a
reader averaging two columns that are not about the same thing, so these pin the
separations rather than the arithmetic:

* the scored half comes from the bake-off and the observed half from the folder, and
  no number crosses between them;
* the six show `calibrated -> shipped` because the bake-off tuned one instrument and
  the folder was scored with another; the learned rows show a threshold, because for
  them one fit produced both halves;
* a row is flagged on participation only when its lone rate approaches its OWN chance
  rate — the check that two earlier drafts got wrong, in the same direction, by
  reading a raw percentage that the detector's declared width sets;
* detectors come out in the glossary's order for the six and arrival after, so a
  second detections file cannot silently reorder the page.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "src"))

import make_detector_table as mod  # noqa: E402

SLICES = "slice_id,frame_interval_sec,group_id\ns1,0.1,MALE\n"
REGIONS = ("slice_id,region_idx,label,start_sec,end_sec,"
           "analysis_start_sec,analysis_end_sec\n"
           "s1,1,baseline,0,600,0,600\n"
           "s1,2,APV+CNQX+GZ,600,1200,600,1200\n")
#: Three ROIs fire together at 100, 200, 400, 500 and 800 s; ROI 1 fires alone at
#: 300 s and 700 s. The field is otherwise empty, so a window thrown at random almost
#: always lands on nothing — chance is near 100 %, which is what makes the ratio the
#: only readable quantity here.
EVENTS = ("roi,time_sec,stream\n"
          + "".join(f"{roi},{t}.0,fast\n"
                    for t in (100, 200, 400, 500, 800) for roi in (1, 2, 3))
          + "1,300.0,fast\n1,700.0,fast\n")
#: CoactDetect calls the five crowds and one lone moment; tube_ratio calls only the
#: two lone ones.
DETECTIONS = (
    "slice_id,stream,detector,mode,region_idx,region_label,onset_sec,width_sec\n"
    + "".join(f"s1,fast,coact,threshold,{1 if t < 600 else 2},"
              f"{'baseline' if t < 600 else 'APV+CNQX+GZ'},{t}.0,0.1\n"
              for t in (100, 200, 400, 500, 800, 300))
    + "s1,fast,tube_ratio,learned,1,baseline,300.0,0.1\n"
      "s1,fast,tube_ratio,learned,2,APV+CNQX+GZ,700.0,0.1\n"
)


def _fake_bakeoff(detectors):
    """A bake-off shaped like the real one, with one fold and no ambition."""
    def entry(f1, knob=None, threshold=None):
        return dict(
            f1=dict(mean=f1, min=f1, max=f1), recall=dict(mean=0.9),
            precision=dict(mean=0.8), hot_fa=dict(mean=0.0), n_params=0,
            per_fold=[dict(distractor_hits=2, n_planted=30, hot_fa=0.0,
                           knob=knob, knob_value=knob, threshold=threshold)])
    return {
        "folds": 1, "seeds_per_fold": 2,
        "spec": {"n_distractors": 3, "hot_window": [0.0, 600.0]},
        "hand_written": {"coact": entry(0.77, knob=0.001)},
        "learned": {"tube_ratio": entry(0.70, threshold=0.99)},
    }


def _run(tmp_path: Path, detectors=("coact", "tube_ratio")):
    folder = tmp_path / "folder"
    folder.mkdir()
    (folder / "slices.csv").write_text(SLICES)
    (folder / "regions.csv").write_text(REGIONS)
    (folder / "s1.csv").write_text(EVENTS)
    run = tmp_path / "run"
    (run / "03_bakeoff").mkdir(parents=True)
    (run / "04_detect").mkdir(parents=True)
    (run / "03_bakeoff" / "bakeoff.json").write_text(json.dumps(_fake_bakeoff(detectors)))
    (run / "04_detect" / "detections.csv").write_text(DETECTIONS)
    return run, folder


def _rows(tmp_path, **kw):
    run, folder = _run(tmp_path)
    rows, *_ = mod.build_rows(run, folder, baseline="baseline",
                              treatment="APV+CNQX+GZ", pad=0.25, **kw)
    return {r["key"]: r for r in rows}


def test_the_two_halves_do_not_borrow_from_each_other(tmp_path):
    """F1 comes only from the bake-off; call counts only from the folder."""
    by = _rows(tmp_path)
    assert by["coact"]["f1"] == pytest.approx(0.77)
    assert by["tube_ratio"]["f1"] == pytest.approx(0.70)
    # the counts are the detections file's, not 30 (planted) or 3 (distractors)
    assert by["coact"]["calls"] == 6 and by["tube_ratio"]["calls"] == 2
    # and `calls` is every period, so it need not equal the two named ones
    assert by["coact"]["calls_in_the_two_periods"] == 6


def test_the_six_show_calibrated_against_shipped_and_the_learned_show_a_threshold(tmp_path):
    by = _rows(tmp_path)
    from bugarach.bench import OPERATING_POINTS
    shipped = OPERATING_POINTS["coact"].params[OPERATING_POINTS["coact"].knob]
    assert "0.001" in by["coact"]["knob"] and f"{shipped:g}" in by["coact"]["knob"]
    assert by["tube_ratio"]["knob"].startswith("threshold")


def test_a_lone_call_is_counted_and_a_crowded_one_is_not(tmp_path):
    by = _rows(tmp_path)
    # coact called five 3-ROI moments and one lone one
    assert by["coact"]["pct_lone"] == pytest.approx(100.0 / 6.0)
    # tube_ratio called only lone moments
    assert by["tube_ratio"]["pct_lone"] == pytest.approx(100.0)


def test_the_flag_reads_the_ratio_to_chance_not_the_percentage(tmp_path):
    """The defect two drafts had: a raw percentage flags a detector its width sets.

    In this fixture almost every random window is lone, so chance is near 1.0 and a
    detector at 17 % lone is six times BETTER than chance — no flag. Nothing about
    the percentage alone can distinguish that from a real failure.
    """
    by = _rows(tmp_path)
    assert by["coact"]["pct_chance"] > 90.0
    assert by["coact"]["lone_vs_chance"] < mod.LONE_VS_CHANCE_FLAG
    assert "lone calls" not in by["coact"]["flags"]
    # and the one placing every call on a lone moment, at ~chance, does get flagged
    assert by["tube_ratio"]["lone_vs_chance"] >= mod.LONE_VS_CHANCE_FLAG
    assert "approaching random placement" in by["tube_ratio"]["flags"]


def test_the_page_stays_inside_the_renderer_viewport(tmp_path):
    """The screenshot viewport CUTS rather than scrolls, and it did once."""
    run, folder = _run(tmp_path)
    rows, bake, _s, missing, n_dis, probe_min = mod.build_rows(
        run, folder, baseline="baseline", treatment="APV+CNQX+GZ", pad=0.25)
    html = mod.page_html(rows, bake, run=run, folder=folder, baseline="baseline",
                         treatment="APV+CNQX+GZ", n_dis=n_dis, probe_min=probe_min,
                         pad=0.25, missing=missing)
    assert mod.PAGE_PX <= 1120
    assert f"max-width:{mod.PAGE_PX}px" in html
    # both halves are on the one page, and each says which experiment it is
    assert "SIMULATED" in html and "no ground truth" in html
