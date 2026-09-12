---
status: open
filed: 2026-09-12
---

# Count preservation after encoding is the gate Stella actually found, and it may not be measured

Stella et al. 2022's diagnosis of why uniform dithering fails is not the one this project reached
independently. Theirs: the dithering deletes nothing, but **binarization does** — two onsets displaced
into one bin become one — so the surrogate ends up carrying fewer events than the real recording,
worse at higher rates, with the neuron's dead time and CV setting how much. Fewer events in the null
means fewer chance patterns, which inflates significance in the real data.

## Why it bites harder for a detector than for a significance test

For a discriminator, an event-count difference is not a subtle bias — it is a feature that needs no
cross-ROI information and no learning worth the name. **Count the onsets.** A per-ROI onset count that
differs systematically between real and surrogate is a leak of the most trivial kind, and it survives
any amount of care about intervals.

This project's encoder has **both** of Stella's channels and one of them is worse here:

- **Binarization**, the same as theirs: `encode()` writes a binary raster, so two onsets displaced into
  one frame silently become one.
- **Clipping**, which Stella does not have: out-of-range onsets are pinned onto frame 0 and frame
  *n*−1 rather than dropped, so a displaced event lands on a known frame rather than merely
  disappearing. That is
  [its own todo](2026-09-10-the-encoder-clips-onsets-onto-the-boundary-frames.md), and it converts a
  count deficit into a pile-up at a fixed location.

## What to check first

`src/bugarach/surrogate_stats.py` on the screen's branch carries sub-floor interval counts, edge-band
counts, interval KS distances, serial-order excess, rate-profile dispersion and a `movement` summary
(share of onsets moved, median and RMS displacement). **A per-ROI count of onsets surviving encoding,
real against surrogate, paired, could not be found there by name** on a read of 2026-09-12 — one
comment about an ROI "whose count changed" suggests counts can move without being scored as such.

So the first task is to establish whether the statistic exists under another name. If it does, it
belongs in the verdict rule as a gate rather than one number among many. If it does not, it is cheap
to add and it is the statistic the published literature says catches this family of failure.

## What a gate looks like

Paired, per ROI, per window: onsets in the encoded real raster against onsets in the encoded
surrogate. Any candidate whose count differs systematically fails, regardless of how it does on
intervals — the discriminator would not need to look any further either.

## Closes when

The screen either reports a count-preservation statistic per candidate, or records that it was
considered and why it is not needed.
