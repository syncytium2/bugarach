> **Public copy.** Lines that concern real treatment recordings are removed (32 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 4 ok — Read, Grep, Glob, Bash

# Reviewer 2 (adversarial): blind pass, round 2, on the coordinated-event detector review

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

---

## BLOCKING

### B1. The document never tests whether the detectors whose bar follows the nearby background miss real events in busy stretches, yet its conclusions lean on those detectors
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **The problem.** Nothing is planted in the busy block, and calls there are left out of precision. So a detector that goes blind for the whole block loses no recall and no precision: its F1 cannot drop.
  - Figure 2C shows how big the blind spot is. Inside the block the nearby-60 s bar climbs to about 10 of 33 ROIs, about 30% of them. Every event joined by 10% or 18% of ROIs placed there would be missed, and the score would not change.
  - The document admits this ("this recording plants none there, so the cost is not measured"). That sentence confirms the test cannot detect the failure; it does not defend the conclusions.
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Fix.** Either plant events inside the busy block and report recall there, per detector and per event size, or cut the summary down to "judging chance locally suppresses calls in busy stretches; whether that suppresses real events there is untested." Add this to Section 10. In Section 8, remove the implied reading that the busy-stretch calls are false.
- **Verified against source?** Yes: `simulate.py` places no events in `hot_window`; `score.py`/`pool_scores` leave out `hot_fa`; Figure 2C.

### B2. The precision and F1 headline mostly measures the decoy design, and the document never says so
- **Where.** "In short", paragraph 1 ("Even the best made about one false call for every two correct ones"). Section 7 ("Precision of about 0.65 for the best…"). Table 3 (SPIKE-synch: "The highest precision of the hand-written six"). Section 5, "Decoys".
- **The problem.**
  - **What a perfect detector could score.** Section 5 says decoys cannot be told apart from 18% planted events, so a detector that finds all 15 events can reach precision 0.714 at most. Its F1 can reach 0.83 at most. That F1 ceiling is never stated, so 0.74 reads as mediocre rather than about 89% of what is achievable.
  - **Where the false alarms come from.** Pooled over the 24 simulated recordings at the quiet level, CoactDetect made 169 scored false alarms, and calls landed on 142 of the 144 decoys. LoCo made 156 false alarms and landed on 143 decoys. (A decoy counts as landed on if any call sits within 2.5 s, so this is approximate.) Setting decoys aside, CoactDetect's precision is about 308 / (477 − 142) ≈ 0.92.
  - **The false-call sentence.** "One false call for every two correct ones" is mostly the benchmark's built-in penalty, not a property of the detectors.
  - **SPIKE-synch.** Its "highest precision" follows from missing 18% events: it landed on only 45 decoys. That is the same blindness Table 3 lists as its weakness, listed a second time as a strength.
  - **No stated reason for decoys.** The document never says what real phenomenon a decoy stands for, or why a 6-ROI lineup with a planted event's exact timing spread is "not coordinated." The code calls decoys "genuine cross-ROI coincidence that is not a coordinated event." In practice that means a lineup is non-coordinated only because the answer key says so. An outside reviewer will ask what the ground truth is.
- **Fix.**
  - State the F1 ceiling (≈0.83) next to every F1.
  - Report precision two ways, with decoy calls counted and with them set aside.
  - Rewrite the summary sentence about false calls.
  - Remove "highest precision" as a SPIKE-synch strength, or explain where it comes from.
  - Say what decoys model, or drop them from precision and report decoy calls on their own line.
- **Verified?** Yes: `run/baseline_quiet/bakeoff.json` (`n_hit`, `n_scored`, `distractor_hits`), `simulate.py` GroundTruth docstring.

---

## MAJOR

### M1. The 2.5-second hit window is unexplained, and it was set where the two top-scoring detectors stop improving
- **Where.** Section 6.1 ("within 2.5 seconds").
- **The problem.**
  - **How it was set.** `score.py` records that the window was widened from 1.5 s to 2.5 s because "LoCo and CoactDetect plateau at 2.5 s and RateDetect at 2.0 s". The benchmark's scoring rule was therefore chosen from the F1 curves of the detectors that end up at the top of Table 2.
  - **Its own caveat.** The same source says the window is "generous" compared with a median event footprint of about 0.8 s, and that readers should trust only the order of the rows, not the decimals.
  - **Wide calls are rewarded.** A call that covers an event counts as a hit, so wide calls gain (10-second bins, merged calls; tiny's single call covering everything). The precise timing listed as locust's strength earns nothing.
  - **The text is silent on all of this.**
- **Fix.** Justify the 2.5 s in the text and say how it was chosen. Show F1 against window width for every detector (the project already has the test). Add the "order, not decimals" caveat to Section 7.
- **Verified?** Yes: `score.py` `TOL_SEC` docstring.

### M2. The recording recipe is built around the failure modes of the detectors that judge chance locally
- **Where.** Section 5 ("at least 120 seconds apart"). Section 3.3 ("not measured here").
- **The problem.**
  - **Event spacing.** `generator.md` calls the spacing floor "the most consequential knob here". Below it, the nearby surrogate window contains the signal and the bar inflates. The bench sets the floor at 120 s, at least as long as the 60 s and 120 s windows of CoactDetect and LoCo, so their main weakness cannot show up.
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - **Stated as neutral.** The document presents the spacing as a neutral design fact, and lists "a second event within a minute" as LoCo's unmeasured risk, without saying the bench was built so it cannot happen.
- **Fix.** Say plainly that the spacing was chosen to keep local nulls clean. Add a condition with realistic spacing (for example 15–30 s), or put the gap in Section 10.
- **Verified?** Yes: `generator.md` §min_sep_sec.

### M3. The simulator was never checked on the quantity every detector measures, and several of its settings come from the detectors themselves
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **The problem.**
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - **The timing spread is barely above chance and does not reproduce.** Its surrogate null is 0.42 s, larger than the 0.36 s measured. And "build a recording at 0.36 and the estimator that produced 0.36 measures ~0.64 back." Neither fact is disclosed.
  - **The quiet level is compared the wrong way.** 5.2 mHz is the nominal background, but the real percentiles are total rates. Averaged over the recording, the busy block alone adds about 6 mHz (60 mHz × roughly 4.75 of 45 minutes). Planted events and decoys add about 1.5 mHz more. The quiet recording's realized total is about 13 mHz, above the real median of 9.7; outside the block it is about 6.6 mHz. "Busier than intended" understates this.
- **Fix.**
  - Add simulated bench curves to Figure 2B.
  - Say that event sizes and timing spread come from detector-found clusters, give the 0.42 s null and the round-trip failure, and compare total rates with total rates.
  - Replace "about ten times" with the ratio read off the figure.
- **Verified?** Yes for the documented facts (`generator.md` lines 290–295, 415–425, 483–494). The realized total rate is my own arithmetic from `spec_baseline_quiet.json`, not a measurement.

### M4. No statistical test, even though every detector was scored on the same 24 recordings
- **Where.** "In short" ("No detector stands out"). Section 7 ("Five detectors score about the same… locust, SPIKE-synch and binned SCE score lower"; "The learned detectors' scores spread more widely").
- **The problem.**
  - **Both directions are claimed untested.** "About the same" is an untested equivalence, and "score lower" is an untested difference. The document declines to rank the top five, then ranks the bottom three.
  - **A test is cheap.** All detectors ran on identical recordings, so a paired test on per-recording differences or a paired bootstrap costs almost nothing.
  - **The ranges are not comparable.** A learned detector's range covers 12 scores (3 training runs × 4 rounds); a hand-written one covers 4. A range over 12 draws is expected to be wider than a range over 4 from the same distribution, so "spread more widely" is partly arithmetic.
  - **Surrogate randomness is left out.** The hand-written detectors that use surrogates were each run once, so their spread ignores their own random draws.
- **Fix.** Report paired bootstrap confidence intervals for F1 differences against a reference detector. Use standard deviations, or the mean over training runs per round, rather than lowest–highest. Or soften every comparison to "described, not tested."
- **Verified?** Yes: `bakeoff*.json` (`n_scores` 4 vs 12; seeds 1000–1023 shared by all detectors).

### M5. The learned detectors were trained against the same busy block and decoys they are scored on, so their busy-block result is a test on training-style data
- **Where.** Section 4 ("The ratio versions were built to resist busy stretches"). Section 7 ("The two ratio models almost never call there"). Section 6.3.
- **The problem.**
  - **Training labels.** `encode.frame_targets` marks the busy block and the decoys as 0 in training ("which is what they are for"). The block in every recording is the same shape: +60 mHz, minutes 20–25, a 30 s ramp.
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - **Impossible labels.** Decoys marked 0 next to identical 18% events marked 1 give contradictory targets.
  - **Design choices were made on the same simulator.** The guard width, the 12.8 s surround cutoff and the learning rates were all developed on it; "never saw" applies to recordings, not to the recipe.
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

### M6. SPIKE-synch's weaknesses come from settings this project fixed, but Table 3 lists them as properties of the measure
- **Where.** Sections 3.6 and 6.2, Table 3, Section 11 ("whose cap on the window we use").
- **The problem.**
  - **Who chose the values.** In `bench.py`, the 0.25 s window cap and the 0.1 level a call must stay above are "viewer FAST defaults" chosen in this project. They are not from the SPIKE-synchronization authors, and neither is on the setting list.
  - **Small events cannot be found.** A 10% event is 3 of 33 ROIs (matlab_round), so each of its events can score at most 2/32 ≈ 0.06. That never passes 0.1, so a small event can never produce a call.
  - **Medium events can barely be found.** An 18% event can score 5/32 ≈ 0.16 at most, and only if every partner falls inside a 0.25 s cap, while the planted spread is 0.36 s.
  - **How it reads.** "Misses events joined by few cells (2% at 10% of ROIs)" is a consequence of those fixed values, yet it reads as a flaw of a published measure. The document does say the list "does not control it", but Table 3 still delivers a verdict.
- **Fix.** Name the cap and the minimum level as this project's choices. Sweep them, or state that SPIKE-synch as parameterized here cannot detect events below about 10% of ROIs. Reword the Section 11 attribution so the 0.25 s value is not read as PySpike's.
- **Verified?** Partly. `bench.py` and `sync.py` yes. I did not check PySpike's own default for `max_tau` against its source.

### M7. binned SCE's low score has an anomaly the document does not explain, and the bench may penalize whole-recording bars in a way real use would not
- **Where.** Section 7 ("We have not worked out why binned SCE rises"). Table 3 ("Lowest score of the hand-written six"). Section 6.2 ("F1 cannot see them").
- **The problem.**
  - **Large events are missed.** At the quiet level (tuned), binned SCE finds 62% of events joined by 30% of ROIs, fewer than the 63% it finds at 18%. At the busy level it finds 93%. So the "long-established rule" misses a third of 10-ROI events, which "wide bins hide small events" does not explain.
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - **My check.** On simulated recordings 1–6, I turned the block's rate to zero. binned SCE at the 99th percentile went from F1 0.37 to 0.46, and its recall for 18% events from 0.17 to 0.60. locust's recall for 10% events went from 0.03 to 0.33.
  - **Caveat on that check.** It is unpaired: changing the block rate changes the random draws, so the recordings differ. CoactDetect also moved, from 0.71 to 0.78, so part of the change is noise.
  - **The same effect hits locust,** a third party's detector.
- **Fix.** Before judging binned SCE or locust, rerun with the busy block scored as a separate recording, or excluded from the surrogate pool. Explain why 30% events are missed. Change "F1 cannot see them" to say that the block does lower F1 for detectors with one bar per recording.
- **Verified?** Yes: `numbers.json` `perf_baseline_*_sce.recall_by_pct`, plus my run (unpaired, so indicative only).

### M8. "The setting it ships with" is presented as an untuned reference, but those settings are provisional and some were tuned on this same recipe
- **Where.** Section 6.3 ("Those settings were not chosen on these recordings"). Section 7 ("score about the same as when tuned"). Section 8 ("Fast-stream settings were also used on the slow stream").
- **The problem.**
  - **Where the shipped settings came from.** locust's shipped percentile was retuned from 99.99 to 99.999 on these background levels (`bench.py`). CoactDetect's comes from a "viewer FAST point" and SPIKE-synch's from "viewer FAST defaults".
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - **Slow stream.** Using fast-stream settings on the slow stream has never been checked. That is in Section 8 but not Section 10.
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Verified?** Yes: `bench.py` `OPERATING_POINTS.source`, `generator.md:479–482`, `numbers.json` `opt_*_coact.picks`.

[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **The problem.**
  - **Agreement is never measured.** No pairwise overlap within a time window is reported. And agreement among these detectors is not corroboration: they all read the same event list, and most count ROIs in 1–2 s bins against circular shifts, so they share inputs and much of their design.
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **The problem.**
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Fix.** Say the persistence finding comes from these detectors on paired windows, is reduced in the fast stream (median 0.46 of baseline) and varies by group. Frame it as "no validated negative control exists," not "coordination continues."
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

### M11. Two summary sentences go further than the document's own numbers
- **Where.** "In short", paragraphs 2 and 3.
- **The problem.**
  - **"Detectors that judge it from the nearby seconds do not [call over and over]."** Tuned rate+context judges chance from the nearby minute and averaged 5.3 calls per minute in the busy block, over its limit in 4 of 4 rounds. tube and tube-guard also look at the nearby seconds and call about once a minute there.
  - **"Busier cells make every useful detector less sensitive."** binned SCE's recall rose from 0.48 to 0.60, and "useful" excludes it by definition.
  - **"Five detectors… 0.71 to 0.74."** That is the quiet level only. At the busy level, rate+context (0.63) and binned SCE (0.63) are within 0.03 of the best.
- **Fix.** Qualify both sentences. For example: "at their shipped settings, CoactDetect and LoCo…", and "most detectors; binned SCE's score rose, for reasons not established." State that the five-way tie is at the quiet level.
- **Verified?** Yes: `numbers.json` `perf_baseline_quiet_rate.probe_per_min` = 5.32, `perf_baseline_busy_sce`.

### M12. Section 10 leaves out much of what an outside reviewer would raise
- **Where.** Section 10.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Fix.** Extend the list. Each item should be one line with a section pointer.
- **Verified?** Yes, by comparing against the findings above.

---

## MINOR

1. **Section 5 and Section 6.1: "10% of ROIs" is 3 ROIs** (matlab_round(3.3)), exactly the "at least 3 ROIs" floor of CoactDetect, LoCo and binned SCE. Say so; it explains the collapse in small-event recall. Verified: yes (`simulate.py:110`).
2. **"In short", paragraph 2: "found 57% in a quiet recording"** is pooled over 24 recordings at the quiet level. Change to "at the quiet level". Verified: yes.
3. **Section 3.2: "the true chance rate is higher than that"** is asserted, not measured. Measure the exceedance rate on surrogates or soften to "may be higher". Verified: no.
4. **Section 2: "at 8 or more ROIs about ten times above it or more"** understates Figure 2B (roughly 15× at 8 ROIs, more than 100× at 12 in the fast stream). Give the ratio read off the figure. Verified: yes (Figure 2B).
5. **Section 3.5 / Table 1: locust has no minimum-ROI floor,** unlike the three detectors that list one. State it. `generator.md` mentions a locust "minimum-cell-floor flaw" as still open; I did not check its current status. Verified: partly.
6. **Section 3.5, Section 11: "some of its settings differ"** from CICADA without saying which (percentile retuned here, 1 s on-period, whole-recording bar, peak times). List them. Nothing has been compared against CICADA's output, so "Close to openly released software" is unverified. Verified: yes (`bench.py`), and the document itself says no comparison exists.
7. **Title and Section 4: "Twelve computer programs" / "six learned detectors"** count two controls that failed to train. Say "ten detectors and two failed controls". Verified: yes.
8. **Section 7: "We have not worked out why binned SCE rises."** A candidate explanation exists (M7). Offer it as a hypothesis. Verified: indicative only.
9. **Section 5: decoys fall only between minutes 2 and 18.** A decoy within 2.5 s of a planted event can be scored as a hit. State how often decoys fall that close in the 24 recordings. Verified: partly (window from `spec_baseline_quiet.json`; frequency not counted).

---

**Files relevant to these findings:**
- `<worktree>\src\bugarach\score.py`
- `<worktree>\src\bugarach\simulate.py`
- `<worktree>\src\bugarach\bench.py`
- `<worktree>\src\bugarach\learn\encode.py`
- `<worktree>\src\bugarach\learn\train.py`
- `<worktree>\tools\fair_bakeoff.py`
- `<worktree>\tools\make_detector_review.py`
- `<worktree>\docs\generator.md`
- `<worktree>\docs\FOUNDATIONS.md`
- `<scratchpad>\run\baseline_quiet\bakeoff.json`
- `<scratchpad>\review\_work\numbers.json`
