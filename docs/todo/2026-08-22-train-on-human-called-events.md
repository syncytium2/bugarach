---
status: open
filed: 2026-08-22
---

# Let a lab train on its own human-called events, not only on planted ones

Tony, 2026-08-22. Every operating point and every trained weight in this project comes
from **planted** events in a simulation. That is the loop's central virtue — a hit and a
miss are counted rather than argued about — and it is also the one thing the README
admits it cannot establish:

> **nothing here says any detector is right about a real slice.**

The missing option is the one every learned detector in the literature actually uses:
**train on events a person marked on a real recording.**

## Why this is not a small feature

**It is how the whole comparable genre works.** The literature shelf's three learned
event detectors — DOSED on sleep EEG, cnn-ripple on hippocampal LFP, SEED on spindles —
*all* learn from expert annotations, and the shelf says so in terms. bugarach is the
odd one out, deliberately, and being able to do both is what would make the comparison
to those three a comparison rather than a contrast.

**It is the only route to the question the bake-off cannot reach.** The imitation gap is
measured and open: on a real recording versus its simulated imitation at matched ROI
count, duration, rate, participation and jitter, **LoCo finds 5 events in the real one
and 10 in the imitation**. A detector tuned on the imitation is tuned on the wrong
texture. Human calls on the real recording are the only ground truth that does not
inherit the generator's shape.

**It would give the app a second loop.** The current loop is measure → simulate → tune →
detect. A lab that has already scored some recordings by hand has ground truth sitting
unused, and no way to hand it over.

## What it probably needs

- **A calls file in the export folder.** One more optional CSV — `calls.csv`, say:
  `slice_id, start_sec, end_sec[, stream][, caller]` — read the same way `regions.csv`
  is, optional, extra columns carried through. The contract's rule holds: **the folder
  is the input**, so this arrives from the producer rather than being derived here.
  Note that the README describes the contract as three facts "and no fourth fact";
  adding one is a revision to [`export_folder_spec.md`](../export_folder_spec.md) and a
  conversation with the producer, not a quiet addition.
- **Nothing new in the scorer.** `bugarach.score` already matches detections to truth as
  **intervals**, greedily, closest pair first. A human call is an interval. This is the
  part that is already done.
- **A tolerance the user can see.** DOSED's scoring is the answer the shelf already
  flagged as *"bugarach's open question, answered"*: report precision / recall / F1 for
  **IoU δ swept 0.1 to 0.9**, re-selecting each detector's operating point at every δ.
  With human calls the tolerance question gets sharper, not softer — two people do not
  agree on an event's edges — so the sweep is the honest presentation.

## The things that will bite

- **Human calls are not ground truth, and the document must not call them that.** They
  are *one caller's opinion*, with a false-negative rate nobody knows. Planted events
  have an exact answer; human calls have an inter-rater problem. A detector scored
  against one caller and reported as "accuracy" repeats, on a new axis, the mistake this
  project already caught itself making — see
  [`2026-08-18-spike-synch-knob-may-not-be-the-knob.md`](2026-08-18-spike-synch-knob-may-not-be-the-knob.md)
  for what it costs to quote a number that measures the setup instead of the detector.
- **A detector trained to imitate a caller will imitate the caller's blind spots**, and
  the promiscuity probe cannot see that: the trap block catches keying on density, not
  keying on a person's habits.
- **Two callers, or one caller twice, is the minimum honest ask.** Without any measure of
  caller agreement there is no way to tell a detector that is wrong from a detector that
  disagrees with one person. Worth asking the producer for a re-scored subset before
  building much.
- **Circularity, if the caller used a detector.** If the human calls were made while
  looking at detector output — which the viewer makes easy — then scoring that detector
  against them is a check that cannot fail. The `caller` column should record how the
  calls were made, not just who made them.

## Where it sits against the rest

Related, and worth reading together: the imitation gap in the README, the
[promiscuity probe that cannot fail](2026-08-16-promiscuity-probe-cannot-fail.md), and
[`detector_history.md`](../detector_history.md) §5.3, which argues the operating point
should be set from a stated design false-alarm rate rather than from whatever a sweep
likes. All three are the same underlying gap: **this project can score a detector
precisely against something it made up, and has no way to score it against the world.**
