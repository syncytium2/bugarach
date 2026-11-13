"""A rate-matched negative keeps each channel's train and the slow shared part, and nothing fast.

``bugarach.negatives`` (the decoy record,
``docs/adr/0019-the-decoys-are-retired-negatives-are-rate-matched.md``: "We'll add rate matched
negatives to our toolset"). Every recording here is made in the test from a seed; no data.

The two claims that make it a negative are tested on recordings where the answer is known:

* planted coordinated events stop being co-active after the shift;
* a change in rate that every channel shares over minutes is still there after it, and is gone
  under a control that scatters each channel's onsets evenly over the recording.
"""
from __future__ import annotations

import numpy as np
import pytest

from bugarach import negatives as ng
from bugarach.event_floor import J_SEC

DURATION = 2700.0          # seconds: 45 minutes
N_CHANNELS = 30


def _background(rng, rate_hz: float) -> list[np.ndarray]:
    return [np.sort(rng.uniform(0, DURATION, rng.poisson(rate_hz * DURATION)))
            for _ in range(N_CHANNELS)]


def _with_events(seed: int, n_events: int = 40, participants: int = 10,
                 jitter_sec: float = 0.1) -> list[np.ndarray]:
    """Independent background at 0.01 Hz per channel, plus events of 10 channels 60 s apart."""
    rng = np.random.RandomState(seed)
    trains = _background(rng, 0.01)
    for e in range(n_events):
        centre = 100.0 + 60.0 * e
        for c in rng.choice(N_CHANNELS, participants, replace=False):
            trains[c] = np.sort(np.append(trains[c], centre + rng.randn() * jitter_sec))
    return trains


def _shared_slow(seed: int, tau_sec: float = 120.0, sigma: float = 0.8) -> list[np.ndarray]:
    """No coordination: every channel's rate follows one slow multiplier, onsets independent."""
    rng = np.random.RandomState(seed)
    dt = 1.0
    n = int(DURATION / dt)
    a = np.exp(-dt / tau_sec)
    z = np.empty(n)
    z[0] = rng.randn()
    e = rng.randn(n) * np.sqrt(1 - a * a)
    for i in range(1, n):
        z[i] = a * z[i - 1] + e[i]
    m = np.exp(sigma * z)
    m /= m.mean()
    trains = []
    for _ in range(N_CHANNELS):
        counts = rng.poisson(0.03 * dt * m)
        trains.append(np.sort(np.repeat(np.arange(n) * dt, counts) + rng.uniform(0, dt, counts.sum())))
    return trains


def _windows_with_at_least(times, k: int, window_sec: float, lo: float, hi: float) -> int:
    """How many ``window_sec`` bins between ``lo`` and ``hi`` hold onsets of ``k`` or more channels."""
    edges = np.arange(lo, hi + 1e-9, window_sec)
    active = np.zeros(len(edges) - 1, dtype=int)
    for t in times:
        active += np.histogram(t, edges)[0] > 0
    return int((active >= k).sum())


def _count_variance_ratio(times, bin_sec: float, lo: float, hi: float) -> float:
    """Variance over mean of the population's onset count per bin: 1 for independent channels at
    steady rates, above 1 when the channels' rates rise and fall together."""
    edges = np.arange(lo, hi + 1e-9, bin_sec)
    total = np.zeros(len(edges) - 1)
    for t in times:
        total += np.histogram(t, edges)[0]
    return float(total.var() / total.mean())


def test_each_channel_keeps_its_own_train():
    trains = _with_events(1)
    neg = ng.rate_matched_negative(trains, DURATION, seed=7)
    assert len(neg.times) == N_CHANNELS and neg.j_sec == J_SEC
    lo, hi = neg.valid_window
    assert (lo, hi) == (J_SEC, DURATION - J_SEC)
    lost = 0
    for a, b, u in zip(trains, neg.times, neg.offsets_sec):
        assert abs(u) <= J_SEC
        moved = np.sort(a + u)
        kept = moved[(moved >= 0) & (moved < DURATION)]
        np.testing.assert_allclose(b, kept)                    # one offset, intervals intact
        lost += a.size - kept.size
        # nothing that started inside the valid window can have left the recording
        assert ((a >= lo) & (a <= hi)).sum() <= b.size
    assert neg.dropped == lost


def test_the_same_seed_gives_the_same_negative_and_a_set_can_be_remade_one_at_a_time():
    trains = _with_events(2)
    one = ng.rate_matched_negative(trains, DURATION, seed=11)
    again = ng.rate_matched_negative(trains, DURATION, seed=11)
    assert one.offsets_sec == again.offsets_sec
    several = ng.rate_matched_negatives(trains, DURATION, 4, seed=11)
    assert [n.seed for n in several] == [11, 12, 13, 14]
    assert several[0].offsets_sec == one.offsets_sec
    assert several[2].offsets_sec == ng.rate_matched_negative(trains, DURATION, seed=13).offsets_sec
    assert several[1].offsets_sec != several[2].offsets_sec


def test_planted_coordination_is_gone():
    trains = _with_events(3)
    lo, hi = J_SEC, DURATION - J_SEC
    planted = _windows_with_at_least(trains, 6, 2.0, lo, hi)
    assert planted >= 30, "the recording should hold its 40 events of 10 channels"
    after = [_windows_with_at_least(n.times, 6, 2.0, lo, hi)
             for n in ng.rate_matched_negatives(trains, DURATION, 20, seed=100)]
    # Not zero: the negative still holds the 400 planted onsets, scattered over ±20 s, so its
    # channels are busier than the true background and now and then six of them meet by chance.
    # That excess is the known bias of this negative (the module's last paragraph). Measured on
    # three seeds: 37 to 40 windows before, 0 to 2 in any one draw after.
    assert np.mean(after) < 1.0 and max(after) <= 3, (
        f"2 s windows with 6 or more channels after the shift, per draw: {after}")


def test_the_shared_slow_change_in_rate_survives_and_an_even_scatter_removes_it():
    trains = _shared_slow(4)
    lo, hi = J_SEC, DURATION - J_SEC
    before = _count_variance_ratio(trains, 60.0, lo, hi)
    assert before > 3.0, f"the recording should carry a shared slow change (ratio {before:.2f})"
    after = np.mean([_count_variance_ratio(n.times, 60.0, lo, hi)
                     for n in ng.rate_matched_negatives(trains, DURATION, 20, seed=200)])
    assert after > 0.8 * before, f"the shift lost the slow part: {before:.2f} became {after:.2f}"
    rng = np.random.RandomState(5)
    scattered = [np.sort(rng.uniform(0, DURATION, t.size)) for t in trains]
    assert _count_variance_ratio(scattered, 60.0, lo, hi) < 1.6


@pytest.mark.parametrize("bad, message", [
    (dict(duration_sec=0.0), "duration_sec"),
    (dict(j_sec=0.0), "j_sec"),
    (dict(duration_sec=30.0), "leaves nothing"),
])
def test_it_refuses_what_it_cannot_shift(bad, message):
    kwargs = dict(duration_sec=DURATION, seed=1) | bad
    duration = kwargs.pop("duration_sec")
    with pytest.raises(ValueError, match=message):
        ng.rate_matched_negative([np.array([1.0, 2.0])], duration, **kwargs)


def test_it_refuses_an_onset_outside_the_recording_and_an_empty_recording():
    with pytest.raises(ValueError, match="channel 1"):
        ng.rate_matched_negative([np.array([1.0]), np.array([DURATION + 5.0])], DURATION, seed=1)
    with pytest.raises(ValueError, match="at least one channel"):
        ng.rate_matched_negative([], DURATION, seed=1)
    with pytest.raises(ValueError, match="at least 1"):
        ng.rate_matched_negatives([np.array([1.0])], DURATION, 0, seed=1)


def test_a_channel_with_no_events_stays_empty():
    neg = ng.rate_matched_negative([np.array([]), np.array([100.0, 200.0])], DURATION, seed=3)
    assert neg.times[0].size == 0 and neg.times[1].size == 2
