---
status: open
filed: 2026-09-12
---

# Rigid shift is the likely winner, so test it where it is weakest: the edge it does not wrap

On the screen's own leak results, rigid shift is the only candidate that survives at a displacement
comparable to real event structure — out to 1.6 s on the fast stream, 1.4 s on slow, and four frames
on the cossart folder. It is also, by a different route, the family Stella et al. 2022 recommend. A
candidate in that position should be attacked at its weak point before it is adopted, not after.

## The weak point

Rigid shift entered the candidate set as the cheap repair to the splice objection: displace a whole
train, do not wrap, so no artificial interval is spliced in at the seam. The cost of not wrapping is
that onsets shifted past the window's end have nowhere to go.

**That is an event-count difference, which is exactly the failure Stella diagnosed for uniform
dither** — theirs arrives through binarization, this one through truncation, and a discriminator does
not care which. It needs no cross-ROI information: count the onsets. See
[count preservation](2026-09-12-count-preservation-after-encoding-is-the-gate-stella-actually-found.md).

The loss is also **rate-dependent and displacement-dependent** — a busier ROI loses more, and a larger
shift loses more — so it is not a constant offset a model could not use.

## What to check, on data already measured

- Whether the generation-window margin already absorbs it. The screen generates surrogates over the
  producer's window and scores a 60 s analysis cut inside it; if the margin is at least the
  displacement, nothing is lost from the scored region and this concern is answered by construction.
  That is a documentation question first and a measurement second.
- Whether the edge-band statistics show a density deficit for rigid shift at the larger displacements.
  The screen has edge-band counts and edge-thinning and edge-piling controls.
- Whether per-ROI onset counts differ, which is the direct form of the question.

## Why file it rather than assume the margin handles it

The margin rule appears in several places in the plan, and the encoder's own clipping defect was
latent for exactly the reason a margin makes it latent — nothing is out of range until a surrogate
displaces it. A candidate about to be adopted deserves the check written down rather than inferred.

## Closes when

The report states, with a measurement, whether rigid shift loses onsets from the scored window at each
displacement it is credited at.
