# ADR-0021: The toolset is general and is validated on synthetic data first, with the coded detectors

## Status

Accepted, 2026-10-22 and 2026-10-23, by Tony. **Backfilled 2026-11-11**, when
[ADR-0020](0020-one-route-from-a-folder-to-calls-per-stream.md)'s route first leaned on these
rulings. Until then they lived in a handoff
([`todo/2026-10-23-handoff-synthetic-validation.md`](../todo/2026-10-23-handoff-synthetic-validation.md),
which holds his words in full) and in the *Settled* table of
[`goals/synthetic-validation.md`](../goals/synthetic-validation.md). Nothing here is new; where
this record and those two disagree, they are the source and this is the error.

## Context

Until 2026-10-22 every tuning and comparison in this repository was aimed at this lab's
recordings, with one kind of planted coordinated event. Tony, 2026-10-22: *"Treat the bugarach
project as a general toolset not specific to our data. Underlying premise is not one but two or
more sources of coordinated events."* The same message set the loop (measure, simulate, tune a
few detectors, characterize, then run on the original data) and the first step: *"validate the
approach with purely synthetic data … to determine what each detector is best at."*

The default folder had been stopped for a known contamination since 2026-10-05, so a step that
needs no real recording was also the only one available.

## Decision

1. **bugarach is a general toolset.** Its input is a multichannel stream of unlabelled event
   times. The lab's export contract is one producer's contract, not the general one.
2. **The v0.1 input is per-channel onset times plus the recording's duration.** The frame
   interval is optional and inferred when missing. Amplitude and width are v0.2 (2026-10-23).
3. **The approach is validated on synthetic data before the real-data run**, against known
   truth, and the output is what each detector can do, condition by condition. It is not a
   ranking.
4. **The premise is two or more sources of coordinated events**, each with its own
   participation, jitter, intervals and membership. Membership is a grid axis: a source has
   fixed members or recruits at random, and both are simulated (2026-10-23).
5. **Coded detectors only; the learned models are on hold** (2026-10-22).
6. **The first capability map has four detectors**: CoactDetect, LoCo, binned SCE and count
   (sliding). The others join once the grid is sized (2026-10-23).
7. **The current export supplies realistic parameter values only, never truth** (2026-10-22:
   *"our existing flawed data"*).
8. **Compute is WSMIP065** (2026-10-23).

## Consequences

- A recovery or capability result names its generator, and a claim about the lab's recordings
  waits for the real-data run.
- Measured numbers from the lab's folder may sit in the tree; recordings and per-recording
  figures may not (FOUNDATIONS §5).
- The negatives this work scores against are ADR-0019's, and the tool that makes them is owed.
- ADR-0020's route applies decision 3 per stream. Decision 4's second source is not in the
  generator yet, and whether it is built before the one-source route is rehearsed is open
  there.
- Taking the learned models off hold, or adding a detector to the first map, is a new ruling
  recorded as an ADR that amends this one.
