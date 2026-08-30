---
status: open
filed: 2026-08-30
---

# The rail's last ~97px cannot be trimmed — it has to be argued

> **Not murderboarded** — a work item. Filed by a session that did **not** do the
> measurement, from `bugarach-63`'s handover at its session end on 2026-08-30.

## What already landed

**PR #411 (`0188362`)** took the viewer's canvas top from **514px → 351px** at
1440×900: the header went, its privacy promise moved into the nav, `#demoNote`,
`#meta`, `#bar` and `#wins` merged into one row behind a four-state provenance chip,
the rail was **tightened, not redrawn**, and the diagnostic page now leads with its
figure with the legend in a closed `<details>`.

## What is left, and why it stopped

About **97px** of rail remain, and the session that measured it stopped rather than
take them, because **the remaining trim is not a trim.** Getting them requires
collapsing two grid rows, and the rows are not decoration — **collapsing them changes
what the diagram asserts.**

That makes it a claim about the pipeline, not a layout tweak, and it is the reason
this is a todo and not a follow-up commit. A session optimising for pixels would take
them without noticing the assertion moved.

## What is actually undecided

- **What do the two rows currently assert**, and is that assertion load-bearing for a
  reader who has not seen the pipeline before?
- Is 97px worth a weaker diagram? The screenshot that started this had the raster at
  **43% of its own page**; after #411 it is not, so the pressure that justified
  aggressive trimming has largely been spent.

⚠ **Do not treat this as a continuation of #411.** #411 was cosmetic by construction
and said so; this one is not, and inheriting its "cosmetic" framing is how the
assertion would get changed silently.

## Not authorized

Handed over, not started. Tony pulled that session up for scope on 2026-08-30 —
*"address this critique does not mean run wild"* — so the existence of this file is a
record, not a go-ahead.
