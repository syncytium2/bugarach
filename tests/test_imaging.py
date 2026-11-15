"""A recording imaged in stretches: the loader's checks, the splice and the map back.

docs/adr/2026-11-14-7a3a-a-recording-imaged-in-stretches-says-so-in-imaging-csv-detec.md.
Synthetic fixtures only.
"""

from __future__ import annotations

import csv

import numpy as np
import pytest

from bugarach import imaging
from bugarach.io import load_folder, slice_from_events

# three stretches of 10 s, 17.5 s apart
STRETCHES = [(0.0, 10.0), (27.5, 37.5), (55.0, 65.0)]


def _slice(times, widths=None, imaging_=STRETCHES, regions=None):
    s = slice_from_events([np.asarray(t, float) for t in times], dt=0.1,
                          durations=widths, width_def="w" if widths else None,
                          regions=regions)
    s.imaging = imaging_
    return s


def _write(folder, rows, stretches=STRETCHES, sid="rec"):
    with (folder / f"{sid}.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["roi", "time_sec", "width_sec", "width_def"])
        w.writerows(rows)
    with (folder / "slices.csv").open("w", newline="") as fh:
        csv.writer(fh).writerows([["slice_id", "frame_interval_sec"], [sid, "0.1"]])
    with (folder / "imaging.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["slice_id", "stretch_idx", "start_sec", "end_sec"])
        for k, (a, b) in enumerate(stretches, start=1):
            w.writerow([sid, k, a, b])


def test_a_folder_without_imaging_csv_is_one_continuous_stretch(tmp_path):
    with (tmp_path / "rec.csv").open("w") as fh:
        fh.write("roi,time_sec\na,1.0\n")
    s = load_folder(tmp_path, dt=0.1)[0]
    assert s.imaging is None
    sp = imaging.splice(s, pad_sec=2.0)
    assert sp.to_real([1.0, 5.0]) == pytest.approx([1.0, 5.0])


def test_the_loader_refuses_an_event_in_a_gap(tmp_path):
    _write(tmp_path, [["a", "20.0", "0.5", "w"]])
    with pytest.raises(imaging.EventOutsideImagingError, match="outside every imaged"):
        load_folder(tmp_path)


def test_the_loader_refuses_an_event_that_runs_across_a_gap(tmp_path):
    _write(tmp_path, [["a", "9.5", "1.0", "w"]])           # ends at 10.5 > 10.0
    with pytest.raises(imaging.EventOutsideImagingError, match="runs past the end"):
        load_folder(tmp_path)


def test_stretch_idx_is_the_ordering_and_must_be_complete(tmp_path):
    _write(tmp_path, [["a", "1.0", "0.5", "w"]])
    with (tmp_path / "imaging.csv").open("w", newline="") as fh:
        csv.writer(fh).writerows([["slice_id", "stretch_idx", "start_sec", "end_sec"],
                                  ["rec", 1, 0, 10], ["rec", 3, 27.5, 37.5]])
    with pytest.raises(ValueError, match="must run 1, 2, 3"):
        load_folder(tmp_path)


def test_splice_closes_the_gaps_and_to_real_reopens_them():
    s = _slice([[1.0, 28.0, 64.0]])
    sp = imaging.splice(s, pad_sec=0.0)
    assert sp.slice.streams["events"].locs[0] == pytest.approx([1.0, 10.5, 29.0])
    assert sp.to_real(sp.slice.streams["events"].locs[0]) == pytest.approx([1.0, 28.0, 64.0])
    assert sp.seams == pytest.approx([10.0, 20.0])
    assert sp.slice.imaging is None


def test_a_pad_keeps_a_window_from_reaching_across_a_seam():
    s = _slice([[9.5], [27.6]])                             # 18.1 s apart on the real clock
    tight = imaging.splice(s, pad_sec=0.0).slice.streams["events"].locs
    padded = imaging.splice(s, pad_sec=3.0).slice.streams["events"].locs
    assert tight[1][0] - tight[0][0] == pytest.approx(0.6)  # a 2 s window would pair them
    assert padded[1][0] - padded[0][0] == pytest.approx(3.6)  # a 2 s window cannot


def test_a_time_inside_a_pad_maps_to_the_end_of_its_stretch_not_into_the_gap():
    sp = imaging.splice(_slice([[1.0]]), pad_sec=3.0)
    # spliced 11.5 is 1.5 s into the pad after stretch 1, which ends at real 10.0
    assert sp.to_real(11.5) == pytest.approx(10.0)
    assert sp.to_real(13.0) == pytest.approx(27.5)          # start of stretch 2


def test_regions_move_with_the_events_and_a_boundary_in_a_gap_snaps_to_imaging():
    s = _slice([[1.0]], regions=[("baseline", 0.0, 20.0), ("drug", 20.0, 65.0)])
    sp = imaging.splice(s, pad_sec=0.0)
    (b, d) = sp.slice.regions
    assert (b.start_sec, b.end_sec) == pytest.approx((0.0, 10.0))   # 20 s is in gap 1
    assert (d.start_sec, d.end_sec) == pytest.approx((10.0, 30.0))


def test_pieces_cut_a_drawn_span_at_the_gaps():
    assert imaging.pieces(8.0, 30.0, STRETCHES) == [(8.0, 10.0), (27.5, 30.0)]
    assert imaging.pieces(1.0, 2.0, None) == [(1.0, 2.0)]


def test_a_negative_pad_is_refused():
    with pytest.raises(ValueError, match="cannot be negative"):
        imaging.splice(_slice([[1.0]]), pad_sec=-1.0)
