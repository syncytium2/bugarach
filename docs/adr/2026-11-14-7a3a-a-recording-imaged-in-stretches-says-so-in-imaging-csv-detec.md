# ADR 2026-11-14-7a3a: A recording imaged in stretches says so in imaging.csv; detection splices it and reports on the real clock

Status: Accepted, 2026-11-14

Tony accepted it with *"yes, write the ADR and fix the import"*, in answer to the proposal
summarised under Decision: a contract file for imaged stretches, real-clock event times, and
a shared splice helper. He had asked first whether fixing the DANDI import should come before
anything else, and then whether the data could be shown properly without it. They could not.

## Context

**The export contract assumed every recording was imaged without a break.** Times are
"seconds on the recording's own clock" ([`export_folder_spec.md`](../export_folder_spec.md)),
and nothing in the folder could say that the clock ran on while the microscope was off. Every
recording this lab makes is continuous, so the gap in the contract never mattered.

**The first outside corpus is not continuous.** Each DANDI:000219 session (Cossart lab, CA1
in mouse pups) is five movies of 2,500 frames, with 17–18 s gaps in the frame timestamps.
[`tools/import_dandi.py`](../../tools/import_dandi.py) had no way to say so, and did two
things in its place:

- It wrote times as `t0 + frame × dt`. The gaps vanished, and every event after the first
  movie landed 17 to about 70 s earlier than it happened.
- It found active runs over the whole raster. A cell active across a seam became one event
  spanning time that was never imaged.

[The seam todo](../todo/2026-11-14-dandi-000219-import-respect-movie-seams-and-the-real-clock.md)
records both defects.

**What that cost was shown on a figure the same day.** A one-page detection summary,
drawn on the real clock, showed dense activity on both sides of the gaps. Tony suspected the
analysis method, and he was right. The synthetic data behind the page had been built with the
same importer function. It painted single events across seams, and the windowed detectors
paired cells from different movies through their 2 s windows. When their calls were mapped to
the real clock, the drawn bars spanned gaps in which nothing was imaged. Without a record of
where the gaps are, bugarach cannot draw this corpus on its real clock at all.

**Detection must not run on the real clock either.** Every null in the package builds its
grid over the recording's extent. Given real times, it treats each gap as recording time in
which the data hold no events but its circular shifts place some. That dilutes the null and
lowers the threshold. CICADA itself runs on the spliced raster, the movies back to back.

## Decision

1. **A producer whose recording was not imaged continuously says so in `imaging.csv`.** It is
   optional and has one row per imaged stretch: `slice_id`, `stretch_idx` (1-based,
   chronological), `start_sec`, `end_sec`. A stretch runs from its first frame's time to its
   last frame's time plus one frame interval. A recording with no rows is one continuous
   stretch, so every existing folder means what it meant before. This is contract
   revision 11.
2. **Event times stay on the recording's real clock.** `time_sec` keeps the definition it
   always had. A producer does not splice its own times.
3. **An event lies inside one stretch.** The loader refuses an event that starts in a gap or
   whose width runs past the end of its stretch. A run that crosses a seam is two events, and
   the producer splits it.
4. **Detection splices, through one helper.** [`bugarach.imaging`](../../src/bugarach/imaging.py)
   puts the stretches back to back, moves event times, peaks and regions onto that clock, and
   maps every call back with `to_real` before it is reported, drawn or compared with an
   external clock. No detector learns about gaps.
5. **The caller states the pad at each seam, and there is no default.** A detector that looks
   at one frame at a time (locust, as CICADA does) takes a pad of 0, which is CICADA's own
   convention. A detector that counts coincidence in a window takes a pad at least as long
   as that window, so the window cannot join two movies. The empty time this adds dilutes
   the null slightly (four 3 s pads in a 20-minute recording are 1% of it). That is accepted,
   because the alternative is coincidence that was never observed.
6. **A drawn span is cut at the gaps** (`imaging.pieces`). A call is never drawn across time
   in which nothing was imaged.

## Consequences

- `tools/import_dandi.py` writes real timestamps, finds runs within each movie, and writes
  `imaging.csv`. The folder on disk is not regenerated in this change. It holds the four
  sessions reserved for a timed task outside this repository, and no session may compute on
  them before that task runs, so the re-import and the re-measure of
  [`assessment_cossart.json`](../learned/assessment_cossart.json) wait for that. The todo
  records this.
- `imaging.csv` becomes a reserved name. It is added in `io.RESERVED`, `dataset`'s list of
  non-recordings, `bugarach check` and the browser viewer. The lab-wide naming registry
  (armory `tools/naming/codes.json`, vendored here and not edited here) lists the fixed
  names a folder may hold, and needs `imaging.csv` added upstream.
- The route from a folder to calls ([ADR-0020](0020-one-route-from-a-folder-to-calls-per-stream.md))
  does not splice yet. Until it does, a gapped folder is analysed by calling `imaging.splice`
  explicitly, and the route's own wiring is the open item in the seam todo. No folder this
  lab produces has gaps, so nothing currently analysed changes.
- locust's raster painter still floors frame-aligned onsets one frame early, some of the
  time ([todo](../todo/2026-11-14-locust-repaint-floors-frame-aligned-onsets-one-early.md)).
  Splicing a frame-aligned corpus feeds it exactly such onsets, so that fix is a prerequisite
  for an exact CICADA comparison on this corpus.

## Amendments

**2026-11-14, a correction to decision 5 (no decision changed).** The pad stops a coincidence
window from reaching across a seam. It does not stop a run merge: CoactDetect joins called runs
closer than 8 s and the counts closer than 3 s, so with a 2 s pad a call at the end of one movie
still merged with a call at the start of the next. The task-1 runner found it on synthetic data
(3 of 26 count calls in a small field, and the one whole-session span in the large ones). Decision
6 already cuts a *drawn* span at the gaps. The same cut is needed for *counting*: after mapping a
call back, split it at the gaps and count each piece as a call, or set the pad to at least the
merge gap. `bugarach.imaging` says so in its module docstring.
