# ADR-0023: bugarach does not combine data streams; the export is final

## Status

Accepted, 2026-11-12, by Tony: bugarach is not responsible for combining data streams, and
bugarach assumes the exports are final. Its job is characterizing coordination.

Numbers 0020 to 0022 are taken by records in open pull requests (#923, #924) and are not on
`main` yet.

## Context

**The lab has three streams: fast, slow and combined.** On 2026-09-22 Tony asked for the fast
and slow onsets to be fed through the pipeline as one stream with their labels kept, and
treated from then on exactly as fast and slow are.

**A bugarach session read "the pipeline" as bugarach's own.** That night it built the merge
here (`src/bugarach/combined.py`, PR #752): every fast and every slow onset of a ROI in one
train, each labelled with its source, nothing dropped. It did not ask who should build the
stream, and nothing was sent to interface2. The export contract
(`docs/export_folder_spec.md`) was not revised and does not mention a combined stream, so
every export since has conformed while carrying fast and slow only.

**Nothing recorded the choice.** The decision records restarted the next day. The combined
stream was described on a goal page and in a module docstring, and every later piece of work
took it as settled: the third bench, the raster pages, the settings files, the detect path,
and on 2026-11-11 a request to interface2 for an export with "both streams, fast and slow".

**It came out on 2026-11-12**, when the tracked DI and MALE cohorts became the default dataset
and Tony asked whether the export held the combined stream. It did not.

**Why it matters beyond ownership.** Building a stream means deciding which events are in it.
bugarach made that decision twice, two ways: `combine` keeps every onset, and an earlier
report tool dropped a slow onset within one frame of a fast one. The goal page itself says
that which events belong to which stream is the producer's to state. This is the same error
as a consumer-side exclusion filter (CLAUDE.md, "The export folder is the input"), made on
streams where the earlier ones were made on recordings and ROIs.

## Decision

1. **bugarach does not construct streams.** It does not combine, split, deduplicate or
   re-derive them. A stream is what the export's `stream` column names, with the events the
   producer put in it.
2. **The export is final.** bugarach assumes the folder holds what is to be analysed, in the
   form it is to be analysed in. This extends the standing rule on recordings and ROIs to
   streams and to the events in them.
3. **bugarach's job is characterizing coordination** in the streams it is given.
4. **Something missing from an export is a request to the producer**, stating what should
   exist afterwards (ADR-0007). It is not built here in the meantime.

## Consequences

- **The combined stream has to come from interface2**, and the export contract needs a
  revision that says so. Both are owed and neither is done by this record.
- **`bugarach.combined` is on its way out.** It is retired when an export carries the
  combined stream. Until then, this session's reading is that no new result is produced from
  bugarach's merge; Tony has not ruled on the interim.
- **What already rests on bugarach's merge is provisional:** the combined bench's measured
  values, the combined settings, and every page that draws a combined stream, including the
  four raster pages of 2026-11-12 on the tracked cohorts. Fast and slow are unaffected.
- **A producer's combined stream may differ from bugarach's merge.** Which events it holds is
  the producer's statement, and anything measured on the merge is re-measured on it, not
  carried over.
- **The check for the next mistake of this kind:** code under `src/bugarach` or `tools` that
  makes a stream the export does not name, or changes which events a stream holds, is against
  this record. It is not mechanized yet.
