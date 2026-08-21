---
status: open
filed: 2026-08-18
---

# `_render_png` is copied into three figure tools

`tools/make_roi_rate_distribution.py`, `tools/assembly_power.py` and
`tools/make_assembly_figure.py` each carry their own `_render_png` — the same
Playwright-chromium screenshot helper, with the same try/except shape and the same
"skip rather than fail" contract, differing only in default viewport size.

## Why it is filed rather than fixed

Raised as F7.2 by the murderboard on `assembly_answer`
([`docs/reviews/assembly_answer_2026-08-18.md`](../reviews/assembly_answer_2026-08-18.md)).
Fixing it during that review would have put untested edits into two figures the
review did not cover, and the process's own scope rule says a fix inside a shared
helper changes every artifact that calls it. So the right move was to name it and
leave it.

## What to do

One helper — `bugarach.ui`, or a small `tools/_render.py` — taking the viewport as a
parameter. Keep the contract every copy already has: a missing Playwright or a failed
render prints and returns False, and the caller still writes its HTML and JSON. A
figure tool must not fail because a screenshot could not be taken.

While there: `assembly_power.py` and `make_assembly_figure.py` also share the
darkroom-resolution and `--numbers-only` argument shape. Worth folding in if the
helper grows, and worth leaving alone if it does not.
