---
status: open
filed: 2026-08-28
---

# `git stash` is one stack for every worktree, and `pop` takes whatever is on top

Hit for real on 2026-08-28. **Another session's uncommitted work landed in my
worktree and left their stack**, and the only reason it cost nothing is that the
recovery worked.

## What happened

Standard-looking sequence, in a worktree, to rebase over a merge:

```bash
git stash -q          # my one edited doc
git rebase -q origin/main
git stash pop         # <- popped SOMEBODY ELSE'S work
```

`git status` afterwards showed `src/bugarach/dataset.py` and
`tools/session_briefing.sh` modified — two files I had never opened. Between my
push and my pop, a session on `resolver-is-invisible-briefing` ran its own
`git stash`. **The stash stack is per-repository, not per-worktree**, so theirs
went on top of mine, my `pop` applied theirs into my tree and dropped their entry
from the stack.

Two failures at once, and the quiet one is worse:

1. **I got their changes**, in a worktree whose board block says it touches docs
   only. Committing `git add -A` there would have put another session's
   half-finished `dataset.py` into a documentation PR.
2. **They lost their stash entry.** `pop` deletes on success. Nothing warned
   them; the next time they looked, their WIP would simply not be there.

## Recovery, which is worth writing down because it is not obvious

A dropped stash is unreachable, not gone:

```bash
git fsck --unreachable | awk '/commit/{print $3}' |
  while read c; do git log -1 --format="%h %s (%cr)" $c; done | grep -E '^\w+ (WIP|index) on'
git stash store -m "<original message>" <sha>     # put it back on the stack
git checkout <sha> -- <path>                      # or take one file out of it
```

Both entries were recovered this way — theirs restored to the stack with its
original message and verified byte-identical by diffstat, mine extracted as a
single file. The whole incident cost about four minutes **because the pop
happened to produce a visibly wrong `git status`**. A pop of somebody's WIP that
touched a file I *was* editing would have merged into my work silently.

## What to do instead

- **Do not `git stash` in a shared clone with other sessions live.** Prefer a
  throwaway commit on the branch (`git commit -am wip`, then `git reset --soft
  HEAD^` after), which is per-worktree and cannot be taken by anyone else.
- If a stash is genuinely wanted, `git stash push -m "<worktree>: <what>"` and
  pop **by name**, never by position: `git stash pop stash@{n}` after checking
  `git stash list`.
- **Never `git stash pop` without reading `git stash list` first.** The top of
  the stack is not necessarily yours, and there is no indication of which
  worktree an entry came from beyond the branch name in its message.

## Options for making it not depend on memory

- A `pre-stash`-style wrapper is not available — git has no such hook. The
  practical mechanization is a **guard in `tools/`** that refuses `stash pop`
  when the top entry's branch is not the current worktree's, plus a line in
  `docs/git_workflow.md`. That guard only helps sessions that call it.
- Cheaper and probably better: **say so in the workflow docs**, in favour of the
  wip-commit dance, which has no shared state. Checked: neither
  `docs/git_workflow.md` nor `docs/session_protocol.md` mentions `git stash` at
  all today — so nothing has to be *un*-recommended, and the gap is that a
  session reaching for the obvious git command gets no warning. One paragraph
  under the worktree rules would close it.

The stack today still holds two entries from branches that no longer exist
(`figure-back`, `parameter-spec-proposal`, 5 and 8 days old). Nobody is coming
back for those, and they are the reason the top of the stack is not a safe
assumption in the first place.
