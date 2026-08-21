---
status: open
filed: 2026-08-21
---

# Notes from Tony using the app — collecting, not yet acted on

Tony, 2026-08-21, while driving the deployed page: *"hold until I say go. these
are notes while using the app … store these, then wait for my go."*

**Nothing here is implemented.** The list is open and more may arrive; the call
sites are recorded so acting on it later does not start with a hunt.

---

## 1 · The window legend describes the bar and not the shading

> *"bar = the period · shading = the part scored" — the legend shows the bars,
> legend should show the shading and label as the accordion head (match!)
> "analysis windows"*

**Where.** [`raster_viewer.html:1411-1415`](../site/raster_viewer.html) — the
legend line built at the end of the per-window loop that fills `#wins`, and the
swatches above it at :1395-1398 (`span.sw`, filled with `ink(w.label)`).

**What is wrong.** The legend sentence names two channels — the bar and the
shading — and the swatches next to it draw only one of them. Every swatch is a
solid block of the period's colour, so the reader is told a shading exists and is
never shown what it looks like. The line reads as an explanation of a key that is
not there.

**What Tony asked for.**

- the legend's swatch shows **the shading**, not just the bar, so both channels
  the sentence names are visible in the key;
- the legend is **labelled**, and the label is **the accordion head verbatim** —
  `Analysis windows` (`raster_viewer.html:355`) — so the picture and the panel
  that controls it say the same words. "match!" is the emphasis, and it is the
  point of the note rather than a detail of it.

**Watch out for.** The second branch of that same line reads *"shading = the
same, no analysis window was sent"* — a key drawn for the first branch has to
stay honest under the second, where the shading and the bar are deliberately the
same extent. Whatever the swatch shows must not imply a distinction the folder
did not make.

---

## 2 · "no detector involved" is not true of the assessor

> *"under assess coordination, do not say no detector involved. the assessor is
> by definition a detector"*

**Where.** [`raster_viewer.html:404`](../site/raster_viewer.html) — the chip on
the `Assess coordination` accordion head. It is the only place the page makes
this claim; the fine print inside the panel does not repeat it.

**What is wrong.** The chip is asserting something false about what the step
does. The assessor finds coordinated clusters and returns their times, their
participants and their spread — that is detection. What it is *not* is one of the
**six named detectors**, and it does not need a threshold or an operating point,
which is presumably what the phrase was reaching for. Saying "no detector
involved" buys that distinction by making a wrong statement about the method.

**Why it matters more than a word.** The whole architecture of the page rests on
the assessor being a measurement the six are later scored against. A reader who
believes the assess step involves no detection has the relationship between
stages 3 and 6 backwards, and this is the chip that told them so.

**Not yet chosen: the replacement wording.** The chip is short by design — the
others are `no data needed`, `your own recordings`, `simulated only`, `local
only`, `draft`. Something in that register that says *no threshold to pick* or
*no operating point* rather than *no detector*. Tony's call, and it belongs with
the rest of the copy pass rather than being guessed at here.

---

## Related, and worth doing in the same pass

`docs/todo/2026-08-20-the-scoreboard-copy-needs-review.md` is the other open copy
item. Both are wording on the published page; reviewing them together is cheaper
than twice, and the scoreboard panel cannot be un-hidden until its own review is
done anyway.
