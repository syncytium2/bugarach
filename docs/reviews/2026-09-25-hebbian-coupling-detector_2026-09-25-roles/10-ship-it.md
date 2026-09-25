GRANT 10 ok — Read, Grep, Glob, Bash (plus SubagentHandback, which only delivers this report; I hold no editing tool)

**Role 10, Build & craft gate: round 1.** The document itself renders cleanly. One blocking defect sits outside it: the new INDEX.md row would turn the test suite red. There are also two low-severity rendering inconsistencies.

**How it was rendered.** The GitHub `/markdown` API refused the request (403, the session is bound to its repository), and neither `gh` nor the Python `markdown` package is installed. So I installed `cmarkgfm` into the scratchpad. It is a wrapper around cmark-gfm, the library GitHub's own renderer is built on. I rendered the file to HTML at `<scratchpad>`, then took screenshots with Playwright chromium, `page0.png` … `page4.png` in the same folder, and looked at all five. This is not github.com's own rendering: fonts and CSS are approximate, but parsing is the same library.

| # | Unit (section / line) | Render checked against | Check | Result |
|---|---|---|---|---|
| 1 | Whole file | git log, file dates | Build is current | PASS. The artifact is committed at HEAD `b190f02` on `claude/hebbian-learning-detector-no4cmw`, with no uncommitted edits. Its inputs (`graph.py`, `assess.py`, `decisions_pending.md`, the assembly todo) date from 2026-09-24, before it. INDEX.md and the goal page are newer, but they link to it rather than feed into it. |
| 2 | Title, L1 | page0 | Heading hierarchy | PASS. One h1, then eight h2 headings in order, no skipped levels (checked in the HTML). |
| 3 | Status box, L3–11 | page0 | Blockquote banner | PASS. One grey quote box of two paragraphs; the bold "Status: DRAFT…" line renders; the `>` blank line correctly separates the paragraphs. |
| 4 | Abbreviations, L13–18 | page0 | Bold-italic symbols with Unicode subscripts | PASS. ***W***, ***s*₀**, ***D*** = *W* − *s*₀, ***w*** and ***q*₀** all render bold italic with correct subscripts, and no stray `*` is left over. |
| 5 | L4 link `../goals/unsupervised-learning.md` | page0 + file check | Relative link resolves | PASS. |
| 6 | L37 DOI link | curl | External link | PASS. Returns 302 to the Springer page. |
| 7 | Equation 8, L47–49 | page1 | Subscripts, `_` inside italics | **LOW.** `*s*_d` does not break the markup, but the underscore shows literally as "s_d", three times. The same paragraph shows s₀ as a true subscript, so the two notations sit side by side inconsistently. |
| 8 | "Pairs" bullet, L63; readout 3, L108 | page1, page2 | `*W*_ij`, `*q*(*W*_ij)`, `*D*_ij` | **LOW.** Same defect: renders literally as "W_ij", "W_ji", "q(W_ij)", "D_ij". There is no runaway italics: every `_` sits right after a closing `*`, so it can only open emphasis, never close it. That is fragile, though. A later edit that puts a `_` before a space in the same paragraph could italicise everything in between. |
| 9 | Other italics (Δ*t*, *w*/2, 2*w*, cos(π Δ*t* / *w*), *A*(*t*), *E*(*t*), −*K* … *K*) | page1, page2 | Italic markup | PASS. All close correctly. A scan of the rendered text, code spans excluded, found no leftover `*`, and the only `_` left are the ones in rows 7 and 8. |
| 10 | Code spans, L38, L100–101, L144, L163–169 | page0, page2, page3 | Inline code | PASS. All render; spans that wrap across lines are fine. |
| 11 | L106 link `../todo/2026-08-20-what-could-still-overturn-the-assembly-negative.md` | page2 + file check | Relative link resolves | PASS. |
| 12 | Anchors | the HTML | `#` anchor links | Not applicable. The file contains no anchor links. |
| 13 | Readouts 1–3, L99–110 | page2 | Numbered list | PASS. |
| 14 | "quiet → busy", L113 | page2 | Glyph | LOW, cosmetic, not checkable against GitHub. The arrow drew smaller than the text in my Helvetica render (font fallback). Whether it does on GitHub depends on its font stack; not confirmed. |
| 15 | Stages, L141–151 | page3 | List numbered from 0 | PASS. Renders 0, 1, 2, 3 as written. |
| 16 | Whole file | the HTML | Leftover markup | PASS apart from rows 7 and 8. No stray `**`, no unclosed backticks, no tabs, no trailing spaces. |
| 17 | Named repo paths (`graph.sttc_matrix`, `assess.circular_shift_trains`, `tools/assembly_power.py`, `docs/session_protocol.md`, `tools/check_vendor_freshness.sh`, `decisions_pending.md`, ADR-0007) | Grep / ls | Do they exist? | PASS. All exist. The jitter values 0.106 s and 0.135 s appear at `docs/decisions_pending.md:81–82`. Existence only; whether they are the right numbers belongs to other roles. |
| 18 | `docs/INDEX.md:117` (new row) | Re-ran the logic of `tests/test_index_resolves.py` (pytest is not installed) | Index pointers resolve | **FAIL, BLOCKING.** The code span `` `clamor/malsburg1986.py` `` fits the test's file-name pattern (it ends in `.py`). The test looks for that path in this repo and does not find it: the file is in the private `syncytium2/clamor` repo. It is the only unresolved pointer in the whole index, so `test_every_index_pointer_resolves[span-clamor/malsburg1986.py]` goes red and the PR cannot merge green. |
| 19 | `docs/goals/unsupervised-learning.md:49–53` (new bullet) | file check | Link resolves | PASS. `../proposals/2026-09-25-hebbian-coupling-detector.md` resolves. |
| 20 | `python3 tools/sapper.py --all` | command output | Sapper hits on the artifact, INDEX:117, goal page 49–53 | PASS. Exit code 0 and no hits on any of these lines. The warnings in INDEX.md (lines 58, 64, 74, 97, 130, 158, 186) and on the goal page (line 182) were already there and are outside this change. |
| 21 | `python3 tools/check_quotes.py --all` | command output | Private-correspondence gate | PASS. Output "check_quotes: clear", exit code 0. |
| 22 | Figures, axes, colours, legends, panels | — | Figure checks | Not applicable. The artifact has no figures or images. |

**Findings (location · issue · severity · suggested fix · verified against a source?)**

1. **`docs/INDEX.md:117`** · The code span `` `clamor/malsburg1986.py` `` points at a file that is not in this repo, so the index test goes red. · **BLOCKING** · Take the path out of backticks, e.g. "clamor's malsburg1986.py", or write it as `` `syncytium2/clamor:clamor/malsburg1986.py` ``: the `:` stops the test from treating it as a file name. Do not add it to the test's exemption list; that list is for files that are owed but not yet written. · **Yes.** I re-ran the test's own pattern and resolution logic against the file: `[('span', 'clamor/malsburg1986.py')]`.
2. **Artifact L47–49 and L63, L108** · The `_d` / `_ij` / `_ji` subscripts show as literal underscores, beside true Unicode subscripts (s₀, q₀) in the same paragraphs. · LOW · Use `*s*<sub>d</sub>`, `*W*<sub>ij</sub>`, `*D*<sub>ij</sub>` (GitHub allows `<sub>`), or ᵢⱼ if the font covers them. There is no Unicode subscript d. This also removes the fragile-italics risk in row 8. · **Yes** (cmark-gfm render, page1 and page2).
3. **Artifact L113, "→"** · The arrow may draw from a fallback font. · LOW / cosmetic · Optional: write "quiet-to-busy". · **No.** Seen only in my approximate render, not on github.com.

**Boundary notes.** Whether the prose defines every symbol before using it (*s*_d, *K*, *E*(*t*), *A*(*t*) are not in the abbreviations line) is a judgment call for the prose roles. I only checked that those symbols render. The GitHub API route was unavailable, so render fidelity is cmark-gfm's, not github.com's.

Files:
- docs/proposals/2026-09-25-hebbian-coupling-detector.md
- docs/INDEX.md (line 117)
- tests/test_index_resolves.py
- <scratchpad> page0.png–page4.png
