# ADR-0024: the September bench is stale and is not re-measured; the old data are replaced

## Status

Accepted, 2026-11-13, by Tony: *"sept bench is stale. retracking is in progress. the old data
will be replaced and never touched again"*.

## Context

**The September benches were measured on one folder.** The three benches (`bench.py`,
`bench_slow.py`, `bench_combined.py`) take their backgrounds, rates, widths, jitter and
participation from records measured on the producer's export of 2026-09-23, which
`current_export.toml` names `senktide_ttx`. That folder was the default from 2026-09-23 to
2026-11-12.

**Four tests tied the benches to the default.** They compared each bench record with whatever
folder the default points at, and failed with an instruction to re-measure when the two
differed. That was the answer to a question of 2026-09-17, when the fast bench's background
turned out to have been fitted on a closed archive and nothing had noticed.

**The default moved on 2026-11-12** to the tracked DI and MALE cohorts (`tracked_cohorts`). The
four tests went red on every branch that carried the new default, and each asked for the
September benches to be re-measured on it.

**Two things made re-measuring the wrong answer.** The `senktide_ttx` folder has been stopped
since 2026-10-05 for a known contamination (its note in `current_export.toml`), so the benches
already rested on a folder no analysis may read. And a session had already measured new bench
sets on the new default, one per stream and per set of recordings (PR #929, not merged and not
adopted), without touching the September benches.

**Tony was asked on 2026-11-13** what to do about the red guards, and answered with the ruling
above.

## Decision

1. **The September bench is stale.** Its measured values describe the `senktide_ttx` folder as
   it was in September. They are not current values for any dataset.
2. **It is not re-measured.** No session runs `tools/remeasure_bench.py` or
   `tools/measure_slow_bench.py` to bring the September benches onto the tracked cohorts or
   onto any later default.
3. **The old data are replaced, and then never read again.** Retracking is in progress at the
   producer. When its export arrives it replaces the old data, and no analysis goes back to
   them.

## Consequences

- **The guards name the folder, not the default.** The four tests now compare each September
  record with the `senktide_ttx` table by name (PR #928). They still fail if a bench constant
  is edited without a measurement, or if a background grid stops covering a group's quartiles
  in the record. They no longer ask for a re-measurement when the default moves.
- **The contamination stop stays where the contamination is.** The test of the stop reads
  `senktide_ttx`, whose note is still in the pointer file. The stop clears as that note says,
  not by this record.
- **A score on the September bench is a score on a stale bench.** This session's reading, not
  Tony's words: results already recorded on it stand as records of what was run, and are not
  quoted as current. That covers the settings searches of September and October, the fair
  comparison of 2026-09, and the false-call limits and grids the bench sets of 2026-11-12
  inherited.
- **What replaces the September bench is not decided here.** The bench sets in PR #929 are the
  candidate, and how sets are built and scored is the subject of the Chapter 2 design. Its
  handoff, `docs/handoffs/2026-11-13-chapter-2-synthetic-sets-and-detector-scoring.md`, is in
  the same pull request and is not on `main` yet.
- **The route page is now out of step, and that is open.** Stage 2 of
  [`pipelines/stream-readiness.md`](../pipelines/stream-readiness.md) (ADR-0020) re-measures
  the three benches on a folder with the two tools named in decision 2. This record stops that
  for the September benches. Whether the stage is rewritten around bench sets, or the tools are
  kept to measure a new bench on the retracked export, waits on Tony.
- **`MEASURED_ROLE` still says `default`** in the three bench modules, so the re-measure tools
  would read the tracked cohorts if someone ran them. The code is unchanged by this record;
  decision 2 is what stops the run. Changing or retiring the constant belongs with the
  previous point.
- **"The old data" is read here as every export folder made before the retracking**, the
  `senktide_ttx` folder first among them. This is this session's reading. Which tables leave
  `current_export.toml`, and whether the tracked cohorts of 2026-11-12 are themselves replaced
  by the retracked export, are the producer's and Tony's to state when it arrives.
- **Until the retracked export arrives**, this session's reading is that no new analysis
  starts on the old folders. Tony's words set no date, and he has not ruled on the interim.
