GRANT 10 ok — Read, Grep, Glob, Bash

## Ship It: build and craft gate, Hansen 1973 read-through (blind pass)

Everything was checked against the worktree `hansen-1973-read` at HEAD `756a3ac`, which is also `origin/main`, plus its uncommitted changes. All renders are in `<scratchpad>/h73_shipit/`. I wrote nothing inside the worktree: `git status` shows only the six files that were already modified, and nothing untracked.

**Checklist gaps, stated rather than skipped:**
- **Scope:** axis, colour, glyph, histogram and panel rows don't apply. These units contain no figures.
- **Input patch:** `hansen73_diff.patch` doesn't include `docs/lit_needed.md`. I reviewed that unit from `git diff origin/main` instead.
- **Build is current?** It isn't. `docs/learned/detector_history.html` is **stale** and **does need rebuilding** (row 7).

| # | Unit | Checked against | (a) render: columns, blockquote, lists, quote marks | (b) anchor | (c) pytest | (d) sapper / check_quotes | (e) screenshot | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | detector_history.md §4 table row "LoCo, `maxlt`" | `detector_history.gfm.html` (`gh api markdown`, mode=markdown) | 5 `<th>` columns; all 9 body rows have 5 `<td>`; bold and code render | n/a | 262 passed | sapper: clear, rc 0; check_quotes: clear, rc 0 | n/a | PASS |
| 2 | Paragraph after the table | same render, `<p>` holding "interlibrary-loan copy on the same shelf" | Single paragraph, code span intact | n/a | as above | as above | n/a | Renders fine; see findings F2 and F3 |
| 3 | §4.1 "Where greatest-of began" | same render, extracted to `s41.html` | Heading id `user-content-41-where-greatest-of-began`. 3 bold-lead-in paragraphs. First list has 4 `<li>`, second has 2, then a closing `<p>`. No stray `<pre>`. Nested quote `*"using 'greatest-of' selection"*` and `*"…'Conventional' and 'Split'…"*` render as one `<em>` each. Straight quotes, same as the rest of the file | resolves | as above | as above | n/a | PASS on render; see F4 |
| 4 | Blockquoted ⚠ in "Revised 2026-08-24" | same render | One `<blockquote>` from "Revised 2026-08-24" through "Tier 2 framing". The ⚠ italic is a single `<em>` with `<code>maxlt</code>` nested; nothing is split or escaped | n/a | as above | as above | n/a | PASS |
| 5 | §7 item 2 ⚠ | same render | Stays inside its `<ol><li>`; item 3 still starts a new `<li>` | n/a | as above | as above | n/a | PASS |
| 6 | GLOSSARY.md CFAR paragraph and link | `GLOSSARY.gfm.html` | Single `<p>`; link href is `detector_history.md#41-where-greatest-of-began` | resolves against the id in row 3. README.md line 657 has the same fragment, which also resolves | as above | as above | n/a | PASS |
| 7 | docs/learned/detector_history.html (built page) | Rebuilt `detector_history.md` with `tools/md_to_page.py --out <scratchpad>/h73_shipit/rebuild` and diffed against the committed file | Diff has 11 hunks, all in the changed passages (lines 444, 687, 731, 757–821, 1226). The committed page still says "withdrawn as unverified" and "Hansen & Sawyers **read in full**" | n/a | n/a | n/a | n/a | **FAIL: stale. Needs rebuilding** |
| 8 | lit_needed.md Hansen entry | `lit_needed.gfm.html`, plus a render of the `origin/main` version for comparison | The new "Fetched 2026-09-14" paragraph renders **inside a `<pre><code>` block**: raw `**` and backticks, monospace. The code block already existed on `origin/main` (6-space continuation after a blank line); this change makes it longer. The API's mode=markdown also shows `[x]` as literal text, so I couldn't confirm checkbox rendering | n/a | as above | sapper clear; check_quotes scans it (tracked `*.md`), clear | n/a | FAIL (inherited); see F5 |
| 9 | Proposal footer (`docs/proposals/2026-09-10-coordination-without-labels.html`) | Playwright chromium at 1280×900: `footer_1280_light_ctx.png`, `footer_1280_dark_ctx.png` | The correction bracket stays inline in the lineage paragraph. No overlap, no running off the page, document scrollWidth is 1280 = viewport. Footer box is x=368, w=543 px (42% of width), h=303 px; text 13.12 px. No links in the footer | n/a | n/a | sapper clear. **check_quotes does not scan `.html`**, so it never saw this unit | Light and dark both taken | Renders fine; see F6 |

## Findings

| ID | Location | Issue | Severity | Suggested fix | Verifiable |
|---|---|---|---|---|---|
| F1 | docs/learned/detector_history.html | **Stale build.** The page on disk is older than the edited markdown (15:33 vs 15:34) and contains none of the new text: its hunks match the `origin/main` markdown, not the worktree. Shipping it publishes the "withdrawn as unverified" wording this change replaces. | blocking | Re-run `tools/md_to_page.py docs/detector_history.md` to docs/learned and the darkroom in the same commit, then re-check this row against the new build. | yes |
| F2 | detector_history.md, paragraph after the §4 table; darkroom `lit/radar/` shelf | **The shelved PDF isn't on this machine's shelf.** The text says the 1973 paper was read "from an interlibrary-loan copy on the same shelf", and lit_needed says it is shelved as `radar/gregers_hansen_1973_cfar_search_radars.pdf`. That file isn't in the darkroom `lit/radar/` folder, and no `*1973*` file exists anywhere in the darkroom except `iee_conf_105_1973_CONTENTS_ONLY.pdf`. The shelf's `README.md` (last modified 2026-08-22) has no 1973 or Gregers read-status entry, although the same paragraph says each paper has one. Dropbox may not have synced yet from another machine. | major | Put the PDF on the shelf and add the `radar/README.md` read-status entry before merge, or confirm it is still syncing. | yes (absent on this machine) |
| F3 | detector_history.md line 474 | The bold count "**Four of the table's papers are held and read in full**" no longer matches the rendered table, which now marks five papers read in full (the `maxlt` row says "both"). | minor | Change it to "Five", or reword so the 1973 paper is counted. | yes |
| F4 | detector_history.md line 509 vs lit_needed.md lines 97 and 105 | The title is spelled two ways. §4.1 now quotes *"Constant false alarm rate processing…"* (no hyphens); lit_needed and the contents-listing transcription use "Constant-false-alarm-rate". A quoted title should match one source. | minor | Check the title page (for example with `pdftotext -f 1 -l 1`) and use that spelling in both files. | yes, once the PDF is present |
| F5 | lit_needed.md Hansen entry, new "Fetched 2026-09-14" paragraph | It renders as raw monospace code on GitHub, with literal `**`. The same code block already covered the earlier paragraphs of this entry on `origin/main`; this change only adds to it. | minor | Out-dent the continuation paragraphs after blank lines to the list-item content indent (2 spaces), or fix the lazy `>` line at 105. Probably a separate commit, since it predates this change. | yes |
| F6 | Proposal footer, lineage paragraph | Measured text contrast is **2.79:1 in light** and **4.26:1 in dark**, both below 4.5:1, at 13 px. The correction bracket uses the same gray as the text around it, so it doesn't stand out. The `docs/detector_history.md §4.1` pointer is plain text, not a link. Styling and link absence predate this change; the correction depends on them. | minor | Leave the footer style alone. Consider a link to the §4.1 anchor so readers of the standalone page can follow the pointer. Whether the correction needs more emphasis is for another role to decide. | yes |
| F7 | darkroom `detector_history.html` (root) | The darkroom copy is from 2026-08-29. It is missing this change and also the earlier #564 and #568 text. | minor | Fixed by the F1 rebuild, which writes to both destinations. | yes |
| F8 | Review input | `hansen73_diff.patch` leaves out `docs/lit_needed.md`, a unit named in the brief. A reviewer working only from the patch would never see it. | minor (about the run) | Regenerate the patch from `git diff origin/main` over every changed unit before the re-review. | yes |

**Files I relied on:**
- `<scratchpad>/h73_shipit/detector_history.gfm.html`
- `<scratchpad>/h73_shipit/GLOSSARY.gfm.html`
- `<scratchpad>/h73_shipit/lit_needed.gfm.html`
- `<scratchpad>/h73_shipit/lit_needed.main.html`
- `<scratchpad>/h73_shipit/s41.html`
- `<scratchpad>/h73_shipit/rebuild/detector_history.html`
- `<scratchpad>/h73_shipit/footer_1280_light_ctx.png`
- `<scratchpad>/h73_shipit/footer_1280_dark_ctx.png`
