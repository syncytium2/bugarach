# The session hooks: one delivered, one went silent, and one waves everything through

**Written 2026-08-25.** Not a root handoff — nothing here is half-done. This is the record
of a hook audit, the two fixes that landed from it, and four things left for whoever picks
them up. The root `HANDOFF.md` slot belongs to PR #305 and its ADR-0003 question; this does
not compete with it.

---

## The problem: a briefing that passed fifteen tests and reached nobody

`tools/session_briefing.sh` is the mechanism CLAUDE.md's first rule rests on. A session on
2026-08-13 spent a day reasoning from the textbook prior that TTX silences the field; the
hook exists so the facts that refute it arrive whether or not anyone opens
`FOUNDATIONS.md`.

On 2026-08-25 it emitted **17,568 bytes**. A `SessionStart` hook that size is not trimmed
to fit — the harness spills the whole thing to a file and injects a **~2KB preview**
instead. Going over is not "a bit less gets through"; it is "almost nothing does". Here is
where the cut fell:

```
byte      section                                              delivered?
─────────────────────────────────────────────────────────────────────────
    77    banner                                                  yes
   ~90    FOUNDATIONS §9 — the TTX fact                           yes, first ~20 lines
═══════   ═══ ~2,000B PREVIEW CUT ═══════════════════════════════════════
 6,138    ">> N items FINISHED and waiting on Tony"                no
 7,026    every open todo + feedback item · 9,838B, 56% of all     no
16,880    are the commit gates installed in this clone?            no
16,926    handover gates — "document deliverable -> /murderboard"  no
17,495    where darkroom output goes on this machine               no
17,569    "!! HANDOFF.md present — work is in flight"              no
─────────────────────────────────────────────────────────────────────────
```

Three things make this worse than a long log line.

**The in-flight alarm was last.** This script is the *only code* in the tree that reads
`HANDOFF.md` — six documents mention the convention; one file acts on it — and CLAUDE.md
rests "no handoff file on `main` == nothing in flight" on that one.
The alarm sat 15.5KB past the cut, so a root handoff could not have reached any session —
which is precisely the mechanism PR #305 was written to use.

**The alarm whose own comment says it prints "first, loudly" printed at byte 6,138**,
behind a 5.7KB extract. The design was recorded; the implementation had drifted from it.

**Fifteen tests were green throughout.** Every one asserted what the script *prints*.
`test_waiting_items_come_before_the_fifty_open_ones` is the sharpest: it asserts an
*ordering*, and passed — with both sides of the comparison past the cut.

The 2KB that did survive happened to carry the TTX fact, which is the single most
load-bearing item in the file. That was luck, not design. Reorder `FOUNDATIONS.md` §9 and
the same truncation stops being benign.

**This is the 2026-08-20 incident again, in the other hook.** The fix was built then —
budget, terse re-render, size canary, degrade loudly — and applied only to
`tools/session_start_trimmed.sh`, which delivered 6,809B cleanly that same morning while
its sibling in the same `settings.json` block went silent. `session_briefing.sh`'s header
argued against adopting it: *"COST: local only … deliberately NOT budget-gated."* That was
a claim about **runtime** cost, and it was true. The failure was never runtime.

## What landed

**[PR #306](https://github.com/syncytium2/bugarach/pull/306) — the briefing now fits.**
Merged to `main` 2026-08-25 as `8810566`.

- **Order.** The bounded alarms lead; `FOUNDATIONS §9` follows; the open-todo dump becomes
  a count. The alarms cost ~1.5KB together, so they survive a 2KB preview even if the
  budget machinery fails — ordering as a survival property, not a courtesy.
- **Budget** — `BUGARACH_BRIEFING_BUDGET_BYTES`, default 9,000. Two injections are known
  to have been spilled, 60,235B and 13,414B, and 6,809B is known to have arrived whole
  (the first two are recorded in `session_start_trimmed.sh`'s header; the third is this
  session's own canary). 9,000 sits under the smaller failure and over what the briefing
  costs with both a full §9 and a root handoff present, so the common case never degrades
  and the ladder is a backstop rather than the normal path.
- **Canary.** It prints its own size every run. The 2026-08-20 note ends *"Watch that
  number."* This hook had no number to watch, which is how it crossed the line unobserved.

17,439B → **8,068B**, or 8,820B with a root `HANDOFF.md`, whose alarm is now line 3. Seven
new tests assert what a session *receives* rather than what the script prints, including a
root handoff reaching the first six lines — driven in a throwaway repo, because forging
that file at this root would lie to every other session on the machine. Suite 1,340
passed, 13 skipped. sapper clear.

Those two sizes were measured in one tree at one moment and they move: the briefing reports
on the board, the todos and the handoff, so it tracks all three. That is what the canary is
for, and why the budget is enforced at run time rather than asserted once. The **17,568B**
at the top of this page is the only figure here that is not a re-measurement — it is what
the harness reported when it refused the injection.

**[PR #307](https://github.com/syncytium2/bugarach/pull/307) — the murderboard was stale**
(vendored `5e6b299`, upstream `94d720c`), which the skill treats as a hard stop, so this
handoff could not be reviewed until it was re-vendored. What we had been missing is not
cosmetic — two new rules for role 2, both written after a delivered attribution report
missed the same class twice:

- **Trace citations forward, not only back.** When a deliverable wraps someone's tool, the
  closest prior art for the *wrapping* is usually in that author's own later applied work.
- **Ask what the humans hold.** That case turned on an email that had sat in an inbox for
  four months, naming the two papers the report claimed as its own, while three independent
  review arms reached for radar, seismology and econometrics. "Nobody was asked" is now a
  residual warning in its own right.

Both bear directly on PR #292 and the `attribution-corrections` worktree, in flight now.

---

## Still broken — pick any of these up

### 1. The board guard cannot fail in the primary checkout

CLAUDE.md calls claiming *"a precondition for working, not a courtesy"* and says the gate is
mechanized. `tools/guard_local_board.sh` matches by **substring**: it greps the board for
the worktree's directory basename, then for its branch name.

```
$ grep -cF -- "bugarach" ../bugarach-worktrees/SESSIONS.md
267
$ bash tools/guard_local_board.sh ; echo $?      # from an unclaimed worktree
0
```

The primary checkout's basename is `bugarach`, which appears 267 times in a 3,000-line
board — in paths, in prose, in every other block. This session ran unclaimed for its whole
first hour and the gate said fine. The failure is not universal: a worktree with a
distinctive name genuinely does get refused. It is the primary checkout that can never be
caught, plus any worktree whose name happens to be a substring of something already on the
board.

**Fix:** anchor on the block heading — `### <host>/<worktree>` — instead of a bare
substring. Small change, but it will start *refusing* worktrees that currently coast, so
land it with a run over the live board first to see who it catches. Related and unresolved:
[claim before starting, not before committing](../todo/2026-08-20-claim-before-starting-not-before-committing.md).

**DONE 2026-08-26.** `verdict()` parses the heading and compares the identifier exactly
against the worktree's basename or its branch, and `tools/guard_local_board.sh --audit`
runs both the old rule and the new one over every live worktree so the blast radius can be
read before it lands rather than discovered at somebody's next commit.

The run this item asked for: **three of thirteen worktrees changed verdict, all three true
positives.** `bugarach (main)` — the primary checkout, which is the whole item.
`generator-revision-input` and `parameter-spec-v2` — both passing only because a session
that finished on 2026-08-20 had listed them under its own *Worktrees touched* line. Someone
else's record of having been there is not this session's claim to be there now. No worktree
holding a real block was refused, and the escape hatch is unchanged.

That also repairs a **dead alarm in the session briefing**: §4's "this worktree has NO block
on the machine-local board" is downstream of this guard, so it had never once fired in the
primary checkout either.

### 2. Nothing removes the root `HANDOFF.md` when the in-flight thing lands

PR #305's handoff says the file leaves the root when its work resolves. That promise is
prose *inside the file it governs*. [`docs/handoffs/README.md`](README.md) records what
that costs: `HANDOFF-difficulty-axis-and-synfire.md` sat at the root for four days while
its own second paragraph said *"nothing is half-done"*. `session_briefing.sh` reads the
file; nothing checks it against reality; sapper has no rule for it.

**Fix:** a sapper rule, or a check in the briefing, that reads the handoff's own claim
about what is in flight — a PR number is the obvious handle — and says so once that PR is
closed. This is the most mechanizable item here.

**DONE — and it was already done when this was written.** `tests/test_handoff_is_honest.py`
shipped in #305 (`696cac3`) a couple of hours before this page was drafted, and took the PR
number as the handle exactly as suggested. It has fired for real once: PR #298 closed
unmerged at 03:08 UTC and the spent handoff left the root within minutes (`3b7e022`),
instead of the four days its predecessor sat there. That is the first handoff in this repo
retired by a test rather than by somebody noticing. This item should have been marked
resolved on the day; it stayed open because nothing rereads a handoff's own open list.

**What was left, and is now closed too (2026-08-26).** The liveness half asks the API
through `gh`, `gh` with no token exits non-zero, `_states()` reads a non-zero exit as *no
evidence*, and `ci.yml` set no `GH_TOKEN` — so the check whose docstring says it speaks
*"out loud, in CI"* had never once run in CI. It skipped every time, and a skip is what
silence looks like when it is being careful. CI now passes `github.token` (read-only, no
secret) with `permissions: pull-requests: read`, and `BUGARACH_REQUIRE_PR_API=1` turns
*could not answer* into a failure there — the same treatment `BUGARACH_REQUIRE_BROWSER`
gives the browser step three lines above it in the same file, whose comment already said
why: *"so it cannot go quiet again."* The flag only bites when a root `HANDOFF.md` exists,
so the normal state stays quiet and never touches the network. A workflow-shape test sits
next to the check that depends on it, because that dependency lives in a file the check
cannot see — which is how it went missing in the first place.

### 3. `murderboard_revendor.py --selftest` fails in a consumer, passes upstream

Two failures in this repo, zero in the upstream clone:

```
FAIL this file's docstring states the recomputed count (11 vs 12)
FAIL this tool rewrites none of them (no stamp on its eligible line)
```

Both are the selftest asserting **upstream's own file shape**. A vendored copy carries one
extra stamp — its own — on the very line the tool is permitted to rewrite, so the count
reads 12 against a docstring that says 11, and the "rewrites none of them" case rewrites
one. The second failure predates PR #307. The freshness gate is green and the eleven pytest
checks pass, so nothing is blocked.

**Do not patch this downstream.** It is a vendored file and CLAUDE.md forbids editing one in
place. It wants sending back to `syncytium2/murderboard` as a portability bug: a selftest
that only passes in its home repo cannot tell a consumer whether vendoring worked.

> **STILL OPEN, and it now lives where live things live:**
> [`murderboard_revendor.py --selftest` is not portable](../todo/2026-08-26-murderboard-revendor-selftest-is-not-portable.md).
> Re-checked 2026-08-26: both failures reproduce.

### 4. Two `SessionStart` hooks, and neither knows the other exists

`.claude/settings.json` wires both `session_briefing.sh` and `session_start_trimmed.sh` on
`startup` and `resume`. Each budgets itself; neither sees the total. Measured on `main`
after PR #306: 8,068B + 6,282B, so roughly **14KB** of hook output at every session start,
all of it before the first user message. Both fit individually, so nothing warns.

Whether that total is worth ~14KB of every session's context is a judgement nobody has
made — it accumulated. Worth settling before a third hook is added.

> **STILL OPEN, and those two numbers have already moved** — 8,360B + 7,028B = 15,388B on
> 2026-08-26, because both hooks report on live state and grow with the repo. A figure that
> drifts is the clearest possible argument that it did not belong in a dated record:
> [two SessionStart hooks and neither sees the total](../todo/2026-08-26-two-session-start-hooks-and-neither-sees-the-total.md).

---

## How to reproduce any of it

```bash
bash tools/session_briefing.sh | wc -c                            # the number that matters
bash tools/session_briefing.sh --selftest                         # every rung of the ladder
BUGARACH_BRIEFING_BUDGET_BYTES=1 bash tools/session_briefing.sh   # the degraded form
bash tools/guard_local_board.sh ; echo $?                         # NOW 1 — see below
python3 tools/murderboard_revendor.py --root . --selftest
```

> ⚠ **The board-guard line no longer reproduces, and that is the good news.** It was
> offered as a demonstration of item 1: exit 0 from an unclaimed worktree, the gate waving
> everything through. PR #324 anchored the match on the block heading, so it exits **1**
> now and refuses correctly. A reader running the block as written would get a pass and
> conclude the page was wrong about everything else — which is why a reproduce block for a
> defect has to be retired along with the defect.
>
> The other four commands still do what they say.

## What this session did not do

- **Did not touch `session_start_trimmed.sh` or `board_digest.sh`.** They already carry the
  fix and were working. The audit confirmed them rather than changing them.
- **Did not fix the board guard.** It is a gate other worktrees depend on and it will start
  refusing commits that currently pass. It wants its own branch and a look at who it catches.
- **Did not run the eleven murderboard roles as parallel subagents.** This session was
  configured not to spawn agents, so the review took the single-pass form the process
  permits, walking every role's checklist in turn. That is a weaker pass than the parallel
  form; the run record beside this file says so, and a re-review would not be wasted.
