# ADR-0016: A raster zooms in time only

## Status

Accepted, 2026-10-13, by Tony. Supersedes point 2 of
[ADR-0015](0015-raster-pages-navigate-the-way-igor-does.md), made the same morning. On the first
two real pages drawn with it, the two 4x pilot rasters: *"it's a bit of a mess. disable the
pitch and make zoom only x-axis."*

## Context

**ADR-0015 gave the zoom box a vertical meaning.** Dragged down a raster, it picked rows of that
one recording and redrew the panel taller with longer marks. That was the answer to "vertical,
horizontal or both", offered as row pitch because a plain y-zoom of an ROI index only hides
rows.

**On real pages it did not read.** The synthetic page it was built and tested on had two
recordings. A pilot page has six, each with its period lane, and three things went wrong at
once:

- A drag meant as "zoom time here" is rarely perfectly level, so it was taken as diagonal and
  re-pitched a raster the reader had not meant to touch.
- A panel growing pushes every recording below it down the page, so the recordings being
  compared moved while they were being compared.
- Rasters at different pitches on one page break the rule the page is built on: the same
  height per ROI on every recording, so ink density reads the same down the page.

## Decision

1. **The zoom box sets the time range and nothing else.** It is drawn as a band the full height
   of the panel. A drag has no vertical meaning, on a raster or on a lane.
2. **No gesture changes a panel's height or which rows it shows.** Row height is set when the
   page is built, with `--roi-px`, and is the same for every recording on it.
3. **Everything else in ADR-0015 stands**: the plain drag is the box, Shift-drag slides,
   Ctrl+wheel zooms time and the bare wheel scrolls, double-click shows everything, Ctrl+Z steps
   back, and the bar at the bottom of the window names the gestures.

## Consequences

- `bugarach.ui.navigate` loses the row-pitch half: `navigation_hook` is a plain hook with a
  width-only box, and the page script keeps a history of time ranges alone.
- **A reader who needs taller rows asks for the page to be rebuilt** with a larger `--roi-px`.
  The 2026-09-23 note that 3 px per ROI may be too small for close reading is open again; it
  was closed on the strength of the gesture this record removes.
- The follow-up for the canvas viewer and the Panel app no longer includes row pitch.
- The two 4x pilot pages drawn on 2026-10-13 were rebuilt under this record.
