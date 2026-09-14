GRANT 7 ok — Read, Grep, Glob, Bash

# Reuse audit, round 1: the greatest-of origin change (7 findings)

Two findings are major. §4 still says every radar quotation is "matched mechanically", but the repo's own checker traces only 2 of the 4 new quotes. And four files the change didn't touch still name Hansen 1973 as the origin, one of them an open todo telling future sessions to cite it. No code in `src/` makes an origin claim, so part (c) is clean for code.

## (a) The existing quotation tool

`tools/verify_quotes.py` already does this job. Its docstring calls it a provisional reporting aid and not a gate, and says a miss on a two-column scan means "check by hand", not "wrong". I ran it on the worktree's `docs/detector_history.md` against `<darkroom>/bugarach/lit/radar` and `lit/coordination`. Overall it traced 15 of 57 quotations. For the four new quotations:

| new quotation | tool result | by hand (`pdftotext -layout`) |
|---|---|---|
| *"Constant-false-alarm-rate processing in search radars"* | ok (found in gandhi_kassam_1988) | genuine; also in the contents listing |
| *"a simple rule for determining the detectability loss…"* | MISS | genuine: Hansen & Sawyers 1980, section 1, right-hand column, split by the hyphen in "proces-/sor" |
| *"'Conventional' and 'Split' mean level threshold detectors"* | ok (found in hansen_sawyers_1980) | genuine: reference [2], "Internal memo. Hughes Aircraft Co., Feb. 15, 1972" |
| *"Hansen [9] has proposed a CFAR procedure…"* | MISS | genuine: Gandhi & Kassam 1988, pdftotext line 95; its reference list gives "pp. 325-332" |

## Findings

| # | location | issue | severity | suggested fix | verifiable against a source |
|---|---|---|---|---|---|
| 1 | `docs/detector_history.md:476`, *"Every radar quotation in this document is matched mechanically against a PDF on that shelf."* This line is unchanged, but it sits directly above the new passage. | The claim is false, and the change makes it more false. The tool misses 2 of the 4 new radar quotations. It also misses older ones: *"eliminating the maximum amplitude(s)…"*, *"superior to that of the CA CFAR"*, *"Although the false alarm rate performance of the GO-CFAR…"*, *"in general better overall performance…"*, *"proportional to the square root…"*. Your checks were done by hand with pdftotext, as `verify_quotes.py` itself recommends. The document never says so. It claims a mechanical match that the tool calls unreliable, and `docs/todo/2026-08-22-quote-verification-is-not-a-gate-yet.md` is still open. | major | Reword line 476 to the method actually used, e.g. "every radar quotation was checked by hand against `pdftotext -layout`; `tools/verify_quotes.py` traces some of them automatically and is not yet a gate." Link that open todo. Don't add the new quotes under a claim they fail. | yes (tool run plus pdftotext) |
| 2 | Tree-wide, outside the three reviewed files: `docs/todo/2026-08-24-the-methods-are-not-ours-and-the-app-says-otherwise.md:97` (status open); `docs/proposals/2026-09-10-coordination-without-labels.html:848`; `docs/learned/detector_history.html:243`; `docs/learned/cfar_scope.html:345,382` | These still claim an origin that the change now calls not established. The open todo's "must cite" table lists `maxlt is GO-CFAR 1973` / `Hansen 1973`. It is an instruction to future sessions and will bring the retracted claim back. The public proposal footer credits the family to "Hansen 1973". The rendered `detector_history.html` still says "GO-CFAR (Hansen 1973)"; the closed todo already notes this render is stale. `cfar_scope.html` lists Hansen & Sawyers 1980 as greatest-of's source and says "every primary behind it is on the shelf and read". The closed Hansen todo lists only GLOSSARY, README and detector_history as fixed. CLAUDE.md says to grep the tree for the same pattern before closing, and that step wasn't done. | major | In the same change, fix the open todo's row: `maxlt` is GO-CFAR, origin not established, see §4. File the proposal footer, `cfar_scope.html` and the stale render as follow-ups, or fix them. Say in the closed todo which copies remain. | yes |
| 3 | `src/` (part c) | No finding. `loco.py:1-21` describes `maxlt` only by how it works ("MAX of the trailing and leading half-context thresholds"). `rate.py:190-279` and `bench.py:427-428` cite only Finn & Johnson and Rohling. `tools/` has no citation of Hansen or greatest-of. | none | none | yes |
| 4 | `docs/detector_history.md` §4, new passage lines ~483–518, compared with `docs/lit_needed.md:108-145` (Gregers Hansen entry) | The same evidence now lives in two places. The four bullets, the memo date, the page range, the Rohling note and the list of routes tried (Xplore, "no other route") repeat the evidence table and the "routes that were exhausted" block in lit_needed. They have already drifted apart. lit_needed notes that Gandhi & Kassam's reference says IEEE where the volume says IEE, and names OpenAlex; the passage drops both. §4 never links lit_needed at all. The outside-reader summary does belong in §4, but the search record belongs in one place. | minor | Keep the four bullets in §4 as the version readers see. Change "no other route produced text" to link `lit_needed.md`'s Gregers Hansen entry for the full search. Shrink lit_needed's table to a pointer at §4, or mark §4 as the authority, so the quotes exist once. | yes |
| 5 | `docs/todo/2026-09-10-nobody-has-read-hansen-1973.md:15-16` (changed in this worktree, not in the reviewed patch), *"the four shelf papers that bear on the question"* | This summary already disagrees with the passage it summarises. The passage cites three shelf papers (1980, Gandhi & Kassam, Rohling) plus the contents listing, and the memo is not on the shelf. This is the drift finding 4 predicts. | minor | Say "three shelf papers and the contents listing", or just link the section instead of summarising it. | yes |
| 6 | `<darkroom>/bugarach/lit/radar/README.md`, compared with `detector_history.md:473-474` (*"with a read-status entry each"*) | The shelf's own read-status README has no entry for `iee_conf_105_1973_CONTENTS_ONLY.pdf` or `gregers_hansen_AUTHOR_PROFILE_ieee.pdf`, and grep finds no mention of 1973 or Gregers. The passage relies on both files ("the volume's contents listing confirms…", and the 1971/1972 titles come from the author profile). The shelf's existing record of what it holds wasn't updated. | minor | Add two read-status entries: "contents listing only, not the paper" and "IEEE author record". | yes |
| 7 | `docs/detector_history.md:514-516`, the Hansen & Zottl 1971 and Hansen & Ward 1972 papers, "neither is on the shelf" | These are named as open questions, but they aren't in `docs/lit_needed.md`, which is the repo's list of papers to get (grep for Zottl, Dicke-Fix or LOG/CFAR finds only §4 and the closed todo). A gap listed only in prose won't be picked up by whoever works through that list. | minor | Add both to `lit_needed.md` as asks, or mark them there as deliberately not pursued under Tony's 2026-09-14 ruling, and link from §4. | yes |

Outside my role: the worktree branch is behind origin/main. `git diff origin/main --stat` lists 19 files, including murderboard tooling and deleted figure tools that aren't part of this change. The patch you gave me covers only the three documentation files. Whoever assembles the final record should check the diff base.

Files referenced:
- `<worktree>\docs\detector_history.md`
- `<worktree>\tools\verify_quotes.py`
- `<worktree>\docs\lit_needed.md`
- `<worktree>\docs\todo\2026-09-10-nobody-has-read-hansen-1973.md`
- `<worktree>\docs\todo\2026-08-24-the-methods-are-not-ours-and-the-app-says-otherwise.md`
- `<worktree>\docs\todo\2026-08-22-quote-verification-is-not-a-gate-yet.md`
- `<worktree>\docs\proposals\2026-09-10-coordination-without-labels.html`
- `<worktree>\docs\learned\cfar_scope.html`
- `<worktree>\docs\learned\detector_history.html`
- `<worktree>\src\bugarach\detectors\loco.py`
- `<darkroom>\bugarach\lit\radar\README.md`
