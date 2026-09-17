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

## Decisions of 2026-09-16 — they override anything below that disagrees

Taken by Tony on 2026-09-16, after the workstation session proposed its Gate 1 and asked three
questions. Each is written into the section it changes; this list is the index.

1. **Scripted, not in the app.** The 2026-08-28 ruling that the next bake-off would run in the app
   ([`docs/todo/2026-08-28-the-bakeoff-calibrates-without-the-gate.md`](docs/todo/2026-08-28-the-bakeoff-calibrates-without-the-gate.md))
   rested, Tony says, on an assumption that the project was further along than it was: *"i believe
   these big runs need scripting and not in-app."* This run is scripted.
2. **Gate 1's float check runs at `7fc052d`, and all six hand-written detectors must match the Mac
   exactly.** No exemption for locust or binned SCE. See *Gate 1*.
3. **The tip's grids for the hand-written side**, after #597: 99 configurations for CoactDetect, 72 for
   LoCo. See *Search spaces*.
4. **False alarms: one set of fits, two selections, both declared now** (option D). **Primary:
   ungated**, pooled F1 on both sides, as the table under test was built. **Secondary: gated**, by one
   false-alarm budget shared by every model and anchored to CoactDetect at its shipped setting, with the
   learned threshold inside the gate. See *Two selections from the same fits*.
5. **Comparison only.** Tuned CoactDetect and LoCo exist to be compared against. They are never
   proposed values for `bench.OPERATING_POINTS`, which belongs to `HANDOFF-detector-optimization.md` on
   branch `detector-review-doc` (PR #587); its §4 lists the window widths searched here among the
   parameters never varied. Do not edit `OPERATING_POINTS` from this branch.
6. **It runs overnight, unattended.** Launched so that closed terminals, a closed VS Code and an ended
   session do not stop it, on a machine checked for sleep, restarts and WSL idle shutdown first. See
   *Running it overnight, unattended*.
7. **CoactDetect and LoCo slide** (Tony, later on 2026-09-16: *"use sliding versions. redo step 2"*).
   The reference detectors are `window_mode="sliding"`, with the exact null, from branch
   `sliding-loco-coact` (`005ae98`, merged here at `425ab2e`; not on `main`). The binned ports are not
   compared against. The overnight settings search on branch `full-search` concerns only the six
   hand-written detectors' own operating points and does not change this run. Gate 1 step 2 is redone on
   the sliding code; see *Gate 1*, *Two selections* and *Search spaces*.
8. **Three training seeds per configuration, and no 9-hour cutoff** (Tony, 2026-09-16, after Gate 1:
   *"9 hours is arbitrary. nothing is waiting on these days… a run until noon is fine but not a cutoff.
   run 3 seeds"*). Every learned configuration's inner score pools training seeds 0, 1 and 2. The
   estimate is still written into `meta.json` and reported; it no longer decides whether to launch.

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
3. **Environment — decided by Tony before anything is installed.** The workstation session's review
   (2026-09-16) found no WSL distribution and no Python of any kind on the machine, and its session
   briefing **failed in safe mode**: the hook was killed in its unpushed-work section, so no guard ran.
   The Python in this repo is cross-OS by rule (pathlib and environment variables, sapper SAP004); the
   *guards* are not: the session-start hook, the commit hooks, the board guard and `tools/*.sh` are
   shell scripts, and on native Windows they ran slowly enough to be killed.

   **Recommended: WSL2 with Ubuntu**, because it keeps every guard native and the briefing working.
   It needs admin rights and probably a reboot.
   - Clone **inside the Linux filesystem** (`~/Developer/bugarach`), not under `/mnt/c`: file access
     across that boundary is slow, and the bake-off generates thousands of recordings.
   - Build the venv there: `python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"` (the `dev`
     extra carries torch).
   - The Dropbox mount is on the Windows side. Point `BUGARACH_DARKROOM` at the darkroom's
     `bugarach` folder under `/mnt/c/Users/<user>/<Dropbox folder>/…` **as an environment variable
     only**: that path carries a person's name and must never be written into the repo (SAP004).
     Check it with `.venv/bin/python -c "from bugarach.paths import darkroom; print(darkroom())"`.

   **Fallback: native Windows Python** (for example through `uv`). Faster to install, and then:
   - the venv's interpreter is `.venv\Scripts\python.exe`, not `.venv/bin/python`;
   - commit from Git Bash (it ships with Git for Windows), or the gates do not run;
   - **`--jobs` must be spawn-safe**: Windows starts worker processes by spawning, not forking, so the
     worker is a top-level function and the entry point sits under `if __name__ == "__main__":`;
   - expect the session briefing to keep failing, and **check the board by hand** at session start,
     because nothing will print it for you.

   Either way, record in the board block and in the run's `meta.json`: hostname, OS and whether it is
   WSL, physical and logical CPU counts, RAM, Python version, torch version.
4. **Threads.** `src/bugarach/learn/train.py` pins torch to **one intra-op thread** (`THREADS = 1`) and
   says the number is part of the result. Parallelism comes from running **processes**, one per fit.
   Do not raise `THREADS`. Training runs on the CPU; nothing in `train.py` moves a model to a GPU, and a
   GPU would not help without changing the code, which is out of scope.
   **Run 22 jobs, not 48.** The machine has 24 physical cores and 48 logical ones. Jobs on hyperthread
   siblings inflate each fit's wall time, and the readout reports those times; that is exactly the
   flaw in the Mac's numbers. Leave two cores for the session itself.
5. **Darkroom.** Figures for Tony go to `<darkroom>/bugarach/` through `bugarach.paths.darkroom()`
   (set `BUGARACH_DARKROOM` if the mount is not found). **Claim a new folder in `docs/SESSIONS.md` on
   `main` before the first write** — a one-block PR off `main`, as #595 did for
   `field-size-candidates/`. Suggested folder: `<darkroom>/bugarach/tuned-vs-coact/`.

## Gate 1 — reproduce before tuning anything

A different machine can compute different floats. Before any tuning, three steps, **one process at a
time with nothing else on the machine**, outputs under `~/runs/` (not `/tmp`; see *Things that will
bite*).

**Mechanics.** A worktree has no `.venv` of its own: run `~/bugarach/.venv/bin/python` with
`PYTHONPATH=<worktree>/src`, and check that it imports the worktree's code. `fair_bakeoff.py --learned ""`
falls back to every model, so the six hand-written detectors cannot run alone; run them with
`--learned tube`, which is cheap.

```bash
PYTHONPATH=<worktree>/src ~/bugarach/.venv/bin/python -u tools/fair_bakeoff.py \
  --spec docs/learned/generator_spec.json --out ~/runs/gate1/<step> --seeds-per-fold 6 --null-rates \
  --learned <models>
```

The Mac's seed-0 rows: `tube` and the six hand-written detectors in
`docs/learned/field_size_candidates/bakeoff.json`; `chorus_norm` and `chorus_gain_norm` in
`docs/learned/field_size_candidates/chorus_repairs/<model>/bakeoff.json`; `line_length` in
`docs/learned/field_size_candidates/rest_of_registry/line_length/bakeoff.json`.

**Step 1 — floats, at the Mac's code.** In a detached worktree at `7fc052d`, `--learned tube`.
`7fc052d` comes before #593 (binned SCE scored over its bin) and #594 (every recording carries widths),
and has the grids from before #597.

Two rules, and they are different kinds of rule:
- **The six hand-written detectors: a hard stop.** They are numpy with fixed seeds, so all six must
  match the Mac per fold, exactly, on every result field. No exemptions. A mismatch means the
  recordings, the detectors or the scorer differ, and nothing downstream is comparable until it is
  explained: stop and report. The Mac's references were produced from working trees with uncommitted
  changes (at `239f176`, `3bf3271` and `af407f2`), so say which cause is known and which is not.
- **`tube`: a tolerance, not a stop.** It should match within 0.02 F1. A miss means this machine's
  training is not the Mac's: every comparison with the Mac's learned numbers says so, and tuned against
  untuned is compared on this machine, as it is anyway. Record the miss and go on.

**Result, 2026-09-16** ([`docs/learned/tuned_vs_coact/gate1/README.md`](docs/learned/tuned_vs_coact/gate1/README.md)):
the six matched exactly. `tube` missed by 0.0012 F1 on one fold, which the first wording of this step
treated as a stop; Tony ruled it a training difference between machines, not a defect.

**Step 2 — this machine's baseline, at the tip.** The six plus `tube`. Differences from the Mac are
expected and belong to #593, #594 and #597, not to this machine; report them as such. The generator
did not move: recordings 1000, 1013 and 1023 hash identically at `7fc052d` and at the tip (events,
rise times, amplitudes, ground truth; checked 2026-09-16), and learned detections carry no
`extent_sec`, so the scoring change of #593 does not reach them.

**Step 2 is redone on the sliding code** (decision 7). The first step 2 ran binned CoactDetect and LoCo
and stays in the record as the binned baseline. In the rerun, CoactDetect and LoCo are new detectors, so
they have no Mac reference; the other four hand-written detectors and `tube` must equal the first step 2
exactly, since nothing they run changed.

**Step 3 — lone-fit timings, at the tip.** `chorus_norm`, `chorus_gain_norm` and `line_length`, one model
per process. Record each model's per-fold difference from the Mac. A difference means this machine's
training is not the Mac's, and every comparison with the Mac's numbers must say so; the
tuned-versus-untuned comparison is made on this machine regardless. The logs print `train … s`: these
times, not the Mac's (which ran with 6 to 10 jobs sharing the machine), set the estimate in *Search
spaces*, and the estimate decides whether the run fits in one night.

**Step 3 keeps one stop** (Tony, 2026-09-16). Stop and report if either happens; anything smaller is
recorded, not a stop:
- **A fold further from both Mac seeds than the Mac's own seeds are from each other.** For a model, the
  Mac's largest seed-to-seed gap is the largest per-fold |F1 at seed 1 − F1 at seed 0| in
  [`learned_vs_coact.json`](docs/learned/field_size_candidates/learned_vs_coact.json). Stop if on any fold
  this machine's F1 is further than that from **both** Mac seeds.
- **The failed-training signature:** F1 near 0.125 with the threshold at 0.0001, on any fold.

## The design — nested cross-validation, both sides

**The rule that makes the comparison fair: nothing about a configuration is chosen with the fold it
is scored on.** The bake-off already keeps fitting and threshold-picking apart inside the training folds
(`fold_maker` in `src/bugarach/learn/train.py`); tuning adds one more level of the same discipline.

### Outer loop — the four bake-off folds

For each held-out fold *h* in 0–3, the other three folds (18 recordings) are the **training folds**.
The held-out fold's 6 recordings are touched once, at the end, by the chosen configuration.

### Choosing a learned model's configuration — inner CV on the training folds

For each candidate configuration, at training seeds 0, 1 and 2 (decision 8):

1. For each of the three training folds *j* and each seed: fit on the other two training folds (12
   recordings) with `fold_maker(rec, those_seeds)` exactly as `fair_bakeoff.py` does, so the model's own
   threshold is picked on recordings its fit never saw; then score fold *j*'s 6 recordings.
2. The configuration's **inner score** is F1 pooled with `bench.pool_scores` over all 54 inner-scored
   (recording, seed) rows — 18 recordings × 3 seeds, pooled, not averaged over folds or seeds. An inner
   fit has 10 fitting recordings and uses all 10 at every seed, so its seeds differ in the torch
   initialisation and the crops drawn, not in the recordings.
3. Choose the configuration with the highest inner score. Ties go to fewer parameters, then fewer
   training steps.

**Half the inner fits are the same fit, so cache fits separately from scores.** An inner fit trains on
two of the four folds, and only six pairs exist: the pair of folds 0 and 1 is the same fit whether
fold 2 or fold 3 is the one held out. Key each **fit** (weights and the threshold it picked) by model,
configuration hash, training seed and the **sorted** tuple of its recording seeds; score it on whichever
fold needs it, and key each **score** by fit key and scored fold. Always pass recordings to
`fold_maker` **sorted**: it takes the last two as the threshold-picking set and indexes the rest by
position, so the same recordings in a different order are a different fit. This halves the tuning
compute and changes no result.

Then **refit the chosen configuration on the three training folds** at training seeds 0, 1, 2, 3 and
4, and score the held-out fold at each. The chosen configuration may differ between outer folds; that is
correct nested CV, and it is reported rather than hidden.

**What a refit actually trains on — say this in the readout.** `train` fits on `min(10, n_fit)`
recordings, and `fold_maker` hands it recordings by position, offset by the training seed. Checked on
outer fold 0 (2026-09-16):
- an **inner fit** gets 12 recordings: it fits on 10, all of the non-threshold ones, and picks its
  threshold on the last 2;
- an **outer refit** gets 18: it fits on **10 of the 16** non-threshold recordings and picks its
  threshold on the same last 2 at every seed. **Which 10 alternates with the seed's parity**: seeds 0,
  2 and 4 fit on one subset, seeds 1 and 3 on another, and six recordings go unused at any given
  seed.

So "five training seeds" varies the torch initialisation and two alternating recording subsets. Every
bake-off in this project has worked this way, including the table this run tests; do not change it
here, or the tuned numbers stop being comparable with the untuned ones.

Tuning pools training seeds 0, 1 and 2 (decision 8). Gate 1 measured a one-seed selection's noise at
about 0.04 F1 between two configurations (two standard deviations), and three seeds bring it to about
0.024; say so in the readout, with Gate 1's Table 9.

### Choosing a hand-written detector's configuration — the training folds directly

The hand-written detectors fit nothing, so the configuration is their only fitted quantity. For each
outer fold, score every configuration in their grid on the 18 training-fold recordings, pool F1, pick
the best, and score the held-out fold once. This is `fair_bakeoff.py`'s calibration generalised from
one knob to a grid. They have no training seed.

### Two selections from the same fits — option D

Every fit and every hand-written configuration is scored once; **two selections read those scores**,
both declared here before any result exists. **The primary answers this run's question.** The secondary
says whether that answer holds when no model may buy F1 by firing where nothing is planted.

**Why a gate, and why not `main`'s.** F1 is scored only on recordings with planted events, so a
configuration can raise it while firing more where nothing is planted, and a search over 24 to 99
configurations will find such a configuration if one exists. For this lab the busy-window rate is not
a nuisance: a detector that fires more when background firing rises reports "more coordination"
whenever a treatment raises the rate. `bench`'s budgets (`MAX_PROBE_PER_MIN`,
`MAX_FALSE_POSITIVES_PER_HOUR`) are each detector's **own** measured firing plus a margin, and no learned
model has one, so gating one side with them would be unfair. The secondary uses **one budget for every
model**, measured with the bake-off's own instruments.

**The two false-alarm rates.** Reuse these; do not re-derive them.
- **Busy-window false alarms per hour:** `hot_fa` from `score_stream` on the planted recordings, divided
  by the hot window's duration (5 minutes per recording), as `tools/table_learned_vs_coact.py` converts it.
- **Quiet-field false alarms per hour:** detections on `_null_twin(spec, 0.54)` recordings at seed
  `recording seed + NULL_SEED_OFFSET`, as `null_fa_per_hour` in `fair_bakeoff.py` counts them. **The gate
  uses factor 0.54**, the lower quartile of real untreated recordings. Factor 0.25 is a stress level below
  anything measured: report it, never gate on it. The table this run tests shows 0.25 in its quiet-field
  column, so every quoted quiet-field number says its factor.

**The budget, per outer fold, from training recordings only.** On outer fold *h*'s 18 training
recordings and their 0.54 twins, run CoactDetect at `OPERATING_POINTS["coact"].params` (nothing tuned)
and measure both rates. Fold *h*'s budget is **1.6 times each rate**, for every model, CoactDetect and
LoCo included. **Floor:** never below one false alarm in the measured duration (one per 1.5 busy-window
hours; one per the 18 twins' total hours), so a reference that happens to fire zero times does not
refuse everything. The 1.6 is `bench`'s own ratio of CoactDetect's empty-recording budget to its measured
rate (7.0 against 4.4). Tony may change it until the run starts; `meta.json` records it, and it does not
move after.

**The reference is sliding CoactDetect** (decision 7) at `OPERATING_POINTS["coact"].params` as of this
branch: `window_mode="sliding"` at the binned-tuned values (`int_win_sec` 2.0, `context_win_sec` 60,
`alpha` 1e-4). Those values are not a calibrated sliding point: the `full-search` handoff measured
sliding CoactDetect there at 7.7 false alarms per hour on the empty recording, against `bench`'s limit
of 7. The budget does not need it to be calibrated, only fixed and measured on training recordings; but
the 1.6 was derived from binned CoactDetect's ratio, so say in the readout that it was carried over.
Write the reference's parameters into `meta.json`. If `sliding-loco-coact` later sets new shipped
values, this run keeps the ones it declared.

**Primary, ungated.** Exactly as the two sections above describe: a learned fit keeps the threshold
`train` picked, and the highest pooled inner F1 wins, on both sides.

**Secondary, gated.** On the learned side the **threshold becomes part of the candidate**. A hand-written
configuration already contains its threshold (`alpha`, a percentile), so gating a learned configuration
at one fixed threshold would refuse it where a hand-written one could step down a notch.
- *Hand-written:* candidates are the grid's configurations. Admissible if both rates on the 18 training
  recordings are within fold *h*'s budget; the highest pooled F1 among the admissible wins.
- *Learned:* candidates are (configuration, threshold) pairs over `pick_threshold`'s own threshold grid.
  For each inner fit, compute the model's probabilities **once** per scored recording and per 0.54 twin,
  then decode at every threshold exactly as `Trained.predict` does (`decode`, then `to_seconds`). Pool F1
  and both rates over the 18 inner-scored recordings; admissible within budget; the highest pooled F1
  wins. The chosen configuration's outer refits are decoded at **the chosen threshold**, not their own.
  That carries a threshold chosen at training seed 0 across five seeds: say so in the readout, and report
  how often the held-out rates exceed the budget.
- **No admissible candidate in a fold:** report "no admissible configuration", and count that fold's
  held-out F1 as 0 in the secondary comparison, the same rule as `NaN`.
- Ties as in the primary. Where the two selections choose the same configuration, its outer refits are
  shared (refits are keyed by configuration and seed).

**Extract the threshold grid; do not copy it.** It is built inline in `pick_threshold`. Move it to a
module-level constant in `src/bugarach/learn/train.py`, used by both, with no change in value. That is
training code, not any model's code, and the existing tests of `pick_threshold` cover it.

### Search spaces — declared before any result is seen

Learned models: **24 configurations per model**, the untuned bake-off setting always one of them, so
tuning can only match or beat it on the inner score. **The draw, exactly**, so anyone can recompute it
and check it was declared rather than chosen:

1. For each model, list every configuration as `itertools.product` over that model's axes **in the
   order the table below lists them**: learning rate, training steps, then the model's own axes top to
   bottom.
2. Remove the untuned setting from the list.
3. With a **fresh** `random.Random(20260916)` for each model, take `rng.sample(remaining, 23)`.
4. Append the untuned setting as the 24th.

Write the 24, in that order, into `meta.json` before the first fit. **Do not cut the 24.**

**Hash normalised values.** Configurations are compared by value (`8 == 8.0`, so removing the untuned
setting from the list works), but the cache key is a hash, and `json.dumps` writes `8` and `8.0`
differently. `vote_gain` is registered as `8.0` and declared as `8` in the table below. Normalise every
value (every number as a float) before hashing, or one configuration gets two keys.

**The estimate.** Per learned model: 24 configurations × 6 distinct inner fold pairs × 3 seeds = 432
inner fits, plus outer refits at 5 seeds × 4 folds for the untuned setting and for each selection's
choice (40 to 60 refits), so about 470 to 490 fits. The drawn configurations average about 2.3 times the
untuned 900 steps. From Gate 1's lone-fit times on this machine that is a floor of about 196 CPU hours of
training, 8.9 hours at 22 jobs, before scoring and before the larger configurations' extra cost per step.
Scoring adds inference on the scored recordings and 0.54 twins for every fit, and the hand-written grids
on 24 planted recordings and 24 twins. **Write the estimate into `meta.json` and report it; it does not
gate the launch** (decision 8). Do not cut the 24.

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
own **as of the tip, after #597** (decision 3), written out here so the declaration does not move if
`bench` does; the added axes bracket the shipped value on both sides:

| detector | axis | values | shipped |
|---|---|---|---|
| coact | `alpha` | 1e-1, 3e-2, 1e-2, 3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5, 1e-6, 1e-7 (11 values) | 1e-4 |
| coact | `int_win_sec` | 1.0, 2.0, 4.0 | 2.0 |
| coact | `context_win_sec` | 30, 60, 120 | 60 |
| loco | `threshold_pctile` | 97.0, 98.0, 99.0, 99.5, 99.9, 99.99, 99.999, 99.9999 (8 values) | 99.5 |
| loco | `bin_width_sec` | 0.5, 1.0, 2.0 | 1.0 |
| loco | `context_win_sec` | 60, 120, 240 | 120 |

Every other parameter stays at `OPERATING_POINTS` as of the tip, **including `window_mode="sliding"`**
for both (decision 7). In sliding mode `int_win_sec` and `bin_width_sec` are the width of the sliding
window, and `n_surrogates` and `thr_step_sec` do not apply, so no axis is spent on them. That is 99
configurations for coact and 72 for loco against 24 per learned model.

⚠ **The long context values may win for a reason that does not transfer.** The `full-search` run found
240 s contexts gaining on held-out bench recordings and losing on crowded ones, which it reads as fitting
the bench's spacing of planted events (at least 120 s apart). LoCo's grid here includes 240 s. Whether
the home spec (`docs/learned/generator_spec.json`) spaces its events the same way has not been checked;
check it before launch, and if it does, flag any chosen 240 s context in the readout. **The hand-written
detectors get the larger budget**, deliberately, so a learned margin that survives cannot be blamed on
under-tuning the reference. Say so in the readout.

**Edge-of-grid check, on both sides, on axes of three values or more.** If a chosen value sits at
either end of such an axis in any outer fold, flag it in the output; the project's standing rule is
that an optimum at an edge means the search stopped while still climbing (`bench.EdgeOfRange`, and
`pick_threshold`'s own warning). **Two-value axes are exempt** — `roi_width`, `roi_depth`, `width`,
`max_ratio` — because both of their values are ends and the check would fire on every run. Say in
the readout that they are unchecked. The training-steps axis starts at the untuned 900, so a chosen
900 does flag; report it, since it means fewer steps than any tried might have done as well.

### What to report, per outer fold and overall

- F1 on the held-out fold: each tuned learned model at five training seeds, their mean, and each
  tuned hand-written detector.
- **The primary comparison:** tuned learned model (seed-averaged) minus tuned CoactDetect, per outer
  fold, with the mean and the paired *t* on 3 degrees of freedom. Same against tuned LoCo.
- **The tuning effect:** tuned minus untuned, per model, on this machine. The untuned numbers are the
  24-configuration draw's included default, refitted in the outer loop at the same five seeds.
- The chosen configuration per outer fold, and whether the four agree.
- Busy-window and quiet-field false alarms per hour for each chosen configuration, computed exactly as
  `fair_bakeoff.py --null-rates` does (reuse `_null_twin` and the `hot_fa` count; do not re-derive them),
  at all three twin factors, each labelled with its factor.
- **All of the above twice**, primary and secondary, side by side, never merged into one table. For the
  secondary also: each fold's budget, the chosen (configuration, threshold), the number of admissible
  candidates per model and fold, every "no admissible configuration", and the held-out rates against
  the budget.
- Wall time per fit, and total CPU hours.

**A proposed reading, which Tony has not signed.** The margin *survives* if the tuned leader beats
tuned CoactDetect in all four outer folds on the seed average, and `tube`, tuned the same way, does
not clear tuned CoactDetect by a comparable amount. Apply the same reading to the secondary. A margin
that survives the primary but not the secondary is reported as **"wins only while firing more than the
shared budget allows"**, never as a win. Report the numbers against this reading and **do not declare a
winner**; the decision is his.

## Gate 2 — build the tool, smoke it, then run

Nothing that does nested CV exists yet. Build **`tools/tune_learned_vs_coact.py`**, reusing rather than
copying: `bench.fold_split`, `bench.pool_scores`, `bench.run_detector`, `bench.OPERATING_POINTS`,
`train.fold_maker`, `train.train`, `score.score_stream`, and `fair_bakeoff._make_recording` and
`fair_bakeoff._null_twin`.

Requirements, each from something that has already cost this project a night:

- **One result file per fit and one per score**, keyed as in *Half the inner fits are the same fit*
  above, written atomically (write to a temporary name, then rename). A rerun skips keys that exist. A
  crash at hour five must not cost hours one to four.
- **What a score file holds**, so both selections come from it without rerunning anything: for a
  learned fit, per scored recording and per 0.54 twin, the counts `bench.pool_scores` pools (the
  `score_stream` result's fields, `hot_fa` included) and the twin's detection count and duration, **at
  every threshold of the grid**, with the fit's own threshold marked; for a hand-written configuration,
  the same at its one setting. Twins at 1.0 and 0.25 are scored only for chosen configurations, on the
  held-out fold.
- **The shipped-CoactDetect reference** (the budget's source) is scored first, on all 24 recordings and
  their 0.54 twins, and each fold's budget is pooled from its 18 training recordings. Write every fold's
  budget into `meta.json` before the first learned fit.
- **A fit that raises does not stop the run.** It writes an error file under its key (the traceback, the
  configuration, the seed) and the run goes on; the summary lists every error. No silent retry. A
  selection that needs an errored fit reports the configuration as missing rather than skipping it.
- **`progress.json`**, rewritten atomically after every completed fit or score: done and total per
  stage and per model, errors, fits per hour over the last hour, projected finish, and the commit.
- **Queue in priority order**, so a night cut short still leaves complete answers for the most important
  models: (1) the shipped-CoactDetect reference and budgets; (2) the hand-written grids; (3) the learned
  models in the order `chorus_norm`, `tube`, `chorus_gain_norm`, `line_length`, each through inner fits,
  both selections and outer refits. Idle workers take the next model's inner fits rather than wait for a
  selection to finish.
- **`--jobs N`** runs fits as separate processes. Each process keeps `THREADS = 1`.
- **`--quick`** shrinks everything for a smoke run: 2 configurations per model, 100 steps, 2 folds of
  2 recordings, the hand-written grids thinned to 2 points per axis.
- **`meta.json` written before the first fit**: the declared search spaces, the configuration draw
  and its seed, the budget, the machine record from Setup, the git commit, and
  `registered: sorted(ARCHITECTURES)` beside `registered_but_not_run`, as the pipeline's stage 1 gate
  requires. Also **Gate 1's reproduction record**, as three facts: `tube` at `7fc052d` differs from the
  Mac per fold by −0.0034, −0.0212, −0.0053 and +0.0069 F1, and is deterministic on this machine; the
  committed training code is identical between `239f176` and `7fc052d`; the Mac recorded neither its
  torch version nor its uncommitted changes, so CPU float differences cannot be separated from those
  changes. Add step 3's per-model differences beside them.
- **The torch version in everything this run writes**: `meta.json`, `progress.json`, and every fit and
  score file. `fair_bakeoff.py`'s provenance does not record it, which is why the Mac's
  numbers cannot be attributed.
- **Outputs outside the repo while running** (a scratch folder, or the darkroom once claimed). Every
  run on the Mac recorded `git_dirty: true` because it wrote into an untracked repo folder mid-run. Copy
  the final JSONs into `docs/learned/tuned_vs_coact/` in the commit that reports them.
- **A test**, `tests/test_tune_learned_vs_coact.py`, running `--quick` on one learned model and coact
  and asserting: no held-out recording seed, **and no held-out recording's twin**, ever appears in a fit,
  a threshold pick, a budget or either selection; the result files resume; the declared untuned
  configuration is the 24th draw and the other 23 match the procedure above; a fit reached from two
  different outer folds is trained once and scored twice; decoding a fit at its own threshold reproduces
  `Trained.predict` exactly; pooling stored score rows equals pooling the live results; and `8` and
  `8.0` hash to the same configuration key. Keep it under about a minute:
  the suite has no slow marker to hide behind, only `serial` (in `pyproject.toml`), which is for tests
  that must not share the machine.

Then: `--quick` end to end, then the full run, launched as the next section describes.

## Running it overnight, unattended

Tony, 2026-09-16: the full run goes overnight on the workstation with nobody watching. The resumable
result files above make a crash cheap; this section makes a crash unlikely and the morning readable.

**Before launch.** The session does these, with Tony present for anything that needs `sudo`.

1. **Gates 1 and 2 have passed**, `--quick` has run end to end, and the estimate is in `meta.json`
   (it does not gate the launch; decision 8). Push the branch, with this file's status line naming the commit about to
   run, the budget margin, and the expected finish time.
2. **Output directory `~/runs/tune-learned-vs-coact/`**, in the Linux filesystem. Not `/tmp`, not a
   session scratchpad, not under `/mnt/c`.
3. **Launch detached from every terminal, as a systemd unit**, so that closing VS Code, the Ubuntu
   window or the Claude session does not end it. Ubuntu 26.04 under WSL runs systemd. Either
   `sudo systemd-run --unit=tune-learned-vs-coact --uid=$USER -p WorkingDirectory=<worktree>
   --setenv=PYTHONPATH=<worktree>/src …`, or run `sudo loginctl enable-linger $USER` once and then
   `systemd-run --user`. Log to a file in the output directory as well as the journal. Do not rely on
   `nohup` or `&`.
4. **Prove that WSL keeps running with nothing attached; do not assume it.** WSL can stop an idle
   distribution, or its whole VM, when no Windows-side client is attached, and that kills the unit.
   Test it with the launcher chosen in step 3: a unit that writes a timestamp to a file every 30 seconds
   for 15 minutes. Close every Ubuntu terminal and every VS Code window connected to WSL. After 10
   minutes, check from Windows (`wsl -l -v`, then read the file). If the timestamps stopped, fix it
   before launch, then test again. The likely fixes are an idle-timeout setting in
   `%UserProfile%\.wslconfig`, or a minimised Windows terminal holding `wsl.exe -d Ubuntu -- sleep infinity`.
5. **Windows must not sleep, hibernate or restart.** Check the power plan's sleep setting on mains
   power and any pending Windows Update restart. This is a managed Enterprise machine, so a policy may
   override the user setting: record what was found in the board block. Leave the machine plugged in
   and signed in. Locking the screen is fine; signing out ends WSL.
6. **Board.** The block's `Holds:` names 22 CPUs until the unit ends, and the expected finish time.

**While it runs**, `progress.json` is the one place to look.

**The morning after**, a new session reads `progress.json` and the log first.
- If the unit died, it reruns the identical command (completed keys are skipped) and says in the
  status line what was lost and why.
- If it finished, it goes on to Gate 3.

The unattended run commits and pushes nothing itself. Commits pass through hooks and the board guard,
which need a session.

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
  side's larger budget; the secondary's threshold carried from seed 0 to all five seeds; the budget
  anchored to one reference detector with a margin of 1.6; any Gate 1 difference from the Mac.
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
- **`/tmp` and session scratchpads are not durable.** `/tmp` can be cleared when the distribution
  restarts, and a scratchpad belongs to the session that made it. Every output of this run goes under
  `~/runs/`.
- **The Mac's reference rows came from uncommitted working trees.** A Gate 1 mismatch can be those
  changes, not floats; say which is known and which is not.
- **Do not change `tools/fair_bakeoff.py`'s default behaviour.** Its transfer test
  (`tests/test_fair_bakeoff_transfer.py`) checks that the default path is unchanged.
- **Push every completed stage promptly.** Push the branch `tune-learned-vs-coact` after Gate 1, after
  the tool passes `--quick`, and when the run finishes. If you stop mid-run, push a `wip/` branch and
  update this file with where it stopped.

## Where to put the result

Open a PR from `tune-learned-vs-coact` against `eval-field-size-candidates` while #596 is open, or
against `main` once #596 has merged. Do not set auto-merge on a PR whose base is another session's
branch. Update this handoff's status line below in the same PR.

**Status:** not started. **Reviewed by the workstation session on 2026-09-16** (nothing changed or
claimed there). Its five corrections are folded in above: the inner-fit cache keyed by sorted
recordings, the exact configuration draw, the edge check limited to axes of three values or more, what
a refit trains on (corrected again against the code: 10 of 16 recordings, alternating with the seed's
parity, not "the extra six feed the threshold"), and `chorus_gain_norm` in Gate 1. Its budget and job
count are adopted. **Setup step 3 decided (2026-09-16): WSL2.** Ubuntu 26.04, Python 3.14.4, torch
2.14.0+cpu, 24 physical / 48 logical CPUs, WSL memory 96 GB. The clone is at `~/bugarach`, not
`~/Developer/bugarach`. Its venv lacks `pyspike` (no `python3-dev` to build it), which CI tolerates the
same way; nothing under `src/` imports it. `darkroom()` finds the darkroom without `BUGARACH_DARKROOM`.
**In progress:** board claimed, worktree `tune-learned-vs-coact` created, `main` (#597) merged at
`259d717`. **2026-09-16: Tony's decisions are written in** (the list at the top: scripted run, Gate 1 at
`7fc052d` with no exemptions, the tip's grids, option D, comparison only, unattended overnight). The
budget margin is 1.6 until the run starts.
**Gate 1 step 1 done** ([`docs/learned/tuned_vs_coact/gate1/README.md`](docs/learned/tuned_vs_coact/gate1/README.md)):
the six hand-written detectors match the Mac exactly. `tube` at `7fc052d` differs from the Mac per fold
by −0.0034, −0.0212, −0.0053 and +0.0069 F1, and is deterministic on this machine. The committed
training code is identical between `239f176` and `7fc052d`. The Mac recorded neither its torch version
nor its uncommitted changes, so CPU float differences cannot be separated from those changes. **Tony
ruled the `tube` miss a training difference between machines, not a defect**, and the Gate 1 wording
now keeps the hard stop for the six only. `tube` fits take about 1.4 times the Mac's.
**Gate 1 step 2 done:** at the tip, `tube` is identical to step 1; CoactDetect, LoCo and SPIKE-synch are
still exact against the Mac; locust, rate+context and binned SCE differ, each for a known change (#593,
#594, #597's added grid values). **Gate 1 step 3 STOPPED on `chorus_gain_norm`:** folds 0 and 1 (0.6703
and 0.6975 F1) are further from both Mac seeds than the Mac's own largest seed-to-seed gap (0.0316 F1).
It picked the Mac seed 0's threshold on all 4 folds, so the weights differ, not the operating point; the
committed code on its path is unchanged since the Mac's commits; it is not the failed-training signature.
Not known: whether it is deterministic here, or one unlucky draw. `chorus_norm` is inside the stop;
`line_length` did not run. Provisional training estimate, from this machine's lone fits: 65 CPU hours,
about 3 hours of wall time at 22 jobs, a floor that ignores the larger configurations' cost per step.
**Decision 7: CoactDetect and LoCo slide.** `sliding-loco-coact` merged at `425ab2e`; 118 of 120
selected tests pass, and the 2 failures are that branch's known precision-swing budget breaks at the
binned-tuned values. **Gate 1 step 2 redone on the sliding code** (`2c58092`): locust, rate+context,
binned SCE, SPIKE-synch and `tube` equal the binned step 2 exactly; sliding CoactDetect and LoCo are
deterministic and score mean F1 0.681 and 0.687 (binned 0.645 and 0.653), calibrating in 0.46 and 0.28
times binned's time. Untuned, against sliding CoactDetect, `chorus_norm` leads by +0.061 F1 and
`chorus_gain_norm` by +0.020 on this machine.
**The `chorus_gain_norm` stop, rerun** (Tony: *"do it"*): seed 0 again is identical, so it is
deterministic; seed 1 passes the stop on every fold; this machine's seeds differ per fold by up to 0.0779
F1 against the Mac's 0.0316, and seed-averaged the machines agree within 0.007 F1 (0.7226 here, 0.7296
on the Mac). Seed 0 was a low draw, not a defect. Seed-averaged, `chorus_gain_norm` leads sliding
CoactDetect by +0.041 F1. ⚠ **Flagged for the design, not decided:** one seed moves `chorus_gain_norm` by
up to 0.078 F1 on a fold, likely more than many configurations differ, and this plan tunes at seed 0 only.
All of it: [`docs/learned/tuned_vs_coact/gate1/README.md`](docs/learned/tuned_vs_coact/gate1/README.md).
**Stop lifted** (Tony: *"go for it"*). **`line_length` passes step 3** (every fold within 0.022 F1 of a
Mac seed) but trains at 204.0 s per fit against the Mac's 62.4 s, 3.3 times, unexplained; the others run
1.25 to 1.4 times. **Gate 1 is complete.** Training floor from this machine's lone fits: 80.9 CPU hours,
3.7 hours at 22 jobs, with one seed per configuration; 6.3 hours with two; 8.9 hours with three.
At one seed, seed noise alone puts about 0.04 F1 (two standard deviations) between two configurations'
inner scores; at two, 0.030; at three, 0.024. **Decision 8: three seeds, no 9-hour cutoff.**
**Gate 2 done** (`59704eb`): `tools/tune_learned_vs_coact.py` and its test (10 checks, about 25 s),
`--quick` end to end and resumed with nothing rerun. Storage follows Tony's rule via the Mac unsupervised
session (configs/, fits/, scores/, selections/, chosen/, all keyed by `learn.checkpoint.config_key`),
on PR #602's branch merged early at `36dc5ab` (recorded in `meta.json`; merge `main` once #602 lands).
**Event spacing checked:** the home spec plants events at least 171 s apart (`min_sep_sec`), so a 240 s
LoCo context spans more than one spacing; `meta.json` records it and a chosen 240 s is flagged in the
readout. **Pre-launch, checked 2026-09-16 ~22:00:** Windows never sleeps or hibernates on mains, no
battery, no restart pending, automatic updates off by policy (a managed machine, so IT could still
force one); WSL 2.7.14 with systemd running, user lingering off, no idle timeout set; `sudo` needs
Tony's password. **Estimate for the declared draw:** a training floor of 200.7 CPU hours, 9.1 hours at
22 jobs, before the larger configurations' extra cost per step (18 to 22 of each model's 24 are larger
than untuned), 1,979 jobs before the outer refits the selections add.
**LAUNCHED 2026-09-16 21:52 EDT** at the commit that adds this paragraph (`meta.json` records its sha), 22
jobs, budget margin 1.6, into `~/runs/tune-learned-vs-coact/`. Floor finish about 07:30; likely later,
by the larger configurations' cost. **How it is detached (Tony's choice over a systemd unit, since sudo
needs his password):** a hidden Windows-side `wsl.exe -d Ubuntu -- bash -l
~/runs/tune-learned-vs-coact-launch.sh`, started with `Start-Process`. It survives closing VS Code,
terminals and the session, and that client keeps WSL from idling out; it stops on sign-out or a Windows
restart. **Idle proof on the real run (Tony's choice):** with every VS Code window and Ubuntu terminal
closed, `\\wsl$\Ubuntu\home\defazio\runs\tune-learned-vs-coact\progress.json` should show a recent `at`.
**The run executes from this worktree: do not change `tools/` or `src/` here until it ends** (a restart
would load them, and `meta.json` refuses a changed declaration). **If the run stopped:** read `run.log`
and `progress.json`, then start the launch script the same way
again; finished jobs are skipped. Say in this line what was lost and why. **When it finishes:** Gate 3.
Copy `meta.json`, `configs/`, `selections/`, `chosen/` and `results.json` into
`docs/learned/tuned_vs_coact/`; claim a darkroom folder on `docs/SESSIONS.md` (a PR off `main`) and put
`fits/` and `scores/` there, not in git.
⚠ **Found in the first minute, for Tony: the reference detectors' grids do not bracket their optimum.**
The hand-written grids finished at 21:53 (171 configurations, no errors). In all four outer folds and
both selections, CoactDetect chooses the grid's edge on every axis: `alpha` 1e-7 (1e-6 in fold 1),
`int_win_sec` 1.0, `context_win_sec` 120; LoCo chooses `context_win_sec` 240 in every fold. By the
project's edge rule the search stopped while still climbing, so tuned CoactDetect and LoCo are
under-tuned, which favours the learned models and undercuts the reason the hand-written side got the
larger budget. **This does not touch the learned run:** its budget is anchored to *shipped*
CoactDetect, not tuned. The hand-written grids take seconds, so a widened, separately declared grid can
be run in the morning into its own folder without disturbing anything. Not done, because it changes
the declaration: Tony's call. The 240 s context caution above (the home spec's 171 s spacing) applies to
any wider context too.
**The wider grid, run 22:15-22:21 on Tony's word** (*"run the wider grid when you can"*): branch
`tune-wider-reference-grid` (`314a887`, `--hand-grid wide`, declared before its first result; one
widening round), into `~/runs/tune-wider-reference-grid/`, 600 configurations, no errors, budgets
identical to the overnight run's. **No choice sits at an edge any more.** CoactDetect chooses one
configuration in all four folds and both selections: `alpha` 1e-7 (grid now to 1e-12), window 1.0 s (now
from 0.25 s), context 240 s (now to 960 s). LoCo's choices are unchanged: 480 s and 960 s did not win, so
240 s is interior. Held-out F1, mean over the four folds (sliding, 18 training recordings choose, 6
held-out score):

| reference | CoactDetect, ungated / gated | LoCo, ungated / gated |
|---|---|---|
| shipped, untuned | 0.6672 | — |
| declared grid | 0.7124 / 0.7124 | 0.6924 / 0.7028 |
| wider grid | **0.7225 / 0.7225** | 0.6924 / 0.7028 |

**For Gate 3, not decided:** the wider grid is the reference that brackets its optimum, so it is the
fair one to compare the learned models against; the declared grid's numbers stay in the record beside
it. Both chosen contexts are 240 s against the home spec's 171 s minimum event spacing, which the
full-search run found to favour bench recordings over crowded ones.
`tools/compare_bakeoff_runs.py` needs a test before #596's branch merges.
⚠ PR #596 was still open with CI running; if review changes a model's code, results tuned against an
older commit go stale, which the commit recorded in `meta.json` makes visible.
