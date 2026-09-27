> Archived verbatim. Paths are shown as placeholders (SAP004). Real-data figures are aggregates only.

GRANT 1 ok — Read, Grep, Glob, Bash

# Role 1 (Prove It): blind review of `<darkroom>/bugarach/2026-09-26-full-panel/briefing/index.html`

**Result: 2 major and 4 minor findings. Nearly every number on the page matched the source files when I recomputed it.** I recomputed from the candidates.json files, calls.csv, windows.csv, results.json, the export folder and the bench*.py modules. For the key tables I wrote my own scripts rather than reading briefing.json. Nothing was edited. Scratch files are only under `<scratchpad>/mb3/r1/`.

## Findings

| # | Location | Issue | Severity | Suggested fix | Verified against source |
|---|---|---|---|---|---|
| 1 | Table 1, row "fast old". Also the section 1 headline "against 3 of 21 on the old bench". | The page counts a row that repeats another row's scores only once. It decides which rows repeat by comparing **new-bench** scores, then applies that to the **old** column too. LoCo · proposal matches CoactDetect · proposal to every digit on the new bench only. On the old bench the two differ: LoCo is +0.031 [+0.011, +0.052], F1 0.805; CoactDetect is +0.033, F1 0.806. So LoCo is a separate old-bench row, and its interval is wholly above zero. By the caption's own rule the fast-old cells should read: **4 of 22** above zero (not 3 of 21), 14 including zero, 4 below, 1 unflagged; **5 of 22** above on F1 without decoys (not 4 of 21); 0 of 21 above CoactDetect's proposal; **3 other rows** level with the top (not 2). Table 3's row note correctly says "on the new bench"; the counting does not respect that. | major | Decide which rows repeat separately for each bench column. Or say plainly that rows are merged by their new-bench identity, and give the old-bench count both ways. | yes |
| 2 | Figure 3 (fast, "only the leader") and Table 6 | The Figure 3 call's span sits exactly at the 2.5 s tolerance from CoactDetect's nearest call. It lands on the "no match" side only because of floating-point error. The page's rule is "within 2.5 s", and the bench scorer is inclusive too (`score.py`, `<= tol_sec`). So by the page's own rule this call **agrees**. The caption contradicts itself: "2.5 s away, beyond the 2.5 s tolerance". I recomputed with tolerance 2.5 ± 1e-6. Exactly one call moves: fast becomes **92 both / 31 only-leader** (page: 91 / 32). Slow and combined, and the "no disagreement" counts for line_part and tube_part, do not change. | major | Compare spans with a small epsilon, or round them to the 0.1 s frame grid, before applying the tolerance. Then rebuild Table 6 and re-pick Figure 3. | yes |
| 3 | Section 2 box: "The leaderboard's top rows mostly did not run on the real recordings at all" | Not supported. Of the rows passed over above each leader, 5 of 11 are "did not run" (fast 3 of 8, slow 2 of 3). The rest were passed over for a budget or a search limit. What is true: on fast and slow the top **unflagged** row is a count-rule row, and the count rule did not run. | minor | Reword along those lines. | yes |
| 4 | ORX paragraph: "(The worker's run notes count 17, because they also count intervals against CoactDetect's proposal.)" | The reason is incomplete. RUN_C's 17 = 4 against the shipped setting + 13 against the proposal. The page's 6 includes 2 count-rule rows that RUN_C predates. As written, a reader cannot get from 6 to 17 (17 − 13 = 4). | minor | Add "and they predate the count rule, which accounts for 2 of the 6". | yes |
| 5 | Section 1 headline, slow and combined: "its recall is 0.91 [0.92] against 1.00" | Only the quiet recall is given. Busy is 0.90 (slow) and 0.91 (combined). Correct, but selective. | minor | Write "0.91 · 0.90" to match Table 2. | yes |
| 6 | Terms, "background" | "25th and 75th percentiles of real baseline background rates per cell". bench.py actually uses p25/p75 of the slice-mean per-ROI background rate, fast stream, over the recordings that clear the shape floors, with the coordinated share subtracted. Close enough; slightly loose. | minor | Optional: "slice-mean per-ROI". | yes |

## Claim ledger

Every row below matched its source.

**Leaderboard, Tables 3–5 (all 63 rows).** For each row I checked new ΔF1 with its interval, new F1 and F1 without decoys, recall quiet · busy, merged calls, old ΔF1 with its interval, and old F1 and F1 without decoys. All match my recomputation from the six candidates.json files. I also checked:
- Every learned pick, i.e. which training run was picked. All 23 picks also match the 064 README table.
- The "held-out F1 of the 5 runs" ranges, including the rounding cases (fast line 0.52–0.68, slow line 0.78–0.82, slow chorus_gain_norm 0.79–0.82).
- The slow chorus_gain_norm_part "no pick" row: best run is seed 4, 2.444 calls/h against a limit of 1.

**Budget marks.** I recomputed all 28 pass/fail marks from bench*.py limits and candidates.json. Every one matches, for example:
- fast SPIKE-synch precision swing 0.148 against 0.1;
- combined rate+context 0.319 against 0.15;
- slow locust elevated-rate test 7.233 calls/min against 4.

The page says the worker's notes name one row over budget because they count only the no-coordination budget. That is correct: 065 README finding 2.

**Search-limit marks (†).** These match the bracketing records in candidates.json: 5 rows on fast, 6 on slow, 4 on combined. The count offset k is shown as a note, not a flag, and matches `reason: limit`. SPIKE-synch combined carries no mark, which matches the README ("the one bracketed proposal").

**Table 1.** Every cell matches on every stream and bench except "fast old" (finding 1). That includes the top unflagged row and its level count. On combined old the top row is chorus_gain_norm_part at +0.01128, just ahead of tube_part at +0.01126.

**Table 2.**

| Quantity | Page | Recomputed |
|---|---|---|
| Planted events scored, old / new | fast 395/387, slow 670/636, combined 425/512 | same |
| Calls on decoys, old / new | 214/439, 240/251, 242/232 | same |
| Merged calls, old / new | 0/12, 0/51, 0/35 | same |
| F1 and recall | as printed | same |
| "2.1 times" | 439/214 | 2.05 |

- "About half as many events per fast recording": 8.2 scored events per recording on the old bench, 4.0 on the new.
- "Twice the decoys per event": decoys are fixed at `n_distractors=6` per recording.

**Seeds and timestamps.**
- Seeds: 48/24/24 new, 24/24/24 old (from `seeds_by_bench`).
- Scoring times 1:33 AM, 6:33 PM, 8:03 PM and 8:07 PM EDT match RUN_C and count/RUN.md.

**ORX check.** I recomputed it independently:
- ρ = 0.909 / 0.761 / 0.940;
- top rows as printed;
- 6 of 59 intervals change side, 0 cross;
- RUN_C's list of 17 confirmed.

**Figure 1a–c.** I parsed all 126 marks from the SVGs, rescaled them with the axis ticks and compared them with the data. All are within 0.0015 F1, and all orange/blue colours match the budget and no-pick marks.

**Tables 6–8.** I reimplemented the matching rule myself:
- counts by kind and group, calls per baseline hour, the "two or more matches" counts (2/4, 0/0, 5/4);
- pool sizes, number of recordings per pool, calls away from window edges;
- the Figure 7 edge cut.

All match, except the one fast call in finding 2.

**Leader and runner-up selection.** Consistent with the leaderboard and with results.json's record of which settings ran. The CoactDetect it uses is the proposal on all three streams, as the page says.

**Unit record: the source of group membership.** This is the default export's slices.csv and regions.csv.
- 66 recordings: IDs identical to windows.csv and to Table 9.
- Group labels: 0 mismatches.
- Group × first treatment: 11/6/9/8/8/5/9/10, matching Table 9.
- Baseline hours: DI 5.67, OVX 5.60, MALE 4.27, ORX 6.28, all reconciled.
- 24 review pages; 72,661 calls.
- Recordings share animals: 36 mice, and 55 of the 66 recordings share a mouse with another. The page makes no statistical claim on the real data (its intervals are over simulation seeds only), so there is no finding. Still, "from 27 recordings" counts recordings, not animals.

**Self-describing labels.**
- "starting point (untuned)": bench OPERATING_POINTS `source` says "not tuned … set 2026-09-26".
- "unflagged" and "level" are applied as the page defines them.
- "held-out F1" and "pick": the 064 README describes the same selection rule.

**Definitions and ADR citations.**
- Bootstrap: percentile method, 2,000 draws, per-seed F1 pooled over quiet and busy (score_bench_candidates.py).
- Merged calls: counts only scored events (score.py).
- tube_part: a 20-frame window (tube_part.py).
- Participation floor: max(3 ROIs, chance count reached at most once an hour), per ADR-0008.
- ADR-0010 citations all check out: part 1, part 3, part 4, part 5, ruling 2 (old bench retired as a reference; fast seeds doubled), ruling 5, ruling 7, and ADR-0009 decision 5 (the 120 s ceiling).

**Retractions.** 064/recheck-sce-merge.md withdraws the night's "no call changes" result for binned SCE's merge gap. The page does not repeat the withdrawn claim. Its flag ("a value that switches it off, a ruling-5 finding") is still correct.

**Not verified.** I did not check that the training recordings' seeds are disjoint from the fresh seeds (6000+). The page says "ones neither the search nor the training saw". For the search this is confirmed: selection seeds 1–96, held-out 97–192. For training I found only the test-seed ranges (4000–4047 fast, 4000–4023 slow and combined), which do not overlap.

Files relevant to the findings:
- `<worktree>/tools/make_briefing.py`: finding 1 comes from the repeat check in `build()` and its use in `glance()`; finding 2 comes from `_near()` / `classify()`, which have no epsilon.
- `<darkroom>/bugarach/2026-09-26-full-panel/065/fresh-bench/candidates.json`: the old-bench LoCo and CoactDetect proposal rows (finding 1).
- `<darkroom>/bugarach/2026-09-26-full-panel/065/review/detect/calls.csv` (finding 2).
- `<darkroom>/bugarach/2026-09-26-full-panel/065/RUN_C.md` (finding 4).
