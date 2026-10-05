---
status: open
filed: 2026-09-21
---

# On WSMIP065 the Bash tool starts with no `python3`, no `git` and no coreutils

**Machine-local, and it will bite the next session on this box.** A Claude Code session on WSMIP065
(Windows 11, Git Bash at `/usr/bin/bash`) gets a Bash tool whose default `PATH` finds none of:

| command | default Bash tool | where it actually is |
|---|---|---|
| `ls`, `head`, `wc` (coreutils) | `command not found` | `/usr/bin` — present, just not on the `PATH` |
| `git` | `command not found` | a per-user install, `%LOCALAPPDATA%\Programs\Git\cmd` |
| `python3` | `command not found` | no `python3` anywhere; Windows Python answers to `py` and to each venv's `python.exe` |

PowerShell on the same machine sees `git` and the venvs fine, which is why a session can go a long way
without noticing.

## Why it matters more than an inconvenience

**`tools/merge_when_green.sh` calls `python3`** twice (lines 98 and 290; bash reported the second at
292, where its quoted script ends) to parse the PR's check status.
On 2026-09-20, with `python3` missing, it polled for its full 40-minute timeout, could not read the
checks, and **declined to merge** PR #674 — although all three CI legs had passed.

That was the gate working: it fails closed rather than merging blind. The danger is the next step. A
session that watches it refuse a green PR is one command away from `gh pr merge`, which is the exact
bypass the script's own header was written to prevent — every PR once merged about 90 seconds before
its own CI finished. **A gate that fails for environmental reasons trains people to route around it.**

## What was done to get through, and why it is not the fix

The session put a two-line `python3` shim in its own scratchpad — a script that `exec`s the primary
checkout's venv Python — and prepended `/usr/bin`, the Git directory and the `gh` directory to `PATH`
in each Bash call. Then `merge_when_green.sh` verified the checks itself and merged. That is session
scaffolding: it lives in a temporary directory and dies with the session.

## What would close it

Pick one, and prefer the first:

1. **Make the scripts not need `python3` by that name.** `merge_when_green.sh` could try `python3`,
   then `python`, then `py -3`, and say which it used — the same resolve-don't-assume pattern the
   murderboard skill uses for its own paths. That fixes it on every Windows box, not just this one.
2. **Fix this machine's Bash `PATH`** in the profile the tool sources, adding `/usr/bin` and the Git
   `cmd` directory, and a `python3` that resolves to a real interpreter.

Either way, add a check that fires: a line in the session briefing that runs `command -v python3 git`
under the Bash tool and says so when either is missing, so the next session learns it at startup
rather than 40 minutes into a merge.
