"""The step where a person's verdicts reach the simulator, and the refusal.

`derive_spec` turns an assessment into generator settings. Before 2026-08-24 it
took medians over every candidate the assessor proposed and nobody had looked at
any of them — the state `docs/RESET.md` §1 calls *"not a weaker result of the
same kind — it is not a result"*.

The tests that matter here are the ones about what it will not do quietly.
"""
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

from bugarach.annotate import Verdict, write_annotations

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "derive_spec", ROOT / "tools" / "derive_spec.py")
derive_spec = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(derive_spec)


def _field(median, n=60):
    return {"median": median, "iqr": [median * 0.8, median * 1.2], "n": n}


def assessment():
    """A minimal assessment with the shape `bugarach assess` writes."""
    by_k = {}
    for k, clusters in ((3, 2.0), (4, 1.0), (6, 0.5), (8, 0.25)):
        by_k[str(k)] = {
            "part_n_obs": _field(6.0), "jit_obs": _field(0.40),
            "jit_null": _field(0.90), "jit_excess": _field(-0.50),
            "span_med": _field(1.5), "clusters_permin": _field(clusters),
            "coact_excess": _field(3.0), "ev_rate_permin": _field(9.0),
            "roi_rate_med": _field(0.004),
            "n_jit_defined": 40, "n_slices": 60,
        }
    rows = [{"K": k, "window_sec": 1200.0, "n_roi": 30, "ev_rate_permin": 9.0,
             "roi_rate_med": 0.004, "slice_id": f"s{i}", "stream": "fast"}
            for k in (3, 4, 6, 8) for i in range(6)]
    return {"by_k": by_k, "rows": rows, "n_roi": {"median": 30.0},
            "store": "synthetic", "n_slices_assessed": 6, "n_surrogates": 200,
            "region_labels_seen": ["baseline"], "background": {}}


def mkv(**kw):
    base = dict(slice_id="s1", stream="fast", centre_sec=100.0, k_survived=4,
                n_members=6, members=(1, 2, 3, 4, 5, 6), span_sec=1.5,
                jitter_sd_sec=0.40, verdict="confirmed", annotator="tony",
                decided_at="2026-08-24T15:00:00Z", view_t0_sec=80.0,
                view_t1_sec=120.0, view_roi_order="file", view_stream="fast")
    base.update(kw)
    return Verdict(**base)


# ---------------------------------------------------------------------------
# the refusal
# ---------------------------------------------------------------------------

def test_deriving_without_saying_whether_anyone_looked_is_refused(tmp_path):
    """FOUNDATIONS §6's shape, one layer up: a step that warns has already
    produced the output. Both flags are answers; omitting them is not."""
    ap = tmp_path / "a.json"
    ap.write_text(json.dumps(assessment()))
    with pytest.raises(SystemExit):
        derive_spec.main(["--assessment", str(ap), "--out", str(tmp_path),
                          "--k", "4"])
    assert not (tmp_path / "generator_spec.json").exists()


def test_claiming_both_at_once_is_refused(tmp_path):
    ap = tmp_path / "a.json"
    ap.write_text(json.dumps(assessment()))
    anp = tmp_path / "annotations.csv"
    write_annotations(anp, [mkv()])
    with pytest.raises(SystemExit):
        derive_spec.main(["--assessment", str(ap), "--out", str(tmp_path),
                          "--k", "4", "--annotations", str(anp),
                          "--unreviewed"])


def test_unreviewed_is_allowed_and_says_so_at_the_top_of_the_notes(tmp_path):
    """The escape exists, and it is loud rather than silent — the note governs
    how every number under it should be read."""
    ap = tmp_path / "a.json"
    ap.write_text(json.dumps(assessment()))
    derive_spec.main(["--assessment", str(ap), "--out", str(tmp_path),
                      "--k", "4", "--unreviewed"])
    spec = json.loads((tmp_path / "generator_spec.json").read_text())
    assert "NOBODY HAS LOOKED" in spec["notes"][0]
    assert spec["review"] is None


# ---------------------------------------------------------------------------
# what the verdicts change
# ---------------------------------------------------------------------------

def _build(annotations=None, k=4):
    return derive_spec.build(assessment(), k, annotations=annotations)


def test_the_confirm_rate_scales_the_event_frequency():
    """The number that decides how much coordination the simulator plants."""
    all_yes = _build([mkv() for _ in range(4)])
    half = _build([mkv() for _ in range(2)] + [mkv(verdict="rejected")
                                               for _ in range(2)])
    assert half["review"]["confirm_rate"] == 0.5
    # half the belief, half the planted events
    assert (half["generator"]["n_per_level"][0]
            <= all_yes["generator"]["n_per_level"][0])
    assert any("scaled by the confirm rate" in n for n in half["notes"])


def test_participation_comes_from_confirmed_candidates_only():
    """A rejected 40-ROI candidate must not vote on how many ROIs an event has."""
    got = _build([mkv(n_members=6), mkv(n_members=6),
                  mkv(n_members=40, verdict="rejected")])
    assert got["review"]["part_n_med"] == 6.0
    assert any("a person CONFIRMED" in n for n in got["notes"])


def test_confirming_nothing_does_not_silently_produce_a_spec_of_nothing():
    """"K is too strict" and "this folder has no agreed coordination" are
    different conversations. Neither is settled by writing a zero."""
    got = _build([mkv(verdict="rejected") for _ in range(5)])
    assert got["review"]["n_confirmed"] == 0
    assert any("confirmed NONE" in n for n in got["notes"])
    assert np.isfinite(got["generator"]["n_per_level"][0])


def test_verdicts_that_never_reach_the_chosen_k_are_called_out():
    """Judging at K=3 and deriving at K=8 is a real mistake to make: every
    verdict is about a candidate that does not exist at the K being derived."""
    got = _build([mkv(k_survived=3) for _ in range(5)], k=8)
    assert got["review"]["n_judged"] == 0
    assert any("NONE of them reach K=8" in n for n in got["notes"])


def test_the_review_block_is_present_either_way():
    """A consumer checking `spec["review"]` gets an answer whether or not
    anybody looked; a missing key would read as an older spec format."""
    assert _build(None)["review"] is None
    assert _build([mkv()])["review"]["n_confirmed"] == 1


# ---------------------------------------------------------------------------
# K derived rather than taken
# ---------------------------------------------------------------------------

def _labels():
    """Verdicts a threshold can be fitted to: rejected small, confirmed large,
    proposed from a floor of 2 so the censoring guard is not what answers."""
    out = []
    for i in range(12):
        out.append(mkv(n_members=2 + i % 2, k_survived=2 + i % 2,
                       verdict="rejected", centre_sec=100.0 + i))
        out.append(mkv(n_members=6 + i % 3, k_survived=6 + i % 3,
                       verdict="confirmed", centre_sec=500.0 + i))
    return out


def test_no_k_at_all_is_refused(tmp_path):
    """The old signature made --k required. Making it optional must not make it
    defaultable — omitting both routes is the state this step exists to end."""
    ap = tmp_path / "a.json"
    ap.write_text(json.dumps(assessment()))
    with pytest.raises(SystemExit):
        derive_spec.main(["--assessment", str(ap), "--out", str(tmp_path),
                          "--unreviewed"])
    assert not (tmp_path / "generator_spec.json").exists()


def test_a_chosen_k_and_a_derived_one_contradict_each_other(tmp_path):
    ap = tmp_path / "a.json"
    ap.write_text(json.dumps(assessment()))
    anp = tmp_path / "annotations.csv"
    write_annotations(anp, _labels())
    with pytest.raises(SystemExit):
        derive_spec.main(["--assessment", str(ap), "--out", str(tmp_path),
                          "--k", "4", "--annotations", str(anp),
                          "--k-from-annotations"])


def test_deriving_k_with_nothing_to_derive_it_from_is_refused(tmp_path):
    ap = tmp_path / "a.json"
    ap.write_text(json.dumps(assessment()))
    with pytest.raises(SystemExit):
        derive_spec.main(["--assessment", str(ap), "--out", str(tmp_path),
                          "--k-from-annotations", "--unreviewed"])


def test_labels_that_cannot_locate_a_k_write_no_spec(tmp_path, capsys):
    """A spec is the input to everything downstream, so half of one is worse
    than none. Non-zero exit, no file, and the reason on stderr."""
    ap = tmp_path / "a.json"
    ap.write_text(json.dumps(assessment()))
    anp = tmp_path / "annotations.csv"
    write_annotations(anp, [mkv(n_members=6, k_survived=6, centre_sec=100.0 + i)
                            for i in range(4)])
    rc = derive_spec.main(["--assessment", str(ap), "--out", str(tmp_path),
                           "--annotations", str(anp), "--k-from-annotations"])
    assert rc == 2
    assert not (tmp_path / "generator_spec.json").exists()
    assert "K NOT IDENTIFIED" in capsys.readouterr().err


def test_a_derived_k_reaches_the_spec_with_its_separation(tmp_path):
    ap = tmp_path / "a.json"
    ap.write_text(json.dumps(assessment()))
    anp = tmp_path / "annotations.csv"
    write_annotations(anp, _labels())
    rc = derive_spec.main(["--assessment", str(ap), "--out", str(tmp_path),
                           "--annotations", str(anp), "--k-from-annotations"])
    assert rc == 0
    spec = json.loads((tmp_path / "generator_spec.json").read_text())
    assert spec["k_chosen"] == 4
    d = spec["k_derivation"]
    assert d is not None
    assert d["k"] == 4
    assert d["separation_youden_j"] == pytest.approx(1.0)
    assert d["proposal_floor"] == 2
    assert d["annotators"] == ["tony"]
    assert d["curve"], "the scan the choice was made against is not in the spec"
    assert "DERIVED from labelled calls" in spec["notes"][0]


def test_a_chosen_k_says_it_was_chosen_rather_than_estimated(tmp_path):
    """`k_derivation` is null-valued rather than absent, so a consumer can tell
    "a person picked it" from "the labels located it" without guessing at the
    spec's version."""
    ap = tmp_path / "a.json"
    ap.write_text(json.dumps(assessment()))
    anp = tmp_path / "annotations.csv"
    write_annotations(anp, _labels())
    derive_spec.main(["--assessment", str(ap), "--out", str(tmp_path),
                      "--k", "4", "--annotations", str(anp)])
    spec = json.loads((tmp_path / "generator_spec.json").read_text())
    assert "k_derivation" in spec and spec["k_derivation"] is None
