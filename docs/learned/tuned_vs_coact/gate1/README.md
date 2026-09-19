# Gate 1: does the workstation reproduce the Mac's bake-off?

> **Working material, not murderboarded**, for the sessions running
> [`HANDOFF-workstation-tuning.md`](../../../../HANDOFF-workstation-tuning.md) to review. Every number
> is on **simulated recordings**.

Run 2026-09-16 on the workstation (WSMIP064) by the session that holds branch `tune-learned-vs-coact`.

## Where Gate 1 stands: complete; one design question open

| step | result |
|---|---|
| 1, at `7fc052d` | Six hand-written detectors exact. `tube` missed 0.02 F1 by 0.0012 on one fold; **Tony ruled it a training difference between machines, not a defect.** |
| 2, at the tip | `tube` identical to step 1. CoactDetect, LoCo and SPIKE-synch still exact against the Mac; locust, rate+context and binned SCE differ, each for a known change. See [*Step 2*](#step-2-this-machines-baseline-at-the-tip). |
| 2, redone on sliding CoactDetect and LoCo | **The baseline this run uses** (Tony: *"use sliding versions. redo step 2"*). The other four hand-written detectors and `tube` equal the binned step 2 exactly. Sliding CoactDetect scores mean F1 0.681 and LoCo 0.687, against 0.645 and 0.653 binned. See [*Step 2, redone*](#step-2-redone-on-sliding-coactdetect-and-loco). |
| 3, at the tip | `chorus_norm` inside the stop. **`chorus_gain_norm` fired the stop** on folds 0 and 1 at seed 0. **Rerun:** deterministic; seed 1 passes; this machine's seeds differ by up to 0.078 F1 against the Mac's 0.032, and seed-averaged the machines agree within 0.007 F1, so seed 0 was a low draw. `line_length` passes, but trains 3.3 times slower than on the Mac. See [*Step 3*](#step-3-lone-fit-timings-and-the-stop). |

**What is needed:** how many training seeds each configuration's inner score averages. At one seed, the
declared design, seed noise alone puts about 0.04 F1 of scatter between two configurations; see
[*The reruns*](#the-reruns-deterministic-and-a-low-draw) and, for the cost,
[*The estimate*](#the-estimate-from-this-machines-lone-fits).

## Step 1: result and ruling

- **All six hand-written detectors match the Mac exactly**: every per-fold result field, in all 4
  folds.
- **`tube` does not match within 0.02 F1.** Its largest per-fold difference is **0.0212 F1**, 0.0012
  over the tolerance. The handoff's first wording stopped on it; Tony ruled it a training difference
  between machines, not a defect, and kept the hard stop for the six only.
- **On this machine `tube` is deterministic.** A second run gave identical output, field for field.
- **Why the trained models differ is not known.** Two causes are open: torch computing different
  floats on this CPU than on the Mac's, and the Mac's uncommitted changes. See
  [*What is known about the `tube` difference*](#what-is-known-about-the-tube-difference).

Abbreviations: **F1**, harmonic mean of recall and precision; **WSL**, Windows Subsystem for Linux.
Detector names in the tables are the code's: `cicada` is locust, `coact` CoactDetect, `loco` LoCo,
`rate` rate+context, `sce` binned SCE (synchronous calcium events), `sync` SPIKE-synch.

## What ran

Step 1 as the handoff specifies: `tools/fair_bakeoff.py` in a detached worktree at `7fc052d`, the home
spec, 4 folds of 6 recordings (seeds 1000–1023), `--null-rates`, `--learned tube`, torch training seed
0. One process, nothing else running on the machine.

| run | files | wall time |
|---|---|---|
| step 1: six hand-written detectors and `tube` | [`step1_7fc052d_six_tube/bakeoff.json`](step1_7fc052d_six_tube/bakeoff.json), [log](step1_7fc052d_six_tube.log) | 5 min 13 s |
| rerun of `tube` alone (`--skip-hand-written`), for determinism | [`step1b_7fc052d_tube_rerun/bakeoff.json`](step1b_7fc052d_tube_rerun/bakeoff.json), [log](step1b_7fc052d_tube_rerun.log) | 1 min 6 s |

The Mac's reference is
[`../../field_size_candidates/bakeoff.json`](../../field_size_candidates/bakeoff.json), with training seed
1 in [`bakeoff_seed1.json`](../../field_size_candidates/bakeoff_seed1.json) beside it. Both are unchanged
between `7fc052d` and this branch. Comparisons were made by
[`tools/compare_bakeoff_runs.py`](../../../../tools/compare_bakeoff_runs.py); its full output is in
[`compare_step1_vs_mac.txt`](compare_step1_vs_mac.txt) and
[`compare_step1b_rerun_vs_step1.txt`](compare_step1b_rerun_vs_step1.txt).

**Checked before running.**
- **The code under test is the Mac's committed code.** The Mac's file records commit `239f176`, from a
  working tree with uncommitted changes. Between `239f176` and `7fc052d`, the committed code the six
  and `tube` use is identical: `bench.py`, `score.py`, `simulate.py`, `detectors/`, `learn/train.py`,
  `learn/encode.py` and `learn/nets/tube.py`. `tools/fair_bakeoff.py` only gained model registrations
  and `--skip-hand-written`.
- **The worktree imports its own code.** It runs with the primary checkout's venv and
  `PYTHONPATH=<worktree>/src`, and `bugarach.__file__` resolved inside the worktree.

## The six hand-written detectors: an exact match

"Exact" means every per-fold result field is equal: F1, recall, precision, hits, detections, events
scored, busy-window false alarms, distractor hits, recall by participation fraction, quiet-field false
alarms per hour at twin factors 1.0, 0.54 and 0.25, and the calibrated knob value. Only wall times
differ.

**Table 1.** Held-out F1 and calibrated knob per fold, identical on both machines.

| detector | knob | knob per fold (0, 1, 2, 3) | F1 per fold (0, 1, 2, 3) |
|---|---|---|---|
| cicada | `sce_percentile` | 99.9, 99.9, 99.9, 99.9 | 0.553055, 0.571429, 0.539474, 0.555932 |
| coact | `alpha` | 1e-4, 1e-4, 1e-3, 1e-4 | 0.659898, 0.669903, 0.621277, 0.630000 |
| loco | `threshold_pctile` | 99, 99, 99, 99 | 0.650485, 0.676329, 0.630137, 0.654028 |
| rate | `excess_threshold_hz` | 3 Hz, 3 Hz, 3 Hz, 3 Hz | 0.607477, 0.587156, 0.580087, 0.600000 |
| sce | `threshold_pctile` | 80, 80, 80, 80 | 0.431579, 0.515152, 0.449761, 0.460000 |
| sync | `C_threshold` | 0.08, 0.04, 0.04, 0.04 | 0.222222, 0.267857, 0.319328, 0.273504 |

**So the recordings, the detectors, the scorer and the null twins are the same on both machines**, and
the Mac's uncommitted changes did not touch anything these six use.

## `tube`: outside the tolerance

**Table 2.** `tube` at training seed 0 on both machines, with the Mac's training seed 1 for scale. Busy-
window false alarms are counts over the fold's 6 recordings; quiet-field false alarms are per hour, on
the 0.54 twins.

| fold | F1, workstation | F1, Mac | difference, F1 | F1, Mac training seed 1 | threshold, workstation / Mac | hits, workstation / Mac | detections, workstation / Mac | busy-window false alarms, workstation / Mac | quiet-field false alarms per hour, workstation / Mac |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.6509 | 0.6544 | −0.0034 | 0.6829 | 0.9948 / 0.9908 | 69 / 71 | 147 / 149 | 25 / 22 | 2.72 / 3.40 |
| 1 | 0.6697 | 0.6909 | **−0.0212** | 0.6781 | 0.9838 / 0.9838 | 74 / 76 | 217 / 205 | 86 / 75 | 2.89 / 2.89 |
| 2 | 0.6178 | 0.6231 | −0.0053 | 0.5627 | 0.9908 / 0.9716 | 80 / 81 | 249 / 272 | 80 / 102 | 2.38 / 3.06 |
| 3 | 0.6635 | 0.6566 | +0.0069 | 0.6172 | 0.9948 / 0.9908 | 70 / 65 | 174 / 160 | 53 / 52 | 0.85 / 0.00 |

The mean over the 4 folds is 0.6505 F1 on the workstation and 0.6563 F1 on the Mac, a difference of
−0.0058 F1.

### What is known about the `tube` difference

**Known:**
- **It is not run-to-run noise here.** The rerun reproduced every field of every fold, thresholds to
  the last digit.
- **The trained weights differ, not only the threshold pick.** In fold 1 both machines picked threshold
  0.9838, and hits, detections and false alarms still differ. In folds 0, 2 and 3 the picked thresholds
  differ too.
- **The inputs are the same.** Table 1 shows the recordings and the scorer agree, and the handoff
  records that recordings 1000, 1013 and 1023 hash identically at `7fc052d` and at the branch tip.
- **The gap is small against training-seed spread.** On the Mac, training seeds 0 and 1 differ per fold
  by +0.0285, −0.0128, −0.0603 and −0.0394 F1. The largest workstation gap, 0.0212 F1, is about a third
  of the Mac's largest seed-to-seed gap.

**Not known:**
- **Which cause it is.** Torch 2.14.0+cpu on an x86 CPU can compute different floats than torch on the
  Mac's arm64 CPU, and 900 training steps can amplify a small difference. Or the Mac's uncommitted changes may
  have touched training. The Mac's file records neither its torch version nor its diff, so the two
  cannot be told apart from the record.
- **Whether the other three models differ by more.** `chorus_norm`, `chorus_gain_norm` and
  `line_length` are step 3, which has not run.

**The ruling (Tony, 2026-09-16).** Accept the `tube` miss as a training difference between machines:
every comparison with the Mac's learned numbers says so, and tuned against untuned is compared on this
machine. Recorded facts: the committed training code is identical between `239f176` and `7fc052d`, and
the Mac recorded neither its torch version nor its uncommitted changes, so CPU float differences cannot
be separated from those changes.

## Step 2: this machine's baseline, at the tip

The six and `tube` at `cc8171a`, which has `main` through #597 merged in. 6 min 25 s.
[`step2_tip_six_tube/bakeoff.json`](step2_tip_six_tube/bakeoff.json), [log](step2_tip_six_tube.log),
[`environment.json`](step2_tip_six_tube/environment.json) (the torch version, which `fair_bakeoff.py`
does not record); comparisons in [`compare_step2_vs_mac.txt`](compare_step2_vs_mac.txt) and
[`compare_step2_tube_vs_step1.txt`](compare_step2_tube_vs_step1.txt).

- **`tube` at the tip is identical to `tube` at `7fc052d`**, field for field. The merges changed nothing
  `tube` trains or is scored on.
- **CoactDetect, LoCo and SPIKE-synch are still exact against the Mac.** #597 widened their grids, and
  on these folds calibration picks the same knob values from the wider grids.
- **Locust, rate+context and binned SCE differ, each for a known change:**

**Table 4.** The three hand-written detectors that differ at the tip, per fold.

| detector | knob per fold, tip / Mac | F1 per fold, tip | F1 per fold, Mac | known change |
|---|---|---|---|---|
| cicada | 99.95, 99.95, 99.95, 99.95 / 99.9 on all 4 | 0.5690, 0.5517, 0.5299, 0.5126 | 0.5531, 0.5714, 0.5395, 0.5559 | #594: events held active for their own width; #597 added 99.95 to the grid |
| rate | 3.5 Hz on all 4 / 3 Hz on all 4 | 0.6364, 0.6070, 0.6000, 0.6162 | 0.6075, 0.5872, 0.5801, 0.6000 | #597 added 3.5 Hz to the grid |
| sce | 80, 80, 80, 75 / 80 on all 4 | 0.5684, 0.6263, 0.5263, 0.5586 | 0.4316, 0.5152, 0.4498, 0.4600 | #593: calls scored over their whole bin; #597 extended the grid below 75 |

## Step 2, redone on sliding CoactDetect and LoCo

Tony, 2026-09-16: *"use sliding versions. redo step 2."* Branch `sliding-loco-coact` (`005ae98`, not on
`main`) is merged at `425ab2e`, and `OPERATING_POINTS` runs CoactDetect and LoCo with
`window_mode="sliding"`, the exact null computed rather than drawn, at the values tuned binned. The
first step 2 above stays as the binned baseline.

Run at `2c58092`, 4 min 34 s:
[`step2b_sliding_six_tube/bakeoff.json`](step2b_sliding_six_tube/bakeoff.json),
[log](step2b_sliding_six_tube.log), [`environment.json`](step2b_sliding_six_tube/environment.json);
comparison with the binned step 2 in [`compare_step2b_vs_step2.txt`](compare_step2b_vs_step2.txt).

- **Everything that should not have moved did not.** Locust, rate+context, binned SCE, SPIKE-synch and
  `tube` equal the binned step 2 on every result field.
- **Sliding CoactDetect and LoCo are deterministic.** Their calls on recordings 1000, 1013 and 1023 are
  identical under two different `rng_seed` values (the null draws no random numbers), checked in
  process with [`sliding_determinism.py`](sliding_determinism.py).
- **They have no Mac reference**, so this is this machine's baseline, not a reproduction.
- **Tests after the merge:** 118 of 120 pass across `test_sliding_window.py`, `test_bench.py`,
  `test_loco_detect.py`, `test_coact_detect.py` and `test_fair_bakeoff_transfer.py`. The 2 failures are
  the ones the sliding branch already records: at the binned-tuned values, sliding LoCo's precision swings
  0.13 between backgrounds and CoactDetect's 0.11, against a budget of 0.10
  (`test_precision_survives_the_regime_shift`).

**Table 6.** Sliding against binned, per fold, at each detector's calibrated knob. Busy-window false
alarms are counts over the fold's 6 recordings; quiet-field false alarms are per hour on the 0.54 twins;
calibration seconds are for the fold.

| detector | fold | F1, sliding / binned | knob, sliding / binned | precision, sliding / binned | recall, sliding / binned | detections, sliding / binned | busy-window false alarms, sliding / binned | quiet-field false alarms per hour, sliding / binned | calibration, sliding / binned |
|---|---|---|---|---|---|---|---|---|---|
| coact | 0 | 0.6603 / 0.6599 | 1e-5 / 1e-4 | 0.580 / 0.607 | 0.767 / 0.722 | 122 / 110 | 3 / 3 | 2.72 / 2.55 | 4.9 / 10.7 s |
| coact | 1 | 0.7222 / 0.6699 | 1e-5 / 1e-4 | 0.619 / 0.595 | 0.867 / 0.767 | 126 / 116 | 0 / 0 | 4.94 / 2.55 | 4.8 / 10.6 s |
| coact | 2 | 0.6761 / 0.6213 | 1e-5 / 1e-3 | 0.585 / 0.503 | 0.800 / 0.811 | 123 / 151 | 0 / 6 | 2.89 / 2.72 | 4.6 / 10.2 s |
| coact | 3 | 0.6667 / 0.6300 | 1e-5 / 1e-4 | 0.590 / 0.573 | 0.767 / 0.700 | 119 / 112 | 2 / 2 | 2.55 / 2.04 | 4.9 / 10.6 s |
| loco | 0 | 0.6914 / 0.6505 | 99.5 / 99 | 0.549 / 0.578 | 0.933 / 0.744 | 168 / 125 | 15 / 9 | 2.89 / 2.38 | 7.5 / 26.8 s |
| loco | 1 | 0.7130 / 0.6763 | 99.5 / 99 | 0.586 / 0.598 | 0.911 / 0.778 | 151 / 121 | 11 / 4 | 4.43 / 2.04 | 7.5 / 26.4 s |
| loco | 2 | 0.6193 / 0.6301 | 99.9 / 99 | 0.570 / 0.535 | 0.678 / 0.767 | 108 / 137 | 1 / 8 | 1.36 / 1.36 | 7.1 / 25.5 s |
| loco | 3 | 0.7241 / 0.6540 | 99.5 / 99 | 0.592 / 0.570 | 0.933 / 0.767 | 156 / 128 | 14 / 7 | 2.89 / 0.68 | 7.5 / 26.0 s |

Means over the 4 folds: CoactDetect **0.6813 F1 sliding** against 0.6453 binned; LoCo **0.6870 F1
sliding** against 0.6527 binned. CoactDetect's `alpha` of 1e-5 and LoCo's 99.5 and 99.9 are interior
points of their grids. Sliding CoactDetect calibrates in about 0.46 times binned's time and LoCo in about
0.28 times, which also shortens the hand-written side of the tuning run.

**What this does to the margin the tuning run tests, before any tuning.** Untuned, one training seed,
this machine: the learned models' F1 from step 3 and step 1, minus sliding CoactDetect's, per fold. This
is a description of the starting point, not a result.

| model | − sliding CoactDetect, folds 0, 1, 2, 3 (F1) | mean (F1) |
|---|---|---|
| `chorus_norm` | +0.0841, +0.0201, +0.0402, +0.0975 | +0.0605 |
| `chorus_gain_norm` | +0.0100, −0.0247, +0.0011, +0.0923 | +0.0197 |
| `tube` | −0.0093, −0.0525, −0.0583, −0.0032 | −0.0308 |

Against binned CoactDetect on the Mac the handoff's table showed `chorus_norm` +0.103 and
`chorus_gain_norm` +0.084, averaged over two seeds; part of that lead was the binned reference.

## Step 3: lone-fit timings, and the stop

One model per process at the tip, nothing else running. The stop (Tony, 2026-09-16): halt if on any
fold a model's F1 is further from **both** Mac seeds than the Mac's own largest per-fold seed-to-seed
gap for that model, from
[`learned_vs_coact.json`](../../field_size_candidates/learned_vs_coact.json); or on the failed-training
signature, F1 near 0.125 at threshold 0.0001. The check is [`check_step3.py`](check_step3.py), and its output
per model is in `check_step3_<model>.txt` here.

| model | wall time | files | verdict |
|---|---|---|---|
| `chorus_norm` | 14 min 2 s | [`step3_tip_chorus_norm/`](step3_tip_chorus_norm/bakeoff.json), [log](step3_tip_chorus_norm.log), [check](check_step3_chorus_norm.txt) | no stop |
| `chorus_gain_norm` | 14 min 8 s | [`step3_tip_chorus_gain_norm/`](step3_tip_chorus_gain_norm/bakeoff.json), [log](step3_tip_chorus_gain_norm.log), [check](check_step3_chorus_gain_norm.txt) | **stop, folds 0 and 1** |
| `line_length` | 14 min 12 s, after Tony lifted the stop (*"go for it"*) | [`step3_tip_line_length/`](step3_tip_line_length/bakeoff.json), [log](step3_tip_line_length.log), [check](check_step3_line_length.txt) | no stop: F1 0.7378, 0.7321, 0.6532, 0.7042, each within 0.022 of a Mac seed (Mac seed gap 0.0472) |

**Table 5.** Per-fold F1 at training seed 0 on this machine against both Mac seeds. The Mac's largest
seed-to-seed gap is 0.0358 F1 for `chorus_norm` and 0.0316 F1 for `chorus_gain_norm`.

| model | fold | F1, workstation | F1, Mac seed 0 (difference) | F1, Mac seed 1 (difference) | threshold, workstation / Mac seed 0 / Mac seed 1 |
|---|---|---|---|---|---|
| `chorus_norm` | 0 | 0.7444 | 0.7568 (−0.0124) | 0.7570 (−0.0126) | 0.9716 / 0.9716 / 0.9908 |
| `chorus_norm` | 1 | 0.7424 | 0.7489 (−0.0065) | 0.7847 (−0.0423) | 0.9838 / 0.9716 / 0.9500 |
| `chorus_norm` | 2 | 0.7163 | 0.6932 (+0.0231) | 0.6935 (+0.0227) | 0.9908 / 0.9838 / 0.9716 |
| `chorus_norm` | 3 | 0.7642 | 0.7656 (−0.0014) | 0.7890 (−0.0248) | 0.9838 / 0.9908 / 0.9838 |
| `chorus_gain_norm` | 0 | 0.6703 | 0.7256 (**−0.0553**) | 0.7203 (**−0.0501**) | 0.9908 / 0.9908 / 0.9716 |
| `chorus_gain_norm` | 1 | 0.6975 | 0.7545 (**−0.0571**) | 0.7624 (**−0.0649**) | 0.9500 / 0.9500 / 0.9838 |
| `chorus_gain_norm` | 2 | 0.6772 | 0.7193 (−0.0421) | 0.6885 (−0.0114) | 0.9838 / 0.9838 / 0.9838 |
| `chorus_gain_norm` | 3 | 0.7589 | 0.7488 (+0.0101) | 0.7172 (+0.0418) | 0.9838 / 0.9838 / 0.9838 |

Means over the 4 folds: `chorus_norm` 0.7418 F1 here against 0.7411 and 0.7561 F1 on the Mac;
`chorus_gain_norm` **0.7010 F1** here against 0.7371 and 0.7221 F1 on the Mac. `chorus_norm`'s thresholds here
differ from the Mac's seed 0 on 3 of 4 folds, and it stays inside the stop.

### What is known about the `chorus_gain_norm` stop

**Known:**
- **It is not the operating point.** On all 4 folds this machine picked **the same threshold as the
  Mac's seed 0**, so the lower F1 comes from the trained weights. On fold 0, at the same threshold 0.9908,
  recall is 0.689 here against 0.867 on the Mac.
- **0.95 is not an edge.** Fold 1's threshold is an interior point of `pick_threshold`'s grid, and the Mac's
  seed 0 picked it too.
- **The committed code on its path did not change.** Between the Mac's commits for these files
  (`3bf3271` for seed 0, `af407f2` for seed 1) and the tip, `learn/nets/chorus.py`,
  `learn/nets/chorus_gain_norm.py`, `learn/nets/__init__.py`, `learn/train.py` and `learn/encode.py` are
  identical. `score.py` changed, only for detections that carry `extent_sec`, which learned detections
  do not. The recordings are unchanged (step 2's exact matches, and the hashes in the handoff).
- **It is not the failed-training signature.** No fold is near F1 0.125, and no threshold is at 0.0001.
- **`chorus_norm`, the same architecture without the vote gain, is inside the stop** and matches the
  Mac's mean.

**Not known:**
- **Whether it is this machine's floats or the Mac's uncommitted changes.** Both Mac files come from
  working trees with uncommitted changes, and neither records a torch version.
- ~~Whether it is deterministic here~~ and ~~whether it is one unlucky draw~~: both answered by the
  reruns below.

### The reruns: deterministic, and a low draw

Tony, 2026-09-16, on the recommendation to rerun before going on: *"do it"*. At `e823335`, one process
at a time, nothing else running:
[`step3b_chorus_gain_norm_seed0_rerun/`](step3b_chorus_gain_norm_seed0_rerun/bakeoff.json) (training seed
0 again, 14 min 30 s, [log](step3b_chorus_gain_norm_seed0_rerun.log)) and
[`step3c_chorus_gain_norm_seed1/`](step3c_chorus_gain_norm_seed1/bakeoff_seed1.json) (training seed 1,
14 min 57 s, [log](step3c_chorus_gain_norm_seed1.log)).

- **Deterministic.** Seed 0 again equals step 3 on every result field, every fold
  ([`compare_step3b_seed0_rerun_vs_step3.txt`](compare_step3b_seed0_rerun_vs_step3.txt)).
- **Seed 1 passes the stop.** Every fold is within 0.0294 F1 of one Mac seed or the other
  ([`check_step3_chorus_gain_norm_seed1.txt`](check_step3_chorus_gain_norm_seed1.txt)).
- **This machine's seeds are further apart than the Mac's.** Its largest per-fold seed-to-seed gap is
  **0.0779 F1**, against the Mac's 0.0316 F1. The Mac's two seeds understated the spread, and seed 0 here
  is a low draw inside it.
- **Seed-averaged, the two machines agree within 0.007 F1**: 0.7226 here, 0.7296 on the Mac.

**Table 7.** `chorus_gain_norm` per fold, both training seeds, both machines.

| fold | F1, workstation seed 0 | F1, workstation seed 1 | seed 1 − seed 0, workstation | F1, Mac seed 0 | F1, Mac seed 1 | seed 1 − seed 0, Mac | threshold, workstation seed 1 / Mac seed 1 |
|---|---|---|---|---|---|---|---|
| 0 | 0.6703 | 0.7373 | +0.0670 | 0.7256 | 0.7203 | −0.0052 | 0.9838 / 0.9716 |
| 1 | 0.6975 | 0.7753 | **+0.0779** | 0.7545 | 0.7624 | +0.0078 | 0.9500 / 0.9838 |
| 2 | 0.6772 | 0.7179 | +0.0408 | 0.7193 | 0.6885 | −0.0308 | 0.9838 / 0.9838 |
| 3 | 0.7589 | 0.7464 | −0.0125 | 0.7488 | 0.7172 | −0.0316 | 0.9948 / 0.9838 |
| mean | 0.7010 | 0.7442 | | 0.7371 | 0.7221 | | |

**What it means for the stop.** The stop measured distance in units of the Mac's seed-to-seed gap, and
for `chorus_gain_norm` two Mac seeds put that unit at 0.0316 F1 when this machine shows it can be at
least 0.078 F1. The stop fired on a real low draw, not on a defect. Against sliding CoactDetect (step 2,
redone), `chorus_gain_norm` seed-averaged leads by +0.0435, +0.0142, +0.0215 and +0.0860 F1 per fold,
mean **+0.0413 F1**; seed 0 alone had put it at +0.020.

**What it means for the tuning design: how noisy a one-seed selection is.** The handoff picks each
learned model's configuration by its inner score at training seed 0 only. From the 20 per-fold
seed-to-seed gaps available (two seeds of each of the four models on the Mac, and `chorus_gain_norm`'s
two here), a one-seed F1 on a fold of 6 recordings scatters by a standard deviation of about 0.026. The
inner score pools 3 inner folds, each its own fit, and two configurations are scored on the same
recordings, so the seed noise in the difference between two configurations' inner scores is:

**Table 9.** Seed noise in a selection, by seeds averaged per configuration
([`seed_noise.py`](seed_noise.py), output in [`seed_noise.txt`](seed_noise.txt)).

| seeds per configuration | standard deviation of a difference between two configurations | two standard deviations |
|---|---|---|
| 1 | 0.021 F1 | 0.042 F1 |
| 2 | 0.015 F1 | 0.030 F1 |
| 3 | 0.012 F1 | 0.024 F1 |
| 5 | 0.009 F1 | 0.019 F1 |

So at one seed, two configurations whose true inner scores differ by less than about 0.04 F1 are not
reliably ordered. How far apart the 24 configurations truly are has not been measured. Two consequences
hold either way:
- **The reported numbers stay honest.** Nested cross-validation scores the chosen configuration on a fold
  the choice never saw, at 5 seeds, so noise in the choice can pick a worse configuration but cannot
  inflate what is reported.
- **The noise falls on one side only.** The hand-written detectors are deterministic, so their selection
  carries no seed noise. A noisy learned selection can only cost the learned models, which biases the
  comparison against them.

## Timing: this machine is slower per fit than the Mac

**Table 3.** Seconds per fit, per fold. The Mac's fits ran with 6 to 10 other jobs sharing its CPUs;
the workstation's ran alone.

| model | fold 0 | fold 1 | fold 2 | fold 3 | mean, workstation / Mac |
|---|---|---|---|---|---|
| `tube`, step 1 | 14.1 / 9.1 s | 11.3 / 8.0 s | 11.2 / 8.1 s | 11.3 / 8.2 s | 12.0 / 8.4 s, 1.4× |
| `tube`, step 2 | 13.4 s | 11.1 s | 11.3 s | 11.1 s | 11.7 s |
| `chorus_norm` | 214.7 / 157.5 s | 200.6 / 155.8 s | 198.0 / 160.3 s | 197.7 / 154.5 s | 202.8 / 157.1 s, 1.3× |
| `chorus_gain_norm` | 185.3 / 166.2 s | 211.1 / 171.0 s | 208.2 / 158.7 s | 211.3 / 154.5 s | 204.0 / 162.6 s, 1.25× |
| `line_length` | 211.3 / 68.3 s | 202.8 / 60.5 s | 206.5 / 60.6 s | 195.4 / 60.3 s | 204.0 / 62.4 s, **3.3×** |

Calibrating the six hand-written detectors in step 1, summed over 4 folds, took 0.95 to 1.6 times the
Mac's: cicada 74.5 s against 45.8 s, coact 30.8 s against 20.8 s, loco 78.5 s against 64.5 s, rate 2.4 s
against 2.5 s, sce 6.9 s against 4.5 s, sync 27.4 s against 23.4 s.

**`line_length` is the outlier: 3.3 times the Mac's.** Its fits took 211.3, 202.8, 206.5 and 195.4 s
here (mean 204.0 s) against 68.3, 60.5, 60.6 and 60.3 s on the Mac (mean 62.4 s), and detection on a
fold took 2.1 to 2.3 s against 0.45 to 0.58 s, about 4.7 times. The other models run 1.25 to 1.4 times
the Mac's. Why is not known; nothing has profiled it. It now costs as much as either `chorus` model.

### The estimate, from this machine's lone fits

Per learned model, the inner fits are 6 fold pairs × 24 configurations × *k* training seeds, plus up to
60 outer refits (5 seeds × 4 folds × the untuned setting and each selection's choice). Each fit averages
2.3 times the untuned 900 steps and is costed at this machine's lone untuned fit time: `tube` 11.7 s,
`chorus_norm` 202.8 s, `chorus_gain_norm` 204.0 s, `line_length` 204.0 s.

**Table 8.** Training cost by the number of training seeds each configuration's inner score averages.

| seeds per configuration (*k*) | fits per learned model | training, CPU hours | wall time at 22 jobs |
|---|---|---|---|
| 1, as the handoff declares | 204 | 80.9 | **3.7 hours** |
| 2 | 348 | 138.4 | **6.3 hours** |
| 3 | 492 | 195.7 | **8.9 hours** |

**These are floors, not forecasts**, for two reasons. The 2.3 counts steps only: configurations with
`roi_width` 8, `roi_depth` 6, `width` 16 or `n_scales` 6 cost more per step than the untuned setting, and
nothing has measured by how much. And 22 concurrent fits may each run slower than one fit alone. Scoring
the hand-written grids is minutes.

## The machine

WSMIP064: WSL2 with Ubuntu 26.04 on an Intel Xeon w7-2495X, 24 physical and 48 logical CPUs, 96 GB
of memory given to WSL. Python 3.14.4, torch 2.14.0+cpu. The Mac's file
records macOS 26.6.2 on arm64 with Python 3.14.5, and no torch version.

## Reproduce

From a detached worktree at `7fc052d`, with the primary checkout's venv:

```bash
PYTHONPATH=$PWD/src ~/bugarach/.venv/bin/python -u tools/fair_bakeoff.py \
  --spec docs/learned/generator_spec.json --seeds-per-fold 6 --null-rates \
  --out ~/runs/gate1/step1_7fc052d_six_tube --learned tube
python tools/compare_bakeoff_runs.py ~/runs/gate1/step1_7fc052d_six_tube/bakeoff.json \
  docs/learned/field_size_candidates/bakeoff.json
```

The logs here have the home directory replaced by `~` (sapper SAP004).
