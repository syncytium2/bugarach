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

Results: ⚠ **that folder was overwritten by the overnight re-run** and now holds 288 rows over four
architectures, reported in [`learned/tube_self_supervised/README.md`](../learned/tube_self_supervised/README.md).
This stage's own 144 fits over `tube` and `tube_guard` are no longer on disk; the numbers below are
what it found. ⚠ **`line` in this page means the length-only build**, which the report calls
`line_length`.

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

## Option 1, run after the internet returned — the trained models on real recordings

Tony chose option 1. The tools are `tools/tube_ssl_real_compare.py` and
`tools/make_tube_real_lanes.py`.

**Data and training.**
- **What is kept:** the summary, per-recording event times and seed-0 checkpoints are in
  [`learned/tube_self_supervised/real_compare/`](../learned/tube_self_supervised/real_compare/).
- **Folds:** the models trained against rigid shift were refitted per mouse fold, so every
  recording is called by a model that never saw its mouse.
- **Detectors:** they were run beside supervised tube, CoactDetect and LoCo on all 84 lab
  fast-stream baselines.
- **Threshold:** label-free, at most 2 events per 10 minutes on the recording's own rigid shift.

**Results, trained without labels (supervised in brackets).**
- **Rate:** 5.7–6.6 events per 10 minutes (4.6–5.0). CoactDetect fires 2.7 and LoCo 2.6.
- **Coverage:** 67–77 % of CoactDetect and LoCo events are caught at *J* = 10 s, and 36–55 % at
  *J* = 20 s (80–87 %). Chance is about 10 %.
- **Precision against the hand-written calls:** 18–28 % of their own events land within 1 s of a
  CoactDetect or LoCo event (31–47 %). Chance is about 5 %.
- **Participation within ±1 s, away from window edges:** median 2–3 ROIs, and 40–52 % of events
  involve 3 or more (median 5, 85–89 %). At random times, 19–33 % reach 3.
- **Timing:** the offset from the nearest CoactDetect event is spread across ±5 s, where
  supervised tube is locked at +0.5 to +2 s from the CoactDetect onset.
- **Fragmentation:** 13–22 % of CoactDetect events carry two or more of their events within
  ±5 s (2–6 %).
- **Events far from any hand-written call** (more than 5 s): 51–53 % (44–45 %).
- **Not a crosstalk artefact:** the most frequent ROI pair's share is 0.25–0.33, no more
  concentrated than supervised tube's 0.33–0.5.
- **Not an edge artefact:** only 3–4 % of their events sit within 5 s of a window edge.

**Figures** (darkroom only, because they hold real rasters):
`<darkroom>/bugarach/archive/2026-09/tube_real_lanes_20250827_199_baseline.png` and `..._zoom.png`.

**Reading.** They are a real but weaker coordination detector, not an artefact detector. They
find most of the bursts the hand-written detectors find, but about half of their calls sit on
two ROIs or fewer, they break single bursts into several calls, and their timing is not locked
to the burst.

## `line`, the architecture Tony's question produced

Tony asked whether the weak precision is a limit of tube's architecture, and proposed *"an
orientation detector rather than a center-surround … when most rois fire it looks like a vertical
line. two rois aren't enough and noise/high background looks like fuzz"*.

**The limit is real and measured.** `tools/probe_line_vs_fuzz.py` plants, on a quiet synthetic
field, a **line** (K distinct ROIs in one frame), a **burst** (K/4 ROIs firing 4 times: the same
ink) and **fuzz** (K ROIs over 3 s), and scores each model by its peak response minus the same
field unplanted.

| model | line ÷ burst at K = 16 | line ÷ fuzz at K = 16 |
|---|---|---|
| supervised tube | 1.34 | 1.43 |
| supervised tube_guard | 1.31 | 1.34 |
| trained against rigid shift (15 live fits) | 2.23 (1.48–3.29) | 4.90 (3.41–7.36) |
| a detector that counted distinct ROIs | 4 | about 8–16 |

⚠ The untrained models scored 0.00 on every plant here, so **the untrained baseline in the Stage 2
table needs rechecking** — a model that does not respond to a planted line should not have scored
F1 0.51.

**`src/bugarach/learn/nets/line.py`** is that idea made order-free, because row order is a
coordinate and a literal oriented filter would read the encoder's sort. Each ROI is smoothed on its
own at a fitted width (peak-normalised, so one onset reaches 1 at any width), bounded by a sigmoid
so a bursting cell votes once, averaged over ROIs into the share of the field that is lit, then put
through an area-normalised difference of Gaussians so a rising background cancels. It is `tiny`'s
distinctness with `tube`'s rate invariance; 1,233 parameters against tube's 1,149.

**At initialisation its count channel reads** 0.500 for a 16-ROI line, 0.141 for the same ink from
4 bursting ROIs, and 0.100 (narrow smear) for 16 ROIs spread over 3 s.

**Where it is:** registered (22 registry tests pass), and added to `tools/fair_bakeoff.py`,
`tools/tube_self_supervised.py` and `tools/tube_ssl_real_compare.py`.

### What `line` scored, all three tests

**Supervised, on the bake-off's planted truth** (same run, four folds, one spec:
[`learned/tube_self_supervised/line_bakeoff/`](../learned/tube_self_supervised/line_bakeoff/)):
tube 0.686, tube_guard 0.680, **line 0.655** (recall 0.750, **precision 0.592, the highest of any
learned model**), CoactDetect 0.651, LoCo 0.645, tiny 0.125, trace 0.110. Distinctness alone
(`tiny`) fails; distinctness with rate invariance works.

**Supervised, with the label-free threshold** — set from each recording's own rigid shift, no
labels read at scoring time. This is where `line` separates from the tube models:

| model | ≤ 0.5 events/10 min | ≤ 1 | ≤ 2 | oracle |
|---|---|---|---|---|
| line | **0.612** | **0.665** | **0.703** | **0.693** |
| tube | 0.432 | 0.519 | 0.625 | 0.665 |
| tube_guard | 0.487 | 0.542 | 0.640 | 0.652 |

`line` keeps its F1 as the threshold tightens, where the tube models lose a third of theirs. That
is the count channel doing what it was built for: the surrogate cannot manufacture a long line, so
a threshold read off the surrogate lands in the right place.

**Trained against rigid shift, no labels** — `line` is *not* better than the tube models:
oracle 0.45 (simulated, J 10 s), 0.455 (real, J 10 s), against tube's 0.41–0.49. Label-free 0.24–0.29
against tube's 0.26–0.31. Training stays unstable: 8–11 of 12 fits learned anything.

**On real recordings** (`tools/tube_ssl_real_compare.py`, 84 lab fast baselines): supervised `line`
behaves like supervised tube — 4.5 events per 10 min, median 5 ROIs within ±1 s, 87 % of its events
on 3 or more ROIs, and it catches 69–75 % of CoactDetect and LoCo. `line` trained without labels
behaves like the tube models trained without labels — 6.4 per 10 min, median 2–3 ROIs, 48–54 % on
three or more.

**The reading.** The architecture was the limit for a *supervised* detector's threshold robustness
and precision, and `line` fixes that. It is **not** the limit for the label-free objective: with
rigid shift as the only teacher, both architectures land in the same place. The bottleneck there is
the objective, which rewards anything that separates real from shifted.

**Nothing is running.** Still to do: the probe on the trained `line` (`tools/probe_line_vs_fuzz.py
--checkpoints …`), and the untrained-baseline recheck above.

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
