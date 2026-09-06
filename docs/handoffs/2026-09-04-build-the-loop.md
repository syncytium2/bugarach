# Handoff — build the loop, starting with the output nobody can read yet

**In flight: [#466](https://github.com/syncytium2/bugarach/pull/466)** — the field-step
figure, held because it is a figure with a caption and was never murderboarded, and red on
three legs. When it closes this file is spent and `tests/test_handoff_is_honest.py` says so.

> **Not murderboarded** — working material for sessions in this tree, same standing as
> `docs/run_records.md` and `docs/pipeline.md`. Nothing here is for an outside reader.

**No counts in this file.** Derive them: `git rev-parse --short origin/main` ·
`pytest -q` · `python3 tools/sapper.py --all` · `bash tools/board_digest.sh` ·
[`docs/MILESTONES.md`](docs/MILESTONES.md).

---

## Read this first

**[`docs/pipeline.md`](docs/pipeline.md) is the plan.** Tony walked the whole loop on
2026-09-04, one step at a time, correcting each row before taking the next. Every step is
named, says what it owns, what is built behind it, and what is owed. **Do not re-derive the
loop from `RESET.md` §2** — that section is the 2026-08-24 record, and two of its four marks
were annotating a tree that had since moved.

Two rules from that walk bind everything below:

- **The two modes walk the same pathway** — a Claude Code session driving the steps, and a
  user walking them unattended in the browser. Where they have drifted, that is a defect.
- **They converge on the webapp for MAHICE.** One judging surface. **No rendering-to-judge
  in a chat window** — if judging needs a better picture, the fix goes in the webapp.

The predecessor to this file is
[`docs/handoffs/2026-09-04-walk-the-loop-end-to-end.md`](docs/handoffs/2026-09-04-walk-the-loop-end-to-end.md).
Its field-step section and its traps are still worth reading; its plan is superseded by
`pipeline.md`.

---

## Start here: the summary page

Tony has asked for this twice and it is still not right. Nothing else on this page blocks it.

**What it is.** One page per group per treatment. Rows are recordings; `FAST` beside `SLOW`
as two columns, not stacked; every recording re-zeroed at the end of its own baseline so the
treatment onset is one vertical; treatment regions in a lane above each raster; per-region
event counts in the right margin. Row height constant regardless of ROI count.

**What exists.** `tools/make_group_raster_summary.py`, and the panels it added to
`ui.diagnostic` — `raster_panel(marked=…)`, `region_lane_panel`, and `ydim` on both. It
already aligns on baseline end, lanes the regions, and draws a producer-supplied second ink.

**What is wrong with it: the geometry.** It stacks `FAST` over `SLOW` at full page width, so
a page runs to nine thousand pixels and nothing can be read at once. **interface2 solved this
already** — `render_coord_summary_page.m` in `~/Developer/interface2`, extracted from
`plot_sce_summary.m` on 2026-07-08 precisely so a second caller would not redraw it, and
**detector-agnostic** by design. Port its `D`/`M` contract, not its code. Their
`docs/PLOTTING_ROSTER.md` lists it.

**Three things the current version drops that carry information:** two shading levels per
region (faint is the raw region span, solid is the counted window — the gap is what nobody
scored); region names as text in the panel rather than only a colour key; and the counts
table.

⚠ **The colour rule changed, and the MATLAB page will mislead you.** There, red means
*isolated* — an event belonging to no coordinated event — with colour otherwise encoding
event width. **Going forward: rasters are black, excluded events are red.** Same mark,
different claim.

⚠ **A vertically narrow detector lane is wanted, including the tube variants** — but no
detection row by default. The variants cannot run on real data yet (below), so build the
lane against the six and leave the seam.

---

## The two items upstream of most of the rest

**Nothing persists a trained model.** `torch.save` and `state_dict` appear nowhere in `src/`
or `tools/`. Every learned number in this repo comes from a model trained in the same
process, on simulated recordings. That blocks three steps at once: a variant cannot be tested
on a fresh batch, cannot detect on the user's folder, and a user cannot bring their own
model. It is the most upstream item in `pipeline.md`.

**The library's detect path has no settings argument.** `bugarach detect` reads its
parameters from `bench.OPERATING_POINTS` and cannot be handed a tuned operating point. The
browser can apply one to the user's folder; the command line cannot. **This is where the two
modes stop being one pathway**, at the last step before output.

---

## The data, and one thing owed to interface2

**The analysis folder is `2026-09-03_revised_2v_long_STEPS_EXCLUDED`** — field-step artifacts
removed, 381 events, listed in its own manifest. The producer's standing rule as of
2026-09-03 is that exporters ship clean data.

**`2026-09-03_revised_2v_long_STEPS_FLAGGED_FOR_REVIEW` is the review copy** — the same
recordings with the artifacts still present and marked, for looking at them and nothing else.
`tools/make_group_raster_summary.py` reads it and **refuses a folder without the manifest**,
because a page with no red is indistinguishable from recordings that never had an artifact.

⚠ **`current_export.toml` still declares the August folder**, which carries no `analysis_*`
columns — so anything reading `dataset.current()` scores whole raw periods where the new
folder scores `long_window_20`. Same events, different windows, different numbers.
Redeclaring is Tony's call, and that file says to change the name there and nowhere else.

**Owed to interface2, cheap, and nobody has done it:** `detectors/sync.py` carries a port of
`flagArtifactEvents` whose criterion is narrow near-total synchrony, which reads close to
what a field step looks like. Nobody has checked whether it was already catching these. Run
the six over the excluded and the flagged folders and diff — that answers their question and
measures what the removal changed, in one pass.

---

## Traps that cost time in the thread that produced this

- **The repo already has names for things; use them.** A draft of `pipeline.md` invented step
  names for steps that had them — the webapp's own rail carries the list — and separately
  shipped "corpus" five times, which `GLOSSARY.md` retired on 2026-08-22. Read
  `docs/GLOSSARY.md` and `docs/writing_conventions.md` before writing prose.
- **Do not guess a repo from its directory name.** A session hunting the universal amplitude
  estimator went to `~/Developer/no_peak` on the strength of the word "peak". It is a
  hormone-pulsatility CLUSTER port. The estimator was in `assess.py` the whole time.
- **The universal amplitude is peak coactivity in #ROIs**; the universal width is the
  participant onset span in seconds. Both are detector-free, which is why they are the axes
  detector rows can be compared on — each detector's own `strength` is in its own unit, and
  two of the six report a count of cells.
- **The assessor knows cluster membership; the six detectors do not.** `assess` carries which
  ROIs made up each observed cluster. Five detectors report only how many took part, and
  three build the participating set internally and hand back its size. Those are different
  facts, and the difference is where v2 event tagging starts.
- **`tests/test_syntax_floor.py` runs in under a second — run it before pushing anything with
  an f-string in it.** This machine is 3.14 and the project promises 3.11; CI's oldest leg
  was the only thing testing the floor, and it caught two defects in one afternoon, one of
  them a tool that had been unrunnable on 3.11 since it landed.
- **`tools/show.py` infers the project from the worktree directory name.** Pass
  `--project bugarach`, or your figure lands in a darkroom folder named after your branch.
  Reported to armory.
- **A worktree imports the primary checkout's `src`.** `PYTHONPATH=$PWD/src` on every run.
- **`merge_when_green.sh` reaps the worktree when the PR merges.** Do not claim and build in
  the worktree you are about to land.

---

## Still waiting on Tony

Unchanged, all in [`docs/MILESTONES.md`](docs/MILESTONES.md): the `rate` promiscuity ceiling,
run-record naming, and what happens to `bench-background-is-not-flat` — the only genuinely
unlanded branch in the tree.

**And the one that gates the science rather than the code: nobody has run MAHICE on the
approved folder, so no K is set for it.** Expert attention, not compute — a couple of hundred
confirmations at a low proposal floor, an afternoon. ⚠ **Do not set it for him.** A K a
session picked would pass every test in this repo and be exactly the thing the record was
built to prevent.
