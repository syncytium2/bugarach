---
status: open
filed: 2026-08-26
---

# Two SessionStart hooks, each budgeted, and nothing measures the total

> **Not murderboarded** — a finding for sessions in this tree; every number is one
> command. Moved here from [the hook audit](../handoffs/2026-08-25-the-session-hooks.md)
> item 4, which is a dated record and cannot carry a number that drifts.

`.claude/settings.json` wires two hooks on both `startup` and `resume`:

| hook | own budget (B) | measured 2026-08-26 (B) |
|---|---|---|
| `tools/session_briefing.sh` | 9,000 | 8,360 |
| `tools/session_start_trimmed.sh` | 8,000 | 7,028 |
| **total injected before the first user message** | **none** | **15,388** |

Both fit individually, so neither warns. Nothing anywhere measures the sum.

**The number moves, which is the point of filing it rather than quoting it.** The hook
audit recorded 8,068 + 6,282 ≈ 14KB on 2026-08-25; a day later it is 15,388B. Both hooks
report on live state — the board, the todos, a root handoff, waiting-on-Tony items — so
they grow as the repo does. The audit's figure was true when written and is the kind of
number a dated record should not have been holding.

## The question nobody has answered

Whether ~15KB of every session's context is worth what it buys. It was never decided; it
accumulated, one well-argued hook at a time, and each addition was individually correct:

- the FOUNDATIONS §9 extract exists because a session spent a day reasoning from a
  textbook prior the lab's own data refutes;
- the board digest exists because a 60,235B briefing reached nobody;
- the waiting-on-Tony block exists because finished work sat unfiled for twelve days.

None of those is wrong. The total is simply not anyone's job.

## What would settle it

1. **Measure the sum somewhere**, so it is visible the way each hook's own canary is.
   Neither script can do it alone — a wrapper or a test over `.claude/settings.json`
   could, and the shape already exists in `tests/test_session_briefing.py`, which asserts
   what a session *receives* rather than what a script prints.
2. **Decide a total budget**, or state that there is deliberately none.
3. **Settle it before a third hook is added**, because the failure mode is not a hook
   going over — each is guarded now — but the sum crossing a line nobody is watching.
   That is exactly how the briefing reached 17,568B: no single section was unreasonable.

## Reproduce

```bash
bash tools/session_briefing.sh      | wc -c
bash tools/session_start_trimmed.sh | wc -c
```

Both print their own size on their last line as well; the sum is the thing with no home.
