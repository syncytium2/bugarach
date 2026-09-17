---
status: open
filed: 2026-09-17
---

# Two bake-off folds train the same model

> **Found** by the fourth blind murderboard of the rigid-shift report (role 1, Prove It), 2026-09-17,
> and confirmed in the main thread. Tony ruled the same day to file it here rather than fix it on the
> report's branch.

## What

`bugarach.learn.train.fold_maker` gives the **last `n_val`** training recordings to threshold
validation and fits on the rest. On the bake-off's default split (`bench.fold_split`, 4 folds of 2
recordings, seeds 1000–1007) with `n_val = 2`, the validation block is exactly one whole fold, and it is
always the **last** training fold. So:

| held-out fold | fit on | threshold on |
|---|---|---|
| 1 (1000, 1001) | 1002–1005 | 1006, 1007 |
| 2 (1002, 1003) | 1000, 1001, 1004, 1005 | 1006, 1007 |
| 3 (1004, 1005) | **1000–1003** | 1006, 1007 |
| 4 (1006, 1007) | **1000–1003** | 1004, 1005 |

Held-out folds 3 and 4 fit on the same four recordings, at the same training seed, so they are **the
same model** (the rigid-shift run's saved parameters are identical in 15 of 15 model and seed pairs).
Folds 1 and 2 share their threshold recordings. A four-fold bake-off therefore holds three distinct
fitted models per seed, not four.

## Why it matters

- **Fold counts overstate independence.** "Four folds" of a learned model are three fits scored on four
  held-out pairs.
- **The Nadeau–Bengio correction** used in the rigid-shift report assumes distinct training sets per
  fold; its ratio of test to training size does not describe this split.
- **A margin carried by one fold** (the rigid-shift report's third fold) is that shared model scored on
  its own held-out recordings, which is not what "one fold of four" suggests.
- **It applies wherever `seeds_per_fold == n_val`**: `tools/fair_bakeoff.py`, `tools/ablate_tube.py`,
  `src/bugarach/lab.py`, `tools/probe_*`, `tools/run_learned_on_folder.py`. The 24-seed bake-off
  (6 recordings per fold) is not affected in this way, because its validation block is part of one fold.

It does **not** leak a held-out recording into fitting or threshold-picking; the held-out fold is still
unreachable from `fold_maker`.

## Options

- Rotate the validation block with the held-out fold (for example, validate on the fold after the
  held-out one), so every held-out fold has its own fitting set.
- Validate on part of every training fold rather than one whole fold.
- Keep the split and state it: three fits per seed, with the statistics adjusted.

Any change alters every learned bake-off number: models retrain and the bake-offs rerun. Rows in
`docs/MILESTONES.md` section C that quote bake-off margins cite runs made with this split.

## Closes when

Tony chooses an option, the harness changes (or the split is documented where every bake-off states its
fold count), and the bake-offs that quote fold-level statistics are rerun or annotated.
