GRANT 1 ok — Read, Grep, Glob, Bash

# Role 1: claim and data verifier. Blind round 3 of report.html (blob 9a99a7a4)

## Summary

I rebuilt the report's numbers from the raw run files. That covers both draws' `results.json`, `meta.json`, `selections/` and `configs/`, every per-recording score file, and every fit record in `fits.zip` and `fits.tar.gz`. It also covers both matched-merge files and the rehearsal's `results.json`. I used my own scripts and did not import the generator.

- **Every result number reproduces:** Tables 1–6, the between-draw statistics, the t-tests, the matched-merge claims and the figure labels.
- **Figure 1's call-level claims reproduce:** I reran CoactDetect on seed 2000 quiet and got 20 calls, 14 hits and 6 false alarms, with 4 false alarms on distractors and 2 distractors inside matched calls.
- **The findings are in the hand-written prose.** Two descriptions state things the project's own sources explicitly withdraw. One figure caption is contradicted by the data. A few smaller claims are imprecise.

## Findings

Format: location · issue · severity · suggested fix · verified against a source.

1. **§3, the description of tube** ("tube counts distinct active cells within a pool of about a second and integrates that count over time")
   - **Issue:** this repeats a claim the code has withdrawn. The `tube.py` docstring (lines 61–73, branch replicate-run) says: "distinctness is NOT delivered, and this docstring used to claim it was … It caps nothing … two such cells score 0.997 and fire — level with four genuinely distinct cells at 0.998 … do not assert it."
   - **What tube actually does:** it widens each onset by a max-pool, averages over cells, and applies a zero-integral difference-of-Gaussians (centre-surround) kernel. It also has a raw-brightness bypass channel.
   - **Severity:** major.
   - **Fix:** "tube widens each cell's onsets to about a second, averages them over cells, and compares that against its own surround with a centre-surround kernel. It does not count distinct cells: two bursting cells score like four distinct ones."
   - **Verified:** yes.

2. **§2, the fast and slow streams** ("which differ in how an event's duration is measured")
   - **Issue:** the project has withdrawn this wording. `docs/export_folder_spec.md` lines 382–388 say the difference is an export step, and "Anything that describes it as 'the two streams are measured differently' is wrong." `docs/FOUNDATIONS.md` line 352 says the same: "Fast/slow duration: an export step, not two measurements."
   - **Severity:** major. It is the definition a new reader takes away.
   - **Fix:** drop the clause, or say "for which the export records event duration by different rules".
   - **Verified:** yes.

3. **§3, the description of chorus_norm** ("standardizes each cell's trace … passes every cell through one shared encoder")
   - **Issue:** the order is reversed. The code standardizes each cell's encoder *output* over time, after the shared encoder and before the vote (`chorus.py` lines 104–107; registry note "each cell's encoder output standardised over time before the vote").
   - **Severity:** minor.
   - **Fix:** "passes every cell through one shared encoder, standardizes each cell's output over time ('norm'), and bounds it to a vote".
   - **Verified:** yes.

4. **§3 and Table 7** ("Goal 1 … chose these values on 96 other bench recordings (seeds 1–96)")
   - **Issue:** goal 1 chose on seeds 1–48 and only re-scored on 49–96 (`search_all_settings.py` stage 3 on opt-every-knob-run; HANDOFF-coded-detectors.md line 200, and "Held out on 48 recordings the search never saw"). Also, by this report's own convention (one seed = one recording per background), seeds 1–96 are not 96 recordings.
   - **Severity:** minor.
   - **Fix:** "chose them on bench seeds 1–48 and confirmed them on seeds 49–96, none of which is used here".
   - **Verified:** yes.

5. **Figure 9 caption** ("A triangle at the left edge is a fold below −0.15, where a net's training failed")
   - **Issue:** one triangle is not a failed fold. Second draw, tube, under the budget, fold 0 sits at −0.164 (`comparisons.gated["tube - coact"].per_fold[0]`). None of its refits has `failed_training_signature` or `f1_was_nan`; the refit F1s are 0.638, 0.648, 0.617, 0.388 and 0.649. The other four folds below −0.15 are flagged ones.
   - **Severity:** minor.
   - **Fix:** name the exception in the caption, or extend the axis to −0.17.
   - **Verified:** yes.

6. **§9, "At a matched merge"** ("merging can only lower a detector's call counts, so every budgeted choice stays within its ceilings")
   - **Issue:** the argument holds only at gaps at or above each side's own gap. CoactDetect ran at 8 s, so re-decoding it at 2 s and 4 s un-merges its calls. Separately, Table 3 shows some budgeted choices already broke their ceilings on held-out recordings, so "stays within" is loose.
   - **What I measured:** second draw, fold 0, held-out. At 8 s my rerun reproduces the run's own rates (dense stretch 10.0 and 7.0 calls/hour, empty recording 6.33 calls/hour). At 2 s the empty recording rises to 6.56 calls/hour against a ceiling of 8.65, and the dense stretch is unchanged. So the conclusion holds in that fold; the stated reason does not cover it.
   - **Severity:** minor.
   - **Fix:** restrict the sentence to gaps at or above a side's own, and state the measured CoactDetect rates at 2 s and 4 s.
   - **Verified:** partly (one fold of one draw).

7. **Abstract** ("the closest learned model still trailed under the cap, by half to three-quarters as much")
   - **Issue:** the body's 28%–57% closure leaves 43%–72% of the gap, and the lower end is below half.
   - **Severity:** minor.
   - **Fix:** "by two-fifths to three-quarters as much".
   - **Verified:** yes.

8. **§9, "Where the as-run gap is"** ("chorus_gain_norm found as many planted events as CoactDetect")
   - **Issue:** in the first draw it found more: 6,444 of 7,200 events (0.895) against CoactDetect's 0.856.
   - **Severity:** minor.
   - **Fix:** "at least as many".
   - **Verified:** yes.

9. **§11, first draw's matched-merge path** (`docs/learned/tuned_vs_coact/fair_comparison_2026_09_18/merge_gap.json`)
   - **Issue:** no branch is given, and the file is not on origin/main. It exists only on origin/nets/fair-comparison-report.
   - **Severity:** minor.
   - **Fix:** add "(branch nets/fair-comparison-report)".
   - **Verified:** yes.

10. **References, the CICADA entry**
    - **Issue:** the year is missing. `docs/handoffs/2026-08-28-deploy-notes-2.md` identifies this DOI as v1.0.3, 20 July 2020. The project's own `learned_detector.html` also warns that this version DOI's release does not contain the method.
    - **Severity:** minor.
    - **Fix:** add 2020 and the version, or pin a revision.
    - **Verified:** yes.

11. **§10, outside my scope (for the main thread to route)**
    - **Issue:** the bench was fitted to the contaminated `steps_excluded` folder, and the report presents that as a disclosed limit. CLAUDE.md says a known contamination "stops the work. It does not become a caveat." The report's facts are correct: 83 of 264,075 events is 0.031%; 7 of 8 constants did not move; the item is decision 3 in the slow-comodulation handoff. HANDOFF-workstation-tuning.md says "Consequences for goal 2: none."
    - **Severity:** not assigned (a question about process, not a false claim).
    - **Verified:** yes.

## Claim ledger: what was recomputed and matches

Each row gives the quoted value, the source it was checked against, and the result.

**Tables**
- **Table 1:** all 60 means, and every † and ‡ placement. Source: `results.json` for both draws. Match.
- **Table 2:** 146 and 153, 75 and 75, 8 and 11, 7 and 6 of 432, plus the one partial tube fit. Source: inner fits' `own_index` rows in both score archives. Match.
- **Table 3:** net refit counts recomputed per refit against the `meta.json` ceilings (4/3, 7/5, 3/1, 11/7). Coded: CoactDetect 1 of 4 in the first draw, binned SCE 1 of 4 in the second, locust 4 of 4 in both. Match.
- **Table 4:** grid tops 8, 8, 8, 30, 16 frames and 2 s, from `meta.hand_axes`. The started/moved split comes from the `moves` lists: rate+context 3→8, SCE nan→30, locust 4→16, SPIKE-synch 0.5→2, CoactDetect and LoCo never moved. Match.
- **Table 5:** all 64 cells and the "left out" counts. Source: both merge files, excluding folds with flagged refits. Match.
- **Table 6:** all 16 recall and precision values, with precision = hits / (calls − dense-stretch calls), per `bench.BenchResult`. Match.

**Sections 1 to 8**
- **Figure 1:** 20 calls, 14 hits, 6 false alarms, 0 in the dense stretch, 4 false alarms on distractors, 2 distractors inside hits. Source: my rerun of CoactDetect on quiet:2000 plus the score file. Match. CoactDetect's 0.75 dense-stretch calls per recording (second draw) also matches.
- **§2 bench constants:** 33 ROIs, 2,700 s, 0.0052 and 0.019 (the 25th and 75th percentiles, per the `bench.REGIMES` docstring), 5×3 events, 10/6/3 cells (`matlab_round`), 0.36 s, 120 s apart, 6 distractors at 0.18 placed independently of the events, dense stretch 1,200–1,500 s, empty twin at seed + 100,000. Practical ceiling 15/21 gives F1 0.833. Match.
- **§3 and Table 7 settings:** reference 2 s / 120 s / α = 1e-5 / 1 s guard / 8 s merge. Parameter counts 1,149 / 1,233 / 1,897 / 1,905 (fit records). 24 configurations, the same in both draws. 20 frames × 0.1 s = 2 s merge; 4,096-frame crop; 10 training plus 2 threshold recordings. Match.
- **Refits and training time:** 40–60 refits per net (fit roles: 60/40/55/55 and 55/55/50/55). 1,943 fits in 13.2 h and 1,938 fits in 12.7 h. The difference is fully accounted for: 1,728 inner fits plus 210 or 215 refits. Match.
- **§5 and Figure 4:** ceilings 16.5 / 12.8 / 8.65 = 1.6 × 10.3 / 8.0 / 5.41. Binned SCE 21–33 and CoactDetect 2–6 calls per hour on the busy empty recording. Match.
- **§6:** the declarations differ only in `recording_seeds` and `replicate` (absent in the first draw). The code diff between e8764aa and 7a95e8a touches only the `--replicate` option, a test and a handoff. Rehearsal margins +0.011 and +0.016. Its 240 s context, three settings and do-not-quote note are all in its README. Match.
- **§7:** CoactDetect 0.748 in both draws, gated equal to ungated in every fold. It moved from the reference settings in 3 of 4 folds in the first draw and 0 in the second. SCE minus CoactDetect +0.023 and 0.000. Match.
- **§8:** fold 1 collapse at 2 of 5 refits, F1 0.125, fold mean 0.501 against 0.745 untuned. Figure 7's configuration is the same in both panels. 2 chorus_gain_norm collapses, 3 no-call refits. locust 449–527 against ceilings of 15–18 calls/hour, with 16 of 16 settings refused; SCE fold 2 refused 26 of 26. Match.

**Section 9 onward**
- **Between-draw moves:** medians 0.010 and 0.006, maxima 0.027 and 0.023, 7 of 8 nets rose, 7 of 9 coded did not. The "about 0.018" is a difference of means; the median-based figure is 0.017, which is fine. Match.
- **Headline gap:** 0.030 (SD 0.005) and 0.025 (SD 0.018). t = −13.02 (p = 0.001) and −2.77 (p = 0.070). The gap moved 0.005 between draws. Match.
- **Other margins:** on F1 alone −0.007 and −0.029; within 0.029 on unflagged folds; untuned −0.012 and +0.006. Tuning: +0.032, +0.029, +0.005 and −0.063. Match.
- **Matched merge:** CoactDetect 0.733 / 0.748 / 0.797; 6 refits off by at most 0.0015; 28%–57% of the gap closes; below zero in 8 of 8 folds; the chorus models lead by 0.005–0.022; 11 of 13 folds ahead at 8 s. Match.
- **Figure 11:** 9.1 and 7.6 against 6.4 and 6.0 false alarms per recording. chorus_gain_norm and line_length show the pattern, chorus_norm does not in the second draw, and tube calls more in the dense stretch. Match.
- **Sources quoted in the history:** 30–36% calls lost (forks.md §14: 64% and 70% kept); 0.03% of events; participation 0.1905 against 0.18; the 1.6 margin (7.0 / 4.4); 8 s checked on crowded events 6 s apart; tube tied CoactDetect untuned; chorus models not on main; FOUNDATIONS §9 on the opposite direction of the fast and slow streams under tetrodotoxin (TTX); Cossart 2003 interval reshuffling; Cecchini 2021; the radar CFAR (constant-false-alarm-rate) resemblance. Match.

**Record of design and unit membership.** The source of record is each draw's `meta.json` declaration. The unit counts reconcile: 48 seeds per draw, 12 per fold, 96 held-out recordings per coded entry and 480 per net (96 × 5 refits). The two draws share no seed and no empty twin. Both passed `fold_check` (`distinct: true`, no problems). The quiet and busy recordings of one seed have different event schedules (checked on seed 2000), so they are not duplicates. There are no withdrawn units, since this is a simulation. `errors` is empty in both runs. The only missing (NaN) values are the 3 no-call refits, and the report states them.

**Could not verify:** the parenthetical saying CoactDetect's Gaussian tail makes the true chance-call rate higher; Figure 3's line that an over-budget start first moves toward the ceilings; and the matched-merge budget claim beyond the one fold I measured.

## Files
- Artifact: `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\docs\learned\tuned_vs_coact\replicate1\report.html`
- Code behind findings 1 and 3: `%USERPROFILE%\bugarach\bugarach-worktrees\weekend-runs\src\bugarach\learn\nets\tube.py`, `...\nets\chorus.py`
- Spec behind finding 2: `%USERPROFILE%\bugarach\bugarach\docs\export_folder_spec.md` (lines 382–388)
- Scratch files, not in any repository: `<session-scratch>\scratchpad\r3_text.txt`, `r3_draw1.pkl`, `r3_draw2.pkl`
