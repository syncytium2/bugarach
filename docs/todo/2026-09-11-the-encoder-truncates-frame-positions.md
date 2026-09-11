---
status: open
filed: 2026-09-11
---

# The encoder truncates frame positions, so on-grid onsets can land a frame early

> **Tony's decision.** Changing it changes what every learned model trains on.

## What

`src/bugarach/learn/encode.py` (line 119) computes an onset's frame as
`((v - t0) / dt).astype(int64)` — truncation, not rounding. Our onsets sit exactly on the 0.1-second
frame grid, but as floating-point numbers many sit a hair below their grid point (0.3 / 0.1 is
2.999…), so truncation files them one frame early. The surrogate-screen review measured this on
synthetic on-grid points: about a third land in the wrong frame.

The consequence for surrogates is a leak the pipeline makes rather than the method: a surrogate whose
times carry different floating-point residue from the real export's encodes differently even when it
sits on the same grid point.

## Options

- Round instead of truncate — changes every encoded input; models retrain.
- Feed the encoder integer frame indices, computed once upstream.

The overnight surrogate screen sidesteps it by working in frame indices throughout
([the plan](../proposals/2026-09-10-surrogate-evaluation-overnight.md)).

Related: [the encoder clips onsets onto the boundary frames](2026-09-10-the-encoder-clips-onsets-onto-the-boundary-frames.md).

## Closes when

Tony decides. If the encoder changes, the learned models retrain and the bake-off reruns.
