---
status: open
filed: 2026-08-26
---

# `murderboard_revendor.py --selftest` fails in every consumer and passes upstream

> **Not murderboarded** — a finding for sessions in this tree. Both failures reproduce in
> one command. Moved here from
> [the hook audit](../handoffs/2026-08-25-the-session-hooks.md) item 3, which is a dated
> record and the wrong place for a live item.

```
$ python3 tools/murderboard_revendor.py --root . --selftest
FAIL this file's docstring states the recomputed count (11 vs 12)
FAIL this tool rewrites none of them (no stamp on its eligible line)
FAILED — 2 problem(s)
```

Zero failures in the upstream clone at `~/Developer/murderboard`.

## Why it fails here and not there

Both checks assert **upstream's own file shape**. A vendored copy carries one extra
stamp — its own `vendored from syncytium2/murderboard @ <sha>` line — on precisely the
line the tool is permitted to rewrite. So:

- the stamp-shaped-string count reads **12** against a docstring that says **11**, and
- the *"this tool rewrites none of them"* case rewrites exactly one.

The second failure predates PR #307 and is not something that re-vendoring introduced.

## Why it matters more than two red lines

`murderboard_freshness.sh` is a **gate**: the murderboard skill treats a stale process as
a hard stop, and it stopped a real run on 2026-08-25 until the family was re-vendored.
The selftest is the thing that would tell a consumer its vendoring machinery still works.
It cannot, because it only passes in the repo that does not need it. A check that is green
only at home is the same shape as the defects this repo keeps finding: it measures
something adjacent to the question and reports success.

Nothing is blocked today — the freshness gate is green and the eleven pytest checks pass.

## Do not fix it downstream

`tools/murderboard_revendor.py` is vendored, and CLAUDE.md forbids editing a vendored file
in place: a file edited here cannot be re-copied when upstream moves. This wants sending
back to `syncytium2/murderboard` as a portability bug, with the suggestion that the
selftest derive its expected count from the file it is scanning rather than from a
docstring constant, and that the "rewrites none" fixture be built without a vendor stamp
on its eligible line.

Related deliberate deviation already recorded in CLAUDE.md: `fetch_paper.py` is **not**
vendored here because it hardcodes a personal library path
([the todo](2026-08-12-vendored-lit-tool-carries-personal-paths.md)).
