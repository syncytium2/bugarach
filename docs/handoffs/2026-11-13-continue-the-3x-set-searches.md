# Handoff: finish the 3x bench-set searches and report them beside the 4x ones

**Use this page when** you are the session taking over the 3x run of the route (characterize,
build bench sets, search detector settings, cross-score), or you want to know what state that
run was left in on 2026-11-13.

> Working material, not murderboarded. Written 2026-11-13 at 2:45 PM EST by the session that
> started the run, **while the run was still going**. Check every statement about progress
> against the queue log before relying on it. **A linked file wins** where this page disagrees.

## The task, in Tony's words

2026-11-13: *"build, opt, and test on 3x."* The same route had just been run on the default
dataset (`tracked_cohorts`, events detected at 4 × sigma_est). This repeats it on
`tracked_cohorts_3x` (the same recordings at 3 × sigma_est), so the two can be read side by
side. The larger aim, also his: characterize the data from their timing without a hypothesis
about coordination, build synthetic sets from those measurements, tune detectors on the sets,
evaluate, iterate, then process the original data.

## State when this was written

The run is one shell script, `chain.sh`, in the run folder `2026-11-13-set-searches-3x` under
the workstation's `bugarach-runs` folder (beside the 4x run's `2026-11-12-set-searches`). Each
step writes a start line and an exit line to `queue.log` there.

| Step | State at 2:45 PM EST | Duration |
|---|---|---|
| Characterize: jitter, rates, intervals | done, exit 0 | 9 min |
| Build nine bench sets (`*_3x`) | done, exit 0 | 6 min |
| Search `slow_all_3x` | done, exit 0 | 109 min |
| Search `combined_all_3x` | done, exit 0 | 32 min |
| Search `combined_male_3x` | done, exit 0 | 24 min |
| Search `slow_di_3x` | done, exit 0 | 77 min |
| Search `combined_di_3x` | done, exit 0 | 112 min |
| Search `slow_male_3x` | running since 1:54 PM | |
| Search `fast_all_3x`, `fast_di_3x`, `fast_male_3x` | queued, in that order | |
| Cross-score (`--seeds 12`) | queued | |

At 4x the three fast searches took 114 to 178 minutes each, and 3x searches have run slower
than their 4x twins, so expect the chain to end late evening or after midnight.

**The chain is a background task of the session that started it. If that session has ended,
the chain may have died with it.** First thing: read `queue.log`. If the last line is not
`chain done` and no Python processes are running, restart from the first set whose folder has no
finished `search.json`:

    cd <scratch-3x worktree>
    export PYTHONPATH=src PYTHONUTF8=1 PYTHONIOENCODING=utf-8
    <venv python> tools/search_all_settings.py --bench <set> --sliding --workers 11 --out <run folder>/<set>
    ...
    <venv python> tools/cross_score_sets.py --searches <run folder> --out <run folder>/cross_score --jobs 11 --seeds 12

A restarted search keeps the set's chance floors and starts the search itself over. Copy the
exact lines from `chain.sh`. Run long steps in the background and tell Tony they started.

## Why there is a scratch worktree, and what lives only there

Analyses read the default dataset, and one line of `current_export.toml` sets it. The 3x run
needed 3x as the default without changing the committed pointer, so it runs from a second
worktree, `scratch-3x`, detached at commit `c5040259` of this branch, with an **uncommitted**
edit: `default = "tracked_cohorts_3x"` and that table's `use = "input"`. The committed file is
unchanged: 4x is the default and the 3x folder is `eval`.

These exist **only in the scratch worktree** and are lost if it is removed first:

- stage 1 records: `docs/learned/runs/2026-11-13-stage1-tracked-cohorts-3x/`
- the nine bench records: `docs/learned/bench_sets/*_3x.json`

The searches, logs and cross-score are in the run folder, outside any worktree.

## What is owed when the chain ends

1. **Verdict.** `tools/greatlakes/verdict_search_sets.py --out <run folder> --sets <the nine>`
   opens every `search.json`. An exit code of 0 says nothing about the output.
2. **Report to Tony**: the 3x cross-score table beside the 4x one
   ([`docs/learned/runs/2026-11-12-set-searches/`](../learned/runs/2026-11-12-set-searches/README.md)),
   naming the dataset each was run on. Lead with what differs.
3. **Commit the 3x records to this branch (PR #929)**: copy the stage 1 folder and the nine
   bench records into this worktree, and the searches, verdict and cross-score into
   `docs/learned/runs/2026-11-13-set-searches-3x/` with a README modelled on the 4x one. Each
   bench record's dataset stamp says `use: input`, which is the scratch edit speaking; the
   committed table says `eval`. Correct the field and say so in the README. Add INDEX rows.
4. **Then remove the scratch worktree**, after checking the copies landed.
5. **Check `tools/cross_score_sets.py` did what it should**: in the scratch checkout the 4x sets
   also have records, with no searches in the 3x run folder, so it should print them as left out.

## What the 4x run found, for comparison

Dataset `tracked_cohorts`. All nine searches passed the verdict. Scored on 12 fresh simulated
recordings per background (24 on fast):

- **Slow stream:** settings tuned on all recordings, on DI and on MALE score within 0.008 mean
  F1 of each other on every set.
- **Combined stream:** within 0.006, except SPIKE-synch and binned SCE, where the pooled setting
  loses about 0.04 on the DI set.
- **Fast stream:** they disagree. Rate-plus-context tuned on all scores 0.706 on the DI set
  against 0.980 for the DI-tuned setting, and the DI-tuned setting scores 0.801 on the MALE set.
- **Nothing planted:** tuned settings make near zero false calls per hour, except binned SCE (up
  to 8 per hour on combined) and locust (about 1 per hour).

The 3x bench sets, as measured (events per hour; busy background):

| Set | Events per hour | Busy background (Hz) |
|---|---|---|
| `fast_all_3x` | 32.0 | 0.0290 |
| `fast_di_3x` | 38.4 | 0.0787 |
| `fast_male_3x` | 27.4 | 0.0203 |
| `slow_all_3x` | 66.5 | 0.0189 |
| `slow_di_3x` | 78.6 | 0.0311 |
| `slow_male_3x` | 57.9 | 0.0142 |
| `combined_all_3x` | 70.5 | 0.0487 |
| `combined_di_3x` | 88.8 | 0.1141 |
| `combined_male_3x` | 57.4 | 0.0319 |

## Limits to carry into any report

- The benches are simulated. A score says how a setting does on recordings built from the
  measured values, not on the recordings themselves.
- **No decoys, by ruling** ([ADR-0019](../adr/0019-the-decoys-are-retired-negatives-are-rate-matched.md)):
  decoys were retired on 2026-10-23 in favour of rate-matched negatives. The tool that builds
  those negatives does not exist yet, so precision here is against background only. Do not
  describe the absence of decoys as a gap.
- Every detector's search ended against the edge of its grid on at least one setting.
- Close-pair cells hold 8 to 29 pairs each at 4x; too few to rank on.
- F1 on one bench is a tuning target, not a comparison of detectors.
  [ADR-0021](../adr/0021-the-toolset-is-validated-on-synthetic-data-first-with-coded-detectors.md) asks for a capability
  map per detector. The Chapter 2 brief
  ([handoff](2026-11-13-chapter-2-synthetic-sets-and-detector-scoring.md)) sets out that tension.
- Tuning one setting per group is a statement about detectors on simulated sets. A statement
  that DI and MALE differ is a group finding and is fireflies' by default
  ([ADR-0017](../adr/0017-group-and-treatment-comparisons-default-to-fireflies.md)); ask Tony.

## Offered to Tony, not approved

- Build the rate-matched negative tool that ADR-0019 calls for.
- Score across thresholds: 4x-tuned settings on the 3x sets and the reverse.
- Rerun the cross-score at 24 recordings per background if 3x and 4x come out close.

## Still Tony's

Which settings go forward; merging #928 and #929 (neither approved); the hold on learned
detectors, in force since 2026-10-22; whether to start Chapter 2; the Great Lakes run
([run sheet](../greatlakes/RUN_2026-11-12_set_searches.md), untested, and a session cannot
submit there).

## Owed and not started

- Close-pair search per set: `tools/search_close_events.py --benches`.
- Find the slow evaluations: in `fast_di` at 4x three evaluations took 80 minutes. The suspect is
  SPIKE-synch with `dt` pushed to 0.0008 s; not confirmed.
- The full test suite has not been rerun on this branch since the bench-set work.

## Other sessions

The local board shows a session in worktree `land-tracked-cohorts-default` making PR #928 green.
This branch is based on that PR's branch, so its changes will arrive here by merge. Claim your
own block on the local board before the first edit.
