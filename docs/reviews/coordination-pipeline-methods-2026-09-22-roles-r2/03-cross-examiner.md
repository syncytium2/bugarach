# Role 3 — Cross-Examiner (round 2, blind pass, verbatim as returned)

GRANT 3 ok — Read, Grep, Glob
(The only other tool I hold is SubagentHandback, the channel this report goes back on. It is not an editing tool, and I hold no Edit, Write or NotebookEdit.)

Role 3, Cross-Examiner, round 2 (blind). Artifact: docs\methods\coordination_pipeline_methods.md at 464d995. I spot-checked the built HTML (coordination_pipeline_methods.html) against the source and it matches on the four strings I searched for. I opened Word pages 01 and 03 (Table 1 and Figure 1). I made no edits.

**Headline:** 19 findings: 7 medium and 12 low, no high. The two most serious are both factual contradictions:
- **F1:** the text says the fast and slow streams come from "the same event detection", but the event counts show the streams have different events.
- **F6/F7:** the planted-interval statistics contradict Figure 1 and the generator code.

## Findings
Format: location · issue · severity · suggested fix · checkable against a source?

1. **Line 20, "Two event streams are exported per ROI from the same event detection"** · The counts rule this out. current_export.toml (`steps_and_pins_excluded`) gives 264,075 events across both streams, and the document gives 168,755 fast events. If both streams came from one detection, the total would be 2 × 168,755 = 337,510. Instead slow has about 95,320 events, so the two streams hold different sets of events. export_folder_spec.md (around line 382) says detection is "methodically identical", meaning the same method, not the same detection. · medium · Write "by the same event-detection method, run separately on each stream", or state the slow count. · yes (toml line 97; spec lines 382–388)

2. **Lines 44–47, floor pinning: "8 inspected windows on 8 ROIs in 4 recordings … 56 fast events … in 3 recordings"** · current_export.toml's producer note says motion correction pinned **12 ROIs** across the same 4 recordings (steps_excluded note, lines 137–139). The census lists 14 ROIs over 6 slices, and on 20260629_312 alone four ROIs pin over one span. 8 ROIs does not match 12 unless only 8 of the 12 had windows removed, and the text does not say that. It also does not say why 4 recordings with windows give events in only 3. · medium · State the basis, e.g. "12 ROIs flagged, 8 windows confirmed and removed", and say that the fourth recording's windows held no fast events. Check against moco_pinned_excluded.tsv, which lists 83 events for both streams. · partly (toml; the tsv was not opened)

3. **Line 103, "re-measured on the baseline analysis windows of the 84 recordings"** · docs/learned/bench_measured.json has `"recordings_measured": 84` but `"recordings_in_shape_fits": 80` (`min_baseline_sec` 900). So the three shape rows of Table 2 rest on 80 recordings, not 84. This is the same population counted on two bases. · medium · "84 recordings (80 for the three shape estimates, which need at least 15 min of baseline)". · yes

4. **Line 339, "LoCo, binned SCE and locust draw their surrogates"** vs **lines 155–157, LoCo "calls when the count exceeds a percentile of the exact null distribution"** · LoCo is described as using an exact null and also as drawing surrogates. bench.py (around lines 529–531) says `n_surrogates` does not apply in sliding mode, and LoCo runs sliding in Table 4. · medium · Drop LoCo from the surrogate sentence, or say its surrogates apply only in binned mode. · yes (bench.py)

5. **Line 140, "In each [coded detector], calls separated by no more than the merge gap are joined into one"** · Table 4 says binned SCE has "no merging". locust has no merge-gap parameter (FULL_GRIDS in bench.py), and SPIKE-synch has a maximum gap instead of a merge gap. Also, GLOSSARY.md "merge gap" says "binned SCE merges by firing times", which disagrees with Table 4. · medium · Replace "In each" with "In rate+context, CoactDetect and LoCo", and reconcile the glossary with Table 4 (bench.py: SCE ships NaN, meaning "do not merge"). · yes

6. **Lines 81–83, "realised intervals … mean 133 s, 5th–95th percentile 121–164 s"** vs **line 91–92, "No planted event falls within 120 s of the block"** · Keeping 120 s clear on both sides of the 1,200–1,500 s block forces one real-time interval of at least 540 s. simulate.py `_place_renewal` places events on a timeline with that stretch cut out, and 133 s is the mean on that shortened timeline. A 95th percentile of 164 s cannot include the interval that spans the block: 1 of 14 intervals is about 7%, which is more than 5%. · medium · "excluding the interval that spans the elevated-rate block (at least 540 s)". Also "fill the recording" should say "fill the recording outside the block and its 120 s margins". · yes (simulate.py lines 376–426)

7. **Figure 1 against the text of lines 81–83** · The figure shows the gap from item 6: the last planted event before the block is at about 17.5 min and the next is at about 29 min, roughly an 11-minute interval, while the text calls the intervals "nearly regular" with a 164 s 95th percentile. The figure otherwise matches its caption and the text: 5 + 5 + 5 planted (▼), 6 distractors (▽) all between 2 and 18 min, the shaded block at 20–25 min, and 33 raster rows. · medium (same fix as item 6) · yes (docx page 03)

8. **Line 304, "Each was scored by inner cross-validation over the three tuning folds with three training seeds"** · The glossary's "inner fit" is "trained on 2 of a draw's 4 folds and scored on the other 2 … 6 pairs of folds × 3 seeds", shared across outer folds. That gives 24 × 6 × 3 = 432, which matches "chorus_norm's 432 inner fits per draw" on goals/learned-model-family.md. The document's version, three tuning folds per outer fold, is a different design. · medium · Describe the pairs-of-folds design, or fix the glossary if the document is right. · yes (GLOSSARY.md, goal page line 91)

9. **Line 318–319, "8 s was chosen in 26 of 32 cases"** · The basis is not stated. 32 = 4 nets × 4 folds × 2 rules for one draw, but which draw? Two sentences later the coded counts give both draws (19/48 and 16/48). The learned-model goal page uses 64 choices across both draws, and its only "26 of 32" is "the chosen threshold is unchanged in 26 of the 32 gated choices". That is the same pair of numbers for a different quantity, so this may be a transcription mix-up. The replicate's net_merge_gap.json includes 2, 5 and 15 s choices. I did not complete a full count. · medium · Name the draw and give the replication's count too, then re-count from net_merge_gap.json and replicate_net_merge_gap.json. · partly

10. **Term "analysis window"** (lines 53–57, 103, 159, 287, 349–351) · GLOSSARY.md "generation window / analysis window" reserves the term for the 60-second cut and says explicitly it is "not the producer's analysis_start_sec/analysis_end_sec span", which is how the document uses it. The glossary's own words for the trimmed window are "region window" and "stats window". · low–medium · Either add a glossary entry for the producer's span and rename the surrogate sense, or use the glossary term in the document. · yes

11. **Line 376, "Width and amplitude are undefined when the window holds no events"** · "window" here means the 1 s selection span around the call's centre (step 1). Nearby, "window" also means the analysis window and the detector windows. · low · "when no events fall within the selection span of step 1". · n/a (internal)

12. **"false alarm" used two ways** · Line 194 defines false alarms as unmatched calls *outside* the elevated-rate block. Lines 311–314 ("false alarms held to CoactDetect's level … in both the elevated-rate and the no-coordination tests") and line 314 ("one false alarm over the measured duration") count calls *inside* the block as false alarms. · medium · Keep "false alarm" for the scoring sense and say "calls in the elevated-rate test" for the other, or define the rule's quantity explicitly. · n/a (internal)

13. **"default setting" (lines 205–206, Table 3, 222, 241, 247)** · GLOSSARY.md separates an "operating point" (the stored, benched setting) from "signature defaults", and bench.py notes that CoactDetect's point is "NOT the coact_detect signature default". "The one published with each implementation" reads as the signature default, but the values meant are the bench operating points. The glossary also retires bare "settings" (the document defines "setting" locally, which is acceptable, but it is not in the glossary). · low–medium · "default setting: the operating point stored with each implementation (bench), after …", and add "setting"/"default setting" to the glossary. · yes

14. **"admissible" (line 204, Table 3)** · The document defines admissible as passing Table 3's four limits. GLOSSARY.md defines it as "chosen within the [shared false-alarm] budget and passes the close-events test", which is the goal-2 sense. So one reserved word has two definitions. · low · Reconcile in the glossary: one term, or qualify one of the two senses. · yes

15. **New terms missing from the glossary** · None of these is in the worktree's GLOSSARY.md: benchmark recording, benchmark seed, objective, default setting, period (the export calls these "regions"; the toml says "238 regions"), coincidence cluster, crowding, separable, population filter, smoothed-fraction filter, cell-set network (with gain), threshold recordings, "the false-alarm rule". The house rule is that new terms go into the glossary in the same change. · low (process) · Add the entries. · yes

16. **Line 145–146 against Table 4, rate+context "its threshold, in events s⁻¹, depends on the number of cells"** · Table 4 gives a single fixed 4.5 events s⁻¹, and the recorded fields range from 10 to 51 ROIs (glossary, K entry). The sentence reads as if the threshold scales automatically. · low · "the appropriate value depends on the number of cells; 4.5 events s⁻¹ was tuned at 33 cells and used unchanged". · partly

17. **Lines 380–382, "Across all calls, 443 had zero width and 283 had a single cell"; widths above 10 s per detector** · The counting basis is unstated: which detectors (six coded, or plus the learned one), which recordings (67 analysed or all 84), which windows (baseline and first treatment, or all). · low · State the population. · no (source not in companion set)

18. **Line 353, "67 recordings, from 36 mice"** · Table 1 has no analysed-mice column. conditioned_run.md line 111 gives 29 senktide recordings from 18 mice and 38 TTX recordings from 23 mice. That makes 36 possible only if 5 mice contribute to both arms, which is not stated. The same passage ("eleven mice contribute two slices and two contribute three") does not reconcile with 67 either. · low · Give the 36 with its overlap, or add the per-group mice to Table 1. · partly

19. **Minor units and wording:**
    - (a) Line 357, "at least 12 min (13.0–20 min)": reads as self-contradictory. conditioned_run.md shows 12 min is a floor and 13.0 min is the observed minimum. Write "floor 12 min; observed 13.0–20 min".
    - (b) Table 4 and line 244 give locust values in frames with no conversion. Add "(0.4 s)" and "(12.8 s)", per the house units rule.
    - (c) Line 79, "10%" for 3 of 33 cells is 9.1%. It is the generator's nominal 0.10 (bench.py `participation=(0.30, 0.18, 0.10)`) and the figure agrees, but say "nominal".
    - (d) TTX is first used in the Table 1 caption (line 29) and defined only at line 354. F1 and precision are used at line 88 and defined at line 199–201. SB222200 and cSPIKE are never defined.
    - (e) The glossary's "no-coordination test" says "one per seed at each background", while the document (line 128) has the quiet background only. The goal-page decision says the busy ones are reported, not gated. Mention the busy ones or align the glossary.
    - (f) The glossary "guard" entry says no operating point sets a guard, but Table 4 has CoactDetect guard = 1 s. The glossary is stale.
    - (g) The subtitle is dated 2026-09-22, one day after today.

    All low.

## Totals reconciled
- **Table 1:**
  - mice 10 + 12 + 12 + 10 = 44 ✓
  - recordings 17 + 22 + 25 + 20 = 84 ✓
  - TTX-first 11 + 9 + 9 + 9 = 38 ✓ and senktide-first 6 + 5 + 10 + 8 = 29 ✓, both matching current_export.toml's ttx and senktide notes per group
  - 38 + 29 = 67, and 84 − 67 = 17 = 12 + 5 ✓
- **Dataset:** 84 recordings and 2,630 ROIs match the toml ✓. The 168,755 fast events cannot be derived from "same event detection" (item 1).
- **Brightness steps:** 9 steps, ±2 s, 9 recordings ✓ (toml: 381 events across both streams; 187 fast is plausible).
- **Planted events and cap:** 15 = 3 × 5 ✓. 10/6/3 of 33 cells ✓. Precision 15/21 = 0.714 and F1 = 0.833 ✓. Elevated-rate block 1,200–1,500 s, 0.06 events s⁻¹, 30 s ramp ✓. Distractor window 120–1,100 s ✓ (bench.py).
- **Table 2:** every value and interval matches bench_measured.json. The in/out-of-interval claim is correct (only participation is outside, lower bound 0.1818). 81 and 85 windows match bench.py. 0.18 × 33 and 0.190 × 33 both round to 6 ✓.
- **Table 3:** all 18 cells match bench.py MAX_PROBE_PER_MIN, MAX_FALSE_POSITIVES_PER_HOUR and MAX_PRECISION_DROP; MAX_CROWDED_DROP 0.02 ✓.
- **Table 4:**
  - rate+context 4.5 / 60 / 1 ✓
  - CoactDetect sliding: α 1e-5, context 120 s, guard 1 s, merge gap 8 s ✓ (bench.py SLIDING_SEARCH)
  - LoCo sliding: 99.9, 8 s, symmetric, 120 s ✓
  - binned SCE: 10 s, 98, 200 surrogates ✓
  - locust: 99.999, 100 surrogates ✓
  - SPIKE-synch: 0.25 / 0.5 / 0.1 / 0.1 ✓
  - Locust minimum distance 16 → 128 frames is three doublings, consistent with "at most three times" ✓
- **Optimisation:** seeds 1–48 and 49–96 give 48 recordings per background ✓. Close-events test 12 seeds per background ✓ (replicate_net_merge_gap.json).
- **Nested CV:**
  - 48 seeds = 4 folds × 12, and 3 folds × 12 × 2 backgrounds = 72 ✓
  - test/train ratio 24/72 = 1/3, and √[(1/4)/(1/4 + 1/3)] = √(3/7) = 0.6547, which matches nb_factor in the json ✓
  - learned refit factor √[0.25/(0.25 + 2.4)] = 0.307 ≈ 0.31 ✓
  - t(3) critical value 3.182 ✓
  - 24 configurations = 23 + 1 ✓
  - 20 refits = 4 × 5 ✓
  - 48 = 6 × 4 × 2 ✓; the three always-failing detectors give 12 of 19 and 12 of 16 ✓
- **Threshold grid:** 12 + 17 + 12 = 41 ✓. 0.972 sits on the upper log-spaced branch (json value 0.97158) and 0.95 is on the grid ✓. 1.6× margin ✓. Merge-gap candidates 0–30 s ✓.
- **Close-events provenance:** 39 recordings, 7 above 0.38, minimum gaps 6–26 s ✓ (bench.py TAIL_RECORDING).
- **Recorded-data windows:** 17–20 min and 13.0–20 min ✓ (conditioned_run.md).
- **Numbering and order:** Tables 1–4 and Figure 1 are numbered in order of first citation ✓. Every section cross-reference resolves ✓. Detector order is the same in the list, Table 3 and Table 4 ✓. Participation order 30/18/10 is the same in text and figure ✓. Group order in Table 1 matches the toml's ttx note ✓.

## What I did not check
- dead-ROI counts (66 / 15 / 18)
- the 127 NA rows
- the 240 s dropped periods
- the learned parameter counts
- the held-out gains 0.034, 0.016, 0.041 and 0.042
- the 0.726 refit value
- the widths section counts

None of these has a source in the companion set. Checking the 26-of-32 count properly needs a full parse of net_merge_gap.json and replicate_net_merge_gap.json.

---
*Transcription note: personal absolute paths were replaced with placeholders (sapper SAP004); nothing else was altered.*
