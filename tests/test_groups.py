"""The group workbook loader: resolution, corpus membership, and the animal unit.

Everything here runs on a bare clone. The workbook itself is machine-local behind
an env var (FOUNDATIONS §5), so the tests that need it skip rather than fail — but
the logic that decides *what counts as the corpus* and *what counts as an
independent observation* is pure and is tested unconditionally, because those two
decisions are where a corpus result goes wrong silently.
"""

import os
from pathlib import Path

import pytest

from bugarach import groups as G


# ---- resolution: finding, never guessing -----------------------------------

def test_no_env_means_no_path(monkeypatch):
    monkeypatch.delenv(G.ENV_EXPLICIT, raising=False)
    monkeypatch.delenv(G.ENV_ROOT, raising=False)
    assert G.workbook_path() is None


def test_explicit_env_wins(monkeypatch, tmp_path):
    xl = tmp_path / "indiegroups_db4.xlsx"
    xl.write_bytes(b"")
    other = tmp_path / "other"
    other.mkdir()
    (other / "indiegroups_db4.xlsx").write_bytes(b"")
    monkeypatch.setenv(G.ENV_EXPLICIT, str(xl))
    monkeypatch.setenv(G.ENV_ROOT, str(other))
    assert G.workbook_path() == xl


def test_a_pointed_at_path_that_does_not_exist_is_none(monkeypatch, tmp_path):
    """Refusing beats falling through to a different workbook: the wrong file
    would attach the wrong group to every slice."""
    monkeypatch.setenv(G.ENV_EXPLICIT, str(tmp_path / "absent.xlsx"))
    monkeypatch.delenv(G.ENV_ROOT, raising=False)
    assert G.workbook_path() is None


def test_load_without_a_path_raises_with_an_actionable_message(monkeypatch):
    monkeypatch.delenv(G.ENV_EXPLICIT, raising=False)
    monkeypatch.delenv(G.ENV_ROOT, raising=False)
    with pytest.raises(FileNotFoundError) as e:
        G.load_groups()
    assert G.ENV_EXPLICIT in str(e.value)


# ---- what counts as the corpus ---------------------------------------------

def _meta(**kw):
    base = dict(slice_id="s1", group="DI", mouse=1, excluded=False, study=None,
                treat="TTX", notes="", provisional=False)
    base.update(kw)
    return G.SliceMeta(**base)


def test_a_plain_slice_is_in_the_corpus():
    assert _meta().in_main_corpus is True


def test_excluded_is_out():
    assert _meta(excluded=True).in_main_corpus is False


@pytest.mark.parametrize("study", ["pilot-no-sham", "pilot-cadmium",
                                   "APV+CNQX+GABAZINE", "GABAZINE"])
def test_side_arms_are_out(study):
    """A non-blank `study` names a side arm. These are not the main corpus and a
    result reported as the corpus must not contain them."""
    assert _meta(study=study).in_main_corpus is False


def test_provisional_is_a_caveat_not_an_exclusion():
    """The lab marks a row PROVISIONAL when something is not final. That is a note
    to carry, not grounds to drop the slice — dropping it would quietly change the
    denominator."""
    m = _meta(notes="PROVISIONAL", provisional=True)
    assert m.provisional is True
    assert m.in_main_corpus is True


# ---- the animal is the independent unit ------------------------------------

def test_by_animal_collapses_slices_to_mice():
    meta = {
        "a1": _meta(slice_id="a1", mouse=1, group="DI"),
        "a2": _meta(slice_id="a2", mouse=1, group="DI"),   # same mouse
        "b1": _meta(slice_id="b1", mouse=2, group="DI"),
        "c1": _meta(slice_id="c1", mouse=3, group="ORX"),
    }
    rows = [{"slice_id": "a1", "v": True}, {"slice_id": "a2", "v": False},
            {"slice_id": "b1", "v": False}, {"slice_id": "c1", "v": False}]
    out = G.by_animal(rows, meta, hit=lambda r: r["v"])
    # DI has two ANIMALS (not three slices), one of which shows the effect.
    assert out["DI"]["animals"] == 2
    assert out["DI"]["animals_hit"] == 1
    assert out["DI"]["slices"] == 3
    assert out["DI"]["slice_hits"] == 1
    assert out["ORX"]["animals"] == 1 and out["ORX"]["animals_hit"] == 0


def test_one_positive_slice_carries_its_animal():
    """The documented rule, pinned: ANY slice showing the effect makes the animal
    count. The alternative would let one thin slice veto an animal."""
    meta = {"x": _meta(slice_id="x", mouse=7), "y": _meta(slice_id="y", mouse=7)}
    rows = [{"slice_id": "x", "v": False}, {"slice_id": "y", "v": True}]
    out = G.by_animal(rows, meta, hit=lambda r: r["v"])
    assert out["DI"]["animals"] == 1 and out["DI"]["animals_hit"] == 1


def test_unknown_slices_are_skipped_not_counted():
    """A slice absent from the workbook has no group; counting it anywhere would
    invent a denominator."""
    meta = {"known": _meta(slice_id="known", mouse=1)}
    rows = [{"slice_id": "known", "v": True}, {"slice_id": "ghost", "v": True}]
    out = G.by_animal(rows, meta, hit=lambda r: r["v"])
    assert sum(g["animals"] for g in out.values()) == 1


# ---- the real workbook, when this machine has it ---------------------------

needs_workbook = pytest.mark.skipif(
    G.workbook_path() is None,
    reason="group workbook not on this machine (BUGARACH_GROUPS_XLSX/DATA_ROOT)")


@needs_workbook
def test_the_real_workbook_parses_and_has_the_lab_vocabulary():
    meta = G.load_groups()
    assert len(meta) > 50
    assert {m.group for m in meta.values()} <= {"DI", "MALE", "OVX", "ORX"}
    assert any(m.excluded for m in meta.values())
    assert any(m.study for m in meta.values())


@needs_workbook
def test_timing_is_returned_in_seconds():
    """The sheet records minutes. A unit that changes at a boundary is how a window
    ends up 60x wrong with nothing failing."""
    t = G.load_timing()
    assert t
    durations = [e - s for s, e in t.values()]
    # Baselines are tens of minutes, so hundreds-to-thousands of seconds.
    assert min(durations) > 60.0
    assert max(durations) < 20000.0
