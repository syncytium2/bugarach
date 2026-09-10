---
status: open
filed: 2026-09-10
---

# τ, the dead-time floor, is the producer's number and nobody has asked for it

> **Blocked on the producer, via Tony.** Cheap to answer, and it gates a surrogate design.

## What τ is

The minimum interval between two onsets of the **same** ROI that the producer's event extractor can
emit. It is a property of that extractor — a calcium transient has a rise and a decay, and two
onsets cannot be resolved inside one — so it belongs to whoever built the extraction stage, exactly
the way `width_def` does under [`export_folder_spec.md`](../export_folder_spec.md).

## Why it matters now

A murderboard on 2026-09-10 measured, on the senktide baseline windows, that real within-cell
intervals bottom out at **0.40 s (fast)** and **3.20 s (slow)** and never go below. An independent
per-onset dither has no such floor, so it manufactures intervals that are *impossible* under the
real data — a support difference, which let one hand-picked count separate real from surrogate at
AUC 0.647 using no cross-cell information at all. That is what killed the proposed detector:
[`the run record`](../reviews/2026-09-10-coordination-without-labels_2026-09-10.md).

Any repaired surrogate that respects a dead time needs τ **declared, not fitted**. Fitting it to the
observed minimum is circular — the observed minimum is a sample statistic of the very thing the
surrogate is trying not to violate, and it will drift with recording length and firing rate.

## What to ask

- Is there a **hard** refractory/merge parameter in the extractor, and what is its value?
- Is it **per stream** (the fast and slow observed floors differ by nearly an order of magnitude) and
  per acquisition rate?
- Is it a hard floor or a soft one — i.e. can two onsets ever land closer, and under what condition?

## Do not

Do **not** derive τ from the data and write it into the code as a constant. ⚠ Deriving a quantity
the producer owns is the defect FOUNDATIONS §7 and sapper **SAP012** exist to stop — the same shape
as `rise_durations()` recomputing a producer's truncation a layer too late.

## Closes when

τ is stated by the producer, per stream, and recorded — in the export contract if it belongs there,
otherwise beside the surrogate that consumes it.
