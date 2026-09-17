# Slow co-modulation: shared change in onset rate across ROIs, and what rigid shift leaves of it

> **Why this page exists.** A detector trained without labels to tell a recording from a *rigid
> shift* of itself is rewarded for whatever the shift destroys. Shared rate change that looks like
> synchrony is an old confound in correlation analysis (Perkel, Gerstein & Moore 1967; Brody 1999),
> and the label-free detector thread ([goal page](../../goals/unsupervised-learning.md)) has an open
> question about it: whether shared modulation over tens of seconds counts as coordination, as the
> [rigid-shift report](../tube_self_supervised/README.md#what-waits-on-tony) poses it on `main` (that
> report is being revised on the unmerged branch `unsup/rigid-shift-report-residuals`). This page
> measures that shared change in the recordings.
>
> **Exploratory, one run, 2026-09-17, baseline windows only; nothing here is a milestone.**
> **Measured** marks a number from this run, **argued** marks reasoning nobody has measured. Pooled
> numbers from recordings carry a 95 % interval from resampling mice; per-recording and synthetic
> numbers do not.

## The short answer

- **Every dataset holds both kinds of shared activity**: coordinated events a fraction of a second
  wide, and shared change in onset rate over a minute or more.
- **On the lab fast stream the minute-scale part is real in the pooled numbers but carried by some
  recordings, not all.** Pooled, the population onset count at 1-minute bins varies 3.2 times as much
  as independent ROIs would make it; with CoactDetect's events removed and each ROI's timing scrambled
  within 2-minute blocks it is 2.4 times. But the median recording is at 1.3 times (0.96 once a
  straight-line trend is removed), and one group of mice carries most of it.
- **On the lab slow stream most of the shared activity is the events**; what is left after they are
  removed is about as large as on the fast stream.
- **In the Dard et al. 2022 dataset** (a different preparation, in vivo in mouse pups) the minute-scale
  shared change is large and present in every recording.
- **The benchmark generator the repository trains and scores on contains more minute-scale shared
  change than the lab fast stream**, from the 5-minute promiscuity probe it plants.
- **For the label-free models:** rigid shift at 1.6–20 s leaves change over a minute or more in place
  in every dataset. So that change was in both sides of their training contrast, and what the contrast
  paid for was the events and faster structure.

**The decision this sets up** is stated [at the end](#the-decision-this-sets-up): whether shared change
in onset rate over a minute or more is coordination, background to subtract, or the producer's to
explain. The page builds to it in this order: the two kinds of activity and the words for them; two
measurements that tell them apart; what each surrogate does where the answer is known; the recordings;
the split by group; what it means for the label-free thread; the decision; what is not settled.

## Two ways ROIs are active together

**The data.** The lab recordings are calcium imaging of hippocampal slices, exported with every onset
within ±2 s of a whole-field brightness step removed ([`MILESTONES.md`](../../MILESTONES.md)) and read
over each recording's baseline, the stretch before any treatment. An **ROI** (region of interest) is
one imaged cell; an **onset** is the half-rise time of one of its calcium transients. The **producer**
— the lab's pipeline that extracts events and writes the export — gives every ROI two event
**streams**, **fast** and **slow** transients, whose peaks trail the half-rise by roughly 0.3 s and 2 s
respectively ([`export_folder_spec.md`](../../export_folder_spec.md)). The **Dard et al. 2022 dataset**
is a second folder, non-anesthetized mouse pups aged 5–12 days imaged in CA1, with a different event
inference and hundreds of ROIs per recording (see [Published lineage](#published-lineage)). An ROI is
**lit** in a bin if it has an onset there.

**The two kinds.**

- **A coordinated event:** several ROIs have onsets within a fraction of a second of each other.
- **Shared modulation:** every ROI's onset rate rises and falls together, over tens of seconds or
  longer, without any two onsets being aligned. **Drift** here means shared modulation over a minute
  or more.

Both light more ROIs than independent cells would. A **label-free detector** is a model trained to
score a recording above a **surrogate** of it: a copy that keeps each ROI's own firing and destroys the
relation between ROIs. The thread's surrogate is **rigid shift**: each ROI's whole onset train slid by
its own random offset within ±*J* seconds (*J*, the shift radius). It was chosen to destroy coordinated
events. Two other surrogates serve as references here: the **circular shift** slides each train by its
own lag and wraps it around the window, destroying every relation between ROIs; the **block control**
does the circular shift inside each 2-minute block separately. **CoactDetect** is the repository's
detector that flags stretches where three or more ROIs have onsets together more often than a local
circular shift allows; an **episode** is one such flagged stretch. Each of these is drawn in Figure 2.

![Figure 1. Two kinds of shared activity, and the correlogram each leaves](fig1_two_kinds.png)

**Figure 1, the two kinds.** Three synthetic worlds. The **planted-event world** (A, D) is the
repository's own generator ([`generator_spec.json`](../generator_spec.json)) with its promiscuity probe
and distractors switched off: 32 ROIs whose rates vary per ROI around a mean of 0.0097 onsets per ROI
per second, plus 15 planted events of 3–7 ROIs. The **20 s world** (B, E) and the **5-minute world**
(C, F) give 32 ROIs a flat rate of the same mean, multiplied by one shared multiplier that wanders on
that timescale, with no events; their depth is chosen to be visible. A–C: the share of ROIs lit per
10 s over the first 20 minutes. D–F: a 1-minute raster (D is centered on a planted event). G and H: the
cross-correlogram of each world, defined in the next section, pooled over 24 recordings, with the
generator's background alone for comparison, on a log lag axis (G) and a linear one (H). On the log axis
a narrow peak and a minute-wide shoulder look equally wide; H shows their true durations.

What coordination and drift look like in one **real** lab fast-stream recording — its population count
per minute beside one rigid shift and one circular shift — is in the darkroom as
`<darkroom>/bugarach/2026-09-17-slow-comodulation/one_recording.png`. It is not reproduced here because it
is derived from a single real recording (FOUNDATIONS §5). In it the rigid shift follows the recording's
minute-to-minute swings almost exactly, and the circular shift does not.

## Two measurements

**The excess coincidence** asks *at what lag* the shared activity sits. Count the pairs of onsets
separated by a lag *ℓ* between distinct ROIs, summed over all ROI pairs and recordings; divide by the
count expected if each pair fired independently at its own totals over the window; subtract one.
Plotted against *ℓ* this is the population cross-correlogram normalized by its independence level
(Perkel, Gerstein & Moore 1967). 0 means no more onset pairs than chance at the window's average rates.
**A coordinated event makes a narrow peak**; **shared modulation on a timescale *T* makes a broad
shoulder** out to lags near *T* (Figure 1, panels G and H). Shared modulation also raises the shortest
lags: a busy stretch holds more onsets, and some land close together by chance.

**The count-variance ratio** asks *how much* shared activity there is at a bin width. Sum the onsets of
every ROI in each bin, take the variance of that population count over the window, and divide by the
same variance after a circular shift of the same onsets. 1 means no shared structure at that width. It
is Schluter's (1984) variance ratio with time bins for samples and ROIs for species, and it is what a
detector that counts lit ROIs responds to. It grows roughly as 1 + (number of ROIs − 1) × the mean
correlation between two ROIs' counts, so a folder with more ROIs reads larger for the same per-pair
correlation. The two measurements are the same thing seen two ways: the count variance at bin width *w*
sums the correlogram out to lags near *w*.

⚠ **Both are relative to the window's own average.** The excess summed over every lag up to the window's
length is zero by construction, because chance is set from the window's own totals; and a change that
spans the whole window is only partly visible. A straight-line rise or fall across the window does
register, as extra count variance; the page therefore also reports the ratio after removing each
recording's straight-line trend.

## What the surrogates remove

![Figure 2. The three surrogates, drawn](fig2_the_surrogates.png)

**Figure 2, the surrogates drawn.** A schematic on fixed numbers: four onset trains over 4 minutes that
share one aligned event near 1m40s (A). **Rigid shift** (B) slides each train by its own offset within
±*J* and drops what leaves the window. **Circular shift** (C) slides each train by its own lag and wraps
it around. **The block control** (D) does the circular shift inside each 2-minute block separately, so
every ROI keeps its onset count in every block; the lane above it marks the block edge.

![Figure 3. What each surrogate removes, where the answer is known](fig3_what_the_surrogates_remove.png)

**Figure 3, what the surrogates remove.** Correlograms of the planted-event world (A), the 20 s world
(B), the 5-minute world (C), a **shallow 1-minute world** (D) whose depth gives a shoulder near the lab
fast stream's, and the benchmark generator with its whole spec (E), each against every arm, pooled over
24 recordings and 8 surrogate draws per recording. An **arm** is one condition: the recording as it is
or under one surrogate. **Episodes removed, then block control** runs CoactDetect on the synthetic
recording, deletes every onset inside an episode, and applies the block control. F: the 1-minute
count-variance ratio of every world and arm, with the generator's background alone. Every arm is
analyzed on the same window, trimmed by 20 s at each end so onsets rigid shift drops never enter; the
y-scale differs per panel and is named in each label.

Measured, from Figure 3:

- **Rigid shift spreads an event's coincidences rather than deleting them** (A): the peak becomes a low
  plateau reaching about 2*J*, visible here at *J* = 1.6 s.
- **Rigid shift removes shared modulation only faster than about *J*** (B–D): in the 20 s world the
  shortest-lag excess falls from +0.68 to +0.51 at *J* = 10 s and +0.36 at *J* = 20 s; in the 5-minute and
  shallow 1-minute worlds every rigid-shift curve lies on the recorded one.
- **So at 1-minute bins rigid shift leaves shared change in place whatever made it** (F): the 20 s world
  keeps 5.25 of 5.53, the 5-minute world 6.93 of 6.95, the shallow 1-minute world 1.71 of 1.79. Surviving
  rigid shift at that bin width says nothing about what carries the change.
- **Removing CoactDetect's episodes spares drift** (C, D, F): it deletes a median 1.7–5.0 % of onsets in
  the event-free worlds and leaves their 1-minute ratio within 0.3 of the recorded value.
- **The block control keeps shared change in 2-minute counts** (B–D): most of the 5-minute drift, part of
  the 20 s modulation. At the generator's sparse event density it keeps no event coincidence (A); on the
  lab slow stream removing episodes first lowers what it keeps, which is the sign that it can keep events.
- **The benchmark generator has a shoulder of about +1.0 out to a minute** (E) and a 1-minute ratio of 8.9,
  from its promiscuity probe: every ROI's rate raised by 0.06 onsets per second for 1,200–1,500 s. Its
  background alone reads 0.88 at 1-minute bins, below 1, because the generator varies each ROI's rate on a
  fixed 60 s grid that the circular shift scatters; ratios from the generator carry that offset.

## What the recordings hold

![Figure 4. How much the population count varies](fig4_how_much_the_count_varies.png)

**Figure 4, how much the count varies.** The count-variance ratio of the lab fast stream (A), the lab
slow stream (B) and the Dard et al. 2022 dataset (C) at 1 s, 10 s and 1-minute bins, as recorded, under
rigid shift at *J* = 20 s, under the block control, and with CoactDetect's episodes removed then the block
control (lab only; each removal arm is divided by the circular shift of its own onsets). Filled markers:
raw, with whiskers for the 95 % interval over mice. Hollow markers: after removing each recording's
straight-line trend. The lab folder: 84 recordings from 44 mice, 17–20 minutes each, the fast and slow
streams of the same recordings. The Dard et al. dataset: 59 recordings from 32 mice, read whole from the
first onset of any ROI, 19–25 minutes, a median of 566 ROIs.

![Figure 5. The recordings' cross-correlograms](fig5_recordings.png)

**Figure 5, the recordings' correlograms.** Excess coincidence of each dataset at full range (A–C) and
zoomed (D–F; the zoom differs per column and is named in each label). Shaded: 95 % interval over mice for
the recording as it is; hatched: the same for CoactDetect's episodes removed. CoactDetect runs at the
repository's calibrated operating point on both lab streams (2 s bins, 60 s context window, per-bin
significance level α = 10⁻⁴, episodes merged across gaps up to 3 s). A small down-pointing mark at a
panel's top edge means a curve leaves the view there.

Measured, from Figures 4 and 5 and `summary.json` (numbers in the collapsed block below):

- **Lab fast stream.** The event peak is +1.91 [+1.17, +3.13] at lags under 0.3 s and gone by about 1 s;
  removing episodes halves it (+0.88). A shoulder of +0.06 to +0.08 runs from about 5 s to a minute and is
  still +0.05 at 78–110 s; with episodes removed and the block control it is about +0.07 to +0.04. The
  count varies 3.21 [2.47, 3.97] times the independent level at 1-minute bins; 2.46 once a straight-line
  trend is removed; **2.42 [1.86, 2.94] with episodes removed and the block control, 1.68 once detrended**.
  Per recording that last ratio has a median of 1.33 and is above 1 in 67 % of recordings, where a single
  circular shift scored against the reference is above 1 in 55 %; detrended, the median is 0.96. **So the
  pooled minute-scale excess is concentrated in some recordings, and about a third of the recorded excess is
  a straight-line trend within the window.**
- **Lab slow stream.** The event peak is +20.8 [+16.5, +25.8]. At 1-minute bins the count varies 11.4
  times; removing episodes takes that to 2.59, and the block control after it to **2.17 [1.58, 2.88]**
  (1.43 detrended; per-recording median 1.23, above 1 in 71 %). Onset pairs 2.7–5.4 s apart are about half
  as common as chance (−0.56, −0.51), a dip that goes with the episodes (+0.05, +0.05 once removed) and that
  rigid shift fills in (+0.35 to +0.57); see the aside below. ⚠ The stream leans on a few busy recordings:
  five of them hold 62 % of its expected onset pairs, and removal took 64 % of onsets weighted that way
  against 8.8 % in the median recording.
- **Dard et al. dataset.** The event peak is +0.78 [+0.64, +0.96] and falls over about 3 s, with a small
  dip near 5 s (−0.05 [−0.09, −0.01]). The count varies 15.2 [12.5, 18.3] times at 1-minute bins, 13.2 once
  detrended, and 6.9 detrended under the block control; the per-recording ratio exceeds 1 in every recording.
  Per pair of ROIs — (ratio − 1) ÷ (ROIs − 1), per-recording median, 1-minute bins, as recorded — it is 0.021,
  against 0.019 on the lab fast stream and 0.034 on the slow: **the dataset reads larger mostly because it
  images more ROIs.** No episode-removal arm was run on it.
- **The pooled intervals rest on fewer effective mice than the counts suggest**: weighted as the
  correlograms weight recordings, 12.7 on the fast stream, 7.7 on the slow and 17.5 on the Dard et al.
  dataset; weighted as the count variance weights them, 23–25.

<details>
<summary>Numbers behind Figures 4 and 5</summary>

Count-variance ratio, raw [95 % interval over mice] · after removing a straight-line trend:

| dataset, arm | 1 s bins | 10 s bins | 1-minute bins |
|---|---|---|---|
| lab fast, as recorded | 1.98 [1.59, 2.48] · 1.94 | 2.69 [2.10, 3.33] · 2.38 | 3.21 [2.47, 3.97] · 2.46 |
| lab fast, rigid shift *J* 20 s | 1.09 [1.06, 1.13] · 1.05 | 1.88 [1.57, 2.21] · 1.54 | 3.00 [2.29, 3.74] · 2.22 |
| lab fast, block control | 1.07 [1.04, 1.10] · 1.03 | 1.69 [1.43, 1.98] · 1.34 | 2.75 [2.08, 3.46] · 1.95 |
| lab fast, episodes removed | 1.38 [1.24, 1.56] · 1.35 | 1.79 [1.50, 2.09] · 1.47 | 2.61 [1.97, 3.19] · 1.87 |
| lab fast, episodes removed, then block control | 1.06 [1.03, 1.09] · 1.03 | 1.57 [1.33, 1.80] · 1.24 | 2.42 [1.86, 2.94] · 1.68 |
| lab slow, as recorded | 9.06 [5.58, 12.22] · 8.97 | 11.76 [7.74, 15.29] · 10.79 | 11.37 [7.50, 14.57] · 7.12 |
| lab slow, rigid shift *J* 20 s | 1.24 [1.15, 1.32] · 1.14 | 3.88 [2.85, 4.72] · 2.71 | 9.86 [6.47, 12.71] · 5.30 |
| lab slow, block control | 1.16 [1.09, 1.22] · 1.06 | 2.94 [2.14, 3.63] · 1.74 | 9.14 [5.75, 12.04] · 4.50 |
| lab slow, episodes removed | 1.52 [1.27, 1.81] · 1.51 | 2.11 [1.61, 2.65] · 1.93 | 2.59 [1.84, 3.48] · 1.90 |
| lab slow, episodes removed, then block control | 1.03 [1.01, 1.04] · 1.01 | 1.31 [1.16, 1.49] · 1.11 | 2.17 [1.58, 2.88] · 1.43 |
| Dard et al., as recorded | 9.69 [8.00, 11.35] · 9.64 | 15.54 [12.33, 18.85] · 15.18 | 15.23 [12.50, 18.28] · 13.15 |
| Dard et al., rigid shift *J* 20 s | 1.42 [1.33, 1.52] · 1.36 | 4.49 [3.80, 5.27] · 3.99 | 12.38 [10.18, 14.77] · 10.09 |
| Dard et al., block control | 1.17 [1.13, 1.21] · 1.11 | 2.54 [2.23, 2.92] · 2.02 | 9.33 [7.68, 11.36] · 6.85 |

Paired differences in the ratio (dimensionless), the same mice resampled for both arms, 10 s · 1-minute
bins:

| dataset | as recorded − rigid shift *J* 20 s | as recorded − episodes removed, then block control |
|---|---|---|
| lab fast | 0.81 [0.39, 1.35] · 0.21 [0.10, 0.34] | 1.12 [0.61, 1.76] · 0.79 [0.39, 1.22] |
| lab slow | 7.89 [4.73, 10.59] · 1.50 [0.56, 2.41] | 10.45 [6.48, 13.72] · 9.20 [5.74, 11.99] |
| Dard et al. | 11.05 [8.52, 13.66] · 2.85 [1.77, 3.95] | — |

Per recording, 1-minute ratio: median [quartiles], share of recordings above 1, detrended median. Recordings
are the unit here, 84 from 44 mice on the lab folder. For reference, one circular shift scored against the
8-draw mean is above 1 in 55 % (lab fast), 46 % (lab slow) and 42 % (Dard et al.) of recordings.

| dataset | as recorded | episodes removed, then block control |
|---|---|---|
| lab fast | 1.52 [1.11, 2.70], 83 %, 1.18 | 1.33 [0.92, 1.77], 67 %, 0.96 |
| lab slow | 1.92 [1.09, 7.03], 80 %, 1.50 | 1.23 [0.92, 1.78], 71 %, 1.07 |
| Dard et al. | 13.34 [8.28, 19.00], 100 %, 11.16 | block control alone: 7.72 [4.72, 12.03], 100 %, 5.69 |

Dropping the five recordings with the largest circular 1-minute variance (25 % of that weight on fast, 27 %
on slow, 16 % on Dard et al.) leaves the 1-minute ratio after removal and block control at 2.34 on fast and
1.84 on slow. Removal took a median of 2.5 % of each recording's onsets on fast and 8.8 % on slow; weighted as
the correlograms weight recordings, 7.2 % and 64 %. The emptied episodes cover, weighted the same way, 1.3 % of
the time on fast and 7.5 % on slow.
</details>

## By group

![Figure 6. The lab streams by group](fig6_by_group.png)

**Figure 6, by group.** The lab streams split by the export's group labels, as recorded (A fast, B slow) and
with episodes removed then the block control (C fast, D slow; y-scale named in each label). Solid: pooled
over recordings. Dashed: each mouse weighted equally. The labels are DI, MALE, ORX and OVX; this repository
reads them as intact females in diestrus, intact males, gonadectomized males and gonadectomized females
([`proposals/2026-09-10-surrogate-evaluation-overnight.md`](../../proposals/2026-09-10-surrogate-evaluation-overnight.md)),
a reading the export contract does not state.

**The pooled result is not one group's, and it is not evenly spread.** On the fast stream DI's pooled curve
sits at about +0.11 after removal and blocking, twice the other three groups' (about +0.05); at 1-minute bins
DI's pooled count-variance ratio is 3.71 as recorded (per-recording median 2.94), against 2.83, 1.96 and 3.30
for MALE, ORX and OVX (medians 1.81, 1.20, 1.32). On the slow stream MALE's pooled and equal-weight curves
sit highest after removal and blocking. Each group's heaviest mouse carries 37–48 % of that group's onset pairs
on the fast stream and 52–64 % on the slow, so every group curve leans on one animal. ⚠ Group cannot be
separated from imaging day on this export — no imaging date holds more than one group
([recording identity](../recording_identity.md)) — so these are differences between groups of recordings, not
group differences.

**Why the slow stream dips — an aside, three readings.** A large synchronous event puts many ROIs into a
transient at once, and onset pairs 2.7–5.4 s apart are then about half as common as chance.

- **Extractor dead time.** On the slow stream the shortest interval between two onsets of one ROI is 2.80 s,
  and such intervals stay depleted out to about 5.4 s: per second of interval there are 15 at 2.8–3.4 s, 95 at
  3.4–4.0 s, 333 at 4.0–4.6 s and 771 at 4.6–5.4 s, against about 1,050 beyond (measured). This repository
  attributes that floor to the extractor, which cannot split one transient into two onsets; the producer has
  not been asked ([todo](../../todo/2026-09-10-the-dead-time-floor-is-the-producers-number.md)). The depletion
  ends where the dip ends.
- **A quiet interval in the tissue itself after an event**, which would remove onsets from every ROI.
- **Detection suppressed after a large transient**, a property of the extraction again.

Splitting the lagged pairs by whether their first ROI took part in the event would separate the two extraction
readings, which remove pairs only from members, from a quiet interval in the tissue, which removes them from
every ROI. The Dard et al. dataset, with a different event inference, has a smaller dip at the same lags.

## What this changes for the label-free thread

Argued from the figures above; nothing here was run against a trained model.

- **Change over a minute or more was on both sides of the training contrast.** Rigid shift at 1.6–20 s leaves it
  in every dataset (Figure 4; Figure 3, panel F shows that is expected whatever carries it). On the lab fast
  stream rigid shift at 20 s removes about a tenth of the 1-minute excess and about half of the 10 s excess
  (paired difference 0.81 [0.39, 1.35] of 1.69), and nearly all of the 1 s excess: what the contrast paid for was
  the events and structure faster than about 40 s. How much of the 10 s difference is spread events and how much
  modulation between 10 and 45 s is not separated here.
- **On the lab slow stream the contrast also paid for what follows an event**: rigid shift fills in the dip.
- **The models trained on simulated recordings saw the promiscuity probe on both sides too**, since rigid shift
  leaves it in place (Figure 3, panel E).
- **A separate check on the unmerged branch agrees with this reading**, on synthetic recordings built with a
  sinusoidal modulation rather than this page's: the models trained against rigid shift score a recording with
  planted events above its 1.6 s shift in 95.8–100 % of paired crops, and a shared-modulation recording above its
  shift in 52.4–54.1 % (1.6 s) and 54.9–62.4 % (20 s) — condition means over 12 fits each
  (`tools/check_small_j_mixes_events.py` at `f55db21`, results at `4518d21`).
- **Removing a local background removes drift.** `count_excess`, a baseline on that branch with no fitted
  parameters, counts lit ROIs and subtracts their 30 s moving mean, which cancels change slower than 30 s by
  construction. Whether that is why it scored as it did there is not tested here.

## The decision this sets up

**Does shared change in onset rate over a minute or more belong to coordination, to the background a
detector should subtract, or to the producer to explain?**

Nothing here says where the change comes from. On the slices it could be a slow change in network state, or it
could enter through the measurement: a focus or slice-position change, bleaching, or a baseline fluorescence
estimate that drifts and moves every ROI's event threshold together. Four lab recordings already carry a
motion-correction artefact that pinned ROIs together
([todo](../../todo/2026-09-10-four-recordings-carry-an-unflagged-contaminant.md)), and the Dard et al. group's
own recording protocol excludes recordings with a strong change in baseline fluorescence (Ratsifandrihamanana et
al. 2023). In the Dard et al. data the authors link activity to the pups' movement within about 2 s of a movement,
with a sign that changes with age, and report activity stable over each recording; neither speaks to minutes-scale
shared change. Facts about the preparation are not this repository's to derive: its FOUNDATIONS defers them to the
lab's shared foundations document, and questions about extraction are a conversation with the producer. ⚠ No
record in this tree says anyone has asked the producer, or the Dard et al. authors, about shared slow change.

## What this does not settle

- **Timescale and carrier.** Within a 17–25 minute window, change at a minute or more cannot be resolved into a
  timescale, and it could be carried by every ROI's rate or by the rate of small events CoactDetect does not call.
- **CoactDetect removal both misses and over-removes.** It needs three or more ROIs, so two-ROI coincidences and
  weak events stay, and it removes every onset inside an episode, member or not; the emptied episodes are a small
  shared modulation of their own.
- **The block control keeps shared change in 2-minute counts from any source**; the lab claims rest on the arm
  that removes episodes first.
- **Per-recording shares count recordings as units**; the pooled intervals resample mice, but the effective
  number of mice is small (12.7 fast, 7.7 slow under the correlogram weighting).
- **Synthetic numbers carry no interval.** Independent generator background reads 0.88 at 1-minute bins, so
  differences between synthetic ratios of about 10 % are within scatter; the 20 s and 5-minute worlds are five to
  ten times deeper than the lab shoulder.
- **The two folders differ in more than size.** The Dard et al. dataset is in vivo in pups, and its onset is the
  first frame of an inferred active run, not a half-rise, so compare shapes across folders, not lags to the second.
- **The field-step exclusion leaves a 4 s gap across all ROIs** where a step fell inside a baseline window: three
  recordings, 12 s in 27 hours.
- **Baseline only, by rule.** Nothing here says what treatment does.

## Published lineage

- **Shared rate change inflates the correlogram.** Shared rate changes of independent neurons elevate the
  cross-correlogram near zero lag, and a linear trend elevates it flat: Perkel, Gerstein & Moore 1967, *Biophys J*
  7:419–440, doi:10.1016/S0006-3495(67)86597-4, pp. 428–429. Covariation in excitability across trials produces
  correlogram peaks that look like synchrony, and the shuffle-corrected covariogram sums to the count covariance
  across trials: Brody 1999, *Neural Comput* 11:1537–1551, doi:10.1162/089976699300016133. Slow common
  fluctuations produce zero-lag coincidences: Amarasingham, Harrison, Hatsopoulos & Geman 2012, *J Neurophysiol*
  107:517–531, doi:10.1152/jn.00633.2011. Shared slow trends produce nonsense correlations, circular shifting gives
  false positives under them, and shifting with the ends discarded and a trimmed central segment scored is the
  "linear shift" test: Harris 2021, bioRxiv doi:10.1101/2020.11.29.402719 (version of 19 June 2021).
- **The count-variance ratio** is Schluter 1984, *Ecology* 65:998–1005, doi:10.2307/1938071 (who credits Robson
  1972 for the test), with time bins for samples and ROIs for species.
- **Rigid shift is whole-train dithering.** "Firing rates are smoothed on the timescale of the dither width": Louis,
  Borgelt & Grün 2010, §17.3.3, pp. 359–382 in *Analysis of Parallel Spike Trains*, doi:10.1007/978-1-4419-5675-0_17,
  who credit Pipa et al. 2008 (*J Comput Neurosci* 25:64–88, doi:10.1007/s10827-007-0065-3) and Harrison & Geman 2009
  (*Neural Comput* 21:1244–1258, doi:10.1162/neco.2008.03-08-730); Harrison & Geman trace it to Pipa, Riehle & Grün
  2007 (*Neurocomputing* 70:2064–2068, doi:10.1016/j.neucom.2006.10.142), and Pipa et al. 2008 to the multiple-shift
  method of Grün et al. 1999 (unread; the trace stops there). Louis et al. roll the train; this page drops and trims,
  as in Harris's linear shift. Stella et al. 2022 (*eNeuro* 9(3), doi:10.1523/ENEURO.0505-21.2022) rank trial
  shifting the most robust surrogate for spatio-temporal spike-pattern detection at a 25 ms dither; this page shifts
  by 1.6–20 s.
- **The block control** is a variant of interval jitter (Date, Bienenstock & Geman 1998, technical report, Division of
  Applied Mathematics, Brown University; Amarasingham et al. 2012), which holds each train's count fixed in fixed
  windows but re-places onsets independently inside them; the block control shifts the train circularly instead.
  CoactDetect's own null is a rolling-window circular shift in the same family
  ([`detector_history.md`](../../detector_history.md)).
- **The Dard et al. 2022 dataset.** Dard RF, … Picardo MA (with Cossart R), *eLife* 11:e78116,
  doi:10.7554/eLife.78116, INMED (Inserm U1249, Aix-Marseille University); data DANDI:000219 (Dard, Picardo &
  Cossart), licensed [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/); the published version is
  0.260826.1155 (doi:10.48324/dandi.000219/0.260826.1155), and which version was downloaded is not recorded. Activity
  was inferred with DeepCINAC (Denis et al. 2020, *eNeuro* 7:ENEURO.0038-20.2020), a cell counted active from the
  onset to the peak of a transient; imported by [`tools/import_dandi.py`](../../../tools/import_dandi.py). The authors
  detect synchronous events against a per-cell circular shift. Their recording protocol: Ratsifandrihamanana et al.
  2023, *STAR Protocols*, doi:10.1016/j.xpro.2023.102760 (read in summary).

## Reproduce

| step | command | output |
|---|---|---|
| measure | `python tools/measure_slow_comodulation.py` | `results.json` (per recording) and `summary.json` (pooled, no identifiers) in `<darkroom>/bugarach/2026-09-17-slow-comodulation/` |
| re-summarize | `python tools/measure_slow_comodulation.py --out <that folder> --resummarise` | rebuilds both summaries and checks from `results.json` |
| draw | `python tools/make_slow_comodulation_figure.py --run <that folder> --also docs/learned/slow_comodulation` | the six figures here and in the darkroom folder, and `one_recording.png` in the darkroom only |

`summary.json` beside this page is the run's pooled output, with the paired, per-recording, per-group and
leave-five-out checks under `checks` and `checks_by_group`. The measurement took 2 minutes 15 seconds on 10
workers. The tests, `tests/test_measure_slow_comodulation.py`, check that the pair count matches a brute-force
count out to 300 s of lag; that a fixed lag lands in its bin; that the removal arms are divided by the circular
shift of their own onsets; that the block control keeps each ROI's count per block; that rigid shift moves each ROI
by one whole-frame offset and drops what leaves the window; the count variance; and that the generator's background
reads zero while its planted events, its promiscuity probe and the 20 s world do not. They also check that the
circular arm's excess reads zero in every lag bin, which holds in expectation and tests the arithmetic, not the
estimator.
