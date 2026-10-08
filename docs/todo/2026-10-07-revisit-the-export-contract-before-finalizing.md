---
status: open
filed: 2026-10-07
---

# Revisit the export contract one last time before finalizing

**Tony, 2026-10-07:** *"make a note to revisit the export contract one last time before
finalizing."* Before any result is called final, read [`docs/export_folder_spec.md`](../export_folder_spec.md)
top to bottom against what the analysis now relies on, and settle every gap with the producer.
That is a conversation with the producer, never a filter in bugarach (CLAUDE.md, "The export
folder is the input").

What came up on 2026-10-07 that the contract does not yet say, or says only by implication:

- **How fast and slow are assigned.** Working rule (Tony): custard finds every event, a slow pass
  finds the slow ones, and fast is custard minus the one custard event within 2 s of each slow
  event, so no event is in both streams. It is recorded as an assumption on
  [`goals/combined-stream-coordination.md`](../goals/combined-stream-coordination.md); the
  producer's own statement is still owed, and nothing measured here can check it.
- **`width_def` differs by stream.** Fast's width is the half-prominence width, slow's the rise
  interval (`current_export.toml`). Anything reading width as duration, on combined above all,
  needs the contract to say so plainly.
- **The frame interval.** Every recording states `frame_interval_sec` in `slices.csv`, and the
  ones checked are 0.1 s. FOUNDATIONS §6 keeps it required at load, and internal work assumes
  0.1 s (Tony, 2026-10-07).
- **Combined's closest events.** Distinct combined events a few seconds apart are visible on the
  September pilot rasters. Per-stream merge gaps depend on how close real events can be, and the
  gap measurement that set the realistic bench merged events under 2 s apart first.

Already open and in the same territory: decision 4 in [`decisions_pending.md`](../decisions_pending.md)
(the export contract fireflies proposes), and the contract todos
[`2026-08-20-the-contract-asks-for-width-and-drops-it.md`](2026-08-20-the-contract-asks-for-width-and-drops-it.md),
[`2026-09-10-the-export-contract-does-not-mention-field-steps.md`](2026-09-10-the-export-contract-does-not-mention-field-steps.md)
and [`2026-08-18-experimental-groups-are-not-in-the-import-contract.md`](2026-08-18-experimental-groups-are-not-in-the-import-contract.md).
