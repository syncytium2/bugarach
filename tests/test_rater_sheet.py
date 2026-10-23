"""The rater sheet pilot: rows, key, export parsing and scoring (tools/rater_sheet/)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "rater_sheet"))

import make_pilot  # noqa: E402
import score_export  # noqa: E402
from bugarach.score import TOL_SEC  # noqa: E402


def test_build_is_deterministic_balanced_and_has_no_decoys():
    rows, key = make_pilot.build()
    rows2, key2 = make_pilot.build()
    assert rows == rows2 and key == key2
    assert len(rows) == 2 * len(make_pilot.CONDITIONS)
    fields = [k["field"] for k in key.values()]
    assert fields.count("fitted") == fields.count("flat")
    for rid, r in rows.items():
        assert r["n_roi"] == 32 and len(r["trains"]) == 32
        assert all(0.0 <= t <= make_pilot.DURATION_SEC for tr in r["trains"] for t in tr)
        k = key[rid]
        assert "decoy" not in json.dumps(k) and "distractor" not in json.dumps(k)  # ADR-0019
        assert r["duration_sec"] == make_pilot.DURATION_SEC == 900.0   # one x-axis length
        assert len(k["events"]) == (make_pilot.EVENTS_PER_ROW if k["planted"] else 0)
        if k["planted"]:
            assert sorted({e["participation"] for e in k["events"]}) == sorted(make_pilot.LEVELS)


def test_the_row_length_fits_every_cossart_recording():
    a = json.loads((Path(__file__).resolve().parents[1] / "docs/learned/assessment_cossart.json").read_text())
    assert min(float(r["window_sec"]) for r in a["rows"]) >= make_pilot.DURATION_SEC


def test_the_demo_row_is_not_a_scored_row():
    d = make_pilot.demo_row()
    rows, key = make_pilot.build()
    assert d["row"]["id"] == "demo" and "demo" not in key
    lane_train = d["row"]["trains"][d["lane"]]
    assert any(abs(t - d["event_time"]) < 1.0 for t in lane_train)


def test_the_survey_carries_no_answer_key():
    rows, _ = make_pilot.build()
    js = make_pilot.question_js(rows)
    for word in ("fitted", "flat", "participation", "jitter", "events\"", "rois"):
        assert word not in js.split("var RATER_ROWS = ", 1)[1].split(";", 1)[0]


def _csv(tmp_path, cells):
    import csv
    p = tmp_path / "export.csv"
    with open(p, "w", newline="", encoding="utf-8") as f:   # quoted, as Qualtrics writes it
        w = csv.writer(f)
        w.writerow(["ResponseId"] + [f"{i}_QID1_TEXT" for i in range(len(cells))])
        w.writerow(["Response ID"] + ["row"] * len(cells))
        w.writerow(['{"ImportId":"_recordId"}'] + ["x"] * len(cells))
        w.writerow(["R_abc"] + cells)
    return p


def test_a_perfect_rater_scores_one_and_an_empty_one_zero(tmp_path):
    rows, key = make_pilot.build()
    perfect = [f"row={rid};real={1.0 if k['field'] == 'fitted' else -1.0};"
               f"marks={','.join(f'{e['time']:.1f}' for e in k['events'])}" for rid, k in key.items()]
    s = score_export.score_response(score_export.parse_export(_csv(tmp_path, perfect))["R_abc"], key)
    assert s["recall"] == 1.0 and s["precision"] == 1.0 and s["false_marks"] == 0
    assert s["auc_fitted_vs_flat"] == 1.0 and s["dprime_fitted_vs_flat"] > 2
    assert s["recall_by"]["participation 0.10"]["recall"] == 1.0
    blank = [f"row={rid};real=0.00;marks=" for rid in key]
    s = score_export.score_response(score_export.parse_export(_csv(tmp_path, blank))["R_abc"], key)
    assert s["recall"] == 0.0 and s["precision"] is None
    assert s["auc_fitted_vs_flat"] == 0.5 and s["dprime_fitted_vs_flat"] == 0.0


def test_matching_is_one_to_one_and_uses_the_bench_tolerance():
    ev = [{"time": 10.0}, {"time": 30.0}]
    hit, fm = score_export.match([10.2, 10.4, 30.0 + TOL_SEC + 0.1], ev)
    assert hit == [True, False] and fm == 2
