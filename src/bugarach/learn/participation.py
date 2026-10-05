"""Participation for the learned models: a count they can see, membership they are trained on,
and events planted at the floor's boundary. ADR-0010 (Proposed), part 5 — preparation only.

**Why.** Every registered model combines its cells into a *fraction* of the field: chorus pools
the per-cell votes into their mean, spread and top-4 mean; line averages its votes over ROIs;
tube averages cells away before its kernel. ADR-0008's floor is an *absolute* number of
co-active ROIs, and no fraction-only model can learn "at least 7 cells". This module holds what
the ``*_part`` variants add, and nothing here changes a model registered before it:

* **A count the model can see** (:func:`count_features`). The pooled count is the **sum of
  bounded per-cell votes**, each in [0, 1], so it lies in [0, number of ROIs]. That bound is
  the difference from ``tiny``, whose rate-band pools sum unnormalised encoder activations and
  failed (F1 0.125). The recording's floor enters beside it as a per-recording scalar,
  broadcast in time. The head receives three channels:

  - ``log1p(count)``: the count itself, compressed so a 500-ROI field does not swamp the head;
  - ``log1p(floor)``: the floor, on the same scale;
  - ``tanh(count - floor + 0.5)``: the comparison, made explicit. Its sign flips exactly
    between ``floor - 1`` and ``floor`` co-active ROIs (ADR-0009 decision 2 scores an event
    at ``n_part >= floor``), and one ROI either side of the boundary moves it by about 0.46.

  Families: chorus and line get a new per-cell vote (a 1x1 convolution over the cell's own
  channels, then a sigmoid). Tube has no per-cell stage, so its equivalent is the number of
  ROIs with an onset in a centred window of ``count_frames`` frames (:func:`window_count`),
  which has no learnable part and is bounded by the number of ROIs in the same way.

* **Membership is trained** (:func:`membership_targets`, chorus and line only). Each planted
  event lists its member ROIs. A member's vote is pushed high across the event's realised span,
  and every other (ROI, frame) low. Distractor bursts are *masked*, not labelled low: a per-cell
  vote sees only its own cell, and a distractor member's onset looks exactly like an event
  member's, so a low label there would be a contradiction and not a lesson.

* **The boundary is planted** (:func:`boundary_recording`). A training recording gains events
  at its floor − 1, floor and floor + 1 participants besides the existing levels, and for
  training (:func:`training_targets`) events under the floor are labelled no event, and
  ``train`` centres its event crops on every planted event, so those negatives are seen as often
  as the positives beside them. Scoring
  is untouched: ``score.score_detections`` still treats them as "don't care" (ADR-0009
  decision 2), and bench recordings are built exactly as before.

torch is imported inside the functions that need it, as in the rest of ``bugarach.learn``.
"""
from __future__ import annotations

import numpy as np

from bugarach.learn.encode import Encoded, frame_targets

BOUNDARY_OFFSETS = (-1, 0, 1)
"""Participant counts planted relative to the recording's floor (ADR-0010 part 5)."""

COUNT_FRAMES = 20
"""Tube's counting window, in frames: ADR-0008's 2 s co-activity window
(``event_floor.WINDOW_SEC``) at the bench's 0.1 s grid. In frames because nothing inside a model
knows what a second is (``learn.encode``); at another grid pass another ``count_frames``."""

MEMBERSHIP_WEIGHT = 1.0
"""The membership term's weight in the ``*_part`` variants' loss, beside the frame loss (weight 1).
A starting point of equal weight, not a tuned value: the balanced membership loss and the frame
loss both start near 0.7. It is a training setting, so the night's search can move it."""

PART_TRAINING = dict(membership_weight=MEMBERSHIP_WEIGHT, floor_labels=True)
"""Training defaults of the chorus and line ``*_part`` variants (``Arch.training``)."""

PART_TRAINING_NO_MEMBERSHIP = dict(membership_weight=0.0, floor_labels=True)
"""Training defaults of ``tube_part``: sub-floor events are negatives, and there is no vote to
train membership on."""

VOTE_BIAS_INIT = -2.0
"""Starting bias of the per-cell vote, so an untrained vote is about 0.12 and the count starts
near a floor rather than at half the field."""


def reads_floor(model) -> bool:
    """Does this model take the recording's floor as an input?"""
    return bool(getattr(model, "reads_floor", False))


def floor_tensor(floor, batch: int, device):
    """``floor`` (a number, a sequence of ``batch`` numbers, or a tensor) as a ``(batch,)`` float
    tensor. ``None`` is refused: a model that reads the floor has no floor of its own to assume."""
    import torch

    if floor is None:
        raise ValueError(
            "this model reads the recording's floor (ADR-0010 part 5) and none was given. "
            "Pass floor=<ADR-0008 floor of the window>; learn.train.probabilities and "
            "Trained.predict compute one when they can.")
    f = torch.as_tensor(floor, dtype=torch.float32, device=device).reshape(-1)
    if f.numel() == 1 and batch != 1:
        f = f.expand(batch)
    if f.numel() != batch:
        raise ValueError(f"{f.numel()} floors for a batch of {batch} recordings")
    return f


def count_features(count, floor):
    """``count`` ``(B, T)`` and ``floor`` ``(B,)`` -> ``(B, 3, T)``: log1p(count), log1p(floor)
    broadcast in time, and ``tanh(count - floor + 0.5)``. See the module docstring."""
    import torch

    f = floor.view(-1, 1).expand_as(count)
    return torch.stack([torch.log1p(count), torch.log1p(f),
                        torch.tanh(count - f + 0.5)], dim=1)


def vote_head(nn, c_in: int):
    """The per-cell vote of the chorus and line ``*_part`` variants: a 1x1 convolution over one
    cell's ``c_in`` channels. The caller applies the sigmoid, so the vote is in (0, 1)."""
    import torch

    conv = nn.Conv1d(c_in, 1, kernel_size=1)
    with torch.no_grad():
        conv.bias.fill_(VOTE_BIAS_INIT)
    return conv


def window_count(x, count_frames: int = COUNT_FRAMES):
    """Tube's pooled count: ROIs with at least one onset in a centred window of
    ``2 * (count_frames // 2) + 1`` frames, per frame. ``x`` is the binary ``(B, n_roi, T)``
    raster; the result ``(B, T)`` lies in [0, n_roi]. No parameter, so nothing to train."""
    import torch

    b, n, t = x.shape
    half = max(0, int(count_frames) // 2)
    lit = torch.nn.functional.max_pool1d(x.reshape(b * n, 1, t), kernel_size=2 * half + 1,
                                         stride=1, padding=half).reshape(b, n, t)
    return lit.sum(dim=1)


# ---------------------------------------------------------------------------------------------
# targets
# ---------------------------------------------------------------------------------------------

def _span_frames(e, enc: Encoded):
    lo, hi = e.observed_span
    a = max(0, int(np.floor((lo - enc.t0) / enc.dt)))
    b = min(enc.n_frame, int(np.ceil((hi - enc.t0) / enc.dt)) + 1)
    return a, b


def training_targets(gt, enc: Encoded, floor) -> np.ndarray:
    """:func:`~bugarach.learn.encode.frame_targets` with every event under ``floor`` labelled
    no event — the training half of ADR-0010 part 5. ``floor=None`` is ``frame_targets``."""
    if floor is None:
        return frame_targets(gt, enc)
    y = np.zeros(enc.n_frame, dtype=np.float32)
    for e in gt.events:
        if int(e.n_part) < int(floor):
            continue
        a, b = _span_frames(e, enc)
        if b > a:
            y[a:b] = 1.0
    return y


def membership_targets(gt, enc: Encoded) -> tuple[np.ndarray, np.ndarray]:
    """``(target, mask)``, each ``(n_roi, n_frame)`` float32 in the encoded row order.

    ``target`` is 1 where a ROI is a member of a planted event, across that event's realised
    span (first to last participant onset, as :func:`frame_targets` uses), and 0 elsewhere.
    Every planted event counts, sub-floor ones included: a vote says whether this cell took
    part, and the count, not the vote, is compared with the floor. ``mask`` is 0 on the members
    of distractor bursts across their spans (see the module docstring) and 1 elsewhere.
    """
    n, t = enc.n_roi, enc.n_frame
    row_of = np.empty(n, dtype=np.int64)
    row_of[enc.order] = np.arange(n)
    target = np.zeros((n, t), dtype=np.float32)
    mask = np.ones((n, t), dtype=np.float32)
    for e in gt.events:
        a, b = _span_frames(e, enc)
        if b > a:
            target[row_of[list(e.rois)], a:b] = 1.0
    for d in getattr(gt, "distractors", ()):
        a, b = _span_frames(d, enc)
        if b > a:
            mask[row_of[list(d.rois)], a:b] = 0.0
    return target, mask


def membership_loss(votes, target, mask):
    """Balanced binary cross-entropy on the per-cell votes: half the weight on member frames,
    half on the rest, each averaged over the (ROI, frame) pairs ``mask`` keeps. Members are a
    fraction of a percent of the pairs, so an unbalanced mean would learn "never a member"."""
    import torch

    v = votes.clamp(1e-6, 1.0 - 1e-6)
    bce = torch.nn.functional.binary_cross_entropy(v, target, reduction="none")
    pos = target * mask
    neg = (1.0 - target) * mask
    return (0.5 * (bce * pos).sum() / pos.sum().clamp_min(1.0)
            + 0.5 * (bce * neg).sum() / neg.sum().clamp_min(1.0))


# ---------------------------------------------------------------------------------------------
# floors
# ---------------------------------------------------------------------------------------------

def recording_floor(slice_, gt, stream=None) -> int:
    """The floor a training recording carries (``gt.params["event_floor"]``, set by
    ``bench.with_floor``), or ADR-0008's floor computed from the recording when it carries none."""
    f = (getattr(gt, "params", None) or {}).get("event_floor")
    if f is not None:
        return int(f)
    from bugarach import bench

    name = stream if stream is not None else next(iter(slice_.streams))
    return int(bench.recording_floor(slice_, name).floor)


def encoded_floor(enc: Encoded) -> int:
    """ADR-0008's floor of an encoded window, from its own rigid-shift null — what
    :meth:`~bugarach.learn.train.Trained.predict` uses on a real window when not handed one.
    Seeded by a digest of the raster, so the same window always gets the same floor."""
    import hashlib

    from bugarach import event_floor as ef

    trains = [np.flatnonzero(row) for row in enc.raster]
    key = hashlib.sha256(enc.raster.tobytes()).hexdigest()[:32]
    return int(ef.window_floor(trains, enc.n_frame, enc.dt, key=("learned", key)).floor)


# ---------------------------------------------------------------------------------------------
# boundary planting (training recordings only)
# ---------------------------------------------------------------------------------------------

def boundary_recording(make_recording, regime: str, seed: int, *,
                       offsets=BOUNDARY_OFFSETS, n_per_boundary: int = 1, **overrides):
    """A training recording with extra events planted at its floor + each of ``offsets``.

    ``make_recording`` is a bench module's (``bench``, ``bench_slow``, ``bench_combined``):
    ``(regime, seed, **overrides) -> (slice, gt)`` with the floor in ``gt.params``. Two passes,
    because the floor is a property of the recording and not of its settings:

    1. the ordinary recording is built and its floor *F* read;
    2. the same seed is built again with ``n_per_boundary`` more events at each of
       ``F + offset`` participants (as fractions of the ROI count, which the generator rounds
       back to exactly that count), besides the existing levels.

    The returned recording carries **its own** floor, recomputed by ``with_floor``; planting
    more events can move it, so ``gt.params["boundary_planting"]`` records the floor the levels
    were planned at beside it. Training reads the returned floor (:func:`training_targets`).

    ⚠ Extra events must still fit the recording's spacing: at the bench's 120 s minimum and
    45 minutes, 15 + 3 events fit and 15 + 9 do not (the generator refuses). ADR-0010 part 2
    replaces that spacing; until then keep ``n_per_boundary`` at 1.

    Never use this for a scored recording: ADR-0009's bench is built by ``make_recording``.
    """
    s0, gt0 = make_recording(regime, seed, **overrides)
    base_floor = recording_floor(s0, gt0)
    n_roi = int(gt0.params["n_roi"])
    counts = [c for c in sorted({int(base_floor) + int(o) for o in offsets}) if 1 <= c <= n_roi]
    part = tuple(gt0.params["participation"]) + tuple(c / n_roi for c in counts)
    per = tuple(gt0.params["n_per_level"]) + (int(n_per_boundary),) * len(counts)
    s, gt = make_recording(regime, seed, **{**overrides, "participation": part,
                                            "n_per_level": per})
    gt.params["boundary_planting"] = dict(planned_floor=int(base_floor), counts=counts,
                                          n_per_boundary=int(n_per_boundary),
                                          offsets=[int(o) for o in offsets])
    return s, gt
