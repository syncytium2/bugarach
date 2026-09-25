GRANT 4 ok — Read, Grep, Glob, Bash

Role 4 (Reviewer 2): findings on <repo>/docs/methods/one_page/methods_one_page.pdf. I read the text from methods_one_page.html and checked it against sources at 2fa3127e. The artifact has no figures (0 img/svg/figure elements), so the "read the picture" check does not apply. I did not edit any file. Scratch work was one inline python simulation; no file was written.

Findings are ordered by priority. Each row gives location · issue · severity · suggested fix · verified against source.

**Blocking**

1. **Output ("its amplitude is core ROIs divided by width… how tightly the event is packed")** · The amplitude measure is presented as settled and as a pure packing measure. It is neither.
   - (a) The name is still an open ruling (docs/decisions_pending.md item 6). That item's evidence says review round 3 found amplitude "mostly tracks 1 ÷ width", and it recommends that the methods "say in one sentence that the measure is dominated by width". The draft does not say this.
   - (b) At a fixed timing spread, amplitude rises with participant count, so "not folded in" is false. I simulated planted onsets with SD 0.105 s on the 0.1 s grid. Median amplitude was 20 cells/s for 6 cells and 33 cells/s for 10 cells, at identical packing.
   - (c) On fast, width takes only 3–4 values (0.2–0.4 s in 87% of draws), so amplitude is quantised in steps of up to 3×.
   - (d) The zero-width rule is unstated. `max(span, frame)` is floored at one frame and a single cell gives NaN (call_measure.py:179). decisions_pending item 4 lists 443 calls with `core_span_sec == 0` where amplitude divides by 0.1 s.
   - Fix: add one sentence: "amplitude = core ROIs ÷ max(width, one frame interval); undefined for one ROI; it is dominated by width and quantised by the 0.1 s frame." Mark the name as provisional pending the ruling, or rename it "packing density" now.
   - Verified: yes.

2. **Output (the whole call-measure paragraph)** · This paragraph describes outputs that have not passed validation, and it does not say so.
   - The realistic-bench check (docs/learned/runs/2026-09-25-realistic-bench/README.md) compared `core_n_roi` with the planted participant count. On combined it over-counts in 75–84% of events, by a median of +2 to +3 cells. On slow it is within 1 cell for only 78–82% of events.
   - Width and amplitude were never compared with planted truth at all, even though the planted timing spread is known.
   - ADR-0010 part 6 makes adopting the measure a per-stream decision, still pending.
   - Fix: add one clause: "validated against planted participants on simulated data (fast within 1 cell for 91% of events; combined over-counts by a median of 2–3 cells); width and amplitude not yet validated against planted spread." Alternatively, restrict the output claims to the streams where the measure is adopted.
   - Verified: yes.

3. **CoactDetect ("a window is called only if S also reaches the floor") versus Participation floor ("co-active within a 2 s window")** · The floor is calibrated for a different window than the one it gates.
   - The floor is the 1-per-hour chance count for a 2 s co-activity window (event_floor.WINDOW_SEC = 2.0).
   - CoactDetect's own window w is searched over 0.5–5 s on fast (bench.py:396) and up to 8–10 s on slow (bench_slow.py:306). Combined moved from 2 s to 3 s (final-parameters README, line 518).
   - With w > 2 s, reaching the floor no longer means "beyond chance once per hour". Chance counts in a wider window are higher.
   - Fix: state that the floor is computed at 2 s regardless of w, and give its consequence (the floor is not conservative when w > 2 s). Better, recompute the floor at the detector's w. At minimum, flag it as a caveat.
   - Verified: yes.

**Major**

4. **Simulated recordings ("plants the stream's measured number of events… with gaps resampled from the measured gaps") versus Scoring ("a planted event under its recording's floor counts neither as hit nor miss")** · The rate and spacing measurement and the simulator define "event" differently.
   - The real rate and gaps count only peaks at or above the floor (real-intervals README, step 2).
   - The simulator spends that same count and gap sequence on all three participation levels. The lowest level falls under the floor 100% of the time on fast and combined and 88–100% on slow. On busy fast, 18 of 24 middle-level events are also under the floor.
   - So the scored events on the bench are fewer and further apart than the real above-floor events they are said to reproduce. This undercuts the purpose of ADR-0010 (testing close neighbours), and it means "three participation levels" is in practice one or two scored levels.
   - Fix: state the scored-event share per stream, or plant the measured count at or above the floor and add sub-floor events beyond it.
   - Verified: yes (realistic-bench README floors table).

5. **Parameters for simulation (Participation, "the measured fraction… fast 0.20")** · This quantity is undefined, it is estimated with a different event definition from everything else, and only fast's value is given.
   - It is the median participants in clusters of at least K = 4 ROIs (`assess_coactivity`, tools/remeasure_bench.py:27, 184) divided by the median ROI count: a ratio of medians, truncated at a fixed K = 4. The floor (3–13 ROIs on real windows) is not used.
   - Slow (0.375) and combined (0.25) are omitted.
   - The outer levels are chosen, not measured (bench.py:983). The draft's word "bracket" hides that.
   - The moment-based estimate in coordination_rates.json depends strongly on window and model (fast 0.21 → 0.30 binomial across 1–4 s windows; 0.30 → 0.41 fixed).
   - Fix, one clause: "median participants per ≥4-ROI cluster ÷ median ROI count (fast 0.20, slow 0.38, combined 0.25); outer levels chosen at about ×1.5 and ×0.5."
   - Verified: yes.

6. **Scoring (budgets: "fast 7, slow 1, combined 10", "1 call per minute", "precision drop of at most 0.10")** · The constants are unjustified, one is undefined, and they conflict with the floor.
   - (a) The budgets are headroom over the incumbent CoactDetect setting's own measured rate: `ceil(1.6 × measured)`. For example, fast measured 4.4/h gives a budget of 7 (bench.py MAX_FALSE_POSITIVES_PER_HOUR). The bar is therefore defined by the method being compared against.
   - (b) "Precision drop" never says between what. It is quiet versus busy background (bench.py:2210).
   - (c) The floor targets 1 chance event per hour, while the detector may make 7–10 calls per hour on an empty recording. Two false-alarm standards sit side by side without comment.
   - (d) The empty recording is at the quiet background only, and the code itself warns that the false-positive ranking reorders at busier backgrounds (bench.py:931–934).
   - Fix: one clause: "budgets are 1.6× the shipped CoactDetect setting's measured rates; precision drop is quiet versus busy; empty recording at quiet background only."
   - Verified: yes.

7. **Chorus ("the fit with the best F1 on test recordings within CoactDetect's empty-recording budget was kept")** · The claim is stronger than the code.
   - `ok = [r for r in rows if r["null_per_hour"] <= budget] or rows` (tools/train_learned_on_bench.py:177). If no seed meets the budget, the best out-of-budget fit is kept silently, with only a `best_within_budget` flag.
   - The selection seeds (4000–4023) are called "test". The tool's own docstring says the resulting F1 is "a selection score, not an unbiased estimate".
   - Also undefined: how per-frame logits become calls (the threshold and where it is fitted), and that standardisation runs over a 409.6 s crop in training but over the whole recording at inference (chorus.py:72–74).
   - Fix: say "validation seeds"; state the fallback, or report `best_within_budget` per stream; add the threshold rule in one clause.
   - Verified: yes.

8. **Output ("±1 s fast; ±5 s slow and combined… 0.5 s (fast) or 2.5 s")** · These are unjustified constants, and the one rationale that exists is contradicted by the project's own measurement.
   - call_measure.py:50 calls them "judgements, not measurements", scaled ×5 because slow events are "about five times slower".
   - The measured timing spread is only 1.25× (slow 0.131 s against fast 0.105 s), and combined simply inherits slow's values. That fits the combined over-count in finding 2.
   - The aperture is also not fixed: it widens to cover the detector's reported span (call_measure.py:164–165), and the centre is onset + width/2 taken from the detector.
   - Fix: say "chosen, not measured" and "widened to the call's span". Separately, flag the ×5 scaling for RTFM.
   - Verified: yes.

9. **Output ("The call's onset is the event time") versus "measured the same way whichever detector made it"** · The event time is detector-specific.
   - CoactDetect's onset is its window start. Chorus places its onset mid-stripe (ADR-0010, context section).
   - Event times therefore shift systematically between detectors while being described as detector-independent.
   - Fix: use the core's first onset (`core_first_sec`) as the event time, or state the dependence.
   - Verified: yes.

10. **Input and Simulated recordings (pooled across groups; group nested in imaging day)** · The draft leaves out caveats that its sources say the write-up must carry.
    - Gaps are pooled over groups, but 444 of 507 combined gaps come from DI and MALE (real-intervals README).
    - The event rate differs about 12× between groups (DI 56.5 against ORX 4.5 per hour).
    - The quiet and busy backgrounds turned out to be the spread between groups (bench.py:1970).
    - ADR-0008 says group is nested in imaging day (34 dates, one group each) and "a write-up says so". The draft never mentions it.
    - Fix, one sentence: "All simulation parameters are pooled over groups (pooled gaps are 88% DI+MALE); group is nested in imaging day."
    - Verified: yes.

11. **Simulated recordings ("A variant with gaps from ORX recordings alone tests whether rankings hold where spacing differs")** · The check has little power and its scope is overstated.
    - It changes spacing only; count, background and participation stay pooled.
    - It resamples from 7 ORX gaps on fast, 17 on slow and 17 on combined.
    - Only slow ORX differs in spacing (Mann–Whitney p = 0.009, on dependent gaps).
    - ORX gaps are longer, so the variant cannot test harder, closer-spaced conditions.
    - Fix: "a slow-stream check with ORX's 17 gaps; spacing only."
    - Verified: yes.

12. **Participation floor paragraph** · Required caveats and definitions are missing.
    - (a) ADR-0008 (Consequences) says the methods must state that the null keeps coordinated onsets, so a coordination-rich window gets a higher, conservative floor. The draft omits this. On the bench it means planted events raise their own recording's floor.
    - (b) "At least as many co-active ROIs as chance could produce" reads backwards: chance can produce any count. The rule is exceeding the count chance reaches more than once per hour.
    - (c) "Crossing" is undefined. In the code it is an unbroken run of window positions at or above K.
    - (d) J = 20 s, the 2 s window and 1 per hour are not justified. ADR-0008 records them as stated choices.
    - Fix: reword the first sentence as in (b), and add "(conservative: the null retains coordinated onsets)".
    - Verified: yes.

13. **Input ("detected by the same method and differing only in the width attached to each event")** · The input quantity is undefined, and the sentence contradicts the draft's own numbers.
    - If the streams differed only in width, fast and slow would hold the same onsets. The draft gives different rates, event counts and timing spreads per stream, and "combined" would then duplicate every event.
    - The source (export_folder_spec.md, around line 383) says detection is methodically identical and that the exported *duration* definition differs. It does not say the onsets are the same.
    - Fix: say what assigns an event to fast or slow (the producer's classification), and that the width definition differs by stream.
    - Verified: partly. I confirmed the contradiction; what distinguishes the streams upstream is not in this repo.

14. **Spacing ("coordinated events were located without any detector")** · Overclaim. A count ≥ floor peak-picker, merging within 2 s, is a threshold detector, and it is the same count-and-floor rule that gates CoactDetect. The measured gaps are therefore what that rule sees, and gaps under 2 s are censored.
    - Fix: "without any of the compared detectors, by thresholding the co-active count at the floor (peaks < 2 s apart merged)."
    - Verified: yes.

15. **Simulated recordings ("lasts 45 min")** · The length is unjustified and longer than the data it mimics. Real baseline windows are 17–20 min (median 20 min; windows.csv). The gaps were measured inside at most 20 min windows, so long gaps are right-censored, yet they are planted into a 45 min recording.
    - Fix: justify the 45 min (ADR-0010 ruling 2 keeps the length for continuity of floors and seeds) and note the censoring.
    - Verified: yes.

**Minor**

16. **Scoring ("matched… within 2.5 s")** · The rule is incomplete. Tolerance is measured to the call's span, and a span containing the event matches at any distance (score.py:252). That lets wide calls match.
    - The 2.5 s is where detectors' F1 plateaus (score.py:67–71), which is self-referential. It is also about 24× the timing spread and comparable to the shortest real gaps (5th percentile 3.8 s on fast).
    - Fix: "within 2.5 s of the call's span".
    - Verified: yes.

17. **Scoring ("pooled over recordings")** · The design factors (quiet/busy background, participation level) are pooled into one F1, so an operating point is optimised for an arbitrary 1:1 background mix. The bench already keeps per-level counts (`by_frac`).
    - Fix: state that scores are also reported per background and per level.
    - Verified: yes.

18. **CoactDetect ("compared with a significance level α… allowed down to 6×10⁻¹⁶")** · At about 8 SD a normal tail on a small integer count is not a significance level. ADR-0010 ruling 6 notes that α acts as a second, rate-dependent participation floor.
    - Fix: call α a "z cutoff expressed as a normal tail".
    - Verified: yes.

19. **CoactDetect ("The method is a cell-averaging CFAR test")** · Overclaims equivalence. The null is a circular-shift surrogate within a context window, not an average over reference cells.
    - Fix: "analogous to".
    - Verified: yes, against coact.py. I did not open the 1968 paper.

20. **Parameters for simulation (Timing spread)** · The measured SD (0.105 s) sits at the 0.1 s frame resolution and depends entirely on the simulator calibration. That calibration assumes the bench's own generative model: Gaussian jitter and fixed-size events.
    - Fix: add "at the frame resolution; calibration assumes the simulator's jitter model."
    - Verified: yes.

21. **Unjustified constants listed without rationale:** 32 ROIs (at least a source is given: the median), six decoys (and their fraction), guard ≤ ¼ of context, 20–120 s contexts (ADR-0010 ruling 7 gives a one-line reason), learning rate 0.01, 900 steps, 409.6 s crops, five seeds, top-4 pooling.
    - Fix: given the one-page limit, add one sentence: "Constants not stated as measured were chosen; their rationale is recorded in ADR-0008–0010."
    - Verified: yes.

**Priority under the one-page limit:** 1, 2 and 3 must be fixed. Of the rest, 4, 5, 6 and 10 carry the most weight.

To pay for the space, cut:
- the CFAR sentence (shrink it to "analogous to CFAR")
- the α range and context range numbers
- the per-stream background rates

Those numbers read as Results-adjacent detail, and FOUNDATIONS §9 already carries them.
