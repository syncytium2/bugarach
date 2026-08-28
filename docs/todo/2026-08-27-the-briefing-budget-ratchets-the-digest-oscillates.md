---
status: open
filed: 2026-08-27
---

# One SessionStart budget ratchets and the other oscillates, and only one of them is a problem

> **Corrects this file's own first draft, filed an hour earlier as
> `…-the-board-digest-is-213-bytes-from-degrading.md`.** That draft named
> `session_start_trimmed.sh` as the hook about to degrade, at 213B of headroom. It is at
> 1,182B now. `session_briefing.sh` is at 217B. They swapped inside an hour, and the swap
> is the finding: the first draft measured a *spike* and reported it as a *trend*.

Measured three times in a row, same values each time:

```
$ bash tools/session_start_trimmed.sh | tail -1     # 6818B / 8000B  -> 1,182B headroom
$ bash tools/session_briefing.sh | head -1          # 8783B / 9000B  ->   217B headroom
```

An hour earlier the same two commands gave 7,787B and 8,360B. Neither hook changed.

## The two are driven by different things, and it matters

| hook | its size tracks | behaviour |
| --- | --- | --- |
| `session_start_trimmed.sh` | **ACTIVE blocks** on the machine-local board, via `board_digest.sh` | **oscillates** — blocks go ACTIVE then DONE; this ran 12 -> 5 within the hour |
| `session_briefing.sh` | the **count of open todos** (`docs/todo`, `docs/sapper_feedback`) plus the alarms | **ratchets** — todos open far faster than they close; 73 -> 78 in the same hour |

So the digest's pressure is self-relieving and the briefing's is not. A session that
marks its block DONE gives the trimmed hook its headroom back. Nothing gives the briefing
its headroom back except closing todos, and this repo files them faster than it retires
them — by design, since a todo is where live items are supposed to go.

**Watch the briefing. The digest was a spike.**

## What happens when the briefing crosses

Not a spill: 9,000B is 1,186B under the smallest payload the harness has ever refused
(`tools/hook_spill_census.sh`, floor 10,186B). It **degrades** — the ladder in `deliver()`
re-renders FOUNDATIONS §9 as its six bolded claims plus a pointer. The hook still reports
success and says `(TERSE` on its first line, which is the canary doing its job. But the
reasoning behind the TTX fact — the thing the whole hook exists to deliver, after a
session spent a day reasoning from the textbook prior — stops arriving.

## Why raising the budget is not the fix here

The briefing's 9,000B is pinned from both sides, which the census made checkable:

- **Below:** the ordinary payload is 8,783B today. A budget under it degrades every run.
- **Above:** the observed spill floor is 10,186B, and the census asks for 1,000B of
  margin, so the ceiling is ~9,186B.

That leaves roughly **400B of room** against a payload that ratchets. It buys weeks.

**The fix is the one #306 already used: turn something into a count.** The open-threads
dump was 9.6KB and became three lines — that is why there is a deliverable briefing at
all. The next candidate is the waiting-on-Tony list, rendered in full inside a 1,200B cap:
it could print the count and the single oldest item with the rest behind a `grep`. Worth
~600B at today's three items, and it does not regrow.

The trimmed hook's 8,000B genuinely does have room — 2,186B under the floor — and could go
to 9,000B whenever its oscillation next peaks. One line, and
`bash tools/hook_spill_census.sh --check 9000` says whether it still holds.

## 2026-08-28 — the ratchet bit twice in one day, and the second time it set a design

Both bites were the same shape: a line that fit on a laptop and did not fit in CI.

`a194188` cut FOUNDATIONS §9's signpost from 201B to 124B after **CI measured 9,020B
where the laptop said 8,984B**. Hours later, the input line from
[the resolver being invisible](2026-08-28-the-resolver-exists-and-is-invisible.md) came in
at 228B in its unresolved branch — a fresh clone with no data and no darkroom, which is
what CI is — and put the briefing at **9,013B, 13B over**. Same day, same ~40B gap between
the two machines, twice.

**Measure a fresh clone, not this one.** This laptop resolves the darkroom in one line and
has the board and the commit gates; a fresh clone fires every standing alarm at full
length. The difference is ~90B and it falls entirely on the side with no margin:

```
cp -R <worktree> /tmp/ci && cd /tmp/ci && git config --unset core.hooksPath
HOME=$(mktemp -d) bash tools/session_briefing.sh | head -1
```

**What the second bite settled is worth more than the bytes it saved.** The 228B version
also said *"do not hunt with find(1); do not fall back to a .mat store"*, and the cut moved
that corrective into `.claude/hooks/the-folder-is-the-input.sh`, which fires on the `find`
itself. That is the better home on its own merits — a gate speaks at the moment of need and
has **no byte budget at all** — and it generalises: **the briefing's job is to make a
mistake unnecessary; a PreToolUse gate's job is to catch the session that made it anyway.**
Prose only a session already going wrong needs does not belong in a payload every session
pays for.

So there is a second relief valve beside "turn it into a count", and it does not regrow
either. The briefing sits at **8,878B in a fresh clone — 122B of headroom.**

## Related

- [two SessionStart hooks and neither sees the total](2026-08-26-two-session-start-hooks-and-neither-sees-the-total.md)
  — if that resolves toward trimming the pair, it answers this too. The spill limit is
  applied at least per hook, so the two fail independently and neither endangers the other.
- [the guards that could not fail](../handoffs/2026-08-27-the-guards-that-could-not-fail.md)
  — the record this came out of. Its numbers block carries the earlier, superseded pair; it
  is a dated page and is left alone, which is exactly why this item lives here instead.
