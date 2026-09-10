---
status: open
filed: 2026-09-10
---

# Four recordings carry a known motion-correction contaminant that no column flags

> **In or out of training — Tony's call**, and it needs the producer's view.

## What it is

[`current_export.toml`](../../current_export.toml), under `steps_excluded`, carries the producer's
own caveat: non-rigid motion correction **pinned 12 ROIs to the frame floor** across four
recordings. The note says in terms: *"Not flagged in any column."*

All four are inside the senktide/TTX cohorts — the exact 67 recordings a self-supervised detector
would train on.

## Why it bites this work specifically

A frame-floor-pinned ROI is a **cross-cell artifact**: several cells driven to a common value by the
same registration failure. A surrogate-contrastive objective is trained to find precisely
cross-cell structure that a rate-matched null cannot explain, so it is rewarded for finding this.

That is the same mechanism as the field-step problem, which the producer *did* fix — and which the
proposal correctly named as a precondition. This one has no such fix and no flag, so it is invisible
to any consumer that trusts the columns.

⚠ **Do not filter it here.** *"The export folder is the input. The store is closed."* Which
recordings are analysable is the producer's call, already applied; going around that rule cost a
real error once and Contract revision 6 records it. If a folder looks like it contains something it
should not, that is **a conversation with the producer**, not a filter in the consumer.

## What to ask the producer

- Should those four be withdrawn from the export, or is the pinning tolerable for analysis?
- If tolerable, can the affected ROIs be **flagged in a column** so a consumer can see them, the way
  field steps were?
- Is the pinning per-ROI for the whole recording, or windowed?

## Closes when

Either the producer withdraws or flags them, or Tony rules that they stay unflagged and the decision
is recorded where a training run would read it.
