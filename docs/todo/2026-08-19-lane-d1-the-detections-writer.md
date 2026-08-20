---
status: open
filed: 2026-08-19
---

# Lane D1 — the writer, in the library first, so two callers cannot disagree

Plan: [`docs/webapp_completion_plan.md`](../webapp_completion_plan.md). Python only,
**does not touch `docs/site/raster_viewer.html`** — runs in parallel with the merge
train and with lanes C and E.

## The gap

**Nothing in this tree writes a detections file.** The webapp has no `Blob(` and no
download anywhere; the CLI draws pictures and prints. `docs/webapp_spec.md` calls the
output contract the point of the exercise rather than an afterthought, and it says why:
a pipeline that ends in a file can be checked end to end from day one.

The browser will need the same writer. Settling the shape **once, here**, is what stops
the page and the library shipping two dialects of the same table.

## The contract, already written

Columns and rules are in [`docs/webapp_spec.md`](../webapp_spec.md) and
[`docs/export_folder_spec.md`](../export_folder_spec.md). The ones that are decisions
rather than preferences, each with a reason already in the tree:

- **`slice_id` comes from the data**, never a filename or a code argument. Two slices
  differing only by folder name would otherwise collide.
- **`treatment` is carried, never inferred**, and regions are never merged — effects run
  in opposite directions by group, so a pooled row is not admissible (FOUNDATIONS §9).
- **One row per event per detector.** No consensus merging; that is downstream's call and
  merging discards which detector fired.
- **Seconds on the recording's own clock**, with the frame interval in the sidecar.
  Frames are the model's unit; the conversion happens exactly once, here.
- **A slice with no detections emits no rows and is still listed** in the sidecar roster.
  Absent rows are a finding; an absent slice is a bug, and they must not look alike.
- **No viability column, ever.** Not "dead", not "silent", not "inactive" — that verdict
  is the exporter's and this repo cannot compute it (FOUNDATIONS §9).
- **No column changes meaning between rows.** The existing MATLAB-side contract has a
  strength column holding a cell count for some detectors and a rate for another,
  disambiguated by a lookup table shipped alongside; a reader without the table gets a
  plausible wrong answer instead of an error. Here the unit travels in the row.

**Sidecar `run.json`**, because a table of times with no provenance is unusable in six
months: the generator spec, the chosen K, each detector's fitted knob or threshold, the
corpus seeds, the code version, and the frame interval per slice.

## How to check it

Round-trip: write it, read it back, compare. `NA` spelled literally, newline-only line
endings, and **a real zero preserved as zero rather than becoming missing**.

Then the acceptance test the plan is built around: point the pipeline at a generated
corpus and the exported table must agree with `docs/learned/bakeoff.json` — same
detections, same counts. If it disagrees, the writer is wrong, and that is known on day
one rather than after the UI is built.
