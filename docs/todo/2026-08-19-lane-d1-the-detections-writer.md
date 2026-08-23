---
status: done
filed: 2026-08-19
closed: 2026-08-23
---

# Lane D1 — the writer, in the library first, so two callers cannot disagree

**Done, and the bet paid off.** `bugarach.emit` settled the shape once, and it now has
**three** callers rather than the two this lane anticipated: the browser's download,
the Panel viewer's Save button, and `bugarach detect` over a whole folder. None of them
invented a column. The browser writes its table in JavaScript, so a test pins its
header to the library's column list — the mechanized version of what this page argued
for in prose.

**One thing the writer has that the browser does not use.**
`write_detector_settings` exists and both Python routes call it; the page writes only
`detections.csv` and `run.json`, and records its parameters keyed by detector where the
contract keys them by **detector and stream**. That is carried by
[`2026-08-22-tuned-settings-are-a-file-not-a-survivor.md`](2026-08-22-tuned-settings-are-a-file-not-a-survivor.md),
which wants the same fix for its own reasons — so it is one job rather than two.

**The acceptance test below was not the one that could be run.** Agreeing with
`bakeoff.json` row for row is a claim about the Python pipeline; three of the six
browser detectors sample, and this project's bar for a port that guesses is behavioural
agreement rather than 1e-9. What was built instead: the browser's table reads back
through the library's reader unchanged, the two detectors that draw no random numbers
match exactly, and the row-for-row claim is made where it holds — the lab server
reproduces the published bake-off per fold.

*Everything below is as filed, kept because it is the reasoning the writer was built
from and the contract it was held to.*

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
the seeds, the code version, and the frame interval per slice.

## How to check it

Round-trip: write it, read it back, compare. `NA` spelled literally, newline-only line
endings, and **a real zero preserved as zero rather than becoming missing**.

Then the acceptance test the plan is built around: point the pipeline at a generated
data set and the exported table must agree with `docs/learned/bakeoff.json` — same
detections, same counts. If it disagrees, the writer is wrong, and that is known on day
one rather than after the UI is built.
