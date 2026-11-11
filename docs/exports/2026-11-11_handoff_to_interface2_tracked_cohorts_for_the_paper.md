# Handoff to interface2: one declared export of the two tracked APV+CNQX → gabazine cohorts

**From:** bugarach / `065/handoff-tracked-cohorts` | **2026-11-11**
**To:** an interface2 session, chosen by Tony | **Re:** the September DI cohort and the October
MALE cohort on tracked ROIs, as bugarach's input

**One line: both cohorts are already exported and conform, but each exists in three versions
that disagree about which is final. bugarach needs the producer to declare one, and to make its
own notes agree with its name.**

> **Working material, not murderboarded.** Every count below was read from the folders' own
> files on 2026-11-11; nothing in it was analysed, and no detector was run.

`<data>` below is the shared data root (`$BUGARACH_DATA_ROOT` on bugarach's side; no personal
path is written here because this repository is public).

## Why this is being asked

Tony, 2026-11-11: the DI and MALE APV+CNQX then gabazine studies from September and October can
stand in for the full 66-recording run for the paper. The 66-recording folder has been stopped
in bugarach since 2026-10-05 for a known contamination, and its replacement is not here yet.
These two cohorts are on tracked ROIs with rigid motion correction, and their rasters have been
drawn and reviewed.

bugarach does not choose which recordings or which version is analysable. That is the
producer's call (bugarach `CLAUDE.md`, *The export folder is the input*). A bugarach session
does not act in interface2 either (bugarach ADR-0007), which is why this is a document and not
a commit in your repository.

## What should exist afterwards

1. **One export that the producer declares to be the input for these two cohorts**, under
   `<data>/exports/bugarach/` (the input area), not `exports/bugarach_eval/`. It holds the
   13 recordings below, both streams, at the 4x threshold.
   - **One folder holding both cohorts is preferred**, because bugarach reads one default
     dataset and every analysis reports it (bugarach ADR-0018). If there is a reason to keep
     the cohorts in two folders, say so in the reply and bugarach will declare two.
   - A 3x sibling is welcome as a sensitivity folder. It is not required.
2. **Its `README.md`, `PROVENANCE.md` and `PREFLIGHT.md` agree with its name and with each
   other** on the points in *What bugarach could not settle*, below.
3. **The versions it supersedes are unmistakable as superseded**: moved aside, renamed, or
   listed in the new folder's README. Nothing needs deleting.
4. **Any known contamination is declared in the README, or the README says there is none.**
   bugarach stops on a declared contamination by rule (Tony, 2026-09-17), so an undeclared one
   is the costly case.
5. **A short reply** naming the folder, answering the questions below, and saying what, if
   anything, changed in the recording files against the version named as its source.

## What must not change

- **The recordings.** Whichever existing version is declared final, its recording files should
  arrive byte-identical, or the reply should list every difference and why.
- **The agreement with the reviewed rasters.** Tony reviewed the pages in
  `<darkroom>/bugarach/2026-11-04-tracked-pilot-combined-rasters-reviewed-v2/`. The declared
  export should be the data those pages show, or differ from it only by removals the reply
  lists.
- **The analysis windows, the dead-ROI verdicts and the review blanking**, unless an answer
  below requires a change.
- `20260917_415` stays out (z-axis, Tony 2026-11-03), unless Tony says otherwise.

## What bugarach found (read on WSMIP065, 2026-11-11)

All of these are in `<data>/exports/bugarach_eval/`, each has a 3x sibling, and every one
passes `bugarach check` (bugarach `origin/main` at 5121c918). Counts are from each folder's own
files.

| folder (each prefixed `2026-11-04_`) | written | recordings | ROIs | events (PROVENANCE) | review blank windows | events removed by review blanking |
|---|---|---|---|---|---|---|
| `apv_cnqx_then_gz_sept_tracked_4x_REVIEW_BLANKED_FIELDSTEPS_UNSCANNED` | 07:50 | 5, DI | 191 | 20,090 | 12 | 663 |
| `pilot_apv_cnqx_then_gz_tracked_4x_REVIEWED_REVIEW_BLANKED_FIELDSTEPS_UNSCANNED` | 11:35 | 5, DI | 191 | 20,090 | 13 | 591 |
| `apv_cnqx_then_gz_sept_tracked_4x_CONFIRMED_BLANKED_OCT05WINDOWS` | 12:42 | 5, DI | 191 | 20,090 | 12 | 663 |
| `male_cohort_tracked_4x_REVIEW_BLANKED_FIELDSTEPS_UNSCANNED` | 08:20 | 8, MALE | 300 | 17,425 | 9 | 65 |
| `male_cohort_tracked_4x_CONFIRMED_BLANKED_FIELDSTEPS_REVIEWED` | 11:54 | 8, MALE | 300 | 17,425 | 22 | 487 |
| `male_cohort_tracked_4x_REVIEWED_REVIEW_BLANKED_FIELDSTEPS_UNSCANNED` | 12:12 | 8, MALE | 300 | 17,425 | 22 | 487 |

Times are US Eastern, from the folders' modification times.

What is the same in every version, and suits bugarach as it stands:

- **Periods:** baseline, APV+CNQX, gabazine, high K⁺. Every DI recording has all four. Among
  the 8 MALE recordings, 7 have gabazine and 6 have high K⁺.
- **Baseline analysis windows are 20.0 minutes in all 13 recordings.** bugarach measures a
  baseline only when it is at least 15 minutes, so all 13 qualify.
- **ROIs per recording:** DI 30, 26, 73, 26, 36; MALE 59, 44, 37, 33, 18, 25, 49, 35.
- `field_steps_excluded.tsv` and `moco_pinned_excluded.tsv` have no rows in any version.

## What bugarach could not settle, and asks the producer to state

1. **Which version of each cohort is final?** The names and the times point different ways.
   - **DI:** the newest folder is `..._CONFIRMED_BLANKED_OCT05WINDOWS` (12:42; 12 blank windows,
     663 events removed). The reviewed pages were drawn from
     `pilot_..._REVIEWED_REVIEW_BLANKED_FIELDSTEPS_UNSCANNED` (11:35; 13 blank windows, 591
     events removed). Their recording files differ in all 5 recordings.
   - **MALE:** `..._CONFIRMED_BLANKED_FIELDSTEPS_REVIEWED` (11:54) and
     `..._REVIEWED_REVIEW_BLANKED_FIELDSTEPS_UNSCANNED` (12:12) report the same counts in every
     column above, and their recording files differ in all 8 recordings. The reviewed pages were
     drawn from the second.
2. **What is the field-step status of each cohort?** Tony ruled on 2026-09-12 that analysis
   runs only on data with field-step artifacts excluded. In the MALE folder whose name ends
   `FIELDSTEPS_REVIEWED`, `PREFLIGHT.md` row 6 says *unscanned: no FFave sidecars for this
   cohort*. Its `PROVENANCE.md` says steps are excluded against a roster of 9 confirmed steps,
   and no event was removed. Please state, per cohort, which of these is true: scanned and
   excluded; not scannable, and reviewed by hand by Tony, with the date and what was blanked;
   or neither yet.
3. **Does the roster of 9 confirmed steps cover any of these 13 recordings?** If it is the main
   series' roster, "excluded" is true and empty here, and the notes should say so.
4. **Is the PROVENANCE event count taken before review blanking?** It is identical across
   versions that remove 65 and 487 events (MALE), and 591 and 663 (DI).
5. **Is the MALE tracking final?** `PROVENANCE.md` calls the archive variant *provisional*;
   `PREFLIGHT.md` calls it *final tracking, reviewed by Tony 2026-11-03*.
6. **Did anything change on 2026-11-05 that the bugarach export should carry?** The R-side
   output for the DI cohort has a version dated 2026-11-05 (`..._tracked_20261105_PAIRS5_...`),
   a day newer than any bugarach export.
7. **Are ROIs with no events written, or dropped?** `bugarach check` notes that no ROI is
   declared with no events in any recording. If every ROI had an event, that is right. If some
   had none and were left out, the population is too small and no consumer can tell. The
   contract writes them as `time_sec = NA`.

## What bugarach does on receipt

1. Runs `bugarach check` on the declared folder and reads every warning.
2. Adds the folder to `current_export.toml` with the README's notes, including any declared
   contamination. Whether it becomes the default is Tony's.
3. Starts the readiness route at its first stage, on the baselines only
   (`docs/pipelines/stream-readiness.md` in bugarach, landing in pull request #923).

Comparing APV+CNQX or gabazine with baseline, or DI with MALE, is `fireflies`' work by default
(bugarach ADR-0017). bugarach's part is the detector calls and the measures exported from them.

## Not asked

No detector output, no figures and no change to the 66-recording folder or its pinning review.
How the export is produced is the producer's to choose; nothing here names a tool for it.
