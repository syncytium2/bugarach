---
status: open
filed: 2026-09-03
---

# `show.py` scatters files into a darkroom folder per worktree, not per project

Found by using the tool on the day it was vendored, which is the only way this
surfaces: every check in its own `--selftest` passes.

## What happens

`tools/show.py` derives the darkroom project folder from the **checkout directory
basename**. Run from a worktree, that is the worktree's name:

```
$ cd bugarach-worktrees/vendor-send-goes-nowhere-fresh
$ python3 tools/show.py --no-open docs/learned/three_scoring_rules.png
<darkroom>/vendor-send-goes-nowhere-fresh/three_scoring_rules.png
```

The file was meant for `<darkroom>/bugarach/`. `--project bugarach` places it
correctly, and the selftest even has a case for *"an explicit --project wins"* —
so the override exists because derivation was known to be fallible. What is wrong
is the default.

## Why it matters more here than upstream

**This repo's normal working state is many worktrees at once** — 21 on this machine
today, and `CLAUDE.md` tells every session to make its own rather than share a HEAD.
So the derivation is wrong in the *common* case here, not the edge case. Left as it
is, a week of sessions delivering figures produces a darkroom full of folders named
after branches, each holding one file, and none of them where anybody looks. That is
the same failure the tool exists to end, one level along: the file goes somewhere,
the tool truthfully prints where, and the human still does not find it.

It also silently defeats `bugarach.paths.darkroom()`, which every figure tool in
this repo already routes through, so two delivery paths in one repo would disagree
about where bugarach's darkroom is.

## Do not patch it here

`tools/show.py` is **vendored from armory** (stamp on line 3). The rule in
`CLAUDE.md` is explicit for exactly this case — *"never edit a vendored file in
place"*, and the murderboard-selftest item is the precedent: *"It is a vendored
file: send it back, do not patch it."* Reported to armory rather than fixed locally.

## The fix worth proposing upstream

Derive from the **repository**, not the directory. `git rev-parse --git-common-dir`
answers this correctly from any worktree — it points at the primary checkout's
`.git`, so its parent is the project root whether you are in the primary checkout or
in a worktree of it. `--show-toplevel` does **not** work: in a worktree it returns
the worktree.

Until it lands, a bugarach session using `show.py` should pass `--project bugarach`
explicitly. Worth a line in `CLAUDE.md` only if the upstream fix stalls; a workaround
in a durable doc that outlives the bug is its own defect, and this repo has paid for
that one twice.
