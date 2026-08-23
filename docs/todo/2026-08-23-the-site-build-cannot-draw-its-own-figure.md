---
status: open
opened: 2026-08-23
found-by: viewer-page-dates (reporting; the files belong to other lanes)
---

# The front page ships a degraded figure, and says so only on stderr

`tools/build_site.py` renders the hero and the detector diagnostic through
`tools/make_diagnostic.py`. Every run of it now prints six lines like

```
  loco: TypeError: _compute() missing 1 required keyword-only argument: 'dt'
```

one per detector, and then finishes with exit 0. The site builds. What it
publishes is the fallback: no detector lanes on the front page.

## Why

`src/bugarach/ui/app.py:338` is now

```python
def _compute(det: str, s: Slice, ext, params: dict, *, dt: float):
```

`dt` became required — correctly, and for the best reason in this repo: it is the
Panel viewer's half of FOUNDATIONS §6, landed as PR #243. The viewer itself was
updated with it (`app.py:685` passes `dt=dt`). The other caller was not:

```
tools/make_diagnostic.py:104
    t, y, events, extra = _compute(det, slice_, ext, params)["events"]
```

## Why it is worth a file rather than a line in a commit message

Two things, and the second is the larger one.

**The picture is the front page.** FOUNDATIONS §8 makes this repo a portfolio
artifact, and `index.html` leads with that figure — six detector lanes over a
raster, with hits, misses and false alarms drawn. A stranger deciding whether to
hire its author currently gets the text fallback.

**A required argument was added and one caller was missed, with nothing red.**
The build degrades on purpose when Playwright is unavailable, and that
deliberate soft landing is now also catching a genuine `TypeError` and printing
it in the same voice. No test covers `make_diagnostic.py` running end to end, so
CI is green while the published figure is missing. Whatever fixes the call is
worth pairing with a check that the build's figure step either succeeds or fails
the build for a reason other than "no chromium".

## Not fixed here

`tools/make_diagnostic.py`, `src/bugarach/ui/**` and `tools/build_site.py` are
all held by other ACTIVE lanes (`viewer-calibrated`, `site-dates`,
`built-site-works`). This lane holds `docs/site/raster_viewer.html` and reported
rather than reached across.
