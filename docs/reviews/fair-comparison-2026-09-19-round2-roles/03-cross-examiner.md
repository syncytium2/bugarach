<!-- Verbatim role report, except that this machine's absolute paths are written as %USERPROFILE% and <darkroom> (the repository is public). The unedited original is in <darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-roles-round2/. -->

GRANT 3 ok — Read, Grep, Glob (I also hold SubagentHandback, which only delivers this report. I hold no Edit, Write or NotebookEdit.)

# Role 3, Cross-Examiner: findings on report.html (hash 16ac704)

**Scope.** I checked every number in the text, Tables 1–3 and the figure captions against the run files: results.json, meta.json, crowded_check.json, merge_gap.json, fold_draws.json, replicate_summary.json and ran.json. I also checked Figures 5, 7 and 8 against the round-2 renders. Companions checked: docs/GLOSSARY.md, docs/goals/{README, learned-model-family, coded-detector-optimization}.md, HANDOFF-coded-detectors.md, HANDOFF-slow-comodulation-on-the-de-pinned-export.md, docs/INDEX.md and src/bugarach/bench.py (TAIL_RECORDING).

**What reconciles (no finding):**
- **Table 2:** all 40 means and differences match. Every *t* matches, and the corrected *t* matches at the exact factor 0.6547.
- **Page text:**
  - Tuned minus untuned per fold and means.
  - Budget exceedances per fold (0,0,1,3 / 2,2,0,3 / 1,0,1,1 / 1,4,5,1).
  - CoactDetect over budget in 1 of 4 folds.
  - The two refits below 0.2 (fold, seed, selection, 0.125 and 0.000).
- **Merge-gap numbers:** 0.731, 0.748, 0.803, 0.741, 0.775, 0.587, +0.010 in 4 of 4 folds, +0.009 in 3 of 4 folds, and nets reproducing within 0.001.
- **Table 3:** every range and pass count, the 7 of 8 failures, and "fold 4 under the budget".
- **Table 1:** grid counts match meta.json (49/10, 39/7, 46/10, 19/4, 46/10, 47/10), and the nets' 5/6/5/5 settings.
- **Fold draws (Figure 3):** "2 distinct" before the fix and "4 distinct" after, with seeds 1000–1004 shared by folds 2–4.
- **Job counts:** 1 + 24 + 1,728 + 210 = 1,963 jobs, all "ok" in ran.json, and n_fits = 1,938.
- **Figure 8:** the dots and replicate diamonds match. The two right-of-zero margins (0.0001, 0.0004) are correct.
- **Figure 7:** hollow circles and the × marks match Table 3.
- **Fold numbering:** 1-based everywhere on the page, and the Figure 2 caption discloses it.
- **Category order:** nets, coded detectors, selections, folds and backgrounds are in the same order in Table 1, Table 2, Table 3, Figure 7, Figure 8 and every list.
- **Terminology:** no banned words ("modality", bare "adaptive").
- **Goals page:** the +0.103, tube's tie, decisions 2, 3, 4, 6 and 7, and the e8764aa launch all match.

## Findings

(location · issue · severity · suggested fix · verified?)

1. **§4.5 first paragraph and Figure 5 caption vs Figure 5 panel B.**
   - **Issue:** The text says a wide merge gap "loses nothing", and the caption says merging "costs nothing" on this bench. Panel B shows two nets losing F1 as the gap widens:
     - line_length: 0.705 at 2 s → 0.680 at 4 s → 0.660 at 8 s → 0.674 at 16 s. This comes from collapses in fold 3 (0.694→0.600 at 8 s) and fold 4 (0.712→0.597 at 4 s).
     - tube: 0.631 → 0.615 at 8 s. Fold 2 drops 0.627→0.534.
   - The prose never mentions this. It also bears on the claim that re-tuning the nets' gap "would settle it" and "needs no retraining".
   - **Severity:** medium.
   - **Fix:** Limit "loses nothing" to the coded detectors and to chorus_norm and chorus_gain_norm. Add one sentence naming the line_length and tube drops, and say they come from single folds.
   - **Verified:** yes, merge_gap.json nets.*.f1_mean_by_gap.

2. **Terms paragraph (line 54) vs §4.3 and §4.5 (line 219).**
   - **Issue:** The terms paragraph says goal 1 "settled the values this run starts them from", which reads as all six detectors. §4.3 and §4.5 say only CoactDetect and LoCo start from goal 1's values, and the other four start from the project's defaults (meta.json coded_base holds only coact and loco).
   - **Severity:** medium.
   - **Fix:** "...and settled the values this run starts CoactDetect and LoCo from."
   - **Verified:** yes.

3. **§4.5 (lines 212–214), the crowded recordings.**
   - **Issue:** They are called "24 bench recordings with 180 events each... median 43 s". §2 has just defined a bench recording as 45 minutes. 180 events with a 43 s median gap cannot fit in 45 minutes. The recordings are bench.TAIL_RECORDING, which lasts 3 hours ("180 / 3 h", bench.py line 942).
   - bench.py also says the tail's aggregate crowding is "above anything observed, on purpose". The page says the recordings are "spaced as the crowded end of real recordings is", which overstates the match; only the 6 s floor is fitted to the real tail.
   - **Severity:** medium.
   - **Fix:** "24 three-hour crowded recordings with 180 events each... a 6 s floor fitted to the real tail's minimum gaps; crowded overall beyond any real recording, on purpose."
   - **Verified:** yes, bench.py lines 914–945.

4. **"admissible": Table 2 notes, Figure 7 legend and caption, §6 bullet 5.**
   - **Issue:** The word is used for two different tests and never defined on the page:
     - failing the crowded check: "4 of 4 not admissible" for binned SCE on F1 alone;
     - the budget refusing every setting: locust's "no admissible setting" and Figure 7's ×.
   - The §6 bullet "4 coded detectors have no admissible result" mixes three crowded-check failures with one budget refusal.
   - The glossary reserves the word: "A result is admissible if it was chosen within the budget and passes the crowded-recording check." Under that definition no F1-alone result can be admissible, so "4 of 4 not admissible" on the F1-alone side misuses the reserved word.
   - **Severity:** medium.
   - **Fix:** Use the glossary definition and define it on the page. On the F1-alone side write "fails the crowded check" instead of "not admissible". Keep "no admissible setting" for the budget case only, or split the §6 bullet into its two causes.
   - **Verified:** yes, GLOSSARY.md line 350.

5. **Refit counts: "Of the 210 held-out refits" (§6) vs "80 held-out refits of nets chosen under the budget".**
   - **Issue:** These use two counting bases.
     - 210 counts unique fits: 42 (net, fold, configuration) triples × 5 seeds.
     - Scored rows number 240: untuned, F1 alone and under the budget, each 80. The "80" is on this basis.
   - A fit shared by two selections is scored at two thresholds. Examples: chorus_norm fold 2 is shared between F1 alone and under the budget (different F1s), and chorus_norm and tube fold 1 are shared between untuned and F1 alone. "Every other refit scored..." is therefore ambiguous.
   - The page also never says the untuned configuration is refit, which is how 210 arises.
   - **Severity:** medium.
   - **Fix:** Pick one basis. For example: "Of the 240 held-out scores (210 distinct refits; a refit two selections share is scored at each one's threshold)". Also state that the untuned configuration is refit at the same 5 seeds.
   - **Verified:** yes, results.json config_keys and ran.json (210 outer jobs).

6. **Table 3 "crowded F1 of the setting it replaces" vs goal 1's own record.**
   - **Issue:** For the identical CoactDetect reference (alpha 1e-5, context 120 s, merge 8 s, guard 1 s, sliding), the page gives 0.826 and LoCo 0.834. The goal 1 page (line 78) and HANDOFF-coded-detectors.md (line 325) record crowded 0.818 and 0.827 for the same settings.
   - The tool's docstring says it scores "exactly as goal 1 does" (N_TAIL = 12), and the page says it "uses goal 1's own scoring".
   - **Severity:** medium.
   - **Fix:** Reconcile before publishing: find which seeds, regime or base differ, or state why the two numbers differ. Otherwise drop "goal 1's own scoring".
   - **Verified:** partly. The discrepancy is verified; the cause is not.

7. **Lede ("agrees that no net is ahead"), §5 and Figure 8's replicate diamonds.**
   - **Issue:** The statement is true of the replicate's means only. chorus_norm's F1-alone replicate mean (−0.057) is set by one fold at −0.243 (that fold's net mean is 0.501, a collapse of the kind the page flags in its own run). In the other three replicate folds chorus_norm is ahead of CoactDetect (+0.003, +0.003, +0.007). This run has it behind in 4 of 4.
   - The per-fold replicate result is closer to the page's "does not settle it" than "agrees" implies.
   - **Severity:** medium.
   - **Fix:** Add a clause: "on the replicate's means; one replicate fold holds a collapsed refit, and without it chorus_norm leads in the other three folds by under 0.01."
   - **Verified:** yes, replicate_summary.json.

8. **§7 "Chosen values at the top of their grid" limit.**
   - **Issue 1:** It says this is "every coded detector with one (Table 3)". rate+context under the budget chose 3 s, which is not the top.
   - **Issue 2:** "a search might have gone further" is contradicted for CoactDetect and LoCo by goal 1. HANDOFF-coded-detectors.md line 326 says the axis "was extended to 16 s and the crowded veto refused it".
   - **Severity:** low.
   - **Fix:** "every coded detector with one, except rate+context under the budget". Add that goal 1 bracketed CoactDetect's and LoCo's merge gaps at 8 s.
   - **Verified:** yes.

9. **"defaults" vs operating point (§4.3, §4.5 line 219–221).**
   - **Issue:** The page calls bench.OPERATING_POINTS "the project's defaults". The glossary separates operating points from signature defaults.
   - The pair "the project's defaults for the others. Goal 1 compares against the project's shipped defaults instead" reads as the same thing twice. The intended difference is that goal 1 compares CoactDetect and LoCo against their shipped binned operating points (HANDOFF line 331).
   - **Severity:** low.
   - **Fix:** Use "operating points (bench.OPERATING_POINTS)", and say "goal 1 compares CoactDetect and LoCo against their shipped binned operating points instead".
   - **Verified:** yes.

10. **§2 line 80, "a simulator whose settings are measured".**
    - **Issue:** The glossary's generator spec entry says "Never 'simulation settings'".
    - **Severity:** low.
    - **Fix:** "whose generator spec is measured from real baseline recordings", or "whose inputs are measured".
    - **Verified:** yes.

11. **§6 "each *t* multiplied by 0.65".**
    - **Issue:** The factor used is √(3/7) = 0.6547. A reader multiplying by 0.65 gets LoCo under the budget −23.5 × 0.65 = −15.3, but the table shows −15.4.
    - **Severity:** low.
    - **Fix:** Write "0.655 (√(3/7))".
    - **Verified:** yes, by recomputing every row.

12. **"every other refit scored at least 0.51".**
    - **Issue:** The lowest is 0.5095 (tube, fold 3, under the budget), which is below 0.51.
    - **Severity:** low.
    - **Fix:** "at least 0.50".
    - **Verified:** yes, results.json line 4622.

13. **Lede "it was not re-scored at matched gaps (section 5)".**
    - **Issue:** §5 does not say this. The cross-reference points to a section that lacks the caveat.
    - **Severity:** low.
    - **Fix:** Add the sentence to §5, or point the reference at §4.5 or §6.
    - **Verified:** yes.

14. **"Choices that exceeded the budget on new data": the coded side.**
    - **Issue:** Only CoactDetect (1 of 4) is named. locust's fallback exceeded the budget in 4 of 4 folds (results.json cicada gated over_budget true ×4). No other coded choice exceeded it.
    - **Severity:** low.
    - **Fix:** "no other coded choice did, apart from locust's starting point, which the budget had already refused".
    - **Verified:** yes.

15. **Lede and §6 "4 of 4 folds" at 2 s.**
    - **Issue:** Fold 4 is +0.0004 (0.7179 vs 0.7175), which is below the page's own 0.001 re-decode tolerance. Figure 8's caption does disclose margins that small.
    - **Severity:** low.
    - **Fix:** "4 of 4 folds, one by 0.0004".
    - **Verified:** yes.

16. **§3 "untuned, it scores 0.629 against CoactDetect's 0.748".**
    - **Issue:** This compares untuned tube with tuned CoactDetect. The earlier tie was measured on a different basis.
    - **Severity:** low.
    - **Fix:** "against tuned CoactDetect's 0.748".
    - **Verified:** yes, the 0.629 recomputes from results.json.

17. **Table 1 "24 configurations drawn at random".**
    - **Issue:** In every net's list in meta.json the untuned key is the 24th entry. That suggests 23 random draws plus the untuned configuration.
    - **Severity:** low.
    - **Fix:** "23 drawn at random plus the untuned one", if that is how the draw works.
    - **Verified:** partly. The position is verified; the draw rule is not.

18. **Provenance line.**
    - **Issue 1:** `docs/reviews/fair-comparison-2026-09-19.md` does not exist in the worktree yet.
    - **Issue 2:** The page says it was built at g2ca264e while the artifact is 16ac704.
    - **Severity:** low.
    - **Fix:** Land the review record in the same change. Rebuild at the committing hash, or confirm the builder did not change between the two.
    - **Verified:** issue 1 yes; issue 2 no.

19. **Glossary merge gap vs the page.**
    - **Issue:** The glossary says the nets' merge gap is "fixed at 20 frames". The page says 2 s and gives no conversion.
    - **Severity:** low.
    - **Fix:** Add "(20 frames)" once in §4.5.
    - **Verified:** no (frame interval not checked).

## Informational (companion docs, not artifact defects)

- **docs/goals/README.md decision 3** still says the bench values "do not yet come from `steps_excluded`". HANDOFF-coded-detectors.md step 1 (2026-09-17) says they now do. The page follows the handoff; the README ⚠ is stale.
- **CICADA citation:** GLOSSARY.md cites Hamon et al. 2026 and Zenodo. README.md "Licensing & citations" cites Denis et al. 2020. The page follows the README.
- **Order of lists across files:** no canonical detector order is declared in the glossary. Its listing (rate+context first) and meta.json's order both differ from the page's order, but the page is consistent throughout. Figure 5's end-of-line labels are ordered by value, which is acceptable for direct labels.
