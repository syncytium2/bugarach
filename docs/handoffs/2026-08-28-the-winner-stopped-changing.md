# The winner stopped changing, and the reordering it replaced was living in a tail the flat field made up

**The open decision on `bench-background-is-not-flat`.** Three tests in
`tests/test_background_curve.py` fail, they are the last red on that branch that
is a *finding* rather than a chore, and nobody has ruled on them.

> ⚠ **CORRECTED 2026-08-30 — this quote was read as a ruling and it was a
> question.** Tony, 2026-08-28, on the four decisions the background change
> surfaced, said: *"don't get 4."*
>
> **It means "I do not understand item 4."** Tony, 2026-08-30: *"I meant I didn't
> understand 4 and it inferred something else."* **Item 4 is the three
> `test_background_curve` tests** — [`HANDOFF-bench-background.md`](2026-08-28-the-bench-background-is-no-longer-flat.md)
> §4, *"do not re-baseline these quietly"* — so the question was asked about the
> exact decision this handoff was written to advance, and was recorded as answered.
>
> It was read here as agreement that
> item 4 had been mis-framed, and the sentence originally printed after it —
> *"Fair — it was handed over as a test failure. It is a result."* — presented that
> reading as **Tony's own verdict on his own decision**. He had ruled on nothing. He
> had asked what item 4 was.
>
> The original sentence is quoted above rather than silently dropped, because this
> handoff was read afterwards as though the ruling existed.
>
> **The same phrasing was misread twice on one day**, by two sessions, and one of
> them wrote its misreading into a durable handoff as a ruling — this one. What it
> cost is small and specific: item 4 read as settled when it was asked-and-
> unanswered, so nobody answered it. A `UserPromptSubmit` hook now fires on short
> replies of this shape, and a decisions log is filed so a misread shows up as a
> wrong row rather than as prose nobody questions. Written up as a teaching case in
> `syncytium2/short-course`,
> `docs/cases/2026-08-30-the-hedge-that-crossed-a-session-boundary.md`.
>
> **Item 4 is still unanswered — and it is now measured.** On 2026-08-30 the three
> tests were re-run at **12 seeds** rather than their own `SEEDS = (1, 2, 3)`, which
> is the count this branch's author called noise-dominated one file over. On seeds
> 1–12 coact wins all seven grid points but by **0.0011** at the busy endpoint; on an
> independent block, seeds 13–24, **LoCo takes the busy half and two of the three
> tests pass.** The tests assert a strict inequality on a quantity that is a coin
> flip, so neither "re-baseline them" nor "leave them red" is right. That is the
> answer to item 4, and it is still Tony's call what the tests should assert instead.

**Since then it has been measured, and the two readings are no longer even.**
Skip to *What the measurement says* if you want the answer; the rest is why the
answer was not obvious from the failure.

---

## What the three tests are for

The bench sweeps **background rate** across seven values (`BACKGROUND_GRID`,
0.0026 → 0.0400 Hz/ROI) and scores every detector at each. On the flat field the
**winner changed along that axis**, and one detector moved four places up the
table. Three tests assert exactly that, because it is the evidence for a claim
the project makes everywhere else: *you cannot say "detector X is best" without
naming a background.*

With the fitted background they fail like this:

```
one detector won everywhere ({'coact'}), which would make the axis safe to
quote across and is not what was measured

coact wins at both endpoints — the reordering this test was written for has
gone, which is good news worth looking at

the largest rank change across the axis is 2 places; this was written when a
detector moved four
```

## Why the failure alone could not settle it

Two readings, opposite rewrites:

**(a)** The winner-swapping was largely an artefact of the flat field. The axis
still separates detectors; coact genuinely leads across it. → Rewrite the tests
to assert the new, true claim.

**(b)** The fitted heterogeneity now **dominates** the rate axis, so moving
background rate barely changes anything, and the axis has stopped discriminating.
→ These tests should sweep something else entirely; asserting "coact wins" would
be asserting that a broken instrument reads steady.

A test that says *"the winner stopped changing"* is consistent with both. That is
why it was left alone rather than re-baselined — under (b), rewriting it to match
the new numbers deletes the evidence that the axis went dead.

## What the measurement says

The readings differ in something checkable. Under (a) each detector's F1 still
moves as rate sweeps, and detectors stay far apart at any given rate. Under (b)
the curves flatten, or collapse onto each other.

Six seeds, `baseline_quiet`, same seeds both sides:

| | flat | fitted |
| --- | --- | --- |
| mean **own-range** — how much one detector's F1 moves across the axis | 0.185 | **0.136** |
| mean **spread between detectors** at a given rate | 0.117 | **0.098** |
| distinct winners along the axis | 3 (coact, loco, rate) | **2 (coact, rate)** |

**Reading (a), with a caveat.** Neither quantity collapsed. The axis still moves
each detector by ~0.14 of F1 and still separates them by ~0.10 at a given rate —
it discriminates. Both shrank modestly (−26% and −16%), so the fitted background
*is* somewhat less punishing, but it has not gone dead.

**And the reordering had a location.** Look at the busiest end:

| at 0.040 Hz/ROI | flat | fitted |
| --- | --- | --- |
| loco | 0.49 | 0.62 |
| coact | 0.47 | 0.67 |
| cicada | 0.48 | 0.58 |
| rate | 0.58 | 0.53 |

On a **flat** field, raising the mean rate raises *every* ROI's rate together, so
the whole field gets uniformly noisier and every detector degrades — into a
crowded low-F1 tail where the ordering is unstable and crossings are cheap. On a
**heterogeneous** field, the same mean increase concentrates into ROIs that were
already busy while much of the field stays quiet, so coordination remains
detectable and nobody falls into that tail.

**So the four-place rank change was real, and it was happening in a regime the
flat background manufactured.** That is the sentence these three tests should
end up asserting, in some form.

## What is still not established

- **Six seeds, one regime.** The failing tests run their own seeds and found
  **one** winner; this run found **two**. The difference between "coact wins
  everywhere" and "coact wins nearly everywhere" is inside seed noise at this
  count. Anyone rewriting these tests should pick a seed count deliberately and
  say so, because the assertion is about a ranking and rankings are the thing
  seeds move.
- **`baseline_quiet` only.** The busy regime was not swept.
- **The mechanism above is an explanation of the numbers, not a separate
  measurement.** It follows from how a Gamma-shaped rate field responds to a
  mean shift, and the table is consistent with it; nothing here isolates it. The
  clean test would hold the *shape* fixed and move only the mean, against holding
  the mean and moving the shape.

## What a rewrite has to keep

Whatever these tests become, the claim they exist to protect must survive:
**a single F1 quoted without its background is not a result.** That is still true
— the axis moves each detector by ~0.14 — and it is now true for a plainer
reason than winner-swapping, which was the flat field's artefact. An assertion
that only checks "coact wins" would be strictly weaker than what they defend
today.

The honest options, in the order I would try them:

1. **Assert the spread, not the ordering.** Own-range and between-detector spread
   both stay well above zero; that is the claim, it is what the axis is for, and
   it does not depend on a ranking that seeds can move.
2. **Keep a ranking assertion but move it to where the ordering is still
   unstable** — the busiest end still reorders `rate` against `coact`.
3. **Sweep the shape as well as the rate**, since the shape is now the thing the
   background model actually carries. That is a new test rather than a rewrite,
   and the biggest of the three.

## Where

- `tests/test_background_curve.py` — the three.
- `bench.BACKGROUND_GRID`, `bench.evaluate_background_curve` — the axis.
- Branch `bench-background-is-not-flat`; the other deploy-relevant consequences
  are in [the bench moved under the deploy](2026-08-28-the-bench-moved-under-the-deploy.md).
- The script behind the tables is not in the tree. It is short — two calls to
  `evaluate_background_curve` per detector, flat via
  `gen={"bg_rate_shape": None, "bg_burst_shape": None}` — and belongs in `tools/`
  if anyone wants it kept.

`PYTHONPATH=$PWD/src` is not optional in a worktree —
[why](../todo/2026-08-28-a-worktree-pytest-run-tests-the-primary-checkouts-src.md).
