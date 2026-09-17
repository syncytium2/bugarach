GRANT 1 MISMATCH — missing Grep, Glob; holds no forbidden tools (Read, Bash only)

# Claim and data check: the slow co-modulation explainer, round 1

**Verdict:** the core measurement holds up. All 45 cells of the main table match summary.json. Re-running the measurement gives the same summary.json except the elapsed time, and re-drawing gives the same four figures pixel for pixel. The group, mouse and date counts match the export folder. But one factual claim, stated twice, is false, and the page's conclusions lean on it. Four claims about sources are wrong or overstated.

**About this run:**
- I am missing Grep and Glob, so I searched with `git grep` and `grep` through Bash. Nothing I needed to check went unchecked because of it.
- A repo hook blocks writing script files through a shell heredoc, and I have no Write tool. So my recomputation scripts ran inline with `python -c`. All scratch output is under `.../scratchpad/review/`.
- No recording identifiers or personal paths appear below.

## Findings

| # | location | issue | severity | suggested fix | verified against a source |
|---|---|---|---|---|---|
| 1 | Lines 55–57 (*"so no benchmark in this repository contains a shoulder"*) and 175–176 (*"no supervised model here has seen a shoulder or a dip"*) | **False.** The simulator's *background* is drawn per ROI, as the page says. But both benchmark definitions add a whole-field "promiscuity probe": `docs/learned/generator_spec.json` (loaded by `tools/tube_self_supervised.py` through `SPEC_PATH`) and `bench.BENCH_RECORDING`. The probe is `hot_window` 1200–1500 s: every ROI gets an extra 0.06 Hz for 300 s, ramping in over 30 s, on a 0.0097 Hz background. That is shared drift over minutes. I ran the page's own `pair_counts` on 24 benchmark recordings built from that spec. The shoulder reads **+1.2 flat from 1 s to about 1 minute**, +0.93 at 55–78 s, +0.80 at 78–109 s and +0.37 at 153–214 s. With only the probe removed, every bin from 0.96 s to 300 s reads −0.01 to +0.03. The benchmark's shoulder is about 15× the lab fast stream's (+0.07). The generator's own docstring says the probe and distractors are labelled negatives for training. | **blocking** | Say that the benchmark carries a 300 s whole-field rate block, and that it leaves a shoulder far larger than the recordings'. Say that supervised models and the simulated-recording label-free arm were trained on it. Then re-read the "What this changes" section against that. | yes (recomputed) |
| 2 | Lines 159–160, *"the lab fast stream — the stream every label-free model was trained on"* | `tools/tube_self_supervised.py` has an `ssl_sim` arm ("trained on the training folds' recordings, labels unread"). The branch summary.json has `ssl_sim` results for all five models at J 10 s and 20 s, and those recordings carry the probe block. The page inherits this from the tube report's line 377 ("Only the lab fast stream was used for the label-free work"), which the tool contradicts. | major | Write "every label-free model trained on *real* recordings", and name the simulated-recording arm and its shoulder. | yes |
| 3 | Lines 171–174: `count_excess` *"may be part of why it holds up against trained models"* | No report text says it holds up. The branch commit ef9fdc3 says the report text "is not yet rewritten". The only numbers are in the branch's `tube_self_supervised/summary.json`. There, `count_excess` scores label-free F1 0.31–0.48, against 0.07–0.39 for the label-free trained models. Those scores come from **simulated folds**, where the only shared drift is the probe block. So the proposed reason, cancelling drift over minutes, has to be argued through the probe, and the page currently says the benchmark has no drift. | major | Cite the summary.json cells and say they are simulated folds, or drop the sentence. | yes |
| 4 | Lines 134–136: *"their own refractory interval — the same-ROI floor the goal page records as 2.80–3.20 s"* | (a) The range blends two folders. The goal page gives 3.20 s for the senktide baselines and 2.80 s for the field-step-excluded folder. This page uses the second, so its floor is **2.80 s** (`proposals/2026-09-10-surrogate-evaluation-overnight.md`, line 79). (b) No source calls it refractory. The goal page and the GLOSSARY define τ as the extractor's dead time, the producer's number to declare. Calling it biology is a claim about the preparation, which the page's own FOUNDATIONS §9 paragraph says is not this repo's to decide. (c) A 2.80 s floor does not reach the dip's far edge: −0.53 at 3.7–5.2 s. | major | Write "the 2.80 s shortest same-ROI interval on this folder". Drop "refractory", or mark it as a question for the producer. | yes |
| 5 | Line 158, *"The goal page asks whether shared modulation on timescales of 10–45 s…"* | The goal page does not contain that question. It is in `docs/learned/tube_self_supervised/README.md` line 395 and in `todo/2026-09-16-land-pr-588…` line 103. | minor | Cite the tube report's "What waits on Tony" item. | yes |
| 6 | Lines 121–122: shoulder *"+0.05 to +0.09 … flat from about 3 s out to a minute"* | The page's own table has the 2.7–3.7 s bin at **+0.15 [+0.10, +0.25]**. The curve dips to +0.03 at 1.35–1.9 s, rises to +0.06, then peaks at +0.15, so there is a local bump near 3 s. The bump survives CoactDetect removal (+0.10) and rigid shift at 1.6 s (+0.12). The +0.05 to +0.09 range holds from 3.7 s to 78 s. | minor | Write "flat from about 4 s", and mention the bump near 3 s. | yes |
| 7 | Lines 125–127, *"the share at lags beyond 1 s"* | `peak_and_shoulder` splits on the bin's lower edge being under 1.0 s, so the 0.96–1.35 s bin counts as "under" and the real cut is 1.35 s. Recomputed with the cut at 0.96 s: fast 0.913, slow 0.711, Cossart 0.880, against 0.912, 0.706 and 0.863 as shipped. None of these shares carries an interval. | minor | Say the cut is 1.35 s, or change the code. | yes |
| 8 | Line 4, *"Numbers carry a 95 % interval from resampling mice"* | Several numbers carry none: the shares beyond the cut, the CoactDetect removal percentages, and the synthetic "about" values. | minor | Limit the sentence to the table and figure bands. | yes |
| 9 | Line 148, *"the shoulder is present in all four groups at a similar height"* | For OVX (fast, as recorded) the lower bound reaches −0.02 at 3.7–5.2 s, −0.01 at 20–28 s and 0.00 at 55–78 s, so "present" is not established. DI sits at about +0.10, against +0.04 to +0.07 for the other groups. | minor | Soften to "in every group's point estimate; OVX's interval reaches zero". | yes |
| 10 | Line 94, *"26.9 hours analysed"* | This is per stream (`analysed_hours` 26.88 for fast and again for slow, trimmed windows). The sentence names both streams, so it reads as a total. | minor | Write "26.9 hours per stream". | yes |
| 11 | Line 200, *"20 minutes of baseline per recording"* | Lab windows are 1,020–1,200 s (median 1,200 s). Cossart recordings are read whole, median about 1,490 s, range 1,164–1,552 s. | minor | Give each folder its own range. | yes |
| 12 | Lines 168–170: the rigid-shift session *"confirmed this independently … and is carrying it in that report"* | Commit 65285fa did measure it: `slow_modulation` tells an events-only synthetic recording from its 1.6 s shift at 0.669, and a shared-modulation-only recording at 0.522. But the commit message says a reviewing session argued it first, so "independently" cannot be checked. Commit ef9fdc3 says the report text is not yet rewritten, and the branch is unmerged. | minor | Cite the commit and its numbers. Write "is to carry it". | yes |
| 13 | Figure 1 caption, *"0.0097 onsets per ROI per second"* | That is the background rate only. The events world adds 32 events × 7 ROIs = 224 onsets to about 372 per recording, roughly 0.015 per ROI per second. | minor | Write "background of 0.0097 onsets per ROI per second". | yes |
| 14 | Generator docstrings (not the page), `tools/measure_slow_comodulation.py` | (a) Lines 93–96 say the synthetic worlds are sized to "CoactDetect's 2.70 events per 10 minutes". They plant 32 events in 1,200 s, which is 16 per 10 minutes. This run's lab-fast CoactDetect median is 1.0 per 10 minutes (the mean is 2.69). (b) Lines 31–32 and 72–74 say the block control removes "everything faster, events and minute-scale modulation alike". Its own output disagrees: it keeps 7,798 of the events world's 13,248 total excess pairs, as a flat +0.04 shoulder, and 22,269 of 22,808 in the 20 s world. (c) Line 10 says rigid shift at 10–20 s "removes both"; the page shows drift passes through. The page's ⚠ covers the 20 s world but not events: a flat block-control curve can come from events alone. | minor | Fix the docstrings. Add "events too" to the page's ⚠ about the block control. | yes |
| 15 | Line 93, the export folder | Not disclosed: the export removed every onset within ±2 s of 3 field steps that fall inside baseline analysis windows (`field_steps_excluded.tsv`). That leaves a 4 s gap across all ROIs in 3 recordings, about 12 s out of about 27 hours. The effect on the pooled curves is negligible, but it is a shared gap in the data. | minor | One clause in the limits. | yes |

## Claim ledger

| quoted value | cited source | recomputed value | result |
|---|---|---|---|
| All 45 table cells: 9 rows × 5 lag bins, with intervals | summary.json | same, bins 0, 8, 9, 14 and 17 | match |
| 84 recordings, 44 mice; 59 recordings, 32 mice; 26.9 h; 22.7 h; median 566 ROIs | summary.json | 84/44, 59/32, 26.88 h, 22.74 h, 566 | match (hours per stream, finding 10) |
| Group sizes 17/22/25/20 recordings from 10/12/12/10 mice | summary.json | same. Export `slices.csv`: 84 rows, no empty mouse, group or date | match |
| No imaging date holds more than one group | INDEX, `recording_identity.md` | `slices.csv`: 42 dates, none with two groups; no mouse in two groups | match |
| Withdrawn recordings, and recordings sharing a mouse | export folder (producer's rule) | 84 = `current_export.toml` = run; 0 skipped. Mice with 1/2/3 recordings: 9/30/5, handled by the bootstrap over mice. Cossart: 59 files = 59 recordings | match |
| Removing CoactDetect episodes: +2.06 → +0.95 ("halves"), +21.94 → +3.20 ("six-sevenths") | summary.json | ratios 0.46 and 0.146 | match |
| Onsets removed: median 2.5 % / mean 10 % (fast); 7.1 % / 22 % (slow) | summary.json | 2.47/10.36; 7.09/22.10 | match |
| Share of excess beyond 1 s: 0.91 / 0.71 / 0.86 | summary.json `peak_and_shoulder` | 0.912/0.706/0.863, but the cut is really 1.35 s | match with a caveat (finding 7) |
| Dip −0.55 and −0.53, gone after removal (+0.03, +0.10); rigid shift fills it to +0.36 to +0.57 | summary.json | same (J 10 s: 0.57, 0.52; J 20 s: 0.37, 0.36) | match |
| Rigid shift at 1.6 s: +2.06 → +0.45 | summary.json | +0.45 | match |
| Synthetic 20 s world +0.75; +0.5 at J 10 s; +0.35 at J 20 s; block control +0.15 | summary.json | 0.75, 0.50, 0.36, 0.15–0.18 | match |
| Events world at J 20 s: about +0.1 out to about 30 s | summary.json | +0.12 to 7 s, +0.08 at 14–20 s, +0.06 at 20–28 s, 0 from 40 s | match |
| 5-minute world: rigid-shift curves lie on the recorded curve | summary.json | within 0.05 at every bin | match |
| Controls read zero (independent ROIs, per-ROI modulation) | summary.json | within ±0.08 | match |
| "Spreads, does not delete" | summary.json | total excess pairs, events world: 13,248 real vs 12,429 / 13,125 / 16,194 under rigid shift | match |
| 32 ROIs, 1,200 s, 0.0097 Hz, 32 events × 7 ROIs, 0.3 s jitter, 20 s and 300 s timescales, 24 recordings | `SYN` in the generator; lab data | median 31.5 ROIs, median 1,200 s, lab-fast rate 0.00975 Hz | match (rate is background only, finding 13) |
| Axis thresholds ±1 (Figure 1) and ±0.5 (Figure 2 events panel); ±0.7 zoom (Figure 3); 10 s bins | figure tool | `linthresh` 1.0 and 0.5; `ylim` ±0.7; `bin_sec` 10 | match |
| Rigid shift "exactly as `tube_self_supervised.py`" | tool on main and on the branch | same function, imported, identical on both | match |
| CoactDetect needs at least three ROIs; slow settings 1 s / 120 s / α 10⁻⁶; fast settings = `bench.OPERATING_POINTS` | `coact.py`, `bench.py` | `min_rois=3`; docstring states the slow point; fast parameters identical | match |
| `count_excess` = share of lit ROIs minus its 30 s moving mean | branch GLOSSARY and tool | `BASELINE_BACKGROUND_FRAMES = 301` | match |
| `count_excess` "holds up against trained models" | none cited | branch summary.json, simulated folds only | unsupported as cited (finding 3) |
| "no benchmark … contains a shoulder" | `simulate.py` | +1.2 benchmark shoulder, from the probe | **mismatch** (finding 1) |
| "every label-free model trained on lab fast" | tube report | `ssl_sim` arm exists | **mismatch** (finding 2) |
| Floor 2.80–3.20 s, "refractory" | goal page | 2.80 s on this folder; the source calls it extractor dead time | **mismatch** (finding 4) |
| Goal page asks the 10–45 s question | goal page | it is in the tube report | **mismatch** (finding 5) |
| Seven tests, as described | test file | 7 tests, all pass | match |
| Run under two minutes on 6 workers | summary.json | 90.4 s; worker count not recorded | time matches, workers unverifiable |
| Four figures from this run; summary.json regenerates | results.json, generator | re-draw: 0 pixels differ in all four. Re-run: identical except `elapsed_sec` | match |

Files:
- `<worktree>/docs/learned/slow_comodulation/README.md` (the page)
- `<worktree>/docs/learned/generator_spec.json` (the probe block)
- `<worktree>/src/bugarach/bench.py` (the other benchmark definition, `BENCH_RECORDING`)
- `<worktree>/tools/measure_slow_comodulation.py` (docstrings in finding 14)
- `<scratchpad>/review/` (re-run output and re-drawn figures)
