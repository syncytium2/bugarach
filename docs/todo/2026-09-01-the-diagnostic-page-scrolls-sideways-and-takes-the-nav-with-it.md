---
status: open
filed: 2026-09-01
---

# The diagnostic page scrolls sideways, and the nav bar slides off with it

Found by doing what [`deploy.md`](../deploy.md) asks for and nobody had automated:
serve the built payload over HTTP and walk all four pages. Three are clean. The
fourth is not, and it is invisible from `file://`, from the build's own output and
from the whole test suite.

At a **1280px viewport**, `diagnostic.html` reports
`documentElement.scrollWidth = 1511` against `clientWidth = 1280`. The page
scrolls **231px sideways**. Scrolled fully right, the nav bar and the UNDER
CONSTRUCTION banner — both exactly 1280 wide — sit at `left = -231`, so the
`bugarach` brand and the **Overview** link are off the left edge of the window.
The reader has to scroll back to reach the navigation.

**Pre-existing, not introduced by #439.** That PR touched only `.arch`, and
`diagnostic.html` has no `.arch`. The other three pages measure clean at 1280:
HTTP 200, four nav links each, no console errors, no body overflow.

## Where it comes from

The sole overflowing element on the page is

```
html > body > div > div.bk-panel-models-layout-Column   width 1511  overflow-x: visible
```

and **nothing else on the page overflows at all** — the scan finds exactly one
row. It is not a stray wrapper around a wider figure; it is the figure's own
Panel column, declaring a width the viewport cannot hold.

## Four fixes that do not work, so nobody re-derives them

Measured, each one, rather than reasoned about:

| attempt | what happened |
|---|---|
| `.bk-panel-models-layout-Column:empty { display: none }` | **Removes the overflow and destroys the page.** Document height falls 1970 → 900: the figure goes with it. |
| `.bk-panel-models-layout-Column { max-width: 100% }` | Column clamps to 1280, page `scrollWidth` only falls 1511 → 1501. |
| `nav.site { width: max-content; min-width: 100% }` | **Worse.** Nav becomes 1824 wide and takes the page with it — `max-content` is the nav's natural content width, not the scrollable width. |
| `body > div { max-width: 100%; overflow-x: auto }` | No effect. That parent already measures 1280/1280 and does not contain the column. |

**The `:empty` result is the one worth keeping.** `children.length` on that div is
`0` and `document.querySelectorAll('canvas')` returns `0`, so every DOM scan says
the div is empty and the obvious reading is *dead markup pushing the page 231px
for nothing*. It is not. **Bokeh renders into shadow DOM**, which `*` selectors
and `.children` do not traverse, so an element-children scan reports an empty box
around a full figure. Hiding it deletes the figure. Any future work on this page
that reasons from a DOM scan has to know that first.

## What to try instead

The width is declared by the layout, not by the page shell, so the fix is
most likely a `sizing_mode` / `width` decision in `tools/make_diagnostic.py` or
[`bugarach.ui.diagnostic`](../../src/bugarach/ui/diagnostic.py) — the same place
the plot conventions in `CLAUDE.md` live — rather than CSS bolted on in
`build_site.py`'s `add_nav`. Page CSS cannot reach inside a shadow root, which is
why all four attempts above are working from the outside and losing.

Two shapes worth weighing, and they are not the same decision:

- **Make the figure fit.** If 1511 is incidental, a responsive `sizing_mode` ends
  the problem outright and the nav question never arises.
- **Let it be wide and contain it.** If the figure genuinely wants more than
  1280, it should scroll inside its own box so the *page* never does — the same
  treatment `.arch` got on the front page in #439, and the same one
  `learned_detector.src.html` already gives it with `.archwrap`.

## Mechanize the check that found it

None of this was reachable from the suite. `tests/test_site_coherence.py` proves
every link resolves; it never renders a page. The walk that found this — serve
`site/`, open each page over HTTP, assert 200, a full nav bar, no console errors
and `scrollWidth == clientWidth` — is about forty lines of Playwright and it
already exists in scratch form. It belongs beside
[`test_site_coherence.py`](../../tests/test_site_coherence.py), skipping when
Playwright is absent the way `test_lab_panel_browser.py` does.

`deploy.md` says *"So: serve the payload and open it"* and then asks a human to
click every nav link on every page. A human did that on 2026-08-23 and caught two
pages with no nav bar at all. The instruction is right and it has already paid
once; what it lacks is a machine that runs it on every commit instead of on every
deploy.

## Related

- [`../deploy.md`](../deploy.md) — the drive-it-before-you-upload section, and the
  table of what a local server cannot tell you.
- [`2026-08-21-app-notes-from-use.md`](2026-08-21-app-notes-from-use.md)
