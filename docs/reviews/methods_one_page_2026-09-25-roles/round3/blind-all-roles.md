GRANT: I hold Artifact, Bash, Edit, Glob, Grep, Read, Skill, ToolSearch, Write, SubagentHandback, mcp__ccd_session__spawn_task/dismiss_task, the mcp__Claude_Code_Remote__* tools, mcp__Claude_Docs__batch/guide/update, and WebSearch/WebFetch (loaded through ToolSearch). I used Bash, Read, ToolSearch and WebSearch, plus Crossref through curl. I edited no repo file. The only file I wrote is scratch: <scratch>/mb3/plain.txt. I opened nothing under docs/reviews/ and read no git log messages.

Artifact reviewed: docs/methods/one_page/methods_one_page.html and .pdf, at worktree HEAD ef79c848. The PDF is newer than the HTML and the builder, has 2 pages, and carries a stamped Title and Author.

Headline: the page has no blocking defects but eight major ones. Four state something the code or the decision record contradicts: the event floor, the event time, the decoys and the budget rule. The rest are a mis-credited origin, the unscored lowest level, a forward reference, and a test that fails unless run against the worktree source.

## Findings (role · location · issue · severity · fix, net length · verified)

1. **Role 1/4 · Event floor, sentence 1.** "A call needs at least the event floor of ROIs co-active within 2 s" is false for Chorus.
   - Chorus calls are thresholded frames with no floor applied. The floor is `min_rois` only for CoactDetect, LoCo, SCE and sync (`src/bugarach/bench.py` `FLOORED_SETTING`).
   - ADR-0010 part 6 says a detector without a participation setting "runs unfloored".
   - **Major.** Fix: "A *coordinated event* needs at least…", and say where the floor acts: it is CoactDetect's minimum, and planted events under it leave the score. Net about 0.
   - Verified: yes.

2. **Role 1/4 · Output, "The event time is the core's first onset".** This states an open decision as settled.
   - `tools/measure_calls.py` keeps the detector's `onset_sec` unchanged. It only adds `core_first_sec` as a column.
   - `docs/decisions_pending.md` ("Under check") and `docs/todo/2026-09-22-what-the-full-cohort-rasters-show.md` item 3 leave open whether the emitted onset should come from the call measure (#698). CLAUDE.md forbids restating an undecided item as settled.
   - **Major.** Fix: "The event time is the detector's call onset; the core's first onset is reported beside it (which one is the event time is undecided)." Net about +0.3 line.
   - Verified: yes.

3. **Role 4/3/1 · Simulated recordings ("decoys … not scored") and Scoring ("calls on decoys count against precision").** Two problems in one place.
   - The two phrases read as a contradiction.
   - The page presents a contested choice as settled. ADR-0006 says the decoys are coordination by construction: a middle-level event with only the label changed. The glossary entry for "distractor" calls counting them an open question. `tools/score_bench_candidates.py` reports F1 both ways.
   - The shape claim itself checks out: `distractor_frac` is 0.18, 0.38 and 0.24 against middle levels of 0.203, 0.375 and 0.25, at the same jitter.
   - **Major.** Fix: "(built like middle-level events; calls on them cost precision, and F1 is also reported with them left out)". Net about +0.4 line.
   - Verified: yes.

4. **Role 1 · Scoring, "budgets set from … measured rates … with headroom (1.6×, never below 1)".** The stated rule does not reproduce the budgets listed.
   - Fast CoactDetect's calls-per-hour budget is 7 from a measured 4.4. The 1.6× rule would give ceil(7.04) = 8 (`bench.py` `MAX_FALSE_POSITIVES_PER_HOUR`).
   - The 0.10 precision budget comes from a different rule: measured plus 0.05, at least 0.10 (`tools/measure_slow_budgets.py` `ceiling_swing`). Fast's is measured 0.01 against a limit of 0.10.
   - The numbers themselves (7, 1, 10; 1 call per minute; 0.10) are correct, and the test pins them.
   - **Major.** Fix: drop "(1.6×, never below 1)". Net about −0.2 line.
   - Verified: yes.

5. **Role 2 · "after Pipa et al., 2007" and its reference.** The origin is mis-credited.
   - Pipa, Riehle & Grün 2007 (Neurocomputing 70(10–12):2064–2068) is a re-analysis that applies NeuroXidence. Metadata confirmed by Crossref; content from the abstract, found by web search.
   - The method paper is Pipa, Wheeler, Singer & Nikolić 2008, J Comput Neurosci 25:64–88. It is on the shelf (`docs/lit_needed.md`) and was read. The 2007 paper has no shelf record.
   - The trace stops one step short: Pipa 2008 credits the multiple-shift antecedent to Grün et al. 1999, which is not held.
   - **Major.** Fix: cite Pipa et al. 2008. The reference sits on page 2, so page 1 is unchanged.
   - Verified: yes, from metadata and abstract. The 2007 full text was not read.

6. **Role 2 · CoactDetect, "excess-coincidence tests against a shifted null (Amarasingham et al., 2012)".** Amarasingham 2012 is about the jitter method: interval and window resampling of individual events, framed as conditional inference. It is not about shifting a whole train.
   - Metadata is correct: J Neurophysiol 107(2):517–531, doi:10.1152/jn.00633.2011, confirmed by Crossref.
   - **Minor.** Fix: "tests of excess coincidence against a local resampled null". Net 0.
   - Verified: partly. Metadata yes; I did not open the paper's text (it is on the shelf).

7. **Role 4 · Parameters and Simulated recordings, three planted levels.** The page never says that on the realistic bench the lowest level falls entirely under the floor, so it is never scored.
   - Fast: 16 of 16 events. Slow: 35–40 of 40. Combined: 48 of 48.
   - On busy combined, 75% of the middle level is also under the floor (`docs/learned/runs/2026-09-25-realistic-bench/README.md`).
   - A reader will assume three scored levels.
   - **Major.** Fix: "(the lowest falls under the floor and is left out of the score)". Net about +0.4 line.
   - Verified: yes.

8. **Role 11/8 · Scoring paragraph.** It names CoactDetect and "its shipped settings" before the CoactDetect paragraph introduces them, and "shipped" is never defined. In the CoactDetect paragraph, "held-out F1 gain" has no referent: the gain is over the shipped setting.
   - **Major (order).** Fix: move the budget sentence to the end of the CoactDetect paragraph, and write "shipped (current)" and "gain over the shipped setting". Net about +0.1 line.
   - Verified: yes.

9. **Role 1/4 · Parameters, Background: "coordinated onsets removed".** No onsets are removed.
   - The coordinated share of the rate is estimated with factorial cumulants against per-cell surrogates and subtracted, without deciding which onsets are coordinated (`bench.py` `REGIMES`).
   - It is measured over the 63 recordings that clear the shape floors, not all 66.
   - **Minor.** Fix: "coordinated share subtracted". Net 0.
   - Verified: yes.

10. **Role 4 · Output, "never under-counts … but over-counts".** This reads as "always over-counts". Fast is exact for 75% of events.
    - **Minor.** Fix: "never under-counts and sometimes over-counts". Net 0.
    - Verified: yes (`call_measure_summary.json`, README table).

11. **Role 3 · Unit rule.** Some counts are bare numbers:
    - "(fast 7, slow 17, combined 19)" needs "events".
    - "(OVX, 17)", "(MALE, 13)", "(ORX, 19)" carry no "recordings" after the first.
    - **Minor.** Fix: "fast 7 events…". Net about +0.1 line. `tests/test_methods_one_page_numbers.py`'s string for the event counts must change with it.
    - Verified: yes.

12. **Role 3 · Timing windows.** The definition says "within about a second". The floor counts "within 2 s", participation uses "within 1 s", and the within-event SD is about 0.1 s. None of the three is reconciled with the definition.
    - **Minor.** Fix: drop "about a second" from the definition, or say the 2 s window is the operational one. Net 0.
    - Verified: yes.

13. **Role 3 · Two F1 aggregations.** Scoring pools per background and averages the two. Benchmark pools each seed's quiet and busy recordings. Both match the code (`search_all_settings` and `score_bench_candidates.per_seed_f1`), but a reader sees two F1s.
    - **Minor.** Fix: none needed, or add "(a per-seed F1)". Net 0.
    - Verified: yes.

14. **Role 3 · Glossary.** "combined" (the stream) has no entry in `docs/GLOSSARY.md`, and new terms are supposed to be added in the same change. The "decoy" alias is present.
    - **Minor.** Fix: add a glossary row. Page length unchanged.
    - Verified: yes.

15. **Role 1 · Chorus, "A participation variant sums the votes".** The count sums a separate per-ROI vote (a 1×1 convolution and a sigmoid, `participation.vote_head`), not the channel votes that feed the pool.
    - **Minor.** Fix: "sums a separate bounded per-ROI vote". Net about +0.05 line.
    - Verified: yes (`src/bugarach/learn/nets/chorus.py`).

16. **Role 1 · CoactDetect, "by coordinate search".** The search also runs two-setting grids for the pairs known to interact (stage 2 in `tools/search_all_settings.py`).
    - **Minor.** Fix: "by coordinate search and paired grids". Net about +0.05 line.
    - Verified: yes.

17. **Role 8 · Input.** A cold reader is never told what distinguishes *fast* from *slow* ("assigned upstream"). Senktide is not defined; TTX is.
    - **Minor.** Fix: "senktide (a neurokinin-3 receptor agonist)". Net about +0.1 line.
    - Verified: yes.

18. **Role 7/4 · `tests/test_methods_one_page_numbers.py`.** It pins what it claims, and all 7 tests pass with `PYTHONPATH=src`. Three gaps:
    - It checks values, not the rules stated around them, so finding 4's wrong 1.6× rule passes green.
    - Many page numbers are unpinned: 66 recordings, 2,109 ROIs, 36 mice, the per-group counts, 409.6 s (4,096 frames × 0.1 s), lr 0.01, 900 steps, five initializations, top four, four-layer, K = 4 and the 1 s bin, the 300 s stretch, the 2 s Chorus merge, and the +2–3 over-count.
    - Run from this worktree without `PYTHONPATH=src`, `test_the_simulation_parameters` fails with an AttributeError. The installed `bugarach` resolves to `<primary-checkout>/src`, which has no `realistic_counts`. That is an environment trap, not a page defect.
    - **Minor.** Fix: pin the cohort counts from `docs/learned/runs/2026-09-23-chance-floor-66/summary.json`, pin the training constants from `tools/train_learned_on_bench.py`, and drop or pin the rule text. Page length unchanged.
    - Verified: yes.

19. **Role 5 · Whole page.** `tools/murderboard_prose.sh` is not in the tree, so I ran the scan by hand.
    - I checked the house banned list, plus "fire", data-singular and "modality": zero hits.
    - Block sizes in words: Input 136, Event floor 119, Parameters 183, Simulated 110, Scoring 121, CoactDetect 206, Chorus 187, Benchmark 35, Output 129.
    - Passage test: CoactDetect is the longest. Its payload is the first three sentences. The CFAR resemblance and the "floor only at w = 2 s" caveat earn their place; the "(fast ships fixed 2 s bins)" aside could go. Chorus's payload is also up front.
    - Three sentences are awkward:
      - Input: "each event's onset, its half-rise time (t50)" reads as two fields. The spec's `time_sec` is the t50rise, so write "each event's onset, taken as its half-rise time (t50)".
      - CoactDetect: "a cutoff α stated as a normal tail, a z threshold".
      - Scoring: "leave the score".
    - **Minor.** Net 0.
    - Verified: yes.

Page-1 total if findings 1–4, 7, 8, 11 and 15–17 are all applied: about +1.2 lines, inside the 1.8-line headroom.

## Verified with no finding
- **Cohort:** 66 recordings, 2,109 ROIs, 36 mice; DI 17 / OVX 17 / MALE 13 / ORX 19; group nested in 34 imaging dates (chance-floor-66 README and ADR-0008).
- **Frame grid:** 0.1 s.
- **Floor constants:** 2 s, ±20 s drawn from [−20, 20), 1,000 draws, 1 per hour, minimum 3. Onsets are dropped, not wrapped.
- **Floor scope:** a floor per window and per simulated recording; treatment windows are also scored under the baseline floor.
- **Real gaps:** 41.3 s, 25.1 s and 24.8 s; 9.7, 22.0 and 25.3 events per hour.
- **Planted participation and spread:** middle levels 0.20, 0.38 and 0.25; SD 0.105 s, 0.131 s and 0.150 s from the correlogram half-width, calibrated.
- **Background model:** Gamma rate and burst factors.
- **Bench recordings:** 32 ROIs, 45 min, six decoys; 7, 17 and 19 planted events.
- **Placement:** gaps resampled end to end, starting at a random time.
- **Test recordings:** the no-coordination recording at the quiet background; the elevated-rate recording at 300 s and the 99th percentile; the ORX-spaced variant.
- **Seeds:** selection, held-out and final sets, doubled on fast.
- **Scoring rules:** 2.5 s tolerance, one-to-one matching, don't-care events under the floor, merge count.
- **CoactDetect search:** exact sliding null; α cap 6e-16 is the normal tail at z ≈ 8 (6.2e-16); contexts 20–120 s; guard at most a quarter of the context; the adoptability rule.
- **Chorus model:** architecture; 409.6 s; Adam at lr 0.01, 900 steps, class-weighted BCE; boundary planting; best of five initializations within budget.
- **Benchmark:** 2,000 resamples, per-seed pairing.
- **Call measure:** lengths and amplitude definition.
- **Reference metadata:** Efron, Perkel (Part II), Qi (IEEE pages 77–85), Pipa 2007, Amarasingham, Yu & Koltun, Zaheer and Kingma all check. Crossref confirmed Pipa, Perkel, Qi, Efron and Amarasingham. Finn & Johnson (RCA Review 29(3):414–464) matches the record of its reading in `docs/detector_history.md`.

## Verdict per role
- **1 Prove It:** fails on four claims (findings 1, 2, 4, 9); every other number recomputes.
- **2 DOI or Die:** all references exist and their metadata are correct. The shift surrogate is credited to the wrong Pipa paper (major), and Amarasingham is cited loosely (minor). Not searched: dilated-convolution priors earlier than Yu & Koltun.
- **3 Cross-Examiner:** group order is right. Minor findings on units, the decoy contradiction, the timing windows and the glossary.
- **4 Reviewer 2:** four major caveats are missing: the event floor, the event time, the decoys and the unscored lowest level.
- **5 Kill Your Darlings:** no banned constructions; three awkward sentences; the passage test passes.
- **6 RTFM:** the methods match the code. α and z, the exact null, the floor at w = 2 s, and the train-versus-inference standardization are all stated correctly.
- **7 Reinventing the Wheel:** nothing is re-implemented. The numbers test is sound but covers too little (finding 18).
- **8 You Lost Me:** readable. The forward reference and "shipped" are the main snags (major); fast/slow and senktide are undefined (minor).
- **9 Show, Don't Tell:** prose is right for a one-page methods section with a strict budget. A flow schematic (streams, floor, detectors, call measure) would help but cannot fit. No flag.
- **10 Ship It (non-rendering checks):** the build is current, there are 2 pages, Title and Author are stamped, and the builder refuses a spill and defaults to the darkroom. The rendering table was left to the other reviewer.
- **11 Start With the Problem:** the arc (input → definition → simulation → scoring → detectors → benchmark → output) follows Tony's list, apart from the Scoring-before-CoactDetect forward reference (major).
