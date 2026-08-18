# The fair bake-off — real recordings in, one corpus, one rule

**Run 2026-08-16.** Everything below is regenerable:
`tools/assess_archive.py` → `tools/derive_spec.py` → `tools/fair_bakeoff.py` →
`tools/make_bakeoff_figures.py`. Numbers live in `bakeoff.json`,
`assessment_real.json` and `generator_spec.json`.

## What was run

1. **85 real recordings measured**, without a detector. interface2's rescued
   dead-ROI store (`dead-roi-store` @ `752855a`, rule *keep any ROI that fires
   anywhere*), FAST stream, **baseline regions only** — `hik`, `ttx`, `senktide`,
   `sb222200` and `wash` counted and skipped, per FOUNDATIONS §9. 1000 surrogates.
2. **One generator spec derived** from that assessment at **K=3** — chosen by hand
   because the assessor reports a scan and a human signs off, with the whole scan
   shipped beside the choice. Heterogeneous and bursty background turned on.
3. **One corpus generated**: 8 recordings, 470 recording-minutes, split into 4
   folds of 2.
4. **Every detector calibrated or trained on 3 folds and scored on the 4th**, all
   four rotations. Hand-written detectors sweep their declared knob; learned
   models pick a threshold. Same corpus, same procedure, same scorer
   (`bench.pool_scores`).

## The result

![the bake-off](bakeoff.png)

| detector | F1 (mean of 4 folds) | fold range | recall | precision | fit s | detect s | params | probe firings |
|---|---|---|---|---|---|---|---|---|
| **centre−surround (learned)** | **0.668 ± 0.061** | 0.58–0.73 | 0.775 | 0.590 | 5.6 | **0.014** | 1,149 | 15.8 |
| CoactDetect | 0.651 ± 0.044 | 0.61–0.71 | 0.767 | 0.572 | 1.1 | 0.060 | — | 1.2 |
| LoCo | 0.638 ± 0.053 | 0.57–0.70 | 0.733 | 0.569 | 4.4 | 0.245 | — | 2.5 |
| rate+context | 0.571 ± 0.085 | 0.46–0.65 | 0.700 | 0.485 | 0.2 | 0.005 | — | 34.8 |
| CICADA | 0.541 ± 0.070 | 0.47–0.63 | 0.742 | 0.446 | 2.6 | 0.114 | — | 214.8 |
| binned SCE | 0.422 ± 0.083 | 0.31–0.49 | 0.400 | 0.453 | 0.2 | 0.011 | — | 58.8 |
| SPIKE-synch | 0.254 ± 0.065 | 0.21–0.34 | 0.167 | 0.538 | 1.7 | 0.094 | — | 8.8 |
| pooled trace (learned) | 0.131 ± 0.012 | 0.12–0.15 | 0.075 | 0.825 | 8.0 | 0.015 | 2,065 | 0.0 |
| per-cell bank (learned) | 0.125 ± 0.000 | 0.12–0.12 | 0.067 | 1.000 | 236.4 | 2.453 | 2,393 | 0.0 |

`fit s` is time to calibrate (hand-written) or train (learned). `detect s` is
wall-clock to run one held-out fold — 2 recordings, ~118 minutes of data.

### On accuracy: a tie at the top, and it should be read as one

Centre−surround leads on the mean. **It is not ahead of CoactDetect.** Their fold
ranges are 0.58–0.73 and 0.61–0.71; four folds of 30 planted events cannot
separate 0.668 from 0.651, and panel A draws every fold so that overlap is visible
rather than hidden behind a bar. Three detectors are tied at the top and the
honest statement is that the learned model **reaches the level of the best
hand-written detectors in this project**, having been given no more information
than they were.

### On cost: this is where the difference is

- **Detection.** 0.014 s to scan two hour-long recordings — **4× faster than
  CoactDetect and 17× faster than LoCo**, the two it ties with. Only
  `rate+context` is faster, and it sits 0.10 of F1 lower.
- **Fitting.** 5.6 s to train from scratch. CoactDetect's sweep is quicker (1.1 s),
  LoCo's is comparable (4.4 s) — so for the app's purpose, training a model on a
  lab's own simulated data costs about the same as calibrating a hand-written
  detector, and buys a faster detector at the end of it.
- **Size.** 1,149 parameters. Small enough to ship pre-trained and fine-tune in
  place.

That combination — top-of-pack accuracy, seconds to fit, milliseconds to run,
kilobytes to store — is the case for the in-app loop, and it is the first time
this project has measured it on a footing where the comparison means anything.

### On the two that still do not learn

`pooled trace` and `per-cell bank` remain at the floor (0.13, 0.125). The per-cell
bank costs **236 s to train and 2.45 s to detect** — 42× the training and 175× the
detection of the model that works, for a fifth of the F1. ⚠ Both land their
threshold on the low edge of the searched grid, which this project treats
elsewhere as a search that stopped too early rather than an answer, so their F1 is
reported for completeness and is not an operating point.

## What the assessment found on the way

Two things fell out that were not the objective.

- **The bench's regimes reproduce.** Per-ROI rate across the 85 slices has an
  interquartile range of **0.0037–0.0185 Hz**. The bench's quiet and busy regimes,
  set weeks ago from a different archive, are **0.0038 and 0.0175**.
- **38% of slices have a median ROI that never fires in baseline** — FOUNDATIONS
  §9's "roughly 35% with no events in a baseline window", on a store it was never
  measured on. This also disqualified `roi_rate_med` as a background rate: a median
  over a population a third silent describes the silence. Using it gave 0.0023 Hz,
  below anything this project has recorded.

Observed within-cluster onset spread sits **below** its own circular-shift null at
every K (0.311 vs 0.335 at K=3; 0.255 vs 0.428 at K=8) — the direction real
coordination should show.

## ⚠ What this does not establish

1. **Four folds, 8 recordings, 30 planted events per fold.** Every interval here is
   a fold range, not a confidence interval, and the top three are a tie.
2. **One training run per fold.** Seed variance within a fold is unmeasured; the
   fold-to-fold spread confounds data variation with training variation.
3. **The probe still cannot fail.** Firings inside it leave both numerator and
   denominator, so the column above is a diagnostic and not a penalty
   (`docs/todo/2026-08-16-promiscuity-probe-cannot-fail.md`). Read it as a
   promiscuity *report*: CICADA fires 215 times in a block containing nothing;
   centre−surround fires 16; CoactDetect fires 1.
4. **K=3 was chosen by a human and the choice moves the corpus.** The scan is in
   `generator_spec.json`; K=4 cuts the cluster rate to roughly a quarter of K=3's
   (0.095 against 0.350 per minute) and would build a different
   benchmark.
5. **Timings are one machine, one process, no warm-up control.** They are
   order-of-magnitude comparisons, not benchmarks.
6. **Still simulated.** The generator's settings are measured from real
   recordings; the recordings the detectors were scored on are not real. Nothing
   here says any detector is right about a real slice.
