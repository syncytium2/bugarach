# ADR-0009: The bench keeps its elevated-rate test in a recording of its own, and ADR-0008's floor applies unchanged

## Status

Accepted, 2026-09-24, by Tony (*"R1-R5 as recommended"*). It covers **tuning and scoring detectors
on the bench** under [ADR-0008](0008-the-event-floor-is-set-per-window-from-its-own-null.md), on the
fast, slow and combined benches. It changes nothing in ADR-0008's rule. It settles how the bench
meets that rule: the two questions left open on #793, and three questions that come with them.

## Context

**ADR-0008 applied to the bench as built leaves nothing to tune on.** Every bench recording carries
a 300 s elevated-rate stretch (`hot_window`, 1200–1500 s in `bench.BENCH_RECORDING`): every ROI's
rate is raised together and nothing is planted inside it. ADR-0006 counts shared rate change as
chance, and the rigid-shift null keeps it. So the stretch lifts the whole recording's floor.
Measured by `tools/probe_bench_floor.py` (8 seeds × 2 backgrounds × 3 benches, #793):

- **Fast and combined:** 16–20 co-active ROIs over the whole recording. That is above every planted
  event, so recall has nothing left to measure. Without the stretch, the floors are 5–10.
- **Slow:** 8–10 over the whole recording, and 6–8 without the stretch.

**Real recordings have stretches too, so the bench's is not an artefact to be scored away.** The
[stretch run](../learned/runs/2026-09-24-elevated-rate-stretches/README.md) found them in baseline
windows in all four groups: 8 of 66 recordings on fast, at 3 × the window's median rate for at least
2 minutes on a 60 s window. They lift a baseline window's floor from a median of 4 co-active ROIs
without the stretch to 7 with it.

**Three ways to treat the bench's stretch were set aside**, each for a stated reason:

- **A floor computed on the stretch alone** (the *stretch floor*). Tony, 2026-09-24: *"it doesn't
  seem fair to give the stretch its own floor. we know we put it there."* A floor that moves because
  the bench knows where the stretch is leaves the detectors unprepared for a real stretch, which
  nobody marks for them.
- **A floor computed with the stretch left out** (the *recording floor*). It uses the stretch's
  known location in the same way.
- **A floor that rolls with the local rate.** It treats every minute-scale rate change as chance by
  construction, adds a span to justify, and lets a burst raise its own reference. Tony's reading was
  that it is "more fussing in the methods".

**Detectors already carry the rolling part themselves.** CoactDetect, LoCo and rate+context
threshold against a rolling context of 60–120 s. chorus_norm and chorus_gain_norm standardise each
cell over the span they are given, and need about 100–200 s of it
([the span sweep](../learned/runs/2026-09-24-chorus-span-sweep/README.md)). How a detector copes
with a stretch is therefore a property of the detector, and the elevated-rate test is where it is
measured.

## Decision

1. **The elevated-rate test moves into a recording of its own (R1).**
   - Recordings with planted events carry no elevated-rate stretch. That applies to
     `BENCH_RECORDING` and to every recording built from it (`CROWDED_RECORDING`, `TAIL_RECORDING`).
     Their span 1200–1500 s carries ordinary background.
   - A separate **elevated-rate recording** has the stretch and no planted events. Its floor comes
     from its own null by ADR-0008's rule, like every other recording. It is scored only for calls,
     against the existing budgets: `MAX_PROBE_PER_MIN` inside the stretch, and
     `MAX_FALSE_POSITIVES_PER_HOUR` outside it, where it is a recording with nothing planted.
   - No recording's floor is computed with any part of it left out.
2. **Planted events below the floor are "don't care" (R2).**
   - A planted event with fewer participants than its recording's floor is neither a hit nor a
     miss: it leaves the recall denominator.
   - A call matched to one is neither a true nor a false positive: it leaves precision.
   - Their number is reported with every score, by participation level.
3. **ADR-0008 sets SPIKE-synch's `min_n` (R3).** `min_n` is SPIKE-synch's minimum number of events in
   a call, which is a participation minimum. ADR-0008 decision 6 covers any detector whose minimum
   the floor sets, so `min_n` leaves the search grids with `min_rois`.
4. **The budgets stand as written (R4).**
   - `MAX_FALSE_POSITIVES_PER_HOUR`, `MAX_PROBE_PER_MIN`, `MAX_PRECISION_DROP` and `MAX_CROWDED_DROP`,
     in each bench file, and any gate the search already applies.
   - A proposal that fails one is not adopted.
   - A limit is not loosened to let a result through; changing one takes its own ruling.
5. **No context longer than 120 s is searched (R5).**
   - The context grids of CoactDetect, LoCo and rate+context run 20, 30, 45, 60, 90 and 120 s.
   - 120 s is already the bench's own cap (`context_fits_the_null`, with planted events 120 s
     apart), and Tony is not interested in longer ones.
   - The shorter values let a search find a short context where one works.

## Consequences

- **The bench can be tuned under ADR-0008.** Recordings with planted events get floors of 5–10
  co-active ROIs on fast and combined and 6–8 on slow (the probe's numbers without the stretch).
  Those numbers are measured with the old generator and will be re-measured on the new one.
- **Some planted events drop out of scoring.** Even without the stretch, the lowest planted level
  (3 participants on fast, 4 on combined) is under the floor, and on busy recordings so is part of the
  middle level. That is a third to a half of fast and combined events. Recall is then measured on the
  events chance does not reach, which is what ADR-0008 defines as an event.
- **The elevated-rate test partly measures the floor.** Its recording's floor is lifted by the
  stretch, like a real window's, so a detector that honours the floor makes few calls there by
  construction. The test still separates detectors by what they call above that floor, and it
  measures the whole system a real stretch would meet.
- **Every tuned number before this ADR is pre-ADR-0008**, including the 2026-09-24 overnight
  proposals, and is re-searched rather than adopted.
- **The chorus models are retrained.** Their training recordings change with decision 1.
- **Changing any of this takes a new ADR** that supersedes this one.

## References

- #793: the floor module and `tools/probe_bench_floor.py`, and the two questions this ADR answers.
- The stretch run: `docs/learned/runs/2026-09-24-elevated-rate-stretches/README.md`.
- The chorus span runs: `docs/learned/runs/2026-09-24-chorus-context-span/README.md` and
  `docs/learned/runs/2026-09-24-chorus-span-sweep/README.md`.
- ADR-0006 for what counts as chance, and ADR-0008 for the floor.
