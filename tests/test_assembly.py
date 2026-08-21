"""The assembly measurement: membership capture, both nulls, and the verdict.

The power analysis (`tools/assembly_power.py`, `tests/test_assembly_power.py`)
establishes what the statistics can see at this corpus's geometry. This pins the
path from a real recording to an answer: that the assessor now carries which ROIs
made up each cluster, that the membership matrix is faithful to it, and that the
two nulls behave on data whose truth is known — including the case where the
conservative one is known to be blind.
"""

import numpy as np
import pytest

from bugarach import assembly as A
from bugarach.assess import assess_coactivity
from bugarach.simulate import simulate_coordination


def _sim(seed=3, **kw):
    """A generated recording. Its participants are drawn uniformly by
    construction, which makes it the null hypothesis with a known answer."""
    p = dict(n_roi=24, duration_sec=1200.0, bg_rate_hz=0.004,
             participation=(0.25,), n_per_level=(14,), jitter_sec=0.3,
             min_sep_sec=40.0, spacing="uniform", seed=seed)
    p.update(kw)
    return simulate_coordination(**p)[0]


# ---- membership capture ----------------------------------------------------

def test_the_assessor_now_records_who_took_part():
    s = _sim()
    a = assess_coactivity(s, stream="events", n_surrogates=20)[0]
    assert a.n_clusters_obs > 0, "no clusters to check membership on"
    assert len(a.members) == a.n_clusters_obs, \
        "one membership tuple per observed cluster"
    for who in a.members:
        assert len(who) >= a.min_rois, "a cluster below the floor was kept"
        assert len(set(who)) == len(who), "an ROI counted twice in one cluster"
        assert all(0 <= r < a.n_roi for r in who)


def test_membership_sizes_agree_with_the_participant_count():
    """`part_n_obs` is the median participant count the assessor already
    reported. Membership must reproduce it, or the two disagree about the same
    clusters."""
    s = _sim()
    a = assess_coactivity(s, stream="events", n_surrogates=20)[0]
    sizes = [len(w) for w in a.members]
    assert float(np.median(sizes)) == pytest.approx(a.part_n_obs)


def test_membership_matrix_is_faithful():
    M = A.membership_matrix(((0, 2), (1, 2, 3)), n_roi=5)
    assert M.shape == (2, 5)
    assert M[0].tolist() == [True, False, True, False, False]
    assert M[1].tolist() == [False, True, True, True, False]
    assert M.sum() == 5


# ---- the nulls, on data whose truth is known -------------------------------

def _planted(rng, n_roi, n_events, size, strength, assembly):
    M = np.zeros((n_events, n_roi), dtype=bool)
    for e in range(n_events):
        if rng.random_sample() < strength:
            take = min(size, assembly)
            pick = rng.choice(assembly, size=take, replace=False)
            if take < size:
                pick = np.concatenate(
                    [pick, rng.choice(np.arange(assembly, n_roi),
                                      size=size - take, replace=False)])
        else:
            pick = rng.choice(n_roi, size=size, replace=False)
        M[e, pick] = True
    return M


def test_both_nulls_are_the_right_size_on_uniform_participation():
    """Uniform participation is the null hypothesis. Rejecting it at much more
    than alpha would make every later negative result meaningless."""
    rng = np.random.RandomState(4)
    hits_m = hits_u = 0
    for _ in range(40):
        M = _planted(rng, 24, 18, 5, 0.0, 6)
        hits_m += A.pvalues_margin(rng, M, 100)[0] < 0.05
        hits_u += A.pvalues_uniform(rng, M, 100)[0] < 0.05
    assert hits_m / 40 < 0.20
    assert hits_u / 40 < 0.20


def test_both_nulls_find_a_mid_strength_assembly():
    rng = np.random.RandomState(6)
    m = u = 0
    for _ in range(20):
        M = _planted(rng, 24, 18, 5, 0.5, 5)
        m += A.pvalues_margin(rng, M, 100)[0] < 0.05
        u += A.pvalues_uniform(rng, M, 100)[0] < 0.05
    assert m / 20 > 0.6
    assert u / 20 > 0.6


def test_the_conservative_null_is_blind_to_a_saturated_assembly():
    """The reason this module has two nulls and no single `assembly_pvalue`.

    At full strength the non-members never participate, so the assembly lives
    entirely in the column sums `pvalues_margin` holds fixed. If this ever starts
    passing, the module docstring is wrong and the two-null reading needs redoing.
    """
    rng = np.random.RandomState(6)
    m = u = 0
    for _ in range(20):
        M = _planted(rng, 24, 18, 5, 1.0, 6)
        m += A.pvalues_margin(rng, M, 100)[0] < 0.05
        u += A.pvalues_uniform(rng, M, 100)[0] < 0.05
    assert m / 20 < 0.3, "the conservative null now sees a saturated assembly"
    assert u / 20 > 0.8, "the companion null must still pass the control"


# ---- one recording, end to end ---------------------------------------------

def test_a_generated_recording_shows_no_assembly():
    """The generator draws participants with `rng.choice`, so a recording it
    produced has coordinated events and no recurring group. Reporting one would
    mean the instrument invents structure."""
    s = _sim()
    a = assess_coactivity(s, stream="events", n_surrogates=20)[0]
    r = A.assess_assemblies(a, n_surrogates=200)
    if not r.defined:
        pytest.skip(f"only {r.n_events} clusters — no null exists")
    assert r.verdict() in ("no-assembly", "margin-only"), (
        f"verdict {r.verdict()} on uniformly drawn participation "
        f"(margin {r.p_margin_disp:.3f}/{r.p_margin_eig:.3f}, "
        f"uniform {r.p_uniform_disp:.3f}/{r.p_uniform_eig:.3f})")


def test_too_few_clusters_is_undefined_not_negative():
    """The distinction the whole exercise turns on: 'we could not look' must not
    be reportable as 'we looked and found nothing'."""
    class Stub:
        min_rois, n_roi, meets_floor = 3, 20, True
        members = ((0, 1, 2), (3, 4, 5))
    r = A.assess_assemblies(Stub(), n_surrogates=50)
    assert r.defined is False
    assert r.verdict() == "undefined"
    assert np.isnan(r.p_margin_disp) and np.isnan(r.p_uniform_disp)


def test_a_failed_floor_is_undefined():
    class Stub:
        min_rois, n_roi, meets_floor = 3, 20, False
        members = tuple((0, 1, 2) for _ in range(10))
    assert A.assess_assemblies(Stub(), n_surrogates=50).defined is False


def test_the_result_reproduces():
    """A p-value that moves between runs is not quotable."""
    s = _sim()
    a = assess_coactivity(s, stream="events", n_surrogates=20)[0]
    r1 = A.assess_assemblies(a, n_surrogates=100)
    r2 = A.assess_assemblies(a, n_surrogates=100)
    assert (r1.p_margin_disp, r1.p_uniform_disp) == (r2.p_margin_disp, r2.p_uniform_disp)


def test_fisher_combines_within_group():
    assert A.fisher([1.0, 1.0, 1.0]) == pytest.approx(1.0)
    assert A.fisher([1e-4, 1e-4, 1e-4]) < 1e-6
    assert 0.0 < A.fisher([0.2, 0.3, 0.9]) <= 1.0


def test_the_verdict_itself_has_the_right_false_positive_rate():
    """The nulls being correct at alpha does NOT make the verdict correct.

    `verdict` takes the smaller of two p-values per null, and the minimum of two
    tests is a third test with a larger size. Uncorrected, this called 2 of 8
    uniformly drawn recordings an assembly. What is pinned here is the rate the
    verdict actually delivers, on data with no assembly in it — because
    "no-assembly" is the answer this whole exercise exists to be able to publish,
    and it is worthless if it is wrong one time in four.
    """
    rng = np.random.RandomState(21)
    flagged = 0
    n = 60
    for _ in range(n):
        M = _planted(rng, 24, 16, 5, 0.0, 6)
        md, me = A.pvalues_margin(rng, M, 200)
        ud, ue = A.pvalues_uniform(rng, M, 200)
        r = A.AssemblyResult(
            min_rois=3, n_events=16, n_roi=24, defined=True,
            p_margin_disp=md, p_margin_eig=me,
            p_uniform_disp=ud, p_uniform_eig=ue)
        flagged += r.verdict() != "no-assembly"
    assert flagged / n < 0.20, (
        f"verdict flagged {flagged}/{n} recordings with uniform participation")


# ---- the archive path ------------------------------------------------------

def test_assess_store_carries_the_assembly_answer(tmp_path, monkeypatch):
    """`--assemblies` plumbing, end to end without a real store.

    The measurement itself is validated above and by the power curve; what is
    pinned here is that a run over an archive actually emits a verdict per slice,
    so the answer cannot be computed and then dropped on the floor between the
    assessor and the report.
    """
    import sys
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent / "tools"))
    import assess_archive
    from bugarach import store as bstore

    s = _sim(seed=11)
    region = bstore.Region(name="baseline", slot=None, start_sec=0.0, end_sec=1200.0)
    s.regions = (region,)

    monkeypatch.setattr(bstore, "load_slice", lambda p: s)
    (tmp_path / "one.mat").write_bytes(b"")

    res = assess_archive.assess_store(
        tmp_path, stream="events", n_surrogates=20,
        assemblies=True, assembly_surrogates=100)

    assert res["rows"], "no rows produced"
    for r in res["rows"]:
        assert "asm_verdict" in r, "assembly answer missing from the row"
        assert "asm_defined" in r
        if r["asm_defined"]:
            assert 0.0 < r["asm_p_uniform_disp"] <= 1.0


def test_assess_store_omits_the_assembly_answer_by_default(tmp_path, monkeypatch):
    """Off by default: it roughly doubles the run, and a caller that did not ask
    for it must not silently pay for it."""
    import sys
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent / "tools"))
    import assess_archive
    from bugarach import store as bstore

    s = _sim(seed=11)
    region = bstore.Region(name="baseline", slot=None, start_sec=0.0, end_sec=1200.0)
    s.regions = (region,)
    monkeypatch.setattr(bstore, "load_slice", lambda p: s)
    (tmp_path / "one.mat").write_bytes(b"")

    res = assess_archive.assess_store(tmp_path, stream="events", n_surrogates=20)
    assert res["rows"]
    assert "asm_verdict" not in res["rows"][0]


# ---- the exclusion layer that must NOT come back ----------------------------
#
# This module briefly grew `load_excluded` and `load_dead_roi_keep`, reading a lab
# workbook and a vendored ROI roster so the analysis could apply the producer's
# selection itself. Both were removed on 2026-08-20, and this test is here so the
# reason survives the deletion rather than being rediscovered.
#
# The export contract says bugarach reads one folder and *nothing else* — no store,
# no companion database. The producer expresses selection by what it exports. When
# this repo re-derived it instead, the workbook keyed exclusions on
# (date, mouse, slice_order), bugarach had no slice_order, date-matching dropped a
# recording the lab had NOT withdrawn, and the producer's own export was correct.
# A second opinion computed from less information is not a safety net.

def test_no_exclusion_or_roster_loader_exists():
    """The contract-violating loaders must stay gone.

    Re-adding one is not a small convenience: it puts a second, worse answer about
    which recordings count next to the producer's own, and the two will disagree.
    """
    import bugarach.assembly as A
    for gone in ("load_excluded", "load_dead_roi_keep"):
        assert not hasattr(A, gone), (
            f"{gone} is back — see docs/export_folder_spec.md: the folder is the "
            f"whole input, and selection is the producer's call")


def test_pairing_takes_no_exclusion_argument():
    """`rows_at` must not grow an exclude parameter again."""
    import importlib.util
    import inspect
    from pathlib import Path
    spec = importlib.util.spec_from_file_location(
        "apc", Path(__file__).parent.parent / "tools" / "assembly_pensub_compare.py")
    apc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(apc)
    params = inspect.signature(apc.rows_at).parameters
    assert "exclude" not in params, params
