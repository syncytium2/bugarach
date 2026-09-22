---
status: waiting-on-tony
filed: 2026-09-22
---

# Nine rulings, one page, so a session can see the whole queue

waiting: Rule the nine items in `docs/decisions_pending.md` — the pinning question and the jitter constant come first; both are minutes, and every tuned number on both streams is provisional until the second is answered.

**Read [`docs/decisions_pending.md`](../decisions_pending.md).** This file is the queue entry;
that one is the content.

## Why it is one entry rather than nine

The briefing prints every `status: waiting-on-tony` todo first and loudly, which is exactly
the channel these rulings needed — but it does it inside a size budget. The briefing sits at
about 8.1 KB against a spill threshold this machine's own record puts between 8,768 B and
10,186 B (`tools/hook_spill_census.sh`), and a payload over it is dropped whole, keeping only
its opening 2 KB.

**Measured, not estimated.** This entry took the briefing from 8,070 B to **8,404 B against a
budget of 9,150 B** — 334 B for the entry, leaving 364 B before the low end of the spill range
this machine's own record gives. Nine entries would have cost about 3 KB and silenced the alarm
they were filed to raise. **So the next waiting item is very likely the last one that fits**:
add it to the page instead, or shorten something first.

## Why the page exists at all

On 2026-09-22 nine live rulings were spread across a cover memo, two root handoffs, an open
pull request's body and a document in the darkroom. Tony, that morning: too many moving
pieces. The two rulings that were visible to every session were the two using this channel;
the other nine were visible only to whoever had read the right file that day, and sessions
restarted work that a ruling had already parked.

## When it closes

Each ruling leaves the page in the same commit as the place the work reads it — a bench
constant, a goal page, a contract, a handoff. When the last item goes, this file goes with it.
