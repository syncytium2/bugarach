---
status: open
opened: 2026-09-23
area: scoring design, co-modulation
---

# Minute-scale shared change in event rate is background, for now; what it actually is waits

**Important, and deliberately not today's work.** Tony, 2026-09-23: *"lets keep the co-modulation
story in our backpocket for now. flag for followup as important but off target for today's goals.
let's call it background for this purpose"*.

## The working ruling, and what it binds

For the scoring design now being settled (fast, slow and combined alike), **shared change in the
event rate of many ROIs at a minute or more is background, not coordination.** Concretely:

- A detector's call on shared rate change, with no sub-second coincidence behind it, is a
  **false alarm**. The negative recordings and the real-data check are built on that.
- A real-data false-alarm check may use a surrogate that **keeps** minute-scale change and
  destroys sub-second timing: the per-ROI rigid shift, at a *J* of seconds. Measured on all three
  streams, it leaves the minute-scale part in place (#768).

It is a working choice for one purpose. **It is not a finding about the preparation**, and
nothing here may be cited as one. What the shared change *is* stays open.

## Why it is worth coming back to

Measured on the de-pinned default export, 84 recordings from 44 mice
([#768](https://github.com/syncytium2/bugarach/pull/768),
`docs/learned/runs/2026-09-23-comodulation-three-streams/`):

- With CoactDetect's episodes removed, the population onset count varies **2.2–2.5 times** as much
  as it would if ROIs were independent, at 1-minute bins, on every stream (fast 2.36, slow 2.17,
  combined 2.51, after the 120 s block control). At 1-second bins the same arm reads about 1.0.
  So the events live below a second, and the shared change lives at a minute or more.
- Removing the pinned ROIs moved none of it beyond its own interval, so it is not that artifact.

## The follow-ups, in the order they would be worth doing

1. **Is it the preparation or the measurement?** A baseline estimate that drifts moves every
   ROI's detection threshold together, and would produce exactly this with no change in the
   cells; so would focus or bleaching. That is a question for the producer, and no record says it
   has been asked.
2. **Is it something to detect?** If it is a state of the preparation, it may belong in the
   analysis rather than being subtracted. Tony's call, once (1) is answered.
3. **The 10–45 s band** sits between the two timescales and has not been assigned to either.
4. **Three recordings carry their groups**: `20250806_174` (the same one that carried the slow
   jitter group result in #765), `20260702_334` and `20260115_243`. Look at the recordings, not
   the measures.
5. **The 17 September page** still carries a stop notice the re-run has made untrue
   ([ruling queue](../decisions_pending.md), item 9).
6. **A detector that uses the separation**: a sliding population correlogram scoring the peak
   within the stream's jitter against the shoulder beside it (Tony's idea, 2026-09-23).
   CoactDetect is roughly its zero-lag bin against a 60 s local null. It only makes sense while
   the shoulder is background, which is why it waits on (1) and (2).
