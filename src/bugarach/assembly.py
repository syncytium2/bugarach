"""Do the same cells recur across coordinated events, or is participation fresh?

The assessor answers *how much* coactivity a recording has. This answers *who*
takes part — whether the participants of one coordinated event predict the
participants of the next. The question, and why it gates a whole family of
literature comparisons, is
``docs/todo/2026-08-18-do-real-slices-have-recurring-assemblies.md``.

**The input is membership, not time.** One recording becomes an events x ROI
boolean matrix, built from ``Assessment.members`` — the clusters the assessor
already found, now carrying which ROIs made them up. Onsets, jitter and the
detector play no part past that point, so nothing here inherits an operating
point.

**Two nulls, and neither is sufficient alone.** This is the finding that shaped
the module, measured by ``tools/assembly_power.py`` before any real recording was
touched, and it is the reason there is no single ``assembly_pvalue`` here:

- ``pvalues_margin`` holds event sizes *and* each ROI's own participation total
  fixed (curveball swaps), so it can only answer to *which* cells co-occur, never
  to how busy they are. It is the conservative one — and it **goes blind exactly
  where the signal is purest**: when every event draws from the same group, the
  non-members never fire at all, their column sums are zero, the whole assembly
  has moved into the margins this null conditions on, and power falls back to
  chance. Power is not monotonic in the thing being measured.
- ``pvalues_uniform`` fixes event sizes only and redraws participants uniformly —
  exactly what ``simulate.py`` does today. It is monotonic and passes the
  full-strength control, but it also fires on plain rate heterogeneity, so on its
  own it cannot separate an assembly from a handful of unusually busy cells.

Read them together:

===================  ==========================================================
both reject          structure beyond what per-cell participation rates explain
uniform only         look at the participation counts first — busy cells, or an
                     assembly too sharp for the conservative null to see
neither              no assembly above the strengths the power curve tables
===================  ==========================================================

**Statistics, also two.** Pair-count dispersion, and the leading eigenvalue of
the ROI correlation matrix — the classical assembly instrument. At the geometry
of these recordings the correlation matrix is rank-deficient (fewer events than ROIs), which
is the regime where the Marchenko-Pastur bound stops being available; that is why
both nulls here are permutation nulls rather than analytic ones.

**Baseline windows only** (FOUNDATIONS §9), and group-dependence applies: an
assembly statistic pooled across groups can hide a sign change, so combine within
group and say which.

**There is no exclusion layer here, and that is the contract.**
``docs/export_folder_spec.md``: *"bugarach reads one folder and nothing else: no
data store, no archive, no environment variable, no network, no companion
database."* Which recordings are analysable, and which ROIs are alive, are the
producer's calls, expressed by what the folder contains — a withdrawn recording
is simply absent and a dead ROI is simply not exported.

This module briefly carried ``load_excluded`` and ``load_dead_roi_keep``, reading
a lab workbook and a vendored roster. They were removed on 2026-08-20 and the
reason is worth keeping: the workbook keys exclusions on (date, mouse,
**slice_order**), bugarach had no slice_order, and matching on date alone
**over-excluded a recording the lab had not withdrawn**. The producer's own export
got it right. Re-deriving a producer's selection from a companion source is not a
safety net — it is a second, worse answer.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import exp, lgamma, log

import numpy as np

__all__ = [
    "AssemblyResult", "membership_matrix", "stat_dispersion", "stat_eigen",
    "pvalues_margin", "pvalues_uniform", "assess_assemblies", "fisher",
]


@dataclass(frozen=True)
class AssemblyResult:
    """One recording's answer, at one coactivity floor K."""

    min_rois: int
    n_events: int
    """Co-active clusters the assembly test saw. Two is not a measurement — read
    ``defined`` before reading anything else."""
    n_roi: int
    defined: bool
    """False when there were too few clusters or too few participating ROIs for a
    permutation null to exist. Every p is NaN and the caller reports an exclusion
    rather than a non-significant result — the distinction the whole exercise
    turns on."""

    disp_obs: float = float("nan")
    eig_obs: float = float("nan")

    p_margin_disp: float = float("nan")
    p_margin_eig: float = float("nan")
    p_uniform_disp: float = float("nan")
    p_uniform_eig: float = float("nan")

    n_surrogates: int = 0
    mean_pair_count: float = float("nan")
    """Co-participation observations per ROI pair. Small is expected and is not
    itself evidence of anything — an assembly concentrates counts rather than
    spreading them, which is why these recordings are better powered than this number
    suggests."""

    def verdict(self, alpha: float = 0.05) -> str:
        """The two-null reading, as a word rather than four numbers.

        **Corrected across the two statistics, and it has to be.** Each null is
        tested with both dispersion and the leading eigenvalue, and taking the
        smaller of two p-values is itself a test with a larger size than either.
        Uncorrected, this flagged 2 of 8 generated recordings whose participants
        were drawn uniformly — a quarter of them, from an instrument whose
        individual nulls sit correctly at 0.05. Bonferroni over the two
        statistics keeps each null's verdict at ``alpha``, which is what makes
        "no-assembly" a statement anyone can quote.
        """
        if not self.defined:
            return "undefined"
        a2 = alpha / 2.0
        m = min(self.p_margin_disp, self.p_margin_eig) < a2
        u = min(self.p_uniform_disp, self.p_uniform_eig) < a2
        if m and u:
            return "structure-beyond-rate"
        if u:
            return "uniform-only"
        if m:
            return "margin-only"
        return "no-assembly"


# ---- membership ------------------------------------------------------------

def membership_matrix(members, n_roi: int) -> np.ndarray:
    """``Assessment.members`` as an events x ROI boolean matrix."""
    M = np.zeros((len(members), int(n_roi)), dtype=bool)
    for e, who in enumerate(members):
        for r in who:
            M[e, int(r)] = True
    return M


# ---- statistics ------------------------------------------------------------

def stat_dispersion(M: np.ndarray) -> float:
    """Variance of the pairwise co-participation counts.

    An assembly puts its counts on a few pairs and leaves the rest at zero, which
    is a variance increase whatever the mean count happens to be.
    """
    X = M.astype(np.float64)
    C = X.T @ X
    iu = np.triu_indices(M.shape[1], k=1)
    return float(np.var(C[iu]))


def stat_eigen(M: np.ndarray) -> float:
    """Leading eigenvalue of the ROI correlation matrix.

    ROIs that never vary carry no correlation and are dropped rather than given a
    zero-variance column, which would make the matrix singular for a reason that
    has nothing to do with assemblies.
    """
    X = M.astype(np.float64)
    sd = X.std(axis=0)
    keep = sd > 0
    if int(keep.sum()) < 2:
        return 0.0
    Z = (X[:, keep] - X[:, keep].mean(axis=0)) / sd[keep]
    C = (Z.T @ Z) / max(X.shape[0] - 1, 1)
    return float(np.linalg.eigvalsh(C)[-1])


# ---- the conservative null: both margins fixed -----------------------------

def _to_masks(M: np.ndarray) -> list[int]:
    """Each event as a bitmask over ROIs — a trade is then three integer ops."""
    return [sum(1 << int(j) for j in np.flatnonzero(row)) for row in M]


def _from_masks(masks: list[int], n_roi: int) -> np.ndarray:
    out = np.zeros((len(masks), n_roi), dtype=bool)
    for i, m in enumerate(masks):
        while m:
            b = m & -m
            out[i, b.bit_length() - 1] = True
            m ^= b
    return out


def _trade(rng, masks: list[int], i: int, j: int) -> None:
    """One curveball trade: redistribute the ROIs the two events do not share.

    Both the row sum and every column sum are conserved by construction — the
    swap only moves membership between two events, and only among ROIs that
    exactly one of them has.
    """
    a, b = masks[i], masks[j]
    only_a = a & ~b
    pool = only_a | (b & ~a)
    if pool == 0:
        return
    idx = []
    m = pool
    while m:
        low = m & -m
        idx.append(low.bit_length() - 1)
        m ^= low
    need = bin(only_a).count("1")
    if need == 0 or need == len(idx):
        return
    to_a = 0
    for q in rng.permutation(len(idx))[:need]:
        to_a |= 1 << idx[q]
    masks[i] = (a & b) | to_a
    masks[j] = (a & b) | (pool ^ to_a)


def pvalues_margin(rng, M: np.ndarray, n_surr: int,
                   burn: int = 5) -> tuple[float, float]:
    """Permutation p for both statistics, event sizes and ROI totals both fixed.

    The chain is burned in and then advanced by one sweep between surrogates, so
    successive draws are near-independent without rebuilding it each time.

    **Remember what this cannot see.** A saturated assembly is invisible to it —
    see the module docstring. A non-significant result here is not on its own an
    absence of assemblies.
    """
    n_events, n_roi = M.shape
    obs_d, obs_e = stat_dispersion(M), stat_eigen(M)
    masks = _to_masks(M)
    draws = rng.randint(0, n_events, size=(burn + n_surr) * n_events * 2)
    p = 0
    for _ in range(burn * n_events):
        i, j = int(draws[p]), int(draws[p + 1]); p += 2
        if i != j:
            _trade(rng, masks, i, j)
    ge_d = ge_e = 0
    for _ in range(n_surr):
        for _ in range(n_events):
            i, j = int(draws[p]), int(draws[p + 1]); p += 2
            if i != j:
                _trade(rng, masks, i, j)
        S = _from_masks(masks, n_roi)
        ge_d += stat_dispersion(S) >= obs_d
        ge_e += stat_eigen(S) >= obs_e
    return ((1 + ge_d) / (1 + n_surr), (1 + ge_e) / (1 + n_surr))


# ---- the companion null: uniform participation -----------------------------

def pvalues_uniform(rng, M: np.ndarray, n_surr: int) -> tuple[float, float]:
    """Permutation p against uniform participation — event sizes only.

    This is the generator's own assumption (``rng.choice(nR, size=np_)``), so it
    asks "do these recordings depart from uniform participation" with nothing
    conditioned away. It answers to rate heterogeneity as well as to assemblies,
    which is why it is read beside ``pvalues_margin`` and never alone.
    """
    n_events, n_roi = M.shape
    sizes = M.sum(axis=1)
    obs_d, obs_e = stat_dispersion(M), stat_eigen(M)
    ge_d = ge_e = 0
    for _ in range(n_surr):
        S = np.zeros_like(M)
        for e in range(n_events):
            S[e, rng.choice(n_roi, size=int(sizes[e]), replace=False)] = True
        ge_d += stat_dispersion(S) >= obs_d
        ge_e += stat_eigen(S) >= obs_e
    return ((1 + ge_d) / (1 + n_surr), (1 + ge_e) / (1 + n_surr))


# ---- one recording ---------------------------------------------------------

#: Below this many clusters there is nothing a permutation null can say. Two
#: events share their participants or they do not; there is no distribution.
MIN_EVENTS = 4


def assess_assemblies(assessment, *, n_surrogates: int = 1000,
                      seed: int = 1) -> AssemblyResult:
    """Run both nulls on one ``Assessment``'s observed cluster membership.

    ``seed`` is fixed by default so a rerun on the same recording reproduces —
    a p-value that moves between runs is not quotable. ``RandomState`` rather
    than ``default_rng``, matching the assessor's surrogate loop next door and
    FOUNDATIONS §2 (sapper SAP002 blocks the alternative in this package).
    """
    M = membership_matrix(assessment.members, assessment.n_roi)
    n_events, n_roi = M.shape
    active = int((M.sum(axis=0) > 0).sum())

    if n_events < MIN_EVENTS or active < 2 or not assessment.meets_floor:
        return AssemblyResult(min_rois=assessment.min_rois, n_events=n_events,
                              n_roi=n_roi, defined=False)

    pairs = n_roi * (n_roi - 1) / 2.0
    counts = M.astype(np.float64).T @ M.astype(np.float64)
    mean_pair = float(counts[np.triu_indices(n_roi, k=1)].mean()) if pairs else float("nan")

    rng = np.random.RandomState(seed)
    md, me = pvalues_margin(rng, M, n_surrogates)
    ud, ue = pvalues_uniform(rng, M, n_surrogates)
    return AssemblyResult(
        min_rois=assessment.min_rois, n_events=n_events, n_roi=n_roi,
        defined=True,
        disp_obs=stat_dispersion(M), eig_obs=stat_eigen(M),
        p_margin_disp=md, p_margin_eig=me,
        p_uniform_disp=ud, p_uniform_eig=ue,
        n_surrogates=n_surrogates, mean_pair_count=mean_pair)


def fisher(ps) -> float:
    """Fisher's combination of per-recording p-values, as a p-value.

    Recordings cannot be pooled cell by cell — the ROIs are different cells — so
    a folder-level statement combines per-slice evidence, not per-slice data.
    Combine **within group**: FOUNDATIONS §9 records effects running in opposite
    directions by group, and a pooled number hides a sign change.
    """
    a = np.asarray(ps, dtype=float)
    x = float(-2.0 * np.log(np.clip(a, 1e-12, 1.0)).sum())
    if x <= 0.0:                     # every slice at p = 1; no evidence at all
        return 1.0
    k = len(a)                       # chi-square with 2k df; k integer, so exact
    t = x / 2.0
    s = sum(exp(-t + i * log(t) - lgamma(i + 1)) for i in range(k))
    return float(min(1.0, max(0.0, s)))
