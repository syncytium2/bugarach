---
status: waiting-on-tony
filed: 2026-08-26
---

# Nine files name ADR-0003, and PR #298 was closed without merging

waiting: ADR-0003 was declined — does the decision get a different home, or do the nine files that cite it get rewritten? Both are fine; nobody can pick without you, and the citations read as broken until someone does.

> **Not murderboarded** — a finding for sessions in this tree. Every claim below is one
> `git grep` away.

## What happened

[PR #298](https://github.com/syncytium2/bugarach/pull/298) — *"Parity was the inheritance,
not a standing contract"* — was **closed without merging** at 2026-08-26 03:08 UTC. No
comment says why. The branch `parity-was-the-inheritance` still exists on `origin` at
`016df3b`, so nothing is lost; it is just not on `main` and nothing points at it.

**Do not read the closure as the decision.** The timeline says `closed by syncytium2`, and
that account is both Tony and every session in this tree — so it does not distinguish *"he
looked and declined"* from *"a session tidied an open PR on its way out."* It closed a
minute after #311 merged, during another session's shutdown. The PR was `MERGEABLE`,
`CLEAN` and 3/3 green at the time, and nothing was written down about it anywhere. That is
why this is a question rather than a plan.

The handoff that was at the root called this outcome in advance:

> *"If he declines it, the nine references need rewriting instead, and that is a bigger
> job than the merge."*

## What that leaves

Nine files on `main` name ADR-0003 as an existing document. A session reading any of them
goes looking for `docs/adr/0003-*` and finds `0001` and `0002`.

```
src/bugarach/assess.py                                          1
tests/test_assess.py                                            1
tests/test_assess_null.py                                       3
docs/forks.md                                                   2
docs/todo/2026-08-24-the-null-leaks-...-selection.md            3
docs/todo/2026-08-25-two-scorers-two-winners-...md              2
docs/handoffs/2026-08-25-the-session-hooks.md                   1
docs/handoffs/2026-08-25-the-adr-that-did-not-land.md           5
docs/reviews/HANDOFF_2026-08-25.md                              4
```

**Nothing is broken at runtime and no test fails on this** — it is a citation pointing at
nothing. The two `docs/handoffs/` files and the review are **dated records and must not be
edited**; that rule is `docs/handoffs/README.md`'s and it is why the count only ever grows.
The live ones are the first six.

## The decision is not in doubt; only its home is

Worth separating, because it would be easy to read a closed PR as a reversed decision.
Tony said it three times, and #298 quoted the last:

> *"We are modifying the six detectors at will to improve performance. We are no longer
> concerned about matching MATLAB performance. Consider the MATLAB versions stale."*

That decision is already **implemented and shipped** — `excess_mode="corrected"` is the
default in both the Python and the browser since #303, and `docs/forks.md` §13 records it.
What closed is the ADR *document*, not the practice. So this is a citation problem, not a
question about how the detectors behave.

## Three ways to settle it, none of them a session's call

1. **Reopen or re-land #298.** Cheapest by far — nine citations become correct at a stroke.
   It was held open only because it edits `FOUNDATIONS.md` §2, and that is the part that
   needs you rather than the ADR text.
2. **Give the decision a different home** — `docs/forks.md` §13 already carries it, so the
   six live citations could point there instead and the ADR number retires unused.
3. **Rewrite the six live citations** to state the decision inline without naming an ADR.
   Most work, least leverage, and it loses the single place a reader can go.

If #298 was closed by accident — which nothing rules out, since it was `MERGEABLE`, `CLEAN`
and 3/3 green at the time — option 1 is a click.

## How this surfaced

`tests/test_handoff_is_honest.py` (shipped in #305) asserts that a root `HANDOFF.md` names
at least one still-open PR. It went red within minutes of #298 closing and named what had
closed, which is what moved the handoff off the root the same night rather than four days
later. See [the hook audit](../handoffs/2026-08-25-the-session-hooks.md) for why that guard
exists.
