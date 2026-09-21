GRANT 9 ok — Read, Grep, Glob, Bash

Blind pass. I opened nothing under `docs/reviews/`, `docs/todo/` or `docs/lit_needed.md`. I edited no files. The only things I wrote are four screenshots in `...\scratchpad\r3_sdt\`.

## Thresholds used

These are conventions, not researched limits. The artifact is a set of reference-document edits, not slides, so I did not apply the per-slide rules (40 words per slide, figure under half the canvas). I used these instead:
- Any single text block over **60 words** is flagged.
- A section that compares **three or more sources on the same attributes**, or runs through **four or more dated events** in prose, is flagged as a table or timeline candidate.
- If a changed string sits inside a rendered figure, I measured it in the render, not the source.

## Count

| changed block | words | largest single block | figure | figure share |
|---|---|---|---|---|
| `detector_history.md` §4, table row for LoCo `maxlt` | 35 (one cell) | 35 | n (the table already is the visual) | — |
| `detector_history.md` §4, paragraph after the table | 71 | 71 **(over 60)** | n | — |
| `detector_history.md` §4.1, whole section | **647** | 115 **(over 60)** | n | — |
| · opening paragraph | 112 | 112 **(over 60)** | n | — |
| · search paragraph | 100 | 100 **(over 60)** | n | — |
| · 4 source bullets (Hansen & Sawyers, patent, Rohling, Gandhi & Kassam) | 115 / 78 / 73 / 92 = 358 | 115 **(all 4 over 60)** | n | — |
| · 3 unknowns bullets | 13 / 14 / 37 = 64 | 37 | n | — |
| `detector_history.md` 2026-08-24 note, ⚠ sentence | 25 added (the enclosing paragraph is already 241) | 25 | n | — |
| `detector_history.md` §7 item 2, ⚠ sentence | 37 | 37 | n | — |
| `detector_history.md` Sources entry | 49 | 49 | n | — |
| `docs/GLOSSARY.md` CFAR paragraph | 135 | 135 **(over 60)** | n | — |
| `README.md` citation for `maxlt` | 85 (the whole bullet is 192) | 85 **(over 60)** | n | — |
| `cfar_scope.html` lede | 33 | 33 | page y; the lede is not in a figure | — |
| `cfar_scope.html` map-table row | 13 | 13 | n (table) | — |
| `cfar_scope.html` GO-CFAR mini-panel caption | 5 | 5 | **y** (small-multiple card) | canvas 104 px of a 194 px card = **54%**; 58% before the change (179 px card) |
| proposal footer correction | 23 | 23 | n | — |

I rendered `cfar_scope.html` with Playwright Chromium at 1440, 1024 and 390 px wide. The screenshots are `minis_1440.png` and `map_1440.png` (plus the 1024 and 390 versions) in `<scratchpad>\r3_sdt\`.

## Judgment: should any of this be a figure?

**No rendered figure is warranted.** Nothing here is measured data. The content is claims about who wrote what, and each claim has to stay searchable and checkable against its quotation. A picture of text would break that, and the project's "render it" rule is about visual findings. **Two parts of §4.1 are tables written as prose, though**, and turning them into tables is also the most direct way to meet Tony's brevity brief.

## Findings

| # | location | issue | severity | suggested fix | verifiable against a source |
|---|---|---|---|---|---|
| 1 | `detector_history.md` §4.1, the four source bullets (358 words, each over 60) | Four sources are compared on the same attributes: does it cite the 1973 paper, what does it say that paper did, who does it credit with greatest-of, which pages does it give. The conflicts are what the section is meant to show, and each sits in a different bullet: pages 325–332 vs 1–8, "proposed" by Moore & Lawrence vs by Hansen, both-sides averaging vs greatest-of, IEE vs IEEE venue. A reader has to build the comparison in their head. | **major** | **Replace the bullets with a source × claim table.** Columns: *source (year) · cites 1973 paper? · says the 1973 paper… · credits greatest-of to · pages / venue given*. Rows in the order already used (Hansen & Sawyers 1980; US 4,318,101; Rohling 1983; Gandhi & Kassam 1988), so the disagreements line up in columns. **Keep every quotation** (they are the evidence and are checked against PDFs). Move them into a `<details>` "quotations" block directly under the table, not into cells. A timeline is the wrong replacement: it would show the order of events but not the disagreements, which are what matter. | yes (the bullets' own quotations) |
| 2 | §4.1 search paragraph (100 words) | This is a list of places searched and what each gave, written as a sentence chain. A reader cannot see at a glance which leads are still open: the HathiTrust scan not searched, no library request. | minor | **Two-column table: *where searched · result*.** Rows: the *Proc. IEE* 120(11) notice (confirms author and title; ISBN 0 85296 114 6), the HathiTrust record 001618382 (ISBN 0 85296 112 X; search-only scan, not searched), IEEE Xplore and the IET Digital Library (not queryable with the tools), OpenAlex and Semantic Scholar (catalogue records only), library request (none recorded). The two open leads then stand out as rows. | yes |
| 3 | §4.1 opening paragraph (112 words) | The core statement is three sentences: not established; used to be credited to Hansen 1973; not read here, and the sources credit others. The full bibliographic record is woven through the middle of it: the name as printed, IEE vs IEEE, publication number, London, 23–25 October 1973. | minor | Move the record into **one reference line** under the heading (a formatted citation). Keep the statement and "nothing above depends on it" as the paragraph. The IEE-vs-IEEE point also appears in finding 1's Gandhi & Kassam row, where the conflict actually shows. Nothing is deleted. | yes |
| 4 | `detector_history.md` §4, paragraph after the table (71 words) | It lists the four papers held and read, but the table's last column already says **read in full** on those rows. The 2026-08-22 supply detail repeats the Sources entry, which now says the orders were "delivered the same day". | minor | **The table is already the visual; point at its status column** instead of naming the papers again. Leave the 2026-08-22 supply detail to the Sources entry. Keep the sentences on the 1973 paper and on quote checking. | yes |
| 5 | `README.md` citation bullet for `maxlt` (85 words; whole bullet 192) | A citation list is for scanning. The added text explains the mechanism and narrates the edit ("this README no longer cites a 1973 Hansen conference paper as its origin"). That is change history, and the brief asks to state what is known and stop. | minor | Cut it to the mechanism clause, the Hansen & Sawyers 1980 citation with DOI, and "origin not established (§4.1)". Move the "no longer cites" history into §4.1's opening paragraph (already there) and the commit message. Nothing is lost. | yes |
| 6 | `GLOSSARY.md` CFAR paragraph (135 words) | The paragraph lists the detector-to-CFAR mapping in prose, which duplicates the §4 table and the `cfar_scope.html` map table. The change adds a 22-word pointer to the end. Most of the length was already there. | minor | Replace the inline list (`rate_detect` is…, `maxlt` uses…, percentile is kin to…) with one link to the §4 table. Keep the priority ruling and the pointer to §4.1. | yes |
| 7 | `cfar_scope.html` GO-CFAR mini-panel caption, `cite:"loss analysis: Hansen & Sawyers 1980"` | **Measured in the render:** at 1440 and 1024 px this caption wraps to 3 lines (50 px, against 35 px for the other four cards). Because the cards share a grid row, **all five cards grow from 179 to 194 px**, leaving an empty 15 px strip under the other four captions. That pushes the plot's share of each card down from 58% to 54%. At 390 px (one column) it does not wrap. | minor | Use `"loss: Hansen & Sawyers 1980"`, the wording the map-table row already uses (27 characters). The 29-character TM-CFAR caption fits on one line in the same render, so this will too. Keep the longer wording in the chip's `title` tooltip. Re-render to confirm. | yes (render; `minis_1440.png`) |
| 8 | `cfar_scope.html` map-table row, and the `detector_history.md` §4 table row | Checked, **no finding.** In the render the `maxlt` row fits on one line at 1440 px and is no taller than its neighbours at 1024 (53 px) or 390 px (125 px, same as `rate+context`). The table form is right. | — | none | yes (render; `map_1440.png`) |
| 9 | The two ⚠ sentences (2026-08-24 note, 25 words; §7 item 2, 37 words), the Sources entry (49), the proposal correction (23), the `cfar_scope` lede (33) | Checked, **prose is right.** Each is a correction placed at the stale claim it corrects, and a table or figure cannot sit inside a sentence that is being corrected. All are under 60 words. The 241-word note paragraph was already that long. | — | none | yes |
| 10 | §4.1 unknowns list (64 words) | Checked, **prose is right.** Three short items already in list form. A table would just add column headers. | — | none | n/a |

## Net effect

Findings 1–3 together would turn the 647-word §4.1 into an opening statement, a reference line, a search table, a source table and the three unknowns. The quotations would be kept in a collapsed block. That matches the brief's three parts: the attempt, what is known, what is not. I have not measured the resulting length, because producing that text is not this role's job.
