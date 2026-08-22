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

## The part that changes what this feature *is*: a call is a property of the picture

Tony, 2026-08-22: *"the human calls depend on psychophysics of the raster. Stretch it one
way and nothing, compress another and suddenly they are easy to see. This also depends on
the human."*

This is not a caveat on the feature, it is a correction to what the feature collects. **A
human call is not a property of the recording. It is a property of (recording × rendering
× observer).** The same onsets, drawn at two time scales, are two different stimuli: at
one, a coordinated event is a vertical stripe that jumps out pre-attentively; at another,
the same onsets are scattered across enough horizontal distance that nothing groups. The
event did not change. The picture did.

**And it will masquerade as caller disagreement**, which is the dangerous part. Two people
calling the same recording at different zooms will produce two different call sets, and
the obvious reading — *"inter-rater variability, collect more raters"* — is wrong. The
variance would be in the stimulus, not the observer, and adding raters cannot find that.

### The knobs, and every one of them is currently uncontrolled in our own viewer

Checked against `src/bugarach/ui/app.py` rather than assumed:

- **Time compression (pixels per second).** The dominant one. `_time_axis_hook` binds the
  mouse wheel to an x-constrained zoom (`toolbar.active_scroll = wheel`) and the raster
  ships `active_tools=["xpan"]`, so a caller can pan and rescale time freely and **nothing
  records where they were.** Confirmed in the rendered bokeh model rather than inferred
  from the source: `active_scroll` is a `WheelZoomTool` with `dimensions=width`. The
  `_raster` comment and CLAUDE.md's "scroll wins" convention both say the opposite and are
  stale — filed separately as
  [the wheel zooms, and three places say it does not](2026-08-22-the-wheel-zooms-but-three-places-say-it-does-not.md),
  because which behaviour is *right* is its own decision. For this todo it changes
  nothing: either way the caller's time scale is unpinned and unrecorded.
- **Row order.** `_raster` draws one row per ROI with `for i, v in enumerate(...)` —
  **file order**, i.e. whatever order the producer's CSV happened to list. That is
  arbitrary, and arbitrary is not neutral: any ordering correlated with participation
  packs co-active cells into adjacent rows and makes an event a solid block, while a
  scrambling of the same rows spreads it into noise. Nothing records the order either.
- **Vertical density.** The raster is a fixed `height=150` regardless of ROI count, so a
  30-ROI slice and a 150-ROI slice are drawn at five-fold different rows-per-pixel.
- **Mark geometry.** `marker="dash", size=5, alpha=0.7`. At high compression neighbouring
  dashes overlap and merge into a bar — and that merging *is* the percept being reported.
  Mark size therefore sets the effective coincidence window of the human's eye.

### The observation worth keeping

**Time compression is the human's bin width.** A caller zoomed out is running a wide
integration window; zoomed in, a narrow one. It is the same knob `bin_width_sec` is, on
the same axis, doing the same job — and the asymmetry is glaring: the detector's bin width
is a **declared parameter with a swept grid and a recorded provenance**, and the human's is
an undeclared, unrecorded consequence of how far they happened to scroll.

That asymmetry is the actionable form of Tony's point. **Make the view a declared
parameter of the call**, exactly as the operating point is a declared parameter of a
detector run.

### It is measurable, and the repo can already run it

This is a psychophysics experiment, and a cheap one — the pieces exist. bugarach renders
rasters, and `bugarach.score` already matches interval sets to interval sets.

> Take one recording. Render it at several time compressions and several row orders.
> Present them **randomised, with repeats**, to the same caller. Measure the agreement of
> the call sets across conditions, and of a condition with itself.

Three things fall out, and the first is the one that matters most:

1. **A within-caller ceiling.** Agreement of a caller with *themselves* on the same
   recording at the same view is the upper bound on any agreement a detector trained on
   those calls could show. Reporting a detector's F1 against human calls without that
   ceiling on the same axis would be quoting a number nobody can interpret — the same
   shape of error as [SPIKE-synch's 0.254](2026-08-18-spike-synch-knob-may-not-be-the-knob.md),
   which measured its own setup.
2. **A defensible default view** — whichever compression makes calls most *stable*, which
   is a measured answer rather than a taste.
3. **A finding either way.** If calls are robust across the sweep, that is a real and
   reassuring result and the whole worry retires. If they are strongly view-dependent,
   that is a finding about coordination-scoring in this field generally, and it is worth
   more than the feature that prompted it.

Note this is upstream of the IoU-tolerance sweep already proposed below. The δ sweep
handles disagreement about an event's **edges**; view dependence is disagreement about
whether the event **is there at all**, and no scoring tolerance reaches that.

### The uncomfortable version

If calls do turn out to be strongly view-dependent, then "train on human calls" partly
means "train on a rendering choice". A detector consumes event *times* and has no aspect
ratio; the human's percept has nothing else. Matching one to the other may be fitting an
artifact of the picture.

That is an argument for **pinning and reporting the view before collecting anything**, not
for abandoning the idea — but it does mean the honest first step is the sweep above, not
a call-collection UI.

## What it probably needs

- **A calls file in the export folder, carrying the view the calls were made under.**
  One more optional CSV — `calls.csv`, say: `slice_id, start_sec, end_sec[, stream][,
  caller]` — read the same way `regions.csv` is, optional, extra columns carried
  through. The contract's rule holds: **the folder is the input**, so this arrives from
  the producer rather than being derived here. Note that the README describes the
  contract as three facts "and no fourth fact"; adding one is a revision to
  [`export_folder_spec.md`](../export_folder_spec.md) and a conversation with the
  producer, not a quiet addition.

  **Per the section above, `caller` alone is not enough.** A call without its rendering
  is an answer without its question, so the row — or a companion `views.csv`, since the
  view is one-per-session rather than one-per-call — needs at minimum the **seconds per
  screen width** (or pixels per second), the **row order** actually drawn, and the
  **tool and version**. That is the difference between a file that can be re-scored
  later and one that can only be trusted.
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
  building much. **Same view both times**, or the measurement is of the picture rather
  than the person — see the psychophysics section.
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

And a fourth, which the psychophysics section adds: the human is not a way out of that
gap so much as a **different instrument with its own uncalibrated settings**. The
detector's settings are declared, swept and provenanced in `bench.py`; the human's are
whatever the raster happened to look like. Calibrating the second instrument is the
prerequisite for using it to check the first, and that ordering is the main thing this
todo now says.

## First step

**Not a call-collection UI.** Run the view sweep — one recording, several compressions
and row orders, randomised with repeats, one caller — and measure whether calls are
stable. Everything else in this file is contingent on that answer, including whether the
feature is worth building at all.
