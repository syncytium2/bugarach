---
status: open
filed: 2026-08-22
---

# The mouse wheel zooms the raster, and three places say it does not

Found while writing
[`2026-08-22-train-on-human-called-events.md`](2026-08-22-train-on-human-called-events.md),
which needed to know whether a person reading the viewer can rescale time. They can — but
the code and the documentation disagree about it, and all three statements cannot be true.

**The code makes the wheel zoom.** `_time_axis_hook` in `src/bugarach/ui/app.py` ends with

```python
if wheel is not None and toolbar is not None:
    toolbar.active_scroll = wheel
```

and its own docstring explains why, in detail: *"bokeh leaves active_scroll on 'auto' and
nothing claims the wheel, so scrolling over the plot did nothing at all and zooming meant
finding the box-zoom button first. Hand the wheel to the x-constrained zoom explicitly."*
`_raster` applies that hook.

**Two other places say the opposite.**

- The comment inside `_raster`, a dozen lines above the hook that contradicts it: *"wheel
  zoom stays in the toolbar but NOT active, so the mouse wheel scrolls the page; drag
  pans, toolbar toggles zoom when wanted."*
- `CLAUDE.md`, under **Plot conventions**, as a standing rule: *"**Scroll wins**:
  wheel-zoom stays in the toolbar but inactive — the mouse wheel scrolls the page; drag
  pans."*

## Which is right is a real decision, not a typo

Both behaviours are defensible and they serve different readers:

- **Scroll wins** is right for a *page* — a report with several stacked panels, where
  hijacking the wheel traps the reader partway down and is a well-known way to make a page
  feel broken.
- **Wheel zooms** is right for an *instrument* — someone examining one recording, where
  reaching for a toolbar button to change time scale is friction on the main gesture.

The viewer is arguably both, which is probably how the two rules came to coexist.

## Why it matters beyond tidiness

Whichever way it is settled, **it decides how easily a person can change the time scale of
a raster** — and per the human-calls todo, time scale is the dominant variable in whether a
coordinated event is visible at all. A viewer where the wheel zooms is a viewer where a
caller's effective integration window changes continuously, by accident, without being
recorded. That is not an argument for either answer; it is an argument for the answer being
*known*, and for whatever is chosen to be recorded alongside any call made in the tool.

## To do

1. Decide which behaviour the viewer should have, per surface if that is the honest answer
   (instrument page vs report page).
2. Make the code, the `_raster` comment and the `CLAUDE.md` convention agree.
3. If the wheel keeps the zoom, consider whether the current x-range belongs in anything
   the viewer exports, so a call or a screenshot carries the scale it was made at.

## Verified, not inferred

Rendering the raster element through `hv.render(..., backend="bokeh")` runs the hook and
produces the model the browser would get. The toolbar it builds:

```
active_scroll : WheelZoomTool
active_drag   : PanTool
  tool WheelZoomTool    dimensions=width
  tool PanTool          dimensions=width
  tool HoverTool        dimensions=None
  tool ResetTool        dimensions=None
  tool ResetTool        dimensions=None
```

**The wheel is claimed, and it zooms x.** The `_raster` comment and the `CLAUDE.md`
convention are both wrong as written; the code is doing what its own hook docstring says
it should. Drag-pan is x-constrained too, which is the one part all three agree on.

*(Minor, while the model is open: `ResetTool` appears twice — `tools=[..., "reset"]` and
`default_tools=["reset"]` each contribute one. Harmless, one redundant toolbar button.)*
