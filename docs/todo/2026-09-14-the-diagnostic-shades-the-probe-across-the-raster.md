---
status: open
filed: 2026-09-14
---

# The coordination diagnostic shades the promiscuity probe across the raster

`tools/make_diagnostic.py` — the figure behind the site's detector diagnostic and the intro's
Figure 2 — tints the probe block (1200–1500 s on the bench) across the **raster** as well as the
lane above it. CLAUDE.md, *Nothing is ever drawn on the raster*: a treatment window or any other
cue goes in a lane, never over the marks, because a tinted half invites comparing ink density
between shaded and unshaded regions.

Seen on 2026-09-14 while drawing the brief intro
(`python tools/make_diagnostic.py --bench baseline_quiet --without rate coact cicada --tube`):
the planted lane carries the band, and so does the raster under it.

**Where it comes from: inside `raster_panel` itself.** When `raster_panel` is handed `gt`, it
appends `hv.VSpan(hot_window)` in `PROBE_BAND` to its own overlay before the onsets
(`src/bugarach/ui/diagnostic.py`, the `if gt is not None:` block ahead of the raster
`Scatter`). `lane_panel` draws the same band, which is where it belongs. The same module's
`region_lane_panel` docstring already states the case against exactly this — a window painted
across the raster *"tints every mark it covers"*.

**Why sapper SAP009 did not fire.** It matches an overlay spelled at a call site
(`raster_panel(...) *`, `raster* * hv.`). This one is inside the function that builds the
raster, so there is nothing to match — the rule's recorded blind spot,
`docs/sapper_feedback/2026-08-26-sap009-sees-only-what-is-named.md`.

**Next step:** delete that block from `raster_panel` (the lane keeps the band), check
`tests/test_diagnostic.py` for an assertion on it, and re-render the site's diagnostic, since
`tools/build_site.py` publishes that figure.
