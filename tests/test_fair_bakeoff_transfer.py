"""`--score-spec`: fit on one corpus, score on another, and prove the seam holds.

The transfer question — *does a detector tuned on our preparation work on
another lab's?* — is the first thing a reviewer asks about a learned detector,
and until this landed `fair_bakeoff.run()` could not express it: it built every
recording from ONE spec, so there was no way to put a different corpus in the
held-out fold.

**What the seam has to guarantee, and what these tests check instead of asserting.**

1. *Nothing about the scored corpus reaches the fit.* Checked by consequence
   rather than by inspection: the knob each fold settles on must come out
   **bit-identical** to the home run's, because calibration ran on the same
   recordings in both. If a single scored recording leaked into the grid search
   that equality breaks.
2. *The held-out fold really is the other corpus.* Checked the same way from the
   other side — the planted-event count on the held-out fold must equal what a
   home run **on the scoring spec** plants, not what the fitting spec plants.
3. *The default path did not move.* `score_spec=None` and `score_spec=spec` must
   both reproduce the ordinary bake-off exactly. A transfer switch that perturbs
   the number it is being compared against measures itself.

The two specs here are small and deliberately unalike in the axis that matters —
field size, 12 ROIs against 40. That is the same axis the real experiment turns
on (our median field is ~34 cells, the Cossart corpus's ~566), and it is what
makes an absolute `min_rois` threshold a thing that can fail to travel.

**No real data, no learned models.** The learned half of `run()` reaches the
scoring corpus through the identical `rec_scored` call, and training six
architectures four times over would put minutes into the suite to re-check one
line. `LEARNED` is emptied here; `tests/test_fair_bakeoff_transfer_learned.py`
does not exist and the gap is deliberate — see the module note at the bottom.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


def _load_fair_bakeoff():
    path = REPO / "tools" / "fair_bakeoff.py"
    spec = importlib.util.spec_from_file_location("fair_bakeoff_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


#: Two corpora that differ in the axis a transfer test is about. Short and
#: sparse so the whole file runs in seconds; the shapes are not meant to
#: resemble either real folder.
SPEC_SMALL_FIELD = dict(
    duration_sec=180.0, n_roi=12, bg_rate_hz=0.01,
    participation=(1.0, 0.6), n_per_level=(3, 3),
    jitter_sec=0.05, grid_sec=0.1, min_sep_sec=10.0,
)
SPEC_BIG_FIELD = dict(SPEC_SMALL_FIELD, n_roi=40,
                      participation=(0.30, 0.15), n_per_level=(4, 4))


#: Wall-clock fields. Two runs of the same computation differ in every one of
#: them and in none of the others, so an equality check that includes them is a
#: test of the machine's mood. Stripped before comparing, never before reporting.
_TIMING = ("calibrate_sec", "detect_sec", "detect_x_realtime", "train_sec")


def _findings(res, detector="coact"):
    """A run's result with the wall-clock fields removed."""
    d = dict(res["hand_written"][detector])
    d.pop("calibrate_sec", None)
    d.pop("detect_sec", None)
    d.pop("detect_x_realtime", None)
    d["per_fold"] = [{k: v for k, v in f.items() if k not in _TIMING}
                     for f in d["per_fold"]]
    return d


@pytest.fixture(scope="module")
def fb():
    mod = _load_fair_bakeoff()
    return mod


def _run(fb, monkeypatch, spec, *, score_spec=None, detector="coact"):
    """One `run()` over a single cheap detector and no learned models."""
    import bugarach.bench as bench

    monkeypatch.setattr(bench, "DETECTORS", (detector,), raising=True)
    monkeypatch.setattr(fb, "LEARNED", (), raising=True)
    return fb.run(spec, folds=2, seeds_per_fold=2, quick=True,
                  score_spec=score_spec)


def _knobs(res, detector="coact"):
    return [f["knob_value"] for f in res["hand_written"][detector]["per_fold"]]


def _planted(res, detector="coact"):
    return [f["n_planted"] for f in res["hand_written"][detector]["per_fold"]]


def test_the_two_specs_are_actually_different(fb, monkeypatch):
    """The premise. If these plant the same thing, every test below is vacuous."""
    home = _run(fb, monkeypatch, SPEC_SMALL_FIELD)
    away = _run(fb, monkeypatch, SPEC_BIG_FIELD)
    assert _planted(home) != _planted(away) or _knobs(home) != _knobs(away), (
        "the two fixture specs are indistinguishable through run()'s output; "
        "the transfer tests would pass on a no-op")


def test_score_spec_none_is_the_ordinary_bakeoff(fb, monkeypatch):
    """The default path did not move."""
    a = _run(fb, monkeypatch, SPEC_SMALL_FIELD)
    b = _run(fb, monkeypatch, SPEC_SMALL_FIELD, score_spec=None)
    assert _findings(a) == _findings(b)
    assert a["transfer"] is False and b["transfer"] is False
    assert a["score_spec"] is None


def test_scoring_on_the_same_spec_changes_nothing(fb, monkeypatch):
    """`--score-spec` pointed back at `--spec` is not a second corpus.

    It is the identity case, and it has to be exact: a transfer number is read
    against the home number, so a switch that perturbs the home number by even a
    seed would make the comparison measure itself.
    """
    home = _run(fb, monkeypatch, SPEC_SMALL_FIELD)
    same = _run(fb, monkeypatch, SPEC_SMALL_FIELD,
                score_spec=dict(SPEC_SMALL_FIELD))
    assert same["transfer"] is False, (
        "an identical spec is the same corpus, however it was passed")
    assert _findings(same) == _findings(home)


def test_the_fit_never_sees_the_scored_corpus(fb, monkeypatch):
    """The guarantee, checked by consequence.

    The knob is chosen on the training folds of `--spec`. Under transfer those
    recordings are unchanged, so the chosen knob must come out identical to the
    home run's — every fold, exactly. A leak of even one scored recording into
    the grid search moves it.
    """
    home = _run(fb, monkeypatch, SPEC_SMALL_FIELD)
    xfer = _run(fb, monkeypatch, SPEC_SMALL_FIELD, score_spec=SPEC_BIG_FIELD)
    assert xfer["transfer"] is True
    assert _knobs(xfer) == _knobs(home), (
        "the calibrated knob moved under transfer, which can only happen if a "
        "recording from the scoring corpus reached the grid search")


def test_the_held_out_fold_is_the_other_corpus(fb, monkeypatch):
    """The other side of the same seam.

    Planted-event counts on the held-out fold are a property of the generator
    that made those recordings. Under transfer they must match a home run on the
    SCORING spec, not on the fitting spec.
    """
    home = _run(fb, monkeypatch, SPEC_SMALL_FIELD)
    away = _run(fb, monkeypatch, SPEC_BIG_FIELD)
    xfer = _run(fb, monkeypatch, SPEC_SMALL_FIELD, score_spec=SPEC_BIG_FIELD)
    assert _planted(xfer) == _planted(away), (
        "the held-out fold was not generated from --score-spec")
    assert _planted(xfer) != _planted(home), (
        "the fixture specs plant the same count; this test cannot distinguish "
        "the two corpora and needs a different pair")


def test_the_result_records_both_corpora(fb, monkeypatch):
    """A transfer JSON that does not name what it was scored on is unreadable
    six months later, and indistinguishable from the home result it supersedes."""
    xfer = _run(fb, monkeypatch, SPEC_SMALL_FIELD, score_spec=SPEC_BIG_FIELD)
    assert xfer["spec"] == SPEC_SMALL_FIELD
    assert xfer["score_spec"] == SPEC_BIG_FIELD
    assert xfer["transfer"] is True


def test_the_output_filename_carries_both_corpora(fb, tmp_path, monkeypatch):
    """`main()`'s stem, checked at the level a reader meets it: the file name.

    A transfer result written as `bakeoff.json` is a number about somebody
    else's data wearing the home result's name.
    """
    import json

    import bugarach.bench as bench
    monkeypatch.setattr(bench, "DETECTORS", ("coact",), raising=True)
    monkeypatch.setattr(fb, "LEARNED", (), raising=True)

    ours = tmp_path / "spec_ours.json"
    theirs = tmp_path / "spec_theirs.json"
    ours.write_text(json.dumps({"generator": SPEC_SMALL_FIELD}))
    theirs.write_text(json.dumps({"generator": SPEC_BIG_FIELD}))

    rc = fb.main(["--spec", str(ours), "--score-spec", str(theirs),
                  "--out", str(tmp_path), "--folds", "2",
                  "--seeds-per-fold", "2", "--quick"])
    assert rc == 0
    written = sorted(p.name for p in tmp_path.glob("bakeoff*.json"))
    assert written == ["bakeoff_quick_spec_ours_to_spec_theirs.json"], written
    assert not (tmp_path / "bakeoff_quick.json").exists(), (
        "a transfer run must not land on the home result's file name")


# ---------------------------------------------------------------------------
# WHAT IS NOT COVERED HERE, AND WHY IT IS SAID RATHER THAN SKIPPED
#
# The learned half of `run()` reaches the scoring corpus through the same
# `rec_scored` call these tests exercise, and its fit is separated by the same
# `fold_maker(rec, tr_seeds)` closure — `rec`, never `rec_scored`. Covering it
# here would mean training six architectures across folds for every case above,
# which is minutes of suite time to re-check one call site.
#
# That is a judgement, not a proof. The thing it cannot catch is a future edit
# that routes the learned branch through the wrong cache while the hand-written
# branch stays right, and no test in this repo would see it. If the learned
# transfer numbers are ever published, the run that produces them should be
# checked the same way this file checks the six: fit on A alone, and confirm the
# threshold `pick_threshold` returns is unchanged from the home run.
# ---------------------------------------------------------------------------
