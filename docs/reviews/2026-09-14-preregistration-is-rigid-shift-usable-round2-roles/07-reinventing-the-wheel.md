GRANT 7 MISMATCH — missing Grep, Glob; holds Read, Bash (no editing tools held)

# Reuse audit of the rigid-shift pre-registration, read as a build specification

**Artifact:** `docs/proposals/2026-09-14-preregistration-is-rigid-shift-usable.md` (blob 2c9813d). Where the page contradicts itself, the adopted amendments win.

**How I checked.**
- Without Grep or Glob, I searched with `grep` through Bash.
- I read these files in full: `src/bugarach/surrogate_discriminator.py`, `src/bugarach/surrogates.py`, `src/bugarach/surrogate_stats.py`, `tools/measure_recording_identity.py` and `tools/probe_discriminator.py`.
- I read these in part: `src/bugarach/assess.py` (the assessor and its binning), `src/bugarach/assess_folder.py` (`generation_window`), `src/bugarach/simulate.py` (the planted-event loop), `src/bugarach/learn/encode.py`, and three sections of `tools/build_surrogate_screen.py` (`build_grid`/`params_for`, `run_cell`, `prepare_stream`). In `tools/build_surrogate_report.py` I read the two saturation functions.
- I ran two numerical checks with the main checkout's `.venv` python, with no data involved:
  - Assessor binning of on-grid onsets at 0.5, 1.0 and 2.0 s bins with a 0.1 s frame interval: 0 frames land in the wrong bin.
  - Framing the same onsets by truncation, as the encoder does: 1,632 of 36,000 frames land one frame early.
- **Blind pass:** I opened no review file and no overnight-run output.
- **Disclosure:** grepping `docs/todo/2026-09-12-126-fast-candidates-were-voided-on-one-seed-of-twenty.md` for how seeds were used showed me its fast-stream rigid-shift accuracy range. The page's own lines 31–32 already quote that range. Nothing below depends on it.

**The short answer.** Every instrument and control the page names exists and has tests: `rigid_shift`, `uniform_dither`, `edge_thinning`, `homogeneous_resample`, `do_nothing`, `forced_choice`, `negative_control_pairs`, `destruction`, `destruction_twins`, `recordings_from_slices`. The runner should call them. But the amendments ask for more than "forced_choice unchanged" and "destruction unchanged except the bin" can deliver. `destruction` needs four changes, not one. The refitting bootstrap needs a public no-permutation scoring path. Three things have no code at all: the saturation table, the occupied-frame count and the seed-distribution rule.

---

## Findings

Each finding gives: location · issue · severity · suggested fix · verified against a source.

### Destruction

**1. `destruction` needs four changes the page does not list**
- **Where:** page line 113 ("`surrogate_stats.destruction`, unchanged except the bin") against the destruction and randomness amendments. Code: `src/bugarach/surrogate_stats.py:1175-1264`.
- **Issue:** Beyond the bin, the amendments need four more changes:
  - **An assessor-seed parameter.** `coact_excess` takes `seed=20260722` (`:1176`), but `destruction` never passes one (`:1220-1241`). So the assessor seed cannot be salted, and do-nothing cannot use "a different assessor seed on its after side".
  - **Per-draw values.** Only the mean and SD after the surrogate are returned (`:1253-1256`). The two-level bootstrap (twins, then draws within each twin) needs the paired per-draw `e_pl[K]` and `e_un[K]` arrays.
  - **A twin index in the surrogate key.** The key is `(f"twin-{p}", stream, cell_id, k)` (`:1227`). Rigid shift seeds each ROI from `key + (name, roi)` (`surrogates.py:124-125, 379`). So the "5 independent twins" would get identical offsets per ROI per draw unless the twin index is folded into the key. The bootstrap over twins would then understate spread.
  - **A saltable freeze-half key.** It is `("freeze-half", p, k)` (`:1234`): no run tag, no twin, no cell. The same ROI half is frozen in every cell, and the randomness amendment does not list this key.
- **Severity:** high.
- **Fix:** Add `bin_sec=None`, `assess_seed`, `assess_seed_after`, `return_draws=True` and a `salt` or `twin` component to both keys. Defaults must reproduce today's output exactly, and a test must assert that. Amend the page's instrument line to list these changes.
- **Verified:** yes.

**2. The bin cannot be added as a frame half-width**
- **Where:** page line 167 against the amendment "1.0 s, which is 10 frames". Code: `surrogate_stats.py:93-95, 1193`.
- **Issue:** Today's bin is `(2*DESTRUCTION_HALF_WINDOW_FRAMES+1)*dt`, which can only express odd frame counts (5 frames = 0.5 s at 0.1 s). A half-width parameter cannot express 10 or 20 frames. `assess_coactivity` takes `bin_width_sec` in seconds and bins with `floor(t/bin)` on a fixed grid from the window start (`assess.py:512, 536, 255`).
- **Severity:** medium.
- **Fix:** Take the parameter in seconds. `None` should mean `5*dt`, so the overnight numbers reproduce. Record `bin_sec` in the twins' `describe` instead of `coincidence_half_window_frames`, which `build_surrogate_report.py:595, 628` reads.
- **Verified:** yes. Float binning of on-grid onsets at 0.5, 1.0 and 2.0 s with a 0.1 s frame interval puts 0 frames in the wrong bin.

**3. The visibility rule differs from the code's flag, and the 1.0 threshold has no unit**
- **Where:** the gated-K amendment ("excess before the surrogate is at least 1.0"). Code: `surrogate_stats.py:1258-1259`.
- **Issue:** The code sets `planted_visible = before > 0` and returns NaN retained when `before <= 0`, so the runner must not reuse that flag. The excess is also measured in co-active ROI-bins per minute (`assess.py:572-583`). That unit depends on the bin width, so "1.0" means something different at 0.5, 1.0 and 2.0 s bins.
- **Severity:** medium.
- **Fix:** In the runner, gate on `rows[K]["before"] >= 1.0`, and state the unit and its bin dependence on the page.
- **Verified:** yes.

**4. No saturation table exists; the nearest code computes something else**
- **Where:** the saturation-table amendment. Nearest code: `tools/build_surrogate_report.py:585-648`.
- **Issue:** `saturation_by_J` and `destruction_reach` compute an *expected count*, `0.5·n_roi·min(1, bin/(2J+1))`. They assume uniform dither, 0.5 participation for both twins, and the fixed 5-frame bin, and they read report JSON. The page wants P(largest bin ≥ K). A new implementation has to match these sources exactly:
  - **Participants:** `n_part = max(1, matlab_round(p·n_roi))` (`simulate.py:776`).
  - **Planted jitter:** Gaussian with an SD of one frame, clamped to [0, T] and quantized to the grid (`simulate.py:780`, `surrogate_stats.py:1152`). Event times are continuous, so bin phase is random.
  - **Rigid-shift mapping:** frame `floor(k + 0.5 + u)` with `u ~ U(−J, J)` (`surrogates.py:195-218, 380-383`).
  - **Assessor counting:** distinct ROIs per fixed-grid bin, `floor(t/bin)`, with the last bin clipped (`assess.py:246-258`).
  - **K scan:** `DEFAULT_MIN_ROIS = (3, 4, 6, 8)` (`assess.py:69`).
- **Severity:** medium.
- **Fix:** Write it new in `src/`, with a test holding it to a Monte Carlo run through `_coact_count` itself. Do not reuse the report formula.
- **Verified:** yes.

**5. The freeze-half control composed with homogeneous resample is untested**
- **Where:** the destruction-controls amendment. Code: `surrogate_stats.py:1233-1236`; `tools/build_surrogate_screen.py:120-126`.
- **Issue:** The call works: `destruction("homogeneous_resample", {}, …, freeze_half=True)`. But no unit test covers `freeze_half` in `tests/test_surrogate_stats.py`; it appears only in report fixtures. `build_grid` hard-wires the freeze-half cell to `circular_shift`, so the grid cannot be reused for this control.
- **Severity:** medium.
- **Fix:** Call `destruction` directly, and add a test that `freeze_half` restores exactly `len(tr)//2` ROIs, the same set for the planted and unplanted twins.
- **Verified:** yes.

**6. Twin construction is buried inside `prepare_stream`**
- **Where:** page line 114 ("the stream's own per-ROI counts and floor"). Code: `tools/build_surrogate_screen.py:548-571`.
- **Issue:** The twins take the median frame interval, frame count and ROI count, with counts drawn as `poisson(choice(rates)·n_frames)`. They are not the stream's own per-ROI counts. The floor is `max(f_frames)` = round-half-up(1.0 × `observed_floor`) (`:810`). Seeds are `("twins", role, stream, p)` and `("twin-seed", role, stream, p)`, with no twin index. Calling `prepare_stream` would also run 100 mouse splits and the held-out negatives.
- **Severity:** medium.
- **Fix:** Pull the twin block out into a function taking `(recs, stream, f_frames, twin_index, salt)` and call it from both tools. Say "resampled rates" on the page.
- **Verified:** yes.

### Leak gate

**7. The named bootstrap does not refit and is hard-coded to 95 %**
- **Where:** page line 88 ("the recording-identity run's `mouse_bootstrap`") against the "bootstrap refits" amendment. Code: `tools/measure_recording_identity.py:189-199`.
- **Issue:** `mouse_bootstrap` resamples a *fixed* per-pair correctness vector from one cross-validation fit, and returns `np.percentile(..., [2.5, 97.5])`. It cannot refit, cannot draw fresh fold seeds, and cannot give the 1.67th or 98.33rd percentiles.
  - Refitting through `forced_choice` is impractical. It always runs a permutation null, refusing fewer than 20 permutations (`surrogate_discriminator.py:397-402`), so each of the 2,000 resamples would pay for at least 20 extra refits.
  - The no-permutation path already exists as `cv_correct` (`measure_recording_identity.py:180-186`). It wraps the *private* `sd._scale` and `sd._cv_correct`, hard-codes 5 folds and l2 = 1, and is guarded only by a runtime assert (`:210`), not a test.
- **Severity:** high.
- **Fix:** Promote `cv_correct` into `surrogate_discriminator.py` as a public function, with a test that it equals `forced_choice(...).accuracy`. Build the refitting bootstrap on it. Duplicated mice already share one fold, because `mouse_folds` groups by the string label (`:200-214`). Keep `mouse_bootstrap`'s pair-weighted mean (`:196-197`) and use `np.percentile` with linear interpolation, stated on the page.
- **Verified:** yes.

**8. A salted seed can crash `forced_choice`**
- **Where:** the randomness amendment (fold seeds and negative-control seeds salted). Code: `surrogate_discriminator.py:205, 412`.
- **Issue:** `forced_choice` uses `seed` for the folds and `seed + 1` for the permutations. A crc32-derived seed can be 0xFFFFFFFF (`surrogate_stats.seed_of` masks to the full 32 bits, `:120`), and then `RandomState(2**32)` raises "Seed must be between 0 and 2**32 - 1". Separately, unsalted seeds 1000 to 1019 would share streams: seed s's permutation stream is seed s+1's fold stream.
- **Severity:** low.
- **Fix:** Derive fold and control seeds as `seed_of((tag, …)) & 0x7FFFFFFF`, and state that seeds 1000 to 1019 enter *inside* the salted key.
- **Verified:** yes (the seed-range error was reproduced).

**9. The 20 negative-control seeds share one pairing, so they are not independent**
- **Where:** page line 96 ("Three or more happens 7.5 % of the time by chance, four or more 1.6 %") and the negative-control amendment. Code: `surrogate_discriminator.py:454-465`.
- **Issue:** `negative_control_pairs` always pairs windows (1st, 2nd), (3rd, 4th) within each recording. The seed changes only the orientation, the folds and the null. The 20 seeds therefore test one fixed set of pairs and are correlated. The 7.5 % and 1.6 % figures assume 20 independent tests, which the code does not deliver. It is also unstated whether the pairs come from interior windows or all windows; the choice changes the pairing.
- **Severity:** medium.
- **Fix:** Either add a per-seed pairing permutation to `negative_control_pairs`, with a test, or state that the chance rates are not binomial and calibrate them by simulation before the run. Declare which window set it runs on.
- **Verified:** yes.

**10. `run_cell` and `apply_controls` implement the rule the page replaced**
- **Where:** the leak-bounds amendment. Code: `surrogate_discriminator.py:468-506`; `tools/probe_discriminator.py:136-160`.
- **Issue:** Two differences:
  - `apply_controls` voids on the positive control's P < 0.05 and on a single negative seed. The page requires the positive control's lower bound above 0.55, and 4 or more of 20 seeds.
  - `run_cell` reuses one seed for the candidate and both controls.

  Nothing in `src/`, `tools/` or `tests/` computes a flag rate or a seed-distribution rule. That code is still to be built, as the page says.
- **Severity:** medium.
- **Fix:** The runner must not call `run_cell` or `apply_controls`. Write the new rule beside them, plus the test the page asks for: it must fail if the rule is reverted to the single-seed form.
- **Verified:** yes.

**11. Window layout and loading: reuse existing helpers and the canonical window rule**
- **Where:** the "which windows count" amendment.
- **Issue:** Code already covers most of this:
  - `probe_discriminator.analysis_windows` (`tools/probe_discriminator.py:56-66`) gives the layout without drawing surrogates. Windows are `floor(60/dt + 0.5)` frames from `window[0]`, and the trailing partial window is dropped. Interior windows are `windows[1:-1]`, and the pair count is `len` of that.
  - Edge band: `max(1, floor(5/dt + 0.5))` frames (`:85`).
  - `edge_thinning`'s tiles (`surrogates.py:268-272`) start at the same frame with the same rounding, so they coincide with the analysis windows.
  - Do not load through `measure_recording_identity.load`. It carries its own `baseline_window_sec` copy (`:73-82`), which ignores designated baseline labels and skips recordings without regions; it uses `int(round(60/dt))` for window length. Use `ss.recordings_from_slices` (`surrogate_stats.py:163-232`), which goes through `generation_window` (`assess_folder.py:80-103`, "so the surrogate screen reads the same rule rather than a sixth copy").
  - If the Cossart folder declares no regions, its window runs to one frame past the last onset (`surrogate_stats.py:196-202`), so its last window's end band always holds that onset. Interior windows absorb this.
- **Severity:** low.
- **Fix:** Import `analysis_windows` by path, as `probe_discriminator._screen_tool` already does for `params_for`, or promote it into `src/`. Load with `recordings_from_slices`.
- **Verified:** yes for the code. Whether the Cossart folder has regions is not verified; I read no data.

**12. The can-pass check needs no new code**
- **Where:** the can-pass amendment.
- **Issue:** `ss.draw_surrogates("rigid_shift", recs, 2, cell_id, lambda r: params_for(cell, r.dt))` gives two independent draws: the key carries the draw index (`surrogate_stats.py:966-968`). Then `sd.pair_features` and the refitting bootstrap. J in seconds becomes frames through `params_for` as `round(J/dt, 9)` (`tools/build_surrogate_screen.py:163-164`), which the runner must reuse.
- **Severity:** none (confirmation).
- **Fix:** Reuse as described.
- **Verified:** yes.

**13. The page's claim about entry points is stale**
- **Where:** page line 166 ("The discriminator has no command-line entry point today").
- **Issue:** The module has none, but two tools already drive `forced_choice` from the command line: `tools/probe_discriminator.py` (controls only) and `tools/measure_recording_identity.py`. The overnight leak run itself was driven from scripts outside the tree (`probe_discriminator.py:16-18`).
- **Severity:** low.
- **Fix:** Name both tools as the pattern the runner copies.
- **Verified:** yes.

**14. Mouse-count guard for Cossart and for smoke runs**
- **Where:** leak bootstrap on the Cossart folder, and the `--limit` smoke run.
- **Issue:** `mouse_folds` raises when fewer than 2 distinct mice are present (`surrogate_discriminator.py:202-203`). Mouse is `subject_id`, falling back to `slice_id` (`surrogate_stats.py:226`). A bootstrap resample, or a first-N `--limit` (`build_surrogate_screen.py:760-761`), can go below that on a folder with few subjects.
- **Severity:** low.
- **Fix:** Report the Cossart mouse count before scoring, and make `--limit` sample by mouse.
- **Verified:** no (Cossart mouse count not read).

### Count gate

**15. No occupied-frame count exists, and "the input tube sees" uses a different framing**
- **Where:** the count-gate amendment ("occupied frames … That is the input `tube` sees").
- **Issue:** No code counts occupied frames. `summarize` counts onsets (`surrogate_stats.py:389`). On the screen's frames the count is `np.unique(train[(t >= a) & (t < b)]).size`, where frames are rounded to nearest, halves away from zero (`surrogate_stats.py:131-137, 211-212`). The encoder that feeds `tube` does something else: it frames by truncation, `((v - t0)/dt).astype(int64)`, from the recording's extent start (`src/bugarach/learn/encode.py:119`). Onsets at exact frame multiples are framed one frame early 4.5 % of the time by float truncation. The two grids merge onsets differently.
- **Severity:** medium.
- **Fix:** Declare the grid. Either count on the screen's rounded frames and drop "the input tube sees", or count through `encode`'s framing, and file the truncation as a separate defect.
- **Verified:** yes (1,632 of 36,000 on-grid frames misframed).

**16. The within-mouse average does not match `mouse_bootstrap`'s weighting**
- **Where:** the count-gate amendment ("surrogate minus real, averaged within mouse").
- **Issue:** `mouse_bootstrap` computes a pair-weighted mean over resampled mice (`measure_recording_identity.py:193-197`), not a mean of per-mouse means. The page also does not say whether the ±2 % denominator is the fixed point estimate or recomputed per resample.
- **Severity:** low.
- **Fix:** State pair-weighted (matches the leak gate) or equal-mouse weighting. Fix the denominator at the real point estimate.
- **Verified:** yes.

**17. The `edge_thinning` control at a fixed 5 s works as written**
- **Where:** the count-gate control.
- **Issue:** `params_for` with `{"name": "edge_thinning", "J": 5.0, "J_unit": "sec"}` gives `J = 50.0` frames and `analysis_window = 600` (`build_surrogate_screen.py:165, 170-171`). The generator is uniform dither per tile, dropping what leaves the tile (`surrogates.py:783-817`). The expected onset loss is J/(2·window) = 50/1200 = 4.17 % per full window, which matches "about 4 %". It is equal in every window, including interior ones. On occupied frames the loss is slightly larger, because dither can move two onsets into one frame. The control is tested (`tests/test_surrogates.py:535`).
- **Severity:** none (confirmation).
- **Fix:** Reuse through `params_for`.
- **Verified:** yes (derivation by hand).

### Randomness

**18. The salting test's reference scheme is only partly in the tree**
- **Where:** the randomness amendment ("no key equals one that `tools/build_surrogate_screen.py`'s 2026-09-11 scheme would produce").
- **Issue:** Part of the scheme is in that tool:
  - Surrogate keys: `(recording_id, stream, cell_id, draw)` (`surrogate_stats.py:968`).
  - Twin keys: `build_surrogate_screen.py:558-562`.
  - Destruction key: `surrogate_stats.py:1227`.
  - Freeze-half key: `surrogate_stats.py:1234`.
  - Assessor seed: the constant 20260722 (`surrogate_stats.py:1176`, also the production default at `assess.py:381`).

  The leak test's fold seeds and negative-control seeds came from scripts outside the tree, so they cannot be checked against that tool. Tuple keys that include the tag differ trivially; the collisions that matter are between the derived 32-bit seeds.
- **Severity:** medium.
- **Fix:** Test derived *seeds* against an enumerated old set: screen keys, overnight integer seeds 0 to 19, and 20260722. Add the freeze-half key to the salted list, and use the existing `seed_of` helpers (`surrogates.py:119`, `surrogate_stats.py:118`) rather than a new hash.
- **Verified:** partly. In-tree keys yes; the overnight leak seeds come only from the todo's "seed 0 of 20".

### Per-group reporting

**19. Per-group helper exists; the page's reported quantities need definitions**
- **Where:** the groups amendment and page line 56.
- **Issue:**
  - `by_group` (`measure_recording_identity.py:225-233`) computes each group's accuracy as the subset of *pooled-fit* correctness. The page does not say whether a group's leak point estimate is that or a refit within the group.
  - "Zero-event share" (groups amendment) and "share of ROIs rigid shift cannot change" (line 56) are different quantities. `SurrogateResult.unchanged` (`surrogates.py:246`) also counts active ROIs whose offset rounds to zero frames, which happens with probability 1/(2J): about 3 % at 16 frames, 1 % at 50 frames. Zero-event share is `info["n_in"] == 0` (`surrogates.py:252`).
  - Group labels: `recordings_from_slices` maps an empty `group_id` to `None`, where `measure_recording_identity` uses `""`.
- **Severity:** low.
- **Fix:** Reuse `by_group`'s subsetting, and declare pooled-fit subsetting. Report zero-event share from `n_in` per interior window, and label it as distinct from the unchanged share.
- **Verified:** yes.

---

## Summary for the main thread

**Should the runner reuse existing code?** Yes for:
- `recordings_from_slices` and `params_for` for loading and parameters
- `draw_surrogates` with `generate` for surrogates: `rigid_shift`, `uniform_dither`, `edge_thinning`, `homogeneous_resample`, `do_nothing`
- `pair_features` and `analysis_windows` for the leak pairs
- `negative_control_pairs`, after the pairing fix in finding 9
- `destruction_twins`, `coact_excess` and `destruction`, after the changes in findings 1 and 2
- `seed_of` for salting

**What cannot run without changing code:**
- **`destruction`:** four changes (assessor seed, per-draw values, twin index in the key, salted freeze-half key), plus the bin in seconds.
- **Refitting bootstrap:** needs a public cross-validation scorer; `cv_correct` is currently private internals wrapped in a tool.
- **Twin construction:** has to be pulled out of `prepare_stream`.
- **Seed range:** fold and control seeds need masking to avoid the `seed + 1` crash.

**Named on the page but not present, or not what it says:**
- **`mouse_bootstrap`:** does not refit and is fixed at 95 %.
- **Saturation table:** the report's formula is a different quantity under a different model.
- **Count and voiding code:** no occupied-frame count and no seed-distribution rule exist yet (the page lists both as to be built).
- **Salting test:** the leak test's old seed scheme is not in `build_surrogate_screen.py`.
