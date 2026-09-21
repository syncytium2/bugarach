"""Turning a bake-off's calibration into a file `detect` will run at.

The three refusals are the substance, not the happy path. Each one exists because
the alternative is a settings file that looks like a calibration and is not:

* **folds that disagree are not averaged.** Four folds choosing 99.5, 99.5, 99.9,
  99.5 did not choose 99.6, and a mean over a knob grid is not a knob anyone ran;
* **a value on the end of its grid is not emitted** unless asked for, because this
  project reads that everywhere else as a search that stopped too early
  (`bench.pick_operating_point` raises on it);
* **a detector the bake-off did not sweep does not appear**, because a file
  carrying shipped values for the uncalibrated ones would read as a calibration of
  all six.

And the output has to be loadable by the thing it is for, which is what the last
test checks end to end rather than by inspection.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "src"))

import settings_from_bakeoff as mod  # noqa: E402
from bugarach.bench import OPERATING_POINTS  # noqa: E402
from bugarach.detect_folder import load_settings  # noqa: E402


def _bakeoff(per_detector, *, folds=4, seeds_per_fold=2):
    """A bake-off shaped like the real one: {name: [knob per fold]}."""
    return {
        "folds": folds, "seeds_per_fold": seeds_per_fold,
        "provenance": {"store": "some_cohort"},
        "hand_written": {
            name: {"f1": {"mean": 0.7},
                   "per_fold": [{"knob_value": v,
                                 "knob": OPERATING_POINTS[name].knob}
                                for v in vals]}
            for name, vals in per_detector.items()},
        "learned": {},
    }


def _interior(name):
    """A grid value that is not an end, so the edge rule is not what fires."""
    grid = list(OPERATING_POINTS[name].grid)
    assert len(grid) > 2, name
    return grid[1]


def test_agreeing_folds_give_the_value_they_agreed_on():
    v = _interior("loco")
    got, refused = mod.resolve(_bakeoff({"loco": [v, v, v, v]}),
                               pick="refuse", allow_edge=False)
    assert refused == []
    assert got["loco"]["value"] == v and got["loco"]["agreed"] is True


def test_disagreeing_folds_are_refused_rather_than_averaged():
    grid = list(OPERATING_POINTS["loco"].grid)
    a, b = grid[1], grid[2]
    bake = _bakeoff({"loco": [a, a, b, a]})
    got, refused = mod.resolve(bake, pick="refuse", allow_edge=False)
    assert got == {} and len(refused) == 1
    assert "they disagree" in refused[0] and "not a knob anyone ran" in refused[0]
    # and asked to resolve, it says which rule it used — in the file, not a log
    got, refused = mod.resolve(bake, pick="mode", allow_edge=False)
    assert refused == [] and got["loco"]["value"] == a
    assert got["loco"]["pick"] == "mode" and got["loco"]["agreed"] is False


def test_a_value_on_the_end_of_the_grid_is_refused():
    end = list(OPERATING_POINTS["loco"].grid)[0]
    bake = _bakeoff({"loco": [end] * 4})
    got, refused = mod.resolve(bake, pick="refuse", allow_edge=False)
    assert got == {} and "an END of the searched grid" in refused[0]
    # allowed through only on request, and then it is stamped
    got, refused = mod.resolve(bake, pick="refuse", allow_edge=True)
    assert refused == [] and got["loco"]["on_edge"] is True
    rows = mod.rows_for(got, streams=["fast"], fitted_on="x")
    edge = [r for r in rows if r["parameter"] == "fitted_grid_edge"]
    assert edge and "bound rather than an operating point" in edge[0]["value"]


def test_a_detector_the_bakeoff_did_not_sweep_is_absent():
    v = _interior("loco")
    got, _ = mod.resolve(_bakeoff({"loco": [v] * 4}), pick="refuse",
                         allow_edge=False)
    rows = mod.rows_for(got, streams=["fast"], fitted_on="x")
    named = {r["detector"] for r in rows}
    assert named == {"loco"}, "shipped values for unswept detectors would read as calibration"


def test_the_file_it_writes_is_one_detect_can_load(tmp_path):
    """End to end, because this file exists only to be read by that function."""
    v = _interior("loco")
    bake = tmp_path / "bakeoff.json"
    bake.write_text(json.dumps(_bakeoff({"loco": [v] * 4})))
    out = tmp_path / "detector_settings.csv"
    assert mod.main(["--bakeoff", str(bake), "--out", str(out)]) == 0

    overrides, fitted = load_settings(out)
    assert overrides[("loco", "fast")][OPERATING_POINTS["loco"].knob] == v
    assert fitted["loco/fast"]["fitted_on"] == "some_cohort"
    assert fitted["loco/fast"]["fitted_knob"] == OPERATING_POINTS["loco"].knob


def test_it_refuses_to_write_a_file_with_nothing_in_it(tmp_path, capsys):
    end = list(OPERATING_POINTS["loco"].grid)[0]
    bake = tmp_path / "bakeoff.json"
    bake.write_text(json.dumps(_bakeoff({"loco": [end] * 4})))
    out = tmp_path / "detector_settings.csv"
    assert mod.main(["--bakeoff", str(bake), "--out", str(out)]) == 2
    assert not out.exists(), "an empty settings file would run everything shipped"
