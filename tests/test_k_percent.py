"""K as a percentage, and the MAHICE record that carries the one a person set.

Tony, 2026-09-03: *"K is set by the user during review of the data with MAHICE"*
and *"the human might want different K for a session, but it is not fair to change
K for each slice. We do need K expressed as a percentage."*

Both halves are asserted here, because either alone is the bug. A percentage with
no record of who set it is a number nobody can dispute; a recorded K that is an
absolute count is unfair across a folder whose recordings run 10 to 51 ROIs.

The conversion is the generator's own rule and there is a test that says so — if
the two ever diverge, a spec derived at 10% and a simulation planted at 10% stop
describing the same events, and nothing else would notice.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from bugarach.annotate import (
    MAHICE, SESSION_FILE, MahiceSession, cross_check_k, read_session,
    write_session,
)
from bugarach.assess import (
    DEFAULT_MIN_ROIS, DEFAULT_MIN_ROIS_FRAC, k_from_fraction,
)

from test_annotate import mk


def verdicts(pairs, *, slice_id="s1", annotator="tony"):
    return [mk(slice_id=slice_id, n_members=n, k_survived=n, verdict=v,
               annotator=annotator, centre_sec=100.0 + 10 * i)
            for i, (n, v) in enumerate(pairs)]


def separable(**kw):
    out = []
    for i in range(12):
        out.append((2 + i % 2, "rejected"))
        out.append((6 + i % 3, "confirmed"))
    return verdicts(out, **kw)


def session(**kw):
    base = dict(k_percent=0.20, annotator="tony",
                decided_at="2026-09-03T16:00:00Z",
                k_absolute={"s1": 7}, n_roi={"s1": 34}, proposal_frac=0.05)
    base.update(kw)
    return MahiceSession(**base)


# ---------------------------------------------------------------------------
# the conversion
# ---------------------------------------------------------------------------

def test_it_is_the_generators_own_rule():
    """`simulate.py` plants participation as fractions with
    `max(1, matlab_round(frac * n_roi))`. If K resolves differently, a spec
    derived at 10% and a simulation planted at 10% describe different events and
    nothing in the tree compares the two."""
    from bugarach.detectors._shared import matlab_round

    for frac in (0.05, 0.1, 0.15, 0.33, 0.5, 1.0):
        for n in (1, 7, 10, 12, 34, 51, 405):
            assert k_from_fraction(frac, n) == max(1, matlab_round(frac * n))


def test_the_same_percentage_is_a_different_count_per_recording():
    """The whole point. Both of these recordings are in the approved export."""
    assert k_from_fraction(0.10, 10) == 1
    assert k_from_fraction(0.10, 34) == 3
    assert k_from_fraction(0.10, 51) == 5
    # and across labs, which is why current_export.toml says DO NOT TRANSPLANT
    assert k_from_fraction(0.10, 405) == 41


def test_a_percentage_never_resolves_below_one():
    assert k_from_fraction(0.01, 3) == 1
    assert k_from_fraction(1e-9, 1000) == 1


def test_the_default_percentage_scan_covers_the_default_absolute_one():
    """On the corpus's median field size the two scans should be talking about
    the same region of K, or the percentage scan is not a replacement."""
    got = {k_from_fraction(f, 34) for f in DEFAULT_MIN_ROIS_FRAC}
    assert min(got) <= min(DEFAULT_MIN_ROIS) <= max(got)


# ---------------------------------------------------------------------------
# the assessor
# ---------------------------------------------------------------------------

def _slice(tmp_path: Path, n_roi: int):
    from bugarach.io import load_folder

    d = tmp_path / f"e{n_roi}"
    d.mkdir(parents=True, exist_ok=True)
    rows = ["roi,time_sec,stream"]
    t = 60.0
    while t < 1100.0:                      # a burst every 2 min, all ROIs
        for r in range(n_roi):
            rows.append(f"{r + 1},{t + 0.05 * r:.3f},fast")
        t += 120.0
    for r in range(n_roi):                 # background, out of step
        u = 13.0 + 3.1 * r
        while u < 1100.0:
            rows.append(f"{r + 1},{u:.3f},fast")
            u += 37.0 + r
    (d / "s1.csv").write_text("\n".join(rows) + "\n")
    (d / "slices.csv").write_text("slice_id,frame_interval_sec\ns1,0.1\n")
    return next(iter(load_folder(d)))


def test_the_assessor_resolves_a_fraction_against_this_recording(tmp_path):
    from bugarach.assess import assess_coactivity

    small = assess_coactivity(_slice(tmp_path, 10), window=(0.0, 1100.0),
                              min_rois_frac=(0.30,), n_surrogates=20)
    big = assess_coactivity(_slice(tmp_path, 40), window=(0.0, 1100.0),
                            min_rois_frac=(0.30,), n_surrogates=20)
    assert [a.min_rois for a in small] == [3]
    assert [a.min_rois for a in big] == [12]
    assert small[0].min_rois_frac == big[0].min_rois_frac == 0.30


def test_the_fraction_is_carried_not_recomputed(tmp_path):
    """`min_rois / n_roi` is not the fraction — the rounding is one-way."""
    from bugarach.assess import assess_coactivity

    a, = assess_coactivity(_slice(tmp_path, 12), window=(0.0, 1100.0),
                           min_rois_frac=(0.20,), n_surrogates=20)
    assert a.min_rois_frac == 0.20
    assert a.min_rois == 2
    assert a.min_rois / a.n_roi != pytest.approx(0.20)   # 2/12, not 0.20


def test_two_fractions_landing_on_one_count_are_not_reported_twice(tmp_path):
    """5% and 10% of 12 ROIs are both K=1. Two rows would be one measurement
    reported twice under different labels."""
    from bugarach.assess import assess_coactivity

    out = assess_coactivity(_slice(tmp_path, 12), window=(0.0, 1100.0),
                            min_rois_frac=(0.05, 0.10, 0.20), n_surrogates=20)
    assert [a.min_rois for a in out] == [1, 2]
    assert out[0].min_rois_frac == 0.05          # the coarser label wins


def test_an_absolute_k_still_carries_no_fraction(tmp_path):
    from bugarach.assess import assess_coactivity

    a, = assess_coactivity(_slice(tmp_path, 12), window=(0.0, 1100.0),
                           min_rois=(3,), n_surrogates=20)
    assert a.min_rois_frac is None


def test_asking_both_ways_is_refused(tmp_path):
    from bugarach.assess import assess_coactivity

    with pytest.raises(ValueError, match="two ways of saying K"):
        assess_coactivity(_slice(tmp_path, 12), window=(0.0, 1100.0),
                          min_rois=(3,), min_rois_frac=(0.1,), n_surrogates=20)


def test_a_percentage_out_of_range_is_refused(tmp_path):
    from bugarach.assess import assess_coactivity

    with pytest.raises(ValueError, match="0.10 rather than 10"):
        assess_coactivity(_slice(tmp_path, 12), window=(0.0, 1100.0),
                          min_rois_frac=(10,), n_surrogates=20)


def test_k_of_one_is_computed_without_a_numpy_warning(tmp_path, recwarn):
    """A one-onset cluster has no sample SD. NaN is the answer; ddof=1 dividing
    by zero and warning is not. Only reachable since a percentage can round to 1."""
    from bugarach.assess import assess_coactivity

    a, = assess_coactivity(_slice(tmp_path, 10), window=(0.0, 1100.0),
                           min_rois_frac=(0.05,), n_surrogates=20)
    assert a.min_rois == 1
    assert not [w for w in recwarn if issubclass(w.category, RuntimeWarning)]


# ---------------------------------------------------------------------------
# the MAHICE record
# ---------------------------------------------------------------------------

def test_the_session_round_trips(tmp_path):
    p = write_session(tmp_path, session())
    assert p.name == SESSION_FILE
    back = read_session(tmp_path)
    assert back.k_percent == 0.20
    assert back.annotator == "tony"
    assert back.k_absolute == {"s1": 7}
    assert back.n_roi == {"s1": 34}
    assert json.loads(p.read_text())["mahice"] == MAHICE


def test_a_percentage_given_as_a_whole_number_is_refused():
    """20 is not a fraction, and taking it would set K to the whole field."""
    with pytest.raises(ValueError, match="0.10, not 10"):
        session(k_percent=20)


def test_a_session_with_no_annotator_is_refused():
    """K inherits whoever set it — RESET §1. Anonymous is not disputable."""
    with pytest.raises(ValueError, match="inherits whoever set it"):
        session(annotator="  ")


def test_a_session_with_no_time_is_refused():
    with pytest.raises(ValueError, match="when K was set"):
        session(decided_at="")


def test_k_for_prefers_what_the_review_actually_ran_at():
    s = session(k_percent=0.20, k_absolute={"s1": 7}, n_roi={"s1": 34})
    assert s.k_for("s1") == 7
    # a recording this session never saw resolves, given its population
    assert s.k_for("s2", n_roi=10) == 2
    with pytest.raises(KeyError, match="not in this session"):
        s.k_for("s2")


def test_a_missing_session_says_what_it_is_for(tmp_path):
    with pytest.raises(FileNotFoundError, match="set by a person during MAHICE"):
        read_session(tmp_path)


# ---------------------------------------------------------------------------
# the cross-check — reports, never overrides
# ---------------------------------------------------------------------------

def test_agreement_is_reported_and_changes_nothing():
    """Labels separate at 4; the person set a percentage that came to 4."""
    c = cross_check_k(separable(), session(k_percent=0.12, k_absolute={"s1": 4}))
    assert c.agrees is True and bool(c) is True
    assert c.k_set_median == 4
    assert "agree" in c.message
    assert c.session.k_percent == 0.12          # untouched


def test_disagreement_is_surfaced_and_the_persons_k_still_stands():
    c = cross_check_k(separable(), session(k_percent=0.30, k_absolute={"s1": 10}))
    assert c.agrees is False and bool(c) is False
    assert "NOTHING HAS BEEN CHANGED" in c.message
    assert "10" in c.message and str(c.estimate.k) in c.message
    assert c.session.k_percent == 0.30


def test_labels_that_locate_nothing_are_not_a_disagreement():
    """`agrees` is None, not False. The estimate failing is a statement about
    the labels, and calling it a disagreement would blame the person."""
    c = cross_check_k(verdicts([(6, "confirmed")] * 4), session())
    assert c.agrees is None and bool(c) is True
    assert "Not cross-checked" in c.message


def test_the_message_always_names_who_set_it_and_the_percentage():
    for c in (cross_check_k(separable(), session(k_percent=0.12,
                                                 k_absolute={"s1": 4})),
              cross_check_k(verdicts([(6, "confirmed")] * 4), session())):
        assert "tony" in c.message
        assert "% of ROIs" in c.message
