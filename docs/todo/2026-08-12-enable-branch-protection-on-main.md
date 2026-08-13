---
status: done
filed: 2026-08-12
---

# Enable branch protection on `main` — the PR policy currently gates nothing

> **DONE 2026-08-13.** Tony authorised it and it is live: required checks
> `test (3.11)/(3.13)/(3.14)`, no required reviews, `enforce_admins=false`,
> force-push disabled. Verified by reading the protection back from the API.
> The rest of this file is kept as the record of why, and of the failure that
> prompted it.

## The state of things

`CLAUDE.md` says work lands on `main` through a green PR, and justifies it: CI
runs on `push:[main]` and `pull_request`, so a direct push to `main` gets the
commit in *before* CI can object. A PR was supposed to fix that.

It does not, because **`main` has no branch protection**. With no required status
checks there is nothing for `gh pr merge --auto` to wait on, so it merges
immediately. Measured over one session — every PR merged **~90 seconds before its
own CI finished**:

| PR | merged | its CI finished |
|---|---|---|
| 1 | 21:56:07 | 21:57:38 |
| 4 | 22:08:23 | 22:09:54 |
| 5 | 22:17:44 | 22:19:19 |
| 6 | 22:27:43 | 22:29:17 |

All four passed, so nothing broke and nothing looked wrong. That is luck, not a
gate — the effective behaviour was identical to pushing straight to `main`, with
PR ceremony on top.

The tell was visible and got read past: `gh pr view N --json autoMergeRequest`
returned `null` every time. Armed auto-merge names a merge method.

## The fix — needs repo-admin rights

```bash
gh api -X PUT repos/syncytium2/bugarach/branches/main/protection \
  -f "required_status_checks[strict]=false" \
  -f "required_status_checks[contexts][]=test (3.11)" \
  -f "required_status_checks[contexts][]=test (3.13)" \
  -f "required_status_checks[contexts][]=test (3.14)" \
  -F "enforce_admins=false" \
  -F "required_pull_request_reviews=null" \
  -F "restrictions=null"
```

Choices in that call, and why:

- **`required_pull_request_reviews=null`** — no human reviewer exists. Requiring
  one would deadlock a repo worked by one human and several AI sessions.
- **`enforce_admins=false`** — leaves Tony an override if CI is broken or GitHub
  Actions is down. Protection that can lock the owner out of their own `main` is
  a worse failure than the one it prevents.
- **`strict=false`** — does not force a branch to be up to date with `main`
  before merging. `strict=true` adds a rebase-and-wait cycle every time `main`
  moves, which for a solo operator is friction without a matching benefit.

After enabling, confirm it actually works — the point of this item is that an
unverified gate is the failure mode:

```bash
gh api repos/syncytium2/bugarach/branches/main/protection --jq '.required_status_checks.contexts'
# then on the next PR:
gh pr view <N> --json autoMergeRequest   # must NOT be null
```

## Not blocked on this — the client-side half already landed

Filing a todo that says "a human should run a command" is the same failure this
document is about: a gate that depends on somebody remembering. So the half that
needs no permissions was built instead — `tools/merge_when_green.sh` waits for a
PR's checks, verifies them, and **refuses to merge when no checks are found**,
which is precisely the condition that made `--auto` a no-op. It self-tests and
runs in CI via `tests/test_merge_gate.py`.

That script is **weaker** than branch protection and does not replace it: it only
governs merges that go through it, so a session calling `gh pr merge` directly
still bypasses it. Server-side protection is the real fix — but it is now an
improvement, not a prerequisite for being safe.

## Why the server-side half is filed rather than just done

Changing branch protection is a settings change on a public repo and needs
admin rights; it was declined to the session that found the problem, correctly —
it is not the kind of thing an agent should do to someone's repo unannounced.

## The lesson worth keeping

This is the **skipped gate** from [`../simulation_plan.md`](../simulation_plan.md),
committed in the same session that documented it: a gate written as a sentence
and shipped without its mechanism. The doc argued that a named gate gets skipped
unless something fails closed — and then the policy it was written alongside did
exactly that. Worth remembering that knowing the failure mode is not protection
against it.
