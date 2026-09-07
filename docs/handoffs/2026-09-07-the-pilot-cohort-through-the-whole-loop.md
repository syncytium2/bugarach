# The APV+CNQX+gabazine pilot through the whole loop — what was run, what it took, what it hit

> **Written straight into this directory on 2026-09-07 — nothing in it is half-done.**
> It was never a root signal: the run is complete and its artifacts are in the darkroom.
> This is the record another session picks up from, and the pointer the resume team's
> report is reached by.
>
> **Not murderboarded here — the report it points at is, before delivery, and its run
> record sits beside it in the darkroom.** This file carries no number
> derived from the recordings (FOUNDATIONS §5: real-data-derived output goes to the
> darkroom and never to the repo). The numbers, the figures and the run record are in
> `<darkroom>/bugarach/2026-09-07-pilot-apv-cnqx-gz/REPORT.md`; resolve `<darkroom>` with
> `bugarach.paths.darkroom()`.

Tony, 2026-09-07: *"Run the apv cnqx gz baseline data set through the coordination
pipeline including tube variant training. Assume assessor setting of 10% floor 3 for
ground truth. Document each step for evaluation by the resume team. Output is labeled
rasters and a new fireflies plot before after. Single group fast and slow columns."* Then
*"Proceed autonomously"* and *"Proceed without human confirmation in mahice."*

## The loop, as it ran

Every step of [`pipeline.md`](../pipeline.md) was walked in orchestrator mode, in order:
open a folder → assess (machine half of MAHICE) → derive the spec → simulate, calibrate the
six and train the tube variants → detect on the real folder → output. The summary rasters
(`tools/make_group_raster_summary.py`) and a new before/after figure
(`tools/make_before_after_figure.py`) are the output; a `for_fireflies/` note tells that
team which two files to draw from.

## Three deviations, each on instruction or by necessity, each stamped on its artifact

1. **MAHICE was not run.** The assessor's clusters at the instructed K stand in for
   confirmed events. `derive_spec.py` refused until told `--unreviewed` and wrote why into
   the spec. `RESET.md` §1's rule — a coordination number nobody looked at *is not a
   result* — applies to everything downstream, and the report says so first.
2. **The input folder is consumer-built.** interface2 had exported this cohort for
   fireflies only; its exporter needs the cohort registered in `if2_archive_variant.m`,
   and neither that edit nor a MATLAB launch was permitted from the session. The folder
   was written from the producer's archived onset store through `bugarach.store` with the
   hook's own `BUGARACH_STORE_OK=1` escape, mirroring the exporter's documented
   conventions and applying no producer decision it could not see. Its README lists them.
   **A producer export supersedes it** — that is the first thing to ask interface2 for.
3. **"10 % floor 3" was applied as an absolute K**, because `assess.k_from_fraction` has
   no floor parameter (the live handoff already records that gap). On this cohort's field
   sizes the two are the same K on every recording, and the report shows the arithmetic.

## What the run hit that the pipeline document already owes

- **Tuned settings do not reach `bugarach detect`** from the command line, so detection on
  the real folder ran at the shipped operating points.
- **Trained tube variants cannot run on real data** — nothing persists a model — so the
  learned branch ends at the bake-off table.
- **Two background quantities the pipeline says should be fitted from the user's own
  baseline were inherited** (per-ROI rate heterogeneity, burstiness): six baselines are
  too few to fit them, and the spec says which. The four generator quantities proper —
  rate, cluster, participation, jitter — were derived from the cohort.
- **The bench validated a different instrument from the one that produced the real-data
  calls.** The calibrated knobs sit far from the shipped operating points on five of six
  detectors, two searches ended on the edge of their grids, every shipped point is
  fast-derived and no slow bench was run. The report says so; nothing here fixes it.
- **The folder was never scanned for field steps** (producer: UNCHECKED). The summary tool
  gained `--unscanned` so it can draw such a folder and say so in red, rather than refuse
  or draw a silent clean-looking page.

## In the repository from this run

`tools/make_group_raster_summary.py --unscanned` with its test; `tools/make_before_after_figure.py`
with its test; this record; the darkroom claim on `docs/SESSIONS.md`. No data, no numbers.
