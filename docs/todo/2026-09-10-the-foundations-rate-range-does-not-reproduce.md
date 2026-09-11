---
status: open
filed: 2026-09-10
---

# FOUNDATIONS §9's per-ROI rate range does not reproduce from any current folder

> **Needs its own review before FOUNDATIONS changes.** FOUNDATIONS is canonical; this todo does not
> edit it.

## What was found

FOUNDATIONS §9 gives baseline's interquartile per-ROI rate as **0.0052–0.0190 Hz**, re-derived
2026-08-20 "from the export folder". The murderboard on the surrogate-screen plan (2026-09-10)
recomputed it from the baseline regions of the current export folders — `steps_excluded` and
`senktide` — every way that range could plausibly have been computed: per stream and pooled, with
and without zero-event ROIs, per ROI and per recording. **None of them gives that range.** Counting
zero-event ROIs, which FOUNDATIONS §9 itself says must stay in, the lower quartile is zero.

The recomputation is a one-liner over `regions.csv` and the per-recording CSVs; its numbers are
deliberately not written here (FOUNDATIONS §5).

**A clue, before anyone recomputes anything.** GLOSSARY's **regime** entry describes the same two
numbers as *"the p25 of baseline slices"* and the p75 — a quartile across **recordings** — where
FOUNDATIONS §9 calls them a quartile of the **per-ROI** rate. The two canonical documents already
disagree about what the number is a quartile of.

## Why it matters

The range is quoted as the difficulty axis for the bench ("use the spread among untreated slices")
and was quoted — then dropped — as the estimability basis in the surrogate-screen plan. If it was
computed on a folder that has since been superseded, or with zero-event ROIs excluded, every use of
it inherits that choice without saying so.

## Closes when

Someone establishes which folder and which convention produced the §9 figure, and FOUNDATIONS either
states that convention beside the number or carries a re-derived one — through a change reviewed on
its own, since §9 binds analysis.
