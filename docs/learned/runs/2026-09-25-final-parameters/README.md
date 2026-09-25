# The final-parameters night, 2026-09-25: what is adoptable, and what waits on Tony

**Nothing here is adopted.** Every proposal below is a candidate for Tony, and no `bench*.py`
operating point changed. The night followed
[`docs/handoffs/2026-09-25-overnight-final-parameters.md`](../../../handoffs/2026-09-25-overnight-final-parameters.md)
(the runbook), under [ADR-0008](../../../adr/0008-the-event-floor-is-set-per-window-from-its-own-null.md)
and [ADR-0009](../../../adr/0009-the-bench-keeps-its-elevated-rate-test-in-a-recording-of-its-own.md).

**Floor: ADR-0008 per-window floor, bench per ADR-0009**, in every run below. Each simulated
recording's minimum participation is the larger of 3 ROIs and the smallest number of co-active ROIs
its own rigid-shift null reaches at most once per hour (1,000 draws, *J* = 20 s, a 2 s co-activity
window). A planted event with fewer participants than its recording's floor is "don't care": it
leaves recall, and a call on it leaves precision.

## In one paragraph

Four proposals are **adoptable under the runbook's strict rule**: binned SCE on fast; and binned SCE,
rate+context and SPIKE-synch on combined. Each has a held-out gain whose 95% interval is above zero,
passes every budget on selection, held-out and fresh seeds, and sits inside its grid on every axis.
Ten more have a gain above zero but are held back:

- five only because an axis sits at a value that cannot go further: locust on all three streams,
  and rate+context and SPIKE-synch on slow;
- four at the search's extension cap or at a grid edge: CoactDetect on fast and combined, and LoCo
  on fast and slow. Fast CoactDetect also loses too much on the close-events recordings;
- one, binned SCE on slow, only because it loses too much on the close-events recordings.

Four **shipped** points are themselves out of budget under the floor: SPIKE-synch and rate+context
on fast, locust on slow, and rate+context on combined. Six questions go to Tony; they are listed at
the end.

## The adoption table

One row per detector × stream (the stream a version was tuned on), chorus included.

- **held-out gain [95%]** is the search's: mean F1 minus the shipped point's, on seeds 49–96, which
  nothing was chosen on, with a 400-resample bootstrap interval.
- **fresh F1** is on seeds 6000–6023 per background, which neither the search nor the training saw.
  It is given as scored and without decoy calls (calls on decoys left out of precision, ADR-0006).
- **Budgets** are checked three times: on the selection seeds 1–48, with the search's own gate; on
  the held-out seeds; and on the fresh seeds. The checks are:
  - calls per minute inside the elevated-rate stretch (`MAX_PROBE_PER_MIN`, both backgrounds);
  - calls per hour outside it (`MAX_FALSE_POSITIVES_PER_HOUR`), on the quiet background, which is
    the one the budget was measured on;
  - calls per hour on the no-coordination (empty) recording (the same limit);
  - the precision difference between the quiet and busy backgrounds (`MAX_PRECISION_DROP`);
  - on selection and held-out seeds, the close-events recordings (`MAX_CROWDED_DROP`, a loss of at
    most 0.02 mean F1 against the shipped point).

  The held-out rows do not record precision per background, so the precision swing is marked there
  as not recorded, never as passed.
- **Bracketed (strict)** is the runbook's rule: no axis at an end of its final grid. **Bracketed if
  a limit counts** treats an axis at a value that cannot go further (a guard of 0, a threshold of 0,
  one frame) as bracketed. Which rule applies is Tony's decision; *adoptable* uses the strict one.
- **Under the floor** counts planted events on the quiet background of the fresh seeds, by
  participation level. There are 120 events per level: 24 recordings × 5 events.
- **Chorus** rows are the checkpoint each training run's own rule picked. Chorus has no budget of
  its own, so it is checked against CoactDetect's, the training rule's anchor.

<!-- adoption-table:start (written by tools/make_final_parameters_report.py; do not edit by hand) -->
| stream | detector | shipped → proposal (settings that change) | held-out gain [95%] | fresh F1 as scored / without decoys | budgets: selection · held-out · fresh | bracketed (strict) | bracketed if a limit counts | adoptable (strict) | planted events under the floor (quiet, fresh seeds) |
|---|---|---|---|---|---|---|---|---|---|
| fast | CoactDetect | rounds: `alpha` 0.0001 → 1.4e-09; `context_win_sec` 60 → 30 | +0.055 [+0.036, +0.075] | 0.769 → **0.809** / 0.956 | pass · **fail: crowded** (swing not recorded) · pass | no: alpha (cap), guard_sec (limit) | no | no | floors 5–6 ROIs; 10%: 120 under, 20%: 0 under, 30%: 0 under |
| fast | LoCo | pair: `threshold_pctile` 99.5 → 99.99; `context_win_sec` 120 → 20 | +0.010 [+0.001, +0.018] | 0.777 → **0.794** / 0.989 | pass · pass (swing not recorded) · pass | no: threshold_pctile (cap), guard_sec (limit) | no | no | floors 5–6 ROIs; 10%: 120 under, 20%: 0 under, 30%: 0 under |
| fast | binned SCE | rounds: `bin_width_sec` 10 → 2; `merge_gap_sec` none (no merge) → 10 | +0.060 [+0.046, +0.077] | 0.747 → **0.785** / 0.981 | pass · pass (swing not recorded) · pass | yes | yes | **yes** | floors 5–6 ROIs; 10%: 120 under, 20%: 0 under, 30%: 0 under |
| fast | rate+context | shipped; no proposal | — | 0.703 / 0.931 | **fail: precision_swing** · pass (swing not recorded) · **fail: precision_swing** | — | — | — | floors 5–6 ROIs; 10%: 120 under, 20%: 0 under, 30%: 0 under |
| fast | SPIKE-synch | shipped; no proposal | — | 0.792 / 0.899 | **fail: precision_swing** · pass (swing not recorded) · **fail: precision_swing** | — | — | — | floors 5–6 ROIs; 10%: 120 under, 20%: 0 under, 30%: 0 under |
| fast | locust | rounds: `sce_percentile` 99.999 → 99.99995; `sce_min_distance_frames` 4 → 128 | +0.098 [+0.087, +0.110] | 0.699 → **0.766** / 0.995 | pass · pass (swing not recorded) · pass | no: n_synchronous_frames (limit) | yes | no | floors 5–6 ROIs; 10%: 120 under, 20%: 0 under, 30%: 0 under |
| fast | chorus_norm | picked seed1 | — | 0.773 / 0.891 | — · — · pass (CoactDetect's budgets) | — | — | — | floors 5–6 ROIs; 10%: 120 under, 20%: 0 under, 30%: 0 under |
| fast | chorus_gain_norm | picked seed4 | — | 0.744 / 0.883 | — · — · pass (CoactDetect's budgets) | — | — | — | floors 5–6 ROIs; 10%: 120 under, 20%: 0 under, 30%: 0 under |
| slow | CoactDetect | shipped; no proposal | — | 0.848 / 1.000 | pass · pass (swing not recorded) · pass | — | — | — | floors 6–7 ROIs; 21%: 0 under, 38%: 0 under, 63%: 0 under |
| slow | LoCo | rounds: `merge_gap_sec` 4 → 8; `null_context_mode` maxlt → symmetric | +0.012 [+0.009, +0.016] | 0.831 → **0.846** / 1.000 | pass · pass (swing not recorded) · pass | no: threshold_pctile (cap), context_win_sec (edge), guard_sec (limit) | no | no | floors 6–7 ROIs; 21%: 0 under, 38%: 0 under, 63%: 0 under |
| slow | binned SCE | rounds: `merge_gap_sec` none (no merge) → 5 | +0.014 [+0.011, +0.019] | 0.818 → **0.835** / 0.988 | pass · **fail: crowded** (swing not recorded) · pass | yes | yes | no | floors 6–7 ROIs; 21%: 0 under, 38%: 0 under, 63%: 0 under |
| slow | rate+context | rounds: `merge_gap_s` 3 → 5 | +0.005 [+0.003, +0.007] | 0.830 → **0.834** / 0.995 | pass · pass (swing not recorded) · pass | no: guard_sec (limit) | yes | no | floors 6–7 ROIs; 21%: 0 under, 38%: 0 under, 63%: 0 under |
| slow | SPIKE-synch | rounds: `tau_max` 0.5 → 1; `max_gap` 4 → 8; `dt` 0.1 → 0.00625 | +0.043 [+0.035, +0.051] | 0.796 → **0.845** / 0.999 | pass · pass (swing not recorded) · pass | no: C_min (limit) | yes | no | floors 6–7 ROIs; 21%: 0 under, 38%: 0 under, 63%: 0 under |
| slow | locust | rounds: `sce_min_distance_frames` 4 → 256 | +0.102 [+0.091, +0.115] | 0.740 → **0.845** / 0.974 | pass · pass (swing not recorded) · pass | no: n_synchronous_frames (limit) | yes | no | floors 6–7 ROIs; 21%: 0 under, 38%: 0 under, 63%: 0 under |
| slow | chorus_norm | picked seed3 | — | 0.825 / 0.989 | — · — · **fail: probe** (CoactDetect's budgets) | — | — | — | floors 6–7 ROIs; 21%: 0 under, 38%: 0 under, 63%: 0 under |
| slow | chorus_gain_norm | picked seed3 | — | 0.827 / 0.993 | — · — · pass (CoactDetect's budgets) | — | — | — | floors 6–7 ROIs; 21%: 0 under, 38%: 0 under, 63%: 0 under |
| combined | CoactDetect | rounds: `alpha` 1e-05 → 1.4e-09; `int_win_sec` 2 → 3 | +0.039 [+0.026, +0.056] | 0.777 → **0.803** / 0.978 | pass · pass (swing not recorded) · pass | no: alpha (cap) | no | no | floors 6–7 ROIs; 13%: 120 under, 25%: 0 under, 40%: 0 under |
| combined | LoCo | shipped; no proposal | — | 0.804 / 0.983 | pass · pass (swing not recorded) · pass | — | — | — | floors 6–7 ROIs; 13%: 120 under, 25%: 0 under, 40%: 0 under |
| combined | binned SCE | rounds: `threshold_pctile` 98 → 99 | +0.015 [+0.006, +0.024] | 0.748 → **0.764** / 0.960 | pass · pass (swing not recorded) · pass | yes | yes | **yes** | floors 6–7 ROIs; 13%: 120 under, 25%: 0 under, 40%: 0 under |
| combined | rate+context | rounds: `excess_threshold_hz` 4.5 → 6; `merge_gap_s` 8 → 16 | +0.093 [+0.076, +0.113] | 0.683 → **0.773** / 0.978 | pass · pass (swing not recorded) · pass | yes | yes | **yes** | floors 6–7 ROIs; 13%: 120 under, 25%: 0 under, 40%: 0 under |
| combined | SPIKE-synch | rounds: `C_threshold` 0.08 → 0.1; `tau_mode` isi_adaptive → fixed | +0.029 [+0.016, +0.043] | 0.761 → **0.782** / 0.978 | pass · pass (swing not recorded) · pass | yes | yes | **yes** | floors 6–7 ROIs; 13%: 120 under, 25%: 0 under, 40%: 0 under |
| combined | locust | rounds: `sce_percentile` 99.999 → 99.99995; `n_synchronous_frames` 5 → 1 | +0.036 [+0.020, +0.052] | 0.762 → **0.782** / 0.979 | pass · pass (swing not recorded) · pass | no: n_synchronous_frames (limit) | yes | no | floors 6–7 ROIs; 13%: 120 under, 25%: 0 under, 40%: 0 under |
| combined | chorus_norm | picked seed1 | — | 0.778 / 0.950 | — · — · pass (CoactDetect's budgets) | — | — | — | floors 6–7 ROIs; 13%: 120 under, 25%: 0 under, 40%: 0 under |
| combined | chorus_gain_norm | picked seed0 | — | 0.772 / 0.940 | — · — · pass (CoactDetect's budgets) | — | — | — | floors 6–7 ROIs; 13%: 120 under, 25%: 0 under, 40%: 0 under |
<!-- adoption-table:end -->

## Figures

**Figure 1. Fresh-seed F1 for each detector's shipped point and its proposal, by stream.**

- Open circles are the shipped point. Diamonds are the proposal: blue where it is adoptable under
  the strict rule, orange where it is not. Grey diamonds are the chorus fit each training run picked.
- F1 is the mean over the quiet and busy backgrounds, on 24 fresh recordings per background (seeds
  6000–6023).
- A row with a circle only had no proposal.

![Figure 1](figure1_fresh_f1.png)

**Figure 2. The 3 × 3: each detector's version tuned on one stream, scored on every stream's
bench.**

- Rows give the bench the version was tuned on; columns give the bench it was scored on.
- Each cell is the mean F1 on fresh seeds, and the diagonal is bold.
- The version is the proposal where the stream had one, else the shipped point. For chorus it is the
  picked fit.
- The diagonal reproduces each `candidates.json` row to the digit in 38 of 38 cases (a check the
  tool runs), and all 114 cells ran as-is.
- 95% intervals over seeds, and F1 without decoy calls, are in `adoption.json` under
  `cross_stream`.

![Figure 2](figure2_cross_stream.png)

**Figure 3. The elevated-rate recording (ADR-0009 decision 1), from WSMIP065.**

- Top row: calls per minute inside its 300 s stretch. Bottom row: calls per hour outside it.
- 12 recordings per background, on seeds 66000–66011, one column per stream.
- The bar is the budget. The top row's budget applies to both backgrounds; the bottom row's is
  gated on the quiet background only.

![Figure 3](figure3_elevated_rate.png)

**Figure 4. The bench floors re-measured on the ADR-0009 generator, from WSMIP065.**

- Left: each recording kind's floor, in co-active ROIs, as the range over 8 seeds, against the
  range ADR-0009 expected (grey).
- Right: the share of planted events under the floor at each participation level, as
  events under the floor / events planted.

![Figure 4](figure4_bench_floors.png)

## What waits on Tony

Each item is stated once, with its evidence. None is decided here.

1. **Does a value at a hard limit count as bracketed?**
   - Three locust proposals are held back only because `n_synchronous_frames` sits at 1 frame, which
     cannot go lower. Their gains:

     | Stream | Held-out gain [95%] |
     |---|---|
     | fast | +0.098 [+0.087, +0.110] |
     | slow | +0.102 [+0.091, +0.115] |
     | combined | +0.036 [+0.020, +0.052] |

     Each passes every budget.
   - Slow rate+context (`guard_sec` 0) and slow SPIKE-synch (`C_min` 0) are in the same position.
   - Under the strict rule none of the five is adoptable; if a limit counts, all five are.
2. **Four shipped points are out of budget under the floor.** No limit was loosened (ADR-0009
   decision 4).

   | Stream | Detector | Budget failed | Measured | Limit | Measured on |
   |---|---|---|---|---|---|
   | fast | SPIKE-synch | precision swing | 0.181 (selection), 0.148 (fresh) | 0.10 | selection and fresh seeds |
   | fast | rate+context | precision swing | 0.181 (selection), 0.175 (fresh) | 0.10 | selection and fresh seeds |
   | slow | locust | probe (calls per minute inside the stretch) | 7.24 (quiet), 3.69 (busy) | 4.0 | selection seeds |
   | combined | rate+context | precision swing | 0.245 | 0.15 | selection seeds |

   - For fast SPIKE-synch and rate+context this is why their searches moved nothing. With the
     starting point itself inadmissible and no admissible neighbour, the search has nothing to move
     to. The diagnosis is in the run record of phase 2.
3. **CoactDetect's `alpha` runs to the extension cap** on fast (1e-4 → 1.4e-9) and on combined
   (1e-5 → 1.4e-9).
   - With the floor setting `min_rois`, the detector's own significance threshold stops binding, and
     the search keeps lowering it.
   - Both proposals gain: +0.055 [+0.036, +0.075] on fast and +0.039 [+0.026, +0.056] on combined.
   - Neither is bracketed.
   - The fast one also loses 0.044 mean F1 on the close-events recordings on the held-out seeds,
     against an allowance of 0.02.
4. **Fast LoCo's context was extended below the 20 s grid.** The search's round-1 candidate was a
   5 s context, and the reported proposal (the pair grid) uses 20 s with `threshold_pctile` at the
   cap. ADR-0009 decision 5 set 120 s as the longest context and no shortest one.
5. **The guard cap removes 8 s guards on slow and combined.**
   - The runbook caps a guard at a quarter of its context window, and the slow and combined grids
     carry an 8 s guard. At contexts of 20 s and 30 s (quarters of 5 s and 7.5 s) those
     combinations are not searched.
   - The rule is the runbook's, not an ADR's.
6. **Much of the planted bench now sits under the floor on fast and combined** (Figure 4, right).
   - The lowest level is entirely under the floor on both backgrounds: 3 ROIs on fast and 4 on
     combined.
   - On the busy background, part of the middle level is under too: 25 of 40 events on fast
     (6 ROIs) and 20 of 40 on combined (8 ROIs).
   - Recall there is measured on the events chance does not reach, as ADR-0009 anticipated. On
     slow, only 15 of 40 of the lowest level are under, and on busy only.

Smaller items, reported and not decided:

- Slow binned SCE's proposal loses 0.0207 mean F1 on the close-events recordings on the held-out
  seeds, against an allowance of 0.02, so it is not adoptable. Its gain is +0.014 [+0.011, +0.019].
- Slow `chorus_norm`'s picked fit makes 1.43 calls per minute inside the stretch against
  CoactDetect's slow limit of 1.0. Chorus has no budget of its own.

## Real data

The run of the proposals on the 66 recordings (`tools/detect_with_floors.py`), with every window
under both floors, is WSMIP065's and lands in `065/report-inputs/` in the darkroom. It is
descriptive only (FOUNDATIONS §9).

## What ran

| Phase | Where | Code | Record (darkroom, `bugarach/2026-09-25-final-parameters/`) |
|---|---|---|---|
| 0: the floor and the search (PR B) | #808, #810, #812 | `main` | — |
| 0: the bench (PR A) | #809, #811, #813 | `main` | `065/bench-floor/` |
| 1: pilot, 4 seeds | WSMIP064 | PR B + PR A merged locally, never pushed | `064/pilot/` |
| 2: fast searches and chorus | WSMIP064 | `main` `b6e40f0` | `064/phase2/` |
| 2: slow and combined searches | WSMIP065 | `main` | `065/phase2/` |
| 3: fresh seeds, fast and chorus | WSMIP064 | `main` `a70b185` | `064/phase3/`, `064/phase3-chorus-slow-combined/` |
| 3: fresh seeds, slow and combined | WSMIP065 | `main` | `065/phase3/` |
| 3: the 3 × 3 | WSMIP064 | `main` `723f1e6` | `064/phase3-3x3/` |
| 4: this page | WSMIP064 | `tools/make_final_parameters_report.py` | `report/` |

- **Searches:** `tools/search_all_settings.py --bench <b> --sliding --max-extensions 6`, chosen on
  seeds 1–48 and held out on 49–96.
- **Chorus:** `tools/train_learned_on_bench.py --model <m> --seeds 0 1 2 3 4 --device cuda` on each
  bench.
- **This page's table and Figures 1–2:** built by
  `tools/make_final_parameters_report.py --night <darkroom>/bugarach/2026-09-25-final-parameters`,
  which also writes `adoption.json` beside this file.
