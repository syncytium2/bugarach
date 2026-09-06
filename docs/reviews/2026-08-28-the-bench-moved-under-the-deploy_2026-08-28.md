# Murderboard run — docs/handoffs/2026-08-28-the-bench-moved-under-the-deploy.md

- upstream:  syncytium2/murderboard @ f62acb3
- copy:      vendored @ f62acb3
- freshness: current
- artifact:  `docs/handoffs/2026-08-28-the-bench-moved-under-the-deploy.md` (`59d547a` -> `198bd78`)
- roles:     11 of 11 run
- rounds:    2 (stopping reason: **severity floor** — round 2 produced no blocking and no major findings)

## What was at stake

A deploy note is read once, by someone about to publish, who did not do the work.
This one carries a claim the other two deploy notes cannot: **the bench changed
under them.** The site's `hero.png` and `diagnostic.png` are rendered from
`src/bugarach` at the bench's own settings, so a change with no viewer commit in
it still moves the published picture — and `tools/site_staleness.py` says so in
its own output, as a caveat nobody had yet had to act on.

## What the review caught

**A test count that was wrong in the first sentence.** The draft said "red on
purpose (three tests)". Recomputing gave **five** failures: the three it meant,
plus the stale-`bakeoff.json` one it described later without counting, plus one
nobody had seen.

**That fifth failure was the find.** `test_hooks_installed.py` reported
`core.hooksPath` empty in this worktree — so **two commits on this branch went in
with the branch guard, sapper and the board guard all silently absent.** It was
set when the worktree was created and was gone after a rebase. The test is the
only thing in the tree that notices, and it only ran because role 1 refused to
take the failure count from scrollback. Sapper was re-run by hand over the whole
tree afterwards: clean. The mechanism — rebase, or another session rewriting the
shared `.git/config` — is **not** established, and the note says so rather than
guessing.

Both are the same species as the last two runs on this estate: a number carried
forward from a previous run's output instead of re-derived. Third time, same
door.

## What would validate this, and how it generalises

The note's central claim is falsifiable in one command: build the site from this
branch and from `main`, and compare `hero.png`. It has not been run — the branch
is red and unmerged, so the comparison would be against a state nobody will ship.
That is stated in the note rather than left as an implied check.

The generalisation is the one `site_staleness.py` already wrote down and nobody
had needed: **a repo whose figures are rendered from its own library has build
inputs that do not appear in any commit list.** A staleness tool that reads git
cannot see them. The only defence is a human looking at the render, which is
exactly the step `docs/deploy.md` prescribes and a prose-only change invites
people to skip.

## Method note

Single-pass self-review walking all eleven checklists, not the parallel fan-out
the process prescribes for a substantial deliverable — this session cannot spawn
subagents. Role 2's separate-agent carve-out **does not fire**: the note
attributes no method and claims nothing as novel. Recorded so coverage can be
weighed rather than assumed.

## Appendix — role ledger

| # | role | findings | note |
| --- | --- | --- | --- |
| 1 | Claim & data verifier — "Prove It." | 3 | "three tests" was five (blocking); the hooks failure it exposed; every constant re-read from the tree — `TOL_SEC` 2.5, coact grid `1e-1…1e-7`, `MEASURED_RATE_SHAPE` 0.275, and the "81 windows / 2 643 ROIs" provenance confirmed present in `bench.py` rather than quoted from memory |
| 2 | Citation & reference validator — "DOI or Die." | 0 | nothing to check: no literature cited, no method attributed. Carve-out does not fire (method note) |
| 3 | Consistency auditor — "Cross-Examiner." | 2 | the opening count contradicted the body's own later description of the bakeoff failure; checked against both companion notes and `DEPLOY_HOLD.md` for contradiction — none, the three cover disjoint commits and this one says so explicitly |
| 4 | Adversarial reviewer — "Reviewer 2." | 2 | "if this branch lands the figure changes" was asserted, not measured → now says the comparison has **not** been run and why; the hooks claim was softened to name what is *not* established about its cause |
| 5 | Line editor — "Kill Your Darlings." | 1 | the lead buried the actionable sentence under provenance; the figure-moves claim now opens the note |
| 6 | Methods / domain expert — "RTFM." | 1 | verified the coupling by reading the build rather than assuming it: `make_diagnostic.py` imports from `bugarach.bench` three times, and `build_site.py` mentions `bakeoff` zero times — which is what makes "stale and stays stale" true |
| 7 | Reuse auditor — "Reinventing the Wheel." | 1 | the paired-delta and heterogeneity numbers come from scratch scripts that duplicate what `tools/probe_vs_heterogeneity.py` does for PR #50; noted in the note as where they belong if kept |
| 8 | Naive-reader accessibility — "You Lost Me." | 1 | "the regime budget was not touched, and that is the result" needed the *why* on the same line for a reader who has not seen the four decisions |
| 9 | Density & figure-first — "Show, Don't Tell." | 1 | the build-coupling paragraph was prose doing a table's job → three-row table (build input · what it reads · when it moves). No figure warranted: this is a checklist for one reader, and the figure it would carry lives on the branch already |
| 10 | Build & craft gate — "Ship It." | 0 | Markdown, no render. Table run instead: all 4 relative links resolve from `docs/handoffs/`, both fingerprints recorded, file re-checked after the last edit |
| 11 | Argument order — "Start With the Problem." | 1 | the draft opened on the hold's history; it now opens on what a deploy session would otherwise discover from an unexplained figure |

### Residual ⚠

1. **The before/after `hero.png` comparison has not been run.** The claim that
   the figure moves rests on the build reading `BENCH_RECORDING` and
   `OPERATING_POINTS` (verified by reading the imports), not on two rendered
   files diffed.
2. **Why `core.hooksPath` emptied is unknown.** Restored and verified; cause not
   established, and it could recur in any worktree.

## What this run does not warrant

This review found and fixed 13 defects across 11 roles. **It is not a correctness
proof.** One reviewer walked eleven checklists, so a blind spot shared across them
would not have been caught by any of them — and the most consequential finding
here came from re-running a command rather than from reading the prose.
