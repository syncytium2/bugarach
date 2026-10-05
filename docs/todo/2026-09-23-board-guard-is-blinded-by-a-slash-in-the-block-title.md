---
status: open
filed: 2026-09-23
---

# A slash anywhere in a board block's title makes the guard blind to that block

`tools/guard_local_board.sh` refuses a commit from a worktree with no block on the machine-local
board. It found none for a worktree whose block was sitting on the board, correctly named, seven
lines above `## Archive`.

The heading was:

    ### WSMIP064/release-claim — closing out the option A / option B session (2026-09-23)

`claims_heading` strips `### `, then loops:

    if (index(s, "/")) { while (index(s, "/")) sub(/^[^\/]*\//, "", s) }
    sub(/[[:space:]].*$/, "", s)

The loop is meant to drop the `<host>/` prefix, and it keeps going while any slash remains. The
title's own *"option A / option B"* is another slash, so the loop ate the identifier as well and left
`option B session (2026-09-23)`; the next `sub` cut that to the empty string, and the block was
skipped. The guard then reported, accurately by its own lights, that the worktree had no block.

**Why this is worth fixing rather than avoiding.** The failure is silent in the direction that
matters. A session that writes a block and is refused will go and look, as this one did. But the
identifier is matched against the worktree basename *or* the branch, so a heading like
`### host/feature — rework the a/b split` can also match the **wrong** block and let a commit through
believing it is claimed. A guard that both refuses good claims and can accept absent ones is worse
than one that only does the first.

**The fix.** Strip exactly one leading `<host>/` segment, not every slash-separated segment:

    sub(/^[^\/[:space:]]+\//, "", s)

Then take the identifier up to the first space, as now. A host name cannot contain a slash or a
space, so one substitution is all the prefix ever needs, and the title is left alone.

**Selftest to add**, since `--selftest` claims to prove every branch triggers: a block whose title
contains a slash must still be found, and a block for a different worktree whose title happens to
contain this worktree's name must still be refused.

**Worked around, not fixed, on 2026-09-23** by renaming the block to *"the options A and B session"*.
The workaround is invisible to the next session, which is why this file exists.

## Closes when

`claims_heading` strips one host segment; the two selftest cases above are in
`--selftest`; and `tests/test_local_board_guard.py` covers the slash-in-title case.
