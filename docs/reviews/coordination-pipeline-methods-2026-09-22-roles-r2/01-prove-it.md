# Role 1 — Prove It (round 2, blind pass, verbatim as returned)

GRANT 1 ok — Read, Grep, Glob, Bash, SubagentHandback

I edited nothing. All reads were read-only: the source .md at 464d995 in the methods worktree, the export folder 2026-09-17_revised_2v_long_STEPS_AND_PINS_EXCLUDED (opened directly by path; `dataset.resolve()` did not find it under that name), the darkroom run records, docs/learned/, and origin/tune-bench-comparison. I recomputed values with the repo .venv, running scripts from stdin; no files were written.

# Findings

| # | location (source .md line) | issue | severity | suggested fix | verified against a source |
|---|---|---|---|---|---|
| F1 | L235 "Only the parameters each detector declares were searched; minimum cells was not." Also L301 "minimum cells and detection mode were also searched" | False. The goal-1 search (sliding5/search.json `space`, which is bench.FULL_GRIDS) included `min_rois` for LoCo, CoactDetect and binned SCE, and `detection_mode` for rate+context, binned SCE and SPIKE-synch. search.log shows `sce.min_rois` extended 3→1.5→0.75→0.375 and `loco.min_rois` extended to 0.25. The comparison's meta.json says "the grids are goal 1's", so the word "also" at L301 describes a difference that does not exist. | major | Say that every parameter in bench.FULL_GRIDS was searched, including minimum cells and detection mode. Delete "minimum cells was not" and the "also" in L301. | yes |
| F2 | L381–382 "443 had zero width and 283 had a single cell" | These counts cover both streams. In the fast stream (this document's scope) calls_measured.csv has 308 zero-width calls and 185 single-cell calls. The >10 s counts in the same paragraph (25/23/10) and the 64.8 s maximum are fast-only and correct, so one paragraph mixes streams. | major | Replace with 308 and 185 (fast), or label the pair as both streams. | yes (recomputed) |
| F3 | L47–48 "one analysed recording has not been screened" | This repeats a claim the producer withdrew. The export's own note (current_export.toml) says 20260629_314 is "absent from the census" and "unexamined". The producer's answer of 2026-09-18 (darkroom 2026-09-18-pinned-rois-answer/README.md, "Corrected 2026-09-18, same day") says all three candidates, 20260629_314 included, were in the 85-slice per-ROI sweep, and 314 came back with no flagged ROI. What remains open is the sensitivity of a census that tests hand-selected ROIs only, plus a pixel-level test (pinned pixels vs ROI masks) that has not been run. 314 is TTX-first, so it is analysed. | major | Say that 20260629_314 was screened by the per-ROI census with no ROI flagged, but a whole-frame scan ranks it as a candidate and the pixel-level test has not been run. The producer should also fix the pointer note. | yes |
| F4 | L45–47 "8 inspected windows on 8 ROIs in 4 recordings … 56 fast events … in 3 recordings" | moco_pinned_excluded.tsv has 8 `pin_window` ids on 8 ROIs, all in 3 recordings (309: 16, 17; 312: 14, 16, 20; 316: 2, 6, 20). The census confirms 12 pinned ROIs in 4 recordings. The 4th recording, 20250926_235, contributed nothing: ROIs 23 and 25 were already removed as dead, and ROI 24 is silent. | major | For example: "12 ROIs in 4 recordings were confirmed pinned; all events inside the windows on 8 ROIs in 3 recordings were removed (83 events, 56 fast, all in baseline); the 4th recording's pinned ROIs had already been removed or were silent." | yes |
| F5 | L317–319 vs L346 "Its merge gap is 2 s" | The merge-gap re-selection chose 8 s for this very model. In replicate_net_merge_gap.json, chorus_gain_norm (the cell-set network with gain) in the gated selection, outer fold 0, has `config_kept.gap_sec` = 8.0. The recorded-data run used the checkpoint as run: `merge_gap_frames` 20, i.e. 2 s. The text states both facts and does not reconcile them, so a reader will assume the re-selected gap was applied. The 26-of-32 count is correct (first draw, and the replicate's `config_kept`). | major | State that the detector run on recorded data used the as-run 2 s gap, not its re-selected 8 s. Either justify that or re-run at 8 s. | yes |
| F6 | L244–246, locust's proposed change | Incomplete. The search moved three locust parameters: percentile 99.999→99.99 (round 1), minimum distance 4→128 (round 1, at the extension limit) and synchronous frames 1→2 (round 2). The held-out gain was +0.119 (0.108–0.132). The text names only the minimum distance. | minor | List all three changes. | yes |
| F7 | L243 "lost 0.041 and 0.042 F1" | Against sliding mode at the default values, the crowded (close-events) mean F1 fell 0.8585→0.8185 for CoactDetect (−0.040) and 0.8688→0.8269 for LoCo (−0.042). 0.041 is LoCo's pair candidate, not the adopted setting. | minor | Write "0.040 and 0.042". | yes |
| F8 | L74–76 and L103 "re-measured on the baseline analysis windows of the 84 recordings" | Five of the eight constants were measured on 80 recordings: the three shapes and both rates (bench_measured.json `recordings_in_shape_fits` 80; tool floors ≥300 s, ≥20 events, ≥5 ROIs). Without that filter the 25th/75th percentiles over all 84 are 0.0036/0.0186, not 0.0050/0.0190. | minor | State that shapes and rates use the 80 recordings that pass the fit floors. | yes (reproduced 0.00505/0.01904 on 80, identical in both folders) |
| F9 | L81–83 "120 s apart plus an exponentially distributed excess … mean 133 s, 5th–95th percentile 121–164 s, over 20 recordings" | Reproduces only for quiet seeds 1–20 (133.1 s, 121–164 s), and only after dropping the one interval per recording that straddles the elevated-rate block. With it included the mean is 172 s and the 95th percentile 664 s. Across the block, the spacing is not "120 s plus an exponential excess": events are kept 120 s clear of the block on each side, so that interval is about 540 s longer. | minor | Name the 20 recordings and say the interval spanning the block is excluded. | yes (recomputed) |
| F10 | L145–146 "its threshold, in events s⁻¹, depends on the number of cells" | The code uses a fixed 4.5 events s⁻¹ whatever the cell count. As written the sentence says the threshold is a function of cell count. | minor | For example: "a fixed threshold … whose stringency therefore varies with the number of cells". | yes |
| F11 | L128–130, no-coordination recordings "use the benchmark seeds of the recordings they accompany" | True for the goal-1 search (`false_positives_per_hour(seeds=(s,))`, same seed, identical background). Not true in the comparison: both meta.json files declare `null_quiet` at seed + 100000, so the backgrounds differ there. | minor | Qualify for the comparison section. | yes |
| F12 | L320–322 "LoCo, rate+context and SPIKE-synch failed it in every fold … under the false-alarm rule" | True. It leaves out that binned SCE also failed in every fold of both draws under the F1-alone rule (4 of 4 per draw). | minor | Add it. | yes |
| F13 | L18 "(127 rows)" | 127 is both streams; the fast stream has 87. | minor | Say "127 rows over both streams (87 fast)". | yes |
| F14 | L57 treatment window rule | The 60 high K+ periods have windows equal to the whole period, with no 2 min delay. Only the analysed treatments follow the stated rule. | minor | Restrict the rule to non-high-K+ treatments, or note the exception. | yes |
| F15 | L183–184, agreement with PySpike and "PySpike's cap has had no effect since version 0.8.0" | The PySpike check is a summed-coincidence identity, not a per-spike profile compared at 1e-9 (the cSPIKE comparison is per spike at τ 0.25 and is correct). The repo's own PR text says the cap still applies as the default for edge intervals. docs/sapper_feedback says the cap was "fixed upstream in #89"; the README only says the fix was "filed". Neither is verifiable offline. | minor | "has had no effect on interior spikes since 0.8.0"; describe the PySpike check as an identity check. | partly |
| F16 | L380–382 "Across all calls" | calls_measured.csv covers the six coded detectors only; the learned detector's calls were not measured. | minor | Say "across the coded detectors' calls". | yes |
| F17 | L353, Table 1: units sharing a subject | 67 recordings come from 36 mice, and every mouse is in exactly one group. The section never says whether recordings from the same mouse are treated as independent, although the outputs carry `subject_id`. | minor (major if a group statistic is reported downstream) | State the unit of analysis. | yes (counts) |
| F18 | L49–50 "66 ROIs … from 15 recordings (18 recordings were not evaluated)" | PROVENANCE.md gives these numbers over the 85 archive recordings, which include the one withdrawn. The split over the 84 exported recordings cannot be derived from the folder. | minor | Say "of the 85 archive recordings", or ask the producer. | no |

# Claim ledger

## Dataset and exclusions (export folder, PROVENANCE.md, manifests)

| quoted | checked against | found | verdict |
|---|---|---|---|
| frame interval 0.1 s | slices.csv | 0.1 s in all 84 | match |
| 84 recordings, 2,630 ROIs, 168,755 fast events, 44 mice | event CSVs | same | match |
| 127 rows without a time | event CSVs | 127 (87 fast) | match (F13) |
| fast width rounded to the frame; slow width = peak − t50rise | event CSVs | fast widths all on the 0.1 s grid; slow width = peak − t50rise exactly | match |
| Table 1 mice, recordings, TTX-first, senktide-first per group | slices.csv, regions.csv | DI 10/17/11/6, MALE 12/22/9/5, ORX 12/25/9/10, OVX 10/20/9/8, all 44/84/38/29 | match |
| 67 analysed from 36 mice; SB222200 first 12; no treatment 5 | slices.csv, regions.csv | same | match |
| 9 steps, 187 fast events in 9 recordings | field_steps_excluded.tsv | same | match |
| 56 fast pinned events, all baseline, 3 recordings | moco_pinned_excluded.tsv | same | match |
| 8 windows on 8 ROIs in 4 recordings | moco_pinned_excluded.tsv | 3 recordings | mismatch (F4) |
| two sub-cut recordings kept | producer's answer | 338 and 325 kept | match |
| one analysed recording unscreened | producer's corrected answer | 314 was screened; no ROI flagged | retracted (F3) |
| 2 trailing periods under 240 s dropped; 1 recording withdrawn | PROVENANCE.md | same | match |
| 66 dead ROIs / 15 recordings / 18 not evaluated | PROVENANCE.md | counted over 85 archive recordings | unverifiable (F18) |
| baseline window rule | regions.csv | 0 violations | match |
| treatment window rule | regions.csv | holds except 60 high K+ periods | partial (F14) |
| baseline windows 17–20 min; first treatment 13.0–20 min | regions.csv | same | match |

## Benchmark generator (bench.py, simulate.py, recomputed)

| quoted | checked against | found | verdict |
|---|---|---|---|
| 2,700 s, 33 cells | bench.py | same | match |
| gamma rate shape 0.275; bursts 1.547 / 1.388 at 300 / 60 s | bench.py | same | match |
| Poisson within bins; 0.1 s grid | simulate.py | same | match |
| quiet 0.0052, busy 0.0190 | bench.py | same | match |
| 15 planted events, 5 per level, 10/6/3 cells | bench.py, simulate.py | same | match |
| jitter 0.36 s | bench.py | same | match |
| interval statistics 133 s, 121–164 s | recomputed | only with block interval excluded | match with caveat (F9) |
| distractors: 6 × 6 cells, 120–1,100 s, same jitter | simulate.py | same | match |
| precision 15/21, F1 0.83 | arithmetic | 0.714 and 0.833 | match |
| block 1,200–1,500 s at 0.06 s⁻¹, 30 s ramp | bench.py | same | match |
| no planted event within 120 s of the block | recomputed | nearest 130 s | match |
| widths: median 0.9 s, IQR 0.6–1.2 s | MEASURED_WIDTH_QUANTILES; recomputed on the current folder | same | match |
| Figure 1 is quiet background, seed 1 | make_methods_bench_figure.py | same | match |

## Table 2 (docs/learned/bench_measured.json)

| quoted | checked against | found | verdict |
|---|---|---|---|
| all eight re-measured values and intervals | bench_measured.json | same | match |
| 200 bootstrap resamples | bench_measured.json | same | match |
| only participation lies outside its interval | bench_measured.json | same | match |
| 0.18 and 0.190 both give 6 of 33 cells | arithmetic | 5.94 and 6.27 both round to 6 | match |
| "84 recordings" | bench_measured.json | 80 for shapes and rates | mismatch (F8) |
| after pin removal, five values unchanged | recomputed | rates unchanged | match (rates only) |
| three shapes moved by at most 0.8% | — | not re-run | unverifiable |
| 81 and 85 windows in the "set from" column | bench.py docstrings | same | match |

## Test recordings and scoring

| quoted | checked against | found | verdict |
|---|---|---|---|
| close-events recording: 10,800 s, 180 events, ≥6 s apart, 12 seeds | TAIL_RECORDING, N_TAIL | same | match |
| 39 recordings, 7 above 0.38, gaps 6–26 s, ≥3 calls, 30 s crowding | probe_real_crowding.py and its docstring | same | match |
| match distance 2.5 s | score.py | same | match |
| interval-based matching, nominal time | score.py | same | match |
| one-to-one, closest pair first | score.py | same | match |
| elevated-block calls excluded from precision | score.py, bench.py | same | match |
| rate+context widened 0.5 s | rate.py | same | match |
| binned SCE scored over its bin | score.py (extent_sec) | same | match |

## Admissibility and search

| quoted | checked against | found | verdict |
|---|---|---|---|
| Table 3 limits | bench.py | all 18 values | match |
| close-events drop 0.02 against the binned default | bench.py, search.json | same | match |
| search: 0.002 threshold, 4 rounds, 3 extensions, rescue from an inadmissible start, context ≤ 120 s | search_all_settings.py | same | match |
| two-parameter pairs | bench.FULL_GRID_PAIRS | same | match |
| seeds 1–48 / 49–96; 400 bootstrap; 12 tail seeds | search.json, tool | same | match |
| minimum cells not searched | search.json, search.log | searched | mismatch (F1) |
| CoactDetect held-out gain 0.034 (0.025–0.044) | search.json | same | match |
| LoCo held-out gain 0.016 (0.007–0.026) | search.json | same | match |
| close-events losses 0.041 / 0.042 | search.json | 0.040 / 0.042 | mismatch (F7) |
| gains over binned defaults | search.json | 0.818 > 0.808; 0.827 > 0.816 | match |
| SPIKE-synch minimum events 3→2; rate+context merge gap 3→8 s | search.json | same | match |
| locust minimum distance 4→128 at the extension limit | search.json | same | match, incomplete (F6) |
| binned SCE did not move | search.json | same | match |

## Detector descriptions and Table 4

| quoted | checked against | found | verdict |
|---|---|---|---|
| Table 4, all six rows | full-cohort detector_settings.csv and signature defaults | same | match |
| α 10⁻⁵ gives z ≥ 4.26 | computed | 4.265 | match |
| CoactDetect sliding: guard supported; exact null mean and variance | coact.py, sliding.py | same | match |
| SPIKE-synch hysteresis scan | sync.py | same | match |
| profile binned at 0.1 s | sync.py | same | match |
| cSPIKE agreement to 1e-9 at τ 0.25 | fixture and test | same | match |
| PySpike agreement | test | identity check only | partial (F15) |
| rate+context threshold depends on cell count | rate.py | fixed | mismatch (F10) |

## Learned detectors

| quoted | checked against | found | verdict |
|---|---|---|---|
| parameter counts 1,149–1,905 (defaults) and 1,122–4,565 (searched) | recomputed from all configs | same | match |
| threshold grid: 41 values, 10⁻⁴ to 0.9999 | train.THRESHOLD_GRID | same | match |
| Adam; positive weight = negative/positive frames; 4,096-frame crops, half centred on events | train.py | same | match |
| 10 training recordings plus 2 threshold recordings | checkpoint | same | match |
| frames labelled first to last participant; distractors negative | encode.py | same | match |
| rows ordered busiest first | encode.py | same | match |

## Comparison and separability

| quoted | checked against | found | verdict |
|---|---|---|---|
| seeds 1000–1047 and 2000–2047; 4 × 12; 72 tuning recordings | meta.json | same | match |
| 24 configurations (23 random + default); 3 tuning seeds; 5 refits | meta.json, tool | same | match |
| factor 1.6 with a floor of one false alarm | tool, checkpoint note | same | match |
| grids not extended; context rule kept | meta.json hand_search | same | match |
| merge gaps 0–30 s; 8 s in 26 of 32 | net_merge_gap.json | same | match |
| 19 of 48 and 16 of 48 | crowded_check.json | same | match |
| 3.182; √(3/7) = 0.655 (nb_factor 0.6547); about 0.31 | computed, json | same | match |

## Recorded-data run

| quoted | checked against | found | verdict |
|---|---|---|---|
| surrogate seed 20260706 | run.json | same | match |
| learned detector: cell-set network with gain (chorus_gain_norm), gated, fold 0, default configuration | checkpoint, results.json | same | match |
| refit used is the upper middle of 20, F1 0.726 | results.json | seed 2, 0.7263 | match |
| threshold 0.972; own threshold 0.95 | checkpoint, fits.zip | same | match |
| merge gap 2 s | checkpoint (20 frames) | same | match as run, but see F5 |
| detector families run per window vs whole recording | detect_folder.py | same | match |

## Width and amplitude

| quoted | checked against | found | verdict |
|---|---|---|---|
| ±1 s around the centre, or the whole call; 0.5 s split | call_measure.py; gap_sec and half_aperture_sec for fast | same | match |
| group choice and tie-breaks; amplitude floored at 0.1 s; undefined for a single cell | call_measure.py | same | match |
| widths >10 s: 25 / 23 / 10 | calls_measured.csv (fast, core span) | same | match |
| widest 64.8 s, 37 cells, 1,046 events | calls_measured.csv | same | match |
| 443 zero-width, 283 single-cell | calls_measured.csv | both streams; fast is 308 / 185 | mismatch (F2) |

Minor items I checked by source name only, without recomputing: "coincidence clusters in the same 1 s bin" (K = 4 confirmed, bin width not checked); locust parity under per-event widths; how the null is built for LoCo's symmetric context. Attributions (Finn and Johnson, Cossart, Kreuz, and others) belong to role 2 and are not checked here. No private correspondence is quoted in this report.

# Paths
- Artifact: docs\methods\coordination_pipeline_methods.md
- Export: `<data>\exports\bugarach\2026-09-17_revised_2v_long_STEPS_AND_PINS_EXCLUDED\` (PROVENANCE.md, moco_pinned_excluded.tsv, field_steps_excluded.tsv)
- Producer's corrected answer: `<darkroom>\2026-09-18-pinned-rois-answer\README.md`
- Search record: `<darkroom>\2026-09-17-full-search\sliding5\search.json` and search.log
- Recorded-data run: `<darkroom>\2026-09-21-full-cohort-default\detect\calls_measured.csv`, detect_coact_and_chorus\run.json
- Comparison: docs\learned\tuned_vs_coact\ (replicate1\results.json, both crowded_check.json, fair_comparison_2026_09_18\replicate_net_merge_gap.json)
- docs\learned\bench_measured.json

---
*Transcription note: personal absolute paths were replaced with placeholders (sapper SAP004); nothing else was altered.*
