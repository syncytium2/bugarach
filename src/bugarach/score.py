"""Score detections against planted ground truth.

Ported from interface2's ``score_coord_detection.m``. Unlike the generator, this
one **is** exact — there is no RNG in it, so the matching rule transfers
literally rather than statistically.

The rule: match detections to planted events **greedily, closest pair first**,
within ``tol_sec``. Greedy-nearest matters when detections are dense — walking
the planted events in time order and taking the first detection within tolerance
can consume a detection that was a much better match for the *next* planted
event, inflating misses. Sorting every candidate pair by distance and consuming
the best available first is stable against that.

A detection is an **interval**, not a point
-------------------------------------------
Pass ``widths`` and a detection spans ``[onset, onset + width]``; the distance to
a planted event is zero when the event falls inside that span, and the gap to the
nearer edge otherwise. Omit ``widths`` and every detection is a zero-width
interval, which is exactly the point-matching rule above — this is a
generalization, not a change of behaviour.

It exists because the point rule silently misreads binned detectors. SCE bins at
10 s by default and reports the bin's left edge, so on simulator output it scored
**0.00 recall on fourteen detections that each spanned a planted event** — every
one landed up to 10 s early and nothing matched at ±1.5 s. The detector was
right; the scorer was measuring it at a resolution it does not claim to have.

Widening ``tol_sec`` for everyone is the wrong repair twice over: it makes LoCo
look no better than a detector firing on the right minute, and it assumes the
error is symmetric when a left-edge convention makes it entirely one-sided. Only
the detector knows its own span, so the detector supplies it. That also keeps the
rule convention-independent — left edges, bin centres and episode extents all
work without the scorer knowing which it was handed.

What it reports, and why each part earns its place:

* **recall broken down by participation level** — the headline number hides the
  thing worth knowing. A detector that finds every all-ROI event and nothing at
  50% is a different instrument from one that degrades gracefully, and they can
  share an overall recall.
* **false alarms inside the dense-but-random block** — the promiscuity probe.
  Detections there are, by construction, not coordination: the block has an
  elevated rate and *no planted events*. A detector fooled by rate lights it up.
* **detections on distractors** — correlated population bursts are genuine
  cross-ROI coincidence that is not a coordinated event. They are counted
  separately in ``distractor_hits`` because "should a burst count?" is a live
  question and the number is the way to settle it. **They are not exempt from
  the false-alarm count**: a detection on a distractor matches no planted event,
  so it lands in ``fa_times`` and costs precision like any other. An earlier
  version of this docstring said the opposite, which was wrong about this
  module's own behaviour.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class Score:
    """The outcome of matching one detector's onsets against ground truth."""

    n_planted: int
    n_detected: int
    hits: np.ndarray
    """Boolean, per planted event, in ``gt.events`` order."""
    matched: np.ndarray
    """Matched detection time per planted event; NaN where missed."""
    fa_times: np.ndarray
    """Detections that matched no planted event."""
    dup_times: np.ndarray = field(default_factory=lambda: np.zeros(0))
    """The subset of ``fa_times`` that landed on a planted event which some
    *other* detection had already claimed — a detector firing twice for one
    event rather than firing at nothing."""
    by_frac: dict = field(default_factory=dict)
    """``{participation_fraction: (n_planted, n_hit)}``."""
    hot_fa: int = 0
    """False alarms inside the dense-but-random window (the promiscuity probe)."""
    distractor_hits: int = 0
    """Distractors that a detection landed on. Counted, not penalized."""
    tol_sec: float = 1.5

    @property
    def n_hit(self) -> int:
        return int(self.hits.sum())

    @property
    def n_miss(self) -> int:
        return int((~self.hits).sum())

    @property
    def n_fa(self) -> int:
        return int(self.fa_times.size)

    @property
    def n_duplicate(self) -> int:
        """Unmatched detections sitting on a planted event anyway.

        Greedy matching is one-to-one, so a detector that splits one event into
        three detections gets one hit and two false alarms — scored identically
        to a detector that fired at nothing. The two are not the same failure:
        fragmentation is a merge-gap problem, and firing at noise is a threshold
        problem. Counting them together hides which one you have.
        """
        return int(self.dup_times.size)

    @property
    def n_spurious(self) -> int:
        """False alarms that are not near any planted event — the real ones."""
        return self.n_fa - self.n_duplicate

    @property
    def recall(self) -> float:
        return float(self.n_hit / self.n_planted) if self.n_planted else float("nan")

    @property
    def precision(self) -> float:
        return float(self.n_hit / self.n_detected) if self.n_detected else float("nan")

    @property
    def f1(self) -> float:
        r, p = self.recall, self.precision
        if not np.isfinite(r) or not np.isfinite(p) or (r + p) == 0:
            return float("nan")
        return float(2 * r * p / (r + p))

    def recall_at(self, frac: float) -> float:
        """Recall for one participation level — the breakdown that matters."""
        n, h = self.by_frac.get(frac, (0, 0))
        return float(h / n) if n else float("nan")

    def summary(self) -> str:
        parts = [f"recall {self.recall:.2f}", f"precision {self.precision:.2f}",
                 f"F1 {self.f1:.2f}", f"FA {self.n_fa}"]
        if self.n_duplicate:
            parts.append(f"({self.n_duplicate} duplicate)")
        if self.hot_fa:
            parts.append(f"hot-window FA {self.hot_fa}")
        if self.distractor_hits:
            parts.append(f"on distractors {self.distractor_hits}")
        by = " ".join(f"{int(f * 100)}%:{self.recall_at(f):.2f}"
                      for f in sorted(self.by_frac, reverse=True))
        return "  ".join(parts) + (f"   [{by}]" if by else "")


def _spans(onsets, widths):
    """Detections as sorted ``(onset, end)`` arrays, non-finite onsets dropped.

    Widths ride along with the sort — they are per-detection, so sorting the
    onsets alone would silently pair each span with its neighbour's width. A
    missing or non-finite width is zero, which makes the detection a point.
    """
    o = np.asarray(onsets, dtype=float).ravel()
    if widths is None:
        w = np.zeros(o.size)
    else:
        w = np.asarray(widths, dtype=float).ravel()
        if w.size != o.size:
            raise ValueError(
                f"widths has {w.size} entries for {o.size} onsets — they are "
                "per-detection and must be column-aligned")
        w = np.where(np.isfinite(w), w, 0.0)
        w = np.maximum(w, 0.0)
    keep = np.isfinite(o)
    o, w = o[keep], w[keep]
    order = np.argsort(o, kind="stable")
    o = o[order]
    return o, o + w[order]


def _gap(planted, lo, hi):
    """Distance from a planted time to a detection span; 0 when it falls inside."""
    return np.maximum(0.0, np.maximum(lo - planted, planted - hi))


def score_detections(gt, onsets, *, widths=None, tol_sec: float = 1.5) -> Score:
    """Match detections against ``gt.events`` and report the breakdown.

    gt: a :class:`bugarach.simulate.GroundTruth`.
    onsets: detected event onset times (s).
    widths: detection spans (s), column-aligned with ``onsets`` — every detector
      stream carries these as ``width_sec``. Supply them for any binned or
      episode detector, or its detections are scored as if it claimed a
      precision it never did (see the module docstring). Omitted, detections are
      points and the rule is plain nearest-onset matching.
    tol_sec: match tolerance, applied to the gap between the planted time and the
      detection's span. A detection whose span contains the planted event matches
      at any tolerance.
    """
    planted = np.asarray(gt.times, dtype=float)
    lo, hi = _spans(onsets, widths)
    nP, nD = planted.size, lo.size

    matched = np.full(nP, np.nan)
    used = np.zeros(nD, dtype=bool)

    if nP and nD:
        # Every candidate pair, closest first — see the module docstring for why
        # this is not "walk the planted events in time order".
        pi, di = np.meshgrid(np.arange(nP), np.arange(nD), indexing="ij")
        dist = _gap(planted[pi], lo[di], hi[di])
        # Spans that all contain the same event tie at gap 0; break by distance
        # to the span's midpoint, so the detection centred on the event wins
        # rather than whichever happened to start first. With zero-width spans
        # both keys are |planted - onset| and the order is the old one exactly.
        centre = np.abs(planted[pi] - 0.5 * (lo[di] + hi[di]))
        order = np.lexsort((centre.ravel(), dist.ravel()))
        for flat in order:
            if dist.flat[flat] > tol_sec:
                break
            i, j = int(pi.flat[flat]), int(di.flat[flat])
            if np.isnan(matched[i]) and not used[j]:
                matched[i] = lo[j]
                used[j] = True

    hits = ~np.isnan(matched)
    fa_times = lo[~used] if nD else np.zeros(0)
    fa_ends = hi[~used] if nD else np.zeros(0)

    # Split the false alarms: one that lands on a planted event is a duplicate
    # of an event already claimed, not a detection of nothing.
    if fa_times.size and nP:
        near = np.array([np.min(_gap(planted, a, b)) <= tol_sec
                         for a, b in zip(fa_times, fa_ends)])
        dup_times = fa_times[near]
    else:
        dup_times = np.zeros(0)

    by_frac: dict = {}
    for e, hit in zip(gt.events, hits):
        n, h = by_frac.get(e.frac, (0, 0))
        by_frac[e.frac] = (n + 1, h + int(hit))

    # The probe counts a false alarm that *overlaps* the window, not one whose
    # left edge happens to land in it — a span straddling the boundary was still
    # fired inside the dense block. Zero-width spans reduce to containment.
    hot = gt.params.get("hot_window")
    hot_fa = 0
    if hot is not None and fa_times.size:
        hot_fa = int(np.sum((fa_ends >= hot[0]) & (fa_times <= hot[1])))

    distractor_hits = 0
    if gt.distractors and nD:
        dt = np.array([d.time for d in gt.distractors], dtype=float)
        distractor_hits = int(np.sum(
            [np.any(_gap(t, lo, hi) <= tol_sec) for t in dt]))

    return Score(n_planted=nP, n_detected=nD, hits=hits, matched=matched,
                 fa_times=fa_times, dup_times=dup_times, by_frac=by_frac,
                 hot_fa=hot_fa, distractor_hits=distractor_hits,
                 tol_sec=tol_sec)


_ONSET_FIELDS = (("onset_sec", "width_sec"), ("locs", "widths"))


def score_stream(gt, det, *, tol_sec: float = 1.5) -> Score:
    """Score a detector's own result object, spans included.

    Prefer this to :func:`score_detections` whenever you have a detection object
    rather than a bare array. Passing ``widths`` is not something to remember —
    a scorer handed only onsets cannot tell a binned detector from an
    onset-resolution one, and the failure is silent (SCE read 0.00 recall on
    detections that were all correct). This reads both fields off the detector,
    so the right call is the short one.

    Handles either field convention: ``onset_sec``/``width_sec`` (SCE, LoCo,
    CICADA, CoactDetect) or ``locs``/``widths`` (RateDetect, spike-sync).
    """
    for onset_field, width_field in _ONSET_FIELDS:
        if hasattr(det, onset_field):
            return score_detections(gt, getattr(det, onset_field),
                                    widths=getattr(det, width_field, None),
                                    tol_sec=tol_sec)
    raise TypeError(
        f"{type(det).__name__} carries no detection times — expected one of "
        f"{[f[0] for f in _ONSET_FIELDS]}. Pass the arrays to score_detections "
        "instead, with widths= for a binned detector.")
