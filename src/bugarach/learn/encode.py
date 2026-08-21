"""Recording in, per-frame score out — the representation every architecture shares.

Architecture-free and torch-free on purpose. It fixes what must not vary between
models, because varying it silently makes two models incomparable and a
performance-vs-mass curve stops meaning anything.

Frames, not seconds
-------------------
**Nothing inside a model knows what a second is.** A receptive field is a number
of samples; an event is some number of samples wide. Those transfer between rigs
and seconds do not — at a 0.1 s grid a 0.36 s event spans ~4 samples, and the
same event at 30 Hz spans ~11. A model trained on seconds-shaped windows has
learned the microscope.

Seconds appear at exactly two boundaries: ``dt`` is **required** to encode
(FOUNDATIONS §6 refuses rather than defaults), and :meth:`Detection.to_seconds`
converts back once so :func:`bugarach.score.score_stream` can score a model
against planted truth by the same rule as the six ports.

Row order is canonical, not arbitrary
-------------------------------------
Rows are sorted by firing frequency, busiest first — Tony's rule, and what the
viewer's raster already does. That turns row index from a meaningless label into
a coordinate: *how active is this cell relative to the others*. Permute the input
ROIs and :func:`encode` returns a bit-identical raster, which
:func:`permute_rois` exists to prove rather than assert.

⚠ **The sort reads the whole recording, so it is not causal.** Whatever window a
deployment ranks over must match training. :attr:`Encoded.rank_window` records
which was used so the two cannot drift apart unnoticed.

What a cell may contain is binary: did this ROI have an onset in this frame.
Amplitude and width exist in real stores but the generator does not produce them,
so training cannot use them — a hard limit worth restating before anyone adds a
channel a model could never have learned from.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from bugarach.detectors.rate import recording_extent, stream_trains


@dataclass(frozen=True)
class Encoded:
    """A recording as a model sees it. Every axis is samples."""

    raster: np.ndarray
    """``(n_roi, n_frame)`` float32, 1 where that ROI has an onset in that frame.
    Several onsets in one frame stay 1 — distinct activity, never a spike count."""
    order: np.ndarray
    """Original ROI index per row, so a detection traces back to a cell."""
    t0: float
    dt: float
    rank_window: tuple[int, int]

    @property
    def n_roi(self) -> int:
        return int(self.raster.shape[0])

    @property
    def n_frame(self) -> int:
        return int(self.raster.shape[1])


@dataclass(frozen=True)
class Detection:
    """A model's output, in frames. Converted once, at the boundary."""

    onset_frame: np.ndarray
    width_frame: np.ndarray
    score: np.ndarray
    threshold: float

    def to_seconds(self, enc: Encoded):
        """The six ports' output contract, so ``score_stream`` reads this directly."""
        return _Seconds(
            onset_sec=enc.t0 + self.onset_frame * enc.dt,
            width_sec=self.width_frame * enc.dt,
            score=self.score, threshold=self.threshold,
            times=enc.t0 + np.arange(self.score.size) * enc.dt)


@dataclass(frozen=True)
class _Seconds:
    onset_sec: np.ndarray
    width_sec: np.ndarray
    score: np.ndarray
    threshold: float
    times: np.ndarray


def encode(slice_, *, dt: float, stream: str | None = None,
           onset_field: str = "t50rise", extent=None,
           rank_window: tuple[int, int] | None = None) -> Encoded:
    """Slice -> :class:`Encoded`, rows sorted busiest-first.

    dt: **required.** Seconds per frame. No default and none inferred —
      FOUNDATIONS §6 refuses at the load boundary, because a warning fires after
      the number already exists. A simulated slice knows its own ``grid_sec``.
    """
    if dt is None or not np.isfinite(dt) or dt <= 0:
        raise ValueError(
            f"dt must be a positive sampling interval in seconds, got {dt!r}. "
            "Required, never defaulted — FOUNDATIONS §6.")

    name = stream if stream is not None else next(iter(slice_.streams))
    ext = recording_extent(slice_) if extent is None else extent
    t0, t1 = float(ext[0]), float(ext[1])
    trains = stream_trains(slice_.streams[name], (t0, t1), onset_field)
    n_frame = int(np.floor((t1 - t0) / dt)) + 1

    raster = np.zeros((len(trains), n_frame), dtype=np.float32)
    for r, v in enumerate(trains):
        if v.size:
            idx = np.clip(((v - t0) / dt).astype(np.int64), 0, n_frame - 1)
            raster[r, idx] = 1.0

    lo, hi = (0, n_frame) if rank_window is None else rank_window
    lo, hi = max(0, int(lo)), min(n_frame, int(hi))
    counts = raster[:, lo:hi].sum(axis=1)

    # Descending count, ties broken by the ROI's own activity — NOT by its
    # original index, which is exactly the arbitrary label the sort exists to
    # remove. Two ROIs with equal counts are common at these rates, and an
    # index tie-break makes the encoding depend on input order again: the
    # canonicalisation test caught precisely that. Comparing the onset frames
    # lexicographically keeps the key a function of the data. ROIs identical in
    # both count and onsets produce identical rows, so their order cannot matter.
    firing = [tuple(np.flatnonzero(raster[r, lo:hi]).tolist())
              for r in range(raster.shape[0])]
    order = np.array(sorted(range(counts.size),
                            key=lambda r: (-counts[r], firing[r])),
                     dtype=np.int64)
    return Encoded(raster=raster[order], order=order.astype(np.int64),
                   t0=t0, dt=float(dt), rank_window=(lo, hi))


def frame_targets(gt, enc: Encoded) -> np.ndarray:
    """``(n_frame,)`` — 1 inside a planted event, 0 elsewhere.

    The span is :attr:`~bugarach.simulate.PlantedEvent.observed_span`: **first to
    last participant onset, as actually planted**. Not ``time ± 3·jitter_sec``,
    which restates what the generator was *asked* for — a constant 2.16 s at bench
    settings against realized footprints with a median of 0.80 s and a 17-fold
    spread. The nominal window would teach a model that ~1.4 s of background
    belongs to every event, and erase the tightness axis entirely.

    **Distractors and the hot window are labelled 0**, which is what they are for.
    """
    y = np.zeros(enc.n_frame, dtype=np.float32)
    for e in gt.events:
        lo, hi = e.observed_span
        a = max(0, int(np.floor((lo - enc.t0) / enc.dt)))
        b = min(enc.n_frame, int(np.ceil((hi - enc.t0) / enc.dt)) + 1)
        if b > a:
            y[a:b] = 1.0
    return y


def decode(score: np.ndarray, *, threshold: float = 0.5,
           merge_gap_frames: int = 20, min_width_frames: int = 0) -> Detection:
    """Per-frame score -> detections, in frames.

    Supra-threshold frames become runs; runs closer than ``merge_gap_frames``
    merge — the gap rule the episode-mode detectors use. A detection's width is
    its run length, so the scorer matches it as an interval rather than at a
    resolution it never claimed.
    """
    above = np.asarray(score, dtype=float) >= threshold
    onsets: list[int] = []
    widths: list[int] = []
    if above.any():
        edges = np.diff(above.astype(np.int8))
        starts = list(np.flatnonzero(edges == 1) + 1)
        ends = list(np.flatnonzero(edges == -1) + 1)
        if above[0]:
            starts.insert(0, 0)
        if above[-1]:
            ends.append(above.size)
        merged: list[list[int]] = []
        for a, b in zip(starts, ends):
            if merged and a - merged[-1][1] <= merge_gap_frames:
                merged[-1][1] = b
            else:
                merged.append([a, b])
        for a, b in merged:
            if (b - a) < min_width_frames:
                continue
            onsets.append(a)
            widths.append(b - a)
    return Detection(onset_frame=np.array(onsets, dtype=np.int64),
                     width_frame=np.array(widths, dtype=np.int64),
                     score=np.asarray(score, dtype=np.float32),
                     threshold=float(threshold))


def permute_rois(slice_, seed: int, stream: str | None = None):
    """A copy with ROI rows shuffled — the probe for the canonicalisation claim.

    :func:`encode` sorts by frequency, so a permuted recording must encode
    bit-identically and a model's score must not move. A test rather than an
    assertion because the failure is invisible: a model that learned row order
    scores *well* here and collapses on the next recording.
    """
    import copy

    rng = np.random.RandomState(seed)
    out = copy.deepcopy(slice_)
    name = stream if stream is not None else next(iter(out.streams))
    st = out.streams[name]
    perm = rng.permutation(len(st.locs))
    for field in ("locs", "amp", "width", "t50rise"):
        v = getattr(st, field, None)
        if v is not None and len(v) == perm.size:
            setattr(st, field, [v[i] for i in perm])
    return out
