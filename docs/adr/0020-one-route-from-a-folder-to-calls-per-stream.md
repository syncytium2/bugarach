# ADR-0020: One route from a folder to calls, per stream; readiness for the revised senktide/TTX export comes first

## Status

Accepted, 2026-11-11, by Tony, in three instructions given the same afternoon:

- the goal: *"our goal as we wait for the revised senk-ttx data set is to be ready with an
  established pipeline: characterize raw coordination, build synthetic ground truth data sets
  that represent the primary qualities of our data streams (fast, slow, combined). train and
  optimize our suite of detectors. evaluate performance. iterate if needed. then process the
  original data."*
- the order: *"integrate the the paths first. review the dissertation chapter to ensure we are
  not reinventing anything. unify all work and focus on readiness for the senk-ttx data set"*
- the record: *"and perfect ADR hygiene"*

It does not supersede an earlier ADR. It replaces the 2026-09-17 three-goal program in
[`goals/README.md`](../goals/README.md) as the frame work is ranked against; that program's
decisions about the data and the simulation (baseline only, the fitted field, every knob) are
unchanged.

## Context

**Two bodies of work described the same loop and shared no code path.**

- **The three benches** (September). `bench.py`, `bench_slow.py` and `bench_combined.py` each hold
  one stream's measured constants. The measuring tools write a record, a person transcribes it
  into the module, and the search, budget and detect tools read the module. Every detector was
  searched on all three on 2026-09-25 and nothing was adopted.
- **Synthetic validation** (October; [goal page](../goals/synthetic-validation.md)). Scripts under
  `docs/learned/synthetic_validation/` plant known parameters and ask what the measuring tools
  recover. They called the simulator directly with values typed into each script, so "the lab's
  regime" there was a number copied from a page (33 cells where the benches hold 32).

Neither read the other. A re-measured bench moved no synthetic-validation grid, and a recovery
result changed nothing a search ran on. The third description of the loop,
[`pipeline.md`](../pipeline.md) (Tony, 2026-09-04), is the product's and names the steps; no page
listed the commands that walk it for one stream.

**The data are not here yet.** The default folder has been stopped since 2026-10-05 for a known
contamination, and it clears when the producer's corrected export becomes the default
([todo](../todo/2026-10-05-the-pinning-census-undercounts-on-the-default-folder.md)). Until then
nothing may be re-measured, so what can be made ready is the route.

## Decision

1. **There is one route, walked once per stream** (fast, slow, combined): characterize the
   baseline, simulate from what was measured, check that the measuring tools recover what was
   planted, tune the detectors, evaluate them, and detect on the original folder. It is
   [`pipelines/stream-readiness.md`](../pipelines/stream-readiness.md). The benches and the
   synthetic-validation aims are stages of that route, not programmes of their own.
2. **Integration comes before new results.** Joining the existing pieces is done before any
   stage is extended.
3. **Readiness for the revised senktide/TTX export is what work is ranked against.** A thread
   that does not shorten the distance between that folder arriving and calls on it waits.
4. **Rulings the route leans on are ADRs, written in the same change that first reads them.**
   That is the standing convention ([README](README.md)); this restates it as a condition of
   the route, and the audit that came with it is in
   [the backfill todo](../todo/2026-09-23-adr-backfill-candidates.md).

## What this does not decide

Each of these changes what the route produces, and each is still Tony's:

- what the revised bench is: short gaps added, or events defined in a narrower window
  ([todo](../todo/2026-10-08-the-stack-ceiling-and-the-short-interval-bench.md));
- whether any of the 2026-09-25 search picks is adopted;
- ADR-0012 and ADR-0013, both Proposed on open pull requests (#848, #855);
- whether two sources are built before or after the one-source route has been rehearsed.

## Consequences

*How the first change implements the decision. This part is a session's, and it may change
without a new ADR as long as the four points above hold.*

- **A stream's values have one owner.** `bugarach.stream_profile` reads a bench module and
  holds no number of its own (`tests/test_stream_profile.py`). The synthetic-validation grid at
  the lab's values (`aim1_lab_regime.py`) takes its cells, participants, jitter and backgrounds
  from it. The three modules stay the owners for now: this is the first step of
  [the one-bench rebuild](../todo/2026-09-21-one-stream-aware-bench.md), which inverts that.
- **The route page lists what is owed**, in the order the route needs it, and each item links
  the todo that holds it. When the export arrives, stage 1 is the only stage that reads it.
- **The transcription step is the route's weakest joint.** A measured record still reaches the
  bench by a person editing constants. A profile built from the record is owed.
- **Nothing here reads data.** The stop on the default folder is unchanged.
