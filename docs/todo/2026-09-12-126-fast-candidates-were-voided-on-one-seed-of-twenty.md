---
status: open
filed: 2026-09-12
---

# 126 fast candidates were voided on one seed of twenty

**The voiding rule read a single seed of the negative control while twenty seeds sat in the same run
folder, and every fast candidate that returned a number was voided by it.**

Found by the ROI-swap proposal's murderboard
([record](../reviews/2026-09-12-the-roi-swap-null_2026-09-12.md)), by four roles independently. It is a
defect in how the 2026-09-11 surrogate screen applied its control, not a fact about the preparation,
and it stands whatever happens to that proposal.

## What the run says

`real_vs_real` is the screen's negative control: each real window paired with another real window of
**its own recording**, which of the two is called "real" drawn at random (`negative_control_pairs` in
`surrogate_discriminator.py`, on the screen branch). Its job is to check the machinery — folds,
scaling, the null — and it must not flag.

In `<darkroom>/bugarach/2026-09-11-surrogate-screen/discriminator/steps_excluded/fast/controls/`:

| file | what it holds |
|---|---|
| `negative.json` | **seed 0 only**: accuracy 0.5386, P = 0.035, `significant: True`, 830 pairs |
| `negative_seeds.json` | **20 seeds**: `flag_rate` **0.05**, mean accuracy **0.4948**; seed 0 is the only significant one |

Slow and cossart are 20 seeds at `flag_rate` 0.0.

A negative control flagging at exactly its nominal alpha over twenty seeds, with mean accuracy **below**
chance, is a control that passes. The voiding rule consumed seed 0.

## What that did

In `discriminator/steps_excluded/discriminator.csv`, every fast candidate carries the void reason
`"negative control (real against real) flagged: accuracy 0.539, P = 0.035"`:

- **126 of 248** fast candidates are voided;
- the other 122 are `intractable` and returned no number;
- so among fast candidates that returned a result at all, **126 of 126**.

Slow: 0 voided.

And the flagged seed was below its own detection floor: at 830 pairs the exact minimum detectable
accuracy for 80% power is about **0.544**, and 0.5386 sits under it (power there is about 0.70). The
negative control was less powered than the candidates it gated.

## Why this matters beyond one run

`rigid_shift` — the one candidate surviving contiguously to 1.6 s on fast, and the within-recording
null that the ROI-swap review found may already do what that proposal wanted — is among the 126. Its
fast accuracies are 0.495-0.524 across all six J values. Every conclusion drawn about the fast stream
from the 2026-09-11 screen was drawn from voided rows.

## What to do

1. **Find where `apply_controls` reads the control** and whether it is meant to read `negative.json` or
   the seed distribution. The fix is probably one line; the question is which file is authoritative.
2. **Decide the rule** — flag on the seed distribution (for example, flag_rate materially above alpha)
   rather than on any single draw. That is a design decision, not a patch.
3. **Re-derive the fast verdicts** with the corrected rule. No rerun is needed: the candidate
   accuracies are already on disk and unaffected; only the void column changes.
4. ⚠ **Do not look at which fast candidates would un-void before the rule is fixed**, for the same
   reason the band statistics are not scored against their floor: choosing a rule after seeing its
   effect is post-hoc.

⚠ **Tony stopped the screen thread on 2026-09-12** — his recorded answers were that the family-size
question needed discussion first, and to stop there for now. This todo is a record, not a restart;
whether and when to act on it is his call.
