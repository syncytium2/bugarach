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
                coact=dict(proposal=dict(name="rounds", unbracketed=True, bracketing=dict(
                    bracketed=False, unbracketed_axes=dict(
                        guard_sec=dict(side="low", value=0.0, reason="limit"))))),
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
    wcols = ["slice_id", "group", "region_idx", "label", "window_kind", "stream"]
    with (det / "windows.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, wcols)
        w.writeheader()
        for sid, grp, treat in (("synthA", "ORX", "TTX"), ("synthB", "DI", "senktide"),
                                ("synthC", "MALE", "TTX"), ("synthD", "OVX", "TTX")):
            for s in ("fast", "slow"):
                w.writerow(dict(slice_id=sid, group=grp, region_idx=1, label="baseline",
                                window_kind="baseline", stream=s))
                w.writerow(dict(slice_id=sid, group=grp, region_idx=2, label=treat,
                                window_kind="treatment", stream=s))
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
    assert any("guard_sec" in f for f in fast["coact:proposal"]["per"]["new"]["flags"])
    assert any(f.startswith("no pick") for f in fast["learned:line"]["per"]["new"]["flags"])
    page = (out / "index.html").read_text(encoding="utf-8")
    assert "over budget, precision change between quiet and busy backgrounds" in page
    assert "ruling 5: guard_sec at its limit" in page


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
    assert "count (bin-and-count rule)" in (out / "index.html").read_text(encoding="utf-8")
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
    assert "<b>Figure 1, the leaderboard.</b>" in page
    for t in ("Table 1.", "Table 2.", "Table 3.", "Table 4.", "Table 5."):
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
    assert names == ["figure1_leaderboard.svg", "leaderboard.json"]
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
