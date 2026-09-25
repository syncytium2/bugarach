GRANT 10 ok — Read, Grep, Glob, Bash

I ran role 10 (Ship It) blind on docs/methods/one_page/methods_one_page.pdf. I did not open docs/reviews/methods_one_page_2026-09-25* or git history, and I edited nothing in the repo.

**Verdict: the PDF can ship.** It is current, has two pages, and all the methods text is on page 1 with 18.1 pt to spare. Nothing is clipped or overlapping, every special character renders, and no number is split from its unit. The metadata name this file. The build tool refuses a spill that crosses the page and writes no output when it does. There are no blocking findings. The only substantive one is that the tool's docstring gives the old margin ("under 2 pt"), which is now wrong.

**How I checked**
- **Renders:** I rendered each shipped page with PyMuPDF at 150 dpi (scratch mb3/p1.png and p2.png) and looked at both. I made 5× zoom crops of the three lines that carry a subscript or superscript (mb3/zoom_t50.png, zoom_alpha.png, zoom_sinv.png).
- **Line breaks:** I dumped the start and end of every line on both pages from `get_text("dict")`.
- **Rebuild:** I rebuilt with the tool into mb3/rebuild/. It returned 0 and was **pixel-identical** to the shipped PDF on both pages (compared at 100 dpi), and the words and their positions matched too.

| Page | Render checked | Build current | Page split | Headroom | Clipping / overlap | Special chars | Number–unit splits | HTML validity | Headings | Metadata |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | mb3/p1.png plus three 5× zooms; rebuild mb3/rebuild/ | PASS: PDF modified 20:49:53Z, HTML 20:49:52Z; the rebuild is pixel-identical | PASS: all 9 run-in sections (Input to Output) on page 1, 59 lines, no reference text | **18.1 pt ≈ 1.57 lines** at 11.52 pt line pitch. Found by binary search with a spacer on the body-only render: fits at 18.05, spills at 18.28. Last line's glyph bottom is at 734.8 pt; the content limit is 756 pt. **Type is 9.6 pt: recorded as accepted for this draft only, not failed.** | PASS: text runs x 39.75–572.66 of 612 pt (margins 39.6 pt). Zooms show t₅₀, 6×10⁻¹⁶ and s⁻¹ do not touch adjacent lines (`sub, sup {line-height:0}` holds the pitch) | PASS: − ×5, ± ×2, × ×3, ≈ ×1, α ×2, – ×9 extracted, no U+FFFD. Fonts: LiberationSerif Regular, Bold and Italic; sub/sup at 7.99 pt | PASS: 41 non-breaking spaces keep values with units ("2 s", "45 min", "0.1 s", "[−20 s, 20 s)", "z ≈ 8"). Two cosmetic splits: "Zaheer / et al., 2017" and "Kingma & Ba, / 2015" | PASS: tags balance (html.parser: nothing unclosed or mismatched), `<meta charset="utf-8">`, all entities valid | h1 heading. The section labels are bold run-in spans, not headings, so the PDF has no outline (get_toc empty) | Title = h1 exactly ("Methods: detection of coordinated calcium events"); author "Tony DeFazio" (stamped); created = modified = D:20260925204952Z (16:49 EDT, this build, not a template date); creator HeadlessChrome 141 / Skia m141; subject and keywords empty |
| 2 | mb3/p2.png | PASS (same rebuild) | PASS: "References" plus 9 entries only, text at y 36.6–278.8 pt, rest of the page blank | n/a | PASS: hanging indent renders, nothing clipped | PASS: ó (Póczos) and ü (Grün) render; – in page ranges. **ć does not appear in the source**, so there was nothing to render | One cosmetic split: page range "70(10– / 12):2064–2068" (Pipa) | PASS | h2 "References", styled inline (12 pt) to match the h1 | same file |

**Build-tool tests** (all on scratch copies under mb3/, each run with `--source` and `--out` into scratch)

| Case | Methods lines on page 1 | Tool result | Correct? |
|---|---|---|---|
| Unmodified source | 59 | rc 0, 2 pages, author stamped | yes |
| spill1: +1 line appended to the Output paragraph | 60 (last line bottom at 746.1 pt) | rc 0, wrote the PDF | yes: it genuinely fits (raw Chromium print: 2 pages, references on page 2) |
| spillp: +1 new one-line paragraph | 60 (748.3 pt) | rc 0 | yes: it fits |
| spill2: +2 lines appended | spills | **rc 1**, `REFUSED: 3 pages, not 2; the methods text does not fit on page 1. Cut text; do not shrink the type.` Nothing written to out_spill2/ | yes: the raw print really is 3 pages, with methods text on page 2 |

So the tool does refuse a real spill, and it does not raise a false alarm on an addition that fits. Its page counter (a regex on `/Type /Page`) agreed with PyMuPDF on every file.

**Findings**

| # | Location | Issue | Severity | Suggested fix | Verified against a source |
|---|---|---|---|---|---|
| 1 | tools/build_methods_one_page.py, docstring | It says the page "was built with under 2 pt to spare, and a single added line silently moved the references to page 3". For this source neither holds: headroom is 18.1 pt, and one added line (spill1, spillp) still fits. Only +2 lines spill. | minor (a stale claim inside the artifact's own tool) | Replace the number with the current fact ("~18 pt, about 1.5 lines, as of 2026-09-25"), or drop it and let the check speak | yes: spacer binary search plus the spill1, spillp and spill2 runs |
| 2 | methods_one_page.html, p. 1, "Simulated recordings" | Spacing is inconsistent: `fast&nbsp;7` but `slow 17`, `combined 19` use normal spaces. This does not break the current render. | cosmetic | Use one convention (a normal space after the stream name is fine; these are not units) | yes: HTML source and render |
| 3 | PDF p. 1, Chorus paragraph | Author split from "et al." across the break ("Zaheer / et al., 2017") and names split from year ("Kingma & Ba, / 2015") | cosmetic | Optional: `Zaheer&nbsp;et&nbsp;al.` and `Ba,&nbsp;2015` | yes: line dump and p1.png |
| 4 | PDF p. 2, Pipa reference | Page range split at the en dash: "70(10– / 12):2064–2068" | cosmetic | Optional: `<span style="white-space:nowrap">70(10&ndash;12)</span>` | yes: p2.png |
| 5 | PDF, whole file | No outline or bookmarks, and the section labels are bold spans rather than headings. That is acceptable for a one-page methods sheet. Subject and keywords are empty. | cosmetic / informational | None required. If a navigable PDF is ever wanted, make the run-ins h2 or h3 styled to run in | yes: get_toc() is empty, metadata dump |
| 6 | tools/build_methods_one_page.py, `check()` | Each build leaves its `tempfile.mkdtemp()` directories behind. The references are removed with a non-greedy `<div class="refs">.*?</div>`, which is correct only while that div contains no nested `<div>` (true today). | minor (robustness; no effect on the current render) | Use `tempfile.TemporaryDirectory()`; add a comment or assertion that the refs block has no nested div | yes: source read |
| 7 | Cross-machine layout | The CSS asks for Times New Roman first, and this machine has only Liberation Serif, which is what got embedded. Liberation Serif is designed to match Times New Roman's metrics, so a Mac build should break lines the same way, but I did not verify that. The tool's refusal would catch a spill on any machine anyway. | informational | None; the build gate covers it | no: only one machine available |
| 8 | Requirement note | The 9.6 pt body type is recorded as accepted for this draft only, as instructed, and not failed. | record | none | yes: all body spans measure 9.6 pt |

Scratch evidence is under <scratch>/mb3/: p1.png, p2.png, the zoom_*.png crops, rebuild/, spill1.html, spill2.html, spillp.html and the out_spill*/ folders.
