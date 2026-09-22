---
status: open
filed: 2026-09-21
---

# WSMIP065's session start has run in SAFE MODE, with no guards, since 2026-09-17

**Machine-local, and every session on this box since Wednesday has started blind.** The latch file
`~/.bugarach-hook-running` was written at **2026-09-17 10:05** and has never been cleared. While it
exists, the vendored session-start hook skips the whole briefing so a slow run cannot take a session
down — and prints, in its own words:

> NO GUARDS RAN: unpushed/uncommitted work, branch-moved, live MATLAB and the session board were all
> skipped. **A quiet startup is NOT a clean one.**

So for four days no session on WSMIP065 has been told about uncommitted work in a worktree, a moved
branch, a live MATLAB process, or what the board says is claimed. The last of those is the one that
has cost this repo real work before: the local board is a precondition for working, and the digest
is how a session learns what the others are holding.

## It is not a hang — the briefing finishes, just too late

The hook recorded where the time went. Elapsed time as each section **began**:

| section | began at | took |
|---|---|---|
| settings skip-worktree | 5 s | ~0 s |
| **unpushed-work alarm** | 5 s | **17 s** |
| branch-moved check | 22 s | 7 s |
| live MATLAB check | 29 s | 6 s |
| tail: worktrees / recent commits | 35 s | 1 s |
| tail: session board | 36 s | 3 s |
| done | **39 s** | against a 20 s budget and a 45 s deadline |

The hook's own guidance is that the lever is the biggest gap, and it is the **unpushed-work alarm**:
17 of the 39 seconds. It walks every worktree, and on 2026-09-21 this machine had **31** of them in
`git worktree list`. The briefing reached its end; the session that spawned it gave up first.

## Do NOT just clear the latch

The hook says so directly: *"Clearing the latch alone changes nothing; the next start will be just
as slow."* And do not raise the `settings.json` timeout either — the harness aborts the whole startup
handshake at a hardcoded 60 s that this hook shares with authentication and the network. The fix is
to cut work out of the slow section.

## What would close it

1. **Reap spent worktrees.** 31 is far more than are in flight; each one costs the alarm a `git status`.
   `tools/merge_when_green.sh` reaps the worktree it is run from, so worktrees survive when a merge is
   run from the primary checkout — which is exactly what happened three times on 2026-09-20/21.
2. **Make the alarm cheaper per worktree**, or bound it: check the N most recently touched and say how
   many were skipped, rather than walk all of them inside a fixed budget.
3. Then clear the latch and confirm a full briefing completes inside its 20 s budget.

## A second startup defect, seen the same morning

The trimmed wrapper also reported: *"could not trim the board dump (reason 3) — the markers it keys on
have moved."* So even a full briefing would currently deliver the **untrimmed** board — which is the
60 kB payload the wrapper exists to avoid, and which the harness has refused before. Check
`tools/session_start_trimmed.sh` against `.claude/hooks/session-start.sh` in the same pass.
