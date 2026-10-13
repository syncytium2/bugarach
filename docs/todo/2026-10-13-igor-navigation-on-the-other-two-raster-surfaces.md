---
status: open
filed: 2026-10-13
---

# Igor-style navigation is on the group raster pages only; the canvas viewer and the Panel app still need it

[ADR-0015](../adr/0015-raster-pages-navigate-the-way-igor-does.md) rules how a raster is
navigated: drag a box to zoom time (time only, [ADR-0016](../adr/0016-a-raster-zooms-in-time-only.md)), Shift-drag slides,
Ctrl+wheel zooms time, double-click shows everything, Ctrl+Z steps back. The group raster pages
(`tools/make_group_raster_summary.py`) have all of it through `bugarach.ui.navigate`. Two
surfaces do not.

## The canvas viewer (`docs/site/viewer.template.html`)

Today: `−` and `+` buttons step through ten fixed spans (`RASTER_ZOOMS`), "whole recording"
resets, and there is no way to slide. The window is held as `RASTER_SPAN` and `RASTER_MID`.

What it needs:

- Pointer handlers on `#cv`. A drag longer than about 4 px is a box; anything shorter stays the
  click that selects a candidate, which is the handler already there.
- The span becomes any number of seconds, not one of ten. `zoomRaster` can keep its steps for
  the buttons.
- Shift-drag changes `RASTER_MID`. Ctrl+wheel changes `RASTER_SPAN` about the cursor.
- A view stack for Ctrl+Z, and double-click for the whole recording.
- **A verdict records `view_t0_sec` and `view_t1_sec` already** (`src/bugarach/annotate.py`), so
  a freehand time scale is captured.

## The Panel app (`bugarach view`, `src/bugarach/ui/app.py`)

It has the wheel rule, because `_time_axis_hook` now puts Ctrl on the wheel for every panel.
Plain drag still pans there. Adding `navigation_hook` to its panels gives it the box; the
Shift swap and the history live in a script that `add_navigation` appends to a
saved file, and a served Panel app has no saved file. Either serve the same script through
Panel's own resources or port those two pieces to `CustomJS`.

## Also open from the review

Cursors with a time-difference readout (Igor's A and B), in a lane above the raster. Advised to
Tony on 2026-10-13 and not ruled on.

Whether 3 px per ROI is too small a default for a page read closely
([the 2026-09-23 note](2026-09-23-the-group-raster-page-throws-away-its-own-zoom.md), `--roi-px 8`
was much easier to judge). Zoom is time only now, so row height is whatever the page was built
with.
