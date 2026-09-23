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

## `chorus_norm`, five seeds, none collapsed — the pilot's variant

Run second so today's row is comparable in *architecture* with the 21 September pilot, which used
`chorus_norm`.

| seed | threshold | F1 quiet | F1 busy | mean F1 | calls/h |
|---|---|---|---|---|---|
| 0 | **0.0092** ⚠ | 0.846 | 0.831 | 0.839 | 0.33 |
| **1** | 0.984 | 0.846 | 0.842 | **0.844** | **0.00** |
| 2 | 0.900 | 0.843 | 0.844 | 0.844 | 0.00 |
| 3 | 0.650 | 0.842 | 0.837 | 0.840 | 0.11 |
| 4 | 0.972 | 0.842 | 0.842 | 0.842 | 0.00 |

Best is **seed 1, mean F1 0.844**, at 0.00 calls/hour. Spread **0.005**, tighter still than
`chorus_gain_norm`'s 0.009. Seeds 1 and 2 tie at 0.844 to three figures; seed 1 wins on ordering,
not on a margin.

⚠ **Seed 0's threshold is 0.0092**, where every other seed found 0.65–0.98. That is the same shape
as combined's seed 0 (0.800 against 0.97–0.997) and it is **not** a collapse: its mean F1 is 0.839,
mid-field, and its null rate 0.33/hour is inside budget. A threshold is relative to that fit's own
output scale, so a near-zero one means the scale differs, not that the model fires on everything.
Flagged rather than dropped, because a seed spread quoted in any comparison should be the spread
actually measured.

## The two variants

`chorus_norm` 0.844 against `chorus_gain_norm` 0.842 — **a 0.002 difference on seed spreads of
0.005 and 0.009.** These are not separable, and nothing should be read into which is higher. Both
are trained on identical data with identical protocol, so the comparison is fair in a way the
rows below are not; it simply does not resolve anything.

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

**Both runs were rescored. `chorus_gain_norm` moved four of five values, and not by a constant:**

| seed | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| before | 0.22 | 0.33 | 0.11 | 0.11 | 0.33 |
| after | **0.11** | **0.56** | 0.11 | **0.00** | **0.56** |

Two went down, two went up. `chorus_norm` moved only one (seed 3, 0.22 → 0.11) and the four seeds
already at 0.00 or 0.33 stayed put.

The corrected recording is a *different* draw, not a rescaled one, so a seed's response to it
moves either way — and a model already calling nothing on the old one goes on calling nothing.
**Neither pick changed**: seed 3 and seed 1 were and remain best. Each row keeps its prior value
as `null_per_hour_before_rescore`, with `best_before_rescore` beside it, so the correction is
auditable rather than silent.

## Beside the other slow numbers

⚠ **This is not a ranking, and the rows are not comparable.** They differ in more than seeds.

| | mean F1 (slow) | measured on |
|---|---|---|
| `chorus_norm` seed 1 — **today** | **0.844** | the current bench |
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

`bugarach detect --stream slow --detectors coact --model models/chorus_gain_norm/best.json` on the
default folder, at the slow settings from `2026-09-22-full-cohort-slow`. **4,573 calls** over the
84-recording cohort:

| | calls |
|---|---|
| `chorus_gain_norm` | **2,662** |
| CoactDetect | 1,911 |

**The learned model calls 39% more often than CoactDetect** on the same recordings. On the bench
the two are close — CoactDetect 0.859 against the model's 0.842 — so the gap is not a difference
in bench score showing through. What it is cannot be settled from here: the bench has ground truth
and these recordings do not, so a call is neither right nor wrong, only counted.

Two readings stay open, and the tables cannot separate them. Either the model finds slow events
CoactDetect's `min_rois` 6 floor excludes — which is what a learned detector is *for* — or it is
looser on real data than on simulation, which is the transfer question this project has asked of
every learned model and answered for none. **A raster would start to tell them apart**, which is
exactly why one was not drawn: it is Tony's to look at first.

**No rasters were drawn.** Tony reviews the tables first, and the slow raster with a learned lane
waits on him.
