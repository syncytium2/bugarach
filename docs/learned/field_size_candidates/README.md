# The field-size candidates, on simulation: gauge carries to 566 ROIs, and has a quiet-field problem

> **Working material, not murderboarded.** Same standing as the handoffs and
> [`../../pipelines/learned-model-evaluation.md`](../../pipelines/learned-model-evaluation.md). Every
> number here is on **simulated recordings**. The Cossart spec was built unreviewed, with this lab's
> background shape ([`../cossart_transfer/README.md`](../cossart_transfer/README.md)), so the
> carried scores are good for telling candidates apart and are **not publishable**.

Run 2026-09-16 on branch `eval-field-size-candidates`. The candidates are two of the three designs in
the proposal held back from #589 (branch `claude/net-design-proposal-hw8rve`). `quorum` did not run:
every bench recording has one field size, so its exponent cannot be identified yet.

## What ran

`tools/fair_bakeoff.py`, 4 folds of 6 simulated recordings each (24 recordings), every model fitted
on the **home spec** (32 regions of interest, ROIs) and scored twice: on held-out home recordings,
and with `--score-spec` on the **Cossart spec** (566 ROIs). Nothing about the Cossart spec is visible
to the fit, including the threshold. Each learned model was trained at two torch seeds
(`--train-seed 0` and `1`); the hand-written detectors have no seed.

| model | what it is here | compared against |
|---|---|---|
| `gauge` | `tube`'s kernel bank, standardised against 8 shifted copies of the window, no bypass | `tube_no_bypass` |
| `tube_no_bypass` | the shipped `tube` with its raw-brightness bypass removed | `tube` |
| `chorus` | `line`'s per-ROI vote plus a spread and a loudest-four channel | `line` |
| `tube`, `line` | shipped models | CoactDetect |
| CoactDetect, LoCo | hand-written detectors | — |

All learned models trained at learning rate 1e-2, the control's rate, so no comparison mixes a
mechanism with its optimisation.

**New in this run: a quiet-field negative** (`--null-rates`). Each held-out recording gets null
twins with nothing planted, no distractors and no busy window, at 1×, 0.54× and 0.25× its
background rate, scored at the operating point already chosen. 0.54× is baseline's lower-quartile
per-ROI rate over the lab mean (0.0052 Hz of 0.0097 Hz, FOUNDATIONS §9); 0.25× is a stress level
below anything measured. The existing busy-window probe gives any model that divides by its
surround a free pass, and gauge divides.

**Not run**, and recorded as skipped rather than absent: the pipeline's aggregate-channel leak test,
its rigid-shift controls, label-free training and the real-recording check. These candidates were
built for field size, and the supervised bake-off at home and carried is the stage that asks that.

## Results

F1 is the mean over 4 folds. A fold with planted events and no hits counts as F1 0, not as missing
(`folds_with_no_hits_read_as_zero` in each `compare_seed*/field_size_candidates.json` lists them).

The **probe** columns are the busy-window false alarms (`hot_fa`): every simulated recording carries
a 300 s stretch, 1,200 s to 1,500 s, where every ROI fires at 0.06 Hz with nothing planted. That is
6.2 times the home background (0.0097 Hz) and 2.6 times the Cossart background (0.0233 Hz). A fold
holds 6 held-out recordings, so its count covers 30 minutes of busy window; the table gives the mean
over folds converted to **false alarms per hour of busy window** (count × 2). Probe firings are left
out of precision, so they do not show up in F1.

Each cell gives the seed 0 value, then the seed 1 value. The hand-written detectors have no seed, so they get one value.

| model | F1 home | F1 on Cossart | probe home, per hour | probe on Cossart, per hour |
|---|---|---|---|---|
| gauge | 0.526 / 0.513 | **0.668 / 0.585** | 112 / 79.5 | 26.5 / 31.5 |
| tube_no_bypass | 0.639 / 0.669 | 0.229 / 0.230 | 101.5 / 108 | 0 / 0 |
| tube | 0.656 / 0.635 | 0.140 / 0.244 | 125.5 / 101.5 | 0 / 0 |
| line | 0.666 / 0.710 | 0.005 / 0.145 | 8.5 / 34.5 | 0 / 0 |
| chorus | 0.125 / 0.125 | 0.125 / 0.125 | 0 / 0 | 0 / 0 |
| CoactDetect | 0.645 | 0.774 | 5.5 | 25 |
| LoCo | 0.653 | 0.707 | 14 | 27 |

Per-fold probe counts are in each `bakeoff*.json` under `per_fold[].hot_fa`.

⚠ **A probe count of zero is only evidence from a model that fires.** On Cossart, `tube`,
`tube_no_bypass` and `line` fire almost nowhere (F1 0.005 to 0.244), and chorus fires in the same few
places whatever its input, so their zeros there say they are nearly silent, not that they resist a
busy window. gauge's 26.5 and 31.5 per hour on Cossart sit level with CoactDetect's 25 and LoCo's 27.
At home gauge fires in the busy window about as often as the two tubes (80 to 126 per hour) and 15
to 20 times as often as CoactDetect: standardising against its own null did not buy busy-window
robustness on a 32-ROI field.

`tube` at seed 0 reproduces the shipped 24-recording bake-off's 0.656 exactly, so adding the
`bypass` flag did not move the shipped model.

Paired differences, per fold, as mean and *t* on 3 degrees of freedom:

| comparison | home, seed 0 | home, seed 1 | Cossart, seed 0 | Cossart, seed 1 |
|---|---|---|---|---|
| gauge − tube_no_bypass | −0.113 (*t* −4.2) | −0.157 (*t* −3.1) | **+0.439 (*t* 5.4)** | **+0.356 (*t* 4.3)** |
| tube_no_bypass − tube | −0.017 (*t* −2.4) | +0.034 (*t* 1.2) | +0.088 (*t* 1.4) | −0.014 (*t* −0.2) |
| gauge − CoactDetect | −0.119 (*t* −3.9) | −0.133 (*t* −3.1) | −0.106 (*t* −3.0) | −0.188 (*t* −4.8) |
| line − CoactDetect | +0.021 (*t* 0.9) | +0.065 (*t* 7.3) | −0.768 | −0.629 (*t* −6.1) |

False alarms per hour on the quiet-field twins, home spec, mean over folds:

| model | 1×, seed 0 | 0.54×, seed 0 | 0.25×, seed 0 | 1×, seed 1 | 0.54×, seed 1 | 0.25×, seed 1 |
|---|---|---|---|---|---|---|
| gauge | 23.5 | 42.6 | **76.8** | 15.9 | 26.5 | **57.3** |
| tube_no_bypass | 9.0 | 2.9 | 0.5 | 8.6 | 2.7 | 0.5 |
| tube | 6.6 | 2.3 | 0.3 | 9.5 | 3.1 | 0.8 |
| line | 8.7 | 2.5 | 0.6 | 5.2 | 1.8 | 0.3 |
| CoactDetect | 6.0 | 2.5 | 0.5 | | | |

![Two panels per seed: F1 per fold at home and carried, and false alarms per hour against background rate](compare_seed0/field_size_candidates.png)

**Figure 1. Training seed 0.** Top: F1 per fold, filled blue on the home spec (32 ROIs), open orange
for the same fitted model on the Cossart spec (566 ROIs); grey lines join a fold. Bottom: one panel
per model, false alarms per hour with nothing planted, background rate falling left to right; a
zero is drawn at 0.1 on the log axis. Seed 1 is
[`compare_seed1/field_size_candidates.png`](compare_seed1/field_size_candidates.png) and agrees.

## What the data show

- **gauge is the only learned model that carries to 566 ROIs**, and the gain is the standardisation,
  not the bypass it also drops: gauge beats `tube_no_bypass` on Cossart by +0.44 and +0.36 F1, while
  dropping the bypass alone moves Cossart F1 by +0.09 and −0.01.
- **It pays for that at home and still does not reach the hand-written detectors.** gauge is 0.11 to
  0.16 F1 below its control at home, and 0.11 to 0.19 below CoactDetect in both corpora. Nothing here
  licenses shipping it (the pipeline's gate is the comparison against the hand-written detectors).
- **gauge's false alarms climb as the field empties**, at both seeds, where every other model's fall
  (Figure 1, bottom). Before training, one onset in an otherwise empty 32-ROI, 4,096-frame window
  pushed gauge's standardised input to about 22,900, against a maximum of 29 on a field at the lab's
  rate: the spread of 8 shifted copies of a near-empty window is close to zero, and gauge divides by
  it. On the Cossart spec, where 566 ROIs keep the window busy, its false alarms stay flat at 3 to 5
  per hour.
- **chorus does not train.** At both seeds and in every fold its threshold sat at the bottom of the
  grid (0.0001) and it scored F1 0.125, the same failure `tiny` has always shown. Its *t* values in
  the JSON are arithmetic on a constant and mean nothing. Whether a lower learning rate changes this
  is untested; running it would be a separate, labelled experiment.
- **line, the best learned model at home, carries worst**: 0.005 and 0.145 F1 on Cossart, with
  three and two folds of no hits. A share-of-field-lit statistic thresholded at 32 ROIs does not
  survive 566.

## Limits

- Simulation only, and the Cossart spec is unreviewed with an inherited background.
- 4 folds: *t* has 3 degrees of freedom, and two training seeds are a replicate, not a distribution.
- The quiet-field twins are this run's construction; 0.25× is below any measured baseline.
- gauge's null is deterministic and set by row order, so relabelling the ROIs moves its output
  slightly (about 0.03 on an untrained model at 32 ROIs); `encode` fixes the order in use.
- Every run's provenance records `git_dirty: true`: the output folder was untracked while the runs
  wrote into it. The tools each run used were committed at the recorded commit.

## Files

`bakeoff.json` and `bakeoff_seed1.json` (home), `bakeoff_generator_spec_to_spec_k12.json` and
`..._seed1.json` (Cossart), the four run logs, and `compare_seed0/`, `compare_seed1/` from
`tools/compare_field_size_candidates.py`. Darkroom copies of both figures:
`<darkroom>/bugarach/field-size-candidates/seed0/` and `seed1/`.
