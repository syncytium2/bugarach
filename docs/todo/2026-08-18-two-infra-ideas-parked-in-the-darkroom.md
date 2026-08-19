---
status: parked
filed: 2026-08-18
---

# Two infrastructure ideas are parked in the darkroom, not in this list

Both came out of the 2026-08-18 session and both are infrastructure, which is the
thing this repo has too much of. Tony's call: park them where they stay findable
and stop occupying attention here.

`<darkroom>/ideas/` — resolve with `bugarach.paths.darkroom()`, they sit beside it:

| file | what |
|---|---|
| `bugarach-sendmessage-gate-has-no-test.md` | `.claude/hooks/require-commit-before-message.sh` is the one commit gate with no pytest wrapper, against CLAUDE.md's claim that every gate has one. The hook's own `--selftest` passes and proves six branches; only the wrapper is missing |
| `mechanism-change-gate.md` | a staged-diff rule that fires when a commit installs a hook, commit gate or `pre*`/`post*` script — the class of change that binds every future session and currently gets no review at all |

The second has a full write-up open for comment at
`<darkroom>/needs/mechanism-changes-need-a-gate.md`, copied into this repo at
[`docs/needs/mechanism-changes-need-a-gate.md`](../needs/mechanism-changes-need-a-gate.md).

**Neither is scheduled, and neither should be picked up as filler.** The second is
deliberately unbuilt for a reason that survives being restated: building it means
adding it to sapper, sapper runs on every commit, so writing the gate installs the
gate — which is exactly the act it exists to make deliberate.

`status: parked` rather than `open`, so the session briefing's open-thread count
does not carry them.
