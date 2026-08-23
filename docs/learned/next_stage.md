# The next stage, and the order to do it in

**Working document, for whoever picks this up.** Its companion is
[`landscape.html`](landscape.html), which positions this work against the field and is
written for an outside reader. This one is internal: what to build next, in what
order, and why that order. It points at the todos rather than repeating them, and it
goes stale on purpose — when an item lands, delete it from here.

Everything below came out of the literature survey of 17 August 2026. Nothing in it
requires a paper to be read again.

## The dependency that sets the order

One constraint drives the whole sequence: **three of the four items change what gets
measured, or what gets shown to the thing doing the measuring.** Doing them in the
wrong order produces improvements that cannot be attributed.

> Settle the scorer → then change the detector → then change the training data →
> then compare against somebody else.

Tuning suppression against a scorer that cannot see localization, for instance, will
report a gain that is partly the scorer being generous. And running a published
method against that same scorer wastes the comparison, because the most interesting
axis — does it land on the event or near it — is the axis the bench currently cannot
read.

## 1 · Settle what the scorer can see

[`2026-08-17-scoring-cannot-see-localization.md`](../todo/2026-08-17-scoring-cannot-see-localization.md)

**Already measured.** The sweep is committed (`tools/make_tolerance_figure.py`,
figure at `tolerance_sweep.png`) and it says the published ranking is safe at every
tolerance — so nothing already published needs retracting. But 1.5 s is past the
plateau of all six curves, against a median event footprint of 0.80 s, so timing
accuracy is invisible.

**Cheap half:** report the curve, or a tight tolerance beside the permissive one,
wherever a score is published. Do this now — it costs a figure.

**Expensive half:** move from an absolute gap in seconds to an overlap ratio, which
is what the sleep-EEG detectors use and what makes the metric scale-free. That
changes `score_detections` and re-runs every published number. Decide deliberately;
do not drift into it.

## 2 · Non-maximum suppression on the learned model

[`2026-08-17-no-suppression-of-overlapping-detections.md`](../todo/2026-08-17-no-suppression-of-overlapping-detections.md)

**Measure before building.** `Score` already separates `dup_times` from `fa_times`,
so the share of `tube`'s false alarms that are re-detections of events it already
found is a read of existing bake-off output, not an experiment. If that share is
small this is a tidy-up and should drop down the list; if it is large it is the
cheapest precision win available, and precision is the weak half of `tube`'s case.

Depends on 1 only in that the two must not be tuned against each other.

## 3 · Pretrain on the six, fine-tune on the simulation

[`2026-08-17-pretrain-on-the-six-then-fine-tune.md`](../todo/2026-08-17-pretrain-on-the-six-then-fine-tune.md)

The most interesting of the four and the one most likely to matter to the web app,
because it is a route to a model that has actually seen a given lab's real
backgrounds during fitting rather than only a simulation of them.

**Run the ablation or do not run the item.** Pretrained-then-fine-tuned against
fine-tuned-alone at the same budget. Without the control this produces a number
nobody can interpret, and the paper it is borrowed from reported exactly that
comparison.

## 4 · Run one published method on our recordings

[`2026-08-17-run-a-literature-method-on-our-recordings.md`](../todo/2026-08-17-run-a-literature-method-on-our-recordings.md)

Do the **coactivity frame gate** from Mölter's SGC/CORE/SVD, via
[`docs/clean_room/`](../clean_room/WORKFLOW.md). It is about five sentences of
published method, it needs **no adapter** — its high-coactivity frames already are
events in our scorer's terms — and clean-rooming it sidesteps both problems that
make the alternatives expensive: `cnn-ripple`, CADopti and the Romano toolbox are
GPL-3.0 against this repo's BSD-3, and both Python candidates are pinned to
2018–2021 dependency stacks that will not install here.

This is the item that converts "no literature method has been run" into a measured
comparison, which is the sentence currently blocking honest positioning in the app
and on the site.

## Should the approach broaden?

Two different questions get asked as one, and they have opposite answers.

**Broaden the substrate — no, or not yet.** The obvious move after seeing DOSED and
cnn-ripple is "our architecture should also run on LFP, EEG, MEA." It would be a
mistake now. Those fields have mature learned detectors, large expert-labelled
corpora and published baselines; entering them means competing on their terms with
none of their data. The thing this project has that they do not is a **generator
fitted to a specific lab's recordings**, and that asset is worth nothing in a field
that already has labels.

**Broaden the claim's evidence — yes, urgently.** The narrow claim in
`landscape.html` is defensible precisely because it names a substrate and a source of
truth. What makes it thin is that nothing external has ever been run against it.
Item 4 is the whole answer, and it is a week rather than a project.

**One genuine broadening worth considering later:** the per-lab loop is
substrate-agnostic in a way the architecture is not. Assess a lab's recordings,
simulate a data set with planted truth, fit and score — that procedure would work on
MEA network bursts with nothing changed but the generator, and MEA is the field where
detector parameters are most notoriously arbitrary (autoMEA exists because of it).
That is a second product, not a second detector, and it should not start until item 4
has shown the procedure survives contact with somebody else's method.

## What is deliberately not on this list

- **A manuscript.** The narrow claim would need item 4 done first, and probably
  multi-seed error bars, which remain the oldest unaddressed item
  (`2026-08-16-learned-detectors-handoff.md`).
- **Fetching the two missing papers.** Malvache 2016 and SpikeNet are recorded as
  missing on the shelf. Neither blocks anything here; the SCE rule is implemented
  from interface2's port, not from the paper.
