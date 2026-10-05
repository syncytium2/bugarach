---
status: open
filed: 2026-09-21
---

# Three commit subjects on `main` start with an invisible byte-order mark

Of the **1,756** commits on `main` as of 2026-09-21, exactly **three** have a subject line beginning
with U+FEFF, the Unicode byte-order mark. All three are one session's, from 2026-09-20:

| commit | subject |
|---|---|
| `d8c23a7` | The chorus-collapse page's blind round: three of six repairs do not survive it |
| `5e193ee` | Archive the citation, methods and adversarial role reports |
| `1bf31af` | Archive eight of the blind round's role reports as they arrived |

The character is invisible in most terminals and on GitHub, but it is really there: it shows in
`git log` as a stray glyph in some fonts, it breaks a `grep '^The'` over subjects, and this repo's
commit messages are presentation surface (FOUNDATIONS §8 — a stranger deciding whether to hire the
author reads them).

## How it got in

PowerShell 5.1's `Out-File -Encoding utf8` writes UTF-8 **with** a BOM. The session wrote each commit
message to a file that way and committed with `git commit -F`, and git kept the BOM as the first
character of the subject. Writing the file with `[System.IO.File]::WriteAllText(...)`, which is
BOM-free, fixed it from the fourth commit on.

## Fixing the three is Tony's call, not a session's

Removing them means rewriting commits that are already on `main` and in every clone — exactly what
CLAUDE.md forbids without restating what will be destroyed and getting explicit confirmation in words.
The cost is cosmetic; the remedy is destructive. **Leaving them is a reasonable answer**, and this
todo exists so that it is a decision rather than something nobody noticed.

## What would stop it happening again

Better than repairing three commits: a `commit-msg` hook that refuses a message whose first byte is
U+FEFF, beside the branch and board guards already in `.githooks/`. That turns a PowerShell default
into a refusal at the commit, on every machine, with no one having to remember it — the same reason
this repo prefers a check that fires over a line of prose. It is a sapper-shaped rule, but sapper is a
line matcher over the tree, so the hook is the right place for it.
