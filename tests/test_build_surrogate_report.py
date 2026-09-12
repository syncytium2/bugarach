"""`tools/build_surrogate_report.py` on a synthetic run folder.

Pins the report's contract — one page per folder plus a summary, inline SVG only, a page
without SVG refused, the problem and its figure before the evidence, the Cossart dataset
cited, the render gate refusing to pass without its stamped tools — and, row by row, the
defects the 2026-09-11 murderboard found in the first build. Each of those was a number
that read as a result and was not one, so each gets a test that fails if it returns:

* the discriminator's own control rows pooled into the candidate they validate;
* a candidate whose cells cannot reach alpha shown as "0% flagged" (and that caveat
  dropped on the cross-folder page);
* the FOUNDATIONS §9 reconciliation computed on the Holm-adjusted P the page says can
  never flag, so it read 0/0 by construction;
* the graded freeze-half control measured and filtered out, while its cell was counted
  as a circular-shift candidate cell;
* destruction reported as a property of a candidate on a twin where the measure cannot
  register removal at all.

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
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def _role(run: Path, role: str, stream: str, m_stats: int, unit: str, n_roi: int,
          J_top: float, scopes: tuple = ("all",)) -> None:
    """One folder: two candidates, one control, the freeze-half destruction cell.

    uniform_dither runs at K = 99 (its paired yardstick can reach alpha) and leaks on one
    statistic; circular_shift runs at K = 19 (it cannot); do_nothing moves nothing.
    """
    d = run / role
    # Two radii for uniform dither, because saturation is a property of J: at the small
    # one more ROIs stay inside the coincidence bin than the assessor's scan reaches, at
    # the large one they do not. The second carries no discriminator row — it exists to
    # give the sweep two ends, not to double the candidate's results.
    J_small = J_top / 25 if unit == "sec" else J_top / 8
    spec = [("uniform_dither", "candidate", 99, J_top, 3.0, 0.9, True),
            ("uniform_dither", "candidate", 99, J_small, 3.0, 0.9, False),
            ("circular_shift", "candidate", 19, None, 2804.0, 0.9, True),
            ("do_nothing", "control", 99, None, 0.0, 0.0, True)]
    cells, stats, dest, power, disc = [], [], [], [], []
    for name, kind, K, J, rms, moved, with_disc in spec:
        cid = f"{name}__J{J:g}{'s' if unit == 'sec' else 'fr'}" if J else name
        cells.append({"stream": stream, "cell_id": cid, "name": name, "kind": kind,
                      "J": J if J else "", "J_unit": unit, "f": "", "status": "ok", "why": "",
                      "K": K, "seconds_per_roi_per_draw": 0.001,
                      "movement_rms_disp_frames": rms, "movement_share_moved": moved,
                      "movement_share_rois_unchanged": 0.0 if moved else 1.0})
        for scope in scopes:
            for i in range(m_stats):
                # statistic 0 leaks pooled and in G1; statistic 1 leaks in G1 ALONE, which
                # is the disagreement FOUNDATIONS §9 asks about and the Holm-adjusted
                # version of this check could never see.
                leak = name == "uniform_dither" and (
                    (i == 0 and scope in ("all", "G1")) or (i == 1 and scope == "G1"))
                p = 2.0 / (K + 1) if leak else 1.0
                stats.append({"stream": stream, "cell_id": cid, "name": name, "kind": kind,
                              "scope": scope, "stat": f"subfloor@{i}fr",
                              "band_p": 1 / 101 if leak else 1.0,
                              "band_p_holm": min(1.0, m_stats / 101) if leak else 1.0,
                              "paired_p": p, "paired_p_holm": min(1.0, p * m_stats),
                              "band_flag": leak})
        for part in ("0.2", "0.5"):
            for K_roi in (3, 8):
                dest.append({"stream": stream, "cell_id": cid, "name": name,
                             "freeze_half": False, "participation": part, "K": K_roi,
                             "retained": 1.0 if name == "do_nothing" else 0.5,
                             "planted_visible": True})
        # the discriminator: the candidate's own cells, then ITS controls, which are not
        # results about the candidate and must not widen its range
        if with_disc:
            disc.append({"stream": stream, "cell_id": cid, "name": name, "kind": "candidate",
                         "status": "ok", "accuracy": 0.62, "p_value": 0.01,
                         "significant": True, "void": False, "void_reason": "",
                         "powered": True, "n_mice": 44, "required_mice": 20})
    disc.append({"stream": stream, "cell_id": "control:pos_J1", "name": "uniform_dither",
                 "kind": "discriminator_control", "status": "ok", "accuracy": 0.11,
                 "p_value": 0.01, "significant": True, "void": "", "void_reason": "",
                 "powered": "", "n_mice": 44, "required_mice": 20})
    # the graded destruction control: its own cell, NOT a circular-shift candidate cell
    cells.append({"stream": stream, "cell_id": "freeze_half", "name": "circular_shift",
                  "kind": "candidate", "J": "", "J_unit": unit, "f": "", "status": "ok",
                  "why": "", "K": "", "seconds_per_roi_per_draw": "",
                  "movement_rms_disp_frames": "", "movement_share_moved": "",
                  "movement_share_rois_unchanged": ""})
    for K_roi in (3, 8):
        dest.append({"stream": stream, "cell_id": "freeze_half", "name": "circular_shift",
                     "freeze_half": True, "participation": "0.5", "K": K_roi,
                     "retained": 0.4, "planted_visible": True})
    cells.append({**cells[0], "cell_id": "joint_isi__J1fr", "name": "joint_isi",
                  "status": "intractable", "K": "",
                  "why": "dropped before running, by measured cost"})
    power.append({"stream": stream, "control": "do_nothing", "cell_id": "do_nothing",
                  "scope": "all", "stat": "movement", "paired_p": 1.0,
                  "moved_paired": False, "band_flag": False, "delta": 0})
    power.append({"stream": stream, "control": "edge_thinning",
                  "cell_id": "circular_shift", "scope": "all", "stat": "edge_density",
                  "paired_p": 0.0556, "moved_paired": False, "band_flag": True, "delta": 1})
    _write(d / "cells.csv", cells)
    _write(d / "stats.csv", stats)
    _write(d / "destruction.csv", dest)
    _write(d / "control_power.csv", power)
    # subfloor@0fr has a ZERO-WIDTH band — its real value is identically 0, so "outside
    # the 95% band" degenerates to "not exactly 0" — and a synthetic negative rate above
    # alpha, which is the statistic the page promises to mark where it cites it.
    _write(d / "yardsticks.csv", [{"stream": stream, "scope": "all", "stat": "subfloor@0fr",
                                   "n_splits": 100, "neg_heldout_band": 0.05,
                                   "neg_heldout_paired": 0.04, "neg_synthetic_band": 0.06,
                                   "neg_synthetic_paired": 0.05,
                                   "band_q025": 0.0, "band_q975": 0.0},
                                  {"stream": stream, "scope": "all", "stat": "subfloor@1fr",
                                   "n_splits": 100, "neg_heldout_band": 0.04,
                                   "neg_heldout_paired": 0.04, "neg_synthetic_band": 0.03,
                                   "neg_synthetic_paired": 0.02,
                                   "band_q025": 0.1, "band_q975": 0.9}])
    _write(run / "discriminator" / role / "discriminator.csv", disc)
    (d / "meta.json").write_text(json.dumps({
        "n_recordings_loaded": 4, "jobs": 2, "folder": "C:\\exports\\" + role,
        "settings": {"K": 99, "min_K": 19, "destruction_draws": 19,
                     "destruction_assess_surrogates": 200},
        "streams": {stream: {"destruction_twins": {"n_roi": n_roi, "dt": 0.1,
                                                   "coincidence_half_window_frames": 2}}},
    }), encoding="utf-8")


@pytest.fixture(scope="module")
def built(bsr, tmp_path_factory):
    run = tmp_path_factory.mktemp("run")
    # 13 statistics in five scopes = the real folder's 65 checks per cell; a 31-ROI twin
    # at J = 2.5 s, where the destruction measure can register removal
    _role(run, "steps_excluded", "fast", m_stats=13, unit="sec", n_roi=31, J_top=2.5,
          scopes=("all", "G1", "G2", "G3", "G4"))
    # 11 checks in one scope, and a 566-ROI twin at J = 32 frames, where it cannot —
    # about 22 ROIs stay inside the coincidence bin whatever the surrogate does
    _role(run, "cossart", "events", m_stats=11, unit="frames", n_roi=566, J_top=32)
    (run / "run_notes.json").write_text(json.dumps({"first_agent": {"run_folder": str(run)},
                                                    "resumed_run": {"resumed": "08:12"}}),
                                        encoding="utf-8")
    assert bsr.main(["--run", str(run), "--no-gate"]) == 0
    return run


def _page(built, name):
    return (built / name).read_text(encoding="utf-8")


def test_one_page_per_folder_and_a_summary(built):
    for name in ("report_steps_excluded.html", "report_cossart.html", "report_summary.html"):
        text = _page(built, name)
        assert text.startswith('<!doctype html><meta charset="utf-8">')
        assert "<svg" in text


def test_the_problem_and_its_figure_come_before_the_evidence(built):
    """Role 11: the apparatus arrived before the motivation, on every page."""
    for name in ("report_steps_excluded.html", "report_summary.html"):
        t = _page(built, name)
        assert t.index('id="problem"') < t.index('id="fig1"') < t.index('id="summary"')
    t = _page(built, "report_steps_excluded.html")
    assert t.index('id="terms"') < t.index('id="fig2"')
    assert t.index('id="destruction"') < t.index('id="choices"')     # evidence, then choices


def test_cossart_data_are_cited_with_their_licence_and_missing_version(built):
    t = _page(built, "report_cossart.html")
    assert "DANDI:000219" in t and "CC-BY-4.0" in t
    assert "version" in t.lower()
    assert "DANDI:000219" in _page(built, "report_summary.html")


def test_the_reach_box_says_holm_cannot_flag_and_what_unadjusted_costs(bsr, built):
    R = bsr.load_role(built, "steps_excluded")
    y = bsr.yardstick_reach(R)
    assert y["m"] == 65 and y["band_floor"] == pytest.approx(1 / 101)
    assert y["band_floor_holm"] > bsr.ALPHA and y["paired_floor_holm"] > bsr.ALPHA
    # 1300 and 2600, not 1299 and 2599: at 1299 splits the Holm-adjusted floor is
    # exactly alpha, and a check fires on P < alpha, so the sample that REACHES alpha
    # cannot flag anything. Stage 2 of the 2026-09-12 probe demonstrated it.
    assert y["splits_needed"] == 1300 and y["K_needed"] == 2600
    assert y["fwer"] > 0.9                       # 65 checks at alpha = 0.05
    t = _page(built, "report_steps_excluded.html")
    assert "Holm-adjusted, can flag anything at these settings" in t and "1300" in t
    assert "false flag somewhere in a cell" in t


def test_the_discriminators_own_controls_are_not_the_candidates_results(bsr, built):
    """Role 1 F2: 12 rows were reported where 6 cells existed, and the control that
    validates uniform dither pulled its range down to the control's accuracy."""
    R = bsr.load_role(built, "steps_excluded")
    ud = {r["name"]: r for r in bsr.candidate_rows(R, "fast")}["uniform_dither"]
    assert ud["disc_n"] == 1                      # the control row is not counted
    assert ud["disc_acc"]["min"] == pytest.approx(0.62)


def test_a_candidate_that_cannot_reach_alpha_is_never_shown_as_zero(bsr, built):
    R = bsr.load_role(built, "steps_excluded")
    rows = {r["name"]: r for r in bsr.candidate_rows(R, "fast")}
    assert rows["circular_shift"]["n_unreachable"] == 1
    assert not rows["circular_shift"]["paired_raw"] == 0     # NaN, not a measured zero
    for name in ("report_steps_excluded.html", "report_summary.html"):
        assert "unreachable" in _page(built, name)


def test_the_group_reconciliation_is_computed_on_the_unadjusted_p(bsr, built):
    """Role 4 #1 / role 1 F6: on the Holm-adjusted P both counters are 0 by construction."""
    R = bsr.load_role(built, "steps_excluded")
    g = bsr.group_flags(R, "fast")
    assert g["groups"] == ["G1", "G2", "G3", "G4"]
    assert g["only_group"] > 0                    # G1 leaks where the pooled scope does not
    t = _page(built, "report_steps_excluded.html")
    assert 'id="groups"' in t and "FOUNDATIONS §9" in t


def test_the_graded_control_is_reported_and_is_not_a_candidate_cell(bsr, built):
    R = bsr.load_role(built, "steps_excluded")
    rows = {r["name"]: r for r in bsr.candidate_rows(R, "fast")}
    assert rows["circular_shift"]["n_cells"] == 1          # freeze-half is not its cell
    assert rows["freeze_half"]["ret_JK"]                   # and it is reported on its own
    assert "freeze-half" in _page(built, "report_steps_excluded.html")


def test_destruction_saturation_is_computed_before_it_is_reported(bsr, built):
    """Role 4 #4: on a 566-ROI twin every planted event trips a scan that stops at 8."""
    sat = bsr.destruction_reach(bsr.load_role(built, "cossart"), "events")
    assert sat["saturated"] and sat["expected"] > sat["K_hi"]
    clean = bsr.destruction_reach(bsr.load_role(built, "steps_excluded"), "fast")
    assert not clean["saturated"]
    assert "saturated" in _page(built, "report_cossart.html")
    assert "saturated" in _page(built, "report_summary.html")


def test_saturation_is_evaluated_at_every_J_not_only_the_largest(bsr, built):
    """Blind role 4: expected-in-bin FALLS as J grows, so the largest J is the least
    saturated one. Testing there and generalising called a sweep measurable whose small
    end was not — and the small end is where every reported span starts."""
    sj = bsr.saturation_by_J(bsr.load_role(built, "steps_excluded"), "fast")
    Js = sorted(sj["per_J"])
    assert sj["saturated"][Js[0]] and not sj["saturated"][Js[-1]]
    assert sj["per_J"][Js[0]] > sj["per_J"][Js[-1]]          # smaller J, more left in bin
    assert bsr.sat_Js(bsr.load_role(built, "steps_excluded"), "fast") == [Js[0]]
    t = _page(built, "report_steps_excluded.html")
    assert "†" in t and "saturated" in t
    assert "the destruction measure is saturated" in t       # named, not only marked


def test_the_zero_width_band_is_disclosed_and_the_rate_given_both_ways(bsr, built):
    """Blind role 4: where the real value is identically 0 the band has no width, so the
    flag is an equality test. It carried a third of the band rate, undisclosed."""
    R = bsr.load_role(built, "steps_excluded")
    assert ("fast", "subfloor@0fr") in bsr.zero_width_band_stats(R)
    assert ("fast", "subfloor@1fr") not in bsr.zero_width_band_stats(R)
    y = bsr.yardstick_reach(R)
    assert y["n_zero_width"] > 0 and y["n_zw_stats"] == 1
    assert "zero width" in _page(built, "report_steps_excluded.html")


def test_a_statistic_that_flags_its_own_negative_is_marked_where_it_is_cited(bsr, built):
    """Blind role 4: the page promised the mark and marked nothing."""
    R = bsr.load_role(built, "steps_excluded")
    assert bsr.high_neg_stats(R, "fast") == {"subfloor@0fr"}
    t = _page(built, "report_steps_excluded.html")
    assert "‡" in t and "more often than α" in t


def test_the_circular_shift_is_named_as_the_assessors_own_null(built):
    """Blind role 4: its 0.00 is guaranteed by construction, so it cannot be the
    must-pass control that shows the measure works."""
    t = _page(built, "report_steps_excluded.html")
    assert "circular_shift_trains" in t and "by construction" in t


def test_the_20_percent_arm_names_the_floor_it_was_measured_at(built):
    """Blind roles 1 and 4: the two arms were compared at different K under one header."""
    t = _page(built, "report_steps_excluded.html")
    assert "20% participation arm" in t
    assert "co-active ROIs" in t


def test_the_expected_in_bin_count_never_exceeds_what_was_planted(bsr, built):
    """bin/(2J+1) is a probability, so the expected count is capped by the recruitment.

    Uncapped it read 25.8 co-active ROIs from a twin recruiting 15.5, and 471.7 from one
    recruiting 283 — impossible numbers that reached a shipped page. The saturation
    verdicts survive the cap; the printed counts did not.
    """
    for role, stream in (("steps_excluded", "fast"), ("cossart", "events")):
        R = bsr.load_role(built, role)
        sj = bsr.saturation_by_J(R, stream)
        assert sj, f"no saturation arithmetic for {role}/{stream}"
        for J, exp in sj["per_J"].items():
            assert exp <= sj["recruited"] + 1e-9, (
                f"{role}/{stream} J={J}: {exp} expected from {sj['recruited']} recruited")
        dr = bsr.destruction_reach(R, stream)
        if dr:
            assert dr["expected"] <= dr["recruited"] + 1e-9


def test_a_no_op_cell_is_not_counted_as_a_measurement(bsr, built):
    R = bsr.load_role(built, "steps_excluded")
    rows = {r["name"]: r for r in bsr.candidate_rows(R, "fast")}
    assert rows["do_nothing"]["n_noop"] == 1
    assert rows["do_nothing"]["n_checks"] == 0             # its checks are excluded


def test_every_page_carries_its_sources_and_its_residual_flags(built):
    for name in ("report_steps_excluded.html", "report_cossart.html", "report_summary.html"):
        t = _page(built, name)
        assert 'id="sources"' in t and "doi:" in t
        assert 'id="residual"' in t and "not a correctness proof" in t


def test_a_page_without_svg_is_refused(bsr):
    with pytest.raises(SystemExit, match="no SVG"):
        bsr.refuse_without_svg("x.html", "<p>nothing drawn</p>")


def test_the_gate_never_passes_without_its_stamped_tools(bsr, built):
    with pytest.raises(SystemExit, match="missing stamped copies"):
        bsr.main(["--run", str(built)])


def test_the_gate_fails_on_its_own_counts_not_on_the_tools_exit_code(bsr, built, tmp_path):
    """Blind role 10: render_check --json returns 0 BEFORE it counts anything, so on one
    build it exited 0 while its own JSON held 104 sub-11px labels, 5 overlaps and 2
    viewBox escapes. The caller has the JSON; the caller must be what fails."""
    tools = built / "tools"
    tools.mkdir(exist_ok=True)
    (tools / "render_check.py").write_text(
        "import json, sys\n"
        "json.dump({'file': 'x', 'views': [{'theme': 'light', 'width': 1440,\n"
        "  'texts': [{'svg': 0, 'renderedPx': 8.1, 's': 'tiny'}],\n"
        "  'overlaps': [], 'escapes': []}]}, sys.stdout)\n"
        "sys.exit(0)\n", encoding="utf-8")                       # exits 0, as the real one does
    (tools / "edge_collisions.py").write_text("import sys; sys.exit(0)\n", encoding="utf-8")
    page = built / "report_cossart.html"
    with pytest.raises(SystemExit, match="render gate FAILED"):
        bsr.run_gate(built, [page])
    rec = json.loads((tools / "gate.json").read_text(encoding="utf-8"))
    assert rec["pages"][page.name]["counts"]["small"] == 1
    assert rec["pages"][page.name]["render_check_exit"] == 0     # the tool still said "fine"
