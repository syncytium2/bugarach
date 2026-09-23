---
status: resolved
opened: 2026-09-23
resolved: 2026-09-23
area: data
---

# The treatment windows were never missing — a calls table has no row for a region nothing called in

**Resolved the day it was raised, and the export needs no change.** Recorded because the hold it
caused should lift, and because the reading error behind it will recur.

## What was suspected

`interface2#3` asked whether the default export was missing a first-treatment window for two
recordings: `20241216_137`, whose treatment the lab's own record gives as SB222200, and
`20250808_186`, which the lab counts as a TTX recording. The detection calls showed neither
window. A crossed-labels hypothesis was raised for `20241216_137` against `20241216_135`, the
other slice from the same mouse on the same day.

## What the region tables actually say

Read directly from `regions.csv` in `2026-09-17_revised_2v_long_STEPS_AND_PINS_EXCLUDED`.
**Every window is present and correctly labelled.**

| recording | group, mouse | regions, in `region_idx` order |
|---|---|---|
| `20241216_135` | ORX, 54 | baseline · **SB222200** · senktide |
| `20241216_137` | ORX, 54 | baseline · **SB222200** · senktide |
| `20250808_186` | ORX, 60 | baseline · **TTX** · wash · high K+ |

`20250808_186`'s rows are identical in the archived `2026-09-03_..._STEPS_EXCLUDED_TTX` subset,
which also carries the recording. And the two 16 December slices read *alike*, so nothing was
crossed — there is nothing to cross.

## Why the calls looked like a hole, and why this will happen again

A calls table has a row only where a detector called. **Region 2 produced zero calls in both
recordings**, so it contributed no rows and vanished from a census taken off that table. The
tell is the gap in `region_idx`: `20250808_186` shows 1, 3, 4 and `20241216_137` shows 1, 3.

⚠ **This is systematic, not bad luck.** Any treatment that lowers calls in some recordings makes
its window the one a calls table can be empty in, and a first-treatment census built from
detection output then under-counts that treatment in particular: the failure is correlated with
the thing being counted, which is the kind that survives a sanity check.

**Corrected 2026-09-23, by the orchestrating session.** This paragraph first said *"TTX is the
condition meant to abolish activity"*. That is the textbook prior FOUNDATIONS §9 forbids in terms:
in this preparation coordination persists under TTX, with the slow stream at or above its own
baseline in 44% of slices. What is true of these two recordings is narrower, and it is all this
note needs: region 2 had no calls from any detector. It says nothing about what TTX or SB222200 do.

**Read `regions.csv` for what a recording contains. Read the calls for what was called in it.**

## The cohort, from the region tables

First treatment per group, default folder, 84 recordings, nothing filtered or relabelled:

| first treatment | DI | OVX | MALE | ORX | total |
|---|---|---|---|---|---|
| senktide | 6 | 8 | 5 | 10 | 29 |
| TTX | 11 | 9 | 9 | 9 | 38 |
| SB222200 | 0 | 1 | 6 | 5 | 12 |
| (baseline only) | 0 | 2 | 2 | 1 | 5 |
| **total** | **17** | **20** | **22** | **25** | **84** |

The archived senktide and TTX subset folders are **identical sets** of recording IDs to this
partition — checked both directions, no strays, not merely equal totals. Twelve recordings are
SB222200-first and so sit outside both subsets; two of them (`20241216_135` and `_137`) reach a
senktide window later.

## Consequences

- **The hold lifts.** Treatment-comparing analyses on these three recordings were paused pending
  a producer answer. The labels were right throughout; no re-export is needed and these do not
  need to ride the `_346` re-export.
- **Nothing was relabelled or filtered** at any point, which is the export-folder contract
  working as intended: the suspicion went to the producer instead of becoming a consumer-side fix.
- **The finding reached `interface2#3`** on 2026-09-23, posted by the orchestrating session, and
  the issue was closed with nothing for the producer to do.
