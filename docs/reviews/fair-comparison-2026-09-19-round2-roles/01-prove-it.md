<!-- Verbatim role report, except that this machine's absolute paths are written as %USERPROFILE% and <darkroom> (the repository is public). The unedited original is in <darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-roles-round2/. -->

GRANT 1 ok — Read, Grep, Glob, Bash

# Role 1 (Prove It): findings on report.html (git hash-object 16ac704, the same as HEAD c261f9c and the darkroom index.html)

I recomputed Table 2 and Table 3 and the section 4.5, section 6 and section 8 numbers from results.json, merge_gap.json, crowded_check.json, fold_draws.json, meta.json, ran.json and progress.json. I recomputed the replicate from the raw WSMIP065 results.json and meta.json in the darkroom. I re-simulated Figure 1's recording (seed 1000, busy background) and the 24 crowded recordings, and re-scored CoactDetect's and LoCo's shipped defaults on the crowded recordings. I also read the code that ran: `_heldout`, `budgets`, `within`, `fold_check`, the coded search call, the nets and `score_detections`.

**One thing changed while I was reviewing.** `crowded_check.json` (09:37) and `tools/crowded_check_fair_comparison.py` (09:34) now have uncommitted edits in the fair-comparison-report worktree. The committed version (08:02) is the one the page was built from at 09:16, and it is the one I checked. See m7.

## Findings

Columns: location · issue · severity · suggested fix · verified against a source (yes/no)

| # | location | issue | sev | fix | verified |
|---|---|---|---|---|---|
| M1 | §6 "Refits below 0.2 F1", the tube entry (also §7 "picks its threshold on 2") | The page says tube's F1 0.000 came "at a threshold picked on two recordings". **That is false.** Under the budget, all 5 refits use the threshold the selection chose on the inner loop: index 35 (0.99831), the same for every seed, chosen over 3 training seeds × 3 inner rotations with 131 admissible settings. The results.json per_seed threshold_index is [35,35,35,35,35]. `_heldout` passes `sel["threshold_index"]` when the selection is under the budget. Only choices on F1 alone use `own_index`, which is picked on 2 recordings. | major | "It made no calls at all at the single threshold its selection chose on the training folds (0.9983), applied to all five refits." In §7, say the 2-recording threshold applies to choices on F1 alone. | yes |
| M2 | §4.5 "A wide merge gap therefore loses nothing" | **Figure 5's own net curves refute this.** On F1 alone, line_length falls from 0.705 at 2 s to 0.660 at 8 s, and tube from 0.631 to 0.615. The cause is refits whose threshold sits at or near the bottom of the grid (line_length folds 3 and 4, seed 3 of 5, at 1e-4; tube fold 2, seed 2 of 5, at 1.76e-4). They call almost continuously, merging fuses those calls, and `score_detections` matches calls to events one-to-one. The coded curves do rise monotonically. | major | Limit the claim to the coded detectors and to nets that call discretely. Note that line_length and tube fall. | yes |
| M3 | §3, the paragraph on architecture drawings (HTML line 117) | `<darkroom>` is not escaped there (every other occurrence is `&lt;darkroom&gt;`). The browser drops it, so readers see "/bugarach/2026-09-19-comparison-architectures/index.html". **That folder also does not exist** under `<darkroom>/bugarach/` on this machine. PR #660 does exist, is open, and contains comparison.svg. | major | Escape the path. Either publish the page or remove the pointer. | yes |
| M4 | §4.1 "Settings that break the context-window rule in section 4.5 were skipped" | **Dangling reference.** §4.5 is about the merge gap and states no context-window rule, and no other part of the page states it. The rule (`context_fits_the_null`: context ≤ 120 s planted spacing) removed the 240 s context from CoactDetect's and rate+context's grids and 240 s and 480 s from LoCo's. | major | State the rule and its reason where it is cited, for example in §4.1 or §4.5. | yes |
| m1 | §6 and Table 2, corrected t | The text says each t is "multiplied by 0.65". The values actually use √(3/7) = 0.6547. **Seven of 17 corrected values differ in the last digit** from ×0.65: tube −11.5 (×0.65 gives −11.4), LoCo −9.1 (−9.0), locust −6.3 (−6.2), rate+context −9.4 (−9.3), LoCo under the budget −15.4 (−15.3), SPIKE-synch under the budget −44.2 (−43.9), rate+context under the budget −24.5 (−24.3). | minor | Say "multiplied by 0.655 (√(3/7))". | yes |
| m2 | §4.5 "the nets within 0.001 F1" | The largest per-refit reproduction error is **0.00147** (tube, under the budget, fold 2, seed 1 of 5). | minor | Say "within 0.0015", or "within 0.001 on every fold mean", which is true. | yes |
| m3 | §6 "every other refit scored at least 0.51" | The lowest refit is **0.5095** (tube, under the budget, fold 4, seed 3 of 5). | minor | Say "above 0.50". | yes |
| m4 | §4.5 "every coded choice was rescored" | merge_gap.json rescored only CoactDetect, binned SCE and LoCo (`GAP_KEY` in fair_comparison_evidence.py). rate+context has a merge gap (`merge_gap_s`) and chose 8 s, the top of its grid, on F1 alone, but was not rescored. | minor | Name the three detectors, or add rate+context. | yes |
| m5 | §7 "For the merge gap, that is every coded detector with one", and Table 3 "no merge setting" | rate+context under the budget chose 3 s, not the top of its grid. SPIKE-synch's `max_gap`, which carries an event across gaps, sits at the top of its grid (2.0 s, edge flag "high") in every F1-alone choice. locust's `sce_min_distance_frames` sits at the top (16) in every F1-alone choice. | minor | Qualify with "on F1 alone". Mention the two merge-like settings. | yes |
| m6 | §7 "how far they would move is unmeasured" | meta.json `gate1_reproduction` records per-fold differences between the Mac and this machine: tube −0.0034 to −0.0212, chorus_gain_norm at seed 0 as far as −0.057. The measurement is confounded by the Mac's uncommitted changes. These are the same size as the page's 0.007–0.010 margins. | minor | Say "measured only confounded (meta.json gate1_reproduction): up to 0.02 per fold for tube". | yes |
| m7 | §4.5 "Scored against those [shipped defaults], no verdict changes" | Nothing committed backed this sentence at build time: the committed crowded_check.json has one reference only. **I re-scored the shipped defaults on the crowded recordings:** CoactDetect 0.8077, LoCo 0.8165. Every verdict is unchanged; LoCo under the budget, at 0.771, still fails. The uncommitted crowded_check.json now has the same numbers. | minor | Commit the updated crowded_check.json and tool, rebuild, and cite the file. | yes (recomputed) |
| m8 | Provenance line | docs/reviews/fair-comparison-2026-09-19.md does not exist yet. | minor | Make sure it lands before shipping. | yes |
| m9 | §3 "untuned, it scores 0.629 against CoactDetect's 0.748" | The untuned tube 0.629 is correct, but 0.748 is the tuned (nested cross-validation) CoactDetect. The reference CoactDetect's held-out F1 is not reported anywhere. | minor | Say "against the tuned CoactDetect's 0.748". | yes |
| m10 | §4.4 "firing no more than CoactDetect does" | This contradicts the 1.6× margin stated two sentences later. | minor | "no more than 1.6 times as often as CoactDetect". | yes |
| m11 | §6 "Exceeding the budget can only help a net's F1" | Calls in the probe and on the null recordings do not enter F1. An over-budget threshold usually raises F1, but not necessarily. | minor | Say "tends to help". | yes (score.py) |
| m12 | §4.5 and §6 "these curves bound what tuning the gap could do" | This is not a bound: re-tuning the gap jointly with the other settings could beat these curves. | minor | Say "indicate" rather than "bound". | no (a reasoning claim) |
| m13 | Table 1, SPIKE-synch "coincidence window set by the local gaps" | That is its default mode (`isi_adaptive`). All 4 of its choices under the budget switched to `tau_mode` "fixed" (0.25 s). | minor | Optional footnote. | yes |
| u1 | §7 "because the project lead's brief for this report asked for exactly that" | No source in the repo records the brief. On its face this is in tension with CLAUDE.md "A known contamination stops the work. It does not become a caveat." HANDOFF-workstation-tuning (2120516) records "Consequences for goal 2: none", since the simulation does not read the folder. | ⚠ flag for the main thread | Cite where the brief lives. | no |

## Claim ledger

Columns: quoted value · cited source · recomputed value · result

- Earlier lead +0.103 (untuned nets, CoactDetect tuned on one knob, home spec now retired) · learned-model-family.md:62,138 · +0.103 · **match**
- Tube tied earlier; three nets led · same, :139 · tube +0.000; chorus_norm, chorus_gain_norm, line_length +0.103/+0.084/+0.052 · **match**
- Best net vs CoactDetect at the chosen settings: −0.007 · results.json comparisons · −0.00690 · **match**
- Matched at 2 s: +0.010, ahead in 4 of 4 folds · merge_gap.json · +0.0096, 4/4 · **match**
- Matched at 8 s: +0.009, ahead in 3 of 4 folds · merge_gap.json · +0.0091, 3/4 · **match**
- "within 0.010 F1" · derived · max 0.0096 · **match**
- Replicate: no net ahead at the chosen settings · raw WSMIP065 results.json · net minus CoactDetect: F1 alone −0.057/−0.102/−0.029/−0.039; under the budget −0.092/−0.132/−0.025/−0.053 · **match**
- Replicate summary copied faithfully · replicate_summary vs raw · identical per fold · **match**
- Replicate seeds 2000–2047; everything else held fixed · declarations diffed · only recording_seeds and replicate differ; same GPU model and torch version · **match**
- Figure 1 facts: seed 1000, busy background, window 15m40s–26m, event at 16m33s, 6 ROIs, 18% participation, SD 0.36 s, 2 distractors, 2,595 events · re-simulated with bench.make_recording · 993.33 s, n_part 6, frac 0.18, distractors at 1034.4 and 1091.8 s, 2,595 events · **match**
- Probe: extra 0.06/s, ≈12× quiet and 3× busy, from 20m for 5 min, 30 s ramp · simulate.py:776, meta · 11.5×, 3.16×, window 1200–1500 s · **match**
- Recording layout: 45 min, 33 ROIs, 15 events at 5/5/5 and 30/18/10%, ≥120 s apart, 6 distractors · meta bench_recording · same · **match**
- Backgrounds 0.0052/0.019 are the p25/p75 of real baseline rates · bench.py:640 · same · **match**
- Hit tolerance 2.5 s is where scores plateau · score.py TOL_SEC docstring · CoactDetect and LoCo plateau at 2.5 s, rate+context at 2.0 s · **match** (measured on the coded detectors only)
- Distractor calls count against precision; probe calls are kept out of precision · score.py:44–51, bench.py:1136 · same · **match**
- 96 + 96 recordings · meta · 48 seeds × 2, null twins at seed+100000 · **match**
- Table 1 settings and grid values: 10/49, 7/39, 10/46, 4/19, 10/46, 10/47; nets 5/6/5/5 · meta hand_axes and learned_axes · same · **match**
- Net grids: lr 0.003/0.01/0.03; steps 900/1,800/3,600; 3 or 4 architecture settings; untuned configuration among the 24 · meta, configs · same; untuned key is last in each list · **match**
- Table 1 descriptions of the nets · nets/chorus.py, line.py, tube.py · consistent · **match**
- `build_chorus_norm()` built directly gives plain chorus · chorus_norm.py and registry `make` · cfg={} gives norm=False · **match**
- Table 2, every mean F1, every minus-CoactDetect difference and every t (34 cells) · results.json · all within rounding · **match**. Corrected t: see m1.
- Tuned minus untuned per fold and mean (4 nets) · comparisons tuned − untuned · all · **match**
- Over-budget refits under the budget: 4/7/3/11 of 20, per-fold splits · seeds_over_budget · same · **match**
- CoactDetect over budget on held-out in 1 of 4 folds · results.json hand coact gated · fold 3 True · **match**
- CoactDetect chose the same settings both ways · config_key per fold · identical · **match**
- CoactDetect passes the crowded check 8/8; binned SCE fails 7/8 (fold 4 under the budget passes, drop 0.012 against a 0.02 limit) · crowded_check.json (committed) · same · **match**
- Table 3: every range, reference and pass count (12 rows) · crowded_check.json · all · **match**
- Table 3 chosen merge gaps (8/8/30/30/8/8/8 and 3 s) · results.json chosen_params and meta grids · same · **match**
- locust: the budget refused every setting in 4/4 folds and the search returned its start · selections/gated/outer*/cicada.json · 16 scored, 16 refused, 0 moves · **match**
- 4 coded detectors have no admissible result under the budget in any fold · derived · LoCo, SPIKE-synch, rate+context, locust · **match**
- binned SCE held to 8 s scores 0.587 · merge_gap.json · 0.5867 · **match**
- CoactDetect by merge gap: 0.731 at 2 s, 0.748 at 8 s, 0.803 at 30 s · merge_gap.json · 0.7315, 0.7480, 0.8027 · **match**
- chorus_norm by merge gap: 0.741 at 2 s, 0.775 at 16 s · merge_gap.json · 0.7411, 0.7749 · **match**
- Coded detectors reproduce the run exactly · merge_gap.json reproduces_run · 0.0 · **match**
- Nets reproduce the run within 0.001 · merge_gap.json · max 0.00147 · **mismatch** (m2)
- Crowded set: 24 recordings, 180 events each, min spacing 6 s, median 43 s · re-simulated with make_tail_recording · 24, 180, 6.001 s, 43.3 s · **match**
- 0.02 margin not signed · bench.py MAX_CROWDED_DROP docstring · "Tony has not signed" · **match**
- Run's own search did not apply the crowded check · tune_learned_vs_coact.py:725 · only budget and validity checks · **match**
- Budget 1.6× the reference; floor never binds · meta budgets, `budgets()` · ratios 1.6; floors 0.33/h and 0.037/h · **match**
- Shipped-defaults verdicts unchanged · no committed source; re-scored · CoactDetect 0.8077, LoCo 0.8165 · **match** (m7)
- Goal 1's settings: alpha 1e-05, context 120 s, merge gap 8 s, guard 1 s; LoCo 99.9 and 8 s · meta coded_base, reference · same · **match**
- Goal 1: sliding is better held out and keeps calls under shifts; defaults still binned · goal page:78, HANDOFF-coded-detectors:305, bench.py:532 · same · **match**
- Fold defect: 3 folds share seeds 1000–1004; 2 distinct fitting sets before the fix, 4 after · fold_draws.json and a raw fit record · same; raw outer0 record matches · **match**
- The run refuses to start on shared draws · fold_check, main() · SystemExit · **match**
- Low refits: chorus_gain_norm fold 3 seed 4 of 5 at 0.125 (precision 1.0, recall 0.067, failed-training signature); tube fold 1 seed 5 of 5 at 0.000 · results.json · same · **match**; tube's mechanism is wrong (M1)
- 210 refits, of which 2 below 0.2 · ran.json outer stages, distinct keys · 40+55+60+55 = 210 · **match**
- Every other refit ≥ 0.51 · results.json · 0.5095 · **mismatch** (m3)
- 1,963 jobs, no errors; 1 + 24 + 1,728 + 210 · ran.json · 1,963 ok · **match**
- 13.7 h of wall time · meta started, progress at · 13.73 h · **match**
- 12.7 h spent training · results cpu_hours_training · 12.69 · **match**
- Code at e8764aa from a clean tree · meta started.git · dirty false · **match**
- Participation 0.18 against 0.1905 (lower bound 0.1818 = 6/33) · bench_measured.json, bench.py docstring · same; "inside": false · **match**
- 0.03% of events · HANDOFF-slow-comodulation decision 3 · same · **match**
- Re-measured on both workstations; moves inside the bootstrap interval; commit 2120516 not on main · HANDOFF-workstation-tuning:840–857, git · same; not an ancestor of origin/main · **match**
- Scores 1.1 GB unpacked; darkroom holds the summaries unedited; repo copies redacted · runs/…/scores, cmp · 1.1G; results.json and ran.json identical; meta.json differs only in the redacted paths · **match**
- Citations (Grün 2002, Cossart 2003, Denis 2020, Kreuz 2015, Finn & Johnson 1968; Nadeau & Bengio 2003, Mach Learn 52:239–281; t critical ≈ 3.2) · README §Licensing · consistent; t(0.975, 3) = 3.18 · **match**
- Architecture drawings location · darkroom · folder absent · **unverifiable** (M3)
- Review record · docs/reviews · absent · **unverifiable** (m8)
- Brief asked for the contamination to be stated as a limit · none found · **unverifiable** (u1)

## Record of design and unit membership (checked, not assumed)

- **Where membership is recorded:** meta.json (`recording_seeds`, `folds`, `seeds_per_fold`, `budgets[h].recordings` and `twin_seeds`), with fold_draws.json and the per-fit run.json records for the draws.
- **Nothing is counted as independent that isn't:** each seed's quiet and busy recordings are always in the same fold, and each null twin (seed+100000) stays in its seed's fold. The t statistics pair over folds, not recordings.
- **No seed overlap:** this run's 1000–1047, the replicate's 2000–2047, the crowded set's 1–12 and goal 1's 1–96 (which set the reference values) do not overlap. So nothing chosen before the run saw its held-out recordings.
- **Nothing is missing:** the only NaN F1 is the tube refit with no calls (counted as 0, and disclosed). No coded choice is null, and no chosen parameter is NaN.
- **Withdrawn units:** none apply; the recordings are simulated. The real data behind the simulation's fitted settings is steps_excluded, which carries the uncleared contamination the page discloses (see u1).

## Regeneration diff against the previous version (805fee9)

The only numbers that disappeared are locust's old result under the budget (0.549, −0.199, t −37.5), now "no admissible setting", which the selection files support, and the job-log figures, now restated. Table 2 still has 10 rows. Everything else is added content.

## Files

- Artifact: %USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\report.html
- Uncommitted changes noticed mid-review: …\fair_comparison_2026_09_18\crowded_check.json and %USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\tools\crowded_check_fair_comparison.py
- Source of M1: %USERPROFILE%\bugarach\bugarach-worktrees\tune-bench-comparison\tools\tune_learned_vs_coact.py (`_heldout`, lines 1545–1566) and …\selections\gated\outer0\tube.json
- Scratch: %USERPROFILE%\AppData\Local\Temp\claude\c--Users-<user>-bugarach-bugarach\0c979457-501e-4b3d-9c4b-21e394823cf5\scratchpad\mb\r2-role-1\ (report.txt, prev.html)
