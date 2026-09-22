GRANT 1 MISMATCH — missing Grep, Glob; holds no forbidden tools (Read, Bash only; no Edit, Write or NotebookEdit)

# Claim and data verifier ("Prove It"): `<worktree>/docs/learned/tube_self_supervised/README.md` at f2278da

## What I checked, and how

- **Summary file.** I copied the raw stage outputs to `<scratchpad>/mb4/role01/run/` and reran `tools/summarize_tube_self_supervised.py`. The new `summary.json` matches the committed one on every key except the commit stamp.
- **Independent recomputation.** Separately from the summarizer, I recomputed from the raw outputs:
  - every cell of the per-ROI and aggregate leak tables;
  - the bake-off table and all eight paired comparisons, including the corrected interval, sign test and mean without the largest fold;
  - every range in the label-free training section and the paired-check tables;
  - the twin-check table;
  - event rates and the share of events with at least three ROIs, from `real_compare/events.json` against the export folder;
  - the agreement ranges and the window-edge shares;
  - the plant-probe ratios and their standard errors.
- **Re-runs.**
  - Three repo checkpoints re-score through the probe code with a difference of 0.0 from the stored probe. That supports "the ten here match the previous run's weights".
  - One checkpoint re-scores through the twin check with a difference of 0.0 from the stored result.
  - All five figures rebuild pixel-identical from `summary.json`.
  - The burst-vote ratios in `tests/test_line_vote.py` recompute to 1.04–1.15. Both named tests pass when run separately. Run together in one process they crash with a segmentation fault; that is an environment problem, not a claim in the report.
- **Record of which recording belongs to which mouse and group.** This is the export folder role `steps_excluded`, named in `<worktree>/current_export.toml`. The loader gives 84 recordings, 44 mice and 4 groups (DI 10 mice, MALE 12, ORX 12, OVX 10). Recordings per mouse: 30 mice have 2, 9 have 1, 5 have 3. No mouse sits in two groups. The leak tests fold and bootstrap by mouse; the real-recordings stage pools events without clustering by mouse, and the report says so.

## Claim ledger

M = match, X = mismatch, U = cannot be verified from the sources, P = partly verified.

**Leak tests (`controls_lab/results.json` by_mouse, `aggregate_leak/results.json`)**

| quoted | source | recomputed | |
|---|---|---|---|
| fast-stream table, all 24 cells | by_mouse accuracy | identical | M |
| circular shift lowest lower bound 0.513 | p2_5 | 0.513 | M |
| slow stream 0.500–0.524 up to 11.2 s; 0.558 and 0.567 (lower bounds 0.512, 0.517); shared offset 0.495–0.507 | slow rows | identical | M |
| 84 recordings, 44 mice, 1,501 pairs per stream | n_recordings, n_mice, n_pairs | 84, 44, 1,501 (both streams) | M |
| rigid shift drops 0.5 % and 1.1 % of onsets at 10 and 20 s | dropped_share | 0.0053, 0.0108 | M |
| slow displacements are the fast ones rounded to whole 1.4 s frames | `J_SEC` in `look_rigid_shift_controls.py` | 1.4 × 1, 2, 4, 8, 16, 32 s; rounding 10/20/40 s would give 9.8/19.6/40.6 | **X** |
| 1.4 s per frame on the slow stream | export folder, loader | one frame interval per recording, 0.1 s, for both streams; slow onsets 1 frame apart occur 3,851 times; shifts are drawn in 0.1 s frames | **X/U** |
| aggregate table, all 18 ranges | results.json | identical | M |
| cells-mean trace alone: 0.657–0.674 (initial bank), 0.619–0.643 (fitted heads) | trace accuracy | 0.657–0.674; tube 0.619–0.642, line 0.622–0.643 | M |
| shared-modulation twin 0.503 (0.408–0.583), 0.742, 0.817; real 0.670 at 1.6 s, 0.664–0.688 at other J | init by J | identical | M |
| twins are "20 ROIs' worth of real rates" | `N_TWINS`, twin_shape | 20 twin recordings, each 31 ROIs × 12,000 frames | **X** |
| "one 40 s rate cycle" | `MOD_PERIOD_SEC` | 40 s period over 1,200 s, which is 30 cycles | X (wording) |
| hand-built bank = tube's four initial scales plus four wider | `CENTRES`, `tube.py` init | 1, 2, 4, 8 plus 16–128 frames; tube's kernels are cut off at ±128 frames, the bank's reach ±3× the surround width | P |
| fitted `tube` and `line`, "four folds" | fitted_parameters | folds 2 and 3 are the same model for both | **X** (see F4) |

**Bake-off (`bakeoff_seed*/…json`)**

| quoted | source | recomputed | |
|---|---|---|---|
| F1, SD, recall, precision, probe calls for 15 detectors | per_fold | identical | M |
| seconds per fit (all ranges) | train_sec | identical | M |
| 8 comparisons: per fold, mean, corrected interval, sign test p, mean without largest fold | fold means | identical (sign test 0.625 shown as 0.63) | M |
| line over tube corrected p = 0.027 | Nadeau–Bengio t | 0.027 | M |
| without the third fold no learned lead over CoactDetect exceeds 0.008 | fold means | largest is line_bound, +0.008 | M |
| tiny at the grid floor in all 12 fits; one detection per recording | threshold, n_detected | 0.0001 ×12; 2 detections per 2-recording fold | M |
| 30 planted events per fold | n_planted | 30 | M |
| "All three have 1,305 parameters" | n_params | line 1,305; line_bound 1,305; **line_length 1,233** | **X** |
| 12 fold-seed fits | `fold_maker` split | 9 distinct fits (folds 2 and 3 share the same 4 training recordings) | **X** |

**Plant probe (`probe/line_vs_fuzz.json`)**

| quoted | source | recomputed | |
|---|---|---|---|
| synchronous plant ÷ fuzz at the largest plant: 1.99, 1.75, 1.60, 1.43; standard error 10–14 % of the ratio | scores, n_fields = 12 | identical | M |
| adjacent pairs differ by less than combined error | same | 0.24 < 0.37; 0.15 < 0.31; 0.17 < 0.23 | M |
| counting builds beat tube on synchronous ÷ burst | same | true at plant sizes 4, 8 and 16 | M |
| burst within 0.6 s, fuzz over 2.9 s, wave one frame apart, 32 ROIs | tool code | identical | M |
| the probe reads supervised fits and the seed-0, fold-0 checkpoints | probe keys | it holds 120 checkpoints; its supervised fits use all 8 recordings, not per-fold fits | X (low) |

**Label-free training (`training/results.jsonl`)**

| quoted | source | recomputed | |
|---|---|---|---|
| 360 fits plus 24 baseline rows; 900 steps; 3 crop pairs; top 1 %; crop 409.6 s | meta, rows | 384 rows; code matches | M |
| label-free table, all 18 ranges | scores | identical | M |
| untrained line_length 0.291 beats 14 of 20; trained beat all untrained at the two stricter rates | cells | 14; true | M |
| 1–9 fits with no true positive at ≤ 0.5; up to 5 at ≤ 2 | n_hit | 1–9; 0–5 | M |
| grid floor hit 8, 9, 10 times, all line, 2–4 per condition | at_grid_floor | identical | M |
| slow_modulation "fires within the rate on no held-out recording's shifts" and scores 0 | scores | it fires 29/75/140 times across the 8 rows; every detection is in the dense probe stretch (hot_fa = n_detected), so F1 is undefined and is written as 0 | **X** |
| truth-reading scores: real arm 0.499–0.577, untrained 0.503–0.559; coverage 0.954–0.985 and 0.962–0.984; widths 23–128 s; supervised 0.005–0.010 at 0.662–0.696; count_excess 0.004 at 0.648 | oracle | identical | M |
| simulated-arm coverages 0.035/0.022, 0.36–0.50, ≥ 0.92 | oracle | identical | M |
| grid edge in 4 of 360 fits, all line | oracle_report | 4, all line | M |
| paired-check table, all 32 ranges | checks | identical | M |
| positive control moved in 10–12, 11–12, 8–12, all 4, 1–8 fits | thinned | identical | M |
| untrained read 0.485–0.519 on rigid-shift checks | checks | identical | M |
| slow_modulation 1.6 s check 0.616–0.633 | checks | 0.616, 0.634 | M |
| loss ≥ ln 2 in 0–4 of 12; win share 0.90–1.00 (sim) and 0.63–0.80 (real) | history | identical | M |
| ties up to 0.98; 10 trained fits tie on every crop | tie_share | 0.976; 10 | M |
| a label-free threshold can beat the truth-reading one | scores | yes: 3 supervised conditions at ≤ 2 | M |
| 12 fits per supervised condition | fitted_parameters | fold 2 = fold 3 in 15 of 15 (model, seed) pairs | **X** |

**Twin check (`small_j_check/results.json`)**

| quoted | source | recomputed | |
|---|---|---|---|
| table, all 25 cells | groups pooled | identical | M |
| above chance on the events twin in 11–12 of 12 fits | n_fits_above_half | 11–12 | M |
| 10 conditions × 12 fits; 5 supervised; 5 untrained | n_fits | identical | M |
| "60 twin recordings per scorer" | tool code | 30 twins × 2 draws; the events-only twin is the same 30 recordings both times | X (low) |

**Real recordings (`real_compare/summary.json`, `events.json`)**

| quoted | source | recomputed | |
|---|---|---|---|
| the whole table (rates, share ≥ 3 ROIs, activity chance, rate and share on the shift) | stats | identical; rate and share recomputed from events.json for 7 detectors | M |
| supervised label-free threshold set on shifts at J = 20 s | `SUP_THRESHOLD_J_SEC`, sup_threshold_j_sec | **10 s** | **X** |
| slow_modulation keeps 0.43 on "a 20 s shift" | same | the shift is 10 s | **X** |
| 0.128–0.237 "inside" the activity chance range 0.127–0.203 | stats | 0.237 and 0.218 lie above 0.203; see F2 | **X** |
| median event holds 0–1 ROIs | participation_median | 0–1 | M |
| agreement table, all ranges; references 0.780 and 0.591 | agreement | identical | M |
| three builds 0.804–0.814 and 0.680–0.804 | stats, agreement | identical | M |
| edge shares 0.8 %; 3.8–5.7 %; 5.0–10.0 %; 1.6–2.2 %; 1.1–3.7 %; 0.7–8.8 %; 3.3 / 0.0 / 2.2 % | edge_shares | identical | M |
| zero padding 12.8 s; head reaches 6.3 s | `tube.py`, `receptive_field(6)` | 128 frames; 127-frame field, ±63 frames | M |

**Constants, code and other documents**

| quoted | source | recomputed | |
|---|---|---|---|
| count_excess ±0.2 s minus 30 s mean; slow_modulation 10 s | `BASELINE_*` | 2, 301 and 101 frames at 0.1 s | M |
| merge gap 2 s; participation ±0.2 s; 10 random draws per event | tool constants | identical | M |
| jitter 0.311 against null 0.335; generator.md 0.36 against 0.42, "least trustworthy" | `generator_spec.json`, `generator.md` | identical | M |
| five-minute dense stretch | hot_window | 1,200–1,500 s | M |
| 84–99 % of planted coordination removed | `rigid_shift_look` README | quoted there | M |
| MILESTONES: no ranking; MAHICE (machine-assisted human identification of coordinated events) review blocks transfer figures | MILESTONES rows | present | M |
| rigid_frames test: 1.5 frames, KS distance 0.05, one onset | test file | identical | M |
| the per-ROI test draws every surrogate through `bugarach.surrogates` | tool code | the shared offset is numpy `shared_shift` | **X** |
| per-ROI leak test is exposed to the dropped onsets at the ends | `interior_windows` | first and last 60 s windows are excluded and J ≤ 44.8 s, so dropped onsets never reach a scored window | **X** |
| stage commits 70201e7 (dirty flag null), 28ea5ad ×3, f55db21; summary commit in its provenance key; ea350be fixed the flag | provenance stamps, git | identical; ea350be changes `provenance.py` and is not an ancestor of 70201e7 | M |
| Python 3.14.5, torch 2.14.0, Elephant 1.2.1 | venv | identical (torch and Elephant versions are not stamped in the outputs) | P |
| figures rebuilt pixel-identical | re-render | 5 of 5 identical | M |
| 10 checkpoints match the previous run; the stage regenerates bit for bit | probe and twin re-score | difference 0.0 on 3 and 1 checkpoints | P |
| literature (Stella 25 ms, Louis et al. roll, Pipa, Finn, Cecchini, Hamon/Dard, the Kreuz personal communication) | none opened | — | U |

## Findings

| # | location | issue | severity | suggested fix | verified against source |
|---|---|---|---|---|---|
| F1 | lines 411–412, 480–483, 422 | **A withdrawn setting has come back.** The report says supervised and baseline label-free thresholds on real recordings use 20 s shifts, and that the benchmark and real recordings run at different J. The code (`SUP_THRESHOLD_J_SEC = 10.0`, whose docstring says "20 s until 2026-09-17 … now one value") and the run output (`sup_threshold_j_sec: 10.0`, also in summary.json) say 10 s. The slow_modulation sentence ("survive a 20 s shift") is wrong for the same reason. | high | Say 10 s. Delete the operating-point-mismatch half of that bullet. Rewrite the slow_modulation sentence for a 10 s shift. | yes |
| F2 | lines 107–108, 395–396, 418–419, 522–523 | "Share with ≥ 3 ROIs 0.128–0.237 sits inside the activity-weighted chance range 0.127–0.203" is false: two values lie above the range. Condition by condition, 6 of 10 exceed their own chance by more than 0.01 (line_length at J = 10 s: 0.237 against 0.148; line at 10 s: 0.218 against 0.171). Two are about equal and two are below. The headline "no more co-activity than chance" and the reasoning behind the objective decision rest on this. | high | Compare each condition with its own chance and report the count above. Soften the headline and decision 3. | yes |
| F3 | line 229 | "All three have 1,305 parameters": line_length has 1,233. | medium | "line and line_bound 1,305; line_length 1,233". | yes |
| F4 | Figure 3 caption, lines 204–205, 253–254, table at 160, Figure 4 "12 fits" | Supervised fits for the third and fourth held-out folds are the **same model**. `fold_maker` fits both on recordings 1000–1003; saved parameters are identical in 15 of 15 (model, seed) pairs and for fitted tube and line in the aggregate test. So there are 9 distinct bake-off fits, not 12, and 3 distinct fitted models in the aggregate test, not 4. The third-fold margin that "was not examined" is the same model scored on different held-out recordings. The Nadeau–Bengio ratio of 2/6 assumes distinct training sets. The untrained arm is also one model per seed across all folds. | medium | State it wherever fits are counted. Say where the third-fold margin comes from, and review whether the interval correction still holds. | yes |
| F5 | lines 49–50, 155, 506 | Slow-stream displacements are 1.4 s × powers of two, not rounded fast displacements. The export folder declares 0.1 s per frame for the slow stream, and the shifts are drawn at 0.1 s. "1.4 s per frame" has no source in the export folder or the code. | medium | Correct the J description. Cite a source for 1.4 s or remove it. | yes |
| F6 | lines 174–177 | Twins are 20 recordings of 31 ROIs, not "20 ROIs' worth". The modulation is a 40 s period (30 cycles), not "one cycle". | medium | Correct both. | yes |
| F7 | lines 311–312, table row 303 | slow_modulation does fire within the rate (29, 75 and 140 detections in total). Every detection falls in the dense probe stretch, which precision excludes, so F1 is undefined and is written as 0. | medium | Give that mechanism and mark the 0.000 row as undefined. | yes |
| F8 | whole report | A known problem in the data is never mentioned. `current_export.toml` flags 12 ROIs stuck at the frame floor (from non-rigid motion correction) in 20260629_312, 20260629_309, 20260630_316 and 20250926_235, and **all four are in the 84 recordings**. The folder also removed events within ±2 s of field steps in 3 baseline fast recordings (71 events). That leaves 4 s gaps shared by every ROI, which rigid shift misaligns and a check could read as structure. | medium | Name both. Say whether either can move the leak or paired checks. | yes |
| F9 | lines 649–650 | "The per-ROI leak test draws every surrogate through bugarach.surrogates": the shared offset is numpy code in `look_rigid_shift_controls.py`, and the aggregate test uses it too. | low–medium | Correct the sentence. | yes |
| F10 | line 475 | The per-ROI leak test does stay clear of the ends: only interior windows are scored, and 60 s is more than the largest J. Only the label-free thresholds, and the wide kernels in the aggregate test, reach the ends. | low–medium | Narrow the claim. | yes |
| F11 | line 357 | "60 twin recordings per scorer": the events-only twin is 30 recordings scored twice. The crop margin is set by 20 s at every J. | low | Say 30 twins × 2 draws. | yes |
| F12 | lines 639–641 | The probe read all 120 checkpoints, not only seed 0 fold 0. Its supervised fits are trained on all eight recordings, not the bake-off's per-fold fits. | low | Correct. | yes |
| F13 | line 172 | The hand-built bank does not exactly reproduce tube's kernels: tube cuts them off at ±128 frames, which truncates the surround from the 8-frame scale up. | low | Say "approximates". | yes |
| F14 | lines 442–443, 531–532 | The "bake-off threshold" on real recordings comes from fits on all eight recordings, not the bake-off's per-fold thresholds. | low | Rename, or add a note. | yes |
| F15 | line 339 | "The null checks read chance for every group" is asserted with no test. Supervised independent-crop checks are below 0.5 for all 5 models (0.431–0.487); one baseline reads 0.406. | low | Give an interval, or soften. | yes |
| F16 | lines 450–461 | The "Nothing here is ground truth" paragraph appears twice. | low | Delete one copy. | yes |
| F17 | lines 656–659, `real_compare/` | The report cites FOUNDATIONS §5 for keeping a real raster out of the repo. The same run commits per-recording event times keyed by recording ID, plus checkpoints trained on real data, which §5 ("anything derived from real data stays machine-local … no slice ids") also covers. Recording IDs are already committed elsewhere in the tree. | low (for the main thread to judge) | Check this against §5. | yes |

Everything else in the report that could be checked against the run outputs, code or project documents checks out. The literature citations are left to the role that checks references.

Files that matter:
- `<worktree>/tools/tube_ssl_real_compare.py` (`SUP_THRESHOLD_J_SEC = 10.0`)
- `<worktree>/docs/learned/tube_self_supervised/real_compare/summary.json`
- `<worktree>/tools/look_rigid_shift_controls.py` (`J_SEC`, `shared_shift`)
- `<worktree>/src/bugarach/learn/train.py` (`fold_maker`)
- `<worktree>/tools/tube_self_supervised.py`
- `<worktree>/current_export.toml`
- scratch outputs: `<scratchpad>/mb4/role01/run/summary.json` and `<scratchpad>/mb4/role01/figs/`
