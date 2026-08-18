---
status: open
filed: 2026-08-18
revised: 2026-08-18
---

# Do the real recordings have recurring assemblies, or random participation?

**A question about the preparation, small enough to answer in a day, and it gates a
whole family of comparisons.**

> **Revision.** The first draft of this file proposed testing co-participation against
> the assessor's circular-shift null and called the work free. Both were wrong, and the
> first would have returned a confident yes that meant nothing. The question survives
> unchanged; the method below replaces it. Read *The null has to condition on the events*
> before writing any code.

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

## Do the counting pass first

This is the step that decides whether the question is answerable at all, and it comes
before any statistic is written.

Pairs grow as the square of the ROI count; co-participation observations grow only as
clusters x pairs-per-cluster. At tens of clusters and dozens of ROIs, most pairs are
never observed together even once, per-pair tests have no power, and *"not significant"*
becomes indistinguishable from the honest negative this file wants to be able to publish.

So count first, across all 85 baseline slices: clusters per slice, ROIs per slice, median
participants per cluster. If the geometry supports the question, the design is **one
scalar per slice** — dispersion of the pairwise counts, or the leading eigenvalue against
its own null distribution — combined within group. Per-pair significance is not on the
table at this corpus size.

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
