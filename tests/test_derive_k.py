"""K derived from labelled calls, and the four ways it refuses to be.

**The refusals are the substance, again.** A function that turns verdicts into an
integer is easy; the value is entirely in it declining to when the integer would
be an artefact. Each of the four refusals is a different conversation with the
person who annotated, so each is asserted separately and on its message.

The one that matters most is the censoring guard. `docs/RESET.md` §1 caught this
shape once already in the validation test — asking the assessor to recover planted
events is the convention agreeing with itself — and a proposal list censored at
K>=3 makes "K is 3" the same trick.
"""
import math

import pytest

from bugarach.annotate import (
    MAX_PROPOSAL_FLOOR, MIN_JUDGED, MIN_PER_SIDE, KEstimate, derive_k,
)

from test_annotate import mk


def verdicts(pairs, *, annotator="tony"):
    """`pairs` is (n_members, verdict) repeated — the only two fields that fit.

    `k_survived` is set to `n_members` because that is what nesting means: a
    moment with five co-active ROIs is a candidate at every K up to five.
    """
    return [mk(n_members=n, k_survived=n, verdict=v, annotator=annotator,
               centre_sec=100.0 + 10 * i)
            for i, (n, v) in enumerate(pairs)]


def separable(*, floor=2, n=40):
    """Labels a threshold can actually be fitted to: small rejected, large
    confirmed, with the proposal floor low enough to be legal."""
    out = []
    for i in range(n // 2):
        out.append((floor + i % 2, "rejected"))       # 2-3 co-active, rejected
        out.append((6 + i % 3, "confirmed"))          # 6-8 co-active, confirmed
    return verdicts(out)


# ---------------------------------------------------------------------------
# the four refusals
# ---------------------------------------------------------------------------

def test_too_few_labels_is_a_refusal_naming_the_floor():
    est = derive_k(verdicts([(2, "rejected"), (7, "confirmed")] * 4))
    assert not est
    assert est.k is None
    assert str(MIN_JUDGED) in est.why
    assert "annotate more" in est.why.lower()


def test_labels_all_on_one_side_cannot_locate_a_boundary():
    """Every threshold at or below the smallest confirmed count scores alike, so
    the argmax would be reporting the tie-break rule."""
    est = derive_k(verdicts([(6, "confirmed")] * 30))
    assert not est
    assert f"least {MIN_PER_SIDE} on each side" in est.why


def test_a_censored_proposal_list_is_refused_by_name():
    """THE trap. Propose only at K>=3 and "K is 3" is the input coming back."""
    est = derive_k(separable(floor=3))
    assert not est
    assert "censored at 3" in est.why
    assert "assumption returning under a new name" in est.why
    assert f"K={MAX_PROPOSAL_FLOOR}" in est.why


def test_a_count_that_does_not_separate_is_a_finding_about_the_assessor():
    """Confirmed and rejected drawn from the same counts. There is no threshold,
    and the honest output says the assessor is measuring the wrong quantity —
    not a K."""
    # Counts start at the legal proposal floor, so the censoring guard is not
    # what fires — the first draft of this test used 4 and 5 and was answered by
    # the wrong refusal, which is exactly why the four are asserted separately.
    est = derive_k(verdicts([(2, "confirmed"), (2, "rejected"),
                             (3, "confirmed"), (3, "rejected")] * 8))
    assert not est
    assert "not what the expert is judging on" in est.why
    assert "finding about the assessor" in est.why


# ---------------------------------------------------------------------------
# and when it does answer
# ---------------------------------------------------------------------------

def test_separable_labels_give_the_threshold_between_them():
    est = derive_k(separable())
    assert est
    assert est.k == 4, est.curve          # first threshold above every rejected
    assert est.separation == pytest.approx(1.0)
    assert est.n_confirmed == 20 and est.n_rejected == 20
    assert est.proposal_floor == 2


def test_the_scan_comes_back_beside_the_choice():
    """The argmax is one reading of the curve, so the curve travels with it —
    same posture `derive_spec.py` takes about the assessment scan."""
    est = derive_k(separable())
    assert est.curve, "no curve returned"
    assert est.k in est.curve
    assert max(est.curve.values()) == est.separation
    assert min(est.curve) <= est.proposal_floor


def test_unsure_is_in_neither_side_and_is_still_reported():
    """Same rule as `Agreement.judged`: a candidate a person could not judge is
    evidence about the view, not about the candidate."""
    base = separable()
    est = derive_k(base + verdicts([(9, "unsure")] * 5))
    assert est.n_unsure == 5
    assert est.n_confirmed + est.n_rejected == len(base)
    assert est.k == derive_k(base).k


def test_ties_go_to_the_smaller_k():
    """Matches every other argmax in this repo. Two thresholds separating equally
    well is not a reason to claim the stricter one."""
    est = derive_k(separable())
    best = max(est.curve.values())
    assert est.k == min(k for k, j in est.curve.items() if j == best)


def test_a_wide_band_says_so_in_the_sentence():
    """A band wider than two values means these labels do not distinguish those
    thresholds. Reported rather than hidden behind the point estimate."""
    # rejected at 2, confirmed at 9+ — every threshold from 3 to 9 separates
    # perfectly, so the point estimate is arbitrary inside a 7-wide band.
    est = derive_k(verdicts([(2, "rejected"), (9, "confirmed")] * 12))
    assert est
    assert est.band is not None and est.band[1] - est.band[0] > 2
    assert "band is wide" in est.why


def test_who_labelled_travels_with_the_estimate():
    """K inherits whoever labelled — one observer gives one K, and the record has
    to say whose."""
    est = derive_k(separable())
    assert est.annotators == ("tony",)
    two = derive_k(separable()[:20] + separable(n=20)[:20])
    assert isinstance(two, KEstimate)


def test_the_estimate_is_falsy_when_not_identified_and_truthy_when_it_is():
    """So a caller cannot use the object without having looked at whether it
    holds a number — `if est:` is the whole guard."""
    assert not derive_k([])
    assert derive_k(separable())


def test_the_proposal_scan_reaches_below_the_guard():
    """One decision in two files, so it gets one test.

    `assess.PROPOSAL_MIN_ROIS` is what the machine offers a person;
    `annotate.MAX_PROPOSAL_FLOOR` is what the estimate will accept. If the scan
    ever stops above the guard, every annotation pass produced by this repo is
    refused by its own K estimator — and the failure is silent until someone has
    already spent an afternoon labelling.
    """
    from bugarach.assess import DEFAULT_MIN_ROIS, PROPOSAL_MIN_ROIS

    assert min(PROPOSAL_MIN_ROIS) <= MAX_PROPOSAL_FLOOR, (
        f"the proposal scan starts at {min(PROPOSAL_MIN_ROIS)} but derive_k "
        f"refuses anything above {MAX_PROPOSAL_FLOOR}")
    # and the published scan is untouched, because every assessment number in
    # docs/learned was produced at its floors
    assert DEFAULT_MIN_ROIS == (3, 4, 6, 8)
    assert set(DEFAULT_MIN_ROIS) <= set(PROPOSAL_MIN_ROIS), (
        "the annotation scan must be a superset, so one pass answers both")


def test_the_scan_the_default_offers_would_be_refused():
    """The reason `--for-annotation` had to exist, asserted rather than argued:
    labels drawn from the default scan cannot locate K."""
    from bugarach.assess import DEFAULT_MIN_ROIS

    est = derive_k(separable(floor=min(DEFAULT_MIN_ROIS)))
    assert not est
    assert "censored" in est.why


def test_nothing_at_all_is_a_refusal_rather_than_a_crash():
    est = derive_k([])
    assert not est
    assert est.k is None
    assert est.proposal_floor is None
    assert math.isnan(est.separation)
    assert math.isnan(est.confirmed_median)
