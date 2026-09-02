# Murderboard run — the case report to short-course, and the milestones index

- upstream:  syncytium2/murderboard @ 564b944
- copy:      vendored @ 564b944
- freshness: current (exit 0) — **after** a false STALE that was the real finding; see below
- artifact:  `docs/exports/2026-08-31_case_report_to_short_course_retrieval.md` (adc3c5f → 9484ad6, renamed from `..._to_short_course.md`)
             `docs/MILESTONES.md` (818c2a2 → 7820b26)
             `tools/check_milestones.py` (1c4b8a7 → 5a38e36)
             `tests/test_milestones_resolve.py` (new, e91fa7c)
- roles:     11 of 11 run in round 1; **3 of 11 in the blind round — a deviation, recorded below**
- rounds:    1 blind verify round

---

## What this run was actually about

A document arguing that records decay into overconfidence was **itself** decaying into
overconfidence, in seven places, and could not see any of them.

The review's yield is not a list of typos. It is a **rate**. Seven instances of one failure —
a claim written one confidence level above what the tree supports — inside about thirty hours,
each caught only by a check outside the author, none by the author:

| # | instance | caught by |
|---|---|---|
| 1 | four documents called an open K "the decided K" | the subject of the report |
| 2 | the report's own claims: "a test fails if…" (nothing ran it); six of nine counts wrong | roles 1, 3, 5, 6, 7, 10 |
| 3 | the proposed cure: a rule that **fired backwards**, passing the real decay wording and failing the honest hedge | roles 4, 6 |
| 4 | a critique of the recipient's course, written from a **six-day-stale** copy of material that already contained the finding | role 2 |
| 5 | "13 rules" from `grep`, where `--selftest` says 12 | roles 1, 3 |
| 6 | corrected draft copied a daily-commit series from a reviewer instead of recomputing (3 wrong figures) | blind round |
| 7 | "published 29 August" for a page written 31 August 09:36 on an unmerged branch | blind round |

**Instance 5 reproduced inside the review.** Role 10 counted the same rules the same way and
returned the same wrong 13, while roles 1 and 3 asked the tool and got 12. The apparatus built
to catch the error committed it, from the same method, in the same afternoon. That is the
single most transferable result of this run.

## The freshness gate's false positive was the second-best result

`murderboard_freshness.sh --refresh` exited **1 — STALE**, vendored `f62acb3` against upstream
`564b944`. The skill treats that as a hard stop. It was correct to stop, and the diagnosis was
not staleness: the session was working from the **primary checkout, 14 commits behind
`origin/main`**, where #417 had already re-vendored to `564b944` the day before. Rebuilt in a
fresh worktree off `origin/main`; the gate then passed.

Had the review run in that checkout it would have used a superseded process and reported full
coverage. **The gate caught a stale reader, not a stale file** — a case worth adding upstream,
since the message currently names only the file.

## Deviations, stated rather than absorbed

- **The blind round ran 3 roles, not 11** (claims, adversarial, mechanical). The process says
  every role runs and that a dropped role must be distinguishable from a clean one. These three
  own the failure modes round 1 actually found. **The other eight did not re-run**, and two
  defects (instances 6 and 7) were found by this reduced round — so a full blind round would
  likely have found more.
- **One blind round, not iterate-to-clean.** Round 1's fixes were applied and verified; the
  round-2 findings were applied but have had no blind pass of their own.
- **No figures were rendered**, against `CLAUDE.md`'s standing rule. Role 9 ruled the report in
  violation and named three panels (commits/day, the decay timeline, distance-to-answer). The
  timeline is now an ASCII block in the artifact; the other two are not drawn. `docs/exports/`
  has never carried an image and no delivery path for one exists.

## Role ledger — round 1, all 11 run

| role | findings | headline |
|---|---|---|
| 1 · Prove It | 9 blocking/major | six of nine scale figures wrong; board row copied from another session's prose; commit-pin named a sha where four figures do not reproduce |
| 2 · DOI or Die | 2 blocking | **the recipient had already published the report's thesis**; the absence claim came from a six-day-stale outline. Cossart/DANDI attribution verified **clean** against the DANDI API — no repeat of the CICADA error |
| 3 · Cross-Examiner | 4 critical, 17 high | `tests/test_milestones_resolve.py` did not exist; the index's "same PR" rule contradicted its own checker; "corpus" is a retired term used 8× |
| 4 · Reviewer 2 | 5 blocking | the cure fires on 1 of 5 decay paths and not the real one; the thesis is refuted by `INDEX.md` line 41, which *carried* the error; stale checkout never disclosed |
| 5 · Kill Your Darlings | 9 blockers | named the pattern: *"a claim written one confidence level above what the tree supports… diagnosed on page two and committed four times on page four"* |
| 6 · RTFM | 4 blocking | the flagship rule fires backwards, proven with a six-row table; strength vocabulary unenforced; primary source mis-cited (`import_dandi.py` never opens the NWB) |
| 7 · Reinventing the Wheel | 1 critical, 4 high | the checker is a lossier re-derivation of `tests/test_index_resolves.py`; resolving against `origin/main` breaks in a shallow CI clone |
| 8 · You Lost Me | 6 blocking sections | `K` never defined in the section built on K; the decay asserted rather than shown; the report never says what bugarach is |
| 9 · Show, Don't Tell | 3 high | ruled the report in violation of the repo's own figure-first rule; reconstructing the timeline **caught a factual error the prose carried** ("four days ago" → same morning) |
| 10 · Ship It | 3 high, 14 total | ran the suite (1,660/48 — confirming a figure role 1 called unsourced); **repeated the 13-rule error by grepping** |
| 11 · Start With the Problem | 4 high | 35 lines of framing before the first counted fact; the strongest evidence sat at position 7 |

## Role ledger — blind round, 3 of 11

| role | findings |
|---|---|
| Prove It (blind) | 2 blocking: "published 29 August" false; the specimen's first hop attributed to a commit that said the **opposite** (`31b2a2e` read *"A human has to choose K"*) |
| Reviewer 2 (blind) | pending at hand-off |
| Ship It (blind) | 4 high: daily series wrong in three ways and inconsistent with the report's own total; MILESTONES referenced by nothing |

## Residual ⚠ — not resolved

1. **The report has not been delivered.** No darkroom copy. `CLAUDE.md`: *"a report counts as
   output, and 'in the repo' is not delivered."* Held deliberately pending Tony.
2. **`MILESTONES.md` is referenced by nothing** — not `INDEX.md`, `CLAUDE.md`, or the briefing.
   `tests/test_index_resolves.py::test_the_index_is_announced` exists for exactly this defect
   and has no counterpart here. A findability document nothing can find.
3. **"K=12 by per-slice argmax" does not reproduce** from `assessment_cossart.json` — the blind
   claims pass computed per-slice argmax median/mode as **16**. The claim originates in
   `80b8db6`'s message; the JSON does not support it. This is the K=12 leg of the "two
   defensible peaks" the whole ⚠ `evidence` row rests on. **Softened in the row, not resolved.**
4. **"No coordination ground truth" is still unchecked**, two reviews later. It traces to an
   extractor that reads three groups of each NWB and stops. Settling it needs the DANDI files.
5. **`rows()` skips the 3-column Open table** and does not say so — a smaller instance of the
   coverage-without-disclosure bug this checker was rewritten to remove.
6. **Blind round incomplete**; round-2 fixes unreviewed.
