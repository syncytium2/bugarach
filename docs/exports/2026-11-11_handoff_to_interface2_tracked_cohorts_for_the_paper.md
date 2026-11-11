# Handoff to interface2: an export of the two tracked APV+CNQX → gabazine cohorts for bugarach

**From:** bugarach / `065/handoff-tracked-cohorts` | **2026-11-11**
**To:** an interface2 session, chosen by Tony
**Re:** a new export folder for bugarach, holding the September DI cohort and the October MALE
cohort

> **Working material, not murderboarded.**

**One line: please create one export folder for bugarach that holds both cohorts, as the
reviewed rasters show them.**

`<data>` is the shared data root (`$BUGARACH_DATA_ROOT` on bugarach's side) and `<darkroom>` is
the shared darkroom. No personal path is written here because this repository is public.

## Why

Tony, 2026-11-11: the DI and MALE APV+CNQX then gabazine studies from September and October can
stand in for the full 66-recording run for the paper. Their rasters are prepared and are in the
darkroom, so the data are ready. bugarach's 66-recording input has been stopped since 2026-10-05
and its replacement is not here yet.

bugarach reads an export folder and nothing else, and what goes into one is the producer's
decision. A bugarach session does not act in interface2 (bugarach ADR-0007). So this asks for
the export and leaves how it is made, and every choice inside it, to you and Tony.

## What should exist afterwards

**One export folder under `<data>/exports/bugarach/`**, conforming to bugarach's
`docs/export_folder_spec.md`, that holds:

- **the September 2026 DI cohort and the October 2026 MALE cohort**, APV+CNQX then gabazine, on
  tracked ROIs: the recordings shown on the two pages in
  `<darkroom>/bugarach/2026-11-04-tracked-pilot-combined-rasters-reviewed-v2/4x/`;
- **both streams**, fast and slow;
- **`slices.csv`** with each recording's frame interval and group (`DI` or `MALE`);
- **`regions.csv`** with every period of every recording and the analysis windows to score;
- **a `README.md`** that says what the folder is and states plainly:
  - which recordings are in it, and any left out and why;
  - what was removed from the events, and under which review;
  - whether whole-field brightness steps were scanned and excluded, reviewed by hand, or
    neither. bugarach admits detector results only on data with those artifacts excluded (Tony,
    2026-09-12), so it needs this said in words;
  - **any known contamination, or that there is none.** bugarach stops on a declared one by
    rule (Tony, 2026-09-17).

One folder for both cohorts is asked for because bugarach reads a single default dataset. If two
folders suit the cohorts better, make two and say so; bugarach will declare both.

## What bugarach does not need

- No detector output and no figures.
- No change to the 66-recording folder or its pinning review.
- No second threshold. A 3x sibling is welcome and is not required.

## The reply

A short note, added to this file or sent through Tony, with the folder's name and anything
bugarach should know before reading it.

## What bugarach does on receipt

1. Runs `bugarach check` on the folder and reads every warning.
2. Declares the folder in `current_export.toml`, with the README's notes. Whether it becomes
   the default is Tony's.
3. Starts the readiness route at its first stage, on the baselines only.

Comparing a treatment with baseline, or DI with MALE, is `fireflies`' work by default (bugarach
ADR-0017). bugarach's part is the detector calls and the measures exported from them.
