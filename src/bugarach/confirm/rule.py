"""The confirmatory rule: gate statistics in, one outcome out.

Nothing here touches a recording or draws a random number. Every function takes the numbers a
gate produced (bounds, control readings, flag counts) and returns a verdict, so the whole
decision can be exercised on hand-built inputs before any data exist. That is the point: the
prose version of this rule was reviewed twice and each time a reader found a combination of
results it did not decide.

**Verdicts.** Each gate, each cell (one stream at one displacement *J*) and each stream gets
one of four verdicts. When several apply, the most cautious wins, in this order:

    VOID  >  FAIL  >  UNDECIDED  >  PASS

* **VOID** — a control the gate needs is invalid, so the gate measured nothing readable.
* **FAIL** — the gate failed and the failure is decided: its interval lies wholly on the
  failing side of the threshold, with every control valid.
* **UNDECIDED** — neither decidedly passing nor decidedly failing.
* **PASS** — the interval lies wholly on the passing side, with every control valid.

**Outcomes.** One per run: ``VIABLE``, ``NARROWED``, ``STOPPED``, ``FAILED_ON_COUNT`` or
``UNRESOLVED``. :func:`outcome` documents exactly which inputs give which.

The thresholds are the ones Tony signed on 2026-09-14; the structure is the blind review
round's repairs. Where a choice here was made by the implementation rather than signed, the
constant or function says so in its docstring, and the signing of this module is what adopts
it.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Mapping, Sequence

# -- signed thresholds ------------------------------------------------------------------------

N_DISPLACEMENTS = 3
"""Declared displacements per stream; the family the leak and destruction bounds correct for."""

ALPHA = 0.05
FAMILY_ALPHA = ALPHA / N_DISPLACEMENTS
"""0.05 / 3. Each one-sided bound is taken at this level (the 1.67th / 98.33rd percentile)."""

LEAK_MARGIN = 0.55
"""Forced-choice accuracy at or above which a surrogate leaks. Chance is 0.50."""

COUNT_TOLERANCE = 0.02
"""Occupied-frame change, as a share of the real count, within which counts are preserved."""

RETAINED_MAX = 0.25
"""Largest share of planted coordination a surrogate may leave in place."""

NEGATIVE_SEEDS = 20
NEGATIVE_VOID_FLAGS = 4
"""The real-against-real control voids a stream when this many of its seeds flag at ALPHA."""

VISIBILITY_FLOOR = 1.0
"""Planted-minus-unplanted coactivity excess (ROI·events per minute) below which a K is not gated.

⚠ Implementation choice, not signed as a number with a unit: the amendment said "at least 1.0"
without naming the quantity. This names it."""

GRADED_MIN = 0.10
GRADED_MAX = 0.90
"""The half-frozen control must read retained inside this band at a K for that K to be gated."""

HOMOGENEOUS_MAX = 0.10
DO_NOTHING_MIN = 0.90

N_GROUPS = 4
GROUP_ALPHA = FAMILY_ALPHA / N_GROUPS
"""A group narrows a passing stream only when its leak lower bound at this level is above the
margin. ⚠ Implementation choice from the blind round: the adopted amendment used a point
estimate, which narrows about 15 % of the time on a perfect surrogate."""


class Verdict(enum.IntEnum):
    """Ordered by caution: a larger value wins when verdicts are combined."""

    PASS = 0
    UNDECIDED = 1
    FAIL = 2
    VOID = 3


def most_cautious(verdicts: Sequence[Verdict]) -> Verdict:
    """The winning verdict when several apply: VOID over FAIL over UNDECIDED over PASS."""
    if not verdicts:
        raise ValueError("no verdicts to combine")
    return max(verdicts)


@dataclass(frozen=True)
class Interval:
    """A one-sided lower and upper bound, each at FAMILY_ALPHA, from the same resampling."""

    lo: float
    hi: float

    def __post_init__(self):
        if not (self.lo <= self.hi):
            raise ValueError(f"interval lower bound {self.lo} is above its upper bound {self.hi}")


def _against(iv: Interval, threshold: float, pass_below: bool) -> Verdict:
    """PASS if the interval lies wholly on the passing side, FAIL if wholly on the other."""
    if pass_below:
        if iv.hi < threshold:
            return Verdict.PASS
        if iv.lo > threshold:
            return Verdict.FAIL
    else:
        if iv.lo > threshold:
            return Verdict.PASS
        if iv.hi < threshold:
            return Verdict.FAIL
    return Verdict.UNDECIDED


# -- the leak gate ----------------------------------------------------------------------------

@dataclass(frozen=True)
class LeakReading:
    """What the leak gate measured at one cell."""

    candidate: Interval
    """Forced-choice accuracy of real against rigid shift, bootstrap over mice with refitting."""
    positive: Interval
    """The same pipeline against the fixed positive control; it must be detected."""
    negative_flags: int
    """Seeds of the real-against-real control, out of NEGATIVE_SEEDS, that flagged at ALPHA."""


def leak_verdict(r: LeakReading) -> Verdict:
    """VOID if a control failed; otherwise the candidate's interval against the margin.

    The positive control is valid only when its **lower** bound is above the margin. The
    negative control voids when NEGATIVE_VOID_FLAGS or more seeds flag. There is no can-pass
    override: the blind round showed a single draw calls a perfect surrogate UNDECIDED about a
    quarter of the time and adds nothing a passing bound does not already show.
    """
    if not 0 <= r.negative_flags <= NEGATIVE_SEEDS:
        raise ValueError(f"negative_flags must be 0..{NEGATIVE_SEEDS}, got {r.negative_flags}")
    if r.negative_flags >= NEGATIVE_VOID_FLAGS:
        return Verdict.VOID
    if not r.positive.lo > LEAK_MARGIN:
        return Verdict.VOID
    return _against(r.candidate, LEAK_MARGIN, pass_below=True)


# -- the count gate ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CountReading:
    """Occupied-frame change as a share of the real count, interior windows, over mice."""

    candidate: Interval
    """Two-sided interval (each bound at FAMILY_ALPHA) for rigid shift."""
    control: Interval
    """The same for ``edge_thinning`` at a fixed 5 s, which must be detected as a change."""


def _equivalence(iv: Interval, tol: float) -> Verdict:
    """Two one-sided tests: PASS inside ±tol, FAIL wholly outside it, otherwise UNDECIDED."""
    if -tol < iv.lo and iv.hi < tol:
        return Verdict.PASS
    if iv.hi < -tol or iv.lo > tol:
        return Verdict.FAIL
    return Verdict.UNDECIDED


def count_verdict(r: CountReading) -> Verdict:
    """VOID unless the control lies wholly outside ±COUNT_TOLERANCE; then equivalence."""
    if _equivalence(r.control, COUNT_TOLERANCE) is not Verdict.FAIL:
        return Verdict.VOID
    return _equivalence(r.candidate, COUNT_TOLERANCE)


# -- the destruction gate ---------------------------------------------------------------------

@dataclass(frozen=True)
class DestructionAtK:
    """Destruction readings at one K (absolute co-active ROIs), one participation, one bin."""

    k: int
    before: float
    """Planted minus unplanted coactivity excess before any surrogate, mean over twins."""
    retained: Interval
    """Retained share for rigid shift, bootstrap over twins."""
    graded: float
    """Retained share for the half-frozen homogeneous-resample control."""
    homogeneous: float
    """Retained share for homogeneous resample."""
    do_nothing: float
    """Retained share for do-nothing, scored with a different assessor seed after."""


def gated(d: DestructionAtK) -> bool:
    """A K is gated when the planted events are visible and the graded control reads a grade.

    There is deliberately **no saturation exclusion**: a K where the shifted event still lands
    in one bin is a K where the surrogate left coordination in place, which is a failure to
    be scored, not a case to skip (the blind round's inverted-saturation finding).
    """
    return d.before >= VISIBILITY_FLOOR and GRADED_MIN <= d.graded <= GRADED_MAX


def destruction_block_verdict(rows: Sequence[DestructionAtK]) -> Verdict:
    """One participation level at one bin width.

    VOID when the machinery controls fail at any gated K, or when no K is gated. Otherwise the
    most cautious of the gated K's retained intervals against RETAINED_MAX.
    """
    g = [d for d in rows if gated(d)]
    if not g:
        return Verdict.VOID
    for d in g:
        if d.homogeneous > HOMOGENEOUS_MAX or d.do_nothing < DO_NOTHING_MIN:
            return Verdict.VOID
    return most_cautious([_against(d.retained, RETAINED_MAX, pass_below=True) for d in g])


def destruction_verdict(blocks: Mapping[tuple[float, float], Sequence[DestructionAtK]]) -> Verdict:
    """Every (participation, bin width) block must pass; the most cautious block wins.

    Slow is scored at both 1.0 s and 2.0 s bins, so its mapping carries four blocks; fast
    carries two.
    """
    if not blocks:
        raise ValueError("no destruction blocks")
    return most_cautious([destruction_block_verdict(rows) for rows in blocks.values()])


# -- cells, streams, outcome ------------------------------------------------------------------

@dataclass(frozen=True)
class CellVerdict:
    leak: Verdict
    count: Verdict
    destruction: Verdict

    @property
    def verdict(self) -> Verdict:
        return most_cautious([self.leak, self.count, self.destruction])

    @property
    def failed_only_on_count(self) -> bool:
        """FAIL whose only failing gate is count: the leak and destruction gates passed."""
        return (self.verdict is Verdict.FAIL and self.count is Verdict.FAIL
                and self.leak is Verdict.PASS and self.destruction is Verdict.PASS)


def stream_verdict(cells: Sequence[CellVerdict]) -> Verdict:
    """PASS if any cell passes; FAIL only if every cell fails; VOID if every non-failing cell is
    void; otherwise UNDECIDED. A void or undecided cell can never make a stream FAIL."""
    if len(cells) != N_DISPLACEMENTS:
        raise ValueError(f"a stream has {N_DISPLACEMENTS} cells, got {len(cells)}")
    v = [c.verdict for c in cells]
    if Verdict.PASS in v:
        return Verdict.PASS
    if all(x is Verdict.FAIL for x in v):
        return Verdict.FAIL
    if all(x is Verdict.VOID for x in v if x is not Verdict.FAIL):
        return Verdict.VOID
    return Verdict.UNDECIDED


def passing_positions(cells: Sequence[CellVerdict]) -> set[int]:
    """Grid positions (0 is the smallest *J*) at which a stream's cells pass."""
    return {i for i, c in enumerate(cells) if c.verdict is Verdict.PASS}


def cossart_reading(streams: Mapping[str, Sequence[CellVerdict]], passing: Sequence[str],
                    cossart_leak: Sequence[Verdict]) -> Verdict:
    """Cossart's leak verdict read at the grid positions where a lab stream passed.

    The **least cautious** verdict among those positions is taken, so Cossart passes if it
    passes at any of them. ⚠ Implementation choice: the adopted amendment read Cossart at the
    single smallest passing position, and the property test in ``tests/test_confirm_rule.py``
    showed that rule lets better evidence give a worse outcome — one more lab cell passing at a
    smaller *J* moved the reading onto a position where Cossart was void, and VIABLE fell to
    NARROWED. Reading over every passing position can only improve as positions are added.
    """
    positions = set().union(*(passing_positions(streams[s]) for s in passing))
    return min(cossart_leak[i] for i in positions)


class Outcome(enum.Enum):
    VIABLE = "VIABLE"
    NARROWED = "NARROWED"
    FAILED_ON_COUNT = "FAILED_ON_COUNT"
    STOPPED = "STOPPED"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True)
class Result:
    outcome: Outcome
    passing_streams: tuple[str, ...] = ()
    cossart: Verdict | None = None
    excluded_groups: tuple[str, ...] = ()
    rerun: tuple[str, ...] = field(default=())
    """Streams whose VOID permits a rerun changing only the instrument whose control failed."""
    reason: str = ""


STREAMS = ("fast", "slow")


GroupBounds = Mapping[str, Mapping[str, Mapping[int, float]]]
"""``{stream: {group: {grid position: leak lower bound at GROUP_ALPHA}}}``."""


def excluded_groups(streams: Mapping[str, Sequence[CellVerdict]], passing: Sequence[str],
                    group_leak_lower: GroupBounds | None) -> tuple[str, ...]:
    """Groups that leak at **every** position where some passing stream passes.

    A group is excluded from a passing stream's claim only when its lower bound is above the
    margin at each of that stream's passing positions — so adding a passing position can only
    remove an exclusion, never add one (the same monotone reading as :func:`cossart_reading`).
    """
    out = set()
    for s in passing:
        positions = passing_positions(streams[s])
        for g, by_pos in (group_leak_lower or {}).get(s, {}).items():
            missing = positions - set(by_pos)
            if missing:
                raise ValueError(f"group {g!r} in {s} has no bound at passing positions {sorted(missing)}")
            if all(by_pos[p] > LEAK_MARGIN for p in positions):
                out.add(g)
    return tuple(sorted(out))


def outcome(streams: Mapping[str, Sequence[CellVerdict]],
            cossart_leak: Sequence[Verdict],
            group_leak_lower: GroupBounds | None = None) -> Result:
    """The run's one outcome.

    ``streams`` maps ``"fast"`` and ``"slow"`` to their three cells, smallest *J* first.
    ``cossart_leak`` is the Cossart folder's leak verdict at its three grid positions.
    ``group_leak_lower`` gives, per stream and group, the leak lower bound at each grid position.

    * **VIABLE** — both lab streams PASS, Cossart passes at some position where a lab stream
      passed (:func:`cossart_reading`), and no group is excluded (:func:`excluded_groups`).
    * **NARROWED** — at least one lab stream PASSES and VIABLE does not hold. The result names
      the passing streams, the Cossart verdict and any excluded group. **A passing stream is
      always reported**, whatever the other stream or Cossart did.
    * **STOPPED** — both streams FAIL and **no** cell in either stream failed only on count, so
      no displacement passed both leak and destruction anywhere. Only this outcome stops the
      goal.
    * **FAILED_ON_COUNT** — both streams FAIL, but at least one cell passed leak and
      destruction and failed only on count. The goal is not stopped: a surrogate exists that
      neither leaks nor keeps coordination, and the fix is one that also keeps counts.
    * **UNRESOLVED** — no stream passes and not both fail. Streams that are VOID are named in
      ``rerun``; an UNDECIDED stream is written up as "not decidable on these data".
    """
    missing = [s for s in STREAMS if s not in streams]
    if missing:
        raise ValueError(f"missing streams: {missing}")
    if len(cossart_leak) != N_DISPLACEMENTS:
        raise ValueError(f"Cossart has {N_DISPLACEMENTS} grid positions, got {len(cossart_leak)}")
    sv = {s: stream_verdict(streams[s]) for s in STREAMS}
    passing = tuple(s for s in STREAMS if sv[s] is Verdict.PASS)

    if passing:
        cossart = cossart_reading(streams, passing, cossart_leak)
        excluded = excluded_groups(streams, passing, group_leak_lower)
        if len(passing) == len(STREAMS) and cossart is Verdict.PASS and not excluded:
            return Result(Outcome.VIABLE, passing, cossart, (), (), "both streams and Cossart pass")
        return Result(Outcome.NARROWED, passing, cossart, excluded, (),
                      "a stream passes; the claim names what it covers")

    if all(sv[s] is Verdict.FAIL for s in STREAMS):
        if any(c.failed_only_on_count for s in STREAMS for c in streams[s]):
            return Result(Outcome.FAILED_ON_COUNT,
                          reason="a displacement passed leak and destruction but lost counts")
        return Result(Outcome.STOPPED,
                      reason="no displacement passed both leak and destruction in either stream")

    rerun = tuple(s for s in STREAMS if sv[s] is Verdict.VOID)
    return Result(Outcome.UNRESOLVED, rerun=rerun, reason="no stream passes and not both fail")
