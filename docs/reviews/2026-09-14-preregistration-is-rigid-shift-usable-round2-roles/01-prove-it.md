GRANT 1 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash)

# Prove It: blind review of the rigid-shift pre-registration (blob 2c9813d)

**Summary.** I can't clear this page for building yet. Three places can't be computed as written:
- **Cell outcomes:** a failure is only "decided" for the leak gate, so count or destruction failures can't produce FAIL, and nothing says which label wins when two apply.
- **Destruction gate:** the visibility and "no gated K" checks, and how retained is averaged across twins, are not specified.
- **Group rule:** it has no row in the outcome table.

Separately, three claims are contradicted by the sources:
- The slow displacements do not follow "the same logic" as fast.
- Cossart's destruction measure did register removal, for its controls.
- The saturation rule drops exactly the K values where the shift fails to remove coordination.

**Run finding:** the grant arrived without Grep and Glob. I did every search through Bash, so no check was skipped. The run record should note that this role took a fallback path.

**Contamination rule:** I read no rigid_shift accuracy, P value or retained share from the 2026-09-11 run. One todo repeats the page's own 0.495–0.524 range, and that was the only rigid_shift number I saw. For rigid_shift I read only which cells exist and their `ok` status, not outcomes.

**Record of groups and mice:** the export folder's own subject and group fields. The lab folder has 84 recordings from 44 mice; Cossart has 59 recordings from 32 mice. The page groups by mouse in folds, bootstraps and averages, the four motion-pinned recordings are present, and withdrawn recordings are the producer's call. Nothing to report there.

## Claim ledger

| Quoted | Source | Recomputed | Verdict |
|---|---|---|---|
| 84 recordings, 44 mice, 4 groups, frame interval 0.1 s | export folder | 84 / 44 / MALE 22, ORX 25, OVX 20, DI 17 / dt 0.1 s | match |
| Cossart median 566 ROIs | export folder | 566 (range 117–1050) | match |
| Zero-event ROIs about 39 % | export folder | fast 37.9 %, slow 39.0 % | match |
| Fast grid: 1.6, then 2.5, then double = 5.0 s | discriminator meta.json | fast grid 0.1 … 1.6, 2.5 | match |
| **Slow 1.4 / 2.8 / 5.6 s is "the same logic on the slow grid"** | discriminator meta.json | slow grid 0.7, 1.4, **2.5**, 2.8, 5.6, 11.2; next step after 1.4 is 2.5, doubled 5.0 | **mismatch** |
| Cossart 4 / 8 / 16 frames | `J_FRAMES_COSSART` | 1, 2, 4, 8, 16, 32 | match |
| Results existed at every declared cell except fast 5.0 s | discriminator.csv (J and status only) | all eight other cells `ok`; no fast 5.0 | match |
| Fast accuracies 0.495–0.524; fast rows voided by the seed-0 defect | seed-0 todo | todo states the same range; 126 of 126 fast results voided | matches its citation; values unverifiable (contamination rule) |
| "To 1.6 s fast, 1.4 s slow, four frames"; "0.7 s leaked" | join todo, not opened | — | unverifiable (contamination rule) |
| Other survivors moved onsets by one frame | discriminator.csv, non-rigid rows | only interval_jitter and pattern_jitter at J = 1 frame went undetected | match |
| Uniform dither is known to leak | positive-control files | significant at every J, all folders (slow 1.4 s: 0.587) | match |
| Joint-ISI measured at fast 2.5, slow 5.6 and 11.2 s; leaked everywhere | discriminator.csv | 36 joint_isi rows `ok`, all significant; fast rows also voided | match (note: its todo still says "all intractable") |
| 3+ of 20 flags 7.5 %, 4+ 1.6 % | binomial | 7.55 % / 1.59 % at α = 0.05; exact with 199 permutations (flag rate 9/200): 5.9 % / 1.1 % | match (conservative) |
| 98.33 / 1.67 percentiles | 0.05 / 3 | 1 − 0.01667 = 0.98333 | match |
| 96.67 % interval = TOST at 0.05/3 | 1 − 2·(0.05/3) | 0.96667 | match |
| 199 permutations, 5 folds, 0.55 effect, 2,000 resamples | discriminator module, `N_BOOT` | same | match |
| Bootstrap is "the recording-identity run's `mouse_bootstrap`" | `tools/measure_recording_identity.py` | that function gives a two-sided 2.5/97.5 interval and does not refit | superseded by the amendment; do not reuse it |
| edge_thinning at 5 s loses about 4 % | `surrogates._edge_dither` | loss = J/(2A) = 50/1200 frames = 4.17 %, same tiling as the leak windows; no same-frame duplicates in real data | match |
| ±2 % of mean real count | export folder, interior windows | fast 0.843 occupied frames per ROI per window (2 % = 0.0169); slow 0.494 (0.0099) | computable |
| 1.0 s = 10 frames; old bin ±2 frames = 0.5 s | `DESTRUCTION_HALF_WINDOW_FRAMES` = 2 | 5 frames × 0.1 s; 10 frames | match |
| Slow 2.0 s is the MATLAB default | `measure_coordination_timescale.m` line 33 | fast 1, slow 2 | match |
| Participation 0.2 / 0.5; K scan | `DESTRUCTION_PARTICIPATION`, `DEFAULT_MIN_ROIS` | (0.2, 0.5); (3, 4, 6, 8) | match |
| Retained = (planted − unplanted after, mean over draws) / same before | `surrogate_stats.destruction` | same | match |
| 200 assessor surrogates | `--destruction-assess-surrogates` | 200 (exploratory draws were 19, now 40) | match |
| Visibility floor 1.0 | none cited | excess unit is co-active ROI·events/min. Synthetic twins: before ≈ 2.8–5.4 at p 0.2 (K 3–6), ≈ 14–15 at p 0.5; K 8 at p 0.2 swings 0.0–1.46 between twins | computable, but under-specified (see findings) |
| freeze_half band 0.10–0.90 at K = 4 | synthetic walk-through | K 4: p 0.2 gives 0.19–0.28, p 0.5 gives 0.45–0.47; homogeneous resample about 0 | attainable |
| Do-nothing ≥ 0.9 with a different assessor seed | synthetic | 0.97–1.03; with the same seed exactly 1.0 (exploratory) | match; effectively a machinery check |
| Negative-control seeds 1000–1019 | exploratory negative seeds file | exploratory seeds were 0–19; no overlap | match |
| "Cossart: the measure registered no removal at any setting" | Cossart destruction.csv, non-rigid rows | homogeneous −0.001–0.013, circular shift ≈ 0, freeze_half 0.27–0.48, do-nothing 1.00 | **mismatch** (the measure does read removal) |
| "The discriminator has no command-line entry point" | `tools/probe_discriminator.py` | a CLI exists, but it runs the controls only | partly wrong |
| Cost "hours on the Mac" | timing | assessor call 0.08 / 0.16 / 0.39 s at 0.5 / 1 / 2 s bins; one 5-fold refit 0.003 s | plausible |
| Screen stopped because it "felt like going in circles" | goal page, handoff, todos | stop on 2026-09-12 confirmed; the wording is not in any listed source | unverifiable |

## Findings

**Blocking**

1. **Cell outcomes can't be computed** (The outcome, completed)
   - **Issue:**
     - "Decided" failure is defined only for the leak gate. A count interval outside ±2 %, or retained above 0.25, is neither a defined FAIL nor a defined UNDECIDED.
     - Since "a void or undecided cell can never make a stream FAIL", destruction and count can never lead to STOPPED.
     - No order is given when several labels apply: a decided leak FAIL with a failed can-pass check, a decided FAIL with an invalid control on another gate, or the stream-wide negative-control void.
   - **Fix:** define decided FAIL for count (the 96.67 % interval lies wholly outside ±2 %) and for destruction (the 1.67th percentile of retained is above 0.25 at some gated K). Declare an order, for example VOID before decided FAIL before UNDECIDED before PASS.
   - **Verified:** yes (read against the text).

2. **Destruction gating is under-specified** (The destruction gate)
   - **Issue:**
     - "Excess before ≥ 1.0" doesn't say whether it is the planted twin's excess or planted minus unplanted, per twin or on the mean of 5 twins.
     - "If no K is gated" doesn't say per participation and bin, or per cell.
     - The bootstrap statistic is not stated: mean of per-twin ratios, or ratio of pooled means.
     - In synthetic twins, "before" at K 8, p 0.2 was 0.0 in one twin and 1.46 in another, so these choices change which K is gated and make the ratio unstable.
   - **Fix:** decide visibility on the 5-twin mean of planted minus unplanted, compute retained as a ratio of means within each resample, and apply "no gated K → VOID" per participation × bin.
   - **Verified:** yes (synthetic).

3. **The group rule has no place in the outcome table** (Groups)
   - **Issue:** "NARROWED for that stream, names the group" doesn't say how it combines with the other stream or with Cossart. It also fires on noise. Even ignoring within-mouse correlation, and with pairs per group from interior windows (DI about 304 … ORX about 447), P(some group ≥ 0.55) is ≥ 10 % at a true 0.50 and ≥ 40 % at 0.52. The noise-free-surrogate case at 0.50 alone would narrow about one run in ten.
   - **Fix:** add table rows for a group-narrowed stream, and base the rule on the group's bootstrap lower bound, not its point estimate.
   - **Verified:** yes.

**Major**

4. **The saturation exclusion is inverted** (Gated K)
   - **Issue:** it removes exactly the K at which the shifted planted event still lands in one bin, which is the "1 s coincidences left in place" failure this gate was added to catch. Synthetic saturation table:
     - At fast 1.6 s, 1.0 s bin, p 0.5: P(largest bin ≥ K) after the shift is 1.00 at K 3 and K 4, so both are dropped.
     - At slow 1.4 s, 2.0 s bin, p 0.5: every K is dropped (0.996–1.00).
     - Other K stay gated at the declared cells, so the gate can still fail; not blocking by the brief's definition.
   - **Fix:** a K where the event survives the shift counts as retained, not as ungated. Keep only the visibility floor.
   - **Verified:** yes (synthetic).

5. **The slow displacements contradict their stated rationale** (The displacements)
   - **Issue:** the next step after 1.4 s on the slow grid is 2.5 s, not 2.8 s, and 2.5 s had exploratory results. The page never says why 2.8 was chosen over 2.5.
   - **Fix:** a dated amendment giving the real reason (a doubling series), and a line under "What was known" that the choice was made with results on file.
   - **Verified:** yes.

6. **The reason for excluding Cossart from destruction is contradicted** (Destruction)
   - **Issue:** on Cossart the controls read removal correctly (homogeneous about 0, freeze_half 0.27–0.48, do-nothing 1.0). The non-rigid candidates just didn't remove much (≥ 0.58). A Cossart result would mean something.
   - **Fix:** either score it, or restate the exclusion as a scope choice.
   - **Verified:** yes for non-rigid rows; rigid shift unverifiable (contamination rule).

7. **The randomness test can't fail against the scheme that matters** (Randomness)
   - **Issue:** the 2026-09-11 discriminator ran from scratch scripts outside git (`run_notes.json`), not from `build_surrogate_screen.py`. A salted key tuple can never equal an unsalted one, so asserting inequality of keys is always true.
   - **Fix:** compare the derived integer seeds against the exploratory `draw_surrogates` key form (recording, stream, exploratory cell id, draw) and against fold and permutation seeds 0–20.
   - **Verified:** yes.

8. **UNRESOLVED has no usable next step** (After UNRESOLVED)
   - **Issue:** a VOID caused by a weak positive control is not an instrument defect, so "rerun changing only the instrument" has no defined fix, and an UNDECIDED stream sets no next action. This path looks likely:
     - Slow uniform dither at 1.4 s scored 0.587 with ICC 0.039. With design effect 2.29 on 1,501 interior pairs, its 1.67th percentile comes out around 0.546, below 0.55, so that cell would be VOID.
     - The page itself says the other slow displacements leaked in the exploratory run.
   - **Fix:** state what the goal does after each UNRESOLVED case.
   - **Verified:** estimate.

9. **"Traced to a fixable instrument" has no criterion** (What STOPPED means)
   - **Issue:** any STOPPED can be escaped after the fact.
   - **Fix:** list in advance the causes that count as fixable.
   - **Verified:** yes.

**Minor**

10. **Units and scope of the destruction controls are missing.** The visibility floor has no unit (ROI·events/min). The freeze_half band, homogeneous ≤ 0.10 and do-nothing ≥ 0.9 don't say which participation, which bin, or whether a point estimate or a percentile is meant. **Verified:** yes.
11. **The negative control is described inconsistently.** "Nothing decides on its P values" conflicts with voiding on 4 of 20 flags. Its windows (interior or all) are not stated. **Verified:** yes.
12. **The count control's test is ambiguous.** "Must fall outside ±2 %" could mean the point estimate or the interval. Either reading works at an expected −4.17 %. **Verified:** yes.
13. **"No amendment changes a signed threshold" understates the changes.** The numbers are unchanged, but the gated-K set changed and the interval became one-sided, which is the more lenient reading. **Verified:** yes.
14. **Cossart's grid position is a different physical displacement.** Four frames is 0.37–0.48 s at Cossart's frame intervals (0.093–0.119 s), against 1.6 s in the lab folder. A VIABLE claim should say so. **Verified:** yes.
15. **Stale wording.** The joint-ISI todo still says every cell was intractable. "No command-line entry point" ignores `tools/probe_discriminator.py`. **Verified:** yes.

Artifact reviewed: `docs/proposals/2026-09-14-preregistration-is-rigid-shift-usable.md`. I wrote no files; all checks ran as inline Python.
