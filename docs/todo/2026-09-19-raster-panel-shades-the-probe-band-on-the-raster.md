---
status: open
filed: 2026-09-19
---

# `raster_panel` shades the busy stretch across the raster whenever it is given the ground truth

CLAUDE.md: *nothing is ever drawn on the raster*, and every cue goes in a lane above it. The
shared panel breaks that from the inside. `bugarach.ui.diagnostic.raster_panel`, when it receives
`gt`, adds `hv.VSpan(*gt.params["hot_window"])` in `PROBE_BAND` at alpha 0.16 over the raster's
marks. `lane_panel` already draws the same band in the lane above, where it belongs, so the raster
copy adds nothing but tint.

**Where it shows:** every figure `tools/make_diagnostic.py` renders from a bench recording, because
`coordination_diagnostic` passes `gt` to both panels. Seen on 2026-09-19 rendering
`--bench baseline_quiet --seed 2000`: the busy stretch is shaded across the marks.

**Why SAP009 misses it:** the rule is a line match on overlays added to a variable named `raster`
from *outside* the module. This one is inside the module that owns the panel.

**Worked around, not fixed:** `tools/make_replicate_report.py` calls `raster_panel(..., gt=None)`
and lets `lane_panel` carry the band. The fix is to drop the `VSpan` from `raster_panel` (it still
needs `gt` for nothing else there), then re-render the figures that used it.
