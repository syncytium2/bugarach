"""`bugarach assess` — the assessment pointed at a lab's own export folder.

What these pin is not the arithmetic (that is `test_assess.py`'s job) but the
**reporting policy**, which is where this layer can do harm: choosing K for the
reader, printing a NaN as if it were a measurement, or sourcing coordination
properties from a treatment window.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from bugarach.assess_folder import (
    assess_folder,
    format_assessment,
    is_baseline,
)
from bugarach.simulate import simulate_coordination


def _write_folder(root: Path, *, regions: str | None, duration=1800.0, n=2,
                  n_per_level=(4, 4, 4), min_sep=60.0) -> Path:
    """A conforming export folder, written the way a producer would."""
    root.mkdir(parents=True, exist_ok=True)
    for i in range(n):
        s, _ = simulate_coordination(duration_sec=duration, n_roi=20,
                                     bg_rate_hz=0.02, n_per_level=n_per_level,
                                     min_sep_sec=min_sep, seed=100 + i)
        locs = s.streams["events"].locs
        rows = ["roi,time_sec"]
        for r, v in enumerate(locs):
            if not len(v):
                rows.append(f"{r + 1},NA")
            for t in v:
                rows.append(f"{r + 1},{t:.1f}")
        (root / f"rec_{i + 1}.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (root / "slices.csv").write_text(
        "slice_id,frame_interval_sec\n"
        + "".join(f"rec_{i + 1},0.1\n" for i in range(n)), encoding="utf-8")
    if regions is not None:
        (root / "regions.csv").write_text(regions, encoding="utf-8")
    return root


def test_a_folder_with_no_regions_is_assessed_whole_and_says_so(tmp_path):
    """The common case for an outside lab: no regions.csv at all.

    The contract gives such a recording one implicit whole-recording window, so
    it must be assessed rather than dropped — and the report must name the window
    it got, because a whole recording is an assumption and not a baseline."""
    fa = assess_folder(_write_folder(tmp_path / "f", regions=None),
                       n_surrogates=25)
    assert len(fa.measured) == 2, [r.skipped for r in fa.records]
    for rec in fa.measured:
        assert "whole recording" in rec.window_source
        assert "no regions declared" in rec.window_source


def test_the_summary_says_how_many_windows_were_assumed(tmp_path):
    """Said once at the top, not only per recording.

    Tony, 2026-09-10: when no baseline is defined, use the whole trace and
    **flag to the user that we did it**. The per-recording ``window:`` line has
    always carried it, but a reader scanning 84 blocks for numbers is not
    reading 84 window lines, and the assumption has to arrive before the
    numbers rather than beside them.
    """
    fa = assess_folder(_write_folder(tmp_path / "f", regions=None),
                       n_surrogates=25)
    assert len(fa.assumed) == 2, [r.window_source for r in fa.measured]

    head = format_assessment(fa).split("\n\n")[0]
    assert "declare no regions" in head, head
    assert "WHOLE" in head, head
    # It names them, or the reader cannot go and check which.
    for rec in fa.measured:
        assert rec.slice_id in head, head


def test_a_declared_baseline_is_not_reported_as_assumed(tmp_path):
    """The counterpart: a folder that states its periods produces no flag, or
    the warning becomes noise a reader learns to scroll past."""
    regions = ("slice_id,region_idx,label,start_sec,end_sec\n"
               "rec_1,1,baseline,0,1800\n"
               "rec_2,1,baseline,0,1800\n")
    fa = assess_folder(_write_folder(tmp_path / "f", regions=regions),
                       n_surrogates=25)
    assert fa.measured, [r.skipped for r in fa.records]
    assert fa.assumed == []
    assert "declare no regions" not in format_assessment(fa)


def test_a_treatment_only_folder_is_refused_not_measured(tmp_path):
    """FOUNDATIONS §9: coordination properties are not taken from treatments.

    A folder whose only declared regions are drugs must come back unmeasured,
    with the reason said out loud — not silently assessed on a TTX window."""
    regions = ("slice_id,region_idx,label,start_sec,end_sec\n"
               "rec_1,1,TTX,0,1800\n"
               "rec_2,1,senktide,0,1800\n")
    fa = assess_folder(_write_folder(tmp_path / "f", regions=regions),
                       n_surrogates=25)
    assert fa.measured == []
    for rec in fa.skipped:
        assert "none named as a baseline" in rec.skipped
    assert "not taken from treatments" in format_assessment(fa)


def test_the_refusal_names_the_labels_the_folder_actually_uses(tmp_path):
    """"None named as a baseline" without the names sends a reader to open a CSV.

    The next move is to designate one of them, and nobody can designate a name
    they have not been shown. The refusal also says which rule was applied, so
    "we guessed from a list" and "we matched your word" are distinguishable."""
    regions = ("slice_id,region_idx,label,start_sec,end_sec\n"
               "rec_1,1,vehicle,0,1800\n"
               "rec_2,1,vehicle,0,1800\n")
    fa = assess_folder(_write_folder(tmp_path / "f", regions=regions),
                       n_surrogates=25)
    assert fa.measured == []
    for rec in fa.skipped:
        assert "vehicle" in rec.skipped, rec.skipped
        assert "looked for" in rec.skipped, rec.skipped


def test_a_designated_label_is_measured_and_the_report_says_who_chose(tmp_path):
    """Tony, 2026-09-10: use whatever the reader provides as the baseline.

    `vehicle` is untreated and no built-in token knows the word, so it is
    refused until designated and measured after. The report must say the choice
    was the reader's — "we matched your word" and "we guessed" are different
    claims and only one of them is theirs to defend."""
    regions = ("slice_id,region_idx,label,start_sec,end_sec\n"
               "rec_1,1,vehicle,0,1800\n"
               "rec_2,1,vehicle,0,1800\n")
    folder = _write_folder(tmp_path / "f", regions=regions)

    fa = assess_folder(folder, n_surrogates=25, baseline_labels=("vehicle",))
    assert len(fa.measured) == 2, [r.skipped for r in fa.records]
    for rec in fa.measured:
        assert "vehicle" in rec.window_source
        assert "you designated it" in rec.window_source
    # Not an assumed whole-recording window: a designation is a statement.
    assert fa.assumed == []


def test_designating_replaces_the_builtin_guess_rather_than_joining_it(tmp_path):
    """A folder with both a designated name and one the built-in list knows.

    `pre-wash` matches the token `pre` and is the LONGER period, so "longest
    baseline wins" would take it. Designating `vehicle` has to mean vehicle, or
    the report claims a designation while measuring something else."""
    regions = ("slice_id,region_idx,label,start_sec,end_sec\n"
               "rec_1,1,vehicle,0,600\n"
               "rec_1,2,pre-wash,600,1800\n"
               "rec_2,1,vehicle,0,600\n"
               "rec_2,2,pre-wash,600,1800\n")
    folder = _write_folder(tmp_path / "f", regions=regions)

    # Undesignated: the guess takes pre-wash, the longer of the two matches.
    guessed = assess_folder(folder, n_surrogates=25)
    assert all("pre-wash" in r.window_source for r in guessed.measured)

    said = assess_folder(folder, n_surrogates=25, baseline_labels=("vehicle",))
    assert len(said.measured) == 2, [r.skipped for r in said.records]
    for rec in said.measured:
        assert "vehicle" in rec.window_source, rec.window_source
        assert "pre-wash" not in rec.window_source, rec.window_source


def test_designation_is_a_prefix_and_case_insensitive(tmp_path):
    """`vehicle` covers `Vehicle 2`, the way `pre` covers `pre-drug`."""
    regions = ("slice_id,region_idx,label,start_sec,end_sec\n"
               "rec_1,1,Vehicle 2,0,1800\n"
               "rec_2,1,VEHICLE,0,1800\n")
    fa = assess_folder(_write_folder(tmp_path / "f", regions=regions),
                       n_surrogates=25, baseline_labels=("vehicle",))
    assert len(fa.measured) == 2, [r.skipped for r in fa.records]


def test_the_baseline_region_is_the_one_assessed(tmp_path):
    regions = ("slice_id,region_idx,label,start_sec,end_sec\n"
               "rec_1,1,baseline,0,1200\nrec_1,2,TTX,1200,1800\n"
               "rec_2,1,baseline,0,1200\nrec_2,2,TTX,1200,1800\n")
    fa = assess_folder(_write_folder(tmp_path / "f", regions=regions),
                       n_surrogates=25)
    assert len(fa.measured) == 2
    for rec in fa.measured:
        assert rec.window == (0.0, 1200.0)
        assert "baseline" in rec.window_source


def test_K_is_reported_as_a_scan_and_never_chosen(tmp_path):
    """The whole point of the layer. `min_rois` moves the headline by an order
    of magnitude, so every K is reported and none is marked as the answer."""
    fa = assess_folder(_write_folder(tmp_path / "f", regions=None),
                       n_surrogates=25)
    from bugarach.assess import DEFAULT_MIN_ROIS

    for rec in fa.measured:
        assert [a.min_rois for a in rec.results] == list(DEFAULT_MIN_ROIS)
    text = format_assessment(fa)
    assert "K is a scan, not a choice" in text
    # no line may present one K as the recommended one
    assert "recommended" not in text.lower()
    assert "best" not in text.lower()


def test_an_undefined_jitter_is_printed_as_a_state_never_as_a_number(tmp_path):
    """`jit_defined` False with a finite-looking `jit_*` is the documented trap.
    The report must render that as words, and must never print a bare 'nan'."""
    fa = assess_folder(_write_folder(tmp_path / "f", regions=None),
                       n_surrogates=25)
    text = format_assessment(fa)
    assert "nan" not in text.lower()

    undefined = [a for rec in fa.measured for a in rec.results if not a.jit_defined]
    if undefined:
        assert "undefined (no cluster in surrogates)" in text
    else:                                   # pragma: no cover - seed-dependent
        pytest.skip("no undefined-jitter K at this seed; the NaN guard still ran")


def test_a_window_under_the_floor_prints_no_numbers(tmp_path):
    """Under `region_min_sec` every measure is NaN. Printing the row anyway is
    how a NaN becomes a quoted result."""
    fa = assess_folder(
        _write_folder(tmp_path / "f", regions=None, duration=300.0,
                      n_per_level=(1, 1, 1), min_sep=30.0),
        n_surrogates=25)
    text = format_assessment(fa)
    assert "under the assessment's floor" in text
    assert "coact excess/min" not in text        # the table itself is withheld


def test_is_baseline_never_guesses_from_position():
    """The export contract forbids treating region 1 as the baseline, and this
    project's own exporter has done it. An unnamed region is not a baseline."""
    class R:
        def __init__(self, name): self.name = name
    assert is_baseline(R("baseline"))
    assert is_baseline(R("Pre-drug"))
    assert is_baseline(R("aCSF"))
    assert not is_baseline(R("TTX"))
    assert not is_baseline(R(None))
    assert not is_baseline(R(""))


def test_the_archive_driver_uses_the_same_rule():
    """Two callers, one policy. `tools/assess_archive.py` used to carry its own
    copy; if it grows another, they can disagree about what a baseline is."""
    src = (Path(__file__).resolve().parents[1]
           / "tools" / "assess_archive.py").read_text(encoding="utf-8")
    assert "from bugarach.assess_folder import" in src
    assert "BASELINE_TOKENS = (" not in src
