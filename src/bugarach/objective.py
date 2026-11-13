"""The tuning objective: the most planted events found, with false calls on the negative capped.

**The rule.** Among candidate settings of one detector, a search proposes the one with the
highest recall whose false calls per hour on rate-matched negatives are at or under a stated
cap. A setting over the cap is not a candidate, whatever its recall. If no setting is under the
cap, nothing is proposed: the cap is not loosened to let a result through
(``docs/adr/0009-the-bench-keeps-its-elevated-rate-test-in-a-recording-of-its-own.md``,
decision 4).

**None of this is new**, and the names other fields use for it are in
``docs/scoring_objective.md``: it is the Neyman-Pearson criterion of detection theory, scored
the way lesion detection (the free-response curve), seizure detection (sensitivity with false
detections per hour) and gravitational-wave searches (injections recovered at a false-alarm
rate, on time-shifted background) score event detectors. This module adds no statistic. It
holds the bookkeeping so every search applies the rule the same way.

**What it does not do.** It does not match calls to planted events: recall comes from
:mod:`bugarach.score`, which already does that one to one. It does not make negatives:
:mod:`bugarach.negatives` does. It does not choose the cap.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from bugarach.negatives import Negative

__all__ = ["FalseCalls", "Candidate", "Choice", "false_calls", "choose", "operating_curve",
           "hours_to_resolve"]


@dataclass(frozen=True)
class FalseCalls:
    """Calls counted on negatives, and the recording time they were counted over."""

    calls: int
    hours: float

    @property
    def per_hour(self) -> float:
        return self.calls / self.hours if self.hours > 0 else math.nan

    def __add__(self, other: "FalseCalls") -> "FalseCalls":
        return FalseCalls(self.calls + other.calls, self.hours + other.hours)


def false_calls(call_onsets_sec, negative: Negative) -> FalseCalls:
    """The calls a detector made on one negative, counted inside its valid window.

    ``call_onsets_sec`` are the onsets of the detector's calls on ``negative.times``. Only the
    window where no onset was dropped by the shift is read
    (:attr:`bugarach.negatives.Negative.valid_window`), and the hours are that window's.
    """
    lo, hi = negative.valid_window
    t = np.asarray(call_onsets_sec, dtype=float).ravel()
    return FalseCalls(calls=int(((t >= lo) & (t <= hi)).sum()), hours=(hi - lo) / 3600.0)


def hours_to_resolve(cap_per_hour: float) -> float:
    """Hours of negative needed before zero false calls shows the rate is under the cap.

    With no call in ``T`` hours the 95 % upper bound on the rate is about ``3 / T`` (the rule
    of three), so the cap is resolved only from ``3 / cap`` hours up.
    """
    if not cap_per_hour > 0:
        raise ValueError(f"the cap must be a positive number of calls per hour, got {cap_per_hour!r}")
    return 3.0 / cap_per_hour


@dataclass(frozen=True)
class Candidate:
    """One setting of one detector, scored on recordings with events and on their negatives."""

    setting: dict
    recall: float
    """Share of scored planted events found, one to one (:attr:`bugarach.score.Score.recall`)."""
    n_scored: int
    """Planted events in the recall's denominator: events under the floor are not in it."""
    false: FalseCalls
    """Calls on the negatives of the same recordings."""
    label: str = ""

    def admissible(self, cap_per_hour: float) -> bool:
        return self.false.per_hour <= cap_per_hour


@dataclass(frozen=True)
class Choice:
    """What :func:`choose` proposes, and why the others were not proposed."""

    cap_per_hour: float
    proposed: Candidate | None
    admissible: tuple[Candidate, ...]
    over_the_cap: tuple[Candidate, ...]
    resolved: bool
    """Whether the proposal's negatives cover enough hours for the cap to mean something
    (:func:`hours_to_resolve`). False does not block a proposal; it is reported with it."""
    notes: tuple[str, ...] = field(default_factory=tuple)


def choose(candidates, cap_per_hour: float) -> Choice:
    """The candidate with the highest recall among those at or under the cap.

    Ties in recall go to the candidate with fewer false calls per hour, then to the earlier one
    in ``candidates``, so the same inputs always give the same proposal.
    """
    need = hours_to_resolve(cap_per_hour)
    cands = list(candidates)
    for c in cands:
        if not (c.false.hours > 0):
            raise ValueError(f"candidate {c.label or c.setting} has no hours of negative: its "
                             f"false-call rate is unknown, so it cannot be held to a cap")
        if c.n_scored < 1:
            raise ValueError(f"candidate {c.label or c.setting} has no scored planted event")
    ok = [c for c in cands if c.admissible(cap_per_hour)]
    over = [c for c in cands if not c.admissible(cap_per_hour)]
    notes = []
    if not ok:
        notes.append(f"no setting is at or under {cap_per_hour:g} false calls per hour; "
                     f"nothing is proposed and the cap stands")
        return Choice(cap_per_hour, None, (), tuple(over), False, tuple(notes))
    best = min(range(len(ok)), key=lambda i: (-ok[i].recall, ok[i].false.per_hour, i))
    proposed = ok[best]
    resolved = proposed.false.hours >= need
    if not resolved:
        notes.append(f"the proposal's negatives cover {proposed.false.hours:.2f} hours; "
                     f"{need:.2f} hours are needed before zero calls shows a rate under the cap")
    return Choice(cap_per_hour, proposed, tuple(ok), tuple(over), resolved, tuple(notes))


def operating_curve(candidates) -> list[tuple[float, float]]:
    """``(false calls per hour, best recall at or under that rate)``, rising in both.

    The whole trade-off, for reporting beside the one proposed setting: the free-response
    curve of the lesion-detection literature, with hours in place of images.
    """
    pts = sorted(((c.false.per_hour, c.recall) for c in candidates), key=lambda p: (p[0], -p[1]))
    curve, best = [], -math.inf
    for rate, recall in pts:
        if recall > best:
            best = recall
            curve.append((rate, recall))
    return curve
