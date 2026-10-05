<!-- Verbatim role report, except that this machine's absolute paths are written as %USERPROFILE% and <darkroom> (the repository is public). The unedited original is in <darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-roles/. -->

GRANT 3 ok — Read, Grep, Glob

(SubagentHandback, the channel for returning this report, is also present. It is not an editing tool, and I have no Edit, Write or NotebookEdit.)

# Role 3, Cross-Examiner: findings on the fair-comparison report

**Artifact:** `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\report.html` (built HTML, 76c3270). I read the prose lines of the HTML directly and the figures and tables from the round-1 renders.

**Checked against:**
- The run files in the same folder: `meta.json`, `results.json`, `crowded_check.json`, `fold_draws.json`, `ran.json`.
- Companion docs: `docs/GLOSSARY.md`, `docs/goals/README.md`, `docs/goals/learned-model-family.md`, `HANDOFF-coded-detectors.md`, `HANDOFF-slow-comodulation-on-the-de-pinned-export.md`, `docs/INDEX.md`.

**Counting basis pinned:** folds are 1–4 in the prose and 0–3 in the files (file = prose − 1). Refit seeds are 0–4 in the files. A recording is one (seed, background) pair.

## What reconciles (checked, no finding)
- **Table 2:** every mean and paired difference with CoactDetect, to 3 decimal places, and the *t* values for the nets (from `results.json` comparisons). I recomputed binned SCE−CoactDetect (0.023, *t* 3.1) and LoCo−CoactDetect (−0.010, *t* −13.9) by hand.
- **Section 6 tuning bullets:** they match the `ungated` "tuned − untuned" entries.
- **Table 3:** every crowded range, reference value and veto count matches `crowded_check.json`.
- **Admissibility notes:** SCE 4/4 and 3/4, LoCo 4/4 under the budget, locust. They match Table 3 and the hollow dots in Figure 7.
- **Table 1:** the settings and grid-value counts (49/39/46/19/46/47) match `meta.json` `hand_axes`. The net settings (5/6/5/5) match `learned_axes`.
- **Job counts:** 1,963 jobs, 1,938 fits, 24 searches and 210 refits match `ran.json` stage counts and `results.n_fits`.
- **Timing:** 13.7 h wall and 12.7 h training.
- **Run parameters:** seeds 1000–1047, budget margin 1.6, probe 1200–1500 s with a 30 s ramp, 33 ROIs, participation levels, jitter 0.36 s, 120 s spacing, 6 distractors.
- **Section 4.3 reference values:** match `coded_base`.
- **Section 9:** e8764aa, clean tree.
- **Failed refits:** the chorus_gain_norm refit (file fold 2 → prose fold 3) and the tube refit (file fold 0 → prose fold 1) are located correctly. The 0.125 F1 "predicts everywhere" signature is consistent with the recorded precision 1.0 and recall 0.067.
- **Figure 4 panel B:** matches `fold_draws.json`.
- **Glossary checks:** no "modality", no bare "adaptive", no singular "data". Coded detector names match the glossary. Figure 7, Figure 8 and Tables 1–3 share one order.

## Findings

Format: location · issue · severity · suggested fix · verified against a source (yes/no).

### Major

1. **Section 2, last paragraph: the recording count is on two bases.**
   - Issue: the paragraph says "This run used 96 recordings: 48 recording seeds, each at both backgrounds, plus one recording per seed with nothing planted at each background." 48×2 = 96 planted recordings, plus 48×2 = 96 empty ones (`meta.empty_recordings` null_quiet/null_busy, `twin_seeds`), so the total is 192. Figure 3's "a fold holds 24 recordings (12 seeds x 2)" counts planted recordings only.
   - Severity: major.
   - Fix: "96 recordings with planted events (48 seeds × 2 backgrounds), plus 96 with nothing planted (one per seed at each background): 192 in all." Or drop "plus".
   - Verified: yes (`meta.json`).

2. **Section 1: the probe-rate ratio is wrong.**
   - Issue: the text says "every ROI fires at 0.06 Hz, six times the quiet background rate." The quiet rate is 0.0052 Hz (`meta.backgrounds.quiet`, GLOSSARY `baseline_quiet`), so 0.06 Hz is about 11.5 times quiet. It is about 3.2 times busy (0.019 Hz). Neither ratio is six.
   - Severity: major.
   - Fix: "about 12 times the quiet background rate and 3 times the busy one." Or state the two rates without a ratio.
   - Verified: yes.

3. **Figure 8 caption: "no dot is to the right of it" is false in the data.**
   - Issue: `comparisons.ungated["chorus_gain_norm - coact"].per_fold` is [+0.00006, +0.00040, −0.153, −0.029]. Two dots (prose folds 1 and 2) sit just to the right of zero; the render shows them on the line.
   - Severity: major, because the caption states an absolute that the run's own data contradict.
   - Fix: "no dot is meaningfully right of it; chorus_gain_norm's folds 1 and 2 on F1 alone sit at +0.0001 and +0.0004."
   - Verified: yes (`results.json`).

4. **Section 4.2 heading vs Figure 4 panel A and caption: "two" folds vs three.**
   - Issue: the heading says "two outer folds were training the same model." Figure 4A on this run's split shows "held-out folds 2, 3 and 4 fit the same ten recordings", which is three folds (label: "2 distinct fitting sets for 4 held-out folds"). The body text ("held-out folds that share their first training fold trained exactly the same model") also yields three. "Two of four" is the shakedown's count (goal page decision 5; MILESTONES), carried over.
   - Severity: major.
   - Fix: "three outer folds were training the same model." Or: "outer folds were sharing a fitted model (three of four on this split; two in the shakedown)."
   - Verified: yes (Figure 4 render, `fold_draws.json`, learned-model-family.md decision 5).

5. **Section 4.1 and Figure 3 body vs section 4.2: what the refit trains on.**
   - Issue: section 4.1 and Figure 3 say the winner "is then retrained on all three training folds". Section 4.2 says a net fits only "a run of 10 consecutive recordings" plus 2 threshold recordings. `meta.training_mix` and `fold_draws.n_train` = 10 agree with 4.2, so a net sees 10 of the 72 training-fold recordings.
   - Severity: major.
   - Fix: "retrained on recordings drawn from all three training folds (for a net, 10 of their 72 plus 2 to pick the threshold)."
   - Verified: yes.

6. **Section 7.2 ("choices that missed the budget on new data"): the nets' held-out budget misses are left out.**
   - Issue: the section lists only CoactDetect (1 of 4 folds) and locust. The nets' gated refits exceeded the budget on held-out data in 25 of 80 seed-refits (`seeds_over_budget`):
     - chorus_norm: 0, 0, 1, 3
     - tube: 1, 4, 5, 1
     - chorus_gain_norm: 2, 2, 0, 3
     - line_length: 1, 0, 1, 1

     The coded side's misses are disclosed and the nets' are not, which is an asymmetric account of the same rule.
   - Severity: major.
   - Fix: add a bullet with the per-net counts, or a column in Table 2.
   - Verified: yes (`results.json`).

7. **Section 6, bullet 2 ("The earlier comparison's lead for the nets came from comparing untuned nets against a coded side tuned on one knob; with both sides tuned, it is gone"): the attribution leaves out a change the companions record.**
   - Issue: the earlier comparison (+0.103 / +0.084) ran on the retired home spec (32 ROIs, 4 folds of 6). This run uses the bench (learned-model-family.md "the simulation change … apply to the next comparison"; HANDOFF-coded-detectors §4 table, row 1). The same bullet says tuning barely moved the nets, so the lead's disappearance cannot be pinned on the tuning asymmetry alone. The simulator changed at the same time. The page never says the earlier comparison used a different simulation.
   - Severity: major.
   - Fix: say the earlier comparison was on a different, now-retired simulation, and soften "came from" to "is not reproduced once both sides are tuned on the bench".
   - Verified: yes.

8. **Figure 4 caption, last sentence: the cross-reference points to the wrong section.**
   - Issue: "Section 7 gives what the fix does not change." The residual dependence between folds (overlapping training sets) is discussed in section 6, "How much the t values can carry", and section 8 cites "(section 6)" for the same point. Section 7 does not discuss it.
   - Severity: major, because the reference leads nowhere.
   - Fix: "Section 6 gives …"
   - Verified: yes.

9. **Tables 1, 2 and 3 have no visible number.**
   - Issue: the prose cites "Table 1/2/3" eight times. The number exists only in each table's `aria-label` (lines 95, 179, 223). The renders show a bare header row, so a reader cannot resolve "Table 2" except by counting.
   - Severity: major.
   - Fix: give each table a visible caption: "Table 1. The ten contestants.", "Table 2. …", "Table 3. …".
   - Boundary: rendering or labelling that is purely mechanical belongs to agent 10. I file it here because the defect is a cross-reference that does not resolve.
   - Verified: yes (renders).

10. **Figure 2: category order differs from every other figure and table.**
    - Issue: Figure 2's rows are tube, line_length, chorus_norm, chorus_gain_norm. Table 1, Table 2, Figure 7, Figure 8 and the section 6 bullets all use chorus_norm, chorus_gain_norm, line_length, tube.
    - Severity: major (checklist: figures that disagree on category order).
    - Fix: reorder Figure 2's rows to the canonical order.
    - Verified: yes.

11. **Companion lag: `docs/goals/learned-model-family.md` does not have this result.**
    - Issue: lines 114–119 still say the run was launched and "should finish early on 2026-09-19". There is no result, no link to the report and no finish time. `docs/INDEX.md` line 106 was updated. CLAUDE.md requires the goal page to be updated in the same PR as the result.
    - Severity: major.
    - Fix: add the result, its strength (measured, one draw; replicate pending) and the link, in the same PR.
    - Verified: yes.

12. **Section 8, contamination bullet: the re-measurement claim has no source in the tree.**
    - Issue: the report says the bench was "Re-measured on the corrected folder on 2026-09-17 by both workstations, every constant moved by less than its own bootstrap interval". The only occurrence of this text in the tree is `tools/build_fair_comparison_report.py` line 855. The cited source (HANDOFF-slow-comodulation decision 3) says `bench.MEASURED_ROLE` still points at the contaminated folder, "Untouched", and that moving it "turns the suite red until the bench is re-measured". HANDOFF-coded-detectors' 13:10 status re-measured on `steps_excluded`, which is the contaminated folder.
    - Severity: major.
    - Fix: cite the record of the corrected-folder re-measurement, or remove the claim.
    - Verified: no. I searched the tree and found no record.

13. **Section 8, contamination bullet vs CLAUDE.md: a known contamination is reported as a caveat.**
    - Issue: CLAUDE.md says "A known contamination stops the work. It does not become a caveat." The report presents it as a Limit ("small; not absent"). The page does not say whether `BUGARACH_ACK_CONTAMINATION` was set, or why the stop did not apply. The bench reads fitted constants, so `dataset.current()` may never have fired.
    - Severity: major.
    - Fix: state explicitly why this run is outside the stop, or the acknowledgement it ran under.
    - Verified: partly. The rule is verified. Whether the run bypassed it is not.

### Minor

14. **Figure 3 caption and section 4.5: the fit counts cannot be reconciled from the page.**
    - Issue: "3 inner fits × 3 training seeds" per held-out fold implies 4 nets × 24 configurations × 4 folds × 9 = 3,456 fits, yet the page gives 1,728 inner fits. The real count is 4 × 24 × 3 seeds × 6 distinct training-fold pairs, because each pair serves two outer folds (`ran.json` shows 6 recording-set hashes per configuration and seed). Similarly, 210 refits is neither 160 (2 selections) nor 240 (with untuned); it reflects de-duplication, and the page never says that untuned configurations are refit.
    - Fix: one clause each explaining the 1,728 and the 210.
    - Verified: yes.

15. **Section 7.3: folds and seeds are numbered on different bases.**
    - Issue: "fold 3, refit seed 3" and "fold 1, refit seed 4" use 1-based folds but 0-based seeds (file seeds 0–4). A reader told there are "5 refit seeds" reads seed 4 as the fourth of five.
    - Fix: number seeds 1–5, or say "seeds numbered 0–4".
    - Verified: yes.

16. **Section 4.4 and Figure 5 title vs section 8: "the same fits" vs "two searches".**
    - Issue: section 4.4 says "every contestant was chosen twice from the same fits", and Figure 5 is titled "Two selections from the same candidates". Section 8 says "The two selections are two searches, not one search filtered", which is true for the coded side (the gated search visits different settings).
    - Fix: "for nets, from the same fits; for coded detectors, two separate searches (section 8)."
    - Verified: yes.

17. **Section 4.5: "24 coded-detector searches".**
    - Issue: this counts jobs (6 detectors × 4 folds). Each job runs both selections, which section 8 calls two searches, so there are 48 searches.
    - Fix: "24 coded-detector search jobs (each runs both selections)."
    - Verified: yes (`ran.json` `search/<det>/outer<n>`).

18. **Section 6, "Tuning barely moved the nets".**
    - Issue: the bullets do not say which selection they report. They are the F1-alone comparisons; under the budget, chorus_norm is −0.020 (*t* −2.0) and tube −0.035. Separately, line_length's +0.032 (*t* 2.0) is 4.5 times the 0.007 gap the page treats as the headline, so "barely" does not fit it.
    - Fix: label the bullets "on F1 alone", add the budget column, and qualify "barely" for line_length.
    - Verified: yes.

19. **Section 6, bullet 4 and section 7.1 summary: LoCo is left out.**
    - Issue: "three coded detectors fall well behind: SPIKE-synch, rate+context and locust" omits LoCo. Under the budget LoCo is inadmissible in 4 of 4 folds (0.689, −0.059), per Table 2, Table 3 and Figure 7. Section 7.1 summarises Table 3 as "CoactDetect passes … Binned SCE … does not" but not LoCo, SPIKE-synch or rate+context under the budget. LoCo's gated choice fails the veto with the same 8 s merge gap as its reference, so not every veto failure is the merge-gap artifact.
    - Fix: include LoCo, and add one sentence noting that the budget-selected choices fail the veto through high thresholds, not merges.
    - Verified: yes.

20. **Lede and sections 6 and 7.1: the 30 s merge gap is not always vetoed.**
    - Issue: the page says SCE's lead comes from "a setting that goal 1 has already ruled out" and "Binned SCE's 30 s merge gap does not [pass]". But one SCE choice (gated, prose fold 4) has the 30 s gap and passes the veto (`crowded_check.json`, 0.703 vs 0.714).
    - Fix: "fails the veto in 7 of 8 choices."
    - Verified: yes.

21. **Section 6, SCE bullet ("the top of its grid") and section 8 ("most coded detectors chose the top of their merge-gap grid (Table 3)"): the edge standard is applied selectively.**
    - Issue: CoactDetect and LoCo also chose the top of their merge-gap grids (8 s, edge flag "high" in every fold). Table 3 shows the values but not the grid tops, so the cited table cannot confirm the claim. Table 3's "— s" for locust and SPIKE-synch also hides that their merge-like settings (`max_gap` 2.0 s, `sce_min_distance_frames` 16) are at their tops too.
    - Fix: add a "top of grid?" column to Table 3, and note that CoactDetect's 8 s is also at the edge (goal 1 bracketed it at 16 s: HANDOFF-coded-detectors, 23:50 status).
    - Verified: yes.

22. **Section 7.1: the veto's reference differs from the one goal 1 declared.**
    - Issue: HANDOFF-coded-detectors (23:50 status, item 2) says goal 1's veto reference is "what a detector SHIPS at". `crowded_check.json` uses `coded_base` over OPERATING_POINTS, which for CoactDetect and LoCo is the unshipped sliding value. The verdicts probably do not change (with goal 1's binned crowded numbers, LoCo gated still fails and CoactDetect still passes), but the page calls it "goal 1's crowded veto" without noting the change.
    - Fix: one clause naming the reference.
    - Verified: partly (the crowded recording sets may differ).

23. **Glossary: new terms are not added.**
    - Issue: "probe stretch" is used where the glossary's term is **promiscuity probe**. The page also bolds and defines "bench", "outer/inner fold", "shared false-alarm budget", "crowded veto", "admissible", "nets/coded" and the net names chorus_norm, chorus_gain_norm and tube. None of these is in `docs/GLOSSARY.md`.
    - Fix: use "promiscuity probe", or add "probe stretch" as a synonym, and add the other terms in the same change.
    - Verified: yes.

24. **Figure 2 caption and Table 1: "one bounded vote" for line_length.**
    - Issue: Figure 2's caption says the three per-ROI nets each "cast one bounded vote", and Table 1 says line_length "lets each ROI vote once per moment". The glossary entry for `line` records that "votes once" was retracted on 2026-09-17: the bound is on height only, and a burst still counts as more than one onset.
    - Fix: "a vote bounded in height."
    - Verified: yes.

25. **Figure 2, chorus_gain_norm row: "as line's".**
    - Issue: this refers to `line`, a net that is not in this comparison and is not introduced anywhere on the page.
    - Fix: define it or drop it.
    - Verified: yes.

26. **Figure 7 caption: cross-references are too coarse.**
    - Issue: "(section 7)" covers two different conditions. The veto is section 7.1 and "the budget refused every candidate" is section 7.2.
    - Fix: cite 7.1 and 7.2 separately.
    - Verified: yes.

27. **Section 3: "The four nets are the ones that led the earlier untuned comparison, plus tube".**
    - Issue: this reads as four leaders plus tube, i.e. five nets. The companion shows three leaders (chorus_norm, chorus_gain_norm, line_length) plus tube.
    - Fix: "the three that led …, plus tube".
    - Verified: yes (learned-model-family.md).

28. **Section 4.5: number format.**
    - Issue: "1728" appears beside "1,963" and "1,938".
    - Fix: "1,728".
    - Verified: yes.

29. **Provenance line.**
    - Issue: "Reviewed by the eleven roles of docs/doc_review_process.md" is written into the build while review is in round 1. The build stamp reads `0.1.0+gbdbd77b.dirty`, which does not identify 76c3270, the commit the report is delivered at.
    - Fix: stamp the review status from the run record after adjudication, and build from a clean, committed tree.
    - Verified: partly (I did not check git).

30. **Section 6, bullet 4: order.**
    - Issue: "SPIKE-synch, rate+context and locust" is out of the canonical order (locust, SPIKE-synch, rate+context).
    - Fix: reorder.
    - Verified: yes.

31. **Section 5: the replicate's finish time.**
    - Issue: "finished at 07:48 on 2026-09-19" has no companion source in the tree.
    - Fix: cite the replicate's status file.
    - Verified: no.

## Relevant paths
- `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\report.html`
- `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\results.json` (comparisons at lines 7538–8215; `seeds_over_budget` at lines 2912–7533)
- `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\meta.json`
- `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\crowded_check.json`
- `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\fold_draws.json`
- `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\goals\learned-model-family.md` (lines 61–65, 109, 114–119, 138–139)
- `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\HANDOFF-coded-detectors.md` (lines 250–257, 316–335)
- `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\HANDOFF-slow-comodulation-on-the-de-pinned-export.md` (lines 126–130)
- `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\GLOSSARY.md` (lines 18–43, 330–335, 473–479)
- `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\tools\build_fair_comparison_report.py` (line 855, the only source of the re-measurement sentence)
