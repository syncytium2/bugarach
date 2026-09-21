"""What CoactDetect's merge gap is worth on the crowded recordings, and why NaN is not the baseline.

The merge-gap addendum charges every net for what its chosen gap costs on the crowded
recordings. The same quantity had never been measured for the detector they are all
compared against, and its review record names that as the cheapest missing check. These
tests read what the tool committed; the scoring itself needs the fits and branch
``tune-bench-comparison``'s helpers, neither of which is here.

The subtle one is `test_no_merging_is_not_the_baseline_and_the_file_says_why`. "No merging
at all" sounds like one thing and is two. For a sliding detector, disabling merging does
not report a detector without a merge gap -- it reports one call per significant window,
and the windows overlap by construction. Recall barely moves and precision collapses. A
reader who took that row as the baseline would conclude the gap is worth half an F1 point
when it is worth about a hundredth, with the sign the other way.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
RUN = REPO / "docs" / "learned" / "tuned_vs_coact" / "fair_comparison_2026_09_18"
OUT = RUN / "coact_no_merge_crowded.json"
CROWDED = RUN / "crowded_check.json"


@pytest.fixture(scope="module")
def doc():
    return json.loads(OUT.read_text(encoding="utf-8"))


def test_the_measurement_is_committed():
    assert OUT.is_file(), "the run's summary folder carries the measurement beside crowded_check.json"


def test_the_as_run_setting_reproduces_the_number_already_on_record(doc):
    """The same setting, the same recordings, scored by a different tool: it must agree.

    `crowded_check.json` already holds CoactDetect at the run's base setting. If this tool
    disagreed there, its other rows would mean nothing.
    """
    known = json.loads(CROWDED.read_text(encoding="utf-8"))["reference"]["coact"]["crowded_mean_f1"]
    assert doc["crowded_mean_f1"]["as_run"] == pytest.approx(known, abs=1e-12)


def test_the_gap_is_measured_against_the_minimum_decoding_not_against_nan(doc):
    f1 = doc["crowded_mean_f1"]
    worth = doc["merge_gap_worth_on_crowded_recordings"]
    assert worth == pytest.approx(f1["as_run"] - f1["gap_zero"], abs=1e-12), (
        "the headline is as_run minus gap_zero; measuring it against the NaN row would "
        "attribute a decoding artifact to the merge gap"
    )
    assert doc["baseline"].startswith("gap_zero")


def test_no_merging_is_not_the_baseline_and_the_file_says_why(doc):
    """The evidence that the NaN row measures the decoding rather than the gap."""
    per = doc["diagnostic"]["per_setting"]
    assert per["no_merge"]["calls"] > 4 * per["gap_zero"]["calls"], (
        "disabling merging on a sliding detector should emit many times as many calls -- "
        "one per significant window"
    )
    assert per["no_merge"]["recall"] == pytest.approx(per["gap_zero"]["recall"], abs=0.02), (
        "recall is what says the events are still found; if it moved, the NaN row would be "
        "about detection rather than about decoding"
    )
    assert per["no_merge"]["precision"] < 0.5 * per["gap_zero"]["precision"], (
        "the collapse is in precision, which is the signature of duplicate calls"
    )


def test_the_tool_does_not_adjudicate(doc):
    """Signing the 0.02 F1 allowance is Tony's; this file is evidence for that, not a verdict."""
    assert doc["adjudication"] is None
    assert "unsigned" in doc["adjudication_note"]
    text = json.dumps(doc).lower()
    for forbidden in ("would have been refused", "passes on the same terms", "fails the check"):
        assert forbidden not in text, f"the measurement must not decide: found {forbidden!r}"


def test_the_setting_is_the_one_the_run_scored_coactdetect_at(doc):
    """Goal 1's sliding values, not the shipped operating point -- they differ in five parameters."""
    base = doc["setting"]["base"]
    assert base["window_mode"] == "sliding"
    assert base["merge_gap_sec"] == 8.0
    assert doc["setting"]["as_run_merge_gap_sec"] == 8.0


def test_the_docstring_warns_about_the_misleading_field_name():
    """`coact_crowded_no_merge` in the addendum's JSON is not this measurement.

    It holds the shipped operating point, which carries CoactDetect's own 3 s default gap
    because `bench.OPERATING_POINTS` names none -- and differs from the as-run setting in
    four other parameters besides.
    """
    source = (REPO / "tools" / "coact_no_merge_crowded.py").read_text(encoding="utf-8")
    assert "coact_crowded_no_merge" in source
    assert "3 s" in source
