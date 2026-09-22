# Goal: one stream for coordination, and a call that says which events it recruited

**Set by Tony, 2026-09-22.** Combine fast and slow into a single stream for coordination
detection, and — the part that makes it worth doing — identify the individual events from
each stream inside a coordinated event.

**Status: not started.** No machine, no branch, no result. This page exists so the goal is
findable and so the question under it is asked before any of it is built.

---

## The goal

Every coordination result this repository has produced runs **one stream at a time**. A
coordinated event that recruits three cells in the fast stream and two in the slow one is
not a five-cell event in any output today: it is a three-cell call and a two-cell call, or
it is below threshold in both passes and is nothing at all. The goal is a detection that
sees the recruitment whole, and a call whose membership still names which stream each
recruited event came from — the second half being what keeps the result interpretable
rather than merely larger.

## The question that comes first, and it is not ours to answer

**The two streams may be drawing from one pool of events.** If they are, a combined stream
double-counts, and every number built on it inherits that.

What the export contract already settles
([`export_folder_spec.md`](../export_folder_spec.md), extended 2026-08-28):

> Event detection in this lab's pipeline is **methodically identical** in the fast and slow
> streams. What differs is a preprocessing step applied only when exporting to bugarach —
> full width at half maximum as the fast stream's duration, the rising phase for the slow
> one. Nothing upstream of the export differs, so this is a property of *the file*, not of
> the recording and not of the detection.

That settles the **width**. It says nothing about **membership**: what decides that a given
calcium event is a fast event rather than a slow one, and whether one transient can produce
an event in both streams. The contract's own sentence is the reason to ask rather than
assume — if the detection is methodically identical, the split has to come from somewhere,
and that somewhere is upstream of anything this repository can see.

**That question goes to the producer** (interface2), by the same rule that governs the
pinning question in [`decisions_pending.md`](../decisions_pending.md): the export folder is
the input, the store is closed, and a property of the preparation or the export is the
producer's to state rather than ours to re-derive. Three parts:

1. What assigns an event to the fast stream or the slow one?
2. Can one calcium transient yield an event in both streams?
3. If it can, is there a key — an event id, a source index — that would let a consumer pair
   them, or is pairing ours to infer?

## What we can measure here first, without waiting

**One figure answers whether the pool is shared, on the default export folder, today.** Per
ROI, take every slow onset and find the nearest fast onset in the same ROI; plot the
distribution of those gaps against the frame interval. A mass piled at zero, within a frame
or two, is a shared pool: the same transient recorded twice under two width rules. A
distribution with no such peak is two populations, and the goal is straightforwardly
worth building.

This is cheap — it reads onsets that are already loaded, needs no detector and no
simulation — and it is the kind of evidence the producer's answer should be checked
against rather than replaced by. Related and already measured: the onset correlogram in
`docs/learned/runs/2026-09-22-jitter-correlogram/` notes that the slow stream's peak carries
a tail one jitter does not make, **and that a shared same-frame artefact would read the same
way**. That is a hint pointing at this question, from a measurement made for another one.

## Step 1 — one raster, both streams, coordination in the lane above

Tony's first step, and the drawing primitive for it already exists.
`bugarach.ui.diagnostic.raster_panel` takes `marked` / `marked_ink`, and its docstring
argues the case in terms of the never-draw-on-the-raster rule: a second ink is allowed here
because **nothing is added** — each event is still drawn exactly once, in exactly one place,
and the ink says which of two populations *the producer* put it in. Drawing the producer's
own partition of their own events is the raster, not an annotation on it. Detections stay in
the lane above, where this project's own claims live (sapper SAP009).

So: fast and slow onsets on one set of ROI rows, the slow ones in the second ink, the
coordination calls in the lane above, pointing down. What does not exist yet:

- **Nothing in the tree combines two streams.** There is no `combine_streams`; the union per
  ROI has to be built. `Stream` carries `locs`, `amp`, `width` and `t50rise` as per-ROI
  arrays, so the union is mechanical — but the **width** of a combined stream is not, since
  the two arrive under different `width_def` rules and locust reads that column.
- **ROI identity across streams is safe to assume.** FOUNDATIONS §9: an ROI verdict is
  computed once on the combined signal, precisely so that an ROI alive in the slow stream is
  not rejected on the fast one. The ROI is already one object to the exporter.

## What it costs, in the terms this repository already uses

| what it needs | why, and what already exists |
|---|---|
| **A third parameter set** | `detect_folder.load_settings` keys rows by `(detector, stream)`, so a combined stream is a third value in a column that already exists rather than a new mechanism. ⚠ `bench.OPERATING_POINTS` has **no** stream dimension and must not grow one for this — the slow settings are already kept out of it for the same reason |
| **A third bench** | `bench.py` is fast, `bench_slow.py` is slow, both under the stopgap that [`todo/2026-09-21-one-stream-aware-bench.md`](../todo/2026-09-21-one-stream-aware-bench.md) exists to end. A third copy of the scoring path is a strong argument for that rebuild landing **before** this goal starts, not after |
| **Another set of rasters** | the per-cohort raster pages are built per stream today (the slow set landed 2026-09-22, PR #719) |
| **Another fireflies cohort** | `stream` is a column every consumer parses, and their adapter reads by name with no fallback. A third value is a contract change, and one is already in flight — see item 4 of [`decisions_pending.md`](../decisions_pending.md) |

## Open questions

1. **Producer:** the three membership questions above. Nothing downstream is worth building
   until they are answered, except the gap figure, which helps ask them.
2. **Tony:** does this start before or after the jitter ruling and the slow stream's last
   step? Both of those move benches this goal would inherit.
3. **Tony:** does a combined stream **replace** the two passes or sit beside them? Three
   streams reaching fireflies is a different contract change from two.

## Where the work lives

Nowhere yet. The first artifact will be the gap figure; it belongs in the darkroom under a
claimed folder, with the repo copy beside it.

## Keeping this page true

A result lands in the same change as the page row that describes it. If this page and the
tree disagree, the tree wins and the page is wrong — fix it in the same commit as whatever
you were doing.
