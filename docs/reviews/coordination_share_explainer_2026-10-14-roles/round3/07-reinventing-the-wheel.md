GRANT 7 ok — Read, Grep, Glob, Bash

Role 7 (reuse auditor) on `docs/learned/coordination_share_explainer/README.md`, its six PNGs and `explain_coordination_share.py`, in the worktree `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer`. I edited nothing; the only thing I ran was a read-only Python check.

**Bottom line:** I found no estimator code re-implemented incorrectly, and no blocking or high-severity problems. Everything that estimates is called from the tool, `tools/measure_coordination_rates.py` (referred to below as `mcr`). The functions called are `measure`, `per_recording`, `solve`, `shifted`, `population_cumulants`, `_frames` and `_sim`, plus the constants `DT`, `WINDOWS`, `N_SURR`, `CAL_TOL`, `CAL_JITTER` and `ADOPTED_MODEL`. The generator, rounding and time axis come from `simulate_coordination`, `matlab_round` and `bugarach.time_axis`.

Where the script does re-implement something, it matches the reference:

- **Moment sizes:** `max(1, matlab_round(p*N))` gives 10, 6 and 3 cells, as in `simulate.py:966`.
- **Jitter:** Gaussian, standard deviation 0.106 s from `CAL_JITTER`, clamped to [0, T], as in `simulate.py:970` and `mcr._sim`.
- **Participants:** chosen with `choice(N, k, replace=False)`.
- **Frame conversion and clamp:** identical to `mcr._sim` (`measure_coordination_rates.py:416`).
- **Elevated-rate stretch:** `simulate.py:903-914` adds `hot_rate_hz` on top of the background and thins linearly over `ramp_sec`. That matches the "+0.1334" axis label in Figure 5 and the `span - ramp/2` arithmetic at script lines 643-644.
- **Truth:** it is defined as a share of events, not the tool's `ks.sum()/(N*T)`, but the two give the same ratio. I checked this: across 6 seeds, both the mixed set and the 0.5 s pairs, the explainer's planted count equals `ks.sum()` exactly (95 = 95 every time). Panel 3C uses the tool's own `truth()`.
- **Figure 1C counts:** binned on float seconds, but they match the tool's integer `frames // wf` bins (0 of 2,700 bins differ).
- **Pooling:** f3/f2 is pooled over both backgrounds (48 recordings), the same set the tool's `calibrate` pools over.

## Findings

Each finding: location · issue · severity · suggested fix · verified against a source.

1. **`explain_coordination_share.py:347-350` (Figure 2)** · The surrogate subtraction is written out again instead of calling `mcr.excess_cumulants` (`measure_coordination_rates.py:161-166`). The copy is faithful (spacing `2*wf`, `N_SURR`, `population_cumulants`), and it exists so panel B can show each shifted copy. But it draws from a random-number stream that the panel-A shifted copy (line 346) has already used. So the excess f₂, f₃ and *k* on the figure are not the numbers `mcr.measure` would report for that recording. · Low · Keep the loop, since panel B needs each copy, but add a comment that it mirrors `excess_cumulants`. Either assert it agrees with `mcr.excess_cumulants` on a fresh `RandomState`, or say in the README that panel B's *k* is one draw of the surrogates. · Verified: yes (read both)

2. **Line 68 `SEEDS = tuple(range(1, 25))`, commented "as the tool's"** · Re-types `mcr.SIM_SEEDS`. If the tool changes its seed count, the explainer silently stops matching the claim. · Low · `SEEDS = mcr.SIM_SEEDS`. · Verified: yes (`measure_coordination_rates.py:106`)

3. **Line 69 `SLOT_SEP = 120.0`, commented "the bench's old spacing floor"** · Re-types `bench.BENCH_RECORDING["min_sep_sec"]` (`bench.py:1029`). · Low · `SLOT_SEP = float(bench.BENCH_RECORDING["min_sep_sec"])`. · Verified: yes

4. **Hard-coded label text that copies canonical constants:**
   - line 369, "each of 20 shifted copies" (`mcr.N_SURR`)
   - line 381, "planted: 10, 6 and 3 cells" (`SIZES`)
   - line 400, "(10, 6, 3 cells)" and line 401, "(6 cells)" (`SIZES`, `SIZES[1]`)
   - line 406, "pass band (±25%)" and line 445, "±25%" (`mcr.CAL_TOL`; the band itself is drawn from `CAL_TOL`, so band and label can disagree)
   - line 471, "48 recordings"; line 498, "24 recordings" (`len(SEEDS)` times the number of backgrounds)

   The README captions repeat 20, ±25% and 48. · Low · Build these strings from the constants (f-strings). The README is hand-written, so its numbers need checking whenever the constants move. · Verified: yes

5. **Lines 237-241 `artifact_name()`** · Runs `tools/naming/artifact_name.py build` as a subprocess. CLAUDE.md reserves the subprocess route for R and MATLAB. The Python precedent imports it in-process: `tools/make_group_raster_summary.py:358-364` does `from naming import artifact_name; artifact_name.build(artifact_name.load_codes(), type=..., ext=..., date=..., ...)`. The output is the same, so this is style, not a defect. · Info/Low · Import and call `artifact_name.build` directly, as the repo's other Python tool does. · Verified: yes

6. **Lines 634-645 (Figure 5, panels A and B)** · Builds elevated-rate recordings with `simulate_coordination` directly instead of `bench.make_elevated_rate_recording` (`bench.py:1588`). That is justified for the length and size sweeps, which the bench function cannot express. But the panel B point at 0.1334 Hz is the bench's own elevated recording on a different seed (no `ELEVATED_SEED_OFFSET`), so it is not literally "the bench's own elevated-rate stretch" (README line 214). · Low · Either word the README as "the bench's stretch settings", or build that one point through `bench.make_elevated_rate_recording`. · Verified: yes

7. **Lines 410-411 and 451-458 (Figures 3 and 4)** · The "median, what the check tests" is recomputed as `median(recovered/planted) - 1` instead of calling `mcr.calibrate`. On 3C the two are algebraically identical, because `rate` cancels: x.share/t.share. On A and B the truth differs from the tool's `truth()` only by deduplication, which is zero in practice (see above). The page labels it "what the check tests", but nothing proves the check was run. · Low · For panel 3C, record `mcr.calibrate(bench_cal, 1.0, m)` in `numbers.json` (it also gives the participants and rate errors Figure 4 uses), and assert it equals the plotted median. · Verified: yes (algebra, plus the count check above)

8. **Lines 103-122 `schedule()` and line 70 `MARGIN = 30.0`** · Moment placement is new code rather than `simulate._place_renewal`/`_place_mixed`. That is justified: the docstring at lines 14-18 says simulate cannot plant fixed pairs at fixed gaps, and I confirmed it has no such option. Two side effects:
   - `MARGIN` = 30 s does not match simulate's `margin_sec` default of 5 s; `BENCH_RECORDING` sets no margin.
   - Gaps between slots are 120 s plus uniform stick-breaking, not the bench's `min_sep + Gamma` gaps (`interval_cv` = 1).

   Neither should move the statistic. · Info · Optionally say in the README's method section that the slot spacing is the page's own (120 s plus uniform slack, 30 s margins), not the bench's renewal draw. · Verified: yes (`simulate.py:354-427, 511-513`)

9. **Lines 136-142 `recording(ramp=...)`** · Slow rising background by thinning. There is no generator equivalent to reuse (simulate offers only `bg_burst_shape` clumping), so this is legitimately new code. I checked the arithmetic: the mean is kept at `bg_hz`, and the rate rises from start to end by exactly `ramp` times. · No defect · none · Verified: yes (derived by hand)

## Reused correctly (checked, no action)

- `background()` gives the same background as `bench.make_recording` for the same seed, because simulate draws the background before planting.
- A direct call is justified, since `make_recording` takes only named regimes and the page needs ¼ quiet, 13× quiet and a ramped top rate.
- The time axis uses the `bugarach.time_axis` port of `_time_axis_hook`.
- The darkroom path goes through `bugarach.paths.darkroom()`, with `unresolved_message`.
- Panel 3C runs exactly the tool's `_sim`, which applies `bench.spacing()` ("realistic", recorded in `numbers.json`).
