# Rigid shift as a teacher: what it destroys, and why training on it alone did not work

## What the night found

- **Rigid shift is a sound negative class at the displacements tried, and it removes more than
  intended.** Its shared-offset control reads chance on all three folders — but that control is
  weaker than it looks, and this page now says how.
- **The counting architecture leads the bake-off and the lead is not separable.** `line` takes the
  top mean F1, and its margin over the *existing hand-written* CoactDetect is +0.063 at four folds
  with one fold carrying it. The one-sensor ablation is statistically indistinguishable from
  CoactDetect.
- **Training against rigid shift alone did not work.** No architecture trained this way approaches
  its own supervised score, and on real recordings the calls of the rigid-shift-trained `line`
  often land where no ROI has an onset.
- **The objective, not the architecture, is the bottleneck** — but the evidence for that is weaker
  than the previous draft of this page claimed, and the correction is below.

> **Exploratory, run overnight 2026-09-15 into 2026-09-16, and reviewed twice the same night**
> ([run record](../../reviews/tube-self-supervised-2026-09-16.md)). Nothing here is promoted:
> `docs/MILESTONES.md` reserves promoting a bake-off number to Tony, and its standing ruling is
> **a table of performance, not a ranking**, because the fold spreads do not support an ordering.
>
> **⚠ marks a claim this report is telling you not to lean on**, with the reason beside it.
>
> **Two names collide, and the collision is older than this page.** In the handoff written hours
> earlier, `line` meant the **length-only** build. Here that model is **`line_length`**, and
> `line` is the two-sensor build. Every table below uses the names in that second sense.
>
> **F1** is the harmonic mean of recall and precision, 1.0 perfect. A **ROI** (region of interest)
> is a cell. An **onset** is the frame at which a cell's calcium transient starts.

## The problem

The lab records calcium imaging of hippocampal slices, and a **coordinated event** is several cells
becoming active within a fraction of a second. Nobody has annotated this corpus, so every
*supervised* detector here is fitted on a **simulator** whose events were measured from the lab's
own recordings — and a detector that never sees a real event cannot be told it was wrong about one.

A label-free detector would need no annotation. It needs instead a set of examples of what it
should *not* fire on: copies of a recording that keep everything except the thing being detected.
**Rigid shift** is the candidate. Each ROI's whole onset train slides by one random offset within
±*J* seconds (*J* is the displacement radius, 10 s and 20 s here), so every ROI keeps its own rate
and its own intervals while the alignment *between* ROIs is destroyed. Onsets pushed past the edge
are dropped rather than wrapped.

Three questions follow.

1. **Does rigid shift destroy the right thing** — cross-ROI alignment, and nothing else?
2. **Is a counting architecture better than the centre-surround one** the project already has?
3. **Can a detector be trained against rigid shift alone**, with no labels anywhere?

The night answered the first two and returned a clear negative on the third. A fourth question —
what any of this does on real tissue — is answered last, and it is where the sharpest result sits.

## What holds, and what does not

The measure in this section and in Figure 2's panel C is a **share of paired comparisons**: how
often the real recording scores above its surrogate, where **0.50 is chance**. It is not an F1.

**Rigid shift hides, and it destroys — but the control that says so is weak on the stream that
matters.** Shifting every ROI of a recording by *one shared* offset moves each ROI's own train
exactly as rigid shift does while keeping the ROIs aligned; that control reads chance, 0.49–0.53,
on the lab fast stream, the lab slow stream and the Cossart folder, out to 40 s (44.8 s on lab
slow). ⚠ **On the lab fast stream, the stream the whole label-free experiment ran on, that
classifier never rises above chance for rigid shift either** (0.486–0.505 at every *J* from 1.6 s
to 40 s), so on that stream the control has never been shown able to fail. It does ring on Cossart
(0.586 at *J* = 10 s) and on lab slow (0.567 at 44.8 s). ⚠ **The control is also near-vacuous by
construction**: both crops are taken at the same absolute index from rasters differing by a global
translation, and these models are translation-equivariant, so the two crops are largely the same
frames — **26–42 % of the paired comparisons are ties**, counted as half. And a shared offset
preserves the cross-ROI rate covariance that the aggregate-channel test below does detect, so this
control cannot exclude the one leak the run actually found.

**What rigid shift destroys is not only brief coordination**: at 10–20 s it also removes shared
modulation slower than an event, which is real and detectable on the lab slow stream and on Cossart
and absent on the lab fast stream. Whether that counts as coordination is the **shared-modulation
decision** below, and the rigid-shift note stays under its correction banner until it is answered.
A graded control that freezes half the ROIs and shifts the rest reads 0.39–0.49 against 0.00 for
the fully shifted recording and 1.00 for the untouched one, so the measure can register partial
removal — ⚠ that range is the Cossart folder at 50 % participation and small plant sizes; at 20 %
participation the same control reads 0.00–0.38.

**The counting architecture leads the bake-off, and the lead is not separable from the detector the
project already has.** `line` counts how many ROIs are lit and judges that count against its own
background; it takes the top mean F1, 0.713 against `tube`'s 0.686 and the length-only ablation's
0.655. Against the ablation the paired per-fold differences are +0.045, −0.009, +0.179 and +0.017 —
three folds of four, with the mean carried by one, t(3) = 1.39. ⚠ **The comparison that decides
whether the learned family earns its place is against CoactDetect, and the report's previous draft
never made it**: `line` − CoactDetect is +0.063, t(3) = 1.31, and `line_length` − CoactDetect is
+0.005, t(3) = 0.34. Drop the one fold that carries it and `line`'s margin over CoactDetect is
+0.015. **The one-sensor ablation is statistically indistinguishable from the existing hand-written
detector.**

**Training on rigid shift alone did not work, and the architecture is not why.** Every architecture
lands at 0.34–0.49 with a truth-reading threshold — `line` included, and no better than the tube
family — against 0.65–0.70 supervised. The bottleneck is the objective, which pays for anything
that separates real from shifted. ⚠ **How much of that is "not coordination" is less settled than
the previous draft said**: a classifier reading only the pooled trace separates real from
rigid-shifted at 0.66–0.67 (0.66–0.69 using every aggregate channel), against the trained models'
0.73–0.75 — but the pooled trace **is the share of the field that is lit**, which is the very
quantity `line` computes. So what the aggregate test excludes is **pairwise and ROI-identity
structure**, not co-activity; and its confidence interval, [0.62, 0.72] at *J* = 10 s, reaches the
models' own scores, so the two are not separable.

## Figure 1. What the second sensor buys

![Figure 1. What the second sensor buys](line_sensors_fig.png)

**`line` carries two sensors.** One measures **relative length** — how many of the field's ROIs are
lit at once. The other measures **temporal concentration** — whether those onsets are packed into
one instant or spread out, read as the ratio of the count at a narrow smear to the count at the
next wider one. The registered ablation `line_length` keeps only the first.

**Panel A, the bake-off.** One run, one generator spec, four folds of two recordings, 30 planted
events per fold. Every detector is calibrated or trained on three folds and scored on the fourth.
Rows are grouped by family and **not** ordered by score. Each dot is one fold and the bar is the
mean over the four — deliberately not a range bar, which reads as a confidence interval. ± below
is the sample standard deviation over the four folds.

| detector | what it is | F1 | fold range | recall | precision | probe firings | parameters |
|---|---|---|---|---|---|---|---|
| line, two sensors | learned here | 0.713 ± 0.078 | 0.64–0.81 | 0.933 | 0.580 | 5.50 | 1,305 |
| line_length, length only | learned here | 0.655 ± 0.035 | 0.62–0.69 | 0.750 | 0.592 | 1.25 | 1,233 |
| tube | learned here | 0.686 ± 0.042 | 0.65–0.74 | 0.925 | 0.547 | 20.50 | 1,149 |
| tube_guard | learned here | 0.680 ± 0.060 | 0.63–0.75 | 0.817 | 0.583 | 4.75 | 1,149 |
| tube_ratio | learned here | 0.503 ± 0.069 | 0.42–0.56 | 0.650 | 0.426 | 0.00 | 1,149 |
| tube_ratio_guard | learned here | 0.471 ± 0.055 | 0.42–0.55 | 0.583 | 0.405 | 0.00 | 1,149 |
| tiny | learned here | 0.125 ± 0.000 | 0.12–0.12 | 0.067 | 1.000 | 0.00 | 2,393 |
| trace | learned here | 0.110 ± 0.018 | 0.09–0.12 | 0.075 | 0.372 | 0.00 | 2,065 |
| CoactDetect | hand-written here | 0.651 ± 0.044 | 0.61–0.71 | 0.767 | 0.572 | 1.25 | — |
| LoCo | hand-written here | 0.645 ± 0.057 | 0.57–0.70 | 0.742 | 0.575 | 2.50 | — |
| rate+context | hand-written here | 0.571 ± 0.085 | 0.46–0.65 | 0.700 | 0.485 | 34.75 | — |
| locust | port of another lab's | 0.541 ± 0.070 | 0.47–0.63 | 0.742 | 0.446 | 214.75 | — |
| binned SCE | port of another lab's | 0.451 ± 0.096 | 0.33–0.54 | 0.533 | 0.395 | 59.50 | — |
| SPIKE-synch | wraps another lab's measure | 0.267 ± 0.072 | 0.21–0.34 | 0.175 | 0.569 | 8.75 | — |

**Probe firings** are calls made inside a stretch of the benchmark where ROIs are dense but
uncoordinated — no planted event is there to find. They are excluded from precision and reported
separately, because a detector can buy recall with promiscuity. That is what the second sensor did:
recall 0.750 → 0.933 and probe firings 1.25 → 5.50, for 72 extra parameters. ⚠ **The second sensor
is nearly free to fit**, and the previous draft of this page said the opposite: `line` fits in
51.4 s against the ablation's 50.7 s, **1.4 % slower, not eight times**. Both counting builds fit
about eight times slower than `tube` (6.5 s) — that cost belongs to the family, not to the sensor.

⚠ **Three of these rows are this project's detection layer wrapped around someone else's measure,
and their scores are not statements about those measures.** `SPIKE-synch` wraps the
SPIKE-synchronization profile (Kreuz, Mulansky & Bozanic 2015) as implemented in PySpike (Mulansky
& Kreuz 2016) and sits under two open defects; Kreuz's own lab has since published a detection
layer on that profile (Kreuz et al. 2022, *J Neurosci Methods* 381:109703), so the wrapping is not
an unoccupied idea. `locust` is a **partial, modified** port — by way of interface2 — of the
Cossart lab's CICADA (software: Zenodo `10.5281/zenodo.10041434`; framework: Hamon et al. 2026),
and it skips CICADA's own transient-detection stage, so **its numbers are never measurements of
CICADA**. `binned SCE` descends from Cossart, Aronov & Yuste 2003.

**Panel B, the plant test.** On a quiet synthetic field, four plants of equal **ink** (the same
total number of onsets): a **line plant** (as many ROIs as the plant size, one onset each, all in
one frame), a **burst** (a quarter of them firing four times each over 0.6 s), **fuzz** (the same
ROIs spread over 2.9 s) and a **wave** (the same ROIs one frame apart, 1.5 s at the largest plant).
Each model's score is its peak response with the plant minus the same field without it.

| supervised model | ÷ burst, plant 4 / 8 / 16 | ÷ fuzz, 4 / 8 / 16 | ÷ wave, 4 / 8 / 16 |
|---|---|---|---|
| line, two sensors | 3.90 / 1.63 / 1.83 | 1.27 / 1.44 / 1.99 | 1.01 / 1.05 / 1.32 |
| line_length | 5.05 / 1.99 / 1.82 | 1.24 / 1.31 / 1.75 | 1.01 / 1.04 / 1.14 |
| tube | 2.24 / 1.23 / 1.34 | 1.22 / 1.08 / 1.43 | 1.00 / 0.99 / 1.17 |

Both `line` builds tell a line plant from a burst better than `tube` does at every plant size, and
the **÷ fuzz** column — the comparison the tool was written for, and the one the previous draft
omitted — orders the models the way the count sensor predicts at the largest plant: 1.99, 1.75,
1.43. The temporal-concentration sensor shows up only at the largest plant (1.32 against 1.14), and
at the smallest the ablation is the better discriminator. n = 12 fields, one training seed.

⚠ **Read this panel as a direction and not a measurement**, for four reasons. The two largest
numbers divide by a denominator consistent with zero — `line`'s 3.90 is 10.29 ÷ 2.64 ± 3.37 — which
is why those markers are drawn open. A ratio of two differences is only scale-free if the model is
affine, and the head is a six-layer stack, so these ratios do not strictly compare across models.
The wave's duration is **confounded with the plant size** by construction (3 frames at plant 4,
15 frames at plant 16), so the rise across that row is what any concentration sensor must do when
the stimulus lengthens. And the per-field spread of `line`'s raw response to the 16-ROI line plant
is ±4.4 on a mean of 18.5, in the model's own arbitrary units.

⚠ **The wave is not a tilt.** These models are order-free over ROIs and the encoder sorts rows by
rate, so the diagonal a person sees in a raster is a fact about the *display's* row order, which
the encoder discards before the model sees anything. Tony asked for an orientation detector;
orientation in the image is not available to an order-free model, and temporal concentration is the
nearest readable quantity. ⚠ It is also not what "orientation" means in the vision literature, and
the architecture is nonetheless **registered** under that word, where no caveat travels with it.

⚠ **`line` also names a plant here**, not only a model. The plant is written "line plant"
throughout; the underlying data file uses the bare key.

## Figure 2. Learning from rigid shift alone

![Figure 2. Learning from rigid shift alone](tube_ssl_fig.png)

**Read the contrast before the result.** The objective pays for *anything* that separates a real
crop from its rigid shift, and a classifier reading only the pooled co-activity trace already
reaches 0.66–0.67 of that separation on its own. So a model scoring 0.73–0.75 on the same contrast
has not necessarily learned anything about coordination beyond counting — and the intervals
overlap, so "how much more" is not resolved by this run.

Four architectures × three training seeds × four folds, in six arms: supervised and untrained
controls (at *J* = 10 s), and trained against rigid shift with no labels on unlabelled **simulated**
recordings and on real lab fast-stream baseline recordings, at each displacement. That is 4 × 3 × 4
= 48 fits per arm and **288 scored rows**. The objective is a ranking loss on the mean of the top
1 % of the model's per-frame scores, comparing a real crop — a 4,096-frame window, 409.6 s at this
stream's 0.1 s frame interval — against the same crop rigid-shifted.

**Two thresholds.** The *label-free* threshold is, per recording, the lowest threshold at which the
model fires at most a stated rate (0.5, 1 or 2 events per 10 minutes) on rigid shifts of **that**
recording, reading no labels. The *truth-reading* ("oracle") threshold is the F1-best threshold on
the training folds' validation recordings; it **reads planted truth** and is a comparison ceiling,
not a usable rule. ± is the population standard deviation over the 12 fits of an arm, and a fit
whose detections hit nothing scores 0 and is included in every mean.

**Panel A is the truth-reading threshold; panel B is the label-free one.**

**Supervised, as the threshold tightens:**

| model | ≤ 0.5 ev/10 min | ≤ 1 ev/10 min | ≤ 2 ev/10 min | truth-reading |
|---|---|---|---|---|
| line | 0.573 ± 0.090 | 0.668 ± 0.077 | 0.699 ± 0.067 | 0.698 ± 0.062 |
| line_length | 0.601 ± 0.073 | 0.663 ± 0.064 | 0.703 ± 0.061 | 0.693 ± 0.055 |
| tube | 0.432 ± 0.032 | 0.519 ± 0.075 | 0.625 ± 0.064 | 0.665 ± 0.055 |
| tube_guard | 0.487 ± 0.107 | 0.542 ± 0.105 | 0.640 ± 0.084 | 0.652 ± 0.058 |

Both counting builds give up about a sixth of their F1 as the threshold tightens (0.70 → 0.57–0.60)
whereas `tube` gives up a third (0.63 → 0.43). **This is the ablation's result as much as the
two-sensor build's** — at the tightest threshold the ablation is ahead.

**Trained against rigid shift, both displacements** (truth-reading | label-free ≤ 2 per 10 min):

| model | simulated, *J* 10 s | simulated, 20 s | real, 10 s | real, 20 s |
|---|---|---|---|---|
| line | 0.441 \| 0.261 | 0.465 \| 0.285 | 0.405 \| 0.241 | 0.463 \| 0.305 |
| line_length | 0.450 \| 0.341 | 0.446 \| 0.211 | 0.455 \| 0.286 | 0.448 \| 0.221 |
| tube | 0.409 \| 0.224 | 0.382 \| 0.124 | 0.432 \| 0.256 | 0.488 \| 0.310 |
| tube_guard | 0.338 \| 0.236 | 0.463 \| 0.287 | 0.487 \| 0.289 | 0.441 \| 0.283 |

No architecture separates from the others, and none approaches its own supervised score. Between 0
and 3 fits of each twelve ended at or above chance loss (ln 2 = 0.693); by a looser cut of 0.6, 1
to 5 did.

⚠ **The untrained arm is not a usable baseline, and it is also not uniformly collapsed.** At the
truth-reading threshold its detections are tens of seconds wide and cover almost the whole
recording, so it "hits" planted events by being on nearly everywhere: untrained `tube` fires 85
detections to touch 20 of 30 planted events where supervised `line` needs 46 for 25.6. The
rate-limited label-free threshold collapses most of it — but not all four:

| model | untrained, truth-reading | untrained, label-free ≤ 2 |
|---|---|---|
| line | 0.356 | 0.000 |
| line_length | 0.400 | **0.272** |
| tube | **0.507** | 0.071 |
| tube_guard | 0.441 | 0.099 |

Untrained `line_length` at 0.272 beats nine of the sixteen trained label-free cells, and untrained
`tube` at 0.507 is above **every** trained truth-reading cell. So the honest statement is narrower
than "there is no working baseline": **training against rigid shift did not beat random
initialisation**, and at the truth-reading threshold it was worse than it. ⚠ The widths and
coverage quoted above are read off a diagnostic that is **not shipped** — `results.jsonl` records
only the number of detections — so they cannot be reproduced from this folder.

**Panel C, the paired checks.** Real against the shared offset reads 0.49–0.53, unplanted twins
against their rigid shift read 0.47–0.55, and real against rigid shift reads 0.73–0.75. The first
and third are on held-out mice; the twin leg is synthetic and has no mouse.

## On real recordings

All 84 lab fast-stream **baseline recordings**, each judged by a model that never saw its mouse,
beside CoactDetect and LoCo at their production operating points. **Neither is ground truth** —
nothing in this folder is annotated, and `docs/MILESTONES.md` blocks quoting any transfer figure
until a MAHICE review (machine-assisted human identification of coordinated events — a person
annotating a sample with the tool's help) exists. This is a consistency check.

⚠ **Read the whole section under the edge finding below**: detections of every kind are enriched
near the window edges, which changes how each number here should be taken.

| detector | events per 10 min | ROIs in the detection's extent, ±2 frames: median, share ≥ 3 | within ±1 s: median, share ≥ 3 |
|---|---|---|---|
| CoactDetect | 2.70 | 7, 1.00 | 7, 1.00 |
| LoCo | 2.57 | 7, 1.00 | 8, 1.00 |
| supervised tube, label-free | 4.62 | 5, 0.80 | 5, 0.87 |
| supervised tube_guard, label-free | 5.01 | 5, 0.84 | 5, 0.88 |
| supervised line, label-free | 4.95 | 4, 0.82 | 5, 0.88 |
| supervised line_length, label-free | 4.24 | 4, 0.81 | 5, 0.86 |
| line vs rigid shift, *J* 20 s | 5.73 | **0, 0.14** | 4, 0.63 |
| line vs rigid shift, *J* 10 s | 5.70 | **1, 0.22** | 2, 0.48 |
| random times in the same recordings | — | 0, 0.07–0.18 | 1, 0.19–0.27 |

⚠ **CoactDetect and LoCo cannot report a thin event**: both run at their default floor of **three**
ROIs, so their 1.00 is a floor, not a finding. (The previous draft said four.) ⚠ Each learned model
also has a second arm in the same run, thresholded at its bake-off operating point, which fires
5.2–6.7 events per 10 minutes; those rows are not shown here.

**At the event itself, half the calls from `line` trained against rigid shift contain no ROI onset
at all.** That is the bolded row and not the four supervised rows above it, whose medians are 4–5
ROIs — "label-free" names both a threshold rule and a training regime in this table, and only the
regime is meant here. The ±1 s column is the permissive one, and at that width a random time
already reaches three or more ROIs a quarter of the time.

**This one is worth looking at rather than reading.** A lanes-over-raster view of one baseline
recording is in the darkroom at `2026-09-16-tube-self-supervised/tube_real_lanes_20240813_39_*.png`
(whole baseline, and a 120 s zoom): CoactDetect, LoCo and supervised `line` all mark the same
visible column of onsets, while the rigid-shift-trained lane marks two places where the raster is
empty. ⚠ **It is not embedded here and there is no repo copy**, because it holds a real baseline
raster and FOUNDATIONS §5 releases exactly one such image by name — "a list of one, not a
category". Rebuild it with
`tools/make_tube_real_lanes.py --run <real_compare> --out <darkroom> --family line`.

**Agreement** is matched at ±1 s, where every F1 in this report is matched at the scorer's ±2.5 s.
⚠ It is also a **many-to-one overlap share, not a recall**: a detector that fragments one reference
event into five calls is credited five times.

| supervised model | share of each reference's events caught (CoactDetect / LoCo) | share of its own events near a reference |
|---|---|---|
| tube_guard | 0.854 / 0.872 | 0.462 / 0.435 |
| tube | 0.829 / 0.802 | 0.473 / 0.428 |
| line | 0.774 / 0.758 | 0.444 / 0.399 |
| line_length | 0.745 / 0.688 | 0.431 / 0.381 |

**On real recordings the architecture that leads the bake-off is third of the four supervised
models** — ahead only of its own ablation, and behind both tube builds. The previous draft of this
page said "last of four", quoting the two rows that made it readable; that was wrong.

⚠ **The stated ceiling is exceeded, and the catch rate has no precision partner.** The two
references agree with each other only 0.71–0.77, yet three of four supervised models sit above it
(0.802–0.872) while firing 4.2–5.0 events per 10 minutes against the references' 2.57–2.70. Catching
more of a reference by firing more is exactly the promiscuity the bake-off section warns about, and
the reverse direction — 0.38–0.47 — is the column that bounds it.

The models trained against rigid shift catch 27–77 % of the references' events and place 16–30 % of
their own within 1 s of a reference call, against chance rates of 3–6 % in that direction (8–13 % in
the reverse one); the catch rates are measured against the seed-0 fit.

⚠ **Events concentrate at window edges; the earlier version of this page reported the opposite.**
Within 5 s of a window edge the table's rows run 2.7–5.2 % where the uniform expectation is 0.8 %,
and within 12.8 s they run 4.7–7.0 % against 2.1 % — a three- to sixfold enrichment at 5 s and a two-
to threefold one at 12.8 s, for the learned models **and** for CoactDetect. LoCo puts 0 of 429 events
within 5 s and 4 within 12.8 s. **An edge artefact is not excluded — it is indicated.** The 12.8 s is
the difference-of-Gaussians kernel's **padded support** (128 frames), not the fitted filter's
half-width, which is 0.1–1.2 s. The mechanism that fits every architecture is the dilated head's own
zero padding; a count zero-padded at the recording's ends fits `line` but not `tube`, which shows
the effect too.

## What this does not settle

- **The bake-off ordering is not separable**, and the comparison against the existing hand-written
  detector is the one that matters. Four folds, one training seed per fold. The seed axis is the
  cheap replication and has not been run. *(Gates the orientation decision.)*
- **The surrogate is used three orders of magnitude from its published regime.** Stella et al. 2022
  rank whole-train shifting most robust at a dither of **25 ms**, trial by trial; this run shifts a
  whole recording by **10–20 s**. The slow-modulation removal measured above is why that ranking
  does not simply transfer. *(Gates the shared-modulation decision.)*
- **The objective is untuned**: one pooling rule, one learning rate, 900 steps. It pays for any
  separation of real from shifted, so a two-ROI coincidence earns as much as a crowd. *(Gates the
  objective decision.)*
- **The ablation changes more than one thing.** Removing the concentration sensor also changed the
  fitted smear widths, so the sensor and the time scale it induces are confounded. ⚠ The widths
  quoted in the previous draft are **in no shipped file**; re-running the four fits reproduces the
  direction but not the values.
- ⚠ **`line`'s defining claim does not hold as stated.** Its docstring says one ROI casts at most
  one vote, but onsets are summed *before* the sigmoid, so the cap bounds the vote's height and not
  its time integral — and the difference-of-Gaussians stage downstream reads the integral. A
  four-onset burst delivers 1.7–2.7× the integrated vote of a single onset. The line-versus-burst
  result is therefore partly a width effect.
- ⚠ **The concentration sensor's baseline is not 1.** On an empty field its three channels read
  0.635, 1.30 and 0.494, so "near 1 means a vertical line" does not identify a line.
- **The benchmark is a simulator** whose planted events carry 0.31 s of jitter. Real fast onset
  jitter was measured at **0.36 s against a 0.42 s circular-shift null on 47 of 84 slices**, and
  `docs/generator.md` flags **the 0.36 s** as its least trustworthy number and an upper bound; a
  separate measurement in the private interface2 repository (commit `f76e7b1b`) gives 1.04 s on a
  differently-selected 85 slices and **is not checkable from this repository**.
- **The real-recording statistics are pooled over events, not clustered by mouse.** The 84
  recordings come from 44 mice. ⚠ This caveat is narrower than the previous draft's: the
  aggregate-channel test *is* mouse-grouped, and the controls run ships a per-group breakdown.
- **Only the lab fast stream** was used for the label-free work.
- **`line` was written on 2026-09-15 and has never been reviewed as code**; the behavioural tests
  that pin `tube`'s claims are hardwired to `tube`, and **no test covers the numpy rigid shift that
  actually produced every surrogate here**.
- **The literature search behind the lineage below covered** spike-train surrogates, radar
  constant-false-alarm-rate detection, calcium-imaging event detection and weakly-supervised
  sound-event detection. It did **not** cover anomaly detection and change-point analysis, EEG burst
  detection, or astronomical and seismological transient detection, where thresholds set to a stated
  event rate are routine.

## What waits on Tony

1. **Does the concentration sensor stay on by default?** It is on. For it: the mechanism is clean,
   recall rose 0.750 → 0.933, and the ÷ fuzz ordering at the largest plant goes the right way.
   Against it: the F1 gain of 0.058 is inside a fold spread of 0.17, and probe firings rose
   1.25 → 5.50. **The fit-time argument the previous draft made against it was wrong** — the sensor
   costs 1.4 % of fit time and 72 parameters. Also against it: on real recordings `line` sits third
   of four. Three seeds would settle it; the ablation is already a registered architecture.
2. **Does shared modulation on timescales of 10–45 s count as coordination?** Rigid shift at
   10–20 s removes it. Present and detectable on the lab slow stream (0.550 at 22.4 s, 0.561 at
   44.8 s) and on Cossart (0.58–0.60 from 10 s); absent on the lab fast stream (flat at 0.50). The
   answer decides whether *J* belongs at 10–20 s at all, given that the published regime is 25 ms.
3. **Is the objective worth another attempt?** The surrogate is not obviously the problem; the loss
   is. An objective that pays for the **number** of ROIs in a window, rather than for any separation
   of real from shifted, is the next design — and the weakly-supervised sound-event literature has
   measured which pooling rules localise events in time (Wang, Li & Metze 2019; McFee, Salamon &
   Bello 2018).
4. **Which firing rate should the label-free threshold target?** The supervised table gives 0.5, 1
   and 2 events per 10 minutes; under the ≤ 2 rule the supervised models realise 4.2–5.0 events per
   10 minutes on real recordings, against CoactDetect's 2.70. No recommendation is made here.

## The published lineage

Nearly every component here is prior art, and the report inherits it. Whole-train shifting is
Pipa et al. 2008, surveyed in Louis, Borgelt & Grün 2010 — which recommends it and credits it
jointly to Pipa et al. 2008 and Harrison & Geman 2009 — and ranked most robust by Stella et al. 2022
for the SPADE analysis, at a 25 ms dither. ⚠ Pipa et al. 2008 itself credits the multiple-shift
method (Grün et al. 1999) as its antecedent; that paper is closed-access and unread here, so **where
whole-train shifting begins is not established**. ⚠ An earlier draft attributed the method to Pipa,
Riehle & Grün 2007; that paper is not held and no source reached attributes train shifting to it.

On the edge rule: Louis, Borgelt & Grün 2010 rolls the train specifically to avoid underestimating
the expected coincidence count, and warns that dropping is acceptable only where start and end rates
match. This run drops, which **deflates the surrogate's coincidence count** — biasing the null in the
direction that makes real recordings look more coordinated. ⚠ The previous draft said "the published
form wraps"; Elephant's own `dither_spike_train` does not wrap either, and the only wrapping method
on this page is Dard et al. 2022's *circular* shift.

Counting co-active cells against a per-cell circular shift, with a threshold read off that surrogate,
is how Dard et al. 2022 detect events in the very dataset this page also uses. Holding a false-alarm
rate fixed by estimating the background and setting a threshold from it is constant-false-alarm-rate
(CFAR) detection (Finn & Johnson 1968) — the stage that is CFAR-shaped here is `line`'s
difference-of-Gaussians, whose centre is the cell under test and whose surround is the local
reference; the label-free threshold rule is better described as a surrogate threshold. Capping each
cell at one vote is the clipping step of Unitary Events (Grün, Diesmann & Aertsen 2002, Part I; the
construction is Grün 1996), though here the bound is soft rather than exact.

**What is this project's own** is narrow, and narrower than the previous draft claimed: making that
construction differentiable and trainable, and setting its operating point at a stated event rate,
is new **in the calcium-imaging literature**. ⚠ Training a detector under a stated false-alarm
constraint is established in radar — CFARnet (Diskin et al. 2022) and differentiable
Neyman–Pearson layers — so the transfer, not the idea, is what is ours.

## Provenance and how to reproduce

Branch `unsup/rigid-shift-controls`, code version `0.1.0+g68f2328`. All four analysis stages ran in
one chain on 2026-09-15 night in the Elephant virtual environment (torch 2.14.0), with
`PYTHONPATH=<worktree>/src`; the two figures were rendered from their outputs.

⚠ **Elephant did not generate the surrogates in this run.** Every stage here draws through a numpy
rigid shift in `tools/tube_self_supervised.py`, an exact integer shift matching Elephant's
`dither_spike_train(edges=True)` in distribution but differing in seeding — Elephant seeds per ROI,
this draws all offsets from one generator in row order. Elephant (RRID:SCR_003833) generates the
surrogates in the earlier **controls** stage, through `bugarach.surrogates.rigid_shift`.

| stage | command | output |
|---|---|---|
| bake-off | `tools/fair_bakeoff.py --spec docs/learned/generator_spec.json --out <dir>` | `line_bakeoff/bakeoff.json` |
| label-free training | `tools/tube_self_supervised.py --out <dir> --jobs 12` | `training/` |
| real recordings | `tools/tube_ssl_real_compare.py --out <dir> --checkpoints <dir>/checkpoints --jobs 12` | `real_compare/` |
| plant test | `tools/probe_line_vs_fuzz.py --checkpoints <dir>/checkpoints --out <dir>` | `probe/line_vs_fuzz.json` |
| Figure 1 | `tools/make_line_sensors_figure.py --bakeoff <dir> --probe <dir> --out <dir>` | `line_sensors_fig.png` |
| Figure 2 | `tools/make_tube_ssl_figure.py --run <dir> --out <dir>` | `tube_ssl_fig.png` |

The architecture is `src/bugarach/learn/nets/line.py`; the ablation is `line_length.py`.
`real_compare/checkpoints/` holds the seed-0, fold-0 fit of each architecture and displacement — 8
of the 96 the plant test read; the other 88 are not shipped.

Earlier stages of this thread: the aggregate-channel test in [`aggregate_leak/`](aggregate_leak/),
the controls run in [`../rigid_shift_look/controls/`](../rigid_shift_look/controls/), and the first
tube training run. The
[handoff](../../handoffs/2026-09-15-rigid-shift-controls-and-tube-training.md) describes all three;
⚠ its numbers for the length-only build come from the superseded run whose folder this one
overwrote, and its window-edge paragraph carries the reading this page has now corrected.
