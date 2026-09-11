"""`tools/build_surrogate_report.py` on a synthetic run folder.

Pins the report's contract: one page per folder plus a summary, inline SVG only and a
page without SVG refused, the executive summary before any figure, the Cossart
dataset cited, the render gate refusing to pass without its stamped tools — and the
yardstick-reach box, which states when a Holm-adjusted column cannot be anything but
zero. That box exists because the first build showed every candidate, the known-bad
controls included, at 0% flagged: a column that could not have read otherwise.
Synthetic data only.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("elephant")      # the synthetic figures run the real generators

TOOL = Path(__file__).resolve().parents[1] / "tools" / "build_surrogate_report.py"


@pytest.fixture(scope="module")
def bsr():
    spec = importlib.util.spec_from_file_location("_bsr", TOOL)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_bsr"] = m
    spec.loader.exec_module(m)
    return m


def _write(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def _role(run: Path, role: str, stream: str, m_stats: int, K: int) -> None:
    d = run / role
    names = [("uniform_dither", "candidate"), ("circular_shift", "candidate"),
             ("do_nothing", "control")]
    cells, stats, dest, power, disc = [], [], [], [], []
    for name, kind in names:
        cid = f"{name}__J1fr" if name == "uniform_dither" else name
        cells.append({"stream": stream, "cell_id": cid, "name": name, "kind": kind,
                      "J": 1 if name == "uniform_dither" else "", "J_unit": "frames",
                      "status": "ok", "why": "", "K": K,
                      "seconds_per_roi_per_draw": 0.001,
                      "movement_rms_disp_frames": 0 if name == "do_nothing" else 3.0,
                      "movement_share_rois_unchanged": 1 if name == "do_nothing" else 0})
        for scope in ("all",):
            for i in range(m_stats):
                leak = name == "uniform_dither" and i == 0
                p = 2.0 / (K + 1) if leak else 1.0
                stats.append({"stream": stream, "cell_id": cid, "name": name,
                              "kind": kind, "scope": scope, "stat": f"subfloor@{i}fr",
                              "band_p": 1 / 101 if leak else 1.0,
                              "band_p_holm": min(1.0, m_stats / 101) if leak else 1.0,
                              "paired_p": p, "paired_p_holm": min(1.0, p * m_stats),
                              "band_flag": leak})
        for part in ("0.2", "0.5"):
            dest.append({"stream": stream, "cell_id": cid, "name": name,
                         "freeze_half": False, "participation": part, "K": 3,
                         "retained": 1.0 if name == "do_nothing" else 0.0,
                         "planted_visible": True})
        disc.append({"stream": stream, "cell_id": cid, "name": name, "status": "ok",
                     "accuracy": 0.6, "p_value": 0.01, "significant": True,
                     "void": False, "void_reason": ""})
    cells.append({**cells[0], "cell_id": "joint_isi__J1fr", "name": "joint_isi",
                  "status": "intractable", "why": "dropped before running, by measured cost"})
    power.append({"stream": stream, "control": "do_nothing", "cell_id": "do_nothing",
                  "scope": "all", "stat": "movement", "paired_p": 1.0,
                  "moved_paired": False, "band_flag": False, "delta": 0})
    _write(d / "cells.csv", cells)
    _write(d / "stats.csv", stats)
    _write(d / "destruction.csv", dest)
    _write(d / "control_power.csv", power)
    _write(d / "yardsticks.csv", [{"stream": stream, "scope": "all", "stat": "subfloor@0fr",
                                   "n_splits": 100, "neg_heldout_band": 0.05,
                                   "neg_heldout_paired": 0.04, "neg_synthetic_band": 0.06,
                                   "neg_synthetic_paired": 0.05}])
    _write(run / "discriminator" / role / "discriminator.csv", disc)
    (d / "meta.json").write_text(json.dumps({"n_recordings_loaded": 4, "jobs": 2,
                                             "settings": {"K": K, "min_K": 19}}),
                                 encoding="utf-8")


@pytest.fixture(scope="module")
def built(bsr, tmp_path_factory):
    run = tmp_path_factory.mktemp("run")
    _role(run, "steps_excluded", "fast", m_stats=65, K=99)
    _role(run, "cossart", "events", m_stats=11, K=40)
    assert bsr.main(["--run", str(run), "--no-gate"]) == 0
    return run


def test_one_page_per_folder_and_a_summary(built):
    for name in ("report_steps_excluded.html", "report_cossart.html", "report_summary.html"):
        text = (built / name).read_text(encoding="utf-8")
        assert text.startswith('<!doctype html><meta charset="utf-8">')
        assert "<svg" in text


def test_the_executive_summary_comes_before_any_figure(built):
    text = (built / "report_steps_excluded.html").read_text(encoding="utf-8")
    assert text.index('id="summary"') < text.index('id="fig1"') < text.index('id="fig4"')
    assert text.index('id="terms"') < text.index('id="fig1"')


def test_cossart_data_are_cited(built):
    for name in ("report_cossart.html", "report_summary.html"):
        assert "DANDI:000219" in (built / name).read_text(encoding="utf-8")


def test_the_reach_box_says_holm_cannot_flag_and_why(bsr, built):
    R = bsr.load_role(built, "steps_excluded")
    y = bsr.yardstick_reach(R)
    assert y["m"] == 65 and y["band_floor"] == pytest.approx(1 / 101)
    assert y["band_floor_holm"] > bsr.ALPHA and y["paired_floor_holm"] > bsr.ALPHA
    assert y["splits_needed"] == 1299 and y["K_needed"] == 2599
    text = (built / "report_steps_excluded.html").read_text(encoding="utf-8")
    assert "Holm-adjusted, can flag anything at these settings" in text and "1299" in text


def test_the_known_bad_leak_is_visible_unadjusted(bsr, built):
    R = bsr.load_role(built, "steps_excluded")
    rows = {r["name"]: r for r in bsr.candidate_rows(R, "fast")}
    assert rows["uniform_dither"]["band_q95"] > 0 and rows["uniform_dither"]["paired_raw"] > 0
    assert rows["uniform_dither"]["paired_holm"] == 0          # the reason for the box
    assert rows["do_nothing"]["band_q95"] == 0 and rows["do_nothing"]["paired_raw"] == 0


def test_a_page_without_svg_is_refused(bsr):
    with pytest.raises(SystemExit, match="no SVG"):
        bsr.refuse_without_svg("x.html", "<p>nothing drawn</p>")


def test_the_gate_never_passes_without_its_stamped_tools(bsr, built):
    with pytest.raises(SystemExit, match="missing stamped copies"):
        bsr.main(["--run", str(built)])
