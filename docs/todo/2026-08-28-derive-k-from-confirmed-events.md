---
status: open
filed: 2026-08-28
---

# K should be derived from confirmed events, not picked off a scan

> **Not murderboarded** — a planning note for sessions in this tree, same standing as
> [`the four variants`](2026-08-23-four-variants-of-the-tube.md). Every number is quoted
> from a named file. **If any of it reaches an outside reader, murderboard that artifact
> first.**

Tony, 2026-08-28: *"k>=3 is a fine start, but we'll probably need to derive that from the
machine assisted human confirmation of events."*

**This amends [`the human-in-the-loop todo`](2026-08-16-assessment-needs-a-human-in-the-loop.md),
which stops one step short of it.** That item scopes the K scan shown side by side and an
*accept* step — a person choosing K having seen its consequence. This is different: the
person confirms **events**, and K is **inferred from what they accepted**. K stops being an
input and becomes an estimate.

## Why it matters

K is the only quantity in the pipeline nobody can measure, and it moves the answer more
than any mechanism change in the repo. From `docs/learned/generator_spec.json`, the
assessor's scan over 85 real baseline slices:

| K | clusters/min | cells per cluster | slices with a defined jitter |
|---|---|---|---|
| 3 | 0.350 | 4.5 | 66 of 85 |
| 4 | 0.095 | 6.0 | 48 of 85 |
| 6 | 0.034 | 8.0 | 30 of 85 |
| 8 | 0.000 | 12.0 | 8 of 85 |

Same recordings in every row. Moving 3 → 4 discards roughly three-quarters of the
coordination; at 8 there is none left. Everything downstream inherits the choice: the
generator's cluster rate, the simulated data set, the operating points fitted against it,
and every F1 quoted from them.

## The trap, and it is the whole design

**The proposal stage must sit BELOW the floor being estimated.** If the machine proposes
candidates at K≥3 and the human confirms from that list, the candidate set is censored at
the floor the exercise is supposed to estimate, and the answer is the assumption returning
under a new name. That is the same circularity RESET §1 already caught in the validation
test — *"asking the assessor to recover planted events is the convention agreeing with
itself."*

So: propose at **K = 2**, or at a permissive excess threshold with no floor at all, and let
the accepts and rejects say where the boundary falls.

## How K is then derived

Every proposed moment carries an observed co-active count, and after review it carries a
human verdict. K becomes a **threshold chosen against labelled calls** — the value that
best separates confirmed from rejected — reported with its separation quality rather than
as a bare integer. A K with a wide overlap band is itself a finding: it would say the
count is not what the expert is actually judging on, and that the assessor is measuring
the wrong quantity.

## What this is NOT, and the vocabulary will be enforced

**Confirmed events are not ground truth.** RESET §10 reserves that phrase for planted
events in simulation and nothing else, and RESET §1 makes a human call a property of
**(recording × rendering × observer)**. What this produces is a *recorded judgement*:
the calls, the view they were made in, and who made them. Two consequences that are design
constraints, not caveats:

- **The rendering is part of the record**, so the confirmation surface has to pin the view
  rather than let a reviewer scroll and zoom freely. Half of this exists — #270 landed the
  part that records the decision and the view beside the data set it produced.
- **K inherits whoever labelled.** One observer gives one K. A second observer on a subset
  is what says whether it is stable or is a fact about one person, and that is cheap enough
  that not doing it would be a choice.

## Scale — this is an afternoon, not a campaign

At 0.35 clusters/min a 30-minute window carries about **10 candidates at K=3**, and more at
a K=2 proposal floor. Across the folder that is hundreds to low thousands; a couple of
hundred confirmations already gives a usable estimate. The cost is expert attention, not
compute.

## Where it sits in the order

RESET §7 step 3 — *"fresh assessment of the approved folder, and a K decision"* — is
marked ⛔ and blocks the re-derived generator spec and everything after it. This does not
add a step; it **changes what that step is**. Picking 3 off a scan is minutes and is
defensible as a start. Deriving it is the version that makes the human-in-the-loop claim
operational, and it is the one worth doing before any number is published as final.

**It blocks nothing that is running now.** Mechanism screens that inherit an existing
recorded `k_chosen` compare the tube to itself and never touch this question.
