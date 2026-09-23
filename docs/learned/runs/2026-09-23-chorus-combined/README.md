# chorus_gain_norm trained on the COMBINED bench

**Run 2026-09-22 evening on WSMIP065**, five seeds, about 6 minutes a fit.
`tools/train_learned_on_bench.py --bench combined --model chorus_gain_norm --seeds 0 1 2 3 4`.
Checkpoints and `best.json` are in `<darkroom>/bugarach/2026-09-23-full-cohort-combined/models/`;
only `summary.json` is in the repo, the checkpoints being bulk.

Tony, 2026-09-22: combined gets its own model, *"just like fast and slow"*. Until this run nothing
on `main` had trained a learned detector on a bench other than fast and kept it — the slow pilot
scored its fits and saved none.

Abbreviations: **F1**, the harmonic mean of recall and precision.

## Every seed trained, and none collapsed

| seed | threshold | F1 quiet | F1 busy | mean F1 | null calls/hour |
|---|---|---|---|---|---|
| 0 | 0.800 | 0.830 | 0.736 | 0.783 | **6.22** |
| 1 | 0.972 | 0.809 | 0.764 | 0.786 | 0.33 |
| **2** | 0.997 | 0.822 | 0.782 | **0.802** | 0.44 |
| 3 | 0.995 | 0.825 | 0.761 | 0.793 | 1.33 |
| 4 | 0.991 | 0.815 | 0.774 | 0.795 | 0.44 |

Best is **seed 2, mean F1 0.802**, at 0.44 calls/hour on the no-coordination recording against a
budget of 10. The five seeds exist because about one fit in six collapses; **none did here**, which
is worth saying plainly because it is a fact about this bench rather than about the architecture.

Spread across seeds is **0.019 F1** (0.783 to 0.802) — narrow, and narrower than the 0.063 the
CoactDetect search moved on the same bench.

## ⚠ Seed 0 is not a collapse, but it is not like the others either

Its threshold sits at **0.800** while every other seed found 0.97–0.997, and its null rate is
**6.22 calls/hour against their 0.33–1.33** — fourteen times the median of the rest, though still
inside the budget. A threshold at 0.8 with the others clustered near 1.0 looks like a fit that
stopped somewhere flat rather than one that failed. It is included above rather than dropped,
because the seed spread quoted in any comparison should be the one actually measured.

## What this does NOT say

**It does not say chorus beats CoactDetect on combined.** Chorus is scored here on fresh bench
seeds 4000–4023 per background; the CoactDetect search reports a held-out mean over its own
held-out seeds (`2026-09-23-full-search-combined-coact`). The two numbers — 0.802 and 0.781 — come
from different seed sets and different procedures, and putting them side by side as a ranking
would be the comparison this project refuses elsewhere. A fair comparison on combined is the
nested-CV run that goal 2 does on fast, and nobody has run it on this stream.

**Nothing here is adopted.** The checkpoint is a model for the cohort pass to draw a chorus lane
with; `bench_combined.OPERATING_POINTS` carries the CoactDetect search pick with a source string
saying it awaits Tony's review.

## Trained on CPU

This machine's `.venv` carries torch 2.14.0+**cpu** while its driver is current (RTX A4000,
582.78). At roughly 6 minutes a fit that is half an hour for five seeds, so no CUDA wheel was
installed for it. `docs/windows_workstation_setup.md` has the GPU-against-CPU table; the GPU
figure there is 568 fits an hour.
