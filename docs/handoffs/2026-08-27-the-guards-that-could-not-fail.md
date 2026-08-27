# The guards that could not fail

Four checks in this repo reported success while looking at nothing. Every one was
green the whole time it was broken, and not one was found by a test failing.

| | the check | why it could not fail |
| --- | --- | --- |
| #313 | the briefing's size canary | printed on the **last** line — the one position a spilled payload discards |
| #324 | the machine-local board gate | matched the board by **substring**, and the repo name is in every path on it |
| #331 | the root-handoff liveness test | needed `gh`; CI passed no token; a failed `gh` reads as *no evidence*, so it **skipped** |
| — | the census #313 added | sized files with `stat -f`, which is BSD-only, so on Linux it measured **nothing** and said all checks pass |

> **"Spilled"** is the failure the first and last rows turn on. A `SessionStart` hook
> whose output is too large is not trimmed — the harness writes the whole thing to a
> file and injects roughly the first 2KB as a preview. Going over is not "a bit less
> arrives"; it is "almost nothing does", and everything ordered after the cut reaches
> nobody.

The last row is the one worth keeping. It arrived *inside the fix for the first one*,
in a tool written specifically to stop a check being trusted on the word of the thing
it checks — and CI caught it, on Linux, where this machine never could have. That is
the pattern in one line: **the number that settles a check has to come from outside
the thing being checked.** Offered as the lesson these four cases taught, not as a law.

---

**Written 2026-08-27**, and written straight into `docs/handoffs/` rather than moved
here — it was never a root signal, because nothing in it is half-done. The root slot
stays empty, which is what it should say. This records a day spent on the four items
[the hook audit](2026-08-25-the-session-hooks.md) left open: three are closed, and the
fourth is a todo whose one-line instruction — *send it upstream* — is the part that
does not survive being written down once. The last section is what it means.

Every open item lives in `docs/todo/`, not here. This page only points at them.

## What landed

**[#313](https://github.com/syncytium2/bugarach/pull/313) `ace7fd9` — the canary moved to line 1.**
[#306](https://github.com/syncytium2/bugarach/pull/306) gave the briefing a budget, a
terse fallback and a size canary, and printed the canary last. A refused payload is not
truncated in place: the harness keeps the opening ~2KB and spills the rest to a file. So
the canary reported only when nothing was wrong. It is line 1 now and the number counts
the whole payload including itself, which is why `canary_line()` settles a fixed point
rather than measuring the body. Three more from the same reading: the budget ladder had
no floor, so a terse render still over budget shipped labelled `(TERSE` as though the
degrade had worked; the alarms were bounded in *lines*, and fourteen 300-character lines
is 4KB, enough to push the alarms #306 front-loaded straight back out; and one env var
named two different numbers, so setting it to test either hook silently retuned the other.

**`tools/hook_spill_census.sh` — the threshold, measured.** Both hooks' headers said the
spill threshold "is not observable from inside a session". True, and read by everyone as
not observable. It is observable from *outside* one: refusing a payload is what writes it
to disk, under `<claude-config>/projects/<slug>/<session>/tool-results/hook-*-stdout.txt`.
The smallest payload that record shows being refused is **10,186B**, against the
**13,414B** the sibling hook's header still cites as its smallest known failure — the
guess was loose by 3.2KB, and loose the dangerous way, claiming headroom that is not
there. It also de-circularizes the
size test, which until then read the budget out of the script and asserted the output
was under it: raise the budget to 50,000 and it stays green while the channel dies.

**[#324](https://github.com/syncytium2/bugarach/pull/324) `334d539` — a mention is not a claim.**
`verdict()` grepped the whole board for a bare substring. The primary checkout's
directory basename is the repo name, and the repo name is in every path anyone writes
down, so the checkout most likely to be shared was the one that could never be refused.
The heading is parsed now and the identifier compared exactly — literally, not as a
regex, which is what `grep -F` had been buying. Run over the live board before landing,
because a stricter gate refuses commits that pass today: **three of the thirteen
worktrees live at that moment changed verdict, all three true positives.** (The count
in the block below is today's re-measurement over fourteen; the population moves, the
three do not.) Two of them were passing only because a
session that finished six days earlier had listed them under its own *Worktrees touched*
line. It also repaired a dead alarm one layer up — the briefing's "this worktree has NO
block" is downstream of this guard and had never fired in the primary checkout either.

**[#331](https://github.com/syncytium2/bugarach/pull/331) `e83e8ec` — the handoff guard now runs where it promises to.**
Item 2 was **already built by the time anyone read it as open**, and the timing is the
point rather than a footnote. The hook audit committed its open list at **22:32**; a
concurrent session landed `tests/test_handoff_is_honest.py` at **22:59**, twenty-seven
minutes later, in [#305](https://github.com/syncytium2/bugarach/pull/305) (commit
`696cac3`, merged as `5502764`). Neither session could see the other, and the page went
on listing the item for two days. That is the cost of *"nothing rereads a handoff's own
open list"* measured in minutes, and it is why the live items on this page are todos.
The test has since fired for real once, retiring a spent root handoff at 03:16 UTC
(`3b7e022`) — **eight minutes** after PR #298 closed unmerged at 03:08.

What was left is that its liveness half asks the API through `gh`, `gh` with no token exits
non-zero, and `ci.yml` passed no token — so the check whose docstring says it speaks
*"out loud, in CI"* had skipped in CI every run since it shipped. CI passes
`github.token` now, and `BUGARACH_REQUIRE_PR_API=1` turns *could not answer* into a
failure there while a developer machine keeps the graceful skip. That is the treatment
`BUGARACH_REQUIRE_BROWSER` already gives the browser step three lines above it in the
same file, whose comment says why: *"so it cannot go quiet again."*

**[#338](https://github.com/syncytium2/bugarach/pull/338) `8da5cb7` — the murderboard family re-vendored,
`94d720c` → `73dad04`,** because this page is a document deliverable and the freshness
gate refused to let one be written against a stale process. `doc_review_process.md` did
not change in that range, so the roles are the same roles — but that is knowable only
after looking, which is the argument for the gate being a stop rather than a warning.

## Numbers, and the fact that they move

Measured on this machine on 2026-08-27, in this worktree. Every one of them tracks live
state — the board, the todo count, the session history — so they are re-measurements,
not constants, and the tools that print them are the durable part:

```
briefing delivered: 116 lines, 8360B (budget 9000B)          tools/session_briefing.sh
briefing delivered: 102 lines, 7787B (budget 8000B)          tools/session_start_trimmed.sh
spilled_count=55  spilled_min=10186  delivered_max=8962      tools/hook_spill_census.sh
3 of 14 worktree(s) change verdict                           guard_local_board.sh --audit
```

**They moved while this page was being reviewed**, which is not an aside. The second
line read `90 lines, 6851B` when first measured and `102 lines, 7787B` twenty minutes
later — **936B**, because sessions claimed blocks on the board in between and the
digest renders every ACTIVE one. The board dump behind it went 256,780B → 258,099B in
the same window. This is the concrete reason a figure like this belongs in a tool's
output and not in a dated page: the previous handoff quoted ~14KB for the pair and was
overtaken inside a day.

**And the sibling is the one to watch, not the briefing.** `session_start_trimmed.sh`
is at **7,787B against an 8,000B budget — 213B of headroom**, and the thing it renders
grows every time a session claims a block. On the drift measured above it has minutes,
not weeks. When it crosses, its board digest degrades and the ACTIVE claims stop
arriving, which is the failure the digest was built in 2026-08-20 to prevent, reached
by the other road. **That budget is also the one with room to move**: the census floor
is 10,186B and 8,000 sits 2,186B under it, so unlike the briefing this one can simply
be raised. Nothing in this session's work touched it, and nobody has looked — so it is
filed as [`docs/todo/2026-08-27-the-board-digest-is-213-bytes-from-degrading.md`](../todo/2026-08-27-the-board-digest-is-213-bytes-from-degrading.md),
where it will be reread, rather than left here where it will not.

The briefing is the slower problem. It is 8,360B against its own 9,000B
budget — **640B of headroom**, and it grows with the board and the todo count. A spill
is not the risk: the census floor is 10,186B, so 9,000 sits 1,186B under it. The risk
is the *ladder*, which degrades FOUNDATIONS §9 to its bolded claims the moment the
payload crosses 9,000 — the briefing would still arrive, still report success, and
quietly stop carrying the reasoning that the whole hook exists to deliver.

Raising the budget is the wrong reflex, because the census pins it from both sides:
under the smallest observed refusal, and over the ordinary payload. **The move is to
turn something in the briefing into a count**, the way #306 did to the open-todo dump.
There is no threshold to watch for beyond the two numbers already printed every run —
when the canary and the budget on the same line get close, that is the signal, and
`hook_spill_census.sh` says whether the budget itself still has room to move.

## Open, and where it now lives

| | item | filed as |
| --- | --- | --- |
| 3 | `murderboard_revendor.py --selftest` fails in every consumer and passes upstream | [`…-murderboard-revendor-selftest-is-not-portable.md`](../todo/2026-08-26-murderboard-revendor-selftest-is-not-portable.md) |
| 4 | two SessionStart hooks, neither aware of the other's total | [`…-two-session-start-hooks-and-neither-sees-the-total.md`](../todo/2026-08-26-two-session-start-hooks-and-neither-sees-the-total.md) |
| new | the board digest is ~200B from degrading, and its budget is the one with room | [`…-the-board-digest-is-213-bytes-from-degrading.md`](../todo/2026-08-27-the-board-digest-is-213-bytes-from-degrading.md) |

The third was found **by this review**, not by the work it reviews — the murderboard
re-measured a number the draft had quoted twenty minutes earlier and it had moved.

Item 4 is partly answered by this session's evidence, and the todo should be read with
it: **the limit is applied at least per hook, not once per session start.** This
session watched one hook delivered whole at 6,337B while its sibling was spilled at
17,438B in the same startup — a single observation, but a decisive one, because a
shared budget cannot deliver one half and refuse the other. It does not rule out an
additional session-wide cap; it does rule out the pair sharing one allowance.

So splitting the two hooks is protective rather than accidental, and merging them
would spill the pair. What remains open is the honest question the todo asks — whether
~15KB of every session's context is worth it — and that is a judgement, not a bug.

## "Sending upstream", since it is the whole of item 3

`tools/murderboard_revendor.py` is **vendored**: bugarach holds a copy, and line 2 says
where the original lives. Its `--selftest` fails two checks here and passes in
`syncytium2/murderboard`, because both checks assert upstream's own file shape. A
vendored copy carries one extra stamp — its own `vendored from … @ <sha>` line — on
precisely the line the tool is allowed to rewrite. So the count reads 12 against a
docstring that says 11, and the *"rewrites none of them"* case rewrites exactly one.

**Sending it upstream means fixing it in `syncytium2/murderboard` and re-copying, not
editing the copy in this repo.** Three reasons it is worth the extra step:

1. **A local edit is erased by the next re-vendor.** `murderboard_revendor.py` re-copies
   the body from upstream and bumps the stamp — that is its whole job. A fix applied here
   survives until someone runs the tool, which is exactly when nobody is looking for it.
   #338 re-copied two of the five files in this family today.
2. **A local edit makes the copy un-re-vendorable.** The moment a vendored file diverges,
   the next re-copy is a conflict rather than a copy, and the usual resolution is to keep
   the local version — which is how a vendored file quietly becomes a fork nobody chose.
   CLAUDE.md forbids it in terms for this reason.
3. **The bug is upstream's, and it is about consumers.** The selftest exists to tell a
   *consumer* that its vendoring machinery works. It cannot, because it only passes in the
   one repo that does not need it. Every other consumer of this tool has the same two red
   lines and no way to tell them from a real problem.

What it takes, concretely, and it is small — both repos sit in the same org
(`syncytium2`) and the upstream clone is already on this machine at
`~/Developer/murderboard`, on `main` and clean:

- Open a PR there fixing the selftest to assert the **invariant** rather than the count:
  derive the expected number from the file being scanned, and build the "rewrites none"
  fixture without a vendor stamp on its eligible line. Both checks then hold in a
  consumer and upstream alike, which is the property they were reaching for.
- Land it upstream. Then, back here: `python3 tools/murderboard_revendor.py --root .`
  re-copies and bumps the stamp, and `--selftest` goes green in a consumer for the first
  time.
- Nothing of bugarach's goes into that repo. Its CONTRIBUTING says so on its own face,
  and the fix is a fix to their tool, not a contribution of our content.

**The todo is canonical** for the reproduce command, the failing output and the
diagnosis; this section is only about what the instruction means, so the two do not
drift into two accounts of the same bug.

## How to reproduce any of it

```bash
bash tools/session_briefing.sh | head -1              # the canary, first line, true number
bash tools/session_briefing.sh --selftest             # every rung, including the floor
bash tools/hook_spill_census.sh                       # what the harness has actually refused
bash tools/guard_local_board.sh --audit               # who the anchored gate catches
bash tools/murderboard_freshness.sh ; echo $?         # 0 = the process is current
python3 tools/murderboard_revendor.py --root . --selftest   # item 3, still 2 failures
```

Every one of these passes or reports today, which is the point of listing them: they are
demonstrations of things working, not of things being wrong, so none of them will invert
under a reader the way item 1's block on the previous page did.

## What this session did not do

- **Did not fix item 3 in this repo**, on purpose. See above.
- **Did not decide whether bugarach should consume murderboard as a plugin.** Upstream
  became a Claude Code plugin between `94d720c` and `73dad04` — marketplace manifest,
  `hooks.json`, and most of a +569-line change to the freshness script. Vendoring five
  files still works and is what #338 did. Whether to switch is Tony's call.
- **Did not change either hook's budget.** The census says 9,000 and 8,000 are both
  under the observed floor. The pressure noted above is on the briefing's *content*,
  not on its budget.
- **Did not touch `tools/session_start_trimmed.sh` beyond one variable rename.** It
  already carried the 2026-08-20 fix and was working.
