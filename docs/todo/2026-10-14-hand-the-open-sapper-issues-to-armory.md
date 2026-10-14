---
status: open
filed: 2026-10-14
---

# Hand the open sapper issues to the armory session on the Mac

**A handoff to the armory session on the Mac** (Tony, 2026-10-14: *"handoff addressing sapper
issues to armory session on mac"*). That session reads this file from `syncytium2/bugarach`
`main`. It is a todo rather than a root `HANDOFF-*.md` because nothing here is half-done.

## What should exist afterwards

Every finding in `docs/sapper_feedback/` that is not `done` has an answer **appended to its own
file** (the README's convention), and its `status:` is `done`, `open` with a reason it waits, or
`won't-fix` with the reason. For each one fixed, the fix is on bugarach's `main` with a selftest
fixture proving the rule can fire (`tools/sapper.py --selftest`). Nothing else about what sapper
blocks today changes without the finding saying so.

How a fix reaches bugarach is armory's call, with one default. A rule only bugarach uses lands
here as a PR from a bugarach worktree, under bugarach's `CLAUDE.md`: claim on the board first,
green CI, `tools/merge_when_green.sh`. A fix that belongs to the estate lands in armory and comes
back as a vendored copy with a provenance stamp on line 1, the way `tools/show.py` does.

## The open items, as of 2026-10-14

The guard is not sapper, but it is the same kind of tool and is listed first because it bit
twice in one session:

| filed | finding | rule |
|---|---|---|
| 2026-10-14 | [the board guard reads a slash in a block's title as the worktree](../sapper_feedback/2026-10-14-the-board-guard-reads-a-slash-in-a-title-as-the-worktree.md). The fix is written and tested on three fixtures | `guard_local_board.sh` |
| 2026-08-12 | [`SAPxxx` IDs collide with interface2's, and both are cited bare](../sapper_feedback/2026-08-12-sap-id-namespace-collides-with-interface2.md) | none yet |
| 2026-08-12 | [`sapper --all` is blind to untracked files](../sapper_feedback/2026-08-12-sapper-all-is-blind-to-untracked-files.md) | SAP004 |
| 2026-08-13 | [SAP005 cannot see past one line](../sapper_feedback/2026-08-13-sap005-cannot-see-past-one-line.md) | SAP005 |
| 2026-08-17 | [SAP004 blocks a wildcarded client path](../sapper_feedback/2026-08-17-sap004-blocks-a-wildcarded-client-path.md) | SAP004 |
| 2026-08-19 | [the heredoc ban holds, and what it still misses](../sapper_feedback/2026-08-19-the-heredoc-ban-holds-and-what-it-still-misses.md) | none yet |
| 2026-08-22 | [reading a two-column PDF can manufacture a quotation](../sapper_feedback/2026-08-22-reading-a-two-column-pdf-can-manufacture-a-quotation.md) | none yet |
| 2026-08-23 | [SAP005 reads how a string opens, and the message does not say so](../sapper_feedback/2026-08-23-sap005-reads-how-a-string-opens.md) | SAP005; **no `status:` line** |
| 2026-08-26 | [the down-triangle rule cannot be a line match](../sapper_feedback/2026-08-26-down-triangles-cannot-be-a-line-match.md) | none yet |
| 2026-08-26 | [SAP009 sees only what is named](../sapper_feedback/2026-08-26-sap009-sees-only-what-is-named.md) | SAP009; status `landed-with-a-known-blind-spot` |
| 2026-08-27 | [SAP009 misses an overlay through a named variable](../sapper_feedback/2026-08-27-sap009-misses-an-overlay-through-a-named-variable.md) | SAP009 |
| 2026-08-28 | [a negative claim about code went stale in a contract](../sapper_feedback/2026-08-28-a-negative-claim-about-code-went-stale-in-a-contract.md) | none yet |
| 2026-08-28 | [a verify loop needs a stopping rule](../sapper_feedback/2026-08-28-a-verify-loop-needs-a-stopping-rule.md) | none yet |
| 2026-08-28 | [SAP007 cannot tell an importer from an analysis](../sapper_feedback/2026-08-28-sap007-cannot-tell-an-importer-from-an-analysis.md) | SAP007 |
| 2026-08-29 | [our detector keeps getting published under CICADA's name](../sapper_feedback/2026-08-29-our-detector-keeps-getting-published-under-cicadas-name.md) | none yet |
| 2026-09-04 | [SAP012 cannot see a shift](../sapper_feedback/2026-09-04-sap012-cannot-see-a-shift.md) | SAP012 |
| 2026-09-19 | [SAP004 cannot see a backslash](../sapper_feedback/2026-09-19-sap004-cannot-see-a-backslash.md) | SAP004 |
| 2026-09-19 | [the murderboard roster gate eats underscores](../sapper_feedback/2026-09-19-the-roster-gate-eats-underscores.md) | roster gate; **no `status:` line** |
| 2026-09-20 | [SAP004 matches a list of names, not a path](../sapper_feedback/2026-09-20-sap004-matches-a-list-of-names.md) | SAP004; **no `status:` line** |

Two are `done` and not listed: the private-correspondence check (2026-09-02) and the vendored-code
override (2026-09-01). Three files have no `status:` line at all, which a check could catch. That
is a small finding of its own.

## What to know before starting

- **Read bugarach's `CLAUDE.md` sections "Sapper" and "Other people's words"** first. The second
  explains why `tools/check_quotes.py` is deliberately not a sapper rule (a signature that spans
  lines), and Tony's ruling that a clearance question goes to him, not into an edit of the check.
- **SAP004 guards a public repository against personal paths.** Every loosening proposed for it
  (the wildcard, the list of names) has to keep blocking the real case. Its four findings are
  best answered together.
- **The heredoc ban is a hook, not sapper** (`.claude/hooks/no-heredoc-source.sh`), and its
  finding argues it should stay as broad as it is. Read it before changing anything.
- Several items say a line matcher cannot do the job: the down triangles, SAP009 through a
  variable, the roster gate. "Won't fix in sapper, and here is what would" is an acceptable answer.
