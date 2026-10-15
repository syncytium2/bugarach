---
status: waiting-on-tony
filed: 2026-10-14
---

# A defect review of the 66-recording export, with Tony's marks recorded as he makes them, is interface2's to build

waiting: Tony answers the five questions below; interface2 has the request (TASK_senktide_ttx_defect_review.md, 6c4b5558).

**Why this is filed here and built there.** Tony asked a bugarach session (2026-10-14) to set up a
viewer for checking the 66 recordings of the default export. It should show the artifacts already
detected automatically and let him mark three kinds of defect: a window on every ROI, a window on
some ROIs, and a point artifact. Then: *"this should probably be in interface2 as they are the
producer."* It is. Defects are judged on the fluorescence traces, which the export does not carry,
and which events go in an export is the producer's call (CLAUDE.md, "The export folder is the
input"). A bugarach session does not act in interface2
([ADR-0007](../adr/0007-bugarach-sessions-do-not-act-in-interface2.md)), so the request below
states what should exist afterwards, and Tony gives it to an interface2 session.

**What it unblocks.** The next bench revision waits on this
([the short-interval bench](2026-10-08-the-stack-ceiling-and-the-short-interval-bench.md)). Its
settings, including the real gaps between events, are measured on the default export, and that
export has been under the contamination stop since 2026-10-05
([the stop](2026-10-05-the-pinning-census-undercounts-on-the-default-folder.md)). The stop
clears when a corrected export becomes the default.

## What a bugarach session found, 2026-10-14

Read from the default export's file headers and from interface2 through `gh api`. No event data
were read; the stop holds.

1. **The export holds events only.** Each recording file has one row per onset (`roi, time_sec,
   stream, width_sec, width_def, peak_sec, amp, on_field_step, field_step_id`). There are no
   traces. A viewer built on the export could show rasters, but not the raw F against the frame
   minimum on which pinning was confirmed. The review has to happen where the traces are.
2. **Tony's calls currently reach the record second-hand.** interface2's
   `docs/moco_pinning_blanking.tsv` (branch `pinning-review`) holds his 2026-09-29 and
   2026-10-05 calls. They were made by eye in a viewer, spoken, and typed into the register by a
   session. The register shows what that costs:
   - **Time points with no extent.** The 2295 s square waves on `20250926_235` ROIs 14, 16, 23
     and 24 are four zero-width rows marked `needs_window`. They blank nothing.
   - **A session's reading recorded in place of Tony's.** ROI 22's window is the session's guess
     at what "throughout this period" meant, marked not confirmed.
   - **A call that is still only tentative.** ROI 1, "might have some contamination 39:30-40:30".
   Marks made in the viewer itself, saved with who made them and when, remove that relay.
3. **Direction changed on 2026-10-05 for the four pinned recordings.** In Tony's decision, as the
   register records it, `20260629_309`, `20260629_312`, `20260630_316` and `20250926_235` are
   redone from rigid motion correction, with ROIs picked again, and "time blanking and whole-ROI
   removal are both off the table" for them. The rigid outputs were accepted the same day.
   bugarach's stop todo still describes the earlier plan, a time-blanked cut of the same ROIs;
   that is corrected beside this filing.
4. **One verdict has not reached any export.** `20260630_325` is a field step at 200–232 s, so the
   events in that window are to be removed. The register says it is not yet applied anywhere.
5. **What is already detected automatically, and could be drawn as marks to accept or reject:**
   - the field-step events, in `field_steps_excluded.tsv` (318 events) and the `on_field_step`
     column;
   - the moco floor-pinned windows, in `moco_pinned_excluded.tsv` (83 events, grouped by
     `pin_window`);
   - the 2026-09-02 whole-frame scan's candidates;
   - the pin statistic `moco_verdict` reads.
   Both TSVs list the events they removed, not the window that was judged. A viewer needs the
   windows.

## The request (Tony gives this to an interface2 session)

> **Title:** Tony reviews every recording of bugarach's default export for defects, and his marks
> are recorded as he makes them
>
> **Context:** bugarach's default input is `2026-09-23_revised_2v_long_senktide_ttx_STEPS_AND_PINS_EXCLUDED`
> (66 recordings, listed in its `slices.csv`). It is under a contamination stop until a corrected
> export replaces it. The pinned-recording redo (rigid, ROIs re-picked) is part of that correction.
>
> **What should exist afterwards:**
> 1. A way for Tony to look at every one of the 66 recordings, every ROI, as traces, with the
>    artifacts already detected automatically shown as marks he can accept or reject: field steps,
>    moco floor-pinning, and the whole-frame scan's candidates.
> 2. Tony can add a mark of three kinds, each saved the moment he makes it with the recording, his
>    name and the date:
>    - **a window on every ROI**: start and end times; every event in it is removed;
>    - **a window on some ROIs**: start and end times plus the ROIs he selects;
>    - **a point artifact**: one time, on every ROI or on selected ROIs (its extent, see question
>      1).
>    A recording he has looked at and found clean is recorded as such, so "reviewed, nothing found"
>    is distinguishable from "not reviewed".
> 3. One file of all marks, readable without the viewer, with one row per mark: recording, kind,
>    ROIs, start and end times in seconds, whether it was automatic and accepted or Tony's own, who,
>    and when. Every automatic candidate he rejects is kept, as rejected.
> 4. When Tony signs off, a new dated export folder: the same 66 recordings with every event
>    inside an accepted mark removed, a manifest listing each removed event with the mark that
>    removed it, and `PROVENANCE.md` naming the marks file, the sign-off and its date. The four
>    pinned recordings come from their rigid redo.
>
> **What must not change:** every event outside an accepted mark stays. On a recording with no
> accepted marks that is not one of the four redone, the recording file is byte-identical to the
> current folder, as are the rows of `slices.csv` and `regions.csv`. The export's columns stay as
> they are.
>
> **Not asked:** a new detector, a threshold or a corpus-wide rescreen. bugarach adds no filter of
> its own; the marks reach it only through the export.

## Questions for Tony, before the interface2 session starts

1. **What does a point artifact remove?** A time with no extent removes nothing; the four
   `needs_window` rows show this already happens. Options: a fixed span around the point (say
   ±1 s, or ±1 frame), the events whose onset or width covers it, or a point is a prompt to drag
   out a window.
2. **All 66, or the four pinned plus every recording with an automatic candidate?** All 66 is
   what lets "reviewed, nothing found" be said of the whole set.
3. **Whole recording, or the analysis window only?** The export carries `analysis_start_sec` /
   `analysis_end_sec` (the 20-minute windows). Marks outside them change no analysis bugarach runs
   today.
4. **Which marks count against an export's correctness?** For example, `_235` ROIs 12 and 16 have
   "garbage 2655-end", which lies after every regime window. Should a mark outside the analysis
   window still be applied, or only recorded?

5. **The first-second blank against "byte-identical when unmarked".** Raised by the interface2
   session on receipt (2026-10-14). Tony's standing rule of 2026-10-12, that the first second of
   a recording is blanked, removes events on every recording, so the must-not-change clause cannot
   hold for all 66 as written. Should the clause read "identical except for the first-second
   blank, listed in the manifest like any other mark", or is that blank already applied in the
   current folder?

**Received.** The interface2 producer session filed the request as
`docs/handoffs/TASK_senktide_ttx_defect_review.md` on its `main` (`6c4b5558`), with the outcome,
the must-not-change clauses and all five questions. Nothing is built yet. It will name the folder
to Tony and to this repository when it lands.

## What bugarach does when the folder arrives

Add it to `current_export.toml` with its own note, point `default` at it, and remove the stop
note and its test in the same change (the stop todo, *What clears it*). Then rerun the real-gap
measurement the bench revision rests on.
