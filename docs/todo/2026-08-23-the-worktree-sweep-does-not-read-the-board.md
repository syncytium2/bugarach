---
status: open
filed: 2026-08-23
---

# The worktree sweep judges by git and never reads the board

`tools/worktree_sweep.sh` decides a worktree is removable when its branch is
merged to `origin/main`, the tree is clean, and nothing has touched it recently.
That is a good rule and the tool is careful about it — it reports liveness on
every row, refuses dirty trees, and keeps detached HEADs.

**It does not consult either session board.** So a worktree can be
merged-clean-idle by git and still carry an **ACTIVE claim** from a session that
means to come back to it.

Measured while closing out a session on 2026-08-23: the dry run offered to remove
**27** worktrees, and at least three of them — `widthdef`, `cicada`, `hygiene` —
had ACTIVE blocks on the machine-local board at that moment. A session that ran
`--apply` in good faith would have deleted three other sessions' working
directories, and the tool would have been right about every fact it checked.

## Why this is the board's own failure mode, one level down

`docs/session_protocol.md` exists because *"a live worktree and an abandoned one
look identical"* — the sweep's own docstring says so, and quotes the day it cost
something. The sweep fixes that for **git state** and reintroduces it for
**intent**: merged does not mean finished, because a session may have landed one
PR and be about to open the next from the same worktree.

The two boards are the only record of intent, and the tool that acts on
worktrees is the one tool that ignores them.

## What to do

Cheapest first.

1. **Read the machine-local board and veto any worktree with an ACTIVE block**,
   the same way liveness is vetoed now, and print the claim as the reason. The
   board lives at a known path relative to the worktrees directory, and blocks
   already name their worktree on a `**Worktree:**` line.
2. **Report the claim even where it does not veto** — the sweep's stated
   principle is that presence should mean something, and "merged, clean, idle,
   **and claimed by Mac/widthdef**" is a more useful row than either half.
3. **Consider the same veto for `docs/SESSIONS.md`**, the cross-machine board,
   for worktrees holding a shared external claim.

Until then, the honest workflow is what this session did: **remove your own
worktrees by name, never `--apply`**. Which makes the tool's main affordance the
one nobody should use, and is the argument for fixing it rather than documenting
around it.

## Related

- **`tools/merge_when_green.sh` now reaps its own worktree on a green merge**
  (2026-08-23). That removes the *reason* most of these worktrees exist to be
  swept, but it does not close this item: it only ever touches the worktree the
  caller is standing in, so anything that leaked before it existed, or that a
  crashed session left behind, still needs a collector — and that collector is
  still the one that must not be `--apply`ed. What changed is the backlog's
  growth rate, not its safety.
- `docs/todo/2026-08-20-claim-before-starting-not-before-committing.md` — the
  other end of the same problem: claims arriving after the work rather than
  before it. A sweep that reads the board is worth more once claims are reliably
  early.
