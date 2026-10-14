---
status: in-progress
filed: 2026-10-14
---

> **Built 2026-10-14, on simulated recordings only:**
> [`learned/coordination_share_explainer/`](../learned/coordination_share_explainer/README.md).
> Two things changed from the plan below. **No real number is quoted**: the default export has
> been under the contamination stop since 2026-10-05, and pinning is a cross-cell artifact this
> measure counts, so item 4's baseline figures and item 5's `shape_usable` count wait for the
> corrected export. **The recordings have their own gap schedule** (Tony, 2026-10-14): close pairs
> 2 s apart, medium pairs 10 to 20 s apart, and single moments 120 s apart, for this page only.
> The bench is unchanged. **Item 5's first bullet was backwards**: a slow shared change survives
> into the shifted copies and is subtracted (99% of a threefold rise over 45 minutes). What is
> counted is a change *faster* than the copies' slides, which includes the sharp edges of a long
> busy stretch: it is how fast the rate changes, not how long the change lasts. The tool's
> docstring says "slower than about a minute survives", which is right in direction and too sharp
> as a boundary; Figure 5 of the page shows the curve. What is left: the real numbers when the
> stop clears, a redraw when the revised bench is decided, and three notes for whoever next edits
> the tool, none changed here: its docstring's "120 s spacing floor" predates the realistic
> bench (2026-10-07); `population_cumulants` says two offsets "halve" the moments split by a
> window edge, but they steady the loss without recovering it; and Staude, Grün and Rotter (2010,
> *Front Comput Neurosci* 4:16) extend the cumulant method to changing rates, the weakness Figure
> 5 shows.

# An explainer for `tools/measure_coordination_rates.py`: what fraction of calcium events are coordinated, measured without defining an event

**This is a handoff to a new session** (Tony, 2026-10-14: *"prepare a handoff to a new session
to build an explainer for tools/measure_coordination_rates.py"*). It is filed as a todo rather
than a root `HANDOFF-*.md` because nothing is half-done. A root handoff on `main` means work in
flight, and this is a task ready to start.

## Why now

Coordinated events persist under TTX and under APV+CNQX(+GZ). Tony asked for a measure of how
much of the activity is coordinated: the fraction of calcium events that are coordinated,
against the overall event rate. That measure already exists in this tool, as
`coordinated_share_of_rate`, and so far it has been run on baseline windows only.
[ADR-0017](../adr/0017-group-and-treatment-comparisons-default-to-fireflies.md) makes running
it under treatment bugarach's job, as the first confirmed exception to "group and treatment
comparisons are fireflies'". The results will be read through this measure, so a reader needs
to know what it is before seeing them. (ADR-0017 is PR #886 at the time of writing. If it is not
on `main` when you start, read it on that PR.)

## What to build

A figure-led explainer of the measurement itself, **not** of any treatment result. It is the
sister of [`learned/correlogram_explainer/`](../learned/correlogram_explainer/README.md), which
explains `tools/measure_jitter_correlogram.py` to readers who are not math-oriented. Copy its
shape: a script that draws the figures from synthetic recordings, a README, and a darkroom copy.
It answers the same objection for a different quantity: *how can you count coordinated events
if you have not defined what one is?*

What the reader should come away with, all of it in the tool's own docstring:

1. **The statistic.** Slide a window of *w* seconds along the recording and count the cells with
   an onset in it. Cells that are independent and cells that share moments produce the same mean
   count. Shared moments show up in the **spread** of the count: the second and third factorial
   cumulants (*f*₂, *f*₃) are zero for independent cells and grow with sharing.
2. **Chance is subtracted, not assumed.** Each cell's train is shifted rigidly, by offsets at
   least two windows apart (`shifted`). This keeps every cell's own timing and rate and destroys
   the alignment between cells. The surrogate's cumulants are subtracted from the real ones.
3. **From two numbers to three answers.** With shared moments at rate λ and each of *N* cells
   joining one with probability *p*, the excess cumulants give the number of cells per moment
   (*k*) and λ. The coordinated rate per cell is λ·*k*/*N*, and that divided by the cell's event
   rate is **the fraction of events that are coordinated**. `solve` does this.
4. **The two models disagree, and the reader should see by how much.** "Fixed" assumes the same
   number of cells joins every moment; "binomial" lets it vary. On the 66-recording baseline at
   1 s, fast reads 3.8% fixed against 5.4% binomial, and slow 1.6% against 3.2%. Re-derive these
   from `docs/learned/runs/2026-09-23-coordination-rates-senktide-ttx/coordination_rates.json`
   rather than copying them from here. The bench adopts the fixed model (`ADOPTED_MODEL`);
   say why, from the tool's own note beside it.
5. **What it cannot see, which matters most under treatment:**
   - Shared changes slower than the offsets' span, about a minute at a 1 s window, survive into
     the surrogate and are counted as coordination. Senktide's rising background is one.
   - A stretch where the whole field is busier reads as coordination (the elevated-rate probe;
     the numbers are in the tool's `CAL_NO_PROBE` note).
   - At low event rates *f*₃ is noisy, and `shape_usable` drops recordings. Under TTX the rate
     falls, so say how many recordings a run loses and why.
6. **How we know it works.** The same estimator runs on simulated recordings where every
   planted event's cells are known, and passes when the share is recovered within `CAL_TOL`.
   Show that check as a figure: planted share against recovered share.

Window size (1, 2 and 4 s) moves the answer. Show it, or say plainly why it does not need
showing.

## Rules that bind this page, and where people tripped before

- **Document deliverable: run `/murderboard`** before handing it over (CLAUDE.md). The
  correlogram explainer skipped it on Tony's say-so (*"no time"*). Do not inherit that: ask Tony
  whether this one is reviewed, and default to reviewing it.
- **Figure page layout**: figures first, then controls, then text
  ([ADR-0014](../adr/0014-a-figure-page-is-figures-then-controls-then-text.md)). Number every
  figure, refer to it by number **and** name, and put the legend on its heading line.
- **Define every symbol before a figure uses it**: *w*, *N*, *k*, λ, *f*₂, *f*₃. Write "ROI
  (region of interest)" at first use.
- **"Fire" is banned for calcium events** (SAP017). The correlogram explainer's title says
  "firing" because it predates the rule, so do not copy its title. Use *event*, *onset*,
  *active*.
- "Data" is plural. Every number carries its unit (cells, onsets per second, recordings).
  Groups are ordered DI, OVX, MALE, ORX through `bugarach.groups`. Times use the minutes-friendly
  axis. Nothing is drawn on a raster: cues go in a lane above it, marks point down.
- **Real recordings stay out of the public repo** (FOUNDATIONS §5). Synthetic figures can go in
  `docs/learned/`; anything drawn from real recordings goes to the darkroom only.
- **Output**: the darkroom by default (`bugarach.paths.darkroom()`), with `--also` for the repo
  copy (SAP006). File names come from `tools/naming/artifact_name.py build`.
- **Name the dataset** for every real-data number on the page. Pull it from the run record's
  `dataset` stamp.

## Before you start

1. Read FOUNDATIONS §9 and, if ADR-0017 has merged, §11.
2. Claim on the local board **first**, with a `Touches:` line, and on `docs/SESSIONS.md` for
   the darkroom folder.
3. Read the tool's module docstring end to end. It is long, and nearly every point above comes
   from it.
4. Look at `tools/make_coordination_rates_figure.py`. It already draws the run's figure, so
   reuse its pieces before writing new ones.
5. Open the correlogram explainer's `explain_correlogram.py` for how its synthetic recordings
   and figure code are built.

## Out of scope

- **Running the measure on treatment windows.** That is a separate PR. It needs the tool
  extended past baseline: `_real` measures only the baseline window today. That PR reports
  results per stream and per group, each treatment window against its own baseline, under
  ADR-0017.
- Changing the bench, the adopted model, or any constant.
