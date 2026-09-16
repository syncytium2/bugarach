# Rigid shift as a teacher, and the detector built to learn from it

> **Exploratory, run overnight 2026-09-15 into 2026-09-16, and reviewed the same night**
> ([run record](../../reviews/tube-self-supervised-2026-09-16.md)). Nothing here is promoted:
> `docs/MILESTONES.md` reserves promoting a bake-off number to Tony, and its standing ruling is
> **a table of performance, not a ranking**, because the fold spreads do not support an ordering.
> Read every table below under that ruling. Provenance and commands are at the foot of the page.

## The problem

The lab records calcium imaging of hippocampal slices: each **ROI** (region of interest) is a cell,
and a **coordinated event** is several cells becoming active within a fraction of a second. Nobody
has annotated this corpus, so every learned detector here is fitted on a **simulator** whose events
were measured from the lab's own recordings — and a detector that never sees a real event cannot be
told it was wrong about one.

A label-free detector would need no annotation. It needs a **negative class** instead: copies of a
recording that keep everything except the thing being detected. **Rigid shift** is the candidate.
Each ROI's whole onset train slides by one random offset within ±*J* seconds (*J* is the
displacement radius, 10 s and 20 s here), so every ROI keeps its own rate and its own intervals
while the alignment *between* ROIs is destroyed.

**The published lineage matters and the report inherits it.** Whole-train shifting is Pipa, Riehle &
Grün 2007 and Pipa et al. 2008, surveyed in Louis, Borgelt & Grün 2010 and ranked most robust by
Stella et al. 2022 — where the published form **wraps** the train and this run does not, dropping
onsets pushed past the edge. Counting co-active cells against a per-cell circular shift, with a
threshold read off that surrogate, is how Dard et al. 2022 detect events in the very dataset this
page also uses. Holding a false-alarm rate fixed by estimating the background and setting the
threshold from it is CFAR (Finn & Johnson 1968); `docs/detector_history.md` §4 traces this project's
hand-written detectors to the same tradition. Capping each cell at one vote is the clipping step of
Unitary Events (Grün, Diesmann & Aertsen 2002). **What is this project's own** is narrow: making
that construction differentiable and trainable, and setting its operating point at a stated event
rate rather than a fixed tail quantile.

Three questions follow, and the night answered all three.

## What holds, and what does not

**Rigid shift hides and it destroys — with the destruction measured only where it was measured.**
Shifting every ROI of a recording by *one shared* offset moves each ROI's own train exactly as rigid
shift does while keeping the ROIs aligned; that control reads at chance, 0.49–0.53, on the lab fast
stream, the lab slow stream and the Cossart folder, out to 40 s (44.8 s on lab slow). So the rise
under rigid shift is removed cross-ROI structure, not a per-ROI leak. Removal was measured on
Cossart at that folder's own participation and in the earlier look on the lab folder, and a graded
control (`freeze_half`, 0.41–0.49 against 0.00 and 1.00) shows the measure can register partial
removal. **What rigid shift destroys is not only brief coordination**: at 10–20 s it also removes
shared modulation slower than an event, which is real and detectable on the lab slow stream and on
Cossart and absent on the lab fast stream. Whether that counts as coordination is the second
decision below, and the rigid-shift note stays under its correction banner until it is answered.

**The counting architecture is worth having, by a margin four folds cannot resolve.** `line` counts
how many ROIs are lit and judges that count against its own background; it takes the top mean F1 in
the bake-off, 0.713 against `tube`'s 0.686 and the length-only ablation's 0.655. The ordering is not
separable: `line`'s folds run 0.64–0.81, and against the ablation the paired per-fold differences
are +0.045, −0.009, +0.179 and +0.017 — three folds of four, with the mean carried by one. It also
costs: `line` fires 5.50 probe firings per fold against the ablation's 1.25, and trains eight times
slower.

**Training on rigid shift alone did not work, and the architecture is not why.** Every architecture
lands at 0.40–0.49 with an oracle threshold — `line` included, and no better than the tube family —
against 0.65–0.70 supervised. The bottleneck is the objective, which pays for anything that
separates real from shifted: on tube's own input channel, a classifier reading **only** the pooled
trace already separates real from rigid-shifted at 0.66–0.69, so most of what these models learned
needs no cross-ROI structure at all.

## Figure 1. What the second sensor buys

![Figure 1. What the second sensor buys](line_sensors_fig.png)

**Panel A, the bake-off.** One run, one generator spec, four folds of two recordings, 30 planted
events per fold. Every detector is calibrated or trained on three folds and scored on the fourth.
Rows are grouped by family and **not** ordered by score. Bars are the fold range; ± below is the
sample standard deviation over the four folds.

| detector | F1 | fold range | recall | precision | probe firings | parameters |
|---|---|---|---|---|---|---|
| line, two sensors | 0.713 ± 0.078 | 0.64–0.81 | 0.933 | 0.580 | 5.50 | 1,305 |
| line_length, length only | 0.655 ± 0.035 | 0.62–0.69 | 0.750 | 0.592 | 1.25 | 1,233 |
| tube | 0.686 ± 0.042 | 0.65–0.74 | 0.925 | 0.547 | 20.50 | 1,149 |
| tube_guard | 0.680 ± 0.060 | 0.63–0.75 | 0.817 | 0.583 | 4.75 | 1,149 |
| tube_ratio | 0.503 ± 0.069 | 0.42–0.56 | 0.650 | 0.426 | 2.75 | 1,149 |
| tube_ratio_guard | 0.471 ± 0.055 | 0.42–0.55 | 0.583 | 0.405 | 1.00 | 1,149 |
| tiny | 0.125 ± 0.000 | 0.12–0.12 | 0.067 | 1.000 | 0.00 | 2,393 |
| trace | 0.110 ± 0.018 | 0.09–0.12 | 0.075 | 0.372 | 0.00 | 2,065 |
| CoactDetect | 0.651 ± 0.044 | 0.61–0.71 | 0.767 | 0.572 | 1.25 | — |
| LoCo | 0.645 ± 0.057 | 0.57–0.70 | 0.742 | 0.575 | 2.50 | — |
| rate+context | 0.571 ± 0.085 | 0.46–0.65 | 0.700 | 0.485 | 34.75 | — |
| locust | 0.541 ± 0.070 | 0.47–0.63 | 0.742 | 0.446 | 214.75 | — |
| binned SCE | 0.451 ± 0.096 | 0.33–0.54 | 0.533 | 0.395 | 59.50 | — |
| SPIKE-synch | 0.267 ± 0.072 | 0.21–0.34 | 0.175 | 0.569 | 8.75 | — |

**Probe firings** are calls in the dense-but-random block, excluded from precision and reported
separately because a detector can buy recall with promiscuity. That is what the second sensor did:
recall 0.750 → 0.933 and probe firings 1.25 → 5.50, for 72 parameters. It is also 7.9 times slower
to fit (51.4 s against `tube`'s 6.5 s) and 6.3 times slower to run.

⚠ **Two of these rows are this project's detection layer wrapped around someone else's measure, and
their scores are not statements about those measures.** `SPIKE-synch` wraps Kreuz, Mulansky &
Bozanic 2015 and sits under two open defects; `locust` is a port of the Cossart lab's CICADA (Denis
et al. 2020); `binned SCE` descends from Cossart, Aronov & Yuste 2003.

**Panel B, the probe.** On a quiet synthetic field, four plants of equal **ink** (the same total
number of onsets): a **line** (plant size ROIs, one onset each, in one frame), a **burst** (a
quarter of them firing four times each over 0.6 s), **fuzz** (the same ROIs spread over 2.9 s) and a
**wave** (the same ROIs one frame apart, 1.6 s at the largest plant). Each model's score is its peak
response with the plant minus the same field without it; that removes each model's **offset** but
**not its gain**, so only the ratios compare models, and only ratios are plotted.

| supervised model | line ÷ burst, plant 4 / 8 / 16 | line ÷ wave, plant 4 / 8 / 16 |
|---|---|---|
| line, two sensors | 3.90 / 1.63 / 1.83 | 1.01 / 1.05 / 1.32 |
| line_length | 5.05 / 1.99 / 1.82 | 1.01 / 1.04 / 1.14 |
| tube | 2.24 / 1.22 / 1.34 | 1.00 / 1.02 / 1.17 |

Both `line` builds tell a line from a burst better than `tube` does at every plant size, which is
the distinctness the count channel was built for. **The orientation channels show up only at the
largest plant** (1.32 against 1.14), and at the smallest the ablation is the better discriminator.
n = 12 fields, one training seed, and the per-field spread is ±4.4 on a mean of 18.5 — so this is a
direction, not a measurement.

⚠ **The wave is not a tilt.** These models are permutation-invariant over ROIs and the encoder sorts
rows by rate, so the diagonal a person sees in a raster is a fact about row order, which the model
never reads. What these channels measure is **temporal concentration**. Tony asked for an
orientation detector; orientation in the image is not available to an order-free model, and this is
the nearest readable quantity.

## Figure 2. Learning from rigid shift alone

![Figure 2. Learning from rigid shift alone](tube_ssl_fig.png)

Four architectures × three torch seeds × four folds, in six arms: supervised and untrained controls
(at *J* = 10 s), and trained against rigid shift with no labels on unlabelled **simulated**
recordings and on real lab fast-stream baselines, at each displacement. That is **192 label-free
fits plus 48 supervised and 48 untrained runs, 288 scored rows.** The objective is a ranking loss on
the mean of the top 1 % of per-frame **logits**, a real crop (a 4,096-frame window) against the same
crop rigid-shifted.

**Two thresholds.** *Label-free*: per recording, the lowest threshold at which the model fires at
most *r* events per 10 minutes on three rigid shifts of **that** recording, reading no labels.
*Oracle*: the F1-best threshold on the training folds' validation recordings, which **reads planted
truth** and is a comparison ceiling, not a usable rule. ± here is the population standard deviation
over the 12 fits of each arm.

**Supervised, as the threshold tightens:**

| model | ≤ 0.5 events / 10 min | ≤ 1 | ≤ 2 | oracle |
|---|---|---|---|---|
| line | 0.573 ± 0.090 | 0.668 ± 0.077 | 0.699 ± 0.067 | 0.698 ± 0.062 |
| line_length | 0.601 ± 0.073 | 0.663 ± 0.064 | 0.703 ± 0.061 | 0.693 ± 0.055 |
| tube | 0.432 ± 0.032 | 0.519 ± 0.075 | 0.625 ± 0.064 | 0.665 ± 0.055 |
| tube_guard | 0.487 ± 0.107 | 0.542 ± 0.105 | 0.640 ± 0.084 | 0.652 ± 0.058 |

Both counting builds give up about a sixth of their F1 as the threshold tightens (0.70 → 0.57–0.60)
where `tube` gives up a third (0.63 → 0.43). **This is the ablation's result as much as the
two-sensor build's** — at the tightest threshold the ablation is ahead.

**Trained against rigid shift, both displacements, all arms** (oracle | label-free ≤ 2 per 10 min):

| model | simulated, *J* 10 s | simulated, 20 s | real, 10 s | real, 20 s |
|---|---|---|---|---|
| line | 0.441 \| 0.261 | 0.465 \| 0.285 | 0.405 \| 0.241 | 0.463 \| 0.305 |
| line_length | 0.450 \| 0.341 | 0.446 \| 0.211 | 0.455 \| 0.286 | 0.448 \| 0.221 |
| tube | 0.409 \| 0.224 | 0.382 \| 0.124 | 0.432 \| 0.256 | 0.488 \| 0.310 |
| tube_guard | 0.338 \| 0.236 | 0.463 \| 0.287 | 0.487 \| 0.289 | 0.441 \| 0.283 |

No architecture separates from the others, and none approaches its own supervised score. Between 0
and 4 fits of each twelve ended at or above chance loss (ln 2 = 0.693); by the looser cut of 0.6
used in the figure, 1 to 4 did.

⚠ **The untrained column is not a baseline, and the shaded band in the figure says so.** Its
detections are 32–169 s wide and cover 95–99 % of a recording, so it "hits" planted events by being
on almost everywhere: untrained `tube` fires 85 detections to touch 20 of 30 planted events where
supervised `line` needs 46 for 25.6. Its output at planted events equals its output elsewhere to
four decimal places. The rate-limited label-free threshold collapses it to 0.07 and 0.00, which is
the label-free rule behaving correctly. **The comparison "training beats initialisation" cannot be
made from this run** — there is no working baseline in it.

**Panel C, what the models trained on real recordings learned**, on held-out mice: real against the
shared offset reads 0.49–0.53 (no per-ROI or count leak), unplanted twins against their rigid shift
read 0.47–0.57, and real against rigid shift reads 0.73–0.76. ⚠ **Most of that last number needs no
coordination**: the aggregate-channel test in [`aggregate_leak/`](aggregate_leak/) separates real
from rigid-shifted at **0.66–0.69** using only the pooled trace.

## On real recordings

All 84 lab fast-stream baselines, each judged by a model that never saw its mouse, beside
CoactDetect and LoCo at their production operating points. **Neither is ground truth** — nothing in
this folder is annotated, and `docs/MILESTONES.md` blocks quoting any transfer figure until a MAHICE
review exists. This is a consistency check. The two references agree with each other 0.71–0.77, so
that is the ceiling any model is measured against.

| detector | events per 10 min | ROIs at the event (±2 frames): median, share ≥ 3 | within ±1 s: median, share ≥ 3 |
|---|---|---|---|
| CoactDetect | 2.70 | 7, 1.00 | 7, 1.00 |
| LoCo | 2.57 | 7, 1.00 | 8, 1.00 |
| supervised tube, label-free | 4.62 | 5, 0.80 | 5, 0.87 |
| supervised tube_guard, label-free | 5.01 | 5, 0.84 | 5, 0.88 |
| supervised line, label-free | 4.95 | 4, 0.82 | 5, 0.88 |
| supervised line_length, label-free | 4.24 | 4, 0.81 | 5, 0.86 |
| line vs rigid shift, *J* 20 s | 5.73 | **0, 0.14** | 4, 0.63 |
| line vs rigid shift, *J* 10 s | 5.70 | **1, 0.22** | 2, 0.48 |
| random times in the same recordings | — | 1, 0.21–0.27 | 1, 0.21–0.27 |

⚠ **CoactDetect and LoCo cannot report a thin event**: they run at `min_rois` = 4 on this stream, so
their 1.00 is a floor, not a finding.

**At the event itself, half the label-free calls contain no ROI onset at all.** The ±1 s column is
the permissive one, and at that width a random time already reaches three ROIs a quarter of the
time. Agreement (matched at ±1 s, where every F1 in this report is matched at the scorer's ±2.5 s):
supervised `tube` catches 80–83 % of the two references' events and `line` 76–77 %, so **on real
recordings the architecture that leads the bake-off is last of the four supervised models.** The
models trained against rigid shift catch 47–72 % and place 19–30 % of their own events within 1 s of
a reference call, against chance rates of 4–13 %; the catch rates are measured against the seed-0
fit.

⚠ **The window-edge check is inverted, and the earlier version of this page had it backwards.**
Events within 5 s of a window edge run 2.7–4.6 % where the uniform expectation is 0.8 %, and within
the difference-of-Gaussians half-width of 12.8 s they run 4.9–6.4 % against 2.1 %. That is a three-
to five-fold enrichment at the edges for the learned models and for CoactDetect; LoCo puts 0 of 429
events there. **An edge artefact is not excluded — it is indicated**, and the likely mechanism is
that the count is zero-padded at the recording's ends.

## What this does not settle

- **The bake-off ordering is not separable.** Four folds, one training seed per fold. The seed axis
  (`--train-seed`) is the cheap replication and has not been run.
- **Each label-free row is one of two displacements**, and the table now shows both.
- **The objective is untuned**: one pooling rule, one learning rate, 900 steps. It pays for any
  separation of real from shifted, so a two-ROI coincidence earns as much as a crowd.
- **The ablation is not ceteris paribus.** Removing the orientation channels also changed the fitted
  smear widths (`line` [1.47, 2.25, 3.26, 8.65] samples against `line_length` [1.54, 4.21, 6.50,
  18.36]), so the sensor and the time scale it induces are confounded.
- **The benchmark is a simulator** whose planted events carry 0.31 s of jitter. Real fast onset
  jitter was measured at **0.36 s against a 0.42 s circular-shift null on 47 of 84 slices**, and
  `docs/generator.md` flags **that** number as its least trustworthy and an upper bound; a separate
  measurement in the private interface2 repository (commit `f76e7b1b`) gives 1.04 s on 85 slices.
- **Statistics are pooled over events, not clustered by mouse.** The 84 recordings come from 44
  mice, and no per-group breakdown is given, though the group is in the file the analysis loaded.
- **Only the lab fast stream** was used for the label-free work.
- **`line` is a day old and has never been reviewed as code**, and the behavioural tests that pin
  `tube`'s claims are hardwired to `tube`.

## What waits on Tony

1. **Does orientation stay on by default?** It is on. For it: the mechanism is clean and recall rose
   0.750 → 0.933. Against it: the F1 gain of 0.058 is inside a fold spread of 0.17, probe firings
   rose 1.25 → 5.50, and fitting is eight times slower. Three seeds would settle it; the ablation is
   already a registered architecture.
2. **Does shared modulation on timescales of 10–45 s count as coordination?** Rigid shift at 10–20 s
   removes it. Present and detectable on the lab slow stream (0.550 at 22.4 s, 0.561 at 44.8 s) and
   on Cossart (0.58–0.60 from 10 s); absent on the lab fast stream (flat at 0.50).
3. **Is the objective worth another attempt?** The surrogate is not the problem; the loss is. An
   objective that pays for the **number** of ROIs in a window, rather than for any separation of
   real from shifted, is the next design — and the weakly-supervised sound-event literature has
   measured which pooling rules localise (Wang, Li & Metze 2019; McFee, Salamon & Bello 2018).
4. **Which firing rate should the label-free threshold target?** The tables give 0.5, 1 and 2 events
   per 10 minutes and no recommendation.

## Provenance and how to reproduce

Branch `unsup/rigid-shift-controls`. All four stages ran in one chain on 2026-09-15 night in the
Elephant virtual environment (`bugarach-worktrees/surrogate-screen-overnight-venv`, torch 2.14.0),
with `PYTHONPATH=<worktree>/src`. Elephant (RRID:SCR_003833) generates every surrogate; its version
is not pinned in this run, which it should be.

| stage | command | output |
|---|---|---|
| bake-off | `tools/fair_bakeoff.py --spec docs/learned/generator_spec.json --out <dir>` | `line_bakeoff/bakeoff.json` |
| label-free training | `tools/tube_self_supervised.py --out <dir> --jobs 12` | `training/` |
| real recordings | `tools/tube_ssl_real_compare.py --out <dir> --checkpoints <dir>/checkpoints --jobs 12` | `real_compare/` |
| probe | `tools/probe_line_vs_fuzz.py --checkpoints <dir>/checkpoints --out <dir>` | `probe/line_vs_fuzz.json` |
| Figure 1 | `tools/make_line_sensors_figure.py --bakeoff <dir> --probe <dir> --out <dir>` | `line_sensors_fig.png` |
| Figure 2 | `tools/make_tube_ssl_figure.py --run <dir> --out <dir>` | `tube_ssl_fig.png` |

The architecture is `src/bugarach/learn/nets/line.py`; the ablation is `line_length.py`.
`real_compare/checkpoints/` holds the seed-0, fold-0 fit of each architecture and displacement; the
probe read all 96 checkpoints, which are not shipped. ⚠ **`line` named the length-only build in the
handoff written hours earlier** — that model is `line_length` here.

Earlier stages of this thread: the aggregate-channel leak test in [`aggregate_leak/`](aggregate_leak/),
the controls run in [`../rigid_shift_look/controls/`](../rigid_shift_look/controls/), and the first
tube training run in the
[handoff](../../handoffs/2026-09-15-rigid-shift-controls-and-tube-training.md), which describes all
three.
