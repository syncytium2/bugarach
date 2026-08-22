---
status: open
filed: 2026-08-22
---

# The revision plan: mechanism before calibration, and what the literature added

Companion to
[`the case for revising the detectors`](2026-08-22-the-case-for-revising-the-detectors.md),
written the same day from the other end — that document assembled the evidence that
the **settings** were fitted on the wrong background; this one integrates what
retrieving the detection-theory primaries added, and turns both into an order of
work.

> **Not murderboarded**, and it is a planning note rather than an outside-facing
> artifact — same standing as the case document it extends. Every number below is
> quoted from a named file. **If any of it goes to an outside reader, murderboard
> that artifact first.**

---

## The one sentence that changes the plan

The case document is careful and explicit:

> *"Nothing here says a detector is **wrong**. It says the **settings** were fitted
> on the wrong background."*

That was true when it was written. It is no longer. **Three of the six detectors,
and the learned model that leads the bake-off, have a defect that is not a
setting** — and re-fitting a detector whose mechanism is wrong bakes the defect
into the new operating point at full cost.

So the plan's spine is: **mechanism, then benchmark, then calibration.** Do it in
the other order and the expensive campaign gets run twice.

---

## What the primaries added — six items, numbered on from the case's six

The case lists evidence 1–6. These continue it. Sources are on the shelf at
`<darkroom>/bugarach/lit/radar/`; the full argument is
[`detector_history.md`](../detector_history.md).

### 7 · None of the three rolling detectors excludes the moment it is testing

Read off the source, not inferred:

- `loco.py` — trailing half `[a - half_ctx, a]`, leading half `[a, a + half_ctx]`,
  both abutting the anchor.
- `coact.py` — `c_lo = ctr[b] - C/2`, `c_hi = ctr[b] + C/2`: the bin under test is
  **dead centre** of the window that judges it, and the circular shift runs inside
  that window, so the bin's own events are preserved in the null pool.
- `rate.py` — rate and context are both **centred** sliding windows, so the 1 s test
  window sits inside its own 60 s reference.

Every CFAR detector excludes the cells around the one under test — the **guard
cells** — and Rohling 1983 specifies *"two guard cells directly adjacent to the test
cell"* as an unargued setup detail. Finn & Johnson quantified the cost of not doing
it in **1968**: *"The introduction of a second target in one of the threshold control
cells introduces a masking effect equivalent to a 1-dB loss in detection
efficiency."*

**That is the regime-shift incident.** Four planted events inside every 60 s context
window; binned SCE's precision 74% → 10%; two weeks to find.

### 8 · rate+context thresholds additively where CFAR multiplies

Cell-averaging CFAR sets `θ = α · μ̂`; the multiplication is what holds the
false-alarm rate constant as the background moves. Both primaries state it —
Finn & Johnson make the threshold *"proportional to the square root of this estimate
of the output variance"*, Rohling's processor *"multiplies this estimation Z by a
scaling factor T"*.

`rate_detect` fires where `rate − context ≥ excess_threshold_hz`. Additive. So
`θ/μ̂ = 1 + 5/μ̂` — over-conservative when quiet, over-permissive when busy. **It has
a rolling reference window and no constant-false-alarm property.**

Measured symptom: **34.8 probe firings** — third most promiscuous of the six, an
order of magnitude above the two rate-local detectors — at near-leader recall
(0.700). That is a bar too low where the tissue is busy, which is what an additive
offset does.

**This bears directly on the case's item 1.** A detector with no CFAR property is
*exactly* the one whose operating point will not survive a change of background,
because its effective threshold ratio is a function of the background rate. Fixing
the background without fixing this re-fits a detector that will need re-fitting
again at the next background.

### 9 · The learned model has both defects, and the bake-off already measured it

This is the item that surprised me. `nets.py`'s `tube` — the model that leads the
bake-off at F1 0.668 — computes a **difference of Gaussians**, `centre − surround`,
both centred on the same sample. Its own docstring names the construction correctly:
*"It is what every one of the six detectors computes by hand — observed minus
context."*

Two things follow, and both are the classical findings in learned clothing:

- **The surround is centred on the cell under test.** A Gaussian of width *s*
  centred at 0 has its maximum exactly where the event is, so the event contributes
  to the reference estimate that judges it. No guard, and self-masking by
  construction.
- **It subtracts rather than divides.** The docstring claims *"rate invariance by
  construction"* because the area-normalised DoG integrates to zero, so *"a uniform
  rate change cancels"*. That cancels the **mean**. It does not cancel the
  **variance** — for counting noise the fluctuation about zero grows with the
  background rate, so a fixed threshold on a zero-mean-but-rate-scaled signal has a
  false-alarm rate that rises with rate. Which is item 8, in a network.

**Measured, from `bakeoff.json`:** tube **15.8** probe firings, against LoCo 2.5 and
CoactDetect 1.2 — 6× to 13× more firing in a block containing nothing than the two
rate-local detectors, while the two learned models that pool differently fire 0.0.
The prediction and the measurement agree, and the measurement was already in the
file.

⚠ This is an argument from mechanism plus one measured column, not a controlled
test. The controlled test is cheap and is in the plan (Phase 2).

### 10 · The bake-off ranking tracks calibration status, not detector quality

`bench.py`'s own `source` fields: **loco, cicada, coact** are at calibrated points;
**rate, sce, sync** are at untuned defaults. Ranking among the six hand-written:
1st, 2nd, 4th are the calibrated ones; 3rd, 5th, 6th the uncalibrated. Reading that
table as a ranking of detectors reads a confound as a result.

Corroborates the case's item 3 by a different route — that one measures grids that
do not bracket, this one measures where the *fixed* parameters came from.

### 11 · `pick_operating_point` cannot see a knob that does nothing

The case's item 3 counts folds where the sweep hit a grid boundary and the gate
refused. **SPIKE-synch answers 3 of 3 folds** in that table — the gate does not
refuse it. It should.

`docs/todo/2026-08-18-spike-synch-knob-may-not-be-the-knob.md` records why: the
swept knob is `C_threshold` over `(0.005 … 0.12)` while `C_min` sits **pinned at
0.1** above most of that grid, and the synchrony profile is quantised at `k/(n−1)`
so on a 30-ROI field every threshold below 1/29 is the same threshold. On a default
simulation **every value on the grid returns the identical result**.

Look at `pick_operating_point` and the gap is structural:

```python
optimal = [r for r in scored if r.f1 >= best_f1 - 1e-9]
interior = [r for r in optimal if r is not scored[0] and r is not scored[-1]]
if interior:
    return interior[0]
```

Its plateau reasoning is right for a **saturating** plateau (LoCo at F1 1.00 from
99.99 upward — genuinely optimal, no widening helps). It cannot distinguish that
from a **degenerate** sweep where the knob is not the binding constraint: when every
point ties, `optimal` is the whole grid, interior points exist, and it returns
`interior[0]` without complaint. A boundary answer wearing a plateau's clothes.

**Consequence for the bake-off:** SPIKE-synch's 0.254 — currently published in the
README and on the site — is the score of a detector at an operating point chosen by
a sweep that could not choose. Its recall is 0.167 against a mid-pack precision of
0.538: it is not firing wrongly, it is barely firing.

### 12 · Do not change LoCo's combination rule — it is right for this preparation

Worth stating because a naive reading of "adopt CFAR" would change the wrong thing.

Gandhi & Kassam scored five schemes across both nonhomogeneities: *"Although the
false alarm rate performance of the GO-CFAR processor in regions of clutter
transition is **better than that of any other mean-level CFAR scheme**, the detection
performance in the **multiple target environment is quite poor**."* And ordered
statistics, which have *"in general better overall performance"*, specifically
*"lack effectiveness in preventing excessive false alarms during clutter power
transitions"*.

**bugarach's dominant nonhomogeneity is the drug-onset rate transition — an edge.**
That is exactly where greatest-of wins. Hansen & Sawyers price the split at *"0.1 to
0.3 dB"*, so it is nearly free. `maxlt` is well chosen; the fix for its
multiple-target blind spot is **censoring inside it**, not replacing it.

---

## The constraint that shapes every mechanism change: parity is the product

FOUNDATIONS §2: every detector matches its MATLAB original **to 1e-9 in every
mode**, and *"that is what makes the ports citable in place of the originals."*

A guard interval changes the numbers. So does a multiplicative threshold. Done
carelessly, the revision destroys the one property that makes this repository's
central claim true.

**So every mechanism change lands as an additive option, defaulting to the current
behaviour.** `guard_sec=0.0`, `threshold_mode="additive"` — parity fixtures pass
untouched, the port stays a port, and the revised configuration is a **named
alternative operating point** that the bench scores against the original. That also
makes the comparison honest: same detector, one knob, two modes, one bench.

This is not a compromise. It is the only version of the change that leaves the
project able to say what it currently says.

---

## How this maps onto the case's tasks

| case task | status after these findings |
|---|---|
| **A** · does the bench move to the fitted background? | **Unchanged and still the fork.** Nothing here answers it; items 7–9 are orthogonal to which background is used, and *both* need doing. |
| **B** · re-derive sweep grids so they bracket | **Sharpened.** Item 11 adds a class the current gate misses. Widening grids does not fix a knob that is not binding — SPIKE-synch needs `(C_threshold, C_min)` swept together on a grid scaled to ROI count, not a wider `C_threshold`. |
| **C** · re-fit the operating points | **Now downstream of mechanism, not just of A and B.** Re-fitting rate+context before fixing its threshold rule fits a detector that has no CFAR property. |
| **D** · settle the scoring tolerance | **Unchanged, still before C**, and the literature has an answer — see the learned-model section below. |
| **E** · four webapp notes | **Unchanged**, and note 12 (which detectors to tune) gets *more* valuable: mechanism changes multiply the number of sweeps. |
| **F** · three standing items | Unchanged. |
| — | **NEW: the promiscuity probe must be able to fail before C.** See Phase 2. |

---

## The plan

Six phases. Phases 0–3 are prerequisites for the re-fit; 4–6 are what Tony asked
for in order.

### Phase 0 · Decisions only Tony can make

Nothing below starts until these are answered, because each changes what the others
mean.

1. **Does the bench move to the fitted background?** (case item A, unchanged). The
   fork. If yes, B and C are one campaign; if no, the browser should default to flat
   so the two generators agree.
2. **What overlap should count as a hit?** (case item D). Currently 1.5 s against a
   median realized event 0.80 s wide.
3. **New: is the revision allowed to change mechanism, or only settings?** If only
   settings, items 7–9 become documented limitations and the campaign is smaller —
   but it will need repeating. My recommendation is mechanism-inclusive, with the
   parity constraint above making it safe.

### Phase 1 · Mechanism, behind flags, defaults unchanged

Each is small, each is independently testable, and none breaks parity.

- **`guard_sec` in `rate.py`, `coact.py`, `loco.py`.** Default `0.0`. Note the
  subtlety for the two surrogate detectors: the null is a circular shift *within*
  the window, so excising a middle chunk changes the wrap length and each ROI's rate
  inside the reference — **the shift must be defined on the retained span**, not on
  a window with a hole in it.
- **`threshold_mode` in `rate.py`.** `"additive"` (default) vs `"multiplicative"`
  (`θ = α · context`). Cheapest detector in the repo at 0.005 s/fold, currently 0.08
  of F1 below the leaders with a one-line-fixable defect — best return on effort in
  the suite.
- **A guard on the tube's surround** (`nets.py`), or an explicit note that it has
  none. A DoG whose surround is centred on the cell under test is the same defect;
  the learned analogue of a guard interval is a surround with a hole, or a
  ratio-of-Gaussians rather than a difference.
- **Do not touch LoCo's `maxlt`** (item 12).

**Exit criterion:** parity fixtures pass unchanged at the defaults, and each flag
changes the output when set.

### Phase 2 · Benchmark, so the re-fit has something honest to fit against

- **The fitted background**, if Phase 0.1 says yes (case item A).
- **Make the promiscuity probe able to fail.** Today its firings leave both numerator
  and denominator, so CICADA's 214.8 in an empty block cost it nothing — recorded in
  `docs/todo/2026-08-16-promiscuity-probe-cannot-fail.md`. **This must land before
  the re-fit**, or the campaign re-selects operating points against a score that
  cannot see promiscuity, which is the very thing items 7–9 are about.
- **The controlled test for item 9:** the tube against a rate step, with and without
  a guarded surround. One bench run; settles whether the mechanism argument is real.
- **Grids derived rather than widened.** CFAR's organising idea is to choose the
  false-alarm probability *first* and derive the threshold multiplier from it. That
  is compatible with this repo's rule — `bench.py` forbids picking a point *"from
  whatever makes a curve look like a curve"* — because a stated `Pfa` fixes the
  target **before** the sweep rather than reading it off the curve.

### Phase 3 · Close the gate gap

`pick_operating_point` should raise a **distinct** error when the sweep is
degenerate — when `max(f1) − min(f1)` across the whole grid is within noise, the
knob did nothing and the answer is meaningless regardless of where it sits. Distinct
from `EdgeOfRange`, because the remedy is different: not "widen the grid" but "sweep
a different parameter". Self-test fixture: SPIKE-synch's own grid.

Cheap, and it stops item 11 from recurring silently.

### Phase 4 · The re-fit

Now, and only now: re-derive grids and re-fit operating points, at the chosen
background, against the chosen tolerance, with the probe entering the score, in both
mechanism modes so the comparison is measured rather than assumed.

Budget note from the case: LoCo and CICADA are **97%** of the sweep's wall clock
(fit seconds: sync 0.06, coact 0.08, rate 0.10, SCE 0.17, **LoCo 2.69, CICADA
7.06**), which is why webapp note 12 — sweep a subset — is worth landing first.

Everything in `bakeoff.md`, every figure quoting an operating point, and the site's
scoreboard become stale together. Plan to regenerate them in one pass rather than
discovering them one at a time.

### Phase 5 · The website

- Regenerate the scoreboard and bake-off figures from the re-fit.
- **Correct SPIKE-synch's published number** — the README and the site currently
  report 0.254 as its accuracy, and per item 11 that is the score of a degenerate
  sweep. This is a correction to a published table and does **not** need to wait for
  the campaign.
- The scoreboard copy review and the site-staleness check are already tracked
  (case item F) and gate publication.

### Phase 6 · Run the re-optimization as a new user

The point of this phase is that it is the **only** end-to-end test of the claim the
README makes — that a lab that has never heard of this project can point it at its
own folder. Do it as the loop documents it: measure an untreated recording without a
detector → derive the generator spec → tune and train on that simulated baseline →
detect.

Two things to watch, from this session's other threads:

- **Record the view.** If any human judgement enters — reading a raster to sanity-
  check a detection — the rendering is an uncontrolled variable, and the browser
  currently lets a caller rescale time continuously without recording where they
  were. See
  [`train-on-human-called-events`](2026-08-22-train-on-human-called-events.md) and
  [`the wheel zooms`](2026-08-22-the-wheel-zooms-but-three-places-say-it-does-not.md).
- **Write down what a new user cannot find out.** The value of doing this as a new
  user is entirely in what is missing or confusing; that is the deliverable, not the
  numbers.

---

## The literature's advice for the learned model

Tony asked. There is advice, it is on the shelf at `<darkroom>/bugarach/lit/DL/`,
and **the tube already follows the structural half of it** — which is worth knowing
before anyone changes the architecture.

**Followed, and structural rather than accidental:**

- **Zaheer et al., "Deep Sets" (2017).** Any permutation-invariant function over a
  set can be written `ρ(Σ φ(xᵢ))` — encode every element with the *same* φ, sum,
  decode. This is why the input layer is per-ROI with shared weights rather than
  `n_roi` wide, and why ROI-count independence is a property of the architecture
  instead of a preprocessing trick. The tube's `bright = pooled.sum(dim=1) / n` is
  exactly this, and the docstring calls it *"space invariance"*.
- **Qi et al., "PointNet" (2017).** The same construction reached independently for
  point clouds, pooling with **max** rather than sum. The shelf's note is that max
  pooling is structurally bugarach's distinct-ROI rule — one element, one vote. The
  tube implements it literally: `max_pool1d` per cell inside the centre window
  before the sum, so *"a single cell bursting cannot imitate a crowd"*.

**Available and not yet adopted:**

- **DOSED's δ-swept IoU scoring.** The coordination shelf records it as
  *"bugarach's open question, answered"*: report precision, recall and F1 for **IoU
  δ swept 0.1 to 0.9**, re-selecting each competitor's operating point at every δ,
  so scoring tolerance becomes a reported curve rather than a hidden constant. That
  is **a direct answer to Phase 0.2 / case item D**, and it is the single most
  useful unadopted thing on either shelf.
- **All three learned event detectors — DOSED, cnn-ripple, SEED — train on human
  expert labels.** bugarach is deliberately the odd one out. The todo for doing both
  is [`train-on-human-called-events`](2026-08-22-train-on-human-called-events.md),
  and its first step is a psychophysics sweep, not a labelling UI.

**New, and not in the DL shelf because the radar shelf did not exist when it was
written:** item 9 above. The centre-surround the tube is built on is a
reference-window construction, so the guard-cell and multiplicative-threshold
findings apply to it exactly as they apply to the three classical rolling detectors.
The DL shelf should carry a pointer to `lit/radar/`; they are about the same
machine.

---

## What must not happen

The case document's three, restated by reference and not weakened —
**do not raise `min_rois` until false alarms go away** (FOUNDATIONS §9), **do not let
a detector choose its operating point on the data it is scored on**, **do not read
the tie at the top as a win**. Plus two from this side:

- **Do not break parity to fix a mechanism.** Every change is a flag defaulting to
  current behaviour, or the ports stop being citable and FOUNDATIONS §2 stops being
  true.
- **Do not adopt "CFAR" as a slogan and change the wrong thing.** Item 12: greatest-of
  is *correct here*, and the primaries say so specifically for the nonhomogeneity
  this preparation actually has.
