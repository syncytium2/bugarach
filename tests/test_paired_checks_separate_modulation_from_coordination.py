"""The paired checks can tell a scorer that learned slow co-modulation from one that learned
coordination, which the checks before 2026-09-17 could not.

A murderboard reviewer ran a scorer with no notion of events (the share of ROIs active, averaged
over 10 s) through the label-free run's paired checks on a recording whose only structure was a
slow rate change shared by every ROI. Every check passed: real beat its rigid shift, beat a thinned
copy, and read chance against the shared offset and the stationary twin. So "the checks pass" could
not distinguish a detector of coordinated events from a detector of slow modulation.

These tests pin the control that can: rigid shift at a small displacement. Slow modulation survives
a 1.6 s shift; a sub-second event does not. Two scorers with known answers, run through the tool's
own pairing code (``crop_pairs``, ``rigid_frames``, ``paired_summary``, ``modulated``), must come
out on opposite sides of it.
"""

import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

import tube_self_supervised as ts  # noqa: E402

DT = 0.1
L = 12_000
N_ROI = 32
N_REC = 12


def _smooth(v, k):
    return np.convolve(v, np.ones(k) / k, mode="same")


def slow_modulation_score(x):
    """Knows only co-modulation: share of ROIs active, averaged over 10 s; mean of its top 1 %."""
    s = _smooth(x.mean(axis=0), 101)
    k = max(1, int(ts.TOPK_FRAC * s.size))
    return float(np.sort(s)[-k:].mean())


def coincidence_score(x):
    """Knows only sub-second coincidence: share of ROIs active within ±2 frames, minus its 30 s
    moving mean; mean of its top 1 %."""
    lit = np.zeros_like(x)
    for d in range(-2, 3):
        lit = np.maximum(lit, np.roll(x, d, axis=1))
    share = lit.mean(axis=0)
    s = share - _smooth(share, 301)
    k = max(1, int(ts.TOPK_FRAC * s.size))
    return float(np.sort(s)[-k:].mean())


def _poisson_trains(rng, rate_per_frame):
    return [np.flatnonzero(rng.random_sample(L) < rate_per_frame) for _ in range(N_ROI)]


def _modulated_recording(seed):
    """No events: every ROI's rate follows one slow shared modulation."""
    rng = np.random.RandomState(seed)
    return ts.modulated(_poisson_trains(rng, 0.02), L, DT, rng, shared=True)


def _coordinated_recording(seed):
    """Stationary background plus events: 12 of 32 ROIs within ±1 frame, every ~20 s."""
    rng = np.random.RandomState(seed)
    trains = [list(t) for t in _poisson_trains(rng, 0.003)]
    for c in range(300, L - 300, 200):
        for r in rng.choice(N_ROI, 12, replace=False):
            trains[r].append(c + rng.randint(-1, 2))
    return [np.unique(np.asarray(t, np.int64)) for t in trains]


def _share_real_higher(make, score, J_sec):
    pairs = []
    for seed in range(N_REC):
        trains = make(seed)
        rng = np.random.RandomState(1000 + seed)
        Jf = J_sec / DT
        big_margin = int(np.ceil(20.0 / DT)) + 1
        starts = list(range(big_margin, L - big_margin - ts.CROP + 1, ts.CROP // 2))
        real = ts.raster_of(trains, L)
        sur = ts.raster_of(ts.rigid_frames(trains, L, Jf, rng), L)
        pairs += ts.crop_pairs(score, real, sur, starts)
    return ts.paired_summary(pairs)["share_real_higher"]


def test_a_modulation_scorer_passes_the_old_check_and_reads_chance_on_the_new_one():
    big = _share_real_higher(_modulated_recording, slow_modulation_score, 20.0)
    small = _share_real_higher(_modulated_recording, slow_modulation_score, ts.J_SMALL_SEC)
    # The failure the reviewer found: the 20 s check "passes" for a scorer with no events.
    assert big > 0.75, big
    # The control that can fail: at 1.6 s the modulation is still there.
    assert 0.3 < small < 0.7, small


def test_a_coincidence_scorer_separates_on_the_new_check():
    small = _share_real_higher(_coordinated_recording, coincidence_score, ts.J_SMALL_SEC)
    assert small > 0.85, small


def test_the_modulation_twins_are_what_they_claim():
    """The shared twin co-modulates; the independent one does not. Measured as the correlation
    of two halves of the ROIs' 10 s-smoothed activity."""
    rng = np.random.RandomState(7)
    base = _poisson_trains(rng, 0.02)

    def half_corr(trains):
        x = ts.raster_of(trains, L)
        a, b = _smooth(x[:N_ROI // 2].mean(0), 101), _smooth(x[N_ROI // 2:].mean(0), 101)
        return float(np.corrcoef(a, b)[0, 1])

    shared = half_corr(ts.modulated(base, L, DT, np.random.RandomState(1), shared=True))
    independent = half_corr(ts.modulated(base, L, DT, np.random.RandomState(1), shared=False))
    assert shared > 0.5, shared
    assert abs(independent) < 0.25, independent
