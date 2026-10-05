---
status: open
filed: 2026-09-23
---

# The group raster page throws away its own zoom, so the HTML cannot be read closely

> **Not murderboarded** — a defect report for sessions in this tree. Reproduce with the
> command below. Nothing here is for an outside reader.

`tools/make_group_raster_summary.py` builds its panels through `ui.diagnostic`, which
declares the right tools on every one of them — `xwheel_zoom`, `xpan`, `reset`, with `xpan`
active, exactly the "scroll wins" arrangement CLAUDE.md asks for. **The page builder then
discards all of them**, setting `toolbar=None` on every panel:

```python
for p in flat[:-1]:
    p.opts(xaxis=None, toolbar=None, backend_opts=TIGHT)
if flat:
    flat[-1].opts(height=last_h + AXIS_PX, toolbar=None)
```

The reason it does that is good: the page's other life is a flat PNG rendered by screenshotting
the HTML, and a screenshot of nineteen toolbars is nineteen widgets nobody can press.

**The cost is that the HTML — the half a reader actually opens — has no way to zoom at all.**
Tony hit it on 2026-09-22, on the combined-stream page, in those terms: *"i need the html to
allow zooming to evaluate coordination with the new color scheme."* Whether a column of marks
is really a column is the one question these pages exist to answer, and at a 2 px mark on a
4,734 px page it cannot be answered at fit-to-screen.

## The tools are already in the file, just hidden

Checked on the built page, not assumed. `WheelZoomTool`, `PanTool` and `ResetTool` each
serialise 20 times — once per panel — in a page built today. What differs is only
`toolbar_location`, which is `null` on all 20.

So this is not "add zoom". It is "stop discarding it".

## The fix, verified on a real page

One flag, and the toolbar goes on the **first** panel so it is reachable without scrolling to
the bottom of a long page:

```python
# in build_page's signature
zoom: bool = False

# after the existing toolbar=None loop
if zoom and flat:
    flat[0].opts(toolbar="above")
```

plus `--zoom` in the parser, passed through to `build_page`.

**Confirmed on `ORX_senktide`, 10 recordings**, before the prototype was discarded:

- `toolbar_location` becomes `"above"` on 1 panel and stays `null` on the other 19 — one
  toolbar for the page, not nineteen.
- **All 19 panels share a single `x_range` id**, so zooming any one zooms every raster on the
  page. That is the comparison the page is for, and it already worked; nothing could reach it.
- `xpan` stays active and wheel-zoom stays inactive-but-present, so the mouse wheel still
  scrolls the page.

## Two things to decide while doing it

1. **The PNG.** With the toolbar shown it lands in the screenshot too, so the zoomable HTML and
   the clean flat PNG are two renders. Either document that (`--zoom` implies passing
   `--no-png`, or render twice), or render the PNG from a toolbar-less copy of the layout. The
   prototype did the former because it is honest and obvious; the latter is nicer and costs a
   second build.
2. **`--roi-px`.** Separately from zoom, the default of 3 px per ROI makes a 17-ROI raster
   51 px tall, which is most of why the page reads as unzoomable in the first place. `--roi-px 8`
   made it 136 px and was much easier to judge. The proportional-height rule is right and is not
   in question (Tony, 2026-09-15); the default pitch may simply be too small for a page meant to
   be read closely rather than scanned.

## Provenance

Found while prototyping the combined-stream rasters on 2026-09-22 on `wip/combined-stream-rasters`.
**That branch is gone and should not be looked for**: everything else on it — the combined
stream, the two inks, the vermillion — landed independently and better as
[#752](https://github.com/syncytium2/bugarach/pull/752) and `src/bugarach/combined.py`, which
keeps each event's own width rule through a `label` field where the prototype dropped
`width_def` entirely. The vermillion constant and its measured justification carried over; this
one item did not, because it is a property of the page builder rather than of the combined
stream, and nothing on the combined-stream path needed it.

**The prototype was built against a checkout 119 commits behind `origin/main`, and most of a
session's work was duplicated as a result.** The cheap guard is `git fetch && git log
--oneline HEAD..origin/main -- <the file you are about to edit>` before starting, not after.
