---
status: open
filed: 2026-08-18
---

# The one real-data figure still grades its own raster

`docs/generator/reality_check.png` is the figure that puts a real baseline
recording above the generator's imitation of it, and it is published in four
places: the README, the public site, the lead of `docs/generator.md` ("Start
here: what it is imitating"), and by name in FOUNDATIONS' data policy as the one
real recording released deliberately. Every other raster in the tree now draws each onset the
same, with detections carried by the markers along the top. That one still inks
the onsets falling inside a window LoCo called and mutes the rest, because it is
the only figure here that **cannot be re-rendered without the real store**, and
`BUGARACH_DATA_ROOT` is set on no machine this session could reach (checked
`~/.zshenv` and `~/.zshrc`; only `BUGARACH_DARKROOM` is exported there).

Its generator, `tools/make_reality_check.py`, is already fixed — it no longer
passes detection spans, and its caption no longer describes dark-versus-muted
onsets. So the committed PNG and the script that makes it now disagree, and the
script is the one that is right.

## What to do, on a machine with the store

**Two edits are needed, not one.** The script no longer inks onsets, but its
diamonds still mark each LoCo call's *onset alone* while LoCo also reports the
call's width. The old ink was the only thing in that figure carrying a call's
extent, so removing it without drawing the window makes the figure show less than
the detector reports. Draw the call as a span — `lane_panel` already does exactly
this with `hv.Rectangles` over `onset → onset + width` — and only then re-render:

```
BUGARACH_DATA_ROOT=<archive> python tools/make_reality_check.py --out docs/generator
```

Then check the render before committing it: the two panels should differ only in
texture, which is the whole argument the figure makes, and neither panel should
have any onset drawn differently from its neighbours.

## Why it matters more here than elsewhere

This is the figure a stranger meets first on the site, and the one place real
data appears at all. The old convention drew LoCo's window membership onto
individual onsets — a per-onset claim LoCo does not make — and it did so on the
real panel, where a reader has no ground truth to check it against. Of all the
rasters that carried the old convention, this is the one where it could most
easily be mistaken for a result.
