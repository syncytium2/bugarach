---
title: "Methods: detection of coordinated calcium events"
subtitle: "Draft for review, 2026-09-22. Fast event stream only."
author: "Tony DeFazio"
---

A **coordinated event** is a set of cells whose calcium events fall within about 1 s of one
another more often than independent firing would produce. A **detector** reports each coordinated
event it finds as a **call**, an interval given by its onset and width. **Coded detectors** are
hand-written rules; **learned detectors** are neural networks trained on synthetic recordings.

# Detected calcium events

Analyses start from calcium events detected by the imaging pipeline, not from fluorescence
traces. The pipeline exports one table per recording with one row per calcium event: the region
of interest (ROI, one imaged cell), the half-rise time (t50rise, when the transient reaches half
its rise), and the event's fluorescence amplitude, peak time and width. Rows without a time mark
ROIs that had no events (87 rows in the fast stream). Every recording was acquired at a frame
interval of 0.1 s.

These methods use the **fast stream**, in which an event's width is its width at half prominence
(MATLAB `findpeaks`, Signal Processing Toolbox) rounded to the frame. A second, slow stream, not
used here, is detected by the same method with the width taken from t50rise to peak.

The dataset holds 84 recordings, 2,630 ROIs and 168,755 fast events from 44 mice in four groups
(Table 1). Each recording has a baseline followed by one or more drug treatments. The analyses of
treatment use the 67 recordings, from 36 mice, whose first treatment was TTX (tetrodotoxin, a
voltage-gated sodium channel blocker) or senktide (a neurokinin-3 receptor agonist). Of the
other 17 recordings, 12 had SB222200 (a neurokinin-3 receptor antagonist) first and 5 had no
treatment.

Table: **Table 1. Mice and recordings per group.**

| group                           | mice | recordings | TTX first | senktide first |
|:--------------------------------|-----:|-----------:|----------:|---------------:|
| intact females in diestrus      |   10 |         17 |        11 |              6 |
| intact males                    |   12 |         22 |         9 |              5 |
| orchidectomized males           |   12 |         25 |         9 |             10 |
| ovariectomized females          |   10 |         20 |         9 |              8 |
| all                             |   44 |         84 |        38 |             29 |

The imaging pipeline made the following exclusions before export. The analyses below apply no
event- or ROI-level exclusion of their own.

- **Whole-field brightness steps.** Every event within 2.0 s of one of 9 confirmed steps was
  removed: 187 fast events in 9 recordings.
- **Motion-correction floor pinning.** Non-rigid motion correction (NoRMCorre; Pnevmatikakis and
  Giovannucci, 2017) intermittently held an ROI at the frame's minimum value. 12 ROIs in 4
  recordings were confirmed pinned. All events inside the pinned intervals of 8 of them, in 3
  recordings, were removed, real events included: 56 fast events, all in baseline. The fourth
  recording's pinned ROIs had already been removed or had no events. Two recordings with pinning
  below the screening cut were kept.
- **ROIs, periods and recordings.** Of the 85 recordings in the laboratory's archive, 66 ROIs
  judged dead were removed from 15, and 18 were not assessed. Two trailing treatment periods
  shorter than 240 s were dropped, and one recording withdrawn by the laboratory is absent.

**Periods and analysis windows.** Each recording is divided into periods, baseline then
treatments, and the pipeline supplies one analysis window per period:

- **baseline:** the last 20 min of the baseline period, or the whole period if shorter (17–20 min
  in the recordings analysed);
- **treatment:** from 2 min after the treatment began, to allow for solution exchange, to the end
  of the period, capped at 20 min (13.0–20 min for the first treatments analysed). High-K⁺
  periods, not analysed here, use the whole period.

A first-treatment window had to last at least 12 min; all 67 do.

# Synthetic recordings

Detectors were tuned and trained on synthetic recordings in which the coordinated events are
known. A **benchmark recording** (Figure 1) is 2,700 s (45 min) long with 33 cells. Each
**benchmark seed** generates one benchmark recording at each of two background rates.

![**Figure 1. One benchmark recording** (quiet background, benchmark seed 1). **A**, what was
planted: one row per participation level (▼, the time of each planted event) and one for
distractors (▽); the shaded span is the elevated-rate block. **B**, every calcium event of the
33 cells, one row per cell, one mark per event, with no detections overlaid. A planted event
appears in B as a column of marks under its triangle; the 3-cell events are barely visible
against the background.](figures/fig1_benchmark_recording.png){width=6.5in}

**Background.** Each cell fires independently. Its mean rate is drawn from a gamma distribution
with shape 0.275 and mean equal to the background rate, then modulated by independent
gamma-distributed multipliers of mean 1 in 300 s bins (shape 1.547) and 60 s bins (shape 1.388).
Events are placed as a Poisson process within each bin, and all times are rounded to the 0.1 s
frame grid. The two background rates, **quiet** (0.0052 events s⁻¹ per cell) and **busy** (0.0190
events s⁻¹ per cell), are the 25th and 75th percentiles of the per-recording mean baseline event
rate per cell.

**Planted events.** Each recording holds 15 planted coordinated events, 5 at each of three
participation levels: 10, 6 and 3 of the 33 cells (30%, 18% and nominally 10%), interleaved in
time. Each participating cell fires once, at the planted event's **nominal time** plus Gaussian
jitter (standard deviation 0.36 s). Planted events are at least 120 s apart (the planted
spacing): each interval is 120 s plus an exponentially distributed excess, with the excess mean
set so that the 15 events fill the recording outside the elevated-rate block and its margins.
Draws that overrun are rescaled. Over quiet benchmark seeds 1–20, and excluding the one interval
per recording that spans the block, the intervals were nearly regular: mean 133 s, 5th–95th
percentile 121–164 s.

**Distractors.** Six bursts of 6 cells are placed at uniform random times between 120 s and
1,100 s and labelled as negatives. They are built like the 18% events, with the same cell count
and jitter, so no detector can tell them apart (see *Scoring*).

**Elevated-rate block.** From 1,200 s to 1,500 s every cell fires additional independent events
at 0.06 events s⁻¹, about 6 times the measured baseline rate and 1.6 times the senktide rate, busier than
any recorded condition.
The rate is reached by a linear ramp over the first 30 s and ends abruptly. No planted event falls
within 120 s of the block.

**Event widths.** Each synthetic event is given a width drawn from the distribution of baseline
fast-event widths (median 0.9 s, interquartile range 0.6–1.2 s), independently of whether the event
was planted.

**Origin of the constants.** Every benchmark constant lies inside the 95% interval of its
re-measurement on the recorded data except participation, and at 33 cells the benchmark's 0.18 and
the measured 0.190 both give 6 cells (Table 2). The constants were set from the laboratory's
earlier data: the background shapes were fitted on baseline windows of an earlier archive (81 and
85 windows). The cell count, jitter and participation came from a summary of coincidence
clusters, groups of at least 4 cells active in the same 1 s bin. The 18% level is that measured
participation; the 30% and 10% levels were chosen around it. The re-measurement used the same
cluster method (onsets gathered within 1.5 s of each cluster's centre), so it checks consistency,
not accuracy. It cannot see coordinated events of fewer than 4 cells, and its jitter includes
chance onsets. It used the baseline analysis windows of the 84 recordings (80 for the shapes and
rates, which need enough baseline to fit), with 200 bootstrap resamples over recordings.

Table: **Table 2. Benchmark constants.** Re-measured before floor-pinned intervals were removed;
repeating the measurement after their removal left five values unchanged to four decimal places
and moved the three shape estimates by at most 0.8%. Rates are in events s⁻¹ per cell; shapes are
dimensionless.

| constant                   | benchmark | set from                 | re-measured | 95% interval  |
|:---------------------------|----------:|:-------------------------|------------:|:--------------|
| rate shape                 |     0.275 | 81 archive windows       |       0.269 | 0.218–0.340   |
| burst shape, 300 s bins    |     1.547 | 85 archive windows       |       1.799 | 1.409–2.262   |
| burst shape, 60 s bins     |     1.388 | 85 archive windows       |       1.516 | 1.152–2.105   |
| quiet rate                 |    0.0052 | earlier export           |      0.0050 | 0.0028–0.0066 |
| busy rate                  |    0.0190 | earlier export           |      0.0190 | 0.0162–0.0233 |
| cells                      |        33 | coincidence clusters     |        31.5 | 27–33         |
| jitter, standard deviation |    0.36 s | coincidence clusters     |      0.32 s | 0.25–0.39 s   |
| participation              |      0.18 | coincidence clusters     |       0.190 | 0.182–0.232   |

**Test recordings.** Three tests measure specific failures:

- **Elevated-rate test:** the calls inside the elevated-rate block of each benchmark recording, per
  minute of block. A call there responds to a rise in event rate without coordination.
- **No-coordination test:** recordings generated like benchmark recordings at the quiet
  background, but with no planted events, distractors or block, so that every call is a false
  alarm. In the settings search each shares the seed, and so the background, of one quiet benchmark
  recording; in the comparison of coded and learned detectors it uses the seed plus 100,000.
- **Close-events test:** whether a detector fuses separate events that are close together.
  Recordings are 10,800 s long with 180 planted events (60 per level) at least 6 s apart, without
  distractors or block. The spacing came from an earlier export, using the calls of one coded
  detector (CoactDetect, below) over whole recordings. Crowding, the fraction of calls whose
  nearest neighbour lies within 30 s, exceeded 0.38 in 7 of the 39 recordings with at least 3
  calls, and their shortest gaps between calls were 6–26 s.

# Coded detectors

Six coded detectors were evaluated. Each also requires a minimum number of cells (or events) per
call. In rate+context, CoactDetect and LoCo, calls separated by no more than the merge gap are
joined. CoactDetect and LoCo each have two modes: in **binned** mode the count is taken in
consecutive fixed bins and its null is estimated from surrogates; in **sliding** mode the window
slides frame by frame and the null is computed exactly. Their defaults are binned; the recorded
data were analysed in sliding mode. Table 4 lists every parameter, the grid searched and the value
used.

- **rate+context** subtracts the 60 s moving average of the population event rate (events summed
  over cells in a sliding 1 s window) from that rate, and calls where the excess reaches a fixed
  threshold. The context window is centred on, and includes, the tested window, and is clipped at
  the analysis-window edges. A call must span more than one grid point after merging, and each is
  widened by 0.5 s on both sides. It uses no surrogate null. Because the threshold is fixed in
  events s⁻¹, its stringency varies with the number of cells. It was designed independently of the
  radar literature and resembles the reference-averaging stage of cell-averaging
  constant-false-alarm-rate detection (Finn and Johnson, 1968), but with a fixed additive threshold
  and no guard, so it does not hold the false-alarm rate constant.
- **CoactDetect** counts the distinct cells with an event in a 2 s window. Its null shifts each
  cell's events circularly within a 120 s context around the window, from which a band centred on
  the window (the guard) is removed. In sliding mode each cell's probability of an event in the
  window under this null is computed exactly, so the count's null mean and variance are exact. A
  window is called when its count exceeds the null mean by z null standard deviations, where z is
  the one-sided Gaussian quantile for a nominal level α (z ≥ 4.26 at α = 10⁻⁵). α is a threshold,
  not a false-alarm rate: the count's exact tail is heavier.
- **LoCo** counts distinct cells in a 1 s window under the same null, over a symmetric 120 s
  context that includes the window and stops at period boundaries. It calls when the count exceeds
  a percentile of the exact null distribution.
- **binned SCE** (synchronous calcium events) counts distinct active cells in consecutive 10 s
  bins, too coarse to resolve the 1 s scale of the definition above. Its null shifts each cell's
  events circularly within the analysis window (200 surrogates), and a bin is called when its count
  exceeds the 98th percentile of the null counts pooled over bins and surrogates. It descends from
  Cossart, Aronov and Yuste (2003), who reshuffled each cell's inter-event intervals (1,000
  surrogates per movie) and called frames whose coactive-cell count exceeded the count reached in
  only 5% of surrogates, a technique they credit to Mao et al. (2001). The circular-shift form
  follows later work from the Cossart laboratory (Bocchio et al., 2020; Dard et al., 2022). The
  pooled per-bin percentile used here makes no correction across bins and is more lenient.
- **locust** holds each cell active for the width of each of its events and counts the cells
  active within a window of consecutive frames (the synchronous frames). Its null rolls each cell's
  activity circularly over the whole recording (100 surrogates), and peaks above a percentile of the
  null, at least a minimum distance apart, are called. The threshold is therefore computed once per
  recording, baseline and treatments together. locust is a partial, modified port of CICADA (Denis
  et al., 2020; algorithm described in Dard et al., 2022), with CICADA's transient detection
  replaced by the exported events and widths, so its results are not results of CICADA.
- **SPIKE-synch** computes the SPIKE-synchronization coincidence of each event (Kreuz et al., 2015).
  Its coincidence window adapts to the neighbouring inter-event intervals
  (Quian Quiroga et al., 2002) and is capped at a maximum, an option noted with the adaptive window
  itself (Quian Quiroga et al., 2002) and used with SPIKE-synchronization by Kreuz et al. (2017);
  the minimum-relevant-time-scale extension (Satuvuori et al., 2017) is not used. The coincidence
  profile, binned at 0.1 s, is scanned with hysteresis: a call starts at a bin above the
  coincidence threshold and extends through later bins above the sustain level, each within the
  maximum gap of the last bin taken; bins with no events are skipped. A call needs at least the
  minimum number of events. The measure's authors have detected events with a threshold on the same
  coincidence measure and a maximum gap between an event's spikes, together with a condition on the
  mean fluorescence signal that an event-based pipeline cannot apply (Cecchini et al., 2021;
  T. Kreuz, personal communication, April 2026). The binning and hysteresis here are the
  laboratory's.

The binned modes of CoactDetect and LoCo, and rate+context, binned SCE and locust, are Python ports
of the laboratory's MATLAB implementations, checked against MATLAB reference output. The sliding
modes have no MATLAB counterpart; unit tests check their exact null against simulated shifts and
their Poisson-binomial count against a recursion. SPIKE-synch's coincidence profile agrees event
by event to 10⁻⁹ with cSPIKE (Satuvuori et al., 2017) at the cap used here. It also passes a
summed-coincidence identity against PySpike (Mulansky and Kreuz, 2016) without a cap, because
PySpike's cap has had no effect on interior events since version 0.8.0 (reported upstream as
PySpike pull request 89). Its detection step is a port of the laboratory's MATLAB scan.

# Scoring

A call's interval runs from its onset to its onset plus its width. binned SCE's interval is its
bin, and rate+context's includes its 0.5 s widening. A planted event matches a call when the
distance from its nominal time to the call's interval is at most 2.5 s (zero if the time falls
inside it). Matching is one-to-one, closest pair first, so a long call spanning several planted
events is credited with one. Calls outside the elevated-rate block that match no planted event,
including calls on distractors, are false alarms.

Counts are summed over the recordings of an evaluation before recall and precision are computed:

- recall = matched events / planted events;
- precision = matched calls / calls outside the elevated-rate block;
- F1 score = 2 · precision · recall / (precision + recall).

F1 is computed separately at each background; the **objective** is the mean of the two. The
distractors cap it: a detector that reports every planted event and every distractor has precision
15/21 and F1 0.83. Because distractors match the 18% level, detecting 6-cell events gains 5 true
positives at the cost of up to 6 false alarms, so the objective barely rewards detecting that
level.

A **setting** is one value for each of a detector's parameters. The **default setting** is the one
stored with each implementation, after one parameter per detector was retuned on this benchmark
(binned SCE percentile 99 → 98, rate+context threshold 5.0 → 4.5 events s⁻¹, LoCo percentile
99.9 → 99.5 in binned mode). A setting is **admissible** when it meets the limits in Table 3. The
limits were set by judgement above the rates measured at each detector's default setting, so they
bar settings worse than the default rather than setting an absolute standard.

Table: **Table 3. Admissibility limits.** The elevated-rate limit applies at both backgrounds. The
precision change is the absolute difference in precision between the two backgrounds. The
close-events limit is the largest allowed fall in mean F1 relative to the default setting (for
CoactDetect and LoCo, the default in binned mode).

| detector                  | elevated-rate, calls min⁻¹ | no-coordination, calls h⁻¹ | precision change | close-events F1 fall |
|:--------------------------|---------------------:|---------------------:|-------------------:|-------------------:|
| rate+context |                               2 |                               1 |             0.10 |                 0.02 |
| CoactDetect  |                               1 |                               7 |             0.10 |                 0.02 |
| LoCo         |                               1 |                               3 |             0.10 |                 0.02 |
| binned SCE   |                               9 |                               6 |             0.50 |                 0.02 |
| locust       |                              25 |                               6 |             0.20 |                 0.02 |
| SPIKE-synch  |                               1 |                               1 |             0.10 |                 0.02 |

# Optimization of coded detectors

Each detector's setting was searched from its default setting, with CoactDetect and LoCo in sliding
mode, in two stages over the grids in Table 4:

1. **Coordinate search.** One parameter at a time was varied over its grid, the others held at
   their current values. The parameter moved to its best admissible value when that value's
   objective exceeded the current objective by more than 0.002 F1. If the current setting was
   inadmissible, it moved to the best admissible value whatever the objective. A grid whose best
   value lay at an edge was extended, at most three times per parameter. Rounds repeated until one
   moved nothing, to a maximum of four. A context longer than the 120 s planted spacing was refused,
   because planted events inside it inflate the null.
2. **Two-parameter grids** for pairs expected to interact: LoCo percentile × context, binned SCE
   percentile × bin, and locust percentile × synchronous frames.

Selection used benchmark seeds 1–48 at both backgrounds. The chosen setting was scored once on
seeds 49–96 (held out), and its gain was bootstrapped over benchmark seeds, both backgrounds
together (400 resamples; median and 2.5–97.5 percentiles). The close-events test used 12 seeds per
background.

The settings chosen for CoactDetect and LoCo were adopted (Table 4). Their held-out gains over
sliding mode at the default values were 0.034 F1 (95% interval 0.025–0.044) and 0.016 F1
(0.007–0.026). On the close-events test they passed the limit, which is set against the binned
defaults, but lost 0.040 and 0.042 F1 against sliding mode at the default values. The search also
proposed changes for three other detectors, which were not adopted: for locust, percentile
99.999 → 99.99, synchronous frames 1 → 2 and minimum distance 4 → 128 frames, stopped at the
extension limit rather than at a bracketed optimum; for SPIKE-synch, minimum events 3 → 2; and for
rate+context, merge gap 3 → 8 s. binned SCE did not move. The other four detectors therefore run at
their default settings.

Table: **Table 4. Parameters of the coded detectors.** Grids are the values searched before any
extension; "–" marks a parameter not searched. Value is the one used on the recorded data (the run's
settings file is `recorded_data_detector_settings.csv`). Detection mode "peak" adds a peak
prominence and minimum peak distance, searched with it. One frame is 0.1 s.

| detector | parameter | grid | value |
|:---------------|:-----------------------------------|:-----------------------------|:---------------------|
| rate+context | threshold, excess over context (events s⁻¹) | 3–8 | 4.5 |
| | context window | 20–240 s | 60 s |
| | rate window | 0.5–5 s | 1 s |
| | merge gap | 0.1–8 s | 3 s |
| | guard | 0–4 s | none |
| | threshold form | additive, multiplicative | additive |
| | detection mode | threshold, peak | threshold |
| CoactDetect | mode | – | sliding |
| | window | 0.5–5 s | 2 s |
| | context | 20–240 s | 120 s |
| | guard; guard normalisation | 0–4 s; compact, exposure | 1 s; compact |
| | nominal level α | 10⁻²–10⁻⁶ | 10⁻⁵ |
| | minimum cells | 2–8 | 3 |
| | merge gap | 0–8 s | 8 s |
| | detection mode | threshold, peak | threshold |
| LoCo | mode | – | sliding |
| | window | 0.5–5 s | 1 s |
| | context; null context | 30–480 s; greatest-of, symmetric | 120 s; symmetric |
| | percentile | 97–99.99 | 99.9 |
| | minimum cells | 2–8 | 3 |
| | merge gap | 0.5–8 s | 8 s |
| | guard | 0–4 s | none |
| | threshold update step | – | 15 s |
| | detection mode | threshold, peak | threshold |
| binned SCE | bin | 2–30 s | 10 s |
| | percentile | 70–99.5 | 98 |
| | minimum cells | 3–16 | 3 |
| | merge gap | 0–30 s | none |
| | surrogates | – | 200 |
| | detection mode | threshold, peak | threshold |
| locust | percentile | 99.9–99.9999 | 99.999 |
| | synchronous frames | 1–10 | 1 |
| | minimum distance | 1–16 frames | 4 frames (0.4 s) |
| | threshold scope | whole recording, per period | whole recording |
| | surrogates | – | 100 |
| SPIKE-synch | coincidence threshold | 0.02–0.16 | 0.1 |
| | sustain level | 0.02–0.2 | 0.1 |
| | window rule; window cap | adaptive, fixed; 0.1–2 s | adaptive; 0.25 s |
| | maximum gap | 0.1–2 s | 0.5 s |
| | minimum events | 2–8 | 3 |
| | profile bin | 0.05–0.5 s | 0.1 s |
| | detection mode | threshold, peak | threshold |

# Learned detectors

The configuration, threshold and merge gap of each learned detector were selected inside the
cross-validation described in the next section.

**Input.** Each recording is encoded as a binary raster of cells × 0.1 s frames, 1 in the frame of
each event's t50rise. Rows are ordered by event count, most active first, so the encoding does not
depend on cell order. Frames from each planted event's first to last participating event are
labelled positive; all others, distractors and the elevated-rate block included, are negative.

**Architectures.** Four architectures output a probability per frame, each through a dilated
convolutional head. At their default configurations they have 1,149–1,905 trainable weights, and
the configurations searched have 1,122–4,565.

- **Population filter:** difference-of-Gaussians filters on the fraction of cells active, after each
  event is widened by max-pooling. The raw fraction also passes to the head.
- **Smoothed-fraction filter:** the same filters on the fraction of cells active after per-cell
  smoothing, with the raw fraction also passed to the head.
- **Cell-set network:** a dilated convolutional encoder shared by all cells, the Deep Sets form
  (Zaheer et al., 2017). Its outputs are standardised over time within the input (the crop in
  training, the analysis window on recorded data) and pooled across cells by the mean, the standard
  deviation and the mean of the four largest values at each frame.
- **Cell-set network with channel gain:** the cell-set network with a learned gain and offset on
  each encoder channel, shared by all cells.

In the code these are `tube`, `line_length`, `chorus_norm` and `chorus_gain_norm`.

**Training.** Models were trained with the Adam optimizer (Kingma and Ba, 2015) on weighted binary
cross-entropy, the positive weight being the ratio of negative to positive frames, in batches of 3
crops of 4,096 frames (409.6 s). Each crop is centred on a positive frame with probability 0.5 and
otherwise placed uniformly. A fit trains on 10 benchmark recordings taken from the tuning
recordings of its cross-validation fold; its **training seed** sets the weight initialisation, the
crop sampling and which recordings are taken. Two further recordings, one per background, set the
threshold. The configurations searched vary the learning rate (0.003, 0.01, 0.03), the training
length (900, 1,800, 3,600 steps) and the architecture's size.

**Decoding.** Frames at or above a threshold form calls, and calls at most 2 s apart are merged. The
threshold is chosen from 41 values between 10⁻⁴ and 0.9999: 12 log-spaced values up to 0.05, steps
of 0.05 up to 0.90, and 12 values log-spaced towards 1. It maximises F1 pooled over the two
threshold recordings, except under the false-alarm rule below.

# Comparison of coded and learned detectors

Coded and learned detectors were compared under nested cross-validation. Benchmark seeds 1000–1047,
each at both backgrounds, were split into four outer folds of 12 seeds. For each held-out fold the
other three (72 recordings) were used for tuning:

- **Coded detectors:** stage 1 of the search above over the grids of Table 4, started from the
  Table 4 settings, with grids not extended and contexts longer than 120 s refused. No Table 3 limit
  was applied; under the false-alarm rule below, its budget replaced them.
- **Learned detectors:** 24 configurations, 23 drawn at random plus the default. Each was fitted on
  two of the three tuning folds and scored on the third, rotating, with three training seeds. The
  chosen configuration was refitted on the tuning recordings with five training seeds, and its
  held-out F1 is the mean over refits.

**Two selection rules.** Every detector was selected twice:

- on F1 alone;
- on F1 with false alarms held to CoactDetect's level: a candidate's calls in the elevated-rate and
  no-coordination tests on the tuning recordings could not exceed 1.6 times those of CoactDetect at
  its Table 4 setting, or one call over the test's duration, whichever was larger. For learned
  detectors the threshold was chosen jointly with the configuration under this rule. CoactDetect
  itself passes by construction.

**Replication.** The comparison was repeated on seeds 2000–2047, a second draw from the same
generator.

**Close-events test.** After fitting, each learned detector's merge gap was re-selected from 0, 1, 2,
3, 5, 8, 15 and 30 s on the inner fits without retraining, subject to the close-events limit; 8 s
was chosen in 26 of 32 cases (4 architectures × 4 folds × 2 rules, first draw). For the coded
detectors the test was computed on the chosen settings and reported, not applied: 19 of 48 choices
(6 detectors × 4 folds × 2 rules) would have failed it, and 16 of 48 in the replication. LoCo,
rate+context and SPIKE-synch failed it in every fold of both draws under the false-alarm rule, and
binned SCE in every fold under F1 alone.

**Separability.** Separability is a descriptive bar, not a significance test. A learned detector's
lead over a coded one is **separable** when a corrected paired t over the four outer folds exceeds
3.182, the two-sided 95% critical value at 3 degrees of freedom. The paired t is multiplied by
√(3/7), the Nadeau–Bengio correction for overlapping training sets (Nadeau and Bengio, 2003) at a
test-to-training ratio of 1/3. The correction was derived for random train/test splits; Bouckaert
and Frank (2004) apply it to k-fold cross-validation as a special case of random subsampling. It
assumes training sets several times larger than test sets, which holds for neither ratio here: 3 for
the coded detectors, tuned on 72 recordings, and below 1 for a learned refit fitted on 10, for which
the factor would be about 0.31. √(3/7) was used for every contrast, with no adjustment for the number
of contrasts.

# Analysis of recorded data

The six coded detectors were run on every recording with the Table 4 settings and a surrogate seed of
20260706, used by binned SCE and locust.

One learned detector was run beside them: a cell-set network with channel gain from the replication,
selected with false alarms held to CoactDetect's level. Of its 20 refits (4 outer folds × 5 training
seeds), the one used has the upper-median held-out F1 (0.726); in its fold the chosen configuration
was the default. Its threshold, 0.972, comes from the joint selection (its own threshold recordings
would have given 0.95). It was run with the 2 s merge gap it was trained with, not the 8 s gap
re-selected for it.

rate+context, CoactDetect, SPIKE-synch and the learned detector were run separately inside each
analysis window. binned SCE was run on the whole recording but computes its null and threshold inside
each analysis window. LoCo and locust were run on the whole recording: LoCo's context stops at period
boundaries, and locust computes one threshold per recording. A call counts toward a window when its
onset lies inside it.

**Rates.** A window's rate of coordinated events is the number of calls in it divided by its
duration, in calls min⁻¹. Rates are not normalised by the number of cells. Only baseline and the
first treatment are compared. The statistical comparison of groups and treatments, including how
recordings from one mouse are treated, is not part of these methods.

# Width and amplitude of coordinated events

Each detector sets its call's width by its own rule, so width and amplitude were measured from the
recorded calcium events inside each call, by one rule for every detector:

1. The calcium events considered, the **search span**, are those whose t50rise lies within 1 s of the
   call's centre (its onset plus half its width), or anywhere within the call if the call is longer
   than 2 s.
2. They are sorted by time and split wherever consecutive events are more than 0.5 s apart.
3. The call's **core group** is the group with the most distinct cells. Ties go to the group with
   more events, then to the one whose mean time is nearest the centre.

The **width** is the time from the first to the last event in the core group. The **amplitude** is
the number of cells in it divided by its width, floored at one frame (0.1 s), in cells s⁻¹; it is
unrelated to the fluorescence amplitude of an event. Width and amplitude are undefined when the
search span holds no events, and amplitude is undefined for a single cell. The 1 s span and the
0.5 s gap were set by judgement, and the rule has not been checked against planted events.

When events are dense, as during senktide, consecutive events are often less than 0.5 s apart and
one group can span a long call. Among the coded detectors' calls, widths above 10 s occurred for
rate+context (25 calls), LoCo (23 calls) and CoactDetect (10 calls), the widest being 64.8 s
(rate+context; 37 cells, 1,046 events); 308 calls had zero width and 185 had a single cell.

# Limitations

Every setting was tuned, and every learned detector trained, on 33-cell recordings at baseline
background rates; the recordings have 9–61 cells, and no benchmark places planted events on a
treatment-like background, so detector sensitivity at treatment rates is unmeasured. Several
parameters are absolute in cells (rate+context's threshold, the minimum cells, SPIKE-synch's
coincidence threshold). The comparison of coded and learned detectors is within one generator and
says nothing about transfer to recorded data. The 2.5 s matching tolerance, the 1.6 false-alarm
factor and the width rule's constants were set by judgement.

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

Mao BQ, Hamzei-Sichani F, Aronov D, Froemke RC, Yuste R (2001). Dynamics of spontaneous activity
in neocortical slices. *Neuron* 32(5):883–898. doi:10.1016/S0896-6273(01)00518-9

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
