GRANT 10 ok — Read, Grep, Glob, Bash

# Role 10 — Build & craft gate, round 1

## Build currency (gate before every row below): PASS

| fact | value |
|---|---|
| shipping artifact | `<worktree>/docs/learned/tuned_vs_coact/fair_comparison_2026_09_18/net_merge_gap.html`, 2026-09-19 21:25:54 |
| darkroom copy | `<darkroom>/bugarach/2026-09-18-fair-comparison-run/report/merge-gap.html`, 21:25:53 |
| newest embedded input | `replicate_net_merge_gap.json` 21:16:13 (also `net_merge_gap.json` 17:51:07) |
| builder | `tools/build_net_merge_gap_page.py` 21:25:02 |
| stamp | `Built 2026-09-19 21:25 -0400 … at 0.1.0+g4d522d0` — clean, no `.dirty`; `4d522d0` is HEAD~1, i.e. the code state that produced the build. Worktree clean. |

Build is newer than every input and than the builder. **Not stale.**

**But the renders I was handed are not of this file.** `…/scratchpad/pagereal/shots/*` were shot from `…/scratchpad/pagereal/merge-gap.html`, a sibling build stamped `0.1.0+g667e968.dirty` and carrying *"The tree had uncommitted changes when this was built."* I diffed the two: they differ in exactly three lines — the `<meta generator>`, the addendum link target (`index.html` vs `report.html`) and the provenance paragraph. All figure, table and prose markup is byte-identical, so the craft rows stand; but I re-shot the shipping file anyway and **every row below names my own render**, not the supplied one.

My renders: `<scratchpad>/mb10shots/` (fig1/fig2/fig3/table1/page_full_1100px/page_full_400px .png) plus zoom crops `mb10_f1a.png`, `mb10_f1b.png`, `mb10_f3leg.png`, `mb10_f3x.png`, `mb10_tab_left.png`, `mb10_400top.png` in the scratchpad root. I did **not** write these to the darkroom — that is a claimed shared resource and I am a reviewer; if any crop is to be shown to Tony, the main thread should `tools/show.py … --project bugarach` it under the existing claim.

---

## The table — one row per figure / panel / page

Rendered box measured off the render at an 1100 px viewport; page content column is 980 px.

| # | unit | render checked | box (rendered) | clip / overlap | axis + units | key complete | letters | verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | Figure 1, panel A ("This run's draw") | `mb10shots/fig1.png`, `mb10_f1a.png` | 900 × 424 px whole fig = 91.8 % of column, 81.8 % of viewport | **FAIL** — grey dot drawn over "−0.1**5**" in `◀ −0.15, mean −0.05`; blue mean bar (sw 2.4) strikes through `◀ −0.16`; `3 of 4 folds refitted, so no mean` and `◀ −0.16` overlap 36.6 × 2.5 px; dashed zero line strikes the word "mean" | x = "net minus CoactDetect, held-out F1" ✓; no y label, rows named ✓ | **partial** — `◀` glyph and the dotted group divider keyed only in the caption; "mean of 4 folds" swatch is blue but the glyph also appears grey | A ✓ | **major** |
| 2 | Figure 1, panel B ("The replicate's draw") | `mb10shots/fig1.png`, `mb10_f1b.png` | shares the 900 × 424 box | **FAIL** — grey mean bar strikes the last digit of `◀ −0.11` (renders "−0.1\|1"); `2 of 4 folds refitted, so no mean` overlaps `◀ −0.11` 36.0 × 2.5 px; dashed zero line strikes "mean" | as panel A; x-limits identical to panel A ✓ | as panel A | B ✓ | **major** |
| 3 | Figure 2, panel A | `mb10shots/fig2.png` | 900 × 424 px, 91.8 % / 81.8 % | pass (notes cross only #eee gridlines) | ✓, and A/B x-limits identical ✓ | as Fig 1 | A ✓ | minor |
| 4 | Figure 2, panel B | `mb10shots/fig2.png`, `mb10_f2b.png` | shares the 900 × 424 box | **FAIL** — `2 of 4 folds refitted, so no mean` overprints a data circle at (698.7, 266.8), 6.3 × 3.7 px | ✓ | as Fig 1 | B ✓ | major |
| 5 | Figure 3 (single panel) | `mb10shots/fig3.png`, `mb10_f3leg.png`, `mb10_f3x.png` | 900 × 404 px, 91.8 % / 81.8 % | **FAIL, two ways** — (a) legend `<text>` runs to x = 923.3 in a 900-wide viewBox: the sentence ships cut mid-word, "…on the crowded **record**" (source says "recordings"); (b) 70 `×` glyphs stacked at a 5 px pitch with ~9 px ink merge into uncountable chains in the 15 s and 30 s columns, one × sits on a blue dot in the 8 s column, and four blue dots merge into a solid bar — the caption's "offset vertically so they do not cover each other" is false as rendered | x label "merge gap" carries **no unit**; ticks do ("0 s"…"30 s") | dot ✓, × ✓ but truncated; shaded column keyed by header + caption ✓ | n/a (one panel) | **blocking** |
| 6 | Table 1 | `mb10shots/table1.png`, `mb10_tab_left.png` | 980 × 1273 px, fills the column | **FAIL** — `code{overflow-wrap:anywhere}` breaks the key "net" column mid-identifier: `chorus_ / gain_no / rm`, `line_le / ngth` | headers name units (F1, s, *t*) ✓ | 16 rows = 4 nets × 2 selections × 2 draws ✓ | n/a | major |
| 7 | Whole page @ 1100 px | `mb10shots/page_full_1100px.png` (1100 × 6098) | — | `documentElement.scrollWidth` = 1100; no `.wide` region scrolls (clientW = scrollW = 980); nothing overflows the viewport | — | — | Figures 1–3 + Table 1, numbered, no gaps ✓ | pass |
| 8 | Whole page @ 400 px | `mb10shots/page_full_400px.png` (400 × 11112), `mb10_400top.png` | — | `documentElement.scrollWidth` = **400** — no page-level horizontal scroll; prose column reflows clean, nothing cut. Figures scroll inside their own boxes (clientW 368 / scrollW 900), the documented trade | — | — | — | **pass** |
| 9 | Head, a11y, links, provenance | HTML source + Playwright DOM | — | — | — | — | — | pass (details below) |

Row 9 detail, all verified against the shipping file: `lang="en"` ✓ · `<title>The nets' merge gap, tuned</title>` ✓ · `meta description / author / date 2026-09-19 / generator` all name **this** file, no template residue ✓ · headings h1 → h2 ×9, no level skipped, no stray h3 ✓ · three inline SVGs each `role="img"` with a full descriptive `aria-label` ✓ · all four scroll boxes `role="region"` + `aria-label` + `tabindex="0"` + `:focus` outline ✓ · every figure wrapped in `<figure>` with a `<figcaption>` opening `Figure N.` ✓ · **links: the page's only `href` is `report.html`, which exists beside it (332,870 B); the darkroom build emits `index.html`, which exists beside the darkroom copy — no dead links** ✓ · provenance line present, dated, names tool and version ✓ · cross-refs to the report resolve: "the report's Figure 3" → *Merging calls*, "Figure 4" → *The nested cross-validation layout*, "section 7" → *The setting the two sides did not share: the merge gap*, "section 9" → *The coded detectors' choices*, "section 11" → *Limits* ✓.

---

## Finding list

*location · issue · severity · fix · verifiable against a source?*

**B1.** Figure 3, legend line 2, SVG x = 260 → 923.3 in a 900-wide viewBox · The key that defines the `×` is **truncated mid-word** and ships reading "…it lost more than 0.02 F1 on the crowded **record**". The `×` is the whole point of the figure. · **blocking** · Widen the viewBox to ~960, or wrap the legend onto two lines, or shorten to "…lost more than 0.02 mean F1 on the crowded recordings". Then re-shoot and re-measure. · **yes** — `getBBox()` right edge 923.3 vs viewBox 900, and visible in `mb10_f3leg.png`.

**B2.** Figure 3, the 15 s and 30 s columns; also the 8 s column · 70 `×` glyphs are placed at a 5 px vertical pitch with ~9 px of ink, so they merge into continuous chains you cannot count; one `×` is drawn over a blue chosen-gap dot (circle @ 716.6, 73.1); and the four blue dots per row merge into a solid bar. The caption asserts the opposite — "offset vertically so they do not cover each other". · **blocking** (a caption claim the render contradicts) · Raise the row pitch, shrink the glyph, or jitter on x as well as y; if the exact count is not meant to be read, say "a stack of crosses means several refused settings" instead of claiming separation. · **yes** — 4-fold overlap set dumped from `getBBox()`; visible in `mb10_f3x.png`.

**M1.** Figure 1, panel A, row *chorus_gain_norm, as run, 2 s* · A grey data circle (362.4, 186.4, 6.8 × 6.8) is drawn **on top of** the edge annotation `◀ −0.15, mean −0.05`, obscuring the "5" — 6.3 × 5.1 px of overlap. · **major** · Nudge the annotation baseline up by one line, or reserve a text gutter left of the axis and draw the annotation outside the plot area. · **yes** — programmatic text-vs-circle intersection; visible in `mb10_f1a.png`.

**M2.** Figure 1, panel A row 2 and panel B row 1 · The **mean bar is drawn through the edge annotation**: blue bar (sw 2.4, #1b5fa8) over `◀ −0.16`, grey bar (sw 2.4, #8a8a8a) over `◀ −0.11` — 2.4 × 14 px each. Panel B renders as "−0.1|1", which a reader can read as a different number. · **major** · Same gutter fix as M1, or suppress the bar's left end where an annotation sits. · **yes** — line bbox inflated by stroke-width; visible in `mb10_f1b.png`.

**M3.** Figure 1, panel A bottom pair and panel B bottom pair · `n of 4 folds refitted, so no mean` and the `◀ …` beneath it **overlap by 36 × 2.5 px** (descenders into the arrow row), and the **dashed zero line strikes through the word "mean"** in both panels. · **major** · Add ~4 px between the note and the value line; clip the zero line, or set the note on a small white backing rect. · **yes** — text/text and text/line intersections; visible in `mb10_f1a.png`, `mb10_f1b.png`.

**M4.** Figure 2, panel B, bottom row · `2 of 4 folds refitted, so no mean` overprints a data circle (698.7, 266.8), 6.3 × 3.7 px. · **major** · As M3. · **yes**.

**M5.** Figures 1 and 2, all 12 `◀` annotations and all 4 refit notes · Set at **10 px**, under the **11 px floor the page's own CSS comment declares** ("at 900px and 430px the 12-13px labels rendered at 8.1px, under the 11px floor … Legibility wins"). The page breaks the rule it cites as its reason for not scaling figures. · **major** · Raise to 11 px (or 12, matching the axis label) and re-measure widths — the annotations sit in the tightest space on the figure, so check M1–M3 again after. · **yes** — `getComputedStyle().fontSize` per text node.

**M6.** Figures 1 and 2 — the grey notes and grey `◀` annotations, fill `#8a8a8a` on white · **Contrast 3.45 : 1**, below WCAG AA's 4.5 : 1 for text under 18.66 px, at the smallest size on the page — and these strings carry the reason a whole row has no mean. (The blue `◀`, `#1b5fa8`, is 6.46 : 1 and passes.) · **major** · Darken to ≈ `#6b6b6b` (4.6 : 1) or `#595959` (7 : 1); pairs naturally with the 11 px bump in M5. · **yes** — relative-luminance computation on the computed fills.

**M7.** Figure 1 vs Figure 2, x-axis · The **same measurement** ("net minus CoactDetect, held-out F1") is drawn on **different x-limits** — Fig 1 −0.04…+0.04, Fig 2 −0.06…+0.02 — and the deviation is not marked, while Figure 2's caption opens *"As Figure 1"*, which invites a direct visual comparison at a silently changed scale. (Within each figure, A and B do share limits — that part is correct.) · **major** · Either share one range across both figures, or add one clause to Figure 2's caption: "note the x-axis runs to −0.06 here, wider than Figure 1". · **yes** — tick labels read off both SVGs.

**M8.** Every in-prose figure/table reference — `(Figure 1)`, `(Figure 2)`, `(Figure 3)` ×2, `(Table 1)`, `(Table 1, last column)`, `As Figure 1`, `in Figures 1 and 2` · All are **bare numbers with no name**, against the project convention *"a reference in prose carries the number and the name — 'Figure 3, the candidate field'"* (CLAUDE.md, Plot conventions). 0 of 9 comply. · **major** (a named, mechanized house rule, violated everywhere) · e.g. "(Figure 1, the chorus nets on F1 alone)", "(Table 1, every net in both draws)", "As Figure 1, the chorus nets on F1 alone…". · **yes** — CLAUDE.md states the rule verbatim.

**M9.** Table 1, the `net` column · `EXTRA_CSS = "<style>code{overflow-wrap:anywhere}…"` (builder line 590) breaks the identifiers **mid-token** in the table's key column: `chorus_ / gain_no / rm` and `line_le / ngth`. A reader scanning for a net sees an orphan "rm". · **major** · Scope the rule away from the table: `td code{overflow-wrap:normal;white-space:nowrap}`. The table already lives in a `.wide` scroll region with `tabindex="0"`, so it will simply scroll — the same trade the figures already make, and documented in the same CSS comment. · **yes** — builder line 590 plus `mb10_tab_left.png`.

**m1.** The review's own renders (`…/scratchpad/pagereal/shots/`) · Shot from `pagereal/merge-gap.html`, a **different build** (`0.1.0+g667e968.dirty`, carrying the uncommitted-changes warning) than the artifact under review (`0.1.0+g4d522d0`, clean). Content is byte-identical apart from the link target and the provenance paragraph, so nothing is invalidated — but the run record should not say these are shots of the shipping file. · **minor** (a finding about the run, not the artifact) · Re-shoot from the artifact path; my `mb10shots/` set already is. Name the shot file in the run record. · **yes** — 3-line diff between the two files.

**m2.** Section 1 · "(the report's Figure 3)" and "(the report's Figure 4)" sit on a page that has **its own Figure 3**. Both cross-refs resolve correctly, but the collision is one a scrolling reader will hit. · minor · Name them: "the report's Figure 3, *Merging calls*". Folds into M8. · **yes** — report captions read and matched.

**m3.** Figures 1 and 2, on-figure key · The `◀` edge-marker glyph and the horizontal dotted divider between the two net groups are **not in the key** — both are explained only in the caption (the `◀`) or nowhere (the divider). · minor · Add a key entry "◀ value beyond the axis" and a word for the divider, or drop the divider. · **yes** — full SVG `<text>` inventory dumped; no such entries.

**m4.** Figures 1 and 2, key entry "mean of 4 folds" · Swatch is drawn **blue only**, but the same glyph appears in grey on every "as run" row. One glyph, two colours, one swatch. · minor · Draw the swatch as a grey bar and a blue bar side by side, or add "grey: as run". · **yes** — computed fills `rgb(138,138,138)` and `rgb(27,95,168)` on the same element type.

**m5.** Figure 3, x-axis label · Reads "merge gap" with **no unit in the label**; only the ticks carry "s". · minor · "merge gap (s)". · **yes**.

**m6.** Figure rows vs caption vs table column · The same variant is named three ways: figure row "gap tuned, **failed refits set aside**", caption "with the refits that failed to train (under 0.2 F1) set aside", Table 1 column "gap tuned, **refits under 0.2 F1 set aside**". · minor · Pick the table's wording and use it in the figure rows. · **yes**.

**m7.** Figure 3, key vs caption vs §2 · Key says "0.02 F1"; the caption and §2 both say "0.02 **mean** F1". · minor · Make the key say "0.02 mean F1" (it is the string that gets truncated in B1 — fix both at once). · **yes**.

**m8.** Figures 1 and 2, edge annotations · Values are given to **2 dp** (`mean −0.05`) while the prose and Table 1 give 3 dp (`−0.045`). A reader checking the figure against the table meets two numbers. · minor · Use 3 dp in the annotations. · **yes**.

**m9.** HTML head/body boundary · The second `<style>` block (offset 1781) sits **inside `<main>`** (offset 1774). Browsers honour it, a validator does not. · minor · Merge `EXTRA_CSS` into the head `<style>`. · **yes** — byte offsets.

**m10.** `<style>` block 1 · `.warn{border-left:4px solid #b36b00;…}` is defined and **never used** on the page. If a warning block was meant to render (the dirty-tree note renders as a plain `<b>`, not `.warn`), it is absent; if not, the rule is dead. · minor · Either style the provenance warning with `.warn` or drop the rule. · **yes** — class census of the body: `wide` ×4, `dim` ×2, `lede`, `tcap`, `resid`.

**m11.** Table 1 · `<thead>` and eight `<th>` but **no `scope="col"`**. The surrounding region carries `aria-label="Table 1, every net in both draws"`, so the table is announced, but header association is left to the AT's heuristics on a 16 × 8 grid. · minor · Add `scope=col`; consider a real `<caption>` rather than the preceding `<p class=tcap>`. · **yes**.

---

## What passed clean, stated so it leaves a trace

Build currency (both copies newer than every input, clean git stamp) · no dead links in either copy · provenance line present and current · document properties name this file, no template residue · `lang`, `<title>`, heading order · `role="img"` + `aria-label` on all three SVGs, `role="region"` + `aria-label` + `tabindex=0` + focus outline on all four scroll boxes · figures numbered 1–3 with no gaps, each captioned `Figure N.` · Table 1 captioned · panels lettered A/B, never referred to spatially in prose · A/B share x-limits **within** each figure · **400 px: `scrollWidth == 400`, no page-level horizontal scroll, nothing cut off** · no vertical lines or bars annotating a histogram (no histogram on the page) · no colorbar on the page, so no out-of-range-colour risk · figures are given 91.8 % of the content column — the geometry is not starved.
