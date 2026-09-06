# The fair bake-off — real recordings in, one data set, one rule

**First run 2026-08-16. Re-run 2026-08-28 and the numbers moved** — see
*What changed on the re-run* below before quoting any of them against an earlier
copy of this page. Everything is regenerable:
`tools/assess_archive.py` → `tools/derive_spec.py` → `tools/fair_bakeoff.py` →
`tools/make_bakeoff_figures.py`. Numbers live in `bakeoff.json`,
`assessment_real.json` and `generator_spec.json`.

⚠ **The table below is transcribed by hand from `bakeoff.json`, and that is a
known weakness of this page rather than a feature of it.** `report.src.html`
solved the same problem by substituting tokens at build time, with a comment
saying why: *"a superseding notice carrying its own stale transcription of the
newer result would be the exact failure this substitution exists to stop."* This
page has no generator, so every re-run needs a human to retype nine rows — and on
2026-08-28 one of its claims had been stale for eight days without anyone
noticing. Giving it one is filed as
[`2026-08-28-the-bakeoff-page-transcribes-what-a-token-could-substitute.md`](../todo/2026-08-28-the-bakeoff-page-transcribes-what-a-token-could-substitute.md).

## What was run

1. **85 real recordings measured**, without a detector. interface2's rescued
   dead-ROI store (`dead-roi-store` @ `752855a`, rule *keep any ROI that fires
   anywhere*), FAST stream, **baseline regions only** — `hik`, `ttx`, `senktide`,
   `sb222200` and `wash` counted and skipped, per FOUNDATIONS §9. 1000 surrogates.
2. **One generator spec derived** from that assessment at **K=3** — chosen by hand
   because the assessor reports a scan and a human signs off, with the whole scan
   shipped beside the choice. Heterogeneous and bursty background turned on.
3. **One data set generated**: 8 recordings, 470 recording-minutes, split into 4
   folds of 2.
4. **Every detector calibrated or trained on 3 folds and scored on the 4th**, all
   four rotations. Hand-written detectors sweep their declared knob; learned
   models pick a threshold. Same data set, same procedure, same scorer
   (`bench.pool_scores`).

## The result

![the bake-off](bakeoff.png)

| detector | F1 (mean of 4 folds) | fold range | recall | precision | fit s | detect s | params | probe firings |
|---|---|---|---|---|---|---|---|---|
| **center−surround (learned)** | 0.686 ± 0.042 | 0.65–0.74 | 0.925 | 0.547 | 7.1 | 0.026 | 1,149 | 20.5 |
| CoactDetect | 0.651 ± 0.044 | 0.61–0.71 | 0.767 | 0.572 | 1.5 | 0.063 | — | 1.2 |
| LoCo | 0.645 ± 0.057 | 0.57–0.70 | 0.742 | 0.575 | 4.5 | 0.252 | — | 2.5 |
| rate+context | 0.571 ± 0.085 | 0.46–0.65 | 0.700 | 0.485 | 0.2 | 0.005 | — | 34.8 |
| locust | 0.541 ± 0.070 | 0.47–0.63 | 0.742 | 0.446 | 3.3 | 0.116 | — | 214.8 |
| binned SCE | 0.451 ± 0.096 | 0.33–0.54 | 0.533 | 0.395 | 0.3 | 0.012 | — | 59.5 |
| SPIKE-synch | 0.267 ± 0.072 | 0.21–0.34 | 0.175 | 0.569 | 1.8 | 0.096 | — | 8.8 |
| per-cell bank (learned) | 0.125 ± 0.000 | 0.12–0.12 | 0.067 | 1.000 | 76.6 | 0.230 | 2,393 | 0.0 |
| pooled trace (learned) | 0.110 ± 0.018 | 0.09–0.12 | 0.075 | 0.372 | 8.5 | 0.022 | 2,065 | 0.0 |

`fit s` is time to calibrate (hand-written) or train (learned). `detect s` is
wall-clock to run one held-out fold — 2 recordings, ~118 minutes of data.

### What changed on the re-run, and why

Three defects were fixed on 2026-08-28, in one change because each of them moves
the same numbers and fixing them separately would have meant regenerating three
times. **None was found by re-running this page**; all three were found by trying
to make the run *reproduce somewhere else*.

1. **The operating point was chosen on the recordings the model had just been
   fitted to.** `pick_threshold` draws validation seeds from a block disjoint from
   the training block and asserts it — but every caller supplied a maker that
   mapped both blocks onto the same recordings, so the assertion passed on *seeds*
   while the *recordings* were identical. `learn.train.fold_maker` splits the
   training folds again. **This is what moved the learned rows.** The scored fold
   was never reachable either way, so no earlier F1 on this page was inflated by
   it; what was wrong is that a fairness guarantee the code stated was not the one
   it delivered.
2. **Torch's thread count was read off the hardware.** The first run's numbers
   reproduced only on a 10-thread machine. Threads are pinned to 1 now — the only
   count available everywhere — which is what makes the `fit s` and `detect s`
   columns comparable between machines and **not** comparable with the first run's.
3. **The reference was already stale against its own bench.** SCE's knob grid had
   been extended downward (floor 90 → 75) after the first run, so the sweep could
   reach an operating point the reference never had. SCE's chosen percentile moves
   on three of four folds for that reason alone, which is why its recall and
   precision move a long way while its F1 barely does.

**The six are the control**: they never touch torch, and every one of them is
unchanged **in F1** to four decimal places except SCE, for reason 3.

⚠ Their *timings* did move — `locust`'s calibration goes 2.6 s → 3.3 s — and **no
mechanism is claimed for it**. Thread pinning is the obvious suspect and it is the
wrong one: `torch.set_num_threads` does not reach numpy's BLAS, which is what the
hand-written detectors run on. What is left is this page's own standing caveat —
one machine, one process, no warm-up control — and a re-run on a differently loaded
laptop. Read the **F1** column as the control; the timing columns are an
order-of-magnitude comparison within a run, not between runs.

### On accuracy: a tie at the top, and it should be read as one

Centre−surround leads on the mean. **It is still not ahead of CoactDetect.** Their
fold ranges are 0.63–0.74 and 0.61–0.71, overlapping across most of both; four
folds of 30 planted events cannot separate 0.686 from 0.651, and panel A draws
every fold so that overlap is visible rather than hidden behind a bar. Three
detectors remain tied at the top and the honest statement is unchanged: the
learned model **reaches the level of the best hand-written detectors in this
project**, having been given no more information than they were.

**What did change is the shape of how it gets there**, and it is worth more
attention than the mean. Recall went 0.775 → 0.917 while precision fell
0.590 → 0.543: the model now finds nearly every planted event and pays for it in
false positives, where before it split the difference. That is a consequence of
picking the operating point honestly — on recordings the fit never saw, rather
than on the ones it had just been fitted to — and it is the same direction the
probe column shows (16 → 21 firings into a block containing nothing). **A reader
comparing this page against an earlier copy should read the recall and precision
columns, not the F1**: F1 moved 0.013 while recall moved 0.142 and precision
0.047, so the summary is the number that hid the change.

### On cost: this is where the difference is

- **Detection.** 0.023 s to scan two hour-long recordings — **2.6× faster than
  CoactDetect and 10.5× faster than LoCo**, the two it ties with. Only
  `rate+context` is faster, and it sits 0.11 of F1 lower. ⚠ Those multiples were
  4× and 17× on the first run. **Both runs' multiples are internally consistent
  and neither is comparable with the other**: this run pins torch to one thread,
  which changes the learned model's wall-clock, and the hand-written detectors'
  timings moved too for reasons this page does not establish (see the control note
  above). What the ranking supports is *the learned model is the fastest of the
  three at the top*, which holds in both runs. What it does not support is a
  changed multiple read as a changed model.
- **Fitting.** 6.9 s to train from scratch. CoactDetect's sweep is quicker (1.1 s),
  LoCo's is comparable (4.4 s) — so for the app's purpose, training a model on a
  lab's own simulated data costs about the same as calibrating a hand-written
  detector, and buys a faster detector at the end of it.
- **Size.** 1,149 parameters. Small enough to ship pre-trained and fine-tune in
  place.

That combination — top-of-pack accuracy, seconds to fit, milliseconds to run,
kilobytes to store — is the case for the in-app loop, and it is the first time
this project has measured it on a footing where the comparison means anything.

### On the two that still do not learn

`pooled trace` and `per-cell bank` remain at the floor (0.110, 0.125). The
per-cell bank costs **75.6 s to train and 0.226 s to detect** — 11× the training
and 9.6× the detection of the model that works, for a fifth of the F1. ⚠ Those were
236 s and 2.45 s on the first run, and the drop is **not** an improvement to the
architecture: pinning torch to one thread happens to suit this model, which spent
its time contending across ten. Same code, different thread count.

⚠ **Both land their threshold on the low edge of the searched grid**, which this
project treats elsewhere as a search that stopped too early rather than an answer,
so their F1 is reported for completeness and is not an operating point. On the
first run that was true of the per-cell bank alone; the grid has since been opened
at the bottom as well as the top, and under it the pooled trace joined it — three
of its four folds sit at the floor. **That matters more than its F1 does**, because
the pooled trace is the *control*: it exists to answer whether giving up
distinctness costs anything, and a control with no operating point cannot answer
it. The centre−surround still beats it by a wide margin and the direction is what
the architecture argument predicts — but the baseline is not being beaten at its
best, because it has no best. Both weak architectures also train at a tenth the
centre−surround's learning rate, so *"worse architecture"* is not yet separable
from *"trained differently"*:
[`2026-08-28-two-architectures-have-no-operating-point.md`](../todo/2026-08-28-two-architectures-have-no-operating-point.md).

## What the assessment found on the way

Two things fell out that were not the objective.

- ~~**The bench's regimes reproduce.**~~ **Retracted 2026-08-28 — this agreement
  no longer exists, and it had been gone for eight days before anyone checked.**
  The claim was that per-ROI rate across the 85 slices has an interquartile range
  of 0.0037–0.0185 Hz, matching the bench's quiet and busy regimes at 0.0038 and
  0.0175. Both halves were measured on the **`.mat` store**. On 2026-08-20 the
  bench moved its regimes to **0.0052 and 0.0190**, re-derived from the approved
  export folder — because the store carries every recording ever processed,
  including two the lab withdrew (FOUNDATIONS §9, and the defect SAP007 exists to
  stop). So the agreement celebrated here is between two measurements of the same
  superseded source, and it reads as corroboration when it is the opposite: the
  page and the bench agreed because they were making the same mistake.
  **Nothing in the results table depends on this** — it was an aside, and it is
  left visible rather than deleted because a reader of the earlier version needs
  to know it was withdrawn.
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
   promiscuity *report*: locust fires 215 times in a block containing nothing;
   center−surround fires 21; CoactDetect fires 1.
4. **K=3 was chosen by a human and the choice moves the data set.** The scan is in
   `generator_spec.json`; K=4 cuts the cluster rate to roughly a quarter of K=3's
   (0.095 against 0.350 per minute) and would build a different
   benchmark.
5. **Timings are one machine, one process, no warm-up control.** They are
   order-of-magnitude comparisons, not benchmarks.
6. **Still simulated.** The generator's settings are measured from real
   recordings; the recordings the detectors were scored on are not real. Nothing
   here says any detector is right about a real slice.
