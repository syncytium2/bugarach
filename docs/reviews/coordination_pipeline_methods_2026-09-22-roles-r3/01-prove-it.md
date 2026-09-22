# Role 1 — Prove It (round 3, blind pass, verbatim as returned)

GRANT 1 ok — Read, Grep, Glob, Bash

(I also hold SubagentHandback, which is only the hand-off channel. I hold no editing tools and modified no file.)

# Role 1, Prove It: blind pass on the methods section, round 3

**What I checked:** `docs\methods\coordination_pipeline_methods.md` at ee7bd62. I recomputed its numbers against:
- the default export `2026-09-17_revised_2v_long_STEPS_AND_PINS_EXCLUDED`: slices.csv, regions.csv, the 84 recording CSVs, both .tsv manifests, PROVENANCE.md and READ_ME_FIRST_pinning.md;
- `current_export.toml`;
- the run records: `2026-09-17-full-search/sliding5/search.json` and `search.log`, the `note.md` beside them, `2026-09-21-full-cohort-default/detect/` (run.json, calls_measured.csv, detector_settings.csv) and `detect_coact_and_chorus/run.json`;
- `2026-09-18-replicate-run-status/results/`, and in the repo `docs/learned/tuned_vs_coact/{fair_comparison_2026_09_18,replicate1}/` and `docs/learned/bench_measured.json`;
- the code: bench.py, simulate.py, score.py, loco.py, learn/train.py, remeasure_bench.py, fit_background_shape.py, search_all_settings.py, the tuning tool on origin/tune-bench-comparison, and the parity tests.

**The design record** (which unit is in which group, which recordings share a mouse, which were withdrawn) is `slices.csv` (group_id, mouse_id), `regions.csv` and PROVENANCE. The record reconciles:
- 85 recordings in the archive, minus the one withdrawn (`20250731_149`), gives 84.
- 67 recordings come from 36 mice. The text says the statistics on shared mice are out of scope.
- No withdrawn recording is present.

Most claims recompute exactly. Three do not hold as written, all major. None is blocking.

## Findings

| # | location | issue | severity | suggested fix | verified |
|---|---|---|---|---|---|
| 1 | l.104–105, elevated-rate block | "1.6 times the senktide rate, busier than any recorded condition" is copied from a bench.py:786 docstring written when baseline measured 0.0096 per cell. On the default export, fast-stream events s⁻¹ per cell: first-senktide windows have median 0.0334 (0.06 is 1.8× that) and mean 0.0468 (1.28×); all 35 senktide windows have median 0.0275 (2.2×). **28 analysis windows in 18 recordings are busier than 0.06**: 9 first-senktide, 2 later senktide, 3 baseline, 1 TTX and 13 high-K⁺. The busiest is 0.179. "Busier than any recorded condition" is true only of condition medians. | major | "about 6 times the median baseline rate and 1.8 times the median first-senktide rate. 28 of the 238 recorded analysis windows, including 9 first-senktide and 3 baseline windows, are busier." Or say plainly that the comparison is at condition medians. | yes |
| 2 | l.85–87 and l.122–123, quiet/busy rates | 0.0052 and 0.0190 are percentiles over only **80** recordings: those with at least 20 baseline events and at least 5 ROIs (fit_background_shape floors). Over all 84, p25 is 0.0036 and p75 is 0.0186. The 4 excluded recordings are the **quietest** (2, 4, 6 and 19 baseline events: 20240723_22, 20241002_72, 20260225_280, 20250826_190), so the quiet end sits higher than the stated definition gives. The reason given at l.123, "which need enough baseline to fit", is wrong: every baseline window is 17–20 min long. They fail on event count, not duration. | major | At l.86: "…per-cell rate, over the 80 recordings with at least 20 baseline events". At l.123: "80 … with at least 20 baseline events and 5 ROIs". Optionally add that p25 over all 84 is 0.0036. | yes (reproduced 0.005045 and 0.019035 on the 80) |
| 3 | l.51–52, pinning | "Two recordings with pinning below the screening cut were kept" is incomplete against the source of record. The `current_export.toml` note for this folder names a third recording, **20260629_314**: it is absent from the pinning census, the pinning detector has never been run on it, and a whole-frame scan ranks it beside the known four. The producer's 2026-09-18 answer also lists 20250926_237 and 20260630_325 as candidates "under open challenge". All three are in the 67 first-treatment recordings (TTX, senktide and TTX first respectively), all are DI (diestrus females), and each is the other recording of a mouse that already has a pinned one. | major | Add: "One further recording (20260629_314) has not been screened by the pinning detector, and two more are candidates in the producer's own open review." Whether this triggers the contamination stop is a call for the main thread. | yes |
| 4 | Table 4, LoCo "threshold update step – 15 s" | In sliding mode, the mode used, `thr_step_sec` does not apply (loco.py:621: "thr_step_sec and n_surrogates do not apply"). The CSV carries it, but it has no effect. | minor | Drop the row or mark it "binned mode only". | yes |
| 5 | Table 4 grids | CoactDetect and LoCo list "detection mode: threshold, peak". The sliding5 search, the source of their adopted values, did not search detection mode or peak parameters for those two (search.json `space`). Only the nested-CV search did (meta `hand_axes` = FULL_GRIDS). rate+context's `threshold_alpha` grid (1.5–4, multiplicative form) was searched and is not listed. | minor | Footnote which search each grid applies to, and add threshold_alpha. | yes |
| 6 | l.17–18, "Rows without a time mark ROIs that had no events (87 rows)" | 87 is correct, but 4 of them exist because the pinning removal emptied the ROI (the 2026-09-03 folder has 83). | minor | "…ROIs with no events after the exclusions below (87 rows in the fast stream, 4 of them emptied by the pinning removal)". | yes |
| 7 | l.473–476, width tallies | 25/23/10 calls over 10 s, 64.8 s, 37 cells, 1,046 events, 308 zero-width and 185 single-cell all recompute exactly. But they pool calls from **every period**: senktide 7,104 calls, high K⁺ 3,986, baseline 3,682, plus TTX, wash and SB222200. That is not only baseline and first treatment. The 157 calls whose search span is empty, and the 342 calls with undefined amplitude, are not reported. | minor | "Among the coded detectors' fast calls over all periods…" and add the 157 empty-span calls. | yes |
| 8 | l.26 against l.29–30 | "Each recording has a baseline followed by one or more drug treatments" contradicts "5 had no treatment". Those 5 have a baseline period only. | minor | "Most recordings have…", or "one or more periods". | yes |
| 9 | l.149, close-events test "whether a detector fuses separate events" | The code's own statement of purpose (bench.py, CROWDED_RECORDING and TAIL_RECORDING) is reference-window contamination, meaning neighbours inside the null, as much as fusing. "Fuses" names half the mechanism. | minor | "whether a detector misses or fuses events that are close together". | yes (source text) |
| 10 | Table 2 caption | The re-measured column is the 2026-09-03 steps-excluded folder, as disclosed. On the default folder I recomputed rate shape 0.2667 (−0.78%), burst shapes 1.8001 and 1.5164 (+0.04% each), and both rates unchanged. That confirms "at most 0.8%" and two of the "five values unchanged". I did not recompute n_roi, jitter or participation after the pin removal (1,000-surrogate assessment). | observation | none | partial |

## Claim ledger (quoted · source · recomputed · verdict)

**Data**
| quoted | source | recomputed | verdict |
|---|---|---|---|
| frame interval 0.1 s, every recording | slices.csv | all 0.1 | match |
| 87 fast NA rows | recording CSVs | 87 | match (see F6) |
| fast widths rounded to the frame | recording CSVs | 0 of 168,755 off-grid | match |
| 84 recordings, 2,630 ROIs, 168,755 fast events, 44 mice | slices.csv, CSVs | 84, 2,630, 168,755, 44 | match |
| Table 1, every cell (10/17/11/6, 12/22/9/5, 12/25/9/10, 10/20/9/8; all 44/84/38/29) | slices.csv + regions.csv | identical | match |
| 67 recordings from 36 mice; 12 SB222200-first; 5 untreated | regions.csv | 67, 36, 12, 5 | match |
| field steps: 187 fast events, 9 recordings, 9 steps, ±2 s | field_steps_excluded.tsv | 187, 9, 9 | match |
| pinning: 12 ROIs in 4 recordings; 8 ROIs in 3 recordings; 56 fast events, all baseline; 4th contributed 0; 2 below cut kept | moco_pinned_excluded.tsv, pinned-rois answer | 56, 8 ROIs, 3 slices, all baseline; 2 below cut | match, but incomplete (F3) |
| 85 archive, 66 ROIs from 15, 18 unassessed, 2 trailing periods under 240 s, 1 withdrawn | PROVENANCE | same | match |
| baseline window = last 20 min, 17–20 min | regions.csv | 84 of 84 follow the rule; 17.0–20.0 | match |
| treatment window 2 min delay, 20 min cap, 13.0–20 min, at least 12 min for all 67 | regions.csv; docs/conditioned_run.md:75 | lag 120 s; 13.0–20.0; 67 of 67 | match |
| high K⁺ uses the whole period | regions.csv | 60 of 60 | match |
| cells per recording 9–61 | CSVs | 9–61 | match |

**Benchmark generator**
| quoted | source | recomputed | verdict |
|---|---|---|---|
| 2,700 s, 33 cells, 15 events 5/5/5 at 10/6/3 cells, jitter 0.36, spacing ≥120 s, exponential excess, rescaling | bench.py, simulate.py | same | match |
| interval mean 133 s, 5th–95th 121–164 s (quiet seeds 1–20) | make_recording | 133.07, 120.6–163.5 | match |
| distractors: 6 × 6 cells, 120–1,100 s | bench.py | same | match |
| block 1,200–1,500 s, 0.06 s⁻¹, 30 s ramp; nearest planted event >120 s from block | generator | min 132.7 s | match |
| 0.06 ≈ 6× baseline | export | 6.2× median | match |
| 0.06 = 1.6× senktide; busier than any condition | export | 1.8×; 28 windows busier | **mismatch (F1)** |
| rate shape 0.275; burst shapes 1.547 / 1.388 | bench.py | same; 81 and 85 windows | match |
| quiet 0.0052, busy 0.0190 as p25/p75 of per-recording baseline rate | export | 0.00505 / 0.01904 on 80; 0.0036 / 0.0186 on 84 | **definition mismatch (F2)** |
| width median 0.9 s, IQR 0.6–1.2 s | export | 0.9, 0.6–1.2 | match |
| Table 2, all 8 rows (measured value and interval) | bench_measured.json | identical; reproduced on 09-03 folder | match |
| participation 0.18 and 0.190 both give 6 of 33 cells | arithmetic | 5.94 and 6.27 round to 6 | match |
| cluster gather window 1.5 s | assess.py (wm_factor 1.5 × 1 s bin) | 1.5 s | match |

**Tests and scoring**
| quoted | source | recomputed | verdict |
|---|---|---|---|
| close-events recording: 10,800 s, 180 events, 6 s floor, no distractors or block | TAIL_RECORDING | same | match |
| 7 of 39, 0.38, gaps 6–26 s, at least 3 calls | bench.py docstring, probe_real_crowding.py | docstring only | unverifiable (not re-run) |
| null recording shares its benchmark recording's background | generator | 383 of 384 events shared (seed 5) | match |
| null uses seed + 100,000 in the comparison | meta.json | same | match |
| tolerance 2.5 s, one-to-one closest first, precision excludes block | score.py, bench.py | same | match |
| 15/21 gives F1 0.83 | arithmetic | 0.833 | match |
| Table 3, every limit | bench.py MAX_* | identical | match |
| z = 4.26 at α = 10⁻⁵ | scipy | 4.2649 | match |

**Coded-detector search (sliding5)**
| quoted | source | recomputed | verdict |
|---|---|---|---|
| rule 0.002 F1, 3 extensions, 4 rounds, 400 resamples, 12 close-events seeds per background, seeds 1–48 / 49–96 | search_all_settings.py, search.json | same | match |
| CoactDetect gain 0.034 (0.025–0.044); LoCo gain 0.016 (0.007–0.026) | search.json held_out | 0.0340 (0.0248–0.0442); 0.0164 (0.0068–0.0259) | match |
| close-events losses 0.040 / 0.042; limits passed against binned defaults | search.json | −0.0400 / −0.0419; 0.8185 ≥ 0.788, 0.827 ≥ 0.796 | match |
| locust 99.999→99.99, 1→2 frames, 4→128 frames at the extension cap; SPIKE-synch 3→2; rate+context 3→8 s; binned SCE did not move | search.log, search.json | same | match |
| retuned defaults: SCE 99→98, rate+context 5.0→4.5, LoCo 99.9→99.5 | bench.py sources | same | match |
| Table 4 values | recorded_data_detector_settings.csv | identical to the run's detector_settings.csv | match |
| Table 4 grids | search.json space, meta hand_axes | match except F5 | minor mismatch |
| Table 4, LoCo update step 15 s | loco.py | has no effect in sliding mode | **mismatch (F4)** |

**Learned detectors and the comparison**
| quoted | source | recomputed | verdict |
|---|---|---|---|
| weights 1,149–1,905 (defaults) and 1,122–4,565 (searched) | built from every config | same | match |
| threshold grid: 41 values, 12 / steps of 0.05 / 12 | train.THRESHOLD_GRID | same | match |
| Adam; 3 crops of 4,096 frames; 10 training recordings; lr and steps grids | checkpoint, meta | same | match |
| 24 configurations (23 + default); 3 tuning seeds; 5 refit seeds | tuning tool, meta | same | match |
| seeds 1000–1047 and 2000–2047, 4 folds of 12 | meta.json | same | match |
| budget 1.6×, or one call over the test's duration | tuning tool | max(1.6·v, 1/h) | match |
| √(3/7) = 0.655; about 0.31 for a refit on 10; 3.182 critical value | nb_factor, leaderboard.py | 0.6547, 0.307, 3.182 | match |
| learned merge gap 8 s in 26 of 32 cases | net_merge_gap.json | 26 | match |
| close-events 19 of 48 and 16 of 48; LoCo, rate+context, SPIKE-synch every fold under false-alarm rule; SCE every fold under F1 alone | crowded_check.json, both draws | same | match |

**Recorded-data run**
| quoted | source | recomputed | verdict |
|---|---|---|---|
| model used: outer fold 0, seed 2, upper-median F1 0.726, default config, threshold 0.972 (own threshold 0.95), 2 s merge gap, 8 s re-selected | results.json, checkpoint, replicate_net_merge_gap.json | 0.7263 (11th of 20), eefc… = untuned, 0.97158, index 29 = 0.95, merge_gap_frames 20, 8.0 | match |
| surrogate seed 20260706; which detectors run per window and which on the whole recording | run.json, detect_folder.py | same | match |
| width/amplitude tallies | calls_measured.csv | exact | match, scope issue (F7) |
| cSPIKE agreement to 10⁻⁹ at the 0.25 s cap; PySpike cap broken since 0.8.0, PR 89 | tests/test_sync_detect.py | same | match |
| 12-minute first-treatment floor | docs/conditioned_run.md:75 | decided 2026-09-21 | match |

**Not recomputed:** n_roi, jitter and participation after the pin removal (F10); the real-data crowding probe (7 of 39); the separability t values themselves (the text reports none); every citation, which is role 2's.

---
*Transcription note: personal absolute paths were replaced with placeholders (sapper SAP004); nothing else was altered.*
