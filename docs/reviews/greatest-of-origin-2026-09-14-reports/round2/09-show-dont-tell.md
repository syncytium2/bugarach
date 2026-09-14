GRANT 9 ok — Read, Grep, Glob, Bash

**Thresholds used.** These are project conventions, not researched optima, and I adapted them because this is long-form documentation, not a deck. I flagged:
- any single text block over **60 words**;
- structure typed out as prose: **3 or more dated sources compared**, or **sources that disagree with each other**;
- **2 or more prose-only blocks in a row** where a table or figure would carry the comparison.

I did not apply the 40-words-per-slide rule, because none of these files is a slide. Figure share is "n/a" for Markdown, which has no fixed page. I rendered `docs/learned/cfar_scope.html` in Playwright chromium at 1280 px because it has a fixed layout. Word counts are a scripted token count of the worktree files.

## Count

| # | Changed block | Words | Largest single block | Figure? | Figure share |
|---|---|---|---|---|---|
| 1 | `detector_history.md` §4 table row "LoCo, `maxlt`" | 44 | attribution cell, ~30 | n | n/a |
| 2 | §4 paragraph after the table ("The four papers…") | 93 | 93 | n | n/a |
| 3 | §4 "Where greatest-of began is not established" (whole passage) | **474** | opening paragraph, **139** | n | n/a |
| 3a | first bullet list, "What the sources we hold say" (4 bullets) | 259 | Hansen & Sawyers bullet, 95 | n | n/a |
| 3b | second bullet list, "What we do not know" (4 bullets) | 63 | 22 | n | n/a |
| 4 | 2026-08-24 revision-note flag (struck Hansen 1973 plus ⚠) | 35 (inside a 262-word note) | 262, pre-existing | n | n/a |
| 5 | §7 item 2 ⚠ line | 21 (inside a 235-word item) | 235, pre-existing | n | n/a |
| 6 | Sources entry | 58 | 58 | n | n/a |
| 7 | `GLOSSARY.md` CFAR paragraph | 152 | 152 | n | n/a |
| 8 | `README.md` citation bullet | 158 (84 added) | 158 | n | n/a |
| 9 | `cfar_scope.html` lede | 34 | 34 | n | page figure not touched by the diff |
| 10 | `cfar_scope.html` table row, plus the GO-CFAR caption under its small panel (same `cite` string, reused) | 20 (row), 11 (caption) | 20 | the caption sits under a small canvas panel | not changed; checked by render |

Render checks, both saved in the scratchpad (`<scratchpad>\`):
- **`cfar_map_section.png`:** the table row wraps to 2 lines (53 px tall), the same as its neighbours. No defect.
- **`cfar_minis.png`:** the GO-CFAR caption wraps to **3 lines (50 px)**, while the other four panels' captions take 2 lines (35 px).

## Findings

| Location | Issue | Severity | Suggested fix | Verifiable |
|---|---|---|---|---|
| `detector_history.md` §4, "What the sources we hold say" (4 bullets, 259 words) | This is a comparison table written as prose. Four sources are each described on the same few points: does it cite Hansen 1973, who does it credit, what does it say. The key unknown (Rohling credits Moore & Lawrence, Gandhi & Kassam credit Hansen) is a disagreement **between** bullets, so the reader has to rebuild the table in their head. Brevity is part of Tony's brief, and this is the largest block in the change. | major | **Replace the bullets with one 4-row table.** Columns: *source (year)* · *cites Hansen 1973?* · *credits greatest-of to* · *key words (verbatim)*. Rows: Hansen & Sawyers 1980 (yes, for a loss rule; own curves from Sawyers' 1972 Hughes memo) · US 4,318,101 (yes, pp. 1–8; also Weibull clutter; not on the shelf) · Rohling 1983 (no; Moore & Lawrence proposed it, Hansen et al. 1980 analysed it) · Gandhi & Kassam 1988 (yes, pp. 325–332, venue given as IEEE; Hansen proposed it). Keep every quotation, trimmed to its key clause in the cell. The Hansen & Sawyers acknowledgment line goes in a note under the table, not deleted. The "who proposed it" bullet in 3b then shrinks to "who proposed it (the *credits* column disagrees)". **Do not draw a timeline or citation graph:** arrows between works would state a lineage, and that lineage is exactly what is not established. The brief says "leave it at that". | yes (counts; the quotations are already in the text) |
| §4, opening paragraph of the passage (139 words) | One block does three jobs: the claim, what the 1973 paper is (venue, IEE not IEEE, dates, ISBN), and the search log (Xplore, IET, HathiTrust, OpenAlex, Semantic Scholar, no library request). The search log is a list of *where we looked → what came back* set as running sentences. | minor | Split it. Keep the claim plus identification as prose (about 70 words). Set the attempt as a short two-column list: *Proc. IEE* 120(11) notice → author, title, ISBN confirmed · Hansen's Xplore author record → nothing 1972–74 · Xplore / IET / HathiTrust → refused automated search · OpenAlex / Semantic Scholar → records, no text · library request → none recorded. Keep all of it, because the brief asks to "describe the attempt". | yes |
| `README.md` citation bullet (158 words; 84 added) | A reference-list bullet now carries the history of the correction ("This README used to cite ° Hansen V.G. (1973)… as the origin"). That history already sits in §4 ("This document used to credit…"), and the bullet links there. | minor | Move, don't delete: the "used to cite" sentence and the full 1973 reference go to §4, which already has both. The bullet keeps the `maxlt` = greatest-of statement, the Hansen & Sawyers 1980 reference with its DOI, and "Where greatest-of began is not established; see §4". Prose is right for a citation entry; the problem is only what it carries. | yes |
| `GLOSSARY.md` CFAR paragraph (152 words, one block) | The paragraph lists detector → CFAR variant → source for three detectors inline, and now adds the origin caveat. That mapping is already a table in §4 and in `cfar_scope.html`. A glossary entry is the wrong place to retype it. | minor | Keep the claim sentence ("the mechanisms are CFAR's") and the ruling that priority is closed. Replace the three inline mappings and the caveat with a pointer to the §4 table and to *Where greatest-of began*. Nothing is lost, because the table already holds it. | yes |
| §4 table row "LoCo, `maxlt`", attribution cell | This is the longest cell in the table (about 30 words), including the navigation text "(see *Where greatest-of began*, at the end of this section)". The other rows' cells are just citations. | minor | "**not established** (below); loss analysis: Hansen & Sawyers 1980, *IEEE T-AES* AES-16(1), 115–118". A table is already the right form. | yes |
| `cfar_scope.html`, GO-CFAR caption under its small panel (the `VARIANTS` `cite` string) | The caption now carries a provenance hedge ("; origin not established") and wraps to 3 lines where the other four panels' captions take 2 (rendered, 50 px vs 35 px). The same hedge appears three times on this one page: lede, table row, and this caption. A caption should say what the panel shows. | minor | Caption: "greater of the two half-means / Hansen & Sawyers 1980". The hedge stays in the table row and the lede, which already say it. If a third copy is wanted, put it in the button tooltip (`b.title`) as a separate field. | yes (render in the scratchpad) |
| §4 paragraph after the table (93 words) | Over 60 words, but it is a statement of what the shelf holds and how quotations are checked. There is nothing to compare across and nothing in sequence, so a table or figure would add structure without adding clarity. | none: prose is right here | No change. | yes |
| Revision-note flag (35 words), §7 ⚠ line (21 words), Sources entry (58 words), HTML lede (34 words) | Under the thresholds. Each is a short marker or pointer, and prose is right for that. | none | No change. | yes |

**What I checked:**
- **Files and render:** all changed blocks in the patch, read in the worktree. `cfar_scope.html` rendered at 1280 px, measuring the table row and the five panel captions.
- **Figures:** the only figure in `detector_history.md` is `learned/cfar_map.png` at line 243, and it is unchanged. No changed block adds or removes a figure.
- **Scope:** I did not open `docs/reviews/`, `docs/todo/` or `docs/lit_needed.md`.
- **Overall:** no rendered figure is warranted for this change. The one structural replacement worth making is the four-row table in §4.
