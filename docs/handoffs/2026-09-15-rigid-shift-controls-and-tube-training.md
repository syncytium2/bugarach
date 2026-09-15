# Handoff — rigid-shift controls, and tube trained against rigid shift

**Written 2026-09-15, before a planned loss of internet. Nothing is running.** Branch
`unsup/rigid-shift-controls`, stacked on `main` after #584 (the rigid-shift look's murderboard
record and correction banner). Goal page: [`docs/goals/unsupervised-learning.md`](../goals/unsupervised-learning.md).
Exploratory throughout; **none of this is murderboarded** and the goal page does not yet carry it.

## Where it stands, in one paragraph

The murderboard of the rigid-shift look found its large-displacement "leak" and its Cossart
destruction result unsound. Tony asked for the missing experiments; they reversed the look's
reading. Rigid shift leaves **no per-ROI trace** a classifier can find at any displacement on either
folder, and it **removes planted coordination from about 10 s**. Tony then asked to test the tube
models. Stage 1 showed tube's own input channel carries no count or edge leak under rigid shift,
so Stage 2 trained `tube` and `tube_guard` with rigid shift as the only negative. They learned to
tell real from shifted on held-out mice without leaking, but **scored no better than an untrained
tube** on the planted-truth bake-off. **The decision waiting on Tony is what to do next** (bottom).

## The controls (`tools/look_rigid_shift_controls.py`)

Results: [`learned/rigid_shift_look/controls/`](../learned/rigid_shift_look/controls/) (`lab/`, `cossart/` results and
meta, two figures).

**Figure 1, leak against a shared offset** (`controls_fig1_leak.png`). Every ROI of a recording
moved by one offset keeps cross-ROI alignment and moves each ROI's drift exactly as rigid shift
does. It reads chance everywhere:
- **Shared offset:** 0.49–0.53 on lab fast, lab slow and Cossart, to 40–45 s. Cossart at 20 s is
  0.528, with an upper bound of 0.550.
- **Rigid shift:** climbs only where there is shared slow structure to remove:
  - lab slow: 0.550 at 22.4 s and 0.561 at 44.8 s;
  - Cossart: 0.58–0.60 from 10 s;
  - lab fast: flat at 0.50.
- **Seeds:** the rigid-shift points reproduce the look exactly at its own seeds, and are shown as
  the mean over 10 fold seeds.
- **The DI group at 44.8 s:** 0.668 under rigid shift, 0.521 under the shared offset.

**Figure 2, Cossart destruction at its measured participation** (8.1 % of 566 ROIs, K = 6–24,
`controls_fig2_cossart_destruction.png`):
- **Retained share by displacement:**
  - 1.6 s: 0.52–0.83;
  - 5 s: 0.32–0.39 (K ≤ 12);
  - 10 s: 0.06–0.11;
  - 20 s: ≈ 0.
- **Graded `freeze_half` control:** 0.41–0.49 on Cossart and 0.25–0.47 on the lab folder where
  events are visible, so the measure can register partial removal.
- **Onsets dropped over the whole window:** about 0.5 % at 10 s, 1 % at 20 s and 2 % at 40–45 s.
  Single sparse lab recordings lose far more (to 21 %).

**Scientific decision still open for Tony:** rigid shift at *J* also removes shared modulation
faster than *J*. That structure is real and detectable on lab slow and Cossart, but not on lab
fast. Does it count as coordination?

## Stage 1 — tube's aggregate channel (`tools/tube_aggregate_leak.py`)

Results: [`learned/tube_self_supervised/aggregate_leak/`](../learned/tube_self_supervised/aggregate_leak/). A linear forced
choice on tube's cells-mean trace through its own centre-surround kernels (0.1–12.8 s), lab
folder.

- **Real vs shared offset:** chance (0.49–0.53), though window counts move 3–24 %.
- **Unplanted twin vs rigid shift:** chance (0.44–0.55).
- **Planted twin vs rigid shift:** 0.84–0.94.
- **Real vs rigid shift:** 0.64–0.69.
  - Fast: strongest at 0.1–0.4 s kernels (0.66–0.68), falling to 0.51–0.56 at 12.8 s.
  - Slow: flat across scales.

This is the aggregate-channel test that
[the tube foot-gun todo](../todo/2026-09-12-tube-cannot-tell-a-count-leak-from-coordination.md)
names; it passed for rigid shift on this folder. **Update that todo** when this lands.

## Stage 2 — tube trained against rigid shift (`tools/tube_self_supervised.py`)

Results: [`learned/tube_self_supervised/training/`](../learned/tube_self_supervised/training/) (`results.jsonl`, 144 fits;
`tube_ssl_fig.png`).

- **Objective:** a ranking loss on the mean of the top 1 % of per-frame logits, real crop against
  the same crop rigid-shifted.
- **Training:** crops of 4,096 frames kept more than *J* from the recording ends; *J* = 10 and 20 s;
  900 steps at the bake-off's learning rates.
- **Scoring:** the bake-off's held-out folds (generator spec `docs/learned/generator_spec.json`,
  4 folds of 2 recordings), 3 torch seeds.
- **Thresholds are chosen in logit space**, because the ranking loss saturated the sigmoid.

| arm | oracle F1, tube | oracle F1, tube_guard | label-free F1 (≤ 2 events per 10 min on rigid shift) |
|---|---|---|---|
| supervised, same run | 0.67 | 0.65 | 0.63–0.64 |
| untrained | 0.51 | 0.44 | 0.07–0.10 |
| no labels, simulated | 0.38–0.41 | 0.34–0.46 | 0.12–0.29 |
| no labels, real lab | 0.43–0.49 | 0.44–0.49 | 0.26–0.31 |

- **Spread:** single fits range from 0.1 to 0.7.
- **Fits that never learned:** 25–33 % of runs on simulated recordings stayed at chance loss
  (log 2).
- **Checks on held-out mice**, for the arms trained on real recordings:
  - real vs shared offset: 0.49–0.53;
  - unplanted twin vs rigid shift: 0.51–0.57;
  - real vs rigid shift: 0.73–0.76.
- **Kernel widths:** the smallest fitted centre width is 0.06–0.11 s without labels, against
  0.24–0.27 s supervised. The simulator's event jitter is 0.31 s.
- **Useful on its own:** a threshold set from the recording's own rigid shift works for the
  supervised model (0.63–0.64, against oracle 0.65–0.67).

**Not shown:** that label-free training cannot work.
- The objective, pooling, learning rate and steps are untuned.
- The benchmark is a simulator whose event width differs from what the models trained on real
  recordings latched onto.
- Only the lab fast stream was tested.

## Defects found and fixed along the way (all in the committed tools)

- **Cossart destruction** first ran as one task. At Cossart's measured K one excess call takes about
  37 s, so it would have taken about 15 hours; it is now split into one task per draw.
- **The label-free threshold** first accepted a whole-recording merged detection as one event. It
  now scans down from the top.
- **The paired checks** first counted ties as losses. A shared offset only translates a crop, and
  tube is a convolution, so ties are common; they now count half.
- **Thresholds** were first taken on sigmoid probabilities, which saturate under the ranking loss.
  They are now taken on logits.
- **Process kill:** when the first controls run was stopped, workers were killed with a broad
  `pkill -f multiprocessing.spawn`. A process list 8 minutes earlier showed only this run's
  workers, but the gap is unproven.

## Not done yet

- **The rigid-shift note is not rewritten.** It still carries its correction banner, and the rewrite
  and a blind murderboard round wait on Tony's timescale decision.
- **The goal page does not mention** the controls, Stage 1 or Stage 2.
- **Figures** are in `<darkroom>/bugarach/` at the top level, placed by `tools/show.py`
  (`controls_fig1_leak.png`, `controls_fig2_cossart_destruction.png`,
  `tube_aggregate_fig.png`, `tube_ssl_fig.png`), and in the repo folders above.
- **No PR is open for this branch.**

## The decision waiting on Tony

Three options were put to him, the first recommended:

1. **Run the trained models on real baselines** and compare their detections with CoactDetect and
   LoCo. This asks whether "learned something real" is coordination or a lab-specific artefact.
   It is cheap, but the Stage 2 run did not save checkpoints, so it needs a re-fit (about
   3 minutes).
2. **Fix the objective's scale:** bounded scores and a minimum kernel width near 0.31 s, as one
   matched run.
3. **Stop**, and record the result as a negative on the goal page.

## Rerun

- **Controls:** `tools/look_rigid_shift_controls.py`, about 3 minutes on the lab folder and about
  80 minutes on Cossart at 12 workers.
- **Stage 1:** `tools/tube_aggregate_leak.py`, under a minute.
- **Stage 2:** `tools/tube_self_supervised.py`, about 3 minutes.
- **Environment:** all in the Elephant venv
  (`bugarach-worktrees/surrogate-screen-overnight-venv`, which has torch 2.14), with
  `PYTHONPATH=<worktree>/src`.
- **Figures:** `tools/make_rigid_shift_controls_figure.py`, `tools/make_tube_aggregate_figure.py`
  and `tools/make_tube_ssl_figure.py`.
