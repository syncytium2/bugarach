---
status: done
filed: 2026-08-12
---

# DONE — freshness-gate cross-family bug, reported and fixed upstream (murderboard)

`murderboard_freshness.sh` gives a **confident, wrong verdict** for any vendoring
family whose slug `gh` cannot resolve. Found while wiring it here 2026-08-12;
still present at upstream `b2b2ba2` (checked, not assumed).

## The defect

`--label`/`--slug`/`--clone`/`--file` generalize the gate to any vendoring
relationship — the README advertises exactly that ("**Not murderboard-only**").
But the offline fallback list was never generalized with it:

```sh
# line 63-69 — fixed murderboard paths, does NOT vary with --slug
CLONE_CANDIDATES="
${MURDERBOARD_REPO:-}
$HOME/Documents/murderboard
$HOME/Developer/murderboard
...
```

`resolve_upstream()` tries `gh` and then falls through to `upstream_from_clone()`,
which walks that list. So a `--slug fam/other` query that `gh` cannot answer
returns **murderboard's** `origin/main` as `fam/other`'s upstream HEAD.

## Observed

```
$ gh api repos/syncytium2/interface2        -> 404
$ murderboard_freshness.sh --label session-protocol --slug syncytium2/interface2 \
    --file docs/session_protocol.md
--- !! SESSION-PROTOCOL IS STALE ---
   vendored: 9df9a16   upstream: 635c5a8   (via local-clone)
```

`635c5a8` was the local **murderboard** clone's HEAD. interface2's real
`origin/main` was `9df9a16` — the vendored copy was **current**. Passing
`--clone <interface2>` gives the right answer (`current (@ 9df9a16)`).

## Why it matters more than a wrong-answer bug

The header promises "**never a false 'current'**". Across families that promise
does not hold: the two HEADs are unrelated shas, so a coincidental match would
report current just as readily as this reported stale. And a **false STALE** is
its own harm — a gate that cries wolf is a gate that gets ignored, which is the
exact failure the tool was built to prevent.

## Suggested fix (upstream's call)

Derive the clone candidates from `--slug`'s repo name rather than hardcoding
`murderboard`, and/or refuse the clone fallback when `--slug` is non-default and
no `--clone` was given — returning 2 (undetermined) instead of an answer from
whatever repo happens to be on disk. Failing closed matches the tool's own stated
contract.

## Worked around here

`tools/check_vendor_freshness.sh` never checks the interface2 family without an
explicit `--clone` (from `$BUGARACH_INTERFACE2`), and reports UNKNOWN rather than
letting the gate guess. Remove the workaround once upstream fixes this — and drop
the WARNING block in that file at the same time.

## Also noticed

The local murderboard clone at `~/Documents/murderboard` was **4 commits behind**
its origin (`635c5a8` vs `b2b2ba2`), so the first vendoring attempt here pulled a
stale copy. The gate caught it — working as designed. Re-vendored from
`origin/main`. Worth a `git fetch` on that clone before anyone vendors from it
again.


---

## Resolved 2026-08-17

Fixed upstream in murderboard PR #13, vendored back here at `a46e255`.

The fix splits one list in two. Paths somebody **asserted** are the upstream for the
slug in play (`MURDERBOARD_REPO`, `--clone`) stay trusted — asserting them is what
those knobs are for. The built-in **guesses** are murderboard paths and are now
consulted only when the slug actually names murderboard. Any other family with an
unreachable upstream gets *cannot determine* rather than a confident verdict computed
from the wrong repository.

The selftest gained `clone guesses are slug-scoped`, and it was verified to fire:
reverting only the fix while keeping the case turns it red.

What this does **not** fix: `syncytium2/interface2` is still a 404, so files vendored
from it remain unverifiable — but they are now honestly unverifiable rather than
falsely current. That is the whole difference, and it is the one worth having.
