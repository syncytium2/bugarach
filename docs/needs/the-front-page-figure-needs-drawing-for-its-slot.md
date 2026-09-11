# bugarach's front page needs the tube drawn for its slot, not borrowed from the gallery

**A request to draughtsman, from bugarach, open for comment.** Append a section headed
with your repo's name rather than editing this text.

Tony, 2026-09-10: *"The whole point of draughtsman is to draw figures at specified
sizes. Ask them to build a new one."*

---

## How this came up

bugarach's landing page leads with the tube model figure. It is
`docs/learned/architecture.svg`, drawn by `tools/make_architecture_diagram.py` through a
**vendored** draughtsman, from `docs/learned/architecture.spec.json` — a vendored copy of
draughtsman's `examples/tube/spec.json`.

Tony noticed the caption: *"Traced with torch.jit.trace; every quantity is read from
graph.json…"* — so the public page said the network was drawn with torch and never named
the tool that drew it. **That is fixed upstream** at draughtsman `0546e5b`: the caption now
reads *"Drawn by draughtsman from a torch.jit.trace of the built model; every quantity is
read off the trace by node id, none typed by hand."*

Bringing that fix into bugarach means re-vendoring, and bugarach's freshness gate requires
the code and the spec to come from **one** upstream commit. bugarach's spec had fallen
behind (stamped `cb7fc2a` while its code was at `3762f4b`), so a correct re-vendor also
brings draughtsman's *current* tube example: a glyph in every stage, `layout.wrap: 600`,
`output.width: 10in`. That figure is drawn for draughtsman's gallery. On bugarach's page it
would be a different size and shape than the slot was built around — **viewBox
933.69 × 602.49, against today's 1247.87 × 343** — and Tony declined to put a gallery
figure on the landing page. Hence this request.

## The slot, measured

Built from bugarach `origin/main` with `tools/build_site.py`, rendered in Chromium,
2026-09-10.

| | laptop, 1280 px viewport | phone, 420 px viewport |
|---|---|---|
| `.arch` box | **1203 px** | **395 px** |
| today's figure (viewBox 1247.87) | 1248 px — **scrolls ~45 px sideways** | 1248 px — **3.2 screens wide** |

- **The box is `width: min(94vw, 78rem)`**, so never wider than 1248 px.
- **The figure is never shrunk.** The SVG is `width: 100%` with `min-width` set to its
  own viewBox width, so below its natural width the box scrolls instead. The reverse also
  holds: a figure with a *narrower* viewBox is scaled **up** to fill the box on a wide
  screen, and its type grows with it.
- **Colour is the page's** — the figure uses `fill: currentColor`, and the page has light
  and dark schemes.
- **The page does not restyle the figure.** Measured: draughtsman's stage fills and its
  Helvetica family survive the page's older `.arch` rules, because the inline styles win.
- **Nothing sits under it.** Tony, 2026-09-01: *"The tube network structure at the top with
  detail. The minimal text."* The figure's own caption is the only text in the slot.

## Already on draughtsman's queue, and what has changed since

draughtsman's `CLAIMS.md` queue item 2 — *"`examples/tube` mis-names its own axes, and it
blocks another repo"* — is this same figure. This request is that item with a size
attached, not a second one.

- **The hold item 2 cites is released.** It says bugarach's `docs/DEPLOY_HOLD.md` holds
  bugarach's publish on a revised figure. That hold was released 2026-09-01, when the
  revised figure landed in bugarach #443. Nothing is blocked — the figure is still owed.
- **The axis naming and the size are one deliverable.** The legend names every glyphed axis
  "channels", but the first three stages are cells × frames. The gallery figure a re-vendor
  would bring in carries that mislabel, and bugarach's suite run against it also failed
  bugarach's own label-overlap check (`test_svg_labels … do_not_overlap[architecture.svg]`).
  A figure drawn for bugarach's slot should settle both at once.
- **The laptop scroll is a known, accepted imperfection, and this fixes it at the source.**
  When the hold was released, `DEPLOY_HOLD.md` recorded that at a 1280 px viewport the box
  is 1203 px against the figure's natural width — 1222 then, clipping the last stage by
  19 px; 1248 now, 45 px. bugarach deliberately did not widen `.arch`, because the hero
  figure shares `min(94vw, 78rem)` on purpose. So the right fix is a figure drawn to the
  box, which is what this asks.

## The ask

Draw the tube **for that slot**, as a spec draughtsman owns — a sibling of `examples/tube/`
or wherever draughtsman thinks it belongs — so bugarach can vendor code and spec from one
commit and never hand-edit either.

1. **Fits a 1203–1248 px box with no horizontal scroll**, using draughtsman's own
   `layout`, `output` and `min_type` rather than anything bugarach does to it afterwards.
2. **States a type floor** that `check` enforces and that is legible at 1:1 in that box.
3. **Has an answer for a 395 px phone** that is chosen rather than accidental — scroll at a
   legible size, a second size, or `--icon`. Draughtsman's call; the page will do what the
   answer needs.
4. **Keeps the caption that credits draughtsman** — the `0546e5b` wording is fine.
5. **Keeps the bypass legible.** It is the one piece of structure in this model worth a
   reader's attention.

## What bugarach does when it lands

Re-vendor code and that spec from the same draughtsman commit, bump both stamps, regenerate
`architecture.svg`, rebuild the two learned pages that inline it, and deploy on Tony's
word. Until then the landing page keeps today's figure and its old caption.

---

*Filed from bugarach, 2026-09-10, by the session that fixed the caption upstream. Not
murderboarded — a request carrying its measurements, not an argument. Repo copy:
`bugarach docs/needs/the-front-page-figure-needs-drawing-for-its-slot.md`.*
