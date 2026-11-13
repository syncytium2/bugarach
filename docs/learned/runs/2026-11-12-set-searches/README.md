# The nine bench-set searches and their cross-scores, 2026-11-12

**Use this page when** you want the settings each bench set's search proposed, or how a setting
tuned on one set scores on the other sets of its stream.

> Working material, not murderboarded. Nothing here is adopted; adoption is Tony's.

**What ran.** `tools/search_all_settings.py --bench <set> --sliding` on each of the nine bench
sets (`docs/learned/bench_sets/`: fast, slow and combined, each built from all 12 recordings,
from DI's 5 and from MALE's 7 of the default folder `tracked_cohorts`), on a workstation with
11 workers, then `tools/cross_score_sets.py --seeds 12`. The recordings are simulated; no lab
data are read.

**Files.** `<set>/search.json` is each search; `VERDICT_set_searches.txt` is the output check
(9 of 9 pass); `cross_score.json` is the full table and `cross_score_table.txt` its printed
form (mean F1, and in brackets the share of planted pairs 1 s apart that were called as two).

**Durations.** 17.8 to 177.6 minutes a search for 348 to 462 evaluations each; the spread is
a few very slow evaluations, not the amount of work. Cross-scoring took 35.3 minutes.

**What the table shows** (12 fresh recordings per background, 24 on fast; one draw):

- **Slow:** a setting tuned on any set scores within 0.008 mean F1 of the others on every set.
- **Combined:** the same within 0.006, except SPIKE-synch and binned SCE, where the settings
  tuned on all recordings lose 0.04 on the DI set.
- **Fast:** the sets disagree. rate+context tuned on all recordings scores 0.706 on the DI set
  against 0.980 for the DI-tuned setting, and the DI-tuned setting scores 0.801 on the MALE
  set. SPIKE-synch shows the same pattern at a smaller size. CoactDetect and count (sliding)
  tuned on all recordings lose 0.04 on the MALE set. LoCo and count (binned) do not move.

**Limits.**

- The sets plant no decoys (ADR-0019), so nothing here penalises a call on a near-event.
- Every detector's search ended with at least one setting at the edge of its grid.
- The DI sets rest on 5 recordings from 3 mice.
- The pair counts behind the bracketed shares are small: 8 to 29 pairs a cell.
- The split by group describes synthetic sets built from each group's recordings. It tests
  nothing between the groups (ADR-0017).
- The false-alarm limits and starting settings are inherited from the September benches.
