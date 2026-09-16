# Rigid shift as a teacher, and the detector built to learn from it

> **Exploratory, run overnight 2026-09-15 into 2026-09-16.** Tony: *"run the full test all the way
> to real data. prepare a report for the morning. murderboard is authorized."* Everything here is
> on branch `unsup/rigid-shift-controls`; the data are in the folders beside this page. Nothing has
> been proposed for the goal page yet.

## The problem

A label-free detector needs a **negative class**: recordings that keep everything about the data
except the thing to be detected. Rigid shift is the candidate — each ROI's whole onset train moves
by one random offset within ±*J*, so every ROI keeps its own rate and its own intervals while the
alignment between ROIs is destroyed.

Two questions follow, and the night answered them separately.

1. **Is rigid shift a sound teacher?** It must hide from anything that cannot see coordination, and
   it must actually destroy coordination.
2. **Can a detector learn from it?** With no labels, only real recordings and their shifted copies.

The second question turned into a third when Tony asked whether the weak result was the detector's
fault: *"i wonder if we need an orientation detector rather than a center-surround … when most rois
fire it looks like a vertical line. two rois aren't enough and noise/high background looks like
fuzz"*, and then *"two sensors, orientation and length (relative to the number of rois)"*.

## What holds

**Rigid shift is a sound teacher.** Shifting every ROI of a recording by *one shared* offset — which
moves each ROI's own train exactly as rigid shift does, but keeps the ROIs aligned with each other —
reads at chance on both folders at every displacement tested, 0.49–0.53 out to 40–45 s. The rise
under rigid shift is therefore removed cross-ROI structure, not a leak. It removes planted
coordination from about 10 s, including on the Cossart folder at that folder's measured
participation, and a graded control shows the measure can register partial removal. Details and
figures: [`../rigid_shift_look/controls/`](../rigid_shift_look/controls/).

**The architecture question has an answer, and it is Tony's.** `line` — count how many ROIs are lit,
then judge that count against its own background — is now the best detector in the bake-off, and the
second sensor is what put it there.

## Figure 1. What the two sensors buy

![the two sensors](line_sensors_fig.png)

**Panel A, the bake-off.** One run, one generator spec, four folds, every detector calibrated or
trained on three folds and scored on the fourth. `line` (two sensors) reaches **F1 0.713 ± 0.078**
against `tube`'s 0.686 ± 0.042 and the length-only ablation's 0.655 ± 0.035. The ablation is the
same model with the orientation channels removed, registered as `line_length` so it is measured in
the same run by the same scorer rather than quoted from another one.

| detector | F1 | fold range | recall | precision | parameters |
|---|---|---|---|---|---|
| **line, two sensors** | **0.713 ± 0.078** | 0.64–0.81 | 0.933 | 0.580 | 1,305 |
| tube | 0.686 ± 0.042 | 0.65–0.74 | 0.925 | 0.547 | 1,149 |
| tube_guard | 0.680 ± 0.060 | 0.63–0.75 | 0.817 | 0.583 | 1,149 |
| line_length, length only | 0.655 ± 0.035 | 0.62–0.69 | 0.750 | 0.592 | 1,233 |
| CoactDetect | 0.651 ± 0.044 | 0.61–0.71 | 0.767 | 0.572 | — |
| LoCo | 0.645 ± 0.057 | 0.57–0.70 | 0.742 | 0.575 | — |
| tiny | 0.125 ± 0.000 | 0.12–0.12 | 0.067 | 1.000 | 2,393 |
| trace | 0.110 ± 0.018 | 0.09–0.12 | 0.075 | 0.372 | 2,065 |

**What the second sensor did:** it bought **recall**, 0.750 → 0.933, at a small cost in precision,
0.592 → 0.580, for 72 parameters. ⚠ **The gain (0.058) is inside the fold spread**: `line`'s folds
run 0.64–0.81 and the ablation's 0.62–0.69. Four folds and one training seed per fold cannot
separate those distributions, so treat this as "worth keeping and worth replicating", not as a
measured superiority. The seed axis is the cheap replication and it has not been run.

**Panel B, the probe.** On a quiet synthetic field, four plants of equal ink: a **line** (K distinct
ROIs in one frame), a **burst** (K/4 ROIs firing four times each), **fuzz** (K ROIs spread over 3 s)
and a **wave** (K ROIs one frame apart). Each model's score is its peak response with the plant
minus the same field without it, so its own scale cancels. At K = 16 ROIs' worth of ink:

| trained model | line | line ÷ burst | line ÷ fuzz | line ÷ wave |
|---|---|---|---|---|
| line, two sensors | 18.50 | 1.83 | 1.99 | 1.32 |
| line_length | 17.56 | 1.82 | 1.75 | 1.14 |
| tube | 15.84 | 1.34 | 1.43 | 1.17 |

Both `line` builds separate a line from a burst far better than `tube` does, which is the
distinctness the count channel was built for. The orientation channels show up against the
**wave**, 1.32 against 1.14 — the plant that is a line in every respect except that its members
arrive one frame apart.

⚠ **The wave is not a tilt.** These models are permutation-invariant over ROIs and the encoder sorts
rows by rate, so the diagonal a person sees in a raster is a fact about row order, which the model
never reads. What these channels measure is **temporal concentration**, and the wave is fuzz with an
order the model cannot see.

## Figure 2. Learning from rigid shift alone

![the label-free arms](tube_ssl_fig.png)

Four architectures, two displacements (*J* = 10 s and 20 s), trained on unlabelled simulated
recordings and on real lab fast-stream baselines, three seeds and four folds each: 288 fits. The
objective is a ranking loss on the mean of the top 1 % of per-frame scores, a real crop against the
same crop rigid-shifted.

**Supervised, with a label-free threshold** — set per recording so the model fires at most *r*
events per 10 minutes on that recording's own rigid shift, reading no labels at scoring time:

| model | ≤ 0.5 events / 10 min | ≤ 1 | ≤ 2 | oracle |
|---|---|---|---|---|
| line | 0.573 ± 0.090 | 0.668 ± 0.077 | 0.699 ± 0.067 | 0.698 ± 0.062 |
| line_length | 0.601 ± 0.073 | 0.663 ± 0.064 | 0.703 ± 0.061 | 0.693 ± 0.055 |
| tube | 0.432 ± 0.032 | 0.519 ± 0.075 | 0.625 ± 0.064 | 0.665 ± 0.055 |
| tube_guard | 0.487 ± 0.107 | 0.542 ± 0.105 | 0.640 ± 0.084 | 0.652 ± 0.058 |

**Both `line` builds keep their F1 as the threshold tightens; the tube models lose a third of
theirs.** That is a useful result on its own: a surrogate cannot manufacture a long line, so a
threshold read off the surrogate lands in the right place for a model that counts.

**Trained against rigid shift with no labels** — here the architecture does *not* help:

| arm | oracle F1 | label-free, ≤ 2 per 10 min | fits that learned anything |
|---|---|---|---|
| line, real recordings, *J* 20 s | 0.463 ± 0.171 | 0.305 ± 0.172 | 10 of 12 |
| line_length, real, *J* 10 s | 0.455 ± 0.181 | 0.286 ± 0.191 | 10 of 12 |
| tube, real, *J* 20 s | 0.488 ± 0.118 | 0.310 ± 0.200 | 9 of 12 |
| tube_guard, real, *J* 10 s | 0.487 ± 0.147 | 0.289 ± 0.159 | 9 of 12 |

Every architecture lands between 0.41 and 0.49 with an oracle threshold, against 0.65–0.70
supervised. A quarter of the fits never left chance loss.

## On real recordings

All 84 lab fast-stream baselines, each judged by a model that never saw its mouse, beside
CoactDetect and LoCo at their production operating points.

| detector | events per 10 min | ROIs within ±1 s, median | share with ≥ 3 ROIs |
|---|---|---|---|
| CoactDetect | 2.70 | 7 | 1.00 |
| LoCo | 2.57 | 8 | 1.00 |
| supervised line, label-free | 4.95 | 5 | 0.88 |
| line trained against rigid shift, *J* 20 s | 5.73 | 4 | 0.63 |
| line trained against rigid shift, *J* 10 s | 5.70 | 2 | 0.48 |
| random times in the same recordings | — | 1 | 0.21–0.26 |

Supervised `line` catches 76–77 % of CoactDetect's and LoCo's events (chance 7–10 %), and 40–44 % of
its own events land within 1 s of one of theirs (chance 4–5 %). The models trained against rigid
shift catch 47–72 % and place 19–30 % of their own events near one. They also break single bursts
into several calls and are not locked in time to them.

**Not artefacts.** The most frequent ROI pair takes no larger share of a label-free model's events
than of a supervised one's (0.29–0.33 against 0.33), so this is not crosstalk or a duplicated ROI;
and 3–4 % of events sit within 5 s of a window edge, so it is not the window boundary.

## What this does not settle

- **The gain from orientation is inside the fold spread**, as above. One training seed per fold.
- **The label-free objective is the bottleneck, and it is untuned.** One objective, one pooling rule,
  one learning rate, 900 steps. It pays for anything that separates real from shifted, so a two-ROI
  coincidence earns as much as a crowd.
- **The benchmark is a simulator** whose events carry 0.31 s of jitter. Real fast onset jitter is
  0.36–1.04 s and the second number is flagged soft in `docs/generator.md`.
- **⚠ The untrained baselines are not trustworthy and should not be quoted.** Untrained models scored
  0.00 on every plant in the probe — no response to a planted line at all — yet untrained `tube`
  scored F1 0.507 with an oracle threshold in the label-free run. A model that does not respond to a
  plant should not score half. The quantile-grid threshold on a near-constant output is the suspect;
  until that is chased, the untrained row says nothing.
- **Only the lab fast stream** was used for the label-free work; the slow stream and Cossart were not.
- **`line` has never been murderboarded as code**, and it is four hours old.

## What waits on Tony

1. **Does orientation stay on by default?** It is on now. The evidence for it is a recall gain inside
   the fold spread plus a clean mechanism; the ablation is one registered architecture away
   (`line_length`), so a three-seed replication would settle it.
2. **Does shared modulation on timescales of 10–45 s count as coordination?** Rigid shift at 10–20 s
   removes it. On the lab slow stream and on Cossart that structure is real and detectable; on the
   fast stream it is not. The rigid-shift note stays under its correction banner until this is
   answered.
3. **Is the objective worth another attempt?** The obvious next design pays for **length**: contrast
   a real window against a surrogate that keeps each ROI's timing and breaks only the alignment, so
   the only way to win is to count ROIs.

## How to reproduce

All four stages ran in one chain on 2026-09-15 night, in the Elephant virtual environment
(`bugarach-worktrees/surrogate-screen-overnight-venv`, torch 2.14.0), with
`PYTHONPATH=<worktree>/src`:

| stage | command | output here |
|---|---|---|
| bake-off | `tools/fair_bakeoff.py --spec docs/learned/generator_spec.json` | `line_bakeoff/bakeoff.json` |
| label-free training | `tools/tube_self_supervised.py` | `training/` |
| real recordings | `tools/tube_ssl_real_compare.py --checkpoints …` | `real_compare/` |
| probe | `tools/probe_line_vs_fuzz.py --checkpoints …` | `probe/line_vs_fuzz.json` |
| figures | `tools/make_line_sensors_figure.py`, `tools/make_tube_ssl_figure.py` | the two PNGs here |

The architecture is `src/bugarach/learn/nets/line.py`, with the ablation in `line_length.py`.
Checkpoints of one seed of each label-free fit are in `real_compare/checkpoints/`. The earlier
stages of this thread — the controls, the aggregate-channel leak test, and the first tube training
run — are in [`aggregate_leak/`](aggregate_leak/), [`../rigid_shift_look/controls/`](../rigid_shift_look/controls/)
and the handoff at
[`../../handoffs/2026-09-15-rigid-shift-controls-and-tube-training.md`](../../handoffs/2026-09-15-rigid-shift-controls-and-tube-training.md).
