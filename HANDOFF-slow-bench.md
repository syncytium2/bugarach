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

## Status

Newest last. A session that finds this file picks up at the first step not marked done.

- 2026-09-21 (WSMIP064, branch `opt/slow-bench`): **step 1 measured; two of its values need
  a ruling before step 2 can set them.** `tools/measure_slow_bench.py` →
  `docs/learned/bench_measured_slow.json` (84 baseline windows, slow stream, default folder;
  95% bootstrap intervals over recordings). Slow against the fast bench: quiet background
  0.0030 Hz per ROI (fast 0.0052), busy 0.0113 (fast 0.0190), rate shape 0.42 (fast 0.275),
  300 s burst shape 3.5 (fast 1.547), ROI count 31.5, participation 0.38 (fast 0.18). Widths
  from the producer's column: median 2.0 s, interquartile 1.7–2.5 s, max 5.5 s.
  **Jitter is not identified by this instrument, on either stream**: `assess_coactivity`'s
  cluster SD tracks bin/√12 from 0.5 s to 5 s (fast 0.17 → 2.03 s, slow 0.21 → 1.39 s), so
  it reports the coincidence bin, and the fast bench's 0.36 s is what a 1 s bin gives.
  Participation does not move with the bin. **The 60 s burst shape has no upper bound on
  slow** (interval 5.2 to the fit's cap). Figure 1:
  `<darkroom>/bugarach/2026-09-21-slow-bench-jitter-vs-bin.png`. **Real crowding is not
  measured yet**: `tools/probe_real_crowding.py` runs CoactDetect at its fast setting,
  which would be circular on slow; it comes after step 4 chooses slow settings.
- 2026-09-21 (WSMIP064, branch `opt/slow-bench`): **step 2 built; jitter is the one value
  still waiting.** `src/bugarach/bench_slow.py` with its own copies of every function that
  reads a stream constant, and `tests/test_bench_slow.py` guarding that none is the fast
  object and that a slow recording has slow rates and slow widths. **One more place the trap
  lived, outside `bench.py`:** `simulate._draw_widths` read the fast width table as a global,
  so a slow recording would have handed locust fast widths; `simulate_coordination` now takes
  `width_quantiles`. Tony's rulings the same evening: **no 60 s burst term on slow**, and the
  **budgets re-measured** — `tools/measure_slow_budgets.py` → `docs/learned/bench_slow_budgets.json`,
  at the fast settings on seeds 1–48 of both benches (19 s on 12 workers). ⚠ The headroom
  rule (1.6 × measured, rounded up) is this session's and is tighter than several declared
  fast ceilings, which were set at older settings. **Jitter**: 0.30 s placeholder; Tony was
  offered a per-recording range (no extra cost) plus an F1-against-jitter curve at the end.
  Next: step 3, `--bench fast|slow` in `tools/search_all_settings.py` and slow grids.
- 2026-09-21 (WSMIP064): **jitter fixed at 0.30 s** (Tony: the fast bench fixes 0.36 the same
  way); **budgets kept as measured** (Tony). **Step 3 tooling merged (#711)**; the slow
  every-knob search ran: `--bench slow --sliding`, 12 workers, 11.2 min, empty `search.err`.
  Files: `docs/learned/runs/2026-09-21-full-search-slow/` and the same in the darkroom.
  ⚠ "shipped" in its table means the FAST settings on the slow bench, and its caption's
  "bench.py" means `bench_slow`. **Held-out gains** (mean F1 over the two backgrounds, 95%
  interval): locust +0.239 [+0.226, +0.252], SPIKE-synch +0.155 [+0.144, +0.166],
  CoactDetect +0.081, LoCo +0.044, binned SCE +0.020, rate+context +0.005.
  **Not adoptable as it stands, for reasons the fast search already met:**
  (1) **SPIKE-synch's `C_min` 0.0025 is unbracketed** — the search ran out of extensions
  (`MAX_EXTENSIONS = 3`, the silent cap this file's goal-1 twin named), and it also **fails the
  close-events check held out** (−0.022 against an allowance of 0.02; it passed on the
  selection recordings); its `max_gap` of 16 s is a window-shaped setting the bench can flatter.
  (2) **locust's gain is `sce_min_distance_frames` 4 → 256 (25.6 s)**, bracketed this time
  (512 was tried) — the same climb the fast search saw to 128 frames, which that handoff tied
  to the anchor question; it is not a setting to ship until the anchor is settled.
  (3) **CoactDetect's gain is `min_rois` 3 → 6** — against planted participation of about 7,
  12 and 20 ROIs, which is the warning `min_rois` carries: it can learn the simulation.
  (4) **The search extends integer floors by halving** (`sce.min_rois` 1.5 → 0.375, `loco.min_rois`
  and `sync.min_n` the same): `extend` does not know `min_rois` / `min_n` are integers. None
  of those values was chosen; filed rather than fixed here, because the fast search shares it.
  (5) **LoCo's context sits at 120 s, the null-rule cap**, and did not move; the slow search
  gives no evidence either way on whether slow wants a wider spacing.
  LoCo (+0.044: threshold 99.995 bracketed by 99.9975, merge gap 4 s) and binned SCE
  (threshold 99, bin 5 s) are the clean ones. Nothing is set in `bench_slow.OPERATING_POINTS`;
  choosing is Tony's. Step 5 (the nets) waits on which slow coded settings are the reference.
- 2026-09-21 (WSMIP064): **Tony adopted LoCo and CoactDetect as the slow reference**, now in
  `bench_slow.OPERATING_POINTS` with their `source` strings; the other four stay at the fast
  settings. What came out on the way to that ruling, for whoever picks this up:
  **CoactDetect is fine on slow** — at `min_rois` 3 it scores 0.834 held out, but makes about 4
  calls/hour on the no-coordination recording (chance triples; nothing is planted there)
  against the slow budget of 2, and `min_rois` 6 takes that to 0 while excluding no planted
  event (smallest about 7 ROIs); 0.861 at the adopted setting. **The slow bench is fast with
  events twice as big**: at the same fast settings every detector scores higher on slow
  (0.61–0.85 against 0.45–0.70), and giving the slow bench fast's participation (0.30/0.18/0.10)
  puts the order back to fast's — CoactDetect 0.732, LoCo 0.725, rate+context 0.661, binned
  SCE 0.608, locust 0.529, SPIKE-synch 0.498. So **slow participation, 0.38, is the value the
  whole slow bench turns on**, and a bench where everything scores 0.8+ separates detectors
  — and nets from coded ones — less well. **Step 5 is not started.** What it needs from here
  is one fixed CoactDetect setting to anchor the shared false-alarm budget (this one); what
  it needs first is Tony's call on whether to confirm the 0.38 before spending about 28
  GPU-hours, or to run a short pilot. The tuning tool still lives on `tune-bench-comparison`
  and needs the same `--bench` seam the search got.
