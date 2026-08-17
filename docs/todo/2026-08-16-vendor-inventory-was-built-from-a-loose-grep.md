---
status: open
filed: 2026-08-16
---

# The vendored-file inventory was wrong, and a grep for prose produced it

## What happened

Asked which files bugarach vendors, a session answered with `grep -rl "vendored from"`.
That matches **any line containing the phrase**, including a sentence *about* stamps.
It reported seven vendored files. There are six, and two of the reported seven were
never vendored at all:

- `docs/writing_conventions.md` — line 62 quotes a stamp as an example, inside a
  sentence explaining what stamps look like.
- `tools/check_vendor_freshness.sh` — bugarach's own wrapper, whose header
  *describes* the vendoring families it checks.

## The real inventory

A stamp lives in the **first two lines** — line 1 for markdown, line 2 for shell
(after the shebang). Checking only there:

| file | upstream |
|---|---|
| `docs/session_protocol.md` | interface2 |
| `.claude/hooks/session-start.sh` | interface2 |
| `docs/doc_review_process.md` | murderboard |
| `tools/murderboard_freshness.sh` | murderboard |
| `tools/murderboard_roster.sh` | murderboard |
| `.claude/skills/murderboard/SKILL.md` | murderboard |

**Two files from interface2, not three.**

## Why it is worth a todo rather than a shrug

The bad list was sent to an interface2 session as the basis of a proposal to move
canonical ownership of those files. That session did careful work against it and
returned three corrections — **two of which were artifacts of the bad list**:

1. *"You vendored interface2's repo-specific superset rather than the vendorable
   core."* **False.** bugarach's copy is byte-identical to the core, and its stamp
   names the source file explicitly. Verified by diff.
2. *"`docs/writing_conventions.md` does not exist upstream."* **True and moot** — it
   was never vendored. The finding was real; the premise was ours.
3. *"The stamped sha is not on interface2's mainline."* **False.**
   `git merge-base --is-ancestor` puts it on `main`. It is *also* on feature
   branches, which is what branching does.

So a loose grep in one repo produced a wrong analysis in another, committed to a
file there, in under an hour. The receiving session did nothing wrong; it reasoned
correctly from what it was given.

## The same failure twice in one hour, from opposite directions

The interface2 session diagnosed its own error and it pairs exactly with ours.

It answered *"is this sha on main?"* with `git branch -a --contains <sha> | head -5`,
saw five feature branches, and concluded main was not among them. **53 refs contain
that commit.** `main` was below the truncation. `merge-base --is-ancestor` — which
answers the actual question with a boolean — returns true.

Set the two side by side:

| | the instrument | how it lied |
|---|---|---|
| ours | `grep -rl "vendored from"` | matched prose *about* stamps as though it were a stamp |
| theirs | `git branch --contains \| head -5` | truncated the list above the answer |

Neither tool malfunctioned. Both were **the wrong shape for the question** — one
over-matched, one silently truncated — and both produced a confident answer with no
signal that anything was missing. Their phrase for it is the right one: *a check
that cannot see the answer reporting the answer absent.*

Worth noticing that this is the same defect the session spent all day finding in
other places: a load-boundary check that covers one of two producers, a validator
with no power over the values it validates, a freshness gate whose fallback answers
from the wrong repository. **A check that cannot fail is the recurring bug in this
estate, and it turns up in one-line shell commands as readily as in architecture.**

Practical form: when a lookup answers a yes/no question, use an instrument that
returns yes or no. `--is-ancestor` over `--contains | head`. A positional test over
a substring match. If the output is a list you are about to eyeball, ask what it
would look like if the answer were absent — and whether you could tell.

## What to do

- **When enumerating vendored files, check the first two lines, not the whole
  file.** A stamp has a position, and that position is what distinguishes it from
  prose about stamps.
- **Consider making this mechanical.** The check is a presence test rather than a
  pattern match, so it is the wrong shape for sapper, whose rules fire on a bad line
  appearing. A test in the suite fits: assert every file the freshness tooling
  believes it governs actually carries a stamp where a stamp belongs, and that no
  other file claims one.
- **The consolidation proposal shrinks.** It concerns two files, and the interface2
  session reports one of them — the session-start hook — as actively contested
  upstream, with an open postmortem and a briefing running 31–55 s against a 45 s
  timeout. That one should not move while it is live.
- **Ownership is not ours to move by conversation.** interface2 records its
  canonicality in a decision record, made against a named alternative that was
  rejected on stated grounds. Changing it wants a superseding record, not a
  session-to-session handoff — the interface2 session was right to decline, and its
  reason generalizes.

## Related, and unresolved

The cross-session message gate written this session
(`~/.claude/hooks/require-commit-before-message.sh`, wired from user settings) is
**not in any repository**. It enforces durability and is not itself durable — lose
that directory and it disappears silently, since a missing hook command fails open.
Where it should live is open: vendored per repo, or one tracked copy referenced by
absolute path. See
[`2026-08-16-dt-does-not-travel-with-the-recording.md`](2026-08-16-dt-does-not-travel-with-the-recording.md)
for the same shape of problem in the detectors.
