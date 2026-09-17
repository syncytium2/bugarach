# HANDOFF: goal 1, every knob of the coded detectors, and what the tuning relaunch needs from it

**Written 2026-09-17 on WSMIP065**, at Tony's request: *"create a revised handoff file recognizing you
probably have context to handle a good chunk of it. prepare to relaunch the tuning run."* It
**supersedes** `HANDOFF-evaluate-sliding-detectors.md` on branch `full-search`. When that branch lands,
that file moves to `docs/handoffs/`.

> **Read [`docs/goals/README.md`](docs/goals/README.md), section *The current program*, first.** It
> holds Tony's three goals and five decisions of 2026-09-17. This file is goal 1's working plan and
> the list of what goals 2 and 3 need from it. Where this file and that section disagree, the section
> wins.
>
> **Working material, not murderboarded.** Every restated number links to the file that owns it.

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
| 2 | A fair comparison of the coded detectors against the nets | WSMIP064 | §4: what the relaunch needs from goal 1 |
| 3 | "Final" supervised-learning results on the current best simulation | WSMIP064 | §4 |

The binding decisions, in short (full text in the goals README):

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
| The search's results | `<darkroom>/bugarach/2026-09-16-full-search/`: `search.log`, `search.json`, Figures 1–4. The run finished 2026-09-16 at 17:02 in 11 minutes with an empty `search.err` | darkroom |
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

- **One declaration of the grids, on `main`, imported by both machines.** Put the every-knob grids
  in `bench` (for example `bench.FULL_GRIDS`) and have `search_all_settings.py` and WSMIP064's
  `tune_learned_vs_coact.py` both import it. Two copies of a grid are how the two machines came to
  tune different things on 2026-09-16.
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

### Step 5: run on the full slice, fast stream

The tuned six on every `steps_excluded` recording's full extent, fast stream, through the existing
folder path (`bugarach detect` / `detect_folder`). Real treatment rasters go to the darkroom only
(FOUNDATIONS §5). **Treatment effects are `fireflies`' to interpret, not this repo's** (FOUNDATIONS
§9). This step produces the calls; it does not claim what TTX or senktide does.

### Then: slow stream

Steps 1, 3, 4 and 5 again on the slow stream. Step 1 fits a slow-stream bench, which does not exist
yet.

## 4. What WSMIP064's relaunch needs from goal 1

WSMIP064's own plan is `HANDOFF-workstation-tuning.md` on `tune-learned-vs-coact`: the GPU
correctness check, merging the wider reference grid, then a Task Scheduler launch after its elevation
lapses. **Today's decisions change what that run declares.** Nothing below edits WSMIP064's branch. It
all arrives through `main`.

| the run as declared on `tune-learned-vs-coact` | as of 2026-09-17 | who |
|---|---|---|
| Simulation: `docs/learned/generator_spec.json` (32 ROIs, home spec) | **the bench's fitted field, re-derived in §3 step 1.** The tool reads a spec and calls `simulate_coordination(seed, **spec)`, and so does `bench.make_recording`, so the switch is a matter of spec, not simulator. Open for WSMIP064: how the two regimes split across the four folds, and what `_null_twin`'s quiet-field factor 0.54 means on the bench, where the quiet regime already is baseline's lower quartile | 065 supplies the bench; 064 redeclares |
| Reference detectors: CoactDetect and LoCo, three axes each (plus the wider grid) | **all six coded detectors, every knob**, from the one grid declaration on `main` (§3 step 3). Goal 2 says *the coded detectors*. The coded side's nested CV costs seconds per configuration on the CPU | 065 declares; 064 imports |
| Sliding CoactDetect and LoCo from `sliding-loco-coact` @ `005ae98` | the same code, **from `main`** once §3 step 4 lands | 065 |
| Shared FA budget anchored to shipped CoactDetect at binned-tuned values | anchored to a **declared, fixed** reference, preferably the landed every-knob values. The run records whichever it uses in `meta.json` | 064 decides; 065 lands the values |
| One stream (the home spec's) | **fast stream**, named in every table | both |
| The untuned table on the home spec (`chorus_norm` +0.103 F1 over CoactDetect, and so on) | **kept as the record**. It is not the comparison goal 2 reports | 064 |

**Order, so neither machine waits longer than it must:**

1. **065, today:** this file and the goals README on `main` (the decisions reach WSMIP064 when it
   fetches). Then §3 step 1 (the bench re-derivation), and the grid declaration from §3 step 3 as its
   own small PR, before the search runs.
2. **064, meanwhile:** the GPU correctness check it had planned needs none of this. Adapting the
   tool to a bench spec and to six imported grids can start once step 1's values are on `main`.
3. **065:** the every-knob search (§3 step 3), then landing (§3 step 4).
4. **064: relaunch** once the bench, the grids and sliding are all on `main`. Native Windows,
   GPU, Task Scheduler, not from an elevated session.

⚠ **For Tony, not decided here:** this order puts the relaunch after goal 1's search, a delay of
hours rather than days if step 1's values do not move. Relaunching sooner means comparing against
coded detectors tuned on a partial grid, which is the unfairness goal 2 exists to remove.

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
