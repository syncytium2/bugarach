---
status: open
filed: 2026-08-27
---

# `build_tube`'s docstring asserts two guarantees the model does not deliver

> Found by the murderboard on the learned-detector page
> ([`docs/reviews/learned_detector_2026-08-27.md`](../reviews/learned_detector_2026-08-27.md)).
> The page inherited both claims faithfully from the code, which is why the page was
> wrong and why fixing the page alone does not close this.

Two roles measured against a trained model rather than reasoning about the source.
The page has been corrected. `src/bugarach/learn/nets.py` has not.

## 1 · "the cap is exact rather than soft, because a centre window exists"

`nets.py` claims the tube's one-cell-one-vote bound is exact, in explicit contrast
to `tiny`, whose docstring says its own bound is *"soft, not exact"*. The contrast is
the wrong way round.

**The max-pool caps nothing.** `encode.Encoded.raster` is already one-or-zero per
(cell, frame) — its own docstring says *"several onsets in one frame stay 1"* — so a
max-pool over a binary signal returns a binary signal. What the operation actually
does is **widen** each onset to `2*kmin+1` frames, which increases what a repeatedly
firing cell contributes to the centre integral rather than bounding it.

**And it fails behaviourally at the shipped operating point.** Fed synthetic input:

```
1 cell,  8 onsets 3 samples apart : peak 0.9917   (threshold 0.99703)
2 cells, 8 onsets 3 samples apart : peak 1.0000   FIRES
4 distinct cells, one onset each  : peak 1.0000   FIRES
```

Two bursting cells are indistinguishable from a genuine four-cell crowd — which is
the exact false coordination the whole design exists to reject, and the same
mechanism as the model's 15.75 firings per fold into a block containing nothing.

Third, smaller: the window is described as "the centre window" where there are four.
`forward` uses `int()` of the **narrowest** fitted width, `detach()`ed, clamped to
`[1, k]` — a different clamp from the `[0.5, k/2]` that `_kernels` applies to the same
quantity — while the widest scale integrates over roughly ±15 samples of it.

## 2 · "rate invariance structural rather than learned"

True of the kernel. False of the model, and the module's own architecture figure has
drawn the reason all along: `forward` ends

```python
self.head(torch.cat([bright, resp], dim=1))
```

so the raw pooled brightness trace — the absolute local activity level — reaches the
head on its own channel, beside the zero-integral responses. Whatever the kernel
cancels, that channel carries through.

Measured on recordings with **nothing planted in them**
(`tools/probe_rate_invariance.py`, one training run, seed 7): raising the background
eightfold takes the model from 22 frames over its operating point to 538. Zeroing the
bypass and re-scoring the same recordings gives 4 and 354 — so the bypass is most of
the excess at baseline and about a third of it at the top. The remainder is variance,
which a difference of means cancels and a difference of variances does not.

⚠ A review role measured the same effect at 7 → 1,228 on its own training run. Same
direction, same order, different numbers. **One training run per fold is the standing
limitation and it bites here too** — neither pair should be quoted as the magnitude.

## What to change, and what not to

**Correct the docstring.** Say the bound is soft and why; say the kernel is
DC-invariant and the model is not, and name the bypass. `build_tiny`'s docstring is
the model for the right tone — it already flags its own approximation with a ⚠ and
calls the trade *"the thing to probe behaviourally, not to assert."*

**Do not "fix" the model to match the docstring in the same change.** Removing the
bypass channel is
[item 4 of the learned-detector handoff](2026-08-16-learned-detectors-handoff.md)
(*"Drop the raw brightness channel and re-run. One line."*) and it would move every
published number. Two separate decisions: one is a comment that lies, the other is an
experiment nobody has run.

**The clamp mismatch between `forward` and `_kernels` is a third thing** and is worth
a line either way — one of them is wrong, and nothing currently says which.
