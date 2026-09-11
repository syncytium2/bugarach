# Handoff — deploy the front-page figure drawn for its slot

> **Not murderboarded** — working material, same standing as the root `HANDOFF.md`.
> Written by `bugarach-supple-chisel` (messaging name `bugarach-ec`) just before compaction.
> Tony, 2026-09-11: *"prepare a handoff to handle deploy. pretty sure the new figure is ready."*

**The durable record is the todo:**
[`docs/todo/2026-09-10-the-front-page-figure-waits-on-draughtsman.md`](../todo/2026-09-10-the-front-page-figure-waits-on-draughtsman.md).
This file is the deploy runbook built on it. When the deploy lands, close the todo, delete this
file's pointer from the root `HANDOFF.md`, and move this file into the archive or delete it.

## Where it stands, checked 2026-09-11

- **Merged, not live:** #527 (README credits draughtsman; the figure request) and #528 (a credit line
  linking draughtsman.tonydefazio.com directly under the front-page figure). The live site is
  **48 commits behind `main`**: 5 of them change pages it serves, 4 change the viewer.
- **The figure caption is fixed upstream** at draughtsman `0546e5b` (it now credits draughtsman rather
  than torch). It is not vendored here yet, deliberately — see the todo.
- ✅ **The figure has landed: draughtsman `main` at `5705c46`** (the work itself is `99420f1`),
  delivered by `draughtsman-b3` and verified on the remote 2026-09-11. **Vendor code and spec from
  `5705c46`.** Two specs sit beside the gallery spec, and both read `examples/tube/graph.json`:
  - `examples/tube/front-page.json` → the laptop figure, one row, viewBox **1199.15 × 343** for the
    1203 px slot. **This is now the `_vendored` canonical source path.**
  - `examples/tube/front-page-phone.json` → the phone figure, top to bottom, viewBox **395 × 1053**
    for the 395 px slot — the "second size" the request allowed as the phone answer.

  Each states its slot as `output.width` with `min_type` 9.5px, so `draughtsman check` refuses
  anything that would need scaling down. The laptop figure has no glyphs, so item 2's "channels"
  mislabel is gone from this page, and the caption is `0546e5b`'s, crediting draughtsman.
- ⚠ **The renderer changed, so re-vendor `src/draughtsman/*` as well as the spec.** `render.py` now
  lets the caption's 460-unit floor yield to a narrower stated width, and keeps an edge label beside
  a vertical run off its own line. The phone figure depends on both. No other draughtsman figure moved.
- ⚠ **`tests/test_svg_labels.py` is wrong, not the figure — fix the test.** It measures with
  `getBBox()`, which ignores ancestor transforms, and every draughtsman figure wraps its drawing in
  `<g class="ds-body" transform="translate(…)">`. So it reports the phone subtitle overlapping
  "onset raster" by 69.1 × 6.0 when the real gap is 30.0 units. Measure in SVG coordinates instead —
  `svg.getScreenCTM().inverse().multiply(el.getScreenCTM())` applied to the bbox corners. ⚠ **This
  corrects a claim bugarach made:** the overlap failure cited against the gallery figure was the same
  false positive (real gap 30.4). `draughtsman-b3` ran bugarach's three test functions, with the fix,
  against both new SVGs from bugarach's venv: all pass.
- **Two figures, one slot.** `make_architecture_diagram.py` has to render twice, once per spec, and
  `lead_model()` plus the `.arch` CSS pick the figure by viewport width. The learned pages can keep
  the laptop figure.
- **Node ids come from a trace of bugarach `8cf06f6`.** If the model has changed since, `draughtsman
  check` fails on bugarach's own trace — intended, and the signal to re-trace, not a bug.

## Who deploys

- **bugarach does. The site claim `claim-the-site-for-the-viewer` (#522) stays with bugarach.** A
  machine-local board note, and the first version of this file, recorded it as handed to
  `draughtsman-b3`. That did not take: `draughtsman-b3` declined on Tony's instruction, 2026-09-11 —
  *"deploy is that repo's job, do not deploy another repos website."* This runbook is bugarach's to
  run, and the session that runs it takes the claim over on `docs/SESSIONS.md` and releases it in
  the deploy record.
- ⚠ **No session can publish.** `npm run deploy` runs `wrangler deploy`, which needs a Cloudflare
  login (`npx wrangler login` is an OAuth browser flow and cannot be scripted). **Tony runs the
  publish.** A session prepares, verifies and hands him one command.

## Runbook, once the figure exists

1. **Re-vendor code AND spec from ONE draughtsman commit.** Copy `src/draughtsman/*` (not
   `__pycache__`) to `third_party/draughtsman/`, keeping the two-line stamp at the top of
   `__init__.py`. Copy the new spec to `docs/learned/architecture.spec.json` with its `_vendored`
   key first. Bump **both** stamps to that commit. They are split today (`3762f4b` code, `cb7fc2a`
   spec). If draughtsman put the figure in a new example directory, change the `_vendored`
   canonical-source path to match.
2. `PYTHONPATH=$PWD/src python tools/make_architecture_diagram.py` — needs torch. In a worktree the
   `PYTHONPATH` is required, or you regenerate from the primary checkout's model.
3. Rebuild the pages that inline the figure: `python tools/build_learned_report.py`, then the same
   tool with `docs/learned/learned_detector.src.html`.
4. Full suite. The ones that bite: `test_architecture_diagram_is_current`, `test_svg_labels`,
   `test_site_staleness`. Freshness: `bash tools/murderboard_freshness.sh --verbose --refresh
   --label draughtsman --slug syncytium2/draughtsman --file third_party/draughtsman/__init__.py
   --file docs/learned/architecture.spec.json` — **use `--refresh`**; without it the cache served
   an upstream five days stale and called a current copy stale.
5. Land it through a green PR.
6. **Build from `origin/main` only.** A worktree detached at `origin/main`, with `git rev-parse HEAD`
   compared against `git rev-parse origin/main` first. Serve it
   (`python -m http.server 5096 --bind 127.0.0.1 --directory site`) and look at 1280 and 420 px in
   both themes. The `.arch` box measured **1203 px and 395 px**. At 1280 the figure should fit with no
   horizontal scroll, and the credit line should sit directly under it.
7. **Tony runs `npm run deploy`.** Then `python tools/site_staleness.py --brief` should report the
   site current, and the live front page should contain `arch-credit`.
8. Close the todo; delete the root pointer; release the site claim with a deploy record.

## Traps met on this thread

- **The shell is zsh**: an unquoted `$VAR` is not word-split. Name test files explicitly, or pytest
  receives one nonexistent path, runs nothing, and a `&&` chain silently stops.
- **draughtsman's board**: session names must start with `draughtsman-`; push the claim row and the
  branch in **one** push (their rule 2); release the claim in the last commit before landing
  (rule 4). Getting the name wrong turned draughtsman `main` red for minutes on 2026-09-10.
- `merge_when_green.sh` reaps the worktree when the branch lands, and two concurrent runs race.
- Optional cleanup once the figure lands: the `.arch` text and rect rules in `tools/build_site.py`
  were written for the old hand-drawn SVG. Measured, they do not override draughtsman's inline styles,
  so they are dead weight rather than a bug.
- **The board guard ignores a heading with a `/` in its description.** Its matcher strips
  everything up to the LAST `/` in the heading, not only the `Host/` prefix, so a heading ending
  `(a / b)` matches neither the worktree nor the branch and the commit is refused as unclaimed.
  Keep slashes out of the description. Found 2026-09-11; `--audit` shows it as `allow  BLOCK`.
