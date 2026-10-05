# Role 4 — Reviewer 2 (round 2, blind pass, verbatim as returned)

GRANT 4 ok — Read, Grep, Glob, Bash (also SubagentHandback, the report channel; no editing tools held)

Reviewer 2, round 2 (blind pass). Artifact: `docs\methods\coordination_pipeline_methods.md` (464d995). I also looked at Figure 1.

**Summary.** The methods section is precise and unusually open about what it does. Its weak points are design choices it states without drawing the consequence:
- the benchmark penalises detecting events at the participation level it measured;
- detectors tuned only at baseline rates are applied across a treatment that changes the rate;
- locust's threshold spans baseline and treatment;
- the width rule depends on the background rate;
- the comparison is in-distribution for the learned detectors;
- there is no statistics section for the recorded data.

Each row is: location · issue · severity · suggested fix · checked against a source. [TEXT] marks a disclosure or precision fix. [PIPELINE] marks a design fix.

## Blocking

**B1. Line 7 vs. lines 85–88 (Distractors) and line 101: the scoring punishes detecting events at the measured participation level.** [PIPELINE + TEXT]
- Line 7 defines a coordinated event as cells co-firing more often than chance. Distractors meet that definition, yet they are scored as false alarms.
- They are placed at 6 cells, which is exactly the 18% level that line 102 calls "the measured participation", the most realistic event class.
- Arithmetic under the stated scoring:
  - Detect the 30% and 10% levels only: F1 = 0.80.
  - Detect every planted event and every distractor: F1 = 0.83.
  - Detect the 30% and 18% levels (and so the distractors): recall 10/15, precision 10/16, F1 = 0.645.
- So learning to see 6-cell events gains 5 true positives and costs up to 6 false alarms. The objective barely rewards, and can penalise, sensitivity to the realistic event size. Every search, admissibility decision and learned-versus-coded ranking inherits this.
- Fix (pipeline): give distractors a different participation or jitter from any planted level, or report F1 with and without them.
- Fix (text): at minimum, say that the distractors satisfy the paper's own definition of a coordinated event, and state this consequence for the objective.
- Checked: yes. Distractor settings in `src/bugarach/bench.py` (BENCH_RECORDING: `distractor_frac=0.18`, `distractor_window=(120,1100)`); F1 values by arithmetic from the text's own scoring rules.

**B2. Recorded-data analysis, lines 336–360: no statistical analysis is specified.** [TEXT + PIPELINE]
- There are 84 recordings from 44 mice, four groups, and a baseline-to-first-treatment contrast. Nothing says how group or treatment effects are tested, how recordings nested in mice are handled, or which of the 7 detectors is primary.
- There is no multiplicity plan across 7 detectors × 2 measures (rate, width/amplitude) × groups × treatments.
- Fix: add a statistics subsection (for example a mixed model with mouse as a random effect), and name a primary detector or state that all are reported. If the results are descriptive, say "described, not tested".
- Checked: yes (the text itself).

## Major

**M1. Line 351, locust: one threshold per recording, baseline and treatments together.** [PIPELINE]
- Locust's null rolls activity over the whole recording. A high-rate senktide period therefore sets the threshold for everything, and exceeds that shared null simply because its rate is higher. Baseline is pushed under.
- The repository's own binned SCE docstring rejects this for SCE: a whole-extent wrap "would dilute a high-rate window's events and over-detect". Locust keeps `threshold_scope="global"` anyway, and Table 3 allows it 25 calls min⁻¹ in the elevated-rate block.
- On the cohort run, locust's fast-stream calls are senktide 2,763 vs baseline 998. CoactDetect's are 317 vs 428, the opposite direction. These are whole-period counts, not window-normalised.
- Fix: run locust with `threshold_scope="regional"`, or exclude it from treatment contrasts and say why.
- Checked: yes. `src/bugarach/detectors/cicada.py` (lines 65–66, 224); `sce.py` (lines 10–15); `2026-09-21-full-cohort-default/detect/detections.csv`.

**M2. Synthetic recordings, lines 74–76 and 90–92: detectors are tuned and validated only at baseline rates, then applied across treatments that change the rate.** [PIPELINE + TEXT]
- The quiet and busy backgrounds are the 25th and 75th percentiles of baseline rates. No benchmark puts planted events on a senktide- or TTX-like background; the elevated-rate block has no planted events. Recall at treatment rates is therefore unknown.
- So a change in call rate between baseline and treatment cannot be separated from a change in detector sensitivity.
- Fix (pipeline): add treatment-matched backgrounds carrying planted events.
- Fix (text): state this limitation in the Analysis section.
- Checked: yes. `bench.py` REGIMES; the text.

**M3. Line 91: the 0.06 events s⁻¹ elevated rate is unjustified in the text.** [TEXT]
- The code justifies it as 6× the measured baseline rate and 1.6× the senktide rate. The text gives no reason, and its 30 s ramp also goes unexplained.
- Fix: carry the justification into the text.
- Checked: yes. `bench.py`, around line 783.

**M4. Lines 98–105 and Table 2: the re-measurement is a consistency check, not a validation, and it inherits the measuring method's biases.** [TEXT, partly PIPELINE]
- Cell count, jitter and participation are re-measured with the same kind of coincidence-cluster method that set them: `assess_coactivity` at K = 4, 1 s bins, onsets gathered within ±1.5 s of the cluster centre (`wm_factor=1.5`).
- Participation comes from clusters of at least 4 cells. The 3-cell level is invisible to it, so the median is biased upward. The text says the method "cannot see smaller events" but not what that does to the median.
- Jitter is the raw observed median onset SD (`jit_obs`), not the excess over the null. `jit_null` is computed and not used. Chance onsets from other cells inside ±1.5 s enter both jitter and participation.
- "Every benchmark value lies inside the 95% interval" therefore cannot detect a bias in the method.
- Fix: call it a re-measurement by the same method, and state the K = 4 floor and the uncorrected jitter. Ideally, show the method recovering known jitter and participation on benchmark recordings.
- Checked: yes. `tools/remeasure_bench.py` (lines 27, 59, 110–138); `src/bugarach/assess.py` (`_clusters`, `wm_factor=1.5`, lines 588 and 602).

**M5. Lines 131–136, close-events spacing: derived from CoactDetect's calls, so it is bounded by CoactDetect's resolution.** [TEXT + PIPELINE]
- A detector with a 2 s window and a merge gap cannot report gaps below that gap. The "shortest gaps 6–26 s" are partly a property of the instrument, and the 6 s spacing inherits it. The merge gap used in the earlier export is not stated.
- The 0.38 crowding cut and the 30 s neighbour radius are unjustified.
- Fix: state the setting used, note the bias, and justify or sweep the cut.
- Checked: no (the earlier export was not inspected).

**M6. Table 3 caption, lines 211–212, and lines 240–243: the close-events reference for CoactDetect and LoCo is the binned default, not the like-for-like sliding default.** [TEXT, partly PIPELINE]
- The adopted sliding settings lost 0.041 and 0.042 F1 against the sliding default, about twice the 0.02 allowance. They pass only because the reference is the binned mode.
- Fix: justify the choice of reference, or report that they fail against the sliding default.
- Checked: yes (the text's own numbers).

**M7. Table 3 caption: the limits were "set by judgement above the rates measured at each detector's default".** [TEXT]
- Admissibility therefore means "no worse than now". It cannot reject a default, and it is not comparable across detectors (locust 25 calls min⁻¹, binned SCE precision change 0.50). The admissibility check has no power over the default by construction.
- Fix: say so plainly, give the measured default rates beside the limits, and do not present admissibility as an absolute false-alarm standard.
- Checked: yes (the text).

**M8. Comparison section, lines 296–334: the comparison is uneven and in-distribution.** [TEXT + PIPELINE]
- The learned detectors' merge gap is constrained by the close-events limit. The coded detectors' is not, and 19 of 48 coded choices would have failed it. That favours the coded detectors on F1.
- The tuning budgets differ: 24 configurations with inner cross-validation for the learned detectors, a coordinate search for the coded ones. So do the training sizes: 10 recordings versus 72.
- "Replication" (line 324) is a second seed draw from the same generator. The learned detectors can exploit generator regularities the coded ones cannot: near-regular spacing (121–164 s), always 33 cells, Gaussian jitter, and distractors confined to 120–1,100 s.
- Fix (text): call it a second draw from the same generator. State that the comparison is in-distribution for the learned detectors and that generalisation to recorded data is untested. State the direction of the close-events asymmetry.
- Fix (pipeline): apply the same constraints to both arms.
- Checked: yes (text; `bench.py` BENCH_RECORDING).

**M9. Line 311: the false-alarm rule is anchored to one competitor at 1.6×, with no justification for 1.6.** [TEXT]
- Fix: justify 1.6, or show the ranking at 1× and 2×.
- Checked: yes (the text).

**M10. Width and amplitude, lines 362–382: the measurement rule depends on the background rate, and it was never validated on ground truth.** [PIPELINE + TEXT]
- The 0.5 s chaining gap links chance events whenever the rate is high. That is exactly the senktide condition being compared with baseline: one "coordinated event" spans 64.8 s and 1,046 events. That is a period, not an event.
- The rule has not been shown to recover the known width or participant count of planted benchmark events.
- The 1 s window and the 0.5 s gap are "by judgement".
- Fix: validate the rule on benchmark recordings, including at treatment-matched rates. Report widths with a rate-matched null, or cap chaining. Disclose the direction of the bias for the treatment contrast.
- Checked: yes. `calls_measured.csv` reproduces the long-width counts (fast: 25, 23 and 10 calls).

**M11. Lines 359–360: rates are not normalised by cell count, while cell count varies and dead-ROI screening covered only 66 of 84 recordings.** [TEXT + PIPELINE]
- rate+context's threshold is a fixed 4.5 events s⁻¹, which the text itself says depends on cell count. The learned detector was trained only on 33-cell recordings.
- 18 recordings were never screened for dead ROIs, so cell count and per-cell rate are unevenly defined across recordings.
- Fix: report cell count per group, and include it as a covariate or show rates per cell.
- Checked: partly (`n_roi_recorded` column in `detections.csv`; distribution not tallied).

**M12. Lines 56–57 and 353–357: order and time confound, plus an unjustified 2 min lag.** [PIPELINE + TEXT]
- Baseline is always the last 20 min before treatment, and treatment always follows it. There is no time or vehicle control, although the 5 untreated recordings could provide a time-matched one.
- The 2 min lag after treatment onset is not justified (for example by wash-in time).
- Fix: justify the 2 min, and add or discuss a time control.
- Checked: yes (the text).

## Minor

**m1. Line 382: counts from both streams in a fast-only document.** [TEXT]
- "443 had zero width and 283 had a single cell" counts both streams.
- The fast stream alone has 308 zero-width calls, 185 single-cell calls, and 157 calls with undefined width. The learned detector's calls are not in this file.
- Fix: give the fast-stream counts, and say "coded detectors".
- Checked: yes (`calls_measured.csv`).

**m2. Lines 344–345: the refit used on recorded data was chosen by its held-out F1.** [TEXT]
- Choosing "the upper of the two middle held-out F1 values" uses test-fold scores to select the model.
- Recorded-data variability across the 20 refits is not assessed.
- Fix: say so, or run all 20 refits on the recorded data and report the spread.
- Checked: yes (the text).

**m3. Line 339: one surrogate seed.** [PIPELINE]
- Call-level stability under other surrogate draws is unreported.
- Fix: re-run with 2–3 more seeds and report the fraction of calls that are stable.
- Checked: yes (`detector_settings.csv`, `rng_seed=20260706`).

**m4. Table 4, LoCo: a setting in the run is missing from the table.** [TEXT]
- The run's settings include `thr_step_sec = 15` (the threshold is recomputed every 15 s), which Table 4 does not list.
- CoactDetect's settings list `n_surrogates=100` while the text says its null is exact. Say whether that parameter is unused.
- Checked: yes (`detect/detector_settings.csv`).

**m5. Table 2, "set from" column.** [TEXT]
- "81" and "85" baseline windows differ from the 84 recordings, and name no dataset.
- Say these came from an earlier archive (the code gives 81 windows and 2,643 ROIs).
- Checked: yes for 81 (`bench.py` MEASURED_RATE_SHAPE); no for 85.

**m6. Unjustified constants, beyond those above.** [TEXT]
- 2.5 s matching tolerance.
- 0.002 F1 move threshold.
- 0.02 close-events allowance.
- 2.0 s step-exclusion radius.
- 240 s trailing-period cut.
- 20 min window cap.
- 4,096-frame crop.
- 2 s learned merge gap in decoding.
- Fix: one clause of justification each, or "set by judgement".
- Checked: yes (the text).

**m7. Line 158: binned SCE's 10 s bins cannot resolve the paper's own 1 s definition.** [TEXT]
- Fix: note this where the detector is described.
- Checked: yes.

**m8. Lines 262–265: learned labels and scoring use different anchors.** [TEXT]
- Labels span the first to last participating event; scoring uses the nominal pre-jitter time.
- Standardisation spans a 409.6 s crop in training but the whole window (up to 1,200 s) on recorded data. That shift is disclosed but was never tested.
- Checked: yes (the text).

**m9. Lines 46–48: residual floor-pinning contamination.** [TEXT]
- Two kept recordings are below the screening cut, and one analysed recording is unscreened.
- Fix: name them and give a sensitivity analysis excluding them.
- Checked: no.

**m10. Separability, lines 327–334: no multiplicity handling across the contrasts.** [TEXT]
- There are about 96 contrasts: 4 learned × 6 coded × 2 rules × 2 draws.
- It is disclosed as descriptive, which is acceptable, but say that no multiplicity adjustment was made. The √(3/7) and 0.31 factors check out arithmetically.
- Checked: yes (computed).

**m11. Figure 1, read as a picture.** [TEXT]
- All six distractors sit in the first ~17 min, and none after the block.
- One sits almost on top of an 18% planted event (about 2.2 min).
- Two distractor pairs are about 10–15 s apart (about 3.5 min and 16 min).
- So the stated cap (precision 15/21, F1 0.83) holds only when no distractor falls within 2.5 s of a planted event or within a merge gap of another distractor.
- Fix: state the minimum distractor spacing, or qualify the cap as nominal.
- Checked: yes (Figure 1 image; distractor window in `bench.py`).

## Also checked, no finding
- The CoactDetect z = 4.26 at α = 10⁻⁵ is correct.
- The Nadeau–Bengio factor derivation is correct.
- The retune of 2026-09-16 used seeds 1–48 (`tools/retune_operating_points.py`, line 110), so the held-out seeds 49–96 are not contaminated.
- binned SCE is region-wise inside `sce.py`, consistent with line 348, even though `detect_folder.py` passes it the whole recording.
- The cohort run's settings match Table 4 for the fields listed.

This was a blind pass: I did not read any round-1 review files.

---
*Transcription note: personal absolute paths were replaced with placeholders (sapper SAP004); nothing else was altered.*
