GRANT 7 ok — Read, Grep, Glob, Bash

Role 7, reuse auditor. I checked the plan `docs/proposals/2026-09-25-hebbian-coupling-detector.md` and the tool `tools/make_hebbian_kernel_figure.py` against the code they reuse or redo: `graph.py`, `surrogates.py`, `assembly.py`, `simulate.py`, `bench.py` / `bench_slow.py`, `detect_folder.py`, `detectors/loco.py`, `learn/encode.py`, `groups.py`, `paths.py`, `tools/modularity_null.py`, `third_party/draughtsman/`, `tools/check_vendor_freshness.sh`, 20+ sibling `tools/make_*_figure.py`, and `clamor:clamor/malsburg1986.py` at c25c7e5. I edited nothing and wrote nothing to scratch. The only thing I ran was one read-only import of the tool's own functions, to redo panel B at the current jitter values.

## Findings

Columns: location · issue · severity · suggested fix · verified against a source.

**1.** Tool L36 (`SIGMA_SEC`); plan L74–75 and L262–267 (the ⚠ on σ, and "m is frozen only after it is re-measured").
- **Issue:** the jitter is typed in by hand as 0.106 s fast and 0.135 s slow. Tested production code already holds the re-measurement the ⚠ is waiting for. `src/bugarach/bench.py:930` has `BENCH_RECORDING["jitter_sec"] = 0.105`, and `src/bugarach/bench_slow.py:182` has `0.131`. Both were "re-measured 2026-09-23 on the default folder's 66 recordings" (bench.py ~L960–971, bench_slow.py L206–209, commit 65f3ac7). So the figure uses stale values, and the plan's ⚠ and its freezing condition are already met.
- **Effect:** re-running the tool's own `lag_distribution` at the current values moves B slightly. At m = 2 frames: fast expected Co goes 0.144 → 0.147, slow 0.084 → 0.090. The share of negative updates barely moves (fast 22.5% → 22.4%).
- **Severity:** medium.
- **Fix:** import σ from `bench.BENCH_RECORDING["jitter_sec"]` and `bench_slow.BENCH_RECORDING["jitter_sec"]`. Cite the 2026-09-23 run folder instead of `decisions_pending.md` item 2. Drop or rewrite the two ⚠s, and re-quote "0.144" and "about seven coordinated pairs".
- **Verified:** yes.

**2.** Plan L103–104, readout 1: "onsets jittered uniformly within ±20 s and snapped to frames (`graph.jitter_trains` …)".
- **Issue:** `graph.jitter_trains` (`src/bugarach/graph.py:249–265`) does not snap to frames. It moves each onset in continuous time and wraps it inside the window. The null that is "±J, wrapped, snapped to frames" already exists as `surrogates.shipped_dither` (`src/bugarach/surrogates.py:297–317`). It wraps `jitter_trains` exactly as `modularity_vs_null` draws, drops inactive ROIs, rounds to frames, and uses keyed seeds, and a test covers it (`tests/test_surrogates.py:200`). As written, the plan names the wrong function, and new snapping code would be a third implementation.
- **Severity:** medium.
- **Fix:** name `surrogates.shipped_dither`, or `surrogates.generate("shipped_dither", …)`, for the frame-grid form. If continuous time is meant, drop "snapped to frames". Either way, say that the null wraps: the "seam" the `shipped_dither` docstring describes comes with it.
- **Verified:** yes.

**3.** Plan L132–147, the busy-core check (STTC matrices, jitter surrogates, 95th percentile, 200 surrogate draws, baseline windows).
- **Issue:** almost all of it already exists as the modularity pipeline. `tools/modularity_null.py` is the folder driver: `_dataset_arg`, `load_folder`, its own `baseline_window()` at L45, and a deliberate choice of `t50rise` over `locs` at L96–100. `graph.modularity_vs_null` (graph.py:297) does the surrogate loop: drop inactive ROIs, NaN → 0, zero the diagonal, 200 draws, jitter 20 s. It takes the percentile with `matlab_prctile` (`detectors/_shared.py:40`), and sapper SAP001 forbids the numpy form. The plan names none of these. Three details must match the reference:
  - (a) Percentile: use `matlab_prctile`.
  - (b) Negative weights: `modularity_vs_null` clips negative STTC to 0 because Louvain needs it. An eigenvalue check must not copy that step.
  - (c) Baseline window: `modularity_null.baseline_window` (longest `base*` region, the producer's analysis window) is not the `effective_region_windows` the detector section cites (`detectors/loco.py:300`). For "the null behind the modularity result" to hold, the check has to use the modularity tool's window.
- **Severity:** medium.
- **Fix:** add the second-to-fourth-eigenvalue statistic inside `modularity_null.py`'s loop, or a sibling that reuses its loader and window. State which baseline-window function is used, and state that the percentile is `matlab_prctile`.
- **Verified:** yes.

**4.** Plan L108–115, readout 2 ("the fixed-margin (curveball) null the assembly report uses").
- **Issue:** the curveball already exists: `assembly._trade` and `pvalues_margin` (`src/bugarach/assembly.py:193–252`), over `membership_matrix` built from `Assessment.members`. The reference's own docstring (assembly.py L15–38) says the margin null "goes blind exactly where the signal is purest" and is always read beside `pvalues_uniform`, "never alone". The plan uses the margin null alone, which departs from the reference.
- **Severity:** medium.
- **Fix:** build the timed-train null on `_trade` / `pvalues_margin`, curveball over membership with onset times carried along, instead of a fresh implementation. Add the uniform-participation companion null (`pvalues_uniform`) and the reference's two-null reading table, or say why one null is enough here.
- **Verified:** yes.

**5.** Plan L258–261, "One update per pair of onsets, symmetric", and L268 ("the clamp in clamor's `modulate()`").
- **Issue:** clamor's `modulate()` (`malsburg1986.py:250–285`) is not what the detector can call, and the plan does not say so:
  - It pairs a cell's new break-off with each other cell's most recent break-off only (`last_break`). It does not pair with every onset within the gate.
  - It computes a whole row's deltas from the row's pre-update values, and then clamps.
  - It resets the diagonal to 0 after the clamp.
  - Its gate is `period + burst/2` = 2.5m.

  All-pairs, sequential, symmetric updates are a deviation from "only the most recent break-off" that the plan does not list, and the result depends on update order because q depends on s. The detector will reuse only `coactivity`, `control`, `S_MIN` / `S_MAX` and the constants, and will re-implement the update loop.
- **Severity:** medium.
- **Fix:** add "all onsets within ±m, not the partner's most recent break-off" to the list of deliberate deviations. Say that `modulate()` is not called, and that the new loop must match it on: clamp to [`S_MIN`, `S_MAX`] after each step, keep the diagonal at 0 (or never touch it), and fix an update order (simultaneous per arriving onset, as `modulate` does per row). Also say clamor's default dtype is float32, and the boundary conversion should choose float64.
- **Verified:** yes.

**6.** Tool L45–56 (`weight`, `lag_sum`) and L71–72 (`q`), against clamor `coactivity` (L208–237) and `control` (L240–248).
- **Issue:** the figure re-implements the kernel and the step instead of calling the source it describes, and no check ties the two together.
  - `q(s)` matches `control()` exactly, and `S0`, `S_D`, `Q0`, `S_MIN`, `S_MAX` match clamor L79–86.
  - `cos(πk/m)` equals `coactivity(k, period = 2m, burst = m)` for |k| ≤ m. At |k| = m clamor gives −1 (`torch.round` keeps the lag at ±m), so the half-weighting is new code on top of the source.
  - Once the vendored copy lands, the figure and the detector will be two separate implementations of the half-weighted kernel.
- **Severity:** low.
- **Fix:** keep the torch-free figure, but give the half-weighted kernel exactly one home (for example the detector module, with a pure-math form) and have the figure import it. Add a test that asserts `weight(k, m)` equals `coactivity(k, 2m, m)` for |k| < m, where torch is available. Also wire clamor's own `selftest()` into the suite once it is vendored, as the clean-room harnesses are.
- **Verified:** yes.

**7.** Tool L249–256 (the darkroom fallback).
- **Issue:** the tool departs from the sibling convention three ways:
  - (a) It calls `darkroom(FIGURE_ID)`, which writes into `<darkroom>/bugarach/hebbian_kernel/`. The figure tools' `darkroom()` calls (about 20) almost all write to the darkroom root; one reuses a single `detector_history` folder.
  - (b) When the darkroom does not resolve, it prints its own message instead of the shared `paths.unresolved_message()`, which 103 tool call sites use.
  - (c) With `--also` given it writes only the repo copy and returns 0. `make_modularity_figure.py` L228–232 prints `unresolved_message()` and returns 1. That is the "in the repo is not delivered" failure CLAUDE.md records from 2026-08-18.
- **Severity:** medium.
- **Fix:** use `dest = Path(a.out) if a.out else darkroom()`, and if it is `None`, print `unresolved_message()` and return 1, as the siblings do.
- **Verified:** yes.

**8.** Tool L210–227 (`_render_png`).
- **Issue:** a new copy of the per-tool Playwright helper, with a new environment variable, `BUGARACH_CHROMIUM`. It appears nowhere else in the tree: no tool, doc or setup note. There is no shared helper (about 20 tools each carry their own `_render_png`), but `make_mechanism_figure.py:187` shows the reuse route: `from make_diagnostic import _render_png`. That helper takes HTML, not SVG. It uses `full_page=True`, which `make_diagnostic._render_png`'s docstring warns pads to the viewport; that is harmless here, since the SVG is exactly the viewport size.
- **Severity:** low.
- **Fix:** drop `BUGARACH_CHROMIUM`, or document it in `docs/windows_workstation_setup.md` / the machine-local inventory, because an undocumented environment variable is configuration nobody can find. Optionally file the case for a shared `render_png` helper, since this is copy number 20-something.
- **Verified:** yes.

**9.** Tool L35 (`FRAME_SEC = 0.1`, "about 0.1 s").
- **Issue:** the frame interval is typed in by hand. The simulator's default is `simulate_coordination(grid_sec=0.1)`, and `BENCH_RECORDING` sets no `grid_sec`, so 0.1 s matches the reference. But the value on the default dataset is per recording (`frame_interval_sec` in `slices.csv`, `store.validated_dt`), and the plan says m is set per recording from "each recording's own frame interval".
- **Severity:** low.
- **Fix:** cite the simulator default as the source of 0.1, and say in the caption that panel B assumes 0.1 s frames. Optionally print the spread of the real `frame_interval_sec` values.
- **Verified:** yes (the code). I did not read the real `slices.csv`.

**10.** Plan L301–304: "registers where the six do (`detect_folder.DETECTORS`, the operating points, the display names). It takes its frame interval from `with_microscope` …".
- **Issue:** all the named entry points exist, but the list of places to register is incomplete, and one is misdescribed:
  - `DETECTORS` (detect_folder.py:116) is a literal six-tuple, and it has companions: `FLAT` / `NESTED` (L114–115) and **`ONSET_FIELD`** (L130), which records which onset each detector anchors on. `t50rise` vs `locs` differ by about 0.3 s fast and about 2 s slow, which is several times the span m. The plan says "onsets" throughout and never names the field.
  - `with_microscope` (L490) branches by name, on `rate` and `cicada` only. It will not supply a frame interval to a seventh detector unless a branch is added.
  - `effective_region_windows` lives in `detectors/loco.py:300`, not `detect_folder`.
  - `DISPLAY_NAMES` is in `detectors/__init__.py:33`.
  - `bench` / `bench_slow` / `bench_combined` derive `DETECTORS` from `OPERATING_POINTS`.
  - `tests/test_webapp_tuned_on_raster.py:251` asserts exactly six.
- **Severity:** medium, for the missing onset field.
- **Fix:** name `ONSET_FIELD` and choose `t50rise`, matching `modularity_null.py` L96–100 and `learn/encode.encode(onset_field="t50rise")`. Add "a `with_microscope` branch" and the `FLAT` / `NESTED` membership to the list of registration sites. Flag the six-detector test.
- **Verified:** yes.

**11.** Plan L249 ("Onsets are floored to frames") and tool L65.
- **Issue:** frame binning already exists. `learn/encode.encode` floors onsets as `(v - t0)/dt` to int64, requires `dt`, and reads `t50rise` through `stream_trains`. Floor matches the plan. The simulator instead snaps with `matlab_round` (`simulate._quantize`, L320–331). For a uniform phase offset the lag distribution is the same either way, so the numbers in the figure are unaffected.
- **Severity:** low.
- **Fix:** reuse `stream_trains` and encode's binning (or its `raster`) in the detector instead of a new floor step.
- **Verified:** yes.

**12.** Plan L189–193, the simulation stage ("adds a group-membership option to `simulate_coordination`", "Strength keeps `assembly_power.py`'s meaning").
- **Issue:** the entry points exist and are described correctly. `simulate_coordination` (simulate.py:429) picks participants uniformly with `rng.choice(nR, …)` (L842) and jitters them with Gaussian `jitter_sec`. `assembly_power.simulate_slice` (L99–111) defines `strength` as the fraction of events drawn from the assembly. This is reuse, not reinvention. One point to state: the option must consume random draws only when it is switched on, so existing seeds still reproduce, as the floor mode does (L836–839).
- **Severity:** low.
- **Fix:** add "RNG stream unchanged when the option is off", and take the simulation's `jitter_sec` from `BENCH_RECORDING` (see finding 1).
- **Verified:** yes.

**13.** Plan L284–300, vendoring.
- **Issue:** consistent with the precedent.
  - `malsburg1986.py` imports only `math` and `torch`, so it can be copied as one file. By contrast, draughtsman was copied as a whole package and carries its stamp on `__init__.py`.
  - The stamp format the gate expects is `vendored from <owner/repo> @ <sha>` (`murderboard_freshness.sh` L1174). The draughtsman stamp reads `vendored from draughtsman @ 5705c46`, so it lacks the owner. The plan's `syncytium2/clamor` form is the better one.
  - The `BUGARACH_CLAMOR` / `--clone` pattern mirrors `BUGARACH_DRAUGHTSMAN` (check_vendor_freshness.sh L128–137).
  - The stamp line is necessarily an addition to the file. "Never edited" means apart from line 1, as with draughtsman.
- **Severity:** low.
- **Fix:** say "verbatim apart from the line-1 stamp" and "the gate lists `third_party/clamor/malsburg1986.py` as the family's file".
- **Verified:** yes.

**14.** Plan L185 and L304 (group order via `bugarach.groups`; `dataset.default()`).
- **Issue:** both entry points exist and are used correctly. `groups.GROUP_ORDER`, `group_key` and `in_group_order` are at `groups.py:17–31`, and `dataset.default()` is at `dataset.py:448`. The plan should also record `dataset.stamp()` in its results, as CLAUDE.md requires for anything scored.
- **Severity:** low.
- **Fix:** add "results record `dataset.stamp()`".
- **Verified:** yes.

## Summary

Nothing in the plan or the tool is a wholesale reinvention. The medium-severity items are reference values, nulls and conventions the project already has in tested code, which the artifact either hand-copies (the stale jitter, the darkroom fallback) or does not name:
- `shipped_dither` (finding 2)
- the modularity driver and window (3)
- the paired nulls in `assembly.py` (4)
- `modulate()`'s pairing semantics (5)
- `ONSET_FIELD` (10)

Finding 1 also changes a claim: the ⚠ about σ being measured on a superseded folder is out of date, because production code re-measured it on the default dataset on 2026-09-23.
