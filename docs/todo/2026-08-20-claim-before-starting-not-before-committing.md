---
status: open
filed: 2026-08-20
kind: process proposal — the readable half is done; one decision left for Tony
---

# The boards catch a session at its first commit, which is after the waste

Three sessions collided on 2026-08-20. Every one produced good work twice, and the
boards prevented none of them.

| collision | cost |
|---|---|
| `modularity_null.py` + `make_assembly_closed_figure.py` converted to read the export folder | two independent conversions, hours apart. Theirs was better and mine was discarded |
| export spec **revision 6**, "the folder is the corpus" | two revisions written the same day, same conclusion. Theirs carried the sharper incident; mine was dropped in the merge |
| chromium | one session installed the browser on this laptop, one added a workflow step, each correctly reporting "chromium is in" about a different machine |

None of these was carelessness. Each session claimed properly, on the right board,
in the right format. **The claims simply arrived too late to be read.**

## Why they arrive late

`tools/guard_local_board.sh` refuses a commit from a worktree with no block. It is a
good gate and it fires *at the first commit* — so that is when a session writes its
block, because that is when it is forced to. By then the work exists.

The window that matters is the one before that: a session decides what to do,
spends an hour doing it, and only then announces it. Two sessions in that window
cannot see each other no matter how disciplined they are.

## The boards were not merely long. They were undeliverable.

The first draft of this proposal argued the boards were too long to *scan*. That was
true, and it was the smaller half. Measured:

- The vendored session-start hook emitted **60,235 bytes across 868 lines**. The
  machine-local board, `cat`-ed whole, was **835 of them**.
- The harness will not inject a hook that size. It wrote the output to a file and
  gave the session a **2KB preview** instead.
- `--- session board:` sits at **line 32**. The preview ends at **line 26**.

**So the board did not reach that session's context at all** — and it also evicted
the worktree list, the MATLAB report and the unpushed-work alarm, which share the
stream and come before it. A board of **52 blocks of which 8 were ACTIVE** cost the
entire briefing and delivered none of itself. The git board is **32 blocks, 4
ACTIVE**, and is not printed at session start at all.

That is not a discipline problem, and it is not quite a legibility problem either.
It was a delivery failure wearing both as a disguise.

## What is done

**The briefing prints live claims only.** `tools/board_digest.sh` renders the ACTIVE
blocks with their `Worktree`, `Touches` and `Holds` lines; everything else stays in
the file. `tools/session_start_trimmed.sh` runs the vendored hook and swaps its board
dump for that digest, and `.claude/settings.json` points at the wrapper. The vendored
file is **not edited** — its own header invites a repo to layer around the core, and
CLAUDE.md forbids editing it in place.

On this machine that is **61,558 bytes down to 5,674**, 889 lines to 84, with the
board reaching a session for the first time. Both scripts carry `--selftest`, and
`tests/test_board_digest.py` pins the properties that matter: live blocks survive,
DONE blocks do not, `Touches:` travels, the tail of the briefing is not eaten, and a
filter that cannot find its markers prints the original and says so rather than
passing an empty briefing off as a trimmed one.

The wrapper prints a **size canary** — `briefing delivered: N lines, NB` — and
re-renders the digest terse if it crosses a budget set well under the smallest
injection known to have failed. The exact threshold is not observable from inside a
session, so nothing here guesses at it; the number is simply always in front of the
next reader.

**Blocks declare `Touches:`.** Added to the stanza the commit gate hands you and to
the board the briefing scaffolds. Branch names would have caught none of the three
collisions — mine was `tools-read-the-folder`, theirs was not, and we still hit the
same two files. **The overlap was always in paths.**

**The gate admits that it is late.** Its refusal now says so in terms, and says what
to do instead, because a gate that presents itself as timely teaches the wrong lesson
about when to claim.

## The decision that is still yours

**Should the first *file write* be gated, rather than the first commit?**

"Write your block when you pick up the task" is now in three places and is still only
prose — which is exactly what failed on 2026-08-18, when a session read the briefing's
board line at startup, worked all day across two worktrees, wrote to the shared
darkroom, and never created the board. The commit gate exists because that sentence
did not hold. Adding a fourth copy of it is not a fix.

The mechanized version is a `PreToolUse` hook on `Edit`/`Write` that refuses the first
file mutation from an unclaimed worktree. This repo already runs two `PreToolUse`
hooks, so the pattern is established and the wiring is one settings entry. It fires
**before the hour of work** rather than after it, which is the entire complaint.

What it costs, honestly:

- it fires on every session, including read-only ones that later touch a single file;
- the claim moment lands before a session always knows what it will touch, so early
  `Touches:` lines will be guesses that need editing;
- it needs the same `ALLOW_UNCLAIMED_BOARD` escape, and an escape reached for
  routinely is a gate being disabled slowly rather than all at once.

I think it is worth it, and I did not build it: a gate on every write changes how it
feels to work here, and that is your call rather than mine.

## Not done, deliberately

**Warning on path overlap at commit time.** Proposed in the first draft, dropped here.
It fires in the same late window this document is complaining about; its value falls
sharply now that the digest puts other sessions' paths in front of you at startup; and
it would turn the board from prose that happens to be greppable into a parsed format,
which raises the cost of a malformed block written by a tired session. If the write
gate above happens, it can do that comparison at the right moment instead.

**Archiving the finished blocks.** Still worth doing for anyone who opens the board by
hand, but no longer load-bearing — the briefing does not print them either way.
`tools/worktree_sweep.sh` is **PR #149, open, not merged**; the first draft of this
document cited it as though it already existed.

## Next, and it is the same bug

**The other session-start hook is also being truncated.** `tools/session_briefing.sh`
— the one that injects the binding facts from FOUNDATIONS, written precisely because
*"claude.md is the first thing you ignore"* — emitted **13,414 bytes** and was spilled
to a file with a 2KB preview, exactly like the board. The channel built to survive
being ignored is currently being cut off mid-sentence.

That one is not a filtering problem, it is an editorial one. Deciding which facts are
binding enough to spend a session's first 2KB on is a judgement about the science, not
about shell, so it is filed here rather than fixed.

## Related

[`2026-08-20-webapp-session-status.md`](2026-08-20-webapp-session-status.md) reaches
the same conclusion — "a session should claim **before** starting, not when it first
commits" — filed the same day by a different session. Two independent proposals for
one fix is a fourth collision, and the best evidence available for the argument.
