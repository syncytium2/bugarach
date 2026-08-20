---
status: closed
filed: 2026-08-19
closed: 2026-08-20
---

# Two documents specify `detections.csv`, and they do not agree

> ## Closed 2026-08-20 — superseded, and the consumers had already settled it
>
> Tony: *"pretty sure fireflies and matlab have already fixed this."* They had, and
> checking beat both of the readings this file offered.
>
> **`fireflies`** reads `region_idx` and `treat1` out of the export and builds its own
> `treatment` factor **at its own boundary** — `td/fig-auc-beforeafter.R`, whose comment
> says it maps them *"for this call only"*. Its former `region_idx <= 2` filter is
> annotated there as a **no-op tripwire**, so it has already restructured around the
> export's region indexing rather than waiting on a column from us.
>
> **`interface2`** answered the same question in
> `docs/exports/2026-08-17_bugarach_import_contract_reply.md`: *"region 1 always reads
> `baseline` because that is its name. Nothing is overwritten and nothing is missing —
> the baseline is a fixed period in the protocol, not a treatment slot."*
>
> So the narrow row is **superseded**, not a second deliverable, and the projection this
> file proposed adding to `emit.py` **must not be built**: it already exists, on the
> consumer side, which is where `workflow_plan.md` said it belonged — *"our R side
> adapts; it does not get a private dialect."*
>
> Fixed by deleting the restated schema from `docs/webapp_spec.md` and pointing it at
> `docs/export_folder_spec.md`, now the only place the columns are written down. The
> general lesson is the one that caused it: **a schema written in two places drifts in
> one of them.**

Found while building the writer (lane D1). Both are current, both are cited by the
lane's own todo as the source of the columns, and they describe different files.

## The disagreement

[`docs/webapp_spec.md`](../webapp_spec.md) shows:

```
slice_id,treatment,detector,t_start_sec,t_end_sec,n_participating_rois
```

[`docs/export_folder_spec.md`](../export_folder_spec.md) §"What bugarach emits back"
(revision 5, 2026-08-18) specifies:

```
slice_id, stream, detector, mode, region_idx, region_label,
onset_sec, width_sec, n_roi, strength, strength_unit, + identity columns
```

Not a wording difference. **Three substantive conflicts:**

1. **`treatment` against `region_idx` + `region_label`.** The export spec forbids
   the first in terms — *"no privileged region, and no protocol vocabulary … there
   is the index you sent and the name you gave it"* — while webapp_spec's own prose
   agrees with the export spec's *intent* (*"carried through, never inferred"*) and
   then names the column `treatment` anyway.
2. **`t_start_sec` / `t_end_sec` against `onset_sec` / `width_sec`.** An end and a
   width are not the same field, and converting between them is only lossless while
   both are finite.
3. **The export spec carries `stream`, `mode`, `strength`, `strength_unit` and the
   identity columns; webapp_spec carries none of them.** Losing `strength_unit` in
   particular walks straight back into the failure both documents elsewhere say
   they exist to prevent.

## What was built, and why that one

`src/bugarach/emit.py` implements **`export_folder_spec.md`**. Three reasons, none
of them a preference:

- [`docs/workflow_plan.md`](../workflow_plan.md) points at it by name for the
  columns — *"The columns are in `docs/export_folder_spec.md`"*.
- It is the later document (rev 5, 2026-08-18) and the one that reasons about *why*
  each column is shaped as it is.
- It is a **superset**. A fireflies-shaped consumer reads `slice_id`,
  `region_label`, `detector`, `onset_sec`, `width_sec` and `n_roi` out of it and has
  everything webapp_spec's narrow row carried.

## What still needs deciding, and it is not the writer's to decide

**Is the narrow fireflies row a separate deliverable, or was it superseded?**
webapp_spec calls it *"deliberately narrower … the smallest thing the downstream
consumer can use"*, which reads like a second, additional file rather than a
disagreement about the first. If so it wants its own name and its own section, and
`emit.py` gains one function that projects the full table down to it.

If instead it was simply the earlier draft of one file, then webapp_spec's example
block is stale and should point at the export spec rather than restating it — which
is the general fix here anyway: **one document specifies the output and the others
link to it.** Two documents restating the same schema is how they came apart.

⚠ Until this is settled, do not add a `treatment` column to anything. It is
forbidden by the export contract and by FOUNDATIONS §4, and a consumer that learns
to read it will have to unlearn it.
