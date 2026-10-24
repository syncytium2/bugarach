GRANT 9 MISMATCH — missing none; holds Edit, Write, NotebookEdit (deferred), PowerShell, Agent, Artifact, Skill, ToolSearch, Claude Docs batch/update (MCP write tools), plus deferred Dropbox, Gmail write tools, WebFetch, WebSearch, SendMessage (spawned through the inline fallback as general-purpose). I used only Read, Bash and Grep, and wrote only to `_scratch/r2-role-09/`. No tracked file was edited.

# Role 09: Show, Don't Tell. Review of Aim 0 (r2)

**How I measured.** GitHub Markdown has no fixed canvas, so I treated each section as a "page". The script `_scratch/r2-role-09/count.py` parsed `_scratch/r2_extract.md`, which matches page lines 16–241 plus the plan item. It counts words (link targets, markup and table pipes stripped) and finds the largest single block: a paragraph, bullet, caption or table row.

Figure share is estimated, not taken from a browser screenshot. There is no headless browser here.
- **Column width:** I assumed a GitHub content column of 880 px and checked 760 and 1012 px.
- **Figure height:** every PNG is wider than the column (1950, 1950, 1430 and 1950 px at 130 dpi), so GitHub scales each to the full column width. Rendered height = 880 × h/w, giving 434, 446, 352 and 270 px for Figures 1–4.
- **Text height:** about 112 characters per line, 24 px line height, ~10 px between blocks, 40 px per heading or table row.
- **Share** = figure height ÷ section height. Because every figure already fills the column width, this equals the area share.
- **Sensitivity:** the shares move about ±5 points across 760–1012 px, and no verdict changes.
- **Side margins:** none on GitHub; each image fills the column. So the side-margin rule cannot fire, and the remedy is to move text out of the section, not to reflow it around the figure.

**Thresholds** (project conventions, not optima): more than 40 words per page; any block over 60 words; a results or methods page with no figure; 2 or more prose-only pages in a row; figure share under 50%.

## Count table

| page (section) | total words | largest block (words) | figure | figure share (880 px; 760–1012) |
|---|---|---|---|---|
| Where it stands | 188 | 69 (bullet 2, "Aim 0 (theory) added") | n | 0% |
| Symbols and tools used below | 169 | 94 (the run-on symbol line) | n | 0% |
| Aim 1a, first result | 343 | 95 (Fig 1 caption) | y (Fig 1) | **44%** (38–48) |
| Aim 0, the predictions | 551 | 106 ("What it rests on") | y (Fig 2) | **34%** (28–38) |
| Aim 0, checked by two more sessions | 441 | **151** ("What only the blind passes found") | n (has a 5-row table) | 0% |
| Aim 0, membership and order (whole) | 768 | 109 ("Order" paragraph) | y (Figs 3, 4) | **33%** (28–38) |
| · sub-page: intro + Fig 3 + Membership | ~250 | 102 | y | ~46% |
| · sub-page: Fig 4 + Order + Kreuz + generator | ~520 | 109 | y | ~25% |
| Tried and dropped | 118 | 44 | n | 0% |
| Plan item "Aim 0: predict first…" | 294 | 64 (item 4) | n | 0% |
| GLOSSARY: "Two measures of one spread" | ~60 | ~60 | n | n/a |
| GLOSSARY: Synthetic-validation vocabulary | ~256 | ~45 | n | n/a |

**Every page exceeds 40 words**, and every figure page is under 50%. Blocks over 60 words: 17 in total, listed in the script output. The prose-only runs are "Where it stands" → "Symbols" (two in a row), and "Tried and dropped" → the following context sections ("Settled", the tree survey).

## Findings

Each row: location · issue · severity · suggested fix · could I verify it against a source.

1. **Symbols and tools · the symbol line.** Nine symbols, their units and values, and two corrections to glossary terms (σ vs the half-width, absolute vs percentage K) are packed into one 94-word dot-separated line. That is a table typed as prose. · **High** · **Fix:** a 4-column symbol table (symbol · meaning · values in Aim 1a · not to be confused with), with the two glossary distinctions in the last column. Add a 2-row tool table (tool · what it counts · needs a threshold? · reports) to replace the two tool bullets. · Yes (source lines 35–49).

2. **Aim 0, the predictions · whole section (34% figure, 551 words).** The bullets are typed lists of numbers:
   - participants median/worst at two backgrounds;
   - rate and share residuals;
   - the joint fit, planted 0.2/0.5/1.0 s read as 0.22/0.49/1.01 and 0.20/0.52/1.01;
   - six chance-cluster rates, predicted against measured.

   The last set repeats Fig 2 D/H point for point. · **High** · **Fix:**
   - (a) Replace the residual numbers with a residual figure: a strip plot of (measured − predicted) ÷ planted for each quantity × background, with and without the at-most-one-event term. "Within seed-to-seed noise" and "the term removes ~0.05" are then visible; on Fig 2's 0.2–2.6 identity axes the grey and coloured clouds overlap and the 0.05 shift cannot be seen.
   - (b) Give the joint jitter fit its own panel: fitted σ against planted σ, log–log, with the 0.1 s frame and the 0.005 s search bound drawn and fits at the bound marked (3 and 7 of 20). No figure currently shows the "not resolved at the frame scale" claim. Fig 1 D/H show only median and IQR, and they sit back in the Aim 1a section.
   - (c) Cut the chance-cluster numbers to "Fig 2 D, H", or to a 2×3 table if the values must be quotable.

   · Yes (numbers from the page; residual visibility judged from the rendered Fig 2).

3. **Aim 0, the predictions · "What it rests on" (106 words).** This is provenance and prior-art citation on the face of a results page. · Medium · **Relocate, don't delete:** keep one sentence ("A Neyman–Scott process measured by CuBIC's cumulant route; what is new is g_n with frame rounding, the at-most-one-event term and the cross-window fit"). Move the citations, including the ⚠ not-opened flag, to a "Prior work" note under Tried and dropped, or to `theory.py`'s docstring / the README. · Yes.

4. **Aim 1a · Figure 1 share 44%, caption 95 words.** The caption is a reading key plus method details (backgrounds, what is pooled into each median, the down-triangle, sideways offsets). The ⚠ shared-seeds block repeats "Tried and dropped" bullet 2. · Medium · **Fix:**
   - Move the down-triangle and offset notes into the legend.
   - Put the background levels in the row labels (already there) and delete them from the caption.
   - Cut the ⚠ block to one line ("reseeded per recording; first record kept as `…_shared_seeds.json`") and keep the full story in "Tried and dropped".
   - Put the four bullets' key numbers on the panels: "16×" and "8×" on F; the 0.74 s ceiling as a curve (0.74/σ on the ratio axis) in D and H; and 0.4 on A/E.
   - Text then drops by ~120 words and the share passes 50%.

   · Yes.

5. **Figure 1 · y-axis range.** All 8 panels share a 0.1–30 log axis that is set by F's 16×. The "within about 25–30%" claims for A, C, E and G then occupy a few pixels. At 880 px the image is scaled to 0.45×, so tick text renders at about 8 px. · Medium · **Fix:** per-row or per-quantity y-limits (A/C/E/G at about 0.3–3), with F on its own scale or a broken axis. This judges layout, not the build, so if 8 px text is to be treated as a defect, agent 10 owns that call. · Yes (rendered PNG inspected; scale computed).

6. **Checked by two more sessions · 441 words, no figure, blocks of 131 and 151 words.** This section is mostly provenance. Its one embedded result ("event floor 6 cells at 0.01 Hz, 12 at 0.05 Hz…; chance joiners lift a 5-cell event past 6 about a third of the time") is buried in a list of who found what. · Medium · **Fix:**
   - Prose plus the existing table is the right instrument for a consistency check, so no figure is owed.
   - Turn the 151-word block into a second table: finding · blind A · blind B · already in the repository?
   - Move the event-floor result out to the Aim 1a page as an annotation on Fig 1 B/F: a marker for K against the event floor.
   - Move the caveat paragraph (shared prompt, repository and model) to `blind_README.md`, leaving the one-line ⚠ in place.

   · Yes.

7. **Membership and order · the "Order" paragraph (109 words, mechanism).** It describes, in prose, a procedure: count who leads for each pair, put the cells in an order by net lead (Borda/Copeland), then compute F as net agreement. · **High** · **Fix:** a schematic panel: a 4–5-cell toy raster, then its pairwise lead matrix, then the Borda-score order, with F computed on it. That could be Fig 4's new panel 0 or a small separate figure. The closed forms then read against a picture of what F is. · No (a judgment of form; content checked against the page only).

8. **Membership and order · the Kreuz comparison (83-word intro + 3 bullets of 77, ~70 and 79 words).** Three differences between F and SPIKE-order/Synfire Indicator are listed in running prose. · Medium · **Fix:** a 3-row comparison table (where coincidences come from · how the order is found · normalization), F against Kreuz's measure, with the 0.28 dilution factor in the normalization row. Keep the "untested" bullet on the face: it is the assertion. Move the fast-sort prior-art citations (Coppersmith, Shah & Wainwright, Kreuz 2022, Mariani 2025) to notes or a "Prior work" appendix. That is relocation; nothing is deleted. · Yes.

9. **Membership and order · section split.** At 768 words, the order half gives Fig 4 about 25% of its page. · Medium · **Fix:**
   - Split at "**Order**" into two headed sections, "Membership" (~46% already) and "Order".
   - After findings 7–8 the order section is mostly figure plus table.
   - Fig 4 is a 3-panel row with a 3.3:1 aspect ratio. In a capped-width column that leaves it 270 px tall. A taller layout gives it more of the page at the same width; GitHub's column cannot grow wider, so height is the only lever. One option: A on top, B and C below.

   · Yes (geometry computed).

10. **Captions of Figs 1–4 · no "why it matters".** All four captions describe the encoding only. None states the takeaway, which sits in the bullets below each one. · Low · **Fix:** end each caption with one clause, for example:
    - Fig 1: "a fixed K fails at the higher background; only the joint fit tracks jitter."
    - Fig 2: "the at-most-one-event term closes the participant residual."
    - Fig 3: "excess falls as 1/M; reuse E/M sets it."
    - Fig 4: "F follows (2/π) arctan τ, and order-free F is a 1/√n̄ finite-size bias."

    Methods detail stays where it is or moves to the legend. · Yes.

11. **Where it stands (188 words, prose-only, first of two prose-only pages).** A dated log is legitimately prose, but bullets 2–3 (69 and ~62 words) restate results given below. · Low · **Fix:** keep the log. Trim each bullet to its date, the event and a pointer, or add a 3-row status table (aim · state · headline · figure). The fault catalogue in bullet 3 belongs in the run record it links. · Yes.

12. **Plan item "Aim 0: predict first…" (294 words) and Tried and dropped (118).** No change. Prose is right: an ordered to-do list with dependencies, and a record of dropped routes. Neither carries a result that a figure would show. · — · None · Yes.

13. **GLOSSARY entries.** No change. Prose is right for definitions. The "Two measures of one spread" relation (half-width ≈ 1.67 σ) is short enough to stay inline. · — · None · Yes.

**Outside my scope, noted once for the main thread:** Fig 2's legend still says "exact prediction" for all three coloured series, including the rate and share panels the page now calls "predicted less well". That may conflict with the earlier finding that "exact" was stretched past participants. It is a text-accuracy question for another role, not a density one.

**Scratch:** `C:\Users\defazio\bugarach\bugarach-worktrees\synth-mb-aim0\_scratch\r2-role-09\count.py` (the count and share script) and `C:\Users\defazio\bugarach\bugarach-worktrees\synth-mb-aim0\_scratch\r2-role-09\c2.py` (the width-sensitivity variant).
