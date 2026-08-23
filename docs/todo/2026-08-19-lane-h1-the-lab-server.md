---
status: done
filed: 2026-08-19
closed: 2026-08-20
---

# DONE — Lane H1, the lab server, so the tube trains without the page learning to talk

Landed on `main` at `9ed4140` (PR #159): `src/bugarach/lab.py`, `bugarach lab`, and
`tests/test_lab_server.py`. **The "done means" below was met exactly** — the server's
train path reproduces `docs/learned/bakeoff.json` per fold, not approximately:

| fold | F1 ours | F1 published | threshold | hit / planted | detected |
|---|---|---|---|---|---|
| 0 | 0.6933 | 0.6933 | 0.9970 | 26 / 30 | 71 |
| 1 | 0.6667 | 0.6667 | 0.9908 | 24 / 30 | 47 |
| 2 | 0.7273 | 0.7273 | 0.9716 | 24 / 30 | 58 |
| 3 | 0.5846 | 0.5846 | 0.9983 | 19 / 30 | 45 |

Mean **0.668 ± 0.061** either way, 1,149 parameters, 25 s for four folds. That equality
is the evidence there is one training path rather than two — it is
`tests/test_lab_server.py::test_the_server_reproduces_the_published_bakeoff`, and it
**skips where torch is absent**, which includes CI (`.github/workflows/ci.yml` installs
`[ui]`, not `[dl]`). Said plainly rather than implied to be covered.

## What lane H2 needs from here: the shapes are settled

H2 — the inert `if (window.__lab)` panel in `docs/site/raster_viewer.html` — was waiting
on exactly this. Claim that file on the machine-local board first; it is the
single-holder resource.

- `window.__lab.capabilities()` → `{trains, reason, torch, trainer, models, viewer}`.
  **torch's absence is an answer, not an error**: `trains: false` with `reason` carrying
  the `pip install bugarach[dl]` line. The panel says so and every other stage of the
  page keeps working.
- `window.__lab.train({spec, arch, folds, seeds_per_fold, steps}, onProgress)` →
  `{model, arch, threshold, dt, n_params, per_fold, f1, recall, precision, train_sec,
  detect_sec}`, the spreads shaped like `fair_bakeoff.py`'s. `spec` is the **generator
  settings measured from the user's own untreated recordings** — the data set is simulated
  from those, and the recordings being analysed are never the training set. Absent, the
  server refuses rather than defaulting.
- `window.__lab.detect({model, recordings: [{slice_id, rois}]}, onProgress)` →
  `{model, arch, detections: [{slice_id, onset_sec, width_sec, threshold, dt}]}`.
  `slice_id` comes from the data and is never a filename.
- `onProgress` receives `{stage, fold, of, done, message}` as the fit runs —
  `simulating` → `fit` → `scored`. The transport is chunked NDJSON, so this arrives during
  a multi-minute fit rather than after it.
- **`threshold` is refused, not ignored.** So are `retune`, `calibrate` and `min_rois`.
  The panel must not offer that control; the server will throw with the reason if it does.

`bugarach lab --stub` serves all of it against a trainer that fits nothing and calls an
event a minute — drive the panel against the seam without paying 25 s per reload.

## What is NOT done here, deliberately

- **The panel itself** is lane H2, and it holds `raster_viewer.html`.
- **The JS trainer** is lane C / Phase 3b. It is not cancelled; it now has a reference
  implementation to be checked against, which was the point of sequencing it after this.
- **Multi-architecture progress in one call.** `arch` is one per request (`tube`,
  `trace`, `tiny`); a scoreboard over all three is three calls. Phase 4's row-per-detector
  screen may want them batched — that is a small addition, not a redesign.

---

*Original todo, kept because the traps below still bind whoever builds on this:*

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

Point it at a generated data set and the numbers it returns agree with
`docs/learned/bakeoff.json` — same detections, same counts. That check is available from
the first endpoint onward, which is why it comes before any screen.
