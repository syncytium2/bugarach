---
status: open
filed: 2026-08-17
---

# The learned model never sees a real recording, and there is a published way to fix that

Every learned number in this repo comes from a model trained on simulated data.
That is not an oversight — real slices carry no ground truth, which is the whole
reason the generator exists. But it means the model's only exposure to a real
background is at deployment, after fitting is over, and the transfer measurement
says that gap costs something: fitted quiet and run busy, `tube` loses 0.24 of F1
(`docs/learned/regime_shift_fitted.json`).

**SEED (Tapia-Rivas et al. 2024) solves the neighbouring problem and the method
transfers.** Sleep spindles have expert labels but not many. So they ran **A7**,
a classical rule-based spindle detector, over a large *unlabelled* data set, treated
its output as labels, pretrained on that, and fine-tuned on a small amount of
expert-labelled data. Verified from the paper: the artificial set (CAP-A7) held
51,597 events; after pretraining on it and fine-tuning on **10% of MODA**, SEED
reached F1 78.8% and beat DOSED trained conventionally. And the part that makes
it worth copying — **no significant difference (p > 0.18)** between pretraining on
expert labels and pretraining on A7's labels. Only mean IoU, the localization
score, saturated faster with real expert labels.

## The translation, and what is actually being bought

We have the two ingredients: **85 real recordings with no truth**, and **six
hand-written detectors** that play A7's role exactly. So:

1. Run `sce_detect` / `loco_detect` / CoactDetect over the real archive.
2. Pretrain `tube` on those labels.
3. Fine-tune on the simulated data set, where the truth is planted and exact.

**Be clear about what this buys, because it is not what SEED bought.** Their
constraint was label scarcity; ours is not — simulated labels are unlimited and
free. What we would gain is **exposure to the real background distribution during
fitting**, which is the one thing the simulator can only approximate and the thing
the regime-shift result says is expensive to get wrong. The generator's background
is fitted from real recordings, but fitted is not sampled.

## The objection that has to be answered first

**A model pretrained on the six can only learn what the six already do**, and its
ceiling on that data is agreement with them, not correctness. If it then
fine-tunes toward planted truth, the question is whether pretraining left it
better positioned or merely biased toward its teachers' failure modes — and our
teachers disagree with each other (F1 0.32 to 0.78 on the same data set).

Two guards, both cheap:
- **Score against planted truth only.** Agreement with the six is a training
  signal, never a reported metric.
- **Run the ablation.** Pretrained-then-fine-tuned against fine-tuned-alone, same
  budget. SEED reported exactly this comparison and it is the only thing that
  makes the claim checkable. If pretraining does not beat the control, the answer
  is no and the finding is still worth writing down.

## Where this sits against the alternative

SEED's transfer story is a **different answer to the same goal** as this project's
per-lab loop. We adapt by re-simulating a data set from a new lab's measured
statistics; they adapt by fine-tuning on a little of the new lab's data. Neither
is obviously better and the two compose — assess, simulate, pretrain on the lab's
own unlabelled recordings, fine-tune on the simulation. Worth stating in any
positioning document that we know the alternative exists.

Source on the shelf:
`<darkroom>/bugarach/lit/coordination/tapiarivas_2024_spindle_kcomplex_detector.pdf`.
A7 itself is Lacourse, Delfrate, Beaudry, Peppard & Warby, *J. Neurosci. Methods*
316:3–11 (2019), **not retrieved** — the technique is taken from SEED's
description of it, and nothing here depends on A7's internals.
