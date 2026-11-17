# The nine bench-set searches at 3x and their cross-scores, 2026-11-13

**Use this page when** you want the settings each 3x bench set's search proposed, how a setting
tuned on one 3x set scores on the other sets of its stream, or how that differs from the same
run at 4x ([`2026-11-12-set-searches`](../2026-11-12-set-searches/README.md)).

> Working material, not murderboarded. Nothing here is adopted; adoption is Tony's.

**What ran.** The 4x route repeated on the folder `tracked_cohorts_3x`: the same 12 recordings
with events detected at 3 × sigma_est rather than 4 ×. Stage 1 measured the folder
([`2026-11-13-stage1-tracked-cohorts-3x`](../2026-11-13-stage1-tracked-cohorts-3x/)),
`tools/measure_bench_sets.py --suffix _3x` built the nine `*_3x` records in
`docs/learned/bench_sets/`, then `tools/search_all_settings.py --bench <set> --sliding` searched
each set and `tools/cross_score_sets.py --seeds 12` scored every tuned setting on every set of
its stream. The run used a workstation with 11 workers, from a scratch worktree whose
`current_export.toml` made the 3x folder the default. The recordings scored are simulated; no
lab data are read after stage 1.

**Files.** `<set>/search.json` is each search; `VERDICT_set_searches.txt` is the output check
(9 of 9 pass); `cross_score.json` is the full table and `cross_score_table.txt` its printed
form (mean F1, and in brackets the share of planted pairs 1 s apart that were called as two).
The cross-score correctly left out the nine 4x sets, whose records were in the same checkout
with no search in this run.

**The dataset stamps were corrected.** In the run, the 3x folder was the default, so every
stamp said `use: input`. The committed `current_export.toml` keeps 4x as the default and the 3x
folder as `eval`, so the stamps in `cross_score.json`, the bench records and the stage 1 records
were changed to `eval`. Nothing else in any file differs from what the run wrote.

**Durations.** 24.2 to 225.0 minutes a search for 368 to 534 evaluations each. The spread is a
few very slow evaluations: in `slow_male_3x`, 2 of 11 workers ran for about 45 minutes right
after SPIKE-synch's `dt` reached 0.00078 s. Cross-scoring took 36.6 minutes.

## What differs from 4x

Same scoring as 4x: 12 fresh recordings per background, 24 on fast, one draw.

- **Combined: the sets no longer agree.** At 4x every setting scored within 0.044 mean F1 of
  the others on every set. At 3x three detectors do not:
  - **rate+context:** the DI-tuned setting scores 0.880 on its own set, while the settings tuned
    on all recordings and on MALE score 0.961 there. This is the only place in either run where
    a set's own setting loses to another set's by more than 0.01. Its search started from a
    setting that broke a false-alarm budget and moved `rate_win` 1 → 3 s first. The searches on
    all recordings and on MALE started from the same setting, moved `excess_threshold_hz`
    4.5 → 8 Hz first and ended elsewhere. The DI search also ended at the bottom edge of the
    `context_win` grid. The cross-score does not check the budgets, so whether the 0.961 setting
    is admissible on the DI set is not known.
  - **SPIKE-synch:** the MALE-tuned setting scores 0.826 on the DI set against 0.999 for the
    DI-tuned one. All of the loss is on the busy background (F1 0.652).
  - **count (sliding):** the DI-tuned setting scores 0.856 on the MALE set.
  - Binned SCE, which lost 0.037 on the DI set at 4x, no longer moves.
- **Fast: the sets still disagree, by different amounts.** The worst rate+context loss is 0.174
  (tuned on all recordings, scored on DI: 0.807 against 0.981), down from 0.310 at 4x. The worst
  SPIKE-synch loss rises to 0.219 (MALE-tuned on DI: 0.780 against 0.999) from 0.150.
  CoactDetect, count (sliding) and LoCo tuned on all recordings lose 0.027 on the MALE set.
- **Slow: no change.** Settings tuned on any set score within 0.010 of each other on every set.
- **Nothing planted:** binned SCE still makes the most false calls, up to 6.7 per hour on slow
  (4.2 at 4x) and 3.1 on combined (8.0 at 4x). count (sliding) reaches 1.3 per hour on slow and
  locust 1.1 on combined. The other tuned settings make at most 0.2 per hour.
- **The shipped settings lose more at 3x on combined:** SPIKE-synch 0.476 to 0.800 (0.514 to
  0.912 at 4x), rate+context 0.669 to 0.883 (0.680 to 0.949).

The 3x sets are busier than the 4x ones. The combined DI set has the busiest background,
0.114 Hz, and the combined disagreement is on that set or involves a setting tuned on it.

## Limits

- The sets plant no decoys, as ADR-0019 rules. The rate-matched negatives it calls for are not
  built. The only negatives scored are a recording at the quiet background with nothing planted
  and the elevated-rate recording.
- In every search, 5 to 8 of the 8 detectors ended with a setting at the edge of its grid.
- The DI sets rest on 5 recordings from 3 mice.
- The pair counts behind the bracketed shares are small: 4 to 27 pairs a cell.
- The split by group describes synthetic sets built from each group's recordings. It tests
  nothing between the groups (ADR-0017).
- The false-alarm limits and starting settings are inherited from the September benches.
- One draw of 12 recordings per background. A difference near 0.01 may be noise.
