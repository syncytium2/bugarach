GRANT 1 ok — Read, Grep, Glob, Bash

(I also hold SubagentHandback, which is only the hand-off channel. I hold no editing tool. My scratch folder was not needed: every recomputation ran from stdin and wrote nothing to disk.)

# Role 1 (Prove It): blind review of `<darkroom>/bugarach/2026-09-26-full-panel/briefing/index.html`

**Bottom line.** Every number in Tables 2–4 matches the night's source files: 63 rows × 2 benches × (ΔF1 and its interval, F1, F1 without decoys), plus merged calls, picks, run spreads, budget values and limit marks. So do the Table 1 counts (except two medians), the example tables and captions, Table 6, the seed counts and the timestamps. I found four substantive problems and three minor ones. None changes a number in Tables 2–4. Two change what the page calls "unflagged", and so which row leads on slow.

## How I checked
- I rebuilt the whole leaderboard from the raw source files, without calling the generator's functions:
  - `065/fresh-realistic` and `065/fresh-bench` candidates.json, plus the two count-rule files;
  - the pick rule re-derived from `train_rows` against CoactDetect's no-coordination budget;
  - budgets re-derived from `bench*.py` limits;
  - row order, above / includes-zero / below counts and medians recomputed.
- I re-classified every baseline call in `065/review/detect/calls.csv` into agree / leader-only / reference-only at the 2.5 s tolerance, re-summed baseline hours from `windows.csv`, and re-picked each example call.
- I reconciled Table 6 against the export folder's own `slices.csv` and `regions.csv`. That is the project's record of which group each recording belongs to and what its first treatment was.
- I confirmed `briefing/detections.csv` holds exactly the same 72,661 calls as `calls.csv` (a different schema, the same calls).
- I counted the orange marks and † daggers in Figure 1 against my recomputed flags.

## Findings

| # | Location | Issue | Severity | Suggested fix | Verified against a source |
|---|---|---|---|---|---|
| F1 | Table 1 "unflagged" column and top-row column; headline "(10 of them unflagged)", "(8 of them unflagged)"; §2 slow leader "LoCo · shipped"; the leader rule "is not on a search limit" | For some rows whose search proposed nothing, the shipped setting **is** the search's best, and the search's own bracketing record marks it as on a limit. Slow LoCo shipped: guard 0 s marked off-limit (ADR-0010 ruling 5), context window 120 s at the grid ceiling. `bench_slow.OPERATING_POINTS` confirms its guard really is 0.0. The same holds for slow rate+context shipped (guard 0), combined LoCo shipped (guard 0, context at the ceiling, bin width at the edge), and the count rule's starting points on slow (binned and sliding) and on combined (binned), all at k = 0. `limit_marks()` returns nothing whenever the proposal is named "shipped", so these rows show no mark. Two consequences. **(a)** The page is inconsistent with itself: "Count offset k 0 cells, at its lower limit by design" is a flag on fast count (binned) · proposal and combined count (sliding) · proposal, but the identical record on the starting points raises none. As a result, count (sliding) · starting point is Table 1's "top unflagged row" for slow on the old bench. **(b)** The slow leader is presented as meeting a rule ("not on a search limit") that the search record says it fails. If these rows were flagged, slow new "unflagged" would drop from 10 to 6 and combined new from 8 to 5. | major | Read the bracketing record whatever the proposal is named. Either mark shipped settings the search found on a limit, or change the leader rule and the Terms entry to say explicitly that "search limit" applies to proposals only, and why. Also treat the "k = 0 by design" axis the same way on proposals and starting points. | yes |
| F2 | Section 1, "How to read it": "ADR-0010 ruling 1's check, the same rows … 4 intervals of 51 change side, and 0 cross" | Not the same rows. The board has 60 rows besides CoactDetect shipped; the check covers 51. It leaves out all 9 count-rule rows, although their ORX scoring exists in the same night folder (`064/count/fresh-orx/candidates.json`). `EXTRA_GLOBS` picks that file up, but `orx_check` reads only `065/fresh-orx`. With the count file included: **6 of 60 change side, 0 cross.** The two it misses are slow count (binned) · starting point and combined count (binned) · starting point, both moving from above zero to including zero. Table 1 counts both as above zero and unflagged. The line also does not say that its reference is CoactDetect *shipped*. The worker's README reports 17, counted against both references. | major | Merge `064/count/fresh-orx` into the ORX check and print "6 of 60". Say "against CoactDetect's shipped setting (the README's 17 count both references)". | yes |
| F3 | "What is compared", the note on _part names | The page says every `_part` model gets "a bounded vote per cell summed into a count … and a membership term in the training loss". False for tube_part. `src/bugarach/learn/nets/tube_part.py` registers with `PART_TRAINING_NO_MEMBERSHIP` (membership weight 0.0): tube "averages cells away before any per-cell stage, so it has no vote to train and no membership loss". Its count is ROIs with an onset in a 20-frame window, not summed votes. ADR-0010 part 5 says the same. | major (an "X does Y" statement contradicted by the code) | Say the membership term applies to the chorus and line families only, and describe tube_part's count separately. | yes |
| F4 | Table 1 "median F1 of the other rows"; headline median figures | `glance()` takes `others[len//2]`, the upper-middle value, which is not the median when the count is even (22, 18 and 20 rows). Fast new: page 0.641, true median 0.639. Fast old: page 0.768, true 0.767. Fast move: page −0.127, true −0.128. Combined move: page +0.022, true +0.021. Slow and the other combined cells round the same either way. | minor | Use `statistics.median`, or label the column "middle row". | yes |
| F5 | "How to read it", Budgets; Terms "budget" | "the elevated-rate test … outside its stretch" is gated on the **quiet** background only. That is consistent with `search_all_settings.make_admissible`, which says so in a comment. But the page does not say it. Three rows exceed the outside limit on busy: fast rate+context shipped, and combined rate+context and SPIKE-synch shipped. They are already flagged for precision swing, so no flag changes. | minor | Add "(quiet background, as the search gates it)". | yes |
| F6 | Terms: "merged calls … two or more planted events (ADR-0010 part 3)"; "background … 25th and 75th percentiles of real baseline rates" | ADR-0010 part 3 says **scored** events (planted events under the floor are don't-care). `bench.REGIMES` defines quiet and busy as the 25th and 75th percentiles of slice-mean per-ROI **background** rate, with the coordinated share subtracted and measured on the fast stream. | minor | Tighten both definitions to match their sources. | yes |
| F7 | Byline: "Every number is read from the night's files" | The budget limits come from `<worktree>/src/bugarach/bench*.py`, not from the night's files. The Terms entry says so, but the byline does not. | minor | "… from the night's files and the budget limits in bench*.py". | yes |

## Claim ledger
Each row gives the value quoted on the page, where it comes from, what I recomputed, and the verdict.
- **Seeds.** New bench 48 fast, 24 slow, 24 combined; old bench 24 each, from `seeds_by_bench`. Recomputed: 6000–6047 and 6000–6023 → match. Every row has n_seeds 48 or 24 with 0 dropped.
- **Times.** Scored 1:33 AM, 8:03 PM, 6:33 PM and 8:07 PM EDT, and built 8:58 PM EDT. File modification times and the UTC stamps in RUN_C.md and 064/count/RUN.md agree → match.
- **Tables 2–4, all 63 rows.** ΔF1 [lo, hi] new and old, F1 · F1 without decoys new and old, merged calls, from `paired_f1_vs_coact.shipped`, `mean_f1` (checked equal to the average of quiet and busy F1), `mean_f1_without_decoys`, and the quiet + busy merged-call sum → all match to 3 decimal places.
- **Row order and row counts** (23, 19 and 21 rows) → match.
- **Picks and held-out spreads.** Pick = best training-run mean with no-coordination calls within 7, 1 and 10 calls/h (fast, slow, combined). All 23 picks match, and so does results.json `chosen`. Slow chorus_gain_norm_part: no run within 1/h; 2.444 calls/h → match. All 24 spreads (for example 0.51–0.64) → match.
- **Budget marks.** Every "Over budget" value and limit re-derived from the `bench*.py` limits → match (for example 0.148/0.100, 2.033/1.000 calls/min, 7.233/4.000, 0.319/0.150).
- **Limit marks and daggers.** Every one matches the bracketing record: guard 0, context 20 s and 120 s, 99.9922th percentile at the cap, C_min 0, dt at the cap, run of 1 frame, k = 0, guard 8 s at the edge. The omissions are those in F1.
- **Identical scores.** "Same scores as CoactDetect · proposal to every digit" for fast LoCo proposal: mid, lo, hi and F1 are identical → match.
- **Table 1 counts, all 6 stream × bench rows.** Above / includes zero / below: fast new 13/4/5, fast old 4/14/4, slow new 16/1/1, slow old 0/0/18, combined new 12/5/3, combined old 1/13/6 → match. "Of those, unflagged" 3, 1, 10, 0, 8, 1 → match under the page's own flag definition (but see F1). Top unflagged rows and their ΔF1 → match.
- **Table 1 CoactDetect shipped F1.** 0.608, 0.769, 0.786, 0.848, 0.767, 0.777 → match.
- **Table 1 medians.** Two fast cells and two moves are off → mismatch (F4).
- **Headline moves in CoactDetect's F1.** −0.160, −0.062, −0.009 → match.
- **ORX line.** "4 of 51, 0 cross" is correct for 065/fresh-orx alone; the full row set gives 6 of 60 → incomplete (F2).
- **Bootstrap.** "95% percentile bootstrap, 2,000 draws": `score_bench_candidates.BOOTSTRAP = 2000`, `np.percentile` 2.5 and 97.5 → match.
- **ADR citations.** 0.01 F1 noise unit (part 1), ruling 2 retiring the old bench, ruling 5, ruling 7's 20 s, old bench at least 120 s apart → match. ADR-0010 part 5 as applied to tube_part → mismatch (F3). Part 3 wording → minor (F6).
- **The worker's README "names one row".** Its finding 2 says it is the only row over budget → match.
- **Real-data side.** Examples dataset = default (`2026-09-23_…_PINS_EXCLUDED`) and results.json `dataset.name` → match.
- **Real-data settings.** Coded detectors at their proposal where the search made one: `chosen` matches the board-inferred settings on all 3 streams.
- **Passed-over list and its reasons** (8 rows on fast); leader and runner-up choices → match.
- **Example tables.** 91/32/1, 422/1/3, 388/3/71 by group, and every per-hour rate → match on recount.
- **Baseline hours.** DI 5.7 h, OVX 5.6 h, MALE 4.3 h, ORX 6.3 h → match (5.67, 5.60, 4.27, 6.28).
- **Figures 2–9.** Pool sizes, "away from window edges" counts, groups, participant counts and the selection rule → all match on recount. Where the pool is even, the "median" call is the upper-middle one; no call can sit at an in-between median, so this is not a finding.
- **The slow leader-only case.** "No call … at least 10 s inside (1 call in all)" → match.
- **Table 6.** 66 recordings; DI 17, OVX 17, MALE 13, ORX 19; group and first treatment for every member → match against the export's slices.csv and regions.csv, with 0 mismatches.
- **Table 5.** 24 review pages → match (24 html files).
- **Viewer and detections.** viewer.html is present; detections.csv holds the same calls as calls.csv → match.
- **Participants rule.** [onset − 1 s, onset + width + 1 s] → matches results.json `participants_rule`.
- **Starting point.** "Set 2026-09-26, untuned" → matches the `OPERATING_POINTS` source string. "Shipped settings predate it" → dated 2026-09-16, 09-21 and 09-23 → match.
- **Figure 1.** Orange marks: fast 7 new / 5 old, slow 4/4, combined 6/2. Daggers 6/3/4. The standalone SVG files are identical to the inline ones → match.

## Sources the page did not consult
The project's record of group and subject membership is the export's `slices.csv`. It shows 36 mice across the 66 recordings, and 55 recordings share a mouse with at least one other. The page pools recordings only for per-group call counts and rates; it makes no inferential claim, so this is not a finding. It would become one if the per-group rates were ever compared as independent samples. Withdrawn recordings are absent from the folder by contract, and the unit count reconciles at 66.

## Files
- Artifact: `<darkroom>/bugarach/2026-09-26-full-panel/briefing/index.html`, with `briefing.json` beside it
- Generator: `<worktree>/tools/make_briefing.py`, in particular `limit_marks` (F1), `orx_check` (F2), `PART_NOTE` (F3) and `glance` (F4)
- Contradicting sources:
  - `<worktree>/src/bugarach/learn/nets/tube_part.py`
  - `<darkroom>/bugarach/2026-09-26-full-panel/064/count/fresh-orx/candidates.json`
  - `<darkroom>/bugarach/2026-09-26-full-panel/065/fresh-realistic/candidates.json`, under `benches.{slow,combined}.detectors.{loco,rate}.proposal.bracketing`
  - `<worktree>/src/bugarach/bench_slow.py`, `OPERATING_POINTS['loco']`
  - `<worktree>/tools/search_all_settings.py`, `make_admissible`
