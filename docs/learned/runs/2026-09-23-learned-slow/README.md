# A learned detector on the CURRENT slow bench

**Run 2026-09-23 on WSMIP065**, on `main` at `a59ad4c`. Tony, 2026-09-23: set up the learned runs
immediately — **no learned model had been trained on the current slow bench, and slow had none at
all**, so its rasters carry no learned lane. 065 took slow; WSMIP064 took fast on its GPU.

Checkpoints and `best.json` are in `<darkroom>/bugarach/2026-09-23-learned-slow/models/`; the
repo holds each `summary.json`.

**On CPU, not the GPU.** This machine's `.venv` is torch 2.14.0+cpu (`cuda.is_available()` is
False) though the driver is current — about **5.5 minutes a fit** against the 21 September pilot's
**11–15 seconds** on the GPU. That gap is why WSMIP064 took fast.

Abbreviations: **F1**, the harmonic mean of recall and precision.

## `chorus_gain_norm`, five seeds, none collapsed

| seed | threshold | F1 quiet | F1 busy | mean F1 | calls/h on the no-coordination recording |
|---|---|---|---|---|---|
| 0 | 0.95 | 0.841 | 0.832 | 0.836 | 0.11 |
| 1 | 0.95 | 0.840 | 0.834 | 0.837 | 0.56 |
| 2 | 0.90 | 0.844 | 0.835 | 0.840 | 0.11 |
| **3** | 0.95 | 0.846 | 0.838 | **0.842** | **0.00** |
| 4 | 0.90 | 0.837 | 0.829 | 0.833 | 0.56 |

Best is **seed 3, mean F1 0.842**, at 0.00 calls/hour against a budget of 1.0. Every seed is
inside budget. Spread across seeds is **0.009** — the tightest of the three benches so far
(combined was 0.019). Roughly one fit in six collapses; **none did here**.

## ⚠ Rescored, not retrained

These fits ran **before** [#761](https://github.com/syncytium2/bugarach/pull/761) merged, which
corrected `bench_slow.NULL_RECORDING`: it had carried a stale literal 0.0030 Hz background while
`REGIMES` quiet had moved to 0.0024 with the adoption.

**The fits are unaffected** — training reads the main recordings and never the null one. Only the
calls/hour column depends on it, and that column decides which seed becomes `best.json` (the pick
is the best mean F1 among seeds inside the null budget). So the run was **rescored** on the
corrected recording by `tools/rescore_null_on_bench.py`, which reproduces the training tool's own
rule: the same null seeds 4000–4011 at the same `+50_000` offset, the same budget, the same
tie-break. That is equivalent to retraining — the checkpoints are byte-identical to what a retrain
would produce — and far cheaper.

**Four of the five values moved, and not by a constant:**

| seed | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| before | 0.22 | 0.33 | 0.11 | 0.11 | 0.33 |
| after | 0.11 | 0.56 | 0.11 | 0.00 | 0.56 |

Two went down, two went up. The corrected recording is a *different* draw, not a rescaled one, so
a seed's response to it moves either way. **The pick did not change** — seed 3 was and remains
best — and each row keeps its prior value as `null_per_hour_before_rescore`, with
`best_before_rescore` beside it, so the correction is auditable rather than silent.

## Beside the other slow numbers

⚠ **This is not a ranking, and the rows are not comparable.** They differ in more than seeds.

| | mean F1 (slow) | measured on |
|---|---|---|
| `chorus_gain_norm` seed 3 — **today** | **0.842** | the current bench |
| `chorus_norm` seeds 0/1/2 — 21 Sept pilot | 0.842 / 0.827 / 0.835 | **the pre-jitter bench** |
| `tube` seeds 0/1/2 — 21 Sept pilot | 0.843 / 0.842 / 0.836 | **the pre-jitter bench** |
| CoactDetect (hand-written, shipped) — today | 0.859 | the current bench, held-out seeds 49–96 |
| LoCo (hand-written, shipped) — today | 0.845 | the current bench, held-out seeds 49–96 |
| SPIKE-synch (hand-written, shipped) — today | 0.845 | the current bench, held-out seeds 49–96 |

**The pilot rows are a different instrument, not just different seeds.** Its slow bench had
jitter 0.30 s (now 0.135) and backgrounds 0.0030/0.0113 Hz (now 0.0024/0.0089). They sit here as
history, to show what existed before today, and nothing should be read across the rows.

The hand-written rows come from `2026-09-23-full-search-slow` and are scored on that search's
held-out seeds, which are not these seeds either.

⚠ One thing not to over-read: **CoactDetect reads 0.859 in both the pilot and today's search**,
identical to three figures across a bench change. Different seeds, different constants — almost
certainly coincidence, and not evidence that the bench change left the slow stream untouched.

## Real data: detection only

`bugarach detect --stream slow --detectors coact --model <best.json>` on the default folder, at
the slow settings from `2026-09-22-full-cohort-slow`.

**No rasters were drawn.** Tony reviews the tables first, and the slow raster with a learned lane
waits on him.
