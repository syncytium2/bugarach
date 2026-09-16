---
status: open
filed: 2026-09-16
---

# Rebuild the plain-language review on tonight's settings, and give Figure 2 a representative recording

**Do this once the overnight `full-search` run has reported and its settings are decided** — not before,
or everything below gets done twice.

## Figure 2 (Tony, 2026-09-16)

*"figure 2 makes it look like nothing works ... our goal is to improve? figure 2 looks like there's no
hope"*. Tony chose: **a representative recording, redone after tonight's search.**

Why the current one misleads, all three about how it was chosen rather than about the programs:

1. It was picked as the recording, of eight, where the six programs' counts **disagree most**
   (`make_detector_review.py`, `stage_problem`: the max of the spread ratio).
2. It holds **no clear coordinated events** by our clear-stripe rule — only a senktide stretch where every
   neuron gets busy, the one condition every program struggles with.
3. Its calls come from `measurements/real_detections.json` of the **2026-09-15** review build: before the
   retune of LoCo, rate+context and binned SCE (#597), locust's measured durations (#594) and binned SCE's
   bin-width scoring (#593).

What the page hides meanwhile: inside the analysis windows the programs call nearly every clear stripe
(rate+context and locust 100%, CoactDetect 98%, LoCo 95%, binned SCE 58% — plain review, Section "Where
your eye and the programs disagree").

**To do**

- Merge `main` into `detector-review-doc` so the builders see the current `OPERATING_POINTS`.
- Rerun the real-recording detections (the first review's real stage) with the settings from the full
  search.
- Choose Figure 2's recording by a stated rule, written in the builder and the caption: it must contain
  clear stripes, and among those recordings take one whose disagreement between programs is typical (the
  median), not the largest. It should show both halves — programs agreeing on what the eye sees, and
  disagreeing elsewhere.
- Put the settings' date or commit in the caption.
- Remove the caption sentence "This example does not appear to hold any coordinated events" if the new
  recording has them; it is worded from the stripe count, so check what it says.

## Everything else that is stale until then

- The "three tuned, three at their written values" paragraph (grading section): after #597 only SPIKE-synch
  keeps its original value, and that one was tested and kept.
- Score figures and their numbers, the busy-stretch figure, and the interval-rule comparison (Figure 20),
  whose LoCo numbers were measured at 99.9.
- `HANDOFF-detector-optimization.md` and the first review's handoff.
- Consider running `render_check` as part of the page stage rather than by hand: it caught five text
  escapes and 35 overlaps on 2026-09-16 that screenshots had not.
