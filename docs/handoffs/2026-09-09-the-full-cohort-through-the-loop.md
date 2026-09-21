# The full senktide and TTX cohorts through the loop — the pointer

> **Written straight into this directory on 2026-09-09 — nothing in it is half-done.** The
> run is complete and its artifacts are in the darkroom. It was never a root signal.
>
> **This file carries no number derived from the recordings** (FOUNDATIONS §5: anything
> derived from real data stays machine-local). Every measured result, every figure and the
> full run record are in `<darkroom>/bugarach/2026-09-09-full-cohort-senktide-ttx/`;
> resolve `<darkroom>` with `bugarach.paths.darkroom()`, or `python -m bugarach.paths`.
>
> **Not murderboarded**, and neither is the run record it points at — both are working
> material for sessions in this tree, the same standing as `docs/pipeline.md`. The one
> artifact addressed to another team, `for_fireflies/README.md`, is **marked as a draft and
> must not be sent** until it has been through `/murderboard` and Tony has released it.

Successor to [the APV+CNQX+GZ pilot](2026-09-07-the-pilot-cohort-through-the-loop.md),
whose MAHICE and slow-bench caveats are **not** superseded by this run.

## What is different from the pilot, and it is most of what mattered

Both of `pipeline.md`'s blockers closed on 2026-09-08 (#507, #508, #509), and this is the
first run to spend them:

| the pilot could not | this run did |
|---|---|
| apply tuned settings from the command line — the six ran at shipped operating points | detected at a calibration derived from this cohort's own simulated data |
| run a trained model on real data — nothing persisted a model | ran all six learned models from checkpoints, in a separate process from training |
| fit background heterogeneity — six baselines were too few | fitted it from the folder; **burstiness is now the last inherited generator quantity** |
| scan for field-step artifacts — the folder was UNCHECKED | read the producer's artifact-excluded export |

## What the run found before it started

**The producer's newest export had been on disk for six days and no file in this repo named
it.** Its own README says *"for any new analysis, use this folder."* Landed as **#511**,
which declares it as three roles beside `default` rather than instead of it — moving
`default` re-points every existing analysis and every parity fixture, and that is a
decision, not a housekeeping edit.

That PR also carries the three things this run needed and did not have: a **floor under a
percentage K**, a `derive_spec` path that **aggregates across recordings at each one's own
resolved K** instead of selecting one column of the scan, and **group facets** on the
before/after figure. Two silent defects turned up in existing code on the way — a
hardcoded clip width that dropped the rightmost facet of any wide page, and a
positional-tuple read across a module boundary.

## Still open, in the order I would take it

1. **MAHICE has still never been run on an approved folder.** Skipped here on instruction,
   as in the pilot. Everything downstream inherits `RESET.md` §1 — a coordination number
   nobody looked at is not a result. Expert attention, not compute.
2. **An edge-of-grid threshold refuses on the coded branch and only warns on the learned
   one**, and it decided what the best learned model shipped at here.
   [The todo](../todo/2026-09-09-an-edge-of-grid-threshold-refuses-on-one-branch-and-warns-on-the-other.md)
   names the one measurement that settles it.
3. **Six folds cannot support a corrected pairwise winner** — that is arithmetic, not a
   property of the detectors, and the threshold is eight. Relevant to
   [`performance_table.md`](../performance_table.md) §1, whose replacement argument is still
   unwritten.
4. **Burstiness is still inherited.** `pipeline.md` says fit it from the user's own
   baseline; rate heterogeneity now is, and this one is not.
5. **No slow bench.** Every operating point is fast-derived and applied to a stream whose
   measured coactivity is several times higher. Unchanged from the pilot.

## Traps this run hit

- **zsh does not word-split an unquoted parameter.** Building `--model a --model b` into a
  shell variable and passing it unquoted sends **one** argument; argparse reports every
  flag as unrecognised and the leading empty string is the tell. Write the flags out.
- **A recording missing from a detections file is drawn at zero**, where it cannot be told
  from a detector that ran and found nothing. The before/after figure now counts and names
  them on the page; it caught a `--limit` smoke run immediately.
- **A wide page loses its right-hand column silently.** Fixed in the shared renderer, but
  the lesson generalises: the clip was a pixel constant copied from the viewport it was
  meant to track.
