---
status: open
filed: 2026-08-18
---

# Experimental group is not in the import contract, and the contract forbids reading it

Everything an analysis needs must be in the folder the app reads. Group membership is
not — it lives in a spreadsheet on a Dropbox mount, reachable only from machines that
happen to have it, and `bugarach.groups` currently goes and gets it from there. That
is a bridge built to land one result, and it should not survive as architecture.

## The contradiction, which is the real finding

[`docs/export_folder_spec.md`](../export_folder_spec.md) already anticipates this
metadata. `slices.csv` names `group_id`, `mouse_id`, `sex`, `age`, `cohort` as
examples of its open set of identity columns. So the fields are *allowed*.

The same section then says bugarach

> passes through to its output unchanged and **interprets not at all**. It does not
> know what a mouse is.

That sentence is right about lab-agnosticism and it makes FOUNDATIONS §9
unenforceable. §9 says effects run in opposite directions by group and a pooled
across-group number **is not admissible on its own**. An app that refuses to
interpret group cannot produce an admissible corpus result. Both rules are load
bearing and they are currently in direct conflict; the conflict has been invisible
because no analysis here had group at all.

## What is actually missing

Three things, and only the first is a naming question:

- **A reserved column for experimental group**, with the semantics that analyses may
  split by it. Not a new vocabulary — the lab's own values pass through — but a
  reserved *name* so an analysis can find it without being told.
- **A subject key, reserved.** `mouse_id` is named as an example, which is not enough
  to depend on. Slices are not independent: in the archive read on 2026-08-18, 85
  slices came from 48 dates and up to three shared one animal. Without a reserved
  subject column, every corpus statistic silently treats siblings as independent
  observations, and any combination of per-slice p-values is anti-conservative.
- **An exclusion column. There is none, in any form.** The lab withdraws recordings;
  the contract has no way to say so. Every corpus result computed in this repo before
  2026-08-18 therefore included withdrawn units, and nothing could have caught it.
  This is the gap with teeth — the other two produce a weaker claim, this one produces
  a wrong denominator.

## And the archive path needs it too

The 85-slice corpus was read from a `.mat` store, not from an export folder, so it is
not covered by this contract at all. Whatever is agreed here has to reach that path as
well, or the contract governs the input nobody actually uses for corpus work.

## Proposed revision (revision 4)

Reserve three names in `slices.csv`, keep every other column pass-through and
uninterpreted exactly as today:

| column | meaning |
|---|---|
| `group_id` | the experimental group. Values are the lab's own; bugarach never interprets a *value*, only that the column names the design factor to split by. |
| `subject_id` | the independence unit. Recordings sharing one are siblings, never independent observations. |
| `excluded` | truthy means the producer has withdrawn this recording. Anything reported as a corpus must drop it and say how many it dropped. |

The distinction that resolves the contradiction: bugarach interprets the **role** of a
column, never the **meaning of its values**. It still does not know what a mouse is; it
knows which column says two recordings came from the same one.

Then: a corpus-level result that never read `group_id` is incomplete, and a sapper rule
can say so. Absent columns keep working as they do now — the app reports what is missing
rather than refusing, per the spec's own posture — but a *result* that claims to describe
a corpus while the columns were absent has to say that on its face.

## Until then

`bugarach.groups` is the bridge and is written as one: it resolves the workbook from the
environment, never hardcodes it, refuses rather than guesses, and its tests skip when the
file is absent. **It should be deleted when revision 4 lands**, not extended. Anything
built on it inherits the defect this todo describes — a result that can only be
reproduced on a machine holding a file nobody agreed to ship.

Related: [`2026-08-16-dt-does-not-travel-with-the-recording.md`](2026-08-16-dt-does-not-travel-with-the-recording.md)
is the same shape — a property an analysis needs that is not a property of the recording
— and was resolved by putting the field in the contract and gating the load. That is the
precedent to follow.
