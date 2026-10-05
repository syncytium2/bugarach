# Role 10 — Ship It (round 3, blind pass, verbatim as returned)

GRANT 10 ok — Read, Grep, Glob, Bash

# Role 10 (Ship It): methods docx, round 3 blind pass

**Verdict: FAIL, on one fixable defect.** Word breaks three words across lines in the table cells: "benchm/ark" in the Table 2 header, and "rate+contex/t" and "CoactDetec/t" in Table 4. Everything else passes. The build is current, the text matches the source, and nothing runs off a page or overlaps. The figure is legible at print size and the document properties name this file. A column-width fix in `_fix_docx` would turn this into a PASS without a content re-review.

## Build currency
- **Source.** `git show ee7bd62:docs/methods/coordination_pipeline_methods.md` is byte-identical (`cmp`) to the worktree file, and the worktree is clean.
- **Timestamps.** The md was last written at 00:04:57 and the figure PNG at 23:43:06. The docx and html were built at 00:06:06–07, after both. The PDF and page images followed at 00:06:26–30. The commit time (00:06:55) is later than the build, but only because of commit metadata: the committed content already existed at 00:04:57.
- **Content diff.** I converted the committed md, the docx and the html to plain text with pandoc and diffed them line by line.
  - docx: the only differences are the column padding in Tables 1 and 3. The docx also contains the Figure 1 caption, which the md-to-plain conversion drops. No words differ.
  - html: the only differences are the title, subtitle and author lines plus the same table padding.
- **Figure file.** The 1324x794 px image in the PDF is the same size as `fig1_benchmark_recording.png`.

**Currency: PASS.**

## Document properties and page setup (docx)
- **Core properties.** title = "Methods: detection of coordinated calcium events"; author and last_modified_by = "Tony DeFazio" (from the md front matter); created = modified = 2026-09-22 04:06:06 UTC, which is the build time and not a template date. revision = 0.
- **app.xml.** The template's statistics were stripped. It still says `Application: Microsoft Word 12.0.0` / `AppVersion 12.0000` / `Template Normal.dotm`, inherited from pandoc's reference docx (minor).
- **Page setup.** One section, US Letter 8.5x11 in, 1 in margins on all sides. A centred PAGE field is in the footer, and pages 1–15 render as 1–15.
- **Headings.** Title, then Subtitle, Author, and 11 Heading 1 sections. Subsections are bold run-in paragraphs. The structure is flat but consistent, with no skipped levels.
- **Captions.** Four Table Captions and one Image Caption, all set keep-with-next and keep-together.
- **PDF companion.** Its metadata Title and Author are empty. Word dropped them on export, so this does not affect the docx itself (minor).

## Per-page table (Word pages, from `coordination_pipeline_methods.pdf` via `_docx_pageNN.png` at 110 dpi)
| Page | Checked against | Content | Page break / whitespace | Overflow | Result |
|---|---|---|---|---|---|
| 1 | docx_page01.png | Title block, definitions, "Detected calcium events", Table 1 caption with all 5 rows | Table 1 is whole with its caption | none (right-aligned cells end at 542.6 pt; the text edge is 540 pt and the excess is the trailing space) | PASS |
| 2 | docx_page02.png | Exclusions, windows, start of "Synthetic recordings" | **2.36 in blank at the bottom.** Figure 1 and its caption (3.9 in) were pushed to page 3 | none | minor |
| 3 | docx_page03.png + 300 dpi crops | Figure 1 with caption, Background, Planted events | The figure is bound to its caption on the same page | none | PASS |
| 4 | docx_page04.png | Distractors to Origin of the constants; Table 2 caption with all 8 rows | Table 2 is whole with its caption | **Header "benchm/ark" breaks mid-word.** The 0.0028–0.0066 and 0.0162–0.0233 ranges wrap at the dash | FAIL (craft) |
| 5 | docx_page05.png | Test recordings, "Coded detectors", rate+context, start of CoactDetect | ok | none | PASS |
| 6 | docx_page06.png | CoactDetect to SPIKE-synch, ports paragraph | ok | The line ending "only 5%" in the binned SCE bullet runs to 552 pt, about 10 pt past the right margin (still inside the page) | minor |
| 7 | docx_page07.png | Rest of the ports paragraph, "Scoring" | **1.8 in blank at the bottom.** Table 3 and its caption were pushed to page 8 | none | minor |
| 8 | docx_page08.png | Table 3 caption with all 6 rows, "Optimization of coded detectors" | Table 3 is whole | none | PASS |
| 9 | docx_page09.png | End of Optimization; Table 4 caption and rows for rate+context, CoactDetect, LoCo | Table 4 splits across pages 9–10 and its header row repeats on page 10 | **"rate+contex/t" and "CoactDetec/t" break mid-word** in the detector column | FAIL (craft) |
| 10 | docx_page10.png | Table 4 continued (binned SCE, locust, SPIKE-synch), "Learned detectors" | Header repeated. "SPIKE-/synch" breaks at its hyphen, which is acceptable | none | PASS |
| 11 | docx_page11.png | Architectures to Two selection rules | The lead-in "Two selection rules. Every detector was selected twice:" is the last line of the page, and its list starts on page 12 | none | minor |
| 12 | docx_page12.png | Selection rules, Replication, Close-events, Separability, "Analysis of recorded data" | ok | none | PASS |
| 13 | docx_page13.png | Rates, "Width and amplitude", "Limitations" | ok | none | PASS |
| 14 | docx_page14.png | References (12 entries) | ok | none | PASS |
| 15 | docx_page15.png | References (5 entries) | Last page, so the blank area is expected | none | PASS |

**HTML companion.** I checked slices page02 (figure) and page07 (Table 4) of `_pageNN.png`. The figure is embedded (one `data:image`) and sits in a figure with its figcaption. Tables use `<caption>`. The Table 4 detector names do not break. PASS.

## Figure 1: measured
- **Placed box.** 72–540 x 72–352.6 pt, which is 6.50 x 3.90 in. That is 100% of the text width, 76.5% of the page width and 35.4% of the page height.
- **Print size of the text.** One source pixel prints at 0.353 pt. In a 300 dpi crop of the PDF, the tick digits ("30", "0s") are about 26 px tall, which is a 6.2 pt digit height and roughly an **8.5 pt font**. The panel A row labels are the same size. Legible at print.
- **Checklist items.**
  - Panels are lettered A and B, and the caption refers to them by letter.
  - The x-axis is named "time", with the house convention's minutes ticks (0s/10m/20m...) supplying the unit.
  - B's y-axis reads "cell (33 cells)".
  - Every glyph is identified: filled down-triangles for planted events (the row label gives the participation level), open down-triangles for distractors, and the caption explains the shaded span.
  - Nothing is drawn on the raster; the cue lane sits above it with down-pointing triangles.
  - The raster does not have a histogram, so the vertical-line rule does not apply.
  - One glyph per concept. Green, blue and pink contrast clearly.
- **Craft note (minor).** The panel letters "A" and "B" sit rotated and italic in the y-axis-title slot, at the same size as the tick labels. They are present, but they are not in the usual bold, upright, top-left position.

## Element walk (source against render)
- **Present.**
  - Title, subtitle and author.
  - All 11 H1 sections.
  - Tables 1–4, each with its caption, every row present (Table 1: 5 rows; Table 2: 8; Table 3: 6; Table 4: 42 across both pages).
  - Figure 1 with its caption.
  - All bullet and numbered lists, and the inline code names (tube, line_length, chorus_norm, chorus_gain_norm, recorded_data_detector_settings.csv).
  - Superscript units (s^-1, min^-1, h^-1, 10^-5), the arrows and sqrt(3/7).
- **Citations.** All 17 in-text citations have a reference entry, and there are no uncited entries: Bocchio, Bouckaert, Cecchini, Cossart, Dard, Denis, Finn, Kingma, Kreuz 2015, Kreuz 2017, Mao, Mulansky, Nadeau, Pnevmatikakis, Quian Quiroga, Satuvuori, Zaheer.
- **Numbering.** Tables and the figure are numbered and every one is cited in the text. However, **Table 4 is first cited (md line 163, page 5) before Table 3 (line 248, page 7)**, so the numbers do not follow first-citation order.
- **Units.** Counts carry their nouns (mice, recordings, cells, calls, frames). The Table 2 caption gives the rate units, and Table 3 and 4 headers or cells carry theirs.

## Findings
| # | Location | Issue | Severity | Suggested fix | Verified |
|---|---|---|---|---|---|
| 1 | Table 4 detector column, page 9 | "rate+contex/t" and "CoactDetec/t" break mid-word | moderate | In `_fix_docx`, set explicit column widths (e.g. detector 1.35 in) or `autofit` with a fixed first-column width | yes (docx_page09.png) |
| 2 | Table 2 header, page 4 | "benchm/ark" breaks mid-word; the interval column wraps "0.0028–/0.0066" | moderate | Widen the benchmark and 95% interval columns, or shorten the header to "value" | yes (docx_page04.png) |
| 3 | Page 2 bottom | 2.36 in blank above Figure 1, which moved whole to page 3 | minor | Accept, or move the figure reference paragraph or scale the figure to about 6.0 in so it fits | yes (PDF text bbox) |
| 4 | Page 7 bottom | 1.8 in blank where Table 3 moved to page 8 | minor | Accept (keep-together is correct), or place the table after the paragraph that follows it | yes |
| 5 | Pages 11–12 | Lead-in "Two selection rules...:" is stranded from its list | minor | Set keep_with_next on paragraphs ending in ":" | yes |
| 6 | Tables 3 and 4 order | Table 4 is cited before Table 3 | minor | Renumber by first citation, or reword the page-5 sentence so it does not cite Table 4 first | yes (md lines 163 and 248) |
| 7 | Page 6, binned SCE bullet | One line's ink runs about 10 pt past the right margin | minor | Probably Word's handling of "5%"; a non-breaking space before "5%" or a rewrap would fix it | yes (PDF span x1 = 552.3) |
| 8 | Figure 1 panel letters | A and B are rotated italic y-titles, not bold upright corner labels | minor | Put a bold upright letter at the top-left of each panel | yes (300 dpi crop) |
| 9 | docx app.xml | Application "Microsoft Word 12.0.0" and Template Normal.dotm come from pandoc's reference file | minor | Strip or overwrite Application/AppVersion in the app.xml pass | yes |
| 10 | PDF metadata | Title and Author are empty (Word export) | minor, companion only | Set Word's export option to include document properties, or stamp them with PyMuPDF | yes |

## Files
- Artifact: `<scratchpad>\methods_build_r2\coordination_pipeline_methods.docx` (plus the `.pdf`, `_docx_page01..15.png`, `.html` and `_page01..11.png` alongside it)
- Builder: `...\scratchpad\build_methods.py`
- My check outputs, all under `...\scratchpad\r10check\` (none of the artifact files were modified):
  - `src.md` (the committed source)
  - `fig_zoomA.png` and `fig_zoomB.png` (the 300 dpi figure crops)
  - `fig_src.png` (a copy of the source figure)

---
*Transcription note: personal absolute paths were replaced with placeholders (sapper SAP004); nothing else was altered.*
