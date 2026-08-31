"""The performance table — what each detector measured, and what disqualifies it.

**Nothing here produces an ordering, and that is the design.** An earlier version of
this module emitted tiers. It was removed because the question it answered was not
being asked (Tony, 2026-08-30: *"no ranking just a table of performance … no one said
we need to declare a winner"*) and because, tested, it could not answer it: tier
membership moved with the seed block while the argmax stood still.

The table reports the spread instead. A reader looking at ``0.651 (0.606–0.711)``
beside ``0.638 (0.567–0.696)`` can see those two detectors are not distinguishable
here, and no threshold had to be chosen on their behalf. **That is not a weaker
result than a ranking. It is the accurate one**, and the seed-block instability is
what says so.

**What was considered and rejected, because the reasoning outlives the decision.**
Comparing several algorithms across several data sets is a solved problem in
statistics: the Friedman test with a Nemenyi post-hoc, drawn as a critical-difference
diagram, which yields exactly the cliques the tiers were groping toward — derived from
the data rather than chosen (Demšar, *Statistical Comparisons of Classifiers over
Multiple Data Sets*, JMLR 7:1–30, 2006).

It is the wrong tool **here**, for a reason specific to this project. The mean-ranks
post-hoc compares two algorithms through a statistic that depends on *every other
algorithm in the pool*, so its verdict on A-vs-B changes when unrelated C, D, E are
added or removed. Benavoli, Corani & Mangili (*Should We Really Use Post-Hoc Tests
Based on Mean-Ranks?*, JMLR 17:1–10, 2016) put numbers on it: on one pair the sign
test has power 0.94 where the mean-ranks test has 0.046, and the critical value is
inflated by ``sqrt(m(m+1)/6)`` relative to a pairwise test — about **5x at twelve
detectors**.

This bench *deliberately* carries poor learned nets as controls. Under a mean-ranks
test those controls would not sit harmlessly at the bottom of the table; they would
inflate the variance of every comparison made in their presence, and the detectors
they exist to anchor would become harder to tell apart the more carefully the
controls were chosen. If an ordering is ever wanted, the pairwise route — Wilcoxon
signed-rank or the sign test, with Holm — is the one whose verdict does not depend on
who else is in the room.

**Gates stay, and they are not comparisons.** A promiscuity ceiling asks *is this
detector doing something disqualifying*, answered against a declared number, not
against another detector. So a gate survives the removal of the ranking unchanged —
and it becomes a **column**, not a removal: a failing detector stays in the table with
its verdict beside it, because the table's job is to report.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path

from .bench import MAX_PROBE_PER_MIN

__all__ = [
    "MIN_X_REALTIME", "MAX_DISTRACTOR_RATE", "FoldScore", "Row", "Table",
    "performance_table", "fold_scores_from_bakeoff",
]

MIN_X_REALTIME = 1.0
"""Detection throughput a detector must clear, as a multiple of realtime.

Set at "keeps up with acquisition", which is the only threshold meaning the same
thing on two machines. Raw seconds move with hardware and thread count and are
reported next to the platform that produced them, never used as a verdict.
"""

MAX_DISTRACTOR_RATE: float | None = None
"""Fraction of planted distractors a detector may fire on. ``None`` = disarmed.

**Wired and switched off**, because the quantity it would read is currently span
coverage rather than firing: it counts distractors covered by the union of the
detection spans, so it scales with span width, has no opportunity denominator, and
— unlike the probe count computed twenty lines above it in the same function — is
not restricted to unmatched detections. One detector makes two detections in a fold,
matches a planted event with both, and is scored as hitting twelve of twelve
distractors. Repair the measure and set a number here in the same commit:
``docs/todo/2026-08-30-distractor-hits-counts-coverage-not-firing.md``.
"""

_USE_BENCH_CEILINGS = object()
"""Sentinel: ``max_probe_per_min`` was not given, so use the bench's own table.

``None`` already means *disable this gate*, and "use the default" and "use no
ceiling at all" must not collapse into one argument value.
"""


@dataclass(frozen=True)
class FoldScore:
    """One detector on one held-out fold."""

    detector: str
    fold: int
    f1: float
    seeds: tuple[int, ...] = ()
    hot_fa_per_min: float = float("nan")
    distractor_rate: float = float("nan")
    detect_x_realtime: float = float("nan")
    recall: float = float("nan")
    precision: float = float("nan")
    by_frac: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Row:
    """One detector's line in the table.

    ``f1_lo`` / ``f1_hi`` are the min and max across folds — the **observed range,
    not an interval estimate**, and it is deliberately not dressed up as one. It is
    there so a reader can see two detectors overlap without anybody deciding on
    their behalf whether that overlap counts.
    """

    detector: str
    f1: float
    f1_lo: float
    f1_hi: float
    recall: float
    precision: float
    probe_per_min: float
    probe_ceiling: float | None
    gate: str
    """``pass`` · ``FAIL`` · ``none`` — and ``none`` means *no ceiling has been
    declared for this detector*, which is a different statement from passing. The
    learned models have no entries, so they read ``none`` while one of them fires
    above the ceiling a hand-written detector failed on."""
    distractor_rate: float
    detect_x_realtime: float
    n_folds: int


@dataclass(frozen=True)
class Table:
    """The rows, plus what they were measured on."""

    rows: tuple[Row, ...]
    """Ordered by mean F1, descending. **This is presentation, not a finding** —
    it makes the table readable and it is not a ranking. Two adjacent rows whose
    ranges overlap are not distinguishable by this bench, and the table says so by
    printing the range rather than by ordering them more carefully."""

    seeds: tuple[int, ...]
    n_folds: int

    def row(self, detector: str) -> Row | None:
        for r in self.rows:
            if r.detector == detector:
                return r
        return None

    def render(self, titles: dict | None = None) -> str:
        """The table as a reader gets it.

        The seed and fold counts lead, because an F1 quoted without them is the
        defect this project has already paid for twice.
        """
        titles = titles or {}
        head = (f"{len(self.seeds)} seeds, {self.n_folds} folds — "
                "fold range shown; no ordering claimed")
        cols = (f"{'detector':<22}{'F1':>6}{'fold range':>15}{'recall':>8}"
                f"{'prec':>7}{'probe/min':>11}{'ceiling':>9}{'gate':>6}"
                f"{'distr':>7}{'xRT':>10}")
        out = [head, cols, "-" * len(cols)]
        for r in self.rows:
            ceil = "—" if r.probe_ceiling is None else f"{r.probe_ceiling:g}"
            out.append(
                f"{titles.get(r.detector, r.detector):<22}{r.f1:6.3f}"
                f"{r.f1_lo:8.3f}-{r.f1_hi:<6.3f}{r.recall:8.2f}{r.precision:7.2f}"
                f"{r.probe_per_min:11.2f}{ceil:>9}{r.gate:>6}"
                f"{r.distractor_rate:7.2f}{r.detect_x_realtime:10.0f}")
        out.append("")
        out.append("distr is REPORTED, NOT GATED — it counts span coverage, not "
                   "firing; see the module docstring.")
        return "\n".join(out)


def _mean(xs) -> float:
    xs = [x for x in xs if math.isfinite(x)]
    return sum(xs) / len(xs) if xs else float("nan")


def performance_table(scores, *,
                      max_probe_per_min=_USE_BENCH_CEILINGS,
                      min_x_realtime: float | None = MIN_X_REALTIME,
                      max_distractor_rate: float | None = MAX_DISTRACTOR_RATE) -> Table:
    """Summarise :class:`FoldScore` per detector and apply the gates.

    Detectors need not have been scored on the same folds — nothing here compares
    one against another, so there is nothing for a mismatch to invalidate. That is
    a real consequence of dropping the ordering: the paired-fold requirement existed
    only to make comparisons legitimate.

    Pass ``None`` for any gate to disable it. ``max_probe_per_min`` left unset means
    :data:`bugarach.bench.MAX_PROBE_PER_MIN`, so the table and the calibration
    refuse the same behaviour; passing ``None`` explicitly disables the gate, which
    is a different instruction and has to look like one at the call site.
    """
    scores = list(scores)
    if not scores:
        raise ValueError("nothing to tabulate")
    ceilings = (MAX_PROBE_PER_MIN if max_probe_per_min is _USE_BENCH_CEILINGS
                else max_probe_per_min)

    by_det: dict[str, list[FoldScore]] = {}
    for s in scores:
        by_det.setdefault(s.detector, []).append(s)

    rows = []
    for det, v in by_det.items():
        f1s = [s.f1 for s in v if math.isfinite(s.f1)]
        probe = _mean([s.hot_fa_per_min for s in v])
        xrt = _mean([s.detect_x_realtime for s in v])
        distractor = _mean([s.distractor_rate for s in v])

        ceiling = ceilings.get(det) if ceilings is not None else None
        gate = "none"
        if ceiling is not None and math.isfinite(probe):
            gate = "pass" if probe <= ceiling else "FAIL"
        if (min_x_realtime is not None and math.isfinite(xrt)
                and xrt < min_x_realtime):
            gate = "FAIL"
        if (max_distractor_rate is not None and math.isfinite(distractor)
                and distractor > max_distractor_rate):
            gate = "FAIL"

        rows.append(Row(
            detector=det,
            f1=_mean(f1s),
            f1_lo=min(f1s) if f1s else float("nan"),
            f1_hi=max(f1s) if f1s else float("nan"),
            recall=_mean([s.recall for s in v]),
            precision=_mean([s.precision for s in v]),
            probe_per_min=probe,
            probe_ceiling=ceiling,
            gate=gate,
            distractor_rate=distractor,
            detect_x_realtime=xrt,
            n_folds=len(v),
        ))

    rows.sort(key=lambda r: (-(r.f1 if math.isfinite(r.f1) else -1), r.detector))
    seeds = sorted({sd for v in by_det.values() for s in v for sd in s.seeds})
    return Table(rows=tuple(rows), seeds=tuple(seeds),
                 n_folds=max(r.n_folds for r in rows))


def fold_scores_from_bakeoff(source) -> list[FoldScore]:
    """Read ``docs/learned/bakeoff.json`` (a path or the loaded dict) into scores.

    The bake-off records ``hot_fa`` and ``distractor_hits`` as raw counts, so the
    per-minute and per-opportunity conversions happen here, from that file's own
    spec rather than from a constant: a run with a different probe window or a
    different ``n_distractors`` converts correctly without an edit.
    """
    if isinstance(source, (str, Path)):
        source = json.loads(Path(source).read_text())

    spec = source.get("spec", {})
    seeds_all = list(source.get("seeds", ()))
    per_fold = int(source.get("seeds_per_fold", 1)) or 1

    hot = spec.get("hot_window")
    probe_minutes = ((hot[1] - hot[0]) / 60.0 * per_fold) if hot else float("nan")
    n_distractors = spec.get("n_distractors")
    opportunities = (n_distractors * per_fold) if n_distractors else None

    out: list[FoldScore] = []
    for group in ("hand_written", "learned"):
        for det, rec in source.get(group, {}).items():
            for p in rec.get("per_fold", ()):
                i = int(p["fold"])
                out.append(FoldScore(
                    detector=det,
                    fold=i,
                    f1=float(p["f1"]),
                    seeds=tuple(seeds_all[i * per_fold:(i + 1) * per_fold]),
                    hot_fa_per_min=(p["hot_fa"] / probe_minutes
                                    if probe_minutes and math.isfinite(probe_minutes)
                                    else float("nan")),
                    distractor_rate=(p["distractor_hits"] / opportunities
                                     if opportunities else float("nan")),
                    detect_x_realtime=float(p.get("detect_x_realtime", float("nan"))),
                    recall=float(p.get("recall", float("nan"))),
                    precision=float(p.get("precision", float("nan"))),
                    by_frac=dict(p.get("by_frac", {})),
                ))
    return out
