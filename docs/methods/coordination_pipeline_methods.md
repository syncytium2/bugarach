---
title: "Methods: detection of coordinated calcium events"
subtitle: "Draft for review, 2026-09-22. Fast stream only."
---

## Detected calcium events

Analyses start from the calcium events detected by the imaging pipeline, not from
fluorescence traces. The input is an export folder containing one table per recording, with one
row per event: the region of interest (ROI, one imaged cell), the event time, and the event's
amplitude, peak time and width. The event time is the half-rise time (t50rise), when the
transient reached half its rise. Each recording is split into periods (baseline, then
treatments), and each period carries an analysis window supplied by the imaging pipeline.
Recording metadata give the frame interval and the animal's group.

Every recording was acquired at a frame interval of 0.1 s. Two event streams are exported per
cell. The fast stream carries events whose width is the MATLAB `findpeaks` width at half
prominence. The slow stream's width is the rise interval, from t50rise to peak. Both streams use
the same event detection. This section describes the fast stream only; the slow stream awaits a
benchmark built from its own statistics.

The dataset has 84 recordings, 2,630 ROIs and 44 mice. It holds 168,755 fast events and 95,320
slow events. Four groups were imaged:

| group | animals | recordings |
|---|---|---|
| intact females in diestrus (DI) | 10 | 17 |
| intact males (MALE) | 12 | 22 |
| orchidectomized males (ORX) | 12 | 25 |
| ovariectomized females (OVX) | 10 | 20 |

The imaging pipeline removed two artifacts before export, each listed per event in the export:

- **Whole-field brightness steps.** Every event within 2.0 s of one of 9 confirmed steps was
  removed: 381 events in 9 recordings.
- **Motion-correction floor pinning.** Every event inside the 8 human-confirmed windows was
  removed: 83 events in 3 recordings. In these windows an ROI reported the frame minimum.

One recording withdrawn by the laboratory is absent from the export. The analysis below applies
no further exclusion, filtering or windowing of its own.

## Synthetic recordings

Detectors were tuned and trained on synthetic recordings with known coordinated events, built by
a generator whose structural parameters were measured on the recorded data.

**Background.** Each cell fires independent events. Its mean rate is drawn from a gamma
distribution with shape 0.275 and mean equal to the background rate. That rate is then
modulated by independent gamma-distributed multipliers of mean 1 in 300 s bins (shape 1.547)
and 60 s bins (shape 1.388). Events are placed as a Poisson process within each bin, and all
times are rounded to the 0.1 s frame grid.

Two background rates span the recorded data, as the 25th and 75th percentiles of the
per-recording mean event rate per cell during baseline:

- **quiet:** 0.0052 events s⁻¹ per cell;
- **busy:** 0.0190 events s⁻¹ per cell.

Every synthetic recording is generated at both.

**Coordinated events.** Each recording contains 15 planted events: 5 at each of three
participation levels, 30%, 18% and 10% of the 33 cells (10, 6 and 3 cells). Event times follow a
renewal process: the interval is 120 s plus a gamma-distributed excess with coefficient of
variation 1. The participation levels are interleaved in time. Each participating cell fires
once, at the event time plus Gaussian jitter (standard deviation 0.36 s).

**Distractors and elevated rate.** Two kinds of structure are included that a coordination
detector should not report:

- **Distractors:** six correlated bursts of 6 cells (18%), at uniform random times between 120 s
  and 1,100 s. They are built like planted events and labelled as negatives.
- **Elevated-rate block:** from 1,200 s to 1,500 s every cell fires additional independent events
  at 0.06 events s⁻¹, reaching that rate by a linear ramp over the first 30 s. No planted event
  falls within 120 s of the block.

**Event widths.** Each synthetic event is given a width drawn from the empirical distribution
of recorded fast-event widths: median 0.9 s, interquartile range 0.6–1.2 s. Widths are drawn
independently of whether an event is planted, so they carry no information about coordination.

**The benchmark recording** is 2,700 s long with 33 cells, and carries all of the elements
above. The distribution shapes, the two background rates, the cell count, the jitter and the
participation were measured on the baseline analysis windows of the recorded fast stream, with
200 bootstrap resamples over recordings. Every measured value falls inside its 95% interval
except participation:

- **Measured participation:** 0.190 (median participating cells over median cell count; 95%
  interval 0.182–0.232).
- **Benchmark value:** 0.18. ⚠ Its move to 0.19 is scheduled; the change regenerates every
  synthetic recording and requires the tuning below to be rerun.

The measurement was made on the export before floor-pinned windows were removed and repeated on
the current export. Every value agreed to four decimal places.

**Test recordings.** Three further recording types measure specific failures:

- **Elevated-rate test:** the calls made inside the elevated-rate block of each benchmark
  recording. A call there responds to an increase in event rate without coordination.
- **No-coordination test:** benchmark recordings at the quiet background with no planted events,
  distractors or elevated-rate block. Every call is a false alarm.
- **Close-events test:** recordings 10,800 s long with 180 planted events (60 per participation
  level), separated by at least 6 s. The spacing matches the most crowded recorded data: in the 7
  of 39 recordings whose crowding exceeded 0.38, the minimum gap between events was 6–26 s.
  Crowding is the fraction of events whose nearest neighbour lies within 30 s. A detector that
  merges calls over long intervals fuses separate events here.

## Scoring

A call is the interval from its onset to its onset plus its width; binned SCE reports its bin
extent instead. A call matches a planted event when the event time lies within 2.5 s of the
interval, measured as 0 if the time falls inside it. Matching is one-to-one, closest pair first.
Unmatched calls are false alarms, including calls on distractors.

Counts are summed over the recordings of an evaluation before rates are formed:

- recall = matched events / planted events;
- precision = matched calls / all calls outside the elevated-rate block;
- F1 = 2 · precision · recall / (precision + recall).

F1 is computed separately at each background. The objective is the mean of the two.

A setting is admissible only if it passes all four checks in Table 2.

**Table 2. Admissibility limits for a detector setting.** The elevated-rate limit applies at both
backgrounds. The precision change is the absolute difference in precision between the quiet and
busy backgrounds.

| limit | rate+context | CoactDetect | LoCo | binned SCE | locust | SPIKE-synch |
|---|---|---|---|---|---|---|
| elevated-rate test, calls min⁻¹ | 2 | 1 | 1 | 9 | 25 | 1 |
| no-coordination test, calls h⁻¹ | 1 | 7 | 3 | 6 | 6 | 1 |
| precision change, quiet to busy | 0.10 | 0.10 | 0.10 | 0.50 | 0.20 | 0.10 |
| close-events test, largest F1 loss vs. the setting it replaces | 0.02 | 0.02 | 0.02 | 0.02 | 0.02 | 0.02 |

The first three limits are the shipped settings' measured rates plus a margin. The close-events
limit is set by judgement. ⚠ It has not yet been approved.

## Coded detectors

Six coded detectors were evaluated. Table 1 summarises each detector and the settings used on
the recorded data.

- **rate+context** thresholds the population event rate, a sliding 1 s count, against its
  surrounding 60 s moving average. It uses no surrogate null.
- **CoactDetect** counts distinct active cells in a 2 s window. It compares that count with a
  null in which each cell's events are circularly shifted within a 120 s context around the
  window. The null's mean and variance are computed exactly, and a count is significant at a
  one-sided Gaussian p ≤ α.
- **LoCo** thresholds the same count at a percentile of the circular-shift null, over a context
  centred on the window. It uses the exact null distribution.
- **binned SCE** counts distinct active cells in 10 s bins. It thresholds each analysis window
  at the 98th percentile of a circular-shift null, following Cossart, Aronov and Yuste (2003).
- **locust** holds each cell active for the width of each of its events. It thresholds the
  number of simultaneously active cells at a percentile of a circular-roll null. It is a partial,
  modified port of the Cossart laboratory's CICADA: CICADA's own transient detection is replaced
  by the exported events and widths. Its results are not results of CICADA.
- **SPIKE-synch** computes the SPIKE-synchronization coincidence of each event (Kreuz et al.),
  with an adaptive coincidence window capped at 0.25 s. It reports stretches in which the
  coincidence stays above threshold.

Calls closer than the merge gap are joined. rate+context, CoactDetect, LoCo, binned SCE and
locust are ports of the laboratory's MATLAB implementations, verified to a tolerance of 10⁻⁹. The
sliding-window modes of CoactDetect and LoCo have no MATLAB counterpart. SPIKE-synch was verified
to 10⁻⁹ against cSPIKE and PySpike.

**Table 1. Settings used on the recorded data.** CoactDetect and LoCo use the values selected by
the search described under *Optimization*. The other four use the settings they ship with, which
the search did not change. Parameters not listed are at their defaults.

| detector | parameter | value |
|---|---|---|
| rate+context | excess rate threshold · context · rate window · merge gap | 4.5 events s⁻¹ · 60 s · 1 s · 3 s |
| CoactDetect | window · context · α · merge gap · guard · minimum cells · mode | 2 s · 120 s · 10⁻⁵ · 8 s · 1 s · 3 · sliding |
| LoCo | bin · context · null percentile · merge gap · null context · minimum cells · mode | 1 s · 120 s · 99.9 · 8 s · symmetric · 3 · sliding |
| binned SCE | bin · null percentile · minimum cells · merge gap · surrogates | 10 s · 98 · 3 · none · 200 |
| locust | null percentile · synchronous frames · minimum distance · active duration · surrogates | 99.999 · 1 · 4 frames · each event's width · 100 |
| SPIKE-synch | coincidence threshold · sustain level · window cap · maximum gap · minimum events | 0.1 · 0.1 · 0.25 s · 0.5 s · 3 |

## Optimization of coded detectors

Each detector's settings were chosen by coordinate search:

1. Starting from its shipped setting, one parameter was varied at a time over its grid, with the
   others held at their current best.
2. A parameter moved when its best admissible value exceeded the current objective by at least
   0.002 F1.
3. A grid whose best value lay at an edge was extended, at most three times per parameter.
4. Rounds repeated until a round moved nothing, to a maximum of four.

Selection used benchmark recordings with seeds 1–48 at both backgrounds. The chosen setting was
scored once on seeds 49–96, and its gain over the shipped setting was bootstrapped (400
resamples). The close-events test used 12 seeds per background. For CoactDetect and LoCo the
search ran with sliding windows.

## Learned detectors

**Input.** Each recording is encoded as a binary raster of cells × 0.1 s frames, 1 where a cell
has an event. Rows are ordered by event count, most active first, so the encoding does not
depend on cell order. During training, frames from each planted event's first to last
participating event are labelled positive; all other frames, including distractors and the
elevated-rate block, are negative.

**Architectures.** Four architectures, each of 1,149–1,905 parameters, output a probability per
frame:

- **tube:** difference-of-Gaussians filters on the population activity.
- **line_length:** the same filters applied to the fraction of cells active after per-cell
  smoothing.
- **chorus_norm:** a shared per-cell dilated convolutional encoder whose outputs are
  standardised over time and pooled across cells (mean, standard deviation, and mean of the four
  most active cells), followed by a dilated convolutional head.
- **chorus_gain_norm:** chorus_norm with a learned gain and offset on each cell's vote.

**Training.** Models were trained with weighted binary cross-entropy, where the positive weight
is the negative-to-positive frame ratio, and the Adam optimizer. Training used 409.6 s crops,
half centred on a positive frame and half placed uniformly.

**Decoding.** Frames at or above a threshold form calls, and calls less than 2 s apart are
merged. The threshold is chosen from 41 values between 10⁻⁴ and 0.9999 to maximise F1 on two
held-aside training recordings, one at each background.

## Comparison of coded and learned detectors

Coded and learned detectors were compared under nested cross-validation.

**Folds.** 48 benchmark seeds, each generated at both backgrounds, were split into four outer
folds of 12 seeds. For each held-out fold, the other three folds (72 recordings) were used for
tuning:

- **Coded detectors:** the coordinate search above, run on the tuning recordings, with grids not
  extended.
- **Learned detectors:** 24 configurations of learning rate, training length and architecture
  size, 23 drawn at random plus the default. Each configuration was scored by inner
  cross-validation over the three tuning folds, with three training seeds.

The chosen learned configuration was refitted with five training seeds. Each refit trained on 10
of the tuning recordings, and its held-out F1 is the mean over refits.

**Two selection rules.** Every detector was selected twice:

- on F1 alone;
- on F1 with false alarms held to CoactDetect's level: in both the elevated-rate test and the
  no-coordination test, a setting's false-alarm rates on the tuning recordings could not exceed
  1.6 times those of CoactDetect at its Table 1 setting.

The close-events test was applied to the coded detectors' choices after the run. For the learned
detectors it was applied when their merge gap was re-selected, without retraining.

**Replication.** The comparison was repeated on a second, independent draw of 48 seeds.

**Separability.** A learned detector is ahead of a coded one separably when its held-out F1
margin exceeds zero with a corrected t above 3.182, the two-sided 95% critical value at 3
degrees of freedom. The corrected t is the paired t over the four outer folds, multiplied by the
Nadeau–Bengio factor (Nadeau and Bengio, 2003) for training sets reused across folds; here the
factor is √(3/7).

## Analysis of recorded data

All six coded detectors were run on every recording with the Table 1 settings, and a surrogate
seed of 20260706. One learned detector was run beside them: chorus_gain_norm, the refit from fold 0
and training seed 2 of the replication, at its selected threshold of 0.972. Its held-out F1
(0.726) is the upper of the two middle values among its 20 refits.

**Windows.** Detection used the analysis windows supplied by the imaging pipeline:

- **Baseline:** the last 20 min of the baseline period, or the whole period if shorter
  (17–20 min).
- **Treatment:** from 2 min after the treatment began to the end of the period, capped at 20 min
  (13–20 min).

rate+context, CoactDetect and SPIKE-synch were run separately inside each window. LoCo, binned
SCE and locust were run on the whole recording, and their calls were assigned to the window they
fell in.

**Recordings analysed.** Downstream analyses use the 67 recordings whose first treatment after
baseline was TTX or senktide:

- **TTX:** 38 recordings (DI 11, MALE 9, ORX 9, OVX 9).
- **Senktide:** 29 recordings (DI 6, MALE 5, ORX 10, OVX 8).

Only baseline and the first treatment are compared. Every first-treatment window is at least
12 min long. ⚠ An earlier rule required 15 min; two windows are 13.0 and 14.9 min.

**Rates.** The rate of coordinated events in a window is the number of calls in it divided by
its duration. Baseline and treatment were compared statistically in a separate analysis, not
described here.

## Width and amplitude of coordinated events

A detector's own call width follows its own rule, which differs between detectors. Width and
amplitude were therefore measured from the recorded events inside each call, by one rule for
every detector:

1. The events considered are those whose t50rise lies within 1 s of the call's centre, or within
   the call itself if it is longer.
2. The events are sorted by time and split wherever consecutive events are more than 0.5 s apart.
3. The coordinated event is the group containing the most distinct cells.

The **width** is the time from the first to the last event in the coordinated event. The
**amplitude** is the number of cells taking part divided by the width, in cells s⁻¹, with the
width floored at one frame (0.1 s). A single cell has no amplitude.

⚠ When events are dense, as during senktide, successive events are always less than 0.5 s apart
and the grouping chains across a long call. Widths above about 10 s arise this way; the widest
CoactDetect call is 26.3 s, with 53 cells and 629 events. A revision that counts each cell once
is under review.

## References

Cossart R, Aronov D, Yuste R (2003). Attractor dynamics of network UP states in the neocortex.
*Nature* 423:283–288.

Kreuz T, Mulansky M, Bozanic N (2015). SPIKY: a graphical user interface for monitoring spike
train synchrony. *Journal of Neurophysiology* 113:3432–3445.

Nadeau C, Bengio Y (2003). Inference for the generalization error. *Machine Learning*
52:239–281.
