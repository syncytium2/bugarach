---
status: open
filed: 2026-09-11
---

# The phone figure is drawn for a box wider than most phones

The front page's model figure ships in two drawings (#537): one row for a laptop, top to bottom
for a phone. The phone drawing is 395 units wide because that is the `.arch` box bugarach
measured — at a **420 px** viewport, which is wider than most phones. The box is
`min(94vw, 78rem)` and the figure is never shrunk, so on a narrower phone the figure's box
scrolls sideways:

| viewport | `.arch` box | scrolls by |
|---|---|---|
| 375 px | 353 px, measured | 42 px |
| 390 px | ~367 px, computed | ~28 px |
| 412 px | ~387 px, computed | ~8 px |

The page itself never scrolls. Tony shipped it this way on 2026-09-11, choosing to ship now and
ask draughtsman for the right size rather than let the figure shrink below its 9.5 px type floor.

## The ask

Appended to [the request](../needs/the-front-page-figure-needs-drawing-for-its-slot.md): the
phone figure drawn for a **353 px** box, which serves every viewport from 375 px up.

⚠ **Not yet delivered to draughtsman.** It is written in bugarach's repo copy only. The shared
copy under the darkroom's `needs/` and draughtsman's queue both need either a darkroom claim on
`docs/SESSIONS.md` or a draughtsman session to file it.

## When it lands

Re-vendor code and both specs from the one draughtsman commit, run
`tools/make_architecture_diagram.py`, and deploy. The page needs no change: the tall figure
already shows at its own natural width, centred, below the wide figure's width.

## Closes when

A phone figure that fits a 353 px box is on the live page.
