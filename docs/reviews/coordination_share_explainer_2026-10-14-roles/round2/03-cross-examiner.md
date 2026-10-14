GRANT 3 ok — Read, Grep, Glob

Role 3, Cross-Examiner (consistency auditor). Artifact: c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\README.md and its six PNGs. I edited nothing.

**What I checked.** I compared every number in the README against numbers.json, recomputing the rounding myself. I checked each figure caption against the rendered PNG and against the generator (explain_coordination_share.py). Tool constants checked against tools/measure_coordination_rates.py: N_SURR 20, CAL_TOL 0.25, CAL_JITTER 0.106, the half-window second count, offsets 2 windows apart giving ±32 s, shape_usable 300 s / 20 onsets / 5 cells, ADOPTED_MODEL fixed, 48 calibration recordings. Bench constants checked against bench.py and simulate.py: quiet 0.0049, busy 0.0169, hot 0.1334 (additive), sizes 10/6/3 by rounding, realistic spacing since 2026-10-07 with 7 events, median gap 41 s. I also checked terms against GLOSSARY.md (the new section, regime, elevated-rate test, distractor, rigid shift), and read the INDEX row, the explainer todo, the pinning-stop todo, and the correlogram explainer's terminology.

**Clean.** Figure 2 (0.44, 0.03, 0.20, 1.21, about 8.1), all Figure 3 medians and the 0.67 to 1.12 range, all Figure 4 share figures (14 to 19%, 21 vs 14%, 22 to 23%, binomial 3 to 17%), the k figures (56 vs 33%, 50 to 69%), the λ figures (49 vs 35%, 48 to 55%), "about 5 points" for medium pairs, Figure 5A/B medians, −0.4% to +0.6%, all Figure 6 ranges, no_answer = 0, Figure 1's 30m to 35m seed 13, the Figure 4 legend order and markers matching the caption, and "48 per panel / 24 per point".

## Findings (location · issue · severity · suggested fix · verified)

1. **README line 148, against lines 226–229 and the generator's SCHEDULES.** Line 148 says "each recording in a set carries 2 pairs of moments closer together". But the mixed set carries 4 pairs (2 close and 2 medium) and "120 s only" carries none; line 229 itself says "replace the four pairs with 2 pairs of one kind, or with none". "On top of the bench's older layout" is also wrong: the pairs replace single moments, and every set keeps 15 moments (`schedule`: n_total − 2·pairs singles). · **Medium** · Say: "each set keeps 15 moments and turns some of them into pairs: the mixed set 2 close and 2 medium pairs, three sets 2 pairs of one kind, and 120 s only none." · Yes.

2. **Figure 3A vs Figure 4: one set under two names.** Figure 3A "three moment sizes (10, 6, 3 cells)" is the same 48 recordings as Figure 4's "mixed". The fixed median −0.17663 and binomial −0.07510 are identical in numbers.json. Figure 3B (one size) uses the same mixed schedule (`run_set(pool, dict(size=SIZES[1]))`, where mixed defaults to True). Neither the text nor the captions say so. A reader cannot line up Figure 3A's 18% with Figure 4A's black 1 s point, and may think 3A has no close pairs. · **Medium** · In the Figure 3 caption or line 118, say that 3A is Figure 4's mixed set and 3B is the same schedule with every moment 6 cells. Or use one name for the set in both figures. · Yes.

3. **Figure 3C's right answer is counted on a different basis from 3A and 3B.**
   - In 3A and 3B, "planted share" is planted onset frames ÷ all onset frames (generator `recording()` → `truth.share`).
   - In 3C it is the tool's `truth()`: Σk ÷ (N·T) ÷ mean rate, and that sum includes `gt.distractors`. So the bench's decoys count as coordinated in 3C's right answer.
   - The README introduces decoys only as things turned off in its own recordings (line 222) and says 3C has "the decoys on" (line 231). It never says they count toward 3C's planted share. The glossary's distractor entry calls them "real cross-ROI coincidence", which fits counting them.
   - One x-axis label, "planted share of events", therefore means two counting bases across the three panels.

   · **Medium** · Add to the Figure 3 caption or line 122: "in C the planted share counts the bench's decoys as shared moments, as the tool's check does, and is worked out from planted cells rather than onsets." · Yes (measure_coordination_rates.py `truth`, lines 393–398; generator lines 165 and 395).

4. **Line 190 vs numbers.json 5C, "steady, quiet".** The text says "Each cell's own clumping is removed in the same way (Figure 5C, the steady rows)". At the quiet background the subtraction removes only 52% of the median f₂ (0.0030 → 0.0014); only the 13× quiet steady row is removed at 99%. In the figure, the quiet rows' before and after points sit on top of each other at zero, so the figure cannot show removal there either. · **Medium** · Say: "removed at 13 times quiet (99%); at the quiet background there is almost nothing to remove." · Yes.

5. **Lines 179–182 vs Figure 5A.** "So it is counted most when it is short" contradicts the figure's 10 s point: a median of 3.7% (numbers.json "10 s"), below 30 s (7.9%) and 1 m (8.2%). The curve rises and then falls. The closing "not how long the change lasts" also sits against a panel whose x-axis is length and whose values move from 8% to 1.2% with it. · **Medium** · Say: "it peaks for stretches of 30 s to 1 minute (8%) and falls for shorter and longer ones (3.7% at 10 s, 1.2% at 15 minutes)." Reword the last sentence so it does not deny the length dependence the panel shows. · Yes.

6. **Shared moment vs planted event: README contradicts the glossary.** README Terms (line 51) says of shared moments: "The simulations plant these". The README also calls the bench's planted events "moments" (lines 144–148, 230). GLOSSARY.md line 503–506 defines shared moment as "inferred and never located … Not a coordinated event, which is a detector's call or a planted event". The same thing is also called "events" in lines 145 and 230 ("merging any two events", "about 7 events per 45 minutes"), so one population carries two names in one paragraph. · **Medium** · Pick one reading. Either the glossary entry admits planted moments in simulations, or the README calls what the simulation plants "planted events" and keeps "shared moment" for what the measure infers. Make whichever changes in the same change. · Yes.

7. **Line 166 vs numbers.json 4.lam.** "33% to 55% low": the smallest λ error is −0.3354 ("120 s only", 2 s), which rounds to 34%. Every other quoted bound rounds correctly. · **Low** · Change to "34% to 55% low". · Yes.

8. **Line 185 vs numbers.json 5B "28x".** The text says "three quarters of all the recording's onsets fall inside the stretch". But `share_of_onsets_in_stretch` (0.7515) is computed as onsets added by the stretch ÷ (added + background over 45 min): generator line 601. That ignores the background onsets inside the stretch and the ramp's thinning. Onsets inside the stretch, on that formula's own basis, would be about 0.78. · **Low** · Say "three quarters of all the recording's onsets are added by the stretch", or rename the json key to what it measures. · Yes.

9. **Line 183 and the Figure 5B axis label: "the bench's 30 s ramps".** The plural implies a ramp on and a ramp off. simulate.py lines 911–913 ramp in only (`rf = min(1, (ct − h0)/ramp_sec)`) and switch off sharply; the glossary also says "easing in over 30 s". · **Low** · Say "the bench's 30 s ramp in (sharp end)". · Yes.

10. **Line 86 vs Figure 1D.** "Every cell has the same number of ticks" holds over the whole 45-minute recording. Within the 5-minute panel the trains are slid by up to about ±32 s, so per-cell tick counts in 1D need not match 1B, and as written the sentence points the reader at the panel. · **Low** · Say "every cell keeps the same number of onsets over the whole recording". · Partly: I could not count ticks row by row reliably from the PNG.

11. **Line 19, Figure 5 caption.** "A and B: … dotted, no stretch at all": the dotted line is drawn only in A (generator lines 482–483; the PNG agrees). · **Low** · Say "dotted (A only)". · Yes.

12. **λ unit: Terms vs Figure 4C.** Terms (lines 55–56) define λ as moments "per second"; Figure 4C's axis reads "moments per minute (λ)", and the text says "moments per minute". The value plotted is a relative error, so nothing is numerically wrong, but the symbol has two units. · **Low** · Label 4C "moments per minute (60·λ)", or define λ per minute in Terms. · Yes.

13. **Line 260 vs the pinning-stop todo.** "four recordings from the diestrus (DI) group await review cell by cell". The todo says all four affected recordings are DI, but `_312` has already been reviewed; three (`_309`, `_316`, `_235`) await review. As written, the sentence can also be read as 2 + 4 recordings. "Removes cells pinned" is also inaccurate: the folder removes events inside pinned windows. · **Low** · Say: "four recordings, all from the diestrus (DI) group, are affected: on one the check missed cells, on another it removed too much, and three still await review cell by cell. The check removes events inside pinned windows." · Yes.

14. **Companion doc, bench.py `REGIMES` docstring (lines 929–931).** It says the estimator's error on the share "runs +0.06 at 1 s, +0.46 at 2 s and +1.00 at 4 s". That contradicts this page's Figure 4A ("The share hardly moves", −14% to −19% at every window). CAL_NO_PROBE shows the bench docstring predates removing the probe stretch, under which the share reads −16% at 1 s. A reader moving between the two gets opposite answers. · **Medium** (companion) · Not this page's edit: file a note beside the todo's existing three notes to the tool's next editor (the bench is out of scope). · Yes.

15. **Companion doc, GLOSSARY.md `regime` and `elevated-rate test`.**
    - The `regime` entry still gives 0.0052 / 0.0190 Hz; the page and bench.py use 0.0049 / 0.0169.
    - The `elevated-rate test` entry says the rate is "elevated **to** the background's 99th percentile". The page (line 176) and simulate.py add 0.1334 **on top of** the background.

    · **Low** (companion) · Update both glossary entries in the same change that adds the new glossary section. · Yes.

16. **Companion doc, tools/measure_coordination_rates.py docstring (line 42).** It still says "a 120 s spacing floor". The page (line 144) correctly says the bench has drawn intervals from real recordings since 2026-10-07. The todo already records this as a note for the tool's next editor. · **Low** · No page change: confirm the note survives into the review record. · Yes.

Nothing in this run's grant or path needs recording as a mismatch.
