GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch (I also hold SubagentHandback, which is the delivery channel. I hold no Edit, Write or NotebookEdit.)

# Role 6, methods / domain expert: blind verify, round 3

**Artifact:** `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\docs\learned\tuned_vs_coact\replicate1\report.html`. I confirmed the hash `9a99a7a4209b11b7bb285c260a43ea31aabda1d3`.

**Grounding.** I read the code the runs used before judging the prose:
- In weekend-runs @ 7a95e8a: `score.py`, `bench.py` (`pool_scores`, `BenchResult`, `make_null_recording`), `simulate.py` (jitter, distractors), `detectors/coact.py`, `sliding.py`, `sce.py`, `cicada.py`, `sync.py`, `learn/encode.py` (`decode`), `nets/chorus.py`, `chorus_norm.py`, `chorus_gain_norm.py`, `line.py`, `line_length.py`, `tube.py`, `tools/tune_learned_vs_coact.py`, `tools/search_all_settings.py`.
- `tools/fair_comparison_evidence.py` in merge-gap-second-draw.
- Both runs' `results.json`, `meta.json` and score archives, and both `merge_gap.json` files.
- I diffed the code between the two draws' commits: e8764aa..7a95e8a differs only in `--replicate`, as the report says.
- I re-ran CoactDetect myself where a claim needed a measurement.
- Nothing was written into any repository. Scratch runs were stdin scripts only.

## Findings

**1. Section 9, "At a matched merge", first paragraph.**
- **Issue:** "merging can only lower a detector's call counts, so every budgeted choice stays within its ceilings" is false for CoactDetect at the 2 s and 4 s matched gaps. `fair_comparison_evidence.coded_gaps` re-runs CoactDetect with `merge_gap_sec` set to 2 and 4. That is *shorter* than its as-run 8 s, so calls split and counts rise. The tool records only F1, so nobody checked the ceilings.
- **What I measured:** I re-ran all 8 held-out folds at 2 s and 4 s. At 8 s my numbers match the run's own rates exactly. At the shorter gaps:
  - Dense-stretch rates rise by up to 2 per hour. For example, second draw fold 1 quiet goes from 12 to 14 per hour, and fold 3 quiet from 12 at 4 s to 14 at 2 s.
  - First draw fold 2 is over its busy ceiling at both gaps (15 per hour against a ceiling of 12.8). That fold was already over as run (Table 3), so the shorter merge creates no *new* held-out violation.
  - I did not check the training-recording ceilings, which are where the budget is actually defined.
- **Conclusion:** the table numbers survive, but the stated invariant is wrong for half of CoactDetect's matched columns.
- **Severity:** major.
- **Fix:** Say that merging longer can only lower call counts, which covers the nets at 4, 8 and 16 s and CoactDetect at 16 s. Then say that CoactDetect at 2 s and 4 s makes more calls. On the held-out recordings no fold goes newly over, but its training-set admissibility at those gaps was not re-checked. Alternatively, have the tool record call rates per gap and gate on them.
- **Verified against a source:** yes (code plus a re-run).

**2. Table 7, "across refits" row.**
- **Issue:** The row says "one threshold, chosen on the inner fits, carried onto 5 refits trained afresh" for all learned entries. In `summarize`, `idx = sel.get("threshold_index") if w == "gated" else None`. So the untuned and "on F1 alone" refits each use their *own* threshold, picked on their own 2 threshold recordings (`own_index`).
- **Check in the archives:** In the second draw, fold 1, chorus_norm's "on F1 alone" refits use own_index 0 for the two failed seeds and 29–31 for the others. Under the budget, all five use index 30.
- Section 5 scopes the sentence correctly; Table 7 does not.
- **Severity:** major.
- **Fix:** "under the budget: one threshold, chosen on the inner fits, carried onto 5 refits; untuned and on F1 alone: each refit picks its own on its 2 threshold recordings."
- **Verified against a source:** yes.

**3. Section 3, the chorus_norm bullet.**
- **Issue:** "standardizes each cell's trace ("norm"), passes every cell through one shared encoder to a bounded vote" gets the order backwards.
  - The code (`chorus.py` `forward`) runs the shared encoder first: `h = self.roi(xr)`.
  - It then standardizes each cell's *encoder output* over time, channel by channel: `h = (h - mean_t)/std_t`.
  - Only then does it apply the sigmoid vote.
  - The registration note says the same: "each cell's encoder output standardised over time before the vote".
- **Why it matters:** the input raster is not standardized, and that is the mechanism the Table 7 "scaling each cell" row depends on.
- **Severity:** major.
- **Fix:** "passes every cell through one shared encoder, standardizes each cell's encoder output over time ("norm"), turns it into a bounded vote, and pools…"
- **Verified against a source:** yes.

**4. Section 3, the reference CoactDetect paragraph.**
- **Issue:** "A 1 s guard interval around the window is left out of the context, so an event cannot raise its own threshold" is wrong about the geometry and overstates the guarantee.
  - In `_coact_sliding`, the guard is `[c − guard/2, c + guard/2]`, centred on the window centre `c = start − w/2`.
  - With `guard_sec = 1.0` and `int_win_sec = 2.0` (the reference, from `meta.json`), the guard removes only the *middle* 1 s of the 2 s window.
  - Events in the outer 0.5 s at each end of the window stay in the context and do enter the null.
  - The binned path uses the same rule (`ctr[b] ± guard_sec/2`).
- **Severity:** major. It is a false claim about the reference method, though no number in the report depends on it.
- **Fix:** "a 1 s band at the centre of the 2 s window is left out of the context, so the core of an event does not raise its own threshold (its edges can)."
- **Verified against a source:** yes.

**5. The answer box, third bullet ("by half to three-quarters as much").**
- **Issue:** From both `merge_gap.json` files, the budgeted chorus_gain_norm gap left at a matched merge is 0.455, 0.494, 0.550 and 0.573 of the as-run gap in the first draw, and 0.427, 0.503, 0.596 and 0.722 in the second (at 2, 4, 8 and 16 s). Three of the eight are below one half.
- This wording is hand-typed and not asserted. The generator's assert, a closed share between 0.25 and 0.6, allows 0.43.
- **Severity:** minor.
- **Fix:** "by roughly 40–70% as much", or derive the phrase from `closed`.
- **Verified against a source:** yes.

**6. Section 2, "Every detector joins calls closer than some gap into a single call; that gap is its merge". The same framing appears in Tables 4 and 7.**
- **Issue:** locust's setting `sce_min_distance_frames` is a find_peaks minimum peak distance (`cicada.py`). It *suppresses* the lower of two nearby peaks; it does not join them into one call with a longer span. SPIKE-synch's `max_gap` is a hysteresis sustain, which does behave like a join.
- **Severity:** minor.
- **Fix:** Add "(for locust, the lower of two nearby calls is dropped rather than joined)", or word it as "keeps calls at least some gap apart".
- **Verified against a source:** yes.

**7. Section 8, "Searches that found no admissible setting" ("every one-step neighbor was also over").**
- **Issue:** `coordinate_rounds` evaluates *every value on each axis* from the current state, not just the adjacent ones. So the claim is true, but it understates what was searched.
- **Severity:** minor.
- **Fix:** "every setting reachable by changing one knob across its whole grid was also over."
- **Verified against a source:** yes.

**8. Section 3, the tube bullet ("counts distinct active cells within a pool of about a second and integrates that count over time").**
- **Issue:** This leaves out the defining stage. The share of active cells goes through an area-normalised difference-of-Gaussians centre–surround filter, plus a raw-activity bypass channel. It is the share of the field, not a count, and the filter is not a plain integration. The "about a second" pool is 2·kmin+1 frames, where kmin comes from the fitted minimum centre width (3 frames at initialisation).
- **Severity:** minor.
- **Fix:** "…the share of cells active within a short pool, judged against its own surround in time (centre minus surround)…"
- **Verified against a source:** yes.

**9. Section 3, "copies of the recording in which each cell's events are circularly shifted … wrapping around the end".**
- **Issue:** The runs use sliding CoactDetect and LoCo. They make no copies: the null's moments and quantiles are computed exactly (`sliding.py`), and each cell's events wrap within the 120 s context, not at the end of the recording. The following paragraph partly corrects this for CoactDetect.
- **Severity:** minor.
- **Fix:** "…shifted within a context window around each test window, wrapping at its ends; the sliding detectors compute this null exactly rather than sampling copies."
- **Verified against a source:** yes.

**10. Generator: the `matched_gaps` docstring against its code (`make_replicate_report.py` lines 810 and 823).**
- **Issue:** The docstring says the re-decode must reproduce the run "to within 0.001", but the code asserts `worst < 5e-3`. The actual worst is 0.00147 (tube, first draw, fold 1, under the budget), which is above the documented tolerance.
- **Severity:** minor.
- **Fix:** Make the docstring and the assert agree, for example at 0.002, and say why a small mismatch is expected (GPU re-inference).
- **Verified against a source:** yes.

## Checked and found clean (all against the code or the run files)

- **Scoring (`score.py`, `bench.pool_scores`, `BenchResult`):**
  - Greedy closest-pair one-to-one matching at `TOL_SEC = 2.5`, with calls matched as intervals.
  - Precision excludes `hot_fa` (strictly, false alarms *overlapping* the dense stretch; a matched call reaching into it stays in precision, which is negligible).
  - Hits and calls pooled per background, the two backgrounds' F1 averaged, NaN counted as 0.
  - The ceiling of precision 15/21 and F1 0.83 (distractors fall in 120–1100 s, clear of the 1200–1500 s dense window).
  - The collapse giving F1 exactly 0.125: a whole-recording call is matched, so it is not counted in `hot_fa`.
  - In the archives, the flagged refits in the second draw's fold 1 made exactly 1 call on all 24 held-out recordings, and 0 calls under the budget.
- **Bench:** 33 ROIs over 2700 s; rates 0.0052 and 0.019 (p25 and p75 per the `bench.py` docstring); 15 events at least 120 s apart; recruitment 0.30, 0.18 and 0.10; jitter 0.36 s as a Gaussian standard deviation; 6 distractors placed uniformly without regard to the events; dense stretch 1200–1500 s; empty recording at seed + 100000 with no dense stretch or distractors.
- **Budget:** three ceilings (dense stretch at each background, and the quiet empty recording), each 1.6 × CoactDetect's reference rate on that fold's 72 training recordings, gated with ≤ (so the reference is admissible). The busy empty recording is reported only. A single long call is charged once.
- **Nested CV:**
  - 4 folds of 12 seeds; 24 × 3 × C(4,2) = 432 inner fits, each scored on the two folds outside its pair.
  - Selection maximises the pooled objective; under the budget the candidate is a configuration and a threshold, carried onto the refits.
  - Refits at 5 seeds; nets train on 10 recordings and pick the threshold on 2; the coded search uses 72 recordings with `min_gain` 0.002 and fixed grids.
  - The held-out leak audit exists in `select_learned`.
- **Nets:** a probability per 0.1 s frame; `decode` with ≥ threshold and gap ≤ 20 frames (2 s); the chorus pool (mean, spread, top-m mean, sigmoid vote); chorus_gain_norm adds a learnable gain and bias per channel; line_length's vote is bounded in height but not in its time integral; parameter counts are read from the run's own checkpoints.
- **CoactDetect reference:** 2 s sliding window, exact circular-shift moments over a 120 s context, a one-sided Gaussian z-test at α = 1e-5 (the Gaussian-tail caveat points in the right direction), merge 8 s. The chosen settings are identical under both selections in both draws; the first draw moved α to 3e-5.
- **Paired t-test:** recomputed from `results.json`: t = −13.02 (p = 0.00098) and t = −2.77 (p = 0.0698) on 3 degrees of freedom. The dependence caveat and the Bengio & Grandvalet (2004) citation fit how the folds share training data.
- **Matched merge:**
  - Net re-decode uses the saved checkpoints at the chosen thresholds, changing only `merge_gap_frames`.
  - 6 inexact refits in total (5 in the first draw, 1 in the second), worst 0.0015, as stated.
  - CoactDetect's F1 in the second draw is 0.733, 0.748 and 0.797 at 2, 8 and 30 s, as stated.
- **The two draws:** the code differs only by the replicate option; the declarations differ only in `recording_seeds` and `replicate`; `gpu_jobs = 1`, so "hours of training on one graphics processor" is a fair label for summed fit time.

## Not verified (belongs to role 2)

The Cecchini et al. (2021) characterisation, the Cossart, Aronov & Yuste (2003) surrogate description, and Finn & Johnson (1968). I did check that SPIKE-synch uses a capped-window variant of SPIKE-synchronization (`sync.py`). A cap on the coincidence window is a standard option in the Kreuz lab's tooling, so "an implementation, not a new method" is defensible. The adaptive variant (Satuvuori et al., 2017) works the other way, relaxing the window rather than capping it, so it is not the one used here.

Sources:
- [Measures of spike train synchrony for data with multiple time scales (PubMed)](https://www.ncbi.nlm.nih.gov/pubmed/28583477)
- [arXiv:1702.05394](https://arxiv.org/abs/1702.05394)
