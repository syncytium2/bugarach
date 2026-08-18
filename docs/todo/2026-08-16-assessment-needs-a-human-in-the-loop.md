---
status: open
filed: 2026-08-16
---

# The assessment will need a human to judge it, and nothing yet lets one

> **Half of this landed 2026-08-18.** `bugarach assess <folder>` runs the
> assessment over a lab's own export folder and prints **the scoreboard** — the K
> scan side by side, `jit_defined` rendered as *undefined (no cluster in
> surrogates)* rather than as a number, a window under the floor reported with no
> numbers at all, and non-baseline regions counted and skipped. So the judgement
> calls below are now **visible to a person**, which they were not before.
>
> **The figure is still missing, and so is the accept step.** What is described
> under *What the feature probably is* — the raster with clusters marked, the
> per-bin observed-vs-null trace, the cluster-SD distributions — is not built, and
> neither is the part that matters most: **nothing records what the human decided
> next to the parameters it produced.** Until that exists, the promotion gate this
> todo asks for is still open, and the entry below stands unchanged.

Tony, 2026-08-16, approving the assessor port:

> *"port the assessor, but recognize that this might require human interaction to
> judge the assessment (a feature to add at some stage)."*

Filed at the moment the port landed so it does not get discovered later as a
surprise. `bugarach.assess` is a measurement with no review surface at all: it
returns numbers, and a caller — including the generator-parameterization step —
consumes them without anyone ever having looked at the recording they came from.

## Why a human is genuinely needed here, not just prudent

The assessment is **not** a detector, so there is no operating point to check.
What it has instead are judgement calls that only a person looking at the data
can settle:

- **K is a convention, and it changes the answer.** `min_rois` is reported as a
  scan (`3, 4, 6, 8`) precisely so the choice stays visible. Something has to
  pick one before the generator can be parameterized, and on the synthetic
  fixture the scan runs from 2.7 clusters/min at K=3 to 0.25 at K=8 — a 10-fold
  range in the quantity that becomes the generator's event frequency.
- **`jit_defined` can be False while `jit_obs` is a finite number.** The
  surrogate ensemble formed no cluster, so the tightness comparison does not
  exist even though a number is sitting there. Verified on the fixture at K=8
  and pinned by a test. A pipeline that reads the number and not the flag will
  parameterize tightness off nothing, silently.
- **A window can be dominated by one stretch.** The measure is applied inside a
  "roughly stationary" window, and nothing checks that it is. A drifting or
  half-dead recording returns a confident number.
- **The bin width interacts with what counts as one event.** 0.5 s and 2 s are
  both defensible and give different cluster counts.

## What the feature probably is

Not a dialog box. The pattern this repo already has is a **figure plus a
scoreboard** — `tools/make_diagnostic.py` renders detector lanes over the ROI
raster with the analysis trace beneath. The assessment's equivalent:

- the raster, with the co-active clusters the assessment found marked on it,
- the per-bin observed coactivity against the null mean (the explainer's panel B),
- the observed-vs-surrogate cluster-SD distributions (panel D), with
  `jit_defined` shown as a state and not as a NaN,
- the K scan side by side, so the reader picks K having seen its consequence,
- and an accept/annotate step whose output travels with the parameters.

The last part is the one that matters for the learned-detector work: **whatever
the human decides has to be recorded next to the generator parameters it
produced**, or the model's provenance stops at "some numbers". That is the
promotion gate `simulation_plan.md` §8 asks for, arriving one layer earlier than
expected — *refuse to mark a dataset production while its measurements are
unreviewed.*

## Why it is not blocking today

The port is a measurement and writes nothing. Every consumer so far is a test or
a parameterization run a person is watching. It becomes blocking the moment a
model is trained on assessed parameters and the resulting detector is offered to
anyone — because at that point an unreviewed measurement has been baked into a
model instead of into a config file, which is `simulation_plan.md` §6's exact
warning.

## Related

- `docs/todo/2026-08-15-draw-the-pipeline-instead-of-describing-it.md` — same
  instinct, different surface.
- The MATLAB side already has the explainer panels
  (`<darkroom>/constellation/assessment_explainer_{1_stat,2_null,3_window}.png`).
  They are the model for what the Python review view should show, and they are
  worth reading before designing it rather than inventing a new vocabulary.
