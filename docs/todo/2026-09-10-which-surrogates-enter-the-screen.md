---
status: done
filed: 2026-09-10
closed: 2026-09-10
---

# Which surrogates enter the screen, and does it run as a grid

> **RULED IN FULL, 2026-09-10.** Tony answered all three questions below.
>
> - **All eight candidates enter, none is pruned.** *"My read of Stella figure 10 is we need to do
>   all of them. You can't predict a priori which one is right."*
> - **The tiers with a pooling operator run as a grid.** *"02 grid sounds like all are compared, if
>   so agreed."* It does mean that: a grid measures every candidate under every setting of the other
>   factors, so interactions show; contests would test each candidate alone.
> - **Stella does not retire candidates** — it removes the grounds for retiring any.
>
> What follows is planned in
> [`proposals/2026-09-10-surrogate-evaluation-overnight.md`](../proposals/2026-09-10-surrogate-evaluation-overnight.md),
> which turns the screen into a per-dataset tool step and adds Stella's three missing candidates.

An eleven-role review on 2026-09-10 killed the surrogate a proposed self-supervised detector was
built on — independent per-onset dithering, which is separable cell-by-cell on this project's own
recordings. Full account:
[`docs/reviews/2026-09-10-coordination-without-labels_2026-09-10.md`](../reviews/2026-09-10-coordination-without-labels_2026-09-10.md).

Tony, 2026-09-10: *"why pick one replacement? we have compute to test all of them."* So the
replacement is a **screen**, not a choice — the same shape as the tube 2×2, which was built to be
measured rather than argued about.

## The candidate set

| candidate | preserves | why it is in | origin |
|---|---|---|---|
| circular shift | circular ISI multiset | the incumbent; four of the six hand-written detectors use it | this repo's assessor null |
| **uniform per-onset dither** | rate only | **the KNOWN-BAD positive control.** A screen that fails to flag it is broken | Date, Bienenstock & Geman 1998 lineage |
| rigid shift, no wrap | ISIs exactly, no splice | the cheap repair to the splice objection | Pipa et al. 2008 |
| dither with dead-time | rate + a declared floor τ | minimal fix to the killed one | Stella et al. 2022 |
| joint-ISI dither | the ISI pair distribution | preserves interval pairs | Gerstein 2004; extended by Louis et al. 2010 |
| pattern jitter | each event's recent history, exactly | the one to beat | Harrison & Geman 2009 |
| interval / window jitter | per-window counts | conditional inference on fixed windows | Date, Bienenstock & Geman 1998; reviewed in Amarasingham et al. 2012 |
| operational-time dither | the rate profile under drift | aimed at the drift problem | Louis, Gerstein, Grün & Diesmann 2010 |

The shelf at `<darkroom>/bugarach/lit/surrogates/` holds all of these but Gerstein 2004 and Pipa 2008.

**Stella's surrogate implementations ship in Elephant** (BSD-3); the code there descends from
theirs, and their paper ran version 0.10.0. Read and run 2026-09-10 at version 1.2.1: it carries
uniform dither, dither with dead time, the rigid shift, joint-ISI dither and interval jitter — **five
of these eight** — plus ISI dithering, window shuffling and trial shifting, the three Stella
candidates this list lacks. Circular shift is ours; pattern jitter and operational-time dither are
not in it. ⚠ Its uniform dither and shift **drop** onsets pushed out of the window (or clamp them
with `edges=False`); its dither with dead time never drops, confining each onset between its
neighbours; its trial shifting **wraps** within each trial. Every default is millisecond-scale, and
several failures are silent — the overnight plan lists them.

## What had to be decided

1. ~~**Which candidates run.**~~ **RULED: all eight.** Dropping the uniform dither was never
   available — it is the control that proves the screen can fire — and nothing now supports
   dropping any of the others either.
2. ~~**Grid or independent contests.**~~ **RULED: grid**, for the tiers that have a pooling
   operator. [`the four variants of the tube`](2026-08-23-four-variants-of-the-tube.md) says in
   terms that variants "are not a race" — the guard only paid once the bar was multiplicative —
   and surrogate choice may interact with the pooling operator and with *J* the same way. **The
   counting tier has no pooling operator**, so it compares every candidate at once without one; the
   grid binds from the per-cell discriminator onward.
3. ~~**Whether Stella et al. 2022 already answers part of it.**~~ **RULED — in the opposite
   direction from the one anticipated.** It does not retire candidates; it removes the grounds for
   retiring any.

## What Stella settles

**Read the figure, not the conclusion** — this is our reading of figure 10, set against the
authors' own summary. Stella ran six surrogates through SPADE on the same monkey recordings. On
simulated data with ground truth, uniform dither produced a large false-positive count, and dither
with dead time some on Gamma data only; the other four behaved. On the *real* recordings — no ground
truth — the five non-UD surrogates returned overlapping but non-identical sets of significant
patterns, each with its own signature of extras. Read from figure 10 (left column, monkey N) and
checked against the results section: **one epoch out of six is unanimous.** UDD adds an SGHF pattern
nobody else finds in three epochs — early delay, late delay and hold — and shares one with TR-SHIFT
at the start; JISI-D and ISI-D move together; WIN-SHUFF has its own PGLF in early delay. Monkey L
agrees more: three epochs are unanimous at zero patterns, and four of five agree in late delay.

**Uniform dither sits an order of magnitude above all of them** on those recordings — figure 10
gives it its own y-axis, and the results text reports 203 and 121 patterns for the two monkeys
against 7 to 14 for every other surrogate. Stella set it aside as putative false positives, which is
why it is absent from the comparison above.

⚠ **The discussion summarizes more agreement than the figure shows.** It says the five valid
surrogates *"show almost identical participating neurons, lags, and occurrence numbers"* and reach
*"an almost identical significance level."* The figure-10 results describe per-surrogate extras in
five epochs of six for monkey N. **Anyone citing Stella for "surrogate choice barely matters" is
citing the summary, not the result.**

**Their TR-SHIFT recommendation is a tiebreak, not a performance claim** — Tony's read, and the text
bears it out. The first of the five reasons given is that it *"is easy to explain and to
implement"*; the others are that it *"reflects more closely the hypothesis of temporal coding"*,
*"reproduces exactly the most relevant statistical features of a spike train"*, *"is as
conservative as the other methods"*, and *"employs fewer parameters than the other techniques with
the same performance."* It rests on the equivalence premise, and figure 10 is what undercuts that
premise. So TR-SHIFT missing the movement-epoch pattern the other five find — *"in all surrogates,
but TR-SHIFT"* — is not a contradiction of the recommendation; it is one of the disagreements the
summary smooths over. The same discussion says, shortly after, that the choice *"has to be done
appropriately and cautiously case by case"* — which is the ruling above.

Two things transfer regardless:

- **Stella's false-positive counts corroborate uniform dither's defect** under a completely different
  analysis. The defect itself is older: Gerstein (2004) described flat dither adding short intervals
  to the interval histogram, and Platkiewicz, Stark & Amarasingham (2017) built cases where
  spike-centred jitter manufactures temporal structure. That is
  [our own leak finding](../reviews/2026-09-10-coordination-without-labels_2026-09-10.md) with its
  lineage.
- **Stella describe TR-SHIFT as a per-neuron rigid displacement applied trial by trial**, and allow a
  "trial" to be a long spike sequence separated by long silences — so it can run on continuous
  baselines through pseudo-trials, and it joins the screen. Elephant's implementation wraps within
  each trial, which makes it a close cousin of the circular shift rather than of our no-wrap shift.

## Closes when

**Closed by the rulings above, 2026-09-10.** Next is the overnight run, which waits on Tony's go:
[`proposals/2026-09-10-surrogate-evaluation-overnight.md`](../proposals/2026-09-10-surrogate-evaluation-overnight.md).
