# Cell assemblies: the answer, in one page

**Question.** In our slices, bursts of activity recruit a handful of cells at a time. Are
they the **same** cells each time — recurring cell assemblies — or a fresh draw?

**Answer. No recurring assemblies, in either stream, and the absence is the result.** Two
instruments agree, and both have now reported on both streams. Graph modularity on the
spike-time-tiling graph — each recording against its own jitter surrogates — finds **no
partition above its null**: 2 of 78 fast recordings and 1 of 77 slow, against the ~5% the
test's own threshold yields by chance. The membership test finds participation is **not
uniform** — some cells are in most events, many in few — in 45 of 47 testable fast recordings
and 36 of 38 slow. Uneven participation with no modular partition is a **core–periphery**
field, not an assembly: a busy core and a long tail, with no membership that repeats as a unit.

The median recording is in fact *less* modular than its own surrogates (z = −1.17 fast, −3.45
slow): scramble the timing while holding the graph's size, event counts and sparsity fixed and
it scores **higher**. That is the opposite of what a field of assemblies would do.

**Drop the word "assembly"** for this preparation unless the modularity result is overturned.

Both instruments now run **in this repo**. The modularity half used to be computed by an
interface2 pipeline that has no maintainer and does not run out of the box; it was ported
here and validated two ways — exact reproduction of the reference on identical inputs
(worst disagreement 2 × 10⁻¹⁶), and **98.7% verdict agreement across the corpus under a
different windowing convention**, which is the more reassuring of the two.

![A · a real recording's membership table beside a generated one at the same geometry with participants drawn uniformly at random — the question cannot be settled by eye. B · power under the decision rule the corpus is actually scored by, at each real recording's own geometry, one curve per planted group size; the dotted line marks the 5% size of the test, where every curve begins when nothing is planted. C · the verdict before and after optical crosstalk is removed, paired on the fast and slow recordings testable in both stores; the grey bar counts recordings that fell below the testable floor, which is lost power and not a negative.](assembly_closed)

The other instrument, and the one that makes this a negative:

![A · every recording's modularity against its own jitter surrogates, in null standard deviations; the dotted line is zero, and the highlighted marks are those clearing the 95th-percentile threshold the test uses. B · the rate of those in each stream, against the 5% chance produces.](assembly_modularity)

## Why you can believe it

Two objections decide this, and both were tested rather than argued.

**Could the test have failed?** Yes. Scored under the exact rule the recordings are scored
by — two statistics Bonferroni-corrected within each of two nulls, one decision per
recording — and evaluated at **each real recording's own geometry** rather than at a median
slice, the test fires on **6.0%** of fast recordings when nothing is planted (95% interval
3.6–9.8%) and **9.1%** of slow (5.8–14.1%), against a nominal 5% — the fast figure covers it,
the slow one does not, so the slow test looks mildly over-eager and its negative is the less
precise of the two. ⚠ Plant a four-cell group recruiting one event in four and it fires on
**91%** of fast recordings. So a negative here is a measurement, not a shrug. An earlier power curve had scored
a *looser* test than the one that produced the answer; correcting that is what closed this
question.

**Is it just optical crosstalk?** Partly, and not mostly. Neighbouring cells share signal, so
they co-participate for reasons that are not biology — and **no reshuffle can remove this,
because the artifact is already in the table being reshuffled.** Rebuilding the tables from
the penumbra-subtracted recordings and pairing the verdicts: the departure survives in **22
of 26** fast and **21 of 25** slow. All nine recordings that changed moved the same way, and
they come from nine different animals rather than one preparation counted twice (sign test
p ≈ 0.004; neither stream reaches significance alone) — so crosstalk **inflates the effect
without accounting for it**.

**Two recordings the lab had marked unusable were inside every number this work previously
reported**, in a workbook column no part of the analysis had ever opened. They are dropped
here. Nothing about the answer changed; several counts did. ⚠

## What this changes

- **The event generator is right as it stands.** It draws participants uniformly at random,
  which is a faithful model of this preparation. **Do not plant assemblies in it** — an
  earlier version of this work recommended exactly that, and on this evidence it would make
  the benchmark *less* faithful.
- **Do not port an assembly detector to score it on our corpus.** It would lose on membership
  recovery, and it would lose because the tissue has no membership to recover. That is a fact
  about the preparation, not a result about the method.
- **A previously claimed difference between experimental groups is withdrawn.** Planting the
  *same* assembly at each group's median event count reproduces the whole gradient — it was
  detection power, not biology.

## What it does not settle

**Modularity cannot see overlapping groups**, which is now the main route by which this
negative could still be wrong, in either stream. The penumbra-subtracted modularity run covers
slow only. Core–periphery is the reading that reconciles two measurements, **not a fitted
model**; nothing here tests it against alternatives. Penumbra subtraction removes an *estimate* of
optical overlap, so a residual is evidence the estimate was incomplete as much as evidence
the coordination is real. Modularity handles overlapping groups badly, so a field of
overlapping assemblies could evade it. And 36 of the 83 analysed recordings never reached the
test at all — too few coordinated clusters — and are reported as **undefined, never
negative**.

Full detail, every number and every caveat: **the assembly report**, beside this file.
