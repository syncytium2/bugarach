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
  source of coordinated events, random membership, 240 simulated recordings measured without the
  planted values. A fixed threshold does not transfer across backgrounds. The assessor reads
  jitter only against the quieter background, and only up to about 0.7 s. Rerun the same day
  with a seed per recording.
- 2026-10-23: **Aim 0 (theory) added** after Tony asked whether an analytical prediction could
  replace the brute force. For events of 10 or more cells, the coordination-rates tool's
  participants are predicted to within about 0.01 at every jitter. A fit across its three
  windows recovers jitter from 0.2 s up; the lab's own jitter (0.10–0.15 s) sits in the untested
  gap below that. Two more Claude sessions, with the same prompt and model, reached the same
  core derivation (a consistency check). Nothing here tests two sources yet.
- 2026-10-23: **membership and order.** Fixed groups of cells reused across events look more and
  more like random participation as the groups multiply, if the total number of events stays
  fixed. An order indicator has closed forms; with no order present it carries a bias that grows
  as events get fewer. It has not been compared with Kreuz's Synfire Indicator on the same data.
- 2026-10-23/24: **reviewed by 11 Claude review agents** (no human reviewer) in three rounds, the
  later two blind to the earlier findings
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
| condition | one grid point (k, σ, E, b), simulated as 5 recordings | 48 conditions |
| M | the number of assemblies, or of latency templates | |
| δ, r | a template's spread of offsets (s); r = δ/σ | |
| F, n̄ | the order indicator; the mean number of events a pair of cells shares | |

- **The coordination-rates tool** (`tools/measure_coordination_rates.py`) counts how much more
  often pairs and triples of cells are active in the same window than in time-shifted copies of
  the recording (the surrogates). It converts that into participants per event, events per
  minute and the coordinated share of onsets (the fraction of all onsets that belong to a
  coordinated event). It needs no event definition and no threshold.
- **The assessor** (`bugarach.assess`) finds clusters of at least K active cells in 1 s bins,
  gathers each cluster's onsets within ±1.5 s, and reports participants, rate and onset jitter.
- **Population-count tools** see only how many cells are active in each window or bin: these two
  and the count detector. **Cell-by-cell statistics** look at which cells are active together:
  `bugarach.assembly` and an order indicator.
- **An assembly** is a fixed set of cells reused across events. **A latency template** is a fixed
  lead or lag per cell, the same in every event of one source; it is what Kreuz's SPIKE-order
  looks for.

### Aim 1a, first result (2026-10-23; measured; reseeded the same day)

![Figure 1](../learned/synthetic_validation/synth_recovery_plot_one-source-jitter_20261023.png)

**Figure 1, recovery against planted jitter, events of 10 or more cells.** 160 of the 240
simulated recordings (33 cells, 45 min each); 5-cell events are quoted in the text. Each point is
a median over participation, event count and the 5 recordings per condition; bars are the
interquartile range. A–C, E–G: recovered ÷ planted. D, H: recovered jitter in seconds against the
identity line, so an estimator that returns a constant draws as a flat line; the assessor's
jitter is drawn only where the assessor marks it defined. A fixed K fails at the higher
background (F), and there the assessor's jitter is flat (H). The violet joint fit is Aim 0's,
explained in the next section. Each recording has its own seed; the first run's shared
backgrounds are in *Tried and dropped*.

Numbers below are per-condition medians for events of 10 or more cells unless marked pooled;
`theory.py --from-record` prints them.
- **A fixed K does not transfer across backgrounds.** At 0.05 Hz per cell, chance alone gives the
  assessor 7.97 clusters per minute at K = 3 cells and 3.85 at K = 4, against 0.33 or 1 planted
  events per minute (measured on background-only recordings; pooled in F). By the assessor's own
  rule, chance falls to one cluster per hour or fewer only from K = 5 at 0.01 Hz and K = 8 at
  0.05 Hz. ADR-0008's event floor, which counts in a sliding 2 s window against the same budget,
  gives 6 and 12 cells, and both blind passes derived it to within one cell. A K that is safe
  against chance also loses spread-out events: at 0.01 Hz, K = 6 finds 0.76–0.80 of planted
  10-cell events at 0.5 s jitter and 0.29–0.33 at 1 s, because their onsets fall in several
  bins (B). That is the case for a threshold set per recording from its own null, as ADR-0008's
  floor is set per window.
- **The assessor reads jitter only against a quiet background, and only up to about 0.7 s.** At
  0.01 Hz, K = 4 reads 0.07, 0.23, 0.49 and 0.72 s for planted 0.05, 0.2, 0.5 and 1 s (D). At
  0.05 Hz it reads 0.64–0.73 s at K = 3 or 4 and 0.43–0.68 s at K = 6, whatever was planted
  (H). The ceiling is the ±1.5 s gather: a 1 s Gaussian cut there has SD 0.74 s. At low jitter
  and high background, chance onsets inside the gather set the reading; both blind passes
  model the assessor's output as a mix of chance and event clusters (B reports a 2 % median
  error on its jitter).
- **Participants need a window wider than the jitter.** At 1 s jitter the 1 s window reads
  0.34–0.42 of planted and the 4 s window 0.68–0.85 (A, E); across all jitters the 4 s window
  stays within 0.68–1.04. At 1 s jitter the same tool's event rate at the 1 s window reads
  1.6–2.4 times planted (B, F). Aim 0 predicts both.
- **The coordinated share moves least**: 0.78–1.11 of planted at the 2 and 4 s windows at
  0.01 Hz, and 0.67–1.11 at 0.05 Hz.
- **5-cell events** sit below the event floor at 0.05 Hz, and there every estimate is
  noise-dominated: up to 6.3 times planted (participants) and 6.4 (rate). K = 6 cannot count a
  5-cell event from its own cells; chance joiners lift a few to 6 (0–0.27 of planted at
  0.01 Hz).

### Aim 0, the predictions (2026-10-23; derived, checked against Aim 1a)

Tony, 2026-10-23: *"Is it possible there's an analytical prediction to be made here? We are
solving this with brute force."* For this generator, mostly yes. Aim 1a's two failures are what
it answers: chance clusters set where a fixed K fails, and window sharing sets what each window
can read. Derivations and assumptions are in
[`theory.py`](../learned/synthetic_validation/theory.py). `check()` recomputes everything here in
about a minute into [`theory_check.json`](../learned/synthetic_validation/theory_check.json),
from the run record [`aim1_one_source.json`](../learned/synthetic_validation/aim1_one_source.json).

**The core prediction.** A window of width w catches all n onsets of one event with probability
g_n(w, σ). The tool assumes every window catches all of an event's onsets, so it reports
k̂ = 2 + (k − 2) g_3/g_2. As the jitter approaches the window, g_3 falls faster than g_2 and k̂
falls toward 2: the *window must exceed the jitter* result. Events here are at least 20 s apart,
so a window never holds two of them. A Poisson event train would let two events share a window
now and then; the **at-most-one-event term** removes that contribution from the expected pair and
triple counts.

![Figure 2](../learned/synthetic_validation/synth_recovery_plot_one-source-predicted-against-measured_20261023.png)

**Figure 2, predicted against measured, one point per condition and window.** A–C, E–G: the
coordination-rates tool's three estimates as ratios to planted. Coloured points use the full
prediction (with the at-most-one-event term); grey points are the same measurements placed at
the prediction for a Poisson event train. D, H: chance clusters per minute on 100 background-only
recordings per background, pooled, with exact Poisson 95 % intervals (smaller than the markers).
The at-most-one-event term shrinks the participant residual from about 0.05 to 0.007–0.016.

The residual below is |condition median of recovered ÷ planted − predicted ÷ planted|. The tool
refused an estimate (pair or triple count ≤ 0) in 17 of 720 recording-windows, all 5-cell events
at 0.05 Hz; the medians exclude them and the prediction cannot, so those medians carry a
selection. "Of 48" below means condition-windows for events of 10 or more cells at one background
(16 conditions × 3 windows); the three windows reuse the same recordings.
- **Participants: predicted to within about 0.01, slightly high.** Median residual 0.007 (worst
  0.037) at 0.01 Hz and 0.016 (worst 0.11) at 0.05 Hz; about 0.05 without the at-most-one-event
  term. 7 and 10 of 48 sit beyond 2 SE of their condition's 5 recordings, where about 6 are
  expected: the SE of a median from 5 values is heavy-tailed, and its simulated null rate is
  0.118. The direction is consistent: measured is below predicted in 34 and 31 of 48 (sign test
  p = 0.006 and 0.06), by a median 0.006 and 0.005.
- **Chance clusters at K: the first failure.** On background-only recordings the assessor's
  rate is 60 q (1 − q)² per minute, q the chance a 1 s bin holds K or more active cells; squared
  because the assessor starts a cluster only when the two preceding bins are below K. Predicted
  0.256 and 0.019 per min at K = 3 and 4 cells and 0.01 Hz (measured 0.262, 0.020); 7.97, 3.86
  and 0.284 at 0.05 Hz (measured 7.97, 3.85, 0.279); all within their 95 % intervals. At K = 6
  and 0.01 Hz the prediction is 5 × 10⁻⁵ per min, 0.2 clusters in the whole arm, so measuring 0
  tests nothing. Whether a planted event reaches K is not modelled here.
- **Jitter, participants and rate, fitted together across the 1, 2 and 4 s windows: the second
  failure.** For events of 10 or more cells, planted 0.2, 0.5 and 1.0 s read 0.22, 0.50 and
  1.01 s at 0.01 Hz and 0.20, 0.52 and 1.01 s at 0.05 Hz (condition medians within 0.88–1.13 of
  planted); participants within 0.94–1.14 and rate within 0.73–1.14 per condition. Not
  resolved: planted 0.05 s (reads 0.075 and 0.039 s; 1 and 4 of 20 fits at the 0.005 s search
  bound) and 5-cell events (jitter 0.1 to 3.6 times planted). **The lab's measured jitter,
  σ = 0.105–0.150 s ([GLOSSARY](../GLOSSARY.md)), lies between the resolved and unresolved points
  and is untested** (plan item 1). A latency template would add to the jitter here (derived, not
  simulated; see *Order*). The fit assumes one k, Gaussian jitter and events at least 20 s apart;
  real data will need a mixture over k (blind A).
- **Event rate and share: predicted less well; measured high at 0.01 Hz.** The rate residual
  has median 0.03 (worst 0.18) at 0.01 Hz and 0.06 (worst 0.38) at 0.05 Hz; the share 0.02 (worst
  0.07) and 0.02 (worst 0.28). Measured exceeds predicted in 43 (rate) and 41 (share) of 48 at
  0.01 Hz, and in 30 and 29 at 0.05 Hz, which is no consistent direction. Candidate cause: the
  surrogates' shifted copies are not independent of the event train. A review agent's test found
  that term of the right sign and size, about 1 % of the pair count and so about 3 % in rate (run
  record; not kept here).
- **Not predicted: 5-cell events at 0.05 Hz**, which are noise-dominated (see Aim 1a).
- **Two sources: predicted, not tested.** Two sources with the same jitter leave only their
  combined participation term in pair and triple counts, so these tools cannot tell them apart
  (blind B; plan item 2).

**What it rests on.** The generator is a Neyman–Scott cluster process (Neyman & Scott 1952,
*ApJ* 116:144, restated 1958 in *J R Stat Soc B* 20:1; ⚠ abstract only). Its Gaussian-scatter case is
now called the Thomas process, after Thomas 1949 (*Biometrika* 36:18; ⚠ not opened), but here
the number of events is fixed and they are held apart rather than Poisson-placed. The tool's
route is the cumulant route of CuBIC (Staude, Rotter & Grün 2010, *J Comput Neurosci* 29:327) on
the multiple-interaction model of Kuhn, Aertsen & Rotter 2003, with factorial rather than
ordinary cumulants. Grün et al. 1999 (*J Neurosci Methods* 94:67) derived the two-onset,
uniform-jitter case of window loss ("fission probability") and read the temporal scatter from how
detection changes with the analysis width. Pazienti et al. 2008 (*Brain Res* 1225:39; ⚠ abstract
only) estimated synchronization precision from how detection decays with the dither width at one
fixed window. **The joint fit's idea is not new.** Louis & Grün 2009 (*BMC Neurosci*
10(Suppl 1):P253) and Louis, Borgelt & Grün 2010 (*Neural Netw* 23:705; ⚠ abstract only) fit group
size and jitter together from the population count's distribution across bin widths. Spatial
statistics fits a Thomas process's scatter and parent rate by minimum contrast on its pair-count
curve across scales (Diggle, Besag & Gleaves 1976; Waagepetersen 2007; ⚠ software documentation
read, not the papers). What is added here: g_n for Gaussian jitter and n onsets, the pair-and-
triple form, the at-most-one-event term, and the event rate in the same fit. ⚠ Not searched:
quadrat-variance ecology, physics counting statistics, composite likelihood for cluster
processes.

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
| expected pair and triple counts with the at-most-one-event term | full form | drops the surrogate's 1/N and 1/N² corrections | drops the 1/N² correction in the triple term |
| k̂ = 2 + (k − 2) g_3/g_2 | yes | yes | yes |
| jitter from how the pair count changes with window | one-parameter fit (dropped) | joint fit (adopted, re-specified) | ratio of two windows, read 0.2 s 5–15 % high |
| chance clusters 60 q (1 − q)² per min | yes | yes | yes |
| two equal-jitter sources inseparable from pair and triple counts | taken from B | implied by its linear form, not stated | stated, untested |

**What only the blind passes found:**
- the shared-background flaw in Aim 1a (both);
- the noise of each estimate, and with it when the tool will refuse (A and B by two different
  approximations; CuBIC gives its own estimators' noise);
- the assessor's participants and jitter as a mix of chance and event clusters (both);
- the event floor as the rate at which chance first crosses a count, within one cell of the
  simulated floor (both; `tools/measure_chance_floor.py` already had a closed form for its
  sliding window);
- count-detector recall within about 0.03 of simulated recall in 20 of B's 24 conditions (B);
- the joint fit (A).

**Open residuals:** B's report gives the triple count 5–7 % below prediction at 0.05 Hz over 60
seeds (its saved 40-seed run: 3–19 % per window); A, the rate 3–5 % high.

### Aim 0, membership (2026-10-23; simulated with membership as the only structure)

Tony asked whether the analysis generalizes so that, as sources multiply, assembled participation
converges to random. **Yes, if the total number of events is fixed as assemblies multiply**: the
excess over random then falls as 1/M. If instead each new assembly brings its own e events
(E = M e), the excess stays near e and never reaches random. Membership is invisible to every
population-count tool at any number of sources; only cell-by-cell statistics see it.

The model ([`membership_limit.py`](../learned/synthetic_validation/membership_limit.py)): M
assemblies of k random cells (they may overlap), each event picking one with equal probability,
and perfect readout (every member seen, no background cell joining). Two events then share an
assembly with probability 1/M, and the variance of pair co-participation counts across cell pairs
is **1 + (E − 1)/M** times its value under random participation. For unequal use, 1/M becomes
Σ p_m², p_m the share of events that use assembly m. This has the form of Kish's design effect
(1965; ⚠ analogy, book not opened). Real readout dilutes the excess; no correction is derived yet.

![Figure 3](../learned/synthetic_validation/synth_assembly-membership_plot_assemblies-converge-to-random_20261023.png)

**Figure 3, assembled against random participation.** 33 cells, 10 per event, 45 events. A: the
pair co-participation variance divided by its value under random participation, mean of 400
simulations; the seven points share one random baseline, so their common 1–2 % shortfall is one
error, not seven. B: the share of 60 recordings in which the repository's assembly test
(`bugarach.assembly`, 200 surrogates per null; the package default is 1000) rejects both of its
nulls, and either one. Its two nulls are a margin-preserving null, which keeps each cell's event
count, and a uniform null. Dotted: both reject in 1 of 60 recordings under random participation.

Both nulls reject in every recording while reuse E/M is between 1 and 15, in 72 % at 0.3 and in
13 % at 0.045 (B). At M = 1 only the uniform null rejects: one assembly holding every event is the
case the margin-preserving null cannot see, as the module documents.

### Aim 0, order (2026-10-23; simulated with order as the only structure)

**The question.** In August the synfire indicator from `tools/synfire_scan.py` fell as spike
count rose (fast ρ −0.75, slow ρ −0.40;
[`todo/2026-08-19-synfire-measured-and-what-it-cost.md`](../todo/2026-08-19-synfire-measured-and-what-it-cost.md)).
Tony expects Kreuz's method to be brute force and slow. Does an order indicator have a closed
form, and how large is it when no order is present?

**A latency template also reaches the population-count tools, as extra jitter** (derived, not
simulated; on average over random membership). With template spread δ and jitter σ, two
participants' lag has SD √(2(δ² + σ²)), so g_n and the joint fit see √(δ² + σ²). Only cell-by-cell
statistics separate the two.

**The method** ([`order_limit.py`](../learned/synthetic_validation/order_limit.py)): known events,
no background. For each pair of cells, count who leads across the events they share. The **score
sort** orders the cells by each one's net lead count (a Borda count; O(N²), no search). The
**local search** then moves single cells while that raises F. **F** is the net agreement of the
pair lead signs with the order (agreeing minus disagreeing), as a share of pair co-participations:
1 for a perfect sequence, near 0 with no order once events are many. The 0.1 s frame grid is
omitted; rounded onsets tie, and a review agent's test found that lowers F about 9 % at
δ = σ = 0.1 s.

![Figure 4](../learned/synthetic_validation/synth_recovery_plot_order-indicator-closed-forms_20261023.png)

**Figure 4, an order indicator against its closed forms and fits.** 33 cells, 10 per event. A: one
template, 200 events; solid, (2/π) arctan r; dashed, the same with the no-order bias of 200
events added. B: M templates at r = 2.5, 2000 events; solid, the many-template signal, an
asymptotic form that at M = 2 already sits well below the one-template value at M = 1 (diamond);
dashed, with the no-order bias added. C: no order planted, under both sorts. All three panels
share one log axis.

- **One template**: F = (2/π) arctan r, equivalently (2/π) arcsin(r/√(1 + r²)): the population
  Kendall rank correlation between template and observed latencies under a normal model
  (Greiner's relation, via Kruskal 1958; ⚠ neither opened). The score sort sits on it at r = 1
  to 2.5 (0.503, 0.753) and 2 % below at r = 5 (its own misorders). At r = 0.25 it reads 0.176
  against the closed form's 0.156; the 0.02 excess is the no-order bias.
- **M templates**: the signal falls as 1/√M from a constant √(2/π) · √((2/π) arcsin(r²/(1 + r²))),
  0.65 at r = 2.5 (derivation in the script). It is asymptotic and assumes the order agrees with
  every pair's net sign, so it runs up to 10 % high at M = 2–16. The no-order bias adds in
  quadrature.
- **No order**: F ≈ c/√n̄, the 1/√n scaling of a mean of random signs. **c is fitted, not
  derived**: 0.38 under the score sort and 0.50 under the local search at 33 cells and 10 per
  event, over n̄ = 2–68; across 15–100 cells and 5–30 per event, 0.22–0.51 (score sort) and
  0.31–0.60 (local search). Kreuz et al. 2017 (sec. 2.5, 3.1) already describe the finite-size
  effect and note the null would be binomial if pairs were independent.

**With few events the no-order bias is large, and raw indicators are not comparable across
recordings.** Simulated directly at 33 cells under the score sort: with 7 cells per event the
no-order F is 0.48 ± 0.06 at 10 events (n̄ 0.4) and 0.14 ± 0.02 at 140 (n̄ 5.6); with 13 per
event, 0.34 ± 0.04 and 0.09 ± 0.01. A calibrated null such as `synfire_scan.py`'s relabelling
removes the mean bias; what limits detection is the null's spread. At r = 2.5, a template signal
clears that null by 2 SD up to about 3 templates at 10 events of 7 cells, and up to about 80 at
140 events of 13 cells. The lab's events per recording are not settled here: the glossary's 9.7–25.3
coordinated events per hour give 10–25 in a 59 min recording, but its median intervals of
25–41 s imply more. r in the real recordings is unknown.

**Against Kreuz's synfire measure: not yet measured on the same trains.** His sort is a search
(simulated annealing over orders); his indicator itself is not. F differs from SPIKE-order's
Synfire Indicator (Kreuz, Satuvuori, Pofahl & Mulansky 2017, *New J Phys* 19:043028) in four
ways:

| | F here | Kreuz's Synfire Indicator |
|---|---|---|
| coincidences | known events | ISI-adaptive windows. On sparse trains they also pair onsets of neighbouring events, and those pairs lean against the planted order. A review agent's PySpike 0.9.0 test (33 cells, 10 per event, r = 2.5; not kept here): 36 % more coincidences with an event every 25 s, which put his indicator 23 % below its known-event value; 44 % more with irregular gaps |
| order | score sort, no search; its speed and power against annealing are not measured | simulated annealing (PySpike; it draws from the C library's `rand()`, which a numpy seed does not fix) |
| normalization | pair co-participations | all spikes (eq. 14): with no background and known coincidences F_Kreuz = F (k − 1)/(N − 1), 0.28 at 10 of 33 cells, and less with background spikes |
| null | relabelling, or the fitted c/√n̄ | surrogates that swap order within coincidences and keep spike times (sec. 2.5). The August relabel null permutes which cell owns each onset across the whole recording: a different null, which approximates the exchangeable limit (cells interchangeable within events) and also moves background onsets |

- **The August fall of the synfire indicator with spike count is consistent with the no-order
  bias, but untested.** The same todo's order-free control (40 generated recordings) had a median
  indicator of 0.101, against 0.036 fast and 0.099 slow, so neither stream's median exceeds an
  order-free control. Against their own relabel null, though, 23 of 80 recordings (fast) and 44 of
  82 (slow) were significant at p < 0.05, against 3 of 40 controls. Dilution by non-coincident spikes and cross-event
  coincidences predict a fall with spike count too. Kreuz et al. 2017 (sec. 3.1) warn that their
  indicator is "not sufficient to reliably compare two datasets with widely different number of
  spike trains and spikes". The test is plan item 3.
- **Prior art for the fast sort.** Sorting by net wins comes within a factor of 5 of the fewest
  disagreements (a feedback arc set) when each pair's two weights sum to 1 (Coppersmith,
  Fleischer & Rudra 2010, *ACM Trans Algorithms* 6:55; ⚠ abstract); that bounds disagreements, not
  F. Borda counting is optimal up to constants for ranking from noisy pairwise comparisons (Shah &
  Wainwright 2018, *JMLR* 18:199; ⚠ abstract). Kreuz's lab has replaced annealing with direct
  pairwise estimates for latency correction, not for the sort (Kreuz et al. 2022, *J Neurosci
  Methods* 381:109703; Mariani et al. 2025, *J Neurosci Methods* 416:110378: 9.7 s against
  861.8 s on one 183-train dataset). Kreuz's review (*Biol Cybern* 120(3):21, 2026) still sorts
  by annealing.

### What membership and order change for the generator

A source should carry participation and jitter (k, σ), intervals, a membership rule (random, or
an assembly reused E/M times) and a latency template (spread δ). That is close to the PP-Seq model
of Williams, Degleris, Wang & Linderman (NeurIPS 2020), a Neyman–Scott process with per-neuron
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
| A fixed K does not transfer across backgrounds; the assessor reads jitter only at the lower background (0.01 Hz) and only up to about 0.7 s | measured (one generator) | *Aim 1a, first result* |
| The coordination-rates tool's participants are predicted to within about 0.01 for events of 10+ cells; rate and share less well | derived and checked (one generator: one k, Gaussian jitter, events ≥ 20 s apart) | *Aim 0, the predictions* |
| A joint fit across the tool's windows recovers jitter from 0.2 s up (not 0.05 s; the lab's 0.10–0.15 s untested), participants within 0.94–1.14 and rate within 0.73–1.14, for events of 10+ cells | derived and checked (same scope) | *Aim 0, the predictions* |
| Chance clusters at K follow 60 q (1 − q)² per minute | derived and checked (background only; K = 6 at 0.01 Hz untestable at this size) | *Aim 0, the predictions* |
| With assemblies, pair co-participation variance is 1 + (E − 1)/M times random | derived and checked (equally used random assemblies, perfect readout, fixed E) | *Aim 0, membership* |
| One latency template gives F = (2/π) arctan r; the no-order constant is fitted | derived and checked; fitted (known events, no background, no frame grid) | *Aim 0, order* |
| Three sessions reached the same core derivation | consistency check, not review | *Aim 0, checked by two more sessions* |

## Tried and dropped

- **A Poisson treatment of the event train** (first derivation): left a participant residual of
  about 0.05 of planted (up to 0.20 at the 4 s window); the at-most-one-event term removes it.
- **One background per replicate** (the first Aim 1a run): the generator draws the background
  first, so every condition with the same replicate index got the same background, and errors
  were correlated across conditions.
- **A one-parameter jitter fit of the pair count across windows**: it ignored the
  at-most-one-event term, so its readings (0.2 s read as 0.17 s; jitter appearing to floor near
  the 0.1 s frame) were partly model error and partly the fit's search bound. Replaced by the
  joint fit.
- **A frame-rounding term in window sharing**: rounding onsets to the frame adds nothing in
  expectation, and the term biased the joint fit low at 0.05 s (8 % at 0.01 Hz, 35 % at 0.05 Hz,
  in a review agent's rerun). Dropped.
- **Chance plus every planted event as the assessor's cluster rate**: it assumed every event
  reaches K. Replaced by the chance term on background-only recordings.
- **A 10-recording chance arm**: too few clusters at K = 4 and 0.01 Hz to tell a predicted rate
  from one twice as large. Replaced by 100 recordings per background.
- **A membership detection rule written for the script** (one statistic against one null):
  replaced by the repository's own assembly test.
- **"About 2 of 48 expected beyond 2 SE"**: the normal rate, wrong for an SE estimated from 5
  values. Replaced by the simulated rate and a sign test.
- **"The assessor cannot measure jitter"**: Figure 1 D shows it can against the quieter
  background. Scoped to 0.05 Hz and the 0.7 s ceiling.
- **"The order signal sits below the bias at the lab's scale, from about 4 templates"**: it
  extrapolated a constant fitted at 10 cells per event below the event counts simulated, and
  compared the signal with the null's mean rather than its spread. Replaced by direct
  simulation at small event counts.

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
the coordinated share, with no K and no event definition). So do the correlogram tool's
`pairs` and `hwhm`. The command lines of the correlogram, real-interval and slow-comodulation
tools read `dataset.default()` only; running them on a synthetic folder needs a `--folder` flag
or a pointer swap, and there is **no library writer** for a simulated folder (three tests write
one inline).

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
test the prediction and measure what is left over. (This page adds *What the tree has* and *The
plan* to the order in [`goals/README.md`](README.md), because the aims are this goal's
structure.)

*Owed by results this page already states*, in order:
1. Add σ = 0.1 and 0.15 s (the lab's jitter) to the Aim 1a grid and rerun the joint fit; and
   compare its jitter with the correlogram tool's on the same recordings.
   `tools/measure_jitter_correlogram.py`'s `pairs` and `hwhm` take frame trains in memory, so this
   needs no `--folder` route.
2. Check by simulation the two-source prediction (equal jitters leave only a combined
   participation term in pair and triple counts), and that a latency template reads as jitter
   in the joint fit. The goal's premise is two or more sources, so this comes before the order
   work.
3. Compare the order indicator with PySpike's on the same trains (indicator, speed, and power
   against the relabel null), then run `synfire_scan.py` on order-free simulations matched to the
   August recordings (cells, spike counts) before any explanation of the August result is
   claimed. It needs a library writer for a simulated folder. A capped coincidence window also
   needs a `max_tau` flag in `synfire_scan.py` and PySpike with the unmerged PR #89: in released
   PySpike `max_tau` does not cap the window ([`FOUNDATIONS.md`](../FOUNDATIONS.md) §2). The
   annealer's `rand()` makes a rerun reproduce only in the same call order and C runtime, which
   `synfire_scan.py`'s docstring overstates.
4. Model planted-event detection (the chance that an event reaches K) for the assessor and the
   count detector, and the readout dilution of the membership excess.

*For later aims*:

5. Derive the detectability threshold for membership structure in the cell-by-cell co-activation
   matrix: planted low-rank structure against sampling noise (Baik & Silverstein 2006, *J
   Multivariate Anal* 97:1382; Baik, Ben Arous & Péché 2005, *Ann Probab* 33:1643; ⚠ neither
   opened). The repository has met the limits of the PCA method: `bugarach.assembly` notes that
   the Marchenko–Pastur bound is unavailable with fewer events than cells, and
   [`assembly_report.md`](../assembly_report.md) found PCA against it flags every simulated
   recording. That method comes from Peyrache et al. 2009 (*Nat Neurosci* 12:919) and 2010 (*J
   Comput Neurosci* 29:309), building on Chapin & Nicolelis 1999; Lopes-dos-Santos et al.
   extended it in 2011 (*PLoS ONE* 6:e20996) and restated it in 2013 (*J Neurosci Methods*
   220:149).
6. Bound (λ, k, σ) from the likelihood of the cluster process (Cramér–Rao, or composite
   likelihood where it is intractable) as Aim 1's identifiability boundary. Wang, Degleris,
   Williams & Linderman (*JASA* 119:2382, 2024) do Bayesian inference for Neyman–Scott processes;
   ⚠ the composite and Palm likelihood literature for them is not searched.
7. Check the [slow-comodulation](../GLOSSARY.md) prediction: shared slow rate change adds pair
   excess that grows with the window while coordination levels off. Staude, Rotter & Grün 2008
   (*Neural Comput* 20:1973) show how to separate coordination from rate covariation.
8. Re-plot Figure 1 on dimensionless axes (σ/w, λw, N·b·w, K against the event floor) and place
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
  Synfire Indicator exists? The repository's correspondence with Kreuz does not cover it: his
  letter of 2026-04-23 (paraphrased in
  [`todo/2026-08-24-kreuz-answered-the-spike-synch-questions-in-april.md`](../todo/2026-08-24-kreuz-answered-the-spike-synch-questions-in-april.md)),
  which pointed to his own papers on a construction this repository had claimed, and the
  August–September `max_tau` thread ([`kreuz_note.md`](../kreuz_note.md) and its two sequels), in
  which he pointed to Mariani et al. 2025. Ask before the score sort or the 1/√n̄ scaling is
  offered as new.
- **Has anyone asked the Grün lab** about the joint fit? Louis & Grün 2009 and Louis, Borgelt &
  Grün 2010 are its closest precedent (*Aim 0, the predictions*).

## Open work a session can do without a ruling

1. Aim 0's numbered next steps (*The plan*), items 1–8.
2. Aim 1a, extended: recovery against participation and event count separately (Figure 1 pools
   them).
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
- **Every simulation number on this page is recomputed by a script beside its record**
  (`theory.py --from-record`, `membership_limit.py`, `order_limit.py`). Numbers from the
  literature, the August todo and review agents' tests are marked as such. A number changed by
  hand is a number nobody will recompute.
