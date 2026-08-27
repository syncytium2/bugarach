# Murderboard run — the guards that could not fail

## The review found a defect of the same kind the document is about

The draft said item 2 of the hook audit had been built *"hours before the page listing
it as open was written."* Role 1 checked the commit times instead of the sentence:

```
13b767f  2026-08-25 22:32  the hook audit, written down where the next session will find it
696cac3  2026-08-25 22:59  the handoff is honest now, and a test keeps it that way
```

The test landed **twenty-seven minutes after** the page, not hours before it. The
direction was inverted, and the claim had been inherited — it came from `3b7e022`'s
commit message ("shipped in #305 a couple of hours before"), carried into a session
summary, and then into this draft, without anyone recomputing it. Three documents
repeating a number is not three sources.

That is the failure the document itself is about, one level up: **a claim that reports
success while nothing has looked at it.** The corrected version is also the better
story — two sessions running concurrently, one closing an item twenty-seven minutes
after the other wrote it down, and neither able to see the other.

**A second finding came from re-measuring rather than re-reading.** The draft quoted
`session_start_trimmed.sh` at `90 lines, 6851B`. Twenty minutes later, mid-review, the
same command returned `102 lines, 7787B` — **936B of drift**, because sessions claimed
blocks on the board in between. That put the hook **213B from its 8,000B budget**, which
is a live problem nobody had looked at, found by a review of a document about hooks
rather than by the hook work itself. It is filed as
[`docs/todo/2026-08-27-the-board-digest-is-213-bytes-from-degrading.md`](../todo/2026-08-27-the-board-digest-is-213-bytes-from-degrading.md).

## What this run does not warrant

This review found and fixed 13 defects across two rounds. **It is not a correctness
proof.** The convergence table below measures how quickly reviewers stopped finding
things, not whether anything remains — and this run had a structural weakness recorded
in the residuals: it was a single-pass self-review, so every role inherited the
drafter's blind spots by construction.

## Convergence

| round | blocking | major | minor | notes |
| --- | --- | --- | --- | --- |
| 0 — initial, 11 roles | 1 | 3 | 6 | the inverted timing; two arithmetic/consistency defects; cold open was housekeeping |
| 1 — blind | 0 | 2 | 1 | a quoted measurement had drifted; imprecision about which fix the census bug arrived in |
| 2 — blind | 0 | 0 | 0 | reproduce block re-run end to end; all arithmetic recomputed |

**Stopping reason: severity floor reached** (a blind round with no blocking and no
major findings), not the round cap.

## How it generalises

The two findings that mattered were both produced by **recomputing rather than
rereading** — commit timestamps instead of a remembered ordering, and a re-run command
instead of a quoted figure. Neither required a subagent, a search, or domain knowledge.
For a document whose subject is prior work in the same repo, the highest-yield role is
role 1 run literally: take every identifier and every number, and derive it again from
the tree at writing time.

---

# Appendix — run record

- upstream:  syncytium2/murderboard @ 73dad04
- copy:      vendored @ 73dad04 (re-vendored in PR #338 this session, from 94d720c)
- freshness: current (`murderboard_freshness.sh --refresh --verbose` → exit 0)
- artifact:  `docs/handoffs/2026-08-27-the-guards-that-could-not-fail.md`
             (`c4a4eb4b` → `0ac95193` → final, hash changed at every round)
- roles:     11 of 11 run
- rounds:    2 blind verify rounds; stopped at the severity floor

## Role ledger

| # | role | findings | what it checked |
| --- | --- | --- | --- |
| 1 | Claim & data verifier — "Prove It." | **1 blocking, 1 major** | Every identifier and quantity recomputed from the tree: four merge shas via `gh pr view`; `696cac3`/`5502764`/`13b767f`/`3b7e022` commit times via `git log --date=iso`; PR #298's close time via the API; all seven arithmetic claims via `python3`. Found the inverted timing (blocking) and `13414−10186 = 3228`, i.e. 3.2KB not "four kilobytes" (major). |
| 2 | Citation & reference validator — "DOI or Die." | 1 minor | No literature citations. Attributions are internal: PRs, commits, and "another session" — each resolved against `git`/`gh` rather than memory. Verified the murderboard CONTRIBUTING quotation by opening the file. Corrected "Tony owns both repos" (unverified) to the checkable fact that both sit in the `syncytium2` org. **See residual ⚠1 and ⚠2.** |
| 3 | Consistency auditor — "Cross-Examiner." | 1 major, 1 minor | Cross-checked counts against companion docs. Found "three of thirteen worktrees" (at #324) unreconciled with "3 of 14" in the numbers block — same three, different population, now stated. Found the handoffs index carried three rows and needed a fourth; added. Checked "spill/spilled", "canary", "budget", "ladder" used consistently with `session_briefing.sh` and the 2026-08-25 page. |
| 4 | Adversarial reviewer — "Reviewer 2." | 2 minor | Attacked the two general claims. "The number that settles a check has to come from outside the thing being checked" — a generalisation from four cases; now marked as such rather than stated as a law. "The spill limit is per hook" rests on **one** observation (6,337B delivered while 17,438B spilled in the same startup); softened to "at least per hook", with what it does and does not rule out stated. Also flagged the unjustified constant "~8,800", removed in favour of the two numbers the canary already prints. |
| 5 | Line editor — "Kill Your Darlings." | 1 minor | Sentence-level pass. Cut "in the direction that matters" for the thing it actually means (claiming headroom that is not there). Checked each section asserts one thing; no jargon left undefined on first use except the terms role 8 covers. |
| 6 | Methods / domain expert — "RTFM." | **no findings** | Nothing to check: no new analysis code, no library call, no statistical method. Verified the one methodological claim the document makes about its own tooling — that `comm` compares as strings, which is why the census sorts lexically before subtracting — against the shipped `hook_spill_census.sh`. |
| 7 | Reuse auditor — "Reinventing the Wheel." | 1 minor | The document restates item 3 at length while `docs/todo/…-selftest-is-not-portable.md` also carries it — two accounts of one bug, free to drift. Resolved by naming the todo canonical for the reproduce command and diagnosis, leaving the handoff section to explain only what the instruction *means*. Checked the page points at tools rather than duplicating their output. |
| 8 | Naive-reader accessibility — "You Lost Me." | 1 minor | Read cold. "Spilled" is load-bearing in rows 1 and 4 of the opening table and was used before definition; added a blockquote defining it before the table is interpreted. "Board", "worktree", "sapper", "vendored", "FOUNDATIONS §9" left undefined deliberately — the audience is a session in this repo, and each resolves in `CLAUDE.md`. |
| 9 | Density & figure-first — "Show, Don't Tell." | **no findings** | Counted: 7 sections, largest text block 118 words, two tables, one code block. **Prose is right here and no figure is owed** — the subject is four logic defects and a set of byte counts, neither of which has a visual form the tables do not already carry. The one genuinely visual artifact in this lineage, the byte-map of where a preview cut falls, belongs to the 2026-08-25 page and is not re-drawn. Applied the project convention rather than a slide threshold, since this is a Markdown record with no canvas. |
| 10 | Build & craft gate — "Ship It." | 1 minor | Mechanical, run against the file: all 4 relative links resolve on disk (re-run after every edit round); 6 external PR links well-formed; heading hierarchy `#` → `##` with no skips; both tables have matching column counts; `sapper --all` clear; the full reproduce block executed end to end, all six lines producing what the document claims, including the one that is meant to fail. Artifact hash changed at each round, so the shipped file is the reviewed one. |
| 11 | Argument order — "Start With the Problem." | 1 major | Reduced to its spine. The draft opened on housekeeping — *"not a root handoff, nothing is half-done"* — putting the reader through provenance before the finding. Moved the four-row defect table to the cold open and demoted the housekeeping below the rule. Arc used: **problem → the pattern behind it → what was fixed → the evidence → what is still open → what the instruction costs.** Deviation from the default arc, stated here: there is no separate "what it costs" section; cost is carried inside each row of the opening table. |

## Findings and adjudications

**Blocking**

1. *"hours before the page listing it as open was written"* — **inverted**. Fixed: the
   page was committed at 22:32, the test landed at 22:59, twenty-seven minutes later
   from a concurrent session. The corrected passage also states the eight-minute gap
   between PR #298 closing (03:08Z) and the handoff being retired (03:16Z), both
   verified rather than quoted.

**Major**

2. "four kilobytes tighter" → 3.2KB, and the two operands are now named so a reader can
   redo the subtraction.
3. "three of thirteen" vs "3 of 14" → reconciled in place; the population moves, the
   three do not.
4. Cold open was housekeeping → the defect table now leads (role 11).
5. A quoted figure had drifted 936B mid-review → updated, **and the drift itself written
   into the page** as evidence for the claim it was already making about dated numbers.
6. "the census built to fix #313" / "while fixing the first three" → the census shipped
   *in* #313 and its bug arrived inside that fix; corrected.

**Minor** — all fixed: the unjustified `~8,800` constant; "spilled" defined before use;
"Tony owns both repos" → the org fact; the handoffs index row; the todo named canonical
for item 3; the n=1 claim marked as one observation.

**Spawned by the review, not a defect in the artifact:** the 213B-headroom finding,
filed as its own todo rather than left in a dated record.

## Residual ⚠

1. **⚠ Single-pass, not parallel subagents.** This session is configured not to spawn
   agents, so the review took the single-pass form the process permits: every role's
   checklist walked in turn, none skipped. That is **weaker than the parallel form** —
   one reader cannot be blind to their own draft — and the same limitation is recorded
   on the 2026-08-25 run. A re-review with parallel arms would not be wasted.
2. **⚠ Role 2 could not be run as a separate blind agent.** The process names this the
   one role the size rule may not collapse, because the defect it catches is a search
   that stopped too early and a single pass inherits the drafter's search history. The
   attributions here are internal — PRs, commits, sessions — and every one was resolved
   against `git`/`gh` rather than memory, which is the check that mattered for *this*
   artifact. The blindness the rule asks for was still not available.
3. **⚠ Nobody was asked.** No correspondence check. The claim that item 2 was built by a
   concurrent session is inferred from commit times and branch names, not confirmed with
   whoever ran it. For internal attribution this is close to decisive; it is not the
   same as asking.
