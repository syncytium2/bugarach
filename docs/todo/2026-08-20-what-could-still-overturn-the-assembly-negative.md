---
status: open
filed: 2026-08-20
---

# What could still overturn the assembly negative

**The assembly question is closed** — `docs/assembly_report.md`, with both instruments now
running in this repo. This file exists because the ways it could still be *wrong* were only
recorded in a murderboard run record's residual list, and nobody looks there for work. They
are ranked by how much they would cost if true.

## 1. Modularity cannot see overlapping groups — the main route

Louvain finds a **partition**: every cell in exactly one module. A field of *overlapping*
assemblies — cells belonging to several groups, which is what most of the assembly literature
actually models — can carry real structure that a partition-based method scores at chance.
Both streams' negatives rest on this instrument, so this is the single most likely way the
answer is wrong.

**What would settle it:** an overlap-tolerant method on the same graphs — link communities,
or a mixed-membership stochastic block model. The graphs are already built
(`bugarach.graph.sttc_matrix`), so the cost is the method, not the pipeline.

## 2. The penumbra-subtracted modularity covers slow only

The crosstalk control is complete for the membership instrument in **both** streams, and for
modularity in **slow only** — the interface2 pensub file is a slow-stream file and fast was
never rebuilt. So "the modularity negative survives optical crosstalk" is a slow-stream claim.

**What would settle it:** run `tools/modularity_null.py` against the penumbra-subtracted
store for fast. This is now cheap — it is one command against
`processed_archive/event_store_onset_pensub_revised_2v`, no MATLAB.

## 3. The slow membership test may be anti-conservative at its own geometry

Its false-positive rate came out at **9.1%** (95% interval 5.8–14.1), which does not cover
the nominal 5%; an earlier run of the same design gave 6.6%. Two noisy estimates, both above
nominal. It costs the slow negative precision and not its direction — 36 of 38 is 95% against
a null of at most 14% — but the estimate should be pinned rather than left as a range.

**What would settle it:** more replicates at strength 0 in `tools/assembly_power.py`. The
current design gives one simulated recording per real recording per cell, so the strength-0
row is only ~190 draws.

## 4. The corpus-level port agreement is not exercised by CI

`tests/test_graph.py` certifies the coefficient against a committed fixture, which needs no
store. The **98.7% corpus agreement** is evidence recorded in the report and the run record,
and nothing re-checks it. If the port drifts in a way the fixture does not cover — the window
rule, the active-cell filter, the surrogate scheme — CI stays green.

**What would settle it:** a store-gated test, skipped when `BUGARACH_DATA_ROOT` is unset, that
re-runs a handful of recordings and asserts the verdicts.

## 5. Everything downstream of "the store is the universe"

Filed separately and more urgent than anything above, because it is not about this result:
[`2026-08-19-lab-exclusions-were-never-consulted.md`](2026-08-19-lab-exclusions-were-never-consulted.md).
Every deliverable in this repo takes the onset store as its population, and the lab's
`exclude` column says which recordings are analysable. The assembly work is only where that
was noticed.

## What is NOT open

- **The fast stream is measured.** 3 of 78 above null by the reference, 2 of 78 by the ported
  instrument. It was the open item of the previous round and it is closed.
- **The dead-ROI roster** is a demonstrated no-op for baseline-only work — see
  [`2026-08-19-the-connectivity-pipeline-has-no-owner.md`](2026-08-19-the-connectivity-pipeline-has-no-owner.md).
- **The dependency on interface2** is gone; the instrument runs here.
