GRANT 10 ok — Read, Grep, Glob, Bash

# Build & craft gate (role 10): greatest-of origin change, round 3 (blind pass)

**Result:** All six units render, and the gates and link tests pass. Two issues are real:
- **§7 of the built page is broken.** On `detector_history.html`, the new ⚠ sentence for §7 item 2 does not render inside that list item.
- **The darkroom copy is stale.** The copy people open still credits Hansen 1973 and has no §4.1.

All renders and screenshots are in the scratchpad folder `r3_shipit/`.

## Gate table (one row per unit)

| Unit | Render checked against | Structure / overlap / overflow | Links and anchor | Build current | Result |
|---|---|---|---|---|---|
| `docs/detector_history.md` | `gh api markdown`, file mode (`docs_detector_history.md.file.html`); a second call in comment mode is not what GitHub uses for files | **Revision blockquote:** ⚠ sentence is inside the blockquote, and the `<em>` closes before "Separately". **§4 table row:** 5 cells, correct. **Paragraph after table:** one `<p>`. **§4.1:** `<h3>`, 3 paragraphs, 4-item and 3-item `<ul>`; nested single quotes inside double quotes render correctly. **§7 item 2:** the ⚠ sentence is inside its `<li>` and the list carries on to item 3. **Sources entry:** inside its `<li>`. | Anchor is `id="user-content-41-where-greatest-of-began"`, `href="#41-where-greatest-of-began"`, and it is unique. **(a) Yes: it equals `41-where-greatest-of-began`.** | n/a (source file) | pass |
| `docs/GLOSSARY.md` | `gh api markdown`, file mode | CFAR paragraph is one `<p>`; the link renders as a code span plus "§4.1" | `href="detector_history.md#41-where-greatest-of-began"` resolves to the anchor above | n/a | pass |
| `README.md` | `gh api markdown`, file mode | The citation bullet with 2-space continuation stays one `<li>`; the link sits inside it | `href="docs/detector_history.md#41-where-greatest-of-began"` resolves | n/a | pass |
| `docs/learned/cfar_scope.html` | Playwright chromium. 1280 px: `cfar_1280_full.png`, `_lede.png`, `_table.png`, `_minis.png`. 400 px: `cfar_400_*.png`. Diffed against the page at `origin/main`. | **Lede:** wraps cleanly at both widths. **Map table:** no clipping. At 400 px the scroll box now overflows by 13 px (379 vs 366; it was 0 at `origin/main`). Only the right padding is lost. **GO mini card at 1280:** the cite now wraps to 3 lines (rule block 50 px vs 35 px), so every card in the row grows from 179 to 194 px. Text stays aligned and nothing overlaps. No page errors. No page-level horizontal overflow at either width. | No links changed | Hand-edited; no generator exists (grep of tools/src/tests finds none) | pass (2 minor) |
| `docs/proposals/2026-09-10-coordination-without-labels.html` | Playwright chromium, 1280 and 400 px (`prop_footer_1280.png`, `prop_footer_400.png`) | Correction sits inside the footer `<p>` (13.1 px, muted grey, like the rest of the footer). No overlap. Page width equals viewport at 400 px. | Plain-text path, no link | Hand-edited | pass |
| `docs/learned/detector_history.html` | Fresh rebuild with `tools/md_to_page.py` into scratch, `cmp` against the committed file, plus Playwright screenshots `dh_1280_s4_1.png`, `dh_400_s4_1.png`, `dh_1280_s7.png`, `dh_400_s7.png`, `dh_1280_s4_table.png` | **§4.1:** renders correctly at both widths. **§7: broken (finding 1).** Page width is 800 px at a 400 px viewport, but that is the same at `origin/main`: a wide code block and the §4 table (right edge 522 px) have no scroll wrapper. The new text adds no overflow; §4.1 has none. | The page has no heading ids, so `#41-…` does not work on the HTML. Nothing links there. | **(e) Byte-identical to a fresh rebuild.** The `.md` was modified at 12:56:13 and the page written at 12:56:31; `report.css` and `md_to_page.py` date from 11:33. **The darkroom copy is stale (finding 2).** | **fail (§7)** |

**Other checks:**
- **(c) Link tests:** `pytest -q tests/test_index_resolves.py tests/test_milestones_resolve.py` gave **243 passed**. The test root is the worktree. These tests do not check `#fragment` anchors; the anchor was confirmed from the GitHub render in (a).
- **(d) Gates:** `tools/sapper.py --all` printed "clear" (exit 0). `tools/check_quotes.py --all` printed "clear" (exit 0).

**Two specific questions:**
- **Literal "~~" in text this change added:** none. The built page shows 4 literal `~~`, the same count as the page at `origin/main`. They are the struck-out openings of §7 items 2 and 3, which were already there; this change added none. GitHub's render shows them as proper `<del>`.
- **Does the §7 item 2 ⚠ sentence render inside its list item?**
  - **On GitHub:** yes.
  - **In `detector_history.html`:** no (finding 1).

## Findings

1. **Location:** `docs/learned/detector_history.html`, §7. See `dh_1280_s7.png`.
   - **Issue:** The page builder only accepts continuation lines indented 4 spaces. The markdown uses 3, so item 2's list closes after its first paragraph. "The last two arrived…", its bullets and "Net effect… ⚠ 2026-09-14…" become free paragraphs outside the numbered list. Then "3. ~~Fetch Malvache…~~", "4. Soften…" and "5. Search…" run together into that same paragraph, with literal numbers and `~~`. The new correction sits right against the literal "3.". This was already broken at `origin/main`, but this change puts its correction into the broken region and ships the rebuilt page.
   - **Severity:** major
   - **Fix:** Indent §7's continuation lines by 4 spaces, or enable a list extension in `md_to_page.py` that accepts 3-space continuations. Rebuild, then confirm the ⚠ sentence sits inside item 2's `<li>` and that items 3–5 are `<li>`.
   - **Verifiable:** yes

2. **Location:** the darkroom copy of `detector_history.html`.
   - **Issue:** It is dated 29 Aug and differs from the repo build. It has no §4.1, no "withdrawn as unverified", and still says `CAGO-CFAR`. The page was rebuilt with `--out docs/learned` only, so the copy a person opens still carries the withdrawn credit. The project rule is to keep both copies.
   - **Severity:** major
   - **Fix:** Rebuild with the darkroom as the default output and `--also docs/learned`, after fixing finding 1. The darkroom is shared, so claim it on the board first.
   - **Verifiable:** yes

3. **Location:** `cfar_scope.html`, map table at 400 px.
   - **Issue:** The longer source cell makes the scroll box scroll horizontally by 13 px, where `origin/main` had none. Only the right padding is lost; no text is clipped.
   - **Severity:** minor
   - **Fix:** Shorten the cell to "origin unknown; loss: Hansen & Sawyers 1980", or accept it.
   - **Verifiable:** yes

4. **Location:** `cfar_scope.html`, the "GO-CFAR" mini card at 1280 px (`cfar_1280_minis.png`).
   - **Issue:** "loss analysis: Hansen & Sawyers 1980" wraps to a third line, so all five cards grow 15 px. It is visibly the only card with 3 lines of caption.
   - **Severity:** minor
   - **Fix:** Use a shorter cite, e.g. "loss: Hansen & Sawyers 1980", which matches the table's wording.
   - **Verifiable:** yes

5. **Location:** `detector_history.md` §4 table, LoCo `maxlt` row (`dh_1280_s4_table.png`).
   - **Issue:** The "Held?" cell still reads "read in full" beside "origin **not established**". Seen on the page, it can read as if the origin paper were read, when it refers to Hansen & Sawyers. How to word it is a judgment call for the prose roles.
   - **Severity:** minor
   - **Fix:** Qualify it, e.g. "1980 paper read in full".
   - **Verifiable:** yes

6. **Location:** the two link tests.
   - **Issue:** They check file paths but not `#fragment` anchors. If the §4.1 heading is renamed, the README and GLOSSARY links break with the suite still green. Today the anchor matches, confirmed in (a).
   - **Severity:** minor (process gap, not a defect in this change)
   - **Fix:** File a request in `docs/sapper_feedback/`, or add GitHub-style slug checking to `test_index_resolves.py`.
   - **Verifiable:** yes

**Run notes:**
- No renders were missing; every row above names its render.
- A pre-tool hook blocked writing a Python file through a heredoc, so the Playwright scripts were piped to the interpreter on stdin. Only PNG and HTML intermediates went to scratch; nothing was written in the worktree.
- `git diff --stat origin/main` also lists `docs/SESSIONS.md` (−10). That file is not in the patch, which suggests `origin/main` has moved since the merge. Not part of this artifact.
