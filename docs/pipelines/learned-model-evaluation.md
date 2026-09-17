# Pipeline: learned-model evaluation

**Use it when** a new learned architecture exists and someone needs a number for it that will be
quoted, compared, or decided on.
**It produces** a bake-off position against the detectors already in the tree, a label-free and a
truth-reading operating point, a real-recording consistency check, two figures, and a murderboard
run record.
**Cost:** roughly one overnight at `--jobs 12`; the training stage dominates.

> **Working material, not murderboarded.** Same standing as [`../pipeline.md`](../pipeline.md) and
> the handoffs: for sessions in this tree.
>
> ⚠ **This is not [`../pipeline.md`](../pipeline.md).** That page is the *product* loop — what the
> app does for a lab, dictated by Tony on 2026-09-04. This is one of several **pipelines**: named,
> repeatable routes to a particular kind of result. The repo has already lost a session to one page
> being read as another ([`../INDEX.md`](../INDEX.md) carries that ⚠ for `workflow_plan.md`), so
> the distinction is worth keeping sharp.

**This route is not hypothetical — it is the one that was run.** On 2026-09-15/16 the `line`
architecture went from written to reported overnight by exactly these stages. The tables it
produced were right: every machine-generated cell reproduced under audit. **Every defect was in the
hand-typed prose around them**, and two of them inverted the decisions the report was asking for.
Eleven blind reviewers found fifty-one. The gates below are that night's findings turned into
steps, so the next run does not pay for them again.

## The route, as commands

One folder per run; each stage writes into it. The gate on each stage says whether the next one is
worth starting.

```bash
D=docs/learned/<run-name>            # one folder, one run
PY=<venv>/bin/python ; export PYTHONPATH=src

# 1  register the architecture and its ablation      (code change, no command)
# 2  what does the contrast already contain, before anything is trained on it?
$PY tools/tube_aggregate_leak.py       --out $D/aggregate_leak --jobs 12
# 3  controls that can fail (the leak cells; destruction lives in the rigid-shift look)
$PY tools/look_rigid_shift_controls.py --role steps_excluded --leak-only --out $D/controls_lab --jobs 12
# 4  supervised bake-off, against the ablation AND the hand-written detectors, at three seeds
for s in 0 1 2; do
  $PY tools/fair_bakeoff.py --spec docs/learned/generator_spec.json --train-seed $s --out $D/bakeoff_seed$s
done
# 5  label-free training: every arm, both displacements, the zero-parameter baselines
$PY tools/tube_self_supervised.py      --out $D/training --jobs 12
# 6  real recordings — this stage WRITES the checkpoints; the probe then reads them
$PY tools/tube_ssl_real_compare.py --out $D/real_compare \
                                   --checkpoints $D/real_compare/checkpoints --jobs 12
$PY tools/probe_line_vs_fuzz.py    --out $D/probe \
                                   --checkpoints $D/real_compare/checkpoints
# 7  every number the report will quote, then the figures, which read it
$PY tools/summarize_tube_self_supervised.py --run $D
#    each figure tool writes to the darkroom by default; --also keeps the repo copy
$PY tools/make_surrogate_schematic_figure.py --also $D
$PY tools/make_rigid_shift_gates_figure.py --run $D --also $D
$PY tools/make_line_sensors_figure.py      --summary $D/summary.json --also $D
$PY tools/make_tube_ssl_figure.py          --summary $D/summary.json --also $D
$PY tools/make_tube_real_summary_figure.py --summary $D/summary.json --also $D
$PY tools/make_tube_real_lanes.py     --run $D/real_compare --out <darkroom> --family <name>
# 8  murderboard, blind round, loop until clean
```

**Smoke-test the whole chain first.** Stages 2–6 all take `--quick`; run the route end to end with
it before committing a night to it. A chain that fails at stage 6 after five hours is the expensive
way to learn that a flag moved.

⚠ **`--checkpoints` on stage 6 is a write, not a read** (*"save the self-supervised fits here"*).
The probe reads what that stage saved, so the two paths must match and the order is fixed.

⚠ Several of these tools are named for `tube`, the architecture they were first written for, and
are **not** tube-specific — `tube_self_supervised.py` and `tube_ssl_real_compare.py` sweep the whole
registry. The names are debt, not scope.

---

## The stages, and the gate on each

A stage skipped is a stage **reported** as skipped — not silently absent.

---

## Stage 1 — Register it, and make the roster self-reporting

Add the architecture to `src/bugarach/learn/nets/` with its `@register` line, and register the
**ablation** beside it in the same commit, so every sweep measures both in the same run rather than
in a later one nobody runs.

**Gate — every sweep records what it did *not* run.** Write `registered: sorted(ARCHITECTURES)` and
`registered_but_not_run` into each stage's `meta.json`, the way `tools/fair_bakeoff.py` already
does and `tests/test_registries_do_not_drift.py` already polices.

> *The incident:* five tools hand-copied their model tuple and none recorded the roster. A figure
> plotted **two** architectures under a caption that said four, and shipped — because "skipped" and
> "absent" were indistinguishable in the record. Four reviewers found it after the fact.

## Stage 2 — Ask what the contrast contains before you train on it

Before any model is trained against a surrogate, run a **dumb classifier on aggregate channels
alone** — the pooled trace, simple summary statistics — on the same real-vs-surrogate contrast.
Whatever it scores is the floor that every later number sits on.

**Gate — report the aggregate score with its confidence interval, and name the channel honestly.**
If the interval reaches the trained models' scores, the models are **not separable** from the dumb
baseline and no "the model learned X" claim survives.

> *The incident, twice over:* the pooled channel reached 0.66–0.67 where the trained models reached
> 0.73–0.75, and the report said "most of what these models learned needs no cross-ROI structure".
> Two errors. The interval ([0.62, 0.72]) reaches the models, so "most" quantified a gap that was
> not resolved — and **the pooled trace *is* the share of the field that is lit**, which is exactly
> what the architecture computes. The test excluded pairwise and identity structure, not
> co-activity. Know what your own channel is before you write what it rules out.

## Stage 3 — Controls that can fail

Every null needs a positive control. Run all three:

- **The matched control** — a transform that moves what the surrogate moves while preserving what
  it is supposed to destroy (a shared offset, where the surrogate uses per-ROI offsets). It should
  read chance.
- **The graded control** — a partial version (freeze half the ROIs, shift the rest). It should read
  *between* the endpoints, which is what shows the measure registers partial removal at all.
- **The endpoints** — the fully destroyed and the untouched recording, which should read 0 and 1.

**Gate — demonstrate the control can fail *on the stream you will actually use*.** A control that
reads chance for the surrogate **and** for its own null on that stream has not been shown to have
any power there; it is an untested instrument, not evidence.

**Gate — report the tie share of any paired comparison.** Translation-equivariant models compared
on crops taken at the same index from a globally-shifted raster are largely comparing identical
frames.

> *The incident (first report, 2026-09-16):* the shared-offset control read 0.49–0.53 and was
> presented as excluding a per-ROI leak. On the lab fast stream — the stream the whole experiment ran
> on — **the same classifier never rose above chance for the surrogate either**, at any
> displacement. And 26–42 % of its comparisons were ties. It also could not, by construction,
> detect the one leak the run did find.

**Gate — name the alternative each control rejects, and construct its opposite.** A positive
control shows power only against the failure it was built to produce. Write down, for every null
check, the most plausible thing other than the effect that would also make it pass, and build the
input that has that thing and not the effect. If the check passes on that input too, it cannot tell
the two apart.

> *The incident (third murderboard of the same report, 2026-09-17):* the controls had been repaired
> to carry positive controls — per-onset dither in the per-ROI test, a thinned copy in the paired
> checks — and all of them passed. A reviewer built a scorer with **no events at all**, only a slow
> rate change shared by every ROI, and ran it through the paired checks: every one passed. Dither
> breaks same-ROI intervals, which rigid shift never does, and thinning moves counts; neither is
> the alternative that mattered, which was slow co-modulation. The stationary synthetic twin could
> not fail under rigid shift at all. The repair that answered it was a small-displacement shift
> (slow modulation survives it, sub-second alignment does not), twins that carry shared and
> independent modulation, and zero-parameter scorers run through the same checks.

## Stage 4 — Supervised bake-off, against the right comparators

Fit the model with labels on the simulator and score it on held-out folds, beside **two** sets of
comparators:

1. its own **ablation**, and
2. the **hand-written detectors already in the tree** (CoactDetect, LoCo, the ports).

**Gate — report paired per-fold differences, not just means.** With four folds, give the
differences and a `t`. State when one fold carries the mean, and say what the margin becomes
without it.

**Gate — the comparison that licenses the work is against the hand-written detectors**, not against
the ablation. "Is the second sensor worth it" is a smaller question than "does the learned family
earn its place at all", and only the second decides whether any of this ships.

**Gate — attribute every cost to the comparison it belongs to.** Fit time, detect time and probe
firings each belong to a named pair.

> *The incident:* "fitting is eight times slower" was offered as the argument **against** keeping
> the second sensor. The eightfold cost was the *family* against `tube`; against its own ablation
> the sensor cost **1.4 %**. The decision brief was wrong by about 560×. Separately, the report
> never made the CoactDetect comparison at all — and when a reviewer ran it, the ablation was
> **statistically indistinguishable** from the detector the project already had (+0.005, t(3)=0.34).

## Stage 5 — Label-free training, if that is the goal

**Gate — always two thresholds, never one.** A **label-free** threshold (the lowest at which the
model fires at most a stated rate on *that recording's own* surrogates) and a **truth-reading**
threshold (F1-best on validation, which reads planted truth and is a ceiling, not a usable rule).
Reporting either alone misleads in a predictable direction.

**Gate — the threshold picker carries an edge-of-grid guard.** An optimum at the first or last grid
point means the search stopped while still climbing; `pick_threshold` in
`src/bugarach/learn/train.py` already warns on this, and a re-derived picker that drops the guard
will pin to the grid floor silently.

**Gate — run the untrained control for *every* model, and check each one is actually collapsed.**

> *The incident (first report, 2026-09-16):* the untrained arm was dismissed as "no working
> baseline", quoting two of four models. Untrained `line_length` scored 0.272 at the label-free
> threshold — beating **nine of the sixteen trained cells** — and untrained `tube` at the
> truth-reading threshold beat **every** trained cell. The claim that run supported was narrower:
> training did not beat random initialisation. ⚠ The rerun of 2026-09-16/17 overturned even that at
> the stricter label-free rates, and found the untrained arm's truth-reading score came from
> detections covering most of each recording — see the report, not this incident, for the result.

**Gate — measure the untrained arm's detections, not only its score, and add a detector that fires
with nothing learned.** An untrained network that fires nothing, or fires everywhere, is not the
comparator a claim that "training bought something" needs. Record detection width and the share of
the recording covered, and run a zero-parameter count scorer through the same thresholds.

## Stage 6 — Real recordings

Nothing in the corpus is annotated, so this is a **consistency check and never a score**.
`docs/MILESTONES.md` blocks quoting a transfer figure until a MAHICE review exists.

**Gate — both directions of agreement.** "Share of the reference's events caught" rewards firing
more. Give the reverse share beside it, and the event rates, so promiscuity is visible.

**Gate — chance rates computed at the *same* window as the column they sit under.** A random-time
baseline at ±1 s does not belong under a ±2-frame column.

**Gate — a window-edge check.** Histogram detections by distance to the nearer window edge against
the uniform expectation, for every detector including the references.

> *The incident:* the ±1 s chance row was copied into the ±2-frame column, inflating that baseline
> two- to threefold and making a rigid-shift row read as at-chance when it sat above it. And the
> edge shares were wrong at both ends, in both windows, with the mechanism attributed to a stage
> only one architecture has.

## Stage 7 — Figures, before the prose

**Gate — draw every model the caption names.** If a measured comparison is not drawn, the caption
says so and why.

**Gate — do not borrow a visual idiom that asserts what you are denying.** A dot with a range bar on
a stacked categorical axis is forest-plot grammar: the bar reads as a confidence interval and
non-overlap reads as significance. If the claim is "this ordering is not separable", plot the folds
as points.

**Gate — if a finding is visual, render it** (`CLAUDE.md`). `bugarach.ui.diagnostic` draws lanes
above a raster and `tools/make_real_detection_figure.py` and `tools/make_tube_real_lanes.py` already
wrap it. Nothing is ever drawn on the raster.

**Gate — real rasters go to the darkroom, never the repo.** FOUNDATIONS §5 releases exactly one real
image by name and calls the exception *"a list of one, not a category"*. Link it by name; do not
embed it, and do not extend the exception by analogy.

> *The incident:* `fuzz` was measured for every model and plant size, named in the caption, and gave
> the probe tool its name — and was **drawn nowhere**, because the constant listing the plants was
> never read in `main()`. The caption and the source both survived its absence, which is what made
> it read as deliberate.

## Stage 8 — Murderboard, then a blind round, then loop

**Gate — if a number is in the prose, it must be in a file.** Anything quoted that no shipped
artifact records cannot be checked and will not survive a reviewer who tries.

**Gate — record provenance for what actually ran**, not for what the library would have done. Which
code generated the surrogates, which version, which seed, which parameters were fitted versus fixed.

**Gate — `/murderboard <artifact>` before the deliverable goes anywhere**, then **a blind round on
the repaired artifact**, and iterate until a blind pass returns nothing new. A repaired deliverable
has not been reviewed.

**Gate — if the loop stops early, the run record says so.** `Mode: retrospective` plus the stopping
reason; `tools/murderboard_roster.sh check --require-reports --require-mode` and
`tools/murderboard_agents.py verify` both gate the record.

> *The incident:* round one found eleven defects and they were repaired. The blind round found
> **fifty-one**, including two inverted decision lines, a misattribution the repo had deliberately
> avoided three weeks earlier, and a provenance claim crediting a third party's library for code
> written here. The repair had not reached the substance, and only a blind pass could show that.

---

## The short version

| # | stage | the gate that matters most |
|---|---|---|
| 1 | register it | the sweep records what it did **not** run |
| 2 | what does the contrast contain | a dumb aggregate classifier, with its interval |
| 3 | controls | show they can **fail**, on the stream you will use |
| 4 | supervised bake-off | paired differences, against the **hand-written** detectors |
| 5 | label-free training | two thresholds, an edge-of-grid guard, every untrained arm |
| 6 | real recordings | both directions, matched chance windows, an edge check |
| 7 | figures | every model drawn; real rasters to the darkroom only |
| 8 | murderboard | blind round after the repair; loop until clean |

**The one-line rule underneath all of it:** the machine-generated tables are usually right. Check
the sentences.
