<!-- Verbatim role report, except that this machine's absolute paths are written as %USERPROFILE% and <darkroom> (the repository is public). The unedited original is in <darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-roles-round2/. -->

GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

(I also hold SubagentHandback, the channel for this report. I hold no editing tool. I wrote no file; one computation ran as an inline `python -c` because the repo's hook blocks heredoc source files.)

# Role 6 (RTFM) report: fair-comparison report.html (blob 16ac704)

The page's arithmetic checks out, and so do the nested cross-validation plumbing and the pooling rule. The problems are in scope and mechanism. The headline reversal only holds for the F1-alone selection (finding 1). The replicate's "agrees" comes from two refits that failed to train (finding 2). The "matched" merge gap applies one number to two different operations (finding 3).

## Findings

Each row gives: location · issue · severity · suggested fix · could I verify it against a source.

**1. "The answer" paragraph; section 6, "With the merge gap matched, the order reverses"**
- **Issue:** The reversal only holds for the **F1-alone** selection.
  - Under the budget, CoactDetect beats the best budgeted net, chorus_gain_norm, in **4 of 4 folds at every matched gap**:
    - at 2 s: −0.014 (folds −0.011, −0.016, −0.022, −0.007)
    - at 8 s: −0.017
    - at 16 s: −0.017
  - It beats chorus_norm (budgeted) in 3 of 4 folds: −0.016 at 2 s, −0.018 at 8 s.
  - So "which one is ahead turns on [the merge gap]" is true only on F1 alone. The page never says this, and Figure 5B is captioned for F1 alone only.
- **Severity:** High. This is the headline's scope.
- **Fix:** Scope both sentences to "on F1 alone". Add the under-budget matched-gap result, where no net is ahead at any gap tried.
- **Verified:** Yes. I recomputed from merge_gap.json (gated rows for coact, chorus_norm, chorus_gain_norm).

**2. "The answer" paragraph ("A second, independent draw … agrees that no net is ahead at the settings as chosen"); Figure 8's orange diamonds**
- **Issue:** The builder sets `repl_agree` from the **sign of the 4-fold mean** only (build_fair_comparison_report.py line 741).
  - In the replicate, chorus_norm on F1 alone is **ahead** of CoactDetect in 3 of 4 folds: +0.0033, +0.0027, +0.0075.
  - The negative mean (−0.057) comes from fold 2 alone (−0.243). Two of that fold's five refits carry the failed-training signature: F1 0.125 each, seeds 1 and 2.
  - With those two refits excluded, chorus_norm is ahead in 4 of 4 folds; fold 2 becomes about +0.0075.
  - chorus_gain_norm's replicate fold 4 (−0.114) is also one failed refit.
  - The gated fold 2 has two refits at F1 0.0.
  - This run has chorus_norm behind in 4 of 4 folds. So on F1 alone the replicate disagrees in direction, apart from training failures.
  - The page discloses this run's failed refits but not the replicate's, and still calls the replicate "the stronger check".
- **Severity:** High.
- **Fix:**
  - Show the replicate per fold.
  - List its failed refits beside this run's.
  - Give means with and without failed refits.
  - Replace the sign-of-mean test with a statement that survives this.
- **Verified:** Yes. I read <darkroom>/bugarach/2026-09-18-replicate-run-status/results/results.json, per_seed.

**3. Section 4.5, "The answer" and section 6 ("both at 2 s", "both at 8 s")**
- **Issue:** The two sides' merge gaps are not the same quantity.
  - **CoactDetect (sliding):** merges significant window *positions*. `sliding.merge_runs` works over `sliding.pieces`, the right edges of a (t−w, t] window with w = int_win_sec = 2 s. Coincidences roughly gap + w apart (about 10 s at an 8 s gap) can therefore fuse. The reported call is the event span [tfirst, tlast].
  - **Nets:** `encode.decode` merges runs of supra-threshold frames whose frame gap is at most 20 frames. Run widths are set by the net's own temporal smearing.
  - The same number drives two different operations, so "matched" is nominal.
- **Severity:** Medium.
- **Fix:** Say "nominally matched" and describe what each gap measures. Better: re-merge both sides' reported spans post hoc with one event-time rule.
- **Verified:** Yes, the code (coact.py `_coact_sliding`, sliding.py, encode.py). The size of the effective difference is not measured.

**4. Section 4.5: "A wide merge gap therefore loses nothing"**
- **Issue:** The run's own data contradict this for two nets:
  - line_length on F1 alone: 0.705 at 2 s, 0.680 at 4 s, 0.660 at 8 s
  - tube: 0.631 at 2 s, 0.615 at 8 s
- Both merge rules are transitive over consecutive runs, so a chain of runs each within the gap can fuse across far more than the gap. Scoring is one-to-one (finding 5), so a fused call spanning two events is credited with only one of them.
- **Severity:** Medium.
- **Fix:** Qualify the claim to "for the coded detectors shown". State that merging chains.
- **Verified:** The numbers, yes (merge_gap.json). The chaining mechanism is inferred from the code; I did not measure it.

**5. Section 2: "a call that spans a long stretch hits any event inside it"**
- **Issue:** `score.score_detections` matches greedily and **one-to-one**. A long call is credited with one event; the others count as misses. Figure 5A ("one merged call, three events: two events lost") and the crowded check depend on exactly this property, and this sentence says the opposite.
- **Severity:** Medium.
- **Fix:** Reword to "…can hit any one event inside it, and only one; each call is matched to at most one event".
- **Verified:** Yes (score.py lines 222–239; `Score.n_duplicate` docstring).

**6. "Refits below 0.2 F1", the tube entry ("made no calls at all at a threshold picked on two recordings")**
- **Issue:** This mechanism is wrong for this refit, which belongs to the **choice under the budget**.
  - Its threshold is the budgeted selection's, THRESHOLD_GRID[35] = 0.9983.
  - That threshold was chosen on the inner fits' pooled scores, among 131 admissible (configuration, threshold) candidates (selections/gated/outer0/tube.json; `_heldout` uses the selection's `threshold_index`). It was not picked on two recordings.
  - The sentence is hardcoded at build_fair_comparison_report.py line 1019, whatever the selection.
- **Severity:** Medium. It is a factual error about what the method did.
- **Fix:** "It made no calls at the budgeted selection's threshold, 0.998, chosen on the inner fits…". Make the text depend on the selection.
- **Verified:** Yes.

**7. "Refits below 0.2 F1"; the per-fold means in Table 2 and Figure 8**
- **Issue:** The failed-training signature needs a threshold at or below 1e-4, which is `THRESHOLD_GRID[0]`, the grid floor. `pick_threshold`'s own contract says an edge choice "is not an operating point. Widen it", and it warns (`at_edge`). The run kept those refits and averaged them in. The page calls them "failed to train" without saying the tool's own edge rule flagged them at fit time. Keeping them is a defensible protocol choice, but it should be stated, because it decides the replicate's direction (finding 2).
- **Severity:** Medium-low.
- **Fix:** State the edge rule and the choice to keep these refits. Give means with and without them, in both runs.
- **Verified:** Yes by code (train.py lines 385–397; tune_learned_vs_coact.py line 1565). I did not open the run.json warnings (they are in fits.tar.gz).

**8. Section 7, "The two sides learn from different amounts of data" (missing item)**
- **Issue:** The net's own threshold (the one the F1-alone choice uses) is picked under a **different objective** from the one the run selects and scores by.
  - `pick_threshold` pools the quiet and busy threshold recordings into one F1.
  - The run uses the mean of each background's pooled F1.
  - `pick_threshold`'s own comment calls choosing under one rule and reporting under another a defect.
  - Separately, `train()` calls `pick_threshold` with its default n_val = 4 on a 2-recording block, so each recording is scored twice. That leaves pooled F1 unchanged, but it is the trap its docstring warns about.
- **Severity:** Low-medium. It may handicap the nets on F1 alone; the budgeted selection picks its threshold under the right objective.
- **Fix:** Add this to the limits.
- **Verified:** Yes (train.py lines 334–384; tune_learned_vs_coact.py `objective`).

**9. Section 4.5: "the nets within 0.001 F1"**
- **Issue:** The largest per-refit deviation is 0.00147 (tube, under the budget). The builder's `{x:.1g}` prints it as "0.001", so the page understates the bound.
  - The drift arises because `checkpoint.load` rebuilds on the CPU while the run scored on the GPU.
  - That makes it a *measured* bound on CPU-vs-GPU inference drift, while section 7 says "how far they would move is unmeasured". Training drift is still unmeasured.
- **Severity:** Low.
- **Fix:** Say "within 0.0015 F1". Cite it in section 7 as an inference-only bound.
- **Verified:** Yes (merge_gap.json).

**10. Section 6, the t-correction paragraph**
- **Issue:** The formula and arithmetic are right. The variance factor is 1/J + n2/n1 (checked against a secondary summary, the correctR vignette), giving sqrt(0.25 / (0.25 + 1/3)) = 0.655. The critical value t(0.975, 3) = 3.18 (computed with scipy). Two problems remain:
  - **(a) n1 is ambiguous for the nets.** A net fits 10 recordings plus 2 for the threshold, not the 72 behind "one third". Set n1 to what a net actually fits and the factor is about 0.33. Meanwhile CoactDetect's per-fold choices are near-identical (only alpha moves, between 1e-5 and 3e-5), so its training-set correlation is close to zero.
  - **(b) Bengio and Grandvalet 2004 is overstated.** JMLR 5:1089–1105 proves there is "no universal (valid under all distributions) unbiased estimator of the variance of K-fold cross-validation", not that "no exact correction exists".
- **Severity:** Low. The page already says to read the corrected values as a ranking.
- **Fix:** State that n1 = 36 seeds (72 recordings) was assumed. Reword the Bengio and Grandvalet claim to the theorem's words.
- **Verified:** Yes. The formula comes from a secondary summary (CRAN correctR vignette); the Nadeau and Bengio paper itself was not opened. The Bengio and Grandvalet abstract was read.

**11. Section 4.1: "Settings that break the context-window rule in section 4.5 were skipped"**
- **Issue:** Section 4.5 never states that rule, and nothing else on the page does. The rule is `context_fits_the_null`: a context window no wider than the 120 s minimum planted spacing, because a wider one lets other planted events into the null. This is a method invariant the search enforced.
- **Severity:** Low.
- **Fix:** State the rule and fix the cross-reference.
- **Verified:** Yes.

**12. Section 4.5: "24 bench recordings with 180 events each … median 43 s"**
- **Issue:** These are `bench.TAIL_RECORDING` recordings, 3 hours long according to its docstring, not the 45-minute bench recording. A 43 s median spacing only fits the 3-hour duration.
- **Severity:** Low.
- **Fix:** Say "3-hour crowded recordings".
- **Verified:** Yes (bench.py line 914 and docstring).

**13. Section 4.5: "Goal 1 compares against the project's shipped defaults instead. Scored against those, no verdict changes."**
- **Issue:** The claim is true, but the committed evidence doesn't show it: crowded_check.json has no shipped-default reference for CoactDetect or LoCo. I recomputed the shipped (binned) crowded F1 with goal 1's `_job`, over 12 recordings × 2 backgrounds:
  - CoactDetect 0.808: its choices (0.820–0.837) still pass.
  - LoCo 0.816: F1 alone (0.834) passes; under the budget (0.771) still fails.
  - SCE 0.714: unchanged, since its reference was already the shipped point.
- **Severity:** Low.
- **Fix:** Have crowded_check_fair_comparison.py record the shipped-default reference too, so the sentence has a file behind it.
- **Verified:** Yes, by my own recomputation.

**14. Sections 2 and 4.5: how the probe interacts with wide merges**
- **Issue:** `hot_fa` counts false alarms that *overlap* the probe. A long merged call straddling the probe edge therefore leaves the precision denominator entirely, which could add to binned SCE's gains at 30 s.
- **Severity:** Low.
- **Fix:** Check by counting the probe-overlapping merged calls at 8 s vs 30 s for SCE.
- **Verified:** No.

## What I checked and found sound

- **Nested cross-validation:**
  - Inner fits score only their third training fold (`_inner`, with the leak assert in `select_learned`).
  - Outer refits come from the other three folds.
  - The coded search sees only training recordings, through the `score`/`admissible` callbacks.
  - Goal 1's values were chosen on seeds 1–48 and held out on 49–96, which is disjoint from 1000–1047. The coded base therefore does not leak.
- **F1 pooling:**
  - F1 is pooled per background, then averaged, with NaN counted as 0 (`objective`, `bench.pool_scores`).
  - Probe calls are excluded from precision (`BenchResult.n_scored`).
  - The tolerance is 2.5 s, applied to call spans.
  - A call on a distractor costs precision.
- **Fold-draw fix:** the draws match `fold_maker`/`train` exactly. Before the fix, held-out folds 2–4 fitted seeds 1000–1004.
- **Budget:** 1.6 times the reference's rate, with a floor of one call per measured time; the floor did not bind in any fold (meta.json budgets).
- **Counts:** 1,728 inner fits (4 nets × 24 configurations × 3 seeds × 6 fold pairs), 210 distinct outer refits, and 1,938 fits.
- **Table 2:** every mean and t (recomputed), and the tuned-minus-untuned values.
- **Merge-gap curve values:** CoactDetect 0.731, 0.748 and 0.803; chorus_norm 0.741 and 0.775; SCE at 8 s 0.587. Matched gaps on F1 alone give +0.0096 (4 of 4 folds) and +0.0091 (3 of 4).
- **Crowded-check verdicts** in Table 3.
- **CoactDetect's re-scoring** reproduces the run exactly.
- **Failed-training signature:** recall 1/15, precision 1, F1 0.125.

## Relevant files

- %USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\tools\build_fair_comparison_report.py (line 741 `repl_agree`, line 753 `repro_txt`, line 1019 the hardcoded tube sentence)
- %USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\tools\fair_comparison_evidence.py
- %USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\tools\crowded_check_fair_comparison.py
- %USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\merge_gap.json, results.json, crowded_check.json, selections\gated\outer0\tube.json
- %USERPROFILE%\bugarach\bugarach-worktrees\tune-bench-comparison\src\bugarach\learn\train.py (`pick_threshold`), encode.py (`decode`), src\bugarach\detectors\coact.py and sliding.py (`merge_runs`, `pieces`), src\bugarach\score.py
- <darkroom>\bugarach\2026-09-18-replicate-run-status\results\results.json

Sources:
- [correctR vignette (Nadeau–Bengio and Bouckaert–Frank formulas)](https://cran.r-project.org/web/packages/correctR/vignettes/correctR.html)
- [Nadeau & Bengio 2003, Machine Learning 52:239–281](https://link.springer.com/article/10.1023/A:1024068626366)
- [Bengio & Grandvalet 2004, JMLR 5:1089–1105](https://www.jmlr.org/papers/v5/grandvalet04a.html)
