---
status: done
opened: 2026-08-23
found-by: viewer-page-dates (reporting; the files belong to other lanes)
closed-by: built-site-works
---

# The front page ships a degraded figure, and says so only on stderr

> **DONE 2026-08-23** by `built-site-works`, which holds `tools/build_site.py`.
> The call passes `dt`, taken from the generator's own `grid_sec` — the imaging
> grid it quantized the onsets onto — so nothing is assumed and FOUNDATIONS §6
> is answered by the stage that actually knows. A second break was hiding behind
> the first: `StreamResult` had grown a fifth field and the call unpacked four
> positionally, so fixing `dt` alone only changed the exception. Fields are read
> by name now, and a sixth will not break it.
>
> **Both halves of the recommendation below are in.** The build reads the
> diagnostic's sidecar and **refuses** when any detector did not run, and a
> missing hero is a hard failure too rather than the one asset that could go
> quiet; `--allow-degraded` prints what is wrong and ships it, for a local look
> and not for a deploy. `tests/test_site_coherence.py` covers the sidecar parser
> and asserts the published payload scored every detector.
>
> **One correction to the diagnosis below**, because it matters to anyone reading
> this as a worked example: the page did **not** fall back to `LEAD_FALLBACK`.
> Playwright was working, `hero.png` rendered, and it was a valid 196 KB PNG. It
> was a picture of a raster with six blank detector lanes. That is worse than the
> text fallback, which at least announces that it is standing in for something —
> the published figure looked like a figure, and read as six detectors finding
> nothing. Rebuilt, it is 974 KB.

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
