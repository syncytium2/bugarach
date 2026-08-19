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


def test_pretrimmed_windows_fail_the_check_even_though_they_load(tmp_path: Path):
    """The blind spot that cost an export. A folder whose regions are already
    analysis windows — baseline capped backward off zero, a wash-in gap at each
    boundary — parses perfectly and then halts every detector. Loading is not
    the same as being analysable, and the check has to know the difference."""
    d = _write(tmp_path / "e", s1=GOOD,
               regions="slice_id,region_idx,label,start_sec,end_sec\n"
                       "s1,1,baseline,60,1260\n"        # does not start at 0
                       "s1,2,TTX,1380,2580\n")          # 2-minute wash-in gap
    rep = check_folder(d)
    assert not rep.ok, "a folder no detector can run on must not pass"
    r, = rep.recordings
    joined = " ".join(r.errors)
    assert "no detector can run on it" in joined
    # both ways out are offered, because either is a valid fix and the producer
    # knows which one their pipeline can actually do
    assert "RAW period" in joined, "say what to send instead"
    assert "analysis_start_sec" in joined, "offer the analysis-window column too"


def test_supplied_analysis_windows_are_used_as_given(tmp_path: Path):
    """Raw bounds plus the producer's own windows: their windows get scored, and
    the wash-in delay and cap this project would have applied do not appear."""
    from bugarach.detectors.loco import effective_region_windows
    from bugarach.detectors.rate import recording_extent
    from bugarach.io import load_folder

    d = _write(tmp_path / "e", s1=GOOD,
               regions="slice_id,region_idx,label,start_sec,end_sec,"
                       "analysis_start_sec,analysis_end_sec\n"
                       "s1,1,baseline,0,1260,60,1260\n"      # window not at 0
                       "s1,2,TTX,1260,2580,1380,2400\n")     # their delay + cap
    rep = check_folder(d)
    assert rep.ok, [e for r in rep.recordings for e in r.errors] + rep.errors
    r, = rep.recordings
    assert any("scored as given" in n for n in r.notes)

    s, = load_folder(d)
    rw = effective_region_windows(s, recording_extent(s))
    assert [(w.win_start, w.win_end) for w in rw] == [(60.0, 1260.0), (1380.0, 2400.0)]
    # the raw period travels alongside, so how much was trimmed stays visible
    assert [(w.raw_start, w.raw_end) for w in rw] == [(0.0, 1260.0), (1260.0, 2580.0)]


def test_half_a_slice_of_analysis_windows_is_refused(tmp_path: Path):
    """Two policies inside one number is worse than either one alone."""
    d = _write(tmp_path / "e", s1=GOOD,
               regions="slice_id,region_idx,label,start_sec,end_sec,"
                       "analysis_start_sec,analysis_end_sec\n"
                       "s1,1,baseline,0,1260,60,1260\n"
                       "s1,2,TTX,1260,2580,,\n")
    rep = check_folder(d)
    assert not rep.ok
    assert any("two policies" in e for r in rep.recordings for e in r.errors)


def test_one_bound_of_an_analysis_window_is_refused(tmp_path: Path):
    d = _write(tmp_path / "e", s1=GOOD,
               regions="slice_id,region_idx,label,start_sec,end_sec,"
                       "analysis_start_sec,analysis_end_sec\n"
                       "s1,1,baseline,0,1260,60,\n")
    rep = check_folder(d)
    assert not rep.ok
    assert any("given together" in e for e in rep.errors)


def test_raw_contiguous_windows_pass(tmp_path: Path):
    """The same two periods, sent raw: region 1 at 0, region 2 where 1 ended."""
    d = _write(tmp_path / "e", s1=GOOD,
               regions="slice_id,region_idx,label,start_sec,end_sec\n"
                       "s1,1,baseline,0,1260\n"
                       "s1,2,TTX,1260,2580\n")
    rep = check_folder(d)
    assert rep.ok, [e for r in rep.recordings for e in r.errors] + rep.errors


# --- the gates a producer sending analysis windows used to fall straight through
#
# Supplying the columns routes a folder through `supplied_region_windows`, which
# validated nothing at all, so the two pairs of bounds that decide what gets
# scored were checked by neither side. Found by interface2 running our own gates
# against a deliberately broken folder, 2026-08-18.


BAD_WINDOW_FOLDER = ("slice_id,region_idx,label,start_sec,end_sec,"
                     "analysis_start_sec,analysis_end_sec\n"
                     "s1,1,baseline,500,1400,99999,-500\n"
                     "s1,2,TTX,10300,12000,10400,11000\n")


def test_the_folder_that_passed_while_scoring_minus_100499_seconds(tmp_path: Path):
    """interface2's reproduction, verbatim. `bugarach check` printed CONFORMING
    and `effective_region_windows` handed the detectors a window of -100,499 s."""
    d = _write(tmp_path / "e", s1=GOOD, regions=BAD_WINDOW_FOLDER)
    rep = check_folder(d)
    assert not rep.ok
    joined = " ".join(e for r in rep.recordings for e in r.errors)
    assert "-100499" in joined.replace(",", "").replace(".000000", ""), joined
    assert "scores nothing" in joined


def test_an_analysis_window_that_ends_before_it_starts_is_refused(tmp_path: Path):
    d = _write(tmp_path / "e", s1=GOOD,
               regions="slice_id,region_idx,label,start_sec,end_sec,"
                       "analysis_start_sec,analysis_end_sec\n"
                       "s1,1,baseline,0,1260,900,300\n")
    rep = check_folder(d)
    assert not rep.ok
    assert any("scores nothing" in e for r in rep.recordings for e in r.errors)


def test_an_analysis_window_outside_its_own_period_is_refused(tmp_path: Path):
    """The two pairs contradict each other and the file cannot say which is wrong."""
    d = _write(tmp_path / "e", s1=GOOD,
               regions="slice_id,region_idx,label,start_sec,end_sec,"
                       "analysis_start_sec,analysis_end_sec\n"
                       "s1,1,baseline,0,1260,60,1260\n"
                       "s1,2,TTX,1260,2580,1380,9999\n")
    rep = check_folder(d)
    assert not rep.ok
    assert any("outside its own period" in e
               for r in rep.recordings for e in r.errors)


def test_a_period_that_ends_before_it_starts_is_refused(tmp_path: Path):
    d = _write(tmp_path / "e", s1=GOOD,
               regions="slice_id,region_idx,label,start_sec,end_sec,"
                       "analysis_start_sec,analysis_end_sec\n"
                       "s1,1,baseline,1260,60,100,200\n")
    rep = check_folder(d)
    assert not rep.ok
    assert any("cannot end first" in e for r in rep.recordings for e in r.errors)


def test_a_non_finite_analysis_start_is_refused(tmp_path: Path):
    d = _write(tmp_path / "e", s1=GOOD,
               regions="slice_id,region_idx,label,start_sec,end_sec,"
                       "analysis_start_sec,analysis_end_sec\n"
                       "s1,1,baseline,0,1260,nan,1260\n")
    rep = check_folder(d)
    assert not rep.ok
    assert any("finite time" in e for r in rep.recordings for e in r.errors)


def test_a_foreign_folder_that_is_neither_contiguous_nor_zero_based_passes(tmp_path):
    """FOUNDATIONS §4, and the reason these guards are the universal subset only.

    interface2 asked for `region_windows`' two HALT guards on this path — baseline
    at 0, regions contiguous. Both encode aCa5z's protocol. This folder violates
    both and is perfectly legal: recording starts 500 s in, and 8,900 s of the
    recording sit between the two periods because nothing was being applied then.
    Its windows are sane, so it must load and score.
    """
    from bugarach.detectors.loco import effective_region_windows
    from bugarach.detectors.rate import recording_extent
    from bugarach.io import load_folder

    d = _write(tmp_path / "e", s1=GOOD,
               regions="slice_id,region_idx,label,start_sec,end_sec,"
                       "analysis_start_sec,analysis_end_sec\n"
                       "s1,1,pre-drug,500,1400,600,1400\n"
                       "s1,2,TTX,10300,12000,10400,11000\n")
    rep = check_folder(d)
    assert rep.ok, [e for r in rep.recordings for e in r.errors] + rep.errors

    s, = load_folder(d)
    rw = effective_region_windows(s, recording_extent(s))
    assert [(w.win_start, w.win_end) for w in rw] == [(600.0, 1400.0),
                                                      (10400.0, 11000.0)]


def test_a_period_running_to_the_end_of_the_recording_still_clamps(tmp_path: Path):
    """A non-finite `end_sec` means "it ran to the end", which is legal and is
    why the clamp exists. The new period guard must not refuse it."""
    from bugarach.detectors.loco import supplied_region_windows
    from bugarach.store import Region, Slice

    s = Slice(slice_id="s1", streams={}, roi_ids=None, regions=[
        Region(name="baseline", slot="1", start_sec=0.0, end_sec=600.0,
               analysis_start_sec=0.0, analysis_end_sec=600.0),
        Region(name="TTX", slot="2", start_sec=600.0, end_sec=float("inf"),
               analysis_start_sec=700.0, analysis_end_sec=float("inf")),
    ])
    rw = supplied_region_windows(s, 1800.0)
    assert [(w.win_start, w.win_end) for w in rw] == [(0.0, 600.0), (700.0, 1800.0)]
    assert rw[1].raw_end == 1800.0
