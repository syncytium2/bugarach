---
status: open
filed: 2026-08-22
---

# A back route, for when the pipeline has earned one

Tony, 2026-08-22:

> *"ultimately there will be a backdoor route to automate so users are just
> feeding a reliable pipeline (once it exists). again not a release priority but
> todo."*

**Not a release priority.** Filed because the decision it depends on was made the
same day and would otherwise be lost.

## What it is

A route that skips the click-through, so a lab points at a folder and gets
detections without driving the steps by hand. The front door stays as it is: the
page insists a person chooses K, looks at the comparison, and picks a stream,
because at this stage every one of those is a judgement the tool refuses to make
for them.

## Why it cannot come first

The back route can only automate decisions that have stopped being decisions. Two
of the current gates exist precisely because the answer is not settled yet:

- **K is a scan, not a choice** — the assessor reports every K that clears the
  floor and refuses to pick one.
- **Compare will not rule on whether the gap is acceptable** — that depends on
  what the simulated data is for, and it is a step you click through with
  complaints rather than a check that passes silently
  ([`2026-08-22-compare-is-a-step-you-click-through.md`](2026-08-22-compare-is-a-step-you-click-through.md)).

Automating those today would not be a convenience; it would be the tool quietly
answering the questions it was built to put in front of a person. The order is:
the pipeline becomes reliable, *then* it gets a back route — not the reverse.

## What it needs first

- Settings as a loadable file, so a run can be specified rather than performed —
  [`2026-08-22-tuned-settings-are-a-file-not-a-survivor.md`](2026-08-22-tuned-settings-are-a-file-not-a-survivor.md).
- The stream fixed by the input rather than by the interface —
  [`2026-08-22-the-stream-is-chosen-at-the-door.md`](2026-08-22-the-stream-is-chosen-at-the-door.md).

With both, the back route is close to a function of (folder, settings file) and
mostly already exists: `analyseFolder` walks a folder and writes the same rows the
on-screen run does, deliberately through one shared `detectOne` so the picture and
the file cannot drift.
