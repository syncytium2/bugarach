# Role 10 — Ship It (round 2, blind pass, verbatim as returned)

GRANT 10 ok — Read, Grep, Glob, Bash, SubagentHandback

(No editing tool held. SubagentHandback is the hand-back channel, not a review tool. I modified no file.)

# Role 10, Ship It: build and craft gate, round 2 blind pass

**Verdict: FAIL.** There are three blocking defects:
- **The build is stale.** It is one edit behind commit 464d995.
- **Figure 1's text is too small to read** at the size Word gives it.
- **Tables 1 and 3 break words in the middle.**

Everything else is minor.

## Build currency (the build is stale)

| file | mtime (−0400) |
|---|---|
| build_methods.py | 23:25:25 |
| fig1_benchmark_recording.png | 23:20:22 |
| .docx / .html | 23:27:30 / 23:27:31 |
| .pdf (from Word) / docx page PNGs | 23:27:49 / 23:27:53 |
| **source .md** | **23:30:36** (committed 23:30:55 as 464d995; the worktree matches HEAD) |

- The outputs are newer than the builder and the figure, but **older than the source**.
- I checked what the three-minute gap contains. Converting both the committed .md and the built .docx to plain text and diffing them leaves exactly one difference, in the SPIKE-synch bullet:
  - build: the Kreuz citation gives day, month and year
  - HEAD: the same citation gives month and year only
- The .html has the same stale line.
- **So every row below describes a file that is not the one at 464d995.**
- Otherwise the content matches the source: headings, all 4 tables, the figure, the captions and the references.

## docx properties and page setup

- **Core properties (pass):**
  - title "Methods: detection of coordinated calcium events"
  - author and lastModifiedBy "Tony DeFazio"
  - created and modified 2026-09-22T03:27:30Z, which is this build, not a template date
  - custom property "subtitle" set correctly
  - app.xml has had the template statistics removed
  - word/comments.xml is empty
- **Page setup (pass):** US Letter 8.5 × 11 in, portrait, 1 in margins, one section.
- **PDF metadata:** empty title and author. This is minor, and only the companion is affected.
- **No page numbers** in the Word pages.

## Per-page table (Word pages, each row checked against the page image of the same number)

| pg | content | check |
|---|---|---|
| 1 | Title, subtitle, author, opening definitions, "Detected calcium events", Table 1 caption plus header and 4 rows | Caption stays with its table. **Row labels break mid-word: "orchidectomize / d males"**, because the 5 columns are equal width. |
| 2 | Table 1 "all" row (header repeats), exclusions list, periods and windows, "Synthetic recordings" intro | The Table 1 total row sits alone on the page. **Bottom ~33% of the page is blank**, because Figure 1 did not fit. |
| 3 | Figure 1 and caption; Background, Planted events, Distractors, Elevated-rate block | Figure box is 420 × 210 pt (5.83 × 2.92 in) = 69% of page width, 27% of page height, 90% of the text width. **Text inside the figure renders at about 4–5 pt** (body text is 11 pt), so the tick labels, row labels and inline key are not legible in print. Caption is bound to the figure. |
| 4 | Event widths, Origin of the constants, Table 2 caption plus table, start of the Test recordings list | Caption is bound. Intervals wrap at the en dash ("0.0050 (0.0028– / 0.0066)"). Text reaches x = 546 pt, 6 pt past the 540 pt right margin, still on the page. Caption shows "events s ⁻¹" with a gap before the superscript. |
| 5 | End of Test recordings, "Coded detectors", 5 detector bullets | OK |
| 6 | locust (end), SPIKE-synch (stale line), port note, "Scoring", start of Table 3 caption | **The Table 3 caption splits across pages 6 and 7.** keep_with_next is set, but keep-lines-together is not. |
| 7 | Rest of Table 3 caption, Table 3, "Optimization of coded detectors" | **Header and row labels break mid-word: "rate+conte / xt", "CoactDete / ct", "no- / coordinati / on test"**, because the 7 columns are equal width. |
| 8 | Optimization (end), Table 4 caption plus table, "Learned detectors" | Caption is bound. Column 1 takes half the width while column 2 is cramped, and a unit is split from its number ("context = 120 / s"). Minor. |
| 9 | cell-set network with gain, Training, Decoding, "Comparison…" | OK |
| 10 | Merge gap (end), Replication, Separability, "Analysis of recorded data" | OK |
| 11 | "Width and amplitude…", "References" (start) | OK |
| 12 | References (end) | Bottom ~20% blank at the end of the document, which is fine. |

## HTML companion

- I viewed page02 and checked the markup.
- **Structure:** 4 `<caption>`s and 1 `<figcaption>`. Headings are the title `h1` plus 10 `h1` sections; the hierarchy is flat, which matches the docx.
- **Figure:** it is about 7 in wide and its internal text is again very small.
- **Accessibility:** the figcaption carries `aria-hidden="true"` (pandoc's default when alt = caption). This is minor.
- **Overflow:** none seen in page02.

## Element walk (source → Word render)

| element | present | page |
|---|---|---|
| Title / subtitle / author | yes | 1 |
| 10 section headings (Heading 1) | yes | 1–11 |
| Table 1 (5 columns, 5 rows) | yes | 1–2 |
| Exclusions list (3 bullets), windows list (2 bullets) | yes | 2 |
| Figure 1 with caption | yes | 3 |
| Table 2 (4 columns, 8 rows) | yes | 4 |
| Tests list (3), detector list (6), scoring list (3) | yes | 4–6 |
| Table 3 (7 columns, 3 rows) | yes | 6–7 |
| Numbered search stages (2) | yes | 7 |
| Table 4 (2 columns, 6 rows) | yes | 8 |
| Architectures (4), selection rules (2), width steps (3) | yes | 8–11 |
| References (16 entries) | yes | 11–12 |

Nothing is dropped.

**Numbering and consistency:**
- Tables 1–4 are numbered in order and each is cited in text before or at its position. Figure 1 is cited on page 2 and placed on page 3.
- Units in tables are present: s⁻¹, min⁻¹, h⁻¹, s, frames.

**Figure 1 against the glyph and label rules:**
- **Legend:** colour key rendered in its own colours; ▼ used for planted events, ▽ for distractors; the shaded span is keyed.
- **Axes:** the y label is "cells · 33". The x label is "time" with no unit, though the ticks carry units ("0s", "10m").

## Findings (location · issue · severity · suggested fix · verified?)

1. **Whole build (docx, pdf, html, PNGs).** The build is one source edit behind 464d995: it shows "23 April 2026" where the source says "April 2026". **Blocking.** Rebuild all three steps (docx+html, --docx-pages, --png) from 464d995 or later and re-check. Verified: yes (mtimes, plus a text diff of docx and html against `git show HEAD:`).
2. **Figure 1, Word page 3.** Text inside the figure renders at about 4–5 pt: 2024 px scaled into 420 pt is 0.21 pt/px, and the tick and label text is about 20 px tall. It is not legible in print. **Blocking.** Regenerate the figure with fonts sized for about 6.5 in of print (≥ 8 pt once placed), for example a narrower pixel canvas with the same font px, and place it at the full 6.5 in text width. Verified: yes (measured PDF image bbox and source PNG).
3. **Table 3 (page 7) and Table 1 (page 1).** Equal-width columns break words in the middle ("rate+conte/xt", "CoactDete/ct", "coordinati/on", "orchidectomize/d"). The cause is the equal-dash pipe-table separators at .md lines 32 and 215. **Major.** Give pipe-table dash counts proportional to the width wanted (wider first column), or shorten the row labels (for example "elevated-rate, calls min⁻¹"), or use a smaller table font. Verified: yes.
4. **Table 3 caption, pages 6–7.** The caption paragraph splits across the page break. **Major (cosmetic).** In `_fix_docx`, also set `paragraph_format.keep_together = True` on Table Caption. Verified: yes.
5. **Figure 1 caption.** Panels are described as "Top:" and "Bottom:" rather than lettered A/B. **Minor.** Letter the lane (A) and the raster (B) in the figure and in the caption. Verified: yes.
6. **Figure 1 x-axis.** The label "time" has no unit. The ticks carry units, so the house tick convention is met, but the name-and-units rule is not. **Minor.** Label it "time (min:s)" or state the unit in the caption. Verified: yes.
7. **Page 2.** The bottom third of the page is blank because the figure moved to page 3, and the Table 1 "all" row is stranded alone at the top. **Minor.** Accept, or shrink the figure's height or keep Table 1's rows together (cantSplit / keep-with-next on the rows). Verified: yes.
8. **Table 2 (page 4).** Intervals wrap at the en dash, and one cell reaches 6 pt past the right margin. **Minor.** Widen the last column (the dash-count fix in finding 3). Verified: yes (PDF text bbox x = 546 pt).
9. **Table 2 caption.** "events s ⁻¹" renders with a space before the superscript. **Minor.** Use pandoc superscript `s^−1^` as in the body text. Verified: yes (visual).
10. **Word pages.** No page numbers on a 12-page review draft. **Minor.** Add a footer page-number field via reference.docx. Verified: yes.
11. **PDF metadata.** Title and author are empty. **Minor** (companion only). Word takes these from the docx core properties, so this probably needs an explicit SaveAs2 or DocumentProperties setting. Verified: yes.
12. **HTML figure.** `figcaption aria-hidden="true"`. **Minor.** Give the image an alt text distinct from its caption. Verified: yes.

## Files

All build outputs (the .docx and its PDF, the .html, and every page PNG) are in `<scratchpad>\methods_build_r1\`.

- Builder: `<scratchpad>\build_methods.py`
- Source: `docs\methods\coordination_pipeline_methods.md`
- Figure: `docs\methods\figures\fig1_benchmark_recording.png`

---
*Transcription note: personal absolute paths were replaced with placeholders (sapper SAP004), and the quoted citation string for a personal communication was paraphrased (tools/check_quotes.py); nothing else was altered.*
