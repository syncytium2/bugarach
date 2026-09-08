---
status: open
filed: 2026-09-08
---

# Three documents argue from a measurement this repo's own tests now contradict

> **Not murderboarded** — working material for sessions in this tree. **If any of it
> reaches an outside reader, murderboard that artifact first.**

`78ebe26` (2026-09-06) re-measured the background axis on the **fitted** field at twelve
seeds and found **one detector leading at all seven grid points, largest rank change two**.
The same seeds on the **flat** field still give three winners and a change of three — which
is how the artefact was identified rather than assumed, and why
`tests/test_background_curve.py` now asserts both curves side by side.

Three documents still argue from the flat-field result. Each now carries a header saying so;
**none has been re-derived**, because restating stale numbers as current is the failure the
headers exist to stop.

| where | the superseded claim | state |
|---|---|---|
| [`performance_table.md`](../performance_table.md) §1 | *"The winner changes at two of the seven levels"* — the whole of **Why there is no ranking** | header added; table left as it stood |
| [`forks.md`](../forks.md), the background-curve fork | *"the winner changes between the two named endpoints … CoactDetect goes from first to fifth"* | paragraph struck through; **the fork's own spread conclusion is untouched and still holds** |
| `docs/learned/background_curve.png` | Panel B draws the rank crossing that no longer reproduces | ⚠ **not regenerated**; forks.md now says not to quote it |

**A fourth, and it is a different defect** — reported by the same session, fixed here rather
than deferred because it is checkable against a file in the same directory.
[`learned/bakeoff.md`](../learned/bakeoff.md) said the pooled trace had *"three of its four
folds at the floor"*; `bakeoff.json` says **one** (0.4, 0.45, 0.0001, 0.45). `78ebe26`
re-quoted that page's tables from the JSON and left its prose behind.

## What was found by grepping rather than by being told

Two of these were reported; **`forks.md` was not**. It turned up by grepping the tree for
the same shape before closing the report out — which is CLAUDE.md's own rule, written after
the Kreuz incident, where *"that was one `grep` and nobody ran it"*. The rule paid here on
its first use since.

## What is actually open

1. **Re-derive `performance_table.md` §1 on the fitted field.** Its conclusion — no ranking —
   may well survive, but *for a different reason*: the axis did not go dead, it narrowed. Mean
   own-range fell 0.185 → 0.136, still several times the 0.017 gap the bake-off asks readers
   to believe. **"No ranking because the spread is large" is a different argument from "no
   ranking because the winner swaps", and it has not been written.**
2. **Regenerate `background_curve.png` on the fitted field**, or delete it. A committed figure
   whose caption describes a crossing that no longer happens is worse than no figure.
3. **Nothing compares generated tables against typed prose.** Both defects here are that
   shape, in two different documents, from the same commit. `docs/INDEX.md` already carries a
   row for *"numbers typed into prose by hand"* naming `bakeoff.md` and `README.md`; this is
   the third and fourth instance. A check that extracts numeric claims from prose and diffs
   them against the JSON they sit beside would have caught both — see also
   [`2026-08-28-the-bakeoff-page-transcribes-what-a-token-could-substitute.md`](2026-08-28-the-bakeoff-page-transcribes-what-a-token-could-substitute.md).

## What this is not

Not a retraction of the bench background work — that landed correctly, with the flat field
kept as a control precisely so the artefact could be named. The defect is that three
*documents* were not walked when the measurement under them moved. The commit that moved it
re-quoted the tables it could see and had no way to find the prose four files away.
