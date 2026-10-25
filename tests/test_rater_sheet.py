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


# ---- the separation rows (Tony, 2026-10-25) ----

PILOT_DIGEST = "ffa5c41ab59286ea4677602f4d2f57bfc74252cf8ee51bd29928ccb664098fde"


def test_the_pilots_ten_rows_did_not_change():
    import hashlib
    rows, key = make_pilot.build()
    assert hashlib.sha256(json.dumps([rows, key], sort_keys=True).encode()).hexdigest() == PILOT_DIGEST


def test_separation_rows_plant_every_separation_and_the_singles():
    rows, key = make_pilot.build_separation()
    assert sorted(rows) == ["r11", "r12", "r13", "r14"]
    for rid, k in key.items():
        assert k["kind"] == "separation" and rows[rid]["duration_sec"] == make_pilot.DURATION_SEC
        pairs = [i for i in k["items"] if i["kind"] == "pair"]
        singles = [i for i in k["items"] if i["kind"] == "single"]
        assert sorted(i["delta_sec"] for i in pairs) == sorted(make_pilot.SEP_DELTAS_SEC)
        assert len(singles) == make_pilot.SEP_SINGLES
        for it in k["items"]:
            for ev in it["events"]:
                assert len(ev["rois"]) == k["n_part"] == 6
                for r, t in zip(ev["rois"], ev["onsets"]):
                    assert round(t, 1) in rows[rid]["trains"][r]
        for p in pairs:
            a, b = p["events"]
            assert not set(a["rois"]) & set(b["rois"])         # two groups of cells
            assert abs((b["time"] - a["time"]) - p["delta_sec"]) < 1e-6
        starts = sorted(i["events"][0]["time"] for i in k["items"])
        ends = sorted(i["events"][-1]["time"] for i in k["items"])
        assert all(s2 - e1 > 30 for e1, s2 in zip(ends, starts[1:]))   # items never interact


def _sep_answers(rule):
    rows, key = make_pilot.build_separation()
    cells = []
    for rid, k in key.items():
        marks = []
        for it in k["items"]:
            marks += rule(it)
        cells.append(f"row={rid};real=0.00;marks={','.join(f'{m:.1f}' for m in marks)};"
                     f"spans={','.join('20.0' for _ in marks)}")
    return key, cells


def test_separation_scoring_at_the_extremes_and_in_between(tmp_path):
    both = lambda it: [e["median_onset"] for e in it["events"]]
    key, cells = _sep_answers(both)
    resp = score_export.parse_export(_csv(tmp_path, cells))["R_abc"]
    assert resp["r11"]["spans"][0] == 20.0
    out = score_export.separation_outcomes(resp, key)
    # A mark on each group's median onset resolves every pair whose two medians differ. Where they
    # coincide (wide timing at 0.5 s can do that), the pair holds no second cluster to find.
    assert all(o["resolved"] for o in out if o["kind"] == "pair" and o["realized_delta_sec"] > 0)
    assert all(not o["resolved"] for o in out if o["kind"] == "pair" and o["realized_delta_sec"] == 0)
    sep = score_export.score_separation(out)["overall"]
    assert sep["split_rate"] == 0.0 and sep["p_resolved_by_delta"]["8"]["resolved"] == 1.0

    merged = lambda it: [sum(e["median_onset"] for e in it["events"]) / len(it["events"])]
    key, cells = _sep_answers(merged)
    resp = score_export.parse_export(_csv(tmp_path, cells))["R_abc"]
    sep = score_export.score_separation(score_export.separation_outcomes(resp, key))["overall"]
    assert all(v["resolved"] == 0.0 and v["detected"] == 1.0 for v in sep["p_resolved_by_delta"].values())
    assert "above the largest" in sep["fit"]["note"]

    from_two = lambda it: (both(it) if it["kind"] == "single" or it["delta_sec"] >= 2 else merged(it))
    key, cells = _sep_answers(lambda it: from_two(it) * (2 if it["kind"] == "single" else 1))
    resp = score_export.parse_export(_csv(tmp_path, cells))["R_abc"]
    sep = score_export.score_separation(score_export.separation_outcomes(resp, key))["overall"]
    assert sep["split_rate"] == 1.0                              # every single marked twice
    key, cells = _sep_answers(from_two)
    resp = score_export.parse_export(_csv(tmp_path, cells))["R_abc"]
    sep = score_export.score_separation(score_export.separation_outcomes(resp, key))["overall"]
    assert 1.0 <= sep["fit"]["delta50_sec"] <= 2.0 and sep["split_rate"] == 0.0


def test_separation_rows_stay_out_of_the_pilot_score(tmp_path):
    rows, key = make_pilot.build()
    srows, skey = make_pilot.build_separation()
    key = dict(key, **skey)
    cells = [f"row={rid};real=0.00;marks=" for rid in key]
    s = score_export.score_response(score_export.parse_export(_csv(tmp_path, cells))["R_abc"], key)
    assert s["rows_answered"] == 10 and s["events"] == sum(len(k["events"]) for k in make_pilot.build()[1].values())
