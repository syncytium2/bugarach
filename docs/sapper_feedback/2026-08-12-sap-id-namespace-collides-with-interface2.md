---
rule: none-yet
status: open
filed: 2026-08-12
---

# `SAPxxx` IDs collide with interface2's, and both are cited bare

## What happened

While auditing interface2 for tooling to bring over (2026-08-12), I compared its
`tools/sapper.sh` rule set against bugarach's `tools/sapper.py`. The two are
independent implementations — bash/MATLAB-oriented upstream, Python here — which
is fine. What is not fine is that they share an ID namespace and mean different
things by the same IDs:

| ID | bugarach (`tools/sapper.py`) | interface2 (`tools/sapper.sh`) |
|---|---|---|
| SAP001 | MATLAB `prctile` matches no `np.percentile` mode | workspace clobber (`load(f)` into caller scope) |
| SAP002 | `default_rng` banned — parity needs `RandomState` | `getenv('HOME'\|'USERPROFILE')` |
| SAP003 | PySpike 0.9.0's `max_tau` cap is broken | hardcoded `/mnt/c/` |
| SAP004 | personal absolute path in a tracked file | `apv_dataDir` |

interface2 goes up to SAP020; bugarach has four.

## Why it is wrong

Both repos cite rules **by bare ID** in prose that a human or a session reads
outside the repo that defines it. bugarach's own `CLAUDE.md` says "sapper SAP004
blocks personal absolute paths" and `FOUNDATIONS.md` §2 says "`default_rng` is
banned in `src/` (sapper SAP002)". A session that has interface2's rule set in
context — increasingly likely, since bugarach now vendors from interface2 and
sessions read both — resolves SAP004 to `apv_dataDir` and SAP002 to a `getenv`
ban. Neither is wrong *there*; both are wrong *here*.

This is a documentation-integrity failure, not a detection failure: no check
misfires, but the prose that explains the checks silently means something else
to a reader standing in the other repo. That is the same class of problem as the
"ONLY needed to regenerate parity references" line corrected in `CLAUDE.md` this
session — a confident statement that is false from another vantage point.

## Suggested fix

Cheapest and least disruptive: **prefix the namespace**, `BUG001`–`BUG004` here
(or `SAP-BUG001`), and update the handful of citations. bugarach has only four
rules and three prose references, so the churn is small and it never has to be
paid again. Renumbering interface2's twenty is the wrong direction.

Alternative if renaming is unwanted: require every citation to name the repo
("bugarach SAP004"), and add a sapper rule that flags a bare `SAP\d{3}` in
tracked prose. That is more machinery for a weaker guarantee — the rule can only
catch citations inside this repo, and the confusion happens in readers who are
holding both.

Not urgent. Filed because it is exactly the kind of thing that is obvious now and
invisible in six months.
