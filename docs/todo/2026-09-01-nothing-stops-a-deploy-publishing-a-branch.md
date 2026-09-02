---
status: open
filed: 2026-09-01
owner: unassigned
---

# Nothing stops a deploy from publishing someone else's branch

`npm run deploy` runs `predeploy` → `tools/build_site.py` → `wrangler deploy`,
and every step of that operates on **whatever tree it is run from**. Nothing
anywhere asks whether that tree is `main`.

Found while preparing the deploy that `DEPLOY_HOLD.md` is currently holding.
The primary checkout was sitting on another session's branch —
`declare-instrument-families` at `ee551e3`, several sessions run against this
repo at once and one of them had left it there. Running `npm run deploy` from it
would have published a build of that branch to `bugarach.tonydefazio.com`, and
nothing in the path would have said a word.

## Why the existing stamp does not catch it

`build_site.py` already stamps the build with `git rev-parse --short HEAD`, and
`stale_payload_warning()` compares `site/`'s stamp against `HEAD` — so a *stale*
payload is caught. That check is about the payload lagging the tree. **A build
from the wrong tree is perfectly self-consistent**: HEAD is `ee551e3`, the stamp
says `ee551e3`, the bytes match, and every guard is satisfied.

`tools/site_staleness.py` compares the **live** page's stamp against
`origin/main`, so after the fact the stamp is at least recoverable — the page
would say it was built from a commit that is not on `main`. But that is a check
someone runs later, on a page readers already have.

## The fix does NOT belong in the build

The obvious move — refuse in `build_site.py` when `HEAD` is not on `origin/main`
— is wrong, and the repo now contains the proof. `tests/test_site_pages_render.py`
(#441) builds the real site in a fixture, which means **CI builds the site on
every pull request branch**. A build-time refusal would fail every PR. Local
builds on a feature branch are legitimate and routine for the same reason.

Building on a branch is normal. *Publishing* from one is the mistake, so the gate
belongs at the deploy step:

- [ ] A preflight — `tools/preflight_deploy.sh` or equivalent — run between the
      build and `wrangler deploy`, refusing unless `HEAD` equals `origin/main`
      after a fetch, and the working tree is clean. With an escape hatch that
      somebody has to type, the way `build_site.py` has `--allow-degraded` and
      `guard_branch.sh` has `ALLOW_MAIN_COMMIT=1`: a gate with no override gets
      deleted the first time it is genuinely in the way.
- [ ] Consider whether the *published page* should carry the branch as well as
      the sha. A stamp reading `ee551e3` is only diagnostic to someone who
      thinks to check whether that commit is on `main`.

## Why this is filed rather than fixed

The gate would go into the one path that cannot be rehearsed. `npm run dry` stops
before the upload, so a preflight can be tested up to the point where it matters
and no further, and the first real exercise of it would be the deploy it is
supposed to protect. Adding an untested gate to the publish path immediately
before publishing is how a routine deploy becomes an incident.

**Handled operationally for the deploy that is pending**: build from a worktree
pinned to `origin/main`, and check `git rev-parse HEAD` against
`git rev-parse origin/main` before uploading. That is the preflight, run by hand,
which is also the right way to find out whether it is the correct check before
mechanizing it.

## Related

- `docs/DEPLOY_HOLD.md` — the hold this was found under.
- `docs/deploy.md` — the runbook, which says to serve and walk the payload but
  says nothing about which commit it came from.
- [`2026-08-20-nothing-publishes-the-site-so-it-goes-stale.md`](2026-08-20-nothing-publishes-the-site-so-it-goes-stale.md)
  — the other half: that one is about the site falling behind `main`, this one is
  about it getting ahead of `main` in the wrong direction.
