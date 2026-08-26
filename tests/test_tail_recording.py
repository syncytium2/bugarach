"""The tail recording is fitted to real recordings, and these pin it to them.

`TAIL_RECORDING` exists because `tools/probe_real_crowding.py` measured a crowded tail
in the export folder that no simulated recording reached. Its settings were chosen
against three statistics of the seven real recordings above 0.38 crowded — crowding
fraction, interval CV and minimum gap — so a change that drifts off any of them has
stopped simulating the thing it was built for.

The bounds below are the real tail's own observed ranges, widened only where a
simulator cannot be expected to land inside a 7-recording sample exactly. They are
deliberately loose: a test that flakes gets deleted rather than fixed.
"""

import numpy as np
import pytest

from bugarach.bench import (BENCH_RECORDING, CROWDED_RECORDING, CROWDING_GAP_SEC,
                            REGIMES, TAIL_RECORDING, make_crowded_recording,
                            make_recording, make_tail_recording,
                            nearest_neighbour_gaps)

SEEDS = range(1, 9)
# the seven export-folder recordings above 0.38 crowded, from probe_real_crowding.py
REAL_TAIL_CV = (0.62, 1.59)
REAL_TAIL_MIN_GAP = (6.0, 26.0)


def _stats(maker):
    crowded, cv, min_gap = [], [], []
    for seed in SEEDS:
        _, gt = maker(seed)
        t = np.sort(np.asarray(gt.times, float))
        d = np.diff(t)
        crowded.append(np.mean(nearest_neighbour_gaps(gt) < CROWDING_GAP_SEC))
        cv.append(d.std(ddof=1) / d.mean())
        min_gap.append(d.min())
    return (float(np.mean(crowded)), float(np.mean(cv)), float(np.mean(min_gap)))


def test_the_bench_cannot_crowd_and_the_tail_can():
    """The premise of the whole exercise, asserted rather than remembered.

    `BENCH_RECORDING` spaces events at 120 s against a ±30 s reference window, so its
    crowding fraction is zero by construction and no experiment run on it can see
    reference-window contamination.
    """
    bench, _, _ = _stats(lambda s: make_recording("baseline_quiet", s))
    crowded, _, _ = _stats(lambda s: make_crowded_recording("baseline_quiet", s))
    tail, _, _ = _stats(lambda s: make_tail_recording("baseline_quiet", s))
    assert bench == 0.0, "the bench planted a crowded event; its floor must have moved"
    assert crowded > bench
    assert tail > crowded, "the tail recording must out-crowd the crowded diagnostic"


def test_the_tail_matches_the_real_tail_on_cv_and_floor():
    """Crowding reached the way real recordings reach it, not by burstiness.

    interval_cv above 1 buys crowding with clumping, and the real tail is not clumpy —
    CV 0.62–1.59, median 0.93. If this ever fails upward, someone has turned the
    burstiness knob and the recording is no longer fitted to anything.
    """
    _, cv, min_gap = _stats(lambda s: make_tail_recording("baseline_quiet", s))
    assert REAL_TAIL_CV[0] <= cv <= REAL_TAIL_CV[1], (
        f"realized interval CV {cv:.2f} is outside the real tail's {REAL_TAIL_CV}")
    assert REAL_TAIL_MIN_GAP[0] <= min_gap <= REAL_TAIL_MIN_GAP[1], (
        f"realized minimum gap {min_gap:.1f}s is outside the real tail's "
        f"{REAL_TAIL_MIN_GAP}")


def test_the_tail_populates_the_bin_the_crowded_recording_cannot():
    """<10 s gaps are the point. `CROWDED_RECORDING`'s 14 s floor forbids them."""
    def below_10(maker):
        n = 0
        for seed in SEEDS:
            _, gt = maker(seed)
            n += int((nearest_neighbour_gaps(gt) < 10.0).sum())
        return n
    assert below_10(lambda s: make_crowded_recording("baseline_quiet", s)) == 0
    assert below_10(lambda s: make_tail_recording("baseline_quiet", s)) > 100


def test_the_tail_stays_on_the_difficulty_axis():
    """Same door `test_the_crowded_recording_stays_on_the_difficulty_axis` closes:
    a missing regime once let `bg_rate_hz` fall through to the simulator's own 0.05,
    off the axis, and two thirds of a recall collapse was that instead."""
    assert "bg_rate_hz" not in TAIL_RECORDING
    with pytest.raises(ValueError):
        make_tail_recording("not_a_regime", 1)
    for regime in REGIMES:
        sl, gt = make_tail_recording(regime, 1)
        assert gt.times.size > 0


def test_the_tail_changes_nothing_that_ships():
    """Additive only. If this fails, a published number moved."""
    assert BENCH_RECORDING["min_sep_sec"] == 120.0
    assert CROWDED_RECORDING["min_sep_sec"] == 14.0
    assert TAIL_RECORDING["min_sep_sec"] == 6.0
    assert TAIL_RECORDING["interval_cv"] == 1.0, "burstiness is not the knob here"
    # inherits the crowded diagnostic's duration, so the two are comparable
    assert TAIL_RECORDING["duration_sec"] == CROWDED_RECORDING["duration_sec"]
