GRANT 10 MISMATCH — missing Grep, Glob; holds no forbidden tools (holds Read, Bash)

I did the searches with `git grep` and plain `grep` in Bash instead. No file edits were made. The GitHub file view shows the page as it should look. The only real rendering defects are in Python-Markdown, plus a few small things.

**Provenance.** `git hash-object` gives `2c9813d5c17a7c946c9c7690ae77f59c9a5fdaf6`, which matches. The worktree is clean. `HEAD` and `origin/unsup/preregistration` are both `4f20d3b` (committed 2026-09-14 18:51 -0400), and the file's blob on origin has the same hash, so it is committed and pushed. The build is current: the Markdown is the deliverable and there is nothing to generate. Document properties and figure checks (axes, colours, glyphs) don't apply, because the page has no metadata block and no figures.

**Renders checked** (all in `<review-session-scratchpad>/r2role10/`):
- **GitHub comment view:** `gh.html`, from `gh api markdown` in gfm mode. This mode turns every source line break into `<br>`, so it is not what the file view shows.
- **GitHub file view:** `ghmd.html`, from `gh api markdown` in markdown mode. Screenshots are `ghmd_page_p0..p5.png`, using CSS that approximates GitHub.
- **Python-Markdown:** `pymd.html`, from the project venv's Markdown 3.10.3 with the tables extension. Screenshots are `pymd_p0..p4.png`.
- All screenshots were taken with Playwright chromium from the venv.

**Scans**
- `python3 tools/sapper.py --all | grep -i preregistration` exited 0 with 74 warnings across the tree, none on the page itself. The grep matched one SAP015 warning ("data" treated as singular) in `docs/reviews/2026-09-14-preregistration-is-rigid-shift-usable-roles/09-show-dont-tell.md:41`.
  - **Blind-pass exposure:** that grep printed one line from a file inside the blind-excluded review directory. I did not open the file, but I did see that line: it argues that figures should exist before any data are read.
- `python3 tools/check_quotes.py --all` exited 0 with `check_quotes: clear`.

## Check table

| Section / table (source lines) | Render checked | Columns per row | Links | *J* / % / ± | Code spans | List separation | Heading | Result |
|---|---|---|---|---|---|---|---|---|
| Title + signed blockquote (1–13) | ghmd_page_p0, pymd.html | n/a | goals/unsupervised-learning.md exists in worktree, branch and main | *afterwards* italic ok | 1 inside link, ok | Lines 8 and 9 have no blank line between them, so "Goal:" and "Why this page exists." merge into one paragraph in every render | h1 | Low defect |
| The question (15–23) | ghmd_page_p0 | n/a | none | bold wraps across the line break; ±*J* renders ± then italic *J* inside bold | none | ok | h2 | pass |
| Why rigid shift (25–38) | ghmd_page_p0 | n/a | 2 todo links, both exist in worktree, branch and main | en dash range ok | none | ok | h2 | pass |
| What this run cannot claim (40–46) | ghmd_page_p0 | n/a | none | ⚠ ok | none | ok | h2 | pass |
| Data (50–61) | ghmd_page_p0, pymd | n/a | 2 todo links, both exist in worktree, branch and main | §9 ok | 2, ok | blank line before list; ok | h2 | pass |
| **Displacements table** (67–71) | ghmd_page_p0/p1, pymd | 3/3/3/3 in all renders | none | header *J* italic | none | n/a | h2 | Pass. Cosmetic: in the screenshot the J column wraps "5.0 s" / "5.6 s" so the "s" sits alone on the next line |
| Family-of-three line (73–74) | ghmd_page_p1 | n/a | none | "98.3 %" ok | none | n/a | n/a | pass |
| Leak gate (82–97) | ghmd_page_p1 | n/a | none | *J* inside bold ok; α, 7.5 %, 1.6 % ok | 2, ok | ok | h3 | pass |
| Count preservation (99–109) | ghmd_page_p1 | n/a | tube todo exists in worktree, branch and main | "±2 %" inside bold ok | 1, ok | ok | h3 | pass |
| Destruction (111–131) | ghmd_page_p1 | n/a | none | ±2-frame ok; *J* ok | 1, ok | ok | h3 | pass |
| **Original outcome table** (141–146) | ghmd_page_p2, pymd | 4/4/4/4/4; the "PASS on one stream, FAIL on the other" row keeps its two empty cells | none | header *J* ok | none | n/a | h2 | pass (above the sign-off line, frozen) |
| What each outcome commits to next (148–154) | ghmd_page_p2 / pymd.html | n/a | none | → ok | 1, ok | **No blank line before the list.** GitHub renders a list; Python-Markdown prints a paragraph with literal "- " | n/a | Low defect in Python-Markdown only |
| Not in this run / What has to be built / Review, once (156–178) | ghmd_page_p2 | n/a | none | × ok | 4, ok | ok | h2 ×3 | pass |
| **Sign-off table** (184–188) | ghmd_page_p2, pymd_p2 | 2/2/2/2 | none | *"agreed. signed"* ok | none | n/a | h2 | Cosmetic: the header row `\| \| \|` renders as an empty bordered strip (frozen area) |
| Amendments preamble (192–204) | ghmd_page_p3 | n/a | Run record `../reviews/…_2026-09-14.md` exists in worktree and on the branch; **not on origin/main** | 98.3 % ok | none | n/a | h2 | Link resolves on the branch; dead from main until merge |
| Adopted amendments intro + terms (208–220) | ghmd_page_p3 | n/a | none | `*J*. *Bootstrap*`: two italics joined by ". " look like one italic phrase | none | n/a | h3 | Cosmetic |
| #### The outcome, completed (222–236) | ghmd_page_p3, pymd_p2 | n/a | none | ok | none | GitHub: 2-space nested list nests correctly. **Python-Markdown: flattened**, so PASS/FAIL/UNDECIDED/VOID become siblings of "Each cell" | h4 | Medium defect in Python-Markdown only |
| **Amended outcome table** (238–245) | ghmd_page_p3, pymd_p2/p3, gh.html | 4 on every one of the 7 rows in all three renders; the "any other combination" row keeps its two empty cells | none | "—" ok | none | n/a | n/a | Pass. Cosmetic: "—" and "any" both mean "doesn't matter" in the same column |
| After UNRESOLVED (247–251) | ghmd_page_p3, pymd_p3 | n/a | none | ok | none | GitHub nested ok; Python-Markdown flattened | n/a | defect in Python-Markdown |
| #### The leak gate (253–271) | ghmd_page_p3/p4, pymd_p3 | n/a | none | 98.33rd / 1.67th ok | none | GitHub nested ok; Python-Markdown flattened (the three bound bullets) | h4 | defect in Python-Markdown |
| #### The count gate (273–285) | ghmd_page_p4 | n/a | none | "96.67 %", "±2 %", "4 %" ok | 2, ok | ok | h4 | pass |
| #### The destruction gate (287–312) | ghmd_page_p4, pymd_p3 | n/a | none | ≥ ok | 1 inside bold, ok | GitHub nested ok; Python-Markdown flattens "Gated K:" and "Controls:" | h4 | defect in Python-Markdown |
| #### Randomness (314–318) | ghmd_page_p4 | n/a | none | ok | 2 (code span inside bold, then the colon), ok | n/a | h4 | pass |
| #### What was known / What a PASS may claim / What STOPPED means / Groups (320–355) | ghmd_page_p4/p5 | n/a | none | *J* in bold and in quotes ok | 1, ok | ok | h4 ×4 | pass |
| All h4 amendment subsections (222–355) | ghmd_page_p3–p5 | n/a | n/a | n/a | n/a | n/a | h4 | Order is valid (h1 > h2 > h3 > h4, nothing skipped), but h4 looks the same as the bold lead-ins around it (1em, bold). The subsections don't stand out as headings |
| Code-span names | `git grep` on the worktree | n/a | `forced_choice`, `destruction`, `edge_thinning`, `freeze_half`, `mouse_bootstrap`, `dataset.current` and `tools/build_surrogate_screen.py` all exist | n/a | n/a | n/a | n/a | Pass. `tools/confirm_rigid_shift.py` is missing, as expected: the page lists it as still to be built |

Totals: 4 tables, 7 relative links (all resolve in the worktree; 6 of 7 on main), 18 code spans, nothing left unrendered (no stray `*` or backticks), 13 percent signs and 6 ± signs, all rendered.

## Findings

| Location | Issue | Severity | Suggested fix | Verified |
|---|---|---|---|---|
| Amendments, lines 224–231, 247–251, 259–262, 298–302, 306–312 | Nested bullets use a 2-space indent. GitHub and CommonMark nest them; Python-Markdown flattens them, so the sub-rules (PASS/FAIL/UNDECIDED/VOID under "Each cell", the three bound rules, the Gated K conditions, the three controls) read as independent top-level rules. | Medium in Python-Markdown; none on GitHub | Indent nested bullets 4 spaces (still correct on GitHub). | yes (pymd_p2, pymd_p3) |
| "What each outcome commits to next.", line 148 | No blank line before the list, so Python-Markdown prints literal "- " inside one paragraph (above the frozen line). | Low | Add a blank line; that counts as a typo-class change. | yes (pymd.html) |
| Amendments preamble, line 204 | The "Run record" link target exists on `unsup/preregistration` but not on `origin/main`. | Low (fixed by merging) | Merge the review record together with the page. | yes (git cat-file) |
| h4 subsections, lines 222–350 | Heading order is valid, but at GitHub's h4 style "The outcome, completed" etc. look like the bold lead-in paragraphs around them, so the amendment structure is hard to scan. | Low | Make "Adopted amendments" h2 and its subsections h3, or add a short list of the subsections at the top of the amendments. | yes (ghmd_page_p3–p5, approximate CSS) |
| Blockquote, lines 8–9 | "Goal:" and "Why this page exists." render as one paragraph (frozen area). | Low | Add a `>` blank line between them (typo-class). | yes (all renders) |
| Amended outcome table, line 244 vs 242–243 | "—" in the Cossart column of the FAIL/FAIL row, "any" in the single-FAIL rows: two marks for "doesn't matter". | Low | Use "any" in the FAIL/FAIL row. | yes (source + ghmd_page_p3) |
| Terms line, line 220 | `*J*. *Bootstrap*` renders as two italics next to each other that read as one italic phrase. | Cosmetic | Write "…declared *J*. **Bootstrap** means…", or put the term definitions on separate bullets. | yes (ghmd_page_p3) |
| Sign-off table header, line 184 | The empty header row renders as an empty bordered strip (frozen area). | Cosmetic | Leave it (frozen), or give it headers "field / value" as a typo-class edit. | yes (ghmd_page_p2, pymd_p2) |
| Displacements table, lines 69–70 | In the screenshot at ~880 px width, "5.0 s" / "5.6 s" wrap so the "s" sits alone. GitHub's real width may differ. | Cosmetic | Use non-breaking spaces (`1.6&nbsp;s`), or shorten the "why" cell. | partial (approximate CSS, not a live GitHub page) |
| Review run itself | This reviewer lacked Grep and Glob, and a scan the brief asked for surfaced one line from the blind-excluded review directory. | Run-record note | Record both in the run ledger: a fallback grant, and a sapper grep that is not blind-safe (it should exclude `docs/reviews/`). | yes |
