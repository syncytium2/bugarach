---
status: open
filed: 2026-11-02
---

# Precursors of a coordinated event, version 2

Version 1 is [the 2026-10-30 run](../learned/runs/2026-10-30-precursors-of-coordinated-events/README.md).
It found weak predictability (within-recording AUC 0.66–0.69). On slow that was almost all "an
event just happened"; on fast a modest rise in background activity 5–30 s before survived. It also
found four limits, and version 2 is built around them.

## What version 1 could not do

1. **It could not see the last seconds.** The detector folds any onset within 1 s (fast) or 3 s
   (slow) of an event into the event, so the moment a precursor would be strongest is empty by
   construction.
2. **It could not tell a precursor from the recording's own drift.** Its controls were random times
   in the same window. A fast background rise before events is also what minute-scale shared
   modulation alone would produce ([slow co-modulation](../learned/slow_comodulation/README.md)),
   and version 1 has no null that keeps that drift and destroys only the link to the events.
3. **It had little to work with.** 183 fast events, about 2 isolated events per recording, and only
   1–3 OVX and ORX recordings with 3 or more events.
4. **It ran past a contamination stop**, on Tony's say, with a sensitivity pass.

## Version 2, in order

1. **Ask the cheaper question first: which nascent bursts grow into events?** Take every candidate
   (two or more distinct ROIs within 1 s, say, well under the floor) and ask which ones the detector
   later calls. The blind spot then becomes the signal. Features: how many ROIs, how fast the next
   onsets come, whether the early ROIs are ones that usually lead (the Aim 0 order indicator, scored
   on other events of the same recording), background rate, time since the last event. This is the
   early-warning question that could be answered, and the one most likely to give a large AUC.
   *Argued, not measured.*
2. **Add a null that keeps drift.** Re-run every measure with the event times moved by a block
   shift that keeps each window's slow rate profile: circular shift of the event train inside
   stretches of 2–5 minutes, or the "shift each ROI inside the stretches no episode covers" null
   from the slow co-modulation page. A precursor is what beats that null. Report AUC as
   *observed − null*, per recording.
3. **Fit a conditional intensity, not a binned classifier.** A point-process GLM of the event rate
   given its history: time since the last event as a spline (so clustering and any recovery period
   show as a curve, not one number), background rate smoothed at 10 s, 30 s and 2 min, and recent
   onsets of each ROI weighted by its participation in *other* events of that recording (leave one
   event out). Recording as a random effect, so it learns *when* and not *which recording*.
   Hold out by mouse.
4. **Check that the method can see a precursor at this sample size.** Plant a ramp of known size
   and lead time in the synthetic bench (`bugarach.bench`, baseline-calibrated) at the real event
   counts, and measure the AUC the pipeline recovers. That gives the smallest precursor version 1
   could have missed, in the Aim 0 style ([goal](../goals/synthetic-validation.md)).
5. **Get more events without leaving baseline.** Add the combined stream (471 baseline events) and
   check the result against a second detector (`count_sliding` or chorus) so it is not
   CoactDetect's. Treatment windows stay out: what a treatment does to predictability is a finding
   about the preparation, which is fireflies' by default (ADR-0017) and needs Tony's yes.
6. **Rerun on the corrected export** when it becomes the default, and drop the sensitivity pass.

## Out of reach from the export folder

A precursor below the event threshold, in the fluorescence itself (summed ΔF/F rising before the
first onset), cannot be measured here: the folder carries events only, and the folder is the input.
If version 2 points that way, it is a request to the producer, stating what should exist afterwards
(per-ROI traces beside the events), drafted here and posted by Tony (ADR-0007).
