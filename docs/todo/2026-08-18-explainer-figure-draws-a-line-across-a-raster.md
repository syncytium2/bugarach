---
status: open
filed: 2026-08-18
---

# The explainer draws the one mark the raster viewer argues against

`tools/make_explainer_figures.py` draws a `VLine` across a raster zoom to mark a
planted event. `docs/site/raster_viewer.html` argues at length that a vertical
line across a raster is a **reading** rather than data — it asserts alignment
that the reader should be judging for themselves, which is the same objection
that made every raster onset draw identically (2026-08-18).

Found by the murderboard while reviewing that change; left alone because it is a
different figure with a different generator, and fixing it means deciding what
replaces the line — a marker above the panel, like the diagnostic's planted row,
is the obvious candidate and matches what the rest of the tree now does.
