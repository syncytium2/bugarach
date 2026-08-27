---
status: open
filed: 2026-08-27
---

# `session_start_trimmed.sh` is ~200B from degrading, and its budget is the one with room

> Found while murderboarding [the guards that could not fail](../handoffs/2026-08-27-the-guards-that-could-not-fail.md).
> The number in that page is a dated re-measurement; this is the live item.

```
$ bash tools/session_start_trimmed.sh | tail -1
briefing delivered: 102 lines, 7787B (board dump was 258099B before trimming; budget 8000B)
```

**213B of headroom.** And it is moving: the same line read `90 lines, 6851B` twenty
minutes earlier in the same session — **936B in twenty minutes** — because the digest
renders every ACTIVE block on the machine-local board and sessions kept claiming them.
The board behind it went 256,780B → 258,099B in that window.

## What happens when it crosses

The hook does not spill — 8,000B is 2,186B under the smallest payload the harness has
ever refused (`tools/hook_spill_census.sh`). It **degrades**: the digest re-renders
terse, and the ACTIVE claims stop arriving in full. That is the failure
`tools/board_digest.sh` was written on 2026-08-20 to prevent, reached by the other
road — not a 60KB dump that gets refused, but a budget quietly spending itself down
until the claims are summarised away. The hook still reports success either way.

## Why this one is easy

Unlike the briefing's 9,000B, this budget is **not pinned from both sides**. The census
gives the floor at 10,186B, so 8,000 can be raised to ~9,000 and still sit 1,186B under
the smallest observed refusal — the same margin `session_briefing.sh` runs on today.
Nothing in #313/#324/#331 touched this hook beyond one variable rename, and nobody has
looked at its budget since it was set on 2026-08-20 against a guess of 13,414B that the
census has since tightened to 10,186B.

Two things worth deciding together, not separately:

1. **Raise the budget** to ~9,000B, which the census supports today, and re-check with
   `bash tools/hook_spill_census.sh --check 9000`.
2. **Cap what the digest can grow into.** Raising the budget buys time against a board
   that grows without bound; the ACTIVE list is the input, and nothing retires a block
   except a session remembering to mark it DONE. A digest that renders N ACTIVE blocks
   is O(sessions), and this machine has run fourteen worktrees at once.

Doing only (1) moves the wall. Doing only (2) leaves the wall 213B away.

## Related

- [two SessionStart hooks and neither sees the total](2026-08-26-two-session-start-hooks-and-neither-sees-the-total.md)
  — the same pair, asking whether ~15KB of every session is worth it at all. If that
  question resolves toward "trim the pair", this item may be answered by it rather than
  on its own.
- The spill limit is enforced at least per hook, so this hook crossing its budget does
  not endanger `session_briefing.sh`. They fail independently, which is why they are
  wired as two entries.
