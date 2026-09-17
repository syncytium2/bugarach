> **Public copy.** Lines that concern real treatment recordings are removed (26 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 4 ok — Read, Grep, Glob, Bash

# Role 4 (Reviewer 2): findings on the coordinated-event detector review

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

Each finding gives: location · issue · severity · fix · verified against a source (yes/no).

## Blocking

**1. Figure 2C caption is false.** It says "The three calls outside the block that both bars make are planted events."
- Recomputed on bench seed 3: the calls sit at 926.5 s, 1084.5 s and 1664.5 s.
- Two of them are decoys (927 s, 1085 s). Only 1665 s is planted.
- Both 10%-of-ROIs planted events in view (984 s, 1792 s) are missed by both bars. So the picture also shows both bars calling the lineups the scorer counts as false alarms.
- Fix: correct the caption. Mark decoys (▽) in the lane.
- Verified: yes.

**2. "Controls show the tube's design does real work" is an uncontrolled comparison.**
- `fair_bakeoff.LR` trains trace and tiny at a learning rate of 1e-3 and all tube models at 1e-2. The comment in that same dict calls this exact setup "uncontrolled".
- tiny's threshold landed on the grid floor, 0.0001. `models.log` shows the warning "this is not an operating point. Widen it."
- In all 24 bakeoff runs tiny made exactly 6 calls for 6 hits, i.e. one call spanning each whole recording.
- Fix: say the controls failed to train at their settings and that nothing follows about the tube's design. Otherwise retrain them at the tube's learning rate with a threshold grid that brackets the optimum.
- Verified: yes.

**3. Precision and the busy-block rate cannot register a detector that calls everything (the alarm cannot ring).**
- A call spanning the whole recording matches one planted event, so it is not a false alarm.
- Table 1 therefore gives tiny a precision of 0.92 (1.0 in 10 of 12 runs), 0.0 busy-block calls per minute, and `distractor_hits` of 36 of 36.
- Figure 12B draws tiny and trace as "no calls".
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- Fix: draw calls that overlap the window. Report the fraction of time covered by calls. Flag the control rows in Table 1 as not meaningful.
- Verified: yes.

**4. Table 1 does not score the detectors the document shows.**
- Table 1 comes from tuned settings:

| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
|---|---|---|
| rate+context | 2 events/s | 5 |
| binned SCE | 75th / 85th percentile | 99 |
| LoCo | 99 / 99.5 | 99.9 |
| SPIKE-synch | 0.04 (quiet) / 0.005 (busy) | 0.1 |
| locust | 99.9 / 99.9999 | 99.999 |

- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- Section 10 puts Table 1 F1 beside behaviour seen at the shipped settings. The shipped points score lower in the in-sample sweep: rate+context about 0.63, binned SCE about 0.37.
- Fix: state this in Section 8 and Section 10, and add a shipped-setting column.
- Verified: yes.

**5. Decoys are identical to the 18% planted events, yet calls on them count as false alarms.**
- `simulate.py` lines 734–753 build decoys with the same fraction (0.18) and the same Gaussian 0.36 s onset spread. Nothing that sees only event times can tell them apart.
- So precision has an unstated ceiling: 15 of 21 lineups, about 0.71, even if every lineup is found. The document gives no reason for scoring decoys this way, and `score.py` itself calls "should a burst count?" a live question.
- Decoys are placed only in 120–1100 s, with no spacing rule. Across seeds 3 and 1000–1023, 119 of 150 decoys sit within 60 s of a planted event, 64 within 30 s, and 6 within 2.5 s. They therefore sit inside the context windows that the 120 s spacing exists to keep clean.
- The Section 6 sentence "so that no detector's chance estimate contains a second planted event" is literally true but misleading.
- Fix: state the ceiling, justify the rule, and disclose the contamination. Better, space decoys at least 120 s from planted events.
- Verified: yes.

**6. The learned-training description is wrong in three ways.**
- **Not 18 recordings.** The document says "trained each one on 18 simulated recordings". `fold_maker` holds out 2 of the 18 for the threshold, and `train(n_train=min(10, 16))` fits on 10. The threshold is picked on those 2 recordings, each read twice through the modulo, and 6 are never used.
- **Seed runs are confounded.** Section 7.2 says three runs from different random numbers show "how much training alone changes the result". But the seed also picks *which* 10 recordings are used: seed 1 takes indices 8–17 mod 16, while seeds 0 and 2 take the same subset. The spread mixes a data change with an optimiser change.
- **Self-contradiction.** Section 5 says "Each was trained once", which contradicts Section 7.2.
- Fix: correct all three statements.
- Verified: yes.

**7. SPIKE-synch's score is reported as an accuracy, which RESET §4 forbids.**
- RESET §4 says SPIKE-synch's score "is not its accuracy": the swept setting does not bind.
- The quiet sweep gives bit-identical F1 (0.5166) at 0.005, 0.01 and 0.02. "Every round chose 0.005" is an artifact of strict `>` tie-breaking picking the first grid value.
- Yet the document reports 0.53, lists "highest precision of the hand-written six" as a strength, and guesses "most likely the other two rules". RESET already names the cause: `C_min` pinned at 0.1.
- Fix: mark the SPIKE-synch row "sweep could not choose; not its accuracy" and remove the strength claims.
- Verified: yes.

## Major

**8. "The fastest detectors here once trained" (Section 5 strengths) is the reverse of Table 1.** The learned models are the slowest. tube_ratio at 9,786× is the slowest of all twelve, against rate+context at 536,163× and locust at 517,797×. Fix: delete or reverse. Verified: yes.

**9. SPIKE-synch "makes few false alarms in busy stretches" is contradicted.**
- Table 1: 1.1 calls per minute in the busy block, over its limit and 5× CoactDetect.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- Fix: restate both claims.
- Verified: yes.

**10. The call limits certify each detector's own past behaviour, and the tuning bypassed the repo's own guards.**
- `bench.MAX_PROBE_PER_MIN` records "measured: 17.3" for locust and sets its limit at 25. A limit derived that way cannot fail the shipped setting, and "stays under its limit" is not comparable across detectors.
- locust broke its limit in 2 of 4 quiet rounds: 1011 and 1041 busy-block calls per 30 min, about 34/min. The mean of 19.4 hides this.
- Figure 11C puts a red ✕ on locust's chosen 99.9 and on SPIKE-synch's chosen 0.04. The "three flaws" list names only rate+context.
- `fair_bakeoff` takes the raw best F1 and skips `pick_operating_point`'s refusals (`EdgeOfRange`, `TooPromiscuous`, `DegenerateSweep`). Table 1 therefore publishes settings the repo's own selector would refuse: binned SCE and LoCo at the grid edge, SPIKE-synch degenerate, rate+context and locust too promiscuous.
- Fix: compare absolute rates, report per-round limit breaks, and disclose the bypass.
- Verified: yes.

**11. "We do not rank because rounds vary more than detectors" uses the wrong variance.**
- Every detector is scored on the same six recordings per round, so the comparison is paired.
- The spread across rounds is not the error on a difference between detectors, and "lowest–highest" of 4 values is fragile.
- Fix: give paired per-round or per-recording differences with a CI, or say "not tested". The no-ranking rule in `performance_table.md` stands on its own.
- Verified: yes (fold data).

**12. "The best detectors find most planted events with few false alarms" (In short) overreaches.**
- Precision leaves out busy-block calls.
- Even so, CoactDetect's 0.65 means 35% of scored calls are false.
- With the block included, rate+context quiet fold 0 is 86 hits out of 322 calls, about 0.27 against the reported 0.57. locust fold 0 is 85 out of 1225, about 0.07 against 0.48.
- Fix: soften the summary, and say beside Table 1 that precision excludes the busy block.
- Verified: yes.

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- It is the median onset spread (SD) within candidate lineups that detectors proposed and nobody reviewed.
- `docs/learned/generator_spec.json` records the measured spread as 0.311 s against 0.335 s for the chance model (excess −0.076). That is chance-level.
- "About 0.36 s" is never defined; it is a Gaussian SD.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- Fix: define the quantity, state that it is chance-level, and caveat the bench's timing.
- Verified: yes.

**14. Figure 2B's "more cells line up than chance explains" is not established.**
- A shift of the whole baseline destroys slow rate drift shared across cells, which is the failure Figure 2C itself shows.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- The flat slow-stream tail (about 1% of bins up to K=16) suggests full-field events.
- Fix: say "not explained by a whole-window shift", show a local-shift curve, and break it down by group.
- Verified: yes (code).

**15. Figure 2A is the most extreme recording, and the bench cannot test the reason given for the shift.**
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- The simulator's background is Gamma-rate-modulated with bunching and no regularity at short intervals, which Figure 10D also reflects. So the bench cannot test whether shift beats shuffle.
- Figure 2 shows that the chance distributions differ, not that detections differ.
- Fix: disclose the selection. Test a shuffle null in CoactDetect on the bench, or say it is untested.
- Verified: yes.

**16. Figure 2C's "nearby bar" is a construction of the figure, and its cost is never shown.**
- It is a centred 60 s window, 100 shifts, the 99.9th percentile and at least 3 ROIs. None of these constants is in the caption, and it is no shipped detector's rule.
- The picture shows this bar at 10–12 of 33 ROIs through the block, rising about 30 s before it. Any event joined by fewer than about 30% of ROIs would be invisible inside a busy stretch.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- Fix: state the constants and the sensitivity cost, and add planted events inside a busy block.
- Verified: yes.

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- `detect_folder.ONSET_FIELD` gives cicada `"locs"`, the event *peak*. Its own note puts the peak–start gap at about 0.3 s fast and 2 s slow, which it calls wider than the scoring tolerance.
- `active_duration_mode` defaults to `"fixed"`, using per-stream constants.
- This contradicts Section 1 ("start from … start times"), Section 4.5 ("from the event's start") and "gets each event's length from the lab's data file".
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- Fix: correct the text, and say the bench and real inputs differ.
- Verified: yes (code). I did not check for an override inside `detect_slice`.

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- LoCo and locust scan the whole recording. CoactDetect, SPIKE-synch, rate+context and the learned models run only inside the lab's windows.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- Verified: yes.

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- Fix: remove the comparative wording, name the stream, and cite the source.
- Verified: yes.

**20. "Where the raster has an obvious stripe, most detectors call it" is weak evidence.**
- "Obvious stripe" is undefined and nothing is counted.
- All twelve detectors read the same event list, so their agreement is not independent.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- "The useful detectors" imports validity from simulation.
- Fix: define a stripe, count it per detector, and add the artifact caveat.
- Verified: yes (one stripe measured).

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

## Minor

**22. CoactDetect's "chance would reach it less than once in 10,000 bins" is a Gaussian approximation.** It is a normal-tail p-value from the mean and SD of 100 surrogate counts (`coact.py` docstring), not an observed frequency. Null counts near 0.3 (Figure 4A) are far from Gaussian, and in quiet stretches the working bar is the 3-ROI floor (about 2.3). Fix: say so. Verified: yes.

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

**24. Figure 9A's picture differs from the text.** tube_ratio_guard's surround is dominated by sharp −0.4 lobes at ±0.9 s, i.e. a flank filter about 1 s out, not the "surrounding seconds" the text describes. Fix: describe what was learned. Verified: yes (picture).

**25. Numbers without a matching figure or label.**
- Busy-background recall by event size (19%, 12%) is quoted but not shown; Figure 12C covers the quiet background only.
- Table 1's busy-block column does not say it is the quiet background.
- Fix: add the busy panel and the label.
- Verified: yes.

**26. Undefined constants.**
- 5.2 and 19 mHz are the 25th and 75th percentiles of slice-mean per-ROI rate (population event rate ÷ ROI count), pooled across groups from the export folder.
- Figure 2C's 99.9th percentile is not stated.
- Fix: define them in text.
- Verified: yes.

**27. binned SCE anomalies go unexplained.** Recall is only 0.62 for 30%-of-ROIs events at the quiet background, and F1 rises at the busy background ("not worked out why"). Either could be the scorer reacting to 10 s call widths. Fix: check per-event matching before publishing the row. Verified: no.

**28. Figures 3–9 rest on one hand-picked event.**
- One seed, one planted event, windows "settled on" for display.
- Figure 6A's miss is a tie: a count of 7 against a bar of 7.
- Fix: disclose the selection, and quote the whole-recording scores already in `numbers.json` (`*_bench_seed_score`).
- Verified: yes.

**29. The parity sentence ("matched … one part in a billion") is in the present tense.**
- FOUNDATIONS §2 was amended ("Parity was the inheritance"), and deliberate forks are allowed.
- locust's parity is against interface2, not CICADA.
- Fix: "matched at port time".
- Verified: partly.

## Files cited
- `<worktree>\tools\fair_bakeoff.py` (LR dict, raw best-F1 calibration)
- `<worktree>\src\bugarach\learn\train.py` (`fold_maker`, `train` seeds, `pick_threshold`)
- `<worktree>\src\bugarach\bench.py` (`BENCH_RECORDING`, `MAX_PROBE_PER_MIN`, `EdgeOfRange`/`TooPromiscuous`)
- `<worktree>\src\bugarach\simulate.py` (distractors, lines 734–753)
- `<worktree>\src\bugarach\detect_folder.py` (`ONSET_FIELD`)
- `<worktree>\tools\make_detector_review.py` (`_lane` onset filter, Figure 2A/2C construction)
- `<worktree>\docs\learned\generator_spec.json` (measured 0.311 s vs chance 0.335 s)
- `<scratchpad>\review\models.log` (tiny threshold warning)
- `<scratchpad>\run\baseline_{quiet,busy}\bakeoff*.json`
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
