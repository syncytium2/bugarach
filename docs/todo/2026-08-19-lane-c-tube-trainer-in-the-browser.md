---
status: open
filed: 2026-08-19
---

# Lane C — the tube trains in the browser, with no install at all

> **Resequenced 2026-08-19, and not cancelled.** Tony chose the lab server first
> ([`ADR-0001`](../adr/0001-the-lab-server.md), lane H1): training moves to a loopback
> process calling `learn.train` directly, which reaches a working end-to-end demo in a few
> hundred lines rather than a thousand lines of new numerics.
>
> **What changed for this lane is that it now has an answer key.** Written blind, it had
> to invent what correct looks like; written after H1, it is checked against an
> implementation that already agrees with `bakeoff.json`.
>
> **What it is still for**: the lab that will not install Python. H1 makes training work;
> this makes it work for everybody, and it is the only route back to the no-install
> promise for stage 6b.

Plan: [`docs/webapp_completion_plan.md`](../webapp_completion_plan.md). It touches nothing
another lane holds until the final splice.

## Why it has to be hand-written

The published page may not reach the network — `tests/test_site_viewer.py` bans `fetch(`,
`<script src` and `import(`, and `tools/build_site.py` refuses to publish it otherwise.
So no CDN-hosted ML library, and **no calling H1's server from the published page** — the
lab server serves its own copy and the published one stays deaf. This trainer goes inline,
in JS, or it does not exist.

## What that actually costs

`tube` is 1,149 parameters and the operation list is closed:

- dilated `conv1d` (k=3, dilation doubling) ×6 plus a 1×1 head — forward and backward
- GELU
- `max_pool1d`, stride 1 — backward is argmax routing
- the difference-of-Gaussians kernel, with gradients through `log_center`, `log_ratio`
  and `gain`: exp, clamp, gaussian, area-normalise so a flat field integrates to zero
- `BCEWithLogitsLoss` with `pos_weight` — events are ~1% of frames and without it the
  model learns to answer "no"
- Adam; 300 steps, batch 4, 4,096-frame crops, half of them drawn to contain an event

Reference: [`src/bugarach/learn/nets.py`](../../src/bugarach/learn/nets.py) `build_tube`
and [`src/bugarach/learn/train.py`](../../src/bugarach/learn/train.py) `train`. PyTorch
fits it in 5.6 s and scans a held-out fold in 0.014 s.

## How to build it so it merges cleanly

**Do not edit `docs/site/raster_viewer.html` while lane A's merge train is running** —
that file is a single-holder resource and five PRs already queue on it. Develop the
trainer as a standalone block plus its parity harness, and splice it in one commit at
the end.

## What "at parity" means here

**Behavioural, not 1e-9.** Gradient descent from a seeded init will not reproduce
PyTorch bit-for-bit across two languages.
[`docs/testing_a_sampling_port.md`](../testing_a_sampling_port.md) sets the bar for
ports that cannot be exact. What *can* be checked tightly, and should be, in this order:

1. **Forward pass on fixed weights** — exact to 1e-9. No RNG is involved, so this is the
   same bar RateDetect met, and it catches almost every real mistake.
2. **Analytic gradients against finite differences**, per parameter group.
3. **One optimiser step from a fixed init on a fixed batch** — parameters must agree to
   tight tolerance.
4. **End to end**: train on a seeded data set in both, compare F1 on the same held-out
   fold. Agreement within fold spread, not to a digit.

## Two rules that are not the trainer's to relax

- **The threshold is picked on held-out training-regime data and never re-picked on the
  recording being analysed.** A "re-tune on this slice" button hides exactly the failure
  the regime-shift test measures.
- **Fit busy, deploy quiet.** Measured in `docs/learned/regime_shift_fitted.json`: fitted
  quiet and run busy, the learned model loses 0.24 of F1. If the app fits for a user, it
  fits on their busier recordings. Free to implement, and the cheapest correctness win
  the UI has.

## The honest framing this lane serves

On the published data set the tube **ties** CoactDetect (0.668 ± 0.061 against
0.651 ± 0.044) rather than leading, and every learned number is one training run per
fold. Building this lane does not make the claim true; it makes the comparison visible.
Moving the result is the model track.
