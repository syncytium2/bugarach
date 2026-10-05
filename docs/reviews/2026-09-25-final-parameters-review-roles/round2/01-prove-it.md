GRANT 1 ok — Read, Grep, Glob, Bash

# Role 1 (Prove It): claim ledger and findings

**Artifact:** `docs/learned/runs/2026-09-25-final-parameters/README.md` in the worktree `floor-and-grids`, with its figures, `adoption.json` and `adoption_table.md`. I made no edits.

## Overall

Most of the numbers are right. I recomputed them independently from the raw run records, and they match. There are **3 major findings** and **10 minor ones**, listed at the end. Nothing is blocking.

- **Tables match their sources.** I re-ran `tools/make_final_parameters_report.py --night <darkroom night folder> --out <scratch>`. The output `adoption_table.md` is byte-identical to the repo copy, and `adoption.json` is identical once keys are sorted. The README's three tables match it.
- **The darkroom copy matches the repo copy.** `<darkroom>/.../report/README.md` and `adoption.json` are identical to the repo's. Figures 3 and 4 are byte-identical to `065/report-inputs/`.
- **The fast search files are exact copies.** Every file in `064/phase2/by-detector/search-fast-<det>/search.json` is byte-identical to its original in `search-fast-rest` or `search-fast-sync`.
- **Compared with the previous version** of `adoption_table.md` (commit 8bc02ad): same 24 rows and the same values. What changed is added `window_mode` changes, confidence intervals, a split budget table, and a selection-seed fail for slow locust's shipped point. Every difference is accounted for.
- **The review's close-events re-run (0.0165) reproduces.** I scored fast CoactDetect on the crowded (close-events) recordings, held-out seeds 49–60, both backgrounds:
  - binned shipped point: 0.97203; sliding start point: 0.99965; proposal: 0.95552.
  - Proposal minus binned: **−0.0165**. Proposal minus sliding: **−0.04414**, which matches the search record's −0.04413506 exactly, so the method is sound.
- **Design record and group membership.** The real-data run reads the export folder `senktide_ttx` (`2026-09-23_revised_2v_long_senktide_ttx_STEPS_AND_PINS_EXCLUDED`). That matches the `default` in `current_export.toml`, and `results.json` stamps 66 recordings with groups in DI, OVX, MALE, ORX order. Under the repository's contract, the export folder is the record: withdrawals are already applied. The treatment-window count reconciles to 128 (the sum of the per-group counts in each stream table). ADR-0008 says the 66 recordings come from 36 mice. The section is descriptive only (per-cell counts and medians), so it makes no claim that recordings are independent. No finding.

## Claim ledger

Shorthand used below:
- **cand** = `064/phase3/candidates.json` (fast) or `065/phase3/candidates.json` (slow and combined), with `results[...]`.
- **search** = `search.json`, `held_out` block.
- **sel** = `064/phase3-3x3/selection_budgets.json`.
- **xs** = `064/phase3-3x3/cross_stream.json`.
- **bf** = `065/bench-floor/bench_floor.json`.

"Match" means I recomputed the value from the source, not just read it.

| # | Quoted value | Source | Recomputed | Verdict |
|---|---|---|---|---|
| 1 | Fast binned SCE: `bin_width` 10→2, merge none→10, gain +0.060 [+0.046, +0.077], fresh 0.747 [0.729, 0.765] → 0.785 [0.769, 0.802] | search, cand, xs | same | match |
| 2 | Combined binned SCE: `threshold_pctile` 98→99, +0.015 [+0.006, +0.024], 0.748 [0.731, 0.763] → 0.764 [0.748, 0.781] | same | same | match |
| 3 | Combined rate+context: 4.5→6 Hz, merge 8→16, +0.093 [+0.076, +0.113], 0.683 [0.642, 0.726] → 0.773 [0.748, 0.793] | same | same | match |
| 4 | Combined SPIKE-synch: `C_threshold` 0.08→0.1, `tau_mode` changed, +0.029 [+0.016, +0.043], 0.761 [0.734, 0.782] → 0.782 [0.768, 0.794] | same | same | match |
| 5 | Held-out gain is a bootstrap median with 400 resamples; proposal = best held-out candidate whose interval is above zero | `search_all_settings.py` lines 110 and 755–758; `score_bench_candidates.proposal()` | same | match |
| 6 | Combined SCE: another candidate led on selection seeds by 0.0003 | search `selection`: pair 0.751934, rounds 0.751619 | 0.000315 | match |
| 7 | Fresh seeds: rate+context intervals "barely touch" | [0.642, 0.726] vs [0.748, 0.793] | gap of 0.022; they do not touch | **mismatch** (F1) |
| 8 | Fast SCE intervals do not overlap; combined SCE and SPIKE-synch intervals overlap | xs | same | match |
| 9 | Combined rate+context proposal: 1.28 calls/h outside the stretch, busy background, held-out; limit 1/h | search `elevated_out_busy` 1.28125; `bench_combined` rate limit 1.0 | same. The fresh value is 1.38 | match (F8) |
| 10 | `bench_combined.py` says the ceilings are "the thing to look at before any of these is trusted" | `bench_combined.py` lines 329–330 | present (split across a line break) | match |
| 11 | The proposals pass combined's elevated-rate ceilings "by wide margins" | fresh calls per minute inside the stretch: SCE 5.75 of 10, rate 1.32 of 8, SPIKE-synch 0.20 of 16 | SCE is at 57% of its ceiling, unchanged from the shipped point | partial (F9) |
| 12 | Decision 2: five held-out gains and the settings at their limits; "moved there from 5"; fast locust shipped at 1 | search, bracketing `only_at_limits`=true for all five | same | match. Slow locust is also shipped at 1 (F12) |
| 13 | Each of the five passes every checked budget; "nine" adoptable if a limit counts | budgets recomputed; `adoption.json` loose list has 9 rows | 9 | match |
| 14 | Decision 3: 0.181·—·0.148; 0.181·—·0.175; 7.24·6.85·7.23; 0.245·—·0.257; limits 0.10 / 0.10 / 4.0 / 0.15 | sel; search held-out probe 6.854/min; cand; `bench*.py` | same | match |
| 15 | Fast rate+context and SPIKE-synch measured a swing near 0.01 before the floor | `bench.py` 2085–2086 "measured: 0.01" | same | match |
| 16 | The diagnosis found every candidate inadmissible, "not a bug" | `DIAGNOSIS-sync-and-rate-moved-nothing.md` | same | match |
| 17 | `alpha` 1e-4 → 1.4e-9 (fast), 1e-5 → 1.4e-9 (combined); alpha alone gained +0.031 / +0.013 on selection; held-out +0.055 [+0.036, +0.075], +0.039 [+0.026, +0.056] | round histories 0.80014−0.76907 and 0.79074−0.77787 | 0.0311, 0.0129 | match |
| 18 | Combined CoactDetect sits at 120 s, the bench's longest; the bracketing record does not flag it | params; ADR-0009 R5; `valid()` / `context_fits_the_null` | the grid was extended to 240 s and then rejected as invalid | match (nuance in F13) |
| 19 | Fast CoactDetect close-events: −0.044 against sliding, −0.0165 against binned | search; my re-run | −0.04414, −0.01651 | match |
| 20 | LoCo context extended to 10 s and 5 s on fast and combined; fast first move to 5 s; final proposal at 20 s from the pair grid | rounds grids and history | same (fast also lists 2.5 s, which the `bin_width` rule makes invalid) | match |
| 21 | Fast LoCo `threshold_pctile`: 6 extensions, all downward (94→1); upper end 99.99 never extended | search space 97–99.99, grid adds 94/88/76/52/4/1 | same | match |
| 22 | The guard cap never reached LoCo; this fix is in `bench.settings_are_valid` with a test | `git show b6e40f0:src/bugarach/bench.py`; the 79efeda diff; `tests/test_bench_floor.py` | same | match |
| 23 | "the slow and combined LoCo searches did walk the 8 s guard at 20 s and 30 s contexts" | round histories: slow and combined LoCo never moved `context_win_sec` off 120; the pair grid holds guard at 0 | not supported. Over-cap guards were reachable only on **fast** LoCo (context 5 s, guards 2 and 4 s, cap 1.25 s) | **mismatch** (F4) |
| 24 | "No proposal uses a nonzero guard" | combined CoactDetect proposal `guard_sec` 8; combined rate+context proposal 4 | false as written; true for LoCo | **mismatch** (F5) |
| 25 | Decision 7 / Table 3: floors 5–6, 6–8, 6–7, 7–10, 7–8 and all under-floor counts; participants 3/6/10, 7/12/20, 4/8/13 | cand under_floor (the same for every detector row); `make_recording` on seeds 1 and 6000 | same | match |
| 26 | Figure 4: "25 of 40, 20 of 40 and 15 of 40 for the last three rows" | bf: fast busy middle 25/40, combined busy middle 20/40, slow busy lowest 15/40 | these are rows 2, 4 and 5; row 3 (combined quiet) is 40/40 | **mismatch** (F6) |
| 27 | Figure 4: 8 "other" seeds | bf seeds are 1–8 | a subset of the selection seeds | partial (F10) |
| 28 | A planted recording's floor sits about 1 ROI above the no-coordination floor | bf: fast 5–6 vs 4–5; combined 6–7 vs 5–6; **slow 6–7 vs 3–4** | slow is about +3 | **mismatch** (F7) |
| 29 | Decision 8 rows: 0.820 [0.806, 0.838] vs 0.794 [0.779, 0.809]; 0.865 [0.855, 0.874] vs 0.834 [0.825, 0.843]; 0.827 vs 0.809 | xs | same | match. Rows 1 and 3 overlap (F11); table incomplete (F3) |
| 30 | The slow bench is easier "for almost every detector" | xs columns | true except fast-tuned SPIKE-synch (0.744 on slow, 0.792 on fast) | match |
| 31 | Slow binned SCE close-events −0.0207 held-out, −0.0198 selection; 12 recordings per background; allowance "still unsigned" | search, sel (−0.01978), `N_TAIL`=12; `bench_slow.py` line 332 | same | match |
| 32 | Slow chorus_norm: 1.43 calls/min inside the stretch vs CoactDetect's slow limit 1.0 | chorus candidates seed 3: quiet 1.433 | same | match |
| 33 | Floor definition: larger of 3 and the chance level reached at most once per hour, J = 20 s, 1,000 draws, 2 s window; split-half stability shown only in bench-floor | ADR-0008 58–67; `event_floor.MIN_DRAWS`; bf `first_half` / `second_half` | same | match |
| 34 | SPIKE-synch `min_n` sums coincident onsets over a call's bins | `detectors/sync.py` 61, 326, 366 | same | match |
| 35 | Hits are matched within 2.5 s | `score.TOL_SEC` = 2.5 | same | match |
| 36 | Close-events recordings put events as little as 6 s apart | `min_sep_sec=6.0` in all three benches | same | match |
| 37 | Elevated-rate recording: 45 min, a 5 min stretch, 12 recordings per background, seeds 66000–66011 | `duration_sec` 2700, `hot_window` 1200–1500, cand `elevated_rate_seeds` | same | match. Rate wording is off (F10b) |
| 38 | Real data: 66 recordings, 128 × 3 × 8 = 3,072 cells, 2,696 floors differ, 498 flips, OVX +17 and ORX +20 on fast senktide | `phase3-real-v3/floor_flips.txt`, `RUN.md`, `results.json` | same | match |
| 39 | v3 supersedes v2, "where locust was left unseeded" | `RUN.md` and `real_data.md`: "locust **and SCE** unseeded" | incomplete | minor (F12b) |
| 40 | What ran: b6e40f0, a70b185 (#811), 7af68c9, "723f1e6 (#812)", #814 unmerged | git log; RUN files | 723f1e6 is the merge commit of **#813** (#812 is 1ad2654) | minor (F14) |
| 41 | The 3 × 3 diagonal reproduces for 38 of 38 versions | xs `diagonal_check.all_reproduce` true; `RUN.md` | same | match |
| 42 | Selection budgets "re-derived independently in review, with no mismatch" | sel | I recomputed and cross-checked the values quoted in the README, not all 38 rows | unverifiable by me in full |
| 43 | Fast CoactDetect and LoCo held-out anchors are the sliding form | search `shipped` has `window_mode: sliding`; bench-shipped has no `window_mode` (binned) | same | match |

## Findings

Each finding gives location · issue · severity · suggested fix · whether I verified it against a source.

**F1.** Decision 1, bullet "The independent check…"
- **Issue:** It says combined rate+context's fresh intervals "barely touch". They do not: [0.642, 0.726] against [0.748, 0.793] leaves a 0.022 gap. That makes it the second non-overlapping pair, which is stronger evidence than the page states.
- **Severity:** major. It is the independent check for an adoption decision.
- **Fix:** "Fast binned SCE's and combined rate+context's intervals do not overlap."
- **Verified:** yes.

**F2.** Decision 8 table, rows 1 and 3
- **Issue:** "beats" rests on point estimates. Combined-tuned LoCo on fast is [0.806, 0.838] against [0.779, 0.809], and combined-tuned CoactDetect is [0.810, 0.845] against [0.791, 0.831]. Both pairs overlap; only the rate+context row separates.
- **Severity:** minor.
- **Fix:** Add the CoactDetect intervals and say which rows overlap.
- **Verified:** yes.

**F3.** Decision 8 framing
- **Issue:** The decision is framed one way, as a combined-tuned version winning on fast or slow. The 3 × 3 also shows a fast-tuned version beating combined's own on the combined bench. That includes the **strictly adoptable combined binned SCE**: fast-tuned scores 0.788 [0.774, 0.802] against 0.764 [0.748, 0.781]. Fast-tuned CoactDetect does the same (0.811 against 0.803), and slow-tuned locust beats fast's own on fast (0.777 against 0.766). This bears directly on Decision 1.
- **Severity:** major.
- **Fix:** List every off-diagonal cell that beats the diagonal, and point from Decision 1 to the combined binned SCE case.
- **Verified:** yes.

**F4.** Decision 6 ⚠ bullet, and the matching comment in `src/bugarach/bench.py` (the fix)
- **Issue:** "The slow and combined LoCo searches did walk the 8 s guard at 20 s and 30 s contexts" is not supported by the record.
  - Coordinate rounds vary one setting from the current state. On slow and combined, LoCo's state context stayed at 120 s (slow's history shows only moves to `merge_gap` and `null_context_mode`; combined's history is empty). The pair grid is threshold × context with the guard at 0.
  - The search that could actually break the cap was **fast** LoCo. It moved to a 5 s context in round 1, and the guard axis (0.5–4 s, cap 1.25 s) comes after context in the same round.
  - The conclusion "no proposal changes" still holds.
- **Severity:** major. It is a false factual statement, repeated in a code comment.
- **Fix:** Name fast LoCo at 5 s context. Say that walking was "possible" for slow and combined rather than asserting it.
- **Verified:** partly. Per-evaluation parameters are not logged; I inferred this from the round histories and the `coordinate_rounds` code.

**F5.** Decision 6, "No proposal uses a nonzero guard"
- **Issue:** False as written. Combined CoactDetect's proposal has `guard_sec` 8 and combined rate+context's (adoptable) proposal has 4. Both are within the cap.
- **Severity:** minor.
- **Fix:** "No LoCo proposal…"
- **Verified:** yes.

**F6.** Decision 7, "25 of 40, 20 of 40 and 15 of 40 for the last three rows"
- **Issue:** The numbers belong to rows 2 (fast busy, middle level), 4 (combined busy, middle) and 5 (slow busy, lowest). Row 3 (combined quiet) is 40/40.
- **Severity:** minor.
- **Fix:** Name each row.
- **Verified:** yes (`bench_floor.json`).

**F7.** Decision 7, last bullet
- **Issue:** "about one ROI above the no-coordination recording's floor" holds for fast and combined but not slow: 6–7 against 3–4, about +3. A no-coordination floor exists only for the quiet background.
- **Severity:** minor.
- **Fix:** Give the per-stream differences, and say "quiet background".
- **Verified:** yes.

**F8.** Decision 1, "Figure 3 shows the same point above its bar"
- **Issue:** Figure 3 is on the fresh elevated-rate seeds, where the value is 1.38 calls/h, not the held-out 1.28.
- **Severity:** minor.
- **Fix:** Quote both values.
- **Verified:** yes.

**F9.** Decision 1, "pass them by wide margins"
- **Issue:** Combined binned SCE's proposal makes 5.75 calls/min inside the stretch against a ceiling of 10 (57%), identical to the shipped point. That is not a wide margin.
- **Severity:** minor.
- **Fix:** Give the three ratios.
- **Verified:** yes.

**F10.** Figure 4 bullets and Decision 7: "8 other seeds"
- **Issue:** The seeds are 1–8, a subset of the selection seeds the search chose on.
- **Severity:** minor.
- **Fix:** Say "seeds 1–8".
- **Verified:** yes.

**F10b.** Figure 3 bullet: "every ROI's own event rate is raised to the background's 99th percentile"
- **Issue:** In the bench, every ROI is set to one fixed rate, `hot_rate_hz` 0.1334 Hz on fast. That is the 99th percentile of per-cell background rate over real 300 s baseline stretches, and it is the same on quiet and busy.
- **Severity:** minor.
- **Fix:** Reword to describe the single fixed rate.
- **Verified:** yes (`bench.py` 1353–1368).

**F11.** Decision 2, "On fast, the proposal did not move…"
- **Issue:** Slow locust's shipped point also sits at `n_synchronous_frames` = 1, so the same remark applies to slow.
- **Severity:** minor.
- **Fix:** Say "on fast and slow".
- **Verified:** yes.

**F12b.** Real data, "where locust was left unseeded"
- **Issue:** The run record says locust **and SCE** were unseeded in v2.
- **Severity:** minor.
- **Fix:** Add SCE.
- **Verified:** yes.

**F13.** Decision 4, combined CoactDetect's context
- **Issue:** The search did extend the context grid to 240 s; the validity rule then rejected it. So 120 s is a hidden edge rather than an unexamined one. The sentence is accurate, but the page could say why the record does not flag it.
- **Severity:** minor.
- **Fix:** Optional one clause.
- **Verified:** yes.

**F14.** What ran, 3 × 3 row: "`main` `723f1e6` (#812)"
- **Issue:** 723f1e6 is the merge commit of PR #813. PR #812 merged at 1ad2654, so 723f1e6 contains it.
- **Severity:** minor.
- **Fix:** "(#812 and #813)" or "after #813".
- **Verified:** yes.

**Not checked by me:** whether the 0.02 close-events allowance counts as signed (for slow binned SCE; only the quote was checked), and the full re-derivation of every selection-budget row (ledger #42).
