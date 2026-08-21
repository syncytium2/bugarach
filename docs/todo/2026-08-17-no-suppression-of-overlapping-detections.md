---
status: open
filed: 2026-08-17
---

# The learned model has no way to say "that was one event, not four"

`tube` emits a per-frame probability and a threshold turns it into detections.
Nothing merges neighbouring crossings. A single planted event whose probability
trace wobbles across the threshold produces several detections, and the scorer
counts the extras as duplicates or false alarms depending on where they land
(`Score.dup_times` exists precisely because this happens).

Every learned event detector in the adjacent literature has the missing step, and
it has a name: **non-maximum suppression**. DOSED (Chambon et al. 2019) generates
a dense set of candidate events, then keeps the highest-scoring one in each
neighbourhood and discards the rest — it is the last stage of the SSD/YOLO
lineage all three of those detectors come from, and it is the reason they can
afford a dense candidate set in the first place.

## Why this is worth more here than a tidying-up

The `tube` model's case rests on **recall 0.775 with precision as the weak half**
(`docs/learned/bakeoff.md`). Duplicate firings on a real event cost precision
without costing recall, so if any measurable share of its false alarms are
re-detections of events it already found, suppression buys precision for free —
no retraining, no architecture change, a post-processing pass over the
probability trace.

**That share is not yet measured, and it should be measured before the work is
done.** `Score` already separates `dup_times` from `fa_times`; the number is a
read of existing output, not a new experiment. If duplicates are a small fraction
of false alarms, this is a tidy-up and should be filed low. If they are a large
one, it is the cheapest precision win available.

## What to do

1. **Measure first.** Pool `dup_times` against `fa_times` for `tube` across the
   bake-off folds. One script, existing data.
2. If it justifies the work: suppress on the probability trace before
   thresholding — keep the local maximum within a window, drop the rest. The
   window is a parameter and must be declared in frames, not seconds
   (FOUNDATIONS §6), and it must be chosen on training-regime data like the
   threshold is, never re-picked at deployment.
3. The six hand-written detectors mostly have their own merging already; do not
   add a second one on top without checking. This is a change to the learned
   path only.

## Trap

Suppression interacts with the scoring tolerance, and the two must not be tuned
against each other. A wide suppression window and a permissive tolerance flatter
each other: merge everything into one detection per neighbourhood, score it
against a 1.5 s window, and precision rises without the detector having improved.
See `2026-08-17-scoring-cannot-see-localization.md` — settle what the scorer can
see before tuning anything that changes what it is shown.

Source on the shelf: `<darkroom>/bugarach/lit/coordination/chambon_2019_dosed.pdf`.
