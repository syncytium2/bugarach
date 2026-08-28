---
status: open
filed: 2026-08-16
---

# The assessment will need a human to judge it, and nothing yet lets one

> ## ⚠ Escalated 2026-08-24 — this is not a feature to add, it is what the assessor **is**
>
> Tony, 2026-08-24:
>
> > *"The assessor should be machine and human working together to find coordination.
> > There's no ground truth and I shouldn't have allowed the idea of an independent
> > assessor."*
>
> The entry below was written as *"this might require human interaction to judge the
> assessment (a feature to add at some stage)"* — a review surface bolted onto an
> instrument that otherwise stands alone. **That framing is withdrawn.** There is no
> autonomous assessor whose output a person optionally checks; the instrument is the pair,
> and a number produced without a person having looked is not a weaker result of the same
> kind — it is not a result.
>
> **Three things this changes, and one it does not.**
>
> **Vocabulary.** *"Ground truth"* stays correct for **planted** events in a simulation —
> those are known by construction, and `score.py` and `simulate.py` use the term properly.
> It is wrong for anything the assessor says about a **real** recording, and the slide is
> already in the tree: `webapp_completion_plan.md` justifies the K screen as what makes
> *"optimized to the same ground truth"* a true statement, and the treatment-contrast note
> opened by listing *"it sets the ground truth"* as the assessor's first job. The second is
> corrected; the first is flagged and left, because the phrase wants one pass with a
> decision behind it rather than six sessions each guessing.
>
> **What the output has to carry.** The machine half already refuses to decide, and says so
> well: `assess_folder` prints *"K is a scan, not a choice"* and that *"nothing here has
> turned a measurement into a setting — that needs somebody who has looked at the
> recording."* The browser goes one step further and holds *"the K a person accepted"* —
> **in a variable**. So the decision exists, briefly, and nothing writes it down. An
> assessment is now a **record with a person's judgement inside it**, not a number with a
> caveat beside it, and that is the same fix as
> [`tuned settings are a file`](2026-08-22-tuned-settings-are-a-file-not-a-survivor.md).
>
> **The view is part of the judgement.** From
> [`train on human-called events`](2026-08-22-train-on-human-called-events.md): *"the human
> calls depend on psychophysics of the raster. Stretch it one way and nothing, compress
> another and suddenly they are easy to see."* A call is a property of
> (recording × rendering × observer). If a person's look is constitutive of the assessment
> rather than a check on it, **the rendering they looked at is part of the record** — and
> the browser currently lets a caller rescale time continuously without recording where
> they were.
>
> **What does not change.** The machine half is still held to 1e-9 against
> `measure_coordination_timescale.m`; parity is faithfulness of the arithmetic and is
> untouched by who reads the output. The assessor still breaks the
> detector → simulation → detector circle — it simply is not an oracle while doing it. And
> treatments still may not parameterize the generator.
>
> **One consequence for a test that was about to be written.** A check that the assessor
> *recovers planted events* is partly circular here: the simulation is built to the
> assessor's own convention, so recovery is the convention agreeing with itself. What
> survives cleanly is the **null** — plant nothing, and the excess must read zero. A
> rate-matched null that leaks is a defect in the machine half whatever convention sits on
> top, and every generator spec derived afterwards inherits it. Write that one, and
> describe it as a check on the arithmetic, never as validation of the assessor.
>
> **Open: whether this belongs in an ADR rather than a todo.** It reverses a premise and
> constrains vocabulary repo-wide, which is ADR-shaped; it is recorded here because this is
> where the subject already lives. Tony's call.

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
