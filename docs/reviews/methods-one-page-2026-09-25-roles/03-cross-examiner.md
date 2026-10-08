GRANT 3 ok — Read, Grep, Glob

# Role 3 (Cross-Examiner): findings on methods_one_page

**Scope.** I read the text of `<repo>/docs/methods/one_page/methods_one_page.html` (the source of the PDF). I checked it against:
- the companion docs: GLOSSARY.md, ADR-0008, ADR-0009, ADR-0010, the realistic-bench README, the real-intervals README, the superseded coordination_pipeline_methods.md and CLAUDE.md;
- the code the numbers come from: bench.py, bench_slow.py, bench_combined.py, call_measure.py, score.py, train_learned_on_bench.py, score_bench_candidates.py and search_all_settings.py.

I did not open the PDF: no figures, so I made no figure-to-text check.

## Numbers I checked that agree with the sources

- **Recordings and groups:** 66 recordings; DI 17, OVX 17, MALE 13, ORX 19 (sums to 66, in the canonical order); 36 mice; 2,109 ROIs; median 32 ROIs.
- **Floor:** *J* = 20 s, 1,000 draws, 2 s window, 1 per hour, minimum 3 ROIs.
- **Timing spread (jitter):** 0.105, 0.131 and 0.150 s.
- **Background rates:** 0.0049/0.0169, 0.0024/0.0093 and 0.0071/0.0292 Hz.
- **Gaps and events per hour:** median gaps 41.3, 25.1 and 24.8 s; 9.7, 22.0 and 25.3 events per hour, giving 7, 17 and 19 events per 45 min.
- **Seeds:** fast's seeds doubled.
- **No-coordination budgets** (CoactDetect's): 7, 1 and 10 calls per hour.
- **Other budgets:** elevated-rate 1 call per minute; precision 0.10.
- **Search limits:** α about 6×10⁻¹⁶; contexts 20–120 s; guard at most a quarter of the context.
- **Output measure:** apertures ±1 s and ±5 s; split gaps 0.5 s and 2.5 s.
- **Chorus training:** learning rate 0.01; 900 steps; crop 4,096 frames (409.6 s); five training seeds; mean of the top 4; receptive field about ±27 s (541 frames).
- **Bootstrap:** 2,000 resamples over seeds.

## Findings

Format: location · issue · severity · suggested fix · verified against a source?

1. **Participation floor, "the smallest count K"**
   - Issue: K is a reserved word. GLOSSARY defines K as the MAHICE coactivity floor, set by a person as a *percentage* of the ROI count. Here K means the chance floor from ADR-0008, a different concept.
   - Severity: **major**.
   - Fix: drop "K" ("the smallest number of co-active ROIs…"). It is never used again on the page, so this also saves length.
   - Verified: yes (GLOSSARY, "K" entries in the Parameter vocabulary and MAHICE sections).

2. **Heading "Participation floor", and bare "floor" throughout**
   - Issue: GLOSSARY reserves **participant floor** for a different concept (the recruitment level below which a detector stops finding events, reported as recall by level). It also says pages meaning the ADR-0008 floor call it "event floor" or "the floor (ADR-0008)". "Participation floor" is one letter-group away from the reserved term. The page also has a separate "Participation" parameter under "Parameters for simulation", which invites confusing the two.
   - Severity: **major**.
   - Fix: rename the heading to "Event floor." and say "event floor" at first use. Bare "floor" is fine after that.
   - Verified: yes (GLOSSARY: "participant floor" and "event floor" entries).

3. **Scoring ("calls per hour on the empty recording") and Chorus ("CoactDetect's empty-recording budget")**
   - Issue: "empty recording" is a RETIRED term. GLOSSARY renamed it the **no-coordination test** on 2026-09-21 (Tony) because the cells are active throughout. The page also never names which recording is "the empty recording": "Simulated recordings" introduces two recordings with nothing planted, so the reference is ambiguous.
   - Severity: **major**.
   - Fix: in "Simulated recordings", name the two recordings "a no-coordination recording (quiet background)" and "an elevated-rate recording (a 300 s stretch at…)". Then use those names in Scoring and Chorus ("calls per hour on the no-coordination recording", "CoactDetect's no-coordination budget"). The net length change is about zero.
   - Verified: yes (GLOSSARY "no-coordination test" entry; bench.py `MAX_FALSE_POSITIVES_PER_HOUR` docstring).

4. **"Window" means at least four things on one page**
   - The senses: (a) a recording's baseline or treatment window ("baseline windows only", "each window's floor", "For each stream and window"); (b) the 2 s co-activity count window; (c) CoactDetect's "surrounding context window"; (d) the position under test ("a window is called only if…", "Called windows closer than a merge gap are joined").
   - "For each window and stream" in the floor paragraph cannot be resolved without prior knowledge.
   - Severity: **major**.
   - Fix: keep "window" for (a) only. Use "2 s bin" or "2 s interval" for (b), "context" for (c) (the page already says "contexts ranged 20–120 s"), and "position" or "time t" for (d): "t is called only if S also reaches the floor. Calls closer than a merge gap are joined."
   - Verified: yes (text; GLOSSARY names CoactDetect's cell under test its *bin*).

5. **Bare "event" switches between a calcium event and a coordinated event**
   - Input defines "event" as a per-ROI calcium event (onset, width, two streams). Later the same bare word means a coordinated event:
     - "fraction of ROIs taking part in an event";
     - "9.7, 22.0 and 25.3 events per hour";
     - "number of events per 45 min";
     - in Output, "the event's core", "event time", "the event's width/amplitude".
   - "Coordinated event" itself appears only twice.
   - The three-way vocabulary (event, call, coordinated event) is never fixed. Output also slides from "call" to "event" mid-paragraph ("each call is then measured… the event's core… The call's onset is the event time").
   - Severity: **major**.
   - Fix: state once, in Input or the floor paragraph, "a *coordinated event* is…; a detector reports one as a *call*". Then write "coordinated event" (or "planted event" on the bench) wherever the unit is not a single ROI's event. In Output, write "the coordinated event's core / width / amplitude". Two or three words net.
   - Verified: yes (text; GLOSSARY "call" entry, "width/amplitude of a coordinated event" entries).

6. **Participation parameter gives fast only ("fast 0.20")**
   - Issue: every other simulation parameter is given for all three streams, so the reader cannot line participation up with them. The measured middle levels are slow 0.375 and combined 0.25.
   - Severity: minor.
   - Fix: "(fast 0.20, slow 0.38, combined 0.25)". Adds about 4 words; the "(SD)" gloss could be cut to compensate.
   - Verified: yes (bench_slow.py:185, 207; bench_combined.py:158, 173; bench.py:941, 978).

7. **Background rate: counting basis changes silently**
   - Issue: Input says the dataset is 66 recordings and every data-derived parameter came from their baseline windows. The quiet and busy rates were in fact taken over "the 63 recordings that clear the shape floors". The page implies all 66.
   - Severity: minor.
   - Fix: "…percentiles, over 63 recordings, of…". Alternatively, accept this as a documented basis in the ledger.
   - Verified: yes (bench.py:811–813). I did not check this for slow and combined.

8. **Scoring: "calls spanning two or more planted events are counted as merges"**
   - Issue: the code and ADR-0010 part 3 count **scored** planted events. Under-floor events are "don't care" and are excluded, which the same paragraph has just said.
   - Severity: minor.
   - Fix: "…two or more scored planted events…" (+1 word).
   - Verified: yes (score.py:122–124; bench.py:1630–1632; ADR-0010 part 3).

9. **Scoring: under-floor events described as leaving recall only**
   - Issue: the page says an under-floor planted event "counts neither as hit nor miss". ADR-0009 decision 2 and GLOSSARY "don't care" also remove a call matched to such an event from precision. As written, a reader would count those calls as false positives.
   - Severity: minor.
   - Fix: "…counts neither as hit nor miss, and a call on it neither as true nor false positive".
   - Verified: yes (ADR-0009 decision 2; score.py:119–121).

10. **Scoring: "a precision drop of at most 0.10"**
    - Issue: "drop" relative to what is not said. The budget is the **precision swing**: the absolute difference in precision between the quiet and busy backgrounds.
    - Severity: minor.
    - Fix: "a quiet-to-busy precision difference of at most 0.10".
    - Verified: yes (GLOSSARY "precision swing"; bench.py:2208).

11. **Scoring: budgets presented as universal**
    - Issue: "Every operating point must stay within fixed budgets: … (fast 7, slow 1, combined 10), 1 call per minute …, … 0.10". These are CoactDetect's values; other detectors' budgets differ (for example rate+context 4.5 calls per minute on fast). Chorus is held to CoactDetect's no-coordination budget, which the page does say later.
    - Severity: minor.
    - Fix: "CoactDetect's budgets, which the learned models share: …".
    - Verified: yes (bench.py `MAX_PROBE_PER_MIN`, `MAX_FALSE_POSITIVES_PER_HOUR`, `MAX_PRECISION_DROP`; bench_slow.py:356–372; bench_combined.py:317–323).

12. **Simulated recordings: "Two further recordings carry nothing planted"**
    - Issue: there is one such recording per seed, not two in total (no-coordination seeds 56000–56011 and elevated-rate seeds 66000–66011). The elevated-rate stretch is also first named "elevated-rate stretch" only in Scoring; Simulated recordings calls it "a 300 s stretch".
    - Severity: minor.
    - Fix: "Each seed also yields two recordings with nothing planted: …, and an elevated-rate recording containing a 300 s stretch…".
    - Verified: yes (GLOSSARY "fresh seeds"; bench.py:1470–1483).

13. **Two bootstraps on different bases**
    - Issue: CoactDetect's "95% bootstrap interval" on held-out gain uses 400 resamples **of recordings** (search_all_settings.py:125, 1122). The fresh-seed comparison uses 2,000 resamples **over seeds**. The page gives the resample count only once, at the end of the Chorus paragraph, so a reader will apply 2,000 to both.
    - Severity: minor.
    - Fix: "95% bootstrap interval (400 resamples of recordings)" in CoactDetect, or drop the count from both.
    - Verified: yes.

14. **Output: "within a fixed aperture around the call's centre"**
    - Issue 1: call_measure widens the aperture to cover the call's own reported span when that is longer (call_measure.py:153–165), so the aperture is not always "fixed". The superseded draft said so ("or the whole call if the call is longer than 2 s").
    - Issue 2: the page omits two rules. Amplitude divides by width floored at one frame (0.1 s). Amplitude is undefined for a core of one ROI. GLOSSARY's amplitude entry and the old draft both state these.
    - Severity: minor.
    - Fix: "…±1 s fast; ±5 s slow and combined, widened to the call's own span if longer…", and "…divided by width (floored at 0.1 s)…".
    - Verified: yes.

15. **Output omits ADR-0008's requirements for any write-up**
    - ADR-0008 decision 4 and its "Writing it up" consequence require three things:
      - treatment windows scored under two floors (their own, and the baseline floor carried over), both reported;
      - the methods state that the null keeps coordinated onsets, so rich recordings get a higher, conservative floor;
      - a note that group is nested in imaging day.
    - The page says "For each stream and window the flow returns a table of calls" but never mentions the two floors.
    - Severity: **major** (the companion fact still holds; the page does not state it).
    - Fix: one clause in the floor paragraph: "Treatment windows are scored under their own floor and under the baseline window's, and both are reported." Offset it by cutting "(a rigid shift)" or the CFAR citation sentence.
    - Verified: yes (ADR-0008 decision 4; Consequences).

16. **"combined" stream, "chorus_norm" and "chorus_norm_part" are not in GLOSSARY**
    - Issue: GLOSSARY's stream axis lists only fast and slow. A new term goes into the glossary in the same change.
    - Severity: minor.
    - Fix: add GLOSSARY entries for the combined stream and the chorus family in this PR. This is a glossary edit, not a page edit.
    - Verified: yes (GLOSSARY has no "combined" or "chorus" entry).

17. **GLOSSARY is stale against the page (the page is right)**
    - GLOSSARY "regime" and "background" still give quiet 0.0052 and busy 0.019 Hz. The code and the page say 0.0049 and 0.0169.
    - GLOSSARY "no-coordination test" still says 33 cells; it is now 32.
    - A reader cross-checking the page against the glossary will find a contradiction.
    - Severity: minor (companion-doc defect).
    - Fix: update those GLOSSARY entries in the same PR.
    - Verified: yes.

18. **Boundary planting: the page and ADR-0010 disagree on scope**
    - Page: "extra events planted at floor − 1, floor and floor + 1" appears under chorus *training* only.
    - ADR-0010 part 5: "Each recording plants events at its floor − 1, at its floor and at floor + 1".
    - realistic-bench README: "in training, boundary planting".
    - The page matches the README (the implementation), not the ADR text.
    - Severity: minor.
    - Fix: none needed on the page. Note in the ledger that ADR-0010 part 5 reads wider than what was built.
    - Verified: yes.

19. **Chorus: "the fit with the best F1 … within CoactDetect's … budget was kept"**
    - Issue: the tool falls back to the best fit overall if none is within budget (`ok = [...] or rows`, train_learned_on_bench.py:176). The page states the budget as a hard condition.
    - Severity: minor.
    - Fix: accept, or add "(or the best overall if none met it)". Better to report in Results whether the fallback fired.
    - Verified: yes.

20. **Spelling is mixed**
    - Issue: "standardised", "labelled" and "neighbours" (British) sit beside "optimized" (American). One document should use one spelling.
    - Severity: minor.
    - Fix: pick one. The ADRs use British ("optimise").
    - Verified: yes (text).

21. **"cell-averaging CFAR" beside "ROI, one imaged cell"**
    - Issue: in the radar term, "cell" means a range bin, not a biological cell. A reader just told that an ROI is a cell may misread it.
    - Severity: minor.
    - Fix: accept (it is the published name), or write "(radar 'cells' are time bins)" if space allows.
    - Verified: n/a (judgment).

22. **HTML `<title>` and h1 differ**
    - `<title>`: "Methods: coordinated calcium events". h1: "Methods: detection of coordinated calcium events" (which matches the superseded draft's title). This may show in PDF metadata.
    - Severity: minor.
    - Fix: make them identical.
    - Verified: yes.

**No contradictions found for:**
- group order (DI, OVX, MALE, ORX, as required);
- the 66-recording and 36-mouse counts against ADR-0008 and ADR-0010;
- the gap and events-per-hour figures against the real-intervals README;
- the ORX-spacing variant against ADR-0010 ruling 1;
- the guard cap and 20 s minimum context against rulings 7 and 8;
- the call_measure lengths against the ×5 rule in ADR-0010 part 6.

The page uses "ROI" consistently rather than "cell". "Modality" and "fire" do not appear, and "data" is not used with a verb.
