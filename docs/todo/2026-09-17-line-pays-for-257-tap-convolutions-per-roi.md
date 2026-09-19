---
status: open
filed: 2026-09-17
---

# `line` pays for a 257-tap convolution on every ROI, and nothing here trains on a GPU

**The concern** (raised to Tony, 2026-09-17): the learned models are not built to use a GPU. It
holds for the counting family and not for `tube`, and the larger saving may be in the code rather
than the device.

## What was measured

One training step (Adam, batch of 3 crops, 4,096 frames each) on an Apple M4 Pro, torch 2.14.0,
one CPU thread against the Apple GPU (MPS), with
[`tools/bench_learned_step.py`](../../tools/bench_learned_step.py) (the same measurement, committed
after the fact; it also finds a CUDA GPU).

| model | ROIs | CPU, 1 thread | GPU (MPS) | GPU speedup |
|---|---|---|---|---|
| `tube` | 32 | 12.7 ms | 14.7 ms | 0.9× |
| `line` | 32 | 173 ms | 18.5 ms | 9.4× |
| `line_bound` | 32 | 827 ms | 80 ms | 10.3× |
| `tube` | 80 | 15.3 ms | 9.6 ms | 1.6× |
| `line` | 80 | 420 ms | 39 ms | 10.6× |
| `line_bound` | 80 | 1,877 ms | 189 ms | 10.0× |

⚠ **The CPU column was timed while 12 training processes were running** on the same 14-core
machine, so it is inflated by an unknown amount. Repeat on an idle machine before quoting it.

In the rigid-shift report's training run (`tools/tube_self_supervised.py`, 2026-09-17), the
gradient steps were **91–97 % of each `line`-family fit's wall time**, and a fit trained against
rigid shift took about 310 s for `line`, 1,300 s for `line_bound` and 27 s for `tube`. Evaluation
is not where the time goes.

## Why

`tube` averages over ROIs **before** its first kernel, so it convolves one channel. `line` smooths
**every ROI on its own**, at four widths, with a kernel of `2k + 1` taps where `k` is
`max_center_frames` (128): 257 taps per ROI per width, forward and backward
(`src/bugarach/learn/nets/line.py`, `forward`). `line_bound` adds a second grouped 257-tap
convolution per ROI to bound each vote in time, and rebuilds `_one_onset_mass` on every forward.

Most of those taps multiply numbers near zero. The smear widths start at 1, 2, 4 and 8 frames
(`log_smear`), so a kernel cut at ±4 standard deviations would be 9–65 taps. The widths are
learnable and clamped at `k / 2`, so the cut would have to follow the fitted width, not be fixed.
The difference-of-Gaussians surround (up to 64 frames wide) does need the full support, but it runs
on the ROI-averaged count, which is cheap.

## What would help, in the order worth trying

1. **Size the per-ROI kernels to the width they carry.** Helps CPU and GPU alike, needs no device
   plumbing, and likely cuts `line`'s main cost several-fold. It **changes results** slightly (the
   dropped tails are below 3 × 10⁻⁴ of the peak at ±4 standard deviations), so it needs a test that
   the truncated forward matches the full one within a stated tolerance, and every quoted `line`
   number re-measured, not assumed unchanged.
2. **An optional device for training and scoring** (`train`, `tools/fair_bakeoff.py`,
   `tools/tube_self_supervised.py`, `tools/tube_ssl_real_compare.py`, and the tuning tool on
   `tune-learned-vs-coact`). Default stays CPU.
3. **Measure throughput, not step time.** A sweep runs 12 or more fits at once on the CPU and the
   GPU is one device. On one stream the table above gives the GPU no clear win for a sweep (about 54
   steps per second for `line` on the GPU against about 70 across 12 CPU workers; about 12.5 against
   14.5 for `line_bound`). What has not been measured: several processes sharing the GPU, or `tube`
   on the CPU and the `line` family on the GPU.

## ⚠ The constraint any change must respect: numbers must stay regenerable

`src/bugarach/learn/train.py` pins torch to **one thread** because the thread count changed
results: the published bake-off reproduced only on a 10-thread machine, and at 1, 2 or 4 threads
the same seeds gave a mean F1 0.0178 higher, with one fold moving from 45 to 62 detections. A GPU
changes reduction order at least as much, and is nondeterministic on some operations. So:

- a device choice is **recorded** wherever training settings are: the checkpoint's `training`
  block (`src/bugarach/learn/checkpoint.py`, which already records `threads`) and each run's
  provenance;
- a number produced on a GPU is **not compared** against one produced on the CPU as if the two
  were the same measurement;
- a run whose numbers a report quotes stays on one device from start to finish. The rigid-shift
  report's 2026-09-17 rerun was deliberately left on the CPU for this reason.

## Where it would pay first

The 064 tuning run (`tools/tune_learned_vs_coact.py` on branch `tune-learned-vs-coact`) fits many
`line` models, and its latest commit on that branch records the run as about four times slower than
its planned floor. Check what hardware WSMIP064 has before assuming the Apple numbers above carry
over: a CUDA GPU would need its own measurement.
