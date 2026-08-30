---
status: open
filed: 2026-08-29
---

# "OK to end session" is a self-report, and it is measured against the wrong predicate

Tony, 2026-08-29: *"so the words 'ok to end session' are not sufficient."* They are
not, and the reason is not that sessions are careless. **Every loss found in the
2026-08-29 audit came from a session that ended cleanly by its own account.**

## The one-file proof

`docs/handoffs/2026-08-29-the-transfer-experiment-and-two-things-i-corrected-myself-on.md`
says, in its own second paragraph:

> **Filed here rather than at the root, deliberately.** Nothing is half-done.
> Everything landed: **#394**, **#395**, **#396**.

and six paragraphs later:

> Raw JSONs are in a session scratchpad, not the repo.

Both sentences were true. That session had defined *done* as **"my PRs merged"**, and
against that predicate it was right. It is simply not the predicate that matters. The
five `bakeoff_seed*.json` behind that document's own headline table sit in
`/private/tmp`, and the bench branch they were measured on never opened a PR. The
session could have said *"ok to end"* honestly and the evidence still evaporates at
the next reboot.

## What the audit found, as four mechanisms

Measured 2026-08-29 on this machine. Every number here is reproducible from the
commands named beside it.

**1 · `/private/tmp` is where results actually live.** 44 session scratchpads, **1.4
GB**, roughly 250 artifacts, none in git and none in the darkroom. Cleared on reboot.
It holds the K scan over both full corpora (`k_scan_full.json`, 84 + 59 recordings),
the overnight tube screen (`tube_screen/bakeoff_seed{1..5}.json`), `dandi_stats.json`,
the bench runs, `probe_vs_heterogeneity.png`, `scoreboard.png`. One session alone has
55 artifacts.

*How it was found:* `find /private/tmp/claude-501/-Users-…-bugarach -type f`.

**2 · Branches ahead of `main` with no PR.** By `git cherry origin/main <branch>`,
counting patches genuinely not upstream:

| branch | unmerged patches | PR |
|---|---|---|
| `learned-detector-page` | **23** | **none ever opened** |
| `bench-background-is-not-flat` | **6** | **none** |
| `tube-variants-overnight` | 6 (the same, it sits on top) | none |
| `parity-was-the-inheritance` / `__pr298` | 4 | #298, closed unmerged |

The second is the costly one. `main`'s `bench.py` still reads `⚠ Not wired into the
bench`; the branch reads `Wired into the bench 2026-08-28`. **Every tube-variant number
in the 2026-08-29 handoff was measured in an environment that does not exist on
`main`** — fitted background, widened grid, 2.5 s tolerance. `__pr298` has no remote at
all and exists only on this disk.

**3 · The boards over-report and the root handoff goes stale in pieces.** The local
board carried **31 ACTIVE** claims of which **16 had no worktree**, while only 2
worktrees held uncommitted work; the git board carried 10. `HANDOFF.md` named #304 and
#270 as in flight the day after both merged — and `tests/test_handoff_is_honest.py`
only goes red when the **last** named PR closes, so a half-stale handoff passes green.

**4 · Four stashes**, the oldest from the PR #47 era.

## Why prose will not fix this, and where the gate belongs

This repo mechanizes the **commit** boundary hard — `.githooks/pre-commit` refuses a
commit on `main`, sapper runs on every commit, `guard_local_board.sh` refuses an
unclaimed worktree, `merge_when_green.sh` refuses an unchecked PR. It mechanizes the
**session-end** boundary not at all, and that is precisely the boundary at which *"will
this survive me?"* is answerable. At commit time the answer is not yet knowable; at
session end it is, and nobody asks.

Note also that this is not the human's job to remember. Tony ends sessions by saying so;
the session is the thing that knows what it made.

## What a gate would have to ask

Four questions, all checkable, none of them opinions, **all four of which failed
silently in the week before this was filed**:

1. **Does every branch I committed to have a PR?** `git cherry origin/main <b>` is
   non-empty and `gh pr list --head <b>` is empty → say so.
2. **Is there an artifact in my scratchpad that no committed file references?** A
   `.json` / `.png` / `.csv` produced this session whose name appears nowhere in the
   tree is either evidence that should be in `docs/learned/`, output that should be in
   the darkroom, or genuinely scratch — and the session is the only thing that knows
   which. Asking is cheap; guessing is what lost the K scan.
3. **Does every number in a document I wrote have a source in the tree?** The transfer
   handoff's table is the worked example.
4. **Is my board claim still true?** ACTIVE with no worktree, or ACTIVE after the PR
   merged, is noise that makes the board unreadable — and the board is the only thing a
   stateless session has.

## Open design questions, deliberately not settled here

- **Where does it hook?** Claude Code has a `SessionEnd` hook, which is the obvious
  home and has the obvious flaw: it does not run when a session dies, is killed, or
  runs out of context — which is how sessions usually end. A `Stop`-hook variant fires
  far more often and would have to be near-silent to be tolerable. Possibly both: a
  cheap `Stop` check and a full `SessionEnd` one.
- **Refuse or report?** Every other gate here refuses. This one cannot refuse anything
  — the session is already over — so it can only write a durable record. That may
  argue for it writing a file rather than printing, since printing at session end is
  read by nobody.
- **Question 2 is the expensive one** and the only one needing a heuristic. Worth
  measuring the false-positive rate over the 44 existing scratchpads before deciding
  the rule, the same way `tools/hook_spill_census.sh` measured the briefing budget from
  the record rather than guessing it.
- **Does the briefing already have the other half?** `tools/board_digest.sh` reads the
  board at start. The unpushed-work alarm already reports branches with no remote. The
  missing check is *branch with a remote but no PR*, which is a different and more
  common state — the four rows in the table above.

## What is NOT in scope

Reaping the branches or recovering the scratchpads. Those are one-off cleanups and
belong in their own items; this one is about the mechanism that will lose the next one.
The audit above is the record of what is currently at risk, not a work list.

## Related

- [`docs/session_protocol.md`](../session_protocol.md) — the vendored protocol, which
  covers claiming and not releasing.
- [`docs/todo/2026-08-20-claim-before-starting-not-before-committing.md`](2026-08-20-claim-before-starting-not-before-committing.md)
  — the same argument at the other end of the session.
- [`docs/todo/2026-08-28-a-worktree-pytest-run-tests-the-primary-checkouts-src.md`](2026-08-28-a-worktree-pytest-run-tests-the-primary-checkouts-src.md)
  — another defect whose whole nature is failing silently toward green.
