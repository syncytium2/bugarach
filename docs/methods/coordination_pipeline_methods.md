---
title: "Methods: detection of coordinated calcium events"
subtitle: "Draft for review, 2026-09-22. Fast event stream only."
author: "Tony DeFazio"
---

A **coordinated event** is a set of cells whose calcium events fall within about 1 s of one
another more often than independent firing would produce. A **detector** reports each coordinated
event it finds as a **call**, an interval with an onset and an extent. **Coded detectors** are
hand-written rules; **learned detectors** are neural networks trained on synthetic recordings.

# Detected calcium events

Analyses start from calcium events detected by the imaging pipeline, not from fluorescence
traces. The input is an export folder with one table per recording and one row per event: the
region of interest (ROI, one imaged cell), the event time, and the event's fluorescence amplitude,
peak time and width. The event time is the half-rise time (t50rise). Rows without a time mark ROIs
that had no events (127 rows). Every recording was acquired at a frame interval of 0.1 s.

Two event streams are exported per ROI from the same event detection. In the fast stream an
event's width is its width at half prominence (MATLAB `findpeaks`, Signal Processing Toolbox),
rounded to the frame; in the slow stream it is the rise interval, from t50rise to peak. These
methods describe the fast stream only.

The dataset holds 84 recordings, 2,630 ROIs and 168,755 fast events from 44 mice in four groups
(Table 1).

Table: **Table 1. Mice and recordings per group.** "Analysed" counts the recordings whose first
treatment was TTX or senktide (see *Analysis of recorded data*).

| group | mice | recordings | analysed, TTX first | analysed, senktide first |
|---|---|---|---|---|
| intact females in diestrus (DI) | 10 | 17 | 11 | 6 |
| intact males (MALE) | 12 | 22 | 9 | 5 |
| orchidectomized males (ORX) | 12 | 25 | 9 | 10 |
| ovariectomized females (OVX) | 10 | 20 | 9 | 8 |
| all | 44 | 84 | 38 | 29 |

The imaging pipeline made the following exclusions before export. The analyses below apply no
event- or ROI-level exclusion of their own.

- **Whole-field brightness steps.** Every event within 2.0 s of one of 9 confirmed steps was
  removed: 187 fast events in 9 recordings.
- **Motion-correction floor pinning.** Non-rigid motion correction (NoRMCorre; Pnevmatikakis and
  Giovannucci, 2017) intermittently held an ROI at the frame's minimum value. All events inside 8
  inspected windows on 8 ROIs in 4 recordings were removed, real events included: 56 fast events,
  all in baseline, in 3 recordings. Two recordings with pinning below the screening cut were kept,
  and one analysed recording has not been screened.
- **ROIs and periods.** 66 ROIs judged dead were removed from 15 recordings (18 recordings were not
  evaluated), two trailing treatment periods shorter than 240 s were dropped, and one recording
  withdrawn by the laboratory is absent.

**Periods and analysis windows.** Each recording is divided into periods, baseline then
treatments, and the pipeline supplies one analysis window per period:

- **baseline:** the last 20 min of the baseline period, or the whole period if shorter;
- **treatment:** from 2 min after the treatment began to the end of the period, capped at 20 min.

# Synthetic recordings

Detectors were tuned and trained on synthetic recordings in which the coordinated events are
known. A **benchmark recording** (Figure 1) is 2,700 s long with 33 cells. Each **benchmark seed**
generates one benchmark recording at each of two background rates.

![**Figure 1. One benchmark recording** (quiet background, benchmark seed 1). Top: what was
planted, one row per participation level (▼) and one for distractors (▽); the shaded span is the
elevated-rate block. Bottom: every event of the 33 cells, one row per cell, one mark per event;
nothing is drawn on it.](figures/fig1_benchmark_recording.png){width=6.5in}

**Background.** Each cell fires independently. Its mean rate is drawn from a gamma distribution
with shape 0.275 and mean equal to the background rate, then modulated by independent
gamma-distributed multipliers of mean 1 in 300 s bins (shape 1.547) and 60 s bins (shape 1.388).
Events are placed as a Poisson process within each bin, and all times are rounded to the 0.1 s
frame grid. The two background rates, **quiet** (0.0052 events s⁻¹ per cell) and **busy** (0.0190
events s⁻¹ per cell), are the 25th and 75th percentiles of the per-recording mean baseline event
rate per cell.

**Planted events.** Each recording holds 15 planted coordinated events, 5 at each of three
participation levels: 10, 6 and 3 of the 33 cells (30%, 18% and 10%), interleaved in time. Each
participating cell fires once, at the event time plus Gaussian jitter (standard deviation 0.36 s).
Successive event times are 120 s apart plus an exponentially distributed excess whose mean is set
so that the 15 events fill the recording; draws that overrun are rescaled. The realised intervals
are nearly regular: mean 133 s, 5th–95th percentile 121–164 s, over 20 recordings.

**Distractors.** Six bursts of 6 cells are placed at uniform random times between 120 s and
1,100 s and labelled as negatives. They are built exactly like the 18% events, with the same cell
count and jitter, so no detector can tell them apart. They therefore cap the score: a detector that
reports every planted event and every distractor has precision 15/21 and F1 0.83.

**Elevated-rate block.** From 1,200 s to 1,500 s every cell fires additional independent events
at 0.06 events s⁻¹, reached by a linear ramp over the first 30 s. No planted event falls within
120 s of the block.

**Event widths.** Each synthetic event is given a width drawn from the distribution of baseline
fast-event widths (median 0.9 s, interquartile range 0.6–1.2 s), independently of whether the event
was planted.

**Origin of the constants.** The constants were set from the laboratory's earlier data (Table 2).
The background shapes were fitted on earlier baseline windows. The cell count, jitter and
participation came from a summary of coincidence clusters, groups of at least 4 cells active in
the same 1 s bin, which cannot see smaller events. The 18% level is the measured participation;
the 30% and 10% levels were chosen around it. Each constant was then re-measured on the baseline
analysis windows of the 84 recordings, with 200 bootstrap resamples over recordings. Every
benchmark value lies inside the 95% interval of its re-measurement except participation. At 33
cells, 0.18 and the measured 0.190 both give 6 cells.

Table: **Table 2. Benchmark constants.** Re-measured on the export before floor-pinned windows were
removed. Repeating the measurement after their removal left five values unchanged to four decimal
places and moved the three shape estimates by at most 0.8%. Rates are in events s⁻¹ per cell;
shapes are dimensionless.

| constant | benchmark | set from | re-measured (95% interval) |
|---|---|---|---|
| rate shape | 0.275 | 81 baseline windows | 0.269 (0.218–0.340) |
| burst shape, 300 s bins | 1.547 | 85 baseline windows | 1.799 (1.409–2.262) |
| burst shape, 60 s bins | 1.388 | 85 baseline windows | 1.516 (1.152–2.105) |
| quiet rate | 0.0052 | earlier export | 0.0050 (0.0028–0.0066) |
| busy rate | 0.0190 | earlier export | 0.0190 (0.0162–0.0233) |
| cells | 33 | coincidence clusters | 31.5 (27–33) |
| jitter, standard deviation | 0.36 s | coincidence clusters | 0.32 s (0.25–0.39) |
| participation | 0.18 | coincidence clusters | 0.190 (0.182–0.232) |

**Test recordings.** Three tests measure specific failures:

- **Elevated-rate test:** the calls inside the elevated-rate block of each benchmark recording,
  per minute of block. A call there responds to a rise in event rate without coordination.
- **No-coordination test:** recordings generated like benchmark recordings but with no planted
  events, distractors or block, at the quiet background. Every call is a false alarm. They use the
  benchmark seeds of the recordings they accompany, so their background equals that of the
  matching quiet benchmark recording.
- **Close-events test:** recordings 10,800 s long with 180 planted events (60 per participation
  level) at least 6 s apart, without distractors or block. The spacing came from an earlier export:
  among the 39 recordings in which CoactDetect made at least 3 calls, 7 had a crowding above 0.38,
  and their shortest gaps between calls were 6–26 s. Crowding is the fraction of calls whose
  nearest neighbour lies within 30 s. A detector that merges calls over long gaps fuses separate
  events here.

# Coded detectors

Six coded detectors were evaluated. In each, calls separated by no more than the merge gap are
joined into one.

- **rate+context** subtracts the 60 s moving average of the population event rate (events summed
  over cells in a sliding 1 s window) from that rate and calls where the excess exceeds a fixed
  threshold. It uses no surrogate null, and its threshold, in events s⁻¹, depends on the number of
  cells. Each call is widened by 0.5 s on both sides. It was designed independently and has the
  structure of cell-averaging constant-false-alarm-rate detection in radar (Finn and Johnson,
  1968), with an additive threshold.
- **CoactDetect** counts the distinct cells with an event in a 2 s window. Its null shifts each
  cell's events circularly within a 120 s context around the window, from which a band centred on
  the window (the guard) is removed. The probability that each cell has an event in the window
  under this null is computed exactly, so the count's null mean and variance are exact. A window
  is called when its count exceeds the null mean by the one-sided Gaussian z for α (z ≥ 4.26 at
  α = 10⁻⁵). α is a threshold, not a false-alarm rate: the count's exact tail is heavier.
- **LoCo** counts distinct cells in a 1 s window, under the same null over a symmetric 120 s
  context that includes the window, and calls when the count exceeds a percentile of the exact null
  distribution.
- **binned SCE** (synchronous calcium events) counts distinct active cells in consecutive 10 s bins.
  Its null shifts each cell's events circularly within the analysis window (200 surrogates), and a
  bin is called when its count exceeds the 98th percentile of the null counts pooled over bins and
  surrogates. It descends from Cossart, Aronov and Yuste (2003), who reshuffled each cell's
  inter-event intervals and thresholded each movie's largest single-frame count at P < 0.05; the
  circular-shift form follows later work from the Cossart laboratory (Bocchio et al., 2020; Dard
  et al., 2022).
- **locust** holds each cell active for the width of each of its events and counts the cells
  active within a window of consecutive frames. Its null rolls each cell's activity circularly over
  the whole recording (100 surrogates). Peaks above a percentile of the null, at least a minimum
  distance apart, are called. It is a partial, modified port of CICADA (Denis et al., 2020), with
  CICADA's transient detection replaced by the exported events and widths, so its results are not
  results of CICADA.
- **SPIKE-synch** computes the SPIKE-synchronization coincidence of each event (Kreuz et al., 2015).
  Its coincidence window adapts to the neighbouring inter-event intervals
  (Quian Quiroga et al., 2002) and is capped at a maximum (Kreuz et al., 2017); the minimum-relevant-time-scale extension
  (Satuvuori et al., 2017) is not used. The coincidence profile, binned at 0.1 s, is scanned with
  hysteresis. A call starts at a bin above the coincidence threshold and extends to each later bin
  above the sustain level that lies within the maximum gap of the last bin taken; empty bins are
  skipped. A call needs at least the minimum number of events. The measure's authors have used a detection step of the same form
  (Cecchini et al., 2021; T. Kreuz, personal communication, April 2026).

rate+context, binned SCE and locust, and the binned modes of CoactDetect and LoCo, are Python ports
of the laboratory's MATLAB implementations, checked against MATLAB reference output. Their sliding
modes have no MATLAB counterpart and were checked only on the benchmark. SPIKE-synch's coincidence
profile agrees to 10⁻⁹ with cSPIKE at the cap used here, and with PySpike (Mulansky and Kreuz, 2016)
without a cap, because PySpike's cap has had no effect since version 0.8.0. Its detection step is a
port of the laboratory's MATLAB scan.

# Scoring

A call's interval runs from its onset to its onset plus its width. binned SCE's interval is its
bin, and rate+context's includes its 0.5 s widening. A planted event matches a call when the
distance from the event's nominal time to the call's interval is at most 2.5 s (zero if the time
falls inside it). The nominal time is the time before jitter. Matching is one-to-one, closest pair
first. A call wider than the planted spacing can therefore match any event within its extent plus
2.5 s. Unmatched calls outside the elevated-rate block, including calls on distractors, are false
alarms.

Counts are summed over the recordings of an evaluation before rates are formed:

- recall = matched events / planted events;
- precision = matched calls / calls outside the elevated-rate block;
- F1 score = 2 · precision · recall / (precision + recall).

F1 is computed separately at each background; the **objective** is the mean of the two. A
**setting**, one value for each of a detector's parameters, is **admissible** when it passes the
limits in Table 3. The **default setting** is the one published with each implementation, after a
2026-09-16 retune of one parameter per detector on this benchmark.

Table: **Table 3. Admissibility limits.** The elevated-rate limit applies at both backgrounds. The
precision change is the absolute difference in precision between the two backgrounds. The limits
were set by judgement above the rates measured at each detector's default setting, and differ by
detector. A fourth limit applies to all six: on the close-events test, the mean F1 may fall by at
most 0.02 relative to the default setting (for CoactDetect and LoCo, the default in binned mode).

| limit | rate+context | CoactDetect | LoCo | binned SCE | locust | SPIKE-synch |
|---|---|---|---|---|---|---|
| elevated-rate test, calls min⁻¹ | 2 | 1 | 1 | 9 | 25 | 1 |
| no-coordination test, calls h⁻¹ | 1 | 7 | 3 | 6 | 6 | 1 |
| precision change | 0.10 | 0.10 | 0.10 | 0.50 | 0.20 | 0.10 |

# Optimization of coded detectors

Each detector's setting was searched from its default setting, with CoactDetect and LoCo in
sliding mode, in two stages:

1. **Coordinate search.** One parameter at a time was varied over its grid, the others held at their
   current values. The parameter moved to its best admissible value when that value's objective
   exceeded the current objective by more than 0.002 F1. If the current setting was inadmissible, it
   moved to the best admissible value whatever the objective. A grid whose best value lay at an edge
   was extended, at most three times per parameter. Rounds repeated until one moved nothing, to a
   maximum of four. A context longer than the 120 s planted spacing was refused, because planted
   events inside it inflate the null.
2. **Two-parameter grids** for pairs expected to interact: LoCo percentile × context, binned SCE
   percentile × bin, and locust percentile × synchronous frames.

Only the parameters each detector declares were searched; minimum cells was not. Selection used
benchmark seeds 1–48 at both backgrounds. The chosen setting was scored once on seeds 49–96 (held
out), with its gain bootstrapped over recordings (400 resamples). The close-events test used 12
seeds per background.

The settings chosen for CoactDetect and LoCo were adopted (Table 4). Their held-out gains over sliding
mode at the default values were 0.034 F1 (95% interval 0.025–0.044) and 0.016 F1 (0.007–0.026).
On the close-events test they gained over the binned defaults, but lost 0.041 and 0.042 F1 against
sliding mode at the default values. The search also proposed changes for three other detectors,
which were not adopted: locust's minimum distance, 4 → 128 frames, stopped at the extension limit
rather than at a bracketed optimum; SPIKE-synch's minimum events, 3 → 2; and rate+context's merge
gap, 3 → 8 s. binned SCE did not move. The other four detectors therefore run at their default
settings.

Table: **Table 4. Settings used on the recorded data.** Parameters not listed are at their defaults.

| detector | setting |
|---|---|
| rate+context | threshold = 4.5 events s⁻¹; context = 60 s; rate window = 1 s; merge gap = 3 s |
| CoactDetect | mode = sliding; window = 2 s; context = 120 s; guard = 1 s; α = 10⁻⁵; minimum cells = 3; merge gap = 8 s |
| LoCo | mode = sliding; window = 1 s; context = 120 s, symmetric; percentile = 99.9; minimum cells = 3; merge gap = 8 s |
| binned SCE | bin = 10 s; percentile = 98; minimum cells = 3; surrogates = 200; no merging |
| locust | percentile = 99.999; synchronous frames = 1; minimum distance = 4 frames; surrogates = 100 |
| SPIKE-synch | coincidence threshold = 0.1; sustain level = 0.1; window cap = 0.25 s; maximum gap = 0.5 s; minimum events = 3 |

# Learned detectors

**Input.** Each recording is encoded as a binary raster of cells × 0.1 s frames, 1 where a cell
has an event. Rows are ordered by event count, most active first, so the encoding does not depend
on cell order. Frames from each planted event's first to last participating event are labelled
positive; all others, distractors and the elevated-rate block included, are negative.

**Architectures.** Four architectures output a probability per frame. At their default
configurations they have 1,149–1,905 parameters, and the configurations searched have 1,122–4,565.

- **population filter** (`tube`): difference-of-Gaussians filters on the number of active cells per
  frame.
- **smoothed-fraction filter** (`line_length`): the same filters on the fraction of cells active
  after per-cell smoothing.
- **cell-set network** (`chorus_norm`): a dilated convolutional encoder shared by all cells, the
  Deep Sets form (Zaheer et al., 2017). Its outputs are standardised over time within each input
  and pooled across cells (mean, standard deviation, and mean of the four most active cells). A
  dilated convolutional head follows.
- **cell-set network with gain** (`chorus_gain_norm`): the cell-set network with a learned gain and
  offset on each cell's encoder output.

**Training.** Models were trained with the Adam optimizer (Kingma and Ba, 2015) on weighted binary
cross-entropy, the positive weight being the ratio of negative to positive frames. Each step used
4,096-frame (409.6 s) crops, half centred on a positive frame and half placed uniformly. A fit
trains on 10 benchmark recordings drawn from a fitting pool; its **training seed** sets the weight
initialisation, the crop sampling and which recordings are drawn. Two further recordings, one per
background, set the threshold. The standardisation in the cell-set networks spans the crop in
training and the whole analysis window on recorded data.

**Decoding.** Frames at or above a threshold form calls, and calls at most 2 s apart are merged.
The threshold is chosen from 41 values between 10⁻⁴ and 0.9999: 12 log-spaced values up to 0.05,
steps of 0.05 up to 0.90, and 12 values log-spaced towards 1. It maximises F1 on the two threshold
recordings, except under the false-alarm rule below.

# Comparison of coded and learned detectors

Coded and learned detectors were compared under nested cross-validation. Benchmark seeds 1000–1047,
each at both backgrounds, were split into four outer folds of 12 seeds. For each held-out fold the
other three (72 recordings) were used for tuning:

- **Coded detectors:** stage 1 of the search above, started from the Table 4 settings, with grids
  not extended. The precision-change and close-events limits were not applied, minimum cells and
  detection mode were also searched, and the context rule was kept.
- **Learned detectors:** 24 configurations of learning rate, training length and architecture
  size, 23 drawn at random plus the default. Each was scored by inner cross-validation over the
  three tuning folds with three training seeds. The chosen configuration was refitted with five
  training seeds, and its held-out F1 is the mean over refits.

**Two selection rules.** Every detector was selected twice:

- on F1 alone;
- on F1 with false alarms held to CoactDetect's level. In both the elevated-rate and the
  no-coordination tests, a candidate's rates on the tuning recordings could not exceed 1.6 times
  those of CoactDetect at its Table 4 setting, or one false alarm over the measured duration,
  whichever was larger. For learned detectors the threshold was chosen jointly with the
  configuration under this rule. CoactDetect itself passes by construction.

**Merge gap.** After fitting, each learned detector's merge gap was re-selected from 0, 1, 2, 3, 5,
8, 15 and 30 s on the inner fits without retraining, subject to the close-events limit. 8 s was
chosen in 26 of 32 cases. For the coded detectors the close-events test was computed on the chosen
settings and reported, not applied: 19 of 48 choices (6 detectors × 4 folds × 2 rules) would have
failed it, and 16 of 48 in the replication. LoCo, rate+context and SPIKE-synch failed it in every
fold of both draws under the false-alarm rule.

**Replication.** The comparison was repeated on seeds 2000–2047, a second draw from the same
generator.

**Separability.** A learned detector's lead over a coded one is **separable** when a corrected
paired t over the four outer folds exceeds 3.182, the two-sided 95% critical value at 3 degrees of
freedom. The paired t is multiplied by √(3/7), the Nadeau–Bengio correction for overlapping training
sets (Nadeau and Bengio, 2003) at a test-to-training ratio of 1/3. That correction was derived for
random splits and carries over to k-fold cross-validation only as a heuristic (Bouckaert and Frank,
2004). The ratio holds for the coded detectors, tuned on 72 recordings, but not for a learned refit
fitted on 10, for which the factor would be about 0.31. √(3/7) was used for every contrast, so
separability is a descriptive bar, not a significance test.

# Analysis of recorded data

The six coded detectors were run on every recording with the Table 4 settings and a surrogate seed
of 20260706. LoCo, binned SCE and locust draw their surrogates from one sequence shared by both
streams.

One learned detector was run beside them: a cell-set network with gain from the replication,
selected with false alarms held to CoactDetect's level. For its fold the chosen configuration was
the default. Of its 20 refits (4 outer folds × 5 training seeds), the one used has the upper of the
two middle held-out F1 values (0.726). Its threshold, 0.972, comes from the joint selection; its
own threshold recordings would have given 0.95. Its merge gap is 2 s.

rate+context, CoactDetect, binned SCE, SPIKE-synch and the learned detector were run separately
inside each analysis window. LoCo and locust were run on the whole recording: LoCo's context stops
at period boundaries, and locust computes one threshold per recording, baseline and treatments
together. A call counts toward a window when its onset lies inside it.

**Recordings analysed.** Analyses of treatment use the 67 recordings, from 36 mice, whose first
treatment was TTX (tetrodotoxin, a voltage-gated sodium channel blocker; 38 recordings) or
senktide (a neurokinin-3 receptor agonist; 29 recordings; Table 1). The other 17 recordings had
SB222200 first (12) or no treatment (5). Only baseline and the first treatment are compared. Baseline
windows are 17–20 min long; first-treatment windows are at least 12 min (13.0–20 min).

**Rates.** A window's rate of coordinated events is the number of calls in it divided by its
duration, in calls min⁻¹. Rates are not normalised by the number of cells.

# Width and amplitude of coordinated events

Each detector sets its call's width by its own rule, so width and amplitude were measured from the
recorded events inside each call, by one rule for every detector:

1. The events considered are those whose t50rise lies within 1 s of the call's centre (its onset
   plus half its reported width), or anywhere within the call if the call is longer than 2 s.
2. They are sorted by time and split wherever consecutive events are more than 0.5 s apart.
3. The coordinated event is the group with the most distinct cells. Ties go to the group with more
   events, then to the one whose mean time is nearest the centre.

The **width** is the time from the first to the last event in that group. The **amplitude** is the
number of cells in it divided by its width, floored at one frame (0.1 s), in cells s⁻¹; it is
unrelated to the fluorescence amplitude of an event. Width and amplitude are undefined when the
window holds no events, and amplitude is undefined for a single cell. The 1 s window and the 0.5 s
gap were set by judgement.

When events are dense, as during senktide, consecutive events are often less than 0.5 s apart and
one group can span a long call. Widths above 10 s occurred for rate+context (25 calls), LoCo (23)
and CoactDetect (10), the widest being 64.8 s (rate+context; 37 cells, 1,046 events). Across all
calls, 443 had zero width and 283 had a single cell.

# References

Bocchio M, Gouny C, Angulo-Garcia D, Toulat T, Tressard T, Quiroli E, Baude A, Cossart R (2020).
Hippocampal hub neurons maintain distinct connectivity throughout their lifetime. *Nature
Communications* 11:4559. doi:10.1038/s41467-020-18432-6

Bouckaert RR, Frank E (2004). Evaluating the replicability of significance tests for comparing
learning algorithms. In *Advances in Knowledge Discovery and Data Mining* (PAKDD 2004), Lecture
Notes in Computer Science 3056:3–12. doi:10.1007/978-3-540-24775-3_3

Cecchini G, Scaglione A, Allegra Mascaro AL, Checcucci C, Conti E, Adam I, Fanelli D, Livi R,
Pavone FS, Kreuz T (2021). Cortical propagation tracks functional recovery after stroke. *PLoS
Computational Biology* 17(5):e1008963. doi:10.1371/journal.pcbi.1008963

Cossart R, Aronov D, Yuste R (2003). Attractor dynamics of network UP states in the neocortex.
*Nature* 423(6937):283–288. doi:10.1038/nature01614

Dard RF, Leprince E, Denis J, Rao Balappa S, Suchkov D, Boyce R, Lopez C, Giorgi-Kurz M, Szwagier T,
Dumont T, Rouault H, Minlebaev M, Baude A, Cossart R, Picardo MA (2022). The rapid developmental
rise of somatic inhibition disengages hippocampal dynamics from self-motion. *eLife* 11:e78116.
doi:10.7554/eLife.78116

Denis J, Dard R, Quiroli E, Cossart R, Picardo M (2020). CICADA (Calcium Imaging Complete
Automated Data Analysis), version 1.0.3. Zenodo. doi:10.5281/zenodo.10041434

Finn HM, Johnson RS (1968). Adaptive detection mode with threshold control as a function of
spatially sampled clutter-level estimates. *RCA Review* 29(3):414–464.

Kingma DP, Ba J (2015). Adam: a method for stochastic optimization. *International Conference on
Learning Representations*. arXiv:1412.6980

Kreuz T, Mulansky M, Bozanic N (2015). SPIKY: a graphical user interface for monitoring spike
train synchrony. *Journal of Neurophysiology* 113(9):3432–3445. doi:10.1152/jn.00848.2014

Kreuz T, Satuvuori E, Pofahl M, Mulansky M (2017). Leaders and followers: quantifying consistency
in spatio-temporal propagation patterns. *New Journal of Physics* 19(4):043028.
doi:10.1088/1367-2630/aa68c3

Mulansky M, Kreuz T (2016). PySpike—A Python library for analyzing spike train synchrony.
*SoftwareX* 5:183–189. doi:10.1016/j.softx.2016.07.006

Nadeau C, Bengio Y (2003). Inference for the generalization error. *Machine Learning*
52(3):239–281. doi:10.1023/A:1024068626366

Pnevmatikakis EA, Giovannucci A (2017). NoRMCorre: an online algorithm for piecewise rigid motion
correction of calcium imaging data. *Journal of Neuroscience Methods* 291:83–94.
doi:10.1016/j.jneumeth.2017.07.031

Quian Quiroga R, Kreuz T, Grassberger P (2002). Event synchronization: a simple and fast method to
measure synchronicity and time delay patterns. *Physical Review E* 66(4):041904.
doi:10.1103/PhysRevE.66.041904

Satuvuori E, Mulansky M, Bozanic N, Malvestio I, Zeldenrust F, Lenk K, Kreuz T (2017). Measures of
spike train synchrony for data with multiple time scales. *Journal of Neuroscience Methods*
287:25–38. doi:10.1016/j.jneumeth.2017.05.028

Zaheer M, Kottur S, Ravanbakhsh S, Póczos B, Salakhutdinov R, Smola AJ (2017). Deep Sets.
*Advances in Neural Information Processing Systems* 30. arXiv:1703.06114
