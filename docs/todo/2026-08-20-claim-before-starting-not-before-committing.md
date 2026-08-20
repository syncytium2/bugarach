---
status: open
filed: 2026-08-20
kind: process proposal — needs Tony
---

# The boards catch a session at its first commit, which is after the waste

Three sessions collided on 2026-08-20. Every one produced good work twice, and the
boards prevented none of them.

| collision | cost |
|---|---|
| `modularity_null.py` + `make_assembly_closed_figure.py` converted to read the export folder | two independent conversions, hours apart. Theirs was better and mine was discarded |
| export spec **revision 6**, "the folder is the corpus" | two revisions written the same day, same conclusion. Theirs carried the sharper incident; mine was dropped in the merge |
| chromium in CI | one session installed the local browser, one changed the workflow, each correctly reporting "chromium is in" about a different machine |

None of these was carelessness. Each session claimed properly, on the right board,
in the right format. **The claims simply arrived too late to be read.**

## Why they arrive late

`tools/guard_local_board.sh` refuses a commit from a worktree with no block. It is a
good gate and it fires *at the first commit* — so that is when a session writes its
block, because that is when it is forced to. By then the work exists.

The window that matters is the one before that: a session decides what to do,
spends an hour doing it, and only then announces it. Two sessions in that window
cannot see each other no matter how disciplined they are.

## And the boards are too long to scan anyway

Right now: **50 blocks on the local board, 7 of them ACTIVE; 33 on the git board.**
DONE and ACTIVE are interleaved in one list. A session that *did* want to check
before starting is reading eighty-three paragraphs, most of them finished months or
days ago, to find seven live ones.

That is not a discipline problem. It is a legibility problem, and it is why "scan
the board before writing" quietly stops happening.

## Four changes, in the order I would do them

### 1. A block is created before the work, not before the commit

The rule becomes: **the block is the first act of the session**, written when you
pick up a task, before any code. This is the only change that addresses the actual
window, and it is a rule rather than a mechanism — which is a weakness, and the
next three are what compensate.

### 2. Blocks declare what they will touch

Add one line to the template:

```
- **Touches:** src/bugarach/detectors/*, tools/make_*_figure.py
```

Branch names would not have caught today's collisions — mine was
`tools-read-the-folder`, theirs was not, and we still hit the same two files. **The
overlap was in paths, never in names.** Paths are what a starting session needs to
compare against, and they are the one thing the gate can check mechanically.

### 3. The briefing prints live claims and their paths, not the whole board

`SessionStart` already prints a briefing. It should print **only ACTIVE blocks**,
with their `Touches:` lines, so a session sees what is spoken for in the first
thing it reads. Seven blocks is scannable; eighty-three is not.

### 4. The commit gate warns on overlap

`guard_local_board.sh` already parses the board to find your block. The same parse
can compare your staged paths against every *other* ACTIVE block's `Touches:` and
warn — not block, because a legitimate overlap exists and a gate that cries wolf
gets disabled.

This still fires late, but it converts "we both did it" into "we both did it, and
somebody was told" — which at least makes the merge deliberate.

## What to do with the finished blocks

DONE blocks should not be deleted: several carry findings nothing else records
(which archive is defective, why a folder must not be moved). They should move to an
`## Archive` section below `## Active`, so the live list stays short and the record
survives. A sweep tool could do it on the same rule
`tools/worktree_sweep.sh` uses — merged, and idle.

## What this does not fix

**Cross-repo collisions.** The chromium one was partly a vocabulary failure: "CI has
no chromium" repeated daily without ever saying *which machine*, until a session
reasonably read it as the laptop and installed it there. No board catches that. The
fix is in how findings are worded, not where they are filed.

**Sessions on other machines.** The git board travels and the local one does not.
Today's collisions were all on this machine, so the local board is the urgent half —
but the same `Touches:` line is worth having on both.

## The honest counter-argument

Every one of these adds friction to starting work, and the failure mode of process
is that it gets skipped under time pressure — which is exactly when collisions are
likeliest. Point 3 is the one I would keep if only one survived: it costs a session
nothing, and it is the only one that puts the information in front of somebody
*before* they choose what to do.
