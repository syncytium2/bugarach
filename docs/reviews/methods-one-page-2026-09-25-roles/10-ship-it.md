GRANT 10 ok — Read, Grep, Glob, Bash

I ran the build and craft checks on <repo>/docs/methods/one_page/methods_one_page.pdf (git hash-object e273fd40…, matches the one you named). The PI's requirement is met: the methods text ends on page 1, the references are alone on page 2, and the PDF is current. Nothing blocks. There are two major findings. The HTML is malformed, so the source asks for layout the render does not have, and page 1 has less than one line of room left.

Renders are in <scratch>/mb/:
- `p1.png` and `p2.png`: the shipped PDF rasterised at 150 dpi with PyMuPDF, which I installed into scratch/pylib. I looked at both with Read.
- `rebuild.pdf`: rebuilt with the stated Chromium command from the current HTML.
- `fixed.html`, `fixed.pdf` and `fixed_p1.png`: the same build with the markup corrected in scratch only. This tests what the intended CSS would do.
- `dom.html`: Chromium's parsed DOM.

I edited nothing in the repo.

## Table

| Page | Render checked | Build current | Contents | Clipped / off page | Margins (measured text box) | Headings | Special characters | Type sizes | Justification / hyphenation | Result |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | p1.png (shipped PDF); per-page text via PyMuPDF; rebuild.pdf compared | Yes. PDF modified 20:25:44 UTC (16:25 EDT), HTML 20:03:06 UTC. The rebuild from the current HTML gives identical text on every page. | Title, draft note, and all 8 sections (Input to Output). The text ends on page 1: the last line is "…not of fluorescence." at y=737.8 pt. | Nothing clipped or overlapping. | Left 46.5 pt (0.65 in set). Right edge at most 565.4 pt against a 565.2 limit, a 0.2 pt glyph overhang that is not visible. Top 44.1 pt (0.6 in set). Bottom: the last line ends 11.0 pt above the bottom margin, less than one line (12.1 pt pitch). | h1 at 12 pt bold. The 8 run-in heads are bold 9.6 pt and render inline. In the DOM, however, they are block-level h2s between empty `<p>` elements (see F1). | All render in embedded Liberation Serif subsets, with no missing glyphs: α ×2, ± ×3, − ×6, × ×2, t₅₀ subscript, 10⁻¹⁶ and s⁻¹ superscripts, en dashes, ’ ×14. Superscripts do not disturb line spacing: the gap across the 6×10⁻¹⁶ line is 24.0 pt over two lines. | Body 9.6 pt (accepted for this draft only, not failed; house minimum is 11 pt). Draft note 8.4 pt gray. Sub/superscripts about 8.0 pt. | Ragged right with no hyphenation, although the CSS says `justify` and `hyphens: auto` (F1). No rivers, because the text is ragged. One number is split from its unit across a line break: "within a 2 / s window" (Participation floor, lines 3–4). | Pass, with findings F1–F3 |
| 2 | p2.png; per-page text | As above | "References" h1 plus 5 entries (Efron, Finn, Kingma, Yu, Zaheer), sorted alphabetically. No body text. Uses the top 185 pt of the page. | None | Same margins. Hanging indent 1.4 em renders. | h1 at 12 pt | "Póczos" ó renders; en dashes in page ranges render. | 9.6 pt | Left-aligned as the CSS intends. | Pass |
| Document properties | PyMuPDF metadata | Created and modified are both D:20260925202544Z, so they belong to this file and not a template. | Title "Methods: coordinated calcium events", which differs from the on-page h1 "Methods: detection of coordinated calcium events". Author is empty. Creator is Chrome's user-agent string; Producer is Skia/PDF m141. | – | – | – | – | – | – | Minor findings F4, F5 |

## Findings

**F1**
- **Location:** HTML lines 25–39, the `<p><h2>…</h2> text</p>` pattern in all 8 sections.
- **Issue:** An `<h2>` is not allowed inside a `<p>`, so the parser closes the `<p>`. The DOM ends up as an empty `<p></p>`, a block-level `<h2>`, loose body text, and another empty `<p></p>` (`dom.html` has 8 such pairs). As a result, none of the `p` rules reach the body text:
  - `text-align: justify` and `hyphens: auto` do nothing.
  - The spacing between paragraphs comes only from the stray empty `<p>` margins.

  The source reads as justified and hyphenated; the render is neither. With the markup corrected (`fixed.pdf`), the line breaks and page fit are unchanged. Justification then turns on and leaves visibly loose lines, for example "and 0.0292 Hz); rates vary across ROIs and over time by Gamma-distributed factors…" and "Simulated recordings. Each simulated recording has 32 ROIs…". It adds no hyphenation, because headless Chromium on Linux has no hyphenation dictionary.
- **Severity:** Major.
- **Suggested fix:** Replace `<h2>` with an inline run-in element such as `<b class="runin">`. Also remove `text-align: justify` and `hyphens: auto`, so the source says "ragged right", which is what ships and looks cleaner.
- **Verified:** Yes (`dom.html`, `fixed.pdf`, `fixed_p1.png`).

**F2**
- **Location:** Page 1, bottom.
- **Issue:** There is 11.0 pt of room left against a 12.1 pt line. Any edit that adds one line to any section will push the end of Output onto page 2. Because `.refs` has `break-before: page`, the result would be 3 pages with the references on page 3, and the one-page requirement would fail silently. The planned move to 11 pt will certainly overflow.
- **Severity:** Major (for the 11 pt revision). Minor for this draft.
- **Suggested fix:** After every edit, have the build check that page 1 ends in "fluorescence." and that there are exactly 2 pages. Plan to cut text for the 11 pt version.
- **Verified:** Yes (measured).

**F3**
- **Location:** Page 1, Participation floor, lines 3–4.
- **Issue:** "within a 2" / "s window": the number is split from its unit across a line break.
- **Severity:** Minor.
- **Suggested fix:** Use `2&nbsp;s`. Ideally put a non-breaking space between every number and its unit (s, Hz, min).
- **Verified:** Yes (text extraction and p1.png).

**F4**
- **Location:** PDF metadata, Author.
- **Issue:** The Author field is empty, and Creator is the Chromium user-agent string. Chrome's print-to-pdf does not set Author from the HTML.
- **Severity:** Minor.
- **Suggested fix:** Stamp Author (and Subject if wanted) on the built PDF in a post-step, e.g. PyMuPDF `set_metadata`. The build command has no option for it.
- **Verified:** Yes.

**F5**
- **Location:** PDF metadata Title, set from the HTML `<title>` (line 5).
- **Issue:** The Title "Methods: coordinated calcium events" does not match the on-page h1 "Methods: detection of coordinated calcium events".
- **Severity:** Minor.
- **Suggested fix:** Make `<title>` match the h1.
- **Verified:** Yes.

**F6**
- **Location:** Build environment (for the record).
- **Issue:** "Times New Roman" is not installed in this container, so the build falls back to Liberation Serif, which has the same metrics. A build on a machine with real Times should wrap the same, but that is not guaranteed with the margin in F2.
- **Severity:** Minor.
- **Suggested fix:** Note the font actually used in the run record, or re-check the page count on the machine that produces the final build.
- **Verified:** Partly: font confirmed from the PDF's embedded fonts, cross-machine wrapping not tested.

**Checked with nothing found:** nothing clipped or off the page; nothing overlapping; the special characters listed; sub/superscript line spacing; the reference hanging indents; the references alone on page 2; created/modified dates belong to this file. The figure, axis, legend and colour checks do not apply, because the document has no figures (it contains no images).
