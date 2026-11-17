# Run sheet: the nine bench-set searches on Great Lakes

**Use this page when** you are Tony, at a terminal, about to run the detector-settings search
on every bench set. Written 2026-11-12. Access and rules: [`README.md`](README.md).

> Working material, not murderboarded. Nothing from bugarach has run on the cluster yet, so
> steps 3 and 4 are the first test of the environment, and either can stop the run.

**What runs.** One search per bench set (three streams, each on all recordings, DI and MALE;
`docs/learned/bench_sets/`), nine tasks in one job array, each on one 36-core node, then a
verdict job that opens every output. The searches simulate their own recordings; no export
folder goes to the cluster.

**How long.** The `fast_di` search took 129.8 minutes on 11 workers on a workstation
(358 evaluations, about 24 core-hours). On 36 cores that is under an hour if it scales; the
job asks for 8 hours and 64 GB, both to be replaced by what this run uses.

**Two values are not in this repository,** because it is public: the Slurm account and the
path of the lab's shared research drive. Both are in interface2's `greatlakes/ACCESS.md`.
`<login>`, `<account>` and `<turbo root>` below stand for them.

One command per line. Paste one, read its last line, then the next.

## 1. Log in

```
ssh <login>@greatlakes.arc-ts.umich.edu
```

## 2. Get the code

```
git clone --branch synth/per-group-benches https://github.com/syncytium2/bugarach.git ~/bugarach
```

If `~/bugarach` is already there: `git -C ~/bugarach pull --ff-only`

## 3. Check what the cluster has

```
bash ~/bugarach/tools/greatlakes/env_check.sh
```

It prints the Python modules available and three lines starting `== reach`, one per site
the environment is built from. **Each must end in `200`. If one does not, stop here** and send
the output back; the environment in step 4 cannot be built that way.

## 4. Build the environment (once, about 2 minutes)

```
bash ~/bugarach/tools/greatlakes/setup_env.sh
```

The last line must read `ENVIRONMENT: READY at ...`. Anything else: stop and send the output.

## 5. Say where to charge and where to write

```
export BUGARACH_SLURM_ACCOUNT=<account>
```

```
export BUGARACH_GL_OUT="<turbo root>/data/bugarach/2026-11-12-set-searches"
```

The quotes matter: the drive's path contains a space. The folder is created by step 6.

## 6. Submit

```
bash ~/bugarach/tools/greatlakes/submit_search_sets.sh
```

It prints the nine sets, the array's job number and the verdict job's number, and writes
`run_record/SUBMITTED_set_searches.txt` under the output folder.

To submit only some sets, name them:
`bash ~/bugarach/tools/greatlakes/submit_search_sets.sh slow_di slow_male`

## 7. Watch

```
squeue -u $USER
```

Each task's log is `logs/search_<array>_<task>.out` under the output folder, readable from a
workstation through the shared drive.

## 8. The verdict

When the queue is empty:

```
cat "$BUGARACH_GL_OUT/run_record/VERDICT_set_searches.txt"
```

The first line is `VERDICT: PASS`, `FAIL` or `FAILED-TO-RUN`, then one line per set. A
bugarach session reads the same file from the workstation and takes it from there: it
cross-scores the searches with `tools/cross_score_sets.py --searches <that folder>`.

## 9. After the run, two numbers to send back

```
sacct -j <array job number> --format=JobID,Elapsed,MaxRSS,State
```

Elapsed time and peak memory per task replace the 8 hours and 64 GB in
`tools/greatlakes/search_sets.sbatch`.

## If something fails

- **A task ran out of time or memory** (`State` is `TIMEOUT` or `OUT_OF_MEMORY`): resubmit that
  set by name (step 6). Its chance floors are kept under the set's own folder, so the second
  run does not compute them again; the search itself starts over.
- **`FAILED-TO-RUN` for every set:** the environment, most likely. Send the first
  `logs/search_*.err`.
