# Handoff: build the slow-stream bench on WSMIP064, then search and train on it

> ⚠ **This file covers the slow-stream bench alone.** The other root handoffs are other
> threads and are NOT superseded by it. Delete only your own file.

**Written 2026-09-21 by a WSMIP065 session, for a fresh session on WSMIP064** that Tony
starts and drives over Remote Control. `main` is where you start.

> **Not murderboarded** — working material for a session in this tree. Nothing here is for
> an outside reader.

**No counts retyped where a command can derive them.** Every figure below that came from a
file says which file.

---

## The job, in one paragraph

Everything the detectors were tuned and trained on this weekend is a synthetic recording
whose structure was measured on the **fast** stream (`bench.MEASURED_STREAM = "fast"`). The
slow stream has never had its own bench, so every slow result so far runs on settings tuned
for fast. Tony, 2026-09-21: build the synthetic set from the **slow** stream, then run the
optimization and the training on it — the same pipeline as the weekend, second stream.

## Before you touch anything

1. **Read** `docs/FOUNDATIONS.md` (§7 and §9 in particular), `docs/GLOSSARY.md`, and
   [`docs/goals/learned-model-family.md`](docs/goals/learned-model-family.md) and
   [`docs/goals/coded-detector-optimization.md`](docs/goals/coded-detector-optimization.md)
   — the fast-stream versions of exactly this work.
2. **Confirm the default dataset with Tony.** `dataset.default()` refuses inside a Claude
   session until he has (merged 2026-09-21, #692). Ask:
   *"Default dataset: 2026-09-17_revised_2v_long_STEPS_AND_PINS_EXCLUDED — confirm?"*, and
   on his yes run `python -m bugarach.dataset confirm`. Never run it on his behalf.
3. **Check WSMIP064's own board** (`../bugarach-worktrees/SESSIONS.md` on that machine) and
   `docs/SESSIONS.md`. On the morning of 2026-09-21 WSMIP064 was dispatched the
   crowded-allowance sensitivity sweep (`HANDOFF-goal-2-comparison.md`); if that is still
   running it holds the cores, and the GPU training in step 5 below waits for it.
4. **Claim** a block on WSMIP064's local board before your first write, with a `Touches:`
   line. `bench.py` is contested — see "Coordination".

## Rulings that are already made — do not reopen them

- **The slow event's duration is the producer's, and it is not our business.** The slow
  stream's `width_sec` arrives under `width_def = rise_interval_peak_minus_t50rise`. That is
  the duration locust reads, as it comes. It is a truncation the producer applies on export
  on purpose: true slow events are long enough that locust fails miserably on them (Tony,
  2026-09-21, after this session asked and should not have). FOUNDATIONS §7: *"If you find
  yourself asking which duration locust should use, the answer is the column."*
- **The input is the default export folder**, `2026-09-17_revised_2v_long_STEPS_AND_PINS_EXCLUDED`
  (field steps and moco-pinned windows removed). No `.mat` store, no archive role.
- **The bench's participation moves 0.18 → 0.19 after the 2026-09-22 meeting** — a fast
  change, filed as `docs/todo/2026-09-21-bench-participation-to-0-19-after-the-meeting.md`.
  The slow bench measures its own participation fresh, so it is not blocked by that; but
  the two overnight reruns (fast with 0.19, slow from scratch) should be scheduled together.
- **Test names for anything a person reads** (glossary, 2026-09-21): *elevated-rate test*
  (was promiscuity probe), *no-coordination test* (was empty recording), *close-events test*
  (was crowded veto). *Quiet* and *busy* name the two backgrounds, never a test. The
  detector keyed `cicada` is **locust** on any page.
- **A coordinated event's width and amplitude** have one definition for every detector:
  width = earliest to last onset in it, amplitude = cells ÷ width
  (`src/bugarach/call_measure.py`, PR #698). Not a detector's own `width_sec`.

## The steps

| # | step | tools | notes |
|---|---|---|---|
| 1 | **Measure the slow stream's structure** on the default folder's baseline windows: per-ROI rate at p25 / p75 (the quiet and busy backgrounds), timing jitter, participation, ROI count, rate and burst shapes, the width distribution (from the producer's column, as it comes), and how crowded the most crowded real recordings get | `tools/remeasure_bench.py` (reads `bench.MEASURED_STREAM`, so it needs a `--stream` option); `tools/fit_background_shape.py --folder`; `tools/probe_real_crowding.py` | The fast `--folder` dry run for `remeasure_bench.py` sits **uncommitted** in WSMIP065's `opt-assess-revised-export` worktree; it is not on `main`. Fast took about 1.5 min on 84 recordings |
| 2 | **Build `src/bugarach/bench_slow.py` — do NOT edit `bench.py`.** Tony, 2026-09-21: *"we don't have time to rebuild bench.py to handle more than one stream."* The slow module carries the slow constants **under the same names** `bench.py` uses (`BENCH_RECORDING`, `REGIMES`, `NULL_RECORDING`, `CROWDED_RECORDING`, `TAIL_RECORDING`, `STREAM`, `MAX_PROBE_PER_MIN`, `MAX_FALSE_POSITIVES_PER_HOUR`, `MAX_PRECISION_DROP`, `FULL_GRIDS`, the `MEASURED_*` values, a slow width distribution) and **its own copies of the functions that read them**: `make_recording`, `make_tail_recording`, `make_crowded_recording`, `make_null_recording`, `false_positives_per_hour`, `run_detector`, `evaluate`, `sweep`, `pick_operating_point` (and `evaluate_curve` / `evaluate_background_curve` if you need them). What reads no module constant — `pool_scores`, the scoring — is imported from `bench.py` and shared. The tools that take a bench get `--bench fast\|slow` and load the module by name | NEW `src/bugarach/bench_slow.py`; NEW `tests/test_bench_slow.py`; `--bench` in `tools/search_all_settings.py`, `tools/remeasure_bench.py`, the tuning tool, `tools/leaderboard.py` | ⚠ **The trap: re-exporting a `bench.py` function that reads a module constant scores FAST recordings under a slow label, silently.** `evaluate` → `make_recording` → `bench.BENCH_RECORDING`; `false_positives_per_hour` → `make_null_recording` → `bench.NULL_RECORDING`; `pick_operating_point` reads `bench.MAX_PROBE_PER_MIN`. (`run_detector` reads `bench.STREAM`, which is only the simulated stream's name, `"events"` — shareable as long as the slow module keeps that name.) So the test must fail if any of those names in `bench_slow` **is** the `bench` object — and must build one slow recording and assert its rates are the slow ones. `bench.py` stays byte-identical: that is also what keeps this clear of the two WSMIP065 claims. Half a day. Folding the two back into one stream-aware `bench.py` is a separate, high-priority todo for after the 2026-09-22 meeting (`docs/todo/2026-09-21-one-stream-aware-bench.md`) — not this job |
| 3 | **Widen the search grids for slow timing.** Slow events are roughly five times slower, so windows, merge gaps and context lengths sized for fast will put slow optima at the grid edge | `bench.FULL_GRIDS`, `tools/search_all_settings.py` | The search refuses an optimum at a grid edge (`EdgeOfRange`) — treat that as the grid being too small, never as a result |
| 4 | **Every-knob search on the slow bench**, with the close-events test applied inside the search as goal 1 does | `tools/search_all_settings.py` | 10–13 min per run on the fast bench (five runs, 2026-09-17); expect a few runs |
| 5 | **Train the nets and run the fair comparison on the slow bench**, then a replicate | `tools/tune_learned_vs_coact.py` — ⚠ **on branch `tune-bench-comparison` only (PR #642, open), not on `main`** | The fast run launched 2026-09-18 16:14 here on WSMIP064 and took about 14 h (training floor 11.7 GPU-hours, `meta.json`). The replicate took 857 min on WSMIP065. They can run on the two machines in parallel |
| 6 | **Leaderboard** from the new run files | `tools/leaderboard.py` (reads the fast run's folder today; a slow run needs its own folder and a way to point the tool at it) | Nothing on the page is retyped — keep it that way |

**Nets' input timing.** The nets decode with a merge gap sized for fast — `decode`'s default
of 20 frames in `learn/encode.py`, which `pick_threshold` (`learn/train.py`) uses. Check that
it is not splitting or truncating slow events before reading any slow net result.

## Coordination

- **`bench.py` and `remeasure_bench.py` are claimed on WSMIP065** by `opt-min-baseline` and
  `opt-assess-revised-export` (WSMIP065's local board, 2026-09-21). Step 2 is built so it
  does not touch `bench.py` at all. It does add `--bench` to `remeasure_bench.py`, whose
  `--folder` change sits uncommitted in the second of those worktrees — ask Tony before
  editing that file, or add the slow measurement as its own small tool.
- **Darkroom writes** go under `<darkroom>/bugarach/`, claimed on `docs/SESSIONS.md` first
  (the darkroom is shared across machines). Use `python3 tools/show.py <file> --project bugarach`
  for anything you show Tony — the bare form writes to the darkroom root.
- **Every run goes to Dropbox and the repo when it finishes** (Tony, 2026-09-21: *"ensure that
  future runs go straight to repo and dropbox. crazy"*, after this weekend's chosen models turned up
  on one disk). Schedule the status mirror with `--archive-as <dated-name>` and raise the task's
  time limit to 60 minutes (`docs/windows_workstation_setup.md` §8, PR #703); then put the run in
  the repo with `tools/archive_run.py <run> --name <name> --to-repo` and a PR. Check
  `python3 tools/archive_run.py --pending` on WSMIP064 before starting: this weekend's
  fair-comparison run there has no `ARCHIVED.json` yet (its copies exist — Dropbox
  `2026-09-18-fair-comparison-run/results/` and the repo, #702 — so write the marker pointing
  at them, as WSMIP065 did for its replicate, rather than copying again).
- **A long run in a desktop session dies with a sign-out** (armory `FINDINGS.md` §20);
  WSMIP064's runs went under `%USERPROFILE%\runs\` with a status mirror
  (`docs/windows_workstation_setup.md` §8).

## Done means

- A slow bench whose every structural value is measured on the default folder's slow
  baselines, recorded like `docs/learned/bench_measured.json` and stamped with
  `dataset.stamp()`, and a test that fails when the two disagree.
- Slow settings for the six coded detectors from the every-knob search, with the
  close-events test applied.
- The four nets trained and compared on the slow bench, with a replicate, and a leaderboard
  for the slow stream.
- This file moved to `docs/handoffs/` (or deleted if nothing in it is still worth reading),
  and the goal pages updated in the same PR as the result.
