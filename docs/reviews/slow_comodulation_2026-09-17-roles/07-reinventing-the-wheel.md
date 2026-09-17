GRANT 7 MISMATCH — missing Grep, Glob; holds no forbidden tools (holds Read, Bash)

(Missing Grep and Glob didn't stop the review: I did every search with `grep`/`git grep` through Bash. Nothing was written to the repo. The only files I created are the empty scratch folder `review/r7/`. My one attempt to write a script file there was blocked by the repo's no-heredoc hook, so the checks ran as inline `python -c`.)

# Reuse audit: slow co-modulation (round 1)

Worktree `<worktree>`, HEAD 8ba5f57.

**Two findings go to the main thread first:**
- **Blocking:** the page says the benchmark has no shared modulation and no shoulder. The simulator code it cites contradicts that, and I measured a shoulder of about +1.0 on the benchmark's own generator.
- **Major:** the "per-ROI modulation (the simulator's kind)" world is not what the simulator draws. It is a stand-in.

Most of the rest is duplicated code. Where it re-implements something, it matches the reference in distribution (I checked empirically) but not draw for draw.

## Findings

**1. The claim that the benchmark has no shoulder is false.**
- **Location:** `docs/learned/slow_comodulation/README.md` lines 55–57 (*"the simulator's background has no shared modulation at all, so no benchmark in this repository contains a shoulder"*) and lines 175–176 (*"The benchmark has never contained any of this … no supervised model here has seen a shoulder or a dip"*).
- **Issue:** The page read the per-ROI Gamma burst series in the simulator (`src/bugarach/simulate.py:764-774`) and missed its shared hot window a few lines later (`simulate.py:782-793`). That window raises every ROI at once.
  - The benchmark turns it on: `BENCH_RECORDING` sets a 1200–1500 s window at 0.06 Hz with a 30 s ramp (`src/bugarach/bench.py:387-389`).
  - So does the generator the label-free and bake-off runs train on: `docs/learned/generator_spec.json` lines 20–39, loaded through `tools/fair_bakeoff.py:89-91`.
  - The benchmark also plants 6 correlated-burst distractors (`bench.py:390-392`), which are sub-second coincidences.
- **Measured:** I ran the page's own `pair_counts`/`pooled` on 6 recordings from `generator_spec.json`, drawn by `simulate_coordination`:

  | recording | 5–7 s | 28–40 s | 78–109 s | 153–214 s |
  |---|---|---|---|---|
  | full generator spec | +1.00 | +0.93 | +0.68 | +0.36 |
  | background plus hot window only | +1.19 | +1.10 | +0.82 | +0.45 |
  | background only (no hot window, no events) | +0.07 | +0.04 | −0.01 | −0.04 |

  The benchmark's shoulder is about ten times the lab fast stream's (+0.05 to +0.09).
- **Severity:** blocking.
- **Fix:**
  - Remove both claims.
  - Add the actual generator as a synthetic world: call `simulate_coordination(seed=…, **generator_spec)` the way `tools/fair_bakeoff.py:89` does, rather than describing the simulator from memory.
  - Say that the hot window, which exists so a detector fooled by rate gets caught, is exactly a shared change over minutes.
- **Verified:** yes (code read and measured).

**2. The "simulator's kind" world is not the simulator's model.**
- **Location:** `tools/measure_slow_comodulation.py:43` (docstring), `:252-275` (`_ou_multiplier`, the `per_roi` world); `tools/make_slow_comodulation_figure.py:49` (legend "per-ROI modulation (the simulator's kind)"); README Figure 1 caption, lines 48–50.
- **Issue:** The two models share only the per-ROI part:

  | | the simulator (`simulate.py:720-774`) | the `per_roi` world |
  |---|---|---|
  | multiplier | Gamma(k, 1/k), constant within each bin | log-normal, driven by an Ornstein–Uhlenbeck process |
  | scales | two, multiplied together: 300 s and 60 s bins | one: τ 20 s |
  | depth | shapes (1.547, 1.388), `bench.MEASURED_BURST_SHAPE` (`bench.py:106`), fitted to data | σ 0.8, chosen by hand |
  | how onsets are drawn | Poisson onsets at continuous times, then rounded to frames | a Bernoulli draw per frame (at most one onset per frame) |

  The real simulator background may not read exactly zero either. On 6 recordings its background-only curve sits at +0.04 to +0.11 from 0.25 s out to 10 s. That may be noise across 6 recordings; I did not settle it.
- **Severity:** major.
- **Fix:** Draw this world with `simulate_coordination(..., bg_rate_shape=MEASURED_RATE_SHAPE, bg_burst_shape=MEASURED_BURST_SHAPE, bg_burst_bin_sec=MEASURED_BURST_BINS, participation=(…), n_per_level=(0,))`, or drop "the simulator's kind" from the legend, docstring and caption. The `independent` and `events` worlds could come from the same call (`n_per_level`, `jitter_sec=0.3`, 7/32 participation).
- **Verified:** yes (code read). The background-only curve is measured.

**3. The 2-minute block control is a copy of an existing registered control.**
- **Location:** `tools/measure_slow_comodulation.py:176-189` (`block_circular`).
- **Issue:** It duplicates `bugarach.surrogates.window_circular_shift` (`src/bugarach/surrogates.py:827-846`), which is registered in `CONTROLS` (`:865-872`) and reachable through `sg.generate("window_circular_shift", trains, window, key, analysis_window=block)`.
  - **What matches:** tiles start at the window start, the last short tile is its own window, each tile gets its own lags, and counts per tile are kept.
  - **What differs:** the reference draws a continuous lag, rounds with `floor(x + 0.5)` and wraps mod the tile width. The copy draws `randint(0, width)`, and one RandomState runs through every block and ROI.
  - I checked the distributions over 4,000 draws: both reach every frame of a full tile (20 of 20) and of the short last tile (10 of 10). Deviation from uniform was at most 0.009 for the copy and 0.010 for the reference, which is noise. They agree in distribution, not draw for draw.
  - The reference's docstring calls this a known-bad control: *"the seam every window acquires is what it is built to move."* The page reads its curve at 56–78 s and beyond without mentioning the 2-minute seams.
- **Severity:** minor for reuse. The seam caveat should go to the interpretation roles.
- **Fix:** Call `sg.generate("window_circular_shift", …)`, or at least name it as the same control and carry its seam warning.
- **Verified:** yes (4,000-draw check).

**4. The circular-shift null is a copy.**
- **Location:** `tools/measure_slow_comodulation.py:151-153` (`circular`).
- **Issue:** It duplicates `bugarach.surrogates.circular_shift` (`surrogates.py:351-365`), which calls `bugarach.assess.circular_shift_trains` (`src/bugarach/assess.py:340-353`). That is the null the assessor itself uses.
  - The reference draws one uniform per ROI (empty ROIs included), multiplies by the window length, rounds with `floor(+0.5)` and wraps mod L. The copy draws `randint(0, L)`.
  - Checked over 4,000 draws at L = 37: both reach all 37 frames, with deviation from uniform of 0.006 and 0.0065. Same distribution, different draw streams.
- **Severity:** minor.
- **Fix:** Call `sg.circular_shift(tr, (0, L), key)`, or cite it as the same null.
- **Verified:** yes.

**5. The rigid-shift arm rests on an untested tool function.**
- **Location:** `tools/measure_slow_comodulation.py:66, 207-213`; README line 65.
- **Issue:** It imports `rigid_frames` from `tools/tube_self_supervised.py:97-104` instead of the tested `bugarach.surrogates.rigid_shift` (`surrogates.py:368-386`). Importing rather than re-deriving is right, and `rigid_frames` avoids Elephant, which is not installed in this venv (so the tested version could not even run here).
  - Nothing tests `rigid_frames`: no file under `tests/` names it. Its claim to equal `rigid_shift` rests on a note in the tube tool's docstring that a reviewer checked it.
  - I checked analytically that it drops onsets correctly at the edges: an onset at frame 95 of 100 with J = 10 survived 73.0% of the time against 72.5% expected.
  - I could not run the Elephant path to compare.
  - Seeding differs from the reference: one RandomState per call, and empty ROIs still consume a draw. The reference seeds each ROI from its key and skips empty ROIs.
  - The J conversion `J / dt` matches `tools/look_rigid_shift_controls.py` (`round(J / dt, 9)`).
  - Trimming by `ceil(20 / dt)` is enough: every onset that can shift into the trimmed window starts inside the window.
- **Severity:** minor.
- **Fix:** Add a test in `tests/test_measure_slow_comodulation.py` that the rigid arm shifts each ROI by a whole number of frames, spread uniformly as `floor(0.5 + U(−J, J))`, and drops onsets outside [0, L). Where Elephant is installed, also test it against `sg.rigid_shift`.
- **Verified:** partly. Edge-drop semantics yes; equivalence with Elephant no.

**6. The minutes-friendly tick labels re-implement a tested module and differ from it.**
- **Location:** `tools/make_slow_comodulation_figure.py:59-64` (`fmt_sec`), `:112-114` (`time_ticks`).
- **Issue:** `src/bugarach/time_axis.py` already provides `label()` and `ticks()` for figures drawn without Bokeh. `tests/test_time_axis.py` tests them against the viewer's own JavaScript formatter. The copy disagrees:

  | seconds | `fmt_sec` (copy) | `time_axis.label` (reference) |
  |---|---|---|
  | 125 | `2m5s` | `2m05s` |
  | 150.5 | `2m30s` | `2m31s` |
  | −120 | `-120s` | `-2m` |
  | 3599.6 | `60m` | `59m60s` |

  The ticks in the current figures (0.25s, 1s, 5s, 15s, 1m, 5m, 10m, 15m) happen to render the same. `time_axis.ticks(0, 1080)` also picks the same 5-minute step the tool hardcodes.
- **Severity:** minor. There is no visible defect today, but it is a second copy of a rule CLAUDE.md says to reuse.
- **Fix:** `from bugarach.time_axis import label, ticks`. Use `label` for the lag ticks, and `ticks(0, t1 - t0)` plus `label` for the raster axis.
- **Verified:** yes (ran both).

**7. The baseline loader and its refusal are a verbatim copy.**
- **Location:** `tools/measure_slow_comodulation.py:223-235` (`load`).
- **Issue:** It copies `tools/look_rigid_shift.py:86-100` line for line. The only change is that the role is an argument instead of the `LOOK_ROLE` environment variable. The refusal prefix `"baseline region"` and the fact that only `steps_excluded` is guarded are the same. This is the second copy; `tools/look_rigid_shift_controls.py` reaches the first through `lr.load`.
- **Severity:** minor.
- **Fix:** Move a `baseline_recordings(role, stream, limit)` into `bugarach.surrogate_stats` beside `recordings_from_slices` and call it from both tools. Otherwise a third copy will drift from the refusal.
- **Verified:** yes (read side by side).

**8. The CoactDetect episodes don't match what the detector itself would report.**
- **Location:** `tools/measure_slow_comodulation.py:81-86, 156-173` (`COACT_PARAMS`, `coact_removed`).
- **Issue:**
  - **Parameters:** fast matches `bench.OPERATING_POINTS['coact'].params` exactly (I printed both), but is hardcoded rather than imported. The canonical route is `bugarach.detect_folder.detector_params("coact", …)` (`src/bugarach/detect_folder.py:409-440`).
  - **Seed:** `rng_seed` is left at the default 20260706, the same as `detect_folder.RNG_SEED` (`:109`), which matches. But the docstring line "Every random key carries TAG" is false for this draw.
  - **Input times:** `detect_folder._run_flat` (`:467-468`) passes raw `t50rise` seconds over the region span. The copy passes times rounded to frames and shifted to start at the window. That moves bin edges by up to half a frame, so episodes can differ from `bugarach detect`'s.
  - **Episode membership:** removal tests `ts <= onset + width`, a closed interval. CoactDetect bins half-open, `floor((t − t0) / bw)` (`src/bugarach/detectors/coact.py:113-115`). Onsets that fall exactly on an episode's end edge belong to the next bin but get removed; with rounded frame times that happens depending on float rounding (for example `20*0.1 == 2.0` but `60*0.1 != 6.0`).
- **Severity:** minor.
- **Fix:**
  - Import the fast point from `bench.OPERATING_POINTS`.
  - Feed `(t + a) * dt` over `(a*dt, b*dt)`, or better the stream's `t50rise` seconds.
  - Assign membership by CoactDetect's own bin index: the onset's bin lies in [first bin, last bin] of the episode.
  - Correct the TAG sentence.
- **Verified:** yes (code read, parameters printed).

**9. The synthetic sizes are hardcoded duplicates of the generator spec.**
- **Location:** `tools/measure_slow_comodulation.py:90-96` (`SYN`).
- **Issue:** `n_roi=32`, `rate_hz=0.0097`, `event_jitter_sec=0.3` and `event_rois=7` duplicate `generator_spec.json` (`n_roi` 32, `bg_rate_hz` 0.009706, `jitter_sec` 0.311, top participation 0.225 × 32 ≈ 7). The docstring credits a manual peek at the export folder instead.
- **Severity:** minor.
- **Fix:** Read these from `docs/learned/generator_spec.json` or cite it, so a new spec cannot silently leave this page behind.
- **Verified:** yes.

**10. The mouse bootstrap is a fourth hand-rolled copy.**
- **Location:** `tools/measure_slow_comodulation.py:303-328` (`pooled`, `summarise`).
- **Issue:** `src/bugarach` has no shared mouse bootstrap. The closest existing versions are `tools/look_rigid_shift.py:222-227` (ratio of sums, one pick matrix of size n_boot × n_mice) and `tools/measure_recording_identity.py:189-199`. The copy matches the ratio-of-sums-over-mice approach, but:
  - it uses `nanpercentile` where the others use `percentile`;
  - it runs one RNG through all arms, so each arm resamples different mice and the intervals are not paired across arms. The look draws its pick matrix once per bootstrap.
- **Severity:** minor.
- **Fix:** Draw the pick matrix once and reuse it for every arm. Longer term, put a single `mouse_bootstrap_ratio` in `surrogate_stats`.
- **Verified:** yes (code read).

**11. Two small helpers duplicate `src`.**
- **Location:** `tools/make_slow_comodulation_figure.py:102-109` (`_lit_share`) and `:238-239` (darkroom-missing message).
- **Issue:**
  - `_lit_share` is `bugarach.detectors._shared.distinct_coact(evs, edges) / n_roi` (`src/bugarach/detectors/_shared.py:63-75`). Its `discretize` bins the same way as `np.histogram`, so the output is identical.
  - The missing-darkroom error is hand-written. 39 tools use `bugarach.paths.unresolved_message("--out")` (`src/bugarach/paths.py:208`), which also tells the user how to fix it.
  - `darkroom(FOLDER, create=True)` itself is used correctly.
- **Severity:** minor.
- **Fix:** Call `distinct_coact` and `unresolved_message`.
- **Verified:** yes.

**12. A second session built a different modulation twin for the same question on the same day.**
- **Location:** `tools/measure_slow_comodulation.py:252-275` against `tools/tube_self_supervised.py:modulated` on `origin/unsup/rigid-shift-report-residuals` (commit 65285fa, draft PR #603, not merged).
- **Issue:** That session's twin is sinusoidal thinning (period 40 s, depth 0.9, one phase shared or one per ROI). This page's is an Ornstein–Uhlenbeck log-normal multiplier with τ of 20 s and 300 s. README lines 168–170 say that session "confirmed this independently", but the two used different modulation models, so the results are not directly comparable. It isn't landed code, so there is no reuse obligation.
- **Severity:** minor.
- **Fix:** Name the other twin's model in the sentence, or align the two worlds before citing agreement.
- **Verified:** yes (`git show`).

**13. Small copies that match their references exactly.**
- **Location:** `tools/measure_slow_comodulation.py:99-100` (`seed31`), `:146-148` (`trimmed`), `:281` (event rounding).
- **Issue:**
  - `seed31` is the seventh copy in `tools/`. `surrogate_stats.rng_of(key)` (`src/bugarach/surrogate_stats.py:123`) already returns the RandomState, so the `& 0x7FFFFFFF` mask isn't needed.
  - `trimmed` equals `surrogates._prepare`'s in-window-minus-start. I checked on a hostile train with onsets on both edges: identical.
  - The event rounding `floor(x/dt + 0.5)` equals `surrogate_stats.to_frames` for positive times, and every planted time is positive here.
- **Severity:** minor.
- **Fix:** Optional: use `ss.rng_of((TAG, …))`.
- **Verified:** yes.

## Checked and not duplicated
- **The cross-correlogram itself** (`pair_counts`, `_autocorr_rows`, `lag_bins`): nothing in `src/bugarach` or `tools/` computes one (searched for correlogram, xcorr, cross-correlation and coincidence).
  - `bugarach.graph.sttc` (`src/bugarach/graph.py:93`) and `detectors/sync.py:_pair_coincidence` measure coincidence between pairs, but they are different statistics.
  - The window-shuffle surrogate (`surrogates.window_shuffle`) is a different operation from the block control.
- **Loading** through `dataset.current`, `load_folder` and `recordings_from_slices` goes through the canonical path.
- **Darkroom resolution** goes through `bugarach.paths.darkroom`.

## Relevant files
- <worktree>/tools/measure_slow_comodulation.py
- <worktree>/tools/make_slow_comodulation_figure.py
- <worktree>/docs/learned/slow_comodulation/README.md
- <worktree>/src/bugarach/simulate.py
- <worktree>/src/bugarach/bench.py
- <worktree>/docs/learned/generator_spec.json
- <worktree>/src/bugarach/surrogates.py
- <worktree>/src/bugarach/assess.py
- <worktree>/src/bugarach/time_axis.py
- <worktree>/src/bugarach/detect_folder.py
- <worktree>/src/bugarach/detectors/coact.py
- <worktree>/src/bugarach/detectors/_shared.py
- <worktree>/tools/tube_self_supervised.py
- <worktree>/tools/look_rigid_shift.py
