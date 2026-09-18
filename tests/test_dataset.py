"""Naming a dataset, and refusing the wrong kind before reading anything.

The failure this exists to prevent is concrete. `synfire_scan.py --store` reads export
folders, and handing it an actual `.mat` store — which is what the flag name invites —
used to produce::

    ValueError: detector_settings.csv must have columns 'time_sec' and 'roi'
                (found ['detector', 'stream', 'param', 'value'])

an error naming an internal file the caller never mentioned. `require()` now says "that
is a mat store, this analysis reads an export folder" before opening anything.

These run anywhere: every case is built in a tmp_path, so none of them need
`$BUGARACH_DATA_ROOT` or the Dropbox mount.
"""
from __future__ import annotations

import pytest

from bugarach import dataset as ds


def _export_folder(root, n=3, extras=("slices.csv", "regions.csv")):
    d = root / "export"
    d.mkdir()
    for i in range(n):
        (d / f"2024010{i}_{i}.csv").write_text("time_sec,roi\n1.0,1\n")
    for e in extras:
        (d / e).write_text("x\n")
    return d


def _mat_store(root, n=4, extras=("detector_settings.csv",)):
    d = root / "store"
    d.mkdir()
    for i in range(n):
        (d / f"2024010{i}_{i}.mat").write_bytes(b"\x00")
    for e in extras:
        (d / e).write_text("detector,stream,param,value\n")
    return d


# ---- kind -----------------------------------------------------------------

def test_export_folder_is_recognised_and_reserved_files_are_not_counted(tmp_path):
    k = ds.kind(_export_folder(tmp_path, n=3))
    assert k.is_export_folder and k.n_recordings == 3, (
        "slices.csv and regions.csv are not recordings")


def test_mat_store_is_recognised_despite_carrying_a_csv(tmp_path):
    """The exact shape that produced the detector_settings.csv error.

    A store directory holds a settings CSV. Counting any `.csv` as evidence of an
    export folder is what let a store be walked into as one.
    """
    k = ds.kind(_mat_store(tmp_path, n=4))
    assert k.is_mat_store and k.n_recordings == 4


def test_a_directory_holding_both_reports_the_majority_and_names_the_rest(tmp_path):
    d = tmp_path / "both"
    d.mkdir()
    for i in range(5):
        (d / f"r{i}.mat").write_bytes(b"\x00")
    (d / "one.csv").write_text("time_sec,roi\n")
    k = ds.kind(d)
    assert k.is_mat_store
    assert "1 loose .csv" in k.detail or "also 1" in k.detail, (
        "the minority shape must be named, not silently dropped")


def test_a_folder_with_only_reserved_files_is_empty_and_says_why(tmp_path):
    d = tmp_path / "hollow"
    d.mkdir()
    (d / "regions.csv").write_text("x\n")
    k = ds.kind(d)
    assert k.name == "empty" and "regions.csv" in k.detail


def test_missing_and_not_a_directory(tmp_path):
    assert ds.kind(tmp_path / "nope").name == "missing"
    f = tmp_path / "f.txt"
    f.write_text("x")
    assert ds.kind(f).name == "missing"


# ---- require --------------------------------------------------------------

def test_the_wrong_kind_is_refused_with_both_halves_named(tmp_path):
    store = _mat_store(tmp_path)
    with pytest.raises(ds.DataError) as e:
        ds.require(store, want="export_folder", flag="--dataset")
    msg = str(e.value)
    assert "mat store" in msg, "must say what it got"
    assert "export folder" in msg, "must say what it needs"
    assert "detector_settings" not in msg, (
        "the whole point is not to surface an internal file the caller never named")


def test_the_right_kind_passes_through(tmp_path):
    d = _export_folder(tmp_path)
    assert ds.require(d, want="export_folder") == d
    assert ds.require(d, want="any") == d


def test_any_still_refuses_an_empty_directory(tmp_path):
    d = tmp_path / "hollow"
    d.mkdir()
    with pytest.raises(ds.DataError):
        ds.require(d, want="any")


# ---- resolve --------------------------------------------------------------

def test_an_existing_path_is_returned_untouched(tmp_path):
    d = _export_folder(tmp_path)
    assert ds.resolve(d) == d
    assert ds.resolve(str(d)) == d


def test_a_bare_name_is_looked_up_under_the_data_root(tmp_path, monkeypatch):
    root = tmp_path / "data"
    (root / "processed_archive").mkdir(parents=True)
    (root / "exports" / "bugarach").mkdir(parents=True)
    store = root / "processed_archive" / "event_store_x"
    store.mkdir()
    (store / "a.mat").write_bytes(b"\x00")
    folder = root / "exports" / "bugarach" / "2026-01-01_x"
    folder.mkdir()
    (folder / "r.csv").write_text("time_sec,roi\n")

    monkeypatch.setenv(ds.ENV_VAR, str(root))
    assert ds.resolve("event_store_x") == store
    assert ds.resolve("2026-01-01_x") == folder


def test_an_unknown_name_lists_what_is_there(tmp_path, monkeypatch):
    root = tmp_path / "data"
    (root / "processed_archive" / "real_one").mkdir(parents=True)
    monkeypatch.setenv(ds.ENV_VAR, str(root))
    with pytest.raises(ds.DataError) as e:
        ds.resolve("typo")
    assert "real_one" in str(e.value), "a typo should show the near misses"


def test_a_bare_name_with_nowhere_to_look_says_so(tmp_path, monkeypatch):
    """No data root and no path: the error must name the variable to set."""
    monkeypatch.setenv(ds.ENV_VAR, str(tmp_path / "does_not_exist"))
    monkeypatch.setattr(ds, "data_root", lambda: None)
    with pytest.raises(ds.DataError) as e:
        ds.resolve("something")
    assert ds.ENV_VAR in str(e.value)


def test_env_var_wins_and_a_bad_one_does_not_silently_fall_back(tmp_path, monkeypatch):
    """A wrong BUGARACH_DATA_ROOT must not be papered over by autodiscovery.

    Falling through to the Dropbox mount would run the analysis on different data
    than the operator asked for and say nothing.
    """
    monkeypatch.setenv(ds.ENV_VAR, str(tmp_path / "nonexistent"))
    assert ds.data_root() is None


def test_describe_names_the_kind_and_the_count(tmp_path):
    line = ds.describe(_export_folder(tmp_path, n=2))
    assert "export folder" in line and "2" in line


# -- the contamination stop ---------------------------------------------------------------
#
# Tony's ruling, 2026-09-17: work stops when the export declares a contamination that
# nothing in the data marks. These tests are what keeps the stop from being softened back
# into a caveat by the next session that finds it inconvenient.

CONTAMINATED = {"steps": {"name": "some_export", "note":
                          "Known contamination this folder does NOT address: moco pinned "
                          "12 ROIs to the frame floor across `20260629_312`. Not flagged in "
                          "any column."}}


def test_a_declared_unflagged_contamination_stops_the_analysis(monkeypatch):
    monkeypatch.setattr(ds, "declared_exports", lambda: CONTAMINATED)
    monkeypatch.delenv(ds.ACK_ENV, raising=False)
    with pytest.raises(ds.ContaminatedExport) as e:
        ds.refuse_if_contaminated("steps")
    assert "frame floor" in str(e.value), "the stop must quote what the producer said"
    assert ds.ACK_ENV in str(e.value), "and say how to proceed deliberately"


def test_the_override_needs_a_reason_and_announces_itself(monkeypatch, capsys):
    monkeypatch.setattr(ds, "declared_exports", lambda: CONTAMINATED)
    monkeypatch.setenv(ds.ACK_ENV, "counts ROIs only, never their values")
    ds.refuse_if_contaminated("steps")
    assert "counts ROIs only" in capsys.readouterr().err, "an override leaves a trace"


def test_a_note_that_says_the_folder_handles_it_does_not_stop_anything(monkeypatch):
    """The stop is for contamination the data do not mark. A folder that removed the
    events, or flagged them in a column, is the resolved case and must not fire."""
    monkeypatch.setattr(ds, "declared_exports", lambda: {
        "steps": {"name": "x", "note": "Known contamination: field steps. Every event "
                                       "within 2 s removed and listed in the sidecar, "
                                       "flagged per event in `on_field_step`."}})
    monkeypatch.delenv(ds.ACK_ENV, raising=False)
    assert ds.contamination_note("steps") is None


def test_the_shipped_pointer_is_checked_not_assumed(monkeypatch):
    """Against this repo's real current_export.toml: whichever roles declare an unflagged
    contamination today, ``refuse_if_contaminated`` must refuse them. When the producer
    answers and the note leaves the file, this test passes by having nothing to do."""
    monkeypatch.delenv(ds.ACK_ENV, raising=False)
    for role in [r for r in ds.declared_exports() if ds.contamination_note(r)]:
        with pytest.raises(ds.ContaminatedExport):
            ds.refuse_if_contaminated(role)
