# Architecture Decision Records

One decision per file, recorded when it is made. The form is borrowed from
`colonel_kernel`, which has been running it for fifty-odd decisions; the point of
copying it rather than inventing one is that Tony already reads that shape.

Where this sits against the rest of the tree:

- **[`docs/FOUNDATIONS.md`](../FOUNDATIONS.md)** — settled foundations and the reasoning
  behind them. Canonical; it wins over anything said in conversation and over anything
  here.
- **ADRs (this directory)** — individual decisions, as they are taken.
- **[`docs/todo/`](../todo/)** — open work items, one file each.

When an ADR changes a settled point in `FOUNDATIONS.md`, update `FOUNDATIONS.md` so the
two never disagree, and cross-reference them.

## Convention

- One decision per file, named `NNNN-title-in-kebab-case.md`, zero-padded, incrementing.
- **Michael Nygard template**: Title, Status, Context, Decision, Consequences.
- **Status** is `Proposed`, `Accepted`, `Deprecated`, or `Superseded by ADR-NNNN`.
- Accepted ADRs are immutable. To change a decision, write a new one that supersedes it
  and update the old one's status — do not edit the history.
- In-place amendments are allowed **only when they change no decision**: dated pointer
  notes recording who delivered it, a correction, or an implementation divergence.

## Index

| ADR | Title | Status |
|-----|-------|--------|
| [0001](0001-the-lab-server.md) | The lab server — training off the page, without changing what ships | Accepted |
| [0002](0002-the-sixth-detector-is-called-locust.md) | The sixth detector is called locust, not CICADA | Accepted |
| [0003](0003-parity-was-the-inheritance-not-the-contract.md) | Parity was the inheritance, not a standing contract | Accepted |
| [0004](0004-ci-installs-torch-from-the-cpu-wheel-index.md) | CI installs torch, and takes it from the CPU wheel index | Accepted |
| [0005](0005-detectors-and-models-are-objects-in-a-folder.md) | Detectors and models are objects in a folder | Accepted |
| [0006](0006-a-false-alarm-is-coincidence-the-event-rates-explain.md) | A false alarm is a call on coincidence the event rates explain | Accepted |
| [0007](0007-bugarach-sessions-do-not-act-in-interface2.md) | bugarach sessions do not act in interface2; a request states the outcome, not the tool | Accepted |
| [0008](0008-the-event-floor-is-set-per-window-from-its-own-null.md) | The event floor is set per window from its own null, and never below 3 ROIs | Accepted |
| [0009](0009-the-bench-keeps-its-elevated-rate-test-in-a-recording-of-its-own.md) | The bench keeps its elevated-rate test in a recording of its own, and ADR-0008's floor applies unchanged | Accepted |
| [0010](0010-tune-train-and-review-against-the-data-as-they-are.md) | Tune, train and review against the data as they are | Proposed (revised 2026-09-25: full panel) |

**The habit lapsed for 25 days and restarted on 2026-09-23.** After ADR-0005 on 2026-08-29
no ADR was written, and nothing decided to stop. Rulings went instead into bench-constant
comments, handoffs, todos, the MILESTONES "decided" rows, the goal pages and the ruling
queue. Each of those says *that* something was decided; none is one immutable record of
context, decision and consequences, so a later session could reopen a ruling without
seeing why it was made. 0005 itself never reached this index. Tony, 2026-09-23: *"let's
restart the adr habit and backfill as needed."* So:

- **A ruling that settles how work is done lands here**, in the same PR as the first place
  the work reads it. The [ruling queue](../decisions_pending.md) stays the queue: an item
  leaves it by becoming an ADR, or a line in a goal page when it is too small for one.
- **Backfill is as needed, not wholesale.** When a session leans on a ruling from the gap,
  it writes the ADR then. The candidates are listed in
  [the backfill todo](../todo/2026-09-23-adr-backfill-candidates.md).
- **Every ADR file is in this index**, checked by `tests/test_adr_index.py`, because the
  one that went missing was the last one before the gap.

**`0003` was reserved-not-skipped for four days, and is now filled.** Nine files cited
it while it did not exist, because it was written and green on
`parity-was-the-inheritance` when PR #298 was closed without merging and nobody knew
whether that was deliberate. Tony answered it on 2026-08-30 by asking for the branch to
be merged. The nine citations resolve; the question that held the number is closed.
