<!-- Verbatim role report, except that this machine's absolute paths are written as %USERPROFILE% and <darkroom> (the repository is public). The unedited original is in <darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-roles-round3/. -->

GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

# Role 6 (RTFM, methods expert): round 3 blind pass

**Artifact:** `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\report.html` (git hash-object 5c0ccbb confirmed).

**Code read:**
- `tune-bench-comparison` at the commit that ran, e8764aa. The only later change to the tool is `--replicate`, which changes the seeds and nothing else (diff e8764aa..7a95e8a).
- `tools/tune_learned_vs_coact.py` and `tools/search_all_settings.py`.
- `src/bugarach/score.py`, `src/bugarach/bench.py` (pool_scores / BenchResult, TAIL_RECORDING, MAX_CROWDED_DROP) and `src/bugarach/simulate.py`.
- `src/bugarach/learn/train.py` and `encode.py`, `nets/chorus.py`, `nets/tube.py`, `detectors/coact.py`, `detectors/loco.py`, `detectors/sliding.py`, `detectors/sce.py`.
- The evidence tools `tools/fair_comparison_evidence.py` and `tools/crowded_check_fair_comparison.py`. The report worktree's `src` differs from e8764aa only in `nets/` and `train.py`. bench, detectors, score, simulate and search_all_settings are identical, so the crowded check ran on the same scoring code as the run.

**Numbers recomputed from the run's JSON:**
- Every paired t in Table 2.
- The matched-gap t values.
- The merge-gap curves and their reproduction of the run.
- Table 3.
- The breakdown claims.
- The replicate margins.
- The budget-overrun counts.
- The fold draws.
- Tuned minus untuned.

## Findings

(location · issue · severity · suggested fix · verified)

1. **§10 and Figure 12, "tuned minus untuned" under the budget** · The tuned side is the budget selection, with its threshold held inside the budget. The untuned side is `results.json` `untuned`, scored at each refit's own F1-picked threshold (`summarize()`: `idx=None` → `own_index`) and never held to the budget. So "under the budget, chorus_norm −0.020, tube −0.035" mixes what the budget costs with what tuning did, and "not always up" partly measures the budget. · **medium** · Either compare against the untuned configuration at a threshold chosen inside the budget (the score files keep every threshold, so this needs no refits), or relabel it: "tuned and held to the budget, minus untuned and not held to it". · verified: yes

2. **§4.1, "at 3 training seeds (the random start of a net's training, unrelated to recording seeds)"** · The training seed also decides which 10 recordings a net fits. `train()` asks for `TRAIN_SEED_BLOCK + seed*1000 + i`, and `fold_maker` maps that modulo the fitting pool. For the outer refits (70-recording pool) that means dealt positions 0–9, 20–29, 40–49, 60–69 and 10–19 for seeds 0 to 4: five disjoint data subsets (`train.py` l.230, `fold_maker`; tune tool l.798). So the spread between refits is data variation as well as initialisation. That covers the up-to-106/h probe spread, "failure … about 1% of refits" and the per-fold refit means. §4.2's own argument depends on this link, which contradicts "unrelated". · **medium-low** · "a training seed sets the net's random start and which 10 of the training recordings it fits". · verified: yes

3. **The answer paragraph and §6, "within 0.01 F1 … once refits that failed to train are set aside"** · The set-aside rule (`LOW_F1 = 0.2`) is decided by the held-out score, and only the net side has such a rule. §10's suggestion that the threshold picker identifies these refits does not hold: the grid-bottom flag also fires on 4 healthy line_length refits (threshold index 0, held-out F1 0.651, 0.671, 0.722, 0.738). No training-side criterion in the run reproduces the exclusion. · **medium** · Lead with the all-refit comparison, which the page already uses everywhere else. Present the set-aside margin as a post hoc sensitivity check, or define the exclusion from training-side evidence alone and show it catches exactly these refits. · verified: yes

4. **§4.5, §9 and Table 2 "(n of 4 not admissible)"** · Goal 1's veto (`search_all_settings.make_admissible`) runs inside the search, on every candidate, against the shipped point, so a refused candidate sends the search elsewhere. Here it was applied after the search, so it can only strike a choice. "Not admissible" for LoCo, SPIKE-synch, rate+context and binned SCE under the budget therefore means "this search's choice fails". It does not mean "no setting passes both rules". The page says the check came after the run but never states this consequence. · **low-medium** · Add one sentence: "applied after the search, the check can refuse a choice but cannot find a passing one; goal 1's in-search veto could have". · verified: yes

5. **§9 and Limits, "path taken" and "one step can move a detector from well over the budget to far under it"** · The mechanism is specific and worth naming. When the starting point breaks the budget, `coordinate_rounds`' rescue takes the best admissible value on the **first axis in grid order** that has any admissible value, whatever F1 that costs. Examples from `selections/gated/*`:
   - LoCo, all 4 folds: `threshold_pctile` 99.9→99.99, inner F1 0.73–0.74 → 0.69, and then no further move.
   - SPIKE-synch: `C_threshold` 0.10→0.16, F1 0.48 → 0.22.
   - rate+context: `excess_threshold_hz` 4.5→8.0, F1 0.64 → 0.43.

   Under the budget these detectors' results are set by the order of the axes in the grid. · **low** · Name the rescue rule and the axis-order dependence in §9. · verified: yes

6. **Table 1, CoactDetect "against the same recording shifted in time" and LoCo "on the recording shifted in time"** · This misdescribes both nulls. Each ROI's events are circularly shifted **independently** within a local context window (the `coact.py` module docstring and `_coact_sliding`, which computes exact moments; `loco.py`, "in-context circular-shift surrogates"). Shifting the whole recording would keep cross-ROI alignment and would not be a null at all. The binned SCE and locust rows already say "each ROI". · **low-medium** · "…against each ROI's events circularly shifted, independently, within a 120 s context". · verified: yes

7. **§4.3, "alpha (the significance level for calling an event) 10⁻⁵"** · In sliding CoactDetect, alpha thresholds a one-sided Gaussian-tail p computed from the exact mean and standard deviation of a Poisson-binomial count, at every window position (`_coact_sliding`: `pval = 0.5*erfc(z/√2)`). It works as a z threshold of about 4.3. It is not a calibrated per-event false-alarm probability: the normal tail is poor that far out for small-mean counts, and nothing corrects for the number of positions tested. · **low** · "alpha, a threshold on a Gaussian-approximation p-value, used as a tuning setting rather than a calibrated false-alarm rate". · verified: yes (code)

8. **§4.1, the Nadeau–Bengio factor, "with that as its training set the factor would be smaller"** · √(3/7) = 0.655 is correct: J = 4, n₂/n₁ = 1/3, and (1/4)/(1/4 + 1/3) = 3/7 under the corrected resampled t. 3.18 is the right two-sided 5% critical value at 3 df. But the heuristic ρ = n₂/(n₁+n₂) stands in for the correlation between splits whose training sets are the whole remainder of the data. The nets fit a subsample, and their fitting sets overlap less (the page says 2–3 of 5 seeds), so plugging in n₁ = 10 (which gives 0.31) has no principled direction. · **low** · Drop the sentence, or write "the heuristic has no stated form for a learner that fits a subsample; neither factor is exact for the nets". · verified: formula yes (NB 2003 and the correctR vignette); the direction argument is my own reasoning

9. **Table 1 and §8, chorus_norm "standardizes it over time"** · The standardisation spans the whole input (`chorus.py`: `h.mean/std(dim=2)` over time). Training inputs are 4,096-frame crops (about 6.8 min). Scoring inputs are the full 45-minute recording (27,001 frames), which includes the probe. So normalisation statistics at scoring differ from training. This is how the net works, not a misuse by the analysis, but it bears on §8's busy-background result and is not stated anywhere. · **low** · Add it to §11 Limits. · verified: yes

10. **§2, "2.5 s is where the coded detectors' scores stop changing"** · The plateau (`tests/test_tolerance_curve.py`, `score.TOL_SEC` docstring) was measured at the **shipped** operating points, on the quiet background, over seeds 1–3. It was not measured at the tuned sliding settings with 8–30 s merge gaps that are scored here. · **low** · "…stop changing at their shipped settings". · verified: yes

11. **§10, the false-alarm paragraph** ·
    - "Differs by up to 106 per hour" sits in the paragraph about choices under the budget. But 106/h is chorus_gain_norm fold 1 **on F1 alone** (quiet background: 45, 107, 1, 27, 5). Under the budget the largest spread is 93/h (tube, fold 2, quiet).
    - "CoactDetect 8 to 12": its held-out probe rates are 8.0 to 12.5.
    - **low** · Correct the scope or the number, and write "8 to 12.5". · verified: yes

12. **§7, "It costs line_length and tube"** · This is true only for choices on F1 alone, which is Figure 9B's scope. Under the budget, a wider merge helps all four nets: line_length 0.697→0.723 and tube 0.594→0.608 at 16 s. · **low** · Add "on F1 alone". · verified: yes

13. **§7, Limits "matched is nominal", and §4.5 "sees gaps wider than about 6 s"** · There are three merge rules, not two:
    - The nets merge runs of frames above threshold when the gap is 20 frames or less.
    - Sliding CoactDetect and LoCo merge window positions (piece start minus the previous piece's end), so events up to about gap + window apart fuse.
    - Binned SCE merges by event time (the bin's first event minus the episode's last event).

    Consequence: CoactDetect with a 2 s window fuses events 6 s apart at a merge gap near 4 s, so the check is sensitive to gaps below 6 s for window-based detectors. · **low** · Name all three rules in the Limits entry, and qualify "about 6 s" by detector. · verified: yes (code)

14. **§1, a distractor "is built exactly as a planted event joined by 18%"** · The construction is the same: the same jitter and matlab_round(0.18 × 33) = 6 ROIs. The placement is not. Distractors are drawn uniformly in 120–1100 s with no spacing from planted events or from each other (`simulate.py` l.789–808). A distractor can therefore land within tolerance of a planted event, and a call on that event then also counts as a distractor hit in §8's 84–100% figure. The effect is small. · **low** · "built as … but placed without regard to the planted events". · verified: yes

## Checked with no findings

- **Nested CV:** outer, inner and refit structure; leakage asserts (`select_learned`, `_run_fit`); `fold_check` distinct; Figure 4 draws (before the fix, held-out folds 2–4 all fit seeds 1000–1004; as run, pairwise overlaps of 2–3 seeds); the job count 1 + 24 + 1,728 + 210 = 1,963.
- **Paired t:** all eight Table 2 t and corrected-t pairs reproduce from `results.json` (for example chorus_norm −1.80 and −1.18; chorus_gain_norm under the budget −13.02 and −8.52). The matched-gap values reproduce: 2.83 and 1.86 at 2 s, 2.25 and 1.47 at 8 s. "0.014 at the least" is 0.0138.
- **One-to-one matching:** greedy, closest pair first, span against the nominal planted time with 2.5 s tolerance (`score_detections`). Probe calls are left out of precision (`BenchResult.n_scored`). A NaN F1 counts as 0. The 0.71 precision ceiling (15/21) holds.
- **Budget:** 1.6 × the reference's rates on training folds only, for the probe at each background and the empty quiet recording, counted after merging. The floor of 1 per measured time (0.33/h) never binds against budgets of 12.8–16/h. Net thresholds under the budget are one common grid value chosen on the inner fits.
- **Merge-gap re-scoring:** it changes only the gap. It reproduces the run exactly for coded detectors, and within 0.00147 per refit and 0.00029 per fold mean for nets. All §7 curve values reproduce.
- **Crowded check:** it applies bench.MAX_CROWDED_DROP = 0.02 over seeds 1–12 × tail_quiet and tail_busy. Every Table 3 range, reference value and pass count reproduces, and "the choice of reference changes no verdicts" holds.
- **Breakdown:** the §8 recall and per-background F1 claims reproduce (0.59 vs 0.35; 0.72 vs 0.81 in 3 of 4 folds; −0.014 and +0.000).
- **Replicate:** only the seeds change, it ran on the same GPU model, and the −0.057, +0.005 and per-fold margins reproduce.
- **§10 values:** the tuned-minus-untuned numbers and the overrun counts (0,0,1,3 / 2,2,0,3 / 1,0,1,1 / 1,4,5,1) reproduce.
- **Deep Sets description:** chorus pools symmetrically (mean, spread, top-m) after a shared per-ROI encoder, so it matches.

## Not verified

- The claim that Cossart, Aronov and Yuste 2003 used interval reshuffling at P < 0.05: the PDF could not be read on this machine.
- Crediting CoactDetect's null to Amarasingham 2012 as its "nearest published form". The implemented null is an independent per-ROI circular shift within a window, which looks closer to the spike-train-shifting surrogates in Louis, Borgelt and Grün 2010 than to jitter. That is for role 2 to decide.

Sources:
- [Nadeau & Bengio 2003, Machine Learning 52:239–281](https://link.springer.com/article/10.1023/A:1024068626366)
- [correctR vignette (resampled and k-fold corrected t formulas)](https://cran.r-project.org/web/packages/correctR/vignettes/correctR.html)
- [Louis, Borgelt & Grün 2010, Generation and Selection of Surrogate Methods for Correlation Analysis](https://link.springer.com/chapter/10.1007/978-1-4419-5675-0_17)
- [Cossart, Aronov & Yuste 2003 (PubMed)](https://pubmed.ncbi.nlm.nih.gov/12748641/)
