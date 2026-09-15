GRANT 1 MISMATCH — missing Grep, Glob; holds Read, Bash (no forbidden editing tools)

This is a finding about the run, not about the note. Without Grep or Glob I searched with `grep` and `ls` through Bash. Without Write, the repo's heredoc hook blocked my scratch script, so every recomputation ran as inline `python -c` against the run outputs. I wrote nothing under the role01 scratch folder except the empty directory.

# Role 1 (Prove It): rigid-shift look note, round 1

**Summary.** Almost every number in the note matches the run outputs. I recomputed each from `results.json`: the retained shares match `destruction_table.json` to 1e-9, and the recording, mouse and window-pair counts match a fresh load of both export folders. The problems are in what the note says the numbers mean, and in claims taken from older documents:
- **The DI attribution is wrong.** The slow-stream leak is not "almost entirely" in DI.
- **The slow-stream window it recommends fails its own reference.** The upper bound at 11.2 s crosses 0.55, the same condition the note flags for Cossart at 5 s.
- **Two Cossart claims repeat statements the project later withdrew.**
- **The provenance pointers are stale.** The branch named in the header cannot produce Figures 5 and 6, and the darkroom copy (in Dropbox) is an older version of the note.

## Findings

| # | Location | Issue | Severity | Suggested fix | Verified against a source |
|---|---|---|---|---|---|
| 1 | Short answer, slow paragraph ("almost entirely in the DI group"), and the goal page ("mostly in DI") | By pair count, DI supplies **49 %** of the above-chance correct answers at 22.4 s and **56 %** at 44.8 s. MALE supplies 23 % and 38 %. Dropping DI leaves pooled accuracy at **0.531** and **0.535**. MALE reads 0.593 at 44.8 s, and the note's own Figure 3 bullet prints that. DI is only 10 mice and 17 slices, and its group accuracies have no interval. The recording-identity note also says group cannot be separated from imaging day, so "DI drift" cannot be told apart from a day effect. | major | Say "about half from DI (10 mice), with MALE also above chance at 44.8 s (0.59)". Add that group and imaging day are confounded (`docs/learned/recording_identity.md` lines 150–152). | yes |
| 2 | Short answer ("Up to about 11 s the shift hides (0.52)") and decision item 2 ("near 11 s, which hides") | At 11.2 s the upper bound is **0.5510 over mice** and **0.5524 over slices**, both at or above the signed 0.55 line. Refit over slices, the point estimate is 0.530, not 0.52. The Cossart reading flags exactly this condition at 5 s ("though its upper bound crosses 0.55"); the slow stream gets no such flag. | major | Report 11.2 s as "0.515, upper bound 0.551, crosses 0.55", or move the slow window to 5.6 s (upper bound 0.542, but 0.60 of large events kept). | yes |
| 3 | "The screen's review found that the destruction measure could not register removal on Cossart at its settings; with K scaled, the controls read 0 and 1, so here it can." | Two later reviews corrected this, so it is a withdrawn claim. Both Prove It reviews of the rigid-shift pre-registration found that at the screen's settings Cossart's controls did register removal: homogeneous resample −0.001 to 0.013, freeze-half 0.27–0.48, do-nothing 1.00. The real failure was saturation. The round-2 record says the measure "does register removal, contrary to the signed text". The note's contrast ("so here it can") rests on the withdrawn version. | major | Replace with: "at the screen's K every rigid-shift displacement was saturated; the controls read correctly there too". | yes (`docs/reviews/2026-09-14-preregistration-is-rigid-shift-usable-round2-roles/01-prove-it.md` line 53; round-1 roles `01-prove-it.md` lines 43 and 76) |
| 4 | Cossart setup ("With 566 ROIs a K of 3–8 would count chance coincidences") | This contradicts the project's measurement over all 59 recordings. The 2026-08-29 handoff says K=3 sits at 61 % of the peak excess ("off-peak by roughly half, not dead"; "Do not cite 'below where the statistic works'"), and Cossart's excess peaks at **K=12**. The scaled K (55–146) is 4.6–12 times that peak. The note's own later caveat ("small K on Cossart is not measured") half-admits this. | major | Drop the chance-coincidence rationale. State that K was scaled by field share (3/31 of 566, and so on), and that the project's measured Cossart K is 12, which this run did not test. | yes (`docs/handoffs/2026-08-29-the-transfer-experiment-and-two-things-i-corrected-myself-on.md` lines 26–31 and 100–101; `docs/learned/cossart_transfer/README.md` lines 8–13) |
| 5 | Header ("Baseline windows of the lab folder only.") and "Exploratory, run 2026-09-14 night" | The note now also covers the Cossart folder. Those runs read whole recordings, not baselines, and ran 2026-09-15 07:21–07:39. | major | Update the scope and dates. | yes (Cossart `meta.json`) |
| 6 | Header ("Code: … on branch `unsup/rule-as-code`") | `origin/unsup/rule-as-code` is at 36b64f5. Both tools there predate Cossart support (no role option, no K scaling), so that branch cannot produce Figures 5–6 or the current renders. The Cossart runner is on `main` (PR #581). The figure builder that drew these PNGs is at 616f124 on `unsup/rigid-shift-look-figures`. | major | Pin the commit that produced each run and render. | yes (git) |
| 7 | Header ("Results: `<darkroom>/bugarach/2026-09-15-rigid-shift-look/`") and the darkroom copy Tony reads | The darkroom `README.md` and `README.html` there have **no Cossart section** (0 mentions of Cossart; Figures 1–4 only). Its figures are the older renders, before the legend fix. The Cossart outputs went to a doubled path, `<darkroom>/bugarach/bugarach/2026-09-15-rigid-shift-look/cossart/`, while the board claims `bugarach/2026-09-15-rigid-shift-look/cossart/`. The run results there are byte-identical to the scratchpad runs. | major | Re-copy the note and all six current PNGs. Move the Cossart subfolder to the claimed path and fix the note's pointer. | yes (`ls` and `cmp` on the darkroom) |
| 8 | Figure 6 ("The homogeneous-resample control reads 0 and sits under the rigid-shift lines") | The code draws the controls **on top** (zorder 4, comment "so a control reading 0 is not hidden"). Commit 616f124 says so, and the rendered PNG shows the dark grey squares over the blue lines. | minor | "…is drawn over the rigid-shift lines at 0". | yes (figure viewed; builder lines 125–129) |
| 9 | "What this cannot say" ("an interface2 commit measured real fast onset jitter at about 1 s") | The source exists: interface2 f76e7b1b reports "onset jitter median 1.04 s (p90 1.53)" over 85 slices. But this repo's `docs/generator.md` gives the measured value as **0.36 s** and calls it "the least trustworthy number": its circular-shift null is 0.42 s, so the value mostly reflects the gather window, and "real tightness is unresolved". The best-case conclusion still holds, since both values are far above one frame (0.1 s). The number cited is the unqualified one. | minor | Name the commit, and say the jitter estimate is flagged soft (0.36–1.04 s, null ≈ measurement). | yes |
| 10 | Short answer ("removes 84–99 % of planted coordination") and the goal page | At 10 s and 20 s on the fast stream, retained ranges from 0.163 down to 0.000, so removal is 84–**100 %**. The 99 matches no defined subset. | minor | "84–100 %", or name the K range. | yes |
| 11 | Figure 2 caption ("5 s still keeps … 0.60 (slow, 2 s bin)") | The slow displacement is **5.6 s**. The value 0.603 is correct. | minor | "5.6 s on slow". | yes |
| 12 | Figure 1 caption ("against the control's −4.6 %") | Edge-thinning reads **−4.76 %** on fast and −4.56 % on slow. | minor | "−4.8 % fast, −4.6 % slow". | yes |
| 13 | What was measured ("typical ROI count (31)") | The median is 31.5; the runner truncates it with `int()`. | minor | "31 (median 31.5, truncated)". | yes (folder load) |
| 14 | Cossart setup ("each recording was read whole; the typical recording is 12,634 frames") | The window runs from frame 0 to one frame past the last onset, because the folder carries no duration. 12,634 is the median of that span (range 12,042–13,105), not a recording length. | minor | Say so in one clause. | yes (`meta.json` window source) |
| 15 | Figure 6 ("as in Figure 2") | Figure 2's caption says bars are 95 % over **20** twin pairs. Cossart has **10 twins and 10 draws** (lab: 20 and 20). | minor | State 10 twin pairs and 10 draws in the Figure 6 caption. | yes |
| 16 | Repo tables | `cossart/` has no `leak_count.json`, while the other two runs do. Figure 5's leak and count numbers have no table in the repo; they exist only in the scratchpad and the doubled-path darkroom folder. | minor | Add `cossart/leak_count.json`. | yes |
| 17 | Header ("Not murderboarded.") | Stale once this review lands. | minor | Update after adjudication. | yes |

## Claim ledger

Rows are numbers as quoted in the note. "Mouse" means the mouse-grouped value; slice values are given where they differ.

| Quoted value | Cited source | Recomputed value | Verdict |
|---|---|---|---|
| Fast 10–20 s accuracy 0.50, chance 0.50 | large run, leak | 0.4950 / 0.5047 (mouse); 0.4963 / 0.4933 (slice) | match |
| Removes 84–99 % (fast, 10–20 s) | large run, destruction | 83.7–100 % | mismatch (upper end) |
| Planned 1.6–5 s: large event keeps up to 87 % | full run | 0.870 (fast, 1.6 s, K=3, 50 %) | match |
| Slow up to about 11 s hides (0.52) | large run | 0.515 (mouse), 0.530 (slice); upper bounds 0.551 / 0.552 | point match; bound crosses 0.55 (finding 2) |
| Slow 2 s bin keeps 29 % | large run | 0.294 (11.2 s, K=3, 50 %) | match |
| Slow 22 s and beyond 0.55–0.56 | large run | 0.5486, 0.5633 | match |
| DI 0.62–0.68 | large run, by group | 0.618, 0.675 | match |
| "Almost entirely in DI" | large run, by group | DI share 49 % / 56 %; without DI 0.531 / 0.535 | mismatch |
| DI least stationary slow baselines | `recording_identity.md` line 161 | 0.73–0.76 vs 0.54–0.65 | match (but group = day confound) |
| 84 recordings, none skipped | full `meta.json`, export folder | 84 and 84; skipped [] | match |
| 1,501 window pairs, 44 mice | results; interior-window count from the folder | 1501; 44 | match |
| First and last windows dropped | `interior_windows` | `wins[1:-1]` | match |
| Offset within ±J per ROI | `surrogates.rigid_shift` | Elephant `dither_spike_train(shift=J)`, no wrap, drops what leaves | match |
| Per-ROI features pooled, no edge features | `feature_names`, `feature_mask` | 47 features, 10 edge features masked, 37 used | match |
| Edge features see coordination (the second review) | pre-registration round-2 review, line 35 | 0.58–0.62 vs 0.50, synthetic | match |
| Mouse and slice intervals almost identical | leak results | max bound difference 0.0097 (point estimates up to 0.015 apart, from different folds) | match |
| Uniform dither moves each onset independently | `uniform_dither` | per-onset `dither_spikes` | match |
| Twins: 31 ROIs, 20 % / 50 %, 20 pairs | `twin_shape`, meta | 31 (median 31.5), (0.2, 0.5), 20 | match (minor truncation) |
| 1 s bin (2 s slow), circular-shift null | `assess_coactivity` | `bin_width_sec`; `circular_shift_trains`; selection-corrected | match |
| K = ROIs co-active in one bin | assess line 571 | `obs >= K` | match (at least K) |
| Controls read 0 and 1 | full/large destruction | homogeneous −0.006 to 0.006; do-nothing 0.994–1.006 | match |
| One frame of planted jitter | `DESTRUCTION_JITTER_FRAMES` | 1 | match |
| Figure 1: thick bars 1.67–98.33 % over mice, thin over slices; dotted 0.5, dashed 0.55 | builder | same | match |
| Figure 1: rigid 0.49–0.52; dither 0.63–0.77 | full run | rigid 0.494–0.518; dither 0.632–0.767 (mouse) | match |
| Figure 1: counts at most 0.14 % | full run, count | max 0.142 % | match |
| Figure 1: control −4.6 % | full run, count | −4.76 % fast, −4.56 % slow | partial |
| Figure 2: bars 95 % over 20 twins | `_retained` | 2.5–97.5 % bootstrap over twins | match |
| Figure 2: K=3, 50 %: 1.6 s 0.87; 5 s 0.41 fast, 0.60 slow | full table | 0.870; 0.414; 0.603 (at 5.6 s) | value match, label (finding 11) |
| Figure 3: fast 0.49–0.51 to 40 s | large run | 0.489–0.506 | match |
| Figure 3: slow 0.549 / 0.563, lower bounds 0.509 / 0.510 | large run | 0.5486 / 0.5633; 0.5094 / 0.5105 | match |
| Figure 3: DI 0.675, MALE 0.593, ORX 0.506, OVX 0.507 | large run | 0.6748, 0.5931, 0.5056, 0.5070 | match |
| Figure 3: counts within 0.4 % | large run | max point 0.362 % (bars to −0.75 %) | match (point) |
| Figure 4: fast 0.41 → 0.16 → 0.07 → 0.04 | large table | 0.414, 0.163, 0.074, 0.040 | match |
| Figure 4: slow 2 s 0.60 → 0.29 → 0.13 → 0.07 | large table | 0.603, 0.294, 0.128, 0.067 | match |
| Cossart: 59 recordings, 32 mice, 1,257 pairs | Cossart meta, results, folder | 59, 32, 1257 | match |
| 12,634 frames, 0.118 s, about 25 min | `twin_shape`, folder | 12634 (median span), 0.11792 s, 24.8 min | match (span, not length) |
| 566 ROIs; K 55 / 73 / 110 / 146; 10 twins; J 1.6–40 s | `k_scan`, meta | 566; round(k/31·566) gives the same; 10; same | match |
| "K 3–8 would count chance coincidences" | none cited | handoff: K=3 at 61 % of peak, peak K=12 | contradicted |
| Figure 5: 0.49 at 1.6 s, 0.52 at 5 s, range 0.48–0.58 | Cossart leak | 0.4916; 0.5179 [0.4764, 0.5751] | match |
| Figure 5: 0.58 / 0.59 / 0.60, lower bounds 0.53–0.56 | Cossart leak | 0.5807 / 0.5863 / 0.6038; 0.5273–0.5557 | match |
| Figure 5: dither 0.98–0.99; slices match mice | Cossart leak | 0.9833–0.9912; max bound difference 0.006 | match |
| Figure 5: counts within 0.11 %, control −4.5 % | Cossart count | max 0.113 %; −4.47 % | match |
| Figure 6: K=146 at 20 % holds 113 ROIs, no point | Cossart table | 0.2·566 = 113.2; before_mean 0, retained NaN | match |
| Figure 6: from 5 s removes all; 1.6 s at 50 %: 0.87 (K=55), 0.79 (K=73) | Cossart table | all 0.000; 0.869, 0.785 | match |
| Figure 6: control "sits under" rigid lines | builder, PNG | drawn on top (zorder 4) | mismatch |
| Cossart 5 s upper bound crosses 0.55 | Cossart leak | 0.5751 | match |
| Event in 283 ROIs, ±5 s over 10 s, about 28 per bin < 55 | arithmetic | 283/10 = 28.3 | match |
| Screen review: Cossart destruction cannot register removal | `report_steps_excluded_2026-09-11.md` line 24 | later corrected: controls did register removal; saturation was the cause | withdrawn claim repeated |
| Interface2 fast onset jitter about 1 s | interface2 f76e7b1b | 1.04 s median; this repo's `generator.md` says 0.36 s and flags the measure as soft | source match, caveat missing |
| Thresholds 0.55, ±2 %, 0.25 signed | pre-registration lines 90, 107, 123, 186 | same, "agreed. signed" | match |
| Same recordings as the screen | screen `meta.json` folder | same 2026-09-03 STEPS_EXCLUDED export | match |
| Follow-up displacements chosen after the first run | meta timestamps, git | full run ended 21:27; `--J` flags committed 21:30 | match |
| Code on `unsup/rule-as-code` | git | branch at 36b64f5, without Cossart or render fix | mismatch |
| Results at `<darkroom>/bugarach/2026-09-15-rigid-shift-look/` | darkroom | lab runs there; note there lacks Cossart; Cossart outputs at a doubled path | partial |

## Group membership and the older artifact

- **Group membership record.** The group column comes from the export folder, which is this project's source of record under the house rule that the export folder is the input. It has no blank labels: DI, MALE, ORX and OVX cover all 1,501 pairs. By group (slices / mice): MALE 22 / 12, ORX 25 / 12, OVX 20 / 10, DI 17 / 10. 84 slices come from 44 mice, and the mouse-resampled interval accounts for slices that share a mouse. Withdrawn recordings are absent from the folder by producer contract. The confound in finding 1 comes from the recording-identity record, which says group is nested in imaging day.
- **Compared against the older artifact.** All three `destruction_table.json` files in the repo are byte-identical to the scratchpad re-renders. Commit 616f124 changed only the PNGs. The darkroom copy is the older version that finding 7 describes.

Files referenced:
- <worktree>/docs/learned/rigid_shift_look/README.md
- <worktree>/tools/look_rigid_shift.py
- <worktree>/tools/make_rigid_shift_look_figure.py
- <worktree>/docs/learned/recording_identity.md
- <worktree>/docs/reviews/2026-09-14-preregistration-is-rigid-shift-usable-round2-roles/01-prove-it.md
- <worktree>/docs/handoffs/2026-08-29-the-transfer-experiment-and-two-things-i-corrected-myself-on.md
- <worktree>/docs/generator.md
- <worktree>/docs/goals/unsupervised-learning.md (line 54 repeats the claims in findings 1 and 10)
