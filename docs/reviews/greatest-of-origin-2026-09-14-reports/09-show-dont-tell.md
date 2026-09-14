GRANT 9 ok — Read, Grep, Glob, Bash

**Thresholds used.** These are conventions, not researched optima. The slide rules (40 words per slide, figure at least 50% of the canvas) don't fit a markdown doc, which has no fixed canvas. I used these instead:
- a single text block (a paragraph, bullet or table cell) over **60 words** gets flagged;
- a run of more than **150 words** with no table or figure gets flagged;
- a block showing results or methods with no figure gets flagged.

Figure share is N/A for every block because none of them carries a figure. Word counts were taken with `wc -w` on the added lines of the diff.

## Count table

| # | Changed block | Words (added) | Largest single block | Figure? | Figure share |
|---|---|---|---|---|---|
| 1 | README.md, citation bullet for LoCo/CoactDetect | 84 (the old one was 56) | 84, one bullet | n | N/A |
| 2 | GLOSSARY.md, CFAR vocabulary paragraph (the parenthetical) | 28 | 28 | n | N/A |
| 3 | detector_history.md, flag inside the 2026-08-24 revision note | 35 | 35 | n | N/A |
| 4 | detector_history.md §4, table row for `maxlt` | 46 | 46, one cell (other cells in the table are 20 words or fewer) | n | N/A |
| 5 | detector_history.md §4, "Where greatest-of began…" to "…*not established*." | **347** | **75**, the opening paragraph. Bullets: 49 (1980 paper) · 58 (memo) · 47 (Gandhi & Kassam) · 22 (Rohling); "what we do not know" list 73, longest item 38; closing sentence 15 | n | N/A |

What gets flagged: block 1 (84 words, over 60); block 5's opening paragraph (75, over 60); block 5 as a whole (347 words, no table or figure, over 150). No block shows results or methods, so the "no figure" rule doesn't fire anywhere.

## Judgment: bullets, table or timeline?

**It should not be a figure.** The claim is about order and about which sources we hold. It is not about how far apart the dates are. That leaves eight uneven dates, most packed into 1971–1973 and 1980–1988, and a drawn timeline would spend its space on empty years. It would also need a figure number, alt text and a build step, all to show what one markdown table already shows. None of this is visual, so the CLAUDE.md "render it" rule doesn't apply.

**The chronology should be a small table. The quotations should stay as prose.** The passage's whole argument is a comparison of dates: a memo from February 1972 comes before the 1973 conference. But the dates are scattered across four sections in this order: 1973 (opening), 1980, 1972, 1988, 1983, then 1971 and 1972 again in the "do not know" list. The reader has to put the sequence back together. A table would help in three ways:
- It puts the sequence in reading order.
- A "held?" column shows what we know and what we don't in one column. That is the split Tony asked for.
- §4's attribution table just above already has a "held?" column, so the format matches.

The three quoted sentences (from the 1980 paper, Gandhi & Kassam, and the memo title) are the evidence. They carry inference and belong in prose: move them, don't cut them. My estimate is about 200 words for the table plus two short quote lines, down from 347. That also serves the brevity brief.

Building the table also shows a gap. The passage never states a held status or a full citation for **Moore & Lawrence 1980**, so that row's cell can't be filled from the text. It appears once, at line 506.

## Findings

| Location | Issue | Severity | Suggested fix | Verifiable against a source |
|---|---|---|---|---|
| detector_history.md §4, lines 484–518 (block 5) | A 347-word prose run. The dates are spread over the opening paragraph, four bullets and the "do not know" list, out of order, so the reader must rebuild the sequence the argument depends on. | major | **Replace the date content with a chronology table**: *date · work · held? · bearing on greatest-of*. Rows: 1971 Hansen & Zottl (not held; bearing unknown) · 1972 Hansen & Ward (not held; unknown) · 15 Feb 1972 Sawyers memo, Hughes, unpublished (not seen; the 1980 paper derives greatest-of performance from it) · Oct 1973 Hansen, IEE Conf. Publ. 105, pp. 325–332 per Gandhi & Kassam (no copy found; usually credited) · 1980 Hansen & Sawyers (read; cites 1972 and 1973) · 1980 Moore & Lawrence (held status?; Rohling credits it) · 1983 Rohling (read; does not cite 1973) · 1988 Gandhi & Kassam (read; "Hansen [9] has proposed…"). Keep the 1980 and 1988 quotations as one line each under the table. The first three items of the "do not know" list become one sentence; the fourth is covered by the 1971 and 1972 rows. Keep the search dates and the IEEE Xplore note: that is provenance, and it stays in the doc. | yes, against the passage and the §4 table; the 1971, 1972 and 1973 works are not on the shelf |
| Same, opening paragraph (lines 484–490) | 75 words, over the 60-word block threshold. It mixes the attribution, the venue details and the search record. | minor | Keep only the assertion and the conference citation in the paragraph. The search record (2026-09-10 to 2026-09-14, the contents listing, IEEE Xplore) becomes a trailing sentence or a line under the table. It moves; it is not deleted. | yes (diff) |
| Same, line 506 (Moore & Lawrence 1980) | The only mention: no held status and no full citation. A table can't be filled in without it, which is how this showed up. | minor | Add the citation and a held/not-held status, or say plainly that it wasn't looked for. | yes, check the darkroom shelf at `lit/radar/` |
| Same, lines 516–517, closing sentence | 15 words restating what the table cell already says. With a chronology table directly below the attribution table, the link back is obvious. | minor | Drop it once the table is in place. If the prose stays, keep it. | yes |
| detector_history.md §4 table, `maxlt` row (line 466) | The attribution cell holds a 46-word sentence; other cells are 20 words or fewer. The table goes ragged and the cell repeats the passage below. | minor | Keep it a table and shorten the cell: `**not established** (see below) · loss: Hansen & Sawyers, *IEEE T-AES* **AES-16**(1), 1980, 115–118`. Held cell: `1980 read · 1973 not found`. | yes |
| README.md lines 651–661 (block 1) | 84 words, up from 56. Saying "not established" made the citation bullet 50% longer, and it now carries the 1973 title and the memo detail that §4 already holds. That runs against the brevity brief. | minor | Prose is right for a citation bullet, but move the detail: keep the Hansen & Sawyers 1980 citation, the words "where greatest-of began is not established", and the §4 link. Delete from the README only the 1973 title and the memo sentence, which §4 already contains. About 45 words. | yes (diff, §4) |
| GLOSSARY.md lines 262–265 (block 2) | The 28-word parenthetical breaks a parallel three-item list: CA-CFAR (Finn & Johnson 1968) · GO-CFAR (…) · OS-CFAR (Rohling 1983). The reader loses the list's thread. | minor | Prose is right, but keep the parallel form: `GO-CFAR (origin not established — detector_history.md §4)`. | yes |
| detector_history.md, revision note at lines 204–206 (block 3) | A 35-word flag dropped into the middle of a sentence, between "GO-CFAR (Hansen 1973" and "and its percentile-of-pool". The sentence's grammar is suspended across three lines. | minor | Prose is right for a dated ⚠ flag. Close the parenthetical after "Hansen 1973" and put the flag in its own `> ⚠ 2026-09-14: …` line at the end of the blockquote paragraph. | yes |
| All five blocks: is a figure needed? | Checked; none needed. The new text is about attribution, not data or mechanism. The greatest-of mechanism is already drawn in Panel B of `learned/cfar_map.png` (line 244). | none | No figure. A markdown chronology table (first row) is the only format change I recommend. | yes |

No findings were outside this role's scope. I checked the added lines in all three files, the §4 table and the text around the passage (detector_history.md lines 440–540), and searched the doc for figures (one, at line 244) and for Moore, Zottl, Ward and Hughes.

Files: `<worktree>\docs\detector_history.md`, `<worktree>\docs\GLOSSARY.md`, `<worktree>\README.md`, diff at `<scratchpad>\go_diff.patch`
