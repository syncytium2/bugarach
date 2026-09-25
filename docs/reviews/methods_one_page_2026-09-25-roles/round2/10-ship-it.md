GRANT 10 ok — Read, Grep, Glob, Bash

# Role 10: Ship It (blind verify pass), docs/methods/one_page/methods_one_page.pdf

The shipped PDF is older than the HTML it is built from (PDF 20:37:57 UTC, HTML 20:38:47 UTC, 50 s later). Under the process rule that fails the build check. A fresh rebuild is pixel-identical on both pages, so the only thing a rebuild changes is the PDF's dates. Every row below therefore describes the file that would ship after a rebuild too.

On the merits, the page split meets the requirement: all the methods text is on page 1 and only the references are on page 2. But page 1 has 1.7 pt of spare room, and a test showed that one more line of text pushes it to three pages. Nothing in the repo checks for that.

**Renders checked** (scratch folder `<scratch>/mb2/`):
- `ship_p1.png` and `ship_p2.png`: the shipped PDF at 150 dpi.
- `fresh.pdf` with `fresh_p1.png` and `fresh_p2.png`: a rebuild using the stated Chrome command. Pixel-identical to the shipped renders.
- `zoom_sup16.png`, `zoom_sub50.png`, `zoom_bottom.png`: 200–400 dpi crops.
- `spill.pdf`: a copy with one extra line of text, used for the spill test.

## Table

| Page / check | Render checked against | Result |
|---|---|---|
| **Build current** (both pages) | File times; rebuilt `fresh.pdf` vs shipped PDF | **FAIL on timestamps.** The HTML is 50 s newer than the PDF. The rebuild is pixel-identical on pages 1 and 2 and has the same byte size (66,376 bytes); the files differ only in the creation/modification dates. The content is effectively current, but the build rule is not met. |
| **Page count and split** | `ship_p1.png`, `ship_p2.png`, text per page | PASS. 2 pages, US Letter (612×792 pt). Page 1: the h1 plus Input, Event floor, Parameters for simulation, Simulated recordings, Scoring, CoactDetect, Chorus, Benchmark and Output (59 lines). Page 2: "References" plus 8 entries (16 lines), ending at y=254.8 pt. No methods text is on page 2. |
| **Page 1 bottom headroom** | `zoom_bottom.png`; text bounding boxes | **Marginal.** The content box ends at 756.0 pt (792 minus the 36 pt margin). The last line's glyphs end at 754.3 pt, leaving **1.7 pt, about 0.15 of a line** (a line is 9.6 pt × 1.22 = 11.7 pt). Spill test: one extra line in Output gave **3 pages**, with methods text on page 2 and the references pushed to page 3. The font is Liberation Serif (what "Times New Roman" resolves to here; it has the same metrics as Times New Roman). |
| **Body size** | HTML CSS; render | 9.6 pt body, 12 pt h1. Recorded as accepted for this draft only, not failed. |
| **Nothing clipped or overlapping** (pages 1 and 2) | `ship_p1.png`, `ship_p2.png`, zoom crops | PASS. Text runs from x=39.8 to 572.9 pt; the content box is 39.6–572.4 pt. The 0.5 pt overshoot is glyph side-bearing, and nothing looks cut off. There are no overlaps. The raised and lowered characters (t₅₀, 10⁻¹⁶, s⁻¹) do not collide with the lines above or below. |
| **Special characters** | `zoom_sup16.png`, `zoom_sub50.png`, `zoom_bottom.png`; extracted text | PASS. Page 1 has the minus sign (−, not a hyphen), ±, ×, α, ≈, en dash and curly apostrophe. The superscript −16 in 6×10⁻¹⁶ and −1 in s⁻¹, and the subscript 50 in t₅₀, all render. Page 2 has ó (Póczos), ć (Nikolić) and en dashes in page ranges. There are no missing-glyph boxes. |
| **Number split from its unit at a line break** | Scan of every line end on both pages | PASS for number–unit pairs; the non-breaking spaces hold everywhere. Minor splits of a label from its number: "(fast / 7, slow 17" (Simulated recordings, lines 1–2), "combined / 0.25)" (Participation), "(ORX, / 19)" (Input), "Zaheer et / al." (Chorus). |
| **HTML problems that change the render** | Source read; rebuild | None found. The page break is `.refs { break-before: page }` and it works. Headings are h1 then h1, so "References" is a second h1; that is a structure point only and does not change the render. |
| **PDF metadata** | PyMuPDF metadata of the shipped PDF | Title "Methods: detection of coordinated calcium events" **matches the h1**: PASS. **Author is empty**, although the HTML has `<meta name="author" content="Tony DeFazio">`, because Chrome does not carry that tag into the PDF: FAIL. Created and modified dates are 2026-09-25 20:37:57 UTC; they are this build's own dates (no inherited template date), but they are older than the last HTML edit. Creator is the HeadlessChrome browser identification string and producer is Skia/PDF m141, which is cosmetic. |

## Findings

1. **`docs/methods/one_page/methods_one_page.pdf` (whole file): stale build.**
   - Issue: the PDF (20:37:57 UTC) is older than `methods_one_page.html` (20:38:47 UTC).
   - Severity: **blocking by the process rule.** The actual impact is nil: a rebuild is pixel-identical on both pages.
   - Fix: rebuild the PDF from the final HTML as the last step, and confirm the PDF's time is later than the HTML's.
   - Verified: yes (file times, rebuild, bytewise PNG comparison).

2. **`docs/methods/one_page/methods_one_page.pdf`, page 1 bottom: almost no headroom.**
   - Issue: 1.7 pt (about 0.15 of a line) is left. Adding one line, or any machine whose serif font has different metrics, moves methods text onto page 2 and the references onto page 3, which breaks the requirement.
   - Severity: **major.**
   - Fix: free at least one line of room (tighten a sentence, or reduce `p` margin-bottom from 3 pt to 2 pt), and pin the font to a specific face so the layout does not depend on what the machine substitutes.
   - Verified: yes (spill test `spill.pdf` gave 3 pages).

3. **No mechanical guard on the build or the split.**
   - Issue: `tests/test_methods_one_page_numbers.py` checks only numbers in the HTML. Nothing checks that the PDF is newer than the HTML, has exactly 2 pages, or keeps the references alone on page 2. The build is a hand-typed Chrome command with no script.
   - Severity: **major.** Finding 1 is the direct result of this gap, and finding 2 would go unnoticed the same way.
   - Fix: add a build script plus a test that checks the PDF is newer than the HTML, the page count is 2, page 1 has no "References", and page 2 starts with "References".
   - Verified: yes (the grep for `methods_one_page` finds only that test, and the test does not open the PDF).

4. **PDF metadata: author is empty.**
   - Issue: Chrome ignores `<meta name="author">`, so the PDF has no author.
   - Severity: **minor.**
   - Fix: stamp the author after the build (for example with PyMuPDF `set_metadata`, which can also set the creator to something readable), then re-check that the PDF is still newer than the HTML.
   - Verified: yes.

5. **Page 1: labels split from their numbers at line ends.**
   - Issue: "(fast / 7", "combined / 0.25)", "(ORX, / 19)" and "et / al." each break across a line.
   - Severity: **minor.**
   - Fix: use a non-breaking space in "fast&nbsp;7", "combined&nbsp;0.25", "ORX,&nbsp;19" and "et&nbsp;al." (this can shift the layout; re-check the headroom afterwards).
   - Verified: yes (line-end scan).

6. **HTML: "References" is a second h1.**
   - Issue: two h1 headings; the render is not affected.
   - Severity: **minor**, structure only.
   - Fix: use h2 styled the same.
   - Verified: yes.

**Recorded, not failed:** the 9.6 pt body size, accepted for this draft only.

**Checked and clean:** nothing clipped or overlapping on either page; all special characters, superscripts and subscripts render; no number is split from its unit; the PDF title matches the h1.

I did not open `docs/reviews/methods_one_page_2026-09-25*` or git history. I wrote only under the scratch `mb2/` folder and made no edits to the repo.
