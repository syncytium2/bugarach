---
status: open
filed: 2026-08-18
revised: 2026-08-18
---

# The contract already carried what an analysis went outside for

> **Revision.** The first version of this file said experimental group was missing from
> the import contract and proposed adding it. That was wrong, and wrong in the
> direction that matters: `group_id` and `mouse_id` were already in `slices.csv`, in a
> conforming export folder that existed before the analysis started. The defect was
> never the contract's coverage — it was an analysis that read `.mat` files and never
> looked. What survives below is the narrower set of things the contract genuinely
> cannot express.

## What happened

On 2026-08-18 the assembly measurement was run over
`processed_archive/event_store_onset_revised_2v_alive_rescued` — a `.mat` store —
because that path was the one to hand and `assess_archive.py` globbed `*.mat`.
Meanwhile `exports/bugarach/2026-08-17_revised_2v` had existed since the previous day,
conforming to [`docs/export_folder_spec.md`](../export_folder_spec.md) revision 3, and
carried everything the analysis then went looking for elsewhere.

Three consequences, in increasing order of how much they cost:

- **Metadata was re-derived from outside the data.** A loader was written to pull group
  and animal out of a spreadsheet on a Dropbox mount. `slices.csv` had both columns.
  The loader has been deleted.
- **A withdrawn recording was analysed.** The folder's producer applies the lab's
  exclusions before writing; the `.mat` store does not. Reading the folder, the
  excluded slice would never have appeared.
- **The wrong window was scored on 24 of 84 recordings.** `regions.csv` separates
  `start_sec`/`end_sec` — what happened — from `analysis_start_sec`/`analysis_end_sec`
  — what to score. `assess_archive.py` used the raw period, which on this corpus ran up
  to **660 s longer**. More window is more clusters and more power, unevenly across the
  corpus. Fixed: the tool now honours the analysis window and reports how many
  recordings had one.

The check that was supposed to catch the third one passed. It compared the analysed
window against the workbook's raw baseline period — the same quantity, from a different
source — and agreed on every slice. It was measuring the wrong thing and could not have
failed.

## What the contract still cannot say

Reading the folder fixes the analysis. Two gaps in the spec itself remain, and both are
now narrower than the first version of this file claimed.

**1. The spec forbids interpreting the identity columns.** `slices.csv` names
`group_id` and `mouse_id` as examples of an open set, and the same section says
bugarach

> passes through to its output unchanged and **interprets not at all**. It does not
> know what a mouse is.

FOUNDATIONS §9 says a pooled across-group number is not admissible on its own. An app
forbidden to interpret group cannot produce an admissible corpus result. The resolution
keeps what that sentence protects: **interpret the ROLE of a column, never the meaning
of its values.** Reserve `group_id` as *the design factor to split by* and `subject_id`
as *the independence unit*; values stay the lab's own and uninterpreted. bugarach still
does not know what a mouse is — it knows which column says two recordings came from
one.

**2. Exclusion and provisional status are producer-side only.** This producer drops
excluded recordings before writing, which is a clean answer. But the contract has no
way to *say* a recording was withdrawn, so a folder cannot distinguish "this corpus is
complete" from "someone silently dropped 12". A count in `PROVENANCE.md` is prose, not
a column. Likewise the lab marks some rows provisional; nothing in the folder can carry
that, so a caveat that belongs on a result is unavailable to the tool computing it.

## What a fix looks like

- Reserve `group_id` and `subject_id` with defined roles; keep every other column
  pass-through exactly as today.
- Add an optional `excluded` column, so a folder can be self-describing about what it
  omits rather than relying on a prose note.
- A corpus result that had no `group_id` available should say so on its face — a sapper
  rule can catch a result written from a folder that lacked it.

## The one that has no todo yet

`assess_archive.py` will still read a `.mat` store when asked. Nothing warns that a
conforming export folder sits beside it, and nothing in the repo prefers the contract
over the raw store. That is how this happened, and a warning at load — *"this store has
an export folder; the folder carries windows and identity this path does not"* — is
cheaper than the day it cost.
