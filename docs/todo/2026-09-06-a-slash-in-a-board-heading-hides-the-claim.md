---
status: open
filed: 2026-09-06
---

# A slash anywhere in a board heading's task text hides the claim from the guard

`tools/guard_local_board.sh` refused a commit from a worktree that had a block on the
board. The block was there, headed correctly, and the guard could not see it.

## What happened

The heading read:

```
### Mac/land-the-interface2-handoff — interface2's delivery note … lands in docs/exports
```

`claims_heading` extracts the identifier by dropping everything up to the **last** slash
on the line, so that a host name containing a slash still parses. The task text carried
`docs/exports`, so the last slash was inside the description, and the identifier the
guard compared was `exports`. Renaming the folder in the heading to "the exports folder"
made the same block pass.

The rule's own comment explains the choice — *"a host may contain one"* — and the
selftest covers a host with a slash. It does not cover a **task** with one, and task
text naming a path is the ordinary case on this board: the protocol asks for a
`Touches:` line full of paths, and headings routinely name the file or folder the
work is about.

## What to do

Parse the heading as `<host>/<id> — <task>`: split on the first ` — ` (or ` - `) before
looking for slashes, so only the `<host>/<id>` half is searched. Add a selftest case
with a slash in the task text, in both directions — a claim that must be found, and a
heading whose task text mentions another worktree's name, which must not be.

Until then: no slash in the heading text. Paths belong on the `Touches:` line.
