---
status: open
filed: 2026-09-10
---

# Which surrogates enter the screen, and does it run as a grid

> **Tony's decision.** Nothing downstream of it can start.

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

1. **Which candidates run.** Dropping any is fine; dropping the uniform dither is not, because it is
   the control that proves the screen can fire.
2. **Grid or independent contests.** [`the four variants of the tube`](2026-08-23-four-variants-of-the-tube.md)
   says in terms that variants "are not a race" — the guard only paid once the bar was
   multiplicative. Surrogate choice may interact with the pooling operator and with *J* the same way.
3. **Whether ⚠ Stella et al. 2022 already answers part of it.** It is a systematic six-way surrogate
   comparison, on the shelf, and may make some of this redundant. **Read it before building.**

## Closes when

Tony names the candidate set and says grid or not. Then
[`build the surrogate screen`](2026-09-10-build-the-surrogate-screen.md) can start.
