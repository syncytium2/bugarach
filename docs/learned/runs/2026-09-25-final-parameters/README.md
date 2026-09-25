# The final-parameters night, 2026-09-25: what is adoptable, and what waits on Tony

**Nothing here is adopted.** No `bench*.py` operating point changed. The night re-searched every
coded detector, and retrained the two chorus models, under the new event floor. The settings
shipped today were all tuned before that floor existed, and four of them now fail a budget
(decision 3). This page asks Tony for one adoption decision and seven rulings. The rules the night
followed are the
[runbook](../../../handoffs/2026-09-25-overnight-final-parameters.md),
[ADR-0008](../../../adr/0008-the-event-floor-is-set-per-window-from-its-own-null.md) (the event
floor) and
[ADR-0009](../../../adr/0009-the-bench-keeps-its-elevated-rate-test-in-a-recording-of-its-own.md)
(the elevated-rate test moves into a recording of its own). Terms are defined at the end of the
page, under *Definitions*.

## Decision 1: adopt these four?

Four proposals meet the runbook's strict rule. Their held-out F1 gain has a 95% interval above zero.
They pass every budget that was checked on the selection, held-out and fresh seeds. And no setting
sits at an end of its searched grid.

| stream | detector | settings that change | held-out gain in F1 [95% interval] | fresh-seed F1, shipped → proposal [95% interval] |
|---|---|---|---|---|
| fast | binned SCE | `bin_width_sec` 10 → 2 s; `merge_gap_sec` none (no merge) → 10 s | +0.060 [+0.046, +0.077] | 0.747 [0.729, 0.765] → 0.785 [0.769, 0.802] |
| combined | binned SCE | `threshold_pctile` 98 → 99 | +0.015 [+0.006, +0.024] | 0.748 [0.731, 0.763] → 0.764 [0.748, 0.781] |
| combined | rate+context | `excess_threshold_hz` 4.5 → 6 Hz; `merge_gap_s` 8 → 16 s | +0.093 [+0.076, +0.113] | 0.683 [0.642, 0.726] → 0.773 [0.748, 0.793] |
| combined | SPIKE-synch | `C_threshold` 0.08 → 0.1; `tau_mode` isi_adaptive → fixed | +0.029 [+0.016, +0.043] | 0.761 [0.734, 0.782] → 0.782 [0.768, 0.794] |

Read these three things before deciding:

- **The held-out seeds also chose.** The search picked its candidates on selection seeds 1–48. Then
  the proposal was chosen as the best of those candidates on held-out seeds 49–96, among the
  candidates whose gain interval there was above zero (`score_bench_candidates.proposal()`).
  - So the held-out gain is not an unbiased estimate, and "interval above zero" is how the
    proposal was chosen, not a test it later passed.
  - For combined binned SCE the choice changed the answer. On the selection seeds another candidate
    led by 0.0003 F1; on the held-out seeds this one did.
  - **The independent check is the fresh seeds** (6000–6023), which nothing chose on. There, fast
    binned SCE's two intervals do not overlap. Combined rate+context's barely touch. Combined
    binned SCE's and combined SPIKE-synch's overlap.
  - These are separate intervals, not an interval on the gain. A paired gain on the same seeds would
    be tighter; it was not computed.
- **"Every budget checked" has gaps.** The held-out rows do not record precision per background, so
  the precision swing was not checked there. The fresh seeds do not run the close-events test.
  Calls outside the elevated-rate stretch are gated on the quiet background only: that is the
  background the budget was measured on (PR A's choice). On the busy background, combined
  rate+context's proposal makes 1.28 calls per hour outside the stretch on the held-out seeds,
  against a limit of 1 call per hour. Figure 3 shows the same point above its bar.
- **Combined's budgets carry an open warning of their own.** `bench_combined.py` says its
  elevated-rate ceilings are "the thing to look at before any of these is trusted". The four
  proposals pass them by wide margins, so no verdict here depends on that.

**Decide:** adopt all four, some, or none.

**Figure 1. Fresh-seed F1 for each detector's shipped point and its proposal, by stream.**

- Circles are the shipped point. Diamonds are the proposal: blue where it is adoptable under the
  strict rule, orange where it is not. Gray diamonds are the chorus fit each training run picked.
- F1 is the mean over the quiet and busy backgrounds, on 24 fresh recordings per background.
- Each line is a 95% bootstrap interval over those recordings. The shipped point's sits just above
  its row and the proposal's just below.
- A row with a circle only had no proposal.

![Figure 1](figure1_fresh_f1.png)

## The rulings the adoption depends on

Each item ends with the decision it asks for. Decisions 2 and 3 are first because they change how
many proposals there are, or what the shipped points are worth.

### Decision 2: does a value at a hard limit count as bracketed?

Five proposals are held back only because one setting sits at a value that cannot go further:

| stream | detector | the setting at its limit | held-out gain [95% interval] |
|---|---|---|---|
| fast | locust | minimum run of synchronous frames (`n_synchronous_frames`) = 1 frame | +0.098 [+0.087, +0.110] |
| slow | locust | the same, 1 frame | +0.102 [+0.091, +0.115] |
| combined | locust | the same, 1 frame (moved there from 5) | +0.036 [+0.020, +0.052] |
| slow | rate+context | guard (`guard_sec`) = 0 s | +0.005 [+0.003, +0.007] |
| slow | SPIKE-synch | minimum coincidence (`C_min`) = 0 | +0.043 [+0.035, +0.051] |

- Each of the five passes every budget that was checked.
- On fast, the proposal did not move `n_synchronous_frames`: the shipped point already sits at 1, so
  the shipped point would fail the same test.
- Under the strict rule none of the five is adoptable. If a limit counts, all five are, which makes
  nine.

**Decide:** does a limit count as a bracket?

### Decision 3: four shipped points are out of budget, and the floor may be why

No limit was loosened (ADR-0009 decision 4).

| stream | detector | budget failed | measured, selection · held-out · fresh | limit |
|---|---|---|---|---|
| fast | SPIKE-synch | precision swing | 0.181 · not recorded · 0.148 | 0.10 |
| fast | rate+context | precision swing | 0.181 · not recorded · 0.175 | 0.10 |
| slow | locust | elevated-rate test, inside the stretch (calls per minute, quiet background) | 7.24 · 6.85 · 7.23 | 4.0 |
| combined | rate+context | precision swing | 0.245 · not recorded · 0.257 | 0.15 |

- **Why fast SPIKE-synch and rate+context have no proposal.** Their shipped points were
  inadmissible from the start, and so was every neighbor tried. So the search had nothing it was
  allowed to move to.
  - The diagnosis is in the darkroom at
    `bugarach/2026-09-25-final-parameters/064/phase2/DIAGNOSIS-sync-and-rate-moved-nothing.md`.
  - It found the gate working as written, not a bug.
- **The precision swing may be the floor's doing, not the detectors'.**
  - Each recording's floor follows its own event rate. So the busy background takes a higher floor
    than the quiet one and sets aside different planted events. On fresh seeds, 85 of 120
    middle-level events are under the floor on fast busy, and none on fast quiet (Table 3).
  - Every budget was set as a ceiling over what the shipped point measured on the bench before the
    floor. Fast rate+context and SPIKE-synch measured a swing near 0.01 then.

**Decide:**
1. Are these four shipped points out of budget?
2. Or does the precision-swing budget need re-measuring under the floor? Re-measuring is a new
   ruling, not a loosened limit.

### Decision 4: CoactDetect's `alpha` runs to the extension cap

- The search lowered `alpha` as far as it was allowed to go:
  - fast, 1e-4 → 1.4e-9;
  - combined, 1e-5 → 1.4e-9.
- It gained F1 at each step. On the selection seeds, lowering `alpha` alone gained +0.031 on fast
  and +0.013 on combined.
- Held-out gains:
  - fast: +0.055 [+0.036, +0.075];
  - combined: +0.039 [+0.026, +0.056].
- Neither is bracketed, and combined's sits at a context of 120 s, the longest the bench allows,
  which the bracketing record does not flag.
- **Fast CoactDetect does not fail the close-events test.**
  - The search's record says it loses 0.044 mean F1 on the held-out seeds. That was measured against
    the shipped values in their sliding form, which fast does not ship.
  - Re-run in review against the binned point fast actually ships (held-out close-events seeds
    49–60), the loss is 0.0165, inside the 0.02 allowance.
  - Table 2 still shows the search's verdict, labelled with what it was measured against.

**Decide:** is an `alpha` of about 1e-9 a setting you would ship? Or should CoactDetect's grid stop
at a stated floor?

### Decision 5: may a context window be shorter than 20 s?

- ADR-0009 decision 5 lists the context grid as 20, 30, 45, 60, 90 and 120 s. It caps the context at
  120 s and does not say whether a search may go below 20 s.
- The search did go below:
  - on fast and combined, LoCo's context was extended to 10 s and 5 s;
  - fast LoCo's first-round move was to 5 s. Its final proposal, which came from the two-setting
    grid, sits at 20 s.
- Fast LoCo's proposal is held back for another reason. `threshold_pctile` shows as "cap", but all
  six extensions went downward (94 to 1). The upper end, 99.99, was never extended; it counts as
  "cap" only because the axis's six extensions were used up going the other way.

**Decide:** is 20 s the shortest context, or only the grid's starting point?

### Decision 6: the guard cap

- The runbook caps a guard at a quarter of its context window (not an ADR). At 20 s and 30 s
  contexts that is 5 s and 7.5 s, so the 8 s guard the slow and combined grids carry is excluded
  there.
- ⚠ **Until this page, the cap never reached LoCo.** Its check sat after LoCo's own validity branch
  returned. So the slow and combined LoCo searches did walk the 8 s guard at 20 s and 30 s contexts.
  - Fixed in the same PR as this page (`bench.settings_are_valid`), with a test.
  - No proposal uses a nonzero guard, so no result on this page changes.

**Decide:** keep the quarter-of-context cap?

### Decision 7: much of the planted bench now sits under the floor

On fast and combined:
- the lowest planted level is entirely under the floor on both backgrounds;
- on the busy background, much of the middle level is too.

| stream | background | floors | lowest level | middle level |
|---|---|---|---|---|
| fast | quiet | 5–6 ROIs | 120 of 120 (3 ROIs) | 0 of 120 |
| fast | busy | 6–8 ROIs | 120 of 120 (3 ROIs) | 85 of 120 (6 ROIs) |
| combined | quiet | 6–7 ROIs | 120 of 120 (4 ROIs) | 0 of 120 |
| combined | busy | 7–10 ROIs | 120 of 120 (4 ROIs) | 55 of 120 (8 ROIs) |
| slow | busy | 7–8 ROIs | 50 of 120 (7 ROIs) | 0 of 120 |

- These counts are on the fresh seeds, 24 recordings × 5 events per level.
- Figure 4 re-measures the same thing on 8 other seeds: 25 of 40, 20 of 40 and 15 of 40 for the last
  three rows.
- So recall on fast and combined counts only events above the floor, as ADR-0009 anticipated.
- In Figure 4, each planted recording's floor sits about one ROI above the no-coordination
  recording's floor on the same background. That suggests the planted events raise their own null,
  and the event set partly defines itself (read off the figure, not measured).

**Decide:** accept a bench whose lowest level no longer counts toward recall? Or change the planted
levels?

### Decision 8: per-stream tuning, when another stream's version scores higher

Figure 2 scores every version on every stream's bench. Several times, a version tuned on combined
beats a stream's own version on that stream's bench (fresh seeds, 95% intervals):

| version | scored on | score | the stream's own version | score |
|---|---|---|---|---|
| combined-tuned LoCo (shipped) | fast | 0.820 [0.806, 0.838] | fast LoCo proposal | 0.794 [0.779, 0.809] |
| combined-tuned rate+context proposal | slow | 0.865 [0.855, 0.874] | slow rate+context proposal | 0.834 [0.825, 0.843] |
| combined-tuned CoactDetect proposal | fast | 0.827 | fast CoactDetect proposal | 0.809 |

- Compare down a column, not across a row. The slow bench is easier for almost every detector, so F1
  levels are not comparable between columns.

**Decide:** does one setting per stream still hold, when a combined-tuned setting wins on fast and
on slow?

### Smaller items

- **Slow binned SCE** loses 0.0207 mean F1 on the close-events test on the held-out seeds, against
  an allowance of 0.02, so it is not adoptable. Its gain is +0.014 [+0.011, +0.019].
  - The same statistic read 0.0198 on the selection seeds, and it is a point estimate on 12
    recordings per background.
  - The 0.02 allowance is itself provisional: `bench_slow.py` calls it "still unsigned".
  - So this row is at the allowance within noise, and the call is Tony's.
- **Slow chorus_norm's picked fit** makes 1.43 calls per minute inside the elevated-rate stretch,
  against CoactDetect's slow limit of 1.0. Chorus has no budget of its own.

## The full tables

**How to read them:**
- **Held-out gain** is the bootstrap median of the proposal's F1 minus the shipped point's, on seeds
  49–96, with a 400-resample interval over recordings. It is selection-biased (Decision 1).
- For fast CoactDetect and LoCo, the search started from the shipped values in their **sliding**
  form, while fast ships them binned. So the held-out gain is against sliding at the shipped values.
  The fresh-seed shipped F1 is against the binned point that actually ships.
- **Fresh F1** is on seeds 6000–6023, as scored and without decoy calls.
- For fast CoactDetect and LoCo, the "shipped" budgets on the selection and held-out seeds are those
  of the sliding starting point as well. The fresh-seed ones are the binned point's.
- **Bracketed (strict)** lists each open setting with its reason: cap, edge or limit. A "cap" counts
  extensions on both ends of a setting. So LoCo's `threshold_pctile` reads "cap" although its upper
  end was never extended.
- **Chorus** is checked against CoactDetect's limits, the anchor of its training rule.
- **Three methods caveats**, all as the ADRs define them, and stated here because they affect how far
  the numbers transfer:
  - The floor is counted in a 2 s co-activity window, whatever window a detector counts in. For
    combined CoactDetect's 3 s window and binned SCE's 2–10 s bins, chance co-activity in the
    detector's own window is larger than the floor assumes.
  - SPIKE-synch's `min_n`, which the floor sets, sums coincident onsets over a call's bins. It does
    not count distinct ROIs.
  - ADR-0008 asks that each floor's stability across halves of its draws be reported. That is done
    in `065/bench-floor/`, but not for the recordings scored here (seeds 1–96 and 6000–6023).

**Table 1. Every detector × stream.**

<!-- adoption-table:start (written by tools/make_final_parameters_report.py; do not edit by hand) -->
| stream | detector | settings that change, shipped → proposal | held-out gain in F1 [95% interval] | fresh F1, shipped → proposal [95% interval] | fresh F1 without decoy calls, shipped → proposal | bracketed (strict) | bracketed if a limit counts | adoptable (strict) |
|---|---|---|---|---|---|---|---|---|
| fast | CoactDetect | `alpha` 0.0001 → 1.4e-09; `context_win_sec` 60 → 30; `window_mode` binned → sliding | +0.055 [+0.036, +0.075] (against sliding at the shipped values) | 0.769 [0.755, 0.782] → 0.809 [0.791, 0.831] | 0.981 → 0.956 | no: `alpha` (cap), `guard_sec` (limit) | no | no |
| fast | LoCo | `context_win_sec` 120 → 20; `threshold_pctile` 99.5 → 99.99; `window_mode` binned → sliding | +0.010 [+0.001, +0.018] (against sliding at the shipped values) | 0.777 [0.755, 0.802] → 0.794 [0.779, 0.809] | 0.946 → 0.989 | no: `threshold_pctile` (cap), `guard_sec` (limit) | no | no |
| fast | binned SCE | `bin_width_sec` 10 → 2; `merge_gap_sec` none (no merge) → 10 | +0.060 [+0.046, +0.077] | 0.747 [0.729, 0.765] → 0.785 [0.769, 0.802] | 0.953 → 0.981 | yes | yes | **yes** |
| fast | rate+context | none (no proposal) | — | 0.703 [0.678, 0.727] | 0.931 | — | — | — |
| fast | SPIKE-synch | none (no proposal) | — | 0.792 [0.763, 0.823] | 0.899 | — | — | — |
| fast | locust | `sce_min_distance_frames` 4 → 128; `sce_percentile` 99.999 → 99.99995 | +0.098 [+0.087, +0.110] | 0.699 [0.682, 0.716] → 0.766 [0.747, 0.786] | 0.954 → 0.995 | no: `n_synchronous_frames` (limit) | yes | no |
| fast | chorus_norm | the fit the training rule picked (training seed 1) | — | 0.773 [0.746, 0.802] | 0.891 | — | — | — |
| fast | chorus_gain_norm | the fit the training rule picked (training seed 4) | — | 0.744 [0.723, 0.766] | 0.883 | — | — | — |
| slow | CoactDetect | none (no proposal) | — | 0.848 [0.838, 0.857] | 1.000 | — | — | — |
| slow | LoCo | `merge_gap_sec` 4 → 8; `null_context_mode` maxlt → symmetric | +0.012 [+0.009, +0.016] | 0.831 [0.824, 0.837] → 0.846 [0.837, 0.855] | 0.996 → 1.000 | no: `threshold_pctile` (cap), `context_win_sec` (edge), `guard_sec` (limit) | no | no |
| slow | binned SCE | `merge_gap_sec` none (no merge) → 5 | +0.014 [+0.011, +0.019] | 0.818 [0.808, 0.826] → 0.835 [0.824, 0.846] | 0.982 → 0.988 | yes | yes | no |
| slow | rate+context | `merge_gap_s` 3 → 5 | +0.005 [+0.003, +0.007] | 0.830 [0.822, 0.837] → 0.834 [0.825, 0.843] | 0.995 → 0.995 | no: `guard_sec` (limit) | yes | no |
| slow | SPIKE-synch | `dt` 0.1 → 0.00625; `max_gap` 4 → 8; `tau_max` 0.5 → 1 | +0.043 [+0.035, +0.051] | 0.796 [0.783, 0.807] → 0.845 [0.835, 0.854] | 0.956 → 0.999 | no: `C_min` (limit) | yes | no |
| slow | locust | `sce_min_distance_frames` 4 → 256 | +0.102 [+0.091, +0.115] | 0.740 [0.726, 0.754] → 0.845 [0.833, 0.857] | 0.914 → 0.974 | no: `n_synchronous_frames` (limit) | yes | no |
| slow | chorus_norm | the fit the training rule picked (training seed 3) | — | 0.825 [0.815, 0.834] | 0.989 | — | — | — |
| slow | chorus_gain_norm | the fit the training rule picked (training seed 3) | — | 0.827 [0.819, 0.834] | 0.993 | — | — | — |
| combined | CoactDetect | `alpha` 1e-05 → 1.4e-09; `int_win_sec` 2 → 3 | +0.039 [+0.026, +0.056] | 0.777 [0.763, 0.788] → 0.803 [0.788, 0.818] | 1.000 → 0.978 | no: `alpha` (cap) | no | no |
| combined | LoCo | none (no proposal) | — | 0.804 [0.787, 0.822] | 0.983 | — | — | — |
| combined | binned SCE | `threshold_pctile` 98 → 99 | +0.015 [+0.006, +0.024] | 0.748 [0.731, 0.763] → 0.764 [0.748, 0.781] | 0.950 → 0.960 | yes | yes | **yes** |
| combined | rate+context | `excess_threshold_hz` 4.5 → 6; `merge_gap_s` 8 → 16 | +0.093 [+0.076, +0.113] | 0.683 [0.642, 0.726] → 0.773 [0.748, 0.793] | 0.855 → 0.978 | yes | yes | **yes** |
| combined | SPIKE-synch | `C_threshold` 0.08 → 0.1; `tau_mode` isi_adaptive → fixed | +0.029 [+0.016, +0.043] | 0.761 [0.734, 0.782] → 0.782 [0.768, 0.794] | 0.949 → 0.978 | yes | yes | **yes** |
| combined | locust | `n_synchronous_frames` 5 → 1; `sce_percentile` 99.999 → 99.99995 | +0.036 [+0.020, +0.052] | 0.762 [0.745, 0.777] → 0.782 [0.768, 0.796] | 0.982 → 0.979 | no: `n_synchronous_frames` (limit) | yes | no |
| combined | chorus_norm | the fit the training rule picked (training seed 1) | — | 0.778 [0.760, 0.796] | 0.950 | — | — | — |
| combined | chorus_gain_norm | the fit the training rule picked (training seed 0) | — | 0.772 [0.752, 0.793] | 0.940 | — | — | — |
<!-- adoption-table:end -->

**Table 2. Every budget, for the shipped point and the proposal, on each seed set.** "Not checked"
means that seed set has no record of the check.

<!-- budget-table:start (written by tools/make_final_parameters_report.py; do not edit by hand) -->
| stream | detector | version | selection seeds 1–48 | held-out seeds 49–96 | fresh seeds 6000–6023 |
|---|---|---|---|---|---|
| fast | CoactDetect | shipped | pass | pass (the sliding starting point) | pass |
| fast | CoactDetect | proposal | pass | **fail: close-events test** (close-events against the sliding starting point) | pass |
| fast | LoCo | shipped | pass | pass (the sliding starting point) | pass |
| fast | LoCo | proposal | pass | pass (close-events against the sliding starting point) | pass |
| fast | binned SCE | shipped | pass | pass | pass |
| fast | binned SCE | proposal | pass | pass | pass |
| fast | rate+context | shipped | **fail: precision swing** | pass | **fail: precision swing** |
| fast | SPIKE-synch | shipped | **fail: precision swing** | pass | **fail: precision swing** |
| fast | locust | shipped | pass | pass | pass |
| fast | locust | proposal | pass | pass | pass |
| fast | chorus_norm | picked fit | not run | not run | pass (CoactDetect's limits) |
| fast | chorus_gain_norm | picked fit | not run | not run | pass (CoactDetect's limits) |
| slow | CoactDetect | shipped | pass | pass | pass |
| slow | LoCo | shipped | pass | pass | pass |
| slow | LoCo | proposal | pass | pass | pass |
| slow | binned SCE | shipped | pass | pass | pass |
| slow | binned SCE | proposal | pass | **fail: close-events test** | pass |
| slow | rate+context | shipped | pass | pass | pass |
| slow | rate+context | proposal | pass | pass | pass |
| slow | SPIKE-synch | shipped | pass | pass | pass |
| slow | SPIKE-synch | proposal | pass | pass | pass |
| slow | locust | shipped | **fail: elevated-rate test, inside the stretch** | **fail: elevated-rate test, inside the stretch** | **fail: elevated-rate test, inside the stretch** |
| slow | locust | proposal | pass | pass | pass |
| slow | chorus_norm | picked fit | not run | not run | **fail: elevated-rate test, inside the stretch** (CoactDetect's limits) |
| slow | chorus_gain_norm | picked fit | not run | not run | pass (CoactDetect's limits) |
| combined | CoactDetect | shipped | pass | pass | pass |
| combined | CoactDetect | proposal | pass | pass | pass |
| combined | LoCo | shipped | pass | pass | pass |
| combined | binned SCE | shipped | pass | pass | pass |
| combined | binned SCE | proposal | pass | pass | pass |
| combined | rate+context | shipped | **fail: precision swing** | pass | **fail: precision swing** |
| combined | rate+context | proposal | pass | pass | pass |
| combined | SPIKE-synch | shipped | pass | pass | pass |
| combined | SPIKE-synch | proposal | pass | pass | pass |
| combined | locust | shipped | pass | pass | pass |
| combined | locust | proposal | pass | pass | pass |
| combined | chorus_norm | picked fit | not run | not run | pass (CoactDetect's limits) |
| combined | chorus_gain_norm | picked fit | not run | not run | pass (CoactDetect's limits) |
<!-- budget-table:end -->

**Table 3. Planted events under the floor, by stream and background, on the fresh seeds.** Levels
are given as a share of a recording's ROIs and as participants.

<!-- floor-table:start (written by tools/make_final_parameters_report.py; do not edit by hand) -->
| stream | background | floors (co-active ROIs) | planted events under the floor, by participation level (of 120 per level: 24 recordings × 5 events) |
|---|---|---|---|
| fast | quiet | 5–6 | 10% (3 ROIs): 120, 20% (6 ROIs): 0, 30% (10 ROIs): 0 |
| fast | busy | 6–8 | 10% (3 ROIs): 120, 20% (6 ROIs): 85, 30% (10 ROIs): 0 |
| slow | quiet | 6–7 | 21% (7 ROIs): 0, 38% (12 ROIs): 0, 63% (20 ROIs): 0 |
| slow | busy | 7–8 | 21% (7 ROIs): 50, 38% (12 ROIs): 0, 63% (20 ROIs): 0 |
| combined | quiet | 6–7 | 13% (4 ROIs): 120, 25% (8 ROIs): 0, 40% (13 ROIs): 0 |
| combined | busy | 7–10 | 13% (4 ROIs): 120, 25% (8 ROIs): 55, 40% (13 ROIs): 0 |
<!-- floor-table:end -->

**Figure 2. Each detector's version tuned on one stream, scored on every stream's bench (the 3 × 3).**

- Rows give the bench the version was tuned on; columns give the bench it was scored on. Each cell
  is the mean F1 on fresh seeds, on the colorbar's scale. The diagonal is bold.
- Compare down a column: the slow bench is easier for almost every detector.
- The version is the proposal where the stream had one, else the shipped point, and for chorus the
  picked fit.
- The cells' 95% intervals are in `adoption.json` under `cross_stream`.

![Figure 2](figure2_cross_stream.png)

**Figure 3. The elevated-rate recording, supplied by WSMIP065.**

- The recording is 45 minutes with nothing planted. For 5 of those minutes, every ROI's own event
  rate is raised to the background's 99th percentile. A call during that stretch is a false alarm
  caused by rate, not by coordination.
- The panels of calls per minute inside the stretch are gated on both backgrounds. The panels of
  calls per hour outside it are gated on the quiet background only.
- Each bar is that detector's own limit.
- The recordings are 12 per background, on seeds 66000–66011.

![Figure 3](figure3_elevated_rate.png)

**Figure 4. The bench floors re-measured on the ADR-0009 bench, supplied by WSMIP065.**

- The floor panel gives each recording kind's floor in co-active ROIs, as the range over 8 seeds,
  against the range ADR-0009 expected.
- The share panel gives the planted events under the floor at each participant count, over the same
  8 seeds × 5 events.

![Figure 4](figure4_bench_floors.png)

## Real data

- **The run.** `tools/detect_with_floors.py` on the 66 recordings of the default dataset,
  `senktide_ttx`, every window scored under two floors:
  - the window's own floor;
  - the floor of the same recording's baseline window.
- **Where it ran.** Run record `065/phase3-real-v3/` in the darkroom, write-up
  `065/report-inputs/real_data.md`. It ran on PR #814, which seeds every detector that draws random
  numbers. #814 is not merged, so the run is on unmerged code. It supersedes `065/phase3-real-v2/`,
  where locust was left unseeded.
- **What it found.**
  - 128 treatment windows × 3 streams × 8 detectors = 3,072 cells.
  - In 2,696 cells the two floors differ.
  - In 498 cells, a call under one floor becomes no call under the other.
  - Under senktide on fast, OVX's own floor sits a median +17 ROIs above its baseline floor, and
    ORX's +20.
- **Descriptive only** (FOUNDATIONS §9). It states no treatment effect.

## Definitions

- **F1.** The harmonic mean of recall and precision, with each call matched to a planted event
  within 2.5 s. *Mean F1* averages the quiet and busy backgrounds.
- **SCE** (synchronous calcium event), **ROI** (region of interest, one imaged cell), **stream**.
  The event trace analysed, one of fast, slow and combined.
- **Chorus.** The learned detector, trained on the bench.
- **Event floor** (ADR-0008). For each window, the larger of 3 ROIs and the smallest number of
  co-active ROIs that the window's own rigid-shift null reaches at most once per hour.
  - The null shifts each ROI's whole event train by up to *J* = 20 s.
  - It uses 1,000 draws and a 2 s co-activity window.
  - A planted event with fewer participants than its recording's floor is **don't care**: it is left
    out of recall, and a call matched to it is left out of precision.
- **Seed sets.** Selection seeds 1–48 are what the search chose on. Held-out seeds 49–96 are what the
  proposal was then chosen on (Decision 1). Fresh seeds 6000–6023, and 56000–56011 and 66000–66011
  for the no-coordination and elevated-rate recordings, are what nothing chose on.
- **Budgets:**
  - the elevated-rate test: calls per minute inside the stretch, and calls per hour outside it;
  - the no-coordination recording (calls per hour);
  - the **precision swing**: the difference in precision between the quiet and busy backgrounds;
  - the close-events test: a loss of at most 0.02 mean F1 against the shipped point, on recordings
    whose planted events are as little as 6 s apart.
- **Decoy.** A planted correlated burst that is not labelled as a coordinated event (ADR-0006). F1
  *without decoy calls* leaves calls on decoys out of precision.
- **Search terms:**
  - *rounds* and *pair* name the two ways the search proposes: moving one setting at a time, and a
    grid over two settings together.
  - The **extension cap**: the search may extend a setting's grid past its end at most 6 times
    (`--max-extensions 6`).
  - An open setting is **cap** (the extensions were used up), **edge** (at an end of the grid for
    another reason) or **limit** (the value cannot go further: 0, or 1 frame).

## What ran

| phase | where | code | record (darkroom, `bugarach/2026-09-25-final-parameters/`) |
|---|---|---|---|
| 0: the floor and the search (PR B) | #808, #810 | `main` | — |
| 0: the bench (PR A) | #809 | `main` | `065/bench-floor/` (code commit not recorded) |
| 1: pilot, 4 seeds | WSMIP064 | PR B + PR A merged locally, never pushed (not recorded in the folder) | `064/pilot/`, `064/pilot-chorus-prb-only/` |
| 2: fast searches and chorus | WSMIP064 | `main` `b6e40f0` | `064/phase2/` |
| 2: slow and combined searches | WSMIP065 | `main` `b6e40f0` | `065/phase2/` |
| 3: fresh seeds, fast and chorus | WSMIP064 | `main` `a70b185` (#811) | `064/phase3/`, `064/phase3-chorus-slow-combined/` |
| 3: fresh seeds, slow and combined | WSMIP065 | branch `score-candidates-benches` `7af68c9`, before #811 merged | `065/phase3/` |
| 3: the 3 × 3 | WSMIP064 | `main` `723f1e6` (#812) | `064/phase3-3x3/` |
| 3: real data | WSMIP065 | PR #814 on `723f1e6`, not merged | `065/phase3-real-v3/` |
| 4: this page | WSMIP064 | `tools/make_final_parameters_report.py` | `report/` |

- **Searches:** `tools/search_all_settings.py --bench <b> --sliding --max-extensions 6`.
- **Chorus:**
  `tools/train_learned_on_bench.py --bench <b> --model <m> --seeds 0 1 2 3 4 --device cuda`.
- **Selection budgets** (`064/phase3-3x3/selection_budgets.json`): recomputed with the search's own
  `Evaluator` and `make_admissible`, by a script that is not in the repository. Its numbers were
  re-derived independently in review, with no mismatch.
- **The 3 × 3:** each version scored on its own bench reproduces its `candidates.json` fresh-seed row
  exactly, for all 38 versions. That is a reproducibility check: both sides come from the same
  scorer on the same seeds.
- **This page:** `tools/make_final_parameters_report.py --night <darkroom>/bugarach/2026-09-25-final-parameters`
  writes the tables, Figures 1–2 and `adoption.json`.
