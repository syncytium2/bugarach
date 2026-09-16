# Gate 1: does the workstation reproduce the Mac's bake-off?

> **Working material, not murderboarded**, for the sessions running
> [`HANDOFF-workstation-tuning.md`](../../../../HANDOFF-workstation-tuning.md) to review. Every number
> is on **simulated recordings**.

Run 2026-09-16 on the workstation (WSMIP064) by the session that holds branch `tune-learned-vs-coact`.

## Where Gate 1 stands: stopped in step 3, on `chorus_gain_norm`

| step | result |
|---|---|
| 1, at `7fc052d` | Six hand-written detectors exact. `tube` missed 0.02 F1 by 0.0012 on one fold; **Tony ruled it a training difference between machines, not a defect.** |
| 2, at the tip | `tube` identical to step 1. CoactDetect, LoCo and SPIKE-synch still exact against the Mac; locust, rate+context and binned SCE differ, each for a known change. See [*Step 2*](#step-2-this-machines-baseline-at-the-tip). |
| 3, at the tip | `chorus_norm` inside the stop. **`chorus_gain_norm` fired the stop**: on folds 0 and 1 it is further from both Mac seeds than the Mac's own seeds are from each other. `line_length` did not run. See [*Step 3*](#step-3-lone-fit-timings-and-the-stop). |

**What is needed:** a ruling on the `chorus_gain_norm` stop. The sections below say what is known about
it and what is not.

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
| `line_length` | not run | | |

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
- **Whether it is deterministic here.** `tube` was; `chorus_gain_norm` has not been rerun (about 14
  minutes).
- **Whether it is one unlucky draw.** A second training seed here would say whether this machine's
  seed-to-seed spread for `chorus_gain_norm` is wider than the Mac's two seeds suggest; two seeds are a
  thin estimate of a spread.

## Timing: this machine is slower per fit than the Mac

**Table 3.** Seconds per fit, per fold. The Mac's fits ran with 6 to 10 other jobs sharing its CPUs;
the workstation's ran alone.

| model | fold 0 | fold 1 | fold 2 | fold 3 | mean, workstation / Mac |
|---|---|---|---|---|---|
| `tube`, step 1 | 14.1 / 9.1 s | 11.3 / 8.0 s | 11.2 / 8.1 s | 11.3 / 8.2 s | 12.0 / 8.4 s, 1.4× |
| `tube`, step 2 | 13.4 s | 11.1 s | 11.3 s | 11.1 s | 11.7 s |
| `chorus_norm` | 214.7 / 157.5 s | 200.6 / 155.8 s | 198.0 / 160.3 s | 197.7 / 154.5 s | 202.8 / 157.1 s, 1.3× |
| `chorus_gain_norm` | 185.3 / 166.2 s | 211.1 / 171.0 s | 208.2 / 158.7 s | 211.3 / 154.5 s | 204.0 / 162.6 s, 1.25× |

Calibrating the six hand-written detectors in step 1, summed over 4 folds, took 0.95 to 1.6 times the
Mac's: cicada 74.5 s against 45.8 s, coact 30.8 s against 20.8 s, loco 78.5 s against 64.5 s, rate 2.4 s
against 2.5 s, sce 6.9 s against 4.5 s, sync 27.4 s against 23.4 s.

### The estimate, provisional because `line_length` did not run

Per learned model, about 204 fits (144 inner fits and up to 60 outer refits), each averaging 2.3 times
the untuned 900 steps, at this machine's lone untuned fit time. `line_length` has no time from this
machine; it is taken as the Mac's 62.4 s times 1.3.

| model | lone untuned fit | training, CPU hours |
|---|---|---|
| `tube` | 11.7 s | 1.5 |
| `chorus_norm` | 202.8 s | 26.4 |
| `chorus_gain_norm` | 204.0 s | 26.6 |
| `line_length` | about 81 s (assumed) | 10.6 |
| **total** | | **65.1 CPU hours, about 3.0 hours of wall time at 22 jobs** |

**This is a floor, not a forecast**, for two reasons. The 2.3 counts steps only: configurations with
`roi_width` 8, `roi_depth` 6, `width` 16 or `n_scales` 6 cost more per step than the untuned setting, and
nothing has measured by how much. And 22 concurrent fits may each run slower than one fit alone.
Scoring the hand-written grids is minutes. The 9-hour limit leaves room for a threefold overrun on the
floor, which is worth measuring before launch rather than assuming.

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
