# The first learned models trained on the ADOPTED fast bench

Run 2026-09-23 on WSMIP064, on the GPU (RTX A4000). **Working material, not murderboarded.**

Tony, 2026-09-23: *"set up the learned runs immediately."* **No learned model had been trained on
the current fast bench.** The only fast/slow learned numbers were the
[2026-09-21 pilot](../2026-09-21-slow-pilot/README.md), fitted before the jitter and background
constants moved, and it saved no checkpoints. WSMIP065 takes slow in parallel.

**Tool:** `tools/train_learned_on_bench.py --bench fast`, the protocol the combined run used
(#754) — fit on bench seeds 1000–1023 on both backgrounds, score on fresh seeds 4000–4023, plus
calls/hour on the no-coordination recording. **On `main` at `a59ad4c`, which contains `2c19003`**
(the adoption, #756): fast quiet 0.0042 Hz, busy 0.0165, probe 0.1271, jitter 0.106 s.
**Checkpoints and `best.json` are in the darkroom**, `bugarach/2026-09-23-learned-fast/models/`;
only each `summary.json` is here, because a checkpoint is bulk.

**12–16 seconds a fit on CUDA**, against about 200 s on CPU — which is why five seeds per model
was affordable and why the combined run's CPU protocol did not have to change to get them.

Abbreviations: **F1**, the harmonic mean of recall and precision; **calls/h**, calls per hour on
the bench's no-coordination recording.

## The fits

Held-out mean F1 is the mean of the quiet and busy scores on seeds 4000–4023.

### `chorus_gain_norm`

| seed | F1 quiet | F1 busy | mean | calls/h | threshold | |
|---|---|---|---|---|---|---|
| 0 | 0.754 | 0.723 | 0.739 | 0.56 | 0.9948 | |
| **1** | **0.822** | **0.781** | **0.801** | **2.33** | 0.9000 | **best** |
| 2 | 0.831 | 0.754 | 0.792 | 2.44 | 0.9716 | |
| 3 | 0.824 | 0.737 | 0.780 | 1.78 | 0.9838 | |
| 4 | 0.802 | 0.687 | 0.744 | 1.67 | 0.9908 | |

### `chorus_norm` — the variant the 2026-09-21 pilot trained, so the rows are comparable

| seed | F1 quiet | F1 busy | mean | calls/h | threshold | |
|---|---|---|---|---|---|---|
| 0 | 0.824 | 0.697 | 0.760 | 4.33 | 0.9000 | |
| **1** | **0.830** | **0.789** | **0.809** | **2.67** | 0.9716 | **best** |
| 2 | 0.824 | 0.763 | 0.794 | 1.00 | 0.9716 | |
| 3 | 0.804 | 0.770 | 0.787 | **9.44** | 0.8500 | ⚠ over the 7.0 budget, excluded from selection |
| 4 | 0.814 | 0.709 | 0.761 | 4.78 | 0.9500 | |

**No fit collapsed.** About a sixth of `chorus_gain_norm` fits normally fall to F1 near 0.125
(`docs/goals/learned-model-family.md`); none of these ten did, so this batch may be luckier than
typical and five seeds is not enough to say otherwise.

**One fit exceeded the false-alarm budget** — `chorus_norm` seed 3 at 9.44 calls/h against
`MAX_FALSE_POSITIVES_PER_HOUR["coact"]` = 7.0, the anchor the selection uses. It is reported, not
deleted, and it was not eligible to be `best`.

## Beside the coded detectors — and this is NOT a ranking

Three reasons it cannot be read as one, and all three matter:

1. **The learned column is a selection score, not an unbiased estimate.** `best.json` is chosen as
   the highest mean F1 *among the same held-out seeds it is scored on*. The tool's own docstring
   says to state this wherever the number is quoted, and this is that statement.
2. **Different seeds.** The coded rows come from
   [the every-knob search](../2026-09-23-full-search-fast/README.md), which uses its own selection
   and held-out sets. Nothing here was scored on the same recordings as anything there.
3. **The coded rows are a search over settings**; these are a search over training seeds at one
   configuration. They answer different questions.

| | mean F1 on the adopted fast bench |
|---|---|
| `chorus_norm`, best of 5 seeds | **0.809** ⚠ selection score |
| `chorus_gain_norm`, best of 5 seeds | **0.801** ⚠ selection score |
| LoCo, shipped | 0.750 |
| CoactDetect, search pick | 0.754 |
| CoactDetect, shipped | 0.720 |
| SPIKE-synch, search pick | 0.699 |
| rate+context, search pick | 0.657 |
| locust, search pick | 0.667 |
| binned SCE, shipped | 0.474 |

A fairer within-model summary: **`chorus_gain_norm`'s five seeds span 0.739–0.801 and
`chorus_norm`'s 0.760–0.809**, so the *median* fit of either sits around 0.78–0.79 — above
CoactDetect's shipped 0.720 and about level with its searched 0.754, without needing the best-of-5
pick to make the point.

## Against the pre-jitter pilot

The 2026-09-21 pilot trained `chorus_norm` on the **old** fast bench and scored 0.739 / 0.692 /
0.720 across three seeds. The same model on the adopted bench scores 0.760 / 0.809 / 0.794 /
0.787 / 0.761.

**Read as a bench change, not a model improvement.** Nothing about the architecture or the
protocol moved; the bench did — jitter 0.36 → 0.106 s, quiet 0.0052 → 0.0042, busy 0.0190 →
0.0165. Events planted three times tighter are easier to recover, which is the expected direction.
The pilot's coded rows moved the same way (CoactDetect 0.708 then, 0.720 shipped now).

## ⚠ The calls/h column is measured on the OLD null

`bench.NULL_RECORDING` still carries `bg_rate_hz` **0.0052**, the pre-#756 quiet endpoint; quiet
is now **0.0042**. So every calls/h number above is measured on a no-coordination recording
slightly busier than the bench's own quiet end. **Not fixed here — it is Tony's call**, and it is
flagged rather than absorbed because it is a real inconsistency in the bench and because the
budget check (`chorus_norm` seed 3 at 9.44 against 7.0) rests on it.

## Real data, detection only

`bugarach detect` on the default export's fast stream — the `chorus_gain_norm` best checkpoint
beside CoactDetect at its shipped point — into the darkroom claim's `detect/`.
**No rasters drawn**: Tony reviews the tables first (his instruction).

Dataset: `2026-09-17_revised_2v_long_STEPS_AND_PINS_EXCLUDED`, confirmed by Tony this session.
84 recordings, 3,004 calls, 17.4 s.

| detector | calls | recordings with at least one |
|---|---|---|
| `chorus_gain_norm` (seed 1) | 1,812 | 79 of 84 |
| CoactDetect, shipped point | 1,192 | 78 of 84 |

**The learned model calls about 52% more often than CoactDetect** on the same recordings, and the
two agree closely on *where* there is anything to call — 79 recordings against 78. Nothing here
says which is right: there are no labels on this cohort, which is the whole reason the bench
exists. The bench says `chorus_gain_norm` scores above CoactDetect at a false-alarm rate inside
the same budget; whether that holds on real data is exactly what cannot be read off this table.

⚠ **Both columns are at settings chosen elsewhere.** CoactDetect is at its shipped point, which
[today's search](../2026-09-23-full-search-fast/README.md) proposes improving (+0.035 held-out),
and the learned model is the best-of-5 pick. A call-count comparison between two differently
chosen settings is a description, not a result.

## What this does not do

No operating point moves, no bench constant moves, and no model is adopted anywhere. `best.json`
exists so a later comparison has something to load, not because it has been chosen for anything.
