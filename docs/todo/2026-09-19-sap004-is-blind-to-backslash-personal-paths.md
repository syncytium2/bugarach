---
status: open
filed: 2026-09-19
---

# SAP004 is blind to a personal path written with backslashes

**Found** on 2026-09-19, sizing up `tune-bench-comparison` for landing. Registered upstream
as armory finding 23, `a-guard-that-knows-one-slash`.

## What

SAP004 keeps usernames out of this **public** repo. Read its pattern in `tools/sapper.py`:
it lists a member-folder name, a cloud-sync folder name, and an absolute home-directory
form — and **every alternative ends in a forward slash**. The same path written for a
Windows or a WSL reader carries the same components, the same username, and matches nothing.

| the path a reader is handed | SAP004 |
|---|---|
| posix home form, `/home/<user>/runs/` | BLOCK |
| Windows drive form, `C:` then `Users`, `<user>`, `runs`, backslash-separated | silent |
| WSL UNC form, `\\wsl$\Ubuntu` then `home`, `<user>`, backslash-separated | silent |

**It is already collecting.** `HANDOFF-workstation-tuning.md` on `tune-bench-comparison`
carries a WSL UNC path with the username in it at line 682, unflagged, and that file is part
of what landing the branch would publish.

The exposure grows with use: both workstations are Windows machines whose run directories are
all of this shape, so every report written from one is a chance to publish a username.

## Why it is the same lesson twice

SAP004's own comment already tells this story once. The rule matched two folder names and was
believed to cover personal paths, until a lowercase home directory matched none of them — in a
file that had carried two such paths in this public repo from the day it was written. The
comment recording that fix says it plainly: *a rule that covers the shape you thought of is
worth less than it looks.*

Then the rule was widened to cover the shape someone thought of, again.

## The fix is not a one-character change, and the blast radius is measured

Widening to accept either slash flags **4 tracked files on `main`** that the current rule does
not, and at least two of those are legitimate and must keep working:

- `docs/windows_workstation_setup.md` — an env-var form naming the cloud folder, with no
  person's name in it. This is the **correct** way to write it.
- `tests/test_paths.py` — a fixture with a fake user name, which exists to test the resolver.

The other two are the 2026-09-12 blind-round review records, which are verbatim and must not
be edited to satisfy a rule (the SAP015 precedent in `docs/sapper_feedback/`).

So the rule has to separate *a path carrying a person's name* from *a path written the safe
way* — most likely by requiring an adjacent member-folder name rather than matching a bare
folder word — with per-rule `exclude` globs for whatever remains.

## A second, smaller defect found while filing this

**The first draft of this file was itself blocked**, three times, for quoting the rule's
pattern and its comment. The rule matches literal folder names, so any document that discusses
it contains them. That is not wrong of the guard, but it means the rule cannot be written about
without an exclusion or a paraphrase, and a paraphrase is what this file now is — which is
worse for the next reader, who has to go and read the pattern anyway. Worth an `exclude` for
`docs/todo/` and `docs/sapper_feedback/` when the rule is next touched.

## Closes when

`--selftest` proves the Windows, WSL and drive-letter forms each fire; `--all` is clean on
`main` with every exclusion commented; `tests/test_sapper.py` passes; and the reason is filed
in `docs/sapper_feedback/`.
