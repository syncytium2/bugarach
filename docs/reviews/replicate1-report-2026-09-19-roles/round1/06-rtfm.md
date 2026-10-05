GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

# Role 6 (Methods / domain expert, "RTFM"), round 1

**Artifact:** `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\docs\learned\tuned_vs_coact\replicate1\report.html` (read as the built file and all 8 screenshots), plus its generator `...\replicate-report\tools\make_replicate_report.py`.

**What I checked it against:**
- Production code in `...\weekend-runs`:
  - `tools\tune_learned_vs_coact.py` (all of it)
  - `tools\search_all_settings.py` (`coordinate_rounds`, `choose_settings`)
  - `src\bugarach\score.py`
  - `src\bugarach\bench.py` (`FULL_GRIDS`, `REGIMES`, `BENCH_RECORDING`, `NULL_RECORDING`, `run_detector`, `BenchResult`, `pool_scores`, `fold_split`)
  - `src\bugarach\simulate.py` (how distractors and planted events are built)
  - `src\bugarach\learn\train.py`
  - `src\bugarach\learn\nets\tube.py` and `line.py`
  - `src\bugarach\detectors\sliding.py` and `coact.py`
  - `docs\forks.md` §14
  - `src\bugarach\ui\diagnostic.py` (`lane_panel`), `src\bugarach\ui\app.py` (`_compute`), `tools\make_diagnostic.py`
- Data: both runs' `meta.json`, `results.json` and `selections\`; `scores.zip` and `fits.zip` (WSMIP065); `scores.tar.gz` and `fits.tar.gz` (WSMIP064).
- Re-computation: every number below was computed with the weekend-runs venv, with code piped to Python on stdin. No file was written anywhere; the scratch folder is empty.
- Literature, for the paired-over-folds point: Bengio & Grandvalet 2004; Nadeau & Bengio 2003. Found by search and cited from their abstracts; I did not open the full texts.

## Findings

Each finding gives location · issue · severity · suggested fix · whether I could verify it against a source.

**1. Precision leaves the busy stretch out, and the page defines it as if it did not.**
- **Location:** §2's F1 definition ("precision (the share of its calls that are real)"); Figure 1 caption ("any call there is a false alarm by construction"); §5 ("F1 alone rewards a detector that fires on the busy stretch…").
- **Issue:** Every score pools through `bench.pool_scores`, and `BenchResult.precision = n_hit / (n_detected − hot_fa)` (bench.py 1141–1162). Calls in the busy stretch are removed from the precision denominator. They cost F1 nothing, and that is the real reason the budget has to exist.
  - Pooled over WSMIP065's 96 held-out recordings (F1 alone), counting busy-stretch calls would give: SPIKE-synch 0.644 → 0.358; locust 0.676 → 0.232; rate+context 0.644 → 0.536; CoactDetect 0.750 → 0.733.
  - The F1-alone column's 0.645 and 0.677 for SPIKE-synch and locust exist only because of this rule.
- **Severity:** major.
- **Fix:** Define precision as "matched calls ÷ calls outside the busy stretch; busy-stretch calls are counted separately, by the budget." Say the same in the Figure 1 caption and §5.
- **Verified:** yes (code and data).

**2. The "decoys" are built exactly like an 18% planted event.**
- **Location:** Figure 1 caption ("real bursts of coincidence that are not coordinated events"); §1's definition of a coordinated event.
- **Issue:**
  - `simulate.py` 789–808 builds each distractor from `matlab_round(0.18×33)` = 6 random ROIs, with onsets jittered at the same 0.36 s SD as planted events (830–854). Only the label differs, plus a 120–1100 s placement window. By the definition in §1, they are coordinated events.
  - On seed 2000 at the quiet background, all 6 of CoactDetect's false alarms are the 6 decoys. These are the × marks in Figure 1's lane, which the caption never explains.
  - In WSMIP065's held-out folds, 556 of CoactDetect's 651 false alarms (85%) are decoys, and it lands on 556 of the 576 decoys. LoCo is at 83% and binned SCE at 88%.
  - A detector that finds every planted event and every decoy scores precision 15/21, so F1 is 0.833. That is the ceiling for any cell-counting detector on this bench. A net can beat it only by learning to under-call 6-cell events, which is label noise.
- **Severity:** major (for how F1 is read, not for the ranking).
- **Fix:** In §2 and the Figure 1 caption, say the decoys are built like an 18% planted event but scored as negatives. State the roughly 0.83 ceiling and what the × marks are.
- **Verified:** yes.

**3. Each net trains on 10 recordings, and the page says "all three training folds".**
- **Location:** §4 ("train on two of the three training folds", "refitted on all three training folds"); Figure 3 ("refit the winner on all three training folds").
- **Issue:**
  - `train()` fits on `n_train = 10` recordings, a contiguous run of the dealt list (5 seeds × 2 backgrounds), and picks its threshold on the last 2 recordings (one seed × 2 backgrounds).
  - All 1,943 fits in WSMIP065's run show this: every inner fit is 10 of 46 fitting recordings, and every refit is 10 of 70. For held-out fold 1, all five refit seeds pick their threshold on the same seed (2011).
  - The coded detectors are searched on all 72 training recordings. In a "fair comparison" report, a reader will assume both sides saw the same data.
- **Severity:** major.
- **Fix:** Say "each fit trains on 10 of the training recordings (5 seeds, spread across the training folds by the round-robin deal) and picks its threshold on 2." Name it as a difference between the two sides.
- **Verified:** yes (`run.json` `fitted_recordings` and `threshold_recordings` in `fits.zip`).

**4. The explanation of the collapse is wrong.**
- **Location:** §8 ("the net's output stayed near zero everywhere, so even the lowest threshold caught only a few events").
- **Issue:**
  - The collapsed refits (WSMIP065, chorus_norm `75d4474550026cfa`, fold 1, seeds 1 and 2) make exactly one call per recording at every threshold from 0.0001 up to 0.50–0.55, and none from 0.55–0.60 up.
  - So the output is nearly constant, around 0.5–0.6, whatever the input. That gives one recording-long call, which matches one planted event: recall 1/15, precision 1, F1 = 2·(1/15)/(16/15) = 0.125 exactly.
  - The threshold lands on the grid bottom because every threshold up to about 0.5 ties at 0.125, and `pick_threshold`'s strict `>` keeps the first (lowest).
  - Under the budget, threshold index 30 (0.97) sits above the constant, so nothing is called.
- **Severity:** major (a wrong mechanism, stated as fact).
- **Fix:** "The net's output sat near 0.5 everywhere, whatever the input, so any threshold below that made the whole recording one call, which matches one of the 15 events (F1 exactly 0.125); the grid-bottom threshold is how the tie was broken."
- **Verified:** yes.

**5. The collapse happens across the chorus search, not in one fold.**
- **Location:** §8's heading "Three things in the results that are not the models"; "a configuration that fails at some seeds can still win there".
- **Issue:**
  - Counting inner (fit, fold) scores with one call per recording:
    - chorus_norm: 292/864 (WSMIP064) and 306/864 (WSMIP065), about 35%.
    - chorus_gain_norm: 150/864 in both (17%).
    - line_length: 16 and 22; tube: 15 and 12 (about 2%).
  - In WSMIP065's run, 13 of chorus_norm's 24 configurations and 15 of chorus_gain_norm's collapse somewhere. The configuration chosen for fold 1 (`75d4…`) had collapsed inner fits and still won.
  - A training recipe that fails about a third of the time belongs to the learned side as it was run, so "not the models" is too strong.
- **Severity:** major.
- **Fix:** Report the rate per net. Say that inner selection pools F1 over seeds, so a configuration can win with collapsed seeds. Retitle or qualify the section.
- **Verified:** yes.

**6. Whether the held-out folds kept to the budget is never reported, and the report's own helper for it is never called.**
- **Location:** Figure 4 text ("every entry in that column is held to the false-alarm rate of one fixed detector"); Table 1's budget column. `over_budget()` is defined at `make_replicate_report.py:101` and never called (`edges()` at 150 is also unused).
- **Issue:**
  - On held-out folds, refits of nets chosen under the budget go over it in 25 of 80 (WSMIP064) and 16 of 80 (WSMIP065) cases. The headline net, chorus_gain_norm, goes over in 7/20 and 5/20; tube in 11/20 and 7/20.
  - CoactDetect in WSMIP064's fold 2 is over budget on held-out and carries no mark in Table 1.
  - There is also an asymmetry. A net's budgeted (configuration, threshold) is chosen on inner fits (seeds 0–2, two folds), then the threshold is applied to different refits (seeds 0–4, three folds) whose output is calibrated differently. A coded setting is the same deterministic object in both places.
- **Severity:** major.
- **Fix:** Add held-out adherence to Table 1: refits over budget, and coded folds over budget. Say the budget constrains the selection on training recordings, not the held-out scores.
- **Verified:** yes (`results.json`: `seeds_over_budget`, `over_budget`).

**7. CoactDetect's two identical columns are explained wrongly for WSMIP064's run.**
- **Location:** §7 ("its two columns are identical in both: the budget is built around its own settings, so its best setting on F1 alone already meets it").
- **Issue:**
  - In WSMIP064's run, the F1-alone choice is not the reference in 3 of 4 folds (α 3e-5 in folds 0 and 2; guard 0 s in fold 1). Those choices happened to pass the budget on training data, and fold 2 then breaks it on held-out.
  - In WSMIP065's run the search never left the reference in any fold. So CoactDetect in that draw is the untuned reference.
- **Severity:** moderate.
- **Fix:** Describe what the search did in each draw.
- **Verified:** yes.

**8. The between-draw yardstick is built from mismatched pieces.**
- **Location:** Summary bullet 3; §7; Figure 7's bold rule; §9 bullets 1–2.
- **Issue:** The arithmetic is right (median 0.0083, max 0.0268, 20 entries). The construction is not.
  - **(a) Two populations mixed.** The nets' clean moves have a median of 0.0153 over 10 entries; the coded detectors' median is 0.0052. A net-minus-CoactDetect gap should be read against the nets' moves, since CoactDetect moved 0.0002. On that basis the budgeted gap (0.025–0.030) is about 2 times the median move and about equal to the largest, not "about 3 times".
  - **(b) One number counted twice.** CoactDetect's F1-alone and budgeted entries are the same selection in 8 of 8 folds, so the two smallest moves are one fact.
  - **(c) Moves share a direction.** 9 of the 10 clean net moves are positive, and 5 of 6 coded F1-alone moves are negative. For a within-draw difference, the right unit is how the difference itself moved between draws: +0.005 for chorus_gain_norm (budgeted) minus CoactDetect.
  - **(d) It is a lower bound.** The configuration draw, training seeds and refit seeds are all held fixed, so "how big a real difference has to be" overstates what it measures.
  - **(e) "Among the steadiest" is post hoc.** It rests on one pair of draws, and chorus_gain_norm's other entries moved +0.016 and +0.027 (the largest of all).
- **Severity:** moderate.
- **Fix:** Split the yardstick into nets and coded; count CoactDetect once; call it a lower bound on replication noise; replace the "steadiest" argument with how the difference moved between draws.
- **Verified:** yes (computed with the report's own functions).

**9. No uncertainty is shown for the headline, though the run computed one.**
- **Location:** Summary bullet 1; §9.
- **Issue:** `results.json` → comparisons → gated → `chorus_gain_norm - coact` gives:
  - WSMIP064: mean −0.0303, sd 0.0047, t −13.0 (df 3).
  - WSMIP065: mean −0.0250, sd 0.0181, t −2.77 (df 3), two-sided p about 0.07.

  The page is right that folds sharing training data inflate a paired t (Bengio & Grandvalet 2004; Nadeau & Bengio 2003). With a Nadeau–Bengio-style variance correction (×(1/4 + 24/72)/(1/4) = 2.33), those t values become about −8.5 and −1.8. So WSMIP065's draw alone does not separate the gap from zero. That is worth saying, because it is the case for having two draws.
- **Severity:** moderate.
- **Fix:** Give each draw's paired mean ± sd, and optionally the corrected t, flagged as a heuristic for K-fold.
- **Verified:** yes (numbers from `results.json`; the correction arithmetic is mine).

**10. "No setting in the grid met the budget" claims more than the search tested.**
- **Location:** Table 1's ‡ footnote; §8 heading "Coded detectors with no admissible setting".
- **Issue:**
  - `coordinate_rounds` only scores settings one axis away from its current point. Locust's 16 scored settings are exactly the one-axis neighbourhood of its start, out of a 7×5×5×2 = 350-point product.
  - §8's prose ("refused every candidate it scored (16 of 16)") is accurate. The footnote and heading are not.
  - The same applies to binned SCE in WSMIP065's fold 2 (26 of 26 refused).
- **Severity:** moderate.
- **Fix:** Say "no setting the search reached met the budget".
- **Verified:** yes.

**11. Table 2's reading of "at the edge" fits only four of the six detectors.**
- **Location:** §8 and Table 2 ("a setting that wanted to go further stops at the edge").
- **Issue:**
  - CoactDetect's and LoCo's merge gaps started at 8 s, the top of the grid (goal 1's value), and never moved in any of 8 folds. The flag records where they started, not a climb.
  - The other four did climb to the top:

    | detector | move | F1 gain |
    |---|---|---|
    | binned SCE | NaN → 30 s | +0.058 to +0.080 |
    | rate+context | 3 → 8 s | +0.008 to +0.010 |
    | SPIKE-synch | 0.5 → 2.0 | +0.0025 to +0.021 |
    | locust | 4 → 16 frames | +0.085 to +0.104 |
- **Severity:** minor.
- **Fix:** Split Table 2 into "started at the top" and "moved to the top".
- **Verified:** yes (the `moves` field in the selection files).

**12. CoactDetect's α is a Gaussian cutoff, not the level of an exact test.**
- **Location:** §5; Figure 4 ("α = 10⁻⁵").
- **Issue:** Sliding CoactDetect uses the exact mean and SD of the Poisson-binomial null, then a one-sided Gaussian z-test, p = ½·erfc(z/√2) ≤ α (`coact.py` 359–369). So α = 10⁻⁵ is a z ≥ 4.26 cutoff, not an exact tail probability. LoCo's percentile, by contrast, is exact.
- **Severity:** minor.
- **Fix:** "α = 10⁻⁵ on a Gaussian z-test against the exact null mean and variance."
- **Verified:** yes (code).

**13. tube does count distinct cells, briefly.**
- **Location:** §3 ("it averages the cells before any learned step, so it cannot count distinct cells").
- **Issue:** `tube.py` 146–150 max-pools each ROI's binary onsets, then averages over ROIs. That is the fraction of distinct ROIs with an onset within about ±0.5–0.7 s, the same kind of statistic as CoactDetect's S(t). What tube loses is each cell's identity after that: the temporal difference-of-Gaussian lets a bursting cell count more than once (its own docstring).
- **Severity:** minor.
- **Fix:** "counts distinct cells only within a ~1 s pool, then integrates that count over time, where a bursting cell counts more than once."
- **Verified:** yes (code).

**14. Figure 3 undercounts the refits.**
- **Location:** Figure 3's footer ("then 4 × 5 refits").
- **Issue:** In WSMIP065's run, each net has 55 outer refits (line_length 50): 10 or 11 distinct (fold, configuration) pairs × 5 seeds. The untuned configuration and the budget's winner are refitted as well as the F1-alone winner.
- **Severity:** minor.
- **Fix:** "up to 4 × 3 × 5 refits (the F1-alone winner, the budget's winner, the untuned configuration)."
- **Verified:** yes.

**15. The F1-alone comparison mixes columns without saying so.**
- **Location:** Summary bullet 2; §9 bullet 3.
- **Issue:** Under the heading "On F1 alone", the page compares untuned chorus_norm with CoactDetect chosen on F1 alone. The tuned-against-tuned numbers are −0.007 (WSMIP064) and −0.057 (WSMIP065, the collapse).
- **Severity:** minor.
- **Fix:** Name the columns being compared and why the untuned one is used.
- **Verified:** yes.

**16. The +0.011 rehearsal lead is measured against a different design.**
- **Location:** Summary; §6; §9.
- **Issue:** The rehearsal ran 6 seeds per fold and had the fold defect (comments in `tune_learned_vs_coact.py`). Its between-draw noise would be larger, and its folds were not independent. The conclusion "inside the noise" survives and only gets stronger, but the yardstick belongs to this design.
- **Severity:** minor.
- **Fix:** One clause saying the rehearsal used a different design.
- **Verified:** partly (the design from the code; I did not open the rehearsal's numbers).

**17. The budget has a floor that Figure 4 does not mention.**
- **Location:** Figure 4.
- **Issue:** The ceilings are max(1.6 × rate, one false alarm in the measured time). The floor does not bind here: 0.33/h and 0.037/h, against ceilings of 12.8–16.5/h and 8.65/h.
- **Severity:** minor.
- **Fix:** Optional clause.
- **Verified:** yes.

**18. The page says nothing is typed by hand; some method facts are.**
- **Location:** Generator docstring and §11 ("nothing on it is typed by hand").
- **Issue:** These method facts are literals in the generator: "0.0052 Hz", "context 120 s", "300 s", "36 training seeds", "48 seeds", "33 ROIs", "72 training recordings", "3 fold pairs", "8 s", "30–36%", "F1 0.125", "2 of its 5". I checked each against the code or data and all are correct today, but the claim itself is false and they can drift.
- **Severity:** minor. This overlaps roles 2 and 3; I note it only for the method constants I checked.
- **Fix:** Read the constants from the runs, or soften the claim.
- **Verified:** yes.

## Checked and clean
- **Figure 1's code path.** `_compute("coact", …)` returns the same 20 onsets as `bench.run_detector` at the declared reference settings on seed 2000 at the quiet background. The lane marks hits with `score_detections` over each call's span at `TOL_SEC` 2.5 s, the rule used for scoring. It shows 14 of 15 hits, which is the single red triangle. The raster is drawn with `gt=None`; the busy stretch (1200–1500 s) and the 6 decoys sit in the lane.
- **Matching.** Greedy, one-to-one, closest pair first, with a span-aware gap at 2.5 s. F1 is pooled per background and then averaged, with NaN counted as 0.
- **No held-out leakage.**
  - `select_learned` asserts that no held-out seed reaches the selection.
  - The coded search sees training recordings only.
  - The budget uses `split.train(h)`.
  - `fold_check` reports `distinct: True` with no problems in both declarations. The round-robin deal is confirmed in the `run.json` files.
- **Counts.** 432 inner fits per net = 24 × 3 × 6 (1,728 inner fits in WSMIP065's run).
- **Search settings.** A move needs a gain strictly greater than 0.002; the grids are fixed (`max_extensions=0`).
- **Figure 4's numbers.** 10.3/8.0/5.41 × 1.6 = 16.5/12.8/8.65.
- **The two declarations** differ only in `recording_seeds` and `replicate`. The seeds are disjoint, and the empty recordings sit at seed + 100,000.
- **Sliding detectors.** "Lost 30–36%" matches 64% and 70% kept (forks.md §14 and `sliding.py`); 100% kept after the switch. The exact Poisson-binomial via DFT-CF is as described.
- **Bench parameters.** 10/6/3 cells (`matlab_round`), 0.36 s jitter SD, 120 s minimum spacing, 0.0052 and 0.019 Hz.
- **Parameter counts** are read from WSMIP065's own checkpoints.
- **Training hours.** `--gpu-jobs 1`, so the summed training time is GPU time.
- **Side note, outside the artifact.** forks.md §14 says sliding shipped in `OPERATING_POINTS` on 2026-09-16, but the code (and the page) say `OPERATING_POINTS` is still binned. forks.md is stale.

## Not verified (outside my role or not reachable)
The rehearsal's +0.011; "`tiny` showed it in every published run"; the claims about the HANDOFF decision item and the 0.03% / 12 ROIs / 4 recordings.

Sources:
- [Bengio & Grandvalet 2004, No Unbiased Estimator of the Variance of K-Fold Cross-Validation, JMLR 5:1089–1105](https://www.jmlr.org/papers/volume5/grandvalet04a/grandvalet04a.pdf)
- [Nadeau & Bengio 2003, Inference for the Generalization Error, Machine Learning 52:239–281](https://link.springer.com/article/10.1023/A:1024068626366)
