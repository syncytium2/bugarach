---
status: open
opened: 2026-09-24
area: scoring design, link 1
---

# Implement ADR-0008: each window's event floor from its own null, never below 3 ROIs

[ADR-0008](../adr/0008-the-event-floor-is-set-per-window-from-its-own-null.md) is accepted; none of
it is in the code yet. The measurement exists (`tools/measure_chance_floor.py`, #790). What remains
is to make the bench, the search and the scoring use it.

## What done looks like

1. **One function computes a window's floor** from its events: `max(3, chance floor)` at 1 false
   alarm per hour, a 2 s window, *J* = 20 s and at least 1,000 draws, with half-draw stability
   reported. `tools/measure_chance_floor.py` calls it rather than holding its own copy.
2. **Every bench recording gets its floor** from its own null, on fast, slow and combined, and the
   scorer uses it as the minimum participation.
3. **`min_rois` leaves the search grids** of every detector whose minimum the floor sets. No grid
   offers 2 any more.
4. **Treatment windows are scored twice**: under the window's own floor and under the same
   recording's baseline floor. Both appear in every result that reports a treatment window.
5. **Every result records its floors**, and group comparisons report calls above the null's call
   rate beside the floored counts.
6. **Tests**: the floor is never below 3; on a baseline window both floors are equal; a recording
   with its rates raised gets a floor at least as high; the bench and the real-data scorer call the
   same function.

## Order

This comes before the three versions are tuned on the retuned benches (#786). Tuning under the old
`min_rois` grid would be tuning under a definition the scoring no longer uses.

## Open, and not this todo's

The objective and its false-alarm limit (links 5 and 6) and the real-data check (link 4). The decoys
stay as ADR-0006 left them until the objective's ADR.
