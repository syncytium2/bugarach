---
status: open
filed: 2026-08-28
---

# The producer page talks producers out of sending analysis windows, for a reason that stopped existing on 2026-08-23

**BLOCKING for the next producer conversation, and not introduced by revision 8** — found
by that revision's blind verify pass, in the same document, one section above the width
text. Filed rather than fixed because it is about regions and analysis windows, not width,
and correcting it means re-deriving revision 7's semantics rather than restating them.

## The false claim

`docs/export_for_producers.md` tells producers to **usually leave `analysis_start_sec` /
`analysis_end_sec` out**, and gives two reasons. The second:

> **Supplying it switches a check off.** The raw bounds are validated — baseline starting
> at zero, regions contiguous — and supplying `analysis_*` short-circuits that validation.
> The same corrupted folder passes clean *with* the columns and is caught *without* them.
> So sending an analysis window costs you the structural gate on the raw one.

Those guards were **removed on 2026-08-23**, and the spec's own revision 7 says so in
terms: *"the guards requiring a baseline at 0 and contiguous periods are gone from this
path."*

Verified by building a folder with `baseline` starting at 500 s, an 8,899 s gap between
regions, and no `analysis_*` columns at all: `bugarach check` returns **CONFORMING**. The
check the page says you give up does not exist, so the trade-off it describes is not a
trade-off.

## What else that drags with it

- The first reason (an analysis window is a named paradigm, not a rule) **still stands** —
  so the advice may survive, but on one leg instead of two.
- **`:61`'s "usually leave them out"** now rests on a false premise and needs re-deciding
  rather than re-wording.
- It contradicts the spec's own normative line, **"Send both when you have a windowing
  policy."** Two producer-facing documents giving opposite instructions is the failure
  revision 7 exists to prevent, in a different place.
- The page's own worked example **sends `analysis_start_sec` / `analysis_end_sec` on both
  regions**, twelve lines after telling producers to leave them out.

## The generalisation, which is the reason this is worth a file of its own

This is the *second* instance of the same defect in one document, found in one review.
Revision 8 corrected a stale claim about `width_sec`; this is a stale claim about
`analysis_*`, made stale by the same day's work (2026-08-23), left standing the same way,
and it is worse: the width note discouraged a column, this one discourages a column **and
gives a fabricated engineering reason for it**.

A producer who read it, and who has a windowing policy, has been told sending their window
costs them a validation. It does not. Whatever they decided on that basis was decided on
a false premise.

The recurrence guard proposed in
[`docs/sapper_feedback/2026-08-28-a-negative-claim-about-code-went-stale-in-a-contract.md`](../sapper_feedback/2026-08-28-a-negative-claim-about-code-went-stale-in-a-contract.md)
is keyed on the width phrasing and would not have caught this one. That is the argument
for the general form — a doc↔code pin — over a keyword tripwire, and this is the second
data point for it.

## Also found in the same pass, smaller

- **"Three of the six detectors build their analysis grid from `frame_interval_sec`"**
  matches neither reader. Python: **two** (`rate` via `grid_dt`, `cicada` via
  `imaging_rate_hz`). Browser: **five**. The number is also hard-coded in
  `conform.py:81`, so a producer meets it at `bugarach check` too. Name the detectors
  instead of counting them.
- **`conform.py`'s `NO_WIDTH` note** says "this folder conforms and every detector runs"
  **unscoped** — false for the browser viewer — and calls the detector *"CICADA's
  per_event mode"*, the retired public name (ADR-0002 makes it **locust**; `cicada`
  survives only as an identifier). Both documents are now ahead of the tool, and this
  string is printed to producers.
- **The duplicate-`width_def` rule only sees rows that carry an event.** `_assemble`
  skips `time is None` before collecting `defs`, so a second spelling appearing only on
  `NA` rows loads clean. Confirmed. Narrow, but both documents state the rule without
  that qualification.
