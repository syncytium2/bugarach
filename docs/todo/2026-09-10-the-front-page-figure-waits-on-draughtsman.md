---
status: open
filed: 2026-09-10
---

# The front page's model figure waits on draughtsman, and the re-vendor that brings it must be whole

> **Blocked on draughtsman.** The request is filed there; this file is bugarach's half, so
> it survives when the conversation that filed it does not.

## What is wrong on the page today

Tony, 2026-09-10: *"Landing page says tube is drawn with torch and doesn't refer to
draughtsman."* The front page's lead figure is `docs/learned/architecture.svg`, inlined as
the only text in its slot, and its caption read *"Traced with torch.jit.trace; every
quantity is read from graph.json by node id."* Nothing on the page named draughtsman, the
tool that drew it.

**The caption is fixed upstream** at draughtsman `0546e5b`. It is **not on bugarach's page
yet**, and that is deliberate.

## Why it is not on the page yet

A correct re-vendor brings code and spec from one draughtsman commit, and that brings
draughtsman's current tube example with it — a gallery figure, two rows, viewBox
933.69 × 602.49 against today's 1247.87 × 343. It carries draughtsman queue item 2's axis
mislabel (every glyphed axis called "channels", though the first three stages are cells),
and bugarach's own suite failed on it: `test_svg_labels … do_not_overlap[architecture.svg]`.
Tony declined it: *"The whole point of draughtsman is to draw figures at specified sizes.
Ask them to build a new one."*

**The request:** [`needs/the-front-page-figure-needs-drawing-for-its-slot.md`](../needs/the-front-page-figure-needs-drawing-for-its-slot.md)
(the darkroom's `needs/` holds the shared copy), and draughtsman's `CLAIMS.md` queue
**item 11**, which builds on item 2.

## bugarach's half, when the figure lands

1. **Re-vendor code AND spec from the same draughtsman commit**, and bump both stamps.
   ⚠ They are split today — code `3762f4b`, spec `cb7fc2a` — a half-finished re-vendor left
   by #480, which is the case freshness family 3 in `tools/check_vendor_freshness.sh` exists
   to catch. Do not re-copy one without the other.
2. Regenerate with `tools/make_architecture_diagram.py` — it needs torch, and in a worktree
   `PYTHONPATH=$PWD/src`, because a worktree otherwise imports the primary checkout's `src`.
3. Rebuild the two pages that inline it: `tools/build_learned_report.py`, and the same tool
   with `docs/learned/learned_detector.src.html`.
4. Full suite. The ones that bite here: `test_architecture_diagram_is_current`,
   `test_svg_labels`, `test_site_staleness`.
5. **Render the front page and look**, at 1280 and 420 px — the `.arch` box measured
   1203 px and 395 px on 2026-09-10, and the figure is never shrunk below its viewBox width.
6. Deploy on Tony's word, with the site claimed on `docs/SESSIONS.md` first.

## Noticed along the way

- **The freshness gate served a five-day-old upstream from its cache.** Without
  `--refresh` it reported draughtsman upstream as `fc4989e`, an ancestor of `main`, and
  called the copy stale; with `--refresh` it said current at `0546e5b`. The cache lives in
  the git common dir. The gate is vendored from murderboard, so the fix belongs upstream
  there, not here.
- **The site builder's `.arch` CSS was written for the old hand-drawn SVG.** It sets text
  to 12px monospace and rects to `fill: none`. Measured 2026-09-10, it does **not** override
  draughtsman's inline styles — stage fills and the Helvetica family survive — so it is dead
  weight rather than a defect. Worth removing when the new figure lands, and checking again
  if the figure ever drops its inline styles.

## Closes when

The figure drawn for the slot is vendored whole, the page shows it with the credit, and
Tony has deployed it.

## Added 2026-09-10, later the same day

- **The page now links draughtsman beside the figure** — Tony: *"make sure there's a link to
  draughtsman near the figure."* `lead_model()` in `tools/build_site.py` emits a credit line under
  the `.arch` box, linking `https://draughtsman.tonydefazio.com` (the repo is public; the site
  answers 200). It is page text, not figure text, so it survives any re-vendor.
- **draughtsman queue item 12** asks for links **in the SVG itself**, opt-in and off by default —
  Tony: *"ask draughtsman to put links in their output upon request."* When it lands, the credit can
  move into the figure's own caption and the page line can go. Filed at draughtsman `8764da0`.
- **Not deployed.** The live site shows neither the link nor the new caption until Tony says go.

## Landed 2026-09-11 — no longer blocked on draughtsman

- **The slot-sized figure is on draughtsman `main` at `5705c46`**, delivered by `draughtsman-b3`:
  `examples/tube/front-page.json` (laptop, one row, viewBox 1199.15 × 343) and
  `examples/tube/front-page-phone.json` (phone, top to bottom, 395 × 1053). The runbook is
  [`docs/handoffs/2026-09-11-deploy-the-slot-figure.md`](../handoffs/2026-09-11-deploy-the-slot-figure.md).
- ⚠ **A correction to this file and to the request.** Both say the gallery figure failed bugarach's
  own label-overlap check. It did fail, but the **test** is what's wrong: `tests/test_svg_labels.py`
  measures with `getBBox()`, which ignores the `translate` every draughtsman figure puts on its
  drawing. The real gap was 30.4 units, not an overlap. Fixing the test is part of the runbook.
- Still open: the re-vendor, the two-figure page, and the deploy. The deploy is bugarach's to run and
  needs Tony's Cloudflare login.

## Re-vendored and on the page, 2026-09-11 — the deploy is what is left

- **The label test was fixed first**, in its own PR (#534): it now maps every box and path sample
  through ancestor transforms, and a guard case proves the old measurement fails. The phone figure's
  reported 69.1 × 6.0 overlap reproduced under the old code and vanished under the new.
- **Vendored whole from `5705c46`**: the package and both specs, one stamp. Regenerated from
  bugarach's own trace, both SVGs are **byte-identical** to draughtsman's renders at that commit, and
  the freshness gate reads draughtsman current from the remote.
- **Both figures ship** (Tony, choosing between shipping both and the laptop one alone). The page
  switches with a container query on `.arch` at the wide figure's own viewBox width — measured, the
  wide figure fills the 1203 px box at 1280 and the tall one takes over at 1275. The tall copy's ids
  are suffixed on the page, because both drawings define `ds-arrow`.
- ⚠ **Phones narrower than 420 px scroll the figure's box sideways**, by 42 px at 375 (measured)
  and roughly 28 at 390 and 8 at 412 (computed from the same `94vw`); the page itself never scrolls.
  The 395 px phone slot this request quoted was measured at a 420 px viewport, which is wider than
  most phones. Tony chose to ship it and ask draughtsman for a figure drawn for the real phone box —
  appended to [`needs/the-front-page-figure-needs-drawing-for-its-slot.md`](../needs/the-front-page-figure-needs-drawing-for-its-slot.md).
- **Still open:** the deploy, and the narrower phone figure when draughtsman draws it.
