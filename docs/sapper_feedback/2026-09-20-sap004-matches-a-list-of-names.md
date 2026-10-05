# SAP004 matched a slash-separated list of names, not a path

**Filed 2026-09-20, from the chorus-collapse blind verify round.**

## What happened

A murderboard role report, archived verbatim under
`docs/reviews/chorus-collapse-verify-2026-09-20-roles/02-doi-or-die.md`, opened with the
reviewer declaring which tools it held. It mentioned that MCP server instructions for three
servers had been injected into its prompt, and wrote the three names slash-separated:

    <cloud-folder-name>/claude.ai-docs/bio-research

SAP004's pattern carries that cloud-folder name followed by a slash as one of its alternatives,
so the line matched and the commit was blocked. There is no path here — it is a list of three
names that happens to put a slash after the first one. (The name is spelled out in the archived
report itself, where it is a server name in prose rather than a path.)

## Why the rule is not the thing to change

SAP004 is a BLOCK rule on a public repository, and its own comment records why it is shaped the
way it is: an earlier version matched only the surname and the cloud-folder name, each with a
trailing slash, and was *believed* to cover personal paths — while a lowercase home directory
slipped through and sat in a public file for months. The comment's conclusion — *"a rule that covers the shape you thought of is worth less
than it looks"* — is the argument against narrowing it now on the strength of one false positive.
The cost of this miss is one rewritten separator. The cost of the miss it was widened to catch
was a personal path in a public repo.

So the fix applied was to the **text**, not the rule: the separators are now commas, and the
archived report carries a note saying so, because that file is evidence and a silent edit to
evidence is worse than the false positive.

## The open question, for whoever wants it

Two of the rule's alternatives — the cloud-folder name and the surname, each followed by a
slash — match a bare token rather than a path shape. The other two (`_UM`, and the
`/Users/<name>/` and `/home/<name>/` forms) are anchored. A tighter form for the first two would
require a preceding path character — a drive letter, a tilde, a slash, or a directory-ish word —
so that the real home-directory spellings still match while a bare list item does not.

**Do not make that change without measuring it against the incident it exists to prevent.**
`tools/sapper.py --selftest` proves every rule can fire; a narrowing needs a new selftest vector
for the lowercase-home case *and* for the Windows `Dropbox-<org>` symlink form described in
CLAUDE.md, or it re-opens the hole the current pattern was widened to close.

Frequency so far: **one** false positive, in the two months since the rule was widened. That is
not yet evidence of a problem worth the risk of touching it.
