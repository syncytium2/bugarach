# A SessionEnd hook, and why every check in it caught something real tonight

> ## ⚠ NOT MURDERBOARDED — Tony's explicit call, 2026-08-30: *"create it as a handoff. do not murderboard."*
>
> This is a design sketch written at the end of a long session, preserved because
> the alternative was losing it in a transcript. **The checks below were each
> verified against this repo on 2026-08-29/30** and the incidents are real. The
> *framing* has had no adversarial pass. Treat the check list as the reliable
> content and the prose around it as unreviewed — the same split
> `HANDOFF-bench-background.md` used for the same reason.

**Nothing here is built.** No hook exists, no settings key was added for it. The
one hook that *was* built and is live is a different thing: the ambiguous-reply
hook, described at the end.

## Why

Tony, 2026-08-30: *"prep for end of session. acknowledge worktree, branch, repo
hygiene. advise if handoff needed. this should be the end of session hook."*

The prep was done by hand, and doing it by hand is what makes it optional. This
ecosystem's own conclusion, twice over (sapper, the SessionStart hook): **a rule
that depends on being remembered is not a gate.**

## The checks, and what each one caught

Every row is something that was actually wrong on this machine at 05:00 on
2026-08-30, found by running the check by hand:

| check | what it caught |
|---|---|
| worktrees dirty or unpushed | a throwaway eval worktree left mid-merge, staged and uncommitted |
| local branches with commits not on `origin` **and no remote** | **three branches stranded on this machine** — `sweep-reads-the-board`, `the-collision-repeated`, `the-width-note-went-stale`. Flagged in the session-START briefing hours earlier and still there |
| worktrees whose branch is already an ancestor of `main` | nine dead checkouts. Removing them took the board from 25 worktrees to 15 |
| open PRs: mergeable state, CI state, **auto-merge armed on something DIRTY** | #402 sat with auto-merge armed on a branch that could not merge — it would have waited forever, looking healthy |
| root `HANDOFF.md` names PRs that are all still open | two of its five had merged; its own test only fires when the **last** one closes, by design, so two-of-five is invisible to it |
| is `main` currently green | **it was red.** Both date gates failed because a viewer edit on the 29th squash-merged at 03:52Z on the 30th. Nobody's mistake, and nobody had noticed |

Six checks, six real findings, one session. That is the argument.

## Shape

**Where:** `~/.claude/settings.json` + `~/.claude/hooks/session-end-hygiene.sh`.
User-level, so it fires in every repo on this machine **including ones that do
not exist yet** — Tony, 2026-08-30: *"This should propagate to all repos and new
ones too."* Nothing vendored per repo, nothing to keep in sync.

**Report, not block.** `SessionEnd` fires as the session closes; it cannot ask
anyone to fix anything. Its job is that the next session and Tony both find out.

**Two layers, because repos differ.** bugarach has sapper, a darkroom, a deploy
and two boards; another repo has none of that.

- **Generic core** in `~/.claude/hooks/`: git hygiene, PR state, handoff honesty.
  Pure `git` and `gh`, no project knowledge, works anywhere.
- **Optional per-repo extension**: if `.claude/hooks/session-end-local.sh` exists,
  run it and append its output. bugarach's would add `sapper --all`,
  `site_staleness.py`, and whether this session's blocks on the two boards were
  released. A repo without one loses nothing.

## Failure discipline, from what bit tonight

- **Exit 0 always.** A hook that errors at session end is a hook someone disables.
  The ambiguous-reply hook already follows this and it is not optional.
- **Time-box every `gh` call.** A network stall must not hang the exit.
- **Write findings to a file, not only stdout.** Session-end output is the least
  read text there is.
- **Say "checked, clean" rather than printing nothing.** Silence and "the check
  did not run" look identical — the same rule `run.json`'s roster is built on.

## The honest limit

`SessionEnd` reports after the fact. It would have *told* Tony about the three
stranded branches; it would not have pushed them. Catching it mid-session wants a
`Stop` hook, which is noisier and needs its own argument. Do not let this design
imply it prevents anything — it makes a bad exit visible, not impossible.

## What is already live, and is not this

`~/.claude/hooks/ambiguous-reply-confirm.sh`, wired into `~/.claude/settings.json`
as a `UserPromptSubmit` hook on 2026-08-30. It fires on short replies —
`don't get 4`, a bare number, `yes`/`go`/`no` — and injects a reminder to read
back the *consequence in different words* before acting on anything expensive.

It exists because *"don't get 4"* and *"i don't get 1"* both mean **I do not
understand item N**, and both were read as **do not do item N**, by two different
sessions on one day. One of them wrote its misreading into a durable handoff as a
ruling. Tony, 2026-08-30: *"if you repeat the question differently and I have the
same answer then we should be on the same page"* — hence a paraphrase rather than
an echo, which is the part that makes it a test rather than a nag.

Tested to fire on nine ambiguous shapes and stay silent on every real instruction
from that session.

## Also still owed

- **`docs/decisions.md`** — a light log: question asked, the answer verbatim, how
  it was interpreted. So a misread shows up as a wrong row rather than as prose
  nobody questions. Not written.
- **A sapper rule** refusing a commit whose durable doc quotes a person as a
  decision without the question attached. That is the hard gate; the hook only
  nudges. Filed, not written.
- **The misquote in
  [`2026-08-28-the-winner-stopped-changing.md`](2026-08-28-the-winner-stopped-changing.md)** —
  *"don't get 4"* stands there as a ruling. Correcting it needs that branch, and
  is described in
  [`../todo/2026-08-30-what-landing-the-fitted-background-actually-costs.md`](../todo/2026-08-30-what-landing-the-fitted-background-actually-costs.md).
