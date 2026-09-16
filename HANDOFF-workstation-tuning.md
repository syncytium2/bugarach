# Handoff — tune the leading learned detectors and CoactDetect under nested cross-validation, on the workstation

> **For a Claude Code session on the workstation.** Written 2026-09-16 by the Mac session
> `bugarach-broad-harbor`, at Tony's request: *"create a detailed handoff for the workstation run.
> repo is cloned and ready"*. The Mac session built everything this run stands on, on branch
> `eval-field-size-candidates` (PR #596, open and deliberately **not** set to auto-merge).
>
> **Working material, not murderboarded.** Same standing as the other handoffs. Every number below is
> on **simulated recordings** and links to the file that owns it; the linked file wins.
>
> When this work lands, this file leaves the repo root: delete it if spent, or move it to
> [`docs/handoffs/`](docs/handoffs/README.md) if anything in it is still worth reading.

## The question, in one paragraph

On 24 simulated home recordings, two repaired versions of `chorus` beat CoactDetect by 0.08 to 0.10
F1 at both training seeds, paired fold by fold. **Every learned model ran at one untuned setting, and
CoactDetect was tuned on one knob.** This run asks whether those margins survive when both sides get
a declared tuning budget, chosen without ever touching the fold they are scored on, and at five
training seeds instead of two. It is also allowed to find that tuning buys the learned models nothing,
or buys CoactDetect as much.

Abbreviations: **F1**, harmonic mean of recall and precision; **ROI**, region of interest (one imaged
cell); **CV**, cross-validation; ***t***, the paired *t* statistic over folds.

## Where things stand — read these first

| what | where |
|---|---|
| The table this run tests: every learned model against CoactDetect, two training seeds | [`docs/learned/field_size_candidates/README.md`](docs/learned/field_size_candidates/README.md), first section; numbers in `learned_vs_coact.json` beside it |
| Why `chorus` failed and how it was repaired | same readout, *Repairing chorus*; [`why_chorus.txt`](docs/learned/field_size_candidates/why_chorus.txt) |
| The evaluation route and its gates | [`docs/pipelines/learned-model-evaluation.md`](docs/pipelines/learned-model-evaluation.md) — stage 4, the supervised bake-off, is the one this run deepens |
| The bake-off tool | [`tools/fair_bakeoff.py`](tools/fair_bakeoff.py) — `--learned`, `--null-rates`, `--skip-hand-written`, `--train-seed` |
| The table builder | [`tools/table_learned_vs_coact.py`](tools/table_learned_vs_coact.py) |
| The gate a model must pass before it is worth training | [`tools/probe_untrained_response.py`](tools/probe_untrained_response.py) |

The numbers this run starts from (seed-averaged F1 minus CoactDetect's, paired over 4 folds, *t* on 3
degrees of freedom; from `learned_vs_coact.json`):

| model | F1 seed 0 / seed 1 | − CoactDetect, seed average | busy-window false alarms per hour | quiet-field false alarms per hour |
|---|---|---|---|---|
| chorus_norm | 0.741 / 0.756 | +0.103 (*t* 6.5) | 2.0 | 1.3 |
| chorus_gain_norm | 0.737 / 0.722 | +0.084 (*t* 10.2) | 1.5 | 0.6 |
| line_length | 0.704 / 0.691 | +0.052 (*t* 4.5) | 16.5 | 0.6 |
| tube | 0.656 / 0.635 | +0.000 (*t* 0.0) | 125.5 | 0.3 |
| CoactDetect | 0.645 | — | 5.5 | 0.5 |

## Scope — what this run is, and what it is not

**In scope.** Four learned models and two hand-written detectors, on the **home spec only**
(`docs/learned/generator_spec.json`, 32 ROIs), with the bake-off's own recordings (4 folds of 6,
recording seeds 1000–1023):

- `chorus_norm`, `chorus_gain_norm`, `line_length` — the three learned models ahead of CoactDetect.
- `tube` — **the tuning-inflation control.** It ties CoactDetect untuned. If tuning lifts `tube` well
  clear of tuned CoactDetect too, the leaders' margins are about tuning budget, not architecture.
- CoactDetect (`coact`) and LoCo (`loco`) — the two hand-written detectors that sit level with the
  learned family.

**Out of scope, on Tony's word or by construction:**

- **The Cossart spec, and transfer of any kind.** Tony, 2026-09-16: *"it's ok if the learned detectors
  don't automaticly work on cossart. don't get distracted"*.
- **Real recordings, label-free training, rigid shift.** That goal has open decisions waiting on Tony
  ([`docs/todo/2026-09-16-land-pr-588-and-finish-the-rigid-shift-report.md`](docs/todo/2026-09-16-land-pr-588-and-finish-the-rigid-shift-report.md)).
  The tuned weights from this run are meant to be its starting point later; do not start it here.
- **New architectures, new registrations, changes to any model's code.** Tune what exists.
- **Promoting a number.** `docs/MILESTONES.md` reserves bake-off promotion to Tony. Report; do not rank.
- **Merging #596.** Registering these models puts them in the lab server and the model picker, and
  that is Tony's call.

## Setup on the workstation

1. **Claim before the first file write.** Add a block to the machine-local board
   (`tools/guard_local_board.sh --path` prints where it is). ⚠ **Put no slash in the heading after the
   first one** — the guard strips the heading to its last slash, so a path or a `wip/` branch name in
   the heading makes the claim invisible to it
   ([`docs/todo/2026-09-16-the-board-guard-cannot-accept-a-branch-with-a-slash-in-it.md`](docs/todo/2026-09-16-the-board-guard-cannot-accept-a-branch-with-a-slash-in-it.md)).
2. **Branch from the evaluation branch, not from `main`**, which does not have the models or tools yet:

   ```bash
   git fetch origin
   git worktree add -b tune-learned-vs-coact ../bugarach-worktrees/tune-learned-vs-coact origin/eval-field-size-candidates
   cd ../bugarach-worktrees/tune-learned-vs-coact
   git branch --unset-upstream        # so a push cannot land on #596's branch
   git config core.hooksPath .githooks
   ```

   `origin/eval-field-size-candidates` already has `main` merged in as of `49fed1f`, including #594
   (every simulated recording now carries widths, drawn on a separate random stream, so event times do
   not move). If `main` has moved again, merge it in and say so in the first commit.
3. **Environment.** Native Windows and WSL both work; nothing in this run needs one over the other,
   and the Python is cross-OS by project rule (pathlib and environment variables, sapper SAP004). The
   commands in this file are bash. On native Windows:
   - the venv's interpreter is `.venv\Scripts\python.exe`, not `.venv/bin/python`;
   - the commit hooks and `tools/*.sh` are shell scripts, so commit from Git Bash (it ships with Git
     for Windows) or the gates do not run;
   - **`--jobs` must be spawn-safe**: Windows starts worker processes by spawning, not forking, so the
     worker is a top-level function and the entry point sits under `if __name__ == "__main__":`. A
     tool that forks happily on Linux and the Mac fails here and nowhere else.

   Build a venv if there is none: `python -m venv .venv`, then install with the `dev` extra
   (`pip install -e ".[dev]"`; it carries torch). Record, in the board block and in the run's
   `meta.json`: hostname, OS and whether it is WSL, logical CPU count, Python version, torch version.
4. **Threads.** `src/bugarach/learn/train.py` pins torch to **one intra-op thread** (`THREADS = 1`) and
   says the number is part of the result. Parallelism comes from running **processes**, one per fit.
   Do not raise `THREADS`. Training runs on the CPU; nothing in `train.py` moves a model to a GPU, and a
   GPU would not help without changing the code, which is out of scope.
5. **Darkroom.** Figures for Tony go to `<darkroom>/bugarach/` through `bugarach.paths.darkroom()`
   (set `BUGARACH_DARKROOM` if the mount is not found). **Claim a new folder in `docs/SESSIONS.md` on
   `main` before the first write** — a one-block PR off `main`, as #595 did for
   `field-size-candidates/`. Suggested folder: `<darkroom>/bugarach/tuned-vs-coact/`.

## Gate 1 — reproduce before tuning anything

A different machine can compute different floats. Before any tuning, rerun one untuned home bake-off
at training seed 0 and compare it with the Mac's file:

```bash
PYTHONPATH=src .venv/bin/python -u tools/fair_bakeoff.py --spec docs/learned/generator_spec.json \
  --out <scratch>/repro --seeds-per-fold 6 --null-rates \
  --learned tube,chorus_norm,line_length
```

(chorus_norm's seed-0 row lives in `docs/learned/field_size_candidates/chorus_repairs/chorus_norm/bakeoff.json`,
the rest in `docs/learned/field_size_candidates/bakeoff.json` and `rest_of_registry/line_length/bakeoff.json`.)

- **The six hand-written detectors must match per fold exactly.** They are numpy with fixed seeds.
  If they do not, stop and find out why; nothing downstream is comparable until they do.
- **The learned models should match per fold to within 0.02 F1.** Record the largest difference. A
  larger gap means this machine's training is not the Mac's, and every comparison with the Mac's
  numbers must say so; the tuned-versus-untuned comparison is then made **entirely on this machine**,
  with the untuned baseline rerun here (Gate 3 does that anyway).
- **Time one fit of each learned model alone** (the logs print `train … s`). The Mac's times ran with 6
  to 10 jobs sharing it and overstate a lone fit. These times set the budget in the next section.

## The design — nested cross-validation, both sides

**The rule that makes the comparison fair: nothing about a configuration is chosen with the fold it
is scored on.** The bake-off already keeps fitting and threshold-picking apart inside the training folds
(`fold_maker` in `src/bugarach/learn/train.py`); tuning adds one more level of the same discipline.

### Outer loop — the four bake-off folds

For each held-out fold *h* in 0–3, the other three folds (18 recordings) are the **training folds**.
The held-out fold's 6 recordings are touched once, at the end, by the chosen configuration.

### Choosing a learned model's configuration — inner CV on the training folds

For each candidate configuration, at training seed 0:

1. For each of the three training folds *j*: fit on the other two training folds (12 recordings) with
   `fold_maker(rec, those_seeds)` exactly as `fair_bakeoff.py` does, so the model's own threshold is
   picked on recordings its fit never saw; then score fold *j*'s 6 recordings.
2. The configuration's **inner score** is F1 pooled over all 18 inner-scored recordings with
   `bench.pool_scores` — pooled, not averaged over the three inner folds.
3. Choose the configuration with the highest inner score. Ties go to fewer parameters, then fewer
   training steps.

Then **refit the chosen configuration on all three training folds** at training seeds 0, 1, 2, 3 and 4,
and score the held-out fold at each. The chosen configuration may differ between outer folds; that is
correct nested CV, and it is reported rather than hidden.

Tuning happens at training seed 0 only, to keep the cost down. Say so in the readout.

### Choosing a hand-written detector's configuration — the training folds directly

The hand-written detectors fit nothing, so the configuration is their only fitted quantity. For each
outer fold, score every configuration in their grid on the 18 training-fold recordings, pool F1, pick
the best, and score the held-out fold once. This is `fair_bakeoff.py`'s calibration generalised from
one knob to a grid. They have no training seed.

### Search spaces — declared before any result is seen

Learned models: **24 configurations per model, drawn once with `random.Random(20260916)`** from the
space below, the untuned bake-off setting always included as one of the 24 so tuning can only match or
beat it on the inner score. If Gate 1's timings say 24 does not fit in one night, reduce **every**
learned model's count equally, and write the number into `meta.json` before starting.

| model | axis | values | untuned setting |
|---|---|---|---|
| all four | learning rate | 3e-3, 1e-2, 3e-2 | 1e-2 |
| all four | training steps | 900, 1800, 3600 | 900 |
| chorus_norm, chorus_gain_norm | `roi_width` | 4, 8 | 4 |
| chorus_norm, chorus_gain_norm | `roi_depth` | 4, 6 | 4 |
| chorus_norm, chorus_gain_norm | `top_m` | 2, 4, 8 | 4 |
| chorus_gain_norm | `vote_gain` | 4, 8, 16 | 8 |
| line_length | `n_scales` | 3, 4, 6 | 4 |
| line_length | `width` | 8, 16 | 8 |
| line_length | `vote_gain` | 4, 8, 16 | 8 |
| tube | `n_scales` | 3, 4, 6 | 4 |
| tube | `width` | 8, 16 | 8 |
| tube | `max_ratio` | 40, 80 | 40 |

Everything else stays at the bake-off's values: `crop=4096`, `batch=3`, `n_train=min(10, n_fit)`.
Architecture axes pass through `train(name, mk, **arch_over)`, which forwards them to the registered
builder; learning rate and steps are `train`'s own arguments.

Hand-written detectors, **full grid** (they are cheap). The knob grids are `bench.OPERATING_POINTS`'
own; the added axes bracket the shipped value on both sides:

| detector | axis | values | shipped |
|---|---|---|---|
| coact | `alpha` | the `OPERATING_POINTS` grid, 1e-1 to 1e-7 (8 values) | 1e-4 |
| coact | `int_win_sec` | 1.0, 2.0, 4.0 | 2.0 |
| coact | `context_win_sec` | 30, 60, 120 | 60 |
| loco | `threshold_pctile` | the `OPERATING_POINTS` grid, 99.0 to 99.9999 (6 values) | 99.9 |
| loco | `bin_width_sec` | 0.5, 1.0, 2.0 | 1.0 |
| loco | `context_win_sec` | 60, 120, 240 | 120 |

That is 72 configurations for coact and 54 for loco against 24 per learned model. **The hand-written
detectors get the larger budget**, deliberately, so a learned margin that survives cannot be blamed on
under-tuning the reference. Say so in the readout.

**Edge-of-grid check, on both sides.** If a chosen value sits at either end of its axis in any outer
fold, flag it in the output. The project's standing rule is that an optimum at an edge means the search
stopped while still climbing (`bench.EdgeOfRange`, and `pick_threshold`'s own warning).

### What to report, per outer fold and overall

- F1 on the held-out fold: each tuned learned model at five training seeds, their mean, and each
  tuned hand-written detector.
- **The primary comparison:** tuned learned model (seed-averaged) minus tuned CoactDetect, per outer
  fold, with the mean and the paired *t* on 3 degrees of freedom. Same against tuned LoCo.
- **The tuning effect:** tuned minus untuned, per model, on this machine. The untuned numbers are the
  24-configuration draw's included default, refitted in the outer loop at the same five seeds.
- The chosen configuration per outer fold, and whether the four agree.
- Busy-window and quiet-field false alarms per hour for each chosen configuration, computed exactly as
  `fair_bakeoff.py --null-rates` does (reuse `_null_twin` and the `hot_fa` count; do not re-derive them).
- Wall time per fit, and total CPU hours.

**A proposed reading, which Tony has not signed.** The margin *survives* if the tuned leader beats
tuned CoactDetect in all four outer folds on the seed average, and `tube`, tuned the same way, does
not clear tuned CoactDetect by a comparable amount. Report the numbers against this reading and **do
not declare a winner**; the decision is his.

## Gate 2 — build the tool, smoke it, then run

Nothing that does nested CV exists yet. Build **`tools/tune_learned_vs_coact.py`**, reusing rather than
copying: `bench.fold_split`, `bench.pool_scores`, `bench.run_detector`, `bench.OPERATING_POINTS`,
`train.fold_maker`, `train.train`, `score.score_stream`, and `fair_bakeoff._make_recording` and
`fair_bakeoff._null_twin`.

Requirements, each from something that has already cost this project a night:

- **One result file per fit**, keyed by model, configuration hash, outer fold, inner fold (or `outer`)
  and training seed, written atomically. A rerun skips keys that exist. A crash at hour five must not
  cost hours one to four.
- **`--jobs N`** runs fits as separate processes. Each process keeps `THREADS = 1`.
- **`--quick`** shrinks everything for a smoke run: 2 configurations per model, 100 steps, 2 folds of
  2 recordings, the hand-written grids thinned to 2 points per axis.
- **`meta.json` written before the first fit**: the declared search spaces, the configuration draw
  and its seed, the budget, the machine record from Setup, the git commit, and
  `registered: sorted(ARCHITECTURES)` beside `registered_but_not_run`, as the pipeline's stage 1 gate
  requires.
- **Outputs outside the repo while running** (a scratch folder, or the darkroom once claimed). Every
  run on the Mac recorded `git_dirty: true` because it wrote into an untracked repo folder mid-run. Copy
  the final JSONs into `docs/learned/tuned_vs_coact/` in the commit that reports them.
- **A test**, `tests/test_tune_learned_vs_coact.py`, running `--quick` on one learned model and coact
  and asserting: no held-out recording seed ever appears in a fit or a threshold pick, the result files
  resume, and the declared untuned configuration is among the draws. Keep it under about a minute:
  the suite has no slow marker to hide behind, only `serial` (in `pyproject.toml`), which is for tests
  that must not share the machine.

Then: `--quick` end to end, then the full run.

## Gate 3 — the readout

`docs/learned/tuned_vs_coact/README.md`, same standing and conventions as the field-size readout:

- The table first; every number with its unit ("F1", "false alarms per hour", "configurations",
  "CPU hours"). Define every abbreviation at first use.
- A figure if the finding is visual, and here it is: per outer fold, tuned and untuned F1 for each
  model beside tuned CoactDetect and LoCo, **drawn as points per fold, never as bars with range
  whiskers** (the pipeline's stage 7 gate; forest-plot grammar asserts a significance nobody computed).
  Number it *Figure 1.* in its caption. Render it, look at it, put a copy in the claimed darkroom folder
  with `python3 tools/show.py <file>`, and give Tony the path it prints.
- A *Limits* section: simulation only; four outer folds; tuning at one training seed; the hand-written
  side's larger budget; any Gate 1 difference from the Mac.
- An [`docs/INDEX.md`](docs/INDEX.md) row pointing at the readout, in the same commit.

## Things that will bite

- **Sapper SAP004 blocks a commit** of any log holding an absolute path from this machine, which every
  torch warning prints. Strip the worktree prefix from logs before `git add`.
- **"Data" is plural in everything you write**, and sapper SAP015 warns on a new line that breaks it.
- **A fold with planted events and no hits has F1 `NaN` in `bench`.** Count it as 0 in any comparison,
  and list which folds were converted; `tools/compare_field_size_candidates.py`'s `_f1` is the rule.
- **`chorus` (unrepaired), `trace` and `tiny` do not train** and are not in this run. If a tuned
  configuration of any model lands at F1 0.125 with its threshold at 0.0001, that is the same failure:
  record it, do not tune around it silently.
- **The Mac's quoted training times are inflated** by up to 10 concurrent jobs. Use Gate 1's.
- **Do not change `tools/fair_bakeoff.py`'s default behaviour.** Its transfer test
  (`tests/test_fair_bakeoff_transfer.py`) checks that the default path is unchanged.
- **Push every completed stage promptly.** Push the branch `tune-learned-vs-coact` after Gate 1, after
  the tool passes `--quick`, and when the run finishes. If you stop mid-run, push a `wip/` branch and
  update this file with where it stopped.

## Where to put the result

Open a PR from `tune-learned-vs-coact` against `eval-field-size-candidates` while #596 is open, or
against `main` once #596 has merged. Do not set auto-merge on a PR whose base is another session's
branch. Update this handoff's status line below in the same PR.

**Status:** not started. The Mac session's runs finished at 13:27 on 2026-09-16 and it holds no CPU;
CI on #596 was still running when this was written.
