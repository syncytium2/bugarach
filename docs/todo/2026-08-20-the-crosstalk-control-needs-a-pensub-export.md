---
status: open
filed: 2026-08-20
---

# The crosstalk control has no export folder, so it can no longer be run

**A request to the producer, not a gap in the analysis.** Store access is closed and the
export folder is the whole input (`docs/export_folder_spec.md` rev 6). Every part of the
assembly work has been moved onto that footing **except one**, because the data it needs
has never been exported.

## What is missing

A **penumbra-subtracted export folder**. It exists only as a `.mat` store —
`processed_archive/event_store_onset_pensub_revised_2v`, 85 recordings — and
`exports/bugarach/` has three folders, none of them pensub.

## Why it matters more than the other store readers

The crosstalk control is the check that makes the co-participation result *mean* something.
Both nulls reshuffle a membership table that has already been built, so optical overlap
between neighbouring ROIs survives every reshuffle — **the artifact is in the table**. The
only way to answer it is to rebuild the table from recordings with the overlap subtracted.

That control is the source of these, which the assembly report currently states:

> the departure survives in **21 of 26** fast and **21 of 25** slow; all nine discordant
> recordings move the same way, sign test p ≈ 0.004, from nine different animals.

**Those numbers came from a `.mat`-against-`.mat` comparison** and cannot be reproduced under
the current policy. They are not withdrawn — nothing suggests they are wrong — but they are
now the only claim in that report resting on a read the project no longer permits, and they
carry a `⚠` saying so.

## What would close it

One export folder of the penumbra-subtracted recordings, conforming to the same contract as
the others: one CSV per recording, plus `slices.csv` and `regions.csv`. Then
`tools/assembly_pensub_compare.py` runs against two folders and the control is reproducible.

**It should carry the producer's own selection**, like the others — the pensub `.mat` store
holds 85 recordings where the current export folder holds 84, and the difference is exactly
the kind of thing the consumer must not resolve for itself.

## The cheaper alternative, if a pensub export is not coming

Say so, and the report states the crosstalk control as a **historical result** with its
provenance named — measured on 2026-08-19 against the `.mat` stores, not reproducible from
the current inputs. That is honest and costs nothing further. What must not happen is the
number staying in the report with no indication that nothing can re-derive it.
