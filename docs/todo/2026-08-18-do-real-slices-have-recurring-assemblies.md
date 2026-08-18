---
status: open
filed: 2026-08-18
revised: 2026-08-18
---

# Do the real recordings have recurring assemblies, or random participation?

**A question about the preparation, small enough to answer in a day, and it gates a
whole family of comparisons.**

> **Revision 2 — the power question is now measured, not argued.**
> `tools/assembly_power.py` plants assemblies of known strength at this corpus's own
> geometry and reports how often the test finds them. Two results change what follows.
> **The event-conditioned null cannot be run alone**: it goes blind exactly where the
> signal is purest. And **the corpus is well powered after all** — the arithmetic in
> revision 1 that made it look hopeless was the wrong intuition. Read
> *What the corpus can actually see* before writing any measurement code.
>
> *Revision 1 replaced the original method, which tested co-participation against the
> assessor's circular-shift null and called the work free. Both were wrong, and the first
> would have returned a confident yes that meant nothing.*

## Why it came up

Tony pushed back on a claim that no literature detector was in our comparison — rightly:
CICADA is the Cossart lab's, ported here, and SpikyDetect runs on cSPIKE/PySpike's
synchrony profile. The question that followed — *which detector would you add* — has a
prerequisite nobody had noticed.

**Our generator draws every planted event's participants at random**
(`simulate.py`: `rois = rng.choice(nR, size=np_, replace=False)`). So the corpus has
coordinated *events* and no cell *assemblies* — no group that recurs. The entire
assembly-detection literature (ICA/PCA, CAD, graph methods, item-set mining) finds
recurring co-activation patterns, so on this corpus it finds nothing, and the zero would
be a fact about our generator rather than about those methods.

## The question

**Across the 85 baseline recordings, do the same cells tend to participate together
across events — and by how much more than chance?**

The measurement is on the real recordings throughout. The generator appears twice below,
once as the thing the answer would change and once as a name for the hypothesis being
tested. Neither is a reason to run this on simulated data.

## The null has to condition on the events

The assessor's circular shift moves each ROI's train independently, so it destroys every
trace of cross-ROI timing. Under it, co-participation sits at chance — and these
recordings are coordinated, which is the one thing about them we already know and which
survives even TTX (FOUNDATIONS §9). So every pair that appears together in a coordinated
event clears that null, on essentially every slice. The test returns a resounding yes,
the yes means *"these recordings are coordinated"*, and read as *"assemblies recur"* it
walks directly into the trap the last section of this file warns about.

**Condition on the events instead.** Hold the observed cluster times and each cluster's
participant count fixed, and redraw *which* ROIs took part — preserving each ROI's own
total participation count, so the busiest cells cannot manufacture an assembly. A
margin-preserving shuffle of the event x ROI membership matrix (curveball / swap
randomization) does this directly; the eigenvalue-against-Marchenko-Pastur route from the
Lopes-dos-Santos and Peyrache line answers the same question with a different instrument
and is worth running as a cross-check rather than a replacement.

That null is exactly the assumption `rng.choice` makes. So the test on real membership
reduces to *"do these recordings depart from uniform participation"* — which is the
decision the answer feeds, stated as a hypothesis.

## What it actually costs

Small, but not free, and the first draft's "no new instrument, no new null" was wrong on
both counts.

- **Membership is not recorded anywhere.** `_clusters` in `src/bugarach/assess.py`
  returns onset SD, participant *count*, peak coactivity and span. It gathers each
  participating ROI's nearest onset and then keeps only the times — the ROI index is
  discarded inside the loop. There is nothing yet to count co-participation over.
- **That function is on the parity path**, running against a 1e-9 MATLAB reference and
  called once per surrogate per K. Add membership additively — an optional return, or a
  sibling function that shares the clustering — and do not reshape what is pinned.
- **The corrected null reuses none of the assessor's surrogate machinery.** It is a new
  randomization over a new matrix. The clustering is what gets reused, not the null.
- **Both nulls and both statistics already exist** in `tools/assembly_power.py`, written
  against simulated membership and validated there — margins conserved exactly, size
  correct at 0.05, positive control passing under the null that has one. Measuring the
  real corpus is wiring real membership into them, not writing them.

## What the corpus can actually see

**Measured, not estimated** — `tools/assembly_power.py`, figure `assembly_power` in the
darkroom. It plants an assembly of known size and known strength at the median slice
geometry the derived spec already records (`docs/learned/generator_spec.json`, medians
over all 85 baseline slices: **32 ROIs**, **21 clusters** at K=3 over a 59-minute window,
**4.5 participants** each) and counts how often the test rejects. Membership is simulated
directly — no onsets, no detector, no operating point — so it runs on a bare clone with no
`BUGARACH_DATA_ROOT`.

### The corpus is well powered, and revision 1's arithmetic was misleading

496 pairs share about 165 co-participation observations, a third of an observation per
pair, and revision 1 read that as fatal. It is not. **An assembly concentrates counts
rather than spreading them**, and concentration is what the statistic measures. At the
median geometry, against the uniform null:

| assembly | detected in one slice | detected across a group of 20 |
|---|---|---|
| 4-8 cells | from ~1 event in 6 (power 0.37-0.64) | from ~1 event in 10 (power 1.00) |
| 12 cells | from ~1 event in 4 (power 0.45) | from ~1 event in 5 (power 1.00) |
| 16 cells — half the field | needs half the events (0.67) | from ~1 event in 4 (power 0.80) |

So a negative result from this corpus would be worth publishing: it would exclude compact
recurring assemblies recruiting more than about a tenth of coordinated events. Both nulls
sit at their nominal 0.05 when nothing is planted.

### The event-conditioned null goes blind at full strength

The null revision 1 argued for — hold event times and sizes fixed, preserve each ROI's own
participation total — **loses all power exactly where the assembly is purest**. At full
strength the non-members never participate at all: 24 of 32 ROIs have a column sum of
zero, the entire signal has moved into the margins the null conditions on, and the
observed statistic lands on the null mean. Power rises to 1.00 and then falls back to
chance, so it is not monotonic in the quantity being measured — the shape a positive
control exists to catch, and the failure mode
[`2026-08-16-promiscuity-probe-cannot-fail.md`](2026-08-16-promiscuity-probe-cannot-fail.md)
records in another guise.

**So run both nulls.** The companion fixes event sizes only and redraws participants
uniformly, which is exactly what `simulate.py` does; it is monotonic and passes the
full-strength control, but it also fires on plain rate heterogeneity. Neither is
sufficient alone and the pair is interpretable:

- **both fire** — structure beyond what per-cell participation rates explain;
- **uniform only** — read the participation counts before claiming an assembly; it may be
  a few busy cells, or an assembly so sharp the conservative null cannot see it;
- **neither fires** — no assembly above the strengths tabled above.

### What is still worth counting on the real store

The spec's medians are enough to size the test, not to run it. When the store is mounted:
the per-slice *distribution* of ROI count and cluster count, since a slice well below the
median may be individually unpowered and should be reported as such rather than as a
negative.

## Why the answer matters either way

- **If assemblies recur:** the generator should plant them, our benchmark is currently
  unable to reward membership structure, and PCA/ICA assembly detection becomes the
  obvious first literature port — a genuinely different principle from our six, which
  are all variations on "more coincidence than the local background explains".
- **If participation is random event-by-event:** the assembly family is simply not the
  right comparison for this preparation, the generator is right as it stands, and that
  is a publishable statement about the biology rather than a gap in our benchmark.

## What must not happen

Do not port an assembly detector first and report its score. On today's corpus it will
lose, we will have "beaten" a respected method by testing it on data built to contain
nothing it looks for, and the first reviewer to notice will be right.

## Constraints

Baseline recordings only, as always — participation properties must not be taken from
senktide or TTX windows. And group-dependence applies: if assembly structure differs by
group, a pooled statistic hides it (FOUNDATIONS §9). With 85 slices split across groups,
the per-group n is around twenty, which is another reason the per-slice scalar is the
unit and not the pair.

Two more that bite this measurement specifically:

- **The dead-ROI store is cleaned asymmetrically** — 67 of 85 slices carry a verdict and
  the other 18 keep every ROI (FOUNDATIONS §9). A membership statistic is directly
  sensitive to which cells are in the matrix, so record per slice whether it was judged.
  Pooling the two silently would put the answer at the mercy of the exporter's coverage.
- **This needs the real store mounted** — `BUGARACH_DATA_ROOT`. Nothing here runs on a
  bare clone.

## What this does and does not block

It gates the assembly family only. The nearest neighbouring item — clean-rooming the
Molter coactivity frame gate, recommended in
[`2026-08-17-run-a-literature-method-on-our-corpus.md`](2026-08-17-run-a-literature-method-on-our-corpus.md)
— detects population *events*, not assemblies, so it is unaffected by how this falls and
remains the better move if a published-method comparison is wanted sooner.
