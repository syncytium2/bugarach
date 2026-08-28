---
status: open
filed: 2026-08-27
---

# `architecture_fitted.json` was fitted at twice the background of every number it sits beside

> Found by the murderboard on the learned-detector page
> ([`docs/reviews/learned_detector_2026-08-27.md`](../reviews/learned_detector_2026-08-27.md)).
> The role reproduced both fits from scratch before reporting it.

`tools/make_architecture_figures.py:86` trains its own tube through
`bench.make_recording("baseline_busy", …, **gen)` where `gen` is the bake-off spec
**with `bg_rate_hz` removed** (line 287). `make_recording` then merges
`REGIMES["baseline_busy"]`. Everything else is overridden by the spec, so the two runs
differ in exactly one parameter — and it is the one the model is most sensitive to:

| | background | fitted centres (samples) | largest fitted ratio |
|---|---|---|---|
| `architecture_fitted.json` | 0.0190 Hz | 4.02, 4.62, 5.18, 6.56 | 37.7 |
| `bakeoff.json` / `tube_ablation.json`, all four folds | 0.0097 Hz | 2.6 – 5.0 | **23.5** |

Same architecture, same 1,149 parameters — which is what makes them look like one
model — trained on different data.

## What it has already cost

**A published page quoted them as one model.** The learned-detector page took the
4.0–6.6 widths from the busy fit and the F1 from the bake-off, two paragraphs apart,
with nothing saying they were different runs. That page has been rewritten and no
longer quotes the widths at all, for a separate reason (see below), so nothing is
currently mis-stating this — but the trap is still set for the next page.

**It also invalidated an ablation's premise.** The observation that motivated the
surround-ratio clamp experiment — *"one fitted ratio sat at 38 against a ceiling of
40"* — comes from the **busy** fit. The ablation then varied that ceiling on the
**bake-off** data, where the largest ratio anywhere is 23.5, so the clamp never binds
and the two runs are bit-identical computations. The suspicious condition was
observed in one fit and "tested" in runs where it cannot occur.

## Note the widths are separately unquotable

Independent of this, the fitted widths **must not be reported as recovering the event
timescale** —
[the learned-detector handoff](2026-08-16-learned-detectors-handoff.md) withdrew that
reading: refitted on a quieter background with identical events they move 40%, and
`regime_shift_fitted.json`'s quiet fit spans 3.8×. So this item is about the
*provenance mismatch*, not about restoring the claim.

## Repair

**Cheap:** give `make_architecture_figures.py` a `--bg-rate` (or `--regime`) flag
defaulting to the spec's own `bg_rate_hz`, regenerate `architecture_fitted.json`, and
the figure and the table describe one model.

**Cheaper and worse:** label the figure as a separate fit. That keeps two fits in the
tree with one filename and relies on every future reader noticing the label.

**Worth doing either way:** the 35% swing in fitted width between the two backgrounds
is itself an unreported result about the model, and it is the same finding as the
handoff's 40%. Two independent observations of the same effect, neither published.
