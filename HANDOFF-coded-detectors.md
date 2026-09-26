# HANDOFF: goal 1, every knob of the coded detectors, and what the next comparison needs from it

**Written 2026-09-17 on WSMIP065**, at Tony's request: *"create a revised handoff file recognizing you
probably have context to handle a good chunk of it. prepare to relaunch the tuning run."* It
**supersedes** the sliding-detectors handoff, which is now
[`docs/handoffs/2026-09-17-evaluate-sliding-detectors.md`](docs/handoffs/2026-09-17-evaluate-sliding-detectors.md)
— `full-search` landed, so that file left the root on 2026-09-21 as this one said it would.

> **Read [`docs/goals/README.md`](docs/goals/README.md), section *The current program*, first.** It
> holds Tony's three goals and five decisions of 2026-09-17. This file is goal 1's working plan and
> the list of what goals 2 and 3 need from it. Where this file and that section disagree, the section
> wins.
>
> **Working material, not murderboarded, and not final.** Tony, 2026-09-17: *"none of this is final.
> we're still troubleshooting and figuring out what models/detectors to keep."* A detector in scope
> below may be dropped. Every restated number links to the file that owns it.

Abbreviations: **F1**, harmonic mean of recall and precision; **ROI**, region of interest (one imaged
cell); **FA**, false alarm; **CV**, cross-validation; **GPU**, graphics processor.

## 0. Status

**The WSMIP065 session that wrote this file is continuing with §3 steps 1–4.** A session that finds
this file with no newer status line picks up at the first step not marked done. Status lines go at the
bottom, newest last.

## 1. The three goals, and who does what

| # | goal | owner | this file's part |
|---|---|---|---|
| 1 | Full tuning of the coded detectors, every knob, all six | **WSMIP065** | all of §3 |
| 2 | A fair comparison of the coded detectors against the nets | WSMIP064 | §4: what the next comparison needs from goal 1 |
| 3 | "Final" supervised-learning results on the current best simulation | WSMIP064 | §4 |

The decisions, in short (full text in the goals README; they hold until Tony changes them):

- **Real data: only `dataset.current("steps_excluded")`**, 84 recordings. The senktide and TTX
  recordings are inside it. Never the declared `senktide` or `ttx` roles, the `.mat` stores, `default`
  or `pensub`.
- **Train on the baseline, run on the full slice.**
- **Simulation: the bench's fitted field** (`bench.BENCH_RECORDING`, regimes `baseline_quiet` and
  `baseline_busy`) for all three goals. The home spec `docs/learned/generator_spec.json` is retired for
  this program.
- **Fast stream first**, then slow.
- **Every knob** means every parameter except the data's own. `min_rois` and the merge gaps are
  included.

## 2. Where things stand

### What exists, on which branch

| what | where | on `main`? |
|---|---|---|
| Sliding LoCo and CoactDetect: counts in a trailing window, and a null computed exactly rather than drawn | `sliding-loco-coact` @ `005ae98`: `src/bugarach/detectors/sliding.py`, `window_mode="sliding"` in `coact.py` / `loco.py`, `docs/forks.md` §14 | no. CI is red at the binned-tuned values: sliding LoCo gives 4.0 calls per hour on the empty recording against a limit of 3, CoactDetect 7.7 against 7 |
| The search over every **declared** setting, and the sliding-vs-binned probe | `full-search` @ `75df220`: `tools/search_all_settings.py` (+ tests), `tools/probe_sliding_vs_binned.py` | no |
| The search's results | `<darkroom>/bugarach/archive/2026-09/2026-09-16-full-search/`: `search.log`, `search.json`, Figures 1–4. The run finished 2026-09-16 at 17:02 in 11 minutes with an empty `search.err` | darkroom |
| The nested tuning tool, now with GPU training | `tune-learned-vs-coact` @ `828cb80` (WSMIP064's): `tools/tune_learned_vs_coact.py`, `train(device=...)` | no |
| A wider reference grid for CoactDetect and LoCo | `tune-wider-reference-grid` @ `314a887` (WSMIP064's) | no |

### What the 2026-09-16 search found: corrected readings

The full table is in the superseded handoff. Four readings in it do not hold up:

1. **locust's 128-frame minimum distance ran out of search, not into an optimum.** The grid
   extended 16 → 32 → 64 → 128 frames, which is exactly `MAX_EXTENSIONS = 3`. The log says "best at
   the edge" at 16, 32 and 64 and **says nothing at 128**, so the cap stopped it silently while it was
   still climbing. A score that keeps rising as repeat calls are suppressed points to one planted
   event being split into several calls. That is the anchor question in
   [`docs/todo/2026-09-16-locust-anchor-and-the-panel-viewer.md`](docs/todo/2026-09-16-locust-anchor-and-the-panel-viewer.md),
   not a setting to ship until the anchor is settled.
2. **LoCo's 8 s merge gap is the top of its grid** (0.5 to 8 s), and every LoCo candidate the old
   handoff proposed uses it. On the crowded recordings, planted events come as little as 6 s apart, so
   an 8 s merge fuses neighbours. That may explain part of the crowded-recording loss the old
   handoff blamed on the 240 s context. **Merge gaps are window-shaped settings**, and the list in its
   §5 lacked them.
3. **CoactDetect at alpha 1e-5 with a 60 s context was measured** on the selection recordings (round 1
   of `search.log`: mean F1 0.710 → 0.715). What is missing is its held-out score and its rate on the
   empty recording.
4. **The tool's docstring says merge gaps are not searched**, yet LoCo's `merge_gap_sec` is in its
   `SPACE`.

WSMIP064 found the same edge problem on the nets' home spec: in its nested CV, CoactDetect chose the
end of every axis. Its wider grid then bracketed alpha 1e-7, window 1.0 s and context 240 s
(`HANDOFF-workstation-tuning.md` on `tune-learned-vs-coact`). **Both machines have now seen the
coded detectors' grids stop short. The every-knob search in §3 extends until each optimum is
bracketed, or refuses to report it.**

### What went wrong overnight, for the record

WSMIP064's tuning run was lost at 01:57 on 2026-09-17. The university's privilege manager signed the
user out about 12 hours after the elevation used to install WSL, and WSL has not started since.
Account: armory `FINDINGS.md` §20 and [`docs/windows_workstation_setup.md`](docs/windows_workstation_setup.md).
**Rules that follow for any long run on either workstation:** native Windows Python, never WSL;
started from Task Scheduler, never from an elevated session; resumable, with atomic result files;
outputs under `%USERPROFILE%\runs\`.

## 3. Goal 1: the plan, fast stream

Each step ends with a push, and a status line at the bottom of this file.

### Step 1: re-derive the bench from `steps_excluded`, fast stream, baseline windows only

**Why first:** decision 3 makes the bench the simulation for all three goals, and decision 1 allows no
other data. The bench's measured values are not yet from this folder:

| value in `src/bugarach/bench.py` | where it came from | re-derive as |
|---|---|---|
| `MEASURED_RATE_SHAPE` 0.275 (81 baseline windows, 2,643 ROIs) | `tools/fit_background_shape.py`, reading `processed_archive/event_store_onset_revised_2v` (a closed store) | the same estimator over `steps_excluded` baseline windows, fast stream |
| `MEASURED_BURST_SHAPE` (1.547, 1.388) at bins of 300 s and 60 s | same tool, same store | same |
| `n_roi`, `jitter_sec`, `participation` and the background rate, via `MEASURED_PROVENANCE` | a MATLAB summary (`constellation/coordination_timescale_summary.csv`, 84 slices) | measured from the folder, or stated as a producer's measurement of this same folder if that is what it turns out to be |
| `REGIMES` 0.0052 and 0.0190 Hz per ROI (baseline interquartile range) | re-derived 2026-08-20 from the export folder current then (FOUNDATIONS §9) | the interquartile range over `steps_excluded` baselines, fast stream |

`tools/fit_background_shape.py` reads the store through `BUGARACH_DATA_ROOT`: migration debt that
CLAUDE.md names. Point it at `dataset.current("steps_excluded")`. It already handles folder input
(`stream_name`); pin the stream to `fast`.

**Deliverable:** a table of old against re-derived values. If they agree within the fit's own
uncertainty, change the provenance strings only. If they move, the bench moves, every bench number
before it is superseded, and **Tony hears it before anything is retuned on it**. The 2026-08-28 bench
revision set that precedent.

**And make it impossible to miss again** (Tony, 2026-09-17: *"not sure how to keep an eye on
that"*). Prose did not catch it. Record the source folder beside each measured value (for example a
`MEASURED_FOLDER` constant naming `2026-09-03_revised_2v_long_STEPS_EXCLUDED`), and add a test that
fails when that name differs from what `current_export.toml` declares for `steps_excluded`. Then a
new export, or a value fitted anywhere else, turns the suite red instead of passing silently. Also
make `fit_background_shape.py` refuse any input but `dataset.current("steps_excluded")`.

⚠ The field-step exclusion removed 381 events in 9 recordings. Report how many fell in baseline
windows, so any shift in the fitted values can be attributed.

### Step 2: reproduce the sliding detectors, then compare them with binned on real recordings

1. On `full-search`: `pytest tests/test_sliding_window.py tests/test_loco_detect.py
   tests/test_coact_detect.py tests/test_search_all_settings.py`, then
   `python tools/probe_sliding_vs_binned.py`. Both should match the superseded handoff's §1: 100% of
   calls kept at every shift, at 0.25–0.75 times binned's time per recording.
2. **Sliding against binned on `steps_excluded`, fast stream, baseline windows** (train on baseline).
   For each recording: calls in each mode and how many coincide. There is no answer key, so a large
   disagreement is a finding to explain before landing. Real rasters stay in the darkroom
   (FOUNDATIONS §5). Claim a folder on `docs/SESSIONS.md` first.

### Step 3: the every-knob search

**The inventory.** Every parameter each detector accepts on `main`, read from the signatures on
2026-09-17. **Data's own, never searched:** the events and time range (`trains`, `s`, `t_range`),
`grid_dt` and `imaging_rate_hz` (the frame interval, FOUNDATIONS §6), `onset_field` and
`duration_field` (column names), `rng_seed`, `emit_signal`.

| detector (code key) | searched: every other parameter |
|---|---|
| CoactDetect (`coact`) | `int_win_sec`, `context_win_sec`, `alpha`, `min_rois`, `merge_gap_sec`, `guard_sec`, `guard_norm`, `detection_mode`, `peak_prominence`, `peak_min_distance_sec`; `window_mode` fixed at `sliding` |
| LoCo (`loco`) | `bin_width_sec`, `context_win_sec`, `threshold_pctile`, `min_rois`, `merge_gap_sec`, `null_context_mode`, `guard_sec`, `detection_mode`, `peak_prominence`, `peak_min_distance_sec`; `window_mode` fixed at `sliding` |
| rate+context (`rate`) | `excess_threshold_hz`, `rate_win`, `context_win`, `merge_gap_s`, `threshold_mode`, `threshold_alpha`, `guard_sec`, `detection_mode`, `peak_prominence`, `peak_min_distance_sec` |
| binned SCE (`sce`) | `analysis_mode`, `bin_width_sec`, `threshold_pctile`, `surrogate_model`, `min_rois`, `merge_gap_sec`, `detection_mode`, `peak_prominence`, `peak_min_distance_sec` |
| SPIKE-synch (`sync`) | `tau_max`, `max_gap`, `tau_mode`, `C_threshold`, `C_min`, `min_n`, `dt` (the profile's bin width, **not** the frame interval: FOUNDATIONS §6), `synchrony_statistic`, `artifact_threshold`, `artifact_threshold_fraction`, `artifact_threshold_plat90`, `detection_mode`, `peak_prominence`, `peak_min_distance_sec` |
| locust (`cicada`) | `sce_percentile`, `n_synchronous_frames`, `sce_min_distance_frames`, `threshold_scope` |

**Readings of "every knob" that are this file's, not Tony's. Ask before the search runs:**

- **The region rules are treated as the data's own and not searched**: `solution_delay_sec`,
  `baseline_window_max_sec`, `treatment_window_sec`, `region_min_sec`, `clamp_context_to_region`
  (LoCo, binned SCE, locust). FOUNDATIONS §4 says an export folder's `regions.csv` is used verbatim,
  and "run on the full slice" reads the whole extent.
- **Surrogate counts (`n_surrogates`) are set for convergence, not tuned for F1.** A count is a
  precision-for-compute trade. The search checks that the chosen setting's calls do not change at
  twice the count. Sliding LoCo and CoactDetect ignore it, and `thr_step_sec` with it.
- **locust's `active_duration_mode` stays `per_event`**, and `active_duration_sec` goes with it.
  FOUNDATIONS §7: *"If you find yourself asking which duration locust should use, the answer is the
  column."*

**How to search**, reusing `tools/search_all_settings.py` rather than writing a new tool:

- **One declaration of the grids, on `main`, imported by both machines.** ✅ Landed 2026-09-17:
  `bench.FULL_GRIDS` (per axis, never a product), `bench.FULL_GRID_PAIRS` and
  `bench.settings_are_valid`, read by `search_all_settings.py` here and by
  `tune_learned_vs_coact.py` on WSMIP064. Two copies of a grid are how the two machines came to
  tune different things on 2026-09-16. **The axes are still the declared settings**; widening them
  to the inventory above is the rest of this step, and the shape callers bind to does not change.
  **Goal 2 searches them per outer fold** through
  `search_all_settings.choose_settings(detector, *, score, admissible=None, …)`, a callable over
  the caller's own callbacks — it never sees a recording, a budget or a pooling rule, so nothing
  about a configuration can be chosen with the fold it is scored on. Inside a fold the declared
  grid stays fixed and an edge is returned as data; goal 1's own search keeps extending until the
  optimum is bracketed. The decision and its options:
  [`docs/todo/2026-09-17-how-is-the-coded-side-searched-inside-nested-cross-validation.md`](docs/todo/2026-09-17-how-is-the-coded-side-searched-inside-nested-cross-validation.md).
  ⚠ **WSMIP064 asks, before these grids are declared** (2026-09-17; its session cannot reach this
  machine directly, so the question travels through `main`): the grids are a **coordinate search's**,
  and goal 2 scores the coded side under **nested cross-validation**, where every candidate is scored
  on each outer fold's training recordings. Every knob as a product is not runnable, and
  `tune_learned_vs_coact.py` refuses a product over 5,000 configurations rather than guess. Three
  options, and 064's recommendation (run this search inside each outer fold), are in
  [`docs/todo/2026-09-17-how-is-the-coded-side-searched-inside-nested-cross-validation.md`](docs/todo/2026-09-17-how-is-the-coded-side-searched-inside-nested-cross-validation.md).
  **Deciding after the grids are declared means declaring them twice.**
- **Replace the silent extension cap.** An optimum still at an edge after the last extension is
  reported as `EdgeOfRange`, the bench's own refusal, and never written as a result.
- **Categorical settings** (`detection_mode`, `guard_norm`, `null_context_mode`, `threshold_mode`,
  `analysis_mode`, `surrogate_model`, `tau_mode`, `synchrony_statistic`, `threshold_scope`) are
  searched as coordinate moves like any other. Where one value switches a group of settings on
  (peak mode's prominence and distance), search that group only under it.
- **Keep the discipline the 2026-09-16 run had:** choose on recordings 1–48, score on 49–96,
  a 95% bootstrap interval on the gain, all three budgets in `bench.py`
  (`MAX_PROBE_PER_MIN`, `MAX_FALSE_POSITIVES_PER_HOUR`, and `MAX_PRECISION_DROP`, which reaches
  `bench.py` only on `sliding-loco-coact`), and the crowded
  recordings (`bench.make_tail_recording`) as a check that never selects. **Window-shaped
  settings** (every `*_win*`, `bin_width_sec`, `context*`, merge gaps, minimum distances, `tau_max`,
  `max_gap`) are the ones the bench's spacing can flatter. A winner among them that loses on the
  crowded recordings is not taken.
- **`min_rois` carries its warning into every table:** it can learn the bench's planted participation
  (30 / 18 / 10% of 33 ROIs).
- **Before trusting the result, look for a fourth budget that lives only in a test** (superseded
  handoff §5: three were found that way in one week).
- Run it as a resumable job from Task Scheduler if it outlasts the session (§2, *what went wrong*).

### Step 4: choose, land, and hand over

1. Set the chosen values in `OPERATING_POINTS` on `sliding-loco-coact` (merged with `full-search`),
   each with its `source` string, and get CI green. **Decisions stay Tony's** where the goal page lists
   them: binned SCE 98 against 75, rate+context 4.5 Hz, and locust's anchor.
2. Land it. The reason given for holding it off `main` no longer applies: WSMIP064's run already
   used this sliding code. What matters to that run is the *values*, and §4 handles those.
3. Update [`docs/goals/coded-detector-optimization.md`](docs/goals/coded-detector-optimization.md) in
   the same PR, and remove its ⚠ branch-only markers for what landed.
4. The browser's `loco.js` and `coact.js` are still binned. They are owed a port once sliding is on
   `main`.

### Step 5: run on the full slice, fast stream — ⚠ HELD

**Tony, 2026-09-17: *"for this training run use only baseline."*** This step does not run yet, and
nothing in the current program scores a treatment window. It stays written down because it is what
the program is aimed at, not because it is next.

When the hold lifts: the tuned six on every `steps_excluded` recording's full extent, fast stream,
through the existing folder path (`bugarach detect` / `detect_folder`). Real treatment rasters go to
the darkroom only (FOUNDATIONS §5). **Treatment effects are `fireflies`' to interpret, not this
repo's** (FOUNDATIONS §9). This step produces the calls; it does not claim what TTX or senktide does.

### Then: slow stream

Steps 1, 3, 4 and 5 again on the slow stream. Step 1 fits a slow-stream bench, which does not exist
yet.

## 4. What WSMIP064's next comparison needs from goal 1

**WSMIP064's tuning run is running again as of 2026-09-17** (Tony), as declared on
`tune-learned-vs-coact` (`HANDOFF-workstation-tuning.md` there). **It is not stopped or changed by
anything here.** It is exploratory, like everything in this program. The table below is what differs
for the *next* comparison, once goal 1 has delivered and Tony has decided which models and detectors
to keep. Nothing below edits WSMIP064's branch. It all arrives through `main`.

| the run as declared on `tune-learned-vs-coact` | the next comparison | who |
|---|---|---|
| Simulation: `docs/learned/generator_spec.json` (32 ROIs, home spec) | **the bench's fitted field, re-derived in §3 step 1.** The tool reads a spec and calls `simulate_coordination(seed, **spec)`, and so does `bench.make_recording`, so the switch is a matter of spec, not simulator. Open for WSMIP064: how the two regimes split across the four folds, and what `_null_twin`'s quiet-field factor 0.54 means on the bench, where the quiet regime already is baseline's lower quartile | 065 supplies the bench; 064 redeclares |
| Reference detectors: CoactDetect and LoCo, three axes each (plus the wider grid) | **all six coded detectors, every knob**, from the one grid declaration on `main` (§3 step 3). Goal 2 says *the coded detectors*. The coded side's nested CV costs seconds per configuration on the CPU | 065 declares; 064 imports |
| Sliding CoactDetect and LoCo from `sliding-loco-coact` @ `005ae98` | the same code, **from `main`** once §3 step 4 lands | 065 |
| Shared FA budget anchored to shipped CoactDetect at binned-tuned values | anchored to a **declared, fixed** reference, preferably the landed every-knob values. The run records whichever it uses in `meta.json` | 064 decides; 065 lands the values |
| One stream (the home spec's) | **fast stream**, named in every table | both |
| The untuned table on the home spec (`chorus_norm` +0.103 F1 over CoactDetect, and so on) | **kept as the record**. It is not the comparison goal 2 reports | 064 |

**Order:**

1. **065, today:** this file and the goals README on `main` (the decisions reach WSMIP064 when it
   fetches). Then §3 step 1 (the bench re-derivation), and the grid declaration from §3 step 3 as its
   own small PR, before the search runs.
2. **064, meanwhile:** its current run continues untouched. Adapting the tool to a bench spec and to
   six imported grids can start once step 1's values are on `main`.
3. **065:** the every-knob search (§3 step 3), then landing (§3 step 4).
4. **064: the next comparison**, once the bench, the grids and sliding are all on `main`, with
   whatever models and detectors Tony keeps. Native Windows, GPU, Task Scheduler, not from an
   elevated session.

## 5. Traps already paid for

- **The grids stop short, on both machines.** Extend until bracketed, or refuse (§2).
- **Budgets that live only in a test cannot stop a calibration.** Three moved into `bench.py` in one
  day.
- **Quote held-out gains**, never the "chosen on" column.
- **Window-shaped settings are the ones the bench can flatter**; merge gaps and minimum distances are
  window-shaped too.
- **Never infer which machine you are on from its hardware.** WSMIP064 and WSMIP065 have the same GPU,
  core count and user name. The machine id comes from the hostname through armory's
  `session_identity.sh` (kept as `origin/interface2/tools/session_identity.sh` in armory), and the
  board's block headings carry it.
- **A long run in a desktop session dies with a sign-out** (armory `FINDINGS.md` §20).
- **Only `steps_excluded`.** A tool that defaults to `dataset.current()` with no role reads `default`,
  a different folder. Pass the role explicitly.

## Status

- 2026-09-17 11:20 (WSMIP065): written; decisions and goals README on `main` via this PR. Next: §3
  step 1.
- 2026-09-17 13:10 (WSMIP065): **§3 step 1 done, and the bench does not move.**
  `tools/remeasure_bench.py` measured all 8 of the bench's measured constants on `steps_excluded`,
  fast stream, baseline analysis windows (84 recordings; 80 in the shape fits), with 200 bootstrap
  draws. Seven sit inside their 95% intervals. **`participation` (0.18) sits 0.0018 below its
  interval (0.1818–0.2322; measured 0.1905)**, and 0.1818 is 6/33, the ratio the bench's docstring
  rounds to 0.18. It waits on Tony and is listed in `bench.MEASURED_OUTSIDE_INTERVAL`. Record:
  `docs/learned/bench_measured.json`. **The check:** `tests/test_bench_is_measured_on_the_declared_folder.py`
  fails when the pointer names a different folder than the one measured, when a measured constant is
  edited without re-measuring, or when a constant leaves its interval unacknowledged.
  `fit_background_shape.py` now reads the analysis window (it had been measuring the raw period), and
  it no longer passes a verdict at a fixed 5%. Next: §3 step 2.
- 2026-09-17 15:05 (WSMIP065): **§3 step 2 done. The two modes disagree only in ways forks.md §14
  predicts, so nothing here blocks landing sliding.**
  *Reproduced:* the 48 tests of the sliding branch pass, and `probe_sliding_vs_binned.py` (repointed
  from the TTX subset to `steps_excluded`) gives sliding 100% of calls kept at every shift of
  0.1–0.9 s against binned 41% for LoCo and 0% for CoactDetect at a 0.05 s match, in 0.23–0.41 times
  the time.
  *On real recordings* (`tools/compare_sliding_vs_binned.py`, 84 baseline analysis windows, fast
  stream): LoCo 598 → 923 calls, CoactDetect 436 → 583, at the **binned-tuned** settings. Sliding
  never calls fewer for LoCo (59 recordings call more) and calls fewer in 4 for CoactDetect. A median
  1.00 of binned calls are also made sliding (within 2.5 s), and 0.40 / 0.33 of sliding calls are new.
  **CoactDetect's shared onsets move a median +0.30 s** (median absolute 0.50 s) where LoCo's move
  0.00 s — the bin edge becoming the first participating event, which is the whole of why only half
  of CoactDetect's calls match at 0.5 s. Run, figures and note:
  `<darkroom>/bugarach/archive/2026-09/2026-09-17-sliding-vs-binned/`. Next: §3 step 3, the every-knob search.
- 2026-09-17 23:50 (WSMIP065): **§3 step 3 done for the sliding pair; step 4 is HELD.** The values
  are chosen, measured and bracketed, and both operating points are **still binned on `main`**:
  switching them moves the viewer's calibrated defaults while the browser runs both detectors
  binned, and moves the calls a slow-comodulation analysis is pinned to. The switch is committed on
  branch `opt-every-knob-run` and pushed, with the full suite's verdict in the darkroom. Held out on
  48 recordings the search never saw, against
  the binned points they replace: **LoCo** threshold 99.9, merge gap 8 s, symmetric null — mean F1
  0.737 against 0.699, 1.7 calls/hour on the empty recording (limit 3, was 4.0 and over), crowded
  0.827 against 0.816. **CoactDetect** alpha 1e-5, context 120 s, merge gap 8 s, guard 1 s — 0.746
  against 0.702, 5.8 calls/hour (limit 7, was 7.7 and over), crowded 0.818 against 0.808. Both merge
  gaps are bracketed: the axis was extended to 16 s and the crowded veto refused it.
  **Three things the search needed first, each found by failing.** (1) `bench.MAX_CROWDED_DROP`, a
  fourth budget: the first every-knob run gained 0.11–0.31 held-out F1 for four detectors by running
  merge gaps out to about a minute, and lost 0.25–0.32 on crowded recordings. The other three budgets
  cannot see it — merging makes a detector call LESS, so the artifact looks *cleaner* on every
  false-alarm measure. (2) The veto's reference is what a detector SHIPS at, not the sliding-forced
  start; anchored wrongly, sliding LoCo had no admissible setting at all. (3)
  `bench.context_fits_the_null`: a context wider than the planted spacing puts other events inside
  the null, the null sits high, the detector calls less and scores better — the search chose 240 s on
  a 120 s bench and `test_bench.py` refused it after the run. It is a validity rule in front now.
  **Also:** the search rescues an inadmissible starting point instead of reporting "nothing moved",
  and refuses to start when the shipped point is not measurable here. `TIE_F1` in
  `tests/test_background_curve.py` widened 0.01 → 0.02 against a measurement, not to fit a result: at
  12 seeds the new values leave no steady leader; at 36 seeds CoactDetect leads every grid point with
  deficit 0.000. Run: `<darkroom>/bugarach/archive/2026-09/2026-09-17-full-search/sliding5/`; the binned every-knob
  run and the artifact it exposed are in the parent folder.
  **Still open, measured and not landed:** locust's 128-frame minimum distance (+0.119 held-out,
  +0.149 crowded, but unbracketed at the extension ceiling and tangled with the anchor question);
  SPIKE-synch `min_n` 3 → 2 (+0.042 held-out, +0.051 crowded, admissible); rate+context merge gap
  3 → 8 s (+0.013 held-out, crowded −0.008). Next: land those three or say why not, then the
  browser's `loco.js` / `coact.js` port, which the sliding switch now owes.
