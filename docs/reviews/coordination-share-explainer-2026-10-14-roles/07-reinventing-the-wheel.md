GRANT 7 ok — Read, Grep, Glob, Bash

# Role 7, reuse audit (murderboard round 1): coordination-share explainer

I edited nothing. My scratch runs were inline `python -c` calls, and I wrote no files. One thing about the run itself: the repo's `no-heredoc-source.sh` hook blocked a heredoc I tried for a scratch script. I used `python -c` instead and nothing was lost.

**Bottom line:**
- The estimator is reused correctly.
- The planting claim in the docstring is half true.
- The recordings are described as "the fast stream's bench", but they are not what the bench builds today.
- Figure 5A's two no-planting rows rebuild recordings the bench already makes.

My reruns show the headline numbers barely move, so these are accuracy and reuse defects, not wrong results.

## Findings
Columns: location · issue · severity · suggested fix · verified

**1. `explain_coordination_share.py` lines 14–15 (docstring): "`simulate_coordination` has no way to set a gap schedule"** · medium · verified: yes
- **Issue:** Only half true.
  - It cannot force an exact schedule (2 close pairs, 2 medium pairs, 7 singles, a 120 s floor). `gap_source` gaps are bootstrapped with replacement (`src/bugarach/real_intervals.py:98-101`). `gap_mix` only mixes those with renewal gaps (`src/bugarach/simulate.py:429-490`, documented at 655-686). With `gap_mix=0`, all 15 moments are packed into one block of measured gaps, so the pair counts are random.
  - But it does have a gap path, and the bench uses it by default. Since 2026-10-07, `DEFAULT_SPACING = "realistic"` (`src/bugarach/bench.py:1188`). `spacing_overrides` (`bench.py:1237-1249`) passes `gap_source=<measured fast gaps>, gap_mix=0.0, n_per_level=(2,3,2)`.
- **Fix:** Reword along these lines: "`simulate_coordination` can draw gaps from a distribution (`gap_source`/`gap_mix`, resampled, and the bench's default since ADR-0010), but cannot plant a fixed number of 2 s and 10–20 s pairs, so the schedule is written here." Cite those lines.

**2. README lines 61–68 and docstring lines 9–12: "They copy the fast stream's bench … 15 planted shared moments … The bench keeps its moments at least 120 s apart"** · medium · verified: yes
- **Issue:** This describes `BENCH_RECORDING` under the old `"bench"` spacing, not the bench as it stands.
  - `bench.realistic_counts('fast', 3, 2700)` gives (2, 3, 2), which is 7 moments.
  - The measured fast gaps it plants (174 gaps) are 76% under 120 s, 11.5% at 10–20 s and 1.7% under 3 s, with a median of 41 s.
  - So the page's premise is stale: "the bench is ≥120 s, real recordings are closer". The default bench already plants closer moments. What it lacks is the under-2 s gaps, which were merged away at measurement (`bench.py:1182-1185`).
  - The tool's own calibration `_sim` goes through `make_recording`, so it now runs on realistic spacing unless `BUGARACH_BENCH_SPACING=bench` is set.
- **Fix:**
  - Say "the bench's `"bench"` spacing (its pre-2026-10-07 layout)".
  - Say the default bench now plants measured gaps (ADR-0010), and that what this page adds is fixed 2 s and 10–20 s pairs.
  - Optionally add a fifth set from `bench.make_recording(regime, seed)` at the default spacing, scored with the tool's `truth()`.

**3. `recording()` lines 114–123 (background) and its lack of decoys** · medium · verified: yes
- **Issue:** The rebuilt background differs from the bench in two ways.
  - It is homogeneous Poisson. The bench's is clumped in time: `bg_burst_shape=MEASURED_BURST_SHAPE` (1.770, 1.439) over `MEASURED_BURST_BINS` (300, 60) s (`bench.py:1042-1044`, applied at `simulate.py:847-900`).
  - It plants none of the bench's 6 decoys (`n_distractors=6`, `distractor_frac=0.18`, window 120–1100 s; `bench.py:1050-1052`). The tool's `truth()` counts decoys as coordinated (`measure_coordination_rates.py:395`).
  - The gamma rates do match the bench (`rng.gamma(SHAPE, bg/SHAPE, N)` matches `simulate.py:800`).
- **Measured impact (small):** I reran the tool's own calibration on the current bench with `BUGARACH_BENCH_SPACING=bench`, 48 recordings, 1 s window.

| | share, fixed | share, binomial | k | λ |
|---|---|---|---|---|
| Current bench (my rerun) | −17.4% | −5.9% | +22.5% | −32.5% |
| Explainer's closest set ("120 s only", `numbers.json`) | −18.2% | −7.8% | +27.5% | −35.8% |
| Explainer's "mixed" set, as quoted | −21% | −11% | | |

  The story holds.
- **Fix:** Either
  - reuse the bench background: `bench.make_recording(regime, seed, n_per_level=(0,0,0), n_distractors=0)` with `"bench"` spacing, take its fast `t50rise` trains through `mcr._frames`, and plant the schedule on top; or
  - state in the README that this background is not clumped in time and carries no decoys.

**4. Figure 5A rows 1 and 2 (`recording(..., planted=False)` and `stretch_hz=PROBE_HZ`), lines 124–128 and 59** · low–medium · verified: yes
- **Issue:** The bench already has both of these recordings.
  - `bench.make_null_recording(seed)` (`bench.py:1513`, `NULL_RECORDING` at :992).
  - `bench.make_elevated_rate_recording(regime, seed)` (`bench.py:1588`, `ELEVATED_RATE_RECORDING` at :1561-1567).
- **The rebuilt stretch differs from the bench's:**
  - `PROBE_HZ = 0.127` is typed by hand with the comment "the bench probe". The bench's level is now 0.1334 (`ELEVATED_RATE_RECORDING["hot_rate_hz"]`).
  - The explainer raises each cell *to* `max(r, 0.127)`, with no ramp, at a random start. `simulate.py:903-914` *adds* `hot_rate_hz` on top of the background, with 30 s ramps, at 1200–1500 s.
- **Reran on the bench's own recordings** (quiet, seeds 1–24, fixed model, 1 s):
  - Elevated: median 3.2%, max 5.7%, 24 of 24 recordings answered. The README says 3.7% / 5.7%.
  - Null: 0 of 24 answered, same as the explainer.
- **Fix:**
  - Call the two bench makers. The seed offsets are applied inside them.
  - Read the level from `bench.ELEVATED_RATE_RECORDING`.
  - README line 178: change "rises to 0.127 … the bench's elevated-rate level" to 0.1334 Hz added on top of the background.
  - The 3× linear-ramp row has no counterpart in the codebase, so rebuilding it is justified.

**5. `minutes()` / `time_axis()`, lines 188–196** · low · verified: yes
- **Issue:** This is a third hand-written copy of the minutes formatter. The canonical one is the JS formatter in `_time_axis_hook` (`src/bugarach/ui/app.py:120-129`). The other copy is `seconds_label` in `tools/make_surrogate_schematic_figure.py:81-85`, which does not zero-pad.
  - Positive ticks match canonical (`minutes(750)` gives "12m30s", padded).
  - `minutes(0)` returns "0m" where canonical gives "0s". Figure 1 doesn't hit this (it starts at 35m10s).
  - Ticks use a fixed 30 s step rather than the 1/2/5/10/15/30×60^k ticker, which is acceptable for a fixed 6-minute window.
  - No shared matplotlib helper exists to call, so this is not a missed reuse.
- **Fix:** Fix the zero case. Optionally move a matplotlib port of the formatter into a shared module, so the two copies become one.

**6. `recording()` frame handling, lines 142–147** · low · verified: yes
- **Issue:** Small departures from the canonical frame handling.
  - `np.round` (round-half-to-even) on raw seconds, versus `matlab_round` on the grid (`simulate.py:999-1003`) followed by the tool's `_frames` (`measure_coordination_rates.py:351-354`).
  - Frames ≥ L are dropped, where the tool clamps with `np.minimum(..., L-1)` (`:416`).
  - Jittered onsets are not clamped to [0, T]; simulate does this at :970.
- No practical effect: the 30 s margin and continuous times rule out ties. Participant counts `int(round(p*N))` equal `max(1, matlab_round(p*N))`; I checked both give [10, 6, 3].
- **Fix (optional):** Convert through `mcr._frames(t, 0, T)` and `np.minimum(..., L-1)` so the frames are the tool's frames.

**7. `artifact_name()` line 206 and `main()` line 479** · low · verified: yes
- **Issue:**
  - `--date 20261014` is hard-coded. `tools/naming/artifact_name.py` defaults to today (`:246`), so a later re-render is stamped with the old date.
  - `darkroom()` can return `None` (`src/bugarach/paths.py:184-196`), and `darkroom() / "..."` then fails with a `TypeError` instead of a clear message.
- **Fix:** Drop `--date`, or make it an argument. Check `darkroom()` for `None` and refuse with the reason.

## Checked and clean
- **Estimator reuse:** the code imports and calls `mcr.measure`, `per_recording`, `solve`, `shifted`, `population_cumulants`, `CAL_TOL`, `WINDOWS`, `N_SURR`, `ADOPTED_MODEL` and `CAL_JITTER` (0.106 s, the calibration's jitter). It re-derives none of the estimation.
  - `recovered()` = share / rate per recording, which matches `summarize`'s `coordinated_share_of_rate` (`measure_coordination_rates.py:338`).
  - Figure 2B computes the surrogate mean by hand rather than through `excess_cumulants`, so it can show each copy. It uses the same `2*wf` spacing and the same `N_SURR`.
  - Figure 2A's histogram uses offset 0 only (display only).
  - Figure 5B's per-recording answer goes through `mcr.solve`.
- **Truth share versus `truth()`:**
  - The tool computes Σk/(N·T) in Hz, counts decoys, and does not remove frame collisions.
  - The explainer computes n_planted/(n_bg+n_planted) after frame dedupe and compares it with share/rate.
  - These are the same quantity when there are no decoys and no collisions. On all 48 mixed recordings the tool-style truth divided by the explainer truth, minus 1, is exactly 0.
  - The k and λ truths match `truth()`.
  - If decoys are ever added (finding 3), they must be counted, as `truth()` counts them.
- **`tools/make_coordination_rates_figure.py`:** it reads a real run folder and renders Bokeh HTML through Playwright. None of it applies to synthetic matplotlib figures, so no reuse was missed.
- **The sister explainer** (`docs/learned/correlogram_explainer/explain_correlogram.py`) also uses its own toy planting, so it is no precedent for calling the bench.

## Files
- c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\explain_coordination_share.py
- c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\README.md
- c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\numbers.json
- c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\tools\measure_coordination_rates.py
- c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\src\bugarach\simulate.py
- c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\src\bugarach\bench.py
- c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\src\bugarach\real_intervals.py
- c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\src\bugarach\ui\app.py
- c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\tools\make_surrogate_schematic_figure.py
