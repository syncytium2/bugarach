# The webapp — the full pipeline, end to end

> **Working a lane?** [`docs/lanes.md`](lanes.md) says which worktree is yours and what
> to read first.
>
> **Building it? The route is
> [`docs/webapp_completion_plan.md`](webapp_completion_plan.md)** — phase order, what
> already exists for each of the seven stages, and the lane table saying which pieces can
> be worked at the same time and which queue on one file. This document is the
> requirement; that one is how it gets built.
>
> **This is the WEBSITE track.** The model track — refining the detectors, the seed
> gap, the rate ceiling, a second corpus — is [`docs/model_track.md`](model_track.md),
> and the two are deliberately separated: Tony, 2026-08-18, *"separate out the two main
> tasks (model and website)"*. Nothing here waits on a model result, and nothing there
> blocks a screen.
>
> **Approval status:** the *requirement* below is Tony's, given 2026-08-18. The
> **execution order and the design choices are proposals** and have not been approved.
> [`docs/overnight_spec.md`](overnight_spec.md) still governs what may run unattended.

## What is being asked for

> *"I need the webapp up and running with the full pipeline. Import, assess, simulate,
> train and optimize (dl model(s) and 6 detectors in parallel), display detection, and
> an output contract. For now output fireflies compatible list of event times by slice
> id and treatment."*

Seven stages. Today the app does **one and a half of them**: it opens a folder and
plots rasters, and its directory mode is broken for conforming export folders — it
globs every `.csv` and hands each to the events loader as a separate recording, so it
tries to read `regions.csv` as a recording and raises.

## The stages, and what each one owes the next

| # | stage | exists? | owes the next stage |
|---|---|---|---|
| 1 | **Import** | ⚠ half — reads a folder, wrong unit | one slice object per slice id, with regions, streams and the frame interval attached |
| 2 | **Assess** | ✅ library, no UI | participation, jitter, cluster rate, background — plus the K scan, unchosen |
| 3 | **Simulate** | ✅ library, no UI | a corpus with planted truth, split into folds |
| 4 | **Train & optimize** | ✅ library, no UI | for each of 9 detectors: a fitted knob or a trained model + threshold |
| 5 | **Display detection** | ⚠ raster only | detections on the existing lanes, per detector, per slice |
| 6 | **Output** | ❌ nothing | the contract below |

**The app writes no data file today.** Every number stays on screen. That is the gap
that makes stage 6 the point of the exercise rather than an afterthought.

## The output contract — what ships first

**The columns are [`docs/export_folder_spec.md`](export_folder_spec.md)'s**, under *"What
bugarach emits back"*, and that document is the only place they are written down. It is
implemented in [`src/bugarach/emit.py`](../src/bugarach/emit.py).

> **This section used to restate the schema, and the two came apart** (2026-08-19). It
> showed a narrower "fireflies-compatible" row keyed on a **`treatment`** column, which
> the export contract forbids in terms — *no privileged region, and no protocol
> vocabulary*. The word came from the original request quoted above, so it was a faithful
> transcription rather than a careless draft, and it survived because a schema written in
> two places drifts in one of them.
>
> **It is superseded, and the consumers settled it before we did.** `fireflies` reads
> `region_idx` straight out of the export and builds its own `treatment` factor at its own
> boundary — *"for this call only"*, in its words (`td/fig-auc-beforeafter.R`) — and its
> old `region_idx <= 2` filter is now a no-op tripwire, so it has already restructured
> around the export's indexing. `interface2` answered the same question in its contract
> reply: *"region 1 always reads `baseline` because that is its name … the baseline is a
> fixed period in the protocol, not a treatment slot."* Neither consumer wants a
> `treatment` column from us, and neither needs a narrower file. **Do not add one.**

What that shape carries, and why, is argued there rather than here. The rules below are
about the *pipeline*, and they hold whatever the columns are called:

- **`slice_id` comes from the data, never from a filename or a code argument.** The
  loader currently takes the slice name as an argument and ignores the `slice_id`
  column the export contract requires. Two slices that differ only by folder name
  would collide.
- **The period is carried through, never inferred.** It arrives as the producer's own
  `region_idx` and `region_label` and is passed on unchanged. The app must not guess a
  period from a filename, must not rename one, and must not merge regions — **effects run
  in opposite directions by group**, so a pooled row is not admissible (FOUNDATIONS §9).
- **One row per event per detector.** Do not pre-merge detectors into a consensus;
  that is a downstream decision and merging discards which detector fired.
- **Times in seconds, on the recording's own clock**, with the frame interval recorded
  in a sidecar. Frames are the model's unit; seconds are the *contract's* unit, and
  the conversion happens exactly once, here.
- **A slice with no detections emits no rows — and is still listed** in the sidecar's
  slice roster. Absent rows and an absent slice must not look the same: the first is a
  finding, the second is a bug.
- **Never emit a viability claim.** No "dead", "silent" or "inactive" column. A
  zero-event ROI is not a dead ROI and that verdict is `fireflies`' to make
  (FOUNDATIONS §9).

**Sidecar** (`run.json`), because a table of times with no provenance is unusable in
six months: the generator spec, the chosen K, each detector's fitted knob or threshold,
the corpus seeds, the code version, and the frame interval per slice.

## Build order, and why this one

1. **Fix import, then write the output contract with a stub detector.**
   Counter-intuitive, and it is the point: a pipeline that ends in a file can be
   checked end to end from day one. Build stage 6 against a detector that emits one
   event per minute and the whole seam is testable before any real work lands on it.
2. **Wire the six detectors to that contract.** They already run; this is display and
   export, not new analysis.
3. **Display detection** on the existing lanes — the viewer already draws detector
   lanes over a raster; this is connecting fitted detectors to it.
4. **Assess, with the K screen.** This is the one screen that cannot be a spinner: it
   must show the scan and take a decision. See the K figure in the coordination report
   for what the choice actually does.
5. **Simulate + train.** The expensive stages, and the ones a user should be able to
   walk away from. Nine detectors in parallel, one progress row each.
6. **Optimize** — the fold procedure `fair_bakeoff.py` already implements. Reuse it;
   do not write a second scorer.

## "In parallel" — what that has to mean

Nine detectors, and the costs are not comparable: the six calibrate in 0.2–4.4 s, the
centre−surround trains in 5.6 s, the per-cell bank in **236 s**. Parallel here means
*the UI stays responsive and the slow one does not block the other eight*, not that
they finish together. Two consequences for the design:

- **Per-detector progress, not a single bar.** One row per detector, each with its own
  state, because a single bar spends most of its life waiting on one model.
- **Partial results are usable.** A user who has the six and centre−surround should be
  able to export and look at detections while the per-cell bank is still training. The
  export contract already supports this — rows carry the detector name.

## What the app must refuse to do

- **Re-pick a threshold on the recording being analysed.** It is chosen on held-out
  training data on purpose; a "re-tune on this slice" button hides exactly the failure
  the regime-shift test measures.
- **Choose K.** Show the scan, take the decision, record it.
- **Imply a detector is right about a real slice.** Everything measured so far is on
  simulated data. The app may say "these are the detections"; it may not say "these are
  the events".
- **Guess the frame interval.** It sets the grid for three detectors and **two fail
  silently**; a lab imaging at 20 Hz that sends no interval currently gets one warning
  and two quietly wrong answers.

## How we will know it works

The corpus in `docs/learned/` has published numbers. **Point the app at a generated
corpus and its exported table must agree with `bakeoff.json`** — same detections, same
counts. If it disagrees, the app is wrong, and that check exists on day one rather than
after the UI is built.
