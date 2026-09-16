# Gate 1, step 1: does the workstation reproduce the Mac's bake-off?

> **Working material, not murderboarded**, for the sessions running
> [`HANDOFF-workstation-tuning.md`](../../../../HANDOFF-workstation-tuning.md) to review. Every number
> is on **simulated recordings**.

Run 2026-09-16 on the workstation (WSMIP064) by the session that holds branch `tune-learned-vs-coact`.

## Result: stopped, one ruling needed

- **All six hand-written detectors match the Mac exactly**: every per-fold result field, in all 4
  folds.
- **`tube` does not match within 0.02 F1.** Its largest per-fold difference is **0.0212 F1**, 0.0012
  over the tolerance. The handoff says to stop and report either way, so **steps 2 and 3 have not
  run.**
- **On this machine `tube` is deterministic.** A second run gave identical output, field for field.
- **Why the trained models differ is not known.** Two causes are open: torch computing different
  floats on this CPU than on the Mac's, and the Mac's uncommitted changes. See
  [*What is known about the `tube` difference*](#what-is-known-about-the-tube-difference).

**The ruling needed.** Either accept the difference as training that differs across machines, say so in
every comparison with the Mac's learned numbers, and run steps 2 and 3; or keep the stop and find
where the floats part first. **This session recommends accepting it**, for the reasons in that section.

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
  Mac's arm64 CPU; SGD amplifies a small difference over 900 steps. Or the Mac's uncommitted changes may
  have touched training. The Mac's file records neither its torch version nor its diff, so the two
  cannot be told apart from the record.
- **Whether the other three models differ by more.** `chorus_norm`, `chorus_gain_norm` and
  `line_length` are step 3, which has not run.

**Why this session recommends accepting it.** The handoff's own fallback already covers it: a gap means
"this machine's training is not the Mac's, and every comparison with the Mac's numbers must say so",
and the tuned-versus-untuned comparison is made on this machine regardless. Tracking the float
difference down would cost more than the decision it informs: the tuning run never compares a tuned
number with the Mac's.

## Timing: this machine is slower per fit than the Mac

**Table 3.** Seconds per `tube` fit, per fold. The Mac's fits ran with 6 to 10 other jobs sharing its
CPUs; the workstation's ran alone.

| fold | workstation, step 1 | workstation, rerun | Mac |
|---|---|---|---|
| 0 | 14.1 s | 13.0 s | 9.1 s |
| 1 | 11.3 s | 11.5 s | 8.0 s |
| 2 | 11.2 s | 11.7 s | 8.1 s |
| 3 | 11.3 s | 11.5 s | 8.2 s |

Calibrating the six hand-written detectors, summed over 4 folds, took 0.95 to 1.6 times the Mac's:
cicada 74.5 s against 45.8 s, coact 30.8 s against 20.8 s, loco 78.5 s against 64.5 s, rate 2.4 s
against 2.5 s, sce 6.9 s against 4.5 s, sync 27.4 s against 23.4 s.

**This moves the overnight estimate.** The handoff estimates about 2.5 hours of training wall time from
the Mac's times, and warns those times are *inflated*. If every model scales like `tube` did (about 1.4
times the Mac's), training alone is about 3.5 hours at 22 jobs, before scoring, and still under the
9-hour limit. Step 3's lone-fit times replace this guess.

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
