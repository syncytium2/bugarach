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

- 2026-10-23: goal page written; Tony's four decisions answered (*Settled*). **Aim 1a ran**: one
  source, random membership, 240 simulated recordings measured without the planted values. A
  fixed threshold does not transfer across backgrounds, and the assessor cannot measure jitter.
  Rerun the same day with a seed per recording.
- 2026-10-23: **Aim 0 (theory) added** after Tony asked whether an analytical prediction could
  replace the brute force. For events of 10 or more cells and jitter from 0.2 s up, the
  coordination-rates tool's output is predicted, and a fit across its windows recovers jitter,
  participants and event rate. Two more sessions reached the same core derivation. Assembled
  participation converges to random as 1/M; an order indicator has closed forms, but its
  no-order constant is fitted and the comparison with Kreuz's measure is not yet made.
- 2026-10-23/24: **murderboarded**, 11 roles and blind verify rounds
  ([run record](../reviews/synthetic-validation-aim0_2026-10-23.md)). Every number below was
  recomputed after the fixes.

### Symbols and tools used below

| symbol or term | meaning | values in Aim 1a |
|---|---|---|
| N | cells (ROIs) in a recording | 33 |
| k | participants per event (cells) | 5, 10, 20 (participation 0.15, 0.3, 0.6) |
| σ | jitter: SD of each participant's onset about the event time (s) | 0.05, 0.2, 0.5, 1.0 s |
| b | background rate (Hz per cell) | 0.01, 0.05 Hz per cell |
| E, λ | coordinated events per recording; per second | 15 or 45 in 45 min |
| w | the coordination-rates tool's window (s) | 1, 2, 4 s |
| K | the assessor's threshold, an absolute count of cells (not the glossary's percentage K) | 3, 4, 6 cells |
| g_n | the chance that n onsets of one event fall in the same window | |
| M | assemblies or latency templates | |
| condition | one grid point (k, σ, E, b), simulated as 5 recordings | 48 conditions |

- **The coordination-rates tool** (`tools/measure_coordination_rates.py`) counts how much more
  often pairs and triples of cells are active in the same window than in time-shifted copies of
  the recording (the surrogates), and converts that into participants per event, events per
  minute and the coordinated share of onsets (the fraction of all onsets that belong to a
  coordinated event). It needs no event definition and no threshold.
- **The assessor** (`bugarach.assess.assess_coactivity`) finds clusters of at least K active cells
  in 1 s bins, gathers each cluster's onsets within ±1.5 s, and reports participants, rate and
  onset jitter.

### Aim 1a, first result (2026-10-23; measured; reseeded the same day)

![Figure 1](../learned/synthetic_validation/synth_recovery_plot_one-source-jitter_20261023.png)

**Figure 1, recovery against planted jitter.** 240 simulated recordings (33 cells, 45 min each).
Each point is a median over participation, event count and 5 recordings per condition; bars are
the interquartile range. A–C, E–G: recovered ÷ planted. D, H: recovered jitter in seconds against
the identity line, so an estimator that returns a constant draws as a flat line. The joint fit
(violet, Aim 0) is shown only for events of 10 or more cells. A fixed K fails at the higher
background, and only the joint fit tracks jitter.

⚠ **The first run's conditions shared five background draws** (one seed per replicate, used in
every condition, and the generator draws the background first). Each recording now has its own
seed; the first record is kept as `aim1_one_source_shared_seeds.json`.

- **A fixed K does not transfer across backgrounds.** At 0.05 Hz per cell, chance alone gives the
  assessor 7.97 clusters per minute at K = 3 cells and 3.86 at K = 4, against 0.33 or 1 planted
  events per minute (F). At 0.01 Hz, K = 6 cells misses most 5-cell events: their recovered rate
  is 0–0.27 of planted (inside the pooled points of B). Both follow from the event floor, the
  smallest event that beats chance (ADR-0008): at 33 cells it is 6 cells at 0.01 Hz and 12 at
  0.05 Hz. That is the case for setting K per recording (MAHICE, the expert-reviewed threshold).
- **The assessor cannot measure jitter.** At 0.05 Hz it reads 0.66–0.73 s at K = 3 or 4 and
  0.49–0.67 s at K = 6, whatever jitter was planted (H), and it tops out near 0.7 s everywhere.
  Two causes, neither tested here: chance onsets inside the ±1.5 s gather at low jitter, and the
  gather cutting the event's own spread at high jitter (a 1 s Gaussian cut at ±1.5 s has SD
  0.74 s).
- **Participants need a window wider than the jitter.** The 1 s window reads 0.34–0.4 of planted
  at 1 s jitter (A, E); the 4 s window stays within 0.68–1.04 for events of 10 or more cells. The
  same tool's event rate at the 1 s window climbs to 1.7× and 2.1× of planted at 1 s jitter (B,
  F), which Aim 0 predicts.
- **The coordinated share moves least**: for events of 10 or more cells, 0.78–1.11 of planted per
  condition at the 2 and 4 s windows at 0.01 Hz, and 0.67–1.11 at 0.05 Hz. 5-cell events at
  0.05 Hz range 0.09–3.58.

### Aim 0, the predictions (2026-10-23; derived, checked against Aim 1a, murderboarded)

Tony, 2026-10-23: *"Is it possible there's an analytical prediction to be made here? We are
solving this with brute force."* For this generator, mostly yes, and Aim 1a's two failures are
what it answers. Derivations and assumptions are in
[`theory.py`](../learned/synthetic_validation/theory.py); `check()` recomputes everything here in
about a minute.

**The core prediction.** A window of width w catches all n onsets of one event with probability
g_n(w, σ). The tool assumes it catches them all, so it reports k̂ = 2 + (k − 2) g_3/g_2: as the
jitter approaches the window, g_3 falls faster than g_2 and k̂ falls toward 2. That is the
*window must exceed the jitter* result. Events here are at least 20 s apart, so a window never
holds two of them; the **at-most-one-event term** corrects for that, and a Poisson event train
would not need it.

**What it rests on.** The generator is a cluster process of the Neyman–Scott / Thomas type
(Gaussian scatter of participants about each event; Neyman & Scott 1958, Thomas 1949), but with
a fixed number of events held apart rather than Poisson-placed ones. The tool's route is the
cumulant route of CuBIC (Staude, Rotter & Grün 2010, *J Comput Neurosci* 29:327) on the
multiple-interaction model of Kuhn, Aertsen & Rotter 2003; the tool uses factorial rather than
ordinary cumulants. Grün et al. 1999 (*J Neurosci Methods* 94:67) derived the two-onset,
uniform-jitter case of window loss ("fission probability"), and Pazienti et al. 2008 (*Brain Res*
1225:39; ⚠ abstract only) used coincidence detection against window width to estimate
synchronization precision. What is added here: g_n for Gaussian jitter and n onsets, the
at-most-one-event term, and the joint fit. ⚠ Not searched for prior art: spatial point-process
statistics, quadrat-variance ecology, physics counting statistics.

![Figure 2](../learned/synthetic_validation/synth_recovery_plot_one-source-predicted-against-measured_20261023.png)

**Figure 2, predicted against measured, one point per condition and window.** A–C, E–G: the
coordination-rates tool's three estimates as ratios to planted; coloured points use the full
prediction (with the at-most-one-event term), grey points a Poisson event train. D, H: chance
clusters per minute on 100 background-only recordings per background, pooled, with exact Poisson
95 % intervals. The at-most-one-event term closes the participant residual.

The residual below is |condition median of recovered ÷ planted − predicted ÷ planted|. The tool
refused an estimate (pair or triple count ≤ 0) in 17 of 720 recording-windows, all 5-cell events
at 0.05 Hz; medians exclude them, and so does the prediction, which passes through the tool's own
estimator.

- **Participants: predicted closely, not to within noise.** Median residual 0.007 (worst 0.037)
  at 0.01 Hz and 0.016 (worst 0.11) at 0.05 Hz, for events of 10 or more cells; about 0.05
  without the at-most-one-event term. Against each condition's 5-recording spread, 7 and 10 of
  48 condition-windows sit beyond 2 SE where about 2 are expected.
- **Jitter, participants and rate, fitted together across the 1, 2 and 4 s windows** (blind pass
  A's route): for events of 10 or more cells, planted 0.2, 0.5 and 1.0 s read 0.22, 0.50 and
  1.01 s at 0.01 Hz and 0.20, 0.52 and 1.01 s at 0.05 Hz (condition medians within 0.88–1.13 of
  planted); participants within 0.94–1.14 and rate within 0.73–1.14 per condition. Not resolved:
  planted 0.05 s (reads 0.075 and 0.039 s; 1 and 4 of 20 fits at the 0.005 s search bound) and
  5-cell events (jitter 0.1 to 3.6 times planted). ⚠ A latency template would read as extra
  jitter here (see *Order*).
- **Event rate and share: predicted less well, and biased one way.** For events of 10 or more
  cells the rate residual has median 0.03 (worst 0.18) at 0.01 Hz and 0.06 (worst 0.38) at
  0.05 Hz; the share 0.02 (worst 0.07) and 0.02 (worst 0.28). At 0.01 Hz measured exceeds
  predicted in 43 (rate) and 41 (share) of 48. Untested candidate: the surrogates' shifted copies
  are not independent of the event train (a reviewer estimated about 1 % of the pair count).
- **Not predicted: 5-cell events at 0.05 Hz**, where the estimate is noise-dominated (worst ratio
  5.6 of planted).
- **Chance clusters at K** (the assessor, background only; 60 q(1 − q)² per minute, q the chance
  a 1 s bin holds K or more active cells, the square because both preceding bins must be below
  K): predicted 0.256, 0.019 and 0.0001 per min at K = 3, 4, 6 cells and 0.01 Hz (measured 0.262,
  0.020, 0); 7.97, 3.86 and 0.284 at 0.05 Hz (measured 7.97, 3.85, 0.279). All within their 95 %
  intervals. Whether a planted event reaches K is not modelled here.

### Aim 0, checked by two more sessions (2026-10-23)

Tony asked for the pass to be run *"two more times with independent agents that don't know what
you discovered, to see if this is the only solution"*. **Same core derivation in all three
sessions; a consistency check, not independent review.** Two more Claude sessions got his first
question, the code and the Aim 1a record, each in its own checkout of `main`. They shared the
prompt, the repository, the shared-seed record, the tool definitions and the model with this
session, and the tool is itself defined by cumulants, so the route was close to forced. This
session's at-most-one-event term was committed before either blind report arrived. Their reports
are kept verbatim: [`blind_a/REPORT.md`](../learned/synthetic_validation/blind_a/REPORT.md),
[`blind_b/REPORT.md`](../learned/synthetic_validation/blind_b/REPORT.md).

| result | this session | blind A | blind B |
|---|---|---|---|
| excess cumulants with the at-most-one-event term | full form | drops the surrogate's 1/N correction | drops the 1/N² correction in the triple term |
| k̂ = 2 + (k − 2) g_3/g_2 | yes | yes | yes |
| jitter from how the pair count changes with window | one-parameter fit (dropped) | joint fit (adopted) | ratio of two windows, read 0.2 s 5–15 % high |
| chance clusters 60 q (1 − q)² per min | yes | yes | yes |
| two equal-jitter sources inseparable from pair and triple counts | stated, untested | stated, untested | stated, untested |

**What only the blind passes found:**
- the shared-background flaw in Aim 1a (both);
- the noise of each estimate, and with it when the tool will refuse (A by Charlier polynomials,
  B by the delta method; CuBIC gives its own estimators' null variances);
- the assessor's participants and jitter as a mixture of chance and event clusters (both);
- the event floor as an up-crossing rate, within one cell of the simulated floor (both; the
  repository already had a window-budget closed form in `tools/measure_chance_floor.py`);
- count-detector recall within about 0.03 in 20 of B's 24 settings (B);
- the joint fit (A).

The event floor (*Aim 1a*) is the consequence: 5- and 10-cell events cannot reach it at 0.05 Hz
on their own cells, and chance joiners lift a 5-cell event to 6 about a third of the time at
0.01 Hz and 0.2 s jitter (B).

**Open residuals:** B's report gives the triple count 5–7 % below prediction at 0.05 Hz over 60
seeds (its kept 40-seed output, 3–19 % per window); A the rate 3–5 % high.

### Aim 0, membership (2026-10-23; simulated with membership as the only structure)

Tony asked whether the analysis generalizes so that, as sources multiply, assembled
participation converges to random. **Under the assumptions below, yes, at a predicted rate.**
Membership is invisible to every population-count tool at any number of sources; only cell-by-cell
statistics see it.

![Figure 3](../learned/synthetic_validation/synth_assembly-membership_plot_assemblies-converge-to-random_20261023.png)

**Figure 3, assembled against random participation.** 33 cells, 10 per event, 45 events. A: the
variance of pair co-participation counts across cell pairs
(`bugarach.assembly.stat_dispersion`), divided by its value under random participation, mean of
400 simulations. B: the share of 60 single recordings that the repository's assembly verdict
(both nulls and both statistics, `AssemblyResult.verdict()`) flags; dotted, its rate under random
participation (3 of 60). The excess falls as 1/M, and reuse E/M sets it.

[`membership_limit.py`](../learned/synthetic_validation/membership_limit.py). Assumptions: M
assemblies of k random cells (they may overlap), each event picking one with equal probability,
and perfect readout (every member seen, no background cell joining). Then two events share an
assembly with probability 1/M and the ratio is **1 + (E − 1)/M** (A; for unequal use, 1/M becomes
Σ p_m²). It has the form of Kish's design effect (1965; ⚠ analogy, book not opened). The verdict
flags every recording while reuse E/M is at least 1, 83 % at 0.3 and 27 % at 0.045 (B). At M = 1
it reads every recording "uniform-only": one assembly holding every event is the case its
margin-preserving null cannot see, as the module documents. Real readout dilutes the excess; no
correction is derived yet.

### Aim 0, order (2026-10-23; simulated with order as the only structure)

**A latency template is not invisible to the population-count tools: it reads as extra jitter.**
With template spread δ and jitter σ, two participants' lag has SD √(2(δ² + σ²)), so g_n and the
joint fit see √(δ² + σ²). Only cell-by-cell statistics separate the two.

![Figure 4](../learned/synthetic_validation/synth_recovery_plot_order-indicator-closed-forms_20261023.png)

**Figure 4, an order indicator against its closed forms and fits.** 33 cells, 10 per event, known
events, no background. F is the net agreement of pair lead signs with an order of the cells (0 with
no order, 1 for a perfect sequence). A: one template, r = template spread ÷ jitter, 200 events;
dashed, the same with the no-order bias of 200 events added. B: M templates at r = 2.5, 2000
events; the signal term F_M, and with the no-order bias F_0 added. C: no order planted, under the
score sort and a local search. F follows (2/π) arctan r, and with no order it is a finite-size
bias falling as 1/√n̄. All three panels share one log axis.

[`order_limit.py`](../learned/synthetic_validation/order_limit.py). For each pair of cells, count
who leads across the events they share; order the cells by each one's net lead count (a Borda or
Copeland **score sort**, O(N²), no search); F is the net agreement with that order as a share of
pair co-participations.
- **One template**: F = (2/π) arctan r, the population Kendall rank correlation between template
  and observed latencies under a normal model (Greiner's relation, via Kruskal 1958; ⚠ Greiner
  not traced). The score sort sits on it at r = 1 to 2.5 (0.503, 0.753), above it at r = 0.25
  (0.176 against 0.156, which is the no-order bias), and 2 % below at r = 5 (its own misorders).
- **M templates**: the signal term falls as 1/√M (derivation in the script; asymptotic, and it
  assumes the order agrees with every pair's net sign, so it runs up to 10 % high at M = 2–16). The
  no-order bias adds in quadrature.
- **No order**: F ≈ c/√n̄, n̄ the events a pair of cells shares, which is the rate of a sum of
  random signs. **c is fitted, not derived**: 0.38 under the score sort and 0.50 under a local
  search at 33 cells and 10 per event; across 15–100 cells and 5–30 per event, 0.22–0.51 (score
  sort) and 0.31–0.60 (local search). Kreuz et al. 2017 (sec. 2.5, 3.1) already describe the
  finite-size effect and note the null would be binomial if pairs were independent.

**At the lab's scale the order signal may sit below the bias.** With about 30 events per
recording and 7–13 of 33 cells per event, n̄ is about 1–4.5, so the score-sort bias is about
0.18–0.35. At r = 2.5 the template signal falls below that at about 4 or more templates. r in
the real recordings is unknown.

**Against Kreuz's synfire measure, the comparison is not yet made.** Kreuz's sort is a search
(simulated annealing over orders); his indicator itself is not. F differs from SPIKE-order and
its Synfire Indicator (Kreuz, Satuvuori, Pofahl & Mulansky 2017, *New J Phys* 19:043028) in four
ways:

| | F here | Kreuz's Synfire Indicator |
|---|---|---|
| coincidences | known events | ISI-adaptive windows, which on sparse trains also pair onsets of neighbouring events (a reviewer's test, 33 cells, an event every 25 s: +33 % coincidences) |
| order | score sort, no search | simulated annealing (PySpike; it draws from the C library's `rand()`, so a numpy seed does not fix it) |
| normalization | pair co-participations | all spikes (eq. 14): with no background F_Kreuz = F (k − 1)/(N − 1), 0.28 at 10 of 33 cells, and less with background spikes |
| null | relabel, or the fitted c/√n̄ | surrogates that swap order within coincidences and keep spike times (sec. 2.5); the August relabel null, which permutes which cell owns each onset, is a different null |

- **The August anti-correlation with spike count** (fast ρ −0.75, slow ρ −0.40;
  [`todo/2026-08-19-synfire-measured-and-what-it-cost.md`](../todo/2026-08-19-synfire-measured-and-what-it-cost.md))
  **is consistent with a finite-size bias but untested.** The same todo's order-free control (40
  generated recordings) had a median indicator of 0.101, against 0.036 fast and 0.099 slow.
  Dilution by non-coincident spikes and cross-event coincidences predict a negative correlation
  too. Kreuz et al. 2017 (sec. 3.1) warn that F is "not sufficient to reliably compare two
  datasets with widely different number of spike trains and spikes". The test: `synfire_scan.py`
  on order-free simulations matched to those recordings' cells and spike counts, with and
  without `max_tau`.
- **Prior art for the fast sort.** Sorting by net wins approximates the best order within a
  factor of 5 when pair weights are normalized (Coppersmith, Fleischer & Rudra 2010, *ACM Trans
  Algorithms* 6:55; ⚠ abstract), and Borda counting is optimal up to constants for ranking from
  noisy pairwise comparisons (Shah & Wainwright 2018, *JMLR* 18:199; ⚠ abstract). Kreuz's lab has
  replaced annealing with direct pairwise estimates for latency correction, not for the sort
  (Kreuz et al. 2022, *J Neurosci Methods* 381:109703; Mariani et al. 2025, *J Neurosci Methods*
  416:110378, 9.7 s against 861.8 s on one 183-train dataset). Their 2026 review (*Biol Cybern* 120,
  2026) still sorts by annealing.

### What membership and order change for the generator

A source should carry participation and jitter (k, σ), a membership rule (random, or an assembly
reused E/M times) and a latency template (spread δ). That is close to the PP-Seq model of
Williams, Degleris, Wang & Linderman (NeurIPS 2020), a Neyman–Scott process with per-neuron
offsets whose number of sequence types is chosen by cross-validation; a candidate comparison for
Aim 1c.

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
| A fixed K does not transfer across backgrounds; the assessor cannot measure jitter | measured (one generator) | *Aim 1a, first result* |
| The coordination-rates tool's participants are predicted from the planted parameters for events of 10+ cells; rate and share less well | derived and checked | *Aim 0, the predictions* |
| A joint fit across the tool's windows recovers jitter from 0.2 s up, and participants and rate, for events of 10+ cells | derived and checked | *Aim 0, the predictions* |
| Chance clusters at K follow 60 q (1 − q)² per minute | derived and checked (background only) | *Aim 0, the predictions* |
| Assembled participation's excess falls as 1 + (E − 1)/M under random, equally used assemblies and perfect readout | derived and checked | *Aim 0, membership* |
| One latency template gives F = (2/π) arctan r; the no-order constant is fitted | derived and checked; fitted | *Aim 0, order* |
| Three sessions reached the same core derivation | consistency check, not review | *Aim 0, checked by two more sessions* |

## Tried and dropped

- **A Poisson treatment of the event train** (first derivation): left a participant residual of
  about 0.05 of planted (up to 0.20 at the 4 s window); the at-most-one-event term removes it.
- **One background per condition** (the first Aim 1a run): five shared draws made errors
  correlated across each row of the first run's figure.
- **A one-parameter jitter fit of the pair count across windows**: it ignored the
  at-most-one-event term, so "0.2 s reads 0.17 s" and the "floor near the frame" were partly
  model error and partly the fit's search bound. Replaced by the joint fit.
- **A frame-rounding term in window sharing**: rounding onsets to the frame adds nothing in
  expectation, and the term biased the joint fit about 18 % low at 0.05 s. Dropped.
- **Chance plus every planted event as the assessor's cluster rate**: it assumed every event
  reaches K. Replaced by the chance term on background-only recordings.
- **A 10-recording chance arm**: too few clusters at K = 4 and 0.01 Hz to test a 2× difference.
  Replaced by 100 recordings per background.
- **A membership detection rule written for the script** (one statistic against one null):
  replaced by the repository's own assembly verdict.

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
test the prediction and measure what is left over. Next, in order: first the checks owed by
results this page already states, then the derivations later aims will use.
1. Compare the order indicator with PySpike's on the same trains, and run `synfire_scan.py` on
   order-free simulations matched to the August recordings (cells, spike counts), with and
   without `max_tau`, before any explanation of the August result is claimed.
2. Ask Tony whether the lab has already asked Kreuz or Mulansky about a fast sort or an
   analytical null (see *Waiting on Tony*).
3. Check by simulation the two-source prediction (equal jitters leave only a combined
   participation term in pair and triple counts), and that a latency template reads as jitter
   in the joint fit.
4. Model planted-event detection (the chance that an event reaches K) for the assessor and the
   count detector, and the readout dilution of the membership excess.
5. Derive the detectability threshold for membership structure in the cell-by-cell co-activation
   matrix: planted low-rank structure against sampling noise (Baik & Silverstein 2006 for real
   matrices; Baik, Ben Arous & Péché 2005; ⚠ neither opened). The repository has met its limits:
   `bugarach.assembly` notes that the Marchenko–Pastur bound is unavailable with fewer events than
   cells, and [`assembly_report.md`](../assembly_report.md) found PCA against it flags every
   simulated recording. The method to compare against originates in Lopes-dos-Santos et al. 2011
   (*PLoS ONE* 6:e20996) and Peyrache et al., restated in Lopes-dos-Santos et al. 2013.
6. Bound (λ, k, σ) from the likelihood of the cluster process (Cramér–Rao, or composite
   likelihood where it is intractable; Wang, Degleris, Williams & Linderman 2023, *JASA*, do
   likelihood inference for Neyman–Scott processes) as Aim 1's identifiability boundary.
7. Check the [slow-comodulation](../GLOSSARY.md) prediction: shared slow rate change adds pair
   excess that grows with the window while coordination levels off (Staude, Rotter & Grün 2008,
   *Neural Comput* 20:1973, separate coordination from rate covariation).
8. Compare the joint fit's jitter with the correlogram tool (`tools/measure_jitter_correlogram.py`,
   the repository's calibrated jitter measure) on the same recordings, once it can read a
   synthetic folder.
9. Re-plot Figure 1 on dimensionless axes (σ/w, λw, N·b·w, K against the event floor) and place
   the Aim 2 grid around the predicted boundaries.

No closed form is planned for CoactDetect's and LoCo's rolling context and merge gaps, for
clustered intervals, or for per-cell burstiness; those are checked by simulation only.

**Aim 1: recover the parameters, and find where they stop being identifiable.**
1a. One source, random membership: sweep jitter, participation, event count and background rate;
    measure with the two in-memory tools, without the planted values; plot true against recovered. *First experiment.*
1b. One source, fixed assembly: the same sweep, plus whether `bugarach.assembly`'s recurrence test
    finds the assembly.
1c. Two sources: sweep how far apart their jitters, intervals and participations are. The output is
    the separation below which the tools report one source.
Needs, in order: multi-source and assembly support in the generator (seeds of existing calls stay
byte-identical; `tests/test_real_intervals_off_by_default.py` guards that), and a `source` field on
`PlantedEvent`.

**Aim 2: a capability map per detector.** Factorial grid over jitter, participation,
background rate, shared slow comodulation (needs the generator change above), intervals, number of
channels, membership and source separation. Same tuning budget in every condition. Recall scored **per
source**, false alarms on the rate-matched negative. One column scored on a generator setting the
detectors were not tuned on.

**Aim 3: close the loop.** Treat a held-out synthetic recording from a different generator setting
as the "real" one: measure, simulate, choose detectors from the maps, tune, detect, and re-measure
the parameters from the calls. Cossart's statistics (`docs/learned/assessment_cossart.json`) stand
in for a stranger's data.

## Waiting on Tony

- **Has the lab asked Kreuz (or Mulansky)** whether a fast sort or an analytical null for the
  Synfire Indicator exists? The repository's correspondence with Kreuz does not cover it. His
  letter of 2026-04-23 (paraphrased in
  [`todo/2026-08-24-kreuz-answered-the-spike-synch-questions-in-april.md`](../todo/2026-08-24-kreuz-answered-the-spike-synch-questions-in-april.md))
  pointed to his own papers on a construction this repository had claimed. Ask before the score
  sort or the 1/√n̄ scaling is offered as new.

## Open work a session can do without a ruling

1. Aim 0's numbered next steps (*The plan*), items 1 and 3–9.
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
| Aim 0 and Aim 1 scripts, records and figures | [`docs/learned/synthetic_validation/`](../learned/synthetic_validation/README.md) |
| Figures for reading | also in the darkroom, `bugarach/2026-10-23-synthetic-validation/` (claimed in `docs/SESSIONS.md`) |
| The murderboard of Aim 0 | [run record](../reviews/synthetic-validation-aim0_2026-10-23.md) and its role reports |

## Keeping this page true

- **A result toward this goal updates this page in the same PR.** A decision moves from *Waiting
  on Tony* to *Settled* with its date; a dropped approach moves to *Tried and dropped* with its
  reason.
- **A session working on this goal says so on its board claim** (`Goal: synthetic-validation`)
  and names its branch `synth/<slug>`.
- **Every number on this page is recomputed by a script beside its record** (`theory.py`
  `summary()`, `membership_limit.py`, `order_limit.py`). A number changed by hand is a number
  nobody will recompute.
