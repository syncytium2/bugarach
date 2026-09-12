---
status: open
filed: 2026-09-12
---

# Joint-ISI dithering is unmeasured, not failed, and the report must say so

Tony ruled on 2026-09-10 that every candidate is measured and none pruned, because nothing predicts in
advance which surrogate is right. Joint-ISI dithering — Gerstein's method, one of the eight — did not
survive contact with the grid.

## What happened

In the run of 2026-09-11, every joint-ISI cell is recorded intractable and dropped before running.
From the discriminator's own metadata and `run_summary.json`, read 2026-09-12: 96 of 197 cossart
records skipped as intractable, with 3 more killed at the time cap; 120 skipped and 2 killed at the
4 GB memory cap on the fast stream; 96 skipped on slow. The skipped lists are joint-ISI cells at every
displacement and both dead-time settings.

The cause is known and was anticipated: joint-ISI dithering needs a per-ROI two-dimensional interval
histogram, and at one frame of displacement those tables run to multiple gigabytes. The cost probe
records the same shape from the other side — joint-ISI is the most expensive generator by a wide
margin, at 73 to 159 seconds per draw on the fast stream where most candidates take one or two.

## Why it needs saying out loud

**An empty result reads like a negative result.** A table with joint-ISI absent, or present with blank
cells, will be read by the next person as "it was tried and it lost". It was not tried. Under a ruling
that nothing is pruned, silently dropping a candidate on resource limits is a pruning decision made by
the machine rather than by anyone.

There is a second, subtler reason. The second review round found that Gerstein's joint-ISI recipe takes
a square root that both Elephant's default and Stella's own runs skip, and that the smoothing width —
not the displacement — decides whether the method moves anything at all. So joint-ISI's parameters are
themselves unsettled. A candidate with unsettled parameters and no measurements is the one most likely
to be quietly forgotten.

## The options, and they are a decision not a task

- **Measure it at feasible displacements only**, and state the range it was measured over.
- **Reduce the histogram cost** — coarser interval bins, or a cap — and declare the approximation.
- **Declare it out of scope**, with the resource reason recorded, which is an honest outcome but is a
  change to the no-pruning ruling and so is Tony's to make.

## Closes when

The report either carries joint-ISI measurements or names it as unmeasured with the reason, and the
no-pruning ruling is either satisfied or explicitly amended.
