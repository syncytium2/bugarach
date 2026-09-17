GRANT 1 MISMATCH — missing Grep, Glob; holds Read, Bash (no editing tools held)

# Claim verifier: slow co-modulation page at commit 2f77de1

**Verdict: the numbers hold up, and five problems don't.** I reran the measurement into `<scratchpad>/review3/r1/rerun/` (12 workers, 127 s). The new `summary.json` matches the shipped one exactly except for `elapsed_sec`, and the new `results.json` matches the darkroom copy apart from the same field. So every pooled number on the page can be reproduced, and I checked each one against the file rather than reading it off a figure. `tests/test_measure_slow_comodulation.py` passes (11 tests). What doesn't hold is not the arithmetic:
- **The contaminated recordings:** all four the producer flagged are in the analysis, and all four are DI.
- **The slow stream:** the page says things about the models' training contrast on a stream no model was trained on.
- **One group "carrying most of it":** this reads more into the data than the ⚠ in the group section allows.
- **Synthetic intervals:** the page says the synthetic numbers have none, but `summary.json` holds them.
- **Figure 3:** one claim cites panels that don't draw the arm it quotes.

## Notes on this run (not about the page)
- **Missing tools:** Grep and Glob were not granted. I used `git grep` and `grep` through Bash instead.
- **The worktree changed during the review.** `tools/make_slow_comodulation_figure.py` has an uncommitted diff (61 lines added, 35 removed). The page, the figures, `summary.json` and the measurement tool are unchanged from 2f77de1, and I reviewed the committed version of the figure tool.
- **One stray job may still be running.** I launched a helper through stdin with multiprocessing; it produced no output. Both attempts to find and stop it were refused by the permission classifier. It writes nothing outside its own log, and I got the same numbers from a serial rerun.

## Claim ledger
| quoted value | cited source | recomputed | result |
|---|---|---|---|
| Fast stream, 1-minute bins: 3.21 [2.47, 3.97] as recorded, 2.46 detrended; 2.42 [1.86, 2.94] and 1.68 with episodes removed then the block control | summary.json | 3.2114 [2.4681, 3.9689] · 2.4594; 2.419 [1.8589, 2.9447] · 1.6787 | match |
| Median recording 1.33 (0.96 detrended); above 1 in 67 %; one circular shift above 1 in 55 % | checks.per_recording | 1.328 · 0.958; 0.667; 0.548 | match |
| "about a third of the recorded excess is a straight-line trend" | derived | (2.21 − 1.46) ÷ 2.21 = 34 % | match |
| Fast event peak +1.91 [+1.17, +3.13]; +0.88 with episodes removed; shoulder +0.06 to +0.08 from 5 s to 56 s; +0.05 at 78–110 s | excess bins | +1.910 [+1.173, +3.127]; +0.878; 0.061–0.078; +0.046 | match |
| All 39 cells in the table behind Figures 4 and 5 (value, interval, detrended) | summary.json | checked to 4 decimals | match, all 39 |
| Paired differences, 10 cells | checks.paired | e.g. 0.8052 [0.3928, 1.3466]; 9.1981 [5.7443, 11.9925] | match, all 10 |
| Per-recording table, 6 rows | checks.per_recording | e.g. slow as recorded 1.917 [1.095, 7.027], 80 %, 1.505 | match |
| Slow stream: peak +20.8 [+16.5, +25.8]; 11.4 → 2.59 → 2.17 [1.58, 2.88]; 1.43 detrended; median 1.23; 71 % | summary.json | 20.776 [16.484, 25.791]; 11.367 → 2.593 → 2.169 [1.580, 2.882]; 1.432; 1.229; 0.714 | match |
| Slow dip −0.56 and −0.51; +0.05 and +0.05 once episodes are removed | excess at 2.74–5.35 s | −0.558, −0.511; +0.051, +0.055 | match |
| "rigid shift fills in (+0.35 to +0.57)" | excess | J = 10 s: +0.568, +0.516; J = 20 s: +0.366, +0.351; **J = 1.6 s: −0.179, −0.381** | mismatch for J = 1.6 s |
| Five busiest slow recordings hold 62 % of expected pairs; removal took 64 % weighted, 8.8 % median | checks, coact | 0.617; 0.637; 0.0878 | match |
| Dard et al.: +0.78 [+0.64, +0.96]; dip −0.05 [−0.09, −0.01]; 15.2 [12.5, 18.3]; 13.2 detrended; 6.9 detrended under the block control; above 1 in every recording | summary.json | 0.778 [0.639, 0.955]; −0.051 [−0.088, −0.015]; 15.23 [12.50, 18.28]; 13.15; 6.85; 1.0 | match |
| Per pair of ROIs: 0.021 Dard, 0.019 fast, 0.034 slow | per_pair_median | 0.0213, 0.0193, 0.0336 | match |
| Effective mice: 12.7 fast, 7.7 slow, 17.5 Dard; 23–25 under the variance weighting | summary | 12.68, 7.65, 17.46; 24.7, 23.1, 24.4 | match |
| Leave-five-out: 2.34 fast, 1.84 slow; the five hold 25 %, 27 %, 16 % of the weight | checks | 2.34, 1.84; 0.251, 0.272, 0.159 | match |
| Removal: median 2.5 % and 8.8 %; weighted 7.2 % and 64 %; time share 1.3 % and 7.5 % | checks, coact | 0.0247, 0.0878; 0.0718, 0.637; 0.0127, 0.0748 | match |
| DI +0.11 against about +0.05 for the others; DI 3.71 (median 2.94) against 2.83, 1.96, 3.30 (medians 1.81, 1.20, 1.32) | by_group, checks_by_group | 0.10–0.12 against 0.04–0.06; all six values match | match |
| Heaviest mouse per group: 37–48 % fast, 52–64 % slow | by_group top_mouse_share | 37.4–47.9 %; 51.8–64.4 % | match |
| "one group of mice carries most of it" | recomputed from results.json | DI holds 52 % of the pooled 1-minute excess variance after removal and blocking, from 17 of 84 recordings | borderline; see findings |
| 84 recordings, 44 mice, 17–20 min; 59 recordings, 32 mice, 19–25 min, median 566 ROIs | summary; `slices.csv` | 84, 44, 17.0–20.0; 59, 32, 19.2–24.8, 566 | match |
| No imaging date holds more than one group | `slices.csv` | 42 dates, 0 with more than one group; 0 mice in two groups; no blank cells | match |
| Withdrawn recording absent | PROVENANCE (one excluded) | absent from the folder | match |
| Figure 3: 20 s world +0.68 → +0.51 (J = 10 s) → +0.36 (J = 20 s) | synthetic excess | 0.677 → 0.505 → 0.355 | match |
| 5.25 of 5.53; 6.93 of 6.95; 1.71 of 1.79 | var_ratio, rigid_20 (J not named on the page) | 5.250/5.528; 6.932/6.948; 1.714/1.792 | match |
| Removal deletes a median 1.7–5.0 % in the event-free worlds; ratio stays within 0.3 | share_removed; minus_coact | 1.73–4.95 %; −0.18, −0.22, +0.25 | match, but that arm isn't drawn in the cited panels |
| Benchmark shoulder about +1.0, 1-minute ratio 8.9; background 0.88 | synthetic | about 0.9–1.07 out to 56 s; 8.94; 0.884 [0.80, 0.99] | match |
| Background reads 0.88 "because of a fixed 60 s grid" | `simulate.py`; my rerun | Burst grid off: 1.01. Window aligned to the grid: 1.20. The spec has two grids, 300 s and 60 s | cause confirmed; description incomplete |
| 32 ROIs, mean rate 0.0097/s, 15 events of 3–7 ROIs | spec plus `simulate.py` | 32; 0.009706; participant counts 3, 4 and 7 | match |
| Promiscuity probe: +0.06/s from 1,200 to 1,500 s, every ROI | `simulate.py` | yes, with a 30 s ramp the page doesn't mention | match |
| Panel D centred on a planted event | regenerated recording 0 | zoom 725–785 s, 7-ROI event at 754.4 s | match |
| One real recording: rigid shift tracks it, circular shift doesn't | results.json counts per minute | r = 0.94 for rigid, 0.13 for circular | match |
| Onset intervals per second: 15, 95, 333, 771; about 1,050 beyond; shortest 2.80 s | recomputed on slow baselines | 15.0, 95.0, 333.3, 771.2; 1,117 (5.4–7 s), 992 (7–10 s); 2.80 | match |
| Field steps: three recordings, 4 s each, 12 s in 27 hours | `field_steps_excluded.tsv` against baseline windows | 3 of 9 steps inside baselines; 26.9 h trimmed | match |
| CoactDetect: 2 s bins, 60 s context, α = 10⁻⁴, merge gap 3 s | `detector_params`, `coact.py` | identical for both streams | match; "calibrated" is wrong for slow |
| Branch check: 95.8–100 %, 52.4–54.1 %, 54.9–62.4 %, 12 fits each, at f55db21 and 4518d21 | git show | 0.9576–1.0; 0.524–0.5413; 0.5486–0.6243; 12 fits per condition, 10 conditions; both commits on the branch; sinusoid with a 40 s period | match |
| `count_excess` subtracts a 30 s moving mean | branch `tube_self_supervised.py` | 301 frames, which is 30 s only at 0.1 s frames | match with a caveat |
| Question posed on main about "tens of seconds" | origin/main report | "10–45 s" | match |
| Peaks trail the half-rise by 0.3 s and 2 s; ±2 s step exclusion; pups P5–P12 | export spec line 327; MILESTONES line 110; `import_dandi.py` | as stated | match |
| "2 minutes 15 seconds on 10 workers" | results.json | 135.18 s; the worker count isn't recorded, and the default here is 12 | time matches, workers unverifiable |
| Synthetic numbers "carry no interval" | summary.json | Every synthetic arm has `lo`/`hi`/`var_lo`/`var_hi` over 24 recordings | mismatch |
| DeepCINAC; the protocol paper; movement link; activity stable over each recording | round-2 review record (paper read there) | can't reach the papers from here | unverifiable by me |

## Findings
| # | location | issue | severity | suggested fix | verified |
|---|---|---|---|---|---|
| 1 | Decision section (lines 322–324); group section (267–275); short answer (line 25); slow-stream bullet | **The four recordings the producer flagged for a motion-correction contaminant are all in the analysed 84, and all four are DI.** The page raises them only as a possible explanation and says neither of those things.<br>• **Fast stream:** the result holds without them (DI 2.74 → 2.75; pooled 2.42 → 2.41; they carry 4.8 % of the pooled excess).<br>• **Slow stream:** it doesn't. They carry 18 % of the pooled 1-minute excess after removal and blocking; pooled 2.17 → 2.05; DI 2.04 → 1.57; DI's slow curve after removal drops from about +0.11 to about +0.05.<br>This is not a request to filter them out. | major | State that the four are included and all DI. Report the sensitivity (a view without them, not a filter) next to the group paragraph and the slow bullet. | yes |
| 2 | Slow-stream bullet (lines 195–196); label-free section (line 303); short answer (lines 32–34) | **"Rigid shift fills in the dip" is true only at J = 10 and 20 s.** At 1.6 s the dip stays (−0.18, −0.38), yet the page uses the 1.6–20 s range for the models.<br>**"On the lab slow stream the contrast also paid for…" describes a contrast no model was trained on.** The label-free models were trained on lab fast-stream baselines and on simulated recordings, at J = 10 and 20 s (`tube_self_supervised.py`: `J_SEC = (10.0, 20.0)`, `ssl_real` on the fast stream). | major | Say "at J = 10–20 s". Frame the slow-stream point as what such a contrast *would* pay for, and say no model was trained on that stream. | yes |
| 3 | Short answer (line 25) | **"One group of mice carries most of it"** reads more into the data than the page's own ⚠ allows (group can't be separated from imaging day) and than "the pooled result is not one group's". DI holds 52 % of the pooled 1-minute excess variance from 20 % of the recordings. OVX's pooled ratio after removal is 2.62, against DI's 2.74. | minor | "One group of recordings (DI, 17 of 84) holds about half of it." | yes |
| 4 | Lines 14–15, 343–345 | **"Synthetic numbers carry no interval" is false.** `summary.json` has 95 % intervals over the 24 synthetic recordings for every arm. For example, background 0.88 [0.80, 0.99], which excludes 1; shallow 1-minute world with episodes removed 2.05 [1.79, 2.30] against 1.79 [1.53, 2.06] as recorded. | minor | Report the intervals, or say they exist but aren't shown. | yes |
| 5 | Lines 131–135, 149–150 | **The episode-removal claim cites panels that don't draw its arm.** "Removing episodes spares drift (C, D, F)… within 0.3" uses the removal-only arm, but panels C, D and F draw only removal followed by the block control. The caption's "every arm" also leaves out the removal-only arm. In the shallow world, the one closest to the lab, removal *raises* the ratio by 0.25, about a third of that world's excess. | minor | Either cite `summary.json` or draw that arm. Say "raises it by up to 0.25" rather than "spares". | yes |
| 6 | Figure 5 caption (lines 177–178) | **"The calibrated operating point on both lab streams" is overstated for the slow stream.** That point is the viewer's fast-stream setting, tuned on the generator. The previous commit used the documented slow setting (1 s bins, 120 s context, α 10⁻⁶), and its docstring said no slow point exists. I reran the slow arms at that setting with the current null: removal then block control gives 2.36 (detrended 1.53, median 1.25, above 1 in 74 %, median removal 6.8 %), against 2.17 on the page. The conclusion survives. | minor | Say the fast-stream point is used on both streams and that no slow point is calibrated. Optionally give the 2.36 alongside 2.17. | yes |
| 7 | Figure 4 caption (lines 169–170) | **The Dard et al. dataset isn't reconciled with what was published:** 59 recordings from 32 mice, while the published dataset has 62 sessions from 35 pups (tree record: `docs/reviews/rigid-shift-look-2026-09-15-roles/02-doi-or-die.md`). The page doesn't say that three sessions are missing, and nothing records why. | minor | "59 of the 62 published sessions (32 of 35 pups); why three are absent is not recorded." | partly (tree record, not the DANDI API) |
| 8 | Lines 155–157 | **The 0.88 explanation is incomplete.** The generator varies rates on two fixed grids (300 s and 60 s). The below-1 value comes from the 20 s trim putting the 1-minute bins out of phase with the grid: with the grid off the ratio is 1.01, and with the window aligned it is 1.20. So "ratios from the generator carry that offset" isn't a fixed offset; its sign depends on the window. The probe's 30 s ramp is also left out. | minor | Name both grids and say the offset is a phase effect of the trim. | yes |
| 9 | Lines 32–33, 297–298 | **"Leaves change over a minute or more in place in every dataset" hides a removal the data show.** At 1-minute bins, rigid shift at 20 s removes about 10 % (fast), 14 % (slow) and 20 % (Dard) of the excess, and every paired interval excludes zero. | minor | "Leaves 80–90 % of it". | yes |
| 10 | Lines 30–31, 344 | **The generator comparison is across different window lengths.** "The benchmark generator contains more minute-scale shared change than the lab fast stream" compares a 1-minute ratio over 3,525 s windows with one over 17–20 minute windows. Slow structure scales with window length. | minor | Name the window lengths, or compare on a matched crop. | yes |
| 11 | Lines 111–112 | **"The excess summed over every lag… is zero"** holds exactly for the excess *pair count* (observed − expected), not for the ratio − 1 the page defines as "excess". | minor | "the excess pairs summed over every lag". | yes |
| 12 | Line 323 | **"Pinned ROIs together"** paraphrases a source that says "pinned 12 ROIs to the frame floor" (`current_export.toml`, the todo). | minor | Use the source's wording. | yes |
| 13 | Line 312 | **`count_excess` subtracts a 301-frame mean, not a 30 s one.** That is 30 s only at 0.1 s frames, and up to about 36 s at the lab's 0.119 s. | minor | "a 301-frame (about 30 s) moving mean". | yes |
| 14 | Line 397 | **"On 10 workers" can't be checked.** The run doesn't record `--jobs`, the default here is 12, and my rerun on 12 workers took 127 s. The same point was raised in round 2. | minor | Record `--jobs` in `results.json`, or drop the count. | no |

## Sources I checked beyond the ones the page names
- **Group and mouse record:** the steps-excluded export's `slices.csv` (`group_id`, `mouse_id`, `date`), with nothing blank.
- **Withdrawals:** the export's PROVENANCE file. The one withdrawn recording is absent, and the count reconciles at 84.
- **Known contaminant:** the `steps_excluded` note in `current_export.toml` and the todo on four recordings (finding 1).
- **The Dard et al. session count:** from the tree's earlier review record (finding 7).
- **Regeneration:** compared against the previous commit's `summary.json`. Every change is accounted for:
  - New arms were added (the null for the removal arms and the single-circular-shift reference).
  - The removal-arm ratios moved because of the new null.
  - The slow stream's removal changed because its CoactDetect setting changed (finding 6).
  - Recording, mouse and hour counts are unchanged.

Files:
- <worktree>/docs/learned/slow_comodulation/README.md
- <worktree>/docs/learned/slow_comodulation/summary.json
- <worktree>/tools/measure_slow_comodulation.py
- <worktree>/current_export.toml
- <worktree>/docs/todo/2026-09-10-four-recordings-carry-an-unflagged-contaminant.md
- <scratchpad>/review3/r1/rerun/ (rerun `results.json`, `summary.json`, log)
