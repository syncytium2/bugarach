"""The ranking rule — tiers, not an order.

**The rule and the result live apart.** This module is the *rule*: it is a pure
function of scores handed to it, it regenerates nothing, and it reads no data set
of its own. The *result* is whatever it returns when pointed at a particular set
of scores, and a different data set is expected to change that result without
changing a line of this file. That separation is the whole design, and it comes
from a measurement rather than a preference:

    The background-axis winner flips between seed block 1..12 and seed block
    13..24. Same code, same grid, twelve different seeds, different winner.

A scheme that must emit a strict order will therefore emit a *different* strict
order next week. So this one refuses to. It emits **tiers**, and two detectors
share a tier unless one of them wins by a margin that a seed change does not
manufacture.

The decisions encoded here are Tony's, made 2026-08-30 against the five questions
in ``docs/handoffs/2026-08-30-ranking-the-detectors.md``. They are argued in
``docs/ranking_rule.md``; what follows is only what the code needs to say.

**D1 — what ranks and what merely reports.** Ranking runs on F1 alone, paired by
fold. Everything else is a *gate* (a requirement, which survives a change of data
set) or a *report* (a number a reader is owed but which moves no ordering). The
split is by what each measure **requires**, not by what it means: F1, the
participation breakdown and the distractor axis all need planted ground truth;
the promiscuity probe and the timing ratio do not. Point this at a data set with
no ground truth and you still have the second group, and you know exactly which
half you lost.

**D2 — the promiscuity probe is a gate, and the within-tier tiebreak.** It stays
out of F1 for the reason :data:`bugarach.bench.MAX_PROBE_PER_MIN` gives at
length: fold it in and the headline stops measuring the detector and starts
measuring how hard the probe was set. It gates instead, at the same ceilings the
calibration uses. Within a tier — where by construction nobody has won — the
lower probe rate is listed first.

That tiebreak looks like it rewards a detector for never firing, and does not:
reaching a tier at all requires having earned the F1 that put it there, so
"detects nothing" is filtered by the ranking before the tiebreak is ever
consulted. The order matters and is asserted in the tests.

**D3 — the distractor axis is specified and disarmed.** ``distractor_hits`` is
the most scientifically meaningful false positive this bench measures and it has
never entered a ranking. It still does not, because the number does not currently
mean what its name says: it counts *distractors covered by the union of the
detection spans*, so it scales with span width, has no opportunity denominator,
and — unlike ``hot_fa`` twenty lines above it in the same function — is not
restricted to unmatched detections, so a correct detection is charged as a
distractor hit too. ``tiny`` makes two detections in a fold, matches a planted
event with both, and is scored as hitting twelve of twelve distractors.
:data:`MAX_DISTRACTOR_RATE` is therefore ``None`` — the gate exists, is wired,
and is switched off — and the rate is reported so the axis is visible while it is
unusable. Repair it and re-arm it in the same commit:
``docs/todo/2026-08-30-distractor-hits-counts-coverage-not-firing.md``.

**D4 — what counts as a tie.** ``A`` beats ``B`` only if it wins a **majority of
the paired folds** *and* leads by more than :data:`TIE_MARGIN` in mean F1.
Anything else is a tie and the two share a tier. Both halves are load-bearing:
the pairing is the information a marginal mean throws away (``coact`` beat
``loco`` on **3 of 4 folds**, which reads as a coin flip once it is written
``0.651 ± 0.044`` against ``0.638 ± 0.053``), and the margin is what stops a
0.0011 lead at one grid point from being reported as a win.

**D5 — platform-dependent measures gate and never rank.** ``detect_sec`` and
``calibrate_sec`` move with hardware and thread count, and the shipped learned
numbers are bound to one platform. A detector is not better science for having
run on a faster machine, but an unusably slow one is genuinely disqualified, so
the normalised :data:`MIN_X_REALTIME` gates and the raw seconds are reported
beside the platform that produced them.

**Seed count is able to fail.** :func:`rank` refuses a data set thinner than
:data:`MIN_SEEDS` rather than ranking on it and mentioning the caveat somewhere.
The bench's own author left ``SEEDS = (1, 2, 3)`` in one file and *"Use 12 seeds,
not 3"* in the next one over; a rule that only warns is discovered by whoever
happens to read stderr, after the ordering it qualifies has been published. This
is the same argument FOUNDATIONS §6 makes for refusing a load without ``dt``.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path

from .bench import MAX_PROBE_PER_MIN

__all__ = [
    "MIN_SEEDS", "TIE_MARGIN", "MIN_X_REALTIME", "MAX_DISTRACTOR_RATE",
    "FoldScore", "Ranking", "TooThin", "rank", "fold_scores_from_bakeoff",
]

MIN_SEEDS = 12
"""Distinct recording seeds a ranking needs before it is allowed to exist.

Not a round number: it is the count this bench's own author reached for after
calling three noise-dominated, and the background axis needs twelve on each side
to show that the winner flips between blocks. Fewer is refused rather than
warned about — see :class:`TooThin`.
"""

TIE_MARGIN = 0.02
"""Mean-F1 lead below which two detectors are the same tier.

The noise floor of this bench, and comfortably above the 0.0011 that separated
``coact`` from ``loco`` at the busy end of the background grid — a gap that
reversed when the seed block changed.
"""

MIN_X_REALTIME = 1.0
"""Detection throughput a detector must clear, as a multiple of realtime.

Gates, never ranks (D5). Set at "keeps up with acquisition", which is the only
threshold that means the same thing on two machines.
"""

MAX_DISTRACTOR_RATE: float | None = None
"""Fraction of planted distractors a detector may fire on. ``None`` = disarmed.

**The gate is wired and switched off**, because the quantity it would read is
currently span coverage rather than firing — see the module docstring and
``docs/todo/2026-08-30-distractor-hits-counts-coverage-not-firing.md``. Set a
number here in the same commit that repairs ``score.py``, and say in that commit
what moved.
"""


_USE_BENCH_CEILINGS = object()
"""Sentinel: ``max_probe_per_min`` was not given, so use the bench's own table.

Needed because ``None`` already means *disable this gate*, and "use the default"
and "use no ceiling at all" are different instructions that must not collapse
into one argument value.
"""


class TooThin(ValueError):
    """The scores offered cover fewer than :data:`MIN_SEEDS` distinct seeds.

    Raised rather than warned, for the reason the module docstring gives: a
    warning is read after the ranking it qualifies has already been quoted.
    """


@dataclass(frozen=True)
class FoldScore:
    """One detector on one held-out fold.

    Everything the rule needs and nothing it does not. Built from whatever
    produced the scores — :func:`fold_scores_from_bakeoff` reads the shipped
    bake-off, and a caller with :class:`bugarach.bench.BenchResult` objects in
    hand can construct these directly.
    """

    detector: str
    fold: int
    f1: float
    seeds: tuple[int, ...] = ()
    hot_fa_per_min: float = float("nan")
    distractor_rate: float = float("nan")
    detect_x_realtime: float = float("nan")
    recall: float = float("nan")
    by_frac: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Ranking:
    """What the rule returns: tiers, refusals, and the numbers behind both."""

    tiers: tuple[tuple[str, ...], ...]
    """Detectors in tier order. Within a tier, ordered by the D2 tiebreak —
    lower probe rate first — which is presentation, not standing."""

    gated: dict
    """Detector -> the reason it was refused, in words. A gated detector is
    absent from :attr:`tiers` entirely: a gate is a refusal, not a demotion, the
    same way :class:`bugarach.bench.TooPromiscuous` refuses rather than taking
    second place."""

    mean_f1: dict
    """Detector -> mean F1 across its folds. Reported, never compared without
    the pairing that :func:`_beats` applies."""

    probe: dict
    """Detector -> mean promiscuity-probe firings per minute."""

    distractor: dict
    """Detector -> mean fraction of planted distractors fired on. **Reported and
    not gated** while D3's measure is broken."""

    n_folds: int
    seeds: tuple[int, ...]

    def tier_of(self, detector: str) -> int | None:
        """1-based tier, or ``None`` if the detector was gated out."""
        for i, tier in enumerate(self.tiers, start=1):
            if detector in tier:
                return i
        return None

    def table(self) -> str:
        """The result as a reader gets it: tiers, then the refusals with reasons."""
        lines = [f"{len(self.seeds)} seeds, {self.n_folds} folds, "
                 f"tie = majority of folds and >{TIE_MARGIN:g} mean F1"]
        for i, tier in enumerate(self.tiers, start=1):
            lines.append(f"  tier {i}")
            for d in tier:
                lines.append(
                    f"    {d:18}F1 {self.mean_f1[d]:.3f}   "
                    f"probe {self.probe[d]:6.2f}/min   "
                    f"distractor {self.distractor[d]:.2f} (reported, not gated)")
        for d, why in sorted(self.gated.items()):
            lines.append(f"  gated out  {d:18}{why}")
        return "\n".join(lines)


def _mean(xs) -> float:
    xs = [x for x in xs if math.isfinite(x)]
    return sum(xs) / len(xs) if xs else float("nan")


def _beats(a: list[float], b: list[float], tie_margin: float) -> bool:
    """D4: a majority of paired folds **and** a mean-F1 lead over the margin.

    Both conditions, because either alone has already misled this project. The
    pairing without the margin promotes a 0.0011 lead that reverses with the
    seed block; the margin without the pairing throws away that ``coact`` took
    three of four folds from ``loco``.
    """
    if len(a) != len(b) or not a:
        raise ValueError("paired comparison needs the same folds on both sides")
    wins = sum(1 for x, y in zip(a, b) if x > y)
    if wins * 2 <= len(a):
        return False
    return (_mean(a) - _mean(b)) > tie_margin


def rank(scores, *, min_seeds: int = MIN_SEEDS, tie_margin: float = TIE_MARGIN,
         max_probe_per_min=_USE_BENCH_CEILINGS,
         min_x_realtime: float | None = MIN_X_REALTIME,
         max_distractor_rate: float | None = MAX_DISTRACTOR_RATE) -> Ranking:
    """Apply the rule to a flat list of :class:`FoldScore` and return tiers.

    ``scores`` may hold any number of detectors, but every detector must have
    been scored on the **same folds** — that is what makes the comparison paired,
    and a detector scored on a different held-out set is not comparable under one
    heading. Mismatches raise rather than being reconciled.

    Gates are applied first and remove a detector from the ranking entirely.
    Pass ``None`` for any gate to disable it. ``max_probe_per_min`` left unset
    means :data:`bugarach.bench.MAX_PROBE_PER_MIN`, so the ranking and the
    calibration refuse the same behaviour by default; passing ``None``
    explicitly disables the probe gate, which is a different instruction and
    deliberately has to look like one at the call site.
    """
    scores = list(scores)
    if not scores:
        raise ValueError("nothing to rank")
    if tie_margin < 0:
        # A negative margin is the only way to make `beats` cyclic, and a cyclic
        # beats-relation has no tier decomposition to report. Refused at the
        # front rather than handled in the middle.
        raise ValueError(f"tie_margin must be >= 0, got {tie_margin}")
    ceilings = (MAX_PROBE_PER_MIN if max_probe_per_min is _USE_BENCH_CEILINGS
                else max_probe_per_min)

    by_det: dict[str, list[FoldScore]] = {}
    for s in scores:
        by_det.setdefault(s.detector, []).append(s)
    for d in by_det:
        by_det[d].sort(key=lambda s: s.fold)

    fold_sets = {d: tuple(s.fold for s in v) for d, v in by_det.items()}
    if len(set(fold_sets.values())) != 1:
        raise ValueError(
            "detectors were scored on different folds, so the comparison is not "
            f"paired: {fold_sets}")
    folds = next(iter(fold_sets.values()))

    seeds = sorted({sd for v in by_det.values() for s in v for sd in s.seeds})
    if len(seeds) < min_seeds:
        raise TooThin(
            f"{len(seeds)} distinct seeds, and the rule needs {min_seeds}. "
            "Ranking on fewer produces an ordering that changes with the seed "
            "block — which is the finding this rule exists to survive, not a "
            "caveat to attach to the answer.")

    mean_f1 = {d: _mean([s.f1 for s in v]) for d, v in by_det.items()}
    probe = {d: _mean([s.hot_fa_per_min for s in v]) for d, v in by_det.items()}
    distractor = {d: _mean([s.distractor_rate for s in v]) for d, v in by_det.items()}
    xrt = {d: _mean([s.detect_x_realtime for s in v]) for d, v in by_det.items()}

    gated: dict[str, str] = {}
    for d, v in by_det.items():
        if any(not math.isfinite(s.f1) for s in v):
            bad = [s.fold for s in v if not math.isfinite(s.f1)]
            gated[d] = f"F1 undefined on fold(s) {bad} — nothing to compare"
            continue
        ceiling = ceilings.get(d) if ceilings is not None else None
        if ceiling is not None and math.isfinite(probe[d]) and probe[d] > ceiling:
            gated[d] = (f"promiscuity probe {probe[d]:.2f}/min over its {ceiling:g} "
                        "ceiling — fires into a block containing nothing")
            continue
        if (min_x_realtime is not None and math.isfinite(xrt[d])
                and xrt[d] < min_x_realtime):
            gated[d] = (f"{xrt[d]:.2f}x realtime, under the {min_x_realtime:g}x "
                        "floor — cannot keep up with acquisition")
            continue
        if (max_distractor_rate is not None and math.isfinite(distractor[d])
                and distractor[d] > max_distractor_rate):
            gated[d] = (f"fires on {distractor[d]:.0%} of planted distractors, over "
                        f"the {max_distractor_rate:.0%} ceiling")

    live = [d for d in by_det if d not in gated]
    f1_folds = {d: [s.f1 for s in by_det[d]] for d in live}

    tiers: list[tuple[str, ...]] = []
    remaining = set(live)
    while remaining:
        unbeaten = {d for d in remaining
                    if not any(_beats(f1_folds[o], f1_folds[d], tie_margin)
                               for o in remaining if o != d)}
        if not unbeaten:
            # Unreachable while `beats` carries the margin conjunct, and the
            # proof is short: beating requires a mean-F1 lead greater than
            # tie_margin, so a cycle a>b>c>a would need 0 > 3 * tie_margin,
            # which a non-negative margin forbids (refused above). Kept as a
            # guard so that dropping the margin — the "majority only" rule that
            # was considered and rejected — degrades to "these are not
            # separable" rather than to a loop that never ends. Condorcet
            # cycles are not exotic: they turn up in about 3% of random triples
            # under majority alone, which is the test one file over.
            unbeaten = set(remaining)
        # D2's tiebreak, and it is ordering *within* a settled tier only.
        tier = tuple(sorted(unbeaten, key=lambda d: (
            probe[d] if math.isfinite(probe[d]) else float("inf"), d)))
        tiers.append(tier)
        remaining -= unbeaten

    return Ranking(tiers=tuple(tiers), gated=gated, mean_f1=mean_f1, probe=probe,
                   distractor=distractor, n_folds=len(folds), seeds=tuple(seeds))


def fold_scores_from_bakeoff(source) -> list[FoldScore]:
    """Read ``docs/learned/bakeoff.json`` (a path or the loaded dict) into scores.

    The bake-off records ``hot_fa`` and ``distractor_hits`` as raw counts, so the
    per-minute and per-opportunity conversions happen here, from that file's own
    spec rather than from a constant: a data set with a different probe window or
    a different ``n_distractors`` converts correctly without an edit.
    """
    if isinstance(source, (str, Path)):
        source = json.loads(Path(source).read_text())

    spec = source.get("spec", {})
    seeds_all = list(source.get("seeds", ()))
    per_fold = int(source.get("seeds_per_fold", 1)) or 1

    hot = spec.get("hot_window")
    probe_minutes = ((hot[1] - hot[0]) / 60.0 * per_fold) if hot else float("nan")
    n_distractors = spec.get("n_distractors")
    distractor_opportunities = (n_distractors * per_fold) if n_distractors else None

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
                    distractor_rate=(p["distractor_hits"] / distractor_opportunities
                                     if distractor_opportunities else float("nan")),
                    detect_x_realtime=float(p.get("detect_x_realtime", float("nan"))),
                    recall=float(p.get("recall", float("nan"))),
                    by_frac=dict(p.get("by_frac", {})),
                ))
    return out
