---
status: open
filed: 2026-08-30
---

# The briefing has about one todo of headroom, and the next one will degrade §9 again

> **Not murderboarded** — a finding for sessions in this tree. Reproduce with
> `bash tools/session_briefing.sh | head -1` and `bash tools/hook_spill_census.sh`.

Adding two files to `docs/todo/` turned CI red on 2026-08-30. Not because the files
were wrong — because one of them carried `status: waiting-on-tony`, which earns a
three-line block in the session briefing, and the briefing had **144B of headroom on
a fresh clone**. It went over, the ladder did its job, and §9 degraded to its claims
with the consequences stripped off.

That is the alarm working. It is also a channel that fails on the next todo.

## The arithmetic

| | bytes |
|---|---|
| §9, the payload | **5,810** |
| everything else together | ~2,900 |
| **ordinary briefing, set-up machine** | **8,693** |
| **ordinary briefing, fresh clone** | **~8,965** |
| budget (raised from 9,000 this day) | 9,150 |
| smallest payload the harness has ever refused | 10,186 |

A fresh clone costs about **270B more** than a set-up machine, because each missing
resource — no export folder, no darkroom, no local board — prints a warning saying so.
That is not a CI artifact. FOUNDATIONS §8 requires this repo to resume on any machine,
and a new laptop *is* a fresh clone. **The environment with the least context produces
the largest briefing and is the first to lose §9's reasoning** — which is exactly
backwards from what anyone would design.

## Why another 150B is not the fix

The budget cannot keep rising: the census puts the ceiling at **9,186B** (1,000B under
the smallest observed refusal), so 9,150 has spent nearly all of it. And the two
growing sections both grow for good reasons — the waiting-on-Tony list grows with every
decision that reaches him, and the root handoff excerpt grows when work is genuinely in
flight. Squeezing them is squeezing the alarms.

## What would actually fix it, roughly in order of how much it buys

1. **Make §9 pay for itself.** It is 5,810B, two thirds of the briefing, and it is the
   same text every run on every machine. A session that has already read it does not
   need it re-injected — but a session that has *not* absolutely does, which is why it
   is there. A digest plus a "read the file" pointer is the obvious move and the
   obvious risk: the whole reason §9 is inlined is that the pointer form got ignored.
   Any change here needs Tony, because it is a judgment about what a session will
   actually read.
2. **Split the channel.** Alarms and session-specific state in the injected briefing;
   the standing facts delivered once, or on demand. This is the structurally right
   answer and the largest change.
3. **Bound the whole pre-§9 region, not each section separately.** Every section is
   individually bounded and the *sum* is not, which is how the region reached 2,326B
   against the ~1.5KB that the spill-preview guarantee assumes — putting the
   unpushed-work alarm outside the 2KB a spill preserves. Trimmed to 2,180B this day;
   still over.
4. **Have the census tell the briefing its own ceiling** instead of a hardcoded
   number that a human re-derives. `hook_spill_census.sh --check` already answers it.

## What was done on the day, and what was not

Done: the gates block lost its tool-path sub-lines (−112B, all four gates kept, since
the comment above it records that every one was skipped by a real session); the budget
went 9,000 → 9,150 with the census re-run as evidence; and the guard test that stops
the budget being raised into the refusal band still passes with 1,036B to spare.

Not done: any of the four above. This bought one todo of room, not a fix.

## See also

- `tools/session_briefing.sh` — the budget's header carries this reasoning inline.
- `docs/todo/2026-08-25-*` and the CLAUDE.md note on the 60,235B briefing that reached
  nobody: the failure this ladder exists to prevent, and why raising the budget without
  the census is not available.
