---
status: open
filed: 2026-09-10
---

# Training on baseline and deploying on treated is the transfer direction this project measured as harmful

> **Tony's call:** accept the penalty and say so, or bound it before any treatment number is read.

## The collision

FOUNDATIONS §9 forbids taking the properties of coordination from treated recordings — *"do not use
senk or ttx as sources for the properties of coordination"* — so a learned detector must be fitted
on baseline windows and pointed at treated ones. That constraint is right and binding.

But [`model_track.md`](../model_track.md) records, as a **measured** result on the existing learned
detector: *"It transfers worse than two of the six from a quiet background to a busy one, which is a
negative result about its own central claim. **Fit busy, deploy quiet.**"* It puts the size at the
difference between a **−0.24 transfer penalty and a +0.12 gain**.

Baseline → treated is **quiet → busy**: the measured-bad direction. Under TTX the slow stream runs
at roughly **2.5×** its own baseline (FOUNDATIONS §9).

A proposal on 2026-09-10 called the FOUNDATIONS constraint *"the right experimental design anyway"*
while the tree held a measurement saying it costs about a third of the score, and never named it.
Caught by murderboard role 4:
[`the run record`](../reviews/2026-09-10-coordination-without-labels_2026-09-10.md).

## Two things that make it worse than a single number

- ⚠ **The streams transfer in opposite directions.** Fast falls to ~0.46× baseline under TTX, slow
  rises to ~2.5×. A single pooled statement about transfer is not available.
- ⚠ **A threshold calibrated on baseline is calibrated outside its deployment range.** If a
  false-alarm rate is set on baseline windows, the treated regime is by construction not in the
  range it was measured on.

## The options, and neither is free

1. **Argue the penalty does not apply** to a surrogate-contrastive objective — the negative is
   rate-matched to the positive by construction, so the model may be less rate-sensitive than a
   centre-surround model was. That is a hypothesis and needs its own falsification entry with a
   stated test, not an assertion.
2. **Accept it and bound it** — state that the baseline-to-treatment contrast carries a transfer
   confound, and measure its size before any treatment number is quoted.

## Closes when

The chosen option is written down where a treatment number would be read, and — if the first — the
test that would falsify it exists.
