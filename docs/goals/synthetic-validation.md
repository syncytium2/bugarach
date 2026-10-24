# Goal: validate the toolset on synthetic data with two or more sources of coordinated events

**Set by Tony, 2026-10-22; picked up 2026-10-23** from the handoff
[`todo/2026-10-23-handoff-synthetic-validation.md`](../todo/2026-10-23-handoff-synthetic-validation.md),
which holds his words in full. Branch prefix `synth/`.

Treat bugarach as a general toolset, not one built for this lab's data. The input is a
multichannel stream of unlabelled event times. The premise is that **two or more sources** of
coordinated events are mixed in it, each with its own participation, jitter, intervals and
membership. The loop: measure the parameters with our tools, simulate from them, tune a few
coded detectors on the simulation, characterize each detector, then run on the original
recording. **This step is synthetic only.** It checks the approach against known truth and
answers, condition by condition, what each detector can do: close events, noisy backgrounds,
low participation. Tony: *"Treat like a phd project (except we have days not years)."*

## Where it stands

- 2026-10-23: goal page written; Tony's four decisions answered (below). **Aim 1a ran**: one
  source, random membership, 240 simulated recordings measured blind by two tools. It showed that
  a fixed threshold does not transfer across backgrounds and that the assessor cannot measure
  jitter. Rerun the same day with a seed per recording (the first run's conditions shared five
  background draws).
- 2026-10-23: **Aim 0 (theory) added** after Tony asked whether an analytical prediction could
  replace the brute force. The coordination-rates tool's output is predicted from the planted
  parameters, and a fit across its three windows recovers jitter, participants and event rate for
  events of 10 or more cells. Two more sessions, given only the question and the code, reached the
  same core derivation. Membership and order have closed forms too.
- 2026-10-23: **Aim 0 murderboarded** (11 roles,
  [run record](../reviews/synthetic-validation-aim0_2026-10-23.md)). It found overclaims (stale
  numbers, "exact" stretched past participants, an untested explanation of the August synfire
  result), prior work the page had not cited, and two analysis faults (the jitter fit ignored the
  at-most-one-event term; predictions skipped the tool's own refusal rule). Both faults are fixed
  and every number below is recomputed.

### Symbols and tools used below

N cells (33 here) · k participants per event (cells; 5, 10 or 20, from participation 0.15, 0.3,
0.6) · σ jitter, the SD of each participant's onset about the event time (s; the glossary's
correlogram half-width is a different measure of the same spread) · w window (s) · λ coordinated
events per s · b background rate (Hz per cell) · K the assessor's threshold, an **absolute** count
of cells (not the glossary's percentage K) · E events · M assemblies or latency templates.
A **condition** is one grid point (one k, σ, event count and background), 5 recordings each.

- **The coordination-rates tool** (`tools/measure_coordination_rates.py`) counts how much more
  often pairs and triples of cells are active in the same window (1, 2, 4 s) than in
  time-shifted copies, and converts that into participants per event, events per minute and the
  coordinated share of onsets. It needs no event definition and no threshold.
- **The assessor** (`bugarach.assess.assess_coactivity`) finds clusters of at least K active cells
  in 1 s bins and reports their participants, rate and onset jitter.

### Aim 1a, first result (2026-10-23; measured; reseeded the same day)

![Figure 1](../learned/synthetic_validation/synth_recovery_plot_one-source-jitter_20261023.png)

**Figure 1, recovery against planted jitter.** 240 simulated recordings (33 cells, 45 min each;
background 0.01 Hz per cell in A–D, 0.05 Hz per cell in E–H). Each point is a median over
participation (0.15, 0.3 or 0.6 of cells), event count (15 or 45 events) and 5 recordings;
bars are the interquartile range, a down-triangle marks a bar that runs below the axis, and
points are offset sideways only for legibility. The assessor gives no coordinated share (C, G)
and the coordination-rates tool no per-event jitter except through the joint fit (violet, Aim 0).

⚠ **The first run's conditions shared five background draws** (seed 1000 + replicate in every
condition, and the generator draws the background first), found by both blind passes below. Each
recording now has its own seed; the first record is kept as `aim1_one_source_shared_seeds.json`.

- **The coordinated share of onsets moves least**: within about 25 % of planted
  in every condition at the 2 and 4 s windows, and down to 0.74 at the 1 s window when the jitter
  is 1 s (C, G).
- **Participants need a window wider than the jitter.** The 1 s window reads 0.4 at 1 s jitter
  (A, E); the 4 s window stays within about 30 %. The assessor at K = 4 or 6 cells is within about
  30 % at the lower background and is pulled by chance coincidences at the higher one.
- **A fixed K does not transfer across backgrounds.** At 0.05 Hz per cell the assessor at K = 3
  or 4 cells counts chance coincidences as events, 16× and 8× the planted rate (F); at 0.01 Hz
  K = 6 cells misses most 5-cell events (B, 0.3 at 1 s jitter). That is the case for setting K per
  recording (MAHICE, `derive_k`).
- **The assessor cannot measure jitter.** It reads about 0.66 s whatever was planted at 0.05 Hz
  (H) and tops out near 0.7 s everywhere, because it gathers onsets within ±1.5 s of a cluster
  (a 1 s Gaussian cut at ±1.5 s has SD 0.74 s). Aim 0's joint fit (violet) does measure it.

### Aim 0, the predictions (2026-10-23; derived, checked against Aim 1a, murderboarded)

Tony, 2026-10-23: *"Is it possible there's an analytical prediction to be made here? We are
solving this with brute force."* For this generator, mostly yes. The derivations and their
assumptions are in [`theory.py`](../learned/synthetic_validation/theory.py); `check()` recomputes
every comparison below in about a minute.

**What it rests on.** The generator is a Neyman–Scott cluster process (Poisson background plus
events whose participants scatter around the event time). The tool's route, factorial cumulants
of the population count, is CuBIC's (Staude, Rotter & Grün 2010, *J Comput Neurosci* 29:327)
and Ehm, Staude & Rotter 2007 (*Electron J Stat* 1:473; ⚠ not opened). The loss of coincidences
split by a window edge is Grün et al. 1999's "fission probability" (*J Neurosci Methods* 94:67).
What is added here: the Gaussian closed form of that loss for this tool (window sharing g_n, with
frame rounding), the term for at most one event per window, and the fit across windows.

![Figure 2](../learned/synthetic_validation/synth_recovery_plot_one-source-predicted-against-measured_20261023.png)

**Figure 2, predicted against measured, one point per condition and window.** A–C, E–G: the
coordination-rates tool's three estimates as ratios to planted; grey points ignore the
at-most-one-event term (a Poisson event train), coloured points include it, by participants per
event. D, H: chance clusters per minute from the binomial tail, against 10 background-only
recordings each (bars: interquartile range).

- **Participants: predicted to within seed-to-seed noise.** Measured minus predicted, as a ratio to
  planted: median 0.009 (worst 0.056) at 0.01 Hz; for events of 10 or more cells, median 0.015
  (worst 0.11) at 0.05 Hz. Without the at-most-one-event term the median residual is about 0.05:
  events at least 20 s apart make the event train more regular than Poisson, which the tool's
  chance correction does not expect (blind pass B named it a hard-core bias).
- **Event rate and share: predicted less well.** For events of 10 or more cells the rate residual
  has median 0.03–0.06 and worst 0.18–0.38, the share median 0.02 and worst 0.07–0.28. The
  surrogate's own correlations (about 1 % of the pair count, murderboard role 6) are not modelled.
- **Not predicted: 5-cell events at 0.05 Hz**, where the tool's estimate is dominated by noise
  (worst ratio off by 5.6). The tool refused an estimate (pair or triple count ≤ 0) in 17 of 720
  recording-windows, all at 0.05 Hz; medians exclude them, and so does the prediction, which now
  passes through the tool's own `solve()`.
- **Jitter, participants and rate, fitted together across the 1, 2 and 4 s windows** (blind pass
  A's route): for events of 10 or more cells, planted 0.2, 0.5 and 1.0 s read 0.22, 0.49 and
  1.01 s at 0.01 Hz and 0.20, 0.52 and 1.01 s at 0.05 Hz; participants and rate within 4 %. Not
  resolved: jitter at the 0.1 s frame scale (planted 0.05 s reads 0.07 and 0.03 s, with 3 and 7
  of 20 fits at the search bound of 0.005 s) and 5-cell events (jitter off by up to 2×).
- **Chance clusters at K** (the assessor, background only): predicted 0.26, 0.02 and 0 per min at
  K = 3, 4, 6 cells and 0.01 Hz (measured 0.27, 0.04, 0); 7.97, 3.86 and 0.28 per min at 0.05 Hz
  (measured 7.94, 3.96, 0.22). The prediction is the chance term only: whether a planted event
  reaches K depends on k, σ and the bin, and is not modelled here (blind pass A modelled it by a
  one-event simulation).

### Aim 0, checked by two more sessions (2026-10-23)

Tony asked for the pass to be run *"two more times with independent agents that don't know what
you discovered, to see if this is the only solution"*. **One answer, reached three ways; the other
routes lead to the same quantities.** Two more Claude sessions got his first question and pointers
to the code and the Aim 1a record, each in its own checkout of `main`, and reached the same core
derivation. ⚠ This is a consistency check, not independent review: all three shared the prompt,
the repository, the shared-seed record, the tool definitions and the model, and the tool itself
is defined by factorial cumulants, so the cumulant route was close to forced. This session's
exact term was committed before either blind report arrived. Their reports are kept verbatim:
[`blind_a/REPORT.md`](../learned/synthetic_validation/blind_a/REPORT.md),
[`blind_b/REPORT.md`](../learned/synthetic_validation/blind_b/REPORT.md).

| result | this session | blind A | blind B |
|---|---|---|---|
| excess cumulants with the at-most-one-event term | same leading terms (second try) | same leading terms, no 1/N factor | same leading terms, no 1/N² factor in the triple term |
| estimated participants k̂ = 2 + (k − 2) g_3/g_2: the window must exceed the jitter | yes | yes | yes |
| jitter from how the pair count changes with window | one-parameter fit, read 0.2 s as 0.17 s (dropped) | joint fit of jitter, participants and rate (adopted) | ratio of two windows, read 0.2 s 5–15 % high |
| chance clusters at K: 60 q (1 − q)² per min, q the chance a 1 s bin holds K or more cells | yes | yes | yes |
| two sources with equal jitter not separable from pair and triple counts | stated | stated (as a rank question) | stated |

**What only the blind passes found:** the shared-background flaw in Aim 1a (both); the noise of
each estimate and with it when the tool will refuse (A by Charlier polynomials, B by the delta
method; CuBIC gives the null variances of its own estimators); the assessor's participants and
jitter as mixtures of chance and event clusters (both); an up-crossing form of the ADR-0008 event
floor that matches the simulated floor exactly or within one cell (both; the repository already had
a window-budget closed form in `tools/measure_chance_floor.py`); count-detector recall within about
0.03 in 20 of 24 conditions (B); the joint fit (A). At 33 cells the event floor is 6 cells at
0.01 Hz and 12 at 0.05 Hz, so 5- and 10-cell events cannot pass it at 0.05 Hz on their own cells;
chance joiners lift a 5-cell event past 6 about a third of the time at 0.01 Hz (B).

**Open residuals:** B saw the triple count 3–19 % below prediction at 0.05 Hz (40 seeds,
`blind_b/sim_cumulant_check.txt`), A the rate 3–5 % above. The surrogate correlation above may be
part of both.

### Aim 0, membership and order (2026-10-23; checked on membership and order alone)

Tony asked whether the analysis generalizes so that, as sources multiply, assembled participation
converges to random. It does, and so does order. Membership and order are invisible to every
population-count tool, at any number of sources; only cell-by-cell statistics see them. In both
cases the limit is the **exchangeable** one: cells interchangeable, no fixed membership and no
order. It is the null the August synfire work built, permuting which cell owns each onset with
the onsets kept, a variant of Kreuz et al.'s order surrogates (2017, sec. 2.5).

![Figure 3](../learned/synthetic_validation/synth_assembly-membership_plot_assemblies-converge-to-random_20261023.png)

**Figure 3, assembled against random participation.** 33 cells, 10 per event, 45 events, 400
simulations per point. A: the variance of pair co-participation counts across cell pairs
(`bugarach.assembly.stat_dispersion`), divided by its value under random participation, against
how often each assembly is reused; grey band, the 95 % range of a single random recording. B: the
share of single recordings above that range.

**Membership** ([`membership_limit.py`](../learned/synthetic_validation/membership_limit.py)). With
M fixed assemblies and E events, the ratio is **1 + (E − 1)/M**: two events share an assembly with
probability 1/M, the survey-sampling design effect (Kish 1965; ⚠ not opened). At fixed E it falls
to 1 as 1/M, and reuse E/M sets it (A). A single recording is detected every time while each
assembly is used at least once, 63 % of the time at 0.3 uses per assembly, and 8 % at 0.04 (5 %
by chance) (B). **This assumes members are read perfectly**: every member seen, no background cell
joining. Real readout dilutes the excess; no correction factor is derived yet.

![Figure 4](../learned/synthetic_validation/synth_recovery_plot_order-indicator-closed-forms_20261023.png)

**Figure 4, an order indicator against its closed forms.** 33 cells, 10 per event, known events,
no background. A: one latency template, τ = template spread ÷ jitter, 200 events. B: M templates
at τ = 2.5, 2000 events; dotted, the signal term alone. C: no order planted; the indicator falls
as 1/√n̄, with a constant fitted for each way of choosing the order.

**Order** ([`order_limit.py`](../learned/synthetic_validation/order_limit.py)). Each source gets a
latency template over cells. For each pair, count who leads; put the cells in an order; F is the
net agreement with that order (agreeing minus disagreeing pair co-participations, as a share of
all of them). Choosing the order by each cell's net lead count (a Borda or Copeland score) is
O(N²) with no search. Under one template F = (2/π) arctan τ (A), which is the population Kendall τ
between template and observed latencies under a normal model (Greiner's relation, via Kruskal
1958; ⚠ secondary sources only). With M templates the signal term falls as 1/√M, and the
no-order bias adds in quadrature (B).

**Against Kreuz's synfire measure, the comparison is not yet made.** SPIKE-order and its Synfire
Indicator (Kreuz, Satuvuori, Pofahl & Mulansky 2017, *New J Phys* 19:043028) differ from F in
three ways: coincidences come from ISI-adaptive windows, not known events; the order is found by
simulated annealing; and F is normalized by all spikes, coincident or not, which shrinks it by a
factor that varies with participation and background (0.28 at 10 of 33 cells with no background,
less with it; murderboard role 6). So:
- **The no-order constant is not the annealed one.** It is fitted, not derived: 0.38 under the
  score sort and 0.50 under a local search that stands in for annealing (C), and it changes with
  field size (0.22 to 0.61 across 15–100 cells, 5–30 per event; `order_limit.json`). Kreuz et al.
  2017 (sec. 3.1) already note that the sorted indicator on order-free trains is a finite-size
  effect falling with spike count; what is new here is the 1/√n̄ form.
- **The August anti-correlation with spike count** (fast ρ −0.75, slow ρ −0.40;
  [`todo/2026-08-19-synfire-measured-and-what-it-cost.md`](../todo/2026-08-19-synfire-measured-and-what-it-cost.md))
  **is consistent with this bias but untested.** Dilution by non-coincident spikes and the
  ISI-adaptive window predict a negative correlation too. The test: run `synfire_scan.py` on
  order-free simulations matched to those recordings' cells and spike counts.
- **The fast sort has prior art.** Sorting by net wins 5-approximates the best order
  (Coppersmith, Fleischer & Rudra 2010, *ACM Trans Algorithms* 6:55) and is near-optimal for
  ranking from noisy pairwise comparisons (Shah & Wainwright 2018, *JMLR* 18:199; both from
  metadata). Kreuz's lab still anneals the sort (Kreuz et al. 2022, *J Neurosci Methods*
  381:109703) but replaced annealing for latency correction with a direct estimate from pairwise
  matrices (Mariani et al. 2025, *J Neurosci Methods* 416:110378: 9.7 s against 861.8 s).

**What it changes for the generator.** A source should carry participation and jitter (k, σ), a
membership rule (random, or an assembly reused E/M times) and a latency template (spread s). That
is the PP-Seq model of Williams, Degleris, Wang & Linderman (NeurIPS 2020; abstract read), which
fits the number of sources too and is a candidate comparison for Aim 1c.

### Tried and dropped

- **A Poisson treatment of the event train** (first derivation): left a 5 % residual in
  participants (up to 20 % at the 4 s window); the at-most-one-event term removes it.
- **One background per condition** (the first Aim 1a run): five shared draws made errors
  correlated across each row of Figure 1.
- **A one-parameter jitter fit of the pair count across windows**: it ignored the
  at-most-one-event term, so the reported "0.2 s reads 0.17 s" and the "floor near the frame" were
  partly model error and partly the fit's search bound. Replaced by the joint fit.
- **Predicting chance plus every planted event as the assessor's cluster rate**: it assumed every
  event reaches K. Replaced by the chance term on background-only recordings.

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
one interval schedule and several participation levels; `PlantedEvent.kind` is only
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

**Aim 0: predict first, simulate to check** (added 2026-10-23). For each question, derive what
the tools and the simpler detectors should return from the planted parameters, then simulate to
test the prediction and measure what is left over. Next, in order (validation owed by results
already stated comes first, then the derivations later aims will use):
1. Compare the order indicator with PySpike's on the same trains, and run `synfire_scan.py` on
   order-free simulations matched to the August recordings, before the August link is claimed.
2. Ask whether anyone has asked Kreuz (or Mulansky) about a fast sort or an analytical null
   (see *Waiting on Tony*).
3. Model planted-event detection (the chance that an event reaches K) for the assessor and the
   count detector, and the readout dilution of the membership excess.
4. Derive the detectability threshold for membership structure in the cell-by-cell co-activation
   matrix (planted low-rank structure against sampling noise: Baik, Ben Arous & Péché 2005;
   ⚠ not opened). The repository has already met its limits: `bugarach.assembly` notes that the
   Marchenko–Pastur bound is unavailable with fewer events than cells, and
   [`assembly_report.md`](../assembly_report.md) found PCA against it flags every simulated
   recording. Lopes-dos-Santos et al. 2013 is the classical instrument.
5. Bound (λ, k, σ) from the likelihood of the cluster process (Cramér–Rao, or composite
   likelihood where it is intractable) as Aim 1's identifiability boundary.
6. Check by simulation the two-source prediction (equal jitters leave only a combined
   participation term in pair and triple counts) and the slow-comodulation one (its pair excess
   grows with the window while coordination levels off).
7. Re-plot Figure 1 on dimensionless axes (σ/w, λw, N·b·w, K against the event floor) and place
   the Aim 2 grid around the predicted boundaries.
CoactDetect and LoCo (rolling context, merge gaps), clustered intervals and per-cell burstiness
stay simulated.

**Aim 1: recover the parameters, and find where they stop being identifiable.**
1a. One source, random membership: sweep jitter, participation, event count and background rate;
    measure blind with the two in-memory tools; plot true against recovered. *First experiment.*
1b. One source, fixed assembly: the same sweep, plus whether `bugarach.assembly`'s recurrence test
    finds the assembly.
1c. Two sources: sweep how far apart their jitters, intervals and participations are. The output is
    the separation below which the tools report one source.
Needs, in order: multi-source and assembly support in the generator (seeds of existing calls stay
byte-identical; `tests/test_real_intervals_off_by_default.py` guards that), and a `source` field on
`PlantedEvent`.

**Aim 2: a capability map per detector.** Factorial grid over jitter, participation,
background rate, shared slow comodulation (needs the generator change above), intervals, number of
channels, membership and source separation. Same tuning budget in every cell. Recall scored **per
source**, false alarms on the rate-matched negative. One column scored on a generator setting the
detectors were not tuned on.

**Aim 3: close the loop.** Treat a held-out synthetic recording from a different generator setting
as the "real" one: measure, simulate, choose detectors from the maps, tune, detect, and re-measure
the parameters from the calls. Cossart's statistics (`docs/learned/assessment_cossart.json`) stand
in for a stranger's data.

## Waiting on Tony

- **Has anyone asked Kreuz (or Mulansky)** whether a fast sort or an analytical null for the
  Synfire Indicator exists? The repository's correspondence with Kreuz does not cover it, and in
  August his reply pointed to his own papers on a construction this repository had claimed. Ask
  before the score sort or the 1/√n̄ law is offered as new.

## Open work a session can do without a ruling

1. Aim 0's numbered next steps (*The plan*), items 1 and 3–7.
2. Aim 1a, extended: recovery against participation and event count separately (Figure 1 pools
   them), and the correlogram tool's jitter once the `--folder` route lands.
3. The rate-matched negative tool (todo above).
4. The generator: several sources, each with its own participation, jitter, intervals, membership
   rule (random or an assembly) and latency template; optional shared slow comodulation.
5. A `--folder` route for the correlogram, real-interval and slow-comodulation tools, and one
   library function that writes a simulation as a folder.
6. `score` per source.

## Not here

The real-data run; any group or treatment comparison (fireflies' by default, ADR-0017); the
learned models.

## Where the work lives

| what | where |
|---|---|
| Aim 1 scripts and records | `docs/learned/synthetic_validation/` |
| Figures | darkroom `bugarach/2026-10-23-synthetic-validation/` (claimed in `docs/SESSIONS.md`) |
