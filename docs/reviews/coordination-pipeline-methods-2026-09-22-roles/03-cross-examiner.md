# Role 3 — Cross-Examiner (round 1, verbatim as returned)

GRANT 3 ok — Read, Grep, Glob

Role 3 (Cross-Examiner): findings for round 1 of the methods-section review.

**Artifact:** `docs\methods\coordination_pipeline_methods.md`. The build is `...\scratchpad\methods_build_r0\coordination_pipeline_methods.html`. I checked its headings and table captions against the source and they match.

**Companion docs checked:** `docs/GLOSSARY.md`, `current_export.toml`, `docs/export_folder_spec.md` (rev 6–7), `docs/conditioned_run.md`, `docs/goals/coded-detector-optimization.md`, `docs/learned/tuned_vs_coact/README.md`, `docs/todo/2026-09-21-bench-participation-to-0-19-after-the-meeting.md`, and the four fact notes in `scratchpad\methods_facts\`. I did not run `tools/leaderboard.py` because I have no execution tool. The artifact quotes no leaderboard result, so nothing depends on it.

**Canonical group order:** DI, MALE, ORX, OVX (`conditioned_run.md` table; accepted as canonical in the 2026-09-12 v2 review). Both group listings in the doc follow it. **Canonical detector order** (GLOSSARY): rate+context, CoactDetect, LoCo, binned SCE, locust, SPIKE-synch. The prose list, Table 1 and Table 2 all follow it.

## Totals that reconcile (no finding)
- 84 recordings = 17+22+25+20. 44 mice = 10+12+12+10.
- First treatments: 38 TTX + 29 senktide + 12 SB222200 + 5 none = 84.
- TTX split 11+9+9+9 = 38, senktide 6+5+10+8 = 29. Both match `current_export.toml`'s ttx/senktide notes and `conditioned_run.md`.
- Floor-pinned removals: 38+25+20 = 83 events.
- Participant counts 10/6/3 = round(0.30/0.18/0.10 × 33).
- Tables 1 and 2 match the fact notes and the bench constants cell for cell.
- √(3/7) = √((1/4)/(1/4+1/3)). 3.182 is the two-sided 95% critical value at 3 df.
- Architecture parameter range 1,149–1,905. 20 refits = 4 folds × 5 seeds. 72 tuning recordings = 36 seeds × 2 backgrounds.
- The seven benchmark values said to be inside their intervals are inside them.

## Findings
Format: location · issue · severity · suggested fix · verifiable against a source?

1. **Lines 121–123 vs 139/165 · Tables are numbered out of order.** "Table 2" is cited and printed (Scoring) before "Table 1" is first mentioned (Coded detectors). The group table at lines 25–30 has no number or caption, so there are three tables and two numbers. · MEDIUM · Number tables in order of appearance: groups = Table 1, admissibility = Table 2, settings = Table 3. Alternatively, move the Scoring limits after Coded detectors. Update every "Table 1 setting" reference (lines 243, 258). · yes

2. **Lines 32–37 · Artifact-removal counts pool both streams in a section scoped to the fast stream.** 381 events is fast 187 + slow 194. 83 events is fast 56 + slow 27. Line 22 separates fast from slow, but these counts don't, so the same "events" changes basis within two paragraphs. · MEDIUM · Give fast counts (187 and 56) with the both-stream totals in parentheses, or label them "across both streams". · yes (facts 01; `current_export.toml`)

3. **Line 36 · The pinned-window recording count is on a different basis from the producer's.** The 8 windows sit in 4 recordings (`20250926_235` had 0 events removed); `current_export.toml` says "the four that were cleaned". The doc says 3 recordings, which counts recordings that lost events. The archived `steps_excluded` note says 12 ROIs across 4 slices, while the doc and facts say 8 windows on 8 ROIs. · LOW–MEDIUM · Write "8 windows on 8 ROIs in 4 recordings; events were removed in 3 (83 events)". Get the producer to confirm 8 vs 12 ROIs. · partly (8 vs 12 needs the producer)

4. **Lines 76–78 vs 80–92 · The width distribution was not measured on the export the section says it was.** Lines 80–92 imply every generator input was measured on the current export (bootstrap, then repeated after pin removal). The width quantiles came from 47,225 fast events on `2026-08-18_revised_2v_periods`, which `current_export.toml` says "predates both artifact removals" and has no analysis windows. The 47,225 count also differs from the 168,755 fast events in line 22, and the doc doesn't say why. · MEDIUM · State the width source export and event basis, or re-measure on the default export. · yes (facts 02 line 8; `current_export.toml` [periods_2026_08_18])

5. **Lines 88–89 · The claimed cost of the participation move doesn't follow from the doc's own numbers.** At 33 cells, round(0.18 × 33) = round(0.19 × 33) = 6, so the middle level plants 6 cells either way (as does the 18% distractor, line 70). The doc says the move "regenerates every synthetic recording and requires the tuning below to be rerun". That is true only if something besides the participant count changes (RNG path, the 0.30/0.10 spread the todo leaves open, distractors). · MEDIUM · Say what actually changes in the planted events, or note that the participant count is unchanged at 33 cells. The todo should make the same check. · yes (arithmetic; todo 2026-09-21)

6. **Line 83 · The interval sentence inverts the relationship.** The interval belongs to the measurement; what falls inside it is the benchmark value. As written ("Every measured value falls inside its 95% interval"), it is almost true by construction. · LOW · "Every benchmark value falls inside the 95% interval of its measurement except participation." · yes

7. **Line 94 vs 96 · "Three further recording types" includes one that is not a recording type.** The elevated-rate test is defined as the calls in a block of each benchmark recording. GLOSSARY confirms it is "a 5-minute stretch of every bench recording". · MEDIUM · "Three tests measure specific failures: one reads a block of each benchmark recording, two use recordings of their own." · yes

8. **Lines 101–103 · The crowding basis is unexplained.** "7 of 39 recordings": the dataset has 84 recordings, or 67 in the analysis set, and 39 matches neither. Crowding is "the fraction of events whose nearest neighbour lies within 30 s", but it doesn't say which events. Coordinated events found by the assessor is the likely meaning, and 168,755 calcium events would give a different number. The 0.38 cutoff is also unexplained. The fact note records conflicting crowded fractions in the source (38/39/34%). · MEDIUM · Name the 39-recording subset and how it was chosen, name the events, and justify 0.38. · partly (`probe_real_crowding.py`)

9. **Line 98 vs GLOSSARY "no-coordination test" · The two definitions differ.** The doc restricts the test to the quiet background. GLOSSARY says it is generated "one per seed at each background", with busy reported but not gated. The doc is right about what is gated; only the definitions disagree. · LOW · "…at the quiet background (a busy-background twin is generated and reported, not gated)". · yes

10. **Table 1 caption, lines 165–167 · "which the search did not change" is contradicted by the goal page.** `docs/goals/coded-detector-optimization.md` says the every-knob search did propose changes for the other four, for example locust's minimum distance to 12.8 s at +0.119 held-out F1, unbracketed. None was adopted: commit 55c857a says "none of it is adoptable yet". The shipped values themselves include the 2026-09-16 one-knob retune (binned SCE 99→98, rate+context 5.0→4.5), which the doc never describes. · MEDIUM · "The other four use their shipped settings. The search's proposals for them were not adopted." Add one sentence on the one-knob retune that produced the shipped values. · yes

11. **Lines 180–187 vs goal page and facts 03 · The optimization description omits a stage.** The every-knob search also ran two-axis grids (binned SCE percentile × bin, LoCo percentile × context, locust percentile × synchronous frames) and a rescue rule for an inadmissible start. The doc presents a pure one-at-a-time search. · LOW–MEDIUM · Add the stage-2 grids, or say they are omitted. · yes

12. **Lines 229–230 vs 182 and facts 03 · The comparison section says the coded side ran "the coordinate search above", but it was a different search.** In the comparison:
    - CoactDetect and LoCo started from their Table 1 values, not their shipped settings (step 1).
    - There were no two-axis grids.
    - Edges were reported rather than refused.
    - The Table 2 precision-change and close-events limits were not applied in the run. Line 245 admits this only for close-events.

    Readers will assume the Table 2 admissibility applied. · MEDIUM · List the differences explicitly, including the start point and that the precision-change limit was not applied. · yes

13. **Line 243 · The false-alarm rule omits a floor.** Facts 03: the budget is max(1.6 × the CoactDetect reference, 1 false alarm per measured time). Units are also inconsistent across the project: Table 2 gives the elevated-rate test in calls min⁻¹, the comparison computed it per hour, and GLOSSARY lists both code names. · LOW · Add the floor, and give the unit the comparison used. · yes

14. **Line 157 · Bare "adaptive", which GLOSSARY retires.** "with an adaptive coincidence window" should use the reserved term. · MEDIUM (reserved-word rule) · "an ISI-adaptive coincidence window (the minimum of the four surrounding half inter-spike intervals, capped at 0.25 s)". · yes

15. **Lines 180, 166, 139 · "settings" appears bare.** "Each detector's settings were chosen" and "the settings they ship with" are borderline under GLOSSARY's retirement of bare "settings". Table 2's caption ("detector setting") is correct. · LOW · Use "detector settings" consistently. · yes

16. **Lines 121, 184 vs GLOSSARY "shared false-alarm budget" · "Admissible" means two things across the project.** The doc uses it in the goal-1 sense (passes all four Table 2 limits). GLOSSARY also defines "admissible" in the goal-2 sense (chosen within the false-alarm budget and passing close-events). The doc avoids the word in the comparison section, which is good, but a reader of both documents meets two meanings. · LOW · Keep the goal-1 definition here, and flag the collision for the glossary owner. · yes

17. **Lines 293–304 vs GLOSSARY "firing" and "width of a coordinated event" · Terminology collides in the width and amplitude section.**
    - "Events" means both calcium events and coordinated events ("the coordinated event is the group…", "629 events").
    - "The widest CoactDetect call is 26.3 s" reports a coordinated-event width (`core_span_sec`), not the call's own width, which is the distinction the section opens by drawing.
    - The 26.3 s figure is CoactDetect only. The widest across all six detectors is 64.8 s (rate+context), so "widths above about 10 s arise this way" understates the range.

    · MEDIUM · Say "calcium events" for members. Write "the widest coordinated event measured in a CoactDetect call is 26.3 s", and give the six-detector maximum. · yes (facts 01)

18. **Line 96 · "call" is used before it is defined.** It is defined at line 108 (Scoring). · LOW · Move the definition up, or define it at first use. · yes

19. **Lines 217–218 vs 246 · Merge-gap re-selection is referenced but never described.** Decoding describes a fixed 2 s merge. Line 246 then refers to "when their merge gap was re-selected", a step the doc never describes. GLOSSARY and facts 04 say it was re-selected over {0,1,2,3,5,8,15,30} s on the inner fits without retraining, with 8 s chosen in 26 of 32 choices. The real-data model kept 2 s. Also, "less than 2 s apart" vs the code's ≤ 20 frames. · MEDIUM · Describe the re-selection in Decoding. State that the real-data model decodes at 2 s, and use "at most 2 s". · yes

20. **Lines 258–261 · The selection rule for the real-data model is not named.** The "20 refits" are the gated selection's. The chosen configuration is also the untuned default (draw index 23), which a reader would want to know. · LOW · "…selected with false alarms held to CoactDetect's level (the untuned default configuration was chosen for fold 0)…". · yes

21. **Lines 265–268 · The window ranges are on a narrower basis than the text implies.** "17–20 min" and "13–20 min" are ranges over the 67 analysed recordings and their first treatments, per facts 01 and `conditioned_run.md`. The text defines windows for every recording and period (all 84 were run). · LOW · "(17–20 min in the 67 recordings analysed; first treatments 13–20 min)". · yes

22. **Lines 280–281 vs `docs/conditioned_run.md` lines 55–71 · The 12-minute floor is not in the repo.** The only written rule is `conditioned_run.md`'s 15-minute minimum (Tony, 2026-09-09), which the doc calls "an earlier rule". Facts 01 records the 12-minute floor as an in-session ruling of 2026-09-21. The two windows are consistent: 13.0 min is `20241211_127` (MALE, TTX) and 14.9 min is `20250912_227` (ORX, senktide). · MEDIUM · Record the 12-minute ruling in `conditioned_run.md` in the same change, or keep 15 min and state the two exceptions. · no (the ruling is not in the repo)

23. **Line 39 vs GLOSSARY "regime" entry · The withdrawn-recording count differs.** The doc (and `current_export.toml`: `20250731_149`) say one recording was withdrawn. GLOSSARY says the `.mat` store "carries the two recordings the lab withdrew". These are different bases, export vs store, so the doc is right for the export. Separately, facts 01 notes the producer also dropped 2 trailing treatment periods under 240 s, which line 40 ("no further exclusion") leaves out. · LOW · Keep "one". Optionally add "two trailing treatment periods shorter than 4 min were dropped by the imaging pipeline". Flag the glossary wording to its owner. · yes

24. **Lines 154–156, 163 · Citations are missing or incomplete.**
    - CICADA is named but not cited. GLOSSARY gives Zenodo 10.5281/zenodo.10041434 and Hamon et al. 2026.
    - cSPIKE and PySpike are uncited.
    - The in-text "(Kreuz et al.)" has no year, while every other citation has one.

    · MEDIUM · Add the references, and write "(Kreuz et al., 2015)". · yes

25. **Line 161 vs facts 03 · The 10⁻⁹ parity claim is uniform across ports that were not all checked the same way.** CoactDetect's parity is RNG-stream parity, and binned SCE's is not stated in the facts. For SPIKE-synch, the facts say the profile was cross-validated to 10⁻⁹ and the "detection layer [is the] project's own", so line 163 overstates. · LOW–MEDIUM · Scope SPIKE-synch's claim to the coincidence profile. Confirm binned SCE's parity tolerance. · partly

26. **Line 139 · "Table 1 summarises each detector and the settings"** — the table lists parameter values only. · LOW · "Table 1 lists the settings…". · yes

27. **Table 2, close-events row · "largest F1 loss" misstates the quantity.** Per the facts, the limit is a mean-F1 drop of at most 0.02; "largest" reads as a maximum over something. · LOW · "close-events test, maximum allowed drop in mean F1 vs. the setting it replaces". · yes

28. **Line 172 caption, line 166 · A cross-reference names the wrong heading.** It points to "*Optimization*", but the heading is "Optimization of coded detectors". · LOW · Match the heading. · yes

29. **Line 25 vs 22 · The same population is called "animals" and "mice".** · LOW · Pick one. · yes

## Outside the artifact (for the main thread)
`docs/goals/coded-detector-optimization.md` line 79 says the sliding switch for LoCo and CoactDetect "is NOT on yet". Table 1 and the real-data run use sliding mode. Either the goal page is stale or the real run used an unlanded branch. Check before the doc asserts sliding as the shipped mode.

---
*Transcription note: personal absolute paths were replaced with placeholders (sapper SAP004); nothing else was altered.*
