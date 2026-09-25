# The final-parameters night, 2026-09-25: what is adoptable, and what waits on Tony

**Nothing here is adopted.** No `bench*.py` operating point changed. The night re-searched every
coded detector, and retrained the two chorus models, under the event floor of ADR-0008.

**What the floor did.** Each simulated recording now gets a minimum number of co-active ROIs
(regions of interest, one imaged cell each) from its own chance null. A planted event with fewer
participants than that minimum no longer counts for or against a detector. Three things follow:

- On the fast and combined benches, all of the weakest planted events fall under the floor, and so
  do many of the middle ones on the busy background (Decision 4).
- The settings shipped today were tuned before the floor existed, and four of them now fail a budget
  (Decision 3).
- For the four detectors whose participation minimum the floor sets, some of their own thresholds
  stop mattering (Decisions 7 and 8).

The rules the night followed are the
[runbook](../../../handoffs/2026-09-25-overnight-final-parameters.md),
[ADR-0008](../../../adr/0008-the-event-floor-is-set-per-window-from-its-own-null.md) (the event
floor) and
[ADR-0009](../../../adr/0009-the-bench-keeps-its-elevated-rate-test-in-a-recording-of-its-own.md)
(the elevated-rate test moves into a recording of its own). Terms are defined under *Definitions*,
at the end.

**The decisions at a glance:**

| # | the ask | could change today's adoption set? |
|---|---|---|
| 1 | Adopt the four proposals the strict rule allows? One of them changes what SPIKE-synch measures. | — |
| 2 | Does one setting per stream hold, when another stream's version sometimes scores higher? | yes: combined binned SCE |
| 3 | Four shipped points fail a budget. Re-measure those budgets under the new bench, and should decoys under the floor stop counting as false alarms? | yes |
| 4 | Accept a bench whose weakest planted events no longer count toward recall? | yes: what every F1 measures |
| 5 | Does a setting at a hard limit (0, or 1 frame) count as bracketed? | yes: 4 → 9 adoptable |
| 6 | Slow binned SCE is at the close-events allowance within noise: in or out? | yes: one proposal |
| 7 | CoactDetect's `alpha` ran to the extension cap. Ship it, or stop the grid? | no: search rule |
| 8 | May a context window be shorter than 20 s, and what is LoCo's own threshold for now? | no: search rule |
| 9 | Keep the cap that limits a guard to a quarter of its context? | no: search rule |

## Decision 1: adopt these four?

Four proposals meet the runbook's strict rule:
- the held-out F1 gain has a 95% interval above zero;
- every budget that was checked passes on the selection, held-out and fresh seeds;
- the proposal is **bracketed**: no setting sits at an end of its searched grid.

**The independent check is the paired gain on fresh seeds** (6000–6023, which nothing chose on):
proposal minus shipped on the same recordings, with 2,000 paired resamples.

| stream | detector | settings that change | held-out gain in F1 [95%] | paired fresh-seed gain in F1 [95%] | fresh F1, shipped → proposal |
|---|---|---|---|---|---|
| fast | binned SCE | `bin_width_sec` 10 → 2 s; `merge_gap_sec` none (no merge) → 10 s | +0.060 [+0.046, +0.077] | +0.038 [+0.017, +0.058] | 0.747 → 0.785 |
| combined | binned SCE | `threshold_pctile` 98 → 99 percentile | +0.015 [+0.006, +0.024] | +0.017 [+0.001, +0.033] | 0.748 → 0.764 |
| combined | rate+context | `excess_threshold_hz` 4.5 → 6 Hz; `merge_gap_s` 8 → 16 s | +0.093 [+0.076, +0.113] | +0.090 [+0.062, +0.115] | 0.683 → 0.773 |
| combined | SPIKE-synch | coincidence threshold `C_threshold` 0.08 → 0.1; coincidence window `tau_mode` adaptive → fixed | +0.029 [+0.016, +0.043] | +0.021 [+0.003, +0.041] | 0.761 → 0.782 |

All four paired fresh-seed intervals sit above zero. The paired gains are recorded in
`064/phase3-3x3/review_checks.json`, by `tools/final_parameters_review_checks.py`. Before deciding,
read these:

- **Combined SPIKE-synch's proposal changes what the detector is.**
  - It turns off the adaptive coincidence window, which the glossary calls "core
    SPIKE-synchronization (Kreuz 2015), not an option on it". With a fixed window the detector is
    ordinary fixed-window coincidence counting, and it depends on event rate again.
  - Adopting it needs its own ruling: a new name or qualifier, and a changed methods citation.
  - No record shows anyone has asked the measure's author about this variant.
- **What the gain is made of: mostly fewer calls on decoys.**
  - Recall is near 1 almost everywhere. F1 without decoy calls is near 1 for all four proposals,
    and for the shipped points too.
  - So the gain comes from rejecting decoys: planted bursts carrying a non-event label (ADR-0006).
- **What F1 cannot see: calls on real planted events under the floor.**
  - Those events are "don't care" by ADR-0009, so losing them costs nothing in F1.
  - The proposals call far fewer of them. On the busy background the middle level is partly under
    the floor too.

  | proposal | lowest level, quiet | lowest level, busy | middle level, busy |
  |---|---|---|---|
  | fast binned SCE | 22 → 5 of 120 | 23 → 6 of 120 | 60 → 49 of 85 |
  | combined binned SCE | 36 → 24 of 120 | 19 → 12 of 120 | 39 → 33 of 55 |
  | combined rate+context | 34 → 2 of 120 | 41 → 11 of 120 | 55 → 54 of 55 |
  | combined SPIKE-synch | 6 → 5 of 120 | 41 → 20 of 120 | 42 → 41 of 55 |

  Whether losing them is acceptable is part of this decision. The counts are calls matched to under-floor
  events, shipped → proposal, on the fresh seeds.
- **The held-out seeds also chose.**
  - The proposal was picked as the best of the search's final candidates on held-out seeds 49–96,
    among those whose gain interval there was above zero (`score_bench_candidates.proposal()`).
  - So the held-out gain is biased upward, and "interval above zero" is how the proposal was
    chosen, not a test it later passed.
  - For combined binned SCE the choice changed the answer: on the selection seeds another candidate
    led by 0.0003 F1.
- **Some budget checks cannot fail here.** The elevated-rate recording's floor is 16–20 co-active
  ROIs on fast and combined (Figure 4). For detectors whose minimum the floor sets (binned SCE and
  SPIKE-synch among these four), that floor blocks nearly every call in the stretch by construction.
  - Combined SPIKE-synch makes exactly 0.2 calls per minute there, shipped and proposal, on every
    seed set.
  - So a pass there is no evidence for those two. ADR-0009 says as much.
  - Only rate+context, which has no participation minimum, is really tested by it.
- **One proposal goes over a limit on the background that is not checked.** Calls outside the stretch
  are checked on the quiet background only. On busy, combined rate+context's proposal makes 1.28
  calls per hour on the held-out seeds and 1.38 on the fresh ones (Figure 3), against a limit of 1.
- **Other gaps:**
  - The held-out rows do not record precision per background, so the precision swing was not
    checked there.
  - The fresh seeds do not run the close-events test.
  - The budgets are ceilings set a little above what the shipped points measured before the floor.
    Some are far above what these detectors now make, and cannot bind.

What could change this set: Decisions 2 (combined binned SCE), 3 and 4 (what the budgets and F1
mean), 5 (adds up to five) and 6 (adds one).

**Figure 1. Fresh-seed F1 for each detector's shipped point and its proposal, by stream.**

- Circles are the shipped point. Diamonds are the proposal: blue where it is adoptable under the
  strict rule, orange where it is not. Gray diamonds are chorus: the fit its training rule picked.
- F1 is the mean over the quiet and busy backgrounds, on 24 fresh recordings per background.
- Each short line is a 95% bootstrap interval over those recordings (2,000 resamples): black for
  the shipped point, gray for the proposal. A light line joins a shipped point to its proposal.

![Figure 1](figure1_fresh_f1.png)

**Decide:** adopt all four, some, or none, under the strict rule. Separately, may combined
SPIKE-synch's fixed coincidence window still be called SPIKE-synch?

## The rulings that can change today's set

### Decision 2: one setting per stream, when another stream's version sometimes scores higher

Figure 2 scores every version on every stream's bench.

- 14 of the 48 off-diagonal cells score higher than the stream's own version.
- In 13 of those the intervals overlap. With 48 comparisons, some such wins are expected from noise.
- One does not overlap: combined-tuned rate+context on the slow bench, 0.865 [0.855, 0.874] against
  slow's own proposal at 0.834 [0.825, 0.843].
- **The one that bears on Decision 1:** on the combined bench, fast's binned SCE proposal scores
  0.788 [0.774, 0.802]. Combined's own proposal scores 0.764 [0.748, 0.781].

**Figure 2. Each detector's version tuned on one stream, scored on every stream's bench (the 3 × 3).**

- Rows give the bench the version was tuned on; columns give the bench it was scored on.
- Each cell is the mean F1 on fresh seeds, on the colorbar's scale (0.6–0.9). The diagonal is bold.
- Compare down a column: the slow bench is easier for almost every detector, so levels do not
  compare between columns.
- The version is the proposal where the stream had one, else the shipped point, and for chorus the
  picked fit. The cells' 95% intervals are in `adoption.json` under `cross_stream`.

![Figure 2](figure2_cross_stream.png)

**Decide:** keep one setting per stream? For combined binned SCE, fast's proposal is at least as good
on combined.

### Decision 3: four shipped points fail a budget, for two different reasons

No limit was loosened (ADR-0009 decision 4).

| stream | detector | budget failed | measured, selection · held-out · fresh | limit |
|---|---|---|---|---|
| fast | SPIKE-synch | precision swing (busy is *higher*) | 0.181 · not recorded · 0.148 | 0.10 |
| fast | rate+context | precision swing (busy is lower) | 0.181 · not recorded · 0.175 | 0.10 |
| combined | rate+context | precision swing | 0.245 · not recorded · 0.257 | 0.15 |
| slow | locust | elevated-rate test, calls per minute inside the stretch | 7.24 · 6.85 · 7.23 (quiet); 4.35 (busy, fresh) | 4.0 |

**Reason 1, the precision swing: the floor, and decoys.**
- Fast SPIKE-synch's swing is decoy calls alone. Without decoy calls its precision is 1.000 on both
  backgrounds.
- As scored, it makes 84 decoy calls on quiet and 23 on busy. Decoys are planted at 6 participants,
  and the busy floor (6–8) blocks most of them where the quiet floor (5–6) does not.
- A 6-participant planted event under the floor is "don't care", while a call on a 6-participant decoy
  under the same floor counts as a false alarm.
- The gate takes the absolute swing, although the budget was written for precision *falling* on busy.
- Fast rate+context's swing is real (0.992 quiet against 0.764 busy without decoys), and setting
  events aside can deepen it.

**Reason 2, slow locust: the new bench layout, not the floor.**
- Locust has no participation minimum, and nothing is planted in the elevated-rate recording, so the
  floor does not reach it.
- Every elevated-rate ceiling was measured with the stretch inside a planted recording, at an older
  stretch rate. ADR-0009 moved it into a recording of its own, at a re-measured rate.
- Shipped slow locust made 1.83 calls per minute in the old layout (seeds 1–8, quiet) and 5.00 in the
  new one. The ceiling of 4.0 was set over the old figure.

Why fast SPIKE-synch and rate+context have no proposal:
- Their shipped points already fail, and so did every neighboring setting the search tried, so it
  had nothing it was allowed to move to.
- The diagnosis is in the darkroom, at
  `bugarach/2026-09-25-final-parameters/064/phase2/DIAGNOSIS-sync-and-rate-moved-nothing.md`.

**Figure 3. The elevated-rate recording, supplied by WSMIP065.**

- The recording is 45 minutes with nothing planted. For 5 of those minutes every ROI's event rate is
  set to one rate: the 99th percentile of real 300 s baseline stretches (0.1334 Hz on fast, 0.0321 Hz
  on slow, 0.1529 Hz on combined). A call there is a false alarm caused by rate.
- The panels of calls per minute inside the stretch are held to their limit on both backgrounds.
- The panels of calls per hour outside it are held to their limit on the quiet background only, so an
  open (busy) marker above its bar there is not a failure.
- The recordings are 12 per background, on seeds 66000–66011.

![Figure 3](figure3_elevated_rate.png)

**Decide:**
- Re-measure the precision-swing and elevated-rate ceilings on the new bench? That would be a new
  ruling, not a loosened limit.
- Should a call on a decoy under the floor be "don't care", like a planted event under the floor?

### Decision 4: much of the planted bench now sits under the floor

Table 3 gives every count.

| stream | busy background, weakest level under the floor | busy background, middle level under the floor |
|---|---|---|
| fast | 120 of 120 (3 participants) | 85 of 120 (6 participants) |
| slow | 50 of 120 (7 participants) | 0 of 120 |
| combined | 120 of 120 (4 participants) | 55 of 120 (8 participants) |

- On the quiet background of fast and combined, the weakest level is entirely under the floor too.
- So on fast and combined, the weakest level no longer counts toward recall.
- ADR-0009 expected a third to a half of fast and combined events to drop out. Fast busy loses 57%.
- Figure 4 re-measures this on seeds 1–8 (a subset of the selection seeds): fast busy middle 25 of 40, combined busy middle 20 of
  40, slow busy weakest 15 of 40.
- In Figure 4, each planted recording's floor sits about one ROI above the no-coordination
  recording's floor on fast and combined, and about three on slow (quiet background). So the planted
  events raise the null that decides which of them count (read off the figure, not measured).
- The elevated-rate recording's floor is 16–20 ROIs on fast and combined, the fact behind the
  uninformative budget checks in Decision 1.

**Figure 4. The bench floors re-measured on the ADR-0009 bench, supplied by WSMIP065.**

- The floor panel gives each recording kind's floor in co-active ROIs, as the range over 8 seeds,
  against the range ADR-0009 expected.
- The share panel gives the planted events under the floor at each participant count, over the same
  8 seeds × 5 events.

![Figure 4](figure4_bench_floors.png)

**Decide:** accept a bench whose weakest level no longer counts toward recall, or change the planted
levels?

### Decision 5: does a value at a hard limit count as bracketed?

Five proposals are held back only because one setting sits at a value that cannot go further:

| stream | detector | the setting at its limit | held-out gain [95%] |
|---|---|---|---|
| fast | locust | minimum run of synchronous frames (`n_synchronous_frames`) = 1 frame | +0.098 [+0.087, +0.110] |
| slow | locust | the same, 1 frame | +0.102 [+0.091, +0.115] |
| combined | locust | the same, 1 frame (moved there from 5) | +0.036 [+0.020, +0.052] |
| slow | rate+context | guard (`guard_sec`) = 0 s | +0.005 [+0.003, +0.007] |
| slow | SPIKE-synch | minimum coincidence (`C_min`) = 0 | +0.043 [+0.035, +0.051] |

- Each of the five passes every budget that was checked.
- On fast and slow, locust's shipped point already sits at 1 frame, so the shipped point would fail
  the same test.
- Slow SPIKE-synch's `C_min` of 0 sits on a measured plateau: every value from 0 to 0.03 gave
  identical calls on seeds 1–48 (`bench_slow.py`).
- Slow SPIKE-synch's proposal also moves its bin `dt` 0.1 → 0.00625 s. That changes how many onsets
  its floor-set minimum counts, so the search is partly tuning how strict the floor is for it.
- Under the strict rule none of the five is adoptable. If a limit counts, all five are, making nine.

**Decide:** does a limit count as a bracket?

### Decision 6: slow binned SCE at the close-events allowance

- Slow binned SCE's proposal (`merge_gap_sec` none → 5 s) gains +0.014 [+0.011, +0.019] held out.
- It loses 0.0207 mean F1 on the close-events test on the held-out seeds, against an allowance of
  0.02. The same statistic read 0.0198 on the selection seeds.
- It is a point estimate on 12 recordings per background, and `bench_slow.py` calls the 0.02
  allowance "still unsigned". So it is at the allowance within noise.

**Decide:** in or out?

## Search rules for next time

These do not change today's adoption set: every proposal they touch is held back for another reason.

### Decision 7: CoactDetect's `alpha` runs to the extension cap

- The search lowered `alpha` as far as it was allowed:
  - fast, 1e-4 → 1.4e-9;
  - combined, 1e-5 → 1.4e-9.
- It gained F1 at each step; on the selection seeds, `alpha` alone gained +0.031 on fast and +0.013
  on combined.
- **Read `alpha` as a z-cutoff, not a probability.** CoactDetect's p-value is a normal-approximation
  tail, so 1e-4 is a cutoff of about 3.7 standard deviations and 1.4e-9 about 5.9. Out there the
  approximation's nominal probability is far below the true tail.
- Held-out gains: fast +0.055 [+0.036, +0.075]; combined +0.039 [+0.026, +0.056]. Neither is
  bracketed. Combined's context is also at 120 s, the longest the bench allows. The search did extend
  it to 240 s, which the validity rule rejected, so the bracketing record does not flag it.
- **Fast CoactDetect does not fail the close-events test.**
  - Table 2 shows the search's verdict (a loss of 0.044), measured against the shipped values in
    their sliding form, which fast does not ship.
  - Against the binned point fast ships, on the same held-out close-events seeds, the loss is 0.0165
    (`review_checks.json`).

**Decide:** stop CoactDetect's grid at a stated z-cutoff?

### Decision 8: context windows under 20 s, and LoCo's own threshold

- ADR-0009 decision 5 lists the context grid as 20, 30, 45, 60, 90 and 120 s. It caps the context at
  120 s and does not say whether a search may go below 20 s.
- The search did go below on fast and combined LoCo, to 10 s and 5 s.
- **Under the floor, LoCo's own threshold decides almost nothing.**
  - Every LoCo search lowered its `threshold_pctile` to the 1st percentile.
  - On combined, the shipped point and a candidate at the 1st percentile made identical calls, and the
    held-out gain was exactly 0 on 48 recordings.
  - The floor, counted in a 2 s window, sits above chance for LoCo's 0.5 s and 1 s windows. So LoCo's
    calls there are the floor's calls.
- Fast LoCo's `threshold_pctile` shows "cap" because all six extensions went down, from the 94th
  percentile to the 1st. Its upper end, 99.99, was never extended.

**Decide:** is 20 s the shortest context? And should LoCo's threshold be searched at all under the
floor?

### Decision 9: the guard cap

- The runbook caps a guard at a quarter of its context window. A guard is a stretch around the
  tested window left out of the background estimate. No ADR records the cap.
- At 20 s and 30 s contexts the cap is 5 s and 7.5 s, so the 8 s guard the slow and combined grids
  carry is excluded there.
- ⚠ Until this report, the cap was never applied to LoCo.
  - The search that could reach an over-cap guard was **fast** LoCo: it moved to a 5 s context in its
    first round (cap 1.25 s), and its guard grid (0.5–4 s) comes after context in the same round.
  - Slow and combined LoCo could have, but their round histories never moved the context off 120 s,
    and their pair grid holds the guard at 0. Per-evaluation settings are not logged, so this is
    read from the histories.
  - Fixed in the same PR as this page, with a test.
  - No LoCo proposal uses a nonzero guard, so no proposal changes. The bracketing records were not
    re-checked.

**Decide:** keep the cap?

## The full tables

**How to read them:**
- **Held-out gain** is the bootstrap median of the proposal's F1 minus the shipped point's, on seeds
  49–96, with a 400-resample interval over recordings. It is biased upward (Decision 1).
- **Fast CoactDetect and LoCo** were searched from the shipped values in their sliding form, while fast
  ships them binned. So their held-out gain, and their "shipped" budgets on the selection and
  held-out seeds, are those of the sliding starting point. Their fresh-seed shipped figures are the
  binned point's.
- **Fresh F1** is on seeds 6000–6023, as scored and without decoy calls, with 2,000-resample
  intervals.
- **Budgets.** A budget that was not measured is named in its cell, never counted as a pass.
- **Bracketed (strict)** lists each open setting with its reason: cap, edge or limit.
- **Chorus** is checked against CoactDetect's limits, the anchor of its training rule.
- **Methods caveats:**
  - The floor is counted in a 2 s co-activity window, whatever window a detector counts in. For wider
    windows (combined CoactDetect's 3 s, binned SCE's 2–10 s bins) chance co-activity is higher than
    the floor assumes. For narrower ones (LoCo's 0.5 s and 1 s), the floor sits above chance.
  - SPIKE-synch's floor-set `min_n` sums coincident onsets over a call's bins, not distinct ROIs, and
    how many it counts depends on the bin `dt`.
  - The floor sets a minimum inside CoactDetect, LoCo, binned SCE and SPIKE-synch. Rate+context,
    locust and chorus have none. They can call events below the floor, and those calls count as false
    alarms.
  - Floor stability, as ADR-0008 asks: on the 144 fresh-seed recordings, the floors from each half of
    the draws match the full floor on 142. The two exceptions are on slow, off by 1 ROI. Seeds 1–96
    were not checked.

**Table 1. Every detector × stream.**

<!-- adoption-table:start (written by tools/make_final_parameters_report.py; do not edit by hand) -->
| stream | detector | settings that change, shipped → proposal | held-out gain in F1 [95% interval] | fresh F1, shipped → proposal [95% interval] | fresh F1 without decoy calls, shipped → proposal | bracketed (strict) | bracketed if a limit counts | adoptable (strict) |
|---|---|---|---|---|---|---|---|---|
| fast | CoactDetect | `alpha` 0.0001 → 1.4e-09; `context_win_sec` 60 s → 30 s; `window_mode` binned → sliding | +0.055 [+0.036, +0.075] (against sliding at the shipped values) | 0.769 [0.755, 0.782] → 0.809 [0.791, 0.831] | 0.981 → 0.956 | no: `alpha` (cap), `guard_sec` (limit) | no | no |
| fast | LoCo | `context_win_sec` 120 s → 20 s; `threshold_pctile` 99.5 percentile → 99.99 percentile; `window_mode` binned → sliding | +0.010 [+0.001, +0.018] (against sliding at the shipped values) | 0.777 [0.755, 0.802] → 0.794 [0.779, 0.809] | 0.946 → 0.989 | no: `threshold_pctile` (cap), `guard_sec` (limit) | no | no |
| fast | binned SCE | `bin_width_sec` 10 s → 2 s; `merge_gap_sec` none (no merge) → 10 s | +0.060 [+0.046, +0.077] | 0.747 [0.729, 0.765] → 0.785 [0.769, 0.802] | 0.953 → 0.981 | yes | yes | **yes** |
| fast | rate+context | none (no proposal) | — | 0.703 [0.678, 0.727] | 0.931 | — | — | — |
| fast | SPIKE-synch | none (no proposal) | — | 0.792 [0.763, 0.823] | 0.899 | — | — | — |
| fast | locust | `sce_min_distance_frames` 4 frames → 128 frames; `sce_percentile` 99.999 percentile → 99.99995 percentile | +0.098 [+0.087, +0.110] | 0.699 [0.682, 0.716] → 0.766 [0.747, 0.786] | 0.954 → 0.995 | no: `n_synchronous_frames` (limit) | yes | no |
| fast | chorus_norm | the fit the training rule picked (training seed 1) | — | 0.773 [0.746, 0.802] | 0.891 | — | — | — |
| fast | chorus_gain_norm | the fit the training rule picked (training seed 4) | — | 0.744 [0.723, 0.766] | 0.883 | — | — | — |
| slow | CoactDetect | none (no proposal) | — | 0.848 [0.838, 0.857] | 1.000 | — | — | — |
| slow | LoCo | `merge_gap_sec` 4 s → 8 s; `null_context_mode` maxlt → symmetric | +0.012 [+0.009, +0.016] | 0.831 [0.824, 0.837] → 0.846 [0.837, 0.855] | 0.996 → 1.000 | no: `threshold_pctile` (cap), `context_win_sec` (edge), `guard_sec` (limit) | no | no |
| slow | binned SCE | `merge_gap_sec` none (no merge) → 5 s | +0.014 [+0.011, +0.019] | 0.818 [0.808, 0.826] → 0.835 [0.824, 0.846] | 0.982 → 0.988 | yes | yes | no |
| slow | rate+context | `merge_gap_s` 3 s → 5 s | +0.005 [+0.003, +0.007] | 0.830 [0.822, 0.837] → 0.834 [0.825, 0.843] | 0.995 → 0.995 | no: `guard_sec` (limit) | yes | no |
| slow | SPIKE-synch | `dt` 0.1 s → 0.00625 s; `max_gap` 4 s → 8 s; `tau_max` 0.5 s → 1 s | +0.043 [+0.035, +0.051] | 0.796 [0.783, 0.807] → 0.845 [0.835, 0.854] | 0.956 → 0.999 | no: `C_min` (limit) | yes | no |
| slow | locust | `sce_min_distance_frames` 4 frames → 256 frames | +0.102 [+0.091, +0.115] | 0.740 [0.726, 0.754] → 0.845 [0.833, 0.857] | 0.914 → 0.974 | no: `n_synchronous_frames` (limit) | yes | no |
| slow | chorus_norm | the fit the training rule picked (training seed 3) | — | 0.825 [0.815, 0.834] | 0.989 | — | — | — |
| slow | chorus_gain_norm | the fit the training rule picked (training seed 3) | — | 0.827 [0.819, 0.834] | 0.993 | — | — | — |
| combined | CoactDetect | `alpha` 1e-05 → 1.4e-09; `int_win_sec` 2 s → 3 s | +0.039 [+0.026, +0.056] | 0.777 [0.763, 0.788] → 0.803 [0.788, 0.818] | 1.000 → 0.978 | no: `alpha` (cap) | no | no |
| combined | LoCo | none (no proposal) | — | 0.804 [0.787, 0.822] | 0.983 | — | — | — |
| combined | binned SCE | `threshold_pctile` 98 percentile → 99 percentile | +0.015 [+0.006, +0.024] | 0.748 [0.731, 0.763] → 0.764 [0.748, 0.781] | 0.950 → 0.960 | yes | yes | **yes** |
| combined | rate+context | `excess_threshold_hz` 4.5 Hz → 6 Hz; `merge_gap_s` 8 s → 16 s | +0.093 [+0.076, +0.113] | 0.683 [0.642, 0.726] → 0.773 [0.748, 0.793] | 0.855 → 0.978 | yes | yes | **yes** |
| combined | SPIKE-synch | `C_threshold` 0.08 → 0.1; `tau_mode` isi_adaptive → fixed | +0.029 [+0.016, +0.043] | 0.761 [0.734, 0.782] → 0.782 [0.768, 0.794] | 0.949 → 0.978 | yes | yes | **yes** |
| combined | locust | `n_synchronous_frames` 5 frames → 1 frames; `sce_percentile` 99.999 percentile → 99.99995 percentile | +0.036 [+0.020, +0.052] | 0.762 [0.745, 0.777] → 0.782 [0.768, 0.796] | 0.982 → 0.979 | no: `n_synchronous_frames` (limit) | yes | no |
| combined | chorus_norm | the fit the training rule picked (training seed 1) | — | 0.778 [0.760, 0.796] | 0.950 | — | — | — |
| combined | chorus_gain_norm | the fit the training rule picked (training seed 0) | — | 0.772 [0.752, 0.793] | 0.940 | — | — | — |
<!-- adoption-table:end -->

**Table 2. Every budget, for the shipped point and the proposal, on each seed set.** "Not checked"
means that seed set has no record of the check. A budget not recorded is named in the cell.

<!-- budget-table:start (written by tools/make_final_parameters_report.py; do not edit by hand) -->
| stream | detector | version | selection seeds 1–48 | held-out seeds 49–96 | fresh seeds 6000–6023 |
|---|---|---|---|---|---|
| fast | CoactDetect | shipped | pass | pass (precision swing not recorded) (the sliding starting point) | pass |
| fast | CoactDetect | proposal | pass | **fail: close-events test** (precision swing not recorded) (close-events against the sliding starting point) | pass |
| fast | LoCo | shipped | pass | pass (precision swing not recorded) (the sliding starting point) | pass |
| fast | LoCo | proposal | pass | pass (precision swing not recorded) (close-events against the sliding starting point) | pass |
| fast | binned SCE | shipped | pass | pass (precision swing not recorded) | pass |
| fast | binned SCE | proposal | pass | pass (precision swing not recorded) | pass |
| fast | rate+context | shipped | **fail: precision swing** | pass (precision swing not recorded) | **fail: precision swing** |
| fast | SPIKE-synch | shipped | **fail: precision swing** | pass (precision swing not recorded) | **fail: precision swing** |
| fast | locust | shipped | pass | pass (precision swing not recorded) | pass |
| fast | locust | proposal | pass | pass (precision swing not recorded) | pass |
| fast | chorus_norm | picked fit | not run | not run | pass (CoactDetect's limits) |
| fast | chorus_gain_norm | picked fit | not run | not run | pass (CoactDetect's limits) |
| slow | CoactDetect | shipped | pass | pass (precision swing not recorded) | pass |
| slow | LoCo | shipped | pass | pass (precision swing not recorded) | pass |
| slow | LoCo | proposal | pass | pass (precision swing not recorded) | pass |
| slow | binned SCE | shipped | pass | pass (precision swing not recorded) | pass |
| slow | binned SCE | proposal | pass | **fail: close-events test** (precision swing not recorded) | pass |
| slow | rate+context | shipped | pass | pass (precision swing not recorded) | pass |
| slow | rate+context | proposal | pass | pass (precision swing not recorded) | pass |
| slow | SPIKE-synch | shipped | pass | pass (precision swing not recorded) | pass |
| slow | SPIKE-synch | proposal | pass | pass (precision swing not recorded) | pass |
| slow | locust | shipped | **fail: elevated-rate test, inside the stretch** | **fail: elevated-rate test, inside the stretch** (precision swing not recorded) | **fail: elevated-rate test, inside the stretch** |
| slow | locust | proposal | pass | pass (precision swing not recorded) | pass |
| slow | chorus_norm | picked fit | not run | not run | **fail: elevated-rate test, inside the stretch** (CoactDetect's limits) |
| slow | chorus_gain_norm | picked fit | not run | not run | pass (CoactDetect's limits) |
| combined | CoactDetect | shipped | pass | pass (precision swing not recorded) | pass |
| combined | CoactDetect | proposal | pass | pass (precision swing not recorded) | pass |
| combined | LoCo | shipped | pass | pass (precision swing not recorded) | pass |
| combined | binned SCE | shipped | pass | pass (precision swing not recorded) | pass |
| combined | binned SCE | proposal | pass | pass (precision swing not recorded) | pass |
| combined | rate+context | shipped | **fail: precision swing** | pass (precision swing not recorded) | **fail: precision swing** |
| combined | rate+context | proposal | pass | pass (precision swing not recorded) | pass |
| combined | SPIKE-synch | shipped | pass | pass (precision swing not recorded) | pass |
| combined | SPIKE-synch | proposal | pass | pass (precision swing not recorded) | pass |
| combined | locust | shipped | pass | pass (precision swing not recorded) | pass |
| combined | locust | proposal | pass | pass (precision swing not recorded) | pass |
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

## Real data

- **The run.** `tools/detect_with_floors.py`, on the 66 recordings of the default dataset
  (`senktide_ttx`: baseline windows followed by senktide, TTX, high K⁺ or wash treatment windows).
  Every treatment window was scored twice, once under its own floor and once under its recording's
  baseline floor.
- **Where it ran.**
  - Run record `065/phase3-real-v3/` in the darkroom, write-up `065/report-inputs/real_data.md`.
  - The code was `879be03`, the head of #814, which seeds every detector that draws random numbers.
    #814 has since merged, with an identical tree, so that code is on `main`.
  - v3 supersedes `065/phase3-real-v2/`, where locust and binned SCE were unseeded (only locust's
    verdicts changed, 4 of them).
- **What it found.** There are 128 treatment windows × 3 streams × 8 detectors = 3,072
  window–stream–detector combinations. A window's floors are per window and stream, so each floor
  difference appears 8 times.
  - The two floors differ in 2,696 combinations.
  - In 498, calls under one floor become no calls under the other.
- **Under senktide, on fast**, the median of each recording's own floor minus its baseline floor is:
  - DI (diestrus) +1 ROI;
  - OVX (ovariectomized) +17;
  - MALE +1;
  - ORX (orchidectomized) +20.

  So the floor rises with senktide mainly in the gonadectomized groups. There, a per-window floor can
  absorb the treatment-window co-activity the project studies.
- **Descriptive only** (FOUNDATIONS §9). It states no treatment effect. It bears on ADR-0008 decision
  4, which asked for both floors "so we can compare".

## Definitions

- **F1.** The harmonic mean of recall and precision. A call matches a planted event when the event lies
  within 2.5 s of the call's span. *Mean F1* averages the quiet and busy backgrounds.
- **Call.** One event a detector reports.
- **Quiet and busy backgrounds.** The bench's two background event rates, taken from the 25th and 75th
  percentiles of real baseline windows.
- **SCE.** Synchronous calcium event.
- **ROI.** Region of interest: one imaged cell.
- **Stream.** The event trace analyzed: fast, slow or combined.
- **Chorus.** The learned detector trained on the bench, in two variants, chorus_norm and
  chorus_gain_norm.
- **Event floor** (ADR-0008). For each window, the larger of 3 ROIs and the smallest number of
  co-active ROIs its own rigid-shift null reaches at most once per hour.
  - The null shifts each ROI's whole event train by up to *J* = 20 s.
  - It uses 1,000 draws and a 2 s co-activity window.
  - A planted event with fewer participants than its recording's floor is **don't care**: it is left
    out of recall, and a call matched to it is left out of precision.
- **No-coordination recording.** A bench recording with background activity and nothing planted.
- **Seed sets.**
  - The search chose on selection seeds 1–48.
  - It picked the proposal on held-out seeds 49–96 (Decision 1).
  - Nothing chose on the fresh seeds: 6000–6023 for the bench, 56000–56011 for the no-coordination
    recording, 66000–66011 for the elevated-rate recording.
- **Budgets:**
  - the elevated-rate test: calls per minute inside its stretch, and calls per hour outside it;
  - the no-coordination recording, in calls per hour;
  - the **precision swing**: the difference in precision between the quiet and busy backgrounds;
  - the **close-events test**: a loss of at most 0.02 mean F1 against the shipped point, on recordings
    whose planted events can be as little as 6 s apart.
- **Decoy** (the glossary's *distractor*). A planted correlated burst labelled as not a coordinated
  event (ADR-0006). F1 *without decoy calls* leaves calls on decoys out of precision.
- **Search terms.**
  - *rounds* moves one setting at a time; *pair* walks a grid over two settings together.
  - A setting is **bracketed** when it lies strictly inside the grid the search walked.
  - The **extension cap** lets the search extend a setting's grid past its end at most 6 times
    (`--max-extensions 6`).
  - An open setting is **cap** (extensions used up), **edge** (at an end for another reason) or
    **limit** (the value cannot go further: 0, or 1 frame).
- **Sliding and binned.** Two ways a detector can count: in a window that slides with each frame, or in
  fixed bins.
- **Context window.** The stretch around each moment over which a detector estimates its background.
- **WSMIP064 and WSMIP065.** The two workstations that ran the night.

## What ran

| phase | where | code | record (darkroom, `bugarach/2026-09-25-final-parameters/`) |
|---|---|---|---|
| 0: the floor and the search (PR B) | #808, #810 | `main` | — |
| 0: the bench (PR A) | #809 | `main` | `065/bench-floor/` (code commit not recorded) |
| 1: pilot, 4 seeds | WSMIP064 | PR B + PR A merged locally, never pushed (`pilot-chorus-prb-only`: PR B alone) | `064/pilot/`, `064/pilot-chorus-prb-only/` |
| 2: fast searches and chorus | WSMIP064 | `main` `b6e40f0` | `064/phase2/` |
| 2: slow and combined searches | WSMIP065 | `main` `b6e40f0` | `065/phase2/` |
| 3: fresh seeds, fast and chorus | WSMIP064 | `main` `a70b185` (#811) | `064/phase3/`, `064/phase3-chorus-slow-combined/` |
| 3: fresh seeds, slow and combined | WSMIP065 | branch `score-candidates-benches` `7af68c9`, before #811 merged | `065/phase3/` |
| 3: the 3 × 3 | WSMIP064 | `main` `723f1e6` (after #812 and #813) | `064/phase3-3x3/` |
| 3: real data | WSMIP065 | `879be03`, #814's head (merged since, same tree); includes #813 | `065/phase3-real-v3/` |
| 4: review checks | WSMIP064 | `tools/final_parameters_review_checks.py` | `064/phase3-3x3/review_checks.json` |
| 4: this page | WSMIP064 | `tools/make_final_parameters_report.py` | `report/` |

- **Searches:** `tools/search_all_settings.py --bench <b> --sliding --max-extensions 6`.
- **Chorus:** `tools/train_learned_on_bench.py --bench <b> --model <m> --seeds 0 1 2 3 4 --device cuda`.
- **Selection budgets** (`064/phase3-3x3/selection_budgets.json`): computed with the search's own
  `Evaluator` and `make_admissible` by a script that is not in the repository. A reviewer recomputed
  every check from the recorded values with the same rule and found no mismatch. That checks the
  arithmetic; it is not an independent measurement.
- **The 3 × 3:** each of the 38 versions (every shipped point, proposal and picked chorus fit; Figure 2
  shows the 24 chosen ones) reproduces its `candidates.json` fresh-seed row exactly when scored on its
  own bench. That is a reproducibility check: both sides come from the same scorer on the same seeds.
- **This page:** `tools/make_final_parameters_report.py --night <darkroom>/bugarach/2026-09-25-final-parameters`
  writes the tables, Figures 1–2 and `adoption.json`.
