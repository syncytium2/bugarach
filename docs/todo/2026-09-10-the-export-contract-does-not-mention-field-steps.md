---
status: open
filed: 2026-09-10
---

# The export contract does not mention field steps, and the loader drops both columns silently

> Costs nothing on the current folder. Costs a great deal on the next one.

## The gap

The 2026-09-03 export ships two per-event columns, `on_field_step` and `field_step_id`, recording
whole-field brightness artifacts — a real contaminant here, since a brightness step makes **74 % of
cells in the fast stream and 82 % in the slow** appear to fire at once, which is exactly the
signature a coordination detector exists to find.

[`export_folder_spec.md`](../export_folder_spec.md) **does not mention field steps at all** —
verified 2026-09-10, zero occurrences. So:

- a future export has **no stated obligation** to carry those columns, and no definition to carry
  them under;
- `io.py` recognises only `width_sec` / `width_def` / `peak_sec` / `amp` beyond `roi` and `time_sec`,
  and `store.Stream` has no per-event flag field, so **`csv.DictReader` picks both columns up and
  discards them with no error**.

## Why it is harmless now and not later

On `steps_excluded` every surviving row reads `0` for one column and is empty for the other, because
the producer **removed** the offending events rather than flagging them. So nothing is lost today.

⚠ **The `FLAGGED_FOR_REVIEW` companion export cannot be read correctly here at all** — it flags
instead of removing, and the flags evaporate at load. A consumer would analyse contaminated events
with no error and no warning, which is the failure class this contract exists to prevent.

## What closing it looks like

1. The contract defines both columns — name, type, meaning, and whether they are required or
   optional — the way it defines `width_def`.
2. The loader either carries them or **refuses** a folder that has them, rather than dropping them.
   Silence is the defect.
3. Whichever is chosen, `tests/test_io.py` asserts it, so the alarm can ring.

⚠ This is **contract surface shared with the producer**, so item 1 is a conversation, not a
unilateral edit — the same rule that governs the rest of `export_folder_spec.md`.

## Provenance

Found by the murderboard on 2026-09-10 while checking a claim in a withdrawn proposal; the
`current_export.toml` note about the silent drop predates it and is the producer's own.
