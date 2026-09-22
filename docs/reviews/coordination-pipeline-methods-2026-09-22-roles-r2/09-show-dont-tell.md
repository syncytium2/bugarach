# Role 9 — Show, Don't Tell (round 2, blind pass, verbatim as returned)

GRANT 9 ok — Read, Grep, Glob, Bash (plus SubagentHandback, which is not an editing tool; no Edit/Write/NotebookEdit held)

# Role 9: Show, Don't Tell. Blind pass, round 2, methods section

**Artifact reviewed:** the 12 rendered Word pages `<scratchpad>\methods_build_r1\coordination_pipeline_methods_docx_page01..12.png`, the built `.docx` (text and image extents pulled from `word/document.xml`), the source `docs\methods\coordination_pipeline_methods.md` at 464d995, and `docs\methods\figures\fig1_benchmark_recording.png` (2024×1014 px) with `tools\make_methods_bench_figure.py`. I did not open the round-1 role reports, since this is the blind pass.

## Finding about the run (not the artifact)
- **The render is not built from 464d995.** The page PNGs and `.docx` were written at 23:27:30. The commit is 23:30:55. A word-level diff of the docx text against the committed source finds one content difference: on page 6 the Kreuz citation still carries a day of the month, which source line 178 has dropped. Everything else matches. This is small, but it means what reviewers saw is not the committed artifact. Rebuild from the commit before round-2 adjudication. Verifiable: yes.

## Thresholds used (adapted to a manuscript methods section; these are conventions, not researched optima)
The slide rules (40 words per unit, 50% figure share) do not fit a methods section, where prose-only pages are normal. I did not flag prose for being prose. I flagged:
- (a) a single prose block over **120 words**;
- (b) parallel material that is really a table: **4 or more items sharing 3 or more attributes**, written as bullets or prose;
- (c) a table that fails as a table: headers broken mid-word, a rule carried only in the caption, or a two-column "list in a grid";
- (d) a figure narrower than **95% of the text column**, or with in-figure text under **6 pt** at print size;
- (e) more than **30% of a page left blank** by layout, excluding the end of the document.

## Count table (per rendered page)
Prose words come from the docx text, split at each page's first words. Table words are estimates, because the docx joins cell text without spaces. Page 7/8 prose is split from a combined 536. The figure is measured from its rendered ink on the page (626×306 px on a 935×1210 px page at 110 px/in).

| page | prose words | largest prose block (words) | tables | figure | figure share of page / of text block |
|---|---|---|---|---|---|
| 1 | 255 (incl. title) | ~70 (event-table paragraph) | T1 (4 of 5 rows) | n | 0 |
| 2 | 240 | ~75 (floor-pinning bullet) | T1 "all" row, header repeated | n | 0; **~40% of page blank** |
| 3 | 345 | ~80 (Planted events) | – | **Fig 1** | **17% / 27%** |
| 4 | 253 | 116 (Origin of the constants) | T2 (~60) | n | 0 |
| 5 | ~500 | 105 (CoactDetect bullet) | – | n | 0 |
| 6 | ~470 | **125 (SPIKE-synch bullet)** | T3 caption begins | n | 0 |
| 7 | ~330 | 114 (adoption paragraph, runs onto p8); 103 (Coordinate search) | T3 (~40) | n | 0 |
| 8 | ~200 | ~60 | T4 (~120) | n | 0 |
| 9 | 417 | 99 (Training) | – | n | 0 |
| 10 | 472 | **122 (Separability)** | – | n | 0 |
| 11 | 404 (incl. refs) | ~75 (width/amplitude definition) | – | n | 0 |
| 12 | 258 (refs) | – | – | n | 0; end of document |

In total: about 3,600 body words over about 10.5 pages, 4 tables and 1 figure. The PI asked for "as brief as possible". Several findings below trade prose for a table, which serves that request as well as legibility.

## Findings
Each finding gives location · issue · severity · suggested fix · whether it can be checked against a source.

1. **Table 3, p6–7: the table fails as a table.** In the render, column headers break mid-word ("rate+conte xt", "CoactDete ct") and so do row labels ("no-coordinati on test"). The fourth limit (close-events F1 may fall by at most 0.02) exists only in the 80-word caption, not in the grid. The caption also splits across the page break. **High.** Fix: transpose the table so the six detectors are rows and the limits are columns (elevated-rate calls min⁻¹, no-coordination calls h⁻¹, precision change, close-events ΔF1 ≤ 0.02). Move "set by judgement above the default-setting rates" to the Scoring text, so the caption only says what the table is. Verifiable: yes (render p7; source lines 208–218).

2. **Figure 1, p3: rendered at 5.83 in, not the requested 6.5 in.** Source line 68 asks for `{width=6.5in}`, but the docx writes `wp:extent cx=5334000` (5.83 in). The ink measures 5.7 in against a 6.5 in text column (88%). Height is 2.8 in, which is 17% of the page. **Medium.** Fix: make the builder honour the width (check pandoc's `--dpi` or image DPI handling), or pass the width in the docx step. Then give the figure the full column and more height (below). Verifiable: yes (docx XML; page 3 measurement).

3. **Figure 1: in-figure text is about 5 pt at print size.** The figure is built as a ~1000-CSS-px canvas (9 pt y ticks, 10 pt y label, 13 px header) and then shrunk to 5.83 in. That is a factor of about 0.41, so the ticks print at about 5.0 pt and the labels at about 5.5 pt, against 11 pt body text. Most journals require at least 6–7 pt. The raster ticks are sub-point, so the 10% (3-cell) planted events cannot be seen on the page at all. **Medium.** Fix: render at the print width, with the canvas about as wide as 6.5 in at the final DPI and fonts set in final points. Or raise the fonts to about 15 pt on the current canvas, and make raster marks 2 frames tall and at least 1 pt wide. Verifiable: yes (tool lines 60–71 and 108; measurement).

4. **Figure 1 breaks the house convention "no titles above plots".** The header line "Benchmark recording, quiet background, seed 1: 15 planted events (▼ 30% · ▼ 18% · ▼ 10%), ▽ 6 distractors, elevated-rate block" sits above the plot. It repeats the caption and the lane's own y labels, which already name each row with its cell count. **Low–medium.** Fix: drop the header from `make_methods_bench_figure.py` (line ~108). If the caption does not already key the colours, the fill of the block can be keyed there instead. Verifiable: yes (CLAUDE.md "Compact labeling").

5. **Figure 1: the other conventions pass.** Nothing is drawn on the raster. The elevated-rate span is shaded only in the lane. Marks in the lane point down. The time axis is minutes-friendly (0s/10m/20m). The raster's y label carries identity and count ("cells · 33"). The figure is numbered. One minor point: filled ▼ versus hollow ▽ separates planted from distractor, but each also has its own row, so the fill is redundant rather than overloaded. **No finding.** Verifiable: yes.

6. **Figure 1 caption says what the figure shows, not why it matters, and shows one background of two.** Page 2 says every seed makes a recording at each of two backgrounds, and F1 is averaged over both. The figure shows only the quiet one, so the reader never sees what the busy background does to the planted events, which is the difficulty the objective averages over. **Medium.** Fix: make Figure 1 two stacked raster pairs, same seed, quiet (0.0052 events s⁻¹ per cell) and busy (0.0190), sharing the lane layout. Add one clause to the caption saying what to look at, for example that the 10% events are barely separable from background and that the elevated-rate block is dense with no coordination. Verifiable: yes (source lines 62–76).

7. **Page 2 is about 40% blank.** Figure 1 did not fit below the section opening, so Word pushed it to page 3 and left the space empty. **Low** (a journal submission usually moves figures to the end). Fix: anchor the figure as a top-of-page float, or place it after the "Background" paragraph so text fills page 2. For submission, put figures after the references. Verifiable: yes (render p2).

8. **Synthetic-recording prose (p3–4) is really a generator specification, and Table 2 carries only half of it.** Table 2 lists the 8 re-measured constants. The design constants are only in prose across five paragraphs: 15 events, levels 10/6/3 cells, 120 s minimum spacing, 6 distractors × 6 cells between 120 and 1,100 s, block 1,200–1,500 s at 0.06 events s⁻¹ with a 30 s ramp, width distribution. **Medium.** Fix: expand Table 2 into "Table 2. Benchmark generator" with one row per constant and columns value · set from · re-measured (95% interval). Mark design constants "by design" in the last column. The prose then keeps only the mechanism (gamma rate, burst multipliers, Poisson placement, the distractor precision cap and why it exists). Also give the interval its own column, so "0.0050 (0.0028–0.0066)" stops wrapping. Keep the floor-pinning robustness sentence, currently in the Table 2 caption, but move it to a table footnote or the "Origin of the constants" text. Verifiable: yes (source lines 70–121).

9. **The test-recordings bullets (p4–5) should be a table.** There are four recording types (benchmark, and the elevated-rate, no-coordination and close-events tests), described by the same attributes: length, planted events and spacing, distractors, block, background, seeds. **Medium.** Fix: add a table with those rows and columns, keeping one sentence each for why each test exists, for example "a call in the block responds to rate without coordination". The close-events spacing provenance (39 recordings, crowding above 0.38) is a caveat to relocate, not delete: a table note or supplementary text. Verifiable: yes (source lines 123–136).

10. **The coded-detector bullets (p5–6) hold the largest prose blocks in the document (SPIKE-synch 125 words, CoactDetect 105), and they are parallel.** Six detectors share the same attributes: what is counted, window or bin, null (shift type and extent, surrogates), threshold rule, lineage, and port validation (currently a separate paragraph on p6). **Medium.** Fix: one table, "Table 3. Coded detectors", with columns counted quantity · window · null · threshold · origin · checked against. Merge in Table 4's settings as a final column, or keep Table 4 but key it to the same row order. The prose then keeps only what a table cell cannot hold: CoactDetect's "α is a threshold, not a false-alarm rate", the SPIKE-synch hysteresis scan, and the lineage and non-equivalence caveats ("its results are not results of CICADA"). Those move to table notes, not out of the document. Verifiable: yes (source lines 140–185).

11. **Table 4 (p8) is a list set in a grid.** It has two columns, the detector name takes half the width, and each settings cell is a 3–4-line semicolon string. **Low.** Fix: if it is not merged per finding 10, set the column widths to 20/80, or put one parameter per line in the cell. Verifiable: yes (render p8).

12. **Seed sets are spread over three sections with no single place to look them up.** Selection uses seeds 1–48 and the held-out score 49–96 (p7). Close-events uses 12 seeds per background. Nested CV uses 1000–1047 in 4 folds of 12, with 72 tuning recordings (p9). The replication uses 2000–2047 (p10). Learned fits use 10 training recordings plus 2 threshold recordings. A reader has to reconstruct which data touched which decision. **Medium.** Fix: a five-row table "Seed sets", with columns seeds · recordings · used for · section. Or, if a figure is preferred, a schematic Figure 2 of the nested CV split (outer 4 folds, inner 3, refits × 5 training seeds) with the seed ranges written on it. The table is cheaper and briefer. Verifiable: yes (source lines 235–238, 296–325).

13. **Table 1 (p1–2) has layout defects.** "orchidectomize d males" breaks mid-word. The four numeric columns are as wide as the group column. The "all" row is orphaned onto page 2 under a repeated header. **Low.** Fix: widen the group column (or use the abbreviation as the row label and define it in the caption), narrow the numeric columns, and keep the table on one page. Verifiable: yes (render p1–2).

14. **Separability paragraph (p10, 122 words).** **Prose is right here.** It is an argument about the limits of a correction (it was derived for random splits, the ratio fails for the 10-recording refits, so the bar is descriptive), not a list. No figure or table would carry it better. It is over the block threshold only; do not cut the caveat. **No change.** Verifiable: yes.

15. **Scoring match rule (p6) and width/amplitude rule (p11).** Optionally, a small schematic panel could show one call interval with its ±2.5 s tolerance, a nominal time versus jittered events, and the 0.5 s split. That would make "a call wider than the planted spacing can match any event within its extent plus 2.5 s" visible at a glance. **Low, optional.** The numbered list for width/amplitude already works. Verifiable: yes.

## What I checked
All 12 rendered pages; the docx text and image extent; the source at 464d995; Figure 1's PNG and its builder (sizes and fonts); and the house plot conventions in CLAUDE.md (raster, lanes, down-pointing marks, time axis, titles, numbering). I did not check whether the numbers are correct; that belongs to other roles.

---
*Transcription note: personal absolute paths were replaced with placeholders (sapper SAP004), and the quoted citation string for a personal communication was paraphrased (tools/check_quotes.py); nothing else was altered.*
