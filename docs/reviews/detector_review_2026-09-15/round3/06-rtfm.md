> **Public copy.** Lines that concern real treatment recordings are removed (17 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

# Role 6 (RTFM, methods and domain) — blind pass, round 3

**Scope.** I read the built plain-text view against the code at commit 699de8e: `tools/make_detector_review.py`, `tools/fair_bakeoff.py`, `bench.py`, `score.py`, `simulate.py`, `detectors/*`, `learn/{train,encode}.py`, `learn/nets/{tube,trace,__init__}.py` and `count_dispersion.py`. I also re-ran four checks at the shipped settings on the bench recordings:
- binned SCE scoring
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- the SPIKE-synch binning quirk
- the decoy-set-aside precision, recomputed from the bake-off files

**Sources.**
- Stella et al. 2022, fetched from eNeuro.
- CICADA's source could not be fetched (GitLab returned 404 and 401). That claim is checked only against the project's own lineage note.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

---

## BLOCKING

**B1. Binned SCE's calls are scored over the wrong stretch of time, so every SCE score is too low.**
- **Location:** "In short" (the five that score about the same); §6.1 ("A wide window rewards wide calls, such as binned SCE's 10-second bins"); §7 and Table 3 (SCE rows, the "exceptions … tuned binned SCE scored higher at the busy level" sentence and its untested explanation); Figures 12 and 13; Table 4 (SCE "Lowest average score").
- **Cause:** `sce.py` lines 314–317 set `onset = bin start` but `width = tlast − tfirst`, which is the spread of the events, not the bin. `score.py` then treats a call as the stretch `[onset, onset + width]`. That stretch starts at the bin edge but is only as long as the event spread, so it can end seconds before the bin's own events. A planted event late in the bin is scored as a miss plus a false alarm. LoCo does not have this problem (`onset = tfirst`).
- **Evidence:** I re-scored the same 24 bench recordings, changing only the stretch each call covers. Stretch placed as shipped, versus the full 10-second bin:

  | level | percentile | F1 as shipped | F1, full bin | other effects |
  |---|---|---|---|---|
  | quiet | 99 (shipped) | 0.370 | 0.547 | recall 0.27→0.39; precision 0.60→0.89; recall at 30% of ROIs 0.61→0.97 |
  | quiet | 75 | 0.452 | 0.710 | anchoring the stretch at the first event instead gives 0.702 |
  | busy | 75 | 0.608 | 0.655 | |
  | busy | 99 | 0.449 | 0.469 | |

- **What changes:** placed correctly, binned SCE at its loosest setting falls inside the 0.70–0.74 band. It scores higher at quiet than at busy, so the quiet-versus-busy anomaly is produced by the scoring, not by the detector.
- **Fix:** have `sce_detect` report `onset = tfirst`, like LoCo, or `width` = the bin's extent. Then re-run the sweeps, the shipped scores and the bake-off. Until then, withdraw every ranking claim about binned SCE and the busy-level exception.
- **Verified against source:** yes (code, plus a re-run).

## MAJOR

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Evidence:**
  - locust's in-block recall is 1.00, 1.00 and 0.77 (30%, 18%, 10%) against a chance line of about 0.50.
  - Chance-corrected recall, (r−c)/(1−c), is about 1.0, 1.0 and 0.54.
  - locust finds in-block events. It also makes many calls there.
  - Only binned SCE, with a chance line of 1.00, is uninformative.
- **Fix:** correct the sentence. Consider plotting chance-corrected recall.
- **Verified:** yes (`blockrecall.json`).

**M2. §3.5 lists "uses one bar for the whole recording" as a difference from CICADA.**
- **Evidence:** `docs/detector_history.md` §2 says "A regional-scope option was added; the original thresholds over the whole recording." One bar for the whole recording is something locust shares with CICADA, not a difference.
- **Fix:** drop it and say "three ways", or replace it with a difference someone has checked.
- **Verified:** partly. The project doc confirms it; CICADA's source was not reachable.

**M3. "In short" says F1 is capped at 0.83 "because some chance lineups look exactly like real events".**
- **Evidence:** decoys are not chance lineups. They are planted correlated bursts (`simulate.py`, "correlated population bursts … never in gt.events"). §2 defines chance lineups as the ones that survive a circular shift, so the opening contradicts the page's own word list.
- **Fix:** "because the test recordings also contain decoys, lineups built exactly like real events but left out of the answer key."
- **Verified:** yes.

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Fix:**
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - Ideally add a milder block level.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Verified:** yes against FOUNDATIONS, not against the lab data.

**M6. Table 3 shows SPIKE-synch's "precision, decoy calls set aside" as 1.00, but that is a capped value.**
- **Evidence:** the raw value is n_hit / (n_scored − decoys reached) = 145/(188−45) = 1.014, cut to 1.0 by `min(1.0, …)` in `_perf_rows`. The approximation subtracts decoys that some call reached. Those calls can also be hits or duplicates, and one call can reach two decoys. A reader sees perfect precision.
- **Fix:** classify each unmatched call exactly (decoy within 2.5 s or not; `Score.fa_times` already exists). Otherwise print "≥0.97" or a dash for any value that hit the cap.
- **Verified:** yes (bake-off JSON).

## MINOR

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Effect:** for the local-reference detectors, the second event sits inside the first one's reference window. I re-ran with the two events forced ≥150 s apart:
  - CoactDetect 18% in-block recall: 6% → 12%.
  - LoCo 18%: 12% → 19%.
  - At 30%: CoactDetect 52% → 60%; LoCo 62% → 60%.
- **Verdict:** the conclusion holds; the gap is slightly overstated.
- **Second issue:** `n_distractors=2` replaces the bench's six decoys, so these recordings have no decoys outside the block, and "from the same recipe" is inaccurate.
- **Fix:** require ≥120 s between the two events (the 220-s placement window allows it) and say the outside decoys are removed.
- **Verified:** yes (re-run).

**m2. §4.1: the filter widths are Gaussian standard deviations, but the page calls them "wide".**
- **Evidence:** full width at half maximum is about 2.35 times the SD, so the centres are about 0.45–1.5 s and the surrounds about 6–38 s.
- **Second issue:** "No filter reaches more than 12.8 seconds" is true of the filters, but the combining network is a dilated 6-layer stack with a 127-frame receptive field (±6.3 s). The model's total reach is about ±19 s, and the combination is not moment-by-moment.
- **Fix:** say "standard deviation", and give the model's full reach.
- **Verified:** yes.

**m3. §3.6 / Table 4 say SPIKE-synch "cannot call such an event at all".**
- **Evidence:** the bound (at most 2/32) is right for an isolated 3-cell event, but events from other ROIs inside the 0.25-s window raise the score. Measured shipped recall at 10% is not zero: about 1 in 120 at both levels, and 2 of 48 inside the busy block.
- **Fix:** "almost never".
- **Verified:** yes.

**m4. §3.6: the frame score is not quite an "average score of the events in each 0.1-second frame".**
- **Evidence:**
  - The port writes each group of same-time events to the first frame centre within 0.1 s. A later group overwrites an earlier one.
  - `min_n` adds up the size of the last group written to each frame, not every event.
  - On 6 bench recordings, about 3% of time groups overwrote an earlier one.
- **Fix:** "roughly the average", or a footnote.
- **Verified:** yes.

**m5. §3.2: "passed once in 10,000 bins by chance" needs two corrections.**
- **Evidence:**
  - Only bins with ≥3 ROIs are tested, so the rate is per tested bin.
  - With low-mean, right-skewed counts from 100 surrogates, a Gaussian tail understates the true chance rate. The direction is known, not merely "may differ".
- **Fix:** say both.
- **Verified:** yes (code).

**m6. §2 / §11: the Stella et al. 2022 summary overreaches.**
- **Evidence:** they measured uniform dithering (small displacements), which loses spikes when binning merges them. They recommended trial shifting within a bounded window, not a wrap-around shift of whole rows. The mechanism the page describes matches.
- **Fix:** "a related failure for random displacement … and recommend shifting whole trains by a bounded amount".
- **Verified:** yes (eNeuro).

**m7. §5 "What the simulator gets wrong": busy real cells are "close to unbunched (1.17)" only in 30-s windows.**
- **Evidence:**
  - In 5-minute windows the same real ROIs read about 6.2.
  - The overshoot is built into the model: a rate multiplied by a Gamma factor whose shape is fixed across ROIs gives a variance-to-mean ratio of about 1 + rate × window × Var(M), with Var(M) ≈ 1.83 from the fitted shapes.
  - So simulated bunching must grow in proportion to rate.
- **Fix:** state the window, and add that one line of mechanism.
- **Verified:** yes.

**m8. §5 and Figure 10: "the 80 baselines the simulator was fitted to" does not match the fitted constants.**
- **Evidence:** `bench.py` records the rate spread and the bunching as fitted on different window and ROI sets, from an earlier export. The page recomputes on the current export using the fitter's selection.
- **Fix:** "selected the way the fitter selects them".
- **Verified:** yes.

**m9. §5: the busy recordings carry 17.2 mHz outside the block, below the nominal 19 mHz, even counting planted events.**
- **Evidence:** the 24 seeds draw ROI rates about 13% under the Gamma mean at both levels.
- **Fix:** call 5.2 and 19 "nominal".
- **Verified:** yes.

**m10. §3.4 omits that binned SCE never joins adjacent marked bins (`merge_gap_sec` is NaN).**
- **Effect:** an event that straddles a bin edge makes two calls, one hit and one duplicate false alarm.
- **Verified:** yes.

---

## Checked and correct

- **Shipped settings match Section 3 and Table 1** (`OPERATING_POINTS`):

  | detector | settings |
  |---|---|
  | rate+context | 5 Hz above a 60 s average, 1 s window, 3 s merge, single-step drop |
  | CoactDetect | 2 s bins, 60 s context, α 1e-4 (z 3.72), 100 shifts, 3 s merge |
  | LoCo | 1 s bins, ±60 s halves, 15 s step, 99.9, larger-side bar, 2 s merge |
  | binned SCE | 10 s bins, 99, 200 shifts, strictly above the bar |
  | locust | 1 s on-period, 99.999, 100 shifts, one bar, peaks ≥4 frames apart, no ROI minimum |
  | SPIKE-synch | half the smallest of four gaps, cap 0.25 s, level 0.1, gap 0.5 s, minimum 3 events |

- **Surrogates:** every surrogate-based detector uses the circular shift. The shift-versus-shuffle mechanism (same-bin doubles) is correct and consistent with Stella.
- **Event time:** all six use the half-rise. On folder input `locs` holds the half-rise, and the simulator sets `locs` = half-rise.
- **Event sizes:** 10% of 33 ROIs is 3 cells under MATLAB rounding.
- **Tuning:** ties go to the looser value because of grid order.
- **Learned training:**
  - Busy block and decoys are labelled 0.
  - 10 + 2 recordings drawn from 18.
  - The seed-1 run uses a different training set.
  - 1,149 parameters; ±0.8 s guard; one-tenth learning rate for the controls.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Matching:** closest pair first, with a zero gap inside a call's stretch. Busy-block calls are left out of precision.
- **F1 ceiling:** 0.83 is right. With k the share of 18%-sized lineups a detector calls, F1 = 2(10+5k)/(25+11k), which rises with k and reaches its maximum 0.833 at k = 1.
- **Rate levels:** the percentiles are per-recording mean ROI rates, which is the basis `REGIMES` uses.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

**Files:**
- `<worktree>\src\bugarach\detectors\sce.py`
- `<worktree>\src\bugarach\score.py`
- `<worktree>\tools\make_detector_review.py`
- `<worktree>\src\bugarach\bench.py`
- `<worktree>\docs\detector_history.md`
- `<home>\bugarach\bugarach\docs\FOUNDATIONS.md`

Sources:
- [Stella et al. 2022, eNeuro](https://www.eneuro.org/content/9/3/ENEURO.0505-21.2022)
