# ADR-0015: Raster pages navigate the way Igor Pro does

## Status

Accepted, 2026-10-13, by Tony. He asked for a review of Igor Pro's graph navigation and advice
on bringing it to the HTML rasters, was given three decisions, and answered each in a line:
plain drag is *"igor"*, vertical is *"row pitch"*, and Ctrl+wheel zoom is *"yes"*.

**Point 2 of the decision, row pitch, is superseded by
[ADR-0016](0016-a-raster-zooms-in-time-only.md)**, the same day: the box zooms time only. The
rest stands.

Numbers 0012 and 0013 are held by open proposals (#848, #855), so this record is 0015.

## Context

**The pages a reader opens to judge coordination could not be read closely.** Whether a column
of marks is really a column is the question a raster page exists to answer, and at a 2 px mark
on a page 30 to 70 minutes wide it cannot be answered at fit-to-screen. The three raster
surfaces each stopped short in a different place:

- **The group raster pages** declared zoom tools on every panel and then hid every toolbar, so
  the only gesture that worked was drag-to-pan. Filed 2026-09-23 after Tony hit it: *"i need
  the html to allow zooming to evaluate coordination with the new color scheme."*
- **The canvas viewer** zooms through two buttons and ten fixed spans, and cannot be slid.
- **The Panel app** gave the bare wheel to the zoom tool while the written convention said the
  wheel scrolls the page. Filed 2026-08-22 and undecided since.

**Igor Pro's graphs are the interface Tony reads data in.** Its navigation is a marquee dragged
on the plot, followed by a choice of horizontal, vertical or both; a modifier-drag that slides
the graph; the wheel zooming at the cursor; and one keystroke each to undo the last zoom and to
autoscale. None of it needs a toolbar, which matters on a page of twenty stacked panels where a
toolbar is either twenty widgets or one that has scrolled away.

**Three of those gestures collided with decisions already in this repository**, which is why
they went to Tony rather than being built:

1. A plain drag already meant pan ("drag pans"), and bokeh gives the plain drag to one tool.
2. Zooming y was deliberately blocked. The ROI axis is an index, and a y-zoom desynchronises
   rows that are meant to be read against each other.
3. The wheel was supposed to scroll the page.

## Decision

A raster page is navigated by gestures on the plot, as follows.

1. **A plain drag draws a zoom box.** Dragged across, it sets the time range, and every panel
   on the page follows because they share one time axis. Igor asks which way to expand after
   the marquee is drawn; here the direction of the drag is the answer and there is no menu.
2. **Dragged down, the box sets row pitch.** The rows it covers, snapped to whole rows, are
   redrawn with that panel taller and its marks longer. It is never a y-crop at the same
   height. Only that recording's panel changes. A diagonal drag does both at once.
3. **Shift-drag slides the time axis.** Plain drag no longer pans.
4. **Ctrl+wheel zooms time at the cursor. The bare wheel scrolls the page**, always.
5. **Double-click shows everything, and Ctrl+Z steps back one view**, as far as the page has
   history. Both restore row pitch along with time.
6. **The gestures are named in a bar fixed to the bottom of the window**, with a button for
   each of the two in point 5. This is the control block of
   [ADR-0014](0014-a-figure-page-is-figures-then-controls-then-text.md). No toolbar returns.

## Consequences

- **Implemented for the group raster pages** in `bugarach.ui.navigate`, in the same change as
  this record: `navigation_hook` configures each panel's tools and `add_navigation` appends the
  script and the bar to the saved page. `tests/test_raster_navigation.py` reads the tools off
  the model and drives every gesture in a headless browser.
- **The wheel rule is applied wherever the shared time-axis hook is**, so the Panel app and the
  diagnostic figure now leave the bare wheel to the page as well. That closes the 2026-08-22
  todo: the code, its comment and `CLAUDE.md` say the same thing.
- **The Panel app and the canvas viewer do not have the box, the slide or the history yet.**
  They are filed as one todo. In the canvas viewer a drag has to be told apart from the click
  that selects a candidate, and its zoom becomes continuous instead of stepped; a verdict
  already records the view it was made in, so a freehand scale is still captured.
- **A flat PNG is taken before the navigation is added**, so the bar is not in the screenshot.
- **Row pitch is per recording and per visit.** Two readers of one page can be looking at
  different rows at different heights, and nothing on these pages records that. It matters the
  day a call is made on a group page; calls are made in the viewer today.
- **Reversing "drag pans" changes a habit.** A reader who drags to slide now gets a box. The
  bar at the bottom says so on every page.
- **Not adopted from Igor:** cursors A and B with a time-difference readout. Measuring how wide
  a column of marks is in seconds is worth having, and the readout has to live in a lane above
  the raster, since nothing is drawn on it. It was advised and not ruled on.
