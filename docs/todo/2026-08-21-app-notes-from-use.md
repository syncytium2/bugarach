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

## 3 · Define K in the control, and the count-versus-percent question

> *"assessor controls, define K as the min number of ROIs participating in a
> coordinated event. i wonder if this should be toggled to percent, as we have
> some with 10 rois or less maybe"*

**Where.** [`raster_viewer.html:412`](../site/raster_viewer.html) — the control is
labelled `mark clusters at K` and offers `none / 3 / 4 / 6 / 8` with no statement
of what K counts. `K_SCAN = [3, 4, 6, 8]` at :3174, tracking
`assess.DEFAULT_MIN_ROIS`. The panel's fine print calls K *"the floor for how many
ROIs make an event"* — which is the definition Tony wants, sitting two paragraphs
below the control instead of on it.

### The easy half

Label it as what it is: **the minimum number of ROIs participating in a
coordinated event.** No argument here, and it is the one place a reader meets K
before any of the prose.

### The harder half, and it is a real question — measured

Read-only over `2026-08-18_revised_2v_periods`, 84 recordings:

| | ROIs |
|---|---|
| min | **9** |
| p25 / median / p75 | 23 / 32 / 37 |
| max | **61** |

So the field size spans about **7x**, and the same K is a different question on
each end:

| K | on the smallest (9) | at the median (32) | on the largest (61) |
|---|---|---|---|
| 3 | 33% | 9% | 5% |
| 4 | 44% | 12% | 7% |
| 6 | 67% | 19% | 10% |
| 8 | **89%** | 25% | **13%** |

**Tony's instinct is right about the effect and slightly off about the cause.**
Recordings with ≤10 ROIs are **2 of 84 (2%)** — 9 and 10 ROIs, `20241004_80` and
`20260707_346`. The problem is not those two; it is that K is an absolute count
across a corpus whose field size varies 7-fold, so *"coordination at K=8"* is a
claim about a quarter of the field in one recording and nearly all of it in
another. That bites at the median too.

### What blocks a straight swap to percent

**The 3-ROI floor.** `minRois` is fixed at 3 in the detectors
([:2228](../site/raster_viewer.html)) and is deliberately **not a knob** —
FOUNDATIONS §9, because raising it until false alarms disappear is the exact
error this project has already refused once. A percentage lands under it on small
fields:

| asked | smallest (9) | median (32) | largest (61) |
|---|---|---|---|
| 10% | **1 ROI** ⚠ | 3 | 6 |
| 18% | **2 ROI** ⚠ | 6 | 11 |
| 30% | 3 ROI | 10 | 18 |

So on the 9-ROI recording every sensible percentage clamps to the floor and
becomes K=3 — the count behaviour, wearing a percent label. A toggle must **show
that clamp** rather than silently honour a number it did not use.

**And it would fork from Python.** `K_SCAN` tracks `assess.DEFAULT_MIN_ROIS`,
which is a count. A browser scanning percentages is scanning different Ks than
`bugarach.assess` does, and the two stop being comparable unless Python moves
with it.

### Worth noting: the app is already inconsistent about this

The **simulate** side already speaks in percent — participation is
`30/18/10% — measured` ([:302](../site/raster_viewer.html)) — while the
**assess** side speaks in counts. The same quantity, two units, two panels. So
this is not only a convenience question; it is the one place the page contradicts
itself about how participation is expressed.

**Undecided, and Tony's call:** whether to toggle, or to show both (`K = 6 · 19%
of this field`) and keep the scan in counts. The second is cheaper, forks nothing,
and answers the comparability complaint without inventing a clamp to explain.

---

## Related, and worth doing in the same pass

`docs/todo/2026-08-20-the-scoreboard-copy-needs-review.md` is the other open copy
item. Both are wording on the published page; reviewing them together is cheaper
than twice, and the scoreboard panel cannot be un-hidden until its own review is
done anyway.
