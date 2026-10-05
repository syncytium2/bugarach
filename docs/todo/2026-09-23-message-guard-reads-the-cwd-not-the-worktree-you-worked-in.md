---
status: open
opened: 2026-09-23
area: concurrency
upstream: syncytium2/murderboard
---

# The cross-session message guard reads the session's cwd, which on this machine is not the tree the session worked in

`.claude/hooks/require-commit-before-message.sh` refuses a `SendMessage` while the working tree
is dirty. The rule is right and the reasoning in its header is right: messages between sessions
are socket traffic, and a finding that exists only in one is a finding that evaporates.

**The gap is which tree it looks at.** It inspects the session's current directory. On a machine
running several worktrees — which is the normal shape here, and the shape
`../bugarach-worktrees/SESSIONS.md` exists to coordinate — a session's cwd is often the primary
checkout while all of its actual work happens in a worktree beside it.

## What happened

2026-09-23, closing out the co-modulation run. Every finding was committed, pushed and **merged**
— [#768](https://github.com/syncytium2/bugarach/pull/768), #769, #770 — and the worktree the work
was done in was clean with nothing unpushed. The guard still refused the status message, because
the *primary checkout* carried ` M tools/make_group_raster_summary.py`: 156 lines of another
session's combined-stream raster work.

That file was **already durable**. The board records, at the machine-local `SESSIONS.md`, that a
previous session snapshotted it to `origin/wip/combined-stream-raster` with `git stash create`
and **deliberately left the primary checkout dirty** so the work stayed resumable from any
machine. So the guard blocked a message about committed work, on account of a file that was
neither this session's nor uncommitted in the sense the guard means.

The three ways out were all worse than not sending:

- **Commit the foreign change.** It is another session's in-progress work, and it sits on `main`,
  which `.githooks/pre-commit` refuses anyway.
- **`cd` into the clean worktree and re-send.** Mechanically this passes, and it is exactly the
  "route around the guard" move this repo punishes elsewhere. A guard you can satisfy by changing
  directory teaches sessions to change directory.
- **Send from somewhere else.** Same thing wearing a different hat.

So the message was not sent, and the status went into the transcript instead — which is the
outcome the guard exists to prevent.

## What to decide

This is **vendored** (`syncytium2/murderboard @ fae0eca`) and its line 2 says not to edit it here.
A fix goes upstream and gets re-copied. Options, roughly in order of how much they change:

1. **Scope the check to the worktree the session has been writing in**, not the cwd. Hardest to
   define, and probably needs the session to declare it.
2. **Ignore paths no commit in this session touched.** Closer to the rule's intent — "your
   finding" is the thing at risk, not a neighbour's — but the hook would need a session-scoped
   record of what it has committed.
3. **Let a path be excused by name**, e.g. a marker the board or a dotfile carries for work that
   is deliberately parked dirty and already mirrored to `origin`. Cheapest, and it matches how
   this machine already documents the situation in prose.
4. **Leave it.** Defensible: the friction is rare, the false positive is loud rather than silent,
   and a guard that fails closed is the right failure direction. If this is the answer, the
   header should say so, because a session that hits it will otherwise look for a way through.

⚠ **Whatever is chosen, it should not become "dirty tree means send anyway".** The rule caught
real losses; this is about *whose* dirt it counts.

## Not urgent

One blocked message, and the content survived in three merged PRs. Filed because the next session
to hit it will reach for option 2 in the list above — `cd` and re-send — and that is the one
outcome worth preventing.
