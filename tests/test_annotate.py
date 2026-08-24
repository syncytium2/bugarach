"""The annotation record: what it refuses, and what it can be read for.

The refusals are the substance here. A verdict is only worth having if it can be
reproduced and disputed, and the two ways this file stops that being untrue are a
missing view and a silently-empty file.
"""
import csv

import numpy as np
import pytest

from bugarach.annotate import (
    Agreement, Verdict, ViewNotRecorded, agreement_by_k, confirmed_at,
    draw_sample, read_annotations, write_annotations,
)


def mk(**kw):
    base = dict(
        slice_id="s1", stream="fast", centre_sec=120.5, k_survived=4,
        n_members=5, members=(1, 4, 7, 9, 11), verdict="confirmed",
        annotator="tony", decided_at="2026-08-24T14:02:11Z",
        view_t0_sec=100.0, view_t1_sec=140.0, view_roi_order="file",
        view_stream="fast", assess_bin_sec=1.0, assess_surrogates=1000,
        assess_seed=20260722)
    base.update(kw)
    return Verdict(**base)


# ---------------------------------------------------------------------------
# what it refuses
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("missing", ["view_t0_sec", "view_t1_sec",
                                     "view_roi_order", "view_stream"])
def test_a_verdict_without_its_view_is_refused(missing):
    """RESET section 1: a judgement is a property of (recording x rendering x
    observer). Dropping the rendering leaves a number nobody can reproduce."""
    with pytest.raises(ViewNotRecorded, match=missing):
        mk(**{missing: None if missing.endswith("sec") else ""})


def test_a_non_finite_view_bound_is_refused_too():
    """`view_t0_sec = nan` passes a presence check and fails the purpose of one."""
    with pytest.raises(ViewNotRecorded, match="finite"):
        mk(view_t0_sec=float("nan"))


def test_an_unknown_verdict_is_refused():
    with pytest.raises(ValueError, match="verdict must be"):
        mk(verdict="maybe")


def test_writing_nothing_is_refused_rather_than_writing_a_header(tmp_path):
    """An empty file cannot be told apart from a session where a person rejected
    everything — which is a finding, not an absence."""
    with pytest.raises(ValueError, match="rejected everything"):
        write_annotations(tmp_path / "annotations.csv", [])
    assert not (tmp_path / "annotations.csv").exists()


def test_a_hand_edited_file_is_re_validated_on_read(tmp_path):
    """The writer's guarantees are worth nothing if the reader does not re-check
    them: a file edited into a state the writer would have refused is exactly
    what a later analysis must not consume."""
    p = tmp_path / "annotations.csv"
    write_annotations(p, [mk()])
    rows = list(csv.DictReader(open(p, encoding="utf-8")))
    rows[0]["view_t0_sec"] = "NA"
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with pytest.raises(ValueError, match="line 2"):
        read_annotations(p)


# ---------------------------------------------------------------------------
# the round trip
# ---------------------------------------------------------------------------

def test_a_verdict_survives_the_round_trip(tmp_path):
    p = tmp_path / "annotations.csv"
    write_annotations(p, [mk(), mk(centre_sec=300.0, verdict="rejected")])
    back = read_annotations(p)
    assert [v.verdict for v in back] == ["confirmed", "rejected"]
    assert back[0].members == (1, 4, 7, 9, 11)
    assert back[0].view_t0_sec == 100.0
    assert back[0].assess_seed == 20260722


# ---------------------------------------------------------------------------
# what it can be read for
# ---------------------------------------------------------------------------

def test_one_verdict_answers_every_k_at_or_below_the_one_it_survived():
    """Candidates nest: a moment with 8 co-active ROIs also has 3. That is what
    lets a person judge one list and read a whole scan off it."""
    got = agreement_by_k([mk(k_survived=8, verdict="confirmed")])
    assert got[3].confirmed == 1
    assert got[4].confirmed == 1
    assert got[6].confirmed == 1
    assert got[8].confirmed == 1


def test_a_candidate_does_not_count_at_a_k_it_never_reached():
    got = agreement_by_k([mk(k_survived=3, verdict="confirmed")])
    assert got[3].confirmed == 1
    assert got[8].confirmed == 0
    assert got[8].judged == 0


def test_unsure_is_kept_out_of_both_sides_of_the_rate():
    """A candidate a person could not judge is evidence about the view, not
    about the candidate. Counting it as a rejection would make an unreadable
    rendering look like disagreement with the assessor."""
    a = agreement_by_k([mk(verdict="confirmed"), mk(verdict="rejected"),
                        mk(verdict="unsure")])[3]
    assert (a.confirmed, a.rejected, a.unsure) == (1, 1, 1)
    assert a.judged == 2
    assert a.rate == 0.5


def test_no_judgements_gives_nan_not_zero():
    """No agreement measured is not agreement of zero. A spec quoting 0% where
    nobody looked would be stating a claim nobody made."""
    a = Agreement(3, 0, 0, 0)
    assert a.judged == 0
    assert np.isnan(a.rate)


def test_the_scan_is_what_makes_k_readable_off_a_sample():
    """The whole point of the design: a person judges one list, and the table
    they get back says what each K would have bought them.

    Here the tight candidates are believed and the loose ones are not, which is
    the shape that tells an analyst to take a higher K.
    """
    verdicts = ([mk(k_survived=3, verdict="rejected") for _ in range(6)]
                + [mk(k_survived=4, verdict="confirmed") for _ in range(3)]
                + [mk(k_survived=8, verdict="confirmed") for _ in range(2)])
    scan = agreement_by_k(verdicts)
    assert scan[3].judged == 11 and scan[3].confirmed == 5
    assert round(scan[3].rate, 2) == 0.45
    assert scan[4].judged == 5 and scan[4].rate == 1.0
    assert scan[8].judged == 2 and scan[8].rate == 1.0


def test_confirmed_at_is_what_a_spec_should_be_built_from():
    verdicts = [mk(k_survived=8, verdict="confirmed"),
                mk(k_survived=3, verdict="confirmed"),
                mk(k_survived=8, verdict="rejected")]
    assert len(confirmed_at(verdicts, 3)) == 2
    assert len(confirmed_at(verdicts, 6)) == 1
    assert confirmed_at(verdicts, 6)[0].k_survived == 8


# ---------------------------------------------------------------------------
# the draw
# ---------------------------------------------------------------------------

def _folder(counts):
    """One (slice_id, stream, index) per candidate, `counts` per recording."""
    return [(f"s{r}", "fast", i)
            for r, n in enumerate(counts) for i in range(n)]


def test_one_busy_recording_cannot_eat_the_sample():
    """The measured folder has a recording with 200 candidates where the median
    is 8. Uncapped, a person spends the session on that one slice and the
    agreement rate is a statement about it rather than about the folder."""
    s = draw_sample(_folder([200] + [4] * 20), seed=1, budget=60,
                    per_recording_cap=8)
    from collections import Counter
    per = Counter(sid for sid, _, _ in s.picked)
    assert max(per.values()) <= 8
    assert per["s0"] <= 8
    assert s.recordings_drawn > 1


def test_the_draw_is_reproducible_and_the_seed_is_in_the_record():
    a = draw_sample(_folder([9] * 12), seed=7, budget=30)
    b = draw_sample(_folder([9] * 12), seed=7, budget=30)
    c = draw_sample(_folder([9] * 12), seed=8, budget=30)
    assert a.picked == b.picked
    assert a.picked != c.picked
    assert a.seed == 7


def test_coverage_is_reported_because_a_rate_needs_its_denominator():
    """60 of 3,567 and 60 of 60 are different claims, and a spec quoting the
    agreement rate has to be able to say which it is."""
    s = draw_sample(_folder([50] * 20), seed=3, budget=60, per_recording_cap=8)
    assert s.population == 1000
    assert len(s.picked) == 60
    assert round(s.coverage, 3) == 0.06
    assert s.recordings_available == 20


def test_a_folder_smaller_than_the_budget_is_drawn_whole():
    s = draw_sample(_folder([2, 3]), seed=1, budget=60)
    assert len(s.picked) == 5
    assert s.coverage == 1.0


def test_recordings_with_no_candidates_are_simply_absent():
    """18 of 84 recordings have no candidates at K=3. They are not a special
    case and not an error — there is nothing to draw from them."""
    s = draw_sample(_folder([0, 5, 0, 5]), seed=1, budget=60)
    assert {sid for sid, _, _ in s.picked} == {"s1", "s3"}
    assert s.recordings_available == 2


def test_a_nonsense_budget_is_refused():
    with pytest.raises(ValueError, match="positive"):
        draw_sample(_folder([5]), seed=1, budget=0)
