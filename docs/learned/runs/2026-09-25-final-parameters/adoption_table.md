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

| stream | background | floors (co-active ROIs) | planted events under the floor, by participation level (of 120 per level: 24 recordings × 5 events) |
|---|---|---|---|
| fast | quiet | 5–6 | 10% (3 ROIs): 120, 20% (6 ROIs): 0, 30% (10 ROIs): 0 |
| fast | busy | 6–8 | 10% (3 ROIs): 120, 20% (6 ROIs): 85, 30% (10 ROIs): 0 |
| slow | quiet | 6–7 | 21% (7 ROIs): 0, 38% (12 ROIs): 0, 63% (20 ROIs): 0 |
| slow | busy | 7–8 | 21% (7 ROIs): 50, 38% (12 ROIs): 0, 63% (20 ROIs): 0 |
| combined | quiet | 6–7 | 13% (4 ROIs): 120, 25% (8 ROIs): 0, 40% (13 ROIs): 0 |
| combined | busy | 7–10 | 13% (4 ROIs): 120, 25% (8 ROIs): 55, 40% (13 ROIs): 0 |
