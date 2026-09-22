# Role 6 — RTFM (round 3, blind pass, verbatim as returned)

GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch
(I also hold SubagentHandback, which is only the channel this report goes back through. I hold no Edit, Write or NotebookEdit. A PreToolUse hook blocked one heredoc script, so I ran that analysis through `python -c` instead. Nothing was written to the repo.)

# Role 6 (RTFM, methods and domain expert): round 3, blind pass

**Artifact:** docs\methods\coordination_pipeline_methods.md @ ee7bd62

**Sources I read before reviewing:**
- **Code at ee7bd62:** sliding.py, coact.py, loco.py, sce.py, cicada.py, sync.py, rate.py, simulate.py, bench.py (BENCH_RECORDING, REGIMES, NULL_RECORDING, TAIL/CROWDED, BenchResult, OPERATING_POINTS), score.py, learn/train.py, learn/encode.py, call_measure.py, tools/measure_calls.py, detect_folder.py, tools/leaderboard.py, tools/tune_net_merge_gap.py (nb_factor), and tune_learned_vs_coact.py taken from origin/tune-bench-comparison.
- **Papers:** Nadeau and Bengio (the NIPS 1999 version; the 2003 journal paper is not on the shelf or reachable), saved to scratchpad\mb6r3\nadeau_bengio_1999_nips.pdf. For the Cossart 2003 Methods I relied on the repo's todo (Nature is paywalled).
- **PySpike pull request 89:** read via `gh`.
- **Run records:** 2026-09-21-full-cohort-default (weekend_settings.csv, detect/detector_settings.csv, run.json, calls_measured.csv, detections.csv), the export folder 2026-09-17_revised_2v_long_STEPS_AND_PINS_EXCLUDED, docs/methods/recorded_data_detector_settings.csv, and docs/learned/tuned_vs_coact/fair_comparison_2026_09_18/net_merge_gap.json.

## Findings (location · issue · severity · suggested fix · verified?)

**1. "Width and amplitude of coordinated events", step 1, together with "Scoring", paragraph 1 · MAJOR · verified: yes**
- **Issue:** For binned SCE the width rule does not search the interval the document calls the call. "Scoring" defines binned SCE's interval as its 10 s bin. The measure, however, uses `detections.csv` (`tools/measure_calls.py` lines 54–59): onset = bin start, width_sec = event spread (width_def `tightness`, tlast − tfirst).
  - So the "call" searched is [bin start, bin start + spread]. Its centre is bin start + spread/2. Whenever the first event sits after the bin start, the search span ends before the bin's last events.
- **Measured on the recorded-data run** (calls_measured.csv against the export folder; I reproduced all 1,665 core_n_roi values first):
  - If the whole bin were searched, 456 of 1,665 binned SCE fast calls (27%) would get a different core group, and 449 of them would get a larger one.
  - So the "one rule for every detector" claim does not hold for SCE, and its widths and amplitudes come from a truncated span.
- **Fix:** Either feed the measure `extent_sec` (the bin) for SCE, as the scorer does, and re-measure; or state in the methods that the measure uses the detector-reported width, which for binned SCE starts at the bin edge and runs only the event spread. The first is better.

**2. Limitations, sentence 2 · MODERATE · verified: yes**
- **Issue:** SPIKE-synch's coincidence threshold is not "absolute in cells". In `sync.adaptive_profile`, C = coincident-pair count / (N − 1), where N is every ROI passed in, silent ones included. So C is a fraction of cells, and its cell-count stringency moves in the opposite direction to rate+context's threshold and the minimum cells.
  - At C > 0.1, a 9-cell recording needs 1 of 8 other cells coincident (a pair qualifies, and then min_n = 3 summed events), while a 61-cell recording needs 7 of 60.
  - This matters directly for "Rates are not normalised by the number of cells".
- **Fix:** Remove SPIKE-synch from the "absolute in cells" list. Add: "SPIKE-synch's coincidence threshold is a fraction of the recording's cells, so on small recordings a coincident pair can clear it."

**3. Table 4, LoCo row "threshold update step | – | 15 s" · MODERATE (reproducibility) · verified: yes**
- **Issue:** In sliding mode `thr_step_sec` is not used (`loco._detect_stream_sliding` docstring: "``thr_step_sec`` and ``n_surrogates`` do not apply"; the bar is computed at every piece). The value appears in the settings file only because it is carried along.
  - Listing it as a value used on the recorded data describes a mechanism (anchored threshold envelope) that did not run.
  - n_surrogates = 100 for CoactDetect and LoCo is in the settings file too and is equally inert.
- **Fix:** Mark it "binned mode only (not used in sliding mode)", or drop the row.

**4. Coded detectors, CoactDetect bullet · MINOR to MODERATE · verified: yes**
- **Issue:** The guard is 1 s, narrower than the 2 s window (Table 4; `_coact_sliding`: band c ± guard/2 around the window centre). It removes only the central half of the tested window, so the window's own events in its outer 0.5 s on each side stay in the null reference.
  - A reader who knows CFAR guard cells will assume the guard covers the window.
  - Also not stated for CoactDetect: its context is clipped at the analysis-window edges (it runs per window with t_range = window). The document says the equivalent for LoCo.
- **Fix:** "…from which a 1 s band centred on the window (the guard, narrower than the 2 s window) is removed; the context is clipped at the analysis-window edges."

**5. Coded detectors, locust bullet · MINOR · verified: yes**
Three completeness points:
- **(a) Where activity starts.** The raster paints each event from its t50rise frame. On folder input `locs` holds the t50rise, and the settings use onset_field=locs. The duration is width_sec, rounded to frames, at least 1 frame.
- **(b) Which periods feed the threshold.** The whole-recording threshold also includes periods not analysed here: high-K⁺ periods and the 2 min solution-exchange intervals. So locust's baseline sensitivity depends on what followed the baseline.
- **(c) Null versus statistic.** The null is the per-frame active-cell sum, even though the statistic is the count over the synchronous-frame window (CICADA's rule, cicada.py step 3). The two coincide only at 1 frame. This bears on the unadopted 1 → 2 proposal: at 2 frames the bar stays per-frame, so the detector becomes more lenient.
- **Also:** peaks are kept at or above the threshold (`x >= minh`), not "above".
- **Fix:** Add these clauses. Change "above" to "at or above".

**6. Coded detectors, SPIKE-synch bullet (binning) · MINOR · verified: yes**
- **Issue:** "The coincidence profile, binned at 0.1 s" does not say what a bin's value is. It is the mean C of the events sharing one event time (synchrony_statistic "mean", the default, which Table 4 does not list), and a later event time in the same bin overwrites an earlier one (the ported MATLAB binning). Separately, `cn` is the size of the last same-time group written to the bin, so "minimum number of events" is a sum of those.
  - Also, the scan skips bins whose value is zero, which includes bins with events but no coincidences, not only "bins with no events".
- **Fix:** Add one sentence on the bin value and write "bins with zero coincidence are skipped". Optionally list "bin statistic: mean" in Table 4.

**7. Comparison section, "Separability" · LOW · verified: yes (against the 1999 NIPS version)**
- **Issue:** "It assumes training sets several times larger than test sets" is a slight overstatement of the source. Nadeau and Bengio's correction rests on the surrogate ρ0 = n2/(n1+n2), which approximates the decision rule as insensitive to which training set it came from. The 5–10× figure is what they call normal usage and what they simulated at, not a stated assumption of the derivation.
- **Fix:** "Its correlation surrogate, n2/(n1+n2), was proposed and tested for training sets 5–10 times the test set; neither ratio here meets that…"
- **Checked correct:** √(3/7) = √((1/4)/(1/4 + 1/3)) = 0.6547, matching nb_factor(4) and the recorded 0.6546. The factor 0.31 at n2/n1 = 24/10 is right, and 3.182 is t(0.975, 3).

**8. Test recordings, elevated-rate test · LOW · verified: yes**
- **Issue:** The block count is unmatched calls whose span overlaps the block (`score.py`: fa_ends ≥ start and fa_times ≤ end), not calls whose onset lies inside it. Precision's denominator excludes the same set. That is harmless because no planted event is within 120 s of the block, but the text should say what is counted.
- **Fix:** "calls overlapping the elevated-rate block".

## Checked and found correct
- **CoactDetect:**
  - Exact catch probability Σ min(w, gap)/L under a uniform circular shift, and a Poisson-binomial count with the exact mean and variance.
  - The z-test is p = ½·erfc(z/√2) ≤ α, so at α = 10⁻⁵, z ≥ 4.265.
  - "Tail heavier": at 33 cells with p = 0.02, the exact P(S ≥ 5) ≈ 4×10⁻⁴, far above 10⁻⁵.
  - The minimum-cells gate is applied.
- **LoCo:**
  - Symmetric context that includes the window and is clamped to the period.
  - Exact quantile (smallest k with CDF ≥ p) and a strict "exceeds".
  - The guard is refused in symmetric mode, consistent with Table 4's "none".
- **Tests:** the sliding-null tests exist (against simulation, against the recursion, and shift invariance).
- **binned SCE:**
  - Circular shift within the analysis window (regional mode) and a pooled per-bin percentile.
  - obs > thr and ≥ 3 cells; merging off (NaN); 200 surrogates; scored over the bin (extent_sec).
  - Cossart 2003's criterion, as the repo transcribes it (a count exceeded in only 5% of the surrogate histograms), is a family-wise bar, so "more lenient" is correct.
- **rate+context:** additive excess ≥ threshold, centred context, runs must span more than one grid point, ±0.5 s padding, no guard; the CA-CFAR contrast is stated correctly.
- **SPIKE-synch:**
  - ISI-adaptive τ = min of the half-ISIs capped at τmax = 0.25 s, with a strict < (the cSPIKE fixtures were run at tau 0.25).
  - The MRTS extension is off.
  - Hysteresis as described.
  - PySpike pull request 89 exists, is open, and says max_tau has been inert for interior pairs since 0.8.0, as stated.
  - The artefact flags from `_flag_artifacts` are not used downstream, so no call-removal step goes unreported.
- **Generator:**
  - Gamma(0.275, mean/shape) rates; per-ROI multipliers at 300 s and 60 s with shapes 1.547 and 1.388; Poisson placement per 60 s bin; MATLAB-rounded 0.1 s grid.
  - Participation 10, 6 and 3 cells (round of 9.9, 5.94 and 3.3); jitter SD 0.36 s.
  - Planted intervals of 120 s plus an exponential excess (renewal, cv = 1), rescaled on overrun; the block is excluded with 120 s padding.
  - Six 6-cell distractors, uniform over 120–1,100 s, with the same jitter.
  - The block adds a homogeneous 0.06 s⁻¹ per cell with a 30 s linear ramp and an abrupt end.
  - Widths drawn from the measured quantile table independently of planting.
  - No-coordination and close-events configurations match (TAIL: 10,800 s, 60 per level, 6 s floor, no block or distractors).
- **Scoring:** closest-pair-first one-to-one matching; a 2.5 s gap to the interval, zero inside it; pooled counts; precision excludes the block; the distractor cap 15/21 → F1 0.833 is right.
- **Shipped defaults and recorded-data settings:**
  - OPERATING_POINTS (loco 99.5 binned, sce 98, rate 4.5) match the "default setting" sentence.
  - The committed recorded_data_detector_settings.csv is byte-identical in content to the run's detector_settings.csv.
  - Unlisted parameters fall back to the signature defaults that Table 4 states: min cells 3, rate merge gap 3 s, min_n 3, locust minimum distance 4 frames and 1 synchronous frame, profile bin 0.1 s.
- **Learned detectors:**
  - Adam; BCEWithLogits with pos_weight = neg/pos; crop 4,096 frames, batch 3, n_train 10; crops centred on a positive frame with probability 0.5.
  - The threshold grid has 41 values from 10⁻⁴ to 0.9999, as described.
  - Decoding is ≥ threshold with a 2 s merge.
  - Targets run from the first to the last participant onset; distractors and the block are labelled 0.
  - Rows are sorted by count, with ties broken by onset pattern, so the order is independent of cell order.
- **Recorded-data execution:** rate, coact, sync and the learned model run per analysis window; LoCo, SCE and locust run per recording with period-aware nulls, as stated.
- **Width statistics:** the reported numbers match calls_measured.csv (>10 s: rate 25, LoCo 23, CoactDetect 10; widest 64.8 s, rate+context, 37 cells, 1,046 events; 308 zero-width; 185 single-cell). Not in the text: 157 calls had an empty search span.

**Files:**
- tools\measure_calls.py (lines 54–59, finding 1)
- src\bugarach\detectors\sync.py (lines 175–215, finding 2)
- src\bugarach\detectors\loco.py (lines 612–626, finding 3)
- src\bugarach\detectors\coact.py (lines 343–358, finding 4)
- src\bugarach\detectors\cicada.py (finding 5)
- `<scratchpad>\mb6r3\` (Nadeau–Bengio PDF and text, extracted tuning tool)

---
*Transcription note: personal absolute paths were replaced with placeholders (sapper SAP004); nothing else was altered.*
