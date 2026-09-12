---
status: open
filed: 2026-09-12
---

# Building the label-free objective around the current tube is a foot gun: it cannot tell a count leak from coordination

> **Tony, 2026-09-12:** *"if we build the unspervised learning around the current version of tube,
> this is a big foot gun"*.

## The mechanism

`tube`'s second stage is **mean over cells**: the 30×600 onset raster becomes a 1×600 trace, all
cells to one trace, before any kernel touches it (`docs/learned/architecture.svg`, the front page's
own figure). Everything downstream — the difference-of-Gaussian bank, the bypass, the dilated stack —
reads that single trace.

So tube's input is, frame by frame, **how many ROIs are active, over N**. Coordination raises it.
And so does every count difference a surrogate can introduce:

- binarization collisions, when two onsets are displaced into one frame;
- the encoder's [boundary clipping](2026-09-10-the-encoder-clips-onsets-onto-the-boundary-frames.md),
  which pins displaced onsets onto frame 0 and frame *n*−1;
- [rigid shift's unwrapped edge](2026-09-12-rigid-shift-without-wrap-loses-onsets-at-the-window-edge.md),
  which drops onsets off the end of the window;
- any generator that changes the event count at all, which is
  [the gate Stella's paper actually found](2026-09-12-count-preservation-after-encoding-is-the-gate-stella-actually-found.md).

**For tube, the leak and the signal are the same scalar.** A model trained to tell a recording from
its surrogate can win on a mean-amplitude offset, and the result is indistinguishable from having
learned coordination, because coordination is also a mean-amplitude excursion in that trace.

## Why the screen as designed would not catch it

The screen's leak gate asks whether a **per-ROI** discriminator — one that structurally cannot see
across ROIs — can tell real from surrogate. That is the right test for the leaks it was built for.
Tube is the opposite kind of object: it destroys per-ROI identity immediately and reads only the
aggregate. So a candidate can pass the per-ROI gate and still hand tube a free win, and nothing in
the three tiers measures the aggregate channel.

⚠ The same defect was already found once, in a different costume: the murderboard's round-1 finding
that the proposed discriminator `tiny` *"sums per-ROI votes frame by frame — a coactivity trace, the
one thing a sound surrogate removes."* The architecture question survived the fix to the
discriminator choice.

## The second half of the foot gun

Tube's priors come from the generator it was fitted on — one event width, uniform participation, no
recurring assemblies. A self-supervised objective does not retrain the inductive bias; it fits
weights inside it. So "trained without labels on real recordings" would still carry the simulator's
assumptions about what coordination looks like, while sounding like it had escaped them. That is the
claim most likely to be quoted by an outside reader, and it would be wrong in a way the training
story hides.

## What would have to be true first

- **An aggregate-channel leak test**, beside the per-ROI one: does a model reading only the
  cells-mean trace separate real from surrogate? If yes for a candidate, that candidate is unusable
  for tube whatever the per-ROI gate says.
- **Count preservation as a hard gate** rather than one statistic among many, since for tube it is
  the whole exposure.
- **An architecture that keeps the cell axis** for at least part of the network, or an explicit
  argument for why collapsing it is safe under this objective. The estate has variants; none of this
  says tube is the wrong instrument for detection, only that it is the wrong one to *learn* against a
  surrogate with.

## Closes when

Either the objective is built on an architecture that does not collapse the cell axis before its
first kernel, or the aggregate-channel leak test exists and every candidate that reaches the model
tier has passed it.
