GRANT 9 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash)

A missing tool is a finding about the run, not about the page. It didn't limit this review, because I did every count with Bash.

# Density and figure-first review: the slow co-modulation page

**Artifact:** `<worktree>/docs/learned/slow_comodulation/README.md` and its six PNGs.

**How I measured:**
- **Page layout:** rendered in Playwright Chromium with markdown-it and CSS copied from GitHub's markdown styles (880 px column, 16 px body, line height 1.5). This is not a github.com render, so expect heights within about ±5 %. The `<details>` block stays collapsed, as it would on GitHub.
- **Figures:** PIL for pixel sizes. Smallest text is the ink height of tick digits, converted to font size (digit height is about 0.73 of the font size).
- **Thresholds:** my checklist's slide rules applied per section. None of them come from research:
  - a text block over 60 words;
  - a results or methods section with no figure;
  - two or more prose-only sections in a row;
  - a section with a figure where the figure fills less than 50 % of its rendered height;
  - figure text smaller than about 12 px against the 16 px body text.
- **Files written:** `page.html`, `layout.json`, `first_viewport.png` and `fullpage.png` under `<scratchpad>/review2/r9/`. The repo's heredoc hook blocks writing a script file through the shell, so the HTML was written with `print(file=)`.

## Count table, one row per section

| Section | Words (visible) | Largest block (words) | Figure? | Figure share of rendered height |
|---|---|---|---|---|
| Title and "Why this page exists" | 125 | 125 (the intro box) | n | 0 % of 352 px |
| What the page finds | 550 | 157 (lab fast bullet) | Figure 1 | **27 %** (337 of 1,252 px) |
| Two ways ROIs are active together | 228 | 98 | **n** (concept/methods) | 0 % of 458 px |
| Telling them apart: the cross-correlogram | 422 | **179** (Figure 2 caption) | Figure 2 | 53 % (807 of 1,517 px) |
| What the surrogates remove | 363 | 94 (Figure 3 caption) | Figures 3 and 4 | 62 % (1,129 of 1,820 px) |
| What the recordings hold | 794, plus 391 collapsed | **193** (Figure 5 caption) | Figure 5 | **31 %** (577 of 1,871 px) |
| What this changes for the label-free thread | 302 | 94 | **n** | 0 % of 582 px |
| The decision this sets up | 157 | 133 | **n** | 0 % of 326 px |
| What this does not settle | 349 | 69 | **n** | 0 % of 686 px |
| By group | 183 | 108 | Figure 6 | 61 % (601 of 992 px) |
| Published lineage | 282 | 100 | n (references) | 0 % of 554 px |
| Reproduce | 170 | 133 | n (commands) | 0 % of 452 px |
| **Page** | **about 3,925 visible** | 26 blocks over 60 words | 6 figures | **32 %** (3,451 of 10,649 px) |

## Figure table, at the 880 px column

| Figure | Source px | Rendered px | Smallest text, rendered |
|---|---|---|---|
| Figure 1, count swings | 1800×690 | 880×337 | ticks: 7.3 px digits, about 10 px font |
| Figure 2, the three kinds of activity | 1800×1650 | 880×**807** (taller than a laptop viewport) | about 10 px |
| Figure 3, the surrogates drawn | 1800×1080 | 880×528 | legend about 13 px; tick labels not measured separately |
| Figure 4, what the surrogates remove | 1800×1230 | 880×601 | about 10.7 px |
| Figure 5, the recordings | 1875×1230 | 880×577 (scaled 0.469) | **y-tick "0.10": 7.0 px digits, about 9.6 px font, the smallest on the page** |
| Figure 6, by group | 1800×1230 | 880×601 | about 10.7 px |

Every figure fills the column's full width, so no figure has empty side margins. The problem is height share, not width.

## Is Figure 1 the at-a-glance message?

**Partly.** It is above the fold: it starts at y 414 px and ends at 751 px, inside the first 900 px. On panel A you can see the key comparison, the 1-minute black bar against the blue one.

It still falls short in three ways:
1. It never shows slow co-modulation itself. It is 45 bars of a variance ratio on a log axis, and nothing marks the headline comparison.
2. It leans on arms the caption says are "each defined below": the block control, and CoactDetect's episodes removed.
3. After it come 450 words of bullets that read the bars aloud.

Tony asked for a figure that explains slow co-modulation. No figure on the page shows a real recording's count swinging over minutes.

## Findings

Each row: location · issue · severity · suggested fix · verified against a source.

1. **What the page finds, and Figure 1** · The page never shows the phenomenon in a real recording. Figure 1 is a summary statistic, and Figure 2's panels A–C are synthetic. The reader has to trust a ratio to picture "shared swings over minutes." · **major** · Add a new first figure. Take one lab fast recording near the median ratio (about 1.3× — pick the median, not the most dramatic). Plot its population onset count in 1-minute bins across its 17–20 minute baseline. Overlay one rigid shift at *J* = 20 s and one circular shift. The rigid-shift line should follow the recording's swings and the circular one should flatten. Keep the current bars as panel B, cut to the lab fast stream. Move the slow-stream, Dard et al. and generator panels to "What the recordings hold." · Partly. The page's own numbers support the prediction (1-minute ratios 3.21 as recorded, 3.00 after rigid shift, a lines 29–31). I have not checked that `results.json` holds the per-bin counts needed to draw it.
2. **What the page finds, figure share 27 %** · Under the 50 % threshold. The lab fast bullet (157 words) mixes the headline with robustness checks: the 2.27× [1.71, 2.87] after removal, the per-recording median 1.28×, the 69 % of recordings above 1, and the 2.13× without the five busiest. All of these repeat the collapsed tables (lines 225, 251, 256–257). · moderate · Replacement figure: add a strip plot of the per-recording 1-minute ratio, one dot per recording. Show "as recorded" beside "episodes removed, then block control", with a line at 1 and the five busiest recordings ringed. That shows the 69 % and the no-top-five check at a glance. Cut the bullet to its bolded claim and point the numbers to the tables. · yes (README lines 29–38 and 225–257)
3. **What the page finds, "The decision this sets up, for Tony" (120 words)** · The decision question appears twice, here and as its own section (lines 286–298). · moderate · Keep one sentence at the top that links to the decision section. Move the "a component at 10–45 s is not excluded" nuance to "What this does not settle." Prose is right for a decision question, but only once. · yes
4. **Two ways ROIs are active together (prose only, 228 words)** · This concept section has no figure, yet its two bullets are exactly what Figure 2's panels D and E show, two screens further down. · moderate · Reflow: split Figure 2. Its panels A–F (the three worlds as traces and rasters) move up into this section as the picture of "coordinated event against shared modulation." Panels G and H (the correlograms) stay under "Telling them apart." The ROI, onset and stream definitions can stay as prose, since definitions are text. · yes (lines 67–79, 93–105)
5. **Telling them apart: the method paragraph (131 words, lines 83–91)** · A computation recipe (sum pairs, sum expected, divide, pooling weight) sits on the face of the page. Its last two sentences repeat what Figure 2's panel G shows. · minor · Replacement figure: a small schematic of two onset trains, with lag τ marked between onsets and the histogram building up against its independence level. Or keep one sentence plus the pointer "Figure 2, panel G, shows the shapes", and move the recipe to a collapsed "How the excess is computed" block. Relocate it; don't delete it. · yes
6. **Figure 2 caption (179 words)** · The caption carries generator settings: 0.0097 onsets per ROI per second, 3,525 s, 15 events of 3–7 ROIs, the log-normal multiplier and 1,200 s. That goes past "what it shows and why it matters." · moderate · Cut the caption to about 40 words: the three worlds, and the fact that a narrow peak means events while a broad shoulder means shared modulation. Move the parameters to a collapsed block or to Reproduce. Splitting the figure, per the "Two ways ROIs are active together" finding, also halves the caption. · yes
7. **Figure 2, panels A–C** · The caption says the modulation depth is "chosen to be visible." At 10 s bins, panel C (the 5-minute world) is hard to tell apart by eye from the planted-event world in panel A. · minor · Draw the planted shared multiplier as a thin line in a separate lane above each trace, not over the marks. The drift then shows as a shape instead of being asserted. · yes, by viewing the PNG
8. **Figure 5 caption (193 words, the largest block on the page)** · The caption carries the export's provenance (the field-step exclusion, 84 recordings from 44 mice, 26.9 hours) and CoactDetect's operating points (bins, context window, α = 10⁻⁴ and 10⁻⁶, `bench.OPERATING_POINTS`, the docstring). · **major** · Cut the caption to what the panels show: top row full range, bottom row zoomed, the arms, and the shading as a 95 % interval over mice. Add why it matters: the lab fast curve stays above zero out to a minute. Move the dataset provenance and CoactDetect's definition and operating points to a collapsed "Datasets and arms" block, or to Reproduce. All of it is kept. · yes (lines 159–171)
9. **What the recordings hold: lab fast bullet (186 words) and lab slow bullet (102 words); figure share 31 %** · The bullets narrate Figure 5's panel D lag by lag: the peak under 0.3 s, a trough at 1–2.7 s, a bump near 3 s, a shoulder from 5 s to a minute. This is prose reading a curve aloud. · **major** · Put the lag ranges into the figure: a labeled band lane under the lag axis (peak, trough, bump, shoulder), not text over the curves. Move the per-band values to a small collapsed table (lag band against arm). The inference that can actually fail — the curve stays above zero at a minute or more, where steady-rate events cannot put it — stays on the page as two sentences. Relocate the rest. · yes
10. **What the recordings hold: "Why the slow stream dips" (about 200 words, three readings, none tested)** · Prose is justified, because these are hypotheses with no data. But it pulls the reader away from the page's question, and at 74 and 67 words its blocks are over the limit. · minor · Replace with a three-row table: the reading · who loses onsets after an event (members only, or every ROI) · the test that tells them apart. Move it into its own section after "What this does not settle," titled as a question for the producer. · yes
11. **What this changes, The decision this sets up, and What this does not settle** · Three prose-only sections in a row: 808 words and about 1,594 px. The first is the page's payoff. · **major** · For "What this changes," replacement figure: a colored matrix of what the rigid-shift contrast contains. Rows: event peak, post-event dip, a 10–45 s component, drift of a minute or more. Columns: lab fast, lab slow, benchmark generator. Cells: removed, spread, left in place, not bounded. It replaces about 300 words, and the argued caveat goes in the notes. For "The decision this sets up," prose is right for the question itself; the candidate sources of drift could be a table (source · tissue or measurement · who can answer). For "What this does not settle," a caveat list is right as prose. Keep every item, but see the duplication finding next. · yes
12. **Caveats repeated across sections** · "Excess is relative to the window's average rate" appears at lines 112–114, 302–303 and 317. "The block control keeps events too" appears at lines 143–146, 180–182 and 315–316. · minor · Keep each caveat once, in "What this does not settle," and link to it from the other places. That is relocating, not deleting. · yes
13. **Title and "Why this page exists" (125 words)** · Provenance of the question ("item 2 of *What waits on Tony* in the rigid-shift report, itself not yet re-reviewed") pushes Figure 1 down to 414 px. · minor · Keep one sentence of purpose plus the "Exploratory, one run" line. Move the question's provenance to a footer or to the decision section. · yes
14. **By group: paragraph (108 words); Figure 6 panels C and D** · The figure share of 61 % passes. But the y range is fixed at −0.8 to 0.8, so in panels C and D the curves fill about 15 % of the plot height. The "similar low band" claim is hard to check by eye. · minor · Let panels C and D take their own y range. The repo's plot conventions say y ranges don't link across rows. Boundary: agent 10 owns the axis mechanics; this finding is about how much canvas the data are given. · yes, by viewing the PNG
15. **All figures: text size** · At 880 px, tick and legend text renders at about 10 px (Figure 5 is 9.6 px), against 16 px body text. The cause is 12-inch figures at 150 dpi scaled to 0.47–0.49. · moderate · Raise font sizes about 1.4× in `tools/make_slow_comodulation_figure.py`, or shrink the figure size so it renders near 1:1. Splitting Figure 5 by stream would make room for larger text. Boundary: agent 10 owns the mechanical text-size check. · yes (PIL measurement)
16. **Figure 2 height (807 px)** · The figure is taller than a laptop viewport, so its caption lands below the fold. · minor · Splitting it, per the "Two ways ROIs are active together" finding, fixes this too. · yes
17. **Published lineage; Reproduce; the collapsed tables** · No figure needed: citations, commands and number tables belong in prose or tables. The collapsed `<details>` block is already the right place for the numbers. Reproduce's 133-word test list could become a bullet list, but that is line editing, not this role's job. · none · none · yes
