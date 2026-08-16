"""The encoding contract every architecture shares.

torch-free on purpose — these are the invariants the design rests on, and they
must hold whether or not a model has been trained or torch is installed.
"""

from __future__ import annotations

import numpy as np
import pytest

from bugarach.learn.encode import (
    decode,
    encode,
    frame_targets,
    permute_rois,
)
from bugarach.simulate import simulate_coordination

SIM = dict(duration_sec=600.0, n_roi=20, bg_rate_hz=0.02, participation=(0.5, 0.25),
           n_per_level=(3, 3), jitter_sec=0.3, min_sep_sec=40.0, grid_sec=0.1)


def _sim(seed=1):
    return simulate_coordination(seed=seed, **SIM)


def test_dt_is_required_and_never_guessed():
    """FOUNDATIONS §6: the load boundary refuses rather than defaults."""
    s, _ = _sim()
    for bad in (None, 0.0, -0.1, float("nan")):
        with pytest.raises(ValueError, match="dt must be"):
            encode(s, dt=bad)


def test_rows_come_out_sorted_busiest_first():
    """Tony's rule: row index is a coordinate, not a label."""
    s, _ = _sim()
    enc = encode(s, dt=0.1)
    counts = enc.raster.sum(axis=1)
    assert np.all(np.diff(counts) <= 0), f"not descending: {counts}"


def test_permuting_rois_encodes_identically():
    """The sort is a canonicalisation, not merely an invariance.

    A model that learned row order would score well here and collapse on the next
    recording, which is the one place nobody is looking — so this is a test and
    not a comment.
    """
    s, _ = _sim()
    a = encode(s, dt=0.1)
    b = encode(permute_rois(s, seed=3), dt=0.1)
    assert np.array_equal(a.raster, b.raster)


def test_encoding_is_binary_distinct_activity_not_a_spike_count():
    """Coactivity counts ROIs, never spikes (GLOSSARY). Two onsets in one frame
    stay 1, or a bursting ROI would masquerade as several."""
    s, _ = _sim()
    enc = encode(s, dt=5.0)          # coarse enough to collide onsets
    assert set(np.unique(enc.raster)) <= {0.0, 1.0}


def test_targets_come_from_what_was_planted_not_from_jitter_sec():
    """Labels use `observed_span` — first to last participant onset — so they
    track the generator instead of restating its request.

    The nominal +/-3 sigma window is a constant 6*jitter wide for every event.
    The realized footprints are not, and the label must show that spread or the
    tightness axis is erased before training starts.
    """
    s, gt = _sim()
    enc = encode(s, dt=0.1)
    y = frame_targets(gt, enc)
    assert y.sum() > 0

    observed = np.array([hi - lo for lo, hi in (e.observed_span for e in gt.events)])
    nominal = 6.0 * SIM["jitter_sec"]
    assert observed.std() > 0, "realized footprints should vary between events"
    assert observed.max() < nominal * 1.5
    # the labelled mass must match the realized spans, not the nominal constant
    assert y.sum() * 0.1 == pytest.approx(observed.sum(), rel=0.35)


def test_decode_round_trips_through_seconds_for_the_scorer():
    """Frames inside; seconds only at the boundary, in the six ports' contract."""
    s, gt = _sim()
    enc = encode(s, dt=0.1)
    y = frame_targets(gt, enc)
    det = decode(y, threshold=0.5, merge_gap_frames=5).to_seconds(enc)

    assert hasattr(det, "onset_sec") and hasattr(det, "width_sec")
    assert det.onset_sec.size == det.width_sec.size
    # decoding the ground truth back out should recover the planted events
    from bugarach.score import score_stream
    sc = score_stream(gt, det)
    assert sc.recall == 1.0, sc.summary()


def test_decode_merges_by_the_gap_rule():
    score = np.zeros(100)
    score[10:15] = 1.0
    score[20:25] = 1.0          # 5 frames after the first run ends
    assert decode(score, merge_gap_frames=2).onset_frame.size == 2
    assert decode(score, merge_gap_frames=10).onset_frame.size == 1


def test_encoding_does_not_depend_on_roi_count_being_fixed():
    """A model must run on the next recording, which has a different n_roi."""
    a = encode(simulate_coordination(seed=1, **{**SIM, "n_roi": 12})[0], dt=0.1)
    b = encode(simulate_coordination(seed=1, **{**SIM, "n_roi": 41})[0], dt=0.1)
    assert a.n_roi == 12 and b.n_roi == 41
    assert a.raster.shape[1] > 0 and b.raster.shape[1] > 0


def test_rank_window_is_recorded_because_the_sort_is_not_causal():
    """Ranking over a leading window must be reproducible and self-describing —
    training and deployment have to use the same rule or the model sees a
    different encoding than it was trained on."""
    s, _ = _sim()
    full = encode(s, dt=0.1)
    lead = encode(s, dt=0.1, rank_window=(0, 1000))
    assert full.rank_window == (0, full.n_frame)
    assert lead.rank_window == (0, 1000)
    # same data, different ordering rule -> generally a different row order
    assert lead.raster.shape == full.raster.shape
