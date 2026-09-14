GRANT 10 ok — Read, Grep, Glob, Bash

**What I rendered with, and how:**
- **GitHub's renderer:** `gh api markdown`, in both `mode=markdown` (the mode github.com uses for files in a repo) and `mode=gfm`. I rendered `origin/main`'s `detector_history.md` too, as a structural baseline.
- **The project's page builder:** I built `detector_history.md` to scratch twice with `tools/md_to_page.py`, once from this branch and once from `origin/main`.
- **Screenshots:** Playwright chromium, 1280 px viewport. I wrapped the GitHub HTML in approximate GitHub CSS, not GitHub's real stylesheet. I screenshotted the scratch page build as it comes.
- **Screenshots are in the scratchpad:** `gh_table.png`, `gh_bq.png`, `gh_passage.png`, `gh_readme.png`, `gh_gloss.png`, `page_table.png`, `page_passage.png`.

| Changed unit | Checked against | (a) Structure | (b) Nested quotes | (c) Links | (d) Gates | (e) Build current | Result |
|---|---|---|---|---|---|---|---|
| `detector_history.md:466`, §4 table row "LoCo, `maxlt`" | GitHub render (`gh_table.png`); page build (`page_table.png`, 658 px = 51% of the 1280 px viewport) | 5 cells, 5-column header. The render has 5 tables and 29 `<tr>` rows, the same as `origin/main`. Nothing runs off: scrollWidth equals clientWidth in both renders. | n/a | "see *Where greatest-of began* below" is plain text with no anchor (F7) | pass | HTML copy stale (F1) | pass, one minor |
| `detector_history.md:203–205`, flag inside the "Revised 2026-08-24" blockquote | GitHub render (`gh_bq.png`); block-tag sequence of the branch build compared with the `origin/main` build | All 3 inserted lines start with `> `. One blockquote, still 3 paragraphs, same as the baseline. The italic flag closes before `) and`. | ⚠ and the italic flag render correctly | n/a | pass | stale (F1) | pass, cosmetic (F6) |
| `detector_history.md:483–519`, new passage "Where greatest-of began, we could not establish" | GitHub render (`gh_passage.png`); page build (`page_passage.png`) | 4 paragraphs and 2 lists with 4 items each. This is the only structural difference between the two page builds. | `*"…'greatest of'…"*` renders correctly. `*"'Conventional' and 'Split'…"*` renders, but the `"'` pair is cramped (F5). `[9]` stays literal text, not a link. | no links | pass | stale (F1) | pass, minor |
| `GLOSSARY.md:262–264`, CFAR paragraph | GitHub render (`gh_gloss.png`) | Paragraph intact; the parenthesis closes before `, and its` | n/a | `detector_history.md` is resolved from `docs/`, and the file exists | pass | n/a | pass |
| `README.md:651–661`, citations bullet | GitHub render (`gh_readme.png`) | Still one `<li>` (2-space continuation); the next bullet starts cleanly | n/a | `docs/detector_history.md` exists | pass | n/a | pass, minor (F2–F4) |
| `docs/learned/detector_history.html` (not rebuilt) | `git log` of the HTML and the .md; scratch rebuilds compared with the committed HTML; darkroom copy (read-only) | — | — | — | — | **Stale, and already stale before this change** | F1 |
| Repo gates (whole tree, working copy) | `pytest -q` on `test_index_resolves`, `test_milestones_resolve`, `test_check_quotes`, `test_sapper`, `test_handoff_is_honest`, `test_locust_is_findable`; `sapper.py --all` and `--selftest`; `check_quotes.py --all` and `--selftest` | — | — | index and milestone links resolve | 256 tests passed; sapper: clear (13 rules, 0 selftest failures); check_quotes: clear (3 fixtures, 0 failures). `check_quotes` has no per-file mode; `--all` reads every tracked `.md` from the working copy, which covers the changed files. | — | pass |

**Answers to the questions you asked about the HTML copy:**
- **What builds it:** nothing automatic. It is built by hand with `tools/md_to_page.py`. That tool writes to the darkroom by default and takes `--also` for a repo copy.
- **Whether it is on the public site:** no. `build_site.py`'s `PAGES` lists only `index`, `viewer`, `diagnostic` and `learned_detector`. Nothing under `docs/site` refers to it, and `wrangler` serves the `./site` folder that `build_site.py` produces. The only page that cites the history, `cfar_scope.html`, cites the `.md`. The HTML is still a tracked file in a public repo.

## Findings

**F1 · `docs/learned/detector_history.html` · The HTML copy is stale, and was stale before this change.**
- **Before the change:** the HTML was last committed at `1f13973` (2026-08-29 17:01). The .md then gained 144 lines in `81cc134` (2026-08-31). Built to scratch, `origin/main`'s .md has 73 sentences the committed HTML lacks.
- **After the change:** 97 sentences added and 2 removed.
- **What a reader of the HTML sees:** "GO-CFAR (Hansen 1973)" with no flag, and the table crediting Hansen & Sawyers with no "not established".
- **Darkroom copy:** also stale, dated 2026-08-29 16:20.
- **Disclosure:** the todo `2026-09-10-nobody-has-read-hansen-1973.md` already mentions the staleness.
- **Severity:** major. It is not on the site, but it is a tracked copy that contradicts the correction.
- **Fix:** run `python tools/md_to_page.py docs/detector_history.md --also docs/learned`, then re-screenshot the rebuilt page. Alternatively, put a visible "stale, see the .md" banner on it.
- **Verifiable:** yes.

**F2 · `README.md:651–657` · The 1973 paper lost its ° marker.**
- The legend at `README.md:634` says ° marks a work "not read here". The change removed ° from Hansen V.G. (1973), which is still unread, so a reader using the legend would take it as read.
- **Severity:** minor. **Fix:** put the ° back in front of "Hansen V.G. (1973)". **Verifiable:** yes.

**F3 · `README.md:636` against `:655` · The legend and the bullet disagree about the shelf.**
- The legend says the shelf "holds only Finn & Johnson of the works below". The bullet says Hansen & Sawyers 1980 "**is** on this project's shelf".
- The contradiction was already there; this change restates it.
- **Severity:** minor. **Fix:** correct the legend sentence. **Verifiable:** yes.

**F4 · `README.md:657` against `detector_history.md:484` · The 1973 title is spelled two ways.**
- The README has "Constant false alarm rate processing". `detector_history.md`, `lit_needed.md` and the contents-listing quote all have "Constant-false-alarm-rate processing".
- **Severity:** minor. **Fix:** use the hyphenated form in the README. **Verifiable:** yes.

**F5 · `detector_history.md:497` · Cramped quote marks.**
- In `*"'Conventional' and 'Split'…"*` the opening double quote sits directly against a single quote, and the render shows it as a cramped `"'`. It is readable.
- **Severity:** minor (cosmetic). **Fix:** leave it, or drop the inner quotes if the memo title allows it. **Verifiable:** yes.

**F6 · `detector_history.md:204` · One long source line.**
- The inserted blockquote line is 117 characters, against roughly 85 in the lines around it. It renders fine.
- **Severity:** cosmetic. **Fix:** re-wrap, keeping `> ` at the start of each line. **Verifiable:** yes.

**F7 · `detector_history.md:466` · The table's pointer to the passage cannot be followed.**
- "see *Where greatest-of began* below" is not a link. Its target is a bold lead-in, not a heading, so it has no anchor. The italic label is also only the first half of the actual lead-in ("Where greatest-of began, we could not establish").
- **Severity:** minor. **Fix:** quote the full lead-in, or say "later in §4". **Verifiable:** yes.

**F8 · The run itself · The branch is 2 commits behind `origin/main`.**
- The merge base is `b1c8b2b`; `origin/main` is at `3092d8c`, which touches `docs/INDEX.md` among other files.
- As a result, `git diff origin/main --stat` lists unrelated changes in reverse (INDEX.md, `make_intro_figures.py` and others), and my gates ran on the branch tree, not the tree as it will be after merging.
- The worktree also has uncommitted edits outside the stated scope: `docs/lit_needed.md` and three todos. Only `sapper` and `check_quotes --all` covered those.
- **Severity:** minor. **Fix:** merge `main` and rerun `test_index_resolves` before landing. **Verifiable:** yes.

**F9 · The run itself · I briefly wrote a file into the worktree.**
- While preparing the baseline, one of my commands wrote a temporary file `docs_base_tmp_should_not_exist` into the worktree root and deleted it in the same command.
- `git status` straight afterwards showed no trace, and I made no other writes outside the scratchpad.
- Recorded because no reviewer may write to the artifact. **Severity:** minor. **Verifiable:** yes (`git status`).

A boundary note, not my finding: the blockquote flag still reads "GO-CFAR (Hansen 1973 — ⚠ …)" while the table says "not established". Whether that wording is acceptable is a judgment call for the content roles.
