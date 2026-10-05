> Archived verbatim except machine-local paths (shown as `<darkroom>`, `<worktree>`, `<scratchpad>`, `<repo>`, SAP004) and redactions: values of individual calls on real recordings (the onsets in finding 1, one
> call's participant count in finding 3, one onset in finding 4) are replaced by `[t]` or `[n]`, because nothing
> derived from real data goes into this public repo (FOUNDATIONS §5). Aggregate counts are kept. Each finding's
> substance survives.

GRANT 1 ok — Read, Grep, Glob, Bash

# Role 1 (Prove It), round 1: the full-panel briefing page

**Artifact:** `<darkroom>\bugarach\2026-09-26-full-panel\briefing\index.html`, with its `briefing.json`, the nine `example_*.png` files, `detections.csv` and `viewer.html` beside it.
**Generator:** `<worktree>\tools\make_briefing.py` (HEAD 86cfffe2).
**Scratch:** the page text and the recomputed rows are in `<scratchpad>\mb\` (`r1_page.txt`, `r1_rows.json`). I edited nothing else. The only file I wrote was that JSON dump, and it came from a script piped in on stdin, because the repo's hook blocks heredoc source files.

This report names no recording ids. Real-data examples are referred to by figure number only.

## The short version
- **All 63 leaderboard rows match the scorer's files exactly.** I checked them by script, not by eye: ΔF1, both interval ends and mean F1 on both benches, plus each learned model's seed. Table 1's counts, every over-budget mark (with the limits taken from the bench modules), the seed counts, the 2,000 bootstrap draws and the two scoring times all match too.
- **The examples section has real errors.**
  - 4 of the 9 figure captions give the wrong call time.
  - The CoactDetect in the examples is its search proposal, not the shipped setting the leaderboard compares against, and the page never says so.
  - The "median participant count" rule is false for Figure 10.
- **One label is wrong on the leaderboard side:** the count rule's "shipped" rows are an untuned starting point set on 2026-09-26, not a pre-ADR-0010 shipped setting.

## Findings
Columns: location · issue · severity · suggested fix · verified against a source.

1. **Captions of Figures 2, 3, 6 and 9 · the call time is wrong. · major · verified: yes**
   - Cause: the generator formats the time as `f"{t / 60:.0f}m{t % 60:02.0f}s"` (make_briefing.py, around line 769). That rounds the minutes instead of truncating them.
   - Figures 2, 3 and 9 each show a minute one too high; each true onset is earlier than its caption says ([t], [t], [t]). Figure 6 prints the impossible "20m60s" for an onset at [t].
   - Figures 4, 5, 7, 8 and 10 are correct only because their seconds are under 30.
   - The viewer links carry the exact time and are fine. The rendered x-axes confirm the true times: Figure 2's call sits just before a minute tick.
   - Fix: `m, sec = divmod(round(t), 60)` → `f"{m}m{sec:02d}s"`, then rebuild.

2. **Examples section and Figures 2–10 · "CoactDetect as it ran there" is CoactDetect at its search proposal on all three streams, not its shipped setting. · major · verified: yes**
   - Source: `065/review/detect/results.json` `chosen.*.detectors.coact.which` is "proposal" on every stream. The 065 README, step D, says the same.
   - Every one of those proposals carries a ruling-5 flag (not adoptable): guard_sec at its limit of 0 s on fast and slow, and at the grid edge of 8 s on combined.
   - A reader will take the CoactDetect lane to be the leaderboard's reference.
   - The same applies to the fast runner-up lane labelled "LoCo": it is LoCo's proposal, which is also flagged.
   - Fix: state the setting in the section text and in the lane labels ("CoactDetect · proposal §5").

3. **Figure 10 and the claim "Each is the call with the median participant count of its kind" · false for Figure 10. · major · verified: yes**
   - Combined, CoactDetect-only calls: 71 calls, median 15 participants. The pick has [n].
   - Why: the pick is the median of the calls on recordings not already used by an earlier figure (47 of the 71). That rule is in the docstring but not on the page.
   - The other 8 picks do equal the median of their whole pool.
   - Fix: say "the median among recordings not already shown", or drop that preference.

4. **Figure 10 caption, "120 s either side" · false for this figure. · minor · verified: yes (rendered PNG)**
   - The call is [t] into the recording, so the window is clipped at the recording's start.
   - A call in the recording's first second is also a possible edge effect, and a reader should be told.
   - Fix: print the actual window, and flag calls within a few seconds of the recording's start.

5. **Reading note ("the shipped settings… date from before ADR-0010, when the old bench was the only one") and Terms ("shipped: the setting a coded detector ships with") · wrong for both count rows. · major · verified: yes**
   - `src/bugarach/bench.py` OPERATING_POINTS gives count and count_sliding with the source "not tuned: the starting point set 2026-09-26".
   - "count (sliding) · shipped" is #2 on slow and #10 on combined on the new bench, and it reads as an established setting.
   - Fix: label these "starting point (untuned, 2026-09-26)" and exempt them from the sentence about dates.

6. **Tables 2–4, the "new mean F1" / "old mean F1" columns · undefined, and they do not reconcile with ΔF1. · minor · verified: yes (read from score_bench_candidates.py)**
   - mean F1 is the average of the quiet-background and busy-background pooled F1.
   - ΔF1 is the mean over seeds of each seed's pooled F1 minus CoactDetect's.
   - Example: fast SPIKE-synch shipped. Mean F1 0.686 − 0.608 = 0.078, while ΔF1 is +0.063.
   - Fix: add a Terms entry saying the columns are computed differently and need not subtract to ΔF1.

7. **Table 1, "top row (ΔF1)" · the column ignores the page's own marks. · minor · verified: yes**
   - The fast/new top row (SPIKE-synch · shipped) is over budget: precision change 0.148 against a limit of 0.10.
   - The fast/old top row (CoactDetect · proposal) is flagged under ruling 5.
   - Fix: mark flagged rows in this column, or add a "top row within budget" column.

8. **Combined tube_part marks, "precision change 0.10 against a limit of 0.1" · reads as within budget.**
   - Severity: minor. Verified: yes.
   - The true value is 0.1035.
   - Fix: print 3 decimals whenever the rounded value equals the limit.

9. **Ruling-5 marks for binned SCE · the recorded reason is dropped.**
   - Severity: minor. Verified: yes, from the search's bracketing record in candidates.json.
   - Combined reads "unbracketed, no axis named", but the record's `findings` holds off_limit merge_gap_sec = NaN.
   - Fast lists only the threshold_pctile cap and omits the same merge_gap_sec NaN finding.
   - `_unbracketed()` reads `unbracketed_axes` only. It should also read `bracketing.findings`.
   - This also answers the 065 README's open question ("I have not looked into why").

10. **The budget marks against the worker's README · conflict.**
    - Severity: minor. Verified: yes.
    - The 065 README, finding 2, says the slow chorus_gain_norm_part row "is the only row over budget". The page marks 17 more budget failures.
    - The page is right by the bench's own definitions: same formula as `search_all_settings.make_admissible`, limits from bench*.py, and I recomputed every value. The README counted only the empty-recording budget.
    - The generator's docstring knows about this, but the page does not tell the reader.
    - Fix: add one line saying the README counts only the empty-recording budget.

11. **Figure 1 and Table 2, row 17 · "-0.000 [-0.001, +0.000]".**
    - Severity: minor. Verified: yes.
    - A signed zero is cosmetic.

12. **Examples section · no pool sizes are given, so the three-figures-per-stream layout implies disagreement is balanced when it is not.**
    - Severity: minor. Verified: yes.
    - Baseline-window calls split as agree / leader only / CoactDetect only:

| Stream | Agree | Leader only | CoactDetect only |
|---|---|---|---|
| fast | 91 calls | 32 calls | 1 call |
| slow | 422 calls | 1 call | 3 calls |
| combined | 388 calls | 3 calls | 71 calls |

    - Fix: give the counts in each stream's heading.

## Claim ledger
Columns: quoted value · cited source · recomputed value · match.

**Leaderboard**
- **63 table rows** (ΔF1 with interval, mean F1, on both benches) · candidates.json in `065/fresh-realistic`, `065/fresh-bench`, `064/count/fresh-realistic` and `065/fresh-bench-count` · recomputed and string-compared by script · **63 of 63 match**.
- **Count rows paired against the same CoactDetect** · the count files' own coact rows · identical to the night's files (mean F1 and paired values) · match.
- **Learned seeds shown** · `benches.*.chorus.picked` / `out_of_budget.best` · match; all 5 training seeds are present in all 24 runs.
- **Table 1 counts, above / includes zero / below:**

| | fast | slow | combined |
|---|---|---|---|
| new bench | 13 / 4 / 5 | 16 / 1 / 1 | 12 / 5 / 3 |
| old bench | 4 / 14 / 4 | 0 / 0 / 18 | 1 / 13 / 6 |

  Recomputed, all match. The top-row labels and values also match.
- **Every budget mark** (18 rows, value and limit) · fresh_budgets formula plus bench / bench_slow / bench_combined limits · recomputed independently · all match; see finding 8 for the display rounding.
- **"new fast 48, slow 24, combined 24 seeds per background; old 24/24/24"** · `seeds_by_bench`, and each seed yields one quiet and one busy recording · match.
- **"2,000 draws", "95% bootstrap interval"** · score_bench_candidates.py BOOTSTRAP = 2000, 2.5–97.5 percentiles · match.
- **"scored 1:33 AM EDT" (new), "8:03 PM EDT" (old)** · file mtimes, and RUN_C.md gives 05:33Z and 00:03Z · match.
- **"new and old benches score the same candidates"** · proposals and picks compared across files · identical · match.
- **"proposals and learned picks chosen on the new bench"** · all 25 search.json files have `spacing: realistic`, and train_stream.ps1 passes `--spacing realistic` · match.
- **"shipped settings… date from before ADR-0010"** · bench.py OPERATING_POINTS · **mismatch** for count and count_sliding (finding 5).
- **§5 flags** · the `bracketing` records · axes match; reasons incomplete for binned SCE (finding 9).
- **Old bench "at least 120 s apart"** · bench.py SPACINGS docstring, min_sep_sec 120 · match.
- **New bench "spacing measured in real recordings"** · bench.py `spacing_overrides`: gaps pooled over the four groups · match.
- **"pick" = best held-out F1 among seeds within CoactDetect's empty-recording budget, of five seeds** · `picked()` in score_bench_candidates.py · match.
- **Slow chorus_gain_norm_part: 2.44 calls/h against a limit of 1** · candidates.json and bench_slow · 2.444 against 1.0 · match.

**Examples**
- **Examples tolerance "2.5 s, the bench's scoring tolerance"** · score.py TOL_SEC = 2.5 · match.
- **Example picks (9)** · calls.csv, re-derived independently · same call as briefing.json in 9 of 9.
- **Participant counts in the captions (9)** · calls.csv · 9 of 9 match.
- **Groups in the captions** · calls.csv and the export's slices.csv · match.
- **Call times in the captions** · calls.csv onset_sec · **4 of 9 mismatch** (finding 1).
- **"median participant count of its kind"** · the pool medians · **Figure 10 mismatch** (finding 3).
- **"Passed over: LoCo · proposal… Of its 91 calls… none gives an example of…"** · calls.csv · 91 calls, 0 leader-only, 0 CoactDetect-only · match.
- **"CoactDetect excluded, and no row over a budget"** · the leader-selection logic plus the fails recomputed above · match (new-bench budgets only; the chosen leaders pass on both benches).

**Rasters and viewer**
- **"24 pages"** · `065/review/pages/*.html` · 24 · match. All links resolve and all 9 images exist.
- **"66 recordings"** · windows.csv, calls.csv, and the export's slices.csv and recording files · 66 in each · match.
- **Table 6 groups and first treatments** · the export's slices.csv and regions.csv · 0 mismatches over 66 rows · match. Groups are in the house order DI, OVX, MALE, ORX.
- **Export folder named in the viewer steps** · current_export.toml default, and results.json `dataset.name` · same folder · match.
- **detections.csv for the viewer** · calls.csv · identical multiset of 72,661 calls · match.

## Sources a deliverable should consult
- **Record of experimental design and unit membership:** the export's `slices.csv` (group, mouse) and `regions.csv` (treatment order). The page never cites them.
- I checked the page against them and every group and first treatment reconciles.
- The one recording the lab withdrew is absent from the folder and from the page, as the export README says.
- The 66 recordings come from 36 mice: 20 mice with 2 recordings, 5 with 3, and 11 with 1. The page does no statistics on the real recordings, so none of them is treated as independent. Worth keeping in mind if counts are ever added to the examples.

## Retractions
- The 065 README's findings (the missing-seed-0 rerun, the one run with no pick) are reflected correctly.
- The page correctly scores from the post-#836 rerun, not the `fresh-realistic-missing-seed0` folder.

## Main source paths
- `...\2026-09-26-full-panel\065\review\detect\results.json`, which records CoactDetect at proposal (finding 2).
- `<worktree>\src\bugarach\bench.py`, the count operating points (finding 5).
- `<worktree>\tools\make_briefing.py`, around line 769 for the time format (finding 1), and `pick_examples` / `_unbracketed` (findings 3 and 9).
