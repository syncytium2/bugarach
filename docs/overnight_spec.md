# Overnight work — what can run unattended, and what must not

> ## ⛔ NOT APPROVED. Nothing here is authorised to run.
>
> **Status: proposal, awaiting Tony.** Written 2026-08-17 at his request —
> *"prepare the spec but do not run"* — while he was going to sleep and explicitly
> not in a position to approve anything.
>
> If you are a session that found this file through the briefing or a todo scan:
> **this is not a work order.** It reads like one on purpose, because it is meant to
> be executable the moment it is approved, and that is exactly what makes it
> dangerous to leave unmarked. Track B spends real compute, Track C touches an
> external dataset, and Track A changes the app's entry point. None of it has been
> agreed.
>
> **What you may do without approval:** read it, and correct it — every quantity in
> it is checkable and four were wrong in the first draft.
> **What needs Tony first:** running any of it.

**Read [`docs/workflow_plan.md`](workflow_plan.md) first.** That plan already specifies
the app's milestones — folder reader, uniform yardstick, fitting stage, writers, batch,
comparison — and it has been through the murderboard. This file does not restate it. It
answers a different question: *which work can proceed with nobody watching, and in what
order.*

## The constraint that shapes everything

**Overnight means no human, and the pipeline has a decision in the middle of it.**
Choosing K — the cluster size the assessment runs at — moves the corpus materially
(K=3 was chosen; K=4 drops the cluster rate to roughly a quarter of it) and `derive_spec.py` refuses to choose,
deliberately. So any track that runs through that point either stops at it or fabricates
the judgement.

Everything below is sorted by that test, not by importance:

| | can run unattended | why |
|---|---|---|
| **compute sweeps on an existing spec** | ✅ yes | no decision inside; every output is a JSON that a human reads in the morning |
| **infrastructure with tests** | ✅ yes | correctness is checkable by the suite, not by taste |
| **choosing K, approving a corpus** | ❌ no | a judgement, and the whole apparatus exists to keep it visible |
| **shipping a document** | ❌ no | the murderboard's blind rounds need a reader; drafting is fine, shipping is not |
| **writing to the darkroom** | ⚠ with a board claim | shared across machines; see the collision note at the end |

## Track A — infrastructure, unattended-safe subset

Milestones from `workflow_plan.md` Part II, marked for overnight suitability. Do these
first; the model work in Track B is more interesting and less useful, because a model
refined on a pipeline nobody can run is a result nobody can reproduce.

1. **The folder reader** — ✅ safe. It is mechanical and the plan names its traps: a
   conforming folder is *one* input rather than a pile of CSVs, the `slice_id` and
   `stream` columns are currently ignored, and `frame_interval_sec` must reach **all
   three** detectors that assume it, not just the one that warns. That last item is the
   one to verify with a test rather than by reading — a lab imaging at 20 Hz currently
   gets one warning and two quietly wrong answers.
2. **The uniform yardstick** — ✅ safe. Build the synthetic oracle through
   `tools/matlab_ref/` so it travels; the per-event export is the local second check and
   cannot be committed.
3. **The writers** — ✅ safe. This is what makes the app finish rather than display: a
   table a statistician can open. Nothing in the tree writes a data file today.
4. **Batch** — ✅ safe, and it is the multiplier for everything in Track B.
5. **The fitting stage** — ⚠ **build up to the decision and stop.** Everything before
   "choose K" is unattended-safe; the choice is not. Leave the run parked with the scan
   written out, and have the morning session pick.
6. **Screens and the seam** — ❌ not overnight work. The plan leaves them unspecified
   deliberately.

## Track B — model refinement, and what today's results imply

All five are compute-bound, none contains a judgement, and each writes a JSON whose
shape a human can check in a minute. **They are also embarrassingly parallel**, which is
what makes them the right use of an unattended night.

### B1 · Close the seed gap — highest value, least interesting

Every learned number in this project is **one training run per fold**. Fold spread
therefore confounds data variation with training variation, and this caveat has been
carried, unresolved, through every report. It is the cheapest thing that could change a
conclusion and it has never been done for one reason: it needs compute and patience,
which is precisely what an unattended night is.

- **Run:** `tools/fair_bakeoff.py` with **≥5 seeds per fold** rather than one, for every
  learned model, and re-emit `bakeoff.json` with a seed axis alongside the fold axis.
- **What it settles:** whether the tie at the top is a tie. Currently 0.668 ± 0.061
  against 0.651 ± 0.044 with n=4 and no seed replication.
- **What would change a conclusion:** if seed variance is comparable to fold spread,
  every interval in every report is wider than stated and the "ties" language must get
  stronger, not weaker.
- **Cost, and a choice inside it.** Centre−surround and pooled trace fit in 5.6 and
  8.0 s, so 5 seeds × 4 folds of both is about five minutes. The per-cell bank costs
  **236 s a fit** — the same sweep for it is 80 minutes on its own, for a model that
  sits at the floor and whose threshold lands on the edge of its grid. Run it anyway
  *once* overnight, because "it does not train" is currently a single-seed claim about a
  model we have already written off, and writing something off on n=1 is how it stays
  written off.
- **Do this one first.** Every other result below inherits its error bars from it.

### B2 · The event-rate ceiling — the falsifiable prediction

The fitted surround runs 21–59× the centre, i.e. **97–181 samples, 9.7–18.1 s
wide** at this corpus's frame interval, and that surround *is* the model's background estimate. If coordinated events
arrive faster than the surround is wide, the surround averages neighbouring events into
"background" and the model subtracts signal from itself.

- **Predicts:** performance degrades as inter-event interval approaches surround width,
  and the degradation is specific to centre−surround — the six should not show the same
  knee at the same place.
- **Run:** raise the **event count**, not the separation floor. The corpus plants
  `n_per_level = (5, 5, 5)` — 15 events in 3,525 s, a mean interval of **235 s** — and
  `min_sep_sec` is 171. Lowering `min_sep_sec` alone *permits* closer pairs without
  producing them: the mean interval is set by count over duration and would not move,
  so the sweep would have run and shown nothing, for a reason having nothing to do with
  the model. **Sweep `n_per_level` up** — (5,5,5), (10,10,10), (20,20,20), (40,40,40),
  (80,80,80) — giving mean intervals of about 235, 118, 59, 29 and 15 s, and lower
  `min_sep_sec` at each step so it never binds before the interval you are targeting.
  Score all nine detectors per point, and plot F1 and precision against **mean
  inter-event interval** with the fitted surround width drawn on the axis.
- **Reuse:** `tools/ablate_tube.py` is the closest template — it already runs variants
  through the bake-off's folds and scorer. A `--sweep min_sep_sec` mode is a smaller
  change than a new tool.
- **Check the control before believing the result:** more events per recording also
  means more chances to fire, so recall can rise for reasons unrelated to the mechanism.
  The mechanism-specific signature is **precision** falling as the interval crosses the
  surround width, and it falling **for centre−surround and not for the six**.
- **What would change a conclusion:** a knee near the surround width converts "the model
  transfers badly to busier backgrounds" from a puzzle into a mechanism, and makes the
  surround width an operating constraint the app must expose. **No knee** is equally
  useful and would retire the hypothesis.

### B3 · The width ceiling

`max_center_frames=128` clamps the centre to k/2 = **64 samples, about 6.4 s**. Events
wider than that cannot be fitted; the model will sit at the clamp and report a width
that is a wall rather than an answer — the exact pattern the surround-ratio chase just
followed.

- **Run:** sweep the generator's event width (jitter, currently 0.31 s) upward through
  roughly 0.5, 1, 2, 4, 8, 16 s, re-fitting each time, and plot **fitted centre against
  planted width** with the clamp drawn as a line.
- **What good looks like:** fitted width tracks planted width, then flattens at the
  clamp. Where it flattens is the model's usable range and belongs in the app's
  documentation.
- **Cheap dependency:** raise `max_center_frames` in a second arm so the clamp is not
  confounded with the capability.

### B4 · The corpus that could vindicate the multi-scale bank

The bank collapsed to one scale and one scale scored identically — **on a corpus that
plants a single event width**. That is a property of the generator, not a verdict on the
design.

- **Run:** a corpus with **two or three distinct event widths present simultaneously**
  (e.g. 0.3 s and 3 s events interleaved), then the same 1-vs-2-vs-4-scale ablation.
- **What would change a conclusion:** scales that separate and a four-scale model that
  beats one-scale would restore the multi-scale design. Scales that still collapse would
  retire it for good, and 81 parameters come out of the shipped model.
- ⚠ **This one needs a generator change**, not just a parameter — the generator plants
  one participation/jitter set per recording. Check whether interleaving widths is a
  config change or a code change before scheduling it; if it is code, it is a morning
  task with a review, not an overnight one.

### B5 · Drop the raw brightness channel

Carried unresolved from the 16 August handoff. The centre−surround head takes the raw
brightness trace as a fifth channel alongside the four filtered ones. That channel never
had its background subtracted, so it is a candidate explanation for the transfer
asymmetry that the clamp hypothesis failed to explain.

- **Run:** one arm with the bypass removed, through the bake-off folds and the transfer
  test.
- **One line of code**, and it either explains section 5 or eliminates the last cheap
  explanation.

## Track C — a second corpus from DANDI

**Worth doing, and worth being precise about what it buys.** A DANDI dataset carries no
coordination ground truth, so it **cannot score a detector**. What it can do is supply a
*second set of statistics* to fit a generator to, which answers a question nothing here
has touched: do these conclusions survive a corpus that is not ours?

Ordered, with the human checkpoints marked:

1. ❌ **A human picks the dandiset.** Preparation, indicator, frame rate and species all
   change what the numbers mean, and a wrong pick produces a confidently fitted generator
   for a preparation nobody intended. Name it, with the DOI, on the board.
2. ✅ **Read it.** NWB, so a reader is needed; check whether the events are onsets or
   fluorescence, because this project's whole pipeline consumes **onsets** and a
   fluorescence set needs an event-extraction step that is somebody else's method and a
   confound in every downstream number.
3. ⚠ **Frame interval — verify, do not infer.** It sets the grid for three detectors and
   two of them fail silently. This is the single most likely way a foreign dataset
   produces plausible wrong answers.
4. ✅ **Run the assessor** (`tools/assess_archive.py`) and compare the resulting
   participation, jitter, cluster rate and background against
   `docs/learned/assessment_real.json`. **The comparison is the deliverable**, not the
   corpus — if the statistics land close to ours, our conclusions travel further than one
   lab; if they are far apart, we have found the axis along which they do not.
5. ❌ **Choosing K for the new set** is a human decision, same as before.
6. ✅ Only then generate a corpus and re-run the bake-off on it.

**If the DANDI set has wider or more variable events than ours, it supersedes B4** — a
real distribution of widths beats a synthetic one, and it would make the multi-scale
question answerable on data rather than on a construction.

## What must not run overnight, restated so it cannot be missed

- **Choosing K**, or approving any generator spec.
- **Shipping a document.** Draft freely; the murderboard's blind rounds need a reader
  who did not write the draft, and this session has already demonstrated what
  self-review misses — four domain-level defects reached a shipped page after eleven
  roles reported clean.
- **Any claim that a detector is right about a real slice.** Nothing in Track B or C
  establishes that; the corpora are simulated and DANDI has no ground truth.
- **Rewriting git history**, per `CLAUDE.md`.

## Running several of these at once

They are independent, and the point of an unattended night is to run them in parallel.
Three rules make that safe:

1. **One worktree and one branch per item**, off `origin/main`, landing by green PR.
   Never share a HEAD.
2. **Claim shared external outputs on [`docs/SESSIONS.md`](SESSIONS.md) before writing** —
   the darkroom is visible from every machine and both workstations are live. Claim
   before the write, and **release only when the writing stops**, not when the first
   deliverable ships.
3. **Namespace your outputs, including data-store keys.** `tools/build_learned_report.py`
   addresses its JSON stores by name, and a session adding `"t"` for a tolerance sweep
   silently shadowed another session's `"t"` — a dict literal does not error on a
   duplicate key, so the tokens resolved against the wrong file and reported as
   *unresolved paths*. Store names are words now; use a distinctive one and check
   `DATA` before adding.

## Expected wall clock, from measured runs

Everything here is cheap by overnight standards, which is why the seed gap in B1 is
embarrassing rather than expensive.

| item | measured basis | estimate |
|---|---|---|
| one model fit | 5.6 s (centre−surround) | — |
| one ablation arm, 4 folds | 2.5 min for 5 arms | ~30 s |
| full regime-shift, all detectors | measured | ~9 min |
| assessor, 85 slices, 1,000 surrogates | measured | ~2 min |
| **B1, centre−surround + pooled trace, 5 seeds × 4 folds** | 40 fits at 5.6–8.0 s | **~5 min** |
| **B1 including the per-cell bank** | 20 more fits at **236 s each** | **+80 min** |
| **B2, 8 rate points × 9 detectors × 4 folds** | | **~1–2 h** |
| **B3, 6 width points × 2 clamp arms** | | **~20 min** |

**The whole of Track B fits in a night with hours to spare.** The binding constraint is
not compute; it is that each result needs a human to read it in the morning, so prefer
**fewer, better-instrumented runs that write clear JSON** over a sweep so broad nobody
opens it.

## The order I would run them

1. **B1** (seed gap) — everything else inherits its error bars.
2. **Track A 1–4** in parallel on separate branches — the app has to finish before the
   model matters.
3. **B2** (rate ceiling) — the one falsifiable prediction on the table.
4. **B5** (brightness channel) — one line, closes the last cheap explanation.
5. **B3** (width ceiling) — bounds the claim rather than testing it.
6. **C1–C4** — the second corpus, up to the human checkpoint.
7. **B4** last, or never, if DANDI supersedes it.
