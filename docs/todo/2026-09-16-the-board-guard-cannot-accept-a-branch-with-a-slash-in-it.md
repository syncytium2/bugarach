---
status: open
filed: 2026-09-16
---

# The local-board guard cannot accept a branch name with a slash in it, and its own message tells you to write one

`tools/guard_local_board.sh` decides whether a worktree has claimed itself by parsing
block headings. The parse is in `claims_heading`:

```awk
sub(/^###[[:space:]]+/, "", s)
if (index(s, "/")) { while (index(s, "/")) sub(/^[^\/]*\//, "", s) }
sub(/[[:space:]].*$/, "", s)
```

It strips **everything up to the last slash**, because a host name may contain one. The
comment above it says so and is right about hosts. It is wrong about branches.

**Every branch with a slash in it is unclaimable by its own name.** On a branch called
`claude/coordination-detector-nets-hw8rve`, a heading written exactly as the guard's own
refusal message suggests —

```
### vm/claude/coordination-detector-nets-hw8rve — what I am doing
```

— parses down to `coordination-detector-nets-hw8rve`, which equals neither the worktree
basename (`bugarach`) nor the branch (`claude/coordination-detector-nets-hw8rve`). The
commit is refused, and nothing in the refusal says why the heading it just recommended
did not work. The session that hit this on 2026-09-16 rewrote the heading to use the
worktree basename and moved on; a session with less patience reaches for
`ALLOW_UNCLAIMED_BOARD=1`, which is exactly the outcome the escape hatch's own comment
warns about.

This is not rare. `wip/<slug>` is the convention `CLAUDE.md` prescribes for stopping
mid-task, and every branch a hosted Claude session opens is `claude/<slug>`.

## What is actually ambiguous

`### a/b/c` could be host `a` + id `b/c`, or host `a/b` + id `c`. The guard picks the
second, always. Two fixes, and the second is better:

1. **Accept either split.** Compare every suffix of the heading after each slash against
   both wanted names, not only the last one. Three lines of awk, no change to what
   anyone writes.
2. **Compare the whole heading too.** Before splitting at all, test the full identifier
   against both names; that also catches a heading written with no host prefix.

Doing both costs nothing and makes the guard accept every heading a session would
plausibly write.

## What must not change

The 2026-08-26 fix is still right and must survive: the comparison is **exact against a
heading**, never a substring and never a regex, because matching prose let the primary
checkout through every time. This is about which candidates are compared, not about
loosening the comparison.

## Closes when

`--selftest` grows a case for a slashed branch, that case fails against the current
parse, and the parse is changed until it passes.
