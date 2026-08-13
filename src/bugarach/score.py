"""Score detections against planted ground truth.

Ported from interface2's ``score_coord_detection.m``. Unlike the generator, this
one **is** exact — there is no RNG in it, so the matching rule transfers
literally rather than statistically.

The rule: match detected onsets to planted events **greedily, closest pair
first**, within ``tol_sec``. Greedy-nearest matters when detections are dense —
walking the planted events in time order and taking the first detection within
tolerance can consume a detection that was a much better match for the *next*
planted event, inflating misses. Sorting every candidate pair by distance and
consuming the best available first is stable against that.

What it reports, and why each part earns its place:

* **recall broken down by participation level** — the headline number hides the
  thing worth knowing. A detector that finds every all-ROI event and nothing at
  50% is a different instrument from one that degrades gracefully, and they can
  share an overall recall.
* **false alarms inside the dense-but-random block** — the promiscuity probe.
  Detections there are, by construction, not coordination: the block has an
  elevated rate and *no planted events*. A detector fooled by rate lights it up.
* **detections on distractors** — correlated population bursts are genuine
  cross-ROI coincidence that is not a coordinated event. Firing on them is not
  scored as a false alarm by default (they are real structure), but it is
  counted, because "should a burst count?" is a live question and the number is
  the way to settle it.
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
        if self.hot_fa:
            parts.append(f"hot-window FA {self.hot_fa}")
        if self.distractor_hits:
            parts.append(f"on distractors {self.distractor_hits}")
        by = " ".join(f"{int(f * 100)}%:{self.recall_at(f):.2f}"
                      for f in sorted(self.by_frac, reverse=True))
        return "  ".join(parts) + (f"   [{by}]" if by else "")


def score_detections(gt, onsets, *, tol_sec: float = 1.5) -> Score:
    """Match ``onsets`` against ``gt.events`` and report the breakdown.

    gt: a :class:`bugarach.simulate.GroundTruth`.
    onsets: detected event onset times (s).
    tol_sec: match tolerance. A detection matches a planted event when it lands
      within this of the planted time.
    """
    planted = np.asarray(gt.times, dtype=float)
    det = np.sort(np.asarray(onsets, dtype=float).ravel())
    det = det[np.isfinite(det)]
    nP, nD = planted.size, det.size

    matched = np.full(nP, np.nan)
    used = np.zeros(nD, dtype=bool)

    if nP and nD:
        # Every candidate pair, closest first — see the module docstring for why
        # this is not "walk the planted events in time order".
        pi, di = np.meshgrid(np.arange(nP), np.arange(nD), indexing="ij")
        dist = np.abs(planted[pi] - det[di])
        order = np.argsort(dist, axis=None, kind="stable")
        for flat in order:
            if dist.flat[flat] > tol_sec:
                break
            i, j = int(pi.flat[flat]), int(di.flat[flat])
            if np.isnan(matched[i]) and not used[j]:
                matched[i] = det[j]
                used[j] = True

    hits = ~np.isnan(matched)
    fa_times = det[~used] if nD else np.zeros(0)

    by_frac: dict = {}
    for e, hit in zip(gt.events, hits):
        n, h = by_frac.get(e.frac, (0, 0))
        by_frac[e.frac] = (n + 1, h + int(hit))

    hot = gt.params.get("hot_window")
    hot_fa = 0
    if hot is not None and fa_times.size:
        hot_fa = int(np.sum((fa_times >= hot[0]) & (fa_times <= hot[1])))

    distractor_hits = 0
    if gt.distractors and det.size:
        dt = np.array([d.time for d in gt.distractors], dtype=float)
        distractor_hits = int(np.sum(
            [np.any(np.abs(det - t) <= tol_sec) for t in dt]))

    return Score(n_planted=nP, n_detected=nD, hits=hits, matched=matched,
                 fa_times=fa_times, by_frac=by_frac, hot_fa=hot_fa,
                 distractor_hits=distractor_hits, tol_sec=tol_sec)
