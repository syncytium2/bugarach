GRANT 10 ok — Read, Grep, Glob, Bash

**Run note: the artifact changed while I was reviewing it.** I ran checks (a) to (g) against the r2 patch state, where the source was last modified at 15:52 and the build at 15:52:56. Then two commits landed on `hansen-1973-read`: 976b3db (WIP) and 6fce425 ("Apply murderboard round 2 (role 4)"). They rewrote `docs/detector_history.md` (§4.1 opening, the table cell, the blockquote ⚠, the end of the later-sources list) and rebuilt the HTML at 16:04:58. I re-ran (a), (c), (d) and (e) and the §4.1 render at 6fce425, and give both results where they differ. Screenshots and renders are in `<scratchpad>/h73_shipit_r2/`.

Also, `git diff origin/main` now pulls in unrelated files (`docs/SESSIONS.md`, `docs/site/*`, `tests/test_webapp_annotate.py`). The local `origin/main` has moved past the branch base 756a3ac, so "diff vs origin/main" no longer describes this change on its own. Use the merge-base diff instead.

## Check table

| Unit | Render checked against | Result (r2 snapshot) | Result (live, 6fce425) |
|---|---|---|---|
| `detector_history.md` §4 table row | `gh api markdown` mode=markdown → `ghm_detector_history.html` / `ghm_live_dh.html`; built page → `built_table.png` | All 9 rows have 5 cells; `maxlt` row has 5 `<td>`; "both read in full" renders | Same, 5 cells per row |
| Paragraph after the table | gh render | Single `<p>`, bold intact | Unchanged |
| §4.1 nested list (gh) | gh render | Correct `<ul>` with 3 `<li>`; `10⁻⁵` and `√2` intact | Correct. **New defect:** the blank line after the Gandhi & Kassam bullet was deleted, so the "Finn & Johnson 1968 and Weinberg 2017…" paragraph now sits inside that `<li>` |
| §4.1 nested list (built HTML) | `built_41_a.png`, `live_41_b.png` | **FAIL:** the three bullets come out as literal " - Fig. 6…", " - Fig. 5…", " - On p. 327…" run into the quote paragraph | **FAIL**, same. Plus the Finn & Johnson paragraph is absorbed into the Gandhi & Kassam bullet (visible in `live_41_b.png`) |
| Blockquoted ⚠ (~l.205) | gh render | Stays inside the one `<blockquote>`, no stray close; italic span intact | Same |
| §7 item 2 ⚠ | gh render; built HTML | gh: correct `<ol>`, item 3 keeps `<del>`. Built: items 3–5 render as literal "3. ~~…" | Same. The built-page break **is already on origin/main** (checked `main_built.html`), not introduced here |
| (b) `#41-where-greatest-of-began` from README and GLOSSARY | `ghm_README.html`, `ghm_GLOSSARY.html` hrefs vs `id="user-content-41-where-greatest-of-began"` in the detector_history render | Resolves; only one heading makes that slug | Resolves |
| (c) Built HTML vs fresh rebuild (PYTHONUTF8=1) | `rebuild/`, `rebuild_live/` | Byte-identical (sha256 750e22cb…); build newer than source | Byte-identical (6cfb07a3…); build 16:04:58 is newer than source 16:04:19. §4.1 list still renders wrong (row above) |
| `docs/GLOSSARY.md` | `ghm_GLOSSARY.html` | One paragraph, link and code span correct | Not re-rendered (not in 6fce425's source diff) |
| `docs/lit_needed.md` | `ghm_lit_needed.html` vs `ghm_main_lit_needed.html` | New "Fetched 2026-09-14" paragraph renders **inside a `<pre><code>` block**. Everything from l.107 onward in that entry is a code block, and that was already true on main (6063 → 6820 bytes) | Same |
| Proposal footer | Playwright at 1280 px → `proposal_footer_1280.png` | Correction wraps cleanly inside the footer column (box 543×223 px, 13.1 px gray); page scrollWidth 1280, no horizontal overflow; `&sect;` renders | Not in 6fce425's diff |
| (d) pytest: index, milestones, check_quotes | venv python | 262 passed | 262 passed |
| (e) `sapper.py --all`, `check_quotes.py --all` | stdout | Both "clear", exit 0 | Both "clear" |
| (g) Shelf PDF and README entry | `ls` of `<darkroom>/lit/radar/` (`darkroom()` already ends in `bugarach/`); grep of README | `gregers_hansen_1973_cfar_search_radars.pdf` is present (1.92 MB, `%PDF-1.7`, `%%EOF`, /Count 8). README has "Read in full — added 2026-09-14" naming the file. PDF is not in the git index | Same |
| Mojibake scan | grep of all units and renders | None | — |

## Findings

1. **Built `docs/learned/detector_history.html`, §4.1, "What the 1973 paper says".** The three-bullet list (Fig. 6, Fig. 5, p. 327 rule) is not a list on the built page. It is inline " - " text inside the quote paragraph. `md_to_page.py` needs a blank line before a list; GitHub does not, so the gh check passes and the page a person opens fails. This is new in this change, so it is not covered by "pre-existing".
   - **Severity:** major
   - **Fix:** put a blank line between "…(p. 326)." and "- Fig. 6…" in the source, then rebuild.
   - **Verifiable:** yes (`built_41_a.png`)

2. **`docs/detector_history.md` at 6fce425, around l.582–583.** Round 2 deleted the blank line after "their venue, an IEEE conference, does not." The paragraph "Finn & Johnson 1968 and Weinberg 2017, also on the shelf, say nothing…" is now a lazy continuation of the Gandhi & Kassam bullet, both on GitHub and on the built page. It reads as part of what Gandhi & Kassam say.
   - **Severity:** major
   - **Fix:** put the blank line back before "Finn & Johnson 1968 and Weinberg 2017", then rebuild.
   - **Verifiable:** yes (`live_41_b.png`, `ghm_live_dh.html`)

3. **The review target moved during the review.** Two commits edited the artifact while this role was running on the r2 patch. The r2 rows describe a file that is no longer the one shipping, and the round-2 edit brought in finding 2. This is a finding about the run.
   - **Severity:** major
   - **Fix:** freeze the artifact while reviewers run, or re-run this gate against 6fce425 or later, and record which sha each role reviewed.
   - **Verifiable:** yes (`git log`, file mtimes)

4. **`docs/lit_needed.md`, Hansen 1973 entry.** The new "Fetched 2026-09-14, the same afternoon" paragraph, like everything from l.107 in that entry, renders on GitHub as a monospace code block. Blank-line-separated paragraphs indented 6 spaces under a list item whose content starts at column 2 become indented code. This is not new, but the change adds to it and it is the entry's conclusion.
   - **Severity:** minor
   - **Fix:** re-indent the entry's continuation paragraphs to 2 spaces, or accept it and note it as known.
   - **Verifiable:** yes (`ghm_lit_needed.html`)

5. **Built HTML, §7 items 3–5.** They render as literal "3. ~~…~~" text, because item 2's nested bullet list is not indented as list content for `md_to_page.py`. Already true on origin/main; the edited ⚠ in item 2 sits just before the break.
   - **Severity:** minor
   - **Fix:** indent the "The last two arrived…" paragraph and its bullets by 3 spaces with blank lines, or fix the converter.
   - **Verifiable:** yes

6. **Darkroom copy `<darkroom>/detector_history.html`.** It is dated 2026-08-29 (258 KB) and matches neither repo build. It predates this change and the morning's withdrawal. `docs/todo/2026-09-14-greatest-of-follow-ups.md` says the darkroom rebuild is claimed, so this may just be pending, but right now the copy a person would open is stale.
   - **Severity:** minor
   - **Fix:** re-publish to `darkroom()` after findings 1 and 2 are fixed.
   - **Verifiable:** yes

The built page's §4.1 `<h3>` has no `id`, but the README and GLOSSARY links point at the `.md` on GitHub, where the anchor resolves, so this is not a finding.
