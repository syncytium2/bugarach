"""`bugarach detect --settings`: the link that lets a calibration reach real data.

Until this existed, `detector_params` read `bench.OPERATING_POINTS` and nothing
else, so a knob fitted on simulated data derived from a folder could not be applied
to that folder from the command line. The bake-off's calibrated values were a
record, never an input, and the detector that was scored was not the detector that
ran — five of the six shipped values sit outside everything the folds chose.

What these pin, in the order they would break:

* a settings file actually changes what a detector runs with, and the run says so;
* **the file the browser writes and the file this module writes are one format**,
  in BOTH directions — `emit.read_detector_settings` always parsed both, and the
  round trip is what stops that drifting;
* the recording still wins on the two values that describe the microscope, so a
  file fitted on another rig cannot smuggle in that rig's frame interval;
* `fitted_*` provenance reaches `run.json` instead of being handed to a detector,
  where it would be a TypeError;
* the three nested ports refuse per-stream divergence by name rather than
  silently applying one stream's value to both;
* a bad file is refused before the folder is walked, not on recording 84 of 85.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from bugarach.bench import OPERATING_POINTS  # noqa: E402
from bugarach.detect_folder import (  # noqa: E402
    detect_folder,
    detector_params,
    load_settings,
)

SLICES = "slice_id,frame_interval_sec,group_id\ns1,0.05,MALE\n"
REGIONS = ("slice_id,region_idx,label,start_sec,end_sec,"
           "analysis_start_sec,analysis_end_sec\n"
           "s1,1,baseline,0,600,0,600\n")


def _events():
    rows = ["roi,time_sec,stream"]
    for t in (100, 200, 300, 400, 500):
        for roi in range(1, 9):
            rows.append(f"{roi},{t + roi * 0.02:.2f},fast")
            rows.append(f"{roi},{t + roi * 0.02:.2f},slow")
    return "\n".join(rows) + "\n"


def _folder(tmp_path: Path) -> Path:
    folder = tmp_path / "folder"
    folder.mkdir()
    (folder / "slices.csv").write_text(SLICES)
    (folder / "regions.csv").write_text(REGIONS)
    (folder / "s1.csv").write_text(_events())
    return folder


def _settings_csv(path: Path, rows) -> Path:
    """A settings file in the four columns both writers use."""
    out = ["detector,stream,parameter,value"]
    out += [",".join(str(x) for x in r) for r in rows]
    path.write_text("\n".join(out) + "\n")
    return path


def test_a_settings_file_changes_what_a_detector_runs_with(tmp_path):
    shipped = OPERATING_POINTS["loco"].params["threshold_pctile"]
    assert shipped != 99.5, "fixture assumes the shipped value is not the one set"
    csv = _settings_csv(tmp_path / "s.csv",
                        [("loco", "fast", "threshold_pctile", 99.5),
                         ("loco", "slow", "threshold_pctile", 99.5)])
    overrides, _ = load_settings(csv)
    got = detector_params("loco", frame_interval_sec=0.05,
                          overrides=overrides, stream="fast")
    assert got["threshold_pctile"] == 99.5
    # and with no file it is still the shipped point
    assert detector_params(
        "loco", frame_interval_sec=0.05)["threshold_pctile"] == shipped


def test_the_recording_still_wins_on_the_microscope(tmp_path):
    """A file supplies a knob. It does not supply somebody else's frame interval."""
    csv = _settings_csv(tmp_path / "s.csv",
                        [("rate", "fast", "grid_dt", 0.1),
                         ("cicada", "fast", "imaging_rate_hz", 10.0)])
    overrides, _ = load_settings(csv)
    rate = detector_params("rate", frame_interval_sec=0.05,
                           overrides=overrides, stream="fast")
    cicada = detector_params("cicada", frame_interval_sec=0.05,
                             overrides=overrides, stream="fast")
    assert rate["grid_dt"] == 0.05, "the file must not set the acquisition interval"
    assert cicada["imaging_rate_hz"] == pytest.approx(20.0)


def test_the_round_trip_is_the_same_format_in_both_directions(tmp_path):
    """Detect, take the file it wrote, feed it back, and get the same settings.

    This is the claim that matters for the browser: `emit.read_detector_settings`
    parses what the page saves *and* what this writes, so a file crossing between
    them is one table rather than two dialects. A round trip through the real
    writer is the only thing that keeps that true as either side changes.
    """
    folder = _folder(tmp_path)
    first = detect_folder(folder, out_dir=tmp_path / "a")
    wrote = first.paths["settings"]
    again = detect_folder(folder, out_dir=tmp_path / "b", settings=wrote)
    assert (Path(again.paths["settings"]).read_text()
            == Path(wrote).read_text()), "a run at its own settings must restate them"


def test_provenance_reaches_run_json_and_no_detector(tmp_path):
    folder = _folder(tmp_path)
    csv = _settings_csv(tmp_path / "s.csv",
                        [("loco", "fast", "threshold_pctile", 99.5),
                         ("loco", "slow", "threshold_pctile", 99.5),
                         ("loco", "fast", "fitted_on", "some_other_folder"),
                         ("loco", "fast", "fitted_f1", 0.71)])
    overrides, fitted = load_settings(csv)
    # not arguments: handing `fitted_on` to loco_detect is a TypeError
    assert "fitted_on" not in detector_params(
        "loco", frame_interval_sec=0.05, overrides=overrides, stream="fast")
    assert fitted["loco/fast"]["fitted_on"] == "some_other_folder"

    run = detect_folder(folder, out_dir=tmp_path / "out", settings=csv)
    got = json.loads(Path(run.paths["run"]).read_text())
    assert got["settings_file"] == str(csv)
    assert got["settings_fitted_on"]["loco/fast"]["fitted_on"] == "some_other_folder"
    # and with no file, null keeps meaning "shipped operating points"
    bare = json.loads(Path(
        detect_folder(folder, out_dir=tmp_path / "bare").paths["run"]).read_text())
    assert bare["settings_file"] is None and bare["settings_fitted_on"] is None


def test_a_nested_port_refuses_per_stream_divergence(tmp_path):
    """loco, sce and cicada read the whole recording in one RNG sequence, so a
    per-stream value cannot be honoured — and must not be silently half-applied.

    The refusal arrives as a per-recording failure, which on a one-recording
    folder is every recording, so `detect_folder` raises. Both halves matter: the
    reason must name the parameter, and it must reach `run.json` rather than only
    a traceback.
    """
    from bugarach.detect_folder import NoRecordingDetectedOn

    folder = _folder(tmp_path)
    csv = _settings_csv(tmp_path / "s.csv",
                        [("loco", "fast", "threshold_pctile", 99.5),
                         ("loco", "slow", "threshold_pctile", 99.99)])
    out = tmp_path / "out"
    with pytest.raises(NoRecordingDetectedOn) as caught:
        detect_folder(folder, out_dir=out, settings=csv, detectors=("loco",))
    said = str(caught.value)
    assert "different values per stream" in said and "threshold_pctile" in said
    assert "one RNG sequence" in said
    got = json.loads((out / "run.json").read_text())
    assert "different values per stream" in got["not_detected"]["s1"]


def test_a_flat_port_takes_per_stream_values(tmp_path):
    """The three that see one stream at a time can take one stream's settings."""
    csv = _settings_csv(tmp_path / "s.csv",
                        [("coact", "fast", "int_win_sec", 1.0),
                         ("coact", "slow", "int_win_sec", 4.0)])
    overrides, _ = load_settings(csv)
    fast = detector_params("coact", frame_interval_sec=0.05,
                           overrides=overrides, stream="fast")
    slow = detector_params("coact", frame_interval_sec=0.05,
                           overrides=overrides, stream="slow")
    assert (fast["int_win_sec"], slow["int_win_sec"]) == (1.0, 4.0)


def test_an_empty_stream_row_applies_to_every_stream(tmp_path):
    """What the browser writes when no stream is chosen."""
    csv = _settings_csv(tmp_path / "s.csv",
                        [("coact", "", "int_win_sec", 3.0)])
    overrides, _ = load_settings(csv)
    for sname in ("fast", "slow"):
        got = detector_params("coact", frame_interval_sec=0.05,
                              overrides=overrides, stream=sname)
        assert got["int_win_sec"] == 3.0


@pytest.mark.parametrize("rows, says", [
    ([("nosuch", "fast", "threshold_pctile", 99.5)], "unknown detector"),
    ([("loco", "fast", "nosuchknob", 1)], "has no parameter"),
    ([("loco", "fast", "threshold_pctile", "banana")], "is not a float"),
])
def test_a_bad_file_is_refused_by_name(tmp_path, rows, says):
    csv = _settings_csv(tmp_path / "s.csv", rows)
    with pytest.raises(ValueError, match=says):
        load_settings(csv)


def test_a_bad_file_is_refused_before_the_folder_is_walked(tmp_path):
    """On recording 1, not on recording 84 of 85."""
    folder = _folder(tmp_path)
    csv = _settings_csv(tmp_path / "s.csv", [("loco", "fast", "nosuchknob", 1)])
    out = tmp_path / "out"
    with pytest.raises(ValueError, match="has no parameter"):
        detect_folder(folder, out_dir=out, settings=csv)
    assert not (out / "detections.csv").exists()
