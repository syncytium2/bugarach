---
status: done
filed: 2026-08-22
closed: 2026-08-23
---

# One stream in play, chosen when the folder opens

> **Done 2026-08-23, at the selector rather than through the call sites** — which
> is what this file argued for, and it held. `STREAM` is settled when the folder
> opens and read through one accessor, `analysisStream(data)`. The selector
> appears only when a folder holds more than one, and the note beside it says one
> is analysed at a time and where the other went. All three of the disagreeing
> places below now read that single choice, and `detectOne` reading one `cfg`
> before the stream loop stops being a defect the moment there is no second
> stream for it to reach.
>
> A recording that does not hold the stream in play is a **named refusal**, not a
> quiet substitution: analysing its other stream would be a different answer
> under the right label, which FOUNDATIONS §9 rules out in terms.
>
> The lane worry at the bottom was answered by the same move — with one stream in
> play `detectLanes` cannot mix two, and the detect table names the stream
> whenever the folder holds more than one to tell apart.
>
> **What it costs, measured rather than guessed.** A folder run covers one
> stream. The lab's 84 recordings gave 32,640 rows in 55 s against 51,968 in
> 98.8 s for both — the split is exact, the other 19,328 rows are one click and a
> second run away, and both files name which stream they are about. That is what
> "separate folders" means.

Tony, 2026-08-22, working through the viewer's navigation:

> *"most users will have one stream. we should treat fast and slow as separate
> folders (or build this into the folder selector if there are more than one
> streams in the folder/files."*

**The decision.** A folder holding one stream is never asked about it — which is
most of them. A folder holding more is split at the door: the selector offers
fast or slow the way it already offers recordings, and from that point exactly one
stream is in play. Nothing downstream mentions streams again.

## What it fixes, which is not a preference

Three places in `docs/site/raster_viewer.html` disagree about whether a setting
belongs to a stream, and the disagreement is live:

- `tuneLoad` sweeps **one stream** — `streams[0]` — and says so in a comment,
  because the planted truth is per recording and the page's generator writes one
  stream.
- `TUNED[which]` is keyed by **detector alone**. There is no stream in the key.
- `detectOne` reads `cfg = D.read(dt)` **once, before the stream loop**, and
  applies it to every stream. Even deliberately, fast and slow cannot be given
  different values.

So a threshold fitted on fast runs on slow with nothing saying so, and `run.json`
writes a `thresholds` object with no stream in it. Meanwhile
`emit.detector_settings_rows` is keyed `(detector, stream)` and its docstring
gives the reason:

> *"a detector may run with different settings on the fast and slow streams, and
> a table that could not say so would make one of the two unreproducible."*

The export contract agrees with the docstring: `detector_settings.csv` is
`detector, stream, parameter, value`. The browser is the only part of this project
that cannot produce that file honestly.

**Choosing the stream at the door is what makes this go away**, rather than
threading a stream key through six call sites. Once the selection fixes the
stream, every downstream setting is per-stream by construction.

## What it costs

Small. `analysisStreams(data)` and `oneStream(data)` already exist. The selector
appears only when `oneStream` is false, so the common case gains nothing to look
at. The raster keeps drawing every stream it holds — this is about which stream
the *analysis* runs on, not which ones are visible.

**The settings file still records the stream** even though the interface stops
asking. A settings file that could not say which stream it was fitted on could not
be loaded back safely, which is the whole point of
[`2026-08-22-tuned-settings-are-a-file-not-a-survivor.md`](2026-08-22-tuned-settings-are-a-file-not-a-survivor.md).

## Watch out for

`detectLanes` filters detection rows by detector only, so today a single lane
merges calls from every stream. With one stream in play that stops mattering for
the analysis, but the lane code still needs to say which stream it is drawing, or
a two-stream folder viewed after a fast-stream analysis draws a lane that mixes
them.
