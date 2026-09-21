<!-- Verbatim role report, except that this machine's absolute paths are written as %USERPROFILE% and <darkroom> (the repository is public). The unedited original is in <darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-roles-round3/. -->

GRANT 4 ok — Read, Grep, Glob, Bash

Role 4 (Reviewer 2), round 3, blind pass. I reviewed the built artifact %USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\report.html. Its hash is 5c0ccbb, matching the brief. I did not open docs/reviews/* or any run record, and I edited nothing.

**What I checked:**
- The full page text.
- The rendered Figures 1, 6, 7, 8, 9, 10, 11 and 12 in renders_round3.
- Recomputations from the data: results.json (comparisons, per-refit probe and empty-recording rates, budget results), meta.json (budgets, declaration), crowded_check.json, merge_gap.json (all gaps, both selections, with t values), breakdown.json (recall by participation level, precision, distractors) and replicate_summary.json (per-fold values with failed refits set aside, and the replicate's coded detectors).
- The code that ran: tools/tune_learned_vs_coact.py (the N_TRAIN constant) and src/bugarach/learn/encode.py (how training labels are built).
- Table 2 and the section 6, 7, 8 and 10 numbers reproduce from the data, except the two small items at findings 10 and 12.

**Findings** (location · issue · severity · suggested fix · verified)

1. **§7 last paragraph, the "The answer" paragraph, Figure 10B.** The report is not even-handed about uncertainty.
   - On F1 alone, chorus_norm's matched-gap lead is t 2.8 / corrected 1.9. The page calls this "not distinguishable from a tie".
   - Under the budget, CoactDetect's matched-gap lead over chorus_norm is weaker: −0.016 to −0.020, with t −1.5 / −1.7 / −1.8 / −2.1 at 2 / 4 / 8 / 16 s (corrected about −1.0 to −1.4), and the net behind in 3 of 4 folds. The page states it flatly: "CoactDetect stays ahead of both chorus nets at every gap tried". The answer paragraph also says "it stays ahead when the nets are given its merge gap".
   - The net is also handicapped in that comparison. Its budget threshold was chosen at 2 s. A wider merge produces fewer calls, so at 8 s a lower threshold would have fitted inside the budget. That handicap favours CoactDetect.
   - Only chorus_gain_norm's deficit is consistent: 4 of 4 folds, t −4.3 to −7.1.
   - Severity: major.
   - Fix: give t and corrected t for the budget rows of Figure 10. Say chorus_norm's matched-gap deficit under the budget is at the same tie level as the F1-alone reversal. Say budget thresholds were not re-chosen at the wider gap. Soften the answer paragraph to match.
   - Verified: yes (merge_gap.json recomputed).

2. **The answer paragraph, the §4.1/§4.2 text on 10 fitted recordings, §11.** The biggest alternative explanation for the result is missing from the answer.
   - A net fits 10 of the 72 training recordings, and on F1 alone picks its threshold on 2. A coded setting is scored on all 72.
   - §11 admits "That handicaps the nets", but the answer to "once both are tuned fairly?" does not mention it.
   - The constant 10 is never justified on the page. In the code it is `CROP, BATCH, N_TRAIN = 4096, 3, 10    # the bake-off's`, inherited rather than chosen.
   - Tuning also did not demonstrably move the nets: tuned minus untuned is at most 0.035, and some are negative. So "both sides tuned" means both were searched, not that the nets reached their best.
   - Severity: major.
   - Fix: put the data handicap in the answer paragraph. Say why 10, or that it was inherited from the earlier comparison. Say plainly that the net search did not show a gain over the untuned setting.
   - Verified: yes (tools/tune_learned_vs_coact.py line 132; results.json comparisons).

3. **§10 "False alarms on held-out recordings", §4.4.** The page shows the false-alarm number that does not constrain the nets.
   - It shows probe rates: chorus nets 0 to 17 per hour, median 1, against CoactDetect 8 to 12. It concludes "a chosen net can sit anywhere under it".
   - The gate that binds the nets is the empty recordings at the quiet background. There, chorus_gain_norm's held-out refits fire 2.3 to 17.4 per hour and chorus_norm's fold-4 refits fire 20.6 to 22.9. CoactDetect fires 5.9 to 8.2, and the budget is about 10.4 to 11.5. On that gate the nets sit at or over the ceiling. The overruns listed in §10 come from there.
   - The probe is also not a fair test of the nets. They were trained on the probe itself: encode.frame_targets labels the hot window 0, and it is fixed at 1200 to 1500 s with the same rate and ramp in every recording. The coded detectors are never fitted to it. So a low probe rate for a net shows it learned that one pattern, not that it resists rate changes in general.
   - Severity: major.
   - Fix: show the rates on the quiet empty recordings beside the probe rates, and name the gate that binds. State that the nets train on recordings containing the identical probe, labelled negative.
   - Verified: yes (results.json per-seed quiet_per_hour and probe_per_hour; encode.py docstring).

4. **The answer paragraph ("Held to a shared limit on false alarms"), §4.4, §11.**
   - The "shared limit" is CoactDetect's own false-alarm rate on three gates, multiplied by 1.6. CoactDetect sits at about 1.0 times that rate on every gate by construction. A detector whose false alarms are distributed differently is capped by its worst gate. The limit is shared in name but shaped like CoactDetect.
   - The 1.6 margin was declared, not measured, and had no sensitivity check (§4.4). Yet the headline under-budget verdict rests on it, and §11 does not list it.
   - Severity: major, for the headline.
   - Fix: in the answer paragraph, say the limit is 1.6 times the reference CoactDetect's rates, taken gate by gate. Add "1.6 is a declared margin, and no sensitivity to it was run" to §11.
   - Verified: yes (meta.json budgets and budget_margin).

5. **§4.4, where the busy empty recordings are "reported but do not gate".**
   - The page gives no reason for leaving them out of the budget, and does not report their rates anywhere either.
   - It matters. Binned SCE's one admissible result (fold 4, under the budget) fires 22.7 per hour on the busy empty recordings against CoactDetect's 4.3. Across folds, binned SCE fires 23 to 33 per hour there.
   - Severity: minor to major.
   - Fix: justify the choice. Show the busy empty rates for the chosen settings, at least binned SCE's and the nets'.
   - Verified: yes (results.json quiet_per_hour for null_busy).

6. **§9 "that is its merge gap, not a better detector"; Figure 7B, as read from the image.**
   - The evidence is binned SCE re-scored at 8 s (0.587) while its other settings stay tuned for 30 s. §7 calls exactly this kind of comparison a handicap when it is applied to the nets.
   - Figure 7B, as drawn, shows the one admissible binned SCE result to the right of CoactDetect. It passes the crowded check and stayed within budget on held-out, and it scores 0.765 against CoactDetect's 0.735 in that fold (+0.030).
   - In the replicate, binned SCE under the budget is ahead of CoactDetect in 3 of 4 folds. The page does not assess whether those results are admissible.
   - Stronger evidence is available and unused: at binned SCE's own 30 s gap, CoactDetect scores 0.803 against binned SCE's 0.771.
   - Severity: major, since it is a stated conclusion.
   - Fix: make the case from the matched comparison at 30 s. Acknowledge the admissible fold-4 win. Soften "not a better detector" to "no better at a matched gap".
   - Verified: yes (results.json, merge_gap.json, replicate_summary.json).

7. **§1/§2 on distractors, and the page as a whole.** Net training uses contradictory labels, and the page never says so.
   - Distractors are "built exactly as" 18% events and cannot be told apart by construction. encode.frame_targets labels them 0 in net training, while the 5 real 18% events per recording are labelled 1.
   - So the nets are fitted to identical patterns with opposite labels. This is an alternative explanation for their ceiling and threshold behaviour that the coded side, which is only scored on these patterns and never fitted to them, does not face.
   - Severity: medium.
   - Fix: state it as a limit. Its effect was not measured.
   - Verified: the labelling yes (encode.py docstring: "Distractors and the hot window are labelled 0"); the effect no.

8. **The answer paragraph and §6/§10, "refits that failed to train are set aside".**
   - The exclusion rule is based on the held-out outcome: refits below 0.2 F1. Yet the page says the threshold picker already flags these refits before testing. That flag (failed_training_signature, threshold index 0) matches all 3 F1-alone cases exactly, so the rule can be restated without looking at the test score.
   - The "no calls" cases under the budget (tube in this run; chorus_norm fold 2 in the replicate) are not training failures. They come from a threshold chosen on the inner fits, so "failed to train" should not cover them.
   - The answer also says every setting was chosen "without looking at the recordings it is scored on". Two headline numbers do look: the best net is picked by held-out mean, and the exclusion uses held-out F1.
   - Severity: minor to medium.
   - Fix: define the exclusion by the picker's flag. Separate the "no calls" cases. Qualify the "without looking" sentence, or point to §6's admission.
   - Verified: yes (replicate_summary.json refits; results.json per_seed).

9. **The answer paragraph, "which one is ahead changes … with which recordings were drawn".**
   - The replicate changes both the recordings and the machine (§5). §11 estimates cross-machine retraining at up to about 0.02 per fold.
   - The replicate's margins are +0.003 to +0.0075, inside that estimate.
   - Severity: medium.
   - Fix: say "with the draw of recordings and the machine, which this run cannot separate".
   - Verified: yes.

10. **§8 and the answer's "the nets find more of the faintest events against a busy background".**
    - This was measured for the two chorus nets only, in one draw; there is no replicate breakdown. "The nets" should be "the chorus nets, in this run".
    - "Paid for in precision" is asserted but precision is not shown. My recomputation supports it: at the busy background on F1 alone, precision is 0.578 for chorus_norm against 0.624 for CoactDetect.
    - "Recall 0.80 or more in every fold" is strictly false: chorus_gain_norm, F1 alone, fold 3, busy background, 18% level is 0.797, and that fold holds the failed refit.
    - Severity: minor.
    - Fix: narrow the claim, show the precision values, and say "about 0.80".
    - Verified: yes (breakdown.json).

11. **§10 and Figure 12.**
    - Tuned minus untuned is shown for this draw only. The replicate's values are available: F1 alone chorus_gain_norm −0.017, line_length +0.029; under the budget tube −0.035, chorus_norm −0.097 with failed refits counted.
    - In the replicate the untuned chorus_norm is ahead of CoactDetect in 4 of 4 folds (+0.0055), with nothing set aside. That bears directly on "the +0.103 lead is gone" and on whether the net search could find anything.
    - Severity: minor.
    - Fix: add the replicate to Figure 12, or a sentence.
    - Verified: yes (replicate_summary.json).

12. **§10, "CoactDetect 8 to 12".**
    - Fold 1's probe rate, averaged over the two backgrounds, is (14 + 11) / 2 = 12.5 per hour.
    - Severity: nit.
    - Fix: write "8 to 12.5".
    - Verified: yes.

13. **§8, "Both sides also call 84% to 100% of the distractors".**
    - In breakdown.json, distractor_share_of_false_calls reaches 1.017 (chorus_norm, fold 1, quiet background). So a call counted as hitting a distractor can also be a matched true hit. The distractor metric is not defined on the page.
    - Severity: minor.
    - Fix: define what counts as calling a distractor.
    - Verified: the value yes; the mechanism no.

14. **§2, the 2.5 s tolerance.**
    - It is justified from the coded detectors' tolerance curve only. The page says so, but it is a scoring constant justified for one side of a two-sided comparison.
    - Severity: minor, residual.
    - Fix: measure the nets' tolerance curve, or list this in §11.
    - Verified: yes, from the page text.

**Summary.** Findings 1 to 4 and 6 bear on the answer paragraph.
- The under-budget headline rests on a margin with no sensitivity check (finding 4) and on a gate the page does not show (finding 3).
- The matched-gap budget comparison is held to a weaker standard of uncertainty than the reversal the page calls a tie (finding 1).
- The nets' data handicap, the most direct alternative explanation, is kept out of the answer (finding 2).
- The verdict on binned SCE rests on a handicapped re-scoring, while a stronger comparison goes unused and the figure shows an admissible fold win (finding 6).

Nothing I found contradicts the direction of the headline. What I found is that its confidence and framing overreach the evidence.
