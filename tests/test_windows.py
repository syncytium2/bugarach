"""Stage one of the loop: the two things a user supplies, and how absence reads.

`check` conforms on a folder with no periods in it, and must keep conforming —
contract rule 2, and export contract revision 7 records the cost of the opposite:
this side turned its own protocol into a condition of entry and **83 of 85** of
interface2's recordings were refused at the door while `detect` scored them
happily.

So the tests here are about **position and volume**, not about pass and fail. As
notes, these two absences printed after every per-recording line — line 91 of 94
on the lab's own export — and a user could take such a folder all the way to a
results table without ever learning that every number in it came from one
unlabelled window.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from bugarach.cli import main
from bugarach.conform import NO_WINDOWS, PROMOTED, check_folder, format_report
from bugarach.windows import (
    SCAFFOLD_LABEL, RegionsFileExists, describe, scaffold,
)

EVENTS = ("roi,time_sec,stream\n"
          "1,10.0,fast\n1,40.0,fast\n1,95.0,fast\n"
          "2,11.0,fast\n2,41.0,fast\n2,96.0,fast\n"
          "3,NA,fast\n")
SLICES = "slice_id,frame_interval_sec\ns1,0.05\n"
PERIODS = ("slice_id,region_idx,label,start_sec,end_sec\n"
           "s1,1,pre-drug,0,50\ns1,2,TTX,50,100\n")
PERIODS_SCORED = (
    "slice_id,region_idx,label,start_sec,end_sec,"
    "analysis_start_sec,analysis_end_sec\n"
    "s1,1,pre-drug,0,50,5,50\ns1,2,TTX,50,100,60,100\n")


def folder(tmp_path: Path, *, regions=None, slices=SLICES, name="e") -> Path:
    d = tmp_path / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "s1.csv").write_text(EVENTS)
    if slices is not None:
        (d / "slices.csv").write_text(slices)
    if regions is not None:
        (d / "regions.csv").write_text(regions)
    return d


def _line_of(text: str, needle: str) -> int:
    for i, line in enumerate(text.splitlines()):
        if needle in line:
            return i
    raise AssertionError(f"{needle!r} not in:\n{text}")


# ---------------------------------------------------------------------------
# the hard tell — position, and still conforming
# ---------------------------------------------------------------------------

def test_missing_treatment_timing_is_told_above_the_recordings(tmp_path: Path):
    """The whole change is the position. Under the verdict, before the detail."""
    out = format_report(check_folder(folder(tmp_path)))
    assert _line_of(out, "TREATMENT TIMING IS MISSING") < _line_of(out, "  ok ")


def test_missing_treatment_timing_does_not_fail_the_folder(tmp_path: Path):
    """Contract rule 2: only the recording files are required. Turning this into
    a refusal is the revision-7 mistake, and it cost 83 of 85 recordings."""
    rep = check_folder(folder(tmp_path))
    assert rep.ok and rep.n_ok == 1
    assert "CONFORMING" in format_report(rep)


def test_missing_analysis_windows_is_told_above_the_recordings(tmp_path: Path):
    out = format_report(check_folder(folder(tmp_path, regions=PERIODS)))
    assert _line_of(out, "NO ANALYSIS WINDOWS") < _line_of(out, "  ok ")
    assert check_folder(folder(tmp_path, regions=PERIODS)).ok


def test_supplied_analysis_windows_are_not_told_about(tmp_path: Path):
    """Nothing is missing, so the header says nothing. A report that shouts on a
    complete folder teaches people to skip the shouting."""
    out = format_report(check_folder(folder(tmp_path, regions=PERIODS_SCORED)))
    assert "TREATMENT TIMING IS MISSING" not in out
    assert "NO ANALYSIS WINDOWS" not in out


def test_a_folder_with_no_periods_is_not_also_told_about_analysis_windows(
        tmp_path: Path):
    """Two absences, and only the first one matters yet. Reporting the second
    while the first is open buries the one to act on."""
    out = format_report(check_folder(folder(tmp_path)))
    assert "TREATMENT TIMING IS MISSING" in out
    assert "NO ANALYSIS WINDOWS" not in out


def test_neither_absence_is_said_twice(tmp_path: Path):
    """They were notes; they are a header now. Leaving both would print each
    fact two or three times, which is the defect the notes vocabulary exists to
    prevent."""
    out = format_report(check_folder(folder(tmp_path)))
    assert out.count("analysed as ONE unlabelled window") == 1
    assert NO_WINDOWS not in out
    assert "no regions.csv — allowed" not in out


def test_the_promoted_notes_are_still_on_the_report_object(tmp_path: Path):
    """Only the RENDERING moved. A programmatic caller — the browser, a producer's
    CI — reads `notes` and must still find them."""
    rep = check_folder(folder(tmp_path))
    r, = rep.recordings
    assert NO_WINDOWS in r.notes
    assert any(n in PROMOTED for n in rep.notes)


def test_the_tell_names_the_command_that_fixes_it(tmp_path: Path):
    d = folder(tmp_path)
    out = format_report(check_folder(d))
    assert f"bugarach windows {d} --create" in out


# ---------------------------------------------------------------------------
# describe
# ---------------------------------------------------------------------------

def test_describe_separates_having_periods_from_having_windows(tmp_path: Path):
    bare = describe(folder(tmp_path, name="a"))
    assert bare.missing_timing == ["s1"] and bare.missing_analysis == []
    raw = describe(folder(tmp_path, regions=PERIODS, name="b"))
    assert raw.missing_timing == [] and raw.missing_analysis == ["s1"]
    done = describe(folder(tmp_path, regions=PERIODS_SCORED, name="c"))
    assert done.missing_timing == [] and done.missing_analysis == []


def test_half_a_recordings_analysis_windows_counts_as_none(tmp_path: Path):
    """The contract refuses all-or-none, so a partial set is a producer bug
    rather than a partial answer — and reporting it as *supplied* would hide it."""
    # Empty fields, not `NA`. The contract says missing is spelled literally NA,
    # and `io.py` raises `could not convert string to float: 'NA'` on these two
    # columns — a conforming folder the loader cannot read. Out of scope here and
    # filed: docs/todo/2026-09-03-analysis-bounds-reject-the-contracts-own-na.md
    half = ("slice_id,region_idx,label,start_sec,end_sec,"
            "analysis_start_sec,analysis_end_sec\n"
            "s1,1,pre-drug,0,50,5,50\ns1,2,TTX,50,100,,\n")
    fw = describe(folder(tmp_path, regions=half))
    assert fw.missing_analysis == ["s1"]
    r, = fw.recordings
    assert r.n_regions == 2 and r.n_with_analysis == 1


# ---------------------------------------------------------------------------
# scaffold
# ---------------------------------------------------------------------------

def test_scaffold_writes_one_period_per_recording_over_its_own_events(
        tmp_path: Path):
    d = folder(tmp_path)
    path, rows = scaffold(d)
    assert path == d / "regions.csv"
    assert len(rows) == 1
    row, = rows
    assert row["slice_id"] == "s1" and int(row["region_idx"]) == 1
    assert row["label"] == SCAFFOLD_LABEL
    assert float(row["start_sec"]) == pytest.approx(10.0)
    assert float(row["end_sec"]) == pytest.approx(96.0)


def test_the_scaffold_it_writes_is_refused_by_check(tmp_path: Path):
    """The placeholder is the point. A draft that passed would be shipped, and
    the contract requires `label` to be the period's real name."""
    d = folder(tmp_path)
    scaffold(d)
    rep = check_folder(d)
    assert not rep.ok
    r, = rep.recordings
    assert any(SCAFFOLD_LABEL in e for e in r.errors)
    assert "NOT CONFORMING" in format_report(rep)


def test_editing_the_label_is_all_it_takes(tmp_path: Path):
    """The round trip, because a scaffold nothing can complete is worse than
    none: it leaves a folder that used to conform refusing to."""
    d = folder(tmp_path)
    p, _ = scaffold(d)
    p.write_text(p.read_text().replace(SCAFFOLD_LABEL, "aCSF"))
    rep = check_folder(d)
    assert rep.ok, [r.errors for r in rep.recordings]
    r, = rep.recordings
    assert r.windows == ["aCSF"]


def test_scaffold_refuses_to_overwrite_a_persons_record(tmp_path: Path):
    d = folder(tmp_path, regions=PERIODS)
    with pytest.raises(RegionsFileExists, match="will not overwrite"):
        scaffold(d)
    assert "pre-drug" in (d / "regions.csv").read_text()


def test_force_overwrites_and_nothing_else_does(tmp_path: Path):
    d = folder(tmp_path, regions=PERIODS)
    scaffold(d, force=True)
    assert SCAFFOLD_LABEL in (d / "regions.csv").read_text()


def test_with_analysis_prefills_the_raw_bounds(tmp_path: Path):
    """Equal to the raw bounds, so the file is legal the moment it is written and
    narrowing it is an edit rather than a construction."""
    d = folder(tmp_path)
    _, rows = scaffold(d, with_analysis=True)
    row, = rows
    assert row["analysis_start_sec"] == row["start_sec"]
    assert row["analysis_end_sec"] == row["end_sec"]


def test_the_scaffold_is_newline_only_like_the_contract_asks(tmp_path: Path):
    """It has to pass the check that reads it, and the format rule is part of
    the contract — a stray carriage return corrupts the last column under exact
    comparison."""
    d = folder(tmp_path)
    path, _ = scaffold(d)
    raw = path.read_bytes()
    assert b"\r" not in raw
    with path.open(newline="") as fh:
        assert [r["label"] for r in csv.DictReader(fh)] == [SCAFFOLD_LABEL]


# ---------------------------------------------------------------------------
# the command
# ---------------------------------------------------------------------------

def test_windows_reports_without_writing_anything(tmp_path: Path, capsys):
    d = folder(tmp_path)
    with pytest.raises(SystemExit) as e:
        main(["windows", str(d)])
    assert e.value.code == 0
    assert not (d / "regions.csv").exists()
    assert "NO PERIODS" in capsys.readouterr().out


def test_with_analysis_alone_is_refused_rather_than_ignored(tmp_path: Path):
    """A flag that silently does nothing is how somebody believes they sent
    analysis windows."""
    with pytest.raises(SystemExit) as e:
        main(["windows", str(folder(tmp_path)), "--with-analysis"])
    assert "only means something with --create" in str(e.value)


def test_force_alone_is_refused_too(tmp_path: Path):
    with pytest.raises(SystemExit) as e:
        main(["windows", str(folder(tmp_path)), "--force"])
    assert "only means something with --create" in str(e.value)


def test_create_says_what_is_still_missing(tmp_path: Path, capsys):
    """The draft is half an answer and the output has to say which half."""
    with pytest.raises(SystemExit) as e:
        main(["windows", str(folder(tmp_path)), "--create"])
    assert e.value.code == 0
    out = capsys.readouterr().out
    assert "NOT FINISHED" in out
    assert SCAFFOLD_LABEL in out
    assert "one row per recording is a guess" in out.lower()


def test_creating_over_an_existing_file_exits_with_the_reason(tmp_path: Path):
    d = folder(tmp_path, regions=PERIODS)
    with pytest.raises(SystemExit) as e:
        main(["windows", str(d), "--create"])
    assert "will not overwrite" in str(e.value)
    assert "pre-drug" in (d / "regions.csv").read_text()
