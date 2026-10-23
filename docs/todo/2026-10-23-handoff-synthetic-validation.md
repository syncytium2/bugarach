---
status: picked-up
filed: 2026-10-23
---

# Handoff: validate the multi-source toolset on synthetic data

**Picked up 2026-10-23**: the goal page is [`goals/synthetic-validation.md`](../goals/synthetic-validation.md), and Tony's four decisions are answered there.

**This is a handoff to a new session** (Tony, 2026-10-23: *"make a handoff for the synthetic
validation"*). It is filed as a todo because nothing is half-done: this is a programme ready to start.
Your first deliverable is its goal page, `docs/goals/<slug>.md`, in the shape of
[`goals/README.md`](../goals/README.md), with a link back to this file.

## What Tony asked for (2026-10-22)

> Treat the bugarach project as a general toolset not specific to our data. Underlying premise is not
> one but two or more sources of coordinated events. We take a multichannel stream of unlabeled event
> times (and perhaps amp and width, version 0.2). Use our tools to extract parameters. Slow
> comodulation, coordinated event width(s), etc. build synthetic data. Choose from our library of
> detectors a couple to optimize/train. Characterize. Then run on original data. Our work today is
> validate the approach with purely synthetic data (perhaps using our existing flawed data and the
> cossart data) to determine what each detector is best at. Eg which ones can be tuned for close
> coordination events, which are best for noisy backgrounds. Which are best for low participation.
> Treat like a phd project (except we have days not years).

## Most of the loop already exists, for one source

[`pipeline.md`](../pipeline.md) is Tony's per-lab loop, dictated on 2026-09-04: open a folder; **MAHICE**
(*machine-assisted human identification of coordinated events*: the machine proposes, a person
judges and sets K); derive a spec; simulate and validate; tune; test on a fresh batch; detect on the
real folder. **Read it before designing anything.** It already rules that the simulation is settled
before anyone sees detection output, and that each knob's provenance (derived, inherited or hand-set)
is recorded.

**What is new in Tony's framing:**

1. **Two or more sources.** The generator plants one kind of coordinated event, at several
   participation levels. The premise now is several sources, each with its own participation,
   timing spread, spacing and membership. Fast and slow are one example of two sources, not the
   definition.
2. **General input.** Unlabelled multichannel event times (v0.1), plus amplitude and width (v0.2).
   Nothing specific to this lab.
3. **Capability maps.** The aim is what each detector can do, condition by condition. It is not a
   ranking: the detector document's no-ranking ruling (2026-10-20) is about that document, but the
   same spirit fits here.
4. **Synthetic first.** This step validates the approach with known truth. The real-data run comes
   after.

## Tools already in the tree

Use [`INDEX.md`](../INDEX.md) for anything not listed here.

| need | where |
|---|---|
| Measure a folder without a detector | `bugarach assess` (`src/bugarach/assess.py`, `assess_folder.py`); `tools/assess_archive.py` |
| Turn a measurement into a generator spec, saying what it assumed | `tools/derive_spec.py`; `src/bugarach/spec.py` |
| Simulate with planted truth | `bugarach.simulate.simulate_coordination` (read its docstring: rate shape, slow bursts, real-gap spacing, widths) |
| Timing spread across cells within an event | `tools/measure_jitter_correlogram.py` |
| Gaps between coordinated events | `tools/measure_real_intervals.py`; `bugarach.real_intervals` |
| Slow shared change in rate | `tools/measure_slow_comodulation.py`; [`learned/slow_comodulation/`](../learned/slow_comodulation/README.md) |
| Close events | `tools/measure_close_events.py` |
| The share of events that are coordinated, measured without defining an event | `tools/measure_coordination_rates.py` |
| The chance floor per window | `bugarach.event_floor` (ADR-0008) |
| Score detector calls against planted truth | `bugarach.score` (`TOL_SEC` 2.5 s) |
| Tune detectors | `tools/search_all_settings.py`, `tools/retune_operating_points.py` |
| Cossart's public data (DANDI:000219) | `tools/import_dandi.py` (its docstring says what the source lacks); the statistics in `docs/learned/assessment_cossart.json`; the earlier transfer in [`learned/cossart_transfer/`](../learned/cossart_transfer/README.md) |
| What a person sees: the rater sheet | [`tools/rater_sheet/`](../../tools/rater_sheet/README.md), a separate thread run by another session |

## Rulings that bind this work

- **The decoys are retired** ([ADR-0019](../adr/0019-the-decoys-are-retired-negatives-are-rate-matched.md)).
  No row, search or score uses them. Negatives are **rate-matched and carry no coordination**: each
  channel's rate and the slow shared change are kept, and the alignment is destroyed. That tool is
  owed ([todo](2026-10-23-rate-matched-negatives-and-the-bench-without-decoys.md)), and this work
  needs it. With several sources, **a call on a weaker source is a hit for that source**, not a false
  alarm, by ADR-0006's logic.
- **The learned models are on hold** (2026-10-22). Use the coded detectors only: CoactDetect, LoCo,
  binned SCE (synchronous calcium events), rate+context, SPIKE-synch, locust, count (sliding) and the
  stack detectors. The registry is `src/bugarach/detectors/`.
- **ADR-0006**: a false alarm is coincidence the rates explain, and shared change at a minute or more
  is background, by choice, for scoring.
- **ADR-0010**: tune, train and review against the data as they are.
- **Real recordings stay out of the tree** (FOUNDATIONS §5). This step is synthetic, so the issue
  arises only when parameters are measured from our folder: measured *numbers* are fine in the tree,
  recordings and per-recording figures are not.
- **Ask before** anything that compares groups or treatments: those are fireflies' by default
  (ADR-0017). Nothing here should need to.

## Open proposals that overlap; read them before building

- **ADR-0012 (Proposed)**, [#848](https://github.com/syncytium2/bugarach/pull/848): one function builds
  the bench and is the detector.
- **ADR-0013 (Proposed)**, [#855](https://github.com/syncytium2/bugarach/pull/855): the bench simulates
  treatment periods.
- **#856**: a local-rate threshold for count (sliding).

## The plan proposed to Tony on 2026-10-22 (refine it, do not treat it as settled)

**Aim 1: recover the parameters, and find where they stop being identifiable.** Do this first.
Simulate with known parameters and run the measuring tools blind, then compare against truth. Start
with one source, then two, sweeping how far apart their timing spreads and spacings are. The key
output is how close two sources can be before the tools can no longer tell them apart. If recovery
fails, the loop fails, and that is cheap to learn early.

**Aim 2: a capability map per detector.** Run a factorial grid: timing spread, participation,
background rate, slow-comodulation strength, spacing between events (close events), number of
channels, and separation between sources. Give every detector **the same tuning budget in every
cell** (unequal budgets made earlier comparisons unreadable: [`learned-model-family.md`](../goals/learned-model-family.md)),
and score recall per source. The map answers Tony's questions as conditions:
close events, noisy backgrounds, low participation.

**Aim 3: close the loop.** Measure a recording, simulate from the measurement, choose detectors from
the maps, tune on the simulation, then run on the recording. Check with the rate-matched negative,
and by re-measuring the parameters from the calls. This step is synthetic end to end: the "recording"
is a held-out synthetic one built from a *different* generator setting. Cossart's statistics stand in
for a stranger's data. Our current export is a source of realistic parameters only, never truth: it is
being revised (*"our existing flawed data"*).

**Guard against circularity.** A detector tuned on our simulator can look good because the simulator
shares its assumptions. Each map needs a column scored on a deliberately different generator: another
interval distribution, fixed against random membership, or another background model.

## Decisions to ask Tony for

1. **Membership:** does a source have fixed members (an assembly) or recruit at random each time?
   The generator recruits at random now. Cossart's data look assembly-like.
2. **The v0.1 input contract:** per-channel onset times, plus what (frame interval, duration)?
   `export_folder_spec.md` is this lab's contract and is more than a general toolset needs.
3. **Which detectors go on the map**, if not all of the coded ones. Compute decides; the grid in
   Aim 2 grows multiplicatively.
4. **Compute:** the grid runs overnight on WSMIP064 or WSMIP065. Run status mirrors per
   `docs/windows_workstation_setup.md` §8, and a finished run goes to Dropbox and the repo
   (CLAUDE.md).

## Done means, for this step

- The goal page exists, with this plan revised by what you find in the tree and by Tony's answers.
- Aim 1's first experiment has run on one source, with a figure (CLAUDE.md, *Show the picture*): true
  against recovered for each parameter, with its run record.
- The rate-matched negative tool is built, or its absence is the first item on the goal page.
- Not here: the real-data run; any group or treatment comparison; the learned models.
