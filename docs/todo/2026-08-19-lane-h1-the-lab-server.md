---
status: open
filed: 2026-08-19
---

# Lane H1 — the lab server, so the tube trains without the page learning to talk

Decision: [`docs/adr/0001-the-lab-server.md`](../adr/0001-the-lab-server.md).
Plan: [`docs/webapp_completion_plan.md`](../webapp_completion_plan.md).
**Touches no file any other lane holds** — `src/bugarach/`, `tools/`, `tests/`. Start it
now; it is the long pole.

## The shape, so nobody re-derives it

- **`bugarach lab`** serves `docs/site/raster_viewer.html` **from disk** on `127.0.0.1`,
  with a shim appended that defines `window.__lab`. The shim holds the only `fetch(` in
  the system and exists only in the copy this server hands out.
- **The published page is untouched.** `test_site_viewer.py` and `build_site.py` need no
  edit, and the training panel is dead on the public site by **absence** of
  `window.__lab` rather than by anything being stripped out.
- **No filesystem access.** The page already holds the user's folder through the File
  System Access API; it posts event trains as JSON. The server reads no path and takes no
  filename from a request, so there is no traversal surface to get wrong.
- **One training path.** Call `bugarach.learn.train` and `bugarach.bench.pool_scores` —
  the functions that produced `docs/learned/bakeoff.json`. Not a second implementation.

## What to build, in an order that stays checkable

1. **The endpoints, against a stub trainer** that returns one detection a minute. The
   whole seam is then testable before any real work lands on it — the same reason
   `docs/webapp_spec.md` puts the output contract first.
2. **The real call** into `learn.train`, with per-detector progress. Costs to promise:
   the tube trains in 5.6 s and scans a held-out fold in 0.014 s; the per-cell bank costs
   236 s for a fifth of the F1 and **does not belong in a default path**.
3. **The gate.** A test asserting the published page defines no transport, and that
   `site/viewer.html` is byte-identical to `docs/site/raster_viewer.html`. Both halves:
   the first catches a shim that migrated into the page, the second catches a build that
   started transforming it.

## Traps

- **The threshold is never re-picked on the recording being analysed.** More room to
  compute does not make a "re-tune on this slice" button acceptable; it hides exactly the
  failure the regime-shift test measures.
- **Fit busy, deploy quiet.** Fitted on a quiet background and run on a busy one, the
  learned model loses 0.24 of F1 (`docs/learned/regime_shift_fitted.json`). If the server
  fits for a user, it fits on their busier recordings.
- **Frames, not seconds, inside the model.** `dt` is the loader's business. A width shown
  to a user is a *conversion* of a fitted sample count and must never be fed back in.
- **torch is the optional `dl` extra.** Absent, the server says so plainly and the page
  keeps every other stage working. It is not an error to be worked around.
- **Bind loopback explicitly.** `127.0.0.1`, never `0.0.0.0`. A lab laptop on a
  conference network is the case this is protecting.

## Done means

Point it at a generated corpus and the numbers it returns agree with
`docs/learned/bakeoff.json` — same detections, same counts. That check is available from
the first endpoint onward, which is why it comes before any screen.
