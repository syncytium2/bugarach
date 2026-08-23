# Git workflow — how work reaches `main`

The full version. `CLAUDE.md` carries one pointer to this file and no detail, on
purpose: a rule that lives only in `CLAUDE.md` is a rule that will eventually be
missed (`docs/session_protocol.md`, "Durable knowledge lives in git"). Where a
rule here can fire by itself, it does — those are named inline.

## The rule

1. Branch. Push the branch immediately (`git push -u origin <slug>`), so the work
   is durable on `origin` before anything else happens.
2. Open a PR.
3. Land it with **`bash tools/merge_when_green.sh <pr>`**.
4. Never commit directly on `main`.
5. **Cleaning up after yourself is step 3's job now.** `merge_when_green.sh`
   removes the worktree it just merged, so an ordinary landing leaves nothing
   behind; `--no-reap` opts out. See "Worktrees rot" below for the ones that
   leaked before this existed — and note that `worktree_sweep.sh --apply` is
   **not** the way to collect them today.

## What is mechanized, and what is still prose

| rule | how it fires | if it stops working |
|---|---|---|
| never commit on `main` | `tools/guard_branch.sh`, run from `.githooks/pre-commit` | `tests/test_branch_guard.py` fails |
| don't merge a PR whose checks have not passed | `tools/merge_when_green.sh` | `tests/test_merge_gate.py` fails |
| remove your worktree once its PR has landed | `tools/merge_when_green.sh` reaps it on the way out | `tests/test_merge_gate.py` fails |
| **one PR per theme** | *nothing — still prose* | — |
| content rules (personal paths, RNG, …) | `tools/sapper.py`, hook + CI | `tests/test_sapper.py` fails |

The hook needs `git config core.hooksPath .githooks` once per clone. That is the
one link in the chain still made of memory; the CI-side copies of the same checks
are the backstop.

## Why merging needs its own script

`gh pr merge --auto` waits for **required** status checks. With no branch
protection nothing is required, so it merges instantly and the PR gates nothing.

That was live here for a whole session: every PR merged **~90 seconds before its
own CI finished**. All of them passed, so nothing broke and nothing looked wrong.
The tell — `gh pr view N --json autoMergeRequest` returning `null` — was on screen
each time and got read past.

`merge_when_green.sh` does the waiting and verifying itself, and **fails closed
when it finds no checks at all**. That is the important behaviour: zero checks is
exactly the condition that produced the bug, and an absent gate is
indistinguishable from a passed one unless absence counts as failure.

Verified on the PR that introduced it: CI finished 23:33:19, merged 23:33:41 —
22 seconds *after*, on the same commit.

## Why a branch guard rather than a note

"Never commit on main" was already written in two places (`CLAUDE.md`, the
session protocol) and was followed only because someone happened to remember.
`guard_branch.sh` refuses the commit instead, with an explicit one-shot override
(`ALLOW_MAIN_COMMIT=1`) — a guard with no escape hatch gets disabled wholesale
the first time it is genuinely in the way, and then protects nothing.

## What is still weaker than it looks

`merge_when_green.sh` only governs merges that go through it; a session calling
`gh pr merge` directly walks past it. Server-side branch protection is the real
fix and needs repo-admin rights — see
[`todo/2026-08-12-enable-branch-protection-on-main.md`](todo/2026-08-12-enable-branch-protection-on-main.md).
It is an improvement to make, not a prerequisite for being safe today.

## One PR per theme

A PR is a unit of review, not a unit of work. Several related commits — a
vendored tool plus its wiring plus its docs — belong in one. Six PRs for one
afternoon of related doc edits is fragmentation, not rigour. **Not mechanized**;
this one is still a judgement call, and is listed as prose above so that is
visible rather than assumed.

## Stopping mid-task

Push a WIP branch (`wip/<slug>`) and write `HANDOFF.md` at the repo root — what is
in flight, the exact next step, how to verify — then push that too. Delete it when
the task completes. No handoff file on `main` means nothing is in flight.

## History

Never rewrite pushed history (filter-repo, rebase of pushed commits, force-push)
without restating what will be destroyed and getting explicit confirmation in
words. A bare menu-choice reply is not consent (near-miss 2026-08-11). Merging a
PR is not a rewrite; merging your own feature branch is fine.


## Worktrees rot, and the cost is not disk

Several sessions run at once and each takes its own worktree, which is right.
Nobody removes them afterwards, which is understandable: the session that could is
the one that has just finished and is closing down. On 2026-08-20 the count
reached **39 worktrees and 81 local branches**, of which 22 and 66 were finished
work.

**A live worktree and an abandoned one look identical.** That is the whole cost. A
session scanning the list to find out who else is working cannot tell last week's
merged branch from a colleague mid-edit, so it either stomps or freezes. Both
happened in a single day: one session read a worktree that was being written to as
"unpushed and at risk", and another concluded nobody was working on CI while
somebody was.

The list is only worth reading if presence *means* something.

**The leak is fixed at the source, not swept up afterwards.** `merge_when_green.sh`
blocks until the PR lands, which makes it the only process awake at the second a
worktree becomes garbage — so it removes that worktree itself, on the way out. It
removes exactly one: the one you are standing in, on the branch you just merged,
verified merged and clean. It asks nobody's intent but yours.

That matters because the alternative cannot. `worktree_sweep.sh` judges *other
people's* directories, by git state alone, and it reads neither session board — so
a worktree that is merged, clean and idle may still carry an ACTIVE claim from a
session about to open its next PR from it. On 2026-08-23 its dry run offered 27,
at least three of them claimed. **Do not `--apply` it** until it reads the board
(`docs/todo/2026-08-23-the-worktree-sweep-does-not-read-the-board.md`); to collect
the backlog, remove your own by name.

```
bash tools/worktree_sweep.sh            # report; changes nothing
bash tools/worktree_sweep.sh --live     # who is in a worktree RIGHT NOW
```

Its refusals are still worth knowing, because the reaper shares the shape of
them: uncommitted changes, a detached HEAD, a branch not yet an ancestor of
`origin/main`, and — the one the reaper checks first — a branch that is not the
thing that just merged.

**Why the moment matters.** Half the worktrees on this machine were used for under
twenty minutes — made for one task, one PR, never touched again. Anything deferred
to "session end" is deferred past the end of the only thing that knew about it,
which is why step 5 used to be prose and why the tree filled up anyway.

The full shape, measured 2026-08-23 over the 27 non-primary worktrees (creation to
last write, in minutes): 13 under 20, 1 between 20 and 60, 2 from 1–4 h, 7 from
4–24 h, 4 over a day. Median 37, mean 825 — **the mean describes no worktree that
existed**, and this document said "median ten minutes" until a murderboard
recomputation showed that was the short mode quoted as the whole.
