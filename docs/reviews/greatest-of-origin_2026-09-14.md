# Murderboard run — where greatest-of began, and what we could not find

## The problem

`detector_history.md` §4, `GLOSSARY.md` and `README.md` credited LoCo's `maxlt` rule, greatest-of CFAR
selection, to a 1973 IEE conference paper by V. Gregers Hansen. Nobody on this project had read that paper,
and on 2026-09-14 Tony reported that it resolves only to a conference listing. His brief was: *"let's not
replace origin, but discuss our attempt to find it. state what we know, what we don't know. and leave it at
that."*

The deliverable is the change that does that: a new `detector_history.md` §4.1, *Where greatest-of began*,
plus the §4 table row, flags in the 2026-08-24 revision note and §7, and the matching sentences in
`GLOSSARY.md`, `README.md`, `docs/learned/cfar_scope.html`, the withdrawn 2026-09-10 proposal's footer and
`docs/INDEX.md`. The rebuilt `docs/learned/detector_history.html` ships with it.

## What the review changed

The first draft replaced one weak claim with several new ones. Across three blind rounds the reviewers found:

- **The draft misreported the sources it quoted.** Rohling 1983 credits *Moore et al.* with proposing
  greatest-of and Hansen & Sawyers with investigating it; the draft said Rohling credited both. "The work
  usually credited" had no support: only Gandhi & Kassam 1988 credits the 1973 paper.
- **It left out evidence already on the shelf.** Hansen & Sawyers' acknowledgment calls their results
  *"independent work performed by the two authors"*. A 1982 NEC patent (US 4,318,101) describes the 1973
  paper's content and reproduces its Weibull-clutter processor. HathiTrust holds two search-only scans that
  may contain the volume, and its catalogue gives a different ISBN from the IEE notice.
- **Its inferences leaned toward an answer the brief forbids, in both directions.** "The memo predates the
  conference by twenty months", "the earliest dated treatment", "his 'proposed' cannot mean first" and "the
  patent does not mention greatest-of" each implied a priority or a non-origin. The shipped text reports
  what each source says and puts every inference into *What we do not know*.
- **The rest of the document contradicted it.** "All four primaries are held and read", "closed every
  lineage row", a §7 item marked done, a stale HTML copy, `cfar_scope.html` and the proposal footer all
  still asserted the old origin. The draft's own §7 flag also got the chronology wrong: on 2026-08-22 the
  attribution under check *was* Hansen & Sawyers 1980, and the 1973 credit arrived with the 2026-08-24 audit
  (confirmed with `git log -S`).

What generalizes: **a correction is a new claim, and it attracts the same defects as the claim it
corrects.** Here the correction first reproduced an unread-source attribution ("usually credited"), then a
priority argument from dates, then a softened account of how the error got in ("the audit identified the
mechanism, not where it began"; the audit had named 1973 as the origin).

## Convergence

| round | blocking | major | minor | notes |
|---|---|---|---|---|
| 1 | 0 | 52 | 85 | role 8's per-unit verdict table marked 4 units blocking |
| 2 (blind) | 0 | 40 | 103 | role 8's verdict table marked 5 units blocking |
| 3 (blind) | 5 | 31 | 92 | role 8 moved its literal "3+ undefined terms" rule into the finding list, so the 5 are the same kind of verdict as rounds 1–2, not new defect classes |

Counts are tallied by hand from the preserved reports. Several findings are shared across roles and are
counted once per role.

**Stopping reason: round cap reached (3 blind rounds). The run is unconverged.** Majors fell 52 → 40 → 31, so
severity was falling rather than flat, but no round reached the floor.

**Edits after round 3, not re-reviewed.** After the cap, the confirmed factual errors and the inference
sentences that round 3 showed implying an answer were fixed:
- the §7 item 2 chronology;
- the 2026-08-24 note's account of what the audit named;
- "cannot mean first", "earliest dated treatment", and "our only source for the pages";
- "Nothing above depends on the answer", scoped to the mechanism match;
- the patent bullet, now "estimates Weibull parameters from averages of the log amplitudes … does not
  discuss greatest-of either way";
- the "held?" cell;
- the GLOSSARY paragraph, which now names the withdrawn attribution;
- the README bullet, reordered so the caveat precedes the citation and the retired citation removed;
- the `cfar_scope.html` caption shortened.

These are cuts and corrections toward what the sources literally say, but **no reviewer has read them.**

This review found and fixed many defects. It is not a correctness proof. The convergence table measures how
quickly reviewers stopped finding things, not whether anything remains.

## Residual ⚠ — not done, and why

- ⚠ **§4.1 is long for "leave it at that"** (roles 5 and 9, majors in round 3). Role 9 proposes a
  source × claim table with quotations collapsed underneath; role 5 proposes cutting to about 300 words. Not
  done after the cap, because a restructure is a new draft that nobody would review.
- ⚠ **The darkroom copy of `detector_history.html` is stale** and still credits Hansen 1973. The repo copy
  was rebuilt, but the darkroom is a shared resource that needs a claim on `docs/SESSIONS.md` first.
  Filed in [the follow-ups](../todo/2026-09-14-greatest-of-follow-ups.md).
- ⚠ **`tools/md_to_page.py` breaks §7's numbered list** (3-space continuations), so the §7 item 2 flag
  renders outside its item on the HTML page. GitHub renders it correctly. This was broken before this change.
  Filed.
- ⚠ **Adjacent attributions have not been held to this standard.** Finn & Johnson 1968 as the origin of
  cell-averaging is contradicted by nothing yet, but Gandhi & Kassam's reference list includes Steenson,
  July 1968, on mean-level thresholds. §7 item 4 may misstate Rohling as holding LoCo's hybrid, and
  `cfar_scope.html` names a detector "CICADA". All filed.
- ⚠ **Nobody was asked.** No correspondence with the IET archives, V. Gregers Hansen, or anyone connected to
  the 1972 memo is recorded. This is a question for Tony and is filed.
- ⚠ **Unsearched routes:** the two HathiTrust search-only scans (records 001618382 and 011456921), a library
  request, radar handbooks, patents from before 1973, and the Japanese Weibull-clutter literature citing the
  1973 paper. Filed.

## Appendix — run header and role ledger

- upstream:  syncytium2/murderboard @ 08f5ddb
- copy:      vendored @ 08f5ddb (re-vendored from 81a0927 in #558 after the freshness gate stopped this run at step 1)
- freshness: current
- artifact:  docs/detector_history.md (5b38d81 -> 6910def), README.md (983d008 -> 7bc4f7f), docs/GLOSSARY.md (cd819fa -> 8f6beec), docs/learned/cfar_scope.html (origin/main 079657d -> b82e143); also docs/learned/detector_history.html (rebuilt), docs/proposals/2026-09-10-coordination-without-labels.html, docs/INDEX.md
- roles:     11 of 11 run (named agents), in each of 3 rounds
- rounds:    3 blind verify rounds; round cap reached, unconverged

Mode: standard

reports: greatest-of-origin-2026-09-14-reports/

**Run notes, not about the artifact:**
- **Reports.** Round 1 is at the top of `reports:`; rounds 2 and 3 are in `round2/` and `round3/`.
- **How the reports were preserved.** The harness's per-agent output files were **0 bytes** (checked). Each
  report was transcribed from the completion notification.
- **Changes to the transcriptions:**
  - HTML entities (`&amp;`, `&lt;`, `&gt;`) were decoded.
  - Machine-local paths were replaced with `<darkroom>`, `<scratchpad>`, `<worktree>`, `<repo>` and `<home>`.
  - The institution name in paths and text was replaced with "[a US university library]" or "[the library]",
    because sapper SAP004 blocks it from this public repo.
  - The first write of round-1 role 9 was paraphrased by mistake and was overwritten with the verbatim text.
  - In two round-3 lines, straight double quotes around a phrase were changed to italics, with the words
    unchanged: role 1's F8 and role 2's finding 12. `tools/check_quotes.py` read those lines as quoted private
    correspondence. They quote this repo's own text, so the check was not edited.
- **Blind-pass breaches.** In round 3, role 3's tree-wide grep surfaced a few lines of `docs/lit_needed.md`,
  and role 7's grep surfaced one line of a round-2 report. Both said so, and neither file was opened.
- **Worktree write.** In round 1, role 10 wrote and deleted a temporary file inside the worktree in one
  command, and reported it.
- **Base.** The round-1 diff was cut against an `origin/main` the branch had fallen behind. It was merged up
  before round 2.

| # | role | GRANT (verbatim, each round) | round 1 | round 2 | round 3 |
|---|---|---|---|---|---|
| 1 | Prove It | GRANT 1 ok — Read, Grep, Glob, Bash | 6 major, 8 minor; claim ledger of 23 rows | 2 major, 8 minor; ledger of 23 rows | 2 major, 7 minor; ledger of 33 rows |
| 2 | DOI or Die | GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch | 5 major, 5 minor; found the NEC patent, the acknowledgment, and Rohling's proposer | 3 major, 7 minor; found the HathiTrust scan and the ISBN conflict | 3 major, 9 minor; found the CiNii/OpenAlex page records and the Steenson 1968 lead |
| 3 | Cross-Examiner | GRANT 3 ok — Read, Grep, Glob | 9 major, 8 minor | 4 major, 19 minor | 2 major, 13 minor; caught the §7 chronology error |
| 4 | Reviewer 2 | GRANT 4 ok — Read, Grep, Glob, Bash | 8 major, 7 minor | 7 major, 9 minor; caught what the patent describes | 6 major, 11 minor |
| 5 | Kill Your Darlings | GRANT 5 ok — Read, Grep, Glob | 4 major, 14 minor; construction search pasted | 4 major, 14 minor; 0 construction hits | 4 major, 11 minor; 1 construction hit |
| 6 | RTFM | GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch | 3 major, 7 minor; `maxlt` calibration | 1 major, 3 minor; CAGO vs GO over percentile halves | 0 major, 6 minor |
| 7 | Reinventing the Wheel | GRANT 7 ok — Read, Grep, Glob, Bash | 2 major, 4 minor; tree-wide stale copies | 2 major, 4 minor; darkroom copy | 1 major, 6 minor; no uncorrected copy left in the repo |
| 8 | You Lost Me | GRANT 8 ok — Read, Grep, Glob | 10 major, 12 minor; 4 units blocking in the verdict table | 9 major, 20 minor; 5 units blocking | 5 blocking, 7 major, 10 minor |
| 9 | Show, Don't Tell | GRANT 9 ok — Read, Grep, Glob, Bash | 1 major, 7 minor; count table | 1 major, 5 minor; rendered `cfar_scope.html` | 1 major, 6 minor; rendered at 1440/1024/390 px |
| 10 | Ship It | GRANT 10 ok — Read, Grep, Glob, Bash | 1 major, 8 minor; gh renders, page builds, gates | 3 major, 3 minor; Playwright at 1280/400 px | 2 major, 4 minor; §7 list broken in built HTML |
| 11 | Start With the Problem | GRANT 11 ok — Read, Grep, Glob | 3 major, 5 minor; spine | 4 major, 11 minor; spine | 3 major, 9 minor; spine |
