# Murderboard run — the one-page methods section

**What was at stake.** Tony asked for the pipeline, from fast and slow onsets to calls with their
width and amplitude, condensed onto one page with references on a second, describing CoactDetect
and chorus only. A page that short cannot hedge in footnotes, so every sentence it keeps has to be
true of the code as it runs today. The first draft's numbers were right. Its descriptions were
not, in ways a reader could not have caught.

**What the review found, by kind.** Roughly 60 numbers were recomputed from the code and the run
records; all matched. The defects were in what the page said the numbers meant:

- **Four statements the code contradicts** (first draft, fixed). Fast and slow were said to differ
  only in width; they are different event sets. Calls were matched as points; they are matched as
  intervals. Width was said to be floored at one frame; only amplitude's divisor is. The event
  floor was said to gate every call; it gates CoactDetect, not chorus.
- **An attribution the repo does not support** (fixed). CoactDetect was called a cell-averaging
  CFAR test (Finn & Johnson, 1968). The repo records that it converged on CFAR independently; the
  page now says it resembles CFAR and excess-coincidence tests, reached independently.
- **Citations the page owed** (added): the whole-train shift (Pipa et al., 2007, 2008), the
  correlogram (Perkel et al., 1967), permutation-invariant pooling (Qi et al., 2017) and the
  shifted-null family (Amarasingham et al., 2012).
- **Terms that meant something else here**: "K", "participation floor" and "empty recording" are
  reserved in the glossary for other things, and "window" carried four meanings. Renamed.
- **Caveats about the method itself**, which the page now states and which are Tony's to decide:
  the floor is computed at 2 s but gates CoactDetect at whatever window the search picks; the
  lowest planted level falls under the floor and is never scored; the call measure over-counts
  participants on every stream, most on combined; whether the event time is the call's onset or
  the core's first onset is undecided; and the realistic bench lays its events end to end in one
  block rather than across the recording.

**What makes the page hold when the approach changes again.** Two mechanisms, both new:
`tests/test_methods_one_page_numbers.py` pins every quoted constant to the code that sets it (it
was shown to fail when a number on the page was changed), and `tools/build_methods_one_page.py`
refuses a build whose methods text leaves page 1. The second is not hypothetical: it refused two
builds during this review, where Chromium would have silently printed three pages.

**This review found and fixed the defects above. It is not a correctness proof.** The convergence
table below measures how quickly reviewers stopped finding things, not whether anything remains,
and it did not converge on major findings (next section).

## Convergence, and why the run stopped

| Round | Pass | Blocking | Major | Notes |
|---|---|---|---|---|
| 0 | all 11 roles, named agents, draft 1 | 10 | about 60, heavily overlapping across roles | role 4: 3 blocking; role 8: 7 panels blocking on undefined terms |
| 1 | blind, fresh reviewer walking all 11 checklists + role 10 render | 1 | 7 | the blocking row was a PDF 50 s older than its HTML; rebuild pixel-identical |
| 2 | blind, fresh reviewer walking all 11 checklists + role 10 render | 0 | 8 | render passed; four majors were statements the code contradicts |

**Stopping reason: severity did not fall across the two blind rounds** (majors 7 → 8), so per the
process the run stops and goes to the human rather than patching a third time. The round cap (3)
was not reached. Two signs that further rounds are reaching diminishing returns rather than
converging: round 1 asked for Pipa et al. 2007 in place of 2008 and round 2 asked for the
reverse (both are now cited), and each round's fixes lengthened a page with a fixed length, so
each round also reviewed text written to fit. Round 2's findings were all applied; they have not
themselves been reviewed.

**A follow-up pass driven by the finding list was not run**, because the run stopped at the
escalation point. It is the next step if Tony wants the run continued.

## Residual ⚠ — for Tony before this page is used

- ⚠ **Unconverged**: round 2's fixes are unreviewed (see above).
- ⚠ **The five method questions** in the "What the review found" list are decisions, not text.
- ⚠ **Type is 9.6 pt**, accepted for this draft only; the house minimum is now 11 pt (CLAUDE.md).
  At 11 pt the page does not fit without cutting about a quarter of its text.
- ⚠ **Page-1 headroom is 6 pt**; the build refuses a spill, so an edit cannot break the page
  silently.
- ⚠ **Unread sources**: the roots of the whole-train shift (Grün et al., 1999) and of CFAR
  (Finn's 1966–67 papers) were not read; Grün et al. 2002 is unread and not cited. Amarasingham
  et al. 2012 is marked read in `docs/lit_needed.md` but listed as unread in
  `docs/decisions_pending.md` item 7; the two records disagree.
- ⚠ **Fast's shipped CoactDetect is still binned**; the page describes the sliding form, which is
  what the search tunes, and says so in a parenthesis.
- ⚠ **Not on the page for space**: CoactDetect's null keeps the tested interval's own onsets when
  the guard is zero (unlike cell-averaging CFAR).
- ⚠ **Companion documents not updated**: `docs/GLOSSARY.md` has no entry for the combined stream
  and still gives superseded background rates and a 33-cell no-coordination recording; the
  fast-only methods draft of 2026-09-22 is marked superseded only in `docs/INDEX.md`.
- ⚠ **Not delivered to the darkroom**: this container has no darkroom mount; the build tool
  defaults there and wrote the repo copy only.
- ⚠ **Freshness UNDETERMINED**: upstream murderboard was unreachable from this container; the
  vendored process is stamped `08f5ddb`.
- ⚠ **Role 5's prose tool** (`murderboard_prose.sh`) is not vendored here; roles 5 ran the
  banned-construction search by hand, each round, with zero hits.
- ⚠ **Upstream murderboard bug**: `murderboard_roster.sh` strips every underscore from the
  `reports:` line, so the archive name the skill prescribes (`<artifact-stem>_<date>-roles`)
  can never resolve when the stem has an underscore. The archive here is named with hyphens
  instead. A report for upstream, not a local edit (the tool is vendored).
- ⚠ **The blind rounds ran as generic reviewers**, not the named role agents, and both declared
  holding editing tools beyond a reviewer's grant (neither used them). The named-agent grants
  below apply to round 0 only.

---

## Appendix — run header and role ledger

- upstream:  syncytium2/murderboard @ 08f5ddb (vendored stamp; upstream HEAD not reachable)
- copy:      vendored @ 08f5ddb
- freshness: UNDETERMINED
- artifact:  docs/methods/one_page/methods_one_page.pdf (e273fd40 -> rebuilt after the last fix; see git)
- roles:     11 of 11 run (named agents) in round 0; blind rounds 1–2 ran every role's checklist through a generic reviewer (inline fallback) plus the named role 10
- reports:   methods-one-page-2026-09-25-roles/
- rounds:    2 blind verify rounds; stopped for escalation (severity not falling), not clean

Mode: standard

Reports are verbatim, extracted from each agent's own hand-back, except that machine-local paths
are replaced by `<repo>`, `<scratch>` and `<primary-checkout>` (sapper SAP004 blocks them in a
public tree). Round 0 is in the folder's top level; blind rounds are in `round2/` and `round3/`
(named for the review round they belong to, counting the first review as round 1).

| Role | Grant declared (round 0) | Round 0 findings | Adjudication |
|---|---|---|---|
| 1 Prove It | GRANT 1 ok — Read, Grep, Glob, Bash | 3 major (stream definition, CFAR attribution, binned fast), 8 minor; ~60 quantities recomputed, all match | all fixed |
| 2 DOI or Die | GRANT 2 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch | 3 major (CFAR identity, uncited shift null, uncited correlogram), 5 minor; all 5 references verified | fixed; citations added |
| 3 Cross-Examiner | GRANT 3 ok — Read, Grep, Glob | 5 major (reserved K, participation floor, empty recording, window, event), 17 minor | fixed except glossary edits (residual) |
| 4 Reviewer 2 | GRANT 4 ok — Read, Grep, Glob, Bash | 3 blocking (amplitude, unvalidated measure, floor window), 12 major, 6 minor | fixed as caveats; method questions to Tony |
| 5 Kill Your Darlings | GRANT 5 ok — Read, Grep, Glob | 7 major (naming and placement), 21 minor; banned constructions: 0 hits | fixed |
| 6 RTFM | GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch | 8 major (CFAR, α as z, standardization span, decoys, span matching, part variant unscored, binned fast, block placement), 11 minor | fixed; scorer gap handed to WSMIP065 |
| 7 Reinventing the Wheel | GRANT 7 ok — Read, Grep, Glob, Bash | 7 major (duplicate methods doc, delivery, B1–B4, typed numbers, untraced cohort counts), 5 minor | fixed; numbers test and build tool added; darkroom delivery residual |
| 8 You Lost Me | GRANT 8 ok — Read, Grep, Glob | 7 blocking panels, 11 major, 6 minor | fixed |
| 9 Show, Don't Tell | GRANT 9 ok — Read, Grep, Glob, Bash | 0 blocking, 0 major, 4 minor (companion figure and table suggestions) | no change; prose right for the form requested |
| 10 Ship It | GRANT 10 ok — Read, Grep, Glob, Bash | 2 major (malformed run-in headings, no headroom), 4 minor | fixed; build tool added |
| 11 Start With the Problem | GRANT 11 ok — Read, Grep, Glob | 6 major (benchmark mis-filed, missing definition of coordinated event, parameter order, precision reference, seed vocabulary), 7 minor | fixed |
