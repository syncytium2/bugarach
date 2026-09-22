---
status: open
filed: 2026-09-21
priority: immediate — first thing after the 2026-09-22 meeting
---

# Move the bench's participation from 0.18 to 0.19, the day after the meeting

## The ruling

Tony, 2026-09-21: keep the bench at 0.18 for now, and make the move to 0.19 an immediate
todo after the meeting on 2026-09-22. Held until then so the meeting discusses the
synthetic dataset, the optimization and training runs, and the leaderboard exactly as
they were produced.

## Why it moves

`bench.BENCH_RECORDING["participation"]` is `(0.30, 0.18, 0.10)`, and its middle level
is the only measured value outside its bootstrap interval. `bench.MEASURED_OUTSIDE_INTERVAL`
records it: *0.18 held; 0.1905 measured, interval 0.1818 – 0.2322*. The 0.1818 lower end
is 6/33, the ratio the docstring derives and then rounds to 0.18. So this is a rounding,
not a moved measurement.

Measured on the new default dataset (`2026-09-17_revised_2v_long_STEPS_AND_PINS_EXCLUDED`)
on 2026-09-21 with `tools/remeasure_bench.py --folder … --no-write`, it is the same value:

| value | bench | steps_excluded (recorded) | new default |
|---|---|---|---|
| participation | 0.18 | 0.1905 (0.1818 – 0.2322), outside | 0.1905 (0.1818 – 0.2322), outside |

The other seven bench values are inside their intervals on both folders and agree to the
fourth decimal. Removing the pinned windows moved nothing that matters.

## What moving it costs

The synthetic benchmark is drawn from these constants, so changing one changes the
synthetic data, and everything scored on them has to be rerun:

| step | recorded duration |
|---|---|
| bench re-measure on the default, writing the record | ≈ 1.5 min (the dry run took 1 min 33 s) |
| every-knob settings search | 10 – 13 min per run (five runs, 2026-09-17) |
| replicate run, WSMIP065 | 857 min ≈ 14.3 h, 1,968 jobs |
| fair-comparison training run, WSMIP064 | ≈ 14 h, floor 11.7 GPU-hours |

The two long runs can go in parallel on the two workstations, so it is one overnight.

## Steps

1. Set the middle level of `BENCH_RECORDING["participation"]` to 0.19, and decide
   whether its 0.30 / 0.10 spread moves with it (the docstring's spread is around the
   measured median).
2. Remove the `participation` entry from `MEASURED_OUTSIDE_INTERVAL`.
3. Move `bench.MEASURED_ROLE` to the default dataset (`dataset.default_role()`) and
   re-measure with `tools/remeasure_bench.py`, which writes `docs/learned/bench_measured.json`
   with the new folder in it. `tests/test_bench_is_measured_on_the_declared_folder.py`
   pins the role and must move with it. Remove the bench's entries from
   `ROLE_LITERAL_ALLOWED` in `tests/test_where_the_data_are.py`.
4. Rerun the search, then the training and the replicate.
5. Stamp every result with `"dataset": dataset.stamp()`, so that
   `tools/check_scored_dataset.py` reads them as scored on the default. Today it reads
   0 of 18.
6. Rebuild the leaderboard (`tools/leaderboard.py`) from the new run files.

## Where the pieces are

- `src/bugarach/bench.py` — `BENCH_RECORDING`, `MEASURED_OUTSIDE_INTERVAL`, `MEASURED_ROLE`
- `tools/remeasure_bench.py` — its `--folder` dry run sits uncommitted in the
  `opt-assess-revised-export` worktree as of 2026-09-21
- `docs/goals/README.md` decision 1, and PR #692 (one default dataset, confirmed each session)
