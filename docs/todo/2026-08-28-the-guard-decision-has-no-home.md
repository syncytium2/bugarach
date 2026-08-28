---
status: open
filed: 2026-08-28
waiting: Put `guard_sec` on the coact knob axis with a crowded regime in the scoring set, or scope the re-fit to the median on purpose and say so in `forks.md`.
---

# The guard decision has no home, and the file that was supposed to hold it does not mention it

> **Not murderboarded** — a planning note for sessions in this tree, same standing as
> [`CFAR variants are a knob axis`](2026-08-25-cfar-variants-are-a-knob-axis-not-new-detectors.md),
> which it descends from. If any of it reaches an outside reader, murderboard that
> artifact first.

## Why this file exists rather than a paragraph in the handoff

[`docs/handoffs/2026-08-28-guards.md`](../handoffs/2026-08-28-guards.md) landed as #366
carrying five open decisions. `docs/handoffs/README.md` says in terms what should have
happened next and did not:

> **Open items leave for `docs/todo/` when the handoff moves here.** […] **A todo gets
> reread**: the session briefing counts `docs/todo/` at every start and reads
> `waiting-on-tony` out loud. A handoff is read once, by whoever was told to.

That rule was written because `2026-08-25-the-session-hooks.md` carried four open items
into this directory, and *"nothing rereads a handoff's own open list"* — by the time
anyone looked, one item's reproduce command had stopped reproducing and another's byte
counts had drifted. The guards handoff repeated the shape the day after the rule was
added to the README.

**Checked, not assumed.** Of its five decisions, two already have a home and three do not:

| # | decision | home | status |
|---|---|---|---|
| 1 | does `guard_sec` join the coact knob axis, or is the re-fit scoped to the median on purpose | root `HANDOFF.md` names [revise the bench](2026-08-23-revise-the-bench-recording-before-the-refit.md) | ⚠ **that file contains neither `guard_sec` nor "crowded regime"** |
| 2 | is `forks.md` §4a amended | [flat guard gain](2026-08-25-a-flat-guard-gain-is-what-self-masking-relief-looks-like.md), whose closing section says the ruling is not its to make | homed |
| 3 | is `detector_history.md` §5.2's compaction prescription amended | [the history document has moved on](2026-08-24-the-history-document-describes-a-tree-that-has-moved-on.md) covers §5.2 — **for the CFAR-property claim, not this one** | ⚠ **not homed** |
| 4 | what is LoCo's fix for the same inflation | — | ⚠ **nothing** |
| 5 | censoring inside `maxlt` | [censoring is the instrument](2026-08-23-censoring-is-the-instrument-the-guard-was-not.md) | homed |

**A named home is not a home.** Decision 1 is the gating one and the root handoff sends a
reader to a file that has never mentioned it. That is the failure this repo keeps
catching in other forms: a pointer that resolves, to a document that does not carry the
thing.

## The decision, stated so it can be answered

The measurement is settled and is not what is being asked. In the crowded tail a 20 s
`exposure` guard buys **+0.071 recall in the `<10 s` neighbour-gap bin, 17 of 24 seeds,
every other bin flat**, against a no-guard control loosened until it matched on *both*
recall (0.865 vs 0.871) and precision (0.910 vs 0.909) — so a matched threshold change
cannot buy it. And separately, **no guard configuration's best F1 leaves the no-guard
seed band** on any of the three benched recordings. Both hold. The handoff carries the
evidence and every caveat on it; this file does not restate them.

What is unanswered is what the **re-fit campaign** does about that:

- **(a) Put `guard_sec` on the coact knob axis, and add a crowded regime to the scoring
  set.** The campaign then finds the guard or genuinely rejects it. Cost: a wider grid,
  and a regime `bench.py` currently says nothing may be calibrated on — so the crowded
  entry has to be a *scoring* recording with its status stated, not a calibration one.
- **(b) Scope the re-fit to the median recording on purpose**, and write into `forks.md`
  that the guard is **out of scope by construction** — so nobody later reads the
  campaign's silence as evidence. Cost: nothing now; the risk is a future session finding
  a guard-shaped hole in the results and re-running two weeks of this.

**The choice is not "does the guard work".** It is whether a campaign that will be quoted
is allowed to be silent about a knob whose one measured effect lives in a fifth of the
real folder — crowding median **0.00**, IQR 0.00–0.30, range 0.00–0.57, **7 of 39
recordings** above the crowded diagnostic's 0.38.

## What rides on the answer

- **Decision 3 shrinks either way.** §5.2 prescribes *"the shift has to be defined on the
  retained reference span, not on a window with a hole in it"* — which is compaction, and
  compaction is what multiplies every bin by `C / (C − guard)`. Under **(a)** that
  sentence needs a real amendment naming `exposure` as the alternative and saying the
  choice is unsettled. Under **(b)** it is a one-line note that the guard is off and the
  question is parked. Either way it belongs in
  [the history retensing](2026-08-24-the-history-document-describes-a-tree-that-has-moved-on.md),
  which already opens §5.2 for a different reason and should be told to fold this in.
- **Decision 4 dies under (b).** LoCo carries the same density inflation with no fix —
  `exposure` is not portable to it, because its threshold pool is built over bins inside
  each half. Building one is real work and it is only worth doing if a guard can enter the
  campaign at all.
- **Nothing rides on it for the deploy.** `guard_sec` defaults to `0.0`, no entry in
  `bench.OPERATING_POINTS` sets it, and nothing outside the probes and three test files
  has run with one on. This does not gate publishing; `DEPLOY_HOLD.md` is that gate.

## The deferral still binds, and this file does not lift it

Tony, 2026-08-25, in
[`CFAR variants are a knob axis`](2026-08-25-cfar-variants-are-a-knob-axis-not-new-detectors.md)
— **on `main` since #304 landed, 2026-08-28**:

> *"these are all valuable additions that need to be prioritized after the full pipeline
> is viable."*

That governs **building** things — censoring, VI selection, a design P<sub>fa</sub>, a
guarded tube. **Answering the scoping question above is not building anything**, and
option **(b)** is a two-line documentation change. So this is askable now and the ruling
is untouched by it. **If a session lifts the deferral, it says so explicitly in its own
handoff and names what replaced the ruling** — otherwise the next session finds it,
believes it, and stops, correctly.

## ⚠ There is no room for a fourth decision, and that is why this says `open`

**This file wants `status: waiting-on-tony`.** It is a decision no session can advance,
which is exactly what that status is for. It cannot have it, and the reason is measured
rather than argued.

Three items already carry it. Adding a fourth costs **135B** and the budget has **54B**.
Fresh clone, `BUGARACH_DARKROOM` unset, no `core.hooksPath`, no machine-local board —
the configuration CI runs and the one that binds:

| `docs/todo/` state | briefing |
|---|---|
| without this file | **8,946B**, 133 lines — fits |
| this file, `waiting-on-tony` | **9,081B** — over, so **TERSE: 70 lines, 4,251B** |
| …title cut to 38 chars, filename shortened, action line halved | **9,071B** — still over |
| this file, `status: open` | **8,946B**, 133 lines — costs nothing |

**Trimming recovers 10B of the 81B needed, so the cost is the structure of a fourth
entry, not its text.** No wording fits. And the failure is not a truncated line — it is
the whole briefing collapsing from 133 lines to 70, which loses the board, the worktree
list and the other three decisions along with this one. **A fourth decision is worse than
no decision.**

⚠ **I measured the configured machine first and got 8,758B, which fits, and CI failed.**
That is `HANDOFF_2026-08-27.md`'s lesson repeating on the file written after it: on a
configured machine the standing alarms collapse to one line each, so the local number is
never the number. Measure in a throwaway clone.

**So `status: open` is a workaround, not a fix, and the fix is a real choice:** raise the
budget — `tools/hook_spill_census.sh` puts the smallest observed refusal at **10,186B**,
so 9,000B is conservative by its own record — or retire one of the three standing items,
of which [the PySpike report](2026-08-11-file-pyspike-max-tau-issue.md) has been finished
and waiting since 2026-08-11 and needs one email. Neither is this file's call. Related and
already open:
[two session-start hooks and neither sees the total](2026-08-26-two-session-start-hooks-and-neither-sees-the-total.md).

## What must not happen

- **Do not answer this by running the guard again.** It has been measured five times and
  the last three agree; a sixth run is not the missing input. The missing input is a
  ruling about scope.
- **Do not tune the guard to make the crowded number look better.** It moves the number;
  that is the problem, not the solution.
- **Do not edit `forks.md` §4a or `detector_history.md` §5.2 on the strength of this
  file.** Both are reserved, both have been corrected before, and decision 2 is on record
  as *not this repo's to make without a ruling*.
