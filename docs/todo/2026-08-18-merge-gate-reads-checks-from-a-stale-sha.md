---
status: open
filed: 2026-08-18
---

# `merge_when_green.sh` counted checks from the previous commit and tried to merge

Observed 2026-08-18 on PR #109. Sequence:

1. Checks passed for head `d8ddbdd`.
2. A new commit `e6985dc` was pushed (the murderboard fixes).
3. `tools/merge_when_green.sh 109` printed **`3 check(s) passed; merging.`** and issued
   the merge — while CI for `e6985dc` had not started.
4. GitHub refused: `Pull Request is not mergeable`. Branch protection, enabled on
   `main` earlier the same day, was what stopped it.

```
merge_when_green: PR #109 — 3 check(s) passed; merging.
GraphQL: Pull Request is not mergeable (mergePullRequest)
merge_when_green: merge command failed
```

## Why this matters more than it looks

The gate exists because *"`gh pr merge --auto` waits for required status checks"* was
not available here — its whole purpose is to be the thing that will not merge an
unverified commit. In this instance it tried to, and the only reason it did not
succeed is a protection rule that had been added hours earlier and that the gate
does not know about. Run this same race yesterday and the merge lands.

The failure is not "checks were red". It is that the gate answered *"are this PR's
checks green?"* without asking *"green **for which commit**?"* — a check run is
attached to a SHA, and a PR's check list still shows the previous SHA's runs during
the window between a push and CI starting. That window is exactly when someone runs
the merge command, because they have just pushed.

## What to change

Read the head SHA once and require the checks to belong to it:

```sh
head=$(gh pr view "$PR" --json headRefOid --jq .headRefOid)
gh api "repos/{owner}/{repo}/commits/$head/check-runs" ...
```

and treat *"no check run exists for this SHA yet"* as **pending**, not as the
existing "no checks at all" case — the gate already refuses that one, and the
distinction between "this project has no CI" and "CI has not started for this commit"
is the whole bug.

Worth a `--selftest` branch too: the gate self-tests every other decision it makes,
and this one is now known to be reachable.

## Related

- [`2026-08-12-enable-branch-protection-on-main.md`](2026-08-12-enable-branch-protection-on-main.md)
  — protection is what caught this; it appears to be enabled now, so that todo may be
  closable. Verify before closing.
- The gate's own reasoning is in the header of `tools/merge_when_green.sh`, and
  `tests/test_merge_gate.py` is where the new case belongs.
