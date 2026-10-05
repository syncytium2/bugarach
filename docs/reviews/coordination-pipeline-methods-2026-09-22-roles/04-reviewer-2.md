# Role 4 — Reviewer 2 (round 1, verbatim as returned)

GRANT 4 ok — Read, Grep, Glob, Bash

# Reviewer 2 (adversarial), round 1: coordination_pipeline_methods.md (fast stream)

I checked the source markdown, all six built page PNGs (page 3 viewed closely; the pages hold text and tables only, no figures), and the four fact notes. I verified the claims against the repo at `main` (34b3359):
- `src/bugarach/simulate.py` (lines 354–399, 640–700, 800–868)
- `src/bugarach/bench.py` (lines 695–830)
- `src/bugarach/assess.py` (lines 368–600)
- `tools/remeasure_bench.py`
- `tools/search_all_settings.py`
- `tools/crowded_check_fair_comparison.py`
- `src/bugarach/detect_folder.py` (`_run_learned`)
- `src/bugarach/detectors/cicada.py` (`threshold_scope`)
- `docs/goals/learned-model-family.md`
- `docs/learned/tuned_vs_coact/{fair_comparison_2026_09_18,replicate1}/crowded_check.json`

Each row gives: location · issue · severity · suggested fix · verified against a source (yes/no).

## Blocking

**R2-01 · "Comparison…", paragraph after "Two selection rules" (lines 245–246).**
- **Issue:** "The close-events test was applied to the coded detectors' choices after the run" reads as a filter, but it was a report only. `crowded_check_fair_comparison.py` says so itself: "It changes nothing about the run; it reports which choices the veto would have refused."
- The check failed **19 of 48** coded choices in the first draw and **16 of 48** in the replicate.
- Under the false-alarm-held rule, LoCo, rate+context and SPIKE-synch fail in **all 4 folds of both draws**. binned SCE fails in 4 of 4 folds on F1 alone (and 3 of 4 gated in the first draw).
- So the gated comparison sets detectors against coded settings that this document's own admissibility rule (Table 2, row 4) refuses. The text says nothing about what was done with a failing choice.
- **Fix:** say it was reported, not applied. Give the counts per detector and selection rule. State what the comparison does with refused choices (excluded, replaced by the reference, or reported as-is). As written, the comparison and Table 2 contradict each other.
- **Verified:** yes (both `crowded_check.json` files).

**R2-02 · "Comparison…", "Coded detectors: the coordinate search above" (line 229).**
- **Issue:** This implies the Table 2 admissibility rule was used. It was not.
  - Precision-change and close-events limits were not applied in the run.
  - "F1 alone" means no admissibility limit at all.
  - The false-alarm rule replaces Table 2's per-detector limits with 1.6× CoactDetect. The fact notes add a floor, `max(1.6× reference, 1 false alarm per measured time)`, which the text omits.
- **Fix:** list exactly which constraints each selection rule used, including the floor.
- **Verified:** yes (fact note 3; the tool docstring).

**R2-03 · Distractors (lines 67–71) and Scoring (line 111).**
- **Issue:** Distractors are built like planted events and cannot be told apart from the 18% level. `simulate.py` lines 803–821 draw them with the same cell count (6 of 33, taking `matlab_round` of 0.18×33) and the same jitter (0.36 s).
- There are six distractors against five 18% positives, and every hit on one counts as a false alarm. No coordination detector can separate them except by chance.
- The consequence: a detector that finds every burst scores P = 15/21 = 0.71 and F1 = 0.83. That is the practical ceiling, and it is never stated.
- The "negative" cannot fail a detector for the property it claims to test. It only adds a flat tax and noise.
- For the learned models it is worse: identical inputs carry contradictory labels.
- **Fix:** justify how a distractor differs from coordination and what the detector could observe to reject it (timing window? nothing?). State the F1 ceiling. Or rebuild distractors with a property a detector could use (e.g. wider jitter, a different spatial or rate signature).
- **Verified:** yes (`simulate.py`, `bench.py` docstring "real coincidence but not coordination").

**R2-04 · "Benchmark recording" measured values (lines 80–90).**
- **Issue:** Participation and jitter are not properties of ground truth. They are outputs of a detector: `assess_coactivity` at K = 4 cells, 1 s bins, uncorrected `jit_obs` and `part_n_obs` (`remeasure_bench.py` lines 27–28 and 111; `assess.py` lines 580–604). Four consequences:
  - The measure is truncated from below. It cannot see an event with fewer than 4 cells, yet the benchmark's 10% level is 3 cells.
  - Jitter is bounded by the 1 s bin and merge rule, so a jitter wider than about 1 s cannot be measured.
  - The observed clusters include chance coincidences; the surrogate (`jit_null`) is computed but not subtracted.
  - "Participation" is a ratio of medians (6 ÷ 31.5), an integer-quantized quantity. The outside-the-interval result for 0.18 vs 0.190 is largely an artefact of that quantization.
- The 30% and 10% levels are not measured at all. `bench.py` calls them "a spread around the measured median".
- **Fix:** say the values were measured with a K = 4, 1 s coactivity clusterer, name the truncation, and state that 30% and 10% are chosen, not measured. Circularity caveat: the benchmark describes what a coincidence counter sees in real data, which favours coincidence-counting detectors (CoactDetect, LoCo) by construction.
- **Verified:** yes.

**R2-05 · "Measured on the baseline analysis windows…" (lines 81–83).**
- **Issue:** This misattributes where the constants came from.
  - The benchmark's shape constants (0.275, 1.547, 1.388) were fitted on a closed `.mat` archive (81 windows). Structural values came from a MATLAB summary. The export measurement is a later re-check that each lies inside its interval (e.g. burst-300 benchmark 1.547 vs measured 1.799).
  - The width distribution comes from an older export (47,225 fast events, "default" folder, measured 2026-09-16), not the dataset described (168,755 fast events).
- **Fix:** give the true origin of each constant. Say the export check is a consistency check (a constant inside a bootstrap interval), not the source. Report the measured point values beside the benchmark values (a table), since several differ materially.
- **Verified:** yes (`remeasure_bench.py` docstring; fact note 2).

**R2-06 · Admissibility limits (line 134, "shipped settings' measured rates plus a margin").**
- **Issue:** This is circular, and the margin is undefined.
  - The limits are set from the shipped settings' own rates, so the shipped setting is admissible by construction. The limits police drift from the starting point, not absolute quality.
  - The shipped settings were themselves retuned on this benchmark (one-knob retune of 2026-09-16: binned SCE 99→98, LoCo, rate+context 5→4.5).
  - The limits differ by detector (elevated-rate limit 1 vs 25 calls/min; precision change 0.10 vs 0.50), so detectors are held to different standards. A cross-detector comparison under those limits is not level.
  - A precision change of 0.50 for binned SCE, or 25 calls/min for locust, is a limit that can essentially never fire.
- **Fix:** define the margin. Disclose the retune history of the "shipped" settings. Justify limits that vary by detector, or report the comparison under common limits.
- **Verified:** partly. The retune history is in fact note 3; I did not find where the margins are derived.

**R2-07 · "Windows" (lines 270–272), with locust (lines 152–155).**
- **Issue:** locust uses `threshold_scope="global"`: one threshold for the whole recording, drug periods included (`cicada.py` line 65). It runs on the whole recording, so its baseline threshold is raised or lowered by senktide, high K+ or TTX activity elsewhere in the same recording.
- For a baseline-vs-treatment rate comparison this is contamination by design: the baseline rate depends on the treatment.
- The code's own rationale for running the learned model per window ("no model gets context across a drug transition that the hand-written detectors were denied", `detect_folder.py` `_run_learned`) contradicts giving LoCo and locust whole-recording context.
- The text never says how the learned detector was windowed; it was run per window.
- **Fix:** state it for every detector, including the learned one. Caveat locust (and LoCo, if its null can span periods) for before/after comparisons, or rerun locust regional.
- **Verified:** yes (locust scope, learned per-window). LoCo's clamping only from fact note 3.

## Major

**R2-08 · Scoring (lines 108–110).**
- **Issue:** The 2.5 s tolerance is unjustified; it was 1.5 s until 2026-08-28. Matching against the whole call interval also gives wide calls a larger effective tolerance:
  - a 10 s SCE bin matches anything in a 15 s span;
  - an 8 s-merged CoactDetect call matches anything within its span plus 2.5 s.
- So F1 is not comparable across detectors whose call widths differ systematically. "Event time" is also undefined: it is the nominal planted time, not the jittered or quantized one.
- **Fix:** justify 2.5 s against jitter (SD 0.36 s, so about 7 SD). Report F1 at a fixed-point tolerance, or report matched-interval widths per detector. Define "event time".
- **Verified:** yes (fact note 2 / `score.py`).

**R2-09 · No-coordination test (lines 98–99).**
- **Issue:** In the settings search the null recordings use the same seeds as the selection recordings. `simulate.py` draws the background first from `RandomState(seed)` (lines 657–690), with the same duration, cell count, rate and shapes. So null recording s has exactly the same background spike trains as quiet benchmark recording s.
- The "no-coordination test" is not independent of the selection data. Its false-alarm rate is measured on backgrounds the search already saw.
- (The fair comparison uses seed+100000 twins, which is fine.)
- The test also runs at the quiet background only, while `bench.py` warns the ranking reorders at busy.
- **Fix:** disclose the shared seeds, or use offset seeds. Report busy-background null rates.
- **Verified:** yes (RNG order; `search_all_settings.py` loops over `(*REGIMES, NULL)` with the same seeds).

**R2-10 · Close-events test (lines 100–104) and limit (Table 2, row 4).**
- **Issue:** Several problems in one test:
  - The quantity is the mean F1 over two backgrounds, not the "largest F1 loss". The limit is unsigned and unapproved.
  - "Crowding" is computed on real-data events, but the text never says which events (detected by which detector?).
  - It never says why 39 of 84 recordings enter.
  - The synthetic tail's realized crowded fraction, 0.61, exceeds the real maximum of 0.57.
  - The check is not symmetric. CoactDetect's reference already carries its 8 s gap, so its check "had nothing to refuse" (`learned-model-family.md`).
  - Every chosen merge gap sits at the edge the check imposed, not at an optimum (all 64 net folds; CoactDetect's 8 s is the top of its grid).
- **Fix:** define it as used. Name the event source and the 39-recording subset. State the asymmetry, and state that merge gaps are boundary solutions.
- **Verified:** yes (goal page, `search_all_settings.make_admissible`).

**R2-11 · Search design (lines 184–191), with the separability rule (lines 250–254).**
- **Issue:** The move step of 0.002 F1 is 5× below the stated between-draw noise of 0.010 F1, so the search moves on noise.
- "Its gain … was bootstrapped (400 resamples)" says nothing about what the bootstrap decided. Was adoption conditional on the 95% interval excluding 0?
- The context grid is capped at the benchmark's 120 s planted spacing (validity rule `context ≤ min_sep`). The benchmark constrains the search space, and that is undisclosed.
- `search_all_settings.py`'s docstring says merge gaps and `min_rois` are "not searched", yet Table 1 shows an 8 s merge gap chosen. Resolve which is true.
- **Fix:** justify 0.002, state the adoption rule, disclose the grid bounds, and reconcile the merge-gap statement.
- **Verified:** partly (docstring vs fact note 3 conflict).

**R2-12 · Separability (lines 250–254) and Replication (line 248).**
- **Issue:** The separability test has very little power:
  - 4 folds, df = 3, critical t = 3.182, corrected by √(3/7) ≈ 0.65. A hostile reader will ask for the minimum detectable margin.
  - The Nadeau–Bengio factor assumes n_train/n_test = 72/24, but the nets train on 10 recordings.
  - The rule uses the two-sided critical value but requires margin > 0. State the α that implies.
- The "independent draw" varies only the seed under the same generator and measured parameters. It replicates Monte Carlo noise, not generator misspecification. It also changed machine, and the goal page reports a systematic +0.015 F1 shift between draws.
- **Fix:** report the detectable margin at this power. Say "not separable" means "not detectable by this test". Rename replication "a second seed draw from the same generator".
- **Verified:** yes (fact notes 2 and 4; goal page).

**R2-13 · Learned vs coded asymmetry (lines 225–236).**
- **Issue:** The two sides were not given comparable data or starting points:
  - Coded detectors are tuned on 72 recordings, starting from settings already optimized on 96 other recordings from the same generator (seeds 1–96).
  - Nets fit on 10 recordings from defaults, with the threshold picked on 2.
  - The gate reference is CoactDetect's own Table 1 setting, so CoactDetect can never fail the false-alarm gate.
  - The real-data model is the untuned default configuration (draw index 23).
  - The real-data run uses the coded starting point (`coded_base`), not any per-fold choice.
- **Fix:** state each asymmetry in the comparison paragraph.
- **Verified:** yes (fact notes 3 and 4).

**R2-14 · Real-data learned detector (lines 258–261).**
- **Issue:** A single refit (fold 0, seed 2), selected by being the median held-out F1 on synthetic data, is applied to real recordings.
  - The threshold (0.972) is taken from a 41-value grid on 2 recordings.
  - chorus normalization z-scores over a 4,096-frame crop in training but over the whole analysis window at inference (13–20 min). The normalization length differs, and a treatment window's own activity sets its normalization.
  - Nothing reports whether the 20 refits agree on real data.
- **Fix:** add the train/inference normalization caveat. Report the spread of real-data call counts across the 20 refits, or state it untested.
- **Verified:** yes (fact note 4).

**R2-15 · Transfer from synthetic to real, whole document.**
- **Issue:** Tuning and evaluation are entirely on synthetic recordings whose parameters were measured on the same recordings later analysed. Four gaps:
  - The benchmark is fixed at 33 cells and 45 min, while real windows run 13–20 min with varying cell counts.
  - The benchmark is stationary; the elevated-rate block is at 0.06 Hz, described in `bench.py` as 1.6× senktide.
  - No section states that no detector was validated against real ground truth.
  - The sliding CoactDetect and LoCo modes, which are the ones used on real data, have no reference implementation (line 162). Their only verification is the synthetic benchmark.
- **Fix:** add an explicit limitations paragraph.
- **Verified:** yes.

**R2-16 · Rates (lines 283–285).**
- **Issue:** "Calls ÷ duration" is not normalized by cell count, but every detector thresholds on cell counts (minimum 3 cells). Recordings or groups with more ROIs yield more chance coincidences.
- Assignment of a call to a window (by onset? by overlap?) is undefined.
- **Fix:** define the assignment rule. Report or adjust for ROIs per recording by group.
- **Verified:** no (window assignment rule by onset not confirmed in code).

**R2-17 · Width and amplitude (lines 293–305).**
- **Issue:** "Amplitude" is cells ÷ width, a rate, and the 0.1 s floor inverts its meaning. A tight 2-cell group scores 20 cells/s; a 53-cell, 26 s chained group scores 2 cells/s.
- The ⚠ caveat is too narrow:
  - "successive events are always less than 0.5 s apart" is an overstatement;
  - it cites the widest CoactDetect call (26.3 s) but not the widest call overall, 64.8 s (rate+context);
  - it omits the 443 zero-width calls and the 283 calls whose core is a single cell.
- The 1 s aperture and 0.5 s gap are unexplained judgement constants.
- **Fix:** rename the measure (e.g. "recruitment rate"), give all three counts, and justify or label the constants as judgements.
- **Verified:** yes (fact note 1).

**R2-18 · Floor-pinning re-measure (lines 91–92).**
- **Issue:** "Repeated on the current export. Every value agreed to four decimal places" is a check that cannot fail. Removing 56 fast events in 3 recordings cannot move medians and percentiles over 84 recordings, especially if the pinned windows fall outside baseline.
- It reads as reassurance about contamination but has no power to detect it.
- **Fix:** delete it, or restate it as "the removal is too small to affect these statistics (56 events in 3 recordings)".
- **Verified:** yes (counts in fact note 1).

**R2-19 · First-treatment window floor (lines 280–281).**
- **Issue:** The 12 min floor sits just below the observed minimum (13.0 min). It is a post-hoc threshold that admits everything, and it is not recorded in the repo. The conflict with the 15 min rule is noted but not resolved.
- **Fix:** state who set it, when, and why. Otherwise report results with the two short windows excluded as a sensitivity check.
- **Verified:** yes (fact note 1: "not in repo").

## Minor

**R2-20 · Unjustified constants.** Each needs a stated source, or a "judgement" label:
- 120 s minimum separation; its rationale exists in `bench.py` ("contaminated null") but is absent from the text
- elevated-rate block 1,200–1,500 s, 0.06 Hz and 30 s ramp; the rationale exists in `bench.py`
- distractor window 120–1,100 s
- 2,700 s duration
- 1.6× false-alarm multiplier
- 409.6 s crops
- 41-value threshold grid
- 24 configurations
- 2 s decode merge
- CoactDetect α = 10⁻⁵
- locust 99.999 percentile with 100 surrogates
- single surrogate seed 20260706, with no seed-sensitivity report

**R2-21 · Undefined quantities.** Each needs a definition:
- the mean of the gamma excess in the renewal process (it is set by span ÷ (m+1) − min_sep and rescaled)
- guard, null context "symmetric", sustain level, synchronous frames, minimum distance
- the population-level basis of rate+context's "excess rate threshold 4.5 events s⁻¹"
- the elevated-rate unit: calls per minute per recording inside the 5-min block
- "per-recording mean event rate per cell": are silent ROIs included?
- whether the 10⁻⁹ parity tolerance is absolute or relative, and on what inputs

**R2-22 · CoactDetect "null's mean and variance are computed exactly … one-sided Gaussian p ≤ α" (lines 145–147).**
- **Issue:** The moments are exact but the p-value is a Gaussian approximation to a Poisson-binomial, deep in the tail (α = 10⁻⁵, a few cells). α is a tuning knob, not a calibrated error rate.
- **Fix:** say so.
- **Verified:** yes (fact note 3).

**R2-23 · SPIKE-synch parity (line 163).**
- **Issue:** Only the coincidence profile was verified against cSPIKE and PySpike; the fact note says "detection layer project's own". Parity for all the ports verifies translation, not correctness: port and reference share their derivation.
- **Fix:** narrow the claim to the profile.
- **Verified:** partly (fact note 3 is ambiguous).

**R2-24 · Participation caveat (lines 86–89).**
- **Issue:** "Every measured value falls inside its 95% interval" inverts the logic: it is the benchmark value that falls inside the measured interval.
- Also say what the 0.18 vs 0.19 gap plausibly does to the reported numbers. The 10% level stays 3 cells; the 18% level stays 6 cells either way, since 0.19 × 33 = 6.27 rounds to 6. If so, the move may change nothing structural, and that deserves stating.
- **Fix:** fix the wording and add that sentence.
- **Verified:** yes (arithmetic; `matlab_round`).

**R2-25 · Pooling across the design (lines 256–285).**
- **Issue:** Tuning and every benchmark number are pooled over nothing the study manipulates, which is acceptable for synthetic data. But the real-data section gives no per-group or per-treatment breakdown of what the detectors ran on: for example, calls per group and detector, or whether any group's recordings run systematically shorter. It defers everything to "a separate analysis".
- **Fix:** at least point to where the breakdown lives.
- **Verified:** no.

**Checked, nothing to report:** the built pages render the tables legibly and contain no figures, so the image-vs-caption lens had nothing to act on. The Nadeau–Bengio factor √(3/7) is arithmetically consistent with n_test/n_train = 1/3.
