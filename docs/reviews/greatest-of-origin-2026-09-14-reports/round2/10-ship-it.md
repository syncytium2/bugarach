GRANT 10 ok — Read, Grep, Glob, Bash

# Ship It review: the "greatest-of origin not established" change (round 2, blind pass)

**Verdict:** GitHub renders every changed markdown unit correctly, the link tests and both repo gates pass, and `detector_history.html` matches its markdown. Three findings need action:
- **F1:** the page renders `~~Hansen 1973~~` with the tildes showing instead of a strikethrough.
- **F2:** the new §7 item 2 warning runs straight into the text of items 3–5 on the page.
- **F3:** the darkroom copy, which is the one a person opens, is older than all of this and does not contain the correction.

F1 and F2 come from `md_to_page.py` and were already there on origin/main, but this change now puts correction text on them. No blocking findings.

I wrote only to `…\scratchpad\r2_shipit\`. I opened nothing under `docs/reviews/`, `docs/todo/` or `docs/lit_needed.md`.

## Check table

| # | Unit | Render checked against | Result |
|---|---|---|---|
| a1 | `detector_history.md` §4 table, row "LoCo, `maxlt`" | `r2_shipit/detector_history.gh.html` (`gh api markdown`, gfm) | **pass.** All 9 rows have 5 cells, header included. The longer cell stays in its column. |
| a2 | `detector_history.md` paragraph after the table | same | **pass.** One `<p>`. |
| a3 | `detector_history.md` new "Where greatest-of began" passage | same | **pass.** Lead paragraph, 2 lists (4 items and 4 items), then `<hr>`. Nested `'Conventional'`/`'Split'` quotes are inside `<em>`, and every `*"…"*` quote closes. |
| a4 | `detector_history.md` "Revised 2026-08-24" blockquote | same | **pass on GitHub.** `<del>Hansen<br>1973</del>`: the strikethrough spans the line break, and the blockquote stays one unit. `*…see §4,* Where greatest-of began` sets the section name upright inside italics. That looks deliberate. |
| a5 | `detector_history.md` §7 item 2 continuation | same | **pass on GitHub.** The ⚠ lines stay inside item 2's `<p>`, and item 3 opens a new `<li>`. |
| a6 | `detector_history.md` Sources entry | same | **pass.** One `<li>`, and the patent note is inside it. |
| a7 | `GLOSSARY.md` CFAR paragraph and bullet | `r2_shipit/GLOSSARY.gh.html` | **pass.** One `<p>`, both links render, and the bullet is one `<li>` followed by the next `<h2>`. |
| a8 | `README.md` citations bullet and legend | `r2_shipit/README.gh.html` | **pass.** The 2-space continuation stays inside the LoCo/CoactDetect `<li>`, the link renders mid-item, and the next `<li>` (PySpike) starts clean. The legend is one `<p>`. |
| b1 | `cfar_scope.html` at 1280 px | `cfar_full_1280.png`, `cfar_map_1280.png`, `cfar_minis_1280.png` (Playwright chromium) | **pass.** Page width 1280, no JS errors. Map table 1050 px in a 1094 px card, no scroll. The GO row wraps to 2 lines (53 px), the same height as the CA and OS rows. The GO mini-card cite wraps to 3 lines (rule text 50 px vs 35 px on the other cards). The grid gives all 5 cards the same 194 px height, so nothing overlaps. The GO chip tooltip reads correctly. |
| b2 | `cfar_scope.html` at 400 px | `cfar_full_400.png`, `cfar_map_400.png`, `cfar_minis_400.png` | **minor defect (F4).** The map card's scroll width is 379 against a client width of 366, so it now scrolls sideways by 13 px; origin/main is 366 = 366. The cause is the longer GO cell ("established)" / "analysis;"). The mini-cards stack cleanly, and the cite fits on one line. |
| b3 | `detector_history.html` §4 table at 1280 / 400 | `dh_table_1280.png`, `dh_table_400.png` | **pass at 1280.** The table is 658 px inside the 842 px column edge, and the maxlt row is 187 px tall. **At 400 px the table overflows the column** (right edge 530 against 376). That was already true on origin/main (522), and this change adds 8 px. |
| b4 | `detector_history.html` new passage at 1280 | `dh_passage_1280.png` | **pass.** Lists and quotes render, and nothing overlaps. |
| b5 | `detector_history.html` blockquote | `dh_bqp_1280.png` | **defect (F1).** The text renders as `(~~Hansen 1973~~; ⚠ …`. `md_to_page.py` loads no strikethrough extension. |
| b6 | `detector_history.html` §7 | `dh_s7_1280.png` | **defect (F2).** The "Net effect…" paragraph sits *outside* the `<ol>`, and it runs on as "…says what is known. 3. ~~Fetch Malvache…~~ … 4. Soften … 5. Search…". |
| c | Link resolution | `pytest -q tests/test_index_resolves.py tests/test_milestones_resolve.py` | **pass.** 243 passed. |
| d | Repo gates | `tools/sapper.py --all`, `tools/check_quotes.py --all` | **pass.** Both report `clear`. |
| e | `detector_history.html` build is current | rebuilt into `r2_shipit/rebuild/` and `rebuild_utf8/` (with `-X utf8`), then `cmp` | **pass.** Both rebuilds are byte-identical to the repo copy. It is UTF-8 with `<meta charset>`, and its mtime (12:34:20) is later than the markdown (12:32:14). The repo diff also brings in about 200 lines, such as the "Revised 2026-08-30" block and its tables, that origin/main's page had never picked up. That is expected: the old build was stale. |
| e2 | Darkroom copy `<darkroom>/bugarach/detector_history.html` | byte comparison plus text search | **fail (F3).** Last modified 2026-08-29 16:20. It differs from the repo copy and does not contain "Where greatest-of began". |

## Findings

| ID | Location | Issue | Severity | Suggested fix | Verifiable |
|---|---|---|---|---|---|
| F1 | `docs/learned/detector_history.html`, "Revised 2026-08-24" blockquote (source line ~204) | The struck-out citation, which is the point of the correction, shows as literal `~~Hansen 1973~~` on the page. `render()` calls `markdown.markdown(..., extensions=["tables","fenced_code","sane_lists","attr_list"])`, and none of those handles `~~`. The page shows 6 literal `~~`; origin/main showed 4, so this change adds 2. GitHub renders it correctly. | major | Either add a strikethrough extension such as `pymdownx.tilde` to `md_to_page.py` and rebuild, or avoid `~~` in the blockquote (for example "formerly credited to Hansen 1973"). The tool fix is outside this diff. | yes (`dh_bqp_1280.png`) |
| F2 | `docs/learned/detector_history.html` §7 item 2 (source lines ~995–999) | In python-markdown, item 2's 3-space continuation and items 3–5 collapse into one paragraph outside the list. The new "⚠ 2026-09-14: one attribution did not survive…" sentence now runs straight into "3. ~~Fetch Malvache et al. 2016 by hand.~~". This was already broken on origin/main, but the correction note now sits right at the break. GitHub renders it correctly. | major | Indent the §7 list continuations to 4 spaces, or give `md_to_page.py` a list-indent setting. Then rebuild. | yes (`dh_s7_1280.png`) |
| F3 | `<darkroom>/bugarach/detector_history.html` | The page was rebuilt with `--out docs/learned` only. The darkroom copy is from 2026-08-29 and has no "Where greatest-of began" text. The copy a person opens still shows the old attribution. | major | Rebuild with the default destination (the darkroom) and `--also docs/learned`, after claiming the darkroom on the board. | yes |
| F4 | `docs/learned/cfar_scope.html` map table, GO row, at 400 px | The longer source cell makes the card scroll sideways by 13 px (379 against 366). It did not scroll before. The last column touches the card edge. | minor | Shorten the cell, for example "Hansen & Sawyers 1980; origin unsettled", or drop the parenthetical down a line in smaller type. | yes (`cfar_map_400.png`) |
| F5 | `docs/learned/detector_history.html` §4 table at 400 px | The table overflows the text column by 154 px, and the page width is 800 on a 400 px viewport. This was already the case on origin/main; this change adds 8 px. | minor | Wrap `.doc table` in `overflow-x:auto` inside the `md_to_page.py` EXTRA CSS. | yes |
| F6 | `detector_history.md` §4, "Where greatest-of began" | The README, GLOSSARY, the §4 table row, the blockquote, §7 and Sources all send readers to "§4, *Where greatest-of began*". It is a bold lead-in, not a heading, so there is no anchor. The README and GLOSSARY links land at the top of a 66 KB document. | minor | Make it a `###` heading and link `detector_history.md#where-greatest-of-began` from the README and GLOSSARY. | yes |

Note on method: the gfm-mode API renders soft line breaks as `<br>`, which GitHub's file view does not. That changes line breaks only; all the structure checks above hold in either mode.

Files are in `<scratchpad>\r2_shipit\`:
- GitHub renders: `detector_history.gh.html`, `GLOSSARY.gh.html`, `README.gh.html`
- Rebuilds: `rebuild/detector_history.html`, `rebuild_utf8/detector_history.html`
- Screenshots: `cfar_*.png`, `dh_*.png`
- Tool at fault in F1, F2 and F5: `<worktree>\tools\md_to_page.py`
