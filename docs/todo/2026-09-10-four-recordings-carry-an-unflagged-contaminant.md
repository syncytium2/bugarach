---
status: open
filed: 2026-09-10
---

# Four recordings carry a known motion-correction contaminant that no column flags

> **In or out of training — Tony's call**, and it needs the producer's view.

## What it is

[`current_export.toml`](../../current_export.toml), under `steps_excluded`, carries the producer's
own caveat: non-rigid motion correction **pinned 12 ROIs to the frame floor** across four
recordings. The note says in terms: *"Not flagged in any column."*

All four are inside the senktide/TTX cohorts — the exact 67 recordings a self-supervised detector
would train on.

## Why it bites this work specifically

A frame-floor-pinned ROI is a **cross-cell artifact**: several cells driven to a common value by the
same registration failure. A surrogate-contrastive objective is trained to find precisely
cross-cell structure that a rate-matched null cannot explain, so it is rewarded for finding this.

That is the same mechanism as the field-step problem, which the producer *did* fix — and which the
proposal correctly named as a precondition. This one has no such fix and no flag, so it is invisible
to any consumer that trusts the columns.

⚠ **Do not filter it here.** *"The export folder is the input. The store is closed."* Which
recordings are analysable is the producer's call, already applied; going around that rule cost a
real error once and Contract revision 6 records it. If a folder looks like it contains something it
should not, that is **a conversation with the producer**, not a filter in the consumer.

## What to ask the producer

- Should those four be withdrawn from the export, or is the pinning tolerable for analysis?
- If tolerable, can the affected ROIs be **flagged in a column** so a consumer can see them, the way
  field steps were?
- Is the pinning per-ROI for the whole recording, or windowed?

## What happened instead, 2026-09-10 → 2026-09-17

This page said *"conversation with the producer"* on the day it was filed. Nobody had that
conversation for a week, and the work ran anyway:

| date | what | and the contamination was |
|---|---|---|
| 2026-09-10 | filed here | named, with the question to ask |
| 2026-09-14 | a review verified it | cited |
| 2026-09-17 | the rigid-shift report's fourth blind round (role 1) | cited again |
| 2026-09-17 | the slow-co-modulation page's review | cited again |
| 2026-09-17 | the rigid-shift run trained and scored over all four recordings, and **shipped the contamination as a caveat about its own result** | disclosed |

Four rediscoveries, no question asked. **A note everybody cites and nobody acts on is not a
safeguard**, and disclosing is not asking.

**Tony's ruling, 2026-09-17:** a known contamination is a full stop, not a caveat — *"there's no
point in running all of this when you know there's a problem"*. Mechanized the same day:
`dataset.current()` raises `ContaminatedExport` for any role whose note declares a contamination the
folder does not flag, so every analysis resolving its input through the pointer inherits the stop
(`src/bugarach/dataset.py`, `tests/test_dataset.py`). Today that is `steps_excluded` only.
`BUGARACH_ACK_CONTAMINATION='<why this analysis is unaffected>'` overrides it and echoes the reason,
so an override is visible in the run log.

## What this cost the rigid-shift work, concretely

All four recordings are among the 84 that run scored, and in the folds its real-trained models were
fitted on. **All four are DI** (verified in `slices.csv`), which is the group whose co-activity reads
highest in that report's own per-group breakdown — so the contamination is concentrated exactly where
the strongest real-recording signal is. A frame-floor-pinned ROI is a cross-cell artifact and that
report's objective is trained to find cross-cell structure a rate-matched null cannot explain, so it
is rewarded for finding it. Nobody has measured the size of the effect, and nobody should: the
consumer may not filter the export, so the answer is the producer's.

The report now carries a stop notice at its head rather than a footnote, and the
`docs/MILESTONES.md` row that quotes its real-recording numbers says they are not to be leaned on.

## Also filed on the producer's side

`interface2` main, `roi_exclusion` (commit `c1069da1`) carries the same question from that side:
were the affected events cut on the producer side, can a consumer tell, is the pinning windowed or
whole-recording, and did the census cover all 85 slices. ⚠ An open interface2 todo from 2026-09-02
says the census may be incomplete and ranks `20260629_314` and `20260630_325` beside the known four —
so *"four recordings"* may itself be the floor rather than the count.

## Closes when

Either the producer withdraws or flags them, or Tony rules that they stay unflagged and the decision
is recorded where a training run would read it. **Until then the stop stands**, and any analysis that
proceeds does so with an acknowledgement naming why its measurement is unaffected — a reason about
the measurement, not about the schedule.
