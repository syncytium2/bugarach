# The weekend's runs: the fair comparison and its replicate

Two runs of goal 2's fair comparison, the four learned models against the six coded
detectors, tuned under nested cross-validation on the bench:

| folder | machine | launched | what it is |
|---|---|---|---|
| `fair_comparison_2026_09_18/` | WSMIP064 (GPU) | 2026-09-18 16:14 | the first draw |
| `replicate1/` | WSMIP065 | 2026-09-18 | the same design on a second draw of recordings, 857 min, 1,968 jobs |

## What is in the repo, and what is only in Dropbox

Tony, 2026-09-21: *"backup all the results from the weekends run. these should probably be in
the repo and dropbox."* Every file from both runs is in Dropbox. The repo holds everything
except the two bulk folders:

| | repo (here) | Dropbox (`<darkroom>/bugarach/…/results/`) |
|---|---|---|
| `results.json`, `meta.json`, `ran.json`, `progress.json` | ✓ | ✓ |
| `selections/`: which configuration each fold chose | ✓ | ✓ |
| `configs/`: every configuration drawn | ✓ | ✓ |
| `chosen/`: **the chosen models**, 160 checkpoints per run (4 nets × 2 selections × 4 outer folds × 5 training seeds), plus each coded detector's chosen `detector_settings.csv` per fold | ✓ | ✓ |
| `fits/`: every fit, all configurations (about 3,880 files) | — | `fits.tar.gz` (first draw), `fits.zip` (replicate) |
| `scores/`: every fit's score rows (1.1 GB unpacked) | — | `scores.tar.gz` (first draw), `scores.zip` (replicate) |

The Dropbox folders are `2026-09-18-fair-comparison-run/results/` and
`2026-09-18-replicate-run-status/results/`. The bulk folders stay out of git because they are
large (146 MB and 1.1 GB unpacked per run), this repository is public, and it does not use Git
LFS. Nothing reads them except a re-selection, such as `tools/tune_net_merge_gap.py`.

**A chosen checkpoint runs on real data as it is**, e.g.
`bugarach detect <folder> --model replicate1/chosen/gated/outer0/chorus_gain_norm/seed2.json`.
Each one was trained on one outer fold's synthetic training recordings, so there is no single
final model. Say which fold and seed was used, and why.

Copied 2026-09-21 from WSMIP065's `~/runs/bench-replicate1` and from the darkroom. The
fair comparison's `results.json` here is byte-identical to the darkroom copy, and so is the
replicate's.
