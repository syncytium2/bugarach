"""Tests for the headless route: an export folder in, ``detections.csv`` out.

Two things are being pinned here, and only one of them is the plumbing.

The plumbing is that ``bugarach detect`` writes the output contract and that what
it writes reads back. Before this module existed, :mod:`bugarach.emit` — the
writer for that whole contract — had no caller anywhere outside the tests, so
the only way to a detections file was a person clicking through a browser page.

The other is the **windowing default**, and it is the reason a foreign folder
could not be detected on at all. A recording that states no analysis windows is
scored on its raw period bounds with no protocol applied; the parity port that
encodes this lab's protocol is untouched and still halts on the data it was
written for. Both halves are asserted, on the same folder, because either one
alone is the bug: applying the convention everywhere refuses legal folders, and
relaxing the port's guards would let a genuinely broken export through.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from bugarach.detect_folder import (
    DETECTORS,
    NoRecordingDetectedOn,
    detect_folder,
    format_run,
    with_folder_windows,
)
from bugarach.emit import read_detections

# Two detectors, one from each family — the flat three take a stream and a time
# range, the region-aware three take the slice and window it themselves. Running
# one of each keeps these tests in tenths of a second while still exercising both
# paths; ALL_SIX below is used once, where the whole contract is the point.
PAIR = ("coact", "loco")


def _recording(rois: int = 10, windows=((500.0, 1500.0), (2400.0, 3400.0))) -> str:
    """A recording with real coactivity in every window, as a folder CSV.

    Each window gets a coordinated burst every two minutes in which every ROI
    fires inside a second, over a per-ROI background that is deliberately out of
    step with it. Enough for every detector to find something without any of
    them finding it everywhere.
    """
    lines = ["roi,time_sec,stream"]
    for lo, hi in windows:
        t = lo + 60.0
        while t < hi - 30.0:
            for r in range(rois):
                lines.append(f"{r + 1},{t + 0.1 * r:.3f},fast")
            t += 120.0
        for r in range(rois):
            u = lo + 13.0 + 3.1 * r
            while u < hi:
                lines.append(f"{r + 1},{u:.3f},fast")
                u += 37.0 + r
    return "\n".join(lines) + "\n"


#: Baseline starting at 500 s with a 900 s gap after it — legal under the
#: contract, refused by this project's own stores, and the shape that halted a
#: whole export. FOUNDATIONS §4: a lab that recorded before it started treating,
#: or left the tissue alone between conditions, is describing its experiment.
FOREIGN_REGIONS = ("slice_id,region_idx,label,start_sec,end_sec\n"
                   "s1,1,pre-drug,500,1500\n"
                   "s1,2,TTX,2400,3400\n")

SLICES = "slice_id,frame_interval_sec,group_id\ns1,0.1,ORX\n"


def _folder(tmp_path: Path, *, regions=FOREIGN_REGIONS, slices=SLICES,
            recording=None, name="e") -> Path:
    d = tmp_path / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "s1.csv").write_text(_recording() if recording is None else recording)
    if regions is not None:
        (d / "regions.csv").write_text(regions)
    if slices is not None:
        (d / "slices.csv").write_text(slices)
    return d


# --- the headline: a legal foreign folder is analysed, not halted


def test_a_baseline_at_500_seconds_with_a_gap_is_detected_on(tmp_path: Path):
    """The folder this project's windowing convention would have refused.

    ``region_windows`` halts on a baseline that does not begin at 0 and on a gap
    between periods, and until now the folder path fell through into it. Nothing
    about this recording is wrong; the guards simply do not describe it.
    """
    d = _folder(tmp_path)
    run = detect_folder(d, out_dir=tmp_path / "out", detectors=PAIR)

    assert len(run.records) == 1
    assert not run.skipped, [r.skipped for r in run.skipped]
    assert run.n_events > 0
    rec, = run.records
    assert [(w["scored_start_sec"], w["scored_end_sec"]) for w in rec.windows] \
        == [(500.0, 1500.0), (2400.0, 3400.0)]


def test_no_protocol_is_applied_to_a_folder_that_stated_none(tmp_path: Path):
    """No wash-in delay, no cap, no backward-measured baseline.

    This lab's convention would score the second period from 2520 s (two minutes
    of wash-in) and the first backward from its end. The folder said nothing
    about any of that, so nothing of the kind is applied — Tony's decision of
    2026-08-18, point 4.
    """
    d = _folder(tmp_path)
    run = detect_folder(d, out_dir=tmp_path / "out", detectors=("coact",))
    scored = [(w["raw_start_sec"], w["raw_end_sec"],
               w["scored_start_sec"], w["scored_end_sec"])
              for w in run.records[0].windows]
    assert all(raw0 == win0 and raw1 == win1 for raw0, raw1, win0, win1 in scored)


def test_the_store_path_still_halts_on_exactly_these_bounds(tmp_path: Path):
    """The other half, and the constraint the decision came with.

    ``region_windows`` is a 1e-9 parity port and FOUNDATIONS §2 makes that parity
    the product, so the fix could not be to relax it. For a `.mat` store a
    baseline that does not start at 0 really is a data defect, and it must still
    say so — the folder simply does not go through here any more.
    """
    from bugarach.detectors.loco import region_windows
    from bugarach.io import load_folder

    s, = load_folder(_folder(tmp_path))
    with pytest.raises(ValueError, match="expected 0"):
        region_windows(s, 3400.0)


def test_a_producers_own_analysis_windows_still_win(tmp_path: Path):
    """Stating a policy is the contract's own answer, and it is not overridden."""
    d = _folder(tmp_path, regions=(
        "slice_id,region_idx,label,start_sec,end_sec,"
        "analysis_start_sec,analysis_end_sec\n"
        "s1,1,pre-drug,500,1500,600,1500\n"
        "s1,2,TTX,2400,3400,2500,3400\n"))
    run = detect_folder(d, out_dir=tmp_path / "out", detectors=("coact",))
    assert [(w["scored_start_sec"], w["scored_end_sec"])
            for w in run.records[0].windows] == [(600.0, 1500.0), (2500.0, 3400.0)]


def test_half_a_policy_is_reported_rather_than_completed(tmp_path: Path):
    """Windows on some regions and not others is two policies in one number.

    The resolution deliberately does not fill in the missing half — a recording
    scored half on the producer's windows and half on raw bounds would be a
    single number computed two ways, which is worse than either.
    """
    d = _folder(tmp_path, regions=(
        "slice_id,region_idx,label,start_sec,end_sec,"
        "analysis_start_sec,analysis_end_sec\n"
        "s1,1,pre-drug,500,1500,600,1500\n"
        "s1,2,TTX,2400,3400,,\n"))
    # the only recording in the folder, so the run has nothing left to score and
    # says so rather than handing back an empty file
    with pytest.raises(NoRecordingDetectedOn) as e:
        detect_folder(d, out_dir=tmp_path / "out", detectors=("coact",))
    assert len(e.value.run.skipped) == 1
    assert "two policies" in e.value.run.records[0].skipped


def test_with_folder_windows_leaves_the_callers_slice_alone(tmp_path: Path):
    from bugarach.io import load_folder

    s, = load_folder(_folder(tmp_path))
    resolved = with_folder_windows(s)
    assert [r.has_analysis_window for r in s.regions] == [False, False]
    assert [r.has_analysis_window for r in resolved.regions] == [True, True]
    assert [(r.analysis_start_sec, r.analysis_end_sec) for r in resolved.regions] \
        == [(500.0, 1500.0), (2400.0, 3400.0)]


def test_a_recording_with_no_regions_is_scored_whole(tmp_path: Path):
    """No ``regions.csv`` is not the same absence as regions with no windows."""
    d = _folder(tmp_path, regions=None)
    run = detect_folder(d, out_dir=tmp_path / "out", detectors=("coact",))
    assert not run.skipped, [r.skipped for r in run.skipped]
    w, = run.records[0].windows
    assert w["region_idx"] is None                 # no index was sent, none invented
    rows = read_detections(run.paths["detections"])
    assert rows and all(r["region_idx"] is None for r in rows)


# --- the output contract


def test_every_written_row_reads_back(tmp_path: Path):
    d = _folder(tmp_path)
    run = detect_folder(d, out_dir=tmp_path / "out", detectors=DETECTORS)
    rows = read_detections(run.paths["detections"])

    assert len(rows) == run.n_events > 0
    assert {r["detector"] for r in rows} == set(DETECTORS)
    assert {r["stream"] for r in rows} == {"fast"}
    for r in rows:
        assert isinstance(r["onset_sec"], float)
        assert isinstance(r["width_sec"], float)
        assert isinstance(r["strength"], float)
        assert r["strength_unit"]                  # the unit travels in the row
        assert r["mode"] in ("threshold", "peak")
        # the producer's identity columns, carried through and not interpreted
        assert r["group_id"] == "ORX"
        assert r["slice_id"] == "s1"


def test_the_producers_own_region_index_and_name_are_what_is_written(tmp_path: Path):
    d = _folder(tmp_path)
    run = detect_folder(d, out_dir=tmp_path / "out", detectors=DETECTORS)
    rows = read_detections(run.paths["detections"])
    pairs = {(r["region_idx"], r["region_label"]) for r in rows}
    # a detection outside every declared period carries neither, rather than a
    # name the producer never sent
    assert pairs <= {(1, "pre-drug"), (2, "TTX"), (None, None)}
    assert (1, "pre-drug") in pairs and (2, "TTX") in pairs


def test_detector_settings_are_keyed_by_detector_and_stream(tmp_path: Path):
    """``detector, stream, parameter, value`` — because a detector may run with
    different settings on two streams, and a table that could not say so would
    make one of them unreproducible."""
    import csv

    d = _folder(tmp_path)
    run = detect_folder(d, out_dir=tmp_path / "out", detectors=DETECTORS)
    with run.paths["settings"].open() as fh:
        rows = list(csv.DictReader(fh))

    assert [*rows[0]] == ["detector", "stream", "parameter", "value"]
    keyed: dict[tuple[str, str], dict[str, str]] = {}
    for r in rows:
        keyed.setdefault((r["detector"], r["stream"]), {})[r["parameter"]] = r["value"]
    assert set(keyed) == {(d_, "fast") for d_ in DETECTORS}

    # the two that make a run reproducible rather than merely described
    assert keyed[("loco", "fast")]["rng_seed"] == "20260706"
    # the acquisition interval reaches the detector that builds a grid from it,
    # instead of the bench's synthetic 0.1 (FOUNDATIONS §6)
    assert keyed[("rate", "fast")]["grid_dt"] == "0.1"
    assert keyed[("cicada", "fast")]["imaging_rate_hz"] == "10.0"
    # the six do not anchor on the same per-event time, and cicada is the odd one
    assert keyed[("cicada", "fast")]["onset_field"] == "locs"
    assert keyed[("loco", "fast")]["onset_field"] == "t50rise"


def test_a_second_run_of_the_same_folder_is_the_same_file(tmp_path: Path):
    """What the settings file is for: reproducibility, checked rather than
    claimed."""
    d = _folder(tmp_path)
    a = detect_folder(d, out_dir=tmp_path / "a", detectors=DETECTORS)
    b = detect_folder(d, out_dir=tmp_path / "b", detectors=DETECTORS)
    assert a.paths["detections"].read_text() == b.paths["detections"].read_text()
    assert a.paths["settings"].read_text() == b.paths["settings"].read_text()


def test_the_run_sidecar_carries_the_roster_and_the_windowing_policy(tmp_path: Path):
    """``detections.csv`` structurally cannot say which recordings were looked
    at and produced nothing. That is what the roster is for."""
    d = _folder(tmp_path)
    run = detect_folder(d, out_dir=tmp_path / "out", detectors=("coact",))
    doc = json.loads(run.paths["run"].read_text())
    assert doc["slices"] == ["s1"]
    assert doc["frame_interval_sec"] == {"s1": 0.1}
    assert doc["rng_seed"] == 20260706
    assert doc["detectors"] == ["coact"]
    assert "raw period bounds verbatim" in doc["window_policy"]
    assert doc["windows"]["s1"][0]["label"] == "pre-drug"


def test_an_empty_result_still_writes_a_real_file(tmp_path: Path):
    """An empty result and an absent one must not look alike.

    This is the half of the distinction that keeps the header-only file: the
    recording WAS scored and the tissue was quiet. `detections_written` is true,
    the roster holds the recording, and the count of detections is zero because
    zero is the answer.
    """
    d = _folder(tmp_path, recording="roi,time_sec,stream\n1,600.0,fast\n2,NA,fast\n")
    run = detect_folder(d, out_dir=tmp_path / "out", detectors=("coact",))
    assert run.n_events == 0
    assert run.paths["detections"].is_file()
    assert read_detections(run.paths["detections"]) == []
    doc = json.loads(run.paths["run"].read_text())
    assert doc["slices"] == ["s1"]
    assert (doc["detections_written"], doc["n_detected_on"],
            doc["n_detections"]) == (True, 1, 0)


# --- a run that scored nothing is a failed run, not an empty result


def test_scoring_no_recording_at_all_is_refused_not_reported(tmp_path: Path):
    """The defect: `check` refused this folder and `detect` called it a success.

    A folder whose `slices.csv` declares no frame interval cannot be measured —
    FOUNDATIONS §6, and `check` says so with a non-zero exit. `detect` used to
    print its ordinary closing summary, write a one-line `detections.csv`, and
    exit 0, so a lab got a success code and a file containing nothing.
    """
    d = _folder(tmp_path, slices="slice_id,source\ns1,bench\n")
    with pytest.raises(NoRecordingDetectedOn) as e:
        detect_folder(d, out_dir=tmp_path / "out", detectors=("coact",))

    # the refusal names the column, the file and the flag — the three facts
    # `Slice.require_dt` names, not a fourth phrasing of them
    msg = str(e.value)
    assert "frame_interval_sec" in msg and "slices.csv" in msg
    assert "--frame-interval" in msg
    # and it hands back the roster, so the caller can still say which failed
    assert [r.slice_id for r in e.value.run.skipped] == ["s1"]


def test_a_failed_run_leaves_no_result_file_behind(tmp_path: Path):
    """A header with no rows under it must never mean "nothing ran".

    It is the honest shape of "nothing found", which is why the test above keeps
    it. Writing the same bytes for a run that never happened is what made the
    two indistinguishable on disk.
    """
    out = tmp_path / "out"
    d = _folder(tmp_path, slices="slice_id,source\ns1,bench\n")
    with pytest.raises(NoRecordingDetectedOn):
        detect_folder(d, out_dir=out, detectors=("coact",))

    assert sorted(p.name for p in out.iterdir()) == ["run.json"]
    doc = json.loads((out / "run.json").read_text())
    assert doc["detections_written"] is False
    assert (doc["n_recordings"], doc["n_detected_on"],
            doc["n_not_detected"]) == (1, 0, 1)
    assert "NO recording was detected on" in doc["outcome"]
    # and the record of the failed attempt is complete enough to act on
    assert "sampling interval" in doc["not_detected"]["s1"]


def test_some_recordings_skipped_is_a_finding_and_the_rest_are_scored(tmp_path):
    """The other side of the split, and the reason it is not `any`.

    `tools/make_diagnostic.py` was given exactly this threshold in PR #255: one
    detector failing on one slice is a finding to record and carry on with, all
    of them failing is the call site being broken. Same rule here, one level up
    — one malformed recording in a folder of 85 must not cost the other 84.
    """
    d = _folder(tmp_path)
    (d / "s2.csv").write_text(_recording())
    (d / "slices.csv").write_text(SLICES + "s2,,ORX\n")
    (d / "regions.csv").write_text(
        FOREIGN_REGIONS + "s2,1,pre-drug,500,1500\ns2,2,TTX,2400,3400\n")

    run = detect_folder(d, out_dir=tmp_path / "out", detectors=("coact",))
    assert [r.slice_id for r in run.detected] == ["s1"]
    assert [r.slice_id for r in run.skipped] == ["s2"]
    assert run.n_events > 0
    assert run.paths["detections"].is_file()

    doc = json.loads(run.paths["run"].read_text())
    assert (doc["n_recordings"], doc["n_detected_on"],
            doc["n_not_detected"]) == (2, 1, 1)
    assert doc["detections_written"] is True

    # loudly: the roster names it once, and a block of its own names it again,
    # because four lines among eighty is how a partial run reads as a whole one
    report = format_run(run)
    assert "1 of 2 recording(s) produced NOTHING" in report
    assert report.count("s2") >= 2


def test_no_frame_interval_is_refused_rather_than_defaulted(tmp_path: Path):
    """FOUNDATIONS §6. Three detectors build their grid from it, nothing
    downstream can recover it, and a default here is a guess about somebody
    else's microscope.

    The per-recording reason is `Slice.require_dt`'s own sentence, carried
    verbatim — one refusal in the tree rather than a hand-written copy here.
    """
    d = _folder(tmp_path, slices=None)
    with pytest.raises(NoRecordingDetectedOn) as e:
        detect_folder(d, out_dir=tmp_path / "out", detectors=("coact",))
    why = e.value.run.records[0].skipped
    assert "FrameIntervalNotDeclaredError" in why
    assert "never stated one" in why and "frame_interval_sec" in why


def test_the_interval_can_be_supplied_the_way_the_prompt_would(tmp_path: Path):
    """A caller with no interface supplies it the same way a person would."""
    d = _folder(tmp_path, slices=None)
    run = detect_folder(d, out_dir=tmp_path / "out", detectors=("coact",),
                        frame_interval_sec=0.05)
    assert not run.skipped and run.n_events > 0
    assert json.loads(run.paths["run"].read_text())["frame_interval_sec"] == {"s1": 0.05}


def test_one_bad_recording_does_not_cost_the_others(tmp_path: Path):
    d = _folder(tmp_path)
    (d / "s2.csv").write_text(_recording())
    (d / "regions.csv").write_text(
        FOREIGN_REGIONS + "s2,1,baseline,1200,600\n")
    (d / "slices.csv").write_text(
        SLICES + "s2,0.1,ORX\n")
    run = detect_folder(d, out_dir=tmp_path / "out", detectors=("coact",))
    assert [r.slice_id for r in run.detected] == ["s1"]
    assert [r.slice_id for r in run.skipped] == ["s2"]
    assert "cannot end first" in run.records[1].skipped
    # and the reason survives into the sidecar, where a reader will look
    assert "cannot end first" in json.loads(
        run.paths["run"].read_text())["not_detected"]["s2"]


def test_an_unknown_detector_names_the_ones_there_are(tmp_path: Path):
    with pytest.raises(ValueError, match="unknown detector"):
        detect_folder(_folder(tmp_path), out_dir=tmp_path / "out",
                      detectors=("loco", "nonesuch"))


def test_a_stream_this_recording_does_not_have_says_which_it_has(tmp_path: Path):
    d = _folder(tmp_path)
    with pytest.raises(NoRecordingDetectedOn) as e:
        detect_folder(d, out_dir=tmp_path / "out", detectors=("coact",),
                      stream="slow")
    why = e.value.run.records[0].skipped
    assert "no stream named 'slow'" in why and "fast" in why


def test_progress_is_reported_per_recording(tmp_path: Path):
    """Two minutes of silence is indistinguishable from a hang."""
    d = _folder(tmp_path)
    seen = []
    detect_folder(d, out_dir=tmp_path / "out", detectors=("coact",),
                  progress=lambda done, total, sid: seen.append((done, total, sid)))
    assert seen == [(0, 1, "s1"), (1, 1, None)]


# --- the command line


def test_the_cli_writes_the_three_files(tmp_path: Path):
    from bugarach.cli import main

    d = _folder(tmp_path)
    out = tmp_path / "cli"
    with pytest.raises(SystemExit) as e:
        main(["detect", str(d), "--out", str(out), "--detectors", "coact,loco"])
    assert e.value.code == 0
    assert sorted(p.name for p in out.iterdir()) == [
        "detections.csv", "detector_settings.csv", "run.json"]


def test_the_cli_exit_code_says_the_folder_was_not_detected_on(tmp_path: Path):
    """A pipeline reads the exit status and nothing else.

    The report and the sidecar can be as clear as they like; if the process
    exits 0 the next step runs on a file with a header and no rows. Zero is what
    made this defect expensive — four times in one day, a degraded result and a
    green exit.
    """
    from bugarach.cli import main

    d = _folder(tmp_path, slices="slice_id,source\ns1,bench\n")
    out = tmp_path / "cli"
    with pytest.raises(SystemExit) as e:
        main(["detect", str(d), "--out", str(out), "--detectors", "coact"])

    assert e.value.code != 0
    assert "--frame-interval" in str(e.value.code)
    assert not (out / "detections.csv").exists()


def test_the_flag_the_refusal_names_is_the_flag_that_fixes_it(tmp_path: Path):
    """Naming a fix that does not work is worse than naming none.

    Same folder, same command, plus the one option the refusal above pointed at
    — and now there are detections and a zero exit.
    """
    from bugarach.cli import main

    d = _folder(tmp_path, slices="slice_id,source\ns1,bench\n")
    out = tmp_path / "cli"
    with pytest.raises(SystemExit) as e:
        main(["detect", str(d), "--out", str(out), "--detectors", "coact",
              "--frame-interval", "0.05"])

    assert e.value.code == 0
    assert len(read_detections(out / "detections.csv")) > 0
    doc = json.loads((out / "run.json").read_text())
    assert doc["frame_interval_sec"] == {"s1": 0.05}
    assert doc["detections_written"] is True


def test_the_cli_refuses_an_unknown_detector_by_name(tmp_path: Path):
    from bugarach.cli import main

    with pytest.raises(SystemExit) as e:
        main(["detect", str(_folder(tmp_path)), "--out", str(tmp_path / "o"),
              "--detectors", "loco,nonesuch"])
    assert "nonesuch" in str(e.value.code)


@pytest.mark.parametrize("cmd", ["detect", "assess"])
def test_a_folder_that_is_not_there_is_a_message_not_a_traceback(cmd, tmp_path):
    """``check`` has always answered this cleanly; ``assess`` used to hand back a
    NotADirectoryError out of the loader, which reads as a crash rather than as
    the entirely expected thing it is."""
    from bugarach.cli import main

    argv = [cmd, str(tmp_path / "nope")]
    if cmd == "detect":
        argv += ["--out", str(tmp_path / "o")]
    with pytest.raises(SystemExit) as e:
        main(argv)
    msg = str(e.value.code)
    assert "no such folder" in msg and "export_folder_spec" in msg


@pytest.mark.parametrize("cmd", ["detect", "assess"])
def test_a_folder_with_nothing_in_it_says_what_a_folder_is(cmd, tmp_path: Path):
    from bugarach.cli import main

    d = tmp_path / "empty"
    d.mkdir()
    argv = [cmd, str(d)]
    if cmd == "detect":
        argv += ["--out", str(tmp_path / "o")]
    with pytest.raises(SystemExit) as e:
        main(argv)
    assert "holds no recordings" in str(e.value.code)
