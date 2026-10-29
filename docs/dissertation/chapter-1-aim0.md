# Chapter 1. Predict first, simulate to check: an analytical baseline for finding coordinated events in multichannel event times

*A theory chapter checked by simulation. How it was made, and what it does not claim, is in the
note at the end.*

## 1.1 Introduction

### The problem

Reduce a calcium-imaging recording of a few dozen cells to the onset times of each cell's calcium
events, and the result is a multichannel stream of unlabeled event times. Some onsets are
coordinated: several cells have an event within a fraction of a second of one another, more often
than their own rates would produce by chance. The rest are background. Downstream analysis rests on
knowing which onsets belong to which coordinated event, how many events there were, and what
generated them.

The premise of this dissertation is that a recording mixes **two or more sources** of coordinated
events. A source is one generating process, with its own participation (how many cells join an
event), jitter (how far each participant's onset scatters about the event time), intervals between
events, membership rule (a fixed set of cells, or a fresh random set each event) and, optionally, a
latency template (a fixed lead or lag per cell). The goal is a toolset that measures those
parameters from the event times alone, simulates recordings from them, and then characterizes each
detector against known truth.

This chapter takes **one source on purpose**. Before asking whether tools can separate two sources,
it asks what they return for one, and whether that can be derived rather than simulated.

### What brute force found

The obvious way to characterize the tools is a simulation grid: plant a source at many settings,
measure each recording without looking at the planted values, and compare. The first such
experiment (*1.3*) planted one source at 48 settings in 240 recordings. It found two failures it
could not explain (Figure 1.1).

![Figure 1.1](../learned/synthetic_validation/synth_recovery_plot_one-source-jitter_20261023.png)

**Figure 1.1. At the busier background the assessor reads a constant jitter; the joint fit tracks
the planted value from 0.2 s up.** Events of 10 or more cells, 160 of the 240 simulated recordings.
Each point is a median over participation, event count and the 5 recordings per setting; bars are
the interquartile range. A–C (background 0.01 Hz per cell) and E–G (0.05 Hz): recovered ÷ planted
participants, event rate and coordinated share. D and H: recovered jitter in seconds against the
identity line, so an estimator that returns a constant draws as a flat line; markers are dodged
horizontally for visibility. The joint fit (violet) is introduced in *1.4.6*.

- **A fixed threshold does not transfer across backgrounds.** The assessor (*1.2.2*) calls a cluster
  when at least K cells are active in a 1 s bin. On recordings with no coordinated events at all,
  at 0.05 Hz per cell, chance alone gave it 7.97 clusters per minute at K = 3 and 3.85 at K = 4,
  against the 0.33 or 1 planted events per minute of the event-bearing recordings.
- **The assessor reads jitter only at the quieter background.** At 0.01 Hz and K = 4 it read 0.07,
  0.23, 0.49 and 0.72 s for planted 0.05, 0.2, 0.5 and 1 s (Figure 1.1 D). At 0.05 Hz it read
  0.64–0.73 s whatever was planted at K = 3 or 4, and at K = 6 it rose only from a planted 0.5 s
  (0.43–0.68 s; Figure 1.1 H).

A grid can find such failures. It cannot say why they happen, or where else they will.

### The question, and the answer

**For each measuring tool and each simple detector, can we derive from the planted parameters what
it should return, and use simulation only to test the derivation and measure what is left over?**
We call this Aim 0: *predict first, simulate to check*.

For one source, mostly yes. Theory explains both failures above, predicts one tool's participant
estimate to within about 1–2 % of planted, and yields a new estimator of jitter, participation and
event rate. It also says how many events and how much reuse are needed before cell-by-cell
structure becomes detectable, and why the tools, not the data, limit how close two events can be
and still be counted as two. It does not replace simulation: it tells simulation where to look, and
it is wrong in specific, measurable places that this chapter reports.

### Contributions

1. **Why a counting window undercounts participants.** A closed form for the chance that all of one
   event's onsets fall in one window when jitter is Gaussian, and from it the undercount of the
   coordination-rates tool's participant estimate as jitter approaches the window width.
2. **A correction for event trains that cannot share a window**, and its generalization to any
   stationary train of events, including the dependence of the tool's surrogates on the event train.
3. **A joint fit** that recovers jitter, participation and event rate together from the tool's pair
   and triple counts at three window widths.
4. **The rate of chance clusters** for the assessor's clustering rule at each threshold, and from it
   the smallest threshold safe against chance at a given background.
5. **When reused cell groups look random:** the excess variance of how often pairs of cells share
   events, as the number of groups grows.
6. **Order with few events:** the order indicator's value under one latency template, its exact
   mean when no order is present, and the power to detect order at 1–5 events.
7. **How close two events can be:** the separation that likelihood-ratio tests achieve, against the
   separation at which the two binning tools start merging pairs.

Which of these was already known is set out in *1.9.1*. In brief: the closest precedents are Louis,
Borgelt & Grün (2010) and CuBIC (Staude, Rotter & Grün 2010), and two contributions (4 and the
order bias in 6) are known in form from other fields.

## 1.2 Background

### 1.2.1 The data and the generative model

The input is one list of onset times per channel (a cell, or region of interest) and the
recording's duration; the frame interval is optional. The parameter values used here are realistic
ones taken from the lab's recordings, which are imaged at a 0.1 s frame and split into two event
types, called fast and slow (DeFazio et al. 2026). They serve only to choose where to simulate; no
statement in this chapter is about the recordings themselves. The realistic values are a background
rate of 0.0096 Hz per cell (measured on the fast type), onset jitter of 0.105 s (fast) and 0.131 s
(slow), and participation of 7 and 13 of 33 cells, which are the bench's middle participation
levels (0.20 and 0.38 of 33).

The generative model is a cluster process of the Neyman–Scott type (Neyman & Scott 1952): cluster
centers placed at random, and the members of each cluster scattered about its center by a
probability law. With Gaussian scatter it is called the Thomas process, although Thomas (1949) gave
only the count distribution of clustered plants in sampling quadrats, with no spatial scatter law.
Each of N cells carries independent Poisson background onsets at rate b. On top of that, E
coordinated events occur in a recording of duration T (rate λ = E/T). Each event is joined by k of
the N cells, chosen afresh; each participant's onset is the event time plus independent Gaussian
jitter of standard deviation σ, rounded to the frame. Two departures from the textbook process
matter: the number of events is fixed, not Poisson, and events are held at least 20 s apart, a
**hard-core** train, rather than placed independently.

**Table 1.1. Symbols.**

| symbol | meaning | values in the first experiment |
|---|---|---|
| N | cells in a recording | 33 |
| k | participants per event (cells) | 5, 10, 20 (participation 0.15, 0.3, 0.6) |
| σ | jitter: SD of a participant's onset about the event time | 0.05, 0.2, 0.5, 1.0 s |
| b | background rate per cell | 0.01 Hz (realistic) and 0.05 Hz |
| E, λ | coordinated events per recording; per second | 15 or 45 in 45 min |
| w | the coordination-rates tool's window | 1, 2, 4 s |
| K | the assessor's threshold, an absolute count of cells (not the glossary's percentage K) | 3, 4, 6 cells |
| g_n | the chance that all n onsets of one event fall in one window | |
| M | number of assemblies, or of latency templates | |
| δ, r | SD of a latency template's offsets; r = δ/σ | |
| F, n̄ | the order indicator; mean number of events a pair of cells shares | |

### 1.2.2 The tools

![Figure 1.2](figures/synth_raster_plot_data-and-what-each-tool-sees_20261029.png)

**Figure 1.2. What one recording looks like, and what each tool counts.** A: one minute of a
simulated 45-minute recording of 33 cells, one mark per onset. The background is 0.0096 onsets per
second per cell, and there are two coordinated events of 10 cells each with onset jitter σ = 0.2 s.
Triangles above the raster mark the planted event times. B, C: each event enlarged. Each shows its
10 cells' onsets, then those onsets per 0.1 s frame against the Gaussian they were drawn from (σ is
its SD), then the coordination-rates tool's 1, 2 and 4 s windows with the number of the event's
onsets in each. A 1 s window border splits event 1 into 4 and 6, while event 2 falls inside one
window at every width. D–F: what each tool counts in the same minute, colored by event. The
coordination-rates tool counts onsets per window, the assessor counts distinct cells per 1 s bin,
and the count detector counts distinct cells per 2 s bin; the threshold of 5 cells is set for
illustration. This minute was picked from the recording because it shows one split event and one
whole one; the onsets in it are exactly as simulated.

Three population-count tools are analyzed. Each sees only how many onsets or cells fall in a window
or bin, never which cells they are.

- **The coordination-rates tool** counts how much more often pairs and triples of onsets fall in the
  same window than in time-shifted copies of the recording (the surrogates), which keep each cell's
  own train but break the alignment between cells. It counts onsets, not distinct cells, and averages
  over two window offsets. From those excess counts it solves for participants per event, events per
  minute and the coordinated share, the rate of coordinated onsets per cell, λk/N. (As a ratio to
  planted, that share is the same as the fraction of onsets that are coordinated, which is how the
  figures label it.) It needs no event definition and no threshold.
- **The assessor** finds clusters of at least K active cells in 1 s bins, joining triggered bins
  that have at most one untriggered bin between them, gathers each cluster's onsets within ±1.5 s,
  and reports participants, rate and onset jitter.
- **The count detector** calls a coordinated event wherever the number of distinct cells active in a
  2 s bin reaches a threshold, joining called bins with at most one uncalled bin between them (its
  3 s merge gap).

A fourth population tool, the **correlogram tool**, estimates jitter without bins, from the width of
the peak in the cross-cell onset correlogram; it is compared with this chapter's joint fit in *1.4.5*.

Two further statistics look at *which* cells are active together: the repository's **assembly
test** (*1.6.1*) and an **order indicator** (*1.6.2*).

### 1.2.3 Prior work

**Coincidences across bin widths.** Grün et al. (1999, eq. 5) derived the chance that a
near-coincidence is split by a bin border, averaged over a displacement of up to ±j time steps (the
"fission probability"), and showed how detection depends on the analysis bin width. Pazienti et al.
(2008) derived how dithering interacts with jittered coincidences and estimated synchronization
precision from how detection decays with the dither interval, at a single tolerated spread. Louis,
Borgelt & Grün (2010), building on Grün, Abeles & Diesmann (2008), gave the full distribution of the
population count for groups with **uniform** jitter: given how far a jitter window overlaps a bin,
each member is captured independently, so the group contributes a binomial count. They estimated
group size and jitter from where one feature of the observed-minus-independent distribution (its
second maximum) changes slope as the bin widens, by fitting two straight lines to that feature's
trajectory.

**Cumulants of the population count.** CuBIC (Staude, Rotter & Grün 2010) infers a lower bound on the
order of correlation from ordinary cumulants of the population count, under a compound Poisson model
with a Poisson carrier and exactly synchronous copies; the multiple-interaction model of Kuhn,
Aertsen & Rotter (2003) is a special case. The same group extended the approach to non-Poisson spike
trains (Reimer et al. 2012 ⚠) and fitted rates per event size (Ehm, Staude & Rotter 2007 ⚠).

**Cluster processes.** In spatial statistics the parameters of a Neyman–Scott process are fitted by
minimum contrast on its K-function, the pair-count curve across scales (Diggle 1983 ⚠; Diggle &
Gratton 1984, who also fit models that can only be simulated by matching simulated summaries); the
Thomas process's K-function has a closed form used in practice (Waagepetersen 2007). Neyman–Scott
rainfall models are fitted by matching moments of totals at several aggregation windows, and recover
storm arrival rate and cells per storm (Rodriguez-Iturbe, Cox & Isham 1987 ⚠). PP-Seq (Williams et
al. 2020) is a Neyman–Scott model of neural sequences with per-neuron offsets, and Wang et al. (2024)
give Bayesian inference for the class.

**Assemblies.** The PCA assembly method with a Marchenko–Pastur null comes from Peyrache et al.
(2009 ⚠, 2010), building on Chapin & Nicolelis (1999 ⚠), and was extended by Lopes-dos-Santos et al.
(2011, 2013 ⚠).

**Order.** Kreuz, Satuvuori, Pofahl & Mulansky (2017) define SPIKE-order and the Synfire Indicator,
which finds an order of spike trains by simulated annealing and scores it against surrogates. The
same group applied it to wide-field calcium imaging with Pavone's imaging group (Cecchini et al.
2021), introduced a direct shift beside annealing for latency correction (Kreuz et al. 2022) and
later an extrapolation direct shift for it (Mariani et al. 2025); its 2026 review still orders trains
by annealing (Kreuz 2026 ⚠).

## 1.3 Methods: the testbed and how the theory is checked

**The first experiment** simulated one source, with a fresh random set of participants per event, on
a grid of 4 jitters × 3 participations × 2 event counts × 2 backgrounds = 48 settings, 5 recordings
each: 240 recordings of 33 cells and 45 minutes. Each was measured without access to the planted
values, with the coordination-rates tool at its shipped windows (1, 2 and 4 s) and the assessor at
K = 3, 4 and 6. A further 200 background-only recordings (100 per background) tested the
chance-cluster rate. A first run of this grid shared backgrounds across settings (every setting with
the same replicate index had the same background), so its errors were correlated; it was rerun with
a seed per recording, and every number here is from the rerun.

**The residual** for each setting and window is the absolute difference between the setting's median
recovered ÷ planted ratio and the predicted ÷ planted ratio, unless marked signed. Every prediction
is passed through the tool's own estimator, so prediction and measurement are the same calculation,
down to its refusal when a count is not positive. The tool refused in 17 of 720 recording-windows,
all 5-cell events at 0.05 Hz; the medians exclude those, and the predictions cannot.

**A held-out record.** Some model choices were made while looking at the first experiment: a
frame-rounding term was dropped because it biased jitter low on these recordings, the joint fit was
re-specified, and the event-train form was judged partly by how far it shrank these residuals. So
the whole grid was rerun with fresh seeds and every check repeated on that held-out record. Both are
reported; where they differ, the held-out value is the honest one.

## 1.4 The coordination-rates tool: predicted, then tested

### 1.4.1 Window sharing

Place a window of width w at a uniformly random phase. The chance that it holds all n onsets of one
event is

  g_n(w, σ) = 𝔼[max(0, 1 − R_n / w)],

where R_n is the range of the n onsets. For two onsets the difference D is N(0, 2σ²), and with
s = σ√2 and a = w/s,

  g₂(w, σ) = (2Φ(a) − 1) − (2s/w)(φ(0) − φ(a)),

with Φ and φ the standard normal distribution and density. For three onsets g₃ is a
one-dimensional integral over the distribution of the range of three normals; it depends only on
w/σ and is tabulated once. Rounding onsets to the frame changes nothing, because the windows sit on
the frame grid.

How much does the Gaussian shape matter? Computed the same way for uniform jitter of the same SD,
g₂ and g₃ differ from the Gaussian values by at most 0.02 and 0.04 (Figure 1.3 A). With the window's
phase random, both are smooth in w. The edge in Louis, Borgelt & Grün's analysis comes from
conditioning on a fixed overlap between the jitter window and a bin, not from the jitter law. So the
Gaussian form is new on paper but close to its uniform counterpart in value.

![Figure 1.3](figures/synth_recovery_plot_window-sharing-and-participant-bias_20261029.png)

**Figure 1.3. Window sharing, and the undercount of participants it causes.** A: the chance that
one window holds all the onsets of an event, for two onsets (g₂) and three (g₃), against window
width over jitter SD. Solid lines are Gaussian jitter; dashed lines are uniform jitter of the same
SD, computed by numerical integration and checked by simulation; they differ by at most 0.02 (g₂)
and 0.04 (g₃). B: participants reported over planted (k̂/k) against jitter over window, from
k̂ = 2 + (k − 2) g₃/g₂, for 5, 10 and 20 cells per event. Points are medians from the first
experiment (10 recordings each, background 0.01 Hz). Yellow dashes are the full prediction, which
adds the at-most-one-event term and accounts for the points below the lines at the 4 s window.

### 1.4.2 The expected excess counts

With at most one event per window, the coordinated part of the population count has factorial
moments p (k)_r g_r, where p = λw and (k)_r is the falling factorial k(k − 1)…(k − r + 1). The
surrogate keeps each cell's train, so it carries each cell's coordinated onsets (rate λk/N) but
scatters them. The excess pair and triple counts the tool measures are then

    f₂ = p (k)₂ g₂ − (pk)² (1 − 1/N)

    f₃ = p (k)₃ g₃ − 3 p² k (k)₂ g₂ + 2 (pk)³ (1 − 1/N²)

In each, the terms beyond the first are the **at-most-one-event term**: a Poisson event train would
let two events share a window now and then, and the hard-core train forbids it, so that contribution
is removed. The tool itself works with factorial cumulants, which add over independent processes;
CuBIC's eq. 3 relates ordinary cumulants to the amplitude distribution in the same way. Window
sharing and the at-most-one-event term relax CuBIC's two assumptions, exactly synchronous copies and
a Poisson carrier.

### 1.4.3 Why the window must exceed the jitter

Dropping the small terms, f₃/f₂ ≈ (k − 2) g₃/g₂. The tool assumes every window catches every onset
of an event (g = 1), so it reports

  k̂ = 2 + (k − 2) g₃/g₂.

As σ approaches w, g₃ falls faster than g₂ and k̂ falls toward 2. For 10-cell events, k̂/k falls
below 0.9 once σ passes about w/6 and reaches 0.45 at σ = w (Figure 1.3 B). This is the
undercount the first experiment saw at 1 s jitter: there the 1 s window read 0.34–0.42 of planted
participants and the 4 s window 0.68–0.85 (Figure 1.1 A, E).

### 1.4.4 The test

![Figure 1.4](../learned/synthetic_validation/synth_recovery_plot_one-source-predicted-against-measured_20261023.png)

**Figure 1.4. The full prediction matches the coordination-rates tool.** One point per setting and
window, first experiment. A–C (0.01 Hz) and E–G (0.05 Hz): the tool's three estimates as ratios to
planted, against the prediction. Colored points use the full prediction with the at-most-one-event
term; gray points are the same measurements placed at the prediction for a Poisson event train. D,
H: chance clusters per minute, discussed in *1.5*.

**Participants.** For events of 10 or more cells, the prediction matches the setting median to a
median residual of 0.007 of planted at 0.01 Hz and 0.016 at 0.05 Hz in the first experiment (worst
0.037 and 0.11); without the at-most-one-event term it is about 0.05. On the held-out record the
same residuals are 0.012 and 0.021 (worst 0.056 and 0.13).

The prediction is close but not exact. If it were exact, about 6 of the 48 setting-windows per
background would sit beyond 2 standard errors, because the standard error of a median of 5 values is
heavy-tailed. The first experiment had 7 and 10; the held-out record has 17 at 0.01 Hz (probability
under exactness below 0.001) and 10 at 0.05 Hz. The 48 setting-windows reuse the same recordings
across windows, so these counts overstate the independent evidence. Taking one sign per setting and
pooling both records, measured is below predicted in 24 of 32 settings at 0.01 Hz (sign test
p = 0.007): the hard-core form overpredicts participants by about 1 %.

**Rate and share** are predicted less well. At 0.01 Hz the median rate residual is 0.032 (held-out
0.024), and at 0.05 Hz 0.055 (worst 0.38; held-out worst 0.62). The share's median residual is 0.018
at 0.01 Hz (held-out 0.011).

### 1.4.5 Where the hard-core form fails, and the general form

The first experiment's events were at least 20 s apart, so no window held two. Real event trains
need not be. The general form replaces the at-most-one-event term with the event train's pair
correlation, and adds the effect the hard-core form omitted: the surrogates' shifted copies are not
independent of the event train, so they carry some of its structure (derivation in
[`separation/real_intervals/`](../learned/synthetic_validation/separation/real_intervals/derivation.md)).
Poisson, hard-core, renewal, empirical and Palm trains are implemented.

On the first experiment's own trains, the general form changes little and moves the right way:

- **Participants.** The 1 % overprediction goes as a direction: 18 of 32 settings below predicted
  on the pooled records (p = 0.60). But at 0.01 Hz, 12 setting-windows still sit beyond 2 SE on the
  held-out record, against about 6 expected (p = 0.009).
- **Rate at 0.01 Hz.** The median residual falls from 0.032 to 0.020 (held-out 0.024 to 0.014); its
  signed median, the bias, falls from +0.030 to +0.013. Measured still sat above predicted in 35 of
  48 setting-windows in the first experiment (p = 0.002), but not on the held-out record (18 of 48,
  p = 0.11). **At 0.05 Hz** the general form does not help (0.055 to 0.059).

On event trains with realistic intervals the difference is large. These recordings were simulated
with renewal trains whose intervals were resampled from a measured list of fast-type intervals,
σ = 0.105 s, 7 or 13 cells and b = 0.0096 Hz, 40 recordings each; the event rate was set to one
over the mean interval, 0.0099 Hz, which makes these trains denser than the hard-core trains above.
At the 4 s window, for 7-cell events, the hard-core form predicts the tool's rate at 1.16 of planted
and participants at 0.90, where the tool measures 0.99 and 0.97. The general form predicts the tool
to within 0.01–0.04 at every window. On a slow-type interval list (σ = 0.131 s), where the tool
itself reads rate up to 1.37 and participants down to 0.80 of planted, both forms predict it.

### 1.4.6 The joint fit, and the correlogram tool

The tool reports a pair and a triple count at each of its three windows. Fitting those six numbers,
each order scaled by its mean absolute value, against the exact forms above for (σ, k, λ) gives
jitter, participants and rate at once. The dependence on w enters only through g₂ and g₃, which is
what makes σ identifiable; the fit is bounded at σ = 0.005 s. On realistic event trains the fit
takes the train's measured intervals.

**On the first experiment**, for events of 10 or more cells and planted jitter of 0.2 s or more, the
setting medians of recovered ÷ planted jitter lie within 0.91–1.13 at 0.01 Hz and 0.88–1.12 at 0.05
Hz, with participants within 0.94–1.14 and rate within 0.73–1.14. **On the held-out record** they lie
within 0.86–1.22 and 0.86–1.36, participants 0.98–1.06 and 0.89–1.16, rate 0.94–1.04 and 0.87–1.45.
Planted 0.05 s is not resolved: it reads 0.041 s at 0.01 Hz (3 of 20 recordings at the bound) and
0.030 s at 0.05 Hz (7 of 20), held-out. Events of 5 cells read anywhere from 0.1 to 3.6 times
planted.

**Against the correlogram tool**, run as shipped on the same 240 recordings (Table 1.2), the joint
fit is not better everywhere. The correlogram reads 0.05–0.2 s jitter as well or better, though at
0.05 s often only as "below 0.05 s"; its own calibration was made on another simulator and reads 3–14
% low on this one. It fails at 1 s. The joint fit is the better estimator from about 0.5 s up, and at
the busier background.

**Table 1.2. Recovered ÷ planted jitter, events of 10 or more cells**, median [interquartile range]
over 20 recordings, first experiment. "Off the curve" counts recordings whose correlogram width fell
outside its calibration.

| b | planted σ | correlogram tool | joint fit |
|---|---|---|---|
| 0.01 Hz | 0.05 s | 1.06 [1.02, 1.10]; 8 below the curve | 1.33 [0.98, 1.79]; 1 at the bound |
| 0.01 Hz | 0.2 s | 0.97 [0.94, 1.02] | 1.07 [1.02, 1.19] |
| 0.01 Hz | 0.5 s | 0.92 [0.86, 0.94] | 0.98 [0.94, 1.06] |
| 0.01 Hz | 1.0 s | 0.86; 15 above the curve | 1.01 [0.98, 1.03] |
| 0.05 Hz | 0.05 s | 1.07; 15 below the curve | 0.89 [0.48, 1.64]; 4 at the bound |
| 0.05 Hz | 0.2 s | 0.93 [0.83, 1.01] | 0.99 [0.65, 1.13] |
| 0.05 Hz | 0.5 s | 0.81 [0.64, 0.88] | 1.04 [0.98, 1.12] |
| 0.05 Hz | 1.0 s | 0.42 [0.27, 0.55] | 1.01 [0.95, 1.07] |

**At realistic values** the joint fit is usable for participants and rate in each recording but not
for jitter. On the fast-type interval trains at σ = 0.105 s, per-recording jitter reads 1.06 ×
planted [0.39, 1.53] for 7-cell events, with 8 of 40 recordings at the bound and only 10 of 40 within
0.8–1.25 of planted; for 13-cell events 0.88 [0.40, 1.48], 9 of 40 within. Participants (0.97–1.05)
and rate (0.86–1.03) are tight. On the slow-type trains at σ = 0.131 s, 17 and 19 of 40 recordings
read jitter within 0.8–1.25. Without the general form, the fast-type trains read jitter 1.62 and 1.43
times planted. The fit reports no per-recording uncertainty; a parametric bootstrap would supply one.

## 1.5 The assessor's threshold: predicted, then tested

On a background-only recording with every cell at the same rate, each cell is active in a 1 s bin
with probability 1 − e^(−b), so a bin reaches K cells with probability

  q = P(Binomial(N, 1 − e^(−b)) ≥ K).

That part was already in the repository's own field-size and chance-floor tools. The assessor starts
a cluster on a bin at or over K whose two preceding bins are below it, so its chance-cluster rate is

  60 q (1 − q)² per minute.

![Figure 1.5](figures/synth_recovery_plot_chance-clusters-against-threshold_20261029.png)

**Figure 1.5. How many clusters chance alone gives the assessor at each threshold.** Lines show the
predicted rate of chance clusters against the threshold K, for 33 cells at three background rates.
Points were measured on 100 background-only recordings of 45 minutes per background, with exact
Poisson 95 % intervals. At K = 6 and 0.01 Hz no cluster occurred, so the triangle marks the upper
bound. Only K = 3, 4 and 6 were simulated; the shaded thresholds are predictions only. The budget is
one chance cluster per hour (dashed). The smallest threshold under it is 5 cells at 0.01 Hz and 8 at
0.05 Hz, so one fixed threshold cannot serve both backgrounds. At the realistic background of
0.0096 Hz, 4 cells comes in just under the budget, at 0.98 chance clusters per hour.

Predicted 0.256 and 0.019 per minute at K = 3 and 4 and 0.01 Hz (measured 0.262 and 0.020); 7.97,
3.86 and 0.284 at K = 3, 4 and 6 and 0.05 Hz (measured 7.97, 3.85 and 0.279). All lie within their
95 % intervals. At K = 6 and 0.01 Hz the prediction is 0.2 clusters in the whole arm, so measuring
none tests nothing. This explains the first failure. Against the repository's budget of one chance
call per hour (ADR-0008), the formula puts the smallest safe threshold at 5 cells at 0.01 Hz and 8
at 0.05 Hz; K = 5 and 8 were not simulated, so those values extrapolate a formula checked at K = 3, 4
and 6. A threshold therefore has to be set per recording from its own background. The repository's
event floor, a different statistic counted in a 2 s sliding window, gives 6 and 12 cells at these
backgrounds.

A safe threshold also loses spread-out events. At 0.01 Hz and K = 6, one cell above the safe
threshold, the assessor reports 0.76–0.80 of planted 10-cell events at 0.5 s jitter and 0.29–0.33 at
1 s, because their onsets fall in several bins. Whether a planted event reaches K is not modeled
here.

The formula assumes a flat, temporally homogeneous background. Real fields are not: some cells are
silent and others busy. With unequal rates, q becomes a Poisson-binomial tail over the per-cell
rates; what temporal over-dispersion does to it is not derived.

## 1.6 Structure the population count cannot see

A source may also have structure in *which* cells take part (membership) and in *when* each takes
part relative to the others (order). This section asks how much of each is needed before it can be
detected.

### 1.6.1 Membership: when do assemblies look random?

Let a source draw each event's participants from one of M fixed assemblies of k cells, chosen with
equal probability, and assume perfect readout (every member seen, no background cell joining). Two
events then share an assembly with probability 1/M, and the variance of pair co-participation counts
across cell pairs is

  1 + (E − 1)/M

times its value under random participation. With unequal use, 1/M becomes Σ p_m², where p_m is the
share of events using assembly m. This has the form of Kish's design effect for clustered samples,
deft² = 1 + roh(b̄ − 1), with b̄ the mean cluster size and roh his "ratio of homogeneity" (Kish 1995,
pp. 63–64; it is the intraclass correlation). Here E plays b̄ and 1/M plays roh.

Assembled participation therefore converges to random as assemblies multiply **only if the total
number of events is held fixed**, and then almost by definition, since many assemblies each used
once are random participation. If each new assembly brings its own e events (E = Me), the excess
stays near e and never reaches random (derived, not simulated). Membership is invisible to the
population-count tools by construction, exactly so when every cell has the same rate.

![Figure 1.6](../learned/synthetic_validation/synth_assembly-membership_plot_assemblies-converge-to-random_20261023.png)

**Figure 1.6. Assembled participation stays detectable after its variance has converged.** 33 cells,
10 per event, 45 events. A: pair co-participation variance over its value under random
participation, mean of 400 simulations, against reuse E/M (M = 1 is E/M = 45). The points share one
simulated random baseline, so their common 1–2 % shortfall is one error, not seven. B: share of 60
recordings in which the assembly test rejects both of its nulls, and either one, with 200 surrogates
per null. Under random participation both reject in 1 of 60 and either in 3 of 60 (dotted and dashed
lines).

The assembly test has two nulls. The margin-preserving null shuffles which cells join which event
while keeping each cell's event count; the uniform null draws each event's participants at random.
Detection outlasts the variance: both nulls reject in every recording while reuse E/M lies between 1
and 15, in 72 % at reuse 0.3, and still in 13 % at reuse 0.045 (8 of 60; binomial 95 % interval
about 6–25 %), where the variance ratio is 1.04. At M = 1 only the uniform null rejects, because one
assembly holding every event is the case a margin-preserving null cannot see.

### 1.6.2 Order: how many events does an order test need?

**A latency template is extra jitter to the population count.** If each participant has a fixed
offset drawn from N(0, δ²), two participants' lag has SD √(2(δ² + σ²)), so g_n and the joint fit see
an effective jitter √(δ² + σ²) (derived, not simulated). Only cell-by-cell statistics separate the
two.

**The indicator.** With known events and no background, count for each pair of cells who leads
across the events they share. The **score sort** orders cells by net lead count, wins minus losses
(Copeland's rule; O(N²), no search). F is the net agreement of the pair lead signs with that order,
as a share of pair co-participations: 1 for a perfect sequence, near 0 with no order once events are
many. A **local search** then moves single cells while that raises F.

![Figure 1.7](../learned/synthetic_validation/synth_recovery_plot_order-indicator-closed-forms_20261023.png)

**Figure 1.7. The order indicator follows its closed forms.** 33 cells, 10 per event. A: one template,
200 events; solid, (2/π) arctan r; dashed, with the no-order bias of 200 events added. B: M templates
at r = 2.5, 2000 events; solid, the many-template asymptote; dashed, with the bias added. C: no order
planted. Blue lines are derived: the exact mean under the score sort and its asymptote 0.376/√n̄.
Points are simulated; open points come from a separate 200-recording check at small n̄. The local
search's line is fitted.

- **One template.** F = (2/π) arctan r, with r = δ/σ. This is the population Kendall rank
  correlation between template and observed latencies under a normal model: for a bivariate normal
  pair with correlation ρ, τ = (2/π) arcsin ρ (Kruskal 1958, derived in secs. 3–4), and here
  ρ = r/√(1 + r²). The score sort sits on it at r = 1 and 2.5 (0.503 and 0.753).
- **M templates.** The signal falls as 1/√M from √(2/π) · √((2/π) arcsin(r²/(1 + r²))), 0.65 at
  r = 2.5. This form is asymptotic and runs up to 10 % high at M = 2–16, checked at fixed E only.
- **No order.** Under the score sort the mean of F is exact for every N, k and E, from one lattice
  convolution ([`kendall_w/`](../learned/synthetic_validation/kendall_w/derivation.md)). For n̄ ≳ 2
  it approaches c/√n̄ with c(N, k) = √(4(k + 1)/(3πN)), 0.376 at 33 cells and 10 per event, nothing
  fitted; at n̄ = 0.4 the asymptote runs 0.03 high. The exact mean matched fresh simulation in 33 of
  33 comparisons. With every cell in every event, F is the Kendall-τ analogue of √W, Kendall's
  coefficient of concordance (Kendall & Babington Smith 1939); with partial participation the score's
  covariance is that of Durbin's (1951) incomplete-block test in Skillings & Mack's (1981) form. Only
  the mean is derived, not the spread, which is what detection depends on. The local search's
  constant (0.50) is fitted.

**With few events the bias is large**: at 33 cells the no-order F is 0.48 ± 0.06 (SD over 200
recordings) at 10 events of 7 cells and 0.14 ± 0.02 at 140. A null of order-free recordings of the
same size removes the mean bias; detection then depends on the null's spread.

**Power** (Figure 1.8; Table 1.3) is the share of recordings with order planted whose F exceeds the
null's 95th percentile. F takes few values at small E, so the test is randomized to an exact 5 %
size. Power here is for detecting that order is present, not for recovering how many templates
there are.

![Figure 1.8](figures/synth_recovery_plot_order-power-against-event-count_20261029.png)

**Figure 1.8. An order test needs several events, and two templates need more than five.** Power
to detect order: the share of 300 simulated recordings in which the order indicator rejects an
exact-size 5 % test, calibrated on 3,000 order-free recordings of the same size and randomized at
its threshold. It is plotted against events per recording (1, 2, 3, 5), for 7 (A) and 13 (B) of 33
cells per event. Line color gives a template's latency spread as a multiple of the onset jitter
(r = 1, 2.5, 5); solid lines are one template and dashed lines two. With one event no test has
power, because the indicator is 1 with or without order. One template reaches power 0.8 at 3 events
of 13 cells when r is 2.5 or more, but at 5 events of 7 cells only when r = 5. Two templates stay
below 0.8 everywhere up to 5 events.

**Table 1.3. Power to detect order, exact 5 % test**, 300 recordings per point, 33 cells.
One template / two templates.

| cells per event | events | r = 1 | r = 2.5 | r = 5 |
|---|---|---|---|---|
| 7 | 1 | 0.05 / 0.05 | 0.05 / 0.05 | 0.05 / 0.05 |
| 7 | 2 | 0.05 / 0.06 | 0.08 / 0.05 | 0.06 / 0.06 |
| 7 | 3 | 0.08 / 0.06 | 0.20 / 0.07 | 0.24 / 0.13 |
| 7 | 5 | 0.27 / 0.13 | 0.68 / 0.26 | 0.80 / 0.30 |
| 13 | 1 | 0.05 / 0.05 | 0.05 / 0.05 | 0.05 / 0.05 |
| 13 | 2 | 0.13 / 0.06 | 0.30 / 0.16 | 0.45 / 0.25 |
| 13 | 3 | 0.36 / 0.21 | 0.89 / 0.39 | 0.98 / 0.49 |
| 13 | 5 | 0.85 / 0.36 | 1.00 / 0.67 | 1.00 / 0.77 |

At one event no test has power: F is 1 under the null too. At two or three events of 7 cells, order
is barely detectable whatever r is. With 13 cells per event, one template is detected at three events
when r ≥ 2.5, and two need five or more. The earlier record's power at 10 and 25 events used a
300-recording null without randomization, whose realized size ran 1.3–5 %, and one of its entries
reran at 0.52–0.73 against a recorded 0.43; it is not quoted here.

**Against the Synfire Indicator.** An earlier analysis of real recordings found Kreuz's indicator
falling as event counts rose. This section supplies the bias side of that question and does not
analyze those recordings. Kreuz's indicator differs from F in four ways:

| | F here | Kreuz's Synfire Indicator |
|---|---|---|
| coincidences | known events | ISI-adaptive windows, which on sparse trains also pair onsets of neighboring events |
| order | score sort, no search | simulated annealing |
| normalization | pair co-participations | all spikes; with known coincidences and no background, F_Kreuz = F (k − 1)/(N − 1), 0.28 × F at 10 of 33 cells |
| null | order-free recordings, or the exact no-order mean | surrogates that swap order within coincidences |

Kreuz et al. (2017, sec. 3.1 of the preprint) already describe the finite-size effect and warn that
the indicator is "not sufficient to reliably compare two datasets with widely different number of
spike trains and spikes"; they do not give a formula for it. Ranking by net wins is the textbook
Copeland ranking. Two optimality results exist for it, and neither applies directly here:
Coppersmith, Fleischer & Rudra (2006) bound it within a factor of 5 of the fewest disagreements only
when each pair's two weights sum to one, which unequal co-participation breaks; Shah & Wainwright
(2018) prove it optimal for top-m recovery from comparisons independent across pairs, whereas lead
signs within one event are transitive and so dependent. A search of the Kreuz group's papers, code
and website found no ranking sort and no analytical null
([`kreuz_sort/`](../learned/synthetic_validation/kreuz_sort/README.md)).

## 1.7 How close two events can be

Two coordinated events closer than a tool's bins are counted as one, which lowers the event count and
raises the apparent participation. How close can they be before that happens, and is the limit set
by the data or by the tools? Three derivations answer it, each checked by simulation and
re-simulated with the shipped code in a second pass
([`separation/`](../learned/synthetic_validation/separation/README.md)).

![Figure 1.9](../learned/synthetic_validation/separation/floor/synth_recovery_plot_separation-floor-any-method_20261025.png)

**Figure 1.9. Likelihood-ratio tests separate events far closer than the tools' bins.** A–C: the
separation Δ at which a test calls a pair of events two with 80 % power (filled, solid) and 50 %
(open, dashed), against cells per event, at σ = 0.105, 0.131 and 0.5 s; b = 0.0096 Hz, 0.1 s frame,
5 % false alarm. Blue tests pool the onsets; red and green also use cell identity (a cell rarely has
two onsets within its minimum interval); gray knows each onset's event (an oracle). Down-pointing
triangles mark tests that resolved every separation tried; † marks a test whose false-alarm rate
exceeded 7.5 %, so its value is optimistic. Reference lines: the frame, 2σ, the assessor's half-split
point (2.5 s) and the 5th percentiles of two measured interval lists (realistic values). D: power
against Δ at the two realistic parameter sets.

- **The separation the tests achieve.** At 80 % power and 5 % false alarm, b = 0.0096 Hz, a test using
  onset times and cell identity resolves two events 0.44 s apart at σ = 0.105 s with 7 cells per event,
  and 0.59 s apart at σ = 0.131 s with 13 cells; across all four combinations of those values the range
  is 0.26–0.76 s, about 2.5–5.8 σ. Jitter sets it; the frame does not bind. These are the power of
  particular tests, fitted by expectation-maximization against simulated nulls, so they bound the best
  achievable separation from above. The oracle reaches 0.07–0.2 s.
- **The tools' limit is set by their bins.** The chance that a pair is reported as two reaches half its
  plateau at 2.5 bin widths: (m + ½) bins, with m = 2 because both tools join triggered bins that have
  at most one untriggered bin between them. That is about 2.5 s for the assessor (1 s bins) and 5 s for
  the count detector (2 s bins), almost whatever the jitter, participation, background or threshold.
  The data set only the plateau, π_K², where π_K is the chance one event reaches K by itself. The exact
  prediction matched 28,800 simulated pairs within binomial noise (4 of 576 points at p < 0.01).
- **So between about 0.5 and 2.5 s the tools merge pairs the tests could separate.**

![Figure 1.10](../learned/synthetic_validation/separation/assessor_split/synth_recovery_plot_assessor-split-against-separation_20261025.png)

**Figure 1.10. The tools merge pairs closer than their bins.** The chance a pair of events is reported
as two, against the separation of their centers (A–D) and against the realized separation of their
median onsets (E–H). Lines are the exact prediction; points are 400 simulated pairs each. Assessor
solid, count detector dashed; 7 and 13 of 33 cells; jitter 0.105 and 0.5 s; background 0.0096 and
0.05 Hz. Dotted: 2σ. Dash-dot: the 3.8 s 5th percentile of a measured interval list.

## 1.8 What the theory replaces, and what it does not

For one source, theory predicts the coordination-rates tool, the assessor's chance clusters, and what
each window can and cannot read. It turns the two failures of Figure 1.1 into consequences of a
formula: a fixed threshold fails because the chance-cluster rate rises steeply with background, and
the assessor reads jitter poorly because the information about jitter is in how the pair and triple
counts change across windows, which a binned cluster count does not look at. It yields an estimator,
the joint fit, that the brute-force grid did not contain, and that beats the existing bin-free
estimator above about 0.5 s jitter.

It does not predict whether a planted event reaches a threshold, the assessor's participants and
jitter, the rolling detectors (CoactDetect and LoCo, two of the six ported detectors, which compare
each moment with its recent context), clustered intervals or per-cell burstiness. Those stay with
simulation. What changes is where the grid goes: around the predicted boundaries, on dimensionless
axes (σ/w, λw, Nbw, and K against the chance-cluster rate), rather than on a uniform grid chosen in
advance.

![Figure 1.11](figures/synth_recovery_plot_realistic-values-against-tested-grid_20261029.png)

**Figure 1.11. Realistic parameter values sit between the tested points.** Each circle is a
combination of planted jitter and cells per event from the first experiment. A filled circle means
the joint fit recovered jitter within 0.8–1.25 of planted in all four conditions (15 or 45 events,
background 0.01 or 0.05 Hz, each the median of 5 recordings); the numbers give the range of the four
ratios. Boxes mark realistic parameter values at the fast and slow bench levels: jitter 0.105 s with
7 cells per event (0.20 of 33), and 0.131 s with 13 cells (0.38 of 33); box sizes are nominal. Both
lie between the unresolved 0.05 s column and the resolved 0.2 s column, and neither is on the first
experiment's grid; *1.4.6* simulates them directly.

At realistic values (Figure 1.11) the theory's reach is limited. A jitter of 0.105–0.131 s lies
between the joint fit's resolved point (0.2 s) and its unresolved one (0.05 s), and in direct
simulation at those values the fit reads jitter per recording too loosely to use (*1.4.6*). Seven
cells per event lies between the noise-dominated 5-cell arm and the well-predicted 10-cell arm. One
to three events of 7 cells carry almost no power to detect order (*1.6.2*).

## 1.9 Discussion

### 1.9.1 What is old and what is new

| result | status |
|---|---|
| Window sharing, two onsets, uniform jitter | Grün et al. 1999 (fission probability) |
| The full population-count distribution for jittered groups, all orders | Louis, Borgelt & Grün 2010, for uniform jitter |
| Group size and jitter read across bin widths | Grün, Abeles & Diesmann 2008 ⚠; Louis, Borgelt & Grün 2010, by a two-line change-point fit to one feature of the distribution |
| The cumulant route | CuBIC (Staude, Rotter & Grün 2010): ordinary cumulants, Poisson carrier, synchronous copies; non-Poisson extension in Reimer et al. 2012 ⚠ |
| Fitting a cluster process by pair counts across scales | minimum contrast on the K-function (Diggle 1983 ⚠; Diggle & Gratton 1984; Waagepetersen 2007); multi-window moment fits of Neyman–Scott rainfall (Rodriguez-Iturbe, Cox & Isham 1987 ⚠) |
| g_n for Gaussian jitter and n onsets, and k̂ built on it | not found; numerically close to the uniform case (*1.4.1*) |
| The at-most-one-event term, and the general event-train form with the surrogate's dependence | not found in spike-train or spatial statistics; Reimer et al. 2012 not read |
| A formal fit across windows that also recovers the event rate | not found in spike-train statistics; the rainfall fits recover a storm rate and were not read |
| The chance-cluster rate | known in form: accidental-coincidence rates in particle physics and scan statistics (per the repository's prior-art record; not read here); q itself was already in the repository; the assessor-specific run-start factor is new |
| The membership variance ratio | the form of Kish's design effect (Kish 1995; root in Kish 1965 ⚠) |
| One-template F = (2/π) arctan r | τ = (2/π) arcsin ρ under the bivariate normal (Kruskal 1958, who credits its meaning under the normal to Esscher 1924) |
| The score sort | Copeland ranking; Schneider, Havenith & Nikolić 2006 ⚠ rank units by summed pairwise delays |
| The exact no-order mean of F | the covariance is Durbin's and Skillings–Mack's; Kreuz et al. 2017 describe the finite-size bias without a formula; an analytical null for this indicator was not found |
| How close two events can be | no prior-art search was made (super-resolution and radar resolution are the obvious fields) |

"Not found" describes the search, recorded in
[`prior_art/`](../learned/synthetic_validation/prior_art/README.md). Fields not searched: point-process
counting theory (variance-time curves and factorial moments of cluster processes), hydrology beyond
the one rainfall paper, scan statistics and the distribution of the normal range (relevant to g_n),
and the hippocampal replay and cortical sequence literature (Lee & Wilson 2002; Luczak et al. 2007),
where rank-order nulls with few cells are standard. Two enquiries would settle more than any search
and have not been sent: whether the Grün lab has a Gaussian or formal-fit version of the 2010
analysis, and why the Kreuz group anneals rather than ranks.

### 1.9.2 Two sources

The dissertation's premise is that several sources are mixed. On that the chapter has a prediction and
no test: two sources with the same jitter look, to pair and triple counts, like one source whose
participation blends the two, so the coordination-rates tool cannot tell them apart. The full
population-count distribution carries more. Louis, Borgelt & Grün (2010, Fig. 6) separated two and
three groups of different sizes from it, and noted that groups become hard to disentangle as their
sizes converge. Separating sources may therefore need higher orders of the population count,
different jitters (which the joint fit might resolve), or cell-by-cell structure, which *1.6* shows
needs more events than a few. That is where Chapter 2 starts.

### 1.9.3 How the derivations were checked

**Against simulation**, in-sample and on a held-out record (*1.3*). Not every result was simulated:
the E = Me case of membership, the latency template appearing as extra jitter, the many-template order
form away from fixed E, and the Palm form of the event train were derived only.

**Rederivation.** Two further Claude sessions were given the original question, the code and the first
experiment's record, each in its own checkout, without these results. All three reached the same core
derivation: the expected pair and triple counts with the at-most-one-event term, k̂, and the
chance-cluster rate. They shared the prompt, repository, model and tool definitions, and the tool is
itself defined by cumulants, so the route was close to forced: a consistency check, not independent
review. The rederivations found the shared-background flaw in the first run and added the joint fit,
the per-estimate noise and when the tool refuses, the assessor's output as a mixture of chance and
event clusters, and the event floor as the rate at which chance first crosses a count.

**Review.** The underlying record was reviewed by eleven Claude review agents, spawned as
general-purpose agents, in four rounds
([run record](../reviews/synthetic-validation-aim0_2026-10-23.md)), and this chapter by eleven more
playing a committee ([run record](../reviews/chapter-1-aim0_2026-10-29.md)). No human has reviewed the
derivations.

### 1.9.4 Limitations

1. **One generator.** Every check uses one simulated source with Gaussian jitter, one k per source and
   random membership. Real data will need a mixture over k.
2. **The prediction is not exact.** On held-out recordings the participant residuals exceed sampling
   noise (*1.4.4*), and the rate prediction at the busier background is no better under the general
   form.
3. **The joint fit cannot read jitter per recording at realistic values** (*1.4.6*), and reports no
   per-recording uncertainty.
4. **The order results** assume known events, no background onsets and no frame grid; rounding onsets
   to 0.1 s lowered F by about 9 % at δ = σ = 0.1 s in a review agent's test (not kept).
5. **No human has reviewed the derivations** in
   [`theory.py`](../learned/synthetic_validation/theory.py),
   [`kendall_w/`](../learned/synthetic_validation/kendall_w/derivation.md) and
   [`separation/`](../learned/synthetic_validation/separation/README.md).

### 1.9.5 Next steps

1. Test the two-source prediction by simulation, including the full population-count distribution, and
   test that a latency template reads as jitter in the joint fit.
2. Add realistic jitter (σ = 0.1 and 0.15 s) and 7 cells per event to the first experiment's grid, with
   the correlogram tool alongside the joint fit, and give the fit a bootstrap interval.
3. Model planted-event detection (the chance an event reaches K) for the assessor and the count
   detector, and the dilution of the membership excess by real readout.
4. Compare the order indicator with Kreuz's on the same simulated trains.

Further out: the random-matrix threshold for when a fixed assembly shows in the co-activation matrix;
likelihood bounds on the best precision any method could reach for (λ, k, σ); the shared-modulation
prediction, that shared slow rate change adds pair excess growing with the window while coordination
levels off (Staude, Rotter & Grün 2008 ⚠); and re-plotting Figure 1.1 on dimensionless axes.

## 1.10 Conclusion

Brute-force simulation answers the questions it is asked, at the conditions it contains. For one
source, a few closed forms explain why a fixed threshold and a binned jitter estimate fail, predict
the coordination-rates tool's participant count to about 1–2 % with a measurable residual bias, and
yield a joint fit that recovers jitter better than the existing tools from about 0.5 s up, but not at
realistic jitter in a single recording. Cell-by-cell structure needs events: at one event no order
test has power, and at a few it has little. The tools, not the data, limit how close two events can
be. Chapter 2 starts from the two-source prediction, where the full count distribution, not pairs and
triples alone, is the first thing to test.

## About this chapter

This chapter is an exercise: Tony set it up to test how far he and Claude can take a piece of research
together, written as if it were a dissertation's first chapter, from the record on the goal page
([`goals/synthetic-validation.md`](../goals/synthetic-validation.md)) and the scripts in
[`learned/synthetic_validation/`](../learned/synthetic_validation/README.md). Every simulation number
is printed by a script listed under *Reproducing*, including the follow-ups in
[`ch1_followups/`](../learned/synthetic_validation/ch1_followups/README.md) that the committee review
asked for. The one number from a review agent's unkept test is marked where it appears. Sources used
for a quantitative or novelty claim were read against that claim (Tony obtained the paywalled ones
through the university library); references marked ⚠ are cited from the repository's earlier
reading or were not opened.

## Reproducing this chapter

From the repository root, with `PYTHONPATH=src`:

    python docs/learned/synthetic_validation/aim1_one_source.py --workers 24
    python docs/learned/synthetic_validation/theory.py                      # in-sample checks
    python docs/learned/synthetic_validation/theory.py --from-record        # prints 1.1 and 1.4 numbers
    python docs/learned/synthetic_validation/theory.py --train empirical    # general form
    python docs/learned/synthetic_validation/ch1_followups/held_out.py      # held-out record
    python docs/learned/synthetic_validation/ch1_followups/like_for_like.py # sign tests, residuals
    python docs/learned/synthetic_validation/ch1_followups/lab_values.py    # realistic values
    python docs/learned/synthetic_validation/ch1_followups/correlogram_vs_joint.py
    python docs/learned/synthetic_validation/ch1_followups/order_power.py
    python docs/learned/synthetic_validation/membership_limit.py
    python docs/learned/synthetic_validation/order_limit.py
    python docs/dissertation/figures/ch1_new_figures.py
    python docs/learned/synthetic_validation/aim1_figure.py
    python docs/learned/synthetic_validation/aim0_figures.py

The separation scripts and their run times are in
[`separation/README.md`](../learned/synthetic_validation/separation/README.md). The tools are
`tools/measure_coordination_rates.py`, `bugarach.assess`, `bugarach.detectors.count`,
`tools/measure_jitter_correlogram.py` and `bugarach.assembly`.

## References

⚠ cited from the repository's earlier reading, or not opened.

- Cecchini G, Scaglione A, Allegra Mascaro AL, et al. (2021). Cortical propagation tracks functional recovery after stroke. *PLoS Comput Biol* 17:e1008963.
- Chapin JK, Nicolelis MAL (1999). *J Neurosci Methods* 94:121. ⚠
- Coppersmith D, Fleischer L, Rudra A (2006). Ordering by weighted number of wins gives a good ranking for weighted tournaments. *Proc. SODA 2006*, 776–782; journal version *ACM Trans Algorithms* 6(3), 2010.
- DeFazio RA, Burgess CR, Burger LL, Gibson AG, Moenter SM (2026). Arcuate kisspeptin neurons display two types of calcium events: regulation by sex, gonads, and senktide. *J Neuroendocrinol* 38:e70298.
- Diggle PJ (1983). *Statistical Analysis of Spatial Point Patterns*. Academic Press. ⚠
- Diggle PJ, Gratton RJ (1984). Monte Carlo methods of inference for implicit statistical models. *J R Stat Soc B* 46:193–212 (to 227 with discussion).
- Durbin J (1951). Incomplete blocks in ranking experiments. *Br J Stat Psychol* 4:85–90.
- Ehm W, Staude B, Rotter S (2007). Decomposition of neuronal assembly activity via empirical de-Poissonization. *Electron J Stat* 1:473–495. ⚠
- Grün S, Diesmann M, Grammont F, Riehle A, Aertsen A (1999). Detecting unitary events without discretization of time. *J Neurosci Methods* 94:67–79.
- Grün S, Abeles M, Diesmann M (2008). Impact of higher-order correlations on coincidence distributions of massively parallel data. *LNCS* 5286:96–114. ⚠
- Kendall MG, Babington Smith B (1939). The problem of m rankings. *Ann Math Stat* 10:275–287.
- Kish L (1965). *Survey Sampling*. Wiley. ⚠
- Kish L (1995). Methods for design effects. *J Off Stat* 11:55–77.
- Kreuz T (2026). Quantifying spike train synchrony and directionality: measures and applications. *Biol Cybern* 120:21. ⚠
- Kreuz T, Satuvuori E, Pofahl M, Mulansky M (2017). Leaders and followers: quantifying consistency in spatio-temporal propagation patterns. *New J Phys* 19:043028. Read as arXiv 1610.07986.
- Kreuz T, et al. (2022). *J Neurosci Methods* 381:109703.
- Kruskal WH (1958). Ordinal measures of association. *JASA* 53:814–861.
- Kuhn A, Aertsen A, Rotter S (2003). *Neural Comput* 15:67–101. ⚠
- Lee AK, Wilson MA (2002). Memory of sequential experience in the hippocampus during slow wave sleep. *Neuron* 36:1183–1194. ⚠
- Lopes-dos-Santos V, Conde-Ocazionez S, Nicolelis MAL, Ribeiro ST, Tort ABL (2011). *PLoS ONE* 6:e20996.
- Lopes-dos-Santos V, Ribeiro S, Tort ABL (2013). Detecting cell assemblies in large neuronal populations. *J Neurosci Methods* 220:149–166. ⚠
- Louis S, Borgelt C, Grün S (2010). Complexity distribution as a measure for assembly size and temporal precision. *Neural Netw* 23:705–712.
- Luczak A, Barthó P, Marguet SL, Buzsáki G, Harris KD (2007). Sequential structure of neocortical spontaneous activity in vivo. *PNAS* 104:347–352. ⚠
- Mariani B, Senocrate F, Mikiel-Hunter J, et al. (2025). Latency correction in sparse neuronal spike trains with overlapping global events. *J Neurosci Methods* 416:110378. Read as arXiv 2410.15018.
- Neyman J, Scott EL (1952). A theory of the spatial distribution of galaxies. *ApJ* 116:144.
- Pazienti A, Maldonado PE, Diesmann M, Grün S (2008). Effectiveness of systematic spike dithering depends on the precision of cortical synchronization. *Brain Res* 1225:39–46.
- Peyrache A, Khamassi M, Benchenane K, Wiener SI, Battaglia FP (2009). *Nat Neurosci* 12:919. ⚠
- Peyrache A, Benchenane K, Khamassi M, Wiener SI, Battaglia FP (2010). *J Comput Neurosci* 29:309.
- Reimer ICG, Staude B, Ehm W, Rotter S (2012). Modeling and analyzing higher-order correlations in non-Poissonian spike trains. *J Neurosci Methods* 208:18–33. ⚠
- Rodriguez-Iturbe I, Cox DR, Isham V (1987). Some models for rainfall based on stochastic point processes. *Proc R Soc A* 410:269–288. ⚠
- Schneider G, Havenith MN, Nikolić D (2006). *Neural Comput* 18:2387. ⚠
- Shah NB, Wainwright MJ (2018). Simple, robust and optimal ranking from pairwise comparisons. *JMLR* 18(199). Read as arXiv 1512.08949.
- Skillings JH, Mack GA (1981). On the use of a Friedman-type statistic in balanced and unbalanced block designs. *Technometrics* 23:171–177.
- Staude B, Rotter S, Grün S (2008). *Neural Comput* 20:1973. ⚠
- Staude B, Rotter S, Grün S (2010). CuBIC: cumulant based inference of higher-order correlations in massively parallel spike trains. *J Comput Neurosci* 29:327.
- Thomas M (1949). A generalization of Poisson's binomial limit for use in ecology. *Biometrika* 36:18–25.
- Waagepetersen RP (2007). An estimating function approach to inference for inhomogeneous Neyman–Scott processes. *Biometrics* 63:252–258.
- Wang Y, Degleris A, Williams AH, Linderman SW (2024). *JASA* 119:2382.
- Williams AH, Degleris A, Wang Y, Linderman SW (2020). Point process models for sequence detection in high-dimensional neural spike trains. *NeurIPS*. Read as arXiv 2010.04875.
