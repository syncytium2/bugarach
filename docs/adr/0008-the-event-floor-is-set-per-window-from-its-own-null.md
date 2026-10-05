# ADR-0008: The event floor is set per window from its own null, and never below 3 ROIs

## Status

Accepted, 2026-09-24, by Tony. It covers **scoring and tuning detectors** on the fast, slow and
combined streams, and nothing wider.

It is **link 1** of the scoring design worked through on 2026-09-23: how many ROIs must be active
together for a moment to count as a coordinated event. It rests on
[ADR-0006](0006-a-false-alarm-is-coincidence-the-event-rates-explain.md), which says what counts as
chance. The objective and its false-alarm limit (links 5 and 6) and the real-data check (link 4) are
still being decided.

## Context

**Tony's first answer was a count and a fraction.** On 2026-09-23: *"participation should have a
floor and a fraction because the number of ROIs varies."* Recordings in the default export hold
14–61 ROIs each, so a fixed count means something different in a small field than in a large one.

**No rule declared the floor.** The minimum of 3 ROIs was a working convention:

- the bench's lowest planted participation level is 10%, "about 3 ROIs, at the floor itself"
  (`bench.py`);
- several detectors ship with `min_rois` = 3;
- but the tuning grids let `min_rois` go to 2 (`bench.py`, the search grids), so a search could
  pick a pair.

**The chance floor was then measured, and it does not follow ROI count.**
[The chance-floor run](../learned/runs/2026-09-23-chance-floor-66/README.md) (#790) measured, on
each of the 66 recordings' baseline windows and on all three streams, the smallest number of
co-active ROIs that ADR-0006's rigid-shift null reaches at most once per hour. Onsets were counted in
a 2 s window, CoactDetect's `int_win_sec`, and each ROI's train was shifted by its own offset with
*J* = 20 s. The data were 66 recordings from 36 mice, 1,000 draws per recording per stream.

- The floor runs from **2 to 19 co-active ROIs** across recordings.
- It follows the recording's **event rate** (Spearman correlation 0.79–0.84), not its **ROI
  count** (0.27–0.36). A fixed count, a fixed fraction, and count plus fraction all miss it by 2–3
  ROIs.
- **One pooled floor is wrong in both directions.** DI's median floor is 8–11 ROIs by stream and
  ORX's is 4–5. A floor set from all 66 recordings admits DI recordings at counts their own rates
  reach by chance more than once an hour, and asks ORX recordings for more than chance requires.
  The groups differ this way because their event rates differ
  ([the group run](../learned/runs/2026-09-23-groups-rates-comod-66/README.md)).
- **It is stable.** The floor from each half of the draws matches the full-draw floor on 60–64 of
  66 recordings, and never differs by more than 1 ROI.
- **It is cheap.** All 66 recordings × 3 streams × 1,000 draws took 24 s on one workstation.

So a fixed floor contradicts ADR-0006 itself. That ADR defines a false alarm as coincidence the
ROIs' own event rates explain. Those rates differ between recordings, so the count at which
coincidence stops being chance differs too.

**A floor set per window from its own null has precedent here.** The SCE port (`sce.py`, from
interface2's `generate_sce`) already thresholds each region window against a null built from that
window's own events, because a null pooled across windows over-detects where rates are high.

## Decision

1. **Each window's minimum participation is the larger of 3 ROIs and that window's chance
   floor.** 3 is the absolute minimum. It is a stated choice, so that a pair never counts as a
   coordinated event.
2. **The chance floor** is the smallest number of co-active ROIs whose calls, under ADR-0006's null,
   come to at most **1 per hour** of the window.
   - The null shifts each ROI's train by its own offset, uniform in ±*J*, with *J* = 20 s. That is
     `rigid_frames(shared=False)`.
   - Co-activity is counted in a **2 s** sliding window.
   - The method is `tools/measure_chance_floor.py`'s. It uses at least 1,000 draws, and the floor's
     stability across halves of the draws is reported with it.
3. **Each stream's floor comes from that stream's own events.** Fast, slow and combined share the
   rule, not the number.
4. **Treatment windows are scored under two floors, and both are reported.** Tony, 2026-09-24: *"do
   both so we can compare."*
   - **The window's own floor**, from the treatment window's own null.
   - **The baseline floor**, carried over from the same recording's baseline window.

   A treatment can change event rate (FOUNDATIONS §9: senktide raises it). Where the two floors
   disagree, the difference shows how much of an apparent change in coordination is a change in
   rate. On a baseline window the two floors are the same number.
5. **The same rule holds in tuning and in scoring.** Every bench recording gets its floor from its
   own null, exactly as a real window does. So a detector is tuned under the definition it is scored
   under.
6. **The participation minimum is set by this rule, not searched.** `min_rois` leaves the tuning
   grids for any detector whose minimum it sets.

## Consequences

- **The number of tuned and trained parameter sets does not change.** Tuning happens on the bench,
  which is built from baseline, and on baseline the two floors coincide. So each detector still gets
  three versions: fast, slow and combined. Only the scoring of treatment windows runs twice, and
  that reuses the same trained models. Coded detectors that take `min_rois` internally run twice on a
  treatment window, which is a detection run, not a new optimisation.
- **One knob fewer per detector.** With `min_rois` set by rule, the search has one dimension less,
  and the methods section has one arbitrary choice less to explain.
- **Every result carries its floors.** Recordings now have different minimum event sizes, so a
  group comparison reports each recording's floor alongside its result. It also reports one measure
  that does not depend on the floor: calls above the null's call rate.
- **The null keeps every onset, coordinated ones included.** A recording rich in coordination
  therefore gets a higher floor. That is the conservative direction, and it is stated in the
  methods rather than corrected.
- **Merging is not modelled in the floor.** The measurement counts runs of window positions, not
  merged calls, and a detector that merges calls closer than its merge gap sees fewer null calls. So
  a floor from this method is at or slightly above what a merging detector would see: conservative
  again.
- **The settings are this ADR's to change, not a session's.** The false-alarm budget (1 per hour),
  the window (2 s), *J* (20 s) and the minimum (3) are recorded here. Every floor moves with them,
  so changing any of them takes a new ADR that supersedes this one.
- **Group is nested in imaging day.** 34 dates, none with more than one group. A group's floors are
  also the floors of the days its mice were recorded, and a write-up says so.
- **Writing it up.** The methods section can state the rule in one sentence: *for each window, the
  minimum participation was the larger of 3 ROIs and the smallest number of co-active ROIs reached at
  most once per hour under a surrogate that shifts each ROI's train independently, preserving its
  event rate and its own timing.* It cites ADR-0006 for what counts as chance, and it reports
  treatment results under both floors.

## References

- The chance-floor run: `docs/learned/runs/2026-09-23-chance-floor-66/README.md` (#790).
- The group run: `docs/learned/runs/2026-09-23-groups-rates-comod-66/README.md` (#788).
- ADR-0006 and its references, for the definition of chance.
