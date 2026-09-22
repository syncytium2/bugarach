# Role 10 — Ship It (round 1, verbatim as returned)

GRANT 10 ok — Read, Grep, Glob, Bash

I hold Read, Grep, Glob, Bash and SubagentHandback, and no Edit, Write or NotebookEdit. I modified no file. My inspection ran as inline `python -c` calls. A hook blocks heredoc source files, and I have no Write tool, so I left no script behind.

# Role 10 — Build and craft gate, round 1

**Artifact files** (all in `<scratchpad>\methods_build_r0\`):
- `coordination_pipeline_methods.docx`
- `coordination_pipeline_methods.html`
- `coordination_pipeline_methods_page01.png` to `page06.png`

**Source:** `docs\methods\coordination_pipeline_methods.md`

## Build currency: PASS
- The source .md was modified at 22:47:53.
- `build_methods.py` was modified at 22:48:14.
- The .docx was built at 22:48:27 and the .html at 22:48:28.
- The page PNGs were rendered from 22:48:32 to 22:48:33.

Every output is newer than the source and the builder, and the PNGs are newer than the HTML. Nothing is embedded besides `methods.css`, which is written at build time.

## Checked against the renders (six HTML PNGs, each opened)

| page | render it was checked against | content present (vs. source .md) | legible | numbering | units | overflow / overlap |
|---|---|---|---|---|---|---|
| 1 | page01.png | Title, subtitle, "Detected calcium events" in full, group table (4 rows), 2 artifact bullets, start of "Synthetic recordings" through the quiet/busy bullets | yes, 12 pt serif | **group table has no number or caption** (F2) | "events s⁻¹ per cell" renders; table headers name the counts (animals, recordings) | none; text column is x 190–1310 of 1500 px (about 75% of width) |
| 2 | page02.png | quiet/busy bullets again (scroll overlap), coordinated events, distractors, widths, benchmark, ⚠ benchmark value, test recordings, start of Scoring | yes | n/a | s, events s⁻¹ and % all present | none |
| 3 | page03.png | Scoring formulas, Table 2 with caption, ⚠ close-events line, Coded detectors bullets | yes | **Table 2 comes before Table 1** (F1) | calls min⁻¹ and calls h⁻¹ present | none; the equal 7-column grid wraps the first column onto 3 to 5 lines ("no-/coordination") (F5) |
| 4 | page04.png | SPIKE-synch bullet, tolerance paragraph (10⁻⁹ ×2), Table 1 (6 rows, all present), Optimization steps 1–4, start of Learned detectors | yes | Table 1 appears here, after Table 2 (F1) | 10⁻⁵, s and frames present | none; the last line on the page is cut mid-glyph and repeated on page 5 (screenshot slicing, not the document) |
| 5 | page05.png | Architectures (4), training, decoding (10⁻⁴), comparison, folds, selection rules, replication, separability with √(3/7), start of Analysis | yes | n/a | ok | none |
| 6 | page06.png | Analysis: windows, recordings analysed, ⚠ 15-min line; Width and amplitude with ⚠ paragraph; References (3) | yes | n/a | min and cells s⁻¹ present | none; "(13–/20 min)" breaks after the en dash (cosmetic) |

**Element walk:**
- All 10 section headings of the source are present in the HTML render.
- All 3 tables are present.
- All 4 ⚠ flags are present.
- All 3 references are present.
- Both ordered lists are present (4 steps and 3 steps).

Nothing is dropped. No figures exist in this artifact, so the axis, legend, colorbar, glyph and panel-lettering checks do not apply. I checked for figures and found none.

## Checked on the .docx (python-docx and the raw XML; no render)

| element | result |
|---|---|
| Heading styles | Title → `Title`; subtitle → `Subtitle`; all 10 sections → `Heading 2`. The mapping is correct. No `Heading 1` exists, so the outline jumps from Title to level 2 (F6). |
| Tables | 3 of 3 survive with every row and cell intact: 5×3, 5×7 and 7×3. Header rows carry `tblHeader`, so they repeat when a table crosses a page. The style is pandoc's `Table`, with a rule only under the header and no cell borders; it looks unlike the boxed HTML (acceptable for a manuscript, noted). The 7-column table is fixed-layout with equal 1131-twip (0.79 in) columns (F5). |
| Table captions | Plain `Body Text` paragraphs. They use no `Caption` style or SEQ numbering field, and have no keep-with-next, so Word can strand a caption at the foot of a page away from its table (F4). |
| Symbols | Counts in the .docx equal the counts in the source for every symbol checked: ⁻ 11, ¹ 7, ⁹ 2, ⁵ 1, ⁴ 1, ⚠ 4, √ 1, α 2, ≤ 1, × 1, – 12. All are preserved. `findpeaks` keeps its code style (`VerbatimChar`). |
| Lists | Bullets use a bullet format. The two ordered lists use separate decimal numbering instances (numId 1008 and 1014), so the second restarts at 1. Correct. |
| Core properties | title = the document title (correct). created = modified = 2026-09-22T02:48:27Z, the build time (correct; not inherited from a template). **author / creator is empty** (F3). |
| app.xml | **Carries the template's stale statistics**: Words 83, Lines 12, CharactersWithSpaces 583, TotalTime 6, Application "Microsoft Word 12.0.0". None of these describe this file (F3). |
| Page setup | `sectPr` has no `pgSz` and no `pgMar`, so page size and margins fall to whatever each reader's Word defaults to, Letter or A4 (F7). |
| **Page render of the .docx** | **NOT RUN.** No LibreOffice or soffice exists on this machine, and the six PNGs are scroll slices of the HTML, not pages of the .docx. The Word pagination (table breaks, caption orphans, the width of the 7-column table on a real page) has not been checked against any image. Under this role's contract that is a failure, not a clean result (F8). |

## Findings

| # | location | issue | severity | suggested fix | could I verify it against a source? |
|---|---|---|---|---|---|
| F1 | source lines 121–135 vs 165–176; HTML pages 3–4; .docx table order | Tables are numbered out of order. Table 2 is cited, captioned and placed (docx table index 1) before Table 1 (index 2). Readers and journals expect tables numbered in order of first appearance. | medium | Renumber: the admissibility table becomes Table 1 and the settings table becomes Table 2 (or reorder sections), and update every "Table 1" / "Table 2" reference, including "its Table 1 setting" and "with the Table 1 settings". | yes (render and docx) |
| F2 | source lines 25–30; HTML page 1; .docx table 0 | The group table has no number or caption, while the other two tables carry both. Every table in a manuscript needs a numbered caption. | medium | Add a caption such as "Table N. Animals and recordings per group." and number it in sequence; it would become Table 1 if F1 renumbers by appearance. | yes |
| F3 | .docx `docProps/core.xml`, `docProps/app.xml` | `dc:creator` is empty. `app.xml` carries the template's figures (Words 83, TotalTime 6, "Microsoft Word 12.0.0"), which name the reference template, not this file. The document properties do not identify the file. | low | In `build_methods.py`, stamp author (pandoc `--metadata author=...` or python-docx after the build) and drop or regenerate `app.xml` statistics; a save through Word or a post-step would do it. | yes |
| F4 | .docx caption paragraphs "Table 2." and "Table 1." | Captions are unstyled `Body Text` with no keep-with-next, so Word can separate a caption from its table across a page break. Journals' Word workflows also expect the `Caption` style. | low | Use pandoc's table-caption syntax (`Table: ...` under the pipe table) so the caption is emitted as a Table Caption style bound to the table, or post-process to add `keepNext`. | yes (XML); breakage itself not observed, since no docx render exists |
| F5 | Admissibility table (7 columns); HTML page 3; .docx fixed equal grid | The label column gets the same width as the numeric columns (0.79 in in the .docx; one seventh in the HTML), so labels wrap onto 3 to 5 lines ("no-/coordination", "close-events test, largest F1 loss vs. the setting it replaces" across 5 lines). The six numeric columns are mostly empty space. | low | Set relative column widths in the source (a pandoc grid table or wider dashes in the pipe-table separator, e.g. `|------------|---|---|...`) so the first column gets about 35%. | yes (HTML render); docx geometry from the XML only |
| F6 | .docx heading hierarchy | Sections are `Heading 2` directly under `Title`, with no `Heading 1`. The navigation pane works, but the outline skips a level, and a journal template that maps Heading 1 to section heads will misplace them. | low | Use `#` for sections in the source, or pass `--shift-heading-level-by=-1`. | yes |
| F7 | .docx `sectPr` | No page size or margins are set, so the layout depends on each reader's Word default. | low | Supply a `--reference-doc` with Letter (or the journal's size) and 1 in margins. | yes |
| F8 | the .docx deliverable as a whole | No page render of the .docx exists. The "page01..06" PNGs are 1200-px viewport slices of the HTML: a 1150-px step with a 1200-px viewport gives a 50-CSS-px (100-image-px) overlap, and the last slice is clamped. They are not pages of the Word file, so Word pagination, table page breaks and caption orphans are unverified. | **high (gate)** | Render the .docx itself (LibreOffice `soffice --headless --convert-to pdf`, then page images, on a machine that has it, or Word export to PDF) and re-run this table against those pages. Until then, every docx layout row above is only an XML check. | no (no renderer available here) |
| F9 | subtitle "Draft for review, 2026-09-22" | The build ran at 22:48 local time on 2026-09-21 (02:48Z on 09-22); the environment's date is 2026-09-21. The subtitle carries the UTC date, a day ahead of local time. | low | Confirm the intended date, or stamp it from the build time in local time. | yes |

**Scope boundaries.** I filed no findings on prose, claims or citation completeness, for example "(Kreuz et al.)" with no year, or the italic *Optimization* cross-reference not matching the heading "Optimization of coded detectors". Those belong to other roles and I noted them only in passing. The main thread should route them if no one else reports them.

**Verdict for round 1: FAIL.** The HTML render passes every mechanical row except table numbering (F1, F2). The .docx content survives intact: headings map to Word styles, all 3 tables are complete, and every symbol count matches the source. But the .docx pages were never rendered (F8), so its layout rows rest on XML inspection alone.

---
*Transcription note: personal absolute paths were replaced with placeholders (sapper SAP004); nothing else was altered.*
