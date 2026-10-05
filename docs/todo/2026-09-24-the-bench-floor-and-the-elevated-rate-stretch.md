---
status: decided
opened: 2026-09-24
area: scoring design, link 1 (ADR-0008); bench
waits_on: nobody
---

# ADR-0008 on the bench: the elevated-rate stretch sets the floor above every planted event

**Decided 2026-09-24 by
[ADR-0009](../adr/0009-the-bench-keeps-its-elevated-rate-test-in-a-recording-of-its-own.md)**
(Tony, *"R1-R5 as recommended"*). Question 1: none of the three options. The stretch leaves every
recording with planted events and becomes a recording of its own, and each recording's floor is
computed over the whole of it. Question 2: events under the floor are "don't care". Built on the
final-parameters night (PR A, branch `bench-adr-0009`). Re-measured there with
`tools/probe_bench_floor.py` on the new generator, 8 seeds × 2 backgrounds × 3 benches, the
planted recordings' floors are **5–8 co-active ROIs on fast, 6–8 on slow and 6–10 on combined**,
inside ADR-0009's expected ranges. The elevated-rate recording's floor is 16–20 on fast and
combined and 8–10 on slow.
The middle planted level is never under the floor on quiet recordings. On busy ones, 63% of fast's
middle-level events and 50% of combined's are under it. The record is
`<darkroom>/bugarach/2026-09-25-final-parameters/065/bench-floor/bench_floor.json`. What follows
is the question as it was put.

Found overnight on 2026-09-24 while implementing ADR-0008 (PR #791, the per-window
event floor). The floor function is built and tested (`bugarach.event_floor`), but applying it to
the bench as the ADR reads puts the floor above what the bench plants. Two questions follow, and
neither is a session's to answer.

## What was measured

`tools/probe_bench_floor.py`: 8 seeds × 2 regimes × 3 benches, at ADR-0008's settings (2 s window,
*J* = 20 s, 1 call per hour, 1,000 draws). Output: `<darkroom>/bugarach/2026-09-24-overnight-floor-coact-chorus/phase1-bench-floor/bench_floor.json`.
Each bench recording is 2,700 s with 32 ROIs.

The floor, in co-active ROIs, and the share of planted events whose participant count falls below it
(those are not coordinated events under ADR-0008):

| bench / regime | planted participants | whole recording (literal reading) | without the elevated-rate stretch | the stretch as its own window | no-coordination recording |
|---|---|---|---|---|---|
| fast / quiet | 3, 6, 10 | **16–17**, 100% below | 5–6, 33% below | inside 18–19, outside 5–6 | 4–5 |
| fast / busy | 3, 6, 10 | **17–18**, 100% below | 6–8, 54% below | inside 18–20, outside 6–8 | |
| slow / quiet | 7, 12, 20 | 8–9, 33% below | 6–7, 0% below | inside 9–10, outside 6–7 | 4 |
| slow / busy | 7, 12, 20 | 9–10, 33% below | 7–8, 13% below | inside 10–12, outside 7–8 | |
| combined / quiet | 4, 8, 13 | **18–19**, 100% below | 6–7, 33% below | inside 20–21, outside 6–7 | 5–6 |
| combined / busy | 4, 8, 13 | **18–20**, 100% below | 8–10, 50% below | inside 20–21, outside 8–10 | |

## Why

The elevated-rate test raises every ROI's rate together for 300 s. That is shared rate change,
which ADR-0006 counts as chance (decision 2), and the rigid shift keeps it, so the null fills that
stretch with large chance coincidences and the recording's floor rises to match. Generated without
the stretch, and otherwise identical, the same recordings have floors of 5–10 co-active ROIs.

## The two questions

1. **How does a bench recording's floor treat the elevated-rate stretch?**
   - **The recording as one window**, as ADR-0008 reads. On fast and combined nothing planted is
     left to recall, so the bench cannot tune anything.
   - **The floor from the recording without its stretch.** The stretch is already scored on its
     own, as the probe's calls per minute.
   - **The stretch as a window of its own.** Its floor, 18–21 co-active ROIs, then applies inside
     it, and the rest of the recording gets its own floor.
2. **What becomes of planted events below the floor?** Even without the stretch, a third to a half
   of the fast and combined events are smaller than chance reaches: the lowest planted level (3
   and 4 participants) always, and the middle level on busy recordings. Options:
   - score them as "don't care", which is the reading the implementation was heading for;
   - change the planted participation levels, which is a bench constant;
   - leave the bench as it is and accept a lower ceiling on recall.

## What was done meanwhile

The overnight brief's stop-gap: Phase 2 tunes with `min_rois` at no less than 3 (no grid offers
2), labelled **"pre-ADR-0008 floor"** in its run record. ADR-0008's floor PR stays open with this
todo as what is left.
