---
status: open
filed: 2026-09-21
---

# The in-flight guard watches `HANDOFF.md` and none of the thread-named root handoffs

## What it is

`tests/test_handoff_is_honest.py` resolves exactly one path — `ROOT / "HANDOFF.md"` — and skips
when it is absent. Every check in it is therefore blind to `HANDOFF-<slug>.md`, which is the form
[`docs/handoffs/README.md`](../handoffs/README.md) actually documents (*"a session stopping mid-task
writes `HANDOFF-<slug>.md` at the repo root"*) and the form all the live ones use.

So the two guarantees the guard provides —

1. a root handoff **names the PR** it says is in flight, and
2. **not every** PR it names has closed

— hold for one filename and no other.

## What it cost, measured on 2026-09-21

Seven handoffs were at the root. Two were spent: the generically named `HANDOFF.md`, whose only
in-flight item was a PR opened 18 days earlier, and `HANDOFF-evaluate-sliding-detectors.md`, which
its own successor had already declared superseded *and* had said in terms should move to
`docs/handoffs/` once `full-search` landed. `full-search` landed on 2026-09-17. The file was still
at the root four days later, because nothing checked it — and the one file that *was* checked
passed only because its stale PR happened to still be open.

That is the four-day false positive `docs/handoffs/` exists to prevent, at five times the scale,
and the guard written to stop it could not see it.

## Why this is not a one-line fix

Globbing `HANDOFF*.md` gets the coverage, but the two checks do not transfer unchanged:

- **Naming a PR is not universal.** A thread-named handoff can be honest while naming no PR at all
  — a run is in flight, a question is with the producer, a decision is with Tony. `HANDOFF.md`
  could be held to "name the work" because it was the generic file. Held to a glob, check 1 would
  fail several honest handoffs. It probably has to become: name a PR, **or** name what else is in
  flight in a form the test can read.
- **"Every PR closed" is the right rule and needs a second trigger.** The sliding-detectors file
  named no PR; what retired it was a *branch* landing. A check that asks "is the branch this file
  is about an ancestor of `main`?" would have caught it on 2026-09-17.

## What would close it

A guard that covers every `HANDOFF*.md` at the root, with a rule per file that can be satisfied by
a PR, a branch, or a named non-code blocker — and that fails, as this one already does under
`BUGARACH_REQUIRE_PR_API=1`, rather than skipping when it cannot tell.

⚠ Whatever it becomes, it must not make the honest case expensive. Five live threads legitimately
sat at that root on the day this was filed, and a guard that nags about them is a guard someone
switches off.
