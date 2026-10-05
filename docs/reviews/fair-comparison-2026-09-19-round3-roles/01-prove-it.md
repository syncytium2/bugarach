<!-- Verbatim role report, except that this machine's absolute paths are written as %USERPROFILE% and <darkroom> (the repository is public). The unedited original is in <darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-roles-round3/. -->

GRANT 1 ok — Read, Grep, Glob, Bash

# Role 1 (Prove It): round 3, blind pass

**Artifact:** `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\report.html`. I confirmed its hash is 5c0ccbb, and the darkroom `index.html` is byte-identical to it.

**Summary:** every number in Table 2 and Table 3 recomputes exactly from the committed files, and so do the replicate figures. Nothing I found is blocking. There are two moderate findings. In the first, the page applies its own "best net" rule inconsistently to the replicate. In the second, a spread figure (106 per hour) sits in a paragraph about the budgeted choices but comes from an F1-alone choice. The rest are minor wording and precision fixes.

## What I checked, and the source for each
- **Run files** (repo `.json` files, `selections/`, `configs/`), checked against the darkroom originals. The repo copies differ from the darkroom's only in the two paths that were made anonymous, so the page's "the same summaries unedited" holds.
- **Replicate:** the raw darkroom `results.json` and `meta.json`. `replicate_summary.json` matches the raw file with 0 mismatches. The replicate's declaration is identical to this run's (axes, configurations, untuned settings, grids, budget, bench, seeds).
- **Run code** at `e8764aa`: `tools/tune_learned_vs_coact.py`, `train.py`, `encode.py`, `chorus*.py`, `score.py`.
- **Bench:** `bench.py` is unchanged between `e8764aa` and the report's HEAD, and so is `score.py`. I regenerated Figure 1's recording and the crowded recordings with it.
- **Documents behind the prior-result and limit claims:** `docs/goals/learned-model-family.md`, `HANDOFF-coded-detectors.md`, `HANDOFF-slow-comodulation-on-the-de-pinned-export.md`, `docs/learned/bench_measured.json`, commit 2120516, and PR #660 through `gh`.
- **Diff against the previous build** (c261f9c): Table 2 values are unchanged. The only numeric removal is the t values for inadmissible coded choices, which matches the new caption.
- **Record of design and unit membership:** the units here are simulated recording seeds. Both backgrounds of a seed, and its empty twin (seed + 100000), always sit in the same fold (`fold_of` is keyed by seed). The replicate's seeds (2000 to 2047) don't overlap this run's. The only real-data dependency is the bench fit: 84 recordings from the `steps_excluded` export, and the page states that export's contamination as a limit. The page makes no independence claim about real units, so there is no finding here.

## Findings
| # | Location | Issue | Severity | Suggested fix | Verified against a source |
|---|---|---|---|---|---|
| 1 | §6, replicate paragraph ("In the replicate, on F1 alone, the best net is ahead in most folds…") | §6 says the best net is picked by its held-out mean. Counting every refit, the replicate's best net by that rule is **chorus_gain_norm** (0.719), not chorus_norm (0.690). Its difference from CoactDetect is −0.029 per fold (+0.006, −0.005, −0.003, −0.114), ahead in **1 of 4** folds. chorus_norm is the replicate's best only once failed refits are set aside: the generator picks it with `without_low=True` (build_fair_comparison_report.py line 1067). So "the best net is ahead in most folds" mixes two selection rules. | moderate | Name the net: "this run's best net, chorus_norm, …". Or state that the replicate's best net is chosen with failed refits set aside, and give chorus_gain_norm's every-refit figure (−0.029, ahead in 1 of 4 folds). | yes (raw replicate results.json) |
| 2 | §10, "False alarms on held-out recordings": "…differs by up to 106 per hour" | The paragraph opens "Under the budget", but 106 comes from an F1-alone choice: chorus_gain_norm, fold 1, quiet background, refits at 45, 107, 1, 27 and 5 per hour. The code takes the maximum over both selections (line 1583). Under the budget the largest spread is **93 per hour** (tube, fold 2, quiet); for the chorus nets the paragraph is about, it is **23 per hour**. | moderate | Restrict the figure to the budgeted choices (93 per hour), or label 106 as coming from a choice on F1 alone. | yes |
| 3 | §10: "CoactDetect 8 to 12" | CoactDetect's held-out probe rates under the budget, as a mean of the two backgrounds, are 12.5, 10.0, 11.5 and 8.0 false alarms per hour. The `:.0f` format rounds 12.5 down to 12 (Python rounds halves to even). | minor | Write "8 to 12.5". | yes |
| 4 | §8: "recall 0.80 or more in every fold, background and selection" | chorus_gain_norm on F1 alone, fold 3, busy background, 18% level: 239 of 300 events = **0.797**. The same fold's 30% level is exactly 0.800. This is the fold that holds a failed refit. | minor | Write "0.79 or more", or name the exception. | yes (breakdown.json) |
| 5 | Figure 1 caption ("6 ROIs whose onsets have a standard deviation of 0.36 s"); §2 ("Each event's onsets have a standard deviation of 0.36 s") | 0.36 s is the setting the simulator draws onsets with (`jitter_sec`), not a measurement. This event's six onsets (993.4, 993.3, 993.8, 993.1, 992.9 and 993.2 s) have a standard deviation of 0.31 s (n−1). | minor | Write "drawn with a standard deviation of 0.36 s". | yes (regenerated seed 1000, busy background) |
| 6 | §10 and the answer paragraph: "this run cannot say which of three changes removed it … or the tuning" | The run's own rows narrow this down. Tuning moved chorus_norm by only +0.005, and untuned chorus_norm already trails CoactDetect on this simulator (0.736 against 0.748, −0.012). So tuning the nets did not remove a 0.10 lead. What stays confounded is the new simulator against CoactDetect's settings (goal 1's values plus this run's search). | minor | Say "the tuning" means CoactDetect's side, or narrow the sentence to the two changes that remain confounded. | yes (results.json, untuned rows) |
| 7 | Answer paragraph: "the nets find more of the faintest events against a busy background, CoactDetect more against a quiet one" | breakdown.json covers only CoactDetect and the two chorus nets; line_length and tube were never broken down. The claim does hold for both chorus nets under both selections. | minor | Write "the chorus nets". | yes |
| 8 | §9: "4 coded detectors have no admissible result … the starting points of binned SCE, LoCo, SPIKE-synch and rate+context were themselves over it in every fold" | The four detectors listed are not the four with no admissible result (LoCo, SPIKE-synch, rate+context and locust). locust's starting point was also over the budget: all 16 settings its search tried were refused in every fold, the start included. So five starting points were over, not four. | minor | Include locust, or write "every coded starting point except CoactDetect's". | yes (selections/*: `rescued_from_inadmissible`, locust `n_refused == n_scored == 16`) |
| 9 | §9: binned SCE fold 4 under the budget "close to the limit" | Its crowded F1 is 0.703 against a start of 0.714, a drop of 0.011 against the 0.02 allowance. That uses about half the allowance. | minor | Give the number: "0.011 below its start, inside the 0.02 allowance". | yes |
| 10 | Table 1: "49 / 39 / 46 / 19 / 46 / 47 grid values" | These count the declared grids before §4.1's context rule removed the 240 s and 480 s values. After removal, CoactDetect has 48, LoCo 44 and rate+context 46. | minor | Write "declared grid values", or give the counts after the rule. | yes (meta.json hand_axes) |

## Claim ledger (quoted value · source · recomputed · verdict)
**Bench and design**
- Bench recording: 45 min, 33 ROIs, 15 events (5 at each of 30/18/10%), onset SD 0.36 s, events at least 120 s apart, 6 distractors at 18%. Source: meta.json and bench.py; values 2700 s, 33, (5,5,5), 0.36, 120, 6, 0.18. **Match.**
- Probe: extra 0.06 per second, from 20m (1200 s), 5 min, 30 s ramp, about 12× quiet and 3× busy. Source: bench.py and simulate.py (the probe is added on top of background). Recomputed 1200 to 1500 s, 0.06/0.0052 = 11.5, 0.06/0.019 = 3.2. **Match.**
- Backgrounds 0.0052 and 0.019 per second per ROI at p25 and p75. Source: `bench.REGIMES` docstring. **Match.**
- Precision ceiling 0.71. Recomputed 15/21 = 0.714. **Match.**
- Figure 1: seed 1000, busy background, 33 rows, 2,595 firings, event at 16m33s joined by 6 ROIs, 2 distractors in 15m40s–26m. Regenerated: 33, 2595, 993.33 s, 6, 2 (1034.4 and 1091.8 s). **Match.** Onset SD: see finding 5.
- 96 planted-event recordings plus 96 empty ones; seeds 1000–1047; 4 folds of 12. Source: meta.json. **Match.**
- Hit tolerance 2.5 s: `score.TOL_SEC` = 2.5. **Match.** "Stop changing at 2.5 s": the TOL_SEC docstring says CoactDetect and LoCo plateau at 2.5 s and rate+context at 2.0 s. **Match.** The nets' tolerance curve "never measured": `test_tolerance_curve.py` has no nets. **Partly verified.**
- 24 configurations per net (untuned plus 23), with 5, 6, 5 and 5 settings. Source: meta.json, 24 unique keys each, untuned included. **Match.**
- Learning rates (0.003, 0.01, 0.03), steps (900, 1,800, 3,600), 3 or 4 architecture settings. Source: learned_axes. **Match.**
- Settings and grid values: 10/49, 7/39, 10/46, 4/19, 10/46, 10/47. Source: hand_axes. **Match** (declared counts; see finding 10).
- Context values removed (CoactDetect 240 s; LoCo 240 and 480 s; rate+context 240 s). Recomputed from the grids against the 120 s rule. **Match.**
- Nadeau–Bengio factor 0.655: √(3/7) = 0.6547. **Match.** t critical value 3.18 at 3 degrees of freedom: 3.182. **Match.**
- Net fits 10 of 72 recordings; threshold picked on the last 2. Source: fold_draws.json and the code. **Match.**
- Fitting sets at the first training seed share 2 to 3 of their 5 recording seeds. Recomputed pairwise overlaps: 3, 2, 3, 3, 2, 3. **Match.**
- Before the fix, 2 distinct fitting sets, with folds 2 to 4 all fitting seeds 1000–1004. Source: fold_draws before_fix. **Match.**
- Run refuses to start if two folds share a fitting set. Code line 1721; `fold_check.distinct` = True. **Match.**
- Reference CoactDetect: alpha 1e−5, context 120 s, merge gap 8 s, guard 1 s. LoCo at 99.9, 8 s. Source: meta reference and coded_base. **Match.**
- Budget margin 1.6, gated on the probe and on the quiet empty recordings. Source: meta.json. **Match.** Floor of 1 false alarm never reached: code `max(1.6·v, 1/h)`; budgets run 10.4–16 per hour against a floor of about 0.33 per hour. **Match.**
- Under the budget a net uses one threshold per fold; on F1 alone each refit picks its own. results.json: 1 distinct threshold per budgeted fold, 2–5 per F1-alone fold. **Match.**
- Crowded recordings: 24 recordings of 3 h, 180 events each, gaps at least 6 s (median 43 s), seeds 1–12, 0.02 not yet signed. Recomputed: 24, 3.0 h, 180, minimum 6.001 s, median 43.3 s; N_TAIL = 12; `MAX_CROWDED_DROP` docstring says "Tony has not signed". **Match.**
- Goal 1's crowded seeds 49 to 60. Source: the crowded_check tool's docstring (not goal 1's own record). **Match, secondary source.**
- Replicate: seeds 2000–2047, WSMIP065, the same GPU model (RTX A4000), configurations held fixed. Source: replicate meta.json. **Match.**

**Table 2** (all 10 rows, both selections). Recomputed from results.json:
- chorus_norm: 0.741, −0.007 (t −1.80, corrected −1.18); under the budget 0.716, −0.032 (t −3.12, corrected −2.04). **Match.**
- chorus_gain_norm: 0.703, −0.045 (t −1.24, corrected −0.81); under the budget 0.718, −0.030 (t −13.02, corrected −8.52). **Match.**
- line_length: 0.705, −0.043 (t −4.73, corrected −3.10); under the budget 0.697, −0.051 (t −5.33, corrected −3.49). **Match.**
- tube: 0.631, −0.117 (t −17.59, corrected −11.51); under the budget 0.594, −0.154 (t −4.55, corrected −2.98). **Match.**
- CoactDetect: 0.748 both ways. **Match.**
- binned SCE: 0.771, +0.023; under the budget 0.770, +0.022. **Match.**
- LoCo: 0.738, −0.010 (t −13.90, corrected −9.10); under the budget 0.689, −0.059. **Match.**
- locust: 0.683, −0.065 (t −9.60, corrected −6.28). **Match.**
- SPIKE-synch: 0.655, −0.093 (t −10.74, corrected −7.03); under the budget 0.274, −0.474. **Match.**
- rate+context: 0.647, −0.101 (t −14.37, corrected −9.41); under the budget 0.466, −0.282. **Match.**
- Admissibility notes (SCE 4 of 4 fail and 3 of 4 not admissible; LoCo, SPIKE-synch and rate+context 4 of 4 not admissible; locust all refused), recomputed from crowded_check.json and the selections. **Match.**

**Section 6**
- chorus_norm behind CoactDetect in every fold. **Match.**
- CoactDetect's two searches chose the same setting in all 4 folds (config keys equal). **Match.**
- CoactDetect passes the crowded check in 8 of 8 cases. **Match.**
- Replicate chorus_norm per fold +0.003, −0.243, +0.003, +0.007; mean −0.057; 2 of 5 refits below 0.2 in fold 2; with those set aside ahead in 4 of 4 folds by +0.005. **Match** (see finding 1 on which net is "best").
- Replicate: every net behind CoactDetect under the budget (−0.092, −0.025, −0.053, −0.132). **Match.**
- Figure 8's marks right of zero: +0.0001 and +0.0004. **Match.**

**Section 7**
- The nets' merge gap is 2 s, or 20 frames. Source: `encode.py` and `train.py` default `merge_gap_frames=20`. **Match.**
- CoactDetect 0.731, 0.748 and 0.803 at 2, 8 and 30 s. Recomputed 0.7315, 0.7480, 0.8027. **Match.**
- chorus_norm 0.741 at 2 s and 0.775 at 16 s. Recomputed 0.7411 and 0.7749. **Match.**
- line_length and tube fall as the gap widens, and their worst refits sit at the bottom of the grid. Recomputed at thresholds 0.0001 and 0.00018. **Match.**
- Reproduction within 0.0015 per refit and 0.0003 per fold mean. Recomputed 0.00147 and 0.00029. **Match.**
- Matched at 2 s: +0.010 (4 of 4, t 2.83, corrected 1.86). At 8 s: +0.009 (3 of 4, t 2.25, corrected 1.47). **Match.**
- Under the budget, CoactDetect ahead by at least 0.014 (recomputed 0.0138), with no chorus net ahead in more than 1 of 4 folds. **Match.**
- binned SCE held to 8 s: 0.587 (recomputed 0.5867). **Match.**

**Section 8**
- Faintest events, busy background: 0.59 against 0.35, 4 of 4 folds. Quiet background: 0.81 against 0.72, CoactDetect ahead in 3 of 4. **Match.**
- chorus_norm minus CoactDetect by background: −0.014 quiet, +0.000 busy (recomputed +0.0002). **Match.**
- Distractors called: 84% to 100% (minimum 0.844). **Match.**
- Recall of 0.80 or more at the 30% and 18% levels: **mismatch** (finding 4).

**Section 9 and Table 3**
- Every crowded F1 range, starting-setting value, shipped value and pass count. **Match.**
- The reference used changes no verdict. **Match.**
- Merge gaps chosen: 8 s, 30 s, 8 s, 8 s, and 3 s for rate+context under the budget. **Match.**
- SPIKE-synch uses a fixed window in 4 of 4 budgeted folds. **Match.**
- CoactDetect over the budget on the held-out fold in 1 of 4 folds (fold 3). `over_budget` is computed on held-out items (code line 1623). **Match.**
- SPIKE-synch `max_gap` 2.0 and locust minimum distance 16 at the top of their grids. **Match.**

**Section 10**
- Tuned minus untuned: +0.005, −0.006, +0.032, +0.002 on F1 alone and −0.020, +0.009, +0.023, −0.035 under the budget; none larger than 0.04. **Match.**
- 2 of 210 distinct refits below 0.2 F1, scored 240 times; every other refit at least 0.51. **Match.**
- chorus_gain_norm, fold 3, seed 4: F1 0.125, at the bottom of the grid, with the failed-training flag. **Match.**
- tube, fold 1, seed 5: F1 0 with no calls, at threshold index 35 = 0.9983. **Match.**
- Replicate: 3 refits below 0.2 (seeds and folds as listed); its lowest other refit 0.388. **Match.**
- About 1% of refits failed. Recomputed 5/420 = 1.2%; the replicate actually has 215 distinct refits, which still gives 1.2%. **Match.**
- Chorus nets' probe rates under the budget: 0 to 17 per hour, median 1. **Match.** CoactDetect "8 to 12": finding 3. "106 per hour": finding 2.
- Refits over the budget: 4, 7, 3 and 11 of 20, with per-fold counts as listed; 80 refits in all. **Match.**
- The picker flags a bottom-of-grid threshold as "not an operating point": `train.py` warning. **Match.**

**Section 11 limits**
- Participation 19.05%, lower end 18.18% = 6/33. Source: bench_measured.json. **Match.**
- Contamination about 0.03% of events. Source: HANDOFF-slow-comodulation, decision 3. **Match.**
- Re-measurement inside the bootstrap intervals. Commit 2120516, which is not on main. **Match.**
- Cross-machine difference of about 0.02 per fold. Source: meta `gate1_reproduction`, largest 0.0212. **Match.**
- Goal 1 extended the gap to 16 s and the crowded check refused it; goal 1 found sliding mode better and able to keep its calls when a recording is shifted. Source: HANDOFF-coded-detectors.md, 2026-09-17 status lines. **Match.**

**Section 12 and the prior result**
- 1,963 jobs, all ok = 1 + 24 + 1,728 + 210. **Match.**
- 13.7 h of wall time (16:14:16 to 05:58:24). **Match.**
- 12.7 h training (`cpu_hours_training` 12.69). **Match.**
- `scores/` is 1.1 GB (1,155,847,313 bytes). **Match.**
- Darkroom `results/` holds `chosen/`, `fits.tar.gz`, `scores.tar.gz` and `run.log`. **Match.**
- PR #660 is open and adds `comparison.svg`. **Match.**
- Commit e8764aa, clean tree. **Match.**
- Calling `build_chorus_norm()` directly gives plain chorus: its `**cfg` falls through to `build_chorus(norm=False)`. **Match.**
- Earlier comparison: +0.103, three leaders, tube tied, CoactDetect tuned on one setting, simulator since retired. Source: learned-model-family.md, lines 61–65 and 138–139. **Match.**

**Not checked (no source in reach, left to the citation role):**
- The Cossart 2003 "interval reshuffling at P < 0.05" description. **Unverifiable here.**
- The bibliographic details of the other citations look correct as I know them but were not fetched. The CICADA DOI does match `docs/GLOSSARY.md`.

Scratch files: `%USERPROFILE%\AppData\Local\Temp\claude\c--Users-<user>-bugarach-bugarach\0c979457-501e-4b3d-9c4b-21e394823cf5\scratchpad\mb\r3-role-1\` (`text.txt`, `structure.txt`, `prev.html`). I edited nothing.
