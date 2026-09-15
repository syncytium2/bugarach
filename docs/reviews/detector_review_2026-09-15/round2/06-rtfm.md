> **Public copy.** Lines that concern real treatment recordings are removed (10 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

# Role 6 (RTFM, methods and domain) blind review of the detector review document

**What I checked.** I read the built plain-text copy of the artifact against the code in the `detector-review-doc` worktree at shipped settings:
- **Detectors:** `detectors/rate.py`, `coact.py`, `loco.py`, `sce.py`, `cicada.py`, `sync.py`.
- **Grading and settings:** `bench.py` (the settings each detector ships with, the busy-block limits, the fold split), `score.py`, `performance.py`.
- **Simulator, surrogates, dispersion:** `simulate.py`, `surrogates.py` (circular shift and the Elephant resample), `assess.circular_shift_trains`, `count_dispersion.py`.
- **Learned detectors:** `learn/train.py`, `learn/encode.py`, `learn/nets/tube*.py`, `trace.py`.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Tools:** `tools/fair_bakeoff.py`, `tools/make_detector_review.py`, `tools/make_mechanism_figure.py` (`coact_bar`).

For the sources, I compared the PySpike coincidence-window code at tag 0.6.0 and at master. I ran code where it was cheap:
- SPIKE-synch binning behaviour
- the rate window's width
- whether event times fall on the frame grid, on simulated and real folders
- the four learned checkpoints' kernels
- the Fano factor split by cell rate, from the cached generator statistics
- the rate percentiles under both percentile definitions

**What held up.** These match the code at shipped settings, and I did not list them as findings:
- **CoactDetect's bar:** z = 3.72 is the one-sided normal quantile for alpha = 1e-4. The code's p = 0.5·erfc(z/√2) is one-sided, the spread uses ddof = 1, and only bins with at least 3 ROIs are tested. `coact_bar` rebuilds the bar correctly.
- **LoCo:** a new bar at a checkpoint every 15 s, a separate shift in each 60 s half, the 99.9th percentile, the higher side wins, a strict ">" and at least 3 ROIs.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **locust:** each event switches its ROI on for 10 frames, CICADA-style `np.roll` shifts, a pooled 99.999th percentile, peaks ≥ the bar, at least 4 frames apart.
- **SPIKE-synch window:** half the smallest of the four gaps, capped at 0.25 s, with a strict "<".
- **Tube models:** 1,149 adjustable numbers; the guard blanks 8 frames (0.8 s); the ratio variants take a difference of logs; the score is a sigmoid; the call level uses ≥; the learning-rate ratio is right. All four review checkpoints widen by 1 frame.
- **Grading:** tolerance 2.5 s, busy-block calls left out of precision, 4 × 6 folds.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Shuffle vs. shift mechanism:** the doubled-events explanation is exact in expectation. Under independent uniform shifts, each ROI's occupancy of a fixed bin is Bernoulli(its share of distinct occupied bins); the shuffle has the same form. So the gap between the two tail curves comes only from that share, plus wrap and edge effects.

**Blocking findings:** none.

---

## Major

**M1. Real files: locust does *not* use a different event time from the other five.**
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Evidence:**
  - `cicada_detect` defaults to `onset_field="locs"`.
  - On export-folder input, `bugarach.io._as_stream` fills `locs` from `time_sec` and sets `t50rise = locs.copy()`. The `store.py` and `Stream` docstrings say the same: "on folder input `locs` holds the `t50rise`".
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Fix:** Delete the sentence and the Table 3 clause, or say that all six use the same per-event time on the lab's files. Also, `time_sec` is the half-rise time, not "the time its brightening began". Say "the time the event reached half its rise" (or similar).
- **Verified against source:** yes.

**M2. "Bunches events almost twice as much" comes from the busiest cells, not from the whole field.**
- **Where:** Section 5, "What the simulator gets wrong", and the Figure 10D caption.
- **Evidence:** I recomputed the same statistic (variance ÷ mean of per-ROI window counts, averaged over ROIs with ≥ 10 events) from `_work/generator_stats.json`, split by each ROI's own rate:

  | ROI rate | real, 30 s | fitted, 30 s | real, 300 s | fitted, 300 s |
  |---|---|---|---|---|
  | below 20 mHz | 1.55 | 1.42 | 2.75 | 2.70 |
  | 20–50 mHz | 2.19 | 2.21 | 7.27 | 5.66 |
  | 50–100 mHz | 2.27 | 3.54 | 10.1 | 11.1 |
  | above 100 mHz | 1.10 | 10.05 | 5.14 | 39.5 |

  - Below 50 mHz, which is most of the ROIs, the fitted simulator matches real bunching.
  - The pooled "twice" comes almost entirely from the busiest stratum, about a tenth of the ROIs in each set. There real cells are close to Poisson at 30 s, and the simulator is roughly 8–9 times burstier.
  - The cause is structural. `simulate.py` multiplies each ROI's rate by Gamma draws, so the ratio is about 1 + rate·window/shape and grows with rate. The bench's own `MEASURED_RATE_SHAPE` note already flags that the busy tail overshoots.
  - This matters for what the bench tests: busy cells produce chance lineups and drive rate+context, and those are exactly the cells the simulator gets most wrong.
- **Fix:** Replace "almost twice as much" with something like: "matches bunching for most cells, but makes its busiest cells far burstier than real busy cells, which are close to random". Add the split to Figure 10D, or state it in the caption.
- **Verified against source:** yes (recomputed).

---

## Minor

**m1. Fano factor uses ddof = 0 on about 4 windows at 300 s.**
- **Where:** Figure 10D caption ("About 1 means no bunching, as the flat simulation shows").
- **Evidence:** `count_dispersion.fano` uses `c.var()` (ddof = 0). Baselines last at most 1200 s, so the median ROI has 4 windows at 300 s. Expected Poisson reading is (n−1)/n = 0.75, and the flat simulation reads 0.76.
- **Fix:** Use ddof = 1, or say that 1 is the no-bunching value only at short windows.
- **Verified:** yes.

**m2. rate+context's "1 second" window counts 1.1 s, and the call rule is looser than described.**
- **Where:** Table 1 and Section 3.1.
- **Evidence:** `train_rate` uses `half_bins = round(1/(2·0.1)) = 5`, so it counts 11 grid bins but divides by 1.0 s. A synthetic 10 Hz train reads 11.0 Hz in the 1 s window and 10.02 Hz in the 60 s context. The bar is therefore crossed at about 1.1 × local rate ≥ context + 5 Hz. This is inherited from MATLAB parity.
- **Second point:** "for more than one time step" is not the rule. The code keeps a merged group whose span is > 0, so two separate one-step crossings up to 3 s apart make one call.
- **Fix:** Describe the rule as coded, and file the window quirk against the code.
- **Verified:** yes.

**m3. Merging is left out for CoactDetect and the learned detectors.**
- **Where:** Section 3.2 and Section 4.1.
- **Evidence:** CoactDetect joins significant bins up to 3 s apart (`merge_gap_sec = 3.0`, not overridden). The learned decoder joins runs up to 20 frames (2 s) apart. Both change call counts and matching.
- **Fix:** Add one clause to each section.
- **Verified:** yes.

**m4. The learned detectors use 12 of the 18 recordings, not "the same 18".**
- **Where:** Section 6.3.
- **Evidence:**
  - `fold_maker` fits on the first 16 recordings and keeps the last 2 for choosing the call level.
  - `train(n_train=min(10, 16))` uses 10 of the 16: indices 0–9 for training seeds 0 and 2, indices 8–15, 0 and 1 for seed 1.
  - `pick_threshold` asks for 4 validation seeds, but they map onto the same 2 recordings twice.
  - So the call level is chosen on 2 recordings (30 planted events). The hand-written setting is chosen on 18 (270 events). That asymmetry is a likely cause of "tube's call level also changed from run to run".
  - This also contradicts Section 4 ("saw 10 … chose … on 2 other").
- **Fix:** State the 10 + 2 split in Section 6.3.
- **Verified:** yes.

**m5. Ties go to the loosest value, and the text doesn't say so.**
- **Where:** Section 7, "What Figure 11C shows".
- **Evidence:** `fair_bakeoff.py` keeps a value only if `p.f1 > best_f1` (strictly greater), and every grid is ordered loosest first. Exact ties therefore resolve to the loosest value. At the busy level, SPIKE-synch picks 0.005 in all four rounds, while its three loosest values tie — so that pick is the tie-break, not a preference.
- **Fix:** State the tie-break next to the "loosest value" sentences.
- **Verified:** yes.

**m6. SPIKE-synch's bin value is not a plain bin average; it only acts like one because event times sit on the 0.1 s grid.**
- **Where:** Table 1 and Section 3.6 ("averages the scores in 0.1-second bins").
- **Evidence:**
  - `binned_synchrony` averages only events that share the exact same time. Each distinct time writes to the first grid point within dt and overwrites what an earlier time wrote there. Events at 1.02 s (score 0.5) and 1.07 s (score 0) both land in the 1.0 s bin, which reads 0.
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - Section 7's claim that "no score between 0 and about 0.03 is possible" is true only because of this rule. Events sharing a frame coincide with each other through the exact-tie rule, so any nonzero bin is ≥ 1/32. Under a true bin average, 1/64 would be possible.
  - "At least 3 events" is counted with `Cn`, the size of the last group written to the bin.
- **Fix:** Write "the average score of the events in that frame". Note that this depends on event times being quantized to 0.1 s.
- **Verified:** yes.

**m7. SPIKE-synch cannot call a 10% event at all; this isn't just "scores low".**
- **Where:** Sections 3.6 and 9.
- **Evidence:**
  - A 10% event has 3 participants of 33 ROIs, so its best possible score is 2/32 = 0.0625. That is below the shipped 0.1 needed to open a call.
  - The tuned 0.04 can open a call, but later bins must exceed `C_min = 0.1` and the call must reach `min_n = 3` events. That in practice requires all 3 participants in one frame.
  - The 2% recall is therefore built into the settings and cannot be tuned away.
- **Fix:** Say so in Section 3.6.
- **Verified:** yes (arithmetic plus code).

**m8. "SPIKE-synch made no calls in the simulated busy block" rests on one window.**
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Fix:** Quote Table 2's rate and soften the inference.
- **Verified:** yes.

**m9. Pin the PySpike version for "whose cap on the window we use".**
- **Where:** Section 11.
- **Evidence:** bugarach's rule matches PySpike 0.6.0's `get_tau`: the smallest of the four gaps, halved, then `fmin(m, max_tau)`, compared with a strict "<". Current PySpike master's `get_tau` (the version with the adaptive-time-scale option) uses `max_tau` only as the default at the train edges and no longer caps windows between events.
- **Fix:** Cite the version whose cap matches.
- **Verified:** yes (both sources read).

**m10. Decoys: both the "at most 0.71" precision ceiling and "a call on a decoy is a false alarm" are too strong.**
- **Where:** Section 5 and Section 10.
- **Evidence:**
  - Matching is greedy. A call on a decoy within 2.5 s of an unclaimed planted event is scored as a hit. The mechanism figures' recording has one decoy within 2.5 s of a planted event.
  - 15/21 ≈ 0.71 is a ceiling only for a detector that calls every 18% lineup, with decoys that can be told apart in time.
  - Section 10's "which caps precision" is true only for such a detector.
- **Fix:** Qualify both statements.
- **Verified:** yes.

**m11. The matching rule's wording is looser than the code.**
- **Where:** Section 6.1 ("Each planted event goes to its nearest call").
- **Evidence:** `score_detections` matches all pairs greedily, closest pair first, with ties broken by span midpoint. A planted event can end up with a call that is not its nearest.
- **Fix:** Write "pairs are matched closest-first, one call per event".
- **Verified:** yes.

**m12. Tube kernel description is loose in a few places.**
- **Where:** Sections 4.1 and 4.2.
- **Evidence:**
  - The quoted widths are Gaussian standard deviations. Tube's 16.3 s surround, cut off at ±12.8 s, is nearly flat.
  - In tube-ratio-guard, only two of the four surrounds (SD 0.3 s and 1.6 s) pile weight at the guard edge, so "most of its weight" overstates it.
  - Tube-ratio's surrounds (SD 0.6–8.0 s) are shorter than "the surrounding seconds" suggests.
  - The 1-frame widening is learned (the floor of the smallest centre width, minimum 1). It is 1 frame for all four checkpoints here, but it is not a fixed setting.
  - `trace` sees the unwidened share of ROIs plus a constant log(ROI count) channel, not the widened brightness line.
- **Fix:** Tighten the wording.
- **Verified:** yes.

**m13. The guard reduces self-raising; it doesn't remove it.**
- **Where:** Section 4.1, tube-guard ("so an event does not raise its own bar").
- **Evidence:** Planted onsets spread with SD 0.36 s. Figure 10B shows a 1.2 s participant span, and widening adds ±0.1 s. Participants more than 0.8 s from the scored frame still fall in the surround.
- **Fix:** Write "raises its own bar less".
- **Verified:** yes.

**m14. The greatest-of rule has a known origin.**
- **Where:** Section 11 ("We have not found who first proposed it").
- **Evidence:** Secondary sources credit Hansen V.G. (1973), "Constant false alarm rate processing in search radars", IEE International Radar Conference, London.
- **Fix:** Cite it after confirming against the primary source.
- **Verified:** partly (secondary sources only).

**m15. The per-group statements were checked only at n = 6.**
- **Where:** Section 2 ("shuffle sits below the shift in each of the four groups"; "holds in each of the four groups").
- **Evidence:** `sur_*_groups_*` compares the groups only at index 6.
- **Fix:** Write "at 6 or more ROIs", or check every n.
- **Verified:** yes.

**m16. Informational: the ⚠ on the quiet level is not a percentile-definition artifact.**
- **Where:** Section 5, the ⚠ on the quiet level.
- **Evidence:** Recomputed on 84 baselines, numpy's linear percentile gives p25/p75 = 3.63/18.60 mHz and MATLAB's `prctile` gives 3.56/18.73. The gap to 5.2 mHz is not about how the percentile is defined.
- **Fix:** None needed; this supports keeping the flag.
- **Verified:** yes.

Sources:
- [PySpike 0.6.0 cython_profiles.pyx](https://raw.githubusercontent.com/mariomulansky/PySpike/0.6.0/pyspike/cython/cython_profiles.pyx)
- [PySpike master cython_get_tau.pyx](https://raw.githubusercontent.com/mariomulansky/PySpike/master/pyspike/cython/cython_get_tau.pyx)
- [PySpike master cython_profiles.pyx](https://raw.githubusercontent.com/mariomulansky/PySpike/master/pyspike/cython/cython_profiles.pyx)
- [Hansen, Constant false alarm rate processing in search radars (Semantic Scholar)](https://www.semanticscholar.org/paper/Constant-false-alarm-rate-processing-in-search-Hansen/b9f381e35d0cc467d022f6661a4b477f0ba78d8f)
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

Relevant files:
- <worktree>\src\bugarach\io.py
- <worktree>\src\bugarach\detectors\cicada.py
- <worktree>\src\bugarach\detectors\sync.py
- <worktree>\src\bugarach\detectors\rate.py
- <worktree>\src\bugarach\detectors\coact.py
- <worktree>\src\bugarach\count_dispersion.py
- <worktree>\src\bugarach\simulate.py
- <worktree>\src\bugarach\learn\train.py
- <worktree>\src\bugarach\learn\nets\tube.py
- <worktree>\src\bugarach\score.py
- <worktree>\tools\fair_bakeoff.py
- <worktree>\tools\make_detector_review.py
- <scratchpad>\review\_work\generator_stats.json
