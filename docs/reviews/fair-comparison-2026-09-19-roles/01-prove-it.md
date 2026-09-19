<!-- Verbatim role report, except that this machine's absolute paths are written as %USERPROFILE% and <darkroom> (the repository is public). The unedited original is in <darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-roles/. -->

GRANT 1 ok — Read, Grep, Glob, Bash

(SubagentHandback is the report channel, not an editing tool. No file was edited. My only writes were the text extract and a scratch rebuild under the role-1 scratch folder.)

# Role 1 "Prove It": review of report.html (blob 76c3270)

## Summary
Every number the generator computes is correct. I rebuilt the page from the committed run files with the current generator. The output matches the artifact apart from the build timestamp and version string, and the Figure 2 region. That region differs because of uncommitted edits the main thread is making to `tools/build_fair_comparison_report.py` right now (it is `M` in `git status`).

I recomputed the following myself rather than reading them off the page, and all of them match:
- All 36 mean and paired-difference cells in Table 2, and every t value.
- The four tuned-minus-untuned rows.
- Every cell of Table 3.
- The job, fit and refit counts.
- The wall time.
- The facts in Figure 1's caption.
- Figure 4's before-fix and as-run draws, checked against all 1,938 raw `fits/*/*/*.run.json` records.

The defects are in the prose that the generator types in by hand, and in what the page leaves out.

## Findings
Columns: location · issue · severity · suggested fix · checked against a source?

1. **§8 Limits, second bullet.** The sentence is: "Re-measured on the corrected folder on 2026-09-17 by both workstations, every constant moved by less than its own bootstrap interval, and the two constants that describe coordination … did not move."
   - **No source in this repo or in any branch's git history.** `git log --all -S` and a grep across all three trees found nothing. The only bench re-measurement on record is `docs/learned/bench_measured.json`. It was measured 2026-09-17 on `steps_excluded`, which is the contaminated folder, not the corrected one.
   - That record says `all_inside: false`: participation (0.18) lies outside its interval [0.1818, 0.232].
   - This run's own `meta.json` records the same thing under `declaration.measured_outside_interval` as "awaiting Tony". The page does not mention it.
   - Decision 3 of the handoff says "'small' is the argument we agreed not to accept alone", yet the page concludes "That makes the effect small".
   - The 0.03% figure itself **is** confirmed (the de-pinned handoff, line 127).
   - **Blocking.** Fix: delete the re-measurement sentence unless a committed source is cited. State the open participation-outside-interval item from `meta.json`. Do not present the contamination as "small" (see CLAUDE.md, "A known contamination stops the work. It does not become a caveat.").
   - Checked against a source: yes (the claim has none; the record that does exist contradicts the reassurance).

2. **§4.1 "using the same inner loop"; Figure 3 text "Every candidate — 24 configurations per net, or a coded detector's search — is judged in panel B".** Coded candidates are not judged in the inner rotation. The tool's docstring (line 23) says "a hand-written configuration is scored directly on the training recordings". `_run_search` scores the pooled 72 training recordings, as `selections/*/cicada.json` → `pooled.recordings` shows.
   - **Major.** Fix: say coded settings are scored once on all three training folds pooled (there is nothing to train). Both sides still never see the held-out fold.
   - Checked: yes.

3. **Figure 8 caption, "no dot is to the right of it".** Two dots are to the right of zero: chorus_gain_norm, F1 alone, folds 1 and 2 (per-fold differences +0.000061 and +0.000404, from `results.json` comparisons).
   - **Major.** It is not visible at this scale, but it is a false sentence. Fix: "no dot is more than 0.001 to the right of it". Also say that chorus_gain_norm is marginally ahead in 2 of 4 folds on F1 alone.
   - Checked: yes.

4. **§1 "0.06 Hz, six times the quiet background rate".** 0.06 / 0.0052 = **11.5×** the quiet rate, using the page's own §2 value. The source (bench.py `BENCH_RECORDING` docstring) says "6x measured baseline", meaning the ~0.0096–0.0102 Hz median.
   - **Major.** Fix: "about six times the median baseline rate (11 times the quiet background, 3 times the busy one)".
   - Checked: yes.

5. **§6, "The earlier comparison's lead for the nets came from comparing untuned nets against a coded side tuned on one knob; with both sides tuned, it is gone"; also the lede.**
   - The earlier comparison (chorus_norm +0.103, t 6.5) ran on the **retired home spec** (32 ROIs, folds of six; `docs/goals/learned-model-family.md` lines 62 and 134–139). This run changes three things at once: the simulation, CoactDetect's mode (binned to sliding), and the tuning. So it cannot attribute the lost lead to tuning.
   - Its own data point the other way. Untuned nets here already trail tuned CoactDetect (untuned chorus_norm 0.736 against 0.748), and tuning moved the nets by only +0.005 to +0.032.
   - The page never says the earlier result came from a different simulation.
   - The source says CoactDetect was "tuned on one knob". It does not say "the coded detectors … each".
   - **Major.** Fix: state the change of simulation and say the lead's disappearance is not attributed to any single change.
   - Checked: yes.

6. **§7.2, "choices that missed the budget on new data".** The page reports CoactDetect over budget on its held-out fold in 1 of 4 folds. It omits the nets: **25 of 80 gated net refits exceeded the budget on their held-out fold** (`seeds_over_budget`: tube 11/20, chorus_gain_norm 7/20, chorus_norm 4/20, line_length 3/20). One example: tube in fold 2, seed 0, fired 95 and 92 probe alarms per hour against budgets of 14.9 and 13.9.
   - **Major.** This is an omission that favours the nets, in a report whose subject is fairness. Fix: add a nets row from `seeds_over_budget`.
   - Checked: yes.

7. **§7.3 heading "Refits that failed to train", applied to "tube, fold 1, refit seed 4: F1 0.000".** The run's own record says `failed_training_signature: False` and `f1_was_nan: True`. That refit made no calls at all: recall 0, precision NaN, zero probe and zero empty-recording calls, at the gated selection's shared threshold 0.998 (index 35). The 0 comes from the declared rule that turns NaN into 0.
   - **Major.** This is a misattributed mechanism. Fix: retitle to "Refits that scored below 0.2" and say this one made no calls at the threshold chosen on the inner fits. The chorus_gain_norm entry (F1 0.125, threshold 1e-4, precision 1.0, recall 0.067) does match the signature. Its gloss, "predicts nearly everywhere", is consistent with one call per recording.
   - Checked: yes.

8. **Figure 2 caption and Table 1: "tube averages the ROIs first, so it cannot tell three cells firing once from one cell firing three times".** `tube.py`'s docstring says:
   - The first operation is a per-ROI max-pool that widens each onset, and averaging comes after it.
   - Measured: "one cell bursting eight times scores 0.28 and stays silent, but **two** such cells score 0.997 … level with four genuinely distinct cells."

   So tube can tell one bursting cell from many. Its measured defect is that a few bursting cells can imitate a crowd.
   - **Major.** Fix: "tube pools the ROIs before judging, so a few cells firing repeatedly can look like many cells firing once (two bursting cells scored like four distinct ones)".
   - Checked: yes.

9. **§2, "the quiet and busy ends of the range real baseline recordings span".** The bench's `REGIMES` docstring says the two backgrounds are **p25 and p75**, the interquartile points, not the ends of the range. Half of real baselines lie outside them.
   - **Major.** Fix: "the 25th and 75th percentiles of real baseline rates".
   - Checked: yes.

10. **Provenance line, "Reviewed by the eleven roles of docs/doc_review_process.md".** The build (08:16) came before this review, which is round 1 and still in progress. The sentence was not true when it was built. **Minor.** Fix: emit it only once the run record exists, or drop it. Checked: yes.

11. **§9 and the builder's docstring call `fold_draws.json` "this report's derived file", but no tool in any worktree produces it.** A grep across all three trees finds it only in the reader. `crowded_check.json` records no commit or tool version either. My recomputation from the raw fit records and the old ordering rule reproduces `fold_draws.json` exactly, so the data are right, but they cannot be regenerated. **Minor.** Fix: commit the generator, or record in the file how it was made. Checked: yes.

12. **Figure 4 caption, "Section 7 gives what the fix does not change".** Section 7 says nothing about the fold fix. The caveat about overlapping training folds is in §6 ("How much the t values can carry") and §8. **Minor.** Fix: point to section 6. Checked: yes.

13. **§6, third bullet: "three coded detectors fall well behind: SPIKE-synch, rate+context and locust … refused by the veto or not admissible".** LoCo's gated choice also fails the veto in 4 of 4 folds (crowded F1 0.771 against 0.834; −0.059, t −23.5), and the bullet leaves it out. **Minor.** Fix: name LoCo. Checked: yes.

14. **§7.1 veto anchor.** For CoactDetect and LoCo the after-the-fact check anchors on goal 1's sliding base (`crowded_check.json` `reference_rule`). Two sources set a different anchor:
    - bench.py line 521: "MAX_CROWDED_DROP against what the detector ships at today".
    - HANDOFF-coded-detectors.md: "The veto's reference is what a detector SHIPS at, not the sliding-forced start".

    The deviation is not disclosed. Using goal 1's own binned crowded numbers (0.808 CoactDetect, 0.816 LoCo), the pass/fail outcomes would not change. I did not re-run this.
    - **Minor.** Fix: disclose the anchor.
    - Checked: partly (not recomputed).

15. **Figure 2's box text: "at 4 widths", "4 smoothing widths", "loudest 4".** These are the untuned defaults. The chosen configurations differ:
    - tube chose `n_scales` 6 in all 4 gated folds.
    - line_length chose 6 in all 4 gated folds.
    - chorus_gain_norm chose `top_m` 2 in all 4 gated folds; chorus_norm often chose 8.

    **Minor.** Fix: label the figure "at the untuned setting". Checked: yes.

16. **§4.4, "every contestant was chosen twice from the same fits".** For the coded detectors the two selections are separate searches with different candidate sets. For example, rate+context scored 39 candidates ungated and 73 gated in fold 1. §8 says so itself ("two searches, not one search filtered"). **Minor.** Fix: "from the same fits (nets) or the same scoring (coded)". Checked: yes.

17. **§4.2, "Until 2026-09-18 … the run of 10 fell inside the first training fold".** This holds at training seeds 0 and 4, where the run starts at index 0 or 10. At seeds 1–3 it starts at index 20, 40 or 60 of 70 and crosses folds. Distinct fitting sets under the old order, per seed: 2, 3, 3, 2, 2. Figure 4 is scoped to seed 0, so the figure is right; the prose generalises. **Minor.** Fix: "at training seed 0". Checked: yes (recomputed).

18. **§4.1, "walked every setting in goal 1's declared grids".** The validity rule refuses context windows over 120 s (CoactDetect 240; LoCo 240 and 480), and settings that do not apply are skipped. So Table 1's grid-value counts include values that could never be scored; CoactDetect scored 30 candidates against 49 listed values. **Minor.** Fix: add "subject to the context-window rule". Checked: yes.

19. **Table 1, LoCo: "compares the count with a percentile of the counts around it".** In sliding mode, `sliding.py` takes the percentile from an exact circular-shift null. It is not a percentile of neighbouring counts. **Minor.** Checked: yes.

## Claim ledger
Columns: quoted value · cited source · recomputed value · verdict

**Headline results (Table 2 and §6)**
- chorus_norm, F1 alone: 0.741, −0.007 (t −1.8) · results.json · 0.7411, −0.0069, −1.80 · match
- chorus_gain_norm, F1 alone: 0.703, −0.045 (t −1.2) · results.json · 0.7027, −0.0453, −1.24 · match
- line_length, F1 alone: 0.705, −0.043 (t −4.7) · results.json · 0.7053, −0.0427, −4.73 · match
- tube, F1 alone: 0.631, −0.117 (t −17.6) · results.json · 0.6312, −0.1168, −17.59 · match
- CoactDetect: 0.748 both ways; same settings both ways · results.json · 0.7480; config keys equal in 4/4 folds · match
- binned SCE: 0.771 / +0.023 (t 3.1); 0.770 / +0.022 (t 3.2) · results.json · 0.7709 / +0.0229 / 3.10; 0.7699 / +0.0219 / 3.17 · match
- LoCo: 0.738 / −0.010 (t −13.9); 0.689 / −0.059 (t −23.5) · results.json · 0.7376 / −0.0104 / −13.9; 0.6888 / −0.0592 / −23.52 · match
- locust: 0.683 / −0.065 (t −9.6); 0.549 / −0.199 (t −37.5) · results.json · 0.6830 / −0.0650 / −9.6; 0.5493 / −0.1987 / −37.49 · match
- SPIKE-synch: 0.655 / −0.093 (t −10.7); 0.274 / −0.474 (t −67.5) · results.json · 0.6554 / −0.0926 / −10.74; 0.2742 / −0.4738 / −67.5 · match
- rate+context: 0.647 / −0.101 (t −14.4); 0.466 / −0.282 (t −37.4) · results.json · 0.6471 / −0.1010 / −14.37; 0.4664 / −0.2816 / −37.36 · match
- Gated nets: 0.716 (−0.032, t −3.1), 0.718 (−0.030, t −13.0), 0.697 (−0.051, t −5.3), 0.594 (−0.154, t −4.6) · results.json · 0.7157 / −3.12; 0.7177 / −13.02; 0.6968 / −5.33; 0.5939 / −4.55 · match
- Tuned minus untuned: +0.005 (t 1.2), −0.006 (t −0.1), +0.032 (t 2.0), +0.002 (t 0.2) · results.json · 0.0053 / 1.196; −0.0064 / −0.149; 0.0319 / 1.972; 0.0021 / 0.219 · match
- "not admissible" counts: SCE 4/4 and 3/4; LoCo, locust, SPIKE-synch, rate+context gated 4/4 · crowded_check.json + selections · same · match
- "the budget refused every candidate" for locust, 4/4 · selections/gated/*/cicada.json · n_refused = n_scored = 16 in all 4 folds; `moves` is empty · match
- CoactDetect over budget on its held-out fold, 1/4 · results.json · fold index 2 · match
- **"no dot is to the right" of zero (Figure 8)** · results.json · two dots at +0.00006 and +0.0004 · **mismatch**

**Table 3 and the crowded veto**
- Table 3, all cells (merge gaps 8/30/8/—/—/8 and 3; crowded ranges; replaced-setting values 0.826/0.714/0.834/0.666/0.462/0.766; pass counts) · crowded_check.json, results.json · same · match
- CoactDetect passes the veto 8/8; SCE fails 7/8 · crowded_check.json · 8; 7 · match
- 30 s merge gap in every fold, the top of SCE's grid · results.json, meta hand_axes · 8/8 chose 30; grid top is 30 · match
- 12 crowded recordings per background; drop limit 0.02 · crowded_check.json, bench.MAX_CROWDED_DROP · seeds 1–12; 0.02 · match
- Goal 1: merge gaps out to about a minute, lost 0.25–0.32 · bench.py and the goal page · "0.251 to 0.318" · match

**Refits that scored below 0.2 (§7.3)**
- 210 refits, 2 below 0.2 · ran.json, results.json · 210; 2 · match
- chorus_gain_norm fold 3, seed 3, F1 0.125, failed-training signature · results.json · 0.125; signature True · match
- **tube fold 1, seed 4, F1 0.000, listed under "failed to train"** · results.json · F1 NaN (no calls) counted as 0; signature False · **mismatch (mechanism)**

**Run size and timing (§4.5, Figure 3)**
- 1,963 jobs = 1 + 24 + 1,728 + 210 · ran.json · the same, by stage · match
- 1,938 fits · results.json, raw run records · 1,938 (all WSMIP064, one torch build) · match
- Wall time 13.7 h · meta.started to progress.at · 13.736 h · match
- 12.7 h training; no errors · results.json, sum of train_sec · 12.69 h; errors [] · match
- 16:14 to 05:58 · meta.json, progress.json · 16:14:16 to 05:58:24 · match
- Code at e8764aa, tree clean · meta.started.git · e8764aa…, dirty false. The tune-bench-comparison tree at HEAD e5e61f7 has no tools/ or src/ diff from it · match

**Design and counts (§2–§4)**
- 48 seeds (1000–1047), 4 folds of 12, 96 recordings, 24 per fold · meta.json · same · match
- 24 configurations per net, untuned always among them · meta.configurations · 24 unique; the untuned key is in each list · match
- lr and steps grids; 3 or 4 settings of each net's own · meta.learned_axes · 3/3/4/3 · match
- Table 1: net settings 5/6/5/5; coded settings and values 10/49, 7/39, 10/46, 4/19, 10/46, 10/47 · meta.learned_axes, hand_axes · same · match
- 3 tuning seeds, 5 refit seeds · meta.json · (0,1,2), (0–4), n_seeds 5 everywhere · match
- Budget 1.6× the reference, on probe and quiet-empty rates · meta.budgets, `within()` · e.g. 16.0 = 1.6 × 10.0; 11.496 = 1.6 × 7.185 · match
- fold_check.distinct = true · meta.json · true; also recomputed: all outer (model, seed) fitting sets and threshold sets distinct; every fit reaches every training fold · match
- Figure 4: before the fix, 2 distinct sets; folds 2–4 fit seeds 1000–1004 · fold_draws.json plus the old-order rule · recomputed identical · match
- Figure 4 panel B, "read from its fit records" · raw run records · identical to fold_draws.json for all 4 folds and all 4 models · match
- Reference CoactDetect alpha 1e-5, 120 s, 8 s, 1 s; LoCo 99.9 and 8 s · meta.reference and coded_base · same · match
- **"used the same inner loop" (coded side)** · tune_learned_vs_coact.py docstring and `_run_search` · scored directly on the pooled training recordings · **mismatch**

**Bench facts (§1, §2, Figure 1)**
- 45 min, 33 ROIs, 15 events (5 × 3 at 30/18/10%), 0.36 s spread, 120 s apart, 6 distractors · meta.bench_recording, bench.py · same · match
- Backgrounds 0.0052 and 0.019 Hz · bench.REGIMES · same · match
- **"quiet and busy ends of the range" real baselines span** · REGIMES docstring · p25 and p75 · **mismatch**
- Probe 5 min at 0.06 Hz · hot_window 1200–1500 s; hot_rate_hz · 300 s; 0.06 · match
- **"six times the quiet background rate"** · the report's own 0.0052 Hz · 11.5× · **mismatch**
- Hit within 2.5 s; probe kept out of precision · score.TOL_SEC; Score.n_scored · 2.5; hot_fa excluded · match
- Figure 1: event at 993 s, 18%, about 6 ticks, 2 distractors, 2,595 onsets, probe starting at 1,200 s with a 30 s ramp · bench.make_recording("baseline_busy", 1000) · 993.3 s; 0.18; 6 participants; 2 (1034.4, 1091.8); 2,595; 1200/30 · match

**Earlier comparison and goal 1**
- Earlier nets ahead; tube tied untuned · learned-model-family.md · +0.103/+0.084/+0.052; tube +0.000 — **on the home spec** · match; the context is missing (finding 5)
- **"coded detectors tuned on a single knob each"** · the goal page · "CoactDetect had been tuned on one knob" · mismatch (minor)
- Goal 1 sliding better; calls survive shifts; shipped points still binned · HANDOFF-coded-detectors.md, bench.py · 0.737 vs 0.699 and 0.746 vs 0.702; 100% vs 64% kept; "STILL BINNED HERE" · match

**Nets and their architectures**
- **tube "cannot tell three cells once from one cell three times"** · tube.py docstring · one bursting cell scores 0.28 (silent) against 0.998 for distinct cells · **mismatch**
- chorus, line_length and chorus_gain_norm architecture boxes · chorus.py, line.py · per-ROI standardisation, sigmoid vote, mean/spread/top-m pools, learned gain and bias · match (at the untuned defaults)
- Nets' merge gap fixed · encode.decode, trained.merge_gap_frames · not in any search axis · match

**Contamination and the bench measurement (§8)**
- 0.03% of events, decision 3 · the de-pinned handoff, line 127 · 0.03% · match
- **"every constant moved by less than its own bootstrap interval … did not move"** · none in the repo · the only record (bench_measured.json, on steps_excluded) has all_inside false, with participation outside · **unverifiable; contradicts the reassurance**

**Replicate (§5, Figure 6)**
- Replicate: seeds 2000–2047, everything else fixed, finished 07:48 · 7a95e8a diff; darkroom replicate progress.json · replicate stride 1000, nothing else changed; at 07:48:04, 1968/1968 jobs, 0 errors · match

**Files and paths (§9)**
- scores 1.1 GB unpacked; darkroom layout; the darkroom copy is byte-identical · du; ls; cmp · 1.1 GB (1.156e9 B); chosen/, fits.tar.gz, scores.tar.gz, run.log present; index.html identical; results.json and ran.json identical; meta.json differs only by the %USERPROFILE%/<darkroom> redaction · match

**Quote**
- Tony: "for this training run use only baseline" · goals README line 32; HANDOFF-coded-detectors.md line 228 · same · match

## Records and missing items checked
- **What is recorded:** the design record for this run (fold membership, recording seeds, the empty-recording offsets, the budget training seeds) is `meta.json`, and it reconciles. The code asserts that no scored seed was fitted on and that no held-out seed reached a selection.
- **What is not missing:** no coded detector, net, fold, selection or refit seed is absent. All 10 × 4 × 2 selections and all 5 seeds per refit are present.
- **Goal 1's seeds:** the settings goal 1 chose come from seeds 1..2n. The crowded recordings are tail seeds 1–12. Neither overlaps 1000–1047, so no leak into the held-out folds.
- **What is missing:** from the page, the nets' 25 held-out budget overruns (finding 6) and the open participation-outside-interval item (finding 1). From the repo, a generator for `fold_draws.json` (finding 11).

## Files
- Artifact: %USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\report.html
- Main sources:
  - The run's summaries (results.json, meta.json, crowded_check.json, fold_draws.json, selections/) in the same folder
  - %USERPROFILE%\runs\fair-comparison-2026-09-18\fits\ (the raw fit records)
  - %USERPROFILE%\bugarach\bugarach-worktrees\tune-bench-comparison\tools\tune_learned_vs_coact.py
  - …\tune-bench-comparison\src\bugarach\learn\nets\tube.py
  - …\fair-comparison-report\src\bugarach\bench.py (REGIMES, BENCH_RECORDING, MAX_CROWDED_DROP)
  - …\fair-comparison-report\docs\learned\bench_measured.json
  - …\fair-comparison-report\HANDOFF-slow-comodulation-on-the-de-pinned-export.md
  - …\fair-comparison-report\docs\goals\learned-model-family.md
- Scratch: %USERPROFILE%\AppData\Local\Temp\claude\c--Users-<user>-bugarach-bugarach\0c979457-501e-4b3d-9c4b-21e394823cf5\scratchpad\mb\role-1\ (report.txt, rebuild\index.html)
