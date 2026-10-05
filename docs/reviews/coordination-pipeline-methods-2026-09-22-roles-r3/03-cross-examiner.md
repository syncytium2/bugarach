# Role 3 — Cross-Examiner (round 3, blind pass, verbatim as returned)

GRANT 3 ok — Read, Grep, Glob

(SubagentHandback is also present; it is only the channel for this report, not an editing tool. I hold no Edit, Write or NotebookEdit.)

# Role 3, Cross-Examiner: round 3 blind pass
Artifact: `docs\methods\coordination_pipeline_methods.md` (ee7bd62). I also opened page 3 of the Word build to check Figure 1 against its caption and the text.

## Summary
Every count and total I could trace reconciles, and so does every Table 2 value. The remaining defects are: one table-numbering-order error, one Table 4 row that has no effect in the mode it is listed for, the Table 4 caption promising a settings file that holds only some of the table's values, and five terminology or companion-doc conflicts.

## Findings
Each row gives: location · issue · severity · suggested fix · verifiable against a source?

1. **Table 3 and Table 4 are out of order.** *Coded detectors*, l.163, says "Table 4 lists every parameter…". Table 3 is first cited at l.248 (*Scoring*), so the tables are not numbered in order of first citation.
   - Severity: medium (journal requirement).
   - Fix: swap the numbers, so the parameter table becomes Table 3 and the limits Table 4. Update the 9 citations and move the tables to match.
   - Verifiable: yes (the text itself).

2. **Table 4, LoCo "threshold update step – | 15 s".** This is listed as a value used in sliding mode. `src/bugarach/bench.py` l.529–531 says "`thr_step_sec` and `n_surrogates` do not apply in this mode". The CSV also carries `n_surrogates=100` for coact and loco in sliding mode, which is likewise unused.
   - Severity: medium.
   - Fix: drop the row, or mark it "binned mode only; no effect in sliding".
   - Verifiable: yes.

3. **The Table 4 caption says the value column is what the recorded-data run used, "the run's settings file is `recorded_data_detector_settings.csv`".** The CSV holds only a subset of Table 4. About 15 Table 4 values have no row in it:
   - minimum cells for every detector;
   - the rate+context and binned SCE merge gaps;
   - rate+context guard and threshold form;
   - CoactDetect guard normalisation;
   - locust synchronous frames, minimum distance and threshold scope;
   - SPIKE-synch minimum events, window rule and profile bin;
   - every detection mode.

   The CSV also has keys that Table 4 does not list (`rng_seed`, `grid_dt`, `onset_field`, `imaging_rate_hz`). A reader cannot check the table against the file.
   - Severity: medium.
   - Fix: add to the caption that the file lists only values passed explicitly and that the rest are the implementations' signature defaults.
   - Verifiable: yes.

4. **Two different "32"s: 26 of 32 in the methods versus 26 of 32 on the goal page.** Methods l.415 says 8 s was chosen in 26 of 32 cases (4 architectures × 4 folds × 2 rules, first draw). I **verified** this against `fair_comparison_2026_09_18/net_merge_gap.json`: `config_kept` gaps are 26 × 8 s, 3 × 5 s, and one each of 15, 3 and 2 s. `docs/goals/learned-model-family.md` l.134 also has a "26 of the 32", but on a different basis (threshold unchanged, gated choices, both draws).
   - Severity: low. The methods number is correct.
   - Fix: none in the methods. Flag it so no one "reconciles" the two.
   - Verifiable: yes.

5. **l.441: "not the 8 s gap re-selected for it".** The detector used on recorded data comes from the replication. The only re-selection the text reports is for the first draw (l.415). The claimed 8 s for this refit has no stated basis in the text. I did not open `replicate_net_merge_gap.json`.
   - Severity: low.
   - Fix: give the replication's re-selected gap for that fold and rule, or say "the gap re-selection chose for it in the replication".
   - Verifiable: no (not checked).

6. **Elevated-rate block, l.104: "about 6 times the measured baseline rate".** The text defines two measured rates just above: 0.06/0.0052 is about 12× and 0.06/0.019 is about 3×. The 6× comes from an older 0.0096 figure (bench.py l.767, l.786), or from the current median, 0.0102 (bench.py l.642). The GLOSSARY "elevated-rate test" entry says "about 12× the quiet background". So the counting basis is unstated and the glossary disagrees with the text.
   - Severity: medium.
   - Fix: "about 6 times the median baseline rate (0.0102 events s⁻¹ per cell; 12 times quiet)". Align the glossary.
   - Verifiable: yes.

7. **The no-coordination test is quiet-only in the methods but at each background in the glossary.** Methods l.145–148 say the recordings are generated "at the quiet background", and bench.py `NULL_RECORDING` agrees. The GLOSSARY entry says "one per seed at each background". Its "shared false-alarm budget" entry says busy no-coordination recordings exist in the comparison and are "reported, not gated". The methods' false-alarm rule (l.404–407) does not say which backgrounds are gated.
   - Severity: low–medium.
   - Fix: in the false-alarm rule, say "elevated-rate test at each background and no-coordination test at the quiet background", and fix the glossary's first sentence.
   - Verifiable: yes.

8. **"admissible" is a reserved word used with a different meaning.** The GLOSSARY defines it for goal 2 as "chosen within the budget and passes the close-events test". The methods redefine it as "meets the Table 3 limits" (l.248) and use it in the coordinate search.
   - Severity: medium (glossary rule).
   - Fix: update the glossary entry to the Table 3 sense, noting the goal-2 usage, in the same change.
   - Verifiable: yes.

9. **Retired words.**
   - Bare "adaptive" is RETIRED in the GLOSSARY. Methods l.204 ("the adaptive window itself") and Table 4 SPIKE-synch "window rule… adaptive, fixed / adaptive" use it bare. Fix: "ISI-adaptive".
   - Bare "setting" / "settings" is RETIRED in the GLOSSARY. The methods define "setting" locally (l.245), which is defensible, but the new sense is not added to the glossary. Other new terms are also missing from it: "search span", "core group", "planted spacing", "nominal time", "benchmark seed", "threshold recordings", "false-alarm rule", "separable".
   - l.395, "its budget replaced them": "budget" is never defined in the methods.
   - Severity: low–medium.
   - Fix: replace the bare words, add the entries, and change "budget" to "the false-alarm rule's limit".
   - Verifiable: yes.

10. **"archive" is used for two things, and the companion toml uses it for a third.** In the methods it means both "the laboratory's archive" of 85 recordings (l.53) and "an earlier archive" with 81 and 85 windows (l.117, Table 2 "archive windows"). In `current_export.toml`, `use = "archive"` means a superseded export. Table 2 also says "earlier export" for the rates, and the reader cannot tell whether the earlier export and the earlier archive are the same thing, or whether the 85 windows are the 85 archive recordings.
    - Severity: medium.
    - Fix: name the source once, for example "the laboratory's .mat store (85 recordings)", and say whether the rate source is a different export.
    - Verifiable: partly (bench.py: 81 windows, 2,643 ROIs).

11. **The quiet and busy rates read as present-tense measurements, but Table 2 dates them earlier.** l.85–87 present the rates as the 25th and 75th percentiles of the per-recording baseline rate, which reads as the present dataset. Table 2 says they were "set from earlier export", and the present data re-measure quiet at 0.0050, not 0.0052.
    - Severity: low.
    - Fix: "…percentiles, measured on an earlier export (Table 2)".
    - Verifiable: yes.

12. **Width counts are reported although the cover memo says not to report them.** l.474–476 quote "Among the coded detectors' calls…": 25, 23 and 10 calls above 10 s, 308 with zero width, 185 with a single cell. Cover memo §1, defect 2, says binned SCE width and amplitude come from the wrong interval and "results for the detectors named should not be reported". The pooled counts include binned SCE. They also have no denominator and no basis: which stream, which windows, and 67 or 84 recordings.
    - Severity: medium (the methods and the memo contradict each other).
    - Fix: restrict the counts to the unaffected detectors, or hold them until the fix. State the basis ("fast stream, baseline and first-treatment windows of the 67 recordings, N calls").
    - Verifiable: no for the counts; yes for the contradiction.

13. **The bench.py docstring contradicts the methods on planted-event spacing.** Methods l.95–97 say the intervals were "nearly regular: mean 133 s, 5th–95th 121–164 s", which implies a CV of about 0.1. `bench.py` `BENCH_RECORDING`'s docstring (l.801) says the realized spacing "stays irregular (CV ~0.8)". The methods' number is the measured one, so the docstring is probably stale. Cover memo §6 does not list it.
    - Severity: low (the defect is in the companion).
    - Fix: add it to memo §6 as a stale note.
    - Verifiable: yes.

14. **The CSV's locust `onset_field` reads as the peak.** The CSV gives `locs` for locust and `t50rise` for every other detector. The GLOSSARY "onset field" entry says `locs` = peak. bench.py l.557–559 says that on an export folder `locs` holds the half-rise. The methods say nothing, so a reader of the companion CSV will conclude locust anchors on the peak.
    - Severity: low–medium.
    - Fix: one clause in the locust bullet or the Table 4 caption: "anchored on t50rise (the code field `locs`, which on an export folder holds t50rise)". Reconcile the glossary.
    - Verifiable: yes. Note that the two companions disagree with each other.

15. **The CSV's slow-stream rows are stale against `main`.** The CSV lists SPIKE-synch slow `max_gap=0.5` and CoactDetect/LoCo slow values identical to fast. `main` has since adopted slow settings (a7af85e: SPIKE-synch 4 s `max_gap` on slow; 11ea5ef: slow LoCo and CoactDetect). The CSV is a historical run record, but it ships beside a fast-only methods section with no note.
    - Severity: low.
    - Fix: strip the slow rows, or say "run record; slow rows predate the slow tuning".
    - Verifiable: yes (commit messages).

16. **SPIKE-synch hysteresis does nothing at the values used.** l.206–208 describe a start threshold and a separate sustain level. Table 4 gives both as 0.1, so the rule as described has no effect at the setting used.
    - Severity: low (text and table agree, but the reader is misled).
    - Fix: add "(equal at the values used, so no hysteresis operates)".
    - Verifiable: yes (CSV `C_min` = `C_threshold` = 0.1; bench.py).

17. **Minor wording.**
    - The Nadeau–Bengio paragraph (l.424–429) switches from a "test-to-training ratio of 1/3" to "3 for the coded detectors", which is training-to-test. Name the direction both times.
    - l.348 says each learned detector's merge gap "was selected inside the cross-validation", but the deployed detector runs at 2 s, not at the selection.
    - The Figure 1 caption says "no detections overlaid"; the glossary term is "calls".
    - The methods say "replication" and the memo says "replicate". Pick one.
    - Severity: low.
    - Verifiable: yes.

## Checked and consistent
- **Table 1.** Mice 10+12+12+10=44; recordings 17+22+25+20=84; TTX-first 11+9+9+9=38; senktide-first 6+5+10+8=29; 38+29=67; 84−67=17=12+5.
  - Per-group TTX and senktide counts match `current_export.toml` (ttx: DI 11, MALE 9, ORX 9, OVX 9; senktide: ORX 10, OVX 8, DI 6, MALE 5) and `conditioned_run.md`.
  - 85 − 1 withdrawn = 84 recordings; 2,630 ROIs matches the toml.
- **Analysis windows.** Baseline 17–20 min and treatment 13.0–20 min match `conditioned_run.md`. The 12-min floor, "all 67", and the memo's 13.0 and 14.9 min match.
- **Pinning and steps.** 12 ROIs in 4 recordings; two recordings kept below the cut; ±2 s around 9 confirmed steps. All match the toml.
- **Table 2.** All 8 constants, re-measured values and intervals match `bench_measured.json` after rounding. 84 and 80 recordings and 200 bootstrap draws match. Every constant lies inside its interval except participation (0.18 < 0.182). 0.19 × 33 rounds to 6 cells.
- **Table 3.** All 24 limits match bench.py `MAX_PROBE_PER_MIN`, `MAX_FALSE_POSITIVES_PER_HOUR`, `MAX_PRECISION_DROP` and `MAX_CROWDED_DROP`.
- **Table 4.** Every grid range matches `FULL_GRIDS`. The default retunes (99→98, 5.0→4.5, 99.9→99.5 binned) match the `OPERATING_POINTS` sources.
- **Benchmark design.**
  - `BENCH_RECORDING` matches: 2,700 s, 33 cells, (0.30, 0.18, 0.10), 5 events per level, jitter 0.36 s, 120 s spacing, block 1,200–1,500 s at 0.06 with a 30 s ramp, 6 distractors at 18% in 120–1,100 s.
  - Close-events test matches `TAIL_RECORDING`: 60×3=180 events, 6 s, 10,800 s.
  - Median width 0.9 s matches `MEASURED_WIDTH_QUANTILES`.
- **Scoring arithmetic.** 15/21 precision gives F1 = 0.833. Distractors give 5 true positives against 6 false alarms.
- **Cross-validation arithmetic.** 48 seeds in 4 folds of 12; 3 × 12 × 2 = 72 recordings; 4 × 5 = 20 refits; 4 × 4 × 2 = 32 cases; 6 × 4 × 2 = 48 choices.
  - The replication's 16 = 3 detectors × 4 folds + binned SCE × 4. This matches the goal page's "8 of 8 folds" for binned SCE.
  - √(3/7) = 0.6547, which matches `nb_factor` in net_merge_gap.json. The ~0.31 factor at 10 vs 24 recordings is correct. t(0.975, 3) = 3.182.
  - The 0.972 threshold matches the grid value 0.97158 in the JSON.
- **Figure 1** (page 3 of the Word build). 5 ▼ per level, 6 ▽ (two pairs overlap), shaded block at 20–25 min, 33 cells, distractors all before 18.3 min, no planted event within 120 s of the block. It agrees with its caption and the text.
- **Cross-references.** *Scoring*, "next section", "the search above" and "false-alarm rule below" all resolve. The methods' section order matches cover memo §5.
- **Methods against the memo.** Everything the memo quotes matches the methods: 19/48 and 16/48; 0.040 and 0.042 against 0.02; 9–61 cells; 64.8 s and 1,046 events; F1 cap 0.83; the three proposed changes not adopted; 67 recordings from 36 mice; 1.6×; the 2 s against 8 s merge gap. The only exception is finding 12.
- **Units.** Every number carries a unit, apart from dimensionless quantities (F1, percentiles, α, shapes, thresholds), which Table 2's caption declares.

## Not verifiable from the companions
168,755 fast events; 87 empty-ROI rows; 187 and 56 removed fast events; 36 mice; 1.6× the senktide rate; mean 133 s and 121–164 s; 7 of 39 crowded recordings; 1,149–1,905 and 1,122–4,565 trainable weights; 0.726; the held-out gains 0.034 and 0.016; all width counts.

---
*Transcription note: personal absolute paths were replaced with placeholders (sapper SAP004); nothing else was altered.*
