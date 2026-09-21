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
- **The slow measurement gets its own small tool; `tools/remeasure_bench.py` is not edited.**
  Tony, 2026-09-21, asked whether that tool should take `--bench fast|slow`, answered that the
  separate module exists *because* there was no time to expand what `bench.py` can do — and a
  stream flag threaded through the shared measurement tool is that same expansion in a second
  file. The tool is contested besides: claimed on WSMIP065, with an uncommitted `--folder`
  change in its `opt-assess-revised-export` worktree. So write `tools/measure_slow_bench.py`,
  **importing** `remeasure_bench`'s per-recording measurement and its `_values` summary rather
  than copying them, reading `bench_slow`'s constants and writing `bench_slow.MEASURED_RECORD`
  (`docs/learned/bench_measured_slow.json`), with a sibling of
  `tests/test_bench_is_measured_on_the_declared_folder.py` that pins the slow record's stream
  to `"slow"`. The duplication is a stopgap with a scheduled end:
  [`docs/todo/2026-09-21-one-stream-aware-bench.md`](docs/todo/2026-09-21-one-stream-aware-bench.md)
  turns every tool's `--bench` into a profile selector and deletes both the module and this
  tool's reason to exist. The tools nobody has claimed — `tools/search_all_settings.py`,
  `tools/leaderboard.py` — still take `--bench fast|slow` as step 2 says: choosing a module is
  a selector, not a rebuild.
- **Test names for anything a person reads** (glossary, 2026-09-21): *elevated-rate test*
  (was promiscuity probe), *no-coordination test* (was empty recording), *close-events test*
  (was crowded veto). *Quiet* and *busy* name the two backgrounds, never a test. The
  detector keyed `cicada` is **locust** on any page.
- **A coordinated event's width and amplitude** have one definition for every detector:
  width = earliest to last onset in it, amplitude = cells ÷ width
  (`src/bugarach/call_measure.py`, PR #698). Not a detector's own `width_sec`.

## Nothing a slow run writes may land on a fast result

Tony, 2026-09-21, on reading this handoff: the code does not appear to be set up to handle two
channels of data, and the fast fits and results must not get clobbered. Six places where a slow
run overwrites a fast one, read off the tree at `a4db11d`. Five are one argument away from safe;
two have no seam at all.

| what a slow run would overwrite | where | what to do |
| --- | --- | --- |
| `docs/learned/bench_measured.json`, the fast bench's last measurement | `tools/remeasure_bench.py:224` writes that one path unconditionally — no `--stream`, no `--out`, only `--no-write` | the slow record is `bench_slow.MEASURED_RECORD`, its own file. This one is **caught after the fact today**: `tests/test_bench_is_measured_on_the_declared_folder.py` compares the record's `stream` field with `bench.MEASURED_STREAM` and separately pins that to `"fast"`, so a slow write reddens the suite and `git checkout` brings the fast record back — but only once it is already gone |
| the shipped settings, `bench.OPERATING_POINTS` (`src/bugarach/bench.py:523`) | read by the viewer (`src/bugarach/ui/app.py:284`), by real-data detection (`src/bugarach/detect_folder.py:408` and `:477`), by the bake-off and by the figure tools | **the slow winners do not go here.** There is one operating point per detector and it is a fast one — locust's own entry says SLOW's percentile has no bench evidence at either duration. Ship slow settings as a settings CSV instead: `load_settings` (`detect_folder.py:376`) keys rows by `(detector, stream)`, and #700 (`acc6a16`) made `detect --settings` take any parameter a detector takes, so `stream=slow` rows reach real recordings without touching a fast number |
| the search's output folder | `tools/search_all_settings.py:809` defaults to `<darkroom>/<date>-full-search` | pass `--out` on every run: a fast search and a slow search **on the same day write the same folder**. The tool has no bench seam either — it binds `bugarach.bench` at module scope (`:64`) and judges candidates against `_bench.BENCH_RECORDING` (`:121`) |
| the training run's declaration | `tools/tune_learned_vs_coact.py`, branch `tune-bench-comparison` | `--out` is already required, so no folder collides. The danger is the other one: the bench is hardwired in roughly a dozen places, including what `meta.json` records as `bench_recording`, `backgrounds` and `null_recording`, and the provenance string `"bugarach.bench.make_recording"` (`:842`); `--simulation` offers only `bench` or `home` (`:1688`). **Without a seam a slow run trains on fast simulated recordings and stamps them slow** — step 2's trap, one tool further on |
| the leaderboard page | `tools/leaderboard.py:51` defaults `--runs` to the fast run's folder; `:510` writes `leaderboard.html` under the darkroom, a fixed name | the slow page needs both `--runs` and a name of its own, or it replaces the fast one in place |
| nothing — but it invalidates the slow nets | `src/bugarach/learn/encode.py:165`, `decode(..., merge_gap_frames=20)`, which `pick_threshold` uses | a gap sized for fast splits or truncates slow events. Check it before reading any slow net result, as "Nets' input timing" below says |

What is **not** at risk: the run folders are name-stamped
(`docs/learned/tuned_vs_coact/fair_comparison_2026_09_18`, `replicate1`), so the weekend's fast
fits and chosen models survive any slow run given a folder name of its own — and #702 puts that
weekend material in the repo, where a mistake is recoverable rather than disk-only.

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
