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
After the reseeding below, the exact form matches the measured median participants within a median
0.011 (worst 0.06) of the planted value at 0.01 Hz, and within 0.016 (worst 0.11) at 0.05 Hz for
events of 10 or more cells (`theory_check.json`).

### Aim 0, replicated blind (2026-10-23)

Tony then asked for the pass to be run *"two more times with independent agents that don't know
what you discovered, to see if this is the only solution"*. Two agents got his first question and
pointers to the code and the Aim 1a record, nothing else, each in its own checkout of `main`. Their
scripts are kept in [`learned/synthetic_validation/blind_a/` and `blind_b/`](../learned/synthetic_validation/blind_README.md).

**All three reached the same core answer independently:**

| result | this session | blind A | blind B |
|---|---|---|---|
| the coordination-rates tool's excess cumulants, exactly, with the at-most-one-event term | ✓ (on a second try) | ✓ | ✓ |
| k_hat = 2 + (k − 2) g_3/g_2, which is the "window must exceed jitter" behaviour | ✓ | ✓ | ✓ |
| jitter from how the pair count changes with window | ✓ (one-parameter fit) | ✓ (joint fit of jitter, k, rate) | ✓ (ratio of two windows) |
| chance clusters at K: 60 q (1 − q)^2 per minute from the binomial tail | ✓ | ✓ | ✓ |
| two sources with equal jitter are not identifiable from pairs and triples | stated | ✓ (as a rank question) | ✓ |
| a shared slow rate change grows with window differently from coordination | stated | ✓ | — |

**What only the blind passes found:**
- **A design flaw in Aim 1a** (both). The seeds were `1000 + seed` in every cell and the generator
  draws the background first, so every cell at one background rate shared five background draws.
  Errors in Figure 1 were correlated across each row, and at 0.05 Hz the five happened to run low.
  **Fixed**: each recording now has its own seed, Aim 1a was rerun, and the first record is kept as
  `aim1_one_source_shared_seeds.json`. The 0.05 Hz rows now sit on the prediction.
- **The noise of each estimate**, from Charlier polynomials (orthogonal under a Poisson
  background), and with it a signal-to-noise figure that predicts when the tool returns nothing
  (A and B).
- **The assessment fully**: participants and jitter as medians over a mixture of chance and event
  clusters. Its jitter saturates because onsets are gathered within ±1.5 s: a 1 s Gaussian cut
  there has SD 0.74 s (A and B).
- **The ADR-0008 chance floor in closed form**, matching `window_floor` exactly or within one cell
  (A and B). At 33 cells it is 6 at 0.01 Hz and 12 at 0.05 Hz, so a 5-cell event can never pass it
  at either: a capability edge stated before any detector runs.
- **Count detector recall and false alarms** analytically, within about 0.03 recall in most
  conditions (B).
- **A joint fit across windows** that recovers jitter within about 5 % from 0.2 s, and participants
  and rate within a few per cent (A). Better than this session's one-parameter fit, which reads
  0.2 s as about 0.17 s. Adopt it.
- **Routes not yet taken** (both): Fisher information and Cramér–Rao bounds for the cluster
  process, which is the principled answer to *where parameters stop being identifiable*; scan
  statistics for the sliding detectors; grid axes in dimensionless groups (σ/w, λw, N·b·w, the
  signal-to-noise, K against the floor).

**Disagreements:** none on substance. Open residuals: B saw f3 5–7 % below prediction at 0.05 Hz
over 60 seeds; A saw rate 3–5 % above prediction. Neither is explained.

**So: not the only solution, but one answer reached three ways.** The cumulant route is the one all
three found first. The other analytical routes (likelihood bounds, scan statistics, the
correlogram's own second-order prediction) are different ways to the same quantities and to the
limits on them, not competing answers.

### Aim 0, membership and order (2026-10-23; derived and checked on membership and order alone)

Tony asked whether the analysis generalises so that, as the number of sources grows, an
assembly converges to random participation. It does, and the same holds for order. Then:
*"How does this compare with Kreuz synfire measurement? Pretty sure his is brute force. Synfire
is very slow."*

**Three properties of a coordinated event, and which tool sees each:**

| property | seen by | blind to it |
|---|---|---|
| how many cells, and how tightly timed (k, σ) | the coordination-rates tool, the chance floor | — |
| **which** cells (membership) | `bugarach.assembly`; the pair-count dispersion below | every population-count tool, at any number of sources |
| **in what order** (leader to follower) | SPIKE-order / synfire indicator (`tools/synfire_scan.py`) | everything else here |

**Membership** ([`membership_limit.py`](../learned/synthetic_validation/membership_limit.py)).
With M fixed assemblies and E events, the dispersion of pair co-occurrence counts across cell
pairs, relative to random participation, is **1 + (E − 1)/M**. So an assembly converges to random
as 1/M, and what sets it is how often an assembly is reused (E/M), not M alone. Checked at 33
cells, 10 per event, 45 events: 44.5 against 45.0 at M = 1, 5.30 against 5.40 at M = 10, 1.94
against 1.98 at M = 45, 1.03 against 1.04 at M = 1000. Membership is read perfectly here; background
cells joining by chance and missed members shrink the excess by a factor blind pass B derived.

**Order** ([`order_limit.py`](../learned/synthetic_validation/order_limit.py)). Give each source a
latency template (spread s across cells) under the event's jitter σ, and score order the way
SPIKE-order does: for each pair, the mean sign of who leads, cells sorted from leader to follower,
the indicator F the share of pair agreements with that sort. Two changes from the published method:
**the sort is a score sort (each cell's net lead count), O(N²) and deterministic, not simulated
annealing over N! orders**, and the coincidences come from known events rather than adaptive
windows. Predictions, with τ = s/σ:

| case | prediction | check (33 cells, 10 per event) |
|---|---|---|
| one template | F = (2/π) arctan τ | τ = 1: 0.503 against 0.500; τ = 2.5: 0.747 against 0.758 |
| M independent templates | F ≈ √(2/π) · √((2/π) arcsin(τ²/(1+τ²))) / √M | M = 2: 0.461 against 0.460; M = 64: 0.084 against 0.086 |
| no order | F ≈ 0.375 / √n̄, n̄ = events a pair shares | constant to ±0.01 from 25 to 800 events |

The last row matters for the real data. With no order present, the indicator is the
optimisation's own bias, and it falls as 1/√(events per pair). That is the August finding that
the indicator is *"strongly anti-correlated with spike count"* (fast ρ −0.75,
[`todo/2026-08-19-synfire-measured-and-what-it-cost.md`](../todo/2026-08-19-synfire-measured-and-what-it-cost.md)),
and why the order-free control's median sat at 0.10. The null that todo had to build, permuting
which cell owns each onset with the onsets kept, is the exchangeable limit both convergences
reach: no membership and no order.

**Against the brute force:** `synfire_scan.py` anneals each recording several times and then
re-anneals every surrogate. Under the template model the optimal order is the score order in
expectation, the indicator and its null bias are closed forms, and the whole check above runs in
about 20 s. ⚠ Not yet compared with PySpike's indicator on the same trains (PySpike is not
installed in this venv): its adaptive coincidence windows and normalisation change the constants,
and the scaling laws are the claim, not the numbers.

**What it changes for the generator.** The August todos already said the generator plants no
order, so a synfire measure can only score its own bias here. A source should carry three things:
participation and timing (k, σ), a membership rule (random, or an assembly reused E/M times),
and a latency template (spread s). Each has a predicted convergence to the exchangeable limit, so
Aim 1b and 1c can be placed where those predictions say the structure becomes undetectable.

### Aim 1a, first result (2026-10-23; measured, one generator, not reviewed)

⚠ **Rerun the same day with a seed per recording** (see *Aim 0, replicated blind*). The bullets below
were written on the first run, whose cells shared five backgrounds; they still hold in direction,
and Figure 1 is the rerun.

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

**Aim 0: predict first, simulate to check** (added 2026-10-23; replicated blind the same day). For
each question, derive what the tools and the simpler detectors should return from the planted
parameters, then simulate to test the prediction and measure what is left over. Next, in order:
- the detectability threshold for membership structure in the cell-by-cell co-activation matrix
  (planted low-rank structure against sampling noise; random-matrix theory has a sharp threshold)
  and its counterpart for order;
- check the score-sort indicator against PySpike's on the same trains, and if they agree, offer it
  as the fast route for `synfire_scan.py`;
- move blind A's joint fit across windows, the noise model and the closed-form floor into
  `theory.py`, and re-plot Figure 1 on dimensionless axes;
- Cramér–Rao bounds for (λ, k, σ), as Aim 1's identifiability boundary;
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
3. The generator: several sources, each with its own participation, jitter, spacing, membership
   rule (random or an assembly) and latency template; optional shared slow comodulation.
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
