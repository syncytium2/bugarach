"""tools/make_briefing.py: the night's briefing page, built from the run's own files.

Synthetic inputs only: a candidates.json in the scorer's schema, a calls.csv and windows.csv in
detect_with_floors.py's. The examples need the default dataset and are not built here
(``--no-examples``); what is tested is everything the page says about the leaderboard and where
its links go.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

import make_briefing as mb  # noqa: E402

REG = dict(f1=0.6, f1_without_decoys=0.9, recall=0.9, precision=0.5,
           precision_without_decoys=1.0, decoy_calls=1, n_planted=10, n_hit=9, merged_calls=0,
           n_detected=18, probe_calls_per_min=0.0, elevated_calls_per_hour_outside=0.0)


def _row(mid, lo, hi, *, f1=0.6, null=0.0, swing=0.0, probe=0.0):
    q = dict(REG, precision=0.5, probe_calls_per_min=probe)
    b = dict(REG, precision=0.5 + swing, probe_calls_per_min=probe)
    return dict(baseline_quiet=q, baseline_busy=b, null_calls_per_hour=null, mean_f1=f1,
                mean_f1_without_decoys=0.9, recordings_with_one_call=0, collapsed=False,
                paired_f1_vs_coact=dict(shipped=dict(mid=mid, lo=lo, hi=hi, n_seeds=24,
                                                     n_dropped=0)))


def _candidates(spacing: str, shift: float = 0.0) -> dict:
    res, benches = {}, {}
    for s in mb.STREAMS:
        res[s] = {
            "coact:shipped": _row(0.0, 0.0, 0.0),
            "coact:proposal": _row(0.04 + shift, 0.02, 0.06),
            "loco:shipped": _row(0.03 + shift, 0.01, 0.05, swing=0.5),      # over a budget
            "chorus:tube_%s_seed0.json" % s: _row(0.05 + shift, 0.02, 0.08),
            "chorus:tube_%s_seed1.json" % s: _row(0.01, -0.02, 0.04),
            "chorus:line_%s_seed2.json" % s: _row(-0.01, -0.03, 0.01, null=9.0),
        }
        benches[s] = dict(
            budget_null_per_hour=7.0, search_elapsed_min={}, detectors=dict(
                # As the night's searches recorded it: a guard of 0 is both an unbracketed axis
                # and an off-limit finding (ADR-0010 ruling 5).
                coact=dict(proposal=dict(name="rounds", unbracketed=True, bracketing=dict(
                    bracketed=False, unbracketed_axes=dict(
                        guard_sec=dict(side="low", value=0.0, reason="limit")),
                    findings=[dict(setting="guard_sec", value=0.0, kind="off_limit")]))),
                loco=dict(proposal=dict(name="shipped", unbracketed=False, bracketing={}))),
            chorus=dict(
                tube=dict(picked=f"tube_{s}_seed0.json", out_of_budget=None, train_rows=[]),
                line=dict(picked=None, train_rows=[], out_of_budget=dict(
                    best=f"line_{s}_seed2.json", note="no seed within budget"))))
    return dict(spacing=spacing, seeds_by_bench={s: [0, 23] for s in mb.STREAMS},
                results=res, benches=benches)


@pytest.fixture
def night(tmp_path: Path) -> Path:
    n = tmp_path / "night"
    for rel, spacing, shift in (("065/fresh-realistic", "realistic", 0.0),
                                ("065/fresh-bench", "bench", -0.02)):
        (n / rel).mkdir(parents=True)
        (n / rel / "candidates.json").write_text(json.dumps(_candidates(spacing, shift)))
    det = n / "065/review/detect"
    det.mkdir(parents=True)
    cols = ["slice_id", "group", "region_idx", "label", "window_kind", "stream", "detector",
            "variant", "onset_sec", "width_sec", "participants", "own_floor", "baseline_floor"]
    with (det / "calls.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, cols)
        w.writeheader()
        w.writerow(dict(slice_id="synthA", group="ORX", region_idx=1, label="baseline",
                        window_kind="baseline", stream="fast", detector="tube",
                        variant="unfloored", onset_sec=100, width_sec=1, participants=6,
                        own_floor=5, baseline_floor=5))
    wcols = ["slice_id", "group", "region_idx", "label", "window_kind", "stream", "win_start",
             "win_end", "hours"]
    with (det / "windows.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, wcols)
        w.writeheader()
        for sid, grp, treat in (("synthA", "ORX", "TTX"), ("synthB", "DI", "senktide"),
                                ("synthC", "MALE", "TTX"), ("synthD", "OVX", "TTX")):
            for s in ("fast", "slow"):
                w.writerow(dict(slice_id=sid, group=grp, region_idx=1, label="baseline",
                                window_kind="baseline", stream=s, win_start=0, win_end=1200,
                                hours=1 / 3))
                w.writerow(dict(slice_id=sid, group=grp, region_idx=2, label=treat,
                                window_kind="treatment", stream=s, win_start=1300, win_end=2500,
                                hours=1 / 3))
    pages = n / "065/review/pages"
    pages.mkdir(parents=True)
    for name in ("ORX_TTX_fast", "DI_TTX_fast", "DI_TTX_slow"):
        (pages / f"{name}.html").write_text("<meta charset='utf-8'><title>p</title>")
    return n


def _build(night: Path, tmp_path: Path, *extra) -> tuple[Path, dict]:
    out = night / "briefing"          # where the real page sits, so relative links match
    assert mb.main(["--night", str(night), "--out", str(out), "--no-examples", *extra]) == 0
    return out, json.loads((out / "briefing.json").read_text(encoding="utf-8"))


def test_the_board_sets_new_beside_old_and_orders_by_the_new_bench(night, tmp_path):
    _, m = _build(night, tmp_path)
    fast = m["board"]["fast"]
    mids = [e["per"]["new"]["mid"] for e in fast]
    assert mids == sorted(mids, reverse=True)
    tube = next(e for e in fast if e["id"] == "learned:tube")
    assert tube["per"]["new"]["mid"] == pytest.approx(0.05)
    assert tube["per"]["old"]["mid"] == pytest.approx(0.03)
    # Only the pick of a learned family is a row, not every seed.
    assert not any("seed1" in e["setting"] for e in fast)


def test_budget_failures_ruling_5_and_no_pick_are_marked(night, tmp_path):
    out, m = _build(night, tmp_path)
    fast = {e["id"]: e for e in m["board"]["fast"]}
    assert [f["name"] for f in fast["loco:shipped"]["per"]["new"]["budget_fails"]] == \
        ["precision_swing"]
    assert any("guard 0 s" in f and "ruling 5" in f
               for f in fast["coact:proposal"]["per"]["new"]["flags"])
    assert any(f.startswith("no pick") for f in fast["learned:line"]["per"]["new"]["flags"])
    page = (out / "index.html").read_text(encoding="utf-8")
    # Both benches fail alike, so it is said once, with digits enough to show the excess.
    assert "Over budget on both benches: precision swing: 0.500 against a limit of" in page
    assert "the elevated-rate test" in page and "probe" not in page


# THIS REPLACES AN ASSERTION THAT ENCODED THE DEFECT. The first version of this file asserted
# "ruling 5: guard_sec at its limit" on the page, which was the page crediting ADR-0010 ruling 5
# with every stop. Ruling 5 covers only a value that switches a setting off; a grid edge or a cap
# is part 1's "bracketed" (murderboard 2026-09-26, roles 2, 3 and 6).
def test_limit_marks_say_which_rule_governs_each_stop():
    def marks(axes=None, findings=None):
        return mb.limit_marks(dict(proposal=dict(name="rounds", unbracketed=True, bracketing=dict(
            unbracketed_axes=axes or {}, findings=findings or []))))
    off = marks({"guard_sec": dict(side="low", value=0.0, reason="limit")},
                [dict(setting="guard_sec", value=0.0, kind="off_limit")])
    assert off == ["guard 0 s, a value that turns the setting off: the search preferring \"off\" "
                   "is reported as a finding, not a tuned value (ADR-0010 ruling 5)"]
    edge = marks({"context_win_sec": dict(side="high", value=120.0, reason="grid_ceiling")})
    assert "ruling 5" not in edge[0] and "part 1" in edge[0] and "120 s" in edge[0]
    # A STOP AT A HARD LIMIT IS A FLAG, as the search's own rule has it (bracketing(): cap, limit
    # or edge alike make a candidate not adoptable). Round 2 of the murderboard exempted the count
    # offset's k = 0 as "by design", a reading no ADR makes (round 3, roles 6 and 7).
    floor = marks({"k_offset": dict(side="low", value=0, reason="limit")})
    assert "lower limit" in floor[0] and "part 1" in floor[0] and "ruling 5" not in floor[0]
    high = marks({"alpha": dict(side="high", value=0.5, reason="limit")})
    assert "upper limit" in high[0] and "lower" not in high[0]
    cap = marks(findings=[dict(setting="threshold_pctile", value=99.9921875, kind="cap")])
    assert "99.9922th percentile" in cap[0] and "extension cap" in cap[0]
    none = marks(findings=[dict(setting="merge_gap_sec", value=float("nan"), kind="off_limit")])
    assert none[0].startswith("merge gap none (no merge)")
    assert mb.limit_marks(dict(proposal=dict(name="shipped"))) == []


def test_an_unmeasured_budget_is_said_not_crashed_on():
    assert mb.budget_words(dict(name="elevated_out_quiet", value=None, limit=7.0)).endswith(
        "not measured (limit 7 calls/h)")
    assert mb.budget_words(dict(name="precision_swing", value=0.1036, limit=0.1)) == \
        "precision swing: 0.104 against a limit of 0.100"


def test_every_viewer_link_opens_in_the_one_viewer_tab(night, tmp_path):
    # On file:// Chrome refuses the folder picker the viewer's Reopen needs, so a fresh page per
    # link would ask for the folder every time. One named tab turns every later link into a
    # fragment change, which the viewer follows without reloading (murderboard 2026-09-26).
    out, _ = _build(night, tmp_path)
    page = (out / "index.html").read_text(encoding="utf-8")
    links = page.count("href='viewer.html#")
    assert links and page.count(f"target='{mb.VIEWER_TAB}'") == links


def test_a_shipped_setting_the_search_found_on_a_limit_is_marked(night, tmp_path):
    # When the search proposes nothing, its best is the shipped setting, and the bracketing record
    # can still put that on a limit (slow LoCo's guard 0 on the 2026-09-25 night).
    for rel in ("065/fresh-realistic", "065/fresh-bench"):
        p = night / rel / "candidates.json"
        c = json.loads(p.read_text())
        for s in mb.STREAMS:
            c["benches"][s]["detectors"]["loco"]["proposal"]["bracketing"] = dict(
                findings=[dict(setting="guard_sec", value=0.0, kind="off_limit")])
        p.write_text(json.dumps(c))
    _, m = _build(night, tmp_path)
    loco = next(e for e in m["board"]["slow"] if e["id"] == "loco:shipped")
    assert any("ruling 5" in f for f in loco["per"]["new"]["flags"])
    assert mb.flagged(loco)


def test_spearman_is_one_for_the_same_order_and_minus_one_reversed():
    assert mb.spearman([1, 2, 3, 4], [10, 20, 30, 40]) == pytest.approx(1.0)
    assert mb.spearman([1, 2, 3, 4], [4, 3, 2, 1]) == pytest.approx(-1.0)


def test_caption_times_floor_the_minute():
    # The first build printed 7m59s as 8m59s and 19m59.5s as 20m60s (f"{t/60:.0f}m...").
    assert mb.time_label(round(478.9)) == "7m59s"
    assert mb.time_label(round(1199.5)) == "20m"
    assert mb.time_label(round(100.0)) == "1m40s"
    assert mb.time_label(round(0.5)) == "0s"


def _call(sid, det, t, w=1.0, region="1", p=6, group="DI", stream="fast"):
    return dict(slice_id=sid, detector=det, onset_sec=str(t), width_sec=str(w), region_idx=region,
                participants=str(p), group=group, stream=stream, window_kind="baseline")


def test_examples_classify_span_to_span_and_pick_away_from_window_edges():
    calls = [_call("r1", "lead", 100), _call("r1", "coact", 101.5),       # agree (within 2.5 s)
             _call("r1", "lead", 200), _call("r1", "coact", 400),         # one each way
             _call("r1", "lead", 12.0, p=9)]                              # near the window start
    k = mb.classify(calls, "fast", "lead", "coact")
    assert [len(k[x]) for x in ("agree", "leader_only", "ref_only")] == [1, 2, 1]
    bounds = {("r1", "fast", "1"): (10.0, 500.0)}
    pick = mb.pick_one(k["leader_only"], bounds, set())
    assert float(pick["onset_sec"]) == 200         # the call 2 s inside the window is not shown
    assert mb.pick_one([_call("r1", "lead", 495)], bounds, set()) is None


def test_a_gap_of_exactly_the_tolerance_agrees():
    # The scorer's test is inclusive. Spans 2.5 s apart landed on "no match" by floating-point
    # error, and the page's one fast "only the leader" figure showed a call its own rule counts as
    # agreeing (murderboard 2026-09-26 round 3, roles 1, 4 and 6).
    a = _call("r1", "lead", 100.1, w=0.2)
    b = _call("r1", "coact", 100.3 + mb.TOL_SEC, w=0.0)
    assert mb._near(a, [b], mb.TOL_SEC) == [b]


def test_a_disagreement_example_is_a_call_the_other_did_not_make():
    # The median rule picked the one near-miss in each pool; the figure has to show a call clearly
    # beyond the tolerance when one exists (round 3, roles 4 and 8).
    bounds = {("r1", "fast", "1"): (0.0, 1000.0)}
    ref = [_call("r1", "coact", 300)]
    pool = [_call("r1", "lead", 304, p=5), _call("r1", "lead", 600, p=6),
            _call("r1", "lead", 303.5, p=7)]
    pick = mb.pick_one(pool, bounds, set(), ref)
    assert float(pick["onset_sec"]) == 600
    bins = mb.gap_bins(pool, ref)
    assert (bins["near"], bins["far"]) == (2, 1)


def test_rows_that_repeat_on_one_bench_are_counted_on_the_other(night, tmp_path):
    # Fast LoCo's proposal repeats CoactDetect's on the new bench only; on the old bench the two
    # differ and both count (round 3, roles 1, 3 and 6).
    for rel, shift in (("065/fresh-realistic", 0.0), ("065/fresh-bench", 0.002)):
        p = night / rel / "candidates.json"
        c = json.loads(p.read_text())
        r = c["results"]["fast"]
        r["loco:proposal"] = json.loads(json.dumps(r["coact:proposal"]))
        r["loco:proposal"]["mean_f1"] += shift
        r["loco:proposal"]["paired_f1_vs_coact"]["shipped"]["mid"] += shift
        p.write_text(json.dumps(c))
    _, m = _build(night, tmp_path)
    loco = next(e for e in m["board"]["fast"] if e["id"] == "loco:proposal")
    assert loco["same_as"].get("new") and not loco["same_as"].get("old")
    g = mb.glance(m)["fast"]
    assert g["old"]["n"] == g["new"]["n"] + 1


def test_combined_recordings_carry_no_viewer_link(night, tmp_path):
    # The viewer has no combined stream; a link would land on its error (round 3, role 8).
    out, _ = _build(night, tmp_path)
    page = (out / "index.html").read_text(encoding="utf-8")
    assert "stream=combined" not in page


def test_a_missing_old_bench_says_so_rather_than_vanishing(night, tmp_path):
    (night / "065/fresh-bench/candidates.json").unlink()
    out, m = _build(night, tmp_path)
    assert m["sources"]["old"]["present"] is False
    page = (out / "index.html").read_text(encoding="utf-8")
    assert "not scored yet" in page
    assert all(e["per"]["old"] is None for e in m["board"]["fast"])


def test_a_candidates_file_at_the_wrong_spacing_is_refused(night, tmp_path):
    p = night / "065/fresh-bench/candidates.json"
    c = json.loads(p.read_text())
    c["spacing"] = "realistic"
    p.write_text(json.dumps(c))
    with pytest.raises(SystemExit, match="spacing"):
        mb.build(night)


def test_the_count_row_waits_and_a_later_run_adds_it(night, tmp_path):
    out, m = _build(night, tmp_path)
    assert m["count_present"] is False
    assert "count (the simple rule)" in (out / "index.html").read_text(encoding="utf-8")
    c = _candidates("realistic")
    for s in mb.STREAMS:
        c["results"][s] = {"count:bin2s": _row(0.02, 0.0, 0.04)}
        c["benches"][s]["chorus"] = {}
    (night / "064/count").mkdir(parents=True)
    (night / "064/count/candidates.json").write_text(json.dumps(c))
    _, m2 = _build(night, tmp_path)
    assert m2["count_present"] is True
    assert any(e["id"] == "count:bin2s" for e in m2["board"]["slow"])


def test_rasters_are_in_the_house_group_order_and_link_the_viewer(night, tmp_path):
    out, _ = _build(night, tmp_path)
    page = (out / "index.html").read_text(encoding="utf-8")
    order = [page.index(f"<code>{sid}</code>") for sid in ("synthB", "synthD", "synthC", "synthA")]
    assert order == sorted(order), "rows are not DI, OVX, MALE, ORX"
    assert "viewer.html#slice=synthA&stream=fast" in page
    assert (out / "viewer.html").exists()
    # The group pages are linked relative to the page, where they already are.
    assert "../065/review/pages/DI_TTX_slow.html" in page


def test_figures_are_numbered_and_type_is_never_under_11_pt(night, tmp_path):
    out, _ = _build(night, tmp_path)
    page = (out / "index.html").read_text(encoding="utf-8")
    for s in ("a, the fast", "b, the slow", "c, the combined"):
        assert f"<b>Figure 1{s} stream.</b>" in page
    for t in ("Table 1.", "Table 2.", "Table 3.", "Table 4.", "Table 5.", "Table 6."):
        assert t in page
    import re
    # 11 pt is 14.67 px; the page's root is 17 px, so no rem or em size below 0.87.
    for v in re.findall(r"font-size:\s*([\d.]+)(px|rem|em)", page):
        n, unit = float(v[0]), v[1]
        assert (n if unit == "px" else n * 17) >= 14.67, v
    assert all(float(x) >= 14.67 for x in re.findall(r"font-size='([\d.]+)'", page))


def test_also_copies_the_simulation_half_and_nothing_that_names_a_recording(night, tmp_path):
    also = tmp_path / "repo_copy"
    _build(night, tmp_path, "--also", str(also))
    names = sorted(p.name for p in also.iterdir())
    assert names == ["figure1_combined.svg", "figure1_fast.svg", "figure1_slow.svg",
                     "leaderboard.json"]
    for p in also.iterdir():
        assert "synth" not in p.read_text(encoding="utf-8")


def test_a_later_files_coactdetect_rows_do_not_replace_the_nights(night, tmp_path):
    c = _candidates("realistic", shift=0.5)       # its CoactDetect proposal would read +0.54
    for s in mb.STREAMS:
        c["results"][s]["count_sliding:proposal"] = _row(0.02, 0.0, 0.04, swing=0.5)
        c["benches"][s]["chorus"] = {}
        c["benches"][s]["detectors"]["count_sliding"] = dict(proposal=dict(
            name="rounds", unbracketed=False, bracketing=dict(bracketed=True)))
    (night / "064/count/fresh-realistic").mkdir(parents=True)
    (night / "064/count/fresh-realistic/candidates.json").write_text(json.dumps(c))
    out, m = _build(night, tmp_path)
    fast = {e["id"]: e for e in m["board"]["fast"]}
    assert fast["coact:proposal"]["per"]["new"]["mid"] == pytest.approx(0.04)
    row = fast["count_sliding:proposal"]
    assert row["label"] == "count (sliding)"
    assert [f["name"] for f in row["per"]["new"]["budget_fails"]] == ["precision_swing"]
    assert row["per"]["old"] is None                # not scored on the old bench: said, not hidden
