GRANT 10 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash)

The missing Grep and Glob didn't block anything: I ran every search through Bash instead. It still goes in the run ledger as a fallback-path grant.

**Bottom line:** the page renders correctly on GitHub. All three tables have the right number of columns, all six relative links work in both places, and the italics and bold around *J* come out right. Sapper and the private-correspondence check are clean. Nothing blocks. There are three major findings and a few minor ones. Two of the major ones only matter when the result is read against the outcome table, which is the job this frozen table is for.

**Build is current:** the file's hash is `550d3e49d189d128d7522985be787f610cb95b90`. That matches the signed version, the worktree head and `origin/unsup/preregistration` (all at `02fe50e`). The worktree has no uncommitted changes. Markdown has no document properties to stamp; the file has no frontmatter.

**Renders I checked against** (all in `<review-session-scratchpad>/role10/`):
- **GitHub's HTML:** `gh.html`, from `gh api markdown` in gfm mode with the repo as context.
- **Screenshot of GitHub's HTML:** `gh_full.png` for the whole page, plus crops `banner.png`, `table0.png` (displacements), `table1.png` (outcome), `table2.png` (sign-off). These use a GitHub-like stylesheet at 880 px wide, with `<br>` removed to match how GitHub shows a file.
- **Editor-style render:** `local.html`, from Python-Markdown with the tables extension.

## Table

| Unit | Render checked | Columns / structure | Links | Italics, bold, code | Result |
|---|---|---|---|---|---|
| Title + quoted banner | gh.html, banner.png, local.html | 1 blockquote with 2 paragraphs | `../goals/unsupervised-learning.md`: works in the worktree and on origin/main | Bold and code span inside the link are fine | Pass, with a minor issue: on GitHub the "Goal:" line and "Why this page exists." run together in one paragraph |
| The question | gh.html, gh_full.png | h2 plus 2 paragraphs | none | "±*J*" renders as ±<em>J</em> inside bold, and the bold that spans lines closes correctly | Pass |
| Why rigid shift, and why only rigid shift | gh.html | h2 plus 2 paragraphs | the join todo and the seed-0 todo: both work in the worktree and on origin/main | Fine | Pass (a link labelled just "todo" is a wording call for another role) |
| What this run cannot claim | gh.html | h2, 1 paragraph, then a horizontal rule | none | ⚠ and bold are fine | Pass |
| Data | gh.html | 4-item list | the empty-baseline todo and the four-recordings todo: both work in the worktree and on origin/main | `dataset.current("…")` code spans are fine | Pass |
| The displacements — accepted | gh.html | h2 | none | Italic *J* is fine | Pass |
| Displacements table | table0.png, gh.html, local.html | 3 columns in every row, in both renders | none | Italic *J* in the header is fine | Minor: the unit wraps onto its own line ("5.0 / s", "5.6 / s") at 880 px |
| The gates, including its three subsections | gh.html, gh_full.png | h2, 3 h3s, 3 lists | the tube foot-gun todo: works in the worktree and on origin/main | "**Pass at a *J*:**" nests correctly; "**±2 % of the mean real count**", "**at most 0.25** (accepted)" and "**Not circular⏎shift**" all render bold | Pass |
| The outcome, per stream and overall | gh.html, local.html | h2 plus a paragraph, then a list that follows the paragraph with no blank line | none | Fine on GitHub | Minor: in Python-Markdown the "What each outcome commits to next" list shows as plain text with literal "- " |
| Outcome table | table1.png, gh.html, local.html | 4 columns in every row, in both renders; the empty cells are real empty cells | none | Bold outcome words and italic *J* in the header are fine | Major: cells in the wrong columns, blank and dash used inconsistently, and no VOID row (see findings) |
| Not in this run | gh.html | 3-item list | none | Fine | Pass |
| What has to be built, and its cost | gh.html | 4-item list | none (the tool path is in a code span and does not exist yet, which the section says) | Code inside bold (`tools/confirm_rigid_shift.py`) is fine | Pass |
| Review, once | gh.html | 1 paragraph, then a horizontal rule | none | `/murderboard` code span is fine | Pass |
| Sign-off | gh.html, gh_full.png | h2, table, italic closing line | none | Fine | Minor: "the sign-off line" is not a visible line (see findings) |
| Sign-off table | table2.png, gh.html, local.html | 2 columns in every row | none | Bold "Accepted as written." and italic *"agreed. signed"* are fine | Minor: its header row is empty, so a blank grey bar shows above it |
| Amendments | gh.html | h2 plus 1 paragraph | none | Fine | Pass |
| Horizontal rules | gh.html, local.html | 4 in both renders (after the cannot-claim section, the displacements, the gates, and Review) | — | — | Pass |
| Whole page overflow | gh_full.png | page width equals viewport width (960 = 960); every table is 880 px, the column width | — | 19 italics, 69 bold, 12 code spans in both renders; no stray asterisks left in the text | Pass |

**Scripts run:**

| Check | Result | What it actually covers |
|---|---|---|
| `pytest tests/test_index_resolves.py` | 251 passed | **Only the links in `docs/INDEX.md`.** It never reads this page, so it does not vouch for the page's links. My own check of all 6 relative links against the worktree and `origin/main` did that: 6 of 6 work. |
| `tools/sapper.py --all` | 0 hits on this page | The scan does cover `docs/proposals/`: two sibling proposals in that folder raise SAP015. So a clean result here means something. |
| `tools/check_quotes.py --all` | "check_quotes: clear", exit code 0 | Whole tree |
| GitHub rendering API | Worked on the second try | The first try used a path that doesn't exist (`repos/.../markdown` gave a 404). The correct call is `gh api markdown -F text=@file`. |

## Findings

(location · issue · severity · suggested fix · verified yes/no)

1. **Outcome table, "PASS on one stream, FAIL on the other" row** · The text sits in the **fast** column while the slow column is blank. In the render that reads as fast = "PASS on one stream…" and slow = nothing, not as a row covering both streams. The Cossart column is also left blank, when it could say "passes or fails". · major · Amendment below the sign-off gives the two cases as separate rows: fast PASS / slow FAIL and fast FAIL / slow PASS, each with its Cossart value, both NARROWED. · yes, table1.png and gh.html.
2. **Outcome table, Cossart column** · "Doesn't apply" is written three ways: a blank cell in the mixed row, "—" in the FAIL/FAIL row, and a Cossart value that is never stated for the mixed row. A reader can't tell a blank meaning "doesn't apply" from a cell someone forgot to fill. · minor · Use "—" everywhere, or "either" where Cossart really doesn't matter. · yes, table1.png.
3. **Outcome section: the per-stream rule against the outcome table** · The paragraph above the table gives each stream three possible results: PASS, VOID and FAIL. The table has no VOID row, so a run where either stream is VOID has nowhere to land. This is missing from the page itself, not a rendering problem. Whether VOID needs its own overall outcome is a logic reviewer's call; I'm flagging only that the table is missing it. · major · Amendment adds a VOID row saying the instrument is fixed and rerun, and nothing is read from that stream. · yes, compared the source with the render.
4. **Displacements table, *J* column** · At 880 px, "5.0 s" and "5.6 s" break before the unit, leaving "s" alone on the next line. · minor (wording fix, allowed above the line only if treated as a typo) · Use non-breaking spaces (`5.0&nbsp;s`), or write "1.6, 2.5, 5.0 s". · yes, table0.png.
5. **Sign-off table** · The header row `| | |` is empty, so a blank shaded bar shows above the table in the GitHub-style render. · minor · Give it headers such as `| field | value |`. · yes, table2.png.
6. **Banner and the Sign-off section** · The banner says "Everything above the sign-off line is frozen", and the closing italic says "Nothing above this line changes". But the page has four identical horizontal rules and none of them is marked as the sign-off line, and the italic sentence is not itself a visible line. What is frozen is clear from the context; the page never draws the line it refers to. · minor · In an amendment, state that the freeze boundary is the italic sentence directly below the sign-off table. · yes, gh_full.png.
7. **Banner, second paragraph** · There is no blank line between "**Goal:** …" and "**Why this page exists.**", so GitHub runs them together as one paragraph (banner.png). · minor · Put a `>` blank line between them. This is a formatting change, so it is allowed above the line. · yes, banner.png.
8. **"What each outcome commits to next." list** · There is no blank line between the bold paragraph and the list. GitHub renders it as a list. Python-Markdown and other strict editors render literal "- **VIABLE / NARROWED:**" text inside one paragraph. The brief lists editors as a render target. · minor · Add a blank line after the bold paragraph. · yes, local.html lines 175–179 against gh.html.
9. **Link check coverage (about the run, not the page)** · The requested `tests/test_index_resolves.py` passes, but it only checks `docs/INDEX.md`. On its own, "link test green" would be a clean result for a check that never looked at this page. The page's 6 links were verified separately (6 of 6 work in both the worktree and `origin/main`). · minor (run record) · The run record should cite the link check that was actually done, not the pytest pass. · yes.
10. **Names the page cites (outside my core scope, cheap to check)** · Every code name the page cites exists in the worktree: `surrogate_discriminator.forced_choice` (src/bugarach/surrogate_discriminator.py:377), `surrogate_stats.destruction` (src/bugarach/surrogate_stats.py:1198), `mouse_bootstrap` (tools/measure_recording_identity.py:189), `edge_thinning` (src/bugarach/surrogates.py:813). No finding. · — · — · yes.
11. **Page reachability on `main`** · The only link to this page is from `docs/goals/unsupervised-learning.md` on the branch. It isn't linked from `origin/main` or `docs/INDEX.md`. That is expected before PR #575 merges; whether to add an index row is another role's call. · note · — · yes, `git show origin/main:docs/goals/unsupervised-learning.md` does not contain it.

Files checked: `docs/proposals/2026-09-14-preregistration-is-rigid-shift-usable.md` and `tests/test_index_resolves.py`.
