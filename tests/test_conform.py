"""Tests for the conformance check a producer runs on their own export folder.

The point of each test is the *message*: a check that says "not conforming" and
nothing else sends the producer back to the spec to guess, which is the failure
this tool exists to remove.
"""

from __future__ import annotations

from pathlib import Path

from bugarach.conform import check_folder, format_report


def _write(d: Path, **files) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        (d / f"{name}.csv").write_text(text)
    return d


GOOD = "roi,time_sec,stream\n1,1.0,fast\n1,2.0,fast\n2,NA,fast\n2,5.0,slow\n"


def test_a_conforming_folder_passes_and_reports_what_it_found(tmp_path: Path):
    d = _write(tmp_path / "e", s1=GOOD,
               regions="slice_id,region_idx,label,start_sec,end_sec\n"
                       "s1,2,TTX,60,120\ns1,1,baseline,0,60\n",
               slices="slice_id,frame_interval_sec\ns1,0.05\n")
    rep = check_folder(d)
    assert rep.ok and rep.n_ok == 1
    r, = rep.recordings
    assert (r.slice_id, r.n_rois, r.n_events) == ("s1", 2, 3)
    assert r.streams == ["fast", "slow"]
    assert r.windows == ["baseline", "TTX"]        # producer's own order
    assert r.frame_interval == "0.05"
    assert r.n_silent == 0                          # ROI 2 fires in slow
    assert "CONFORMING" in format_report(rep)


def test_silence_is_counted_across_streams_not_within_one(tmp_path: Path):
    """An ROI quiet in FAST but firing in SLOW was not missed by the producer;
    only an ROI quiet everywhere is one they had to declare."""
    d = _write(tmp_path / "e",
               s1="roi,time_sec,stream\n1,1.0,fast\n2,NA,fast\n2,NA,slow\n")
    r, = check_folder(d).recordings
    assert r.n_rois == 2 and r.n_silent == 1


def test_no_declared_silence_is_a_note_not_a_failure(tmp_path: Path):
    d = _write(tmp_path / "e", s1="roi,time_sec\n1,1.0\n2,2.0\n")
    rep = check_folder(d)
    assert rep.ok                                   # conforming: it may be true
    r, = rep.recordings
    assert any("no events" in n and "too high" in n for n in r.notes)


def test_a_folder_with_no_recordings_says_what_it_found(tmp_path: Path):
    d = _write(tmp_path / "e", slices="slice_id,frame_interval_sec\ns1,0.05\n")
    rep = check_folder(d)
    assert not rep.ok
    msg = format_report(rep)
    assert "no recording files" in msg and "slices.csv" in msg


def test_a_label_in_the_ordering_column_names_the_line_and_the_column(tmp_path):
    d = _write(tmp_path / "e", s1=GOOD,
               regions="slice_id,region_idx,label,start_sec,end_sec\n"
                       "s1,baseline,baseline,0,60\n")
    rep = check_folder(d)
    assert not rep.ok
    msg = format_report(rep)
    assert "line 2" in msg and "'label'" in msg


def test_an_unreadable_time_names_the_line(tmp_path: Path):
    d = _write(tmp_path / "e", s1="roi,time_sec\n1,1.0\n2,about noon\n")
    rep = check_folder(d)
    assert not rep.ok and "line 3" in format_report(rep)


def test_a_frame_interval_that_is_not_seconds_fails_that_recording(tmp_path):
    """The likeliest interval mistake is shipping a rate instead of a period."""
    d = _write(tmp_path / "e", s1=GOOD,
               slices="slice_id,frame_interval_sec\ns1,30fps\n")
    rep = check_folder(d)
    assert not rep.ok
    r, = rep.recordings
    assert any("not a number of seconds" in e for e in r.errors)


def test_a_nonpositive_frame_interval_fails(tmp_path: Path):
    d = _write(tmp_path / "e", s1=GOOD,
               slices="slice_id,frame_interval_sec\ns1,0\n")
    assert not check_folder(d).ok


def test_a_missing_table_column_is_named(tmp_path: Path):
    d = _write(tmp_path / "e", s1=GOOD,
               regions="slice_id,region_idx,label,start_sec\ns1,1,baseline,0\n")
    rep = check_folder(d)
    assert not rep.ok and "end_sec" in format_report(rep)


def test_a_table_that_misses_a_recording_is_a_folder_note(tmp_path: Path):
    d = _write(tmp_path / "e", s1=GOOD, s2="roi,time_sec\n1,1.0\n",
               slices="slice_id,frame_interval_sec\ns1,0.05\n")
    rep = check_folder(d)
    assert rep.ok                                   # readable, just incomplete
    assert any("no row for" in n for n in rep.notes)


def test_absent_tables_are_allowed_and_explained(tmp_path: Path):
    d = _write(tmp_path / "e", s1=GOOD)
    rep = check_folder(d)
    assert rep.ok
    joined = " ".join(rep.notes)
    assert "no regions.csv" in joined and "no slices.csv" in joined
    assert "asks for" in joined                     # says what happens next


def test_not_a_folder(tmp_path: Path):
    rep = check_folder(tmp_path / "nope")
    assert not rep.ok and "not a folder" in format_report(rep)
