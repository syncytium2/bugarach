---
status: open
filed: 2026-08-19
---

# Lane E — folds and one scorer in the browser, so "optimized to the same ground truth" is true

Plan: [`docs/webapp_completion_plan.md`](../webapp_completion_plan.md). Pure functions,
no UI, **does not touch `docs/site/raster_viewer.html`** until the splice — so it runs in
parallel with everything else.

## The gap it closes

The webapp's tuning step sweeps **one** detector's **one** knob on **one** recording and
scores it against that recording's own planted events. That is a demonstration, not a
fit: there is no held-out data, so nothing on screen can be called performance on new
ground truth. `tools/fair_bakeoff.py` already does the real thing — generate a corpus,
split it into folds, fit or train every detector on three, score on the fourth, rotate.

This lane ports the two pieces that makes that possible in the browser:

- **the fold split** — deterministic from the corpus seed, so a run reproduces
- **`bugarach.bench.pool_scores`**, and nothing else

## The rule that motivates it

`docs/learned/README_for_the_webapp.md`: *"`pool_scores` is the single scoring path …
Do not compute F1 in the UI layer — an earlier version of the regime-shift tool did its
own arithmetic and put the two halves of a comparison on different metrics."* The page
already has a `scoreDetections` used by the sweep. It must end up being **the same
arithmetic** as the Python, checked, rather than a second one that drifts into agreeing.

## How to check it

Fixed inputs, both languages, compared exactly — no RNG is involved in scoring, so this
is a 1e-9 port, not a sampling one. `tests/test_webapp_tune_parity.py` is the pattern to
copy. Include the degenerate cases the arithmetic hides in: no detections, no planted
events, every detection a hit, a detection matching two truths and a truth matched by
two detections.

## One thing to carry with the number

The bench scores a hit at a **1.5 s edge gap** against a median realized event **0.80 s**
wide (`docs/learned/tolerance_sweep.png`), so the score cannot tell landing on an event
from landing a second away. The *ranking* is stable, so any comparison the app shows is
safe; a bare F1 implying timing accuracy is not. Whatever this lane returns should carry
its tolerance with it so the screen cannot show one without the other.
