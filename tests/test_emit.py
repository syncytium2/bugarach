"""The writer, and the round trip that is the point of it.

Two things are being checked, and they fail differently. The **mapping** tests say
that each detector's own field names were read — a wrong entry in `DETECTOR_FIELDS`
produces a file that looks perfectly well-formed and holds the wrong numbers, which
no amount of CSV validation would catch. The **round-trip** tests say the file
survives being read back, which is where `NA`, a real zero, and a NaN go wrong.
"""

from __future__ import annotations

import json

import numpy as np
import pytest

from bugarach import emit
from bugarach.emit import (
    DETECTOR_FIELDS,
    NA,
    DetectedEvent,
    events_from,
    read_detections,
    read_detector_settings,
    write_detections,
    write_detector_settings,
    write_run,
)


class FakeFlat:
    """A `rate`/`sync`-shaped result: parallel arrays, `locs`/`widths`/`amps`."""

    def __init__(self, **kw):
        self.locs = np.array([1.0, 2.5])
        self.widths = np.array([0.4, 0.8])
        self.amps = np.array([3.0, 4.0])
        self.n_participating_rois = np.array([5, 7])
        self.settings = {"detection_mode": "threshold"}
        self.__dict__.update(kw)


class FakeNested:
    """A `loco`/`sce`/`cicada` stream: carries its own per-event region."""

    def __init__(self, **kw):
        self.onset_sec = np.array([10.0, 20.0])
        self.width_sec = np.array([1.0, 2.0])
        self.strength = np.array([6.0, 8.0])
        self.magnitude = np.array([6.0, 8.0])
        self.mag_total = np.array([9, 11])
        self.region = ["baseline", "ttx"]
        self.width_kind = "tightness"
        self.params = {}
        self.__dict__.update(kw)


# --------------------------------------------------------------------------
# the mapping
# --------------------------------------------------------------------------

def test_every_detector_declares_a_strength_unit():
    """The unit travels in the row, so no entry may leave it blank."""
    for name, spec in DETECTOR_FIELDS.items():
        assert spec.strength_unit, f"{name} has no strength unit"


def test_the_six_are_all_here():
    assert set(DETECTOR_FIELDS) == {"rate", "coact", "sync", "loco", "sce", "cicada"}


def test_no_two_detectors_share_a_strength_unit():
    """Two detectors sharing a unit string would make the column ambiguous again
    in exactly the way the unit column exists to prevent."""
    units = [s.strength_unit for s in DETECTOR_FIELDS.values()]
    assert len(set(units)) == len(units)


def test_rate_reports_no_participation_and_says_so_as_NA():
    """RateDetect measures how fast the population fires and returns no
    participant count at all. That is a fact about the detector, so the column is
    NA rather than 0 — a zero would claim no cells took part."""
    assert DETECTOR_FIELDS["rate"].n_roi is None
    ev = events_from(FakeFlat(), detector="rate", slice_id="s1", stream="fast")
    assert [e.n_roi for e in ev] == [None, None]
    assert ev[0].row()["n_roi"] == NA


def test_flat_detectors_are_read_from_their_own_field_names():
    ev = events_from(FakeFlat(), detector="sync", slice_id="s1", stream="fast")
    assert [e.onset_sec for e in ev] == [1.0, 2.5]
    assert [e.width_sec for e in ev] == [0.4, 0.8]
    assert [e.n_roi for e in ev] == [5, 7]
    assert ev[0].strength_unit == "spike_synchronization_c"


def test_the_three_that_build_a_set_report_mag_total_not_magnitude():
    """`magnitude` is the peak bin; `mag_total` is everyone recruited anywhere in
    the episode. The participant count is the second one."""
    r = FakeNested(magnitude=np.array([6.0, 8.0]), mag_total=np.array([9, 11]))
    ev = events_from(r, detector="sce", slice_id="s1", stream="fast")
    assert [e.n_roi for e in ev] == [9, 11]


def test_a_per_event_region_wins_over_the_callers():
    """The nested three score inside a region and say which. Where they do, that
    is the region the call was actually made in."""
    ev = events_from(FakeNested(), detector="loco", slice_id="s1", stream="fast",
                     region_label="whatever-the-caller-thought")
    assert [e.region_label for e in ev] == ["baseline", "ttx"]


def test_the_caller_supplies_the_region_for_detectors_run_per_window():
    ev = events_from(FakeFlat(), detector="rate", slice_id="s1", stream="fast",
                     region_idx=2, region_label="ttx")
    assert ev[0].region_idx == 2 and ev[0].region_label == "ttx"


def test_half_prominence_width_reports_peak_mode():
    """The width returned *is* a different quantity in the two modes, so it is a
    more reliable witness than the argument that asked for the mode."""
    ev = events_from(FakeNested(width_kind="half_prominence"), detector="sce",
                     slice_id="s1", stream="fast")
    assert ev[0].mode == "peak"
    assert ev[0].width_def == "half_prominence"


def test_detection_mode_in_the_settings_is_read_when_there_is_no_width_kind():
    r = FakeFlat(settings={"detection_mode": "peak"})
    assert events_from(r, detector="rate", slice_id="s1", stream="fast")[0].mode == "peak"


def test_an_unknown_detector_is_refused_and_the_message_says_where_to_add_it():
    with pytest.raises(ValueError, match="DETECTOR_FIELDS"):
        events_from(FakeFlat(), detector="nope", slice_id="s1", stream="fast")


def test_parallel_arrays_of_different_lengths_are_refused():
    """A length mismatch means a wrong field was read, and reading the shorter one
    would silently drop events rather than fail."""
    r = FakeFlat(widths=np.array([0.4]))
    with pytest.raises(ValueError, match="lengths disagree"):
        events_from(r, detector="rate", slice_id="s1", stream="fast")


# --------------------------------------------------------------------------
# the round trip
# --------------------------------------------------------------------------

def _one(**kw) -> DetectedEvent:
    base = dict(slice_id="s1", stream="fast", detector="coact", mode="threshold",
                onset_sec=1.5, width_sec=0.25, strength=3.5,
                strength_unit="coactivity_z", region_idx=1,
                region_label="baseline", n_roi=4)
    base.update(kw)
    return DetectedEvent(**base)


def test_a_real_zero_survives_the_round_trip_as_zero(tmp_path):
    """Zero is a value. A writer that spells it as missing loses a finding."""
    p = write_detections([_one(strength=0.0, n_roi=0, onset_sec=0.0)],
                         tmp_path / "detections.csv")
    back = read_detections(p)[0]
    assert back["strength"] == 0.0
    assert back["n_roi"] == 0
    assert back["onset_sec"] == 0.0


def test_a_missing_value_is_spelled_NA_and_comes_back_as_None(tmp_path):
    p = write_detections([_one(n_roi=None, region_idx=None)],
                         tmp_path / "detections.csv")
    assert ",NA," in p.read_text(encoding="utf-8")
    back = read_detections(p)[0]
    assert back["n_roi"] is None and back["region_idx"] is None


def test_a_nan_is_absence_not_a_number(tmp_path):
    """NaN is how the detectors spell 'not applicable in this mode'. Writing it
    literally would put the string `nan` in a numeric column."""
    p = write_detections([_one(strength=float("nan"))], tmp_path / "d.csv")
    assert "nan" not in p.read_text(encoding="utf-8").lower()
    assert read_detections(p)[0]["strength"] is None


def test_line_endings_are_newline_only(tmp_path):
    p = write_detections([_one()], tmp_path / "d.csv")
    assert b"\r" not in p.read_bytes()


def test_identity_columns_are_carried_through_untouched(tmp_path):
    ident = {"subject_id": "m14", "group_id": "ORX", "note": "second attempt"}
    p = write_detections([_one(identity=ident)], tmp_path / "d.csv")
    back = read_detections(p)[0]
    for k, v in ident.items():
        assert back[k] == v


def test_identity_cannot_overwrite_a_computed_column(tmp_path):
    """A producer whose slices.csv happens to carry a `detector` column must not
    be able to replace which detector fired."""
    p = write_detections([_one(identity={"detector": "not-this-one"})],
                         tmp_path / "d.csv")
    assert read_detections(p)[0]["detector"] == "coact"


def test_a_slice_with_no_detections_still_writes_a_file_with_a_header(tmp_path):
    """No rows is a finding; no file is a bug. They must not look the same."""
    p = write_detections([], tmp_path / "d.csv")
    text = p.read_text(encoding="utf-8")
    assert text.startswith("slice_id,stream,detector,")
    assert read_detections(p) == []


def test_a_float_survives_to_full_precision(tmp_path):
    """The onset is a time on the recording's own clock. Rounding it here would be
    this module inventing a tolerance nobody asked for."""
    t = 1234.5678901234567
    p = write_detections([_one(onset_sec=t)], tmp_path / "d.csv")
    assert read_detections(p)[0]["onset_sec"] == t


def test_no_column_named_for_a_treatment_slot_or_a_viability_claim(tmp_path):
    """Two rules at once. There is no privileged region and no reserved
    vocabulary, so no `treatment` column; and a viability verdict is the
    exporter's, so no `dead`, `silent` or `alive` column, ever."""
    p = write_detections([_one()], tmp_path / "d.csv")
    header = p.read_text(encoding="utf-8").splitlines()[0].lower().split(",")
    for banned in ("treatment", "dead", "silent", "alive", "inactive", "viable"):
        assert banned not in header


# --------------------------------------------------------------------------
# the sidecars
# --------------------------------------------------------------------------

def test_settings_are_keyed_by_detector_and_stream(tmp_path):
    """One detector may run with different settings per stream, and a table that
    could not say so would make one of the two unreproducible."""
    p = write_detector_settings(
        {("sce", "fast"): {"bin_width_sec": 10.0},
         ("sce", "slow"): {"bin_width_sec": 60.0}},
        tmp_path / "detector_settings.csv")
    rows = list(p.read_text(encoding="utf-8").splitlines())
    assert "sce,fast,bin_width_sec,10.0" in rows
    assert "sce,slow,bin_width_sec,60.0" in rows


def test_settings_round_trip_through_their_own_reader(tmp_path):
    """The sibling of `read_detections`, and it exists for the same reason.

    Two writers produce this file — `write_detector_settings` and the browser
    page, which has no Python to call — so a file only one of them can parse is
    a second dialect of one table. The keys have to come back as the
    `(detector, stream)` pairs they went in as, or a consumer cannot tell the
    fast settings from the slow ones.
    """
    written = {("sce", "fast"): {"bin_width_sec": 10.0, "n_surrogates": 200},
               ("sce", "slow"): {"bin_width_sec": 60.0, "n_surrogates": 200},
               ("sync", "fast"): {"tau_max": 0.25, "note": None}}
    p = write_detector_settings(written, tmp_path / "detector_settings.csv")
    got = read_detector_settings(p)
    assert set(got) == set(written)
    assert float(got[("sce", "slow")]["bin_width_sec"]) == 60.0
    # NA comes back as absence rather than as the string "NA" — the same
    # distinction `read_detections` keeps, for the same reason.
    assert got[("sync", "fast")]["note"] is None


def test_a_file_that_is_not_a_settings_file_says_so(tmp_path):
    """A recording opened as a settings file is the obvious slip, and it has to
    name the missing column rather than returning an empty dict — which would
    read as "this run used no settings"."""
    p = tmp_path / "notsettings.csv"
    p.write_text("roi,time_sec\nr01,1.0\n", encoding="utf-8")
    with pytest.raises(ValueError, match="detector settings"):
        read_detector_settings(p)


def test_the_run_roster_lists_a_slice_that_produced_no_rows(tmp_path):
    """This is the half of 'no detections is not no slice' that detections.csv
    structurally cannot hold."""
    p = write_run(tmp_path / "run.json", slices=["s1", "s2", "quiet_one"],
                  frame_interval_sec={"s1": 0.1, "s2": 0.05, "quiet_one": 0.1})
    doc = json.loads(p.read_text(encoding="utf-8"))
    assert "quiet_one" in doc["slices"]
    assert doc["frame_interval_sec"]["s2"] == 0.05


def test_a_run_with_no_generator_says_null_rather_than_omitting_the_key(tmp_path):
    """A detection pass over a real folder has no generator spec and no chosen K.
    Writing null says the question was asked; omitting the key says nothing."""
    p = write_run(tmp_path / "run.json", slices=["s1"],
                  frame_interval_sec={"s1": 0.1})
    doc = json.loads(p.read_text(encoding="utf-8"))
    assert doc["generator_spec"] is None
    assert doc["chosen_k"] is None
    assert "simulated_data_seeds" in doc


def test_emit_reads_nothing_from_outside_the_values_it_was_given(tmp_path):
    """The writer is pure: no environment variable, no data root, no darkroom.
    Everything it writes came in as an argument."""
    src = (emit.__file__)
    text = open(src, encoding="utf-8").read()
    for reach in ("os.environ", "getenv", "BUGARACH_DATA_ROOT", "darkroom",
                  "requests", "urllib"):
        assert reach not in text


# --------------------------------------------------------------------------
# the mapping, against the real detectors
# --------------------------------------------------------------------------

# Everything above uses fakes. Fakes prove the writer's logic and prove *nothing*
# about whether `DETECTOR_FIELDS` names fields that exist — a wrong entry there
# produces a perfectly well-formed file holding the wrong numbers. So this runs the
# actual six and reads the actual objects. It is the only test here that would
# notice a detector renaming a field.


@pytest.fixture(scope="module")
def bench_slice():
    """A short bench recording. Deliberately not the benched one: this is a
    mapping check, not a measurement, and 20 minutes is enough to make every
    detector fire while keeping the suite quick."""
    from bugarach import bench

    s, _gt = bench.make_recording(
        "baseline_quiet", 1, duration_sec=1200.0, n_per_level=(2, 2, 1),
        n_distractors=2, hot_window=(600.0, 700.0),
        distractor_window=(120.0, 560.0))
    return s


@pytest.mark.parametrize("name", sorted(DETECTOR_FIELDS))
def test_the_mapping_reads_fields_the_real_detector_actually_has(name, bench_slice):
    from bugarach import bench

    result = bench.run_detector(name, bench_slice)
    events = events_from(result, detector=name,
                         slice_id=bench_slice.slice_id, stream="events")
    assert events, (f"{name} detected nothing here, so this test checked a "
                    f"mapping it never exercised — fix the recording, not this "
                    f"assertion")
    for e in events:
        assert np.isfinite(e.onset_sec) and np.isfinite(e.width_sec)
        assert e.width_sec >= 0.0
        assert e.strength_unit == DETECTOR_FIELDS[name].strength_unit
        assert e.mode in ("threshold", "peak")
        if DETECTOR_FIELDS[name].n_roi is None:
            assert e.n_roi is None
        else:
            assert e.n_roi is not None and e.n_roi >= 0


def test_all_six_write_into_one_table_without_a_column_changing_meaning(
        bench_slice, tmp_path):
    """The point of the whole exercise: six detectors, one file, and the unit of
    `strength` stated in the row rather than looked up somewhere else."""
    from bugarach import bench

    every = []
    for name in sorted(DETECTOR_FIELDS):
        every += events_from(bench.run_detector(name, bench_slice),
                             detector=name, slice_id=bench_slice.slice_id,
                             stream="events")
    back = read_detections(write_detections(every, tmp_path / "detections.csv"))
    assert len(back) == len(every)
    assert ({r["detector"]: r["strength_unit"] for r in back}
            == {n: s.strength_unit for n, s in DETECTOR_FIELDS.items()})
