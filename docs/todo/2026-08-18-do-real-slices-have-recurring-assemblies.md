---
status: open
filed: 2026-08-18
---

# Do the real recordings have recurring assemblies, or random participation?

**A question about the preparation, cheap to answer, and it gates a whole family of
comparisons.**

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

## Why it is cheap

The assessor already clusters co-active onsets and records which ROIs took part in each
cluster. What is missing is one statistic over those memberships:

- pairwise co-participation counts across events, against the circular-shift null the
  assessor already builds — the null preserves each ROI's own rate, which is exactly
  what a co-participation count must be corrected for, or the busiest cells look like an
  assembly in every recording;
- and a summary per slice: is participation drawn from a few recurring groups, or fresh
  each time?

No new instrument, no new null, no new human decision.

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
group, a pooled statistic hides it (FOUNDATIONS §9).
