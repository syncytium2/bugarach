---
status: open
filed: 2026-09-10
---

# Which surrogates enter the screen, and does it run as a grid

> **RULED IN PART, 2026-09-10.** Tony read Stella et al. 2022 fig. 10 and answered the first and
> third questions below: **all eight candidates enter, none is pruned.** *"My read of Stella
> figure 10 is we need to do all of them. You can't predict a priori which one is right."*
> **Still open: grid or independent contests** — and the ruling makes that the question that
> now matters, because eight surrogates crossed with a per-stream *J* and a pooling operator is a
> far larger product than two or three survivors would have been.
>
> The reading behind it is in [§What Stella settles](#what-stella-settles) below, and laid out
> with figures in [`docs/learned/surrogate_field_ruling.html`](../learned/surrogate_field_ruling.html).

An eleven-role review on 2026-09-10 killed the surrogate a proposed self-supervised detector was
built on — independent per-onset dithering, which is separable cell-by-cell on this project's own
recordings. Full account:
[`docs/reviews/2026-09-10-coordination-without-labels_2026-09-10.md`](../reviews/2026-09-10-coordination-without-labels_2026-09-10.md).

Tony, 2026-09-10: *"why pick one replacement? we have compute to test all of them."* So the
replacement is a **screen**, not a choice — the same shape as the tube 2×2, which was built to be
measured rather than argued about.

## The proposed candidate set

| candidate | preserves | why it is in |
|---|---|---|
| circular shift | circular ISI multiset | the incumbent; four of the six hand-written detectors use it |
| **uniform per-onset dither** | rate only | **the KNOWN-BAD positive control.** A screen that fails to flag it is broken |
| rigid shift, no wrap | ISIs exactly, no splice | the cheap repair to the splice objection |
| dither with dead-time | rate + a declared floor τ | minimal fix to the killed one |
| joint-ISI dither | the ISI pair distribution | Louis et al. 2010 |
| pattern jitter | each event's recent history, exactly | Harrison & Geman 2009 — the one to beat |
| interval / window jitter | per-window counts | Amarasingham et al. 2012 |
| operational-time dither | the rate profile under drift | Louis et al. 2010 |

Every one of those papers is now on the shelf under `<darkroom>/bugarach/lit/surrogates/`.

## What has to be decided

1. ~~**Which candidates run.**~~ **RULED 2026-09-10: all eight.** Dropping the uniform dither was
   never available — it is the control that proves the screen can fire — and nothing now supports
   dropping any of the others either. See below.
2. **Grid or independent contests.** ⚠ **STILL OPEN, and now the binding question.**
   [`the four variants of the tube`](2026-08-23-four-variants-of-the-tube.md)
   says in terms that variants "are not a race" — the guard only paid once the bar was
   multiplicative. Surrogate choice may interact with the pooling operator and with *J* the same way.
   One thing narrows it: **the counting tier has no pooling operator**, so it is grid-free and can
   run over all eight at once. The grid only binds from the per-cell discriminator onward.
3. ~~**Whether Stella et al. 2022 already answers part of it.**~~ **RULED 2026-09-10 — and in the
   opposite direction from the one anticipated.** It does not retire candidates; it removes the
   grounds for retiring any.

## What Stella settles

**Read the figure, not the conclusion.** Stella ran six surrogates through SPADE on the same monkey
recordings. On simulated data with ground truth, five of six behaved and uniform dither produced a
large false-positive count. On the *real* recordings — no ground truth — the five returned
overlapping but non-identical sets of significant patterns, each with its own signature of extras.
Transcribing their results section for monkey N, **one epoch out of six is unanimous**: UDD adds an
SGHF pattern in four separate epochs nobody else finds; JISI-D and ISI-D move together; WIN-SHUFF
has its own PGLF in early delay.

⚠ **The paper's discussion contradicts its own figure.** It says the five valid surrogates *"show
almost identical participating neurons, lags, and occurrence numbers"* and reach *"an almost
identical significance level"*, then names TR-SHIFT the method of choice. That is not what the
figure-10 results section describes. **Anyone citing Stella for "surrogate choice barely matters,
use TR-SHIFT" is citing the summary, not the result** — and their own text says the pattern found
during movement occurs *"in all surrogates, but TR-SHIFT"*, so their recommended method is the one
that misses a pattern the other five find.

Two things transfer regardless:

- **Stella rules out uniform dither independently**, by false-positive count under a completely
  different analysis. That is
  [our own leak finding](../reviews/2026-09-10-coordination-without-labels_2026-09-10.md) reached by
  another route, and it is the strongest corroboration it has.
- **TR-SHIFT is our own `rigid shift, no wrap`** — a per-neuron rigid displacement applied *trial by
  trial*. The trial structure it depends on is something continuous baseline recordings do not have,
  so we inherit the mechanism without the guarantee they draw from it.

## Closes when

Tony says grid or not. The candidate set is settled. Then
[`build the surrogate screen`](2026-09-10-build-the-surrogate-screen.md) can start — and its cost
line is now a **build order** rather than a cut: the four cheap candidates can run while the four
expensive ones are still being written.
