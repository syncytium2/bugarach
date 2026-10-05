> Archived verbatim. Repository and darkroom paths are shown as placeholders (SAP004). No per-call values from
> real recordings appear; the counts are aggregates.

GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

Role 6 (RTFM), blind pass. I checked the built page at <darkroom>/bugarach/2026-09-26-full-panel/briefing/index.html and <worktree>/tools/make_briefing.py against the method sources the page depends on:
- score_bench_candidates.py (paired_difference, picked, train_rows, proposal)
- search_all_settings.py (make_admissible, bracketing, extend, COUNT_FLOOR)
- make_final_parameters_report.py (fresh_budgets, failed)
- score.py (score_detections, merged calls, decoy calls)
- bench.py (BENCH_RECORDING n_distractors, realistic_counts, seed_factor, the budget dicts in all three bench modules)
- detect_with_floors results.json `chosen`, calls.csv variants and windows.csv
- the learn/nets `*_part` registry notes
- ADR-0010 in full, plus ADR-0008 for the floor

I recomputed the leaderboard counts and the budget failures in my own code from the candidates.json files, not by calling the page's functions. No files were modified. My only scratch folder is <scratchpad>/mb3/, and it is empty: the heredoc hook blocked the file, so every script ran inline with `python -c`.

## Findings (location · issue · severity · fix · verified against source)

**1. Table 1 "fast / old" row and the Fast headline ("against 3 of 21 on the old bench")**
- **Issue:** The duplicate-row test (`same_as`) runs on the new bench only, but `glance()` drops those rows from both columns. Fast LoCo·proposal matches CoactDetect·proposal digit for digit on the new bench, so it is dropped. On the old bench the two differ (ΔF1 +0.031 [+0.011, +0.052] against +0.033 [+0.012, +0.053], both printed in Table 3), so a distinct row with its interval above zero goes missing from the old-bench count.
- **Correct values:** 4 of 22 intervals wholly above zero (not 3 of 21); F1 without decoys above the reference in 5 of 22 (not 4 of 21); 14 of 22 including zero.
- **Severity:** Major (the headline number is wrong).
- **Fix:** work out `same_as` per bench column and drop a row only in the column where the scores match. The ORX pairing has the same problem.
- **Verified:** yes, by independent recomputation from 065/fresh-bench plus 065/fresh-bench-count.

**2. Figure 3 (fast, "leader calls it; CoactDetect does not") and Table 6**
- **Issue:** This example sits exactly on the tolerance boundary. The gap to CoactDetect's nearest call beats 2.5 s only by floating-point rounding, about 1e-13 s. The page's own rule ("within 2.5 s") and the bench scorer's inclusive `<= tol_sec` would both count it as agreement. The caption contradicts itself as a result: "2.5 s away, beyond the 2.5 s tolerance".
- **Correct values:** with a float-safe comparison, fast Table 6 reads 92 calls agree and 31 only the leader's (not 91 and 32), and 5 of CoactDetect's calls agree with two or more of the leader's (not 4). Slow and combined do not change.
- **Severity:** Major. The one figure meant to show a leader-only call on fast shows a call that agrees by the stated rule.
- **Fix:** compare with a small epsilon, or round spans to the frame, in `_near` and `nearest_gap`; then re-pick the example.
- **Verified:** yes (re-ran `classify` with the tolerance widened by 1e-9 s).

**3. Section 2 box: "The leaderboard's top rows mostly did not run on the real recordings at all"**
- **Issue:** False according to results.json `chosen`. Of the top five rows, 4 ran on fast, 3 on slow and 4 on combined. What did not run is the two count rules, fast LoCo·shipped and slow chorus_gain_norm_part (no pick). Most top rows were passed over for a budget or a search limit, as the page's own "passed over" lists show.
- **Severity:** Major. It tells the reader the examples cannot test rows they could.
- **Fix:** name what did not run and say that the rest were passed over for budget or limit flags.
- **Verified:** yes.

**4. ORX sentence ("6 intervals of 59 move between above zero and including zero")**
- **Issue:** `changed` counts any change of side. Two of the six move between wholly below and including zero (one on fast, one on combined), so only four match the wording.
- **Second issue:** the parenthetical about the worker's 17 names only one difference. The worker's count also left out the count-rule rows, which reached the files later, so the two row sets differ as well.
- **Severity:** Minor/Major (factual misstatement).
- **Fix:** say "change between a side of zero and including it", or split the count by direction. Qualify the note about the 17.
- **Verified:** yes (broke down the sides of 065/fresh-orx plus 064/count/fresh-orx).

**5. Headline, Combined sentence ("F1 moves from 0.777 to 0.767: recall 0.92 against 1.00, and it merges close events")**
- **Issue:** The explanation leaves out the term that offsets the rest.
  - Recall loss and merges alone would pull F1 down much further.
  - F1 barely moves because planted events rose (425 to 512) while decoy calls held steady (242 to 232), which lifted precision.
  - The recall and merge effect shows up in F1 without decoys, 1.000 to 0.956.
- **Slow's sentence is supported.** Matching is one to one (score.py; ADR-0010 part 3), so each of the 51 merged calls costs at least one miss, against about 57 missed of 636 events.
- **Severity:** Minor.
- **Fix:** add the precision offset, or attribute the recall and merge effect to F1 without decoys.
- **Verified:** yes.

**6. Headline, Fast sentence ("calls decoys 2.1 times as often")**
- **What is right:** the mechanism. BENCH_RECORDING fixes n_distractors at 6 per recording. The realistic spacing plants about 7 events instead of 15. Ruling 2 doubles fast's seeds. So decoys per planted event double.
- **Issue:** "as often" reads as a change in CoactDetect's behaviour. Its decoy calls per recording are unchanged (about 4.5: 214 over 48 recordings, 439 over 96), and it calls about 75% of decoys on both benches.
- **Severity:** Minor.
- **Fix:** say "twice as many decoys per planted event, and it calls the same share of them".
- **Verified:** yes.

**7. `headline()` code (make_briefing.py, the decoy branch)**
- **Issue:** The fast-only explanation ("per fast recording", ruling 2's seed doubling) is printed whenever a generic condition holds (decoy ratio at least 1.5 and quiet recall change under 0.1), on any stream. It is latent: tonight it fires only on fast.
- **Severity:** Minor.
- **Fix:** gate it on the stream, or on `seed_factor(stream) == 2`.
- **Verified:** yes (code).

**8. `limit_marks()` and the "unflagged" definition**
- **Issue in the code:** any unbracketed axis whose reason is "limit" and that is not a ruling-5 finding becomes a NOTE, with fixed wording: "lower limit by design (the floor itself); the search could not go lower". That wording is true only of `k_offset` (COUNT_FLOOR). Any other axis stopped at a hard limit would be exempt from flagging and described falsely. That includes FLOAT_FLOOR's bin_sec and win_sec at 0.1 s, a fraction at 1.0, and alpha's high end.
- **Issue in the method:** the search record marks these count rows `bracketed: False` and `adoptable: False`. The bracketing docstring says a stop at a limit makes a candidate not adoptable, and ADR-0010 part 1 defines "final" as bracketed. The page exempts them on its own reading. It says so, but it does not say that the search's own record disagrees.
- **Effect:** the fast top unflagged row becomes LoCo·shipped (+0.033) instead of count·proposal (+0.034), which is within the level band. The slow top unflagged row becomes line·pick (+0.036) instead of count (sliding)·starting point.
- **Severity:** Minor.
- **Fix:** limit the exemption to `k_offset` by name, and state that the search record marks these rows not adoptable.
- **Verified:** yes.

**9. Byline: "budget limits from src/bugarach/bench*.py"**
- **Issue:** The limits are read from the build tree, not from the night's commit.
  - The recorded no-coordination limits in every candidates.json match today's values; I checked all of them.
  - The elevated-rate and precision-swing limits are not recorded in the run, so they cannot be checked against it.
  - The count limits were set the same day as the run.
- **Severity:** Minor.
- **Fix:** stamp the commit, or read the limits the run recorded.
- **Verified:** partly.

## Checked and clean
- **Interval method:** ΔF1 is computed per seed on pooled F1, with a 2,000-draw percentile bootstrap; the only dropped seeds are on training runs the page does not show.
- **Seed counts and spacing:** new bench 48 fast, 24 slow, 24 combined; old bench 24 each. Every file's spacing matches its column.
- **Learned picks:** each follows the scorer's rule, and every model has 5 runs, so the seed-0 fix is in the scored file.
- **Budget failures:** every mark on all 3 streams × 2 benches matches my own re-implementation of the search's admissibility rule on the fresh seeds. That covers the elevated-rate test inside the stretch on both backgrounds, outside it on quiet only, and the close-events test retired under ADR-0010 part 4.
- **What ran on the real recordings:** `ran_on_real` agrees with results.json `chosen`.
- **Real-data inputs:** calls.csv variants are not double-counted; baseline hours are consistent across rows; the participants rule matches detect_with_floors.
- **Definitions and descriptions:** merged calls match score.py; the `_part` descriptions and the 20-frame window for tube_part match the registry notes; the 0.01 noise unit matches ADR-0010 part 1.
- **Citations:** ADR-0010 part 4 and rulings 2, 5, 6, 7 and 8 are cited correctly; the guard cap is not binding for combined CoactDetect's 8 s guard (90 s context).
