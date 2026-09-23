---
status: open
filed: 2026-09-22
---

# The every-knob search extends a count by halving it, and reads a flat plateau as a climb

Found by the WSMIP064 session during the slow every-knob search (2026-09-21) and listed as open
work in its handoff, now [`docs/handoffs/2026-09-21-slow-bench.md`](../handoffs/2026-09-21-slow-bench.md).
Filed here at the move, because a handoff's open list is read once and a todo gets reread. Both
defects are in `tools/search_all_settings.py` and apply to the fast search too; neither needs a
ruling.

## 1. A count that is not declared `INTEGER` is extended as a real number

> **FIXED 2026-09-23.** `min_rois` and `min_n` are in `INTEGER`, any all-integer grid is treated
> as a count, counts step by one below 4 and double above it, and `COUNT_FLOOR` stops the
> participant floors at two cells. Tested in `tests/test_search_all_settings.py`. It had cost
> something by then: the combined search (#754) returned SPIKE-synch at `min_n` 0.25 with the
> largest gain of the six (+0.131), which could not be installed. **Part 2 below is still open.**

`extend()` handles counts only through the `INTEGER` set, which holds
`n_synchronous_frames` and `sce_min_distance_frames`. `sce.min_rois` is not in it, so it falls
through to the generic branch and is halved. The slow search's own log,
`docs/learned/runs/2026-09-21-full-search-slow/search.log`:

```
sce.min_rois: best at the edge 3; adding 1.5
sce.min_rois: best at the edge 1.5; adding 0.75
sce.min_rois: best at the edge 0.75; adding 0.375
```

A participation floor of 0.375 ROIs is not a setting. It spends three extension rounds on values
that are probably all the same detector, and it can report a winner that no settings file could
hold. **Fix:** add every count-valued setting to `INTEGER`, or derive the set from each
detector's declared parameter types rather than listing names by hand, and refuse a searched value
below the setting's own floor.

## 2. The edge rule cannot tell a flat plateau from a climb

A setting is extended when its best value sits at an edge of the grid. When several values tie,
`max(ok, key=…)` returns the first of them, which is the low edge, so a plateau reads as a climb
toward it. On the slow search, SPIKE-synch's `C_min` went 0.02 → 0.01 → 0.005 → 0.0025 and looked
unbracketed, when every value from 0 to 0.03 scored the same. **Fix:** treat a best value that
ties its inner neighbour as bracketed (a tie being within a stated tolerance, set against seed
noise), and log it as a plateau rather than an edge.

## Done when

Both behaviours have a test in `tests/test_search_all_settings*.py`, and a re-run of either
search's extension phase no longer produces a fractional count or chases a plateau.
