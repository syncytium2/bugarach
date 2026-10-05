GRANT 10 ok — Read, Grep, Glob, Bash

(Tools actually held: Read, Grep, Glob, Bash, plus SubagentHandback as the delivery channel. No Edit/Write/NotebookEdit. Nothing was edited. Blindness held: I did not open anything under `docs/reviews/` — the only exposure was a filename in `git status` output, which I did not read.)

> **Archivist's note.** This is the craft gate re-run alone against the **repaired** page of 2026-09-21
> (items 1–3 of Tony's ruling plus the census re-run), not a fourth full round. The process says role
> 10 re-runs in full on any blind pass and the render is what changed, so this role ran and the other
> ten did not. Recorded here so the archive cannot be read as an eleven-role round.

---

## Renders I inspected

All under `<scratch>/renders/`, produced with the worktree venv's Playwright chromium 153.0.8010.12 from the built page.

- `w1920_band00..10.png`, `w1440_band00..10.png` (11 bands each, 1300 px tall, page height 13,501 px)
- `w390_band00..15.png` (16 bands, page height 20,440 px, 2× device scale)
- Zoom crops at 3×: `z_fig1_top`, `z_fig1_bc`, `z_fig2`, `z_fig3`, `z_fig4`, `z_fig5`, `z_fig6`, `z_fig7`
- Zoom crops at 4–6×: `z4_floor`, `z4_caption`, `z3_caption`, `z5_legend`, `z6_legend`, `z7_legend`, `z_tab3_note`, `z5_junction`, `z1_panelC`
- Colour simulations at 2×: `cvd_gray_*`, `cvd_deut_*`, `cvd_prot_*` for figs 1, 3, 4, 6, 7 (SVG `feColorMatrix`, deuteranope and protanope matrices; `grayscale(1)`)

## Build currency — PASS

| check | result |
|---|---|
| committed/on-disk `index.html` SHA-256 | `c709c1005091cba3c665792991a3bd30f92e36548d00b7a8902743ef4c0f6fa8` |
| fresh rebuild SHA-256 | `c709c1005091cba3c665792991a3bd30f92e36548d00b7a8902743ef4c0f6fa8` |
| identical | **yes**, byte for byte (575,760 B both) |
| mtimes | `index.html` newer than the generator and newer than every input |
| `pytest tests/test_diagnose_chorus_collapse.py -q` | **3 passed in 4.64s** |
| SAP004 personal paths in the shipped HTML | **none** — zero matches; darkroom paths use the `<darkroom>/bugarach/…` placeholder |

## Page-level geometry — PASS

Width sweep at 320 / 390 / 480 / 600 / 768 / 900 / 1024 / 1100 / 1280 / 1440 / 1920 / 2560 px: `document.scrollWidth == clientWidth` at every one; zero elements with `right > clientWidth` outside a declared scroll container; zero with `left < 0`. Repeated at 1440 px with root font forced to 24 px (≈1.7× user zoom): still zero. Block-box pairwise collision test over `p, li, h1..h3, figcaption, figure, table, .tablewrap, .note`: **0 collisions**. Every `<svg>`'s `getBBox()` lies inside its `viewBox`.

All 10 scrollable blocks (7 `.figscroll`, 3 `.tablewrap`) carry a hint element immediately above them, `display:none` at desktop widths and `display:block` at 390 px. Verified programmatically for all 10.

## The table — one row per figure and per table

| # | id | rendered box (CSS px) | scrollW vs clientW @1440 | axes | numbering | shared limits | marks identified | verdict |
|---|---|---|---|---|---|---|---|---|
| **Fig 1** | `fig-problem` | SVG 980 × 434 | 1000 = 1000 | x 60-base ticks ✓; y per-panel, logit defined ✓ | ✓, 3 refs linked | B/C differ, **marked** in caption ✓ | ▼/ticks/bar row-labelled; down-triangles point at the panel below ✓ | **pass** (F12) |
| **Fig 2** | `fig-rates` | SVG 990 × 298 | 1000 = 1000 | ✓ units on row counts | ✓ | A/B share x ✓ | on-figure shape legend ✓; all 29 marks have tooltips | **pass** |
| **Fig 3** | `fig-census` | SVG 928 × 380 | 1000 = 1000 | ✓ "(logits, log scale)" | ✓ | A/B share x and y ✓ | on-figure legend incl. hollow rule ✓; counts match caption | **pass** (F7, F10) |
| **Fig 4** | `fig-onset` | SVG 840 × 284 | 1000 = 1000 | ✓ | ✓ | single panel | **FAIL — no on-figure legend (F2)**; bare row counts (F3) | **fail** |
| **Fig 5** | `fig-training` | SVG 830 × 462 | 1000 = 1000 | B label bare (F5) | ✓; bare back-ref (F6) | **B 0–2.0 vs Figs 6/7 0–2.5, unmarked (F4)** | 2-entry legend ✓ | **pass** (F4, F5, F6, F8) |
| **Fig 6** | `fig-curves` | SVG 830 × 504 | 1000 = 1000 | ✓ | ✓ | consistent with Fig 7 | **five series by COLOUR ALONE; two merge under deuteranopia (F1)** | **fail** |
| **Fig 7** | `fig-warmup` | SVG 830 × 356 | 1000 = 1000 | ✓ | ✓; bare caption ref (F6) | shared with Fig 6 ✓ | 3-entry legend incl. dashed 0.5 ✓ | **pass** (F6) |
| **Tab 1** | `tab-shape` | 775 px in a 1000 px wrap | **no overflow** | units on headers and cells ✓ | ✓ both refs resolve | n/a | em-dash cells explained ✓ | **pass** |
| **Tab 2** | `tab-chose` | 899 px in a 1000 px wrap | **no overflow** | units on every cell ✓ | ✓ | n/a | note explains the "failed" heading ✓ | **pass** |
| **Tab 3** | `tab-warmup` | 874 px in a 1000 px wrap | **no overflow at any desktop width** | "encoder" gloss dropped (F11) | ✓ | n/a | **† checked: cell reads "trains †" and the note below explains it, present and visible** ✓ | **pass** (F11) |

**Cross-references:** all 13 internal anchors resolve and land on the figure/table their text names. Both external links resolve on disk.

**Abbreviations** in rendered reading order: ROI, F1, logit, lr, top m, GELU, ReLU all defined at first use; Adam cited. **SD is the one exception — F7.**

## Findings

| # | location | issue | severity | fix | verifiable? |
|---|---|---|---|---|---|
| **F1** | Figure 6, all five series | Five series separated by **colour alone**. Under the deuteranope matrix the as-run curve and the "replayed at lr 0.01" curve render as the **same yellow-green** — exactly the contrast the figure exists to show. In greyscale the four coloured strokes land at luminance 128 / 140 / 149 / 166 of 255. | **major** | Give each replay its own dash pattern, and move "lr 0.01" off amber onto a blue/purple. | **yes** — `cvd_deut_fig6.png`, `cvd_gray_fig6.png` |
| **F2** | Figure 4 colour key | **No on-figure legend.** The key is the tail of a five-line grey caption, and "gray, untrained" is identified by the *word* "gray" set in the caption's own grey — no swatch. Figure 3, same idiom, has a proper legend row. | **major** | Add the Figure-3-style legend row inside Figure 4's SVG. | **yes** — `z4_caption.png` vs `z3_caption.png` |
| **F3** | Figure 4 row labels | Bare counts, and the **unit changes between rows** — the first two are starting seeds, the rest are fits. | minor | "(3 seeds)", "(279 fits)". | **yes** |
| **F4** | Fig 5B vs Figs 6/7 | Same measurement, 0–2.0 against 0–2.5, unmarked; the orange as-run curve appears in both and reads 25% taller in one. | minor | One scale, or state the tighter range in the caption. | **yes** |
| **F5** | Fig 5B y-axis | "training loss" where Figs 6/7 say "training loss (mean of 5 logged steps)" for the identical quantity. | minor | Use the fuller label. | **yes** |
| **F6** | Fig 4/5/7 captions, §5 prose | Four cross-references carry the number without the name, against the house convention; the other 13 carry it. | minor | Add the name and hyperlink them. | **yes** |
| **F7** | Figure 3 axis and legend | **SD used before it is defined** — axis and legend use it four rendered lines above the caption that expands it. | minor | Attach the abbreviation at its first body mention in §4. | **yes** |
| **F8** | Figure 5 A/B junction | Panel letter "B" wedged into a ≈22 px gutter, ≈10 px under panel A's zero line; reads as belonging to panel A. | minor | Open the gutter or move the letters to the left margin as Figure 1 does. | **yes** — `z5_junction.png` |
| **F9** | Figures 4–7 | Render 830 px inside a 1000 px column — 43.2% of a 1920 px page — running ragged against captions that use the full width. Figures 1–3 use 928–990 px. | minor | Widen or centre them. | **yes** |
| **F10** | Fig 4 (and Fig 3) floor markers | Hollow "on the floor" rings centred **on the plot spine**, half outside the plot, spine drawn through them. | minor | Inset by half a radius, or give the rings a halo. | **yes** — `z4_floor.png` |
| **F11** | Table 3 "encoder" header | Bare "encoder" where Table 1 glosses it "(units wide × layers deep)". Units dropped on second use. | minor | Repeat the gloss. | **yes** |
| **F12** | Figure 1 panel C | The y tick "−9" and the dashed threshold annotation "−9.2" render on the same pixel row, so the tick reads as the label for the line. | minor | Drop that tick or move it to a round value clear of the threshold. | **yes** — `z1_panelC.png` |

**Observation, out of my beat:** Table 3's note narrates the page's own editing history — "This note carries what used to sit in the outcome cell itself, where it made the table wider than the page and pushed the verdict … off the right-hand edge at every desktop width." I verified the claim is true of the *fix* (874 px in a 1000 px wrap; no overflow at any of 12 widths swept). Whether a published page should carry that sentence is a prose/voice call for another role.

## Overlap classes my method CANNOT see

1. **Within-SVG glyph-level collisions** — the automated test is DOM-block-level; SVG `<text>`/`<path>` children were checked only by eye at 3–6× on the listed crops.
2. **Deliberate vs accidental overplotting** in Figures 3 and 4's ~900-point scatters.
3. **Hover, focus and print states** — 1,847 `<title>` tooltips exist but none was rendered; `@media print` untested, so a paginated PDF could break figures across pages.
4. **Other engines and font stacks** — Chromium on Windows only.
5. **Widths between my samples**, and viewport heights outside 844–1080 px.
6. **Whether the numbers are right** — I verified element *counts* against the captions, not against the data files.

## Summary

Build current and byte-identical to a fresh rebuild; tests green; no personal paths; no horizontal overflow, no clipping and no box collisions at any width from 320 to 2560 px or at 1.7× font; all 13 internal anchors and both external links resolve; every scrollable block carries a visible narrow-width affordance; the footnote dagger is explained and visible. **Two major findings** — Figure 6's colour-alone encoding (F1) and Figure 4's missing colour key (F2) — plus ten minor ones.
