<!-- Verbatim role report, except that this machine's absolute paths are written as %USERPROFILE% and <darkroom> (the repository is public). The unedited original is in <darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-roles-round2/. -->

GRANT 4 ok — Read, Grep, Glob, Bash (I also hold SubagentHandback, which only delivers this report. I hold no Edit, Write or NotebookEdit, and I edited no file. My scratch files are in `...\scratchpad\mb\r2-role-4\`.)

**Artifact reviewed:** `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\report.html`. Its blob hash is 16ac704, which matches the one I was given.

**Summary:** the headline holds only under one of the report's two selections, and it is the one section 4.4 itself says flatters detectors that call more. The replicate sentence rests on training failures. The pooled F1 hides where the two sides actually differ. Each of these is backed by numbers that are already in the run's files but not on the page.

## Findings
Format: location · issue · severity · suggested fix · verified against a source (yes/no)

**B1.** The answer paragraph, "What the table says" bullet 2, and section 4.5.
- **Issue:** The answer says the lead flips when the merge gap is matched. That is true only for the choice on F1 alone. The report's own `merge_gap.json` also holds the under-budget re-decodes, and they go the other way. With the gap matched, CoactDetect stays ahead:
  - chorus_norm: −0.016 at 2 s, −0.018 at 8 s, −0.020 at 16 s (net ahead in 1 of 4 folds each time).
  - chorus_gain_norm: −0.014, −0.017, −0.017 (0 of 4 folds at every gap; plain t −4.3 to −7.1).
- Section 4.4 says F1 alone "rewards a detector that calls more". So the headline is built on the selection the report itself distrusts, and the arm that disagrees is left out.
- The answer sentence "within 0.010 F1" is also false for that arm: chorus_norm trails by 0.032 and chorus_gain_norm by 0.030.
- **Severity:** blocking.
- **Fix:** Report the matched-gap comparison for both selections, in the text and as a panel of Figure 5. Restate the answer as: "on F1 alone the order depends on the merge gap; under the false-alarm budget CoactDetect leads at every matched gap tried." Keep the caveat that the thresholds under the budget were chosen at 2 s (see M7).
- **Verified:** yes. I recomputed this from `merge_gap.json`.

**B2.** Answer paragraph ("A second, independent draw … agrees that no net is ahead"), section 5, and Figure 8's orange diamonds.
- **Issue:** The replicate's chorus_norm − CoactDetect gap on F1 alone is −0.057, but per fold it is +0.003, −0.243, +0.003, +0.007.
  - chorus_norm is ahead in 3 of 4 replicate folds. In this run it is ahead in 0 of 4.
  - The whole mean comes from replicate fold 2. Two of its five refits carry the failed-training signature (F1 0.125 each), and the same two score 0.000 in the choice under the budget.
  - Drop those two refits and chorus_norm leads CoactDetect in 4 of 4 replicate folds (fold 2: 0.751 against 0.744).
  - The replicate's chorus_gain_norm mean (−0.029) is also mostly one fold holding one failed refit.
- This report lists its own two refits below 0.2 F1 but says nothing about the replicate's. It then uses the replicate as corroboration: section 6 calls it "the stronger check". In Figure 8 the chorus_norm diamond sits at −0.058, well left of every blue dot, with no explanation.
- **Severity:** blocking.
- **Fix:** Show the replicate per fold. List its refits below 0.2 F1 the same way this run's are listed. Replace "agrees that no net is ahead" with what the data support: at the settings as chosen, the replicate's mean favours CoactDetect only because of failed trainings, and its median fold favours chorus_norm. Treat the failure rate as a property of the nets (see m19).
- **Verified:** yes. Per-fold values come from `replicate_summary.json`; per-refit values from the darkroom `2026-09-18-replicate-run-status/results/results.json`.

**M1.** The headline, Table 2 and Figure 7 all show F1 pooled across backgrounds and participation levels.
- **Issue:** Pooling hides opposite profiles. Figures below are held-out, choice on F1 alone; chorus_norm is pooled over its 5 refits.
  - Events at 30% and 18% participation are saturated: recall is about 1.0 for both sides in every fold and background.
  - Both sides hit 89–100% of distractors, and distractors make up most of their false calls outside the probe (CoactDetect 88–100%).
  - The difference therefore lies almost entirely in the 10%-participation events.
    - Busy background: chorus_norm recall 0.54 / 0.56 / 0.72 / 0.54 against CoactDetect 0.38 / 0.32 / 0.45 / 0.23. The net is ahead by about 0.24 in all 4 folds.
    - Quiet background: CoactDetect is ahead in 3 of 4 folds (e.g. 0.85 against 0.66).
  - By background, chorus_norm − CoactDetect F1 is −0.014 in quiet and 0.000 in busy.
- A "±0.007 F1" headline describes none of this. The rule applies: a pooled headline number on a results claim is a defect, and the breakdown is available.
- **Severity:** major.
- **Fix:** Add a table or figure of recall by participation level × background, plus precision split into distractor calls and other false calls, for CoactDetect and the best nets. Say in the answer where each side wins.
- **Verified:** yes. Computed from `%USERPROFILE%\runs\fair-comparison-2026-09-18\scores\coact\outer*__ungated.json` and the chosen chorus_norm outer refits' score files, at each refit's `threshold_index`.

**M2.** Section 1: distractors "count the same way for every contestant".
- **Issue:** Counting the same way is not neutral. A distractor is built exactly like an 18% event, and both sides find 18% events at recall about 1.0. So any sensitive detector must call nearly every distractor, which caps precision near 15/21 ≈ 0.71; observed precision is 0.56–0.70. The rule penalises sensitivity at 18%, and the project calls it an open question.
- **Severity:** moderate.
- **Fix:** State the ceiling. Report F1 with distractor calls left out of precision as a sensitivity check, alongside the main numbers.
- **Verified:** yes (from the score rows and the bench declaration in `meta.json`).

**M3.** Answer paragraph and section 2 ("2.5 s is where the scores stop changing").
- **Issue:** The scorer's own documentation (`src/bugarach/score.py`, `TOL_SEC`) says: "read the ORDER of the bench's rows, never the decimal places of one". The headline turns on 0.007–0.010 F1.
- The 2.5 s plateau was measured for the coded detectors only (LoCo and CoactDetect plateau at 2.5 s, RateDetect at 2.0 s). `tests/test_tolerance_curve.py` runs over `bench.DETECTORS`, and no net's tolerance curve was ever measured.
- **Severity:** major.
- **Fix:** Say the plateau was established for the coded detectors, and measure it for the nets or state the gap. Quote the scorer's resolution caveat next to the headline margin.
- **Verified:** yes.

**M4.** "With the gap matched, the order reverses".
- **Issue:** Four problems:
  - **No statistics.** The matched-gap numbers carry no t, though every row of Table 2 has one. Plain t is 2.8 at 2 s and 2.3 at 8 s; corrected, 1.8 and 1.5. That is weaker than the evidence the report already calls unsettled.
  - **Gaps picked after seeing the held-out results.** The gaps shown were chosen by looking at held-out results.
  - **Each matched comparison handicaps one side.** At 2 s, CoactDetect's other settings were tuned together with an 8 s gap. At 8 s, chorus_norm keeps a threshold chosen at 2 s.
  - **"Bound" has no stated direction.** Taking the best gap on held-out data is optimistic; not re-choosing the threshold is pessimistic.
- "A rerun … would settle it" overclaims when there are 3 degrees of freedom and the effects are this size.
- **Severity:** major.
- **Fix:** Give plain and corrected t, and the fold counts, for the matched comparisons. Say which side each matched comparison disadvantages. Replace "reverses" with "reverses in point estimate; not distinguishable". Replace "would settle it" with "would remove the asymmetry".
- **Verified:** yes (computed from `merge_gap.json`).

**M5.** "Tuning moved some nets and not others" reports F1 alone only.
- **Issue:** Under the budget, tuning made chorus_norm worse than untuned: −0.020, t −2.0, lower in 3 of 4 folds. Tube also got worse (−0.035; in the replicate −0.035, t −4.0). This undercuts the premise "once both are tuned": for the nets, the inner-loop selection is at or below noise level and sometimes harmful.
- **Severity:** major.
- **Fix:** Report tuned minus untuned for both selections, and say that under the budget tuning did not help or hurt the chorus nets.
- **Verified:** yes (`results.json` comparisons for both selections, and `replicate_summary.json`).

**M6.** Section 4.4, Figure 4 and Table 2's under-budget column.
- **Issue:** No held-out false-alarm rate for any contestant appears anywhere on the page. Figure 4 is labelled "a schematic, not data", even though the data exist.
  - Under the budget, the nets sit far inside it: chorus_gain_norm fires 0–6 per hour in the probe, against CoactDetect's 6–14 per hour. So "under the budget" is a ceiling, not a matched operating point.
  - The nets' false-alarm rates swing from 0 to 107 per hour across training seeds of the same configuration in the same fold. That instability is never mentioned.
- **Severity:** moderate.
- **Fix:** Replace or augment Figure 4 with the real held-out F1 against false-alarm rate, one point per fold or refit. Report the spread across training seeds.
- **Verified:** yes (`results.json`, `probe_per_hour` and `quiet_per_hour` per seed).

**M7.** Sections 4.4 and 4.5.
- **Issue:** The budget counts calls after merging (`n_detected` and `hot_fa` in `_score_settings`). So the nets' fixed 2 s gap splits calls and makes the budget bind harder on the nets than on CoactDetect at 8 s. The unequal merge gap therefore also distorts the under-budget arm, and the report never says so.
- Separately, only the empty recordings at the quiet background gate the budget (`meta.json`: `gate_empty_recording: null_quiet`; `null_busy` is reported only). Section 2 says all 96 empty recordings are "used to count false alarms".
- **Severity:** moderate.
- **Fix:** State the interaction between merge gap and budget. Say that only the quiet-background empty recordings gate the budget.
- **Verified:** yes (`tools/tune_learned_vs_coact.py` lines 559–574 and 651–673; `meta.json`).

**M8.** Constants: the 1.6 margin, "10 consecutive recordings", "last two … pick its threshold", and the Nadeau–Bengio "one third".
- **Issue:**
  - 1.6 is declared rather than justified, and no sensitivity is shown, yet it decides the entire under-budget column: four coded detectors inadmissible, nets −0.03.
  - Why nets fit 10 of 72 training recordings and choose their threshold on 2 is never justified. This is a large handicap for the nets, and the answer paragraph never says which way it cuts.
  - The Nadeau–Bengio test/train ratio of one third is right for the coded side but not for the nets, whose fitting set is 10 recordings.
- **Severity:** moderate.
- **Fix:** Justify each constant or state it as arbitrary. Show F1 under the budget at, for example, margins of 1.2 and 2.0. Put "nets fit 14% of the training data and set thresholds on 2 recordings; this handicaps the nets" in the answer.
- **Verified:** partly. The constants are confirmed in `meta.json`; I ran no sensitivity analysis.

**M9.** "Under the budget, 4 coded detectors have no admissible result … the budget forced them into stricter settings that lose events everywhere".
- **Issue:** LoCo's crowded-check reference is goal 1's sliding setting, and that setting is itself over the budget: 16–19 false alarms per hour in the probe, against a limit of 13–16. Any LoCo setting inside the budget must be stricter, so it will fail a check benchmarked against a reference outside the budget. On top of that, the coarse grid moves LoCo from about 17 per hour to 2–4 per hour in a single step. "Not admissible" is partly produced by stacking the two rules and by grid coarseness, not only by the detector. SPIKE-synch and rate+context also drop from 60–280 per hour to 1–5.
- **Severity:** moderate.
- **Fix:** State that the reference is over the budget and that the grid is coarse. Qualify "no admissible result" accordingly.
- **Verified:** yes (`selections/*/outer*/loco.json`, `inner_probe_per_hour`; `meta.json` budgets).

**M10.** Section 4.5 and Table 3: CoactDetect passes the crowded-recording check "8 of 8", and "scored against [shipped defaults], no verdict changes".
- **Issue:** Three points:
  - **The check cannot see the 8 s gap.** CoactDetect's reference already uses 8 s. The crowded recordings are spaced at median 43 s, minimum 6 s, so an 8 s gap is barely exercised.
  - **No file backs the shipped-defaults sentence.** `crowded_check.json` holds only the base-reference comparison.
  - **It does hold for CoactDetect.** I checked: shipped CoactDetect (binned, alpha 1e-4, context 60 s, default 3 s gap) scores a crowded mean of 0.808 (0.860 quiet, 0.755 busy), so its choices at 0.820–0.837 pass.
- **Severity:** moderate.
- **Fix:** Write the shipped-defaults comparison to `crowded_check.json`. State what the check can and cannot detect about gaps under about 10 s.
- **Verified:** yes. I scored it with `search_all_settings._job`, `TAIL`, seeds 1–12.

**m11.** "Exceeding the budget can only help a net's F1 under the budget".
- **Issue:** Nothing mechanically links the two: F1 excludes the probe and the empty recordings. The comparison also mixes denominators ("1 of 4 folds" against "4 of 20 refits").
- **Severity:** minor.
- **Fix:** Rephrase as "reflects a more liberal operating point, which tends to favour the net". Use one denominator.
- **Verified:** yes (code).

**m12.** "The best net".
- **Issue:** The best net is picked from 4 using held-out means, which is optimistic for the net side. In the replicate, the best net on F1 alone is chorus_gain_norm.
- **Severity:** minor.
- **Fix:** Say so once.
- **Verified:** yes.

**m13.** Section 4.5: "the nets within 0.001 F1".
- **Issue:** The maximum reproduction difference is 0.0015, in 5 of 160 refits, and the cause is unexplained.
- **Severity:** minor.
- **Fix:** Write "within 0.002" and give the cause.
- **Verified:** yes (`merge_gap.json`, `reproduces_run`).

**m14.** Figure 5B.
- **Issue:** The nets are drawn from 2 to 16 s; the coded detectors from 0 to 30 s. CoactDetect's 0.803 at 30 s sits where no net was tried, so the picture invites a comparison the data cannot make.
- **Severity:** minor.
- **Fix:** Extend the nets to 30 s, or clip the coded curves to 16 s.
- **Verified:** yes (read the render).

**m15.** Section 5: "A difference between the two runs is then a difference between draws of data".
- **Issue:** The replicate also ran on another workstation and GPU. Section 7 itself says that can move F1 by an unmeasured amount.
- **Severity:** minor.
- **Fix:** Add "and of device".
- **Verified:** yes.

**m16.** Answer paragraph: "it was not re-scored at matched gaps (section 5)".
- **Issue:** Section 5 does not mention matched gaps.
- **Severity:** minor.
- **Fix:** Correct the cross-reference.
- **Verified:** yes.

**m17.** Section 7, contamination.
- **Issue:** "Every value moved by less than its own bootstrap interval" has little power to detect an effect on 0.03% of events, yet it reads as reassurance. "The project lead's brief … asked for exactly that" cannot be traced to any file in the tree, and CLAUDE.md says a known contamination stops the work rather than becoming a caveat. The compliance question belongs to other roles; I flag only the power of this check.
- **Severity:** minor.
- **Fix:** Drop the bootstrap sentence or state its power. Cite the brief.
- **Verified:** partly. I found no source for the brief.

**m18.** Section 4.2, the fold-draw check.
- **Issue:** "Distinct" means only that the sets are not identical. Neighbouring outer folds share 3 of 5 fitted seeds at training seed 0, which Figure 3B shows.
- **Severity:** minor.
- **Fix:** Quantify the overlap.
- **Verified:** yes (`fold_draws.json`).

**m19.** "Refits below 0.2 F1".
- **Issue:** Training failure is listed case by case, not as a rate. Across both runs it is 4 distinct failed trainings in about 420 refits (roughly 1%), all in chorus nets, plus runs with zero calls. "The cut falls in an empty stretch" holds for this run only: the replicate's lowest refit above 0.2 is 0.388.
- **Severity:** minor.
- **Fix:** Give the failure rate for both runs and treat it as a property of the nets.
- **Verified:** yes.

**m20.** Table 2.
- **Issue:** t statistics are printed for rows the report calls not admissible (e.g. −67.5). They are noise.
- **Severity:** minor.
- **Fix:** Drop them or grey them.
- **Verified:** yes.

## What the pictures show
- **Figure 1:** supports the text.
- **Figure 7:** supports the text.
- **Figure 8:** the replicate diamond contradicts the blue dots, and the caption says nothing about it (B2).
- **Figure 5B:** supports the reversal only for the choice on F1 alone; there is no panel for the budget arm (B1). Its range is asymmetric (m14).
- **Figure 3B:** shows the overlap that "four different sets" glosses over (m18).
- **Figure 4:** a schematic standing in for data that exist (M6).

## What I checked and found correct
- Every per-fold number in the four tuned-minus-untuned lists.
- The +0.010 (4 of 4) and +0.009 (3 of 4) matched-gap figures.
- Binned SCE at 8 s = 0.587, and 30 s at the top of its grid.
- CoactDetect over the budget in 1 of 4 folds.
- The Nadeau–Bengio factor 0.65 (= √(3/7)) and t₀.₉₇₅,₃ ≈ 3.18.
- Job counts: 1,963 = 1 + 24 + 1,728 + 210.
- The +0.103 earlier lead is sourced to `docs/goals/learned-model-family.md`.
- Probe calls are excluded from precision, as stated (`bench.pool_scores`).

## Sources
- Run summaries: `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\` (`results.json`, `merge_gap.json`, `replicate_summary.json`, `crowded_check.json`, `fold_draws.json`, `meta.json`, `selections\`)
- `%USERPROFILE%\runs\fair-comparison-2026-09-18\scores\` and `fits\`
- `<darkroom>\bugarach\2026-09-18-replicate-run-status\results\results.json`
- `%USERPROFILE%\bugarach\bugarach-worktrees\tune-bench-comparison\tools\tune_learned_vs_coact.py`
- `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\src\bugarach\score.py` and `bench.py`
- `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\tools\crowded_check_fair_comparison.py`
- `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\tests\test_tolerance_curve.py`
