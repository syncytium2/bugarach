# Goal: validate the toolset on synthetic data with two or more sources of coordinated events

**Set by Tony, 2026-10-22; picked up 2026-10-23** from the handoff
[`todo/2026-10-23-handoff-synthetic-validation.md`](../todo/2026-10-23-handoff-synthetic-validation.md),
which holds his words in full. Branch prefix `synth/`.

Treat bugarach as a general toolset, not one built for this lab's data. The input is a
multichannel stream of unlabelled event times. The premise is that **two or more sources** of
coordinated events are mixed in it, each with its own participation, timing spread, spacing and
membership. The loop: measure the parameters with our tools, simulate from them, tune a few
coded detectors on the simulation, characterise each detector, then run on the original
recording. **This step is synthetic only.** It checks the approach against known truth and
answers, condition by condition, what each detector can do: close events, noisy backgrounds,
low participation. Tony: *"Treat like a phd project (except we have days not years)."*

## Where it stands

- 2026-10-23: goal page written; Tony's four decisions answered (below). **Aim 1a has run**: one
  source, random membership, 240 simulated recordings, measured blind. Result below and in
  [`learned/synthetic_validation/`](../learned/synthetic_validation/README.md).
- 2026-10-23, later: **Aim 0 (theory) added** after Tony asked whether an analytical prediction
  could replace the brute force. It predicts Aim 1a from the planted parameters alone, and gives a
  jitter estimate that works where the assessment's does not. Result below; `theory.py`.

### Aim 0, first result (2026-10-23; derived and checked against Aim 1a, not reviewed)

Tony, 2026-10-23: *"Is it possible there's an analytical prediction to be made here? We are
solving this with brute force."* For this generator, yes. The derivations are in the docstring of
[`learned/synthetic_validation/theory.py`](../learned/synthetic_validation/theory.py); its
`check()` prints every comparison in about 12 s, against about a minute of simulation.

- **Window sharing.** The chance that n onsets of one event share a window of width w is
  g_n(w, σ) = E[(1 − R_n/w)+], with R_n the range of n jittered onsets. g_2 has a closed form.
- **The coordination-rates tool is predicted exactly.** Factorial cumulants add over independent
  processes, and with at most one event per window (events ≥ 20 s apart) the excess pair and
  triple cumulants are closed forms in (k, σ, w, λ, N). At 0.01 Hz background the predicted
  participants match the measured median within about 0.03 in every cell. The residual a Poisson
  treatment leaves (5–15 %, growing with window and event rate) is the regularity of the event
  train, and the exact form removes it.
- **Jitter from how the pair count changes with window**, fitted across the tool's 1, 2 and 4 s
  windows: planted 0.2, 0.5 and 1.0 s come back as about 0.17, 0.48 and 1.0 s at both
  backgrounds. That turns jitter from Aim 1a's weakest parameter into one of its best. It floors
  near the 0.1 s frame (planted 0.05 s reads about 0.02 s).
- **Chance clusters at K** (the assessment): a binomial tail per 1 s bin, with the tool's merging,
  predicts the measured cluster rate within about 10 % at every K and background. K = 3 or 4 at
  0.05 Hz is swamped before anything is simulated.
- **Not predicted:** the weakest cells (5 cells per event, 15 events, 0.05 Hz), where the tool's
  estimate is noise-dominated rather than biased.

Figure 1 now carries the predictions as dashed lines, and the fitted jitter as its own series.

### Aim 1a, first result (2026-10-23; measured, one generator, not reviewed)

Figure 1, *recovery against planted jitter*, is
`synth_recovery_plot_one-source-jitter_20261023.png` in the darkroom folder below and in
the learned folder. What it shows:

- **The coordinated share of onsets is the most robust quantity**: within about 20 % of
  planted at every jitter, both background rates and every window of the coordination-rates tool.
- **Participants per event are recovered** within about 30 % by the coordination-rates tool at
  a 4 s window and by the assessment at K = 4 or 6. The 1 s window undercounts once the jitter
  nears the window (0.4× at 1 s jitter): **the window must exceed the jitter**, and choosing it
  needs the jitter first.
- **Event rate needs K to rise with the background.** At 0.05 Hz per cell the assessment at
  K = 3 or 4 counts background coincidences as events (8–16× the planted rate); K = 6 and the
  coordination-rates tool stay within about 30 %. A fixed K does not transfer across
  backgrounds, which is the case for setting K per recording (MAHICE, `derive_k`).
- **Jitter is the weak parameter.** The assessment's `jit_obs` reads about 0.6 s whatever was
  planted at 0.05 Hz background unless participation is high, and tops out near 0.7 s at
  every background. It is only usable at low background and high participation. The correlogram
  tool is the dedicated jitter measure and cannot yet run on a synthetic folder (open work 4),
  so it moves up the list.

## Settled

| what | strength | source |
|---|---|---|
| **Membership is a grid axis**: a source either has fixed members (an assembly) or recruits at random each event, and both are simulated. The second also serves as the circularity column (score on the generator you did not tune on). | decided | Tony, 2026-10-23 |
| **The v0.1 input is per-channel onset times plus the recording's duration.** Frame interval is optional and inferred when missing. Amplitude and width are v0.2. The lab's [`export_folder_spec.md`](../export_folder_spec.md) is one producer's contract, not the general one. | decided | Tony, 2026-10-23 |
| **The first capability map has four detectors**: CoactDetect, LoCo, binned SCE (synchronous calcium events), count (sliding). The others join once the grid is sized. | decided | Tony, 2026-10-23 |
| **Compute is WSMIP065.** Run status mirrors per [`windows_workstation_setup.md`](../windows_workstation_setup.md) §8; a finished run goes to Dropbox and the repo. | decided | Tony, 2026-10-23 |
| Coded detectors only; the learned models are on hold. | decided | Tony, 2026-10-22 (handoff) |
| Negatives are rate-matched and carry no coordination; no decoys. A call on a weaker source is a hit for that source. | decided | [ADR-0019](../adr/0019-the-decoys-are-retired-negatives-are-rate-matched.md), ADR-0006 |
| Our current export supplies realistic parameter values only, never truth. | decided | Tony, 2026-10-22 (*"our existing flawed data"*) |

## What the tree has, and what it lacks (surveyed 2026-10-23)

**The generator plants one source.** `bugarach.simulate.simulate_coordination` has one jitter,
one spacing schedule and several participation levels; `PlantedEvent.kind` is only
`coordinated` or `distractor`. **Membership is a fresh uniform draw per event**
(`rng.choice(n_roi, …)`); there is no assembly mode. `tools/assembly_power.py` plants a fixed
assembly on an events-by-ROI matrix with no times, and is the template for one.
**Shared slow comodulation is not in the generator either**: its burst multiplier is drawn per
ROI. The shared form exists only inside `tools/measure_slow_comodulation.py` (`_ou_multiplier`).

**Measuring tools that run on arrays in memory**, so Aim 1 can use them directly:
`assess.assess_coactivity` (participants, jitter, span, cluster rate, rate per ROI, at chosen K)
and `measure_coordination_rates.measure` + `solve` (participants per shared moment, their rate and
the coordinated share, with no K and no event definition). The correlogram, real-interval and
slow-comodulation tools read `dataset.default()` only. Running them on a synthetic folder needs
a `--folder` flag or a pointer swap, and there is **no library writer** for a simulated folder
(three tests write one inline).

**Round trips that already exist:** `tests/test_adapt.py` (one setting, eight seeds: participants
+18 %, jitter +9 %, frequency −7 % at K = 4) and the coordination-rates tool's bench calibration.
Nothing sweeps conditions, and nothing runs simulate → assess → `derive_spec` → compare.

**The rate-matched negative tool is not built.** Its pieces exist
(`surrogates.rigid_shift`, `operational_time`, `window_circular_shift`;
`event_floor.rigid_frames`); its todo is
[`2026-10-23-rate-matched-negatives-and-the-bench-without-decoys.md`](../todo/2026-10-23-rate-matched-negatives-and-the-bench-without-decoys.md).
**It is owed before Aim 2 scores anything**, and it is the first build item below.

**Scoring has no notion of a source**: `score.score_stream` reads `gt.times` and `gt.frac` only.

## The plan (revised from the handoff's)

**Aim 0: predict first, simulate to check** (added 2026-10-23). For each question, derive what the
tools and the simpler detectors should return from the planted parameters, then simulate to test
the prediction and measure what is left over. Next derivations, in order of use:
- two sources: their cumulants add, so the tool's window dependence separates sources only when
  their jitters differ; with equal jitters only a combined participation term is identifiable
  (Aim 1c's answer, predicted before it is run);
- a shared slow rate change adds pair excess that grows with the window, while coordination levels
  off once the window exceeds the jitter;
- count (sliding) and binned SCE: recall as the chance that at least K of k jittered onsets share
  the detector's window, false alarms as the chance tail; their capability maps are then drawn
  analytically and the grid in Aim 2 is placed around the predicted boundaries;
- CoactDetect and LoCo (rolling context, merge gaps), clustered spacing and per-cell burstiness
  stay simulated.

**Aim 1: recover the parameters, and find where they stop being identifiable.**
1a. One source, random membership: sweep jitter, participation, event count and background rate;
    measure blind with the two in-memory tools; plot true against recovered. *First experiment.*
1b. One source, fixed assembly: the same sweep, plus whether `bugarach.assembly`'s recurrence test
    finds the assembly.
1c. Two sources: sweep how far apart their jitters, spacings and participations are. The output is
    the separation below which the tools report one source.
Needs, in order: multi-source and assembly support in the generator (seeds of existing calls stay
byte-identical; `tests/test_real_intervals_off_by_default.py` guards that), and a `source` field on
`PlantedEvent`.

**Aim 2: a capability map per detector.** Factorial grid over timing spread, participation,
background rate, shared slow comodulation (needs the generator change above), spacing, number of
channels, membership and source separation. Same tuning budget in every cell. Recall scored **per
source**, false alarms on the rate-matched negative. One column scored on a generator setting the
detectors were not tuned on.

**Aim 3: close the loop.** Treat a held-out synthetic recording from a different generator setting
as the "real" one: measure, simulate, choose detectors from the maps, tune, detect, and re-measure
the parameters from the calls. Cossart's statistics (`docs/learned/assessment_cossart.json`) stand
in for a stranger's data.

## Waiting on Tony

- Nothing (PR #905 and #906 merged 2026-10-23).

## Open work a session can do without a ruling

1. Aim 1a, extended: recovery against participation and event count separately (Figure 1 pools
   them), and the correlogram tool's jitter once open item 4 lands.
2. The rate-matched negative tool (todo above).
3. The generator: several sources, each with its own participation, jitter, spacing and
   membership rule (random or assembly); optional shared slow comodulation.
4. A `--folder` route for the correlogram, real-interval and slow-comodulation tools, and one
   library function that writes a simulation as a folder.
5. `score` per source.

## Not here

The real-data run; any group or treatment comparison (fireflies' by default, ADR-0017); the
learned models.

## Where the work lives

| what | where |
|---|---|
| Aim 1 scripts and records | `docs/learned/synthetic_validation/` |
| Figures | darkroom `bugarach/2026-10-23-synthetic-validation/` (claimed in `docs/SESSIONS.md`) |
