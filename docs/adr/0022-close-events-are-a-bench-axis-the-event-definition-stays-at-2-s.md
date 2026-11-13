# ADR-0022: Close events are a bench axis of set separations, below 2 s included; the event definition stays at the 2 s window until the revised export is re-measured

## Status

Accepted, 2026-11-11, by Tony (*"agreed"*, to the recommendation as put to him that afternoon),
with one observation added in the same message: *"by eye separation less than 2s is
detectable"*.

It answers the question that had waited since 2026-10-08
([todo](../todo/2026-10-08-the-stack-ceiling-and-the-short-interval-bench.md), item 1): whether
the revised bench only adds short gaps, or moves the event definition to a narrower window. It
leaves [ADR-0008](0008-the-event-floor-is-set-per-window-from-its-own-null.md)'s 2 s window
standing and adds to [ADR-0010](0010-tune-train-and-review-against-the-data-as-they-are.md)'s
bench; it supersedes neither.

## Context

**The bench plants no two events closer than about 2 s.** Its gaps were measured with events
found as peaks of a count in a 2 s window, and peaks under 2 s apart merged. So every detector's
merge gap was searched on recordings where a long gap costs nothing, and the searches picked 3
to 8 s.

**Close events separate the detectors.** In the controlled test of 2026-10-08
(`tools/measure_close_events.py`, fast stream), planted events 10 s apart leave the detectors
within 0.09 F1 of each other; at 1 s they span 0.40 to 0.66. The merge gap decides it, then the
window.

**The data hold close events, and a narrower window changes what an event is.** Measured in a
0.5 s window, 4 to 6 % of gaps are under 2 s. The same window counts 18.4 fast events per hour
against 9.7 at 2 s, at a median floor of 4 cells against 6: the extra events are small ones
([run record](../learned/runs/2026-10-08-stack-ceiling/README.md)). That measurement ran on the
stopped default folder, on Tony's acknowledgment.

**Small events are where characterization fails.** At each stream's own values, the joint fit
did not recover jitter for events of 3 to 4 cells; it read about twice the planted value
([goal page](../goals/synthetic-validation.md), *Aim 1a at the lab's values*, 2026-11-11). A
bench built on the 0.5 s definition would plant a population the measuring tools cannot yet
characterize.

**A person separates events closer than 2 s.** Tony, 2026-11-11, as quoted above. It is an
expert's observation and not yet a measurement; the rater sheet's separation test (pull request
#916) is the measurement. The derivations agree in direction: from onset times and cell
identity alone, two events could be told apart at 0.26 to 0.76 s at the lab's values, while the
assessor merges them below about 2.5 s and the count detector below about 5 s
([goal page](../goals/synthetic-validation.md), *the minimum separation of two events*).

## Decision

1. **Close events are a difficulty axis, not a measurement.** The bench plants neighbouring
   events at set separations, at the current event sizes, and every detector is scored at each
   separation. No separation is taken from a real gap distribution.
2. **The axis goes below 2 s.** Because a person separates events closer than 2 s, a detector
   that joins such a pair into one call has missed an event, and is scored so.
3. **The event definition stays at the 2 s window** (ADR-0008) for now. Moving it to a narrower
   window is not ruled out: it is decided after the revised export is the default and the gaps
   and floors have been re-measured on it at 0.5, 1 and 2 s.
4. **The axis is one of the difficulty axes of
   [ADR-0013](0013-the-bench-simulates-treatment-periods.md)**, beside its intervals,
   participation and jitter, and it applies to baseline recordings as well as treatment ones.

## Consequences

- **The starting levels are 0.5, 1, 2, 3 and 5 s.** They are a session's choice and may be
  changed without a new ADR; that the axis exists and reaches below 2 s may not.
- **The generator can already do this.** `simulate_coordination(gap_source=, gap_mix=)` sets a
  share of the gaps to one value, and `tools/measure_close_events.py` is that test on the fast
  stream. What is owed is the same test on slow and combined, on the four detectors of the first
  capability map (ADR-0021), through `bugarach.stream_profile`.
- **Merge gaps are searched with close events present.** A search that never sees a pair under
  its merge gap cannot price that gap. The 2026-09-25 search picks predate this and are not
  adopted on it.
- **The pass mark is not set here.** That people separate events under 2 s says a detector
  should; how close, and at what recall, waits for the rater sheet's numbers.
- **What would supersede this:** a ruling, after the re-measurement, that the event is defined
  in a narrower window. That ruling also amends ADR-0008.
