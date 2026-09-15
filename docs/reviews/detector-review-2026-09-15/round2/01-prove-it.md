> **Public copy.** Lines that concern real treatment recordings are removed (21 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 1 ok — Read, Grep, Glob, Bash

# Claim and data check (role 1, blind pass): the detector review page

## What I checked
- **The page text:** every claim in `detector_review_plain.txt`, covering prose, captions, Tables 1–3 and the word list.
- **Numbers:** each number was checked against `_work/numbers.json`, `shipped.json`, the three bake-off runs per background level in `scratchpad/run/`, and the Section 2 bar data.
- **How detectors work:** each description was checked against the code in `src/bugarach/detectors/` (all six), `learn/nets/` (tube and its variants, trace, tiny), `simulate.py`, `bench.py` (the shipped settings, busy-block limits and background levels), `score.py`, `io.py`/`store.py`, `detect_folder.py` and the builder.
- **Recomputed myself:**
  - the test recording's bin counts;
  - the Figure 2C bars, rerun with the builder's own random seed;
  - the event rates the simulator actually produces on the 24 bench recordings;
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - which training recordings each training run uses.
- **Figures opened as images:** 1, 2, 9, 13 and 15.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

---

## BLOCKING

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Where:**
  - Section 3.5: "In the lab's real files, locust places each event at the time it was brightest, while the other five use the time its brightening began."
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Evidence:**
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - On folder input, `io._as_stream` sets `locs` to the event time column and `t50rise` to a copy of it.
  - `store.py` says so directly: "on **folder** input ``locs`` holds the ``t50rise``".
  - `docs/export_folder_spec.md` revision 8 says the same: "The Python locust anchors on the **half-rise** — `time_sec` — and never consumes a peak."
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - The `ONSET_FIELD` comment in `detect_folder.py` ("CICADA anchors on the peak (`locs`)") is out of date and is probably where the claim came from.
  - Separately, "began" is loose wording: `t50rise` is the moment the event reached half its rise.
- **Fix:**
  - Say that on these runs all six detectors place an event at its half-rise time.
  - Delete the Table 3 weakness.
  - If the peak difference matters, say it applies only to the browser viewer.
  - File the stale `ONSET_FIELD` comment separately.
- **Checkable against a source:** yes.

---

## MAJOR

**M1. A "Read this first" claim is contradicted by the page's own Table 2.**
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Evidence:**
  - rate+context judges chance from the nearby 60 seconds. Tuned, it averages 5.32 calls per minute in the busy block (`perf_baseline_quiet_rate.probe_per_min`). That is almost the same as binned SCE's 5.91, which judges chance from the whole stretch.
  - tube and tube-guard also use a nearby surround and make 1.40 and 1.01 calls per minute.
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - Figure 2C is an illustration built for the page, not a detector.
- **Fix:** Soften the claim. Say that a bar that does not follow the nearby background (locust) calls again and again in busy stretches. Say that following the background helps, but some such detectors still call often (tuned rate+context).
- **Checkable:** yes.

**M2. "Every useful detector" is contradicted by the page's own results.**
- **Where:** In short, paragraph 2: "Busier cells make every useful detector less sensitive, most of all to small events."
- **Evidence:**
  - Tuned binned SCE finds more events on the busy background: recall 0.48 quiet against 0.60 busy. For events joined by 30% of ROIs it rises from 0.62 to 0.93. Its recall for events joined by 10% barely moves (0.18 to 0.175).
  - At its shipped setting, binned SCE's recall also rises (0.27 to 0.31).
  - Section 7 itself says "almost every detector" and names the exception.
- **Fix:** Use "almost every" and name the binned SCE exception, or limit the sentence to the named detectors.
- **Checkable:** yes.

**M3. The conclusion about SPIKE-synch rests on one recording and conflicts with Table 2.**
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Evidence:**
  - The zero is from one test recording (`sync_winB.calls` = 0; `sync_bench_seed_score.probe_calls` = 0).
  - Across the 24 recordings, SPIKE-synch at its shipped setting makes 0.29 calls per minute in the busy block (`shipped_baseline_quiet_sync.probe_per_min`).
  - Tuned, it makes 1.05 per minute and breaks its limit in 3 of 4 rounds (`perf_baseline_quiet_sync.rounds_over_limit`).
  - So it does call in simulated busy stretches, and the "different cause" reasoning has nothing to stand on.
- **Fix:** Say "made no calls in the busy block of the one test recording". Cite Table 2's busy-block rate. Drop or soften "a different cause".
- **Checkable:** yes.

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Evidence (inside-window counts in `numbers.json`):**
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - Both learned detectors are drawn in these lanes.
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Checkable:** yes.

**M5. The page's bunching result contradicts the project's own record, and the page does not say so.**
- **Where:** Figure 10D and "What the simulator gets wrong": "it bunches events almost twice as much as these recordings do".
- **Evidence:**
  - The page's numbers match its tokens: real 1.77 and 5.28; simulated 2.99 and 9.18 (`gen_real_fano`, `gen_fitted_fano`).
  - But `bench.py` `MEASURED_BURST_SHAPE` documents a different result for the same simulator settings. At 30 s: real 1.82, simulated 1.87. At 300 s: real 5.69, simulated 4.44. That record says the simulator *matches* at fine timescales and falls *short* at coarse ones.
  - The page instead finds the simulator 1.55 to 1.97 times higher at every window.
  - A likely cause is that the page's version adds uneven rates across ROIs and keeps only ROIs with at least 10 events. That would push busy ROIs' bunching up. The page never mentions the conflict.
  - "Almost twice" overstates it: the ratios are 1.69, 1.97, 1.55 and 1.74.
- **Fix:**
  - Reconcile the page with the `bench.py` table: say why they differ, and correct whichever is stale.
  - Say "about 1.5 to 2 times".
- **Checkable:** yes (both sources are in the tree).

---

## MINOR

**m1. SPIKE-synch's bin value is not an average of the scores in the bin.**
- **Where:** Table 1 ("the average score in each 0.1-second bin"); Section 3.6 ("averages the scores in 0.1-second bins"; "must include at least 3 events"); Figure 8.
- **Evidence:**
  - In `sync.binned_synchrony`, events at exactly the same time are averaged. Each such group then writes to the first bin center within 0.1 s of it and *overwrites* anything written there earlier.
  - The "at least 3 events" floor adds up `Cn`, which is the size of the last group written to each bin, not the number of events in the bin.
- **Fix:** Describe it as "the score at that moment (events at the same instant averaged)", and word the floor loosely.

**m2. Figure 2's per-group check covers less than the prose says.**
- **Where:** Section 2: "The shuffle sits below the shift in each of the four groups ... in both streams", and "That holds in each of the four groups".
- **Evidence:**
  - The builder tests both statements at n = 6 only (`i6`).
  - The "about ten times at 8 or more ROIs" part was never tested per group.
  - In Figure 2B's pooled slow-stream panel, the shuffle line rises above the shift line from about n = 11 upward.
- **Fix:** Say "at 6 or more ROIs".

**m3. Figure 2C's "outside the block" counts cover only the 15 minutes shown.**
- **Where:** Section 2: "Outside the block, each bar makes 3 calls: 1 on a planted event and 2 on decoys."
- **Evidence:**
  - I reran the builder's code with the same seed. The split holds for each bar: one call at the planted event near 27 min 45 s, and one at each of the two decoys.
  - But the count is limited to minutes 15–30, which hold 3 planted events, so each bar misses 2 of them.
  - Over the whole recording, the whole-recording bar is passed in 12 bins outside the block.
  - "Passed 46 times" counts 2-second bins; they form 30 separate runs.
- **Fix:** Say "in the 15 minutes shown", and mention the two missed planted events.

**m4. The limits are not "a little above" earlier rates.**
- **Where:** Section 6.2: "Each limit was set a little above that detector's own earlier measured rate."
- **Evidence:** `MAX_PROBE_PER_MIN` comments give the earlier measured rates:
  - CoactDetect: 1 against 0.0
  - LoCo: 1 against 0.1
  - SPIKE-synch: 1 against 0.2
  - rate+context: 2 against 0.6
  - binned SCE: 9 against 5.6
  - locust: 25 against 17.3
- **Fix:** Say "set above that detector's own earlier measured rate".

**m5. The learned detectors do not use all 18 recordings.**
- **Where:** Section 6.3: "trained, and choose their call level, on the same 18 recordings."
- **Evidence:**
  - `fair_bakeoff.py` calls `fold_maker(rec, 18 seeds)`, which keeps 16 recordings for fitting and 2 for picking the call level, then trains with `n_train=min(10, 16)`.
  - So 12 of the 18 are used and 6 are not.
  - Section 4's "10 … 2" is correct.
- **Fix:** Say "on 12 of those 18 (10 to train, 2 to choose the call level)".
- **Also verified:** the claim that one of the three runs picked a different set of training recordings is correct. With training seed 1, recording indices start at 1000 mod 16 = 8. Seeds 0 and 2 both start at 0.

**m6. The busy/quiet comparison mixes two kinds of rate.**
- **Where:** Section 5: quiet 5.2 and busy 19 mHz compared against real 3.6 and 18.6 mHz, "so the quiet level is busier than intended".
- **Evidence:**
  - 5.2 and 19 are the background settings only. Across the 24 bench recordings, the rate the simulator actually produces outside the busy block (planted events and decoys included) averages 6.1 mHz per ROI at quiet (range 3.4–9.5) and 17.2 at busy (range 9.7–25.8).
  - The real 3.6 and 18.6 are total rates. So the busy level is actually slightly *below* the real 75th percentile.
  - `bench.REGIMES` says the 5.2 and 19 settings *were* the 25th and 75th percentiles when set from the export folder (2026-08-20). The page does not say why its recomputation differs (different window, or a different set of recordings).
- **Fix:** Compare produced rates, or say the settings exclude planted events. Note the recomputation difference.

**m7. The 0.36 s timing spread is not described accurately.**
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Evidence:**
  - `docs/generator.md` shows the lineups came from a measurement script (`measure_coordination_timescale.m`), not the detectors.
  - It measured 0.36 s against 0.42 s under circular shift, which is slightly *tighter* than chance, not "no tighter".
  - The measurement does not survive a round trip: planting 0.36 s measures back as about 0.64 s.
- **Fix:** Say "barely tighter than chance lineups (0.36 against 0.42 s), from a measurement that does not reproduce its own input".

**m8. The test recording does have lineups within a minute of planted events.**
- **Where:** Section 3.3: "the test recording spaces events 2 minutes apart, so this is not measured here". Also Section 5: the nearby window "never holds two of them".
- **Evidence:**
  - Planted events are at least 120 s apart, but decoys are placed with no spacing rule.
  - In the test recording, 5 of the 6 decoys fall within 60 s of a planted event, and one is 1.9 s away (`bench_seed_decoys_on_planted` = 1).
  - Decoys are exactly the kind of nearby lineup that could raise LoCo's or CoactDetect's bar.
- **Fix:** Add that decoys can sit within a minute of planted events.

**m9. Table 3's rate+context limit claim holds only at the quiet level.**
- **Where:** Table 3, rate+context: "Tuned, it breaks its busy-block limit in every round."
- **Evidence:** Quiet: 4 of 4 rounds. Busy: 0 of 4 (`perf_baseline_busy_rate.rounds_over_limit`).
- **Fix:** Add "at the quiet level".

**m10. "The learned detectors' scores spread more widely" holds only at the quiet level, and the ranges are not like for like.**
- **Where:** Section 7.
- **Evidence:**
  - Busy-level ranges: tube 0.62–0.67 (width 0.05), binned SCE 0.59–0.65 (0.05), SPIKE-synch 0.47–0.55 (0.08).
  - A learned range covers 12 scores; a hand-written range covers 4.
- **Fix:** Say "at the quiet level", and note the 12-against-4 difference.

**m11. The CoactDetect chance-rate claim is not measured.**
- **Where:** Section 3.2: "Real surrogate counts are lumpy and rarely bell-shaped, so the true chance rate is higher than that."
- **Evidence:** Nothing in the tree measures what happens when the p-value from the bell-curve assumption is applied to 100 surrogate counts.
- **Fix:** Say "may differ from that; not measured".

**m12. Two small precision issues.**
- **Decoy window:** it is minutes 2 to 18.3, not 2 to 18 (`distractor_window` 120–1100 s).
- **trace:** its input also carries a ROI-count channel (log n / 5), so it does not look "only at the brightness line".

---

## Claims I checked that match (condensed)

**Rounding convention:** a match means the page's value equals the source value rounded to the digits shown.

**In short and Section 1**
- F1 0.71–0.74 for the five named detectors — matches.
- CoactDetect finds 57% and 19% of the smallest events — matches.
- About one false call per two correct at precision 0.65 — matches.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

**Section 2**
- Fast-stream double events per 1,000: 24.5 real, 25.6 shift, 107.9 shuffle; slow stream 33.0 for shuffle. Match.
- Share of bins with 6 or more ROIs: 0.35% against 0.58% (fast), 0.35% against 0.40% (slow). Match.
- 8 or more ROIs: 16 to 19 times above the shift. Matches "about ten times or more".
- Figure 2C: whole-recording bar 4 ROIs, 46 in-block passes, nearby bar 10 ROIs with 0 passes. Recomputed with the same seed; exact match.
- Figure 2A: the busiest of 84 baselines, 15 ROIs. Matches the builder's selection.

**Table 1 and Sections 3.1–3.6, checked against the code**
- **rate+context:** 1 s rate, 60 s context, additive 5 per second, joins calls up to 3 s apart, drops single-step crossings. Matches.
- **CoactDetect:** distinct ROIs per 2 s bin, at least 3 ROIs, 100 circular shifts inside a 60 s centered window, one-sided cutoff at α = 10⁻⁴ (3.72 spreads). Matches.
- **LoCo:** 1 s bins, bar reset every 15 s, 60 s halves, higher of the two 99.9th percentiles, count must exceed the bar with at least 3 ROIs, 2 s merge. Matches.
- **binned SCE:** 10 s bins, 200 shifts, one pooled 99th percentile per window, count must exceed the bar. Matches.
- **locust:** 1 s on-period, 100 circular rolls, one 99.999th-percentile bar for the whole recording, peaks at or above the bar at least 4 frames apart. Matches.
- **SPIKE-synch:** window is half the shortest of the four gaps, capped at 0.25 s; hysteresis 0.1/0.1 with 0.5 s gaps. Matches, apart from m1.
- **Settings:** match `bench.OPERATING_POINTS`.
- **Test-window counts** for Figures 3–9: 2, 0, 0, 18, 15, 0 calls; 3 and 7 calls; 0 and 0 calls. All match.
- **Figure 4A:** count 7 = 6 planted ROIs + 1 background event. Recomputed; matches.
- **Figure 6A:** count 7 equals bar 7. Matches.
- **Figure 8:** 5/32 = 0.16. Matches.
- **Figure 11C:** SPIKE-synch's lowest three values give identical results because no score between 0 and 1/32 is possible. Verified in code: a shared-time group always scores at least 1/32.

**Section 4**
- 1,149 adjustable numbers; one frame of widening on each side (0.3 s); center filters 0.19–0.63 s; surround 2.6–16.3 s; 12.8 s cut-off; 0.8 s guard (8 frames); "ratio" is a log difference; brightness fed straight to the network. All match the code.
- trace and tiny at a tenth of the learning rate (1e-3 against 1e-2). Matches.
- tiny: 1 call covering 100%; trace: 3 calls covering 97%. Match.
- Call level 0.972. Matches.
- Figure 9C: 3 and 7 calls, visible in the image. Figure 9A: tube-ratio-guard's dips outside the blanked part, visible. Match.

**Section 5**
- Simulator recipe: 33 ROIs, 45 min, 15 planted (5 per level; 3, 6 and 10 ROIs), at least 120 s apart and kept 120 s clear of the busy block, 60 mHz extra ramping in over 30 s, 6 decoys of 6 ROIs with the same timing spread, 300 s and 60 s bunching timescales. All match.
- Precision ceiling 15/21 = 0.71. Matches.
- 38%, 37% and 4% silent ROIs; 2,630 ROIs; 84 recordings. Match their tokens.

**Sections 6 and 7**
- 2.5 s matching tolerance; rounds of 24 = 4 × 6, choosing on 18. Match.
- Every Table 2 cell was checked against its source value and rounds correctly. The one borderline case is locust's shipped busy-block rate: 8.075 is shown as 8.07.
- Busy-block limits; rounds over the limit (4, 2, 3); values chosen at the loosest end in 3 of 4 rounds; SPIKE-synch F1 0.48–0.53 across its list; slowest and fastest speeds. All match.
- Table 3 F1 pairs, 83%, 2% (twice), 64%, and "highest precision of the hand-written six". Match.

**Section 8**
- Fast-stream settings used on the slow stream. Verified in `detector_params`, which applies the same scalar values to both streams.
- Which detectors run inside each window versus on the whole recording. Matches `detect_folder` and `_run_learned`.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

**Colophon**
- The page is built from commit f240215 with uncommitted changes in `tools/`, which matches the worktree state.

**Could not check:** reference details in Section 11 (no network); the claim that "each Python version matched its MATLAB predecessor to within 10⁻⁹" (asserted in module docstrings; test fixtures not rerun); "precise timing" for locust (no timing measurement exists).
