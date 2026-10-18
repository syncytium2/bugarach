---
rule: none-yet (tools/guard_local_board.sh, not a sapper rule)
status: done
filed: 2026-10-14
---

# The board guard reads a slash in a block's title as the start of the worktree name

**Filed 2026-10-14, after it refused two commits from correctly claimed worktrees in one
session.**

## What happened

`tools/guard_local_board.sh` refuses a commit from a worktree with no block on the machine-local
board. Twice in one session it refused a worktree that had one:

| block heading | worktree | the guard read it as |
|---|---|---|
| `### WSMIP065/handoff-explainer — a todo handing off the explainer for tools/measure_coordination_rates.py …` | `handoff-explainer` | `measure_coordination_rates.py` |
| `### WSMIP065/deprecated-exports — move the stale export folders to exports/bugarach/deprecated and …` | `deprecated-exports` | `deprecated` |

Each time the refusal said the worktree had no block, which was false. Removing the slashes from
the title fixed it. The first time it took reading the guard's source to see why. The second time
the cause was known and it still happened, because nothing at the point of writing a block says
that a title must not contain a path. In this repository, a path is the most natural thing to put
in one.

## Why it is wrong

`claims_heading` takes a heading line, strips `### `, and then removes **everything up to the last
slash in the whole line** before taking the identifier up to the first space:

```awk
if (index(s, "/")) { while (index(s, "/")) sub(/^[^\/]*\//, "", s) }
sub(/[[:space:]].*$/, "", s)
```

The comment above it explains the loop: the host part (`<host>/<id>`) may itself contain a slash.
But the loop runs over the title as well as the identifier, so any slash in the task description
moves the start of the identifier into the title. The two steps are in the wrong order: the
identifier should be cut out first (up to the first space), and the host stripped from that token
alone.

## Suggested fix

Swap the two substitutions, so the host is stripped only from the first token:

```awk
sub(/[[:space:]].*$/, "", s)                               # the first token: <host>/<id> or <id>
if (index(s, "/")) { while (index(s, "/")) sub(/^[^\/]*\//, "", s) }   # its last segment
```

Known-good fixtures for the selftest:

- `### WSMIP065/handoff-explainer — explainer for tools/measure_coordination_rates.py` claims
  `handoff-explainer`.
- `### Mac/a/b/settle-the-guard — x` still claims `settle-the-guard` (a host containing slashes, the
  case the loop exists for).
- `### handoff-explainer — moves exports/bugarach/deprecated` (no host) claims `handoff-explainer`.

A worktree name with a space in it would still be cut short, as it is today. None exists here.

**Ownership.** The guard is a bugarach-local addition (CLAUDE.md, "Multi-session coordination"),
not a vendored file, so the fix is allowed here. It is handed to the armory session with the other
open items in
[`../todo/2026-10-14-hand-the-open-sapper-issues-to-armory.md`](../todo/2026-10-14-hand-the-open-sapper-issues-to-armory.md).

## What was done (2026-10-14, the armory session on the Mac)

The suggested fix, as written: `claims_heading` now cuts the first token before it strips the
host. The comment above it says why the order matters.

The guard's `--selftest` has four new cases: the three headings above, and a check that the last
path segment of a title (`measure_coordination_rates.py`, `deprecated`) no longer counts as a
claim. Run against the old order, three of the four fail. The fourth case, a host with slashes,
passes either way, and that is its job: it shows the fix kept what the loop was for.
`tests/test_local_board_guard.py`, `tests/test_board_digest.py` and
`tests/test_hooks_installed.py` pass locally.

**Not done: a warning at the moment a block is written.** The finding notes that nothing tells a
session, as it writes a heading, that a path in the title breaks the guard. With the fix, a path
in the title no longer does, so there is nothing left to warn about. A worktree name containing a
space is still cut short, as before. None exists.
