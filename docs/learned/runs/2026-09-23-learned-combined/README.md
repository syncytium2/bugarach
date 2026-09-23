# `chorus_norm` on the combined bench — parity with fast and slow

Run 2026-09-23 on WSMIP064, on the GPU (RTX A4000). **Working material, not murderboarded.**

Tony, 2026-09-23: *"learned runs on combined too please."* Combined already had
`chorus_gain_norm` on its current bench (#754); what it lacked for parity with the fast and slow
runs was **`chorus_norm`**, the variant the 2026-09-21 pilot trained. This is that.

**Tool:** `tools/train_learned_on_bench.py --bench combined`, the same protocol as everywhere
else — fit on bench seeds 1000–1023 on both backgrounds, score on fresh 4000–4023, plus
calls/hour on the no-coordination recording.
**Checkpoints are in the darkroom**, `bugarach/2026-09-23-learned-combined/models/`; only
`summary.json` is here.

**Started after [#761](https://github.com/syncytium2/bugarach/pull/761)**, so the calls/h column
is on the corrected no-coordination recording from the start — `NULL_RECORDING` now follows
`REGIMES` quiet instead of a stale literal. **No rescore was needed for this run.**

Abbreviations: **F1**, the harmonic mean of recall and precision; **calls/h**, calls per hour on
the bench's no-coordination recording. Combined's anchor budget is **10/h**, not fast's 7.

## `chorus_norm`, combined bench, GPU

| seed | F1 quiet | F1 busy | mean | calls/h | threshold | |
|---|---|---|---|---|---|---|
| **0** | **0.835** | **0.799** | **0.817** | **1.89** | 0.9838 | **best** |
| 1 | 0.835 | 0.770 | 0.803 | 1.33 | 0.9838 | |
| 2 | 0.829 | 0.791 | 0.810 | 1.56 | 0.9908 | |
| 3 | 0.835 | 0.781 | 0.808 | 2.22 | 0.9716 | |
| 4 | 0.826 | 0.779 | 0.803 | 0.56 | 0.9908 | |

**No fit collapsed**, and every one is inside the budget.

**The spread is remarkably tight: 0.803 to 0.817, a span of 0.014** across five training seeds.
Compare the same model on fast, trained the same way on the same day: **0.760 to 0.809, a span of
0.049** — three and a half times wider. That echoes what the slow pilot found on its own bench
(everything within 0.032), and it is the same warning: **a bench where every fit lands in the same
place separates models less well**, so a comparison run here would be asked to resolve differences
smaller than the noise it can measure.

## Beside the existing combined `chorus_gain_norm`

From [#754's run](../2026-09-23-chorus-combined/README.md), same bench, same protocol, same
budget.

| | best | spread across 5 seeds | trained on |
|---|---|---|---|
| `chorus_norm` (this run) | **0.817** | 0.803 – 0.817 | **GPU** |
| `chorus_gain_norm` (#754) | 0.802 | 0.783 – 0.802 | **CPU** |

⚠ **These are not one series.** The existing rows were fitted on CPU and these on GPU, and the
arithmetic differs slightly — different accumulation order in the same operations, which is enough
to move a fit. The gap above (0.015 between the two bests) is **the same order as that difference
plus seed noise**, so it does not establish that either variant is better on this bench. Two
models trained on different hardware are a pair of measurements, not a comparison.

⚠ **Both bests are selection scores.** `best.json` is the highest mean F1 *among the same held-out
seeds it is scored on*, for both rows. The tool's docstring requires that statement wherever the
number is quoted.

## Against the other two streams, same model, same day

| bench | `chorus_norm` best | spread |
|---|---|---|
| combined | 0.817 | 0.803 – 0.817 |
| fast | 0.809 | 0.760 – 0.809 |
| slow (2026-09-21 pilot, pre-jitter bench) | 0.842 | 0.827 – 0.842 |

The slow column is on the **old** bench and is here for shape, not for level — the pilot ran
before the jitter and background constants moved. What travels across all three is the pattern:
**fast separates fits, combined and slow do not.**

## What this does not do

No operating point moves, no bench constant moves, and no model is adopted. `best.json` exists so
a later comparison has something to load. No rasters were drawn — Tony reviews the tables first.
