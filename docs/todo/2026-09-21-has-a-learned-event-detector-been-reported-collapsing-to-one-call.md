---
status: open
filed: 2026-09-21
---

# Has anyone reported a learned event detector collapsing to one call over the whole recording?

**The one search that could still make the chorus-collapse page's claim old, and nobody has run it.**

## Where the claim stands

The page, [`docs/learned/chorus_collapse/index.html`](../learned/chorus_collapse/index.html), used to
close with *"That it prevents this collapse is this page's result."* #679 withdrew that after reading
two papers:

- **Kosson et al. 2024** walks the same chain — too large an early step, damage training does not
  undo, a warm-up prevents it — but its units are alive and get killed, in a ReLU network whose
  remedy is a leaky ReLU.
- **Lu et al. 2020** is closer: networks dead *before* training, optimised to a constant function,
  more likely deeper and narrower — Table 1's ordering. But its theory is ReLU-only and forbids the
  recovery the page demonstrates.

Both are filed on the literature shelf, `<darkroom>/bugarach/archive/2026-08/lit/optimization/`, with the distinction
written into each entry.

What the page now claims is narrower: a head can start almost silent in a network with **no zero
region** to be stuck in, whether training wakes it decides the fit, and the failure is recoverable.
And since #687 it carries a second, independent result: **where** the signal stops differs by net —
the head for chorus_norm, before the head for 43% of chorus_gain_norm's failures.

## What has not been searched

The page says so itself, and so does the shelf's README: whether a **learned event detector** has
been reported **collapsing to a single call covering the whole recording** has **not** been searched.
The three literatures that were — warm-up, dying-ReLU, dormant units — are all general deep learning.
None is about event detection, and none is about calcium imaging.

This is the gap that matters, because it is where someone else would most plausibly have met exactly
this failure. A detector trained on sparse events, with a class-weighted loss and a threshold picked
from a grid, has an obvious degenerate solution — output a constant and let the lowest threshold
call everything once — and anyone who has trained one has had reason to look.

## Where to look

- **Learned calcium-imaging and spike-inference detectors** — CASCADE, DeepCINAC and their kin; the
  project's own `lit/coordination/` shelf already holds several.
- **Learned event detectors outside imaging** — sleep-EEG spindle and K-complex detectors (DOSED and
  successors), hippocampal ripple detectors (cnn-ripple). `docs/detector_history.md` already names
  these as *"an established genre with a standard architecture family"*; that shelf was built to stop
  a novelty claim four web searches had failed to check, and this is the same risk one level down.
- **The class-imbalance literature on degenerate base-rate predictors** — role 2's one probe there
  surfaced only generic material, which is not the same as a search.

## How this should close

Read, not search — the repo has paid for the difference before. Either a paper turns up, and the
claim comes down or narrows again with the paper filed on a shelf and the difference stated, or the
search comes back empty and the page's *"not searched"* becomes *"searched, here is what was read"*.
Both are a good outcome; only leaving the sentence as it is is not.
