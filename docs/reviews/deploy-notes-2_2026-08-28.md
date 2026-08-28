# Murderboard run — `docs/handoffs/2026-08-28-deploy-notes-2.md`

## What was at stake

A deploy handoff is read once, in a hurry, by somebody about to publish. Everything wrong
in it becomes a wrong action or an omitted check, and unlike a report nobody re-reads it
afterwards to notice.

This one carries something sharper than a checklist: **the live public page is currently
misattributing a result to another laboratory**, and the fix is queued behind a
deliberate hold. So the note has to do two things that pull against each other — surface a
decision urgently enough that it is not discovered at deploy time, and **not make that
decision**, because `DEPLOY_HOLD.md` says lifting is a person's call recorded in words.

A handoff that soft-pedalled the first would let the error sit. One that overstepped the
second would route around a hold, which is the specific behaviour the hold exists to
prevent.

## What was found

**A number that had already drifted, in the twenty minutes it took to write the file.**
The draft said the site was *"behind by 33 commits."* Re-derived at review time: **35**.
Main had moved. The fix is not a corrected number — it is **deleting the number** and
sending the reader to `tools/site_staleness.py`, which is what `DEPLOY_HOLD.md` itself does
and for the same stated reason: *"a second copy of 'what is pending' is a thing that goes
stale."* The draft had quoted that sentence approvingly on one line and violated it three
lines later.

**A link to a file that does not exist yet.** The note calls itself a companion to
`2026-08-28-what-351-changes-under-the-deploy.md` — which is on **PR #361's branch, not
`main`**. If #361 lands second, the link is dead on arrival for anyone reading `main`. Now
labelled in both places: *"if the link above 404s, it has not landed yet."* Naming the
dependency is the fix; silently linking across an unmerged branch is not.

**The live-page quotes were fetched, not reconstructed.** Both retired sentences were
pulled from `bugarach.tonydefazio.com` rather than from `git show 0ed939d`. That matters
here more than usual: the whole claim of the note is *"the deployed page says X"*, and the
deployed page is the one artifact the repo cannot vouch for.

## What would validate this

Every checkable claim was re-derived at review time against a source, not carried from the
drafting session:

- **`222` and `12` insertions** for `173accd` and `f7c0edb`, and **35 changed lines** in
  `build_site.py` for `ed5e02e` — all from `git show --stat`.
- **The four commits that change what the site serves** — from `site_staleness.py`, not
  hand-listed. The *identity* of the four is stable; the total behind is not, which is the
  finding above.
- **The three retired/added strings** in the built page, by `grep` on `site/index.html`
  during the `ed5e02e` review, quoted here as the pre-flight commands rather than as
  results.
- **The Zenodo citation** — v1.0.3, five named authors, 20 July 2020, CC-BY-4.0.
- **The live page's two sentences**, by HTTP fetch.

**Not validated, and stated as such in the note:** anything about `173accd` and `f7c0edb`
beyond their diffstat. 222 insertions into the viewer is not this session's work and the
note says so rather than summarising code it did not read.

## How it generalises

**A handoff's most dangerous content is the part that is true and moving.** The wrong
attribution on the live page has been wrong for days and will still be wrong tomorrow —
it is safe to write down. The commit count was accurate when typed and false within the
hour. Reviews reliably catch the first kind, because it reads like a claim; the second
kind reads like a fact and slips through.

The countermeasure is not care. It is the rule `DEPLOY_HOLD.md` already states and this
draft still broke: **where a tool computes it, point at the tool.** A handoff should carry
what a tool cannot — judgement, provenance, what nobody has checked — and nothing a
command answers better.

---

## Appendix — run record

- upstream:  syncytium2/murderboard @ 3593c44
- copy:      **vendored** (repo's own `docs/doc_review_process.md` + `tools/murderboard_*.sh`)
- freshness: **current** (`--refresh --verbose`: *"current (@ 3593c44, via remote)"*, exit 0)
- artifact:  `docs/handoffs/2026-08-28-deploy-notes-2.md` (`42e94f37` -> see below)
- roles:     **11 of 11 run**
- rounds:    2 blind verify rounds to clean

> ⚠ **Single-pass, not parallel arms.** This session cannot spawn subagents, so one
> reviewer walked all eleven checklists. The process permits this scaling for a short
> deliverable and requires it be stated. **The attribution exemption does not bite here** —
> this note makes no attribution claim of its own; it reports one already reviewed under
> [`locust_attribution_2026-08-28.md`](locust_attribution_2026-08-28.md), where the same
> gap is flagged and is load-bearing.

### Role ledger

| # | role | findings | note |
|---|---|---|---|
| 1 | Claim & data verifier | **1 fixed** | "behind by 33 commits" had drifted to 35 during drafting; the number is now deleted rather than corrected. Re-derived: 222/12 insertions, 35 lines in `build_site.py`, the four serving commits, the Zenodo record, and both live-page sentences by HTTP fetch |
| 2 | Citation & reference validator | **1 fixed** | the companion handoff link points at PR #361's branch, not `main` — dead until it lands. Labelled in both places. Other three relative links resolve. No external literature; the one citation (Zenodo) is carried unchanged from an already-reviewed artifact |
| 3 | Consistency auditor | 0 | does not contradict `DEPLOY_HOLD.md` and repeats its "does not lift, amend or duplicate" disclaimer, matching #361's wording so the two notes read as a pair. Commit shas agree with `site_staleness.py` output. No count appears twice on different bases |
| 4 | Adversarial reviewer | 0 | pressed the central move: does raising the escape clause amount to arguing for it? The note names the clause, gives the evidence, and says *"raise it, do not act on it"* and *"decided elsewhere"*. It also does not soften the case to seem neutral — the harm (a promiscuity result attributed to another lab) is stated plainly because that is what the decision turns on |
| 5 | Line editor | 0 | the lead is a decision, not a description, and the note says why it is ordered that way. Section titles are consequences |
| 6 | Methods / domain expert | 0 | **no method or analysis underlies this deliverable** — it is a coordination note. The technical claims it repeats (the unvalidated middle link, the skipped stage, the parked status) were each verified under `locust_attribution_2026-08-28.md` and are cited, not re-derived |
| 7 | Reuse auditor | 0 | deliberately keeps **no** list of what is pending; defers to `site_staleness.py`. Does not restate `DEPLOY_HOLD.md`, `docs/deploy.md`'s runbook, or #361's content |
| 8 | Naive-reader accessibility | 0 | read cold by a deploy session with no context: the hold, the escape clause, the four commits and the pre-flight commands are all self-contained. "1e-9" and "parity fixture" appear once each, both glossed |
| 9 | Density & figure-first | 0 | one table, carrying the four commits and their owners — the only content with real structure. **Prose is right for the rest** and the reason is that it is a chain of judgement, not a measurement; there is nothing here a figure would show that a sentence does not |
| 10 | Build & craft gate | 0 | markdown renders; 6 table rows well-formed; **0 personal absolute paths**; all links checked after the fix. Pre-flight `grep` commands were run against a real build during the `ed5e02e` review and reproduce the stated counts |
| 11 | Argument order | 0 | the decision first, the inventory second, the detail third, what-it-does-not-know fourth. A deploy session that stops reading after the first screen has still met the only thing it cannot discover on its own |

### Residual ⚠

1. **`173accd` (222 insertions to the viewer) has no handoff.** Its author should write one
   or say none is needed. Not this note's to supply.
2. **No session has driven `raster_viewer.html` with all three pending changes present.**
   Flagged in the note; closing it needs someone to serve the build and walk it.
3. **The hold decision is unmade.** By design — the note raises it.
4. **Single-pass review** (above).
