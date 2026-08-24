"""`bugarach check` and `bugarach detect` must reach the same verdict.

A lab's first command is `check`. Being told a conforming folder is malformed,
and then watching `detect` analyse that same folder without complaint, is worse
than either behaviour on its own: it makes the tool look broken and gives the lab
no way to tell which answer is true.

That is not hypothetical. Two lanes landed on 2026-08-23 — one taught `detect`
the windowing default (raw period bounds scored verbatim where the producer sent
no `analysis_*`), the other did not touch the door — and for one afternoon a
folder whose baseline began at 500 s with a gap after it FAILED `check` and was
scored happily by `detect`. Each command had its own copy of the question.

**The fix is one call site; this file is the durable half.** The drift is the
recurring hazard, so the agreement is pinned rather than assumed: every folder
below goes through both public entry points and the two verdicts must match, per
recording, for the same stated reason.

It then drifted a second time, in the opposite direction and on a different
question. A folder whose `slices.csv` declares no `frame_interval_sec` cannot be
measured at all (FOUNDATIONS §6); `check` said NOT CONFORMING and exited 1, and
`detect` printed its ordinary closing summary, wrote a `detections.csv` of one
header line, and exited 0. Agreeing about a recording is not enough when the
**exit status** says the opposite, because the exit status is the half a
pipeline reads — so the second section below pins the codes as well as the
verdicts.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from bugarach.conform import check_folder
from bugarach.detect_folder import NoRecordingDetectedOn, detect_folder

#: One cheap detector. Window resolution happens in `detect_slice` before any
#: detector runs, so which of the six is asked for cannot change the verdict —
#: and running all six over every case below would buy nothing but minutes.
ONE = ("coact",)

EVENTS = ("roi,time_sec,stream\n"
          "1,10.0,fast\n1,900.0,fast\n1,1500.0,fast\n"
          "2,11.0,fast\n2,905.0,fast\n2,NA,fast\n"
          "3,10.5,fast\n3,1490.0,fast\n")

HDR = ("slice_id,region_idx,label,start_sec,end_sec,"
       "analysis_start_sec,analysis_end_sec\n")
RAW = "slice_id,region_idx,label,start_sec,end_sec\n"

#: name -> (regions.csv, does this folder conform?)
#:
#: The legal half is the point of the exercise: each one violates something
#: `region_windows` halts on, and none of them violates the contract. The
#: illegal half is what "conforming" must keep excluding — bounds that are
#: wrong under anybody's protocol, not under this lab's.
CASES: dict[str, tuple[str | None, bool]] = {
    # ---- legal ----------------------------------------------------------
    "no regions at all":
        (None, True),
    "raw bounds, zero-based and contiguous":
        (RAW + "s1,1,baseline,0,1200\ns1,2,TTX,1200,2400\n", True),
    "baseline starts at 500 s, then an 8,900 s gap":
        (RAW + "s1,1,pre-drug,500,1400\ns1,2,TTX,10300,12000\n", True),
    "pre-trimmed bounds — the export that halted 83 of 85":
        (RAW + "s1,1,baseline,60,1260\ns1,2,TTX,1380,2580\n", True),
    "one period, beginning nowhere near zero":
        (RAW + "s1,1,aCSF,732.5,3600\n", True),
    "producer's own analysis windows":
        (HDR + "s1,1,baseline,0,1260,60,1260\ns1,2,TTX,1260,2580,1380,2400\n",
         True),
    "producer's windows on a folder that is also gappy":
        (HDR + "s1,1,pre-drug,500,1400,600,1400\n"
               "s1,2,TTX,10300,12000,10400,11000\n", True),
    "a label containing \"hi\", which the store path would exempt":
        (RAW + "s1,1,baseline,0,1200\ns1,2,histamine,1200,2400\n", True),
    # ---- not legal, under anybody's protocol -----------------------------
    "a period that ends before it begins":
        (RAW + "s1,1,baseline,1260,60\n", False),
    "an analysis window that ends before it begins":
        (HDR + "s1,1,baseline,0,1260,900,300\n", False),
    "an analysis window outside its own period":
        (HDR + "s1,1,baseline,0,1260,60,1260\n"
               "s1,2,TTX,1260,2580,1380,9999\n", False),
    "an analysis start that is not a finite time":
        (HDR + "s1,1,baseline,0,1260,nan,1260\n", False),
    "windows for one region and not the other":
        (HDR + "s1,1,baseline,0,1260,60,1260\ns1,2,TTX,1260,2580,,\n", False),
    "interface2's -100,499 second window":
        (HDR + "s1,1,baseline,500,1400,99999,-500\n"
               "s1,2,TTX,10300,12000,10400,11000\n", False),
}


def _folder(tmp_path: Path, name: str, regions: str | None) -> Path:
    d = tmp_path / "e"
    d.mkdir(parents=True, exist_ok=True)
    (d / "s1.csv").write_text(EVENTS)
    (d / "slices.csv").write_text("slice_id,frame_interval_sec\ns1,0.1\n")
    if regions is not None:
        (d / "regions.csv").write_text(regions)
    return d


def _detect_says(folder: Path, out: Path) -> dict[str, str]:
    """slice_id -> why detect produced nothing, or "" where it scored.

    A folder that cannot even be read is one verdict for the whole folder, which
    is how `check` reports it too, so it is keyed under the empty id.
    """
    try:
        run = detect_folder(folder, out_dir=out, detectors=ONE)
    except NoRecordingDetectedOn as exc:
        # Every recording was skipped, so the run as a whole failed — but the
        # per-recording verdicts are exactly what this file compares, and they
        # survive on the roster the refusal carries.
        run = exc.run
    except (ValueError, OSError) as exc:
        return {"": str(exc)}
    return {r.slice_id: r.skipped for r in run.records}


@pytest.mark.parametrize("name", list(CASES))
def test_check_and_detect_reach_the_same_verdict(name, tmp_path: Path):
    regions, conforming = CASES[name]
    d = _folder(tmp_path, name, regions)

    rep = check_folder(d)
    detected = _detect_says(d, tmp_path / "out")

    # first: each command on its own is right about this folder
    assert rep.ok is conforming, (
        f"{name}: check says {'CONFORMING' if rep.ok else 'NOT CONFORMING'}; "
        f"{[e for r in rep.recordings for e in r.errors] + rep.errors}")
    scored = [k for k, v in detected.items() if not v]
    assert bool(scored) is conforming, f"{name}: detect said {detected}"

    # then the thing this file exists for: they agree recording by recording
    if "" in detected:                       # the folder never loaded
        assert not rep.ok, f"{name}: detect could not read a folder check passed"
        return
    for r in rep.recordings:
        why = detected.get(r.slice_id, "<absent from the run>")
        assert r.ok is (why == ""), (
            f"{name}/{r.slice_id}: check {'passed' if r.ok else 'failed'} it and "
            f"detect {'scored' if why == '' else 'skipped'} it — "
            f"check said {r.errors}, detect said {why!r}")


@pytest.mark.parametrize("name", [n for n, (_, ok) in CASES.items() if not ok])
def test_a_refusal_gives_both_commands_the_same_reason(name, tmp_path: Path):
    """Agreeing on the verdict is not enough if the two explain it differently.

    A producer who runs `check`, fixes what it named, and then gets a different
    complaint out of `detect` has been sent round the loop twice for one defect.
    """
    regions, _ = CASES[name]
    d = _folder(tmp_path, name, regions)

    rep = check_folder(d)
    detected = _detect_says(d, tmp_path / "out")
    said_by_check = " ".join(
        [e for r in rep.recordings for e in r.errors] + rep.errors)
    said_by_detect = " ".join(detected.values())

    # the detector-side message is carried through verbatim, minus check's own
    # framing, so the two are literally the same sentence about the same bounds
    core = said_by_detect.split(": ", 1)[-1] if said_by_detect else ""
    assert core and core in said_by_check, (
        f"{name}: check said {said_by_check!r}, detect said {said_by_detect!r}")


def test_neither_command_derives_windows_of_its_own():
    """The structural half — the copies are gone, not merely reconciled.

    Verdict agreement can be restored by patching one call site; it drifts again
    the moment somebody adds a second reading of the same rules. `conform` holds
    no window logic at all, and the resolver it names is the one `detect_folder`
    defines, so the two cannot answer differently.
    """
    import ast
    import inspect

    from bugarach import conform
    from bugarach import detect_folder as df

    assert conform.folder_analysis_windows is df.folder_analysis_windows

    # names, not prose: the comment in conform.py explains what it no longer
    # calls, and explaining it is exactly what we want it to keep doing
    tree = ast.parse(inspect.getsource(conform))
    used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    used |= {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    for reimplemented in ("effective_region_windows", "region_windows",
                          "with_folder_windows", "recording_extent"):
        assert reimplemented not in used, (
            f"conform.py reaches past folder_analysis_windows to "
            f"{reimplemented} — that is the second copy this file exists to "
            f"prevent, and it is how check and detect drifted apart before")


def test_the_store_path_still_halts_on_the_data_it_was_written_for():
    """The fix must not have been bought by relaxing the parity port.

    `region_windows` is a 1e-9 port of aCa5z's convention, and for a `.mat`
    store a baseline that does not begin at 0 really is a data defect. What
    changed is that the folder path no longer routes into it — not what it does
    when it is called.
    """
    from bugarach.detectors.loco import region_windows
    from bugarach.store import Region, Slice

    s = Slice(slice_id="s1", streams={}, dt=None, roi_ids=None, regions=[
        Region(name="baseline", slot="1", start_sec=500.0, end_sec=1400.0),
        Region(name="TTX", slot="2", start_sec=10300.0, end_sec=12000.0),
    ])
    with pytest.raises(ValueError, match="expected 0"):
        region_windows(s, 12000.0)


# --- the frame interval, where the two commands disagreed the other way round


#: what slices.csv says -> can this folder be detected on?
#:
#: `check` has always been right about all five. `detect` agreed about the
#: verdict per recording and then contradicted it with an exit status: it
#: printed its ordinary closing summary, wrote a one-line `detections.csv`, and
#: exited 0, so a lab that had just been told NOT CONFORMING was handed a
#: success code and an empty result file for the same folder.
INTERVALS: dict[str, tuple[str, bool]] = {
    "the interval declared":
        ("slice_id,frame_interval_sec\ns1,0.1\n", True),
    "slices.csv with no frame_interval_sec column":
        ("slice_id,source\ns1,bench\n", False),
    "the column present and the cell empty":
        ("slice_id,frame_interval_sec\ns1,\n", False),
    "an interval that is not a number":
        ("slice_id,frame_interval_sec\ns1,soon\n", False),
    "an interval of zero seconds":
        ("slice_id,frame_interval_sec\ns1,0\n", False),
}


def _interval_folder(tmp_path: Path, slices: str | None) -> Path:
    d = tmp_path / "e"
    d.mkdir(parents=True, exist_ok=True)
    (d / "s1.csv").write_text(EVENTS)
    if slices is not None:
        (d / "slices.csv").write_text(slices)
    return d


@pytest.mark.parametrize("name", list(INTERVALS))
def test_the_two_commands_agree_about_the_frame_interval(name, tmp_path: Path):
    slices, runnable = INTERVALS[name]
    d = _interval_folder(tmp_path, slices)

    assert check_folder(d).ok is runnable
    if runnable:
        run = detect_folder(d, out_dir=tmp_path / "out", detectors=ONE)
        assert run.detected and run.paths["detections"].is_file()
    else:
        with pytest.raises(NoRecordingDetectedOn):
            detect_folder(d, out_dir=tmp_path / "out", detectors=ONE)


@pytest.mark.parametrize("name", list(INTERVALS))
def test_the_two_commands_agree_about_the_exit_code(name, tmp_path: Path):
    """The verdicts matching is not enough — the exit status is what a pipeline
    reads, and it is the half that was wrong.

    `check` exited 1 on a folder with no declared interval and `detect` exited 0
    on the same folder in the next breath. Whichever a lab believed, the tool had
    contradicted itself with nothing to say which answer was true.
    """
    from bugarach.cli import main

    slices, runnable = INTERVALS[name]
    d = _interval_folder(tmp_path, slices)

    codes = {}
    for argv in (["check", str(d)],
                 ["detect", str(d), "--out", str(tmp_path / "out"),
                  "--detectors", "coact"]):
        with pytest.raises(SystemExit) as e:
            main(argv)
        codes[argv[0]] = 0 if e.value.code in (0, None) else 1

    assert codes["check"] == codes["detect"] == (0 if runnable else 1), codes
    assert (tmp_path / "out" / "detections.csv").exists() is runnable


def test_a_folder_may_conform_and_still_need_the_interval_supplied(tmp_path):
    """The one place the two answer differently, and they are not in conflict.

    `slices.csv` is optional under the contract, so a folder without it
    **conforms** — and `check` says in the same breath that bugarach will ask
    for the frame interval and cannot proceed without it. `detect` refusing is
    that sentence arriving. Conforming is a statement about the folder;
    runnable needs one fact the folder may legally omit, and the fix is the
    option the refusal names rather than a change to either verdict.
    """
    d = _interval_folder(tmp_path, None)

    rep = check_folder(d)
    assert rep.ok
    assert any("frame interval" in n for r in rep.recordings for n in r.notes)

    with pytest.raises(NoRecordingDetectedOn) as e:
        detect_folder(d, out_dir=tmp_path / "out", detectors=ONE)
    assert "--frame-interval" in str(e.value)

    run = detect_folder(d, out_dir=tmp_path / "out", detectors=ONE,
                        frame_interval_sec=0.05)
    assert run.detected and run.paths["detections"].is_file()
