---
status: open
filed: 2026-08-17
---

# The bench cannot see whether a detector lands on the event

Every score in this repo is computed at one scoring tolerance, `tol_sec = 1.5`,
the edge-to-edge gap allowed between a detection's interval and a planted event
(`bugarach.score.score_detections`). The value has never been varied. Sweeping it
says the number is safe and the *instrument* is not.

**Measured, 2026-08-17** — `tools/make_tolerance_figure.py`, six detectors, three
seeds, both regimes, figure at `docs/learned/tolerance_sweep.png`:

| | quiet | busy |
|---|---|---|
| leader at every tolerance from 0.1 s to 3.0 s | LoCo | rate+context |
| CICADA, F1 at 0.1 s → at 1.5 s | 0.33 → 0.52 | **0.12 → 0.56** |
| SPIKE-synch, same | 0.29 → 0.42 | 0.39 → 0.51 |
| LoCo / CoactDetect / rate+context | flat | flat |

Two things follow, and they point in opposite directions.

**The published ranking is safe.** Whoever leads a regime leads it at every
tolerance tested. No comparison in the report or the bake-off rests on the choice
of 1.5 s, and that is worth knowing rather than assuming.

**But 1.5 s is deep in the saturated part of every curve.** Every detector has
plateaued by roughly 0.75 s. Above that the bench cannot distinguish a detector
that lands on an event from one that lands a second away from it — and the
realized event footprint has a median of **0.80 s** (`PlantedEvent.observed_span`,
PR #46), so the shipped tolerance is close to *twice the width of the thing being
found*. Localization accuracy is not measured badly here; it is not measured.

The detectors that move are the binned ones, which is exactly where timing error
lives. CICADA's fourfold swing in the busy regime is the whole difference between
"finds coordination" and "finds roughly when coordination happened".

## What to do

Two changes, the first small.

1. **Report F1 against a swept tolerance, not a scalar.** `evaluate` and
   `score_stream` already take `tol_sec`, so the sweep is a loop and the figure
   exists. The bake-off and the report should carry the curve, or at minimum
   quote a tight tolerance beside the permissive one.
2. **Add a localization metric.** F1 at any single tolerance answers "did it
   fire near the event"; it never answers "how near". The sleep-EEG literature
   reports **mean IoU** as a separate number for exactly this — see SEED
   (Tapia-Rivas et al. 2024) — and DOSED (Chambon et al. 2019) reports F1 across
   an overlap criterion swept 0.1–0.9, re-tuning every competitor at each value
   so the comparison stays fair at each. Both are on the shelf at
   `<darkroom>/bugarach/lit/coordination/`.

Note the unit difference before copying either: **their criterion is IoU, a
ratio; ours is an absolute gap in seconds.** A ratio is scale-free and an
absolute tolerance is not, which matters here because event width varies
0.10–1.70 s. Adopting IoU is the bigger change and the more defensible one; a
swept `tol_sec` is the cheap version and worth doing first.

## What this is not

**Not a re-litigation of `2026-08-13-scoring-tolerance-vs-detector-resolution.md`,
which is closed and was closed correctly.** That todo fixed a real bug — a
point-matched scorer read SCE at 0.08 recall on detections that were all correct,
and the fix was to score interval overlap so a binned detector is not punished
for being binned. This is the next question, not that one: given that overlap
scoring is right, *how much* overlap should be required, and what is invisible
while the answer is a single permissive constant.

An earlier note of mine described DOSED's sweep as "an answer to" that todo. That
was wrong — the todo was already done — and the description is corrected here.

## Cost

The sweep is done and the tool is committed. Adopting IoU means a change to
`score_detections` and a re-run of every published number, which is why it is
filed rather than applied.
