---
status: open
filed: 2026-08-24
---

# Does the ISI-adaptive window ever shrink below the frame interval?

**The question, in one line:** SPIKE-synch's coincidence window τ is the minimum
of the four half-ISIs around a spike pair. If those ISIs get short enough, τ drops
below the imaging interval — and the measure starts resolving time differences the
camera never recorded.

**Nobody has looked.** This is a measurement, not an argument, and it is cheap.

## Why it comes up now

The Satuvuori 2017 **minimum relevant time scale (MRTS)** is a floor under exactly
this: a declared scale below which differences are not treated as resolvable. It is
cSPIKE's `threshold` argument, **interface2's wrapper passed it as 0**, and so this
lineage has run with no floor at all since the beginning. That was invisible while
"adaptive" was one undifferentiated word; naming the two apart
([GLOSSARY](../GLOSSARY.md), fork #11) made the gap visible.

**It may well be nothing.** These are calcium event onsets at 10 Hz, not cortical
spike trains — the events are sparse, ISIs are seconds, and τ is capped at 0.25 s
(FAST) / 0.5 s (SLOW) from above. The floor question is whether anything reaches
the *bottom*.

## The measurement

Over the approved export folder, per stream, per recording: for every spike pair
that `adaptive_profile` evaluates, record the τ it used. Then ask:

1. **What fraction of τ values fall below the frame interval** (0.1 s at 10 Hz)?
2. **Where do they come from** — a handful of bursty ROIs, or everywhere?
3. **Does it touch detections?** τ below the frame interval makes coincidence
   *harder*, so the effect would be missed events, not false ones. Compare
   `sync_detect` output against a run with τ floored at the frame interval.

`adaptive_profile` does not currently return τ, so step 1 needs a debug path or a
reimplementation of the four-half-ISI rule in the analysis script — small either
way, and the second is arguably better because it is an independent check of the
rule.

## What each answer means

- **Fraction ~0** — the question is closed, MRTS is irrelevant to this
  preparation, and that is worth one sentence in the methods rather than a
  parameter. **This is the expected outcome.**
- **Fraction small but detections move** — then the floor is a real parameter and
  belongs in the fork table beside `tau_mode`, defaulting to *no floor* to keep
  parity.
- **Fraction large** — then a chunk of what SPIKE-synch reports is being decided
  below the resolution of the instrument, and its operating point was fitted in
  that regime. That would be a finding about the detector, not a tuning note.

## Do not implement MRTS to answer this

Measuring τ needs no new mode. Implementing the Satuvuori extension to find out
whether it is needed is backwards, and it would be a mechanism change landing
ahead of the evidence for it — [RESET §7](../RESET.md) puts mechanism behind
measurement for exactly this reason.
