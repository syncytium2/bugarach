GRANT 7 ok — Read, Grep, Glob, Bash

Role 7, reuse auditor. Round 1 findings on `docs/proposals/2026-09-25-hebbian-coupling-detector.md` (bugarach at b190f02, clamor at c25c7e5).

**Bottom line:** the proposal says to copy clamor's `coactivity()` and `control()` out on their own. That does not work as the proposal assumes (R1–R4). It also names two things to reuse that do not exist: planted overlapping groups in time, and stored STTC matrices (R5, R6). Everything else it names does exist and should be called directly (R7–R13). No torch was installed in this environment, so the clamor behaviour was worked out by reading the code, not by running it. The arithmetic for R1 and R2 is shown in each row.

Columns: location · issue · severity · suggested fix · verified against a source (yes/no)

**R1** · "How the code arrives" (lines 163–165) and the proposal's claim that the 1986 bound keeps every coupling within 80 % of its resting value (lines 47–50)
- **Issue:** copying `control()` alone loses the bound. `control()` (`clamor:clamor/malsburg1986.py:239-248`) only computes q(s). The clamp to `[S_MIN, S_MAX]` is in `modulate()` (`malsburg1986.py:277`, `.clamp(S_MIN, S_MAX)`), with the constants at lines 84–85. clamor's own comment at lines 86–96 says one step at rest is 1.04× the half-range (`Q0_OVER_HALF_RANGE`). So a single Co = +1 update from s₀ = 0.012 lands at 0.022, past S_MAX = 0.0216. There q(s) = 0.01·(1 − (0.010/0.0096)²) ≈ −0.00085, which is negative: after that, a coincidence pushes the coupling *down* and a near-miss pushes it *up*. Without the clamp, "stays within 80 %" is false at the paper's q₀.
- **Severity:** HIGH
- **Fix:** also take `S_MIN`/`S_MAX` and apply the clamp after every update. Better, take them from a verbatim vendored copy of the module (see R4). Say in the proposal that the bound comes from q(s) *plus* the clamp, not from q(s) alone.
- **Verified:** yes (source read; arithmetic from the file's own constants)

**R2** · Kernel bullets (lines 62–72): "call clamor's `coactivity` with period 2w and burst w"
- **Issue:** `coactivity` cannot be called with plain float arguments. At `malsburg1986.py:233-236`, `edge = burst / 2.0` followed by `edge.clamp(...)` and `(half - edge).clamp(...)` needs `burst` to be a torch tensor; a Python float raises `AttributeError`.
- **Severity:** MEDIUM
- **Fix:** state the calling contract: tensors in, numpy↔torch conversion at the boundary, since bugarach's detectors are all numpy.
- **Verified:** yes (source read, not executed)

**R3** · Same bullets, and "Pairs further apart than w contribute nothing" (line 63)
- **Issue:** `coactivity` wraps Δt modulo the period (`malsburg1986.py:231`, `dt - period*torch.round(dt/period)`). With period 2w, a pair 2w apart folds back onto Δt = 0 and scores **+1** (full coincidence). In clamor the far-pair gate (the `seen` mask, lines 268–275) lives in `modulate()`, which is not being copied, and clamor's own comment (lines 265–268) warns that the wrap "would otherwise fold a cell silent for several periods back onto coincidence". Nothing in the copied pair does the ±w cutoff.
- **Severity:** HIGH
- **Fix:** the bugarach caller must drop |Δt| > w **before** calling `coactivity`, and a test should pin Co(2w) as never applied. Also note the round-half-to-even behaviour at exactly ±w: `torch.round(±0.5)` gives 0, so Co(±w) = −1 as the proposal wants. Keep that in a test.
- **Verified:** yes (source read)

**R4** · "How the code arrives": the vendoring convention
- **Issue:** copying two methods out of a class and putting them in `src/bugarach/detectors/` does not fit the convention it cites.
  - Every existing vendored family is a **whole file or whole package copied verbatim**:
    - `docs/session_protocol.md` line 1
    - `tools/murderboard_freshness.sh` line 2
    - `third_party/draughtsman/__init__.py` lines 1–2: "re-copy the whole package"
    - the armory files
  - An excerpt of two `@staticmethod`s, plus the module constants they need (`Q0`, `S0`, `S_D`, `S_MIN`, `S_MAX`; `control` reads `S0`/`S_D` as module globals and cannot take a different s₀), plus the gating from `modulate`, is an **adaptation**. Its "never edited in place" stamp could not be checked: nothing diffs an excerpt against upstream.
  - The freshness gate (`tools/check_vendor_freshness.sh:72-160`, `tools/murderboard_freshness.sh:470-530`) compares the **stamp sha with the upstream repo HEAD**, not per file. A clamor family would therefore go STALE on every clamor commit, related or not.
  - clamor is private, so the family needs the `--clone` / `BUGARACH_<NAME>` env pattern that draughtsman and armory use (`check_vendor_freshness.sh:128-163`).
- **Severity:** HIGH
- **Fix:** vendor `clamor/malsburg1986.py` **whole and verbatim** into `third_party/clamor/`, following the draughtsman precedent. It is self-contained (imports only `math` and `torch`; 716 lines; no personal paths, so SAP004 is clean). Then import `CocktailParty.coactivity`, `CocktailParty.control`, `S_MIN` and `S_MAX` from it, and add family 5 to `check_vendor_freshness.sh` with `BUGARACH_CLAMOR`. Alternatively, drop the copy: at the one kernel point used, Co = cos(πΔt/w). Write it natively and add a parity test against clamor's `selftest()` values.
- **Verified:** yes

**R5** · "How the code arrives": torch in `detectors/`
- **Issue:** `src/bugarach/detectors/__init__.py:55-80` imports every detector eagerly, and the whole package is numpy-only. torch is used only under `learn/` and `lab.py`, and is an optional extra (`pyproject.toml`: `dl`, `dev`). CI installs it (`.github/workflows/ci.yml:69-73`), so the proposal's CI claim holds. But a torch module under `detectors/` would break `import bugarach.detectors` on a core install.
- **Severity:** MEDIUM
- **Fix:** keep the torch import lazy, or put it outside the eager `detectors/__init__` imports (with R4's `third_party/` placement).
- **Verified:** yes

**R6** · Stage 1 (lines 144–145): "planted overlapping groups at the strengths `tools/assembly_power.py` already plants"
- **Issue:** no existing generator does this.
  - `tools/assembly_power.py:99-129` (`simulate_slice`) plants **one** non-overlapping assembly (ROIs 0..size−1) in an **events × ROI membership matrix with no time**. Its docstring, lines 20–23, says onsets are "not modelled". The Hebbian rule needs onset times.
  - `src/bugarach/simulate.py:429` (`simulate_coordination`) has onset times, but draws each planted event's participants uniformly (`rng.choice(nR, …)`, `simulate.py:845`), so it has no fixed or overlapping groups.
  - Stage 1 therefore needs new planting code.
- **Severity:** HIGH
- **Fix:** add a group-membership option to `simulate_coordination` rather than a separate generator, so the existing machinery comes along:
  - background rate spread: `bg_rate_shape`, `bench.MEASURED_RATE_SHAPE`
  - burstiness over time: `bg_burst_shape`
  - refractory floor: `bg_floor_sec`, which the "does not claim" section needs
  - frame grid: `grid_sec` plus `_quantize`, `simulate.py:320`
  - `GroundTruth`, for scoring

  Define "strength" exactly as `assembly_power.simulate_slice` does (the fraction of events recruited from the assembly) so its power curve carries over. Reword the sentence so it does not claim this already exists.
- **Verified:** yes

**R7** · Check A (lines 122–125): "On the existing STTC matrices of the baseline windows"
- **Issue:** no STTC matrices are stored. `tools/modularity_null.py:102-108` builds them inside `graph.modularity_vs_null` (`src/bugarach/graph.py:297`) and writes only summary rows (Q, meanSTTC). They are also built at a tile of **dt = 2.0 s** (`modularity_null.py` `--dt` default), much wider than the proposal's w of 0.2–0.5 s. The existing STTC-graph null is **jitter** (`graph.jitter_trains`, `graph.py:249`, ±20 s), not circular shift. So Check A's "same share on circular-shift surrogates" is a different null from the one behind the modularity negative it wants to extend.
- **Severity:** MEDIUM
- **Fix:** recompute with `graph.sttc_matrix(trains, dt, t0, t1)` (`graph.py:128`). State the dt, and state which null and why. For comparability with the modularity result, reuse `jitter_trains`; if circular shift is chosen, justify it. Reuse the baseline-window selection too (see R11).
- **Verified:** yes

**R8** · Check B (lines 132–135): "rank correlation between D and the STTC matrix at the same w"
- **Issue:** use `graph.sttc_matrix(trains, dt=w, t0, t1)` (`graph.py:128-148`). Its conventions differ from D's:
  - the diagonal is 1.0
  - a pair is **NaN** when either ROI is empty (`graph.py:93-106`, "undefined, not zero")

  D for a silent ROI is exactly 0. A rank correlation over all pairs would compare NaN with 0 or drop those pairs inconsistently.
- **Severity:** MEDIUM
- **Fix:** correlate only the off-diagonal pairs where STTC is defined, and say so.
- **Verified:** yes

**R9** · Readout 1 (lines 99–102): circular-shift surrogates via `assess.circular_shift_trains`
- **Issue:** the reuse is correct, but the proposal does not state the function's contract (`src/bugarach/assess.py:340-353`):
  - trains must be **relative to the window start**, over `win_dur`
  - `rng` must be a `np.random.RandomState`: it calls `random_sample`, which `np.random.Generator` does not have
  - it draws exactly one uniform per ROI per call; that draw order is what the parity fixtures rest on
- **Severity:** LOW
- **Fix:** state the contract, and seed a `RandomState` the way `assess.py:545` does.
- **Verified:** yes

**R10** · Readout 3 (lines 107–110): "threshold set on the circular-shift surrogates", "comparable with the six coded ones"
- **Issue:** two unstated choices, both with existing machinery.
  - **The null.** CoactDetect, the comparator, does not use the assessor's whole-window shift. It uses a **rolling, rate-local** circular-shift null with α and a context window (`src/bugarach/detectors/coact.py:65-83`; sliding variant `_coact_sliding`, `coact.py:310`). The proposal does not say which null readout 3 uses. Mixing the two would confound the "does readout 3 beat CoactDetect" test.
  - **Registration.** A seventh detector must be registered in:
    - `detect_folder.DETECTORS` (`src/bugarach/detect_folder.py:116`)
    - `bench.OPERATING_POINTS`, read by `detector_params` (`detect_folder.py:454`)
    - `DISPLAY_NAMES` (`src/bugarach/detectors/__init__.py:33`)
    - `with_microscope` (`detect_folder.py:490`): this is where the frame interval reaches a detector, and the proposal's w and frame-grid lags should come from there, not from reading `slices.csv` directly

    The package docstring (`detectors/__init__.py:3-4`) also says each detector "lands only with a MATLAB parity test", which this one cannot have.
- **Severity:** MEDIUM
- **Fix:** name the null (the rate-local one, to match CoactDetect). Add a registration paragraph naming these entry points and saying how the parity-test convention is waived.
- **Verified:** yes

**R11** · Readout 3's active set A(t), and the frame grid (lines 80–84, 107)
- **Issue:** existing code covers this.
  - `learn/encode.encode` (`src/bugarach/learn/encode.py:96-139`) already builds the per-frame onset raster with a required `dt`. Its `Detection.to_seconds` (`encode.py:79-86`) is the output contract `score_stream` reads.
  - Caveats if reused: `encode` **reorders ROIs busiest-first** (`enc.order`), so D's rows must be mapped through `order`. It floors each onset to a frame.
  - Onsets are `t50rise` (`docs/export_folder_spec.md:313,322`), a half-rise time, and the export spec does not say they sit on the frame grid. The trapezoid argument (whole-frame lags only) holds only after the same flooring.
  - For ROI-distinct counts per bin, `detectors/_shared.distinct_coact` (`_shared.py:63`) exists.
- **Severity:** MEDIUM
- **Fix:** build A(t) with `encode` (or `distinct_coact`), and say that onsets are floored to frames before lags are taken. The trapezoid weighting depends on that step.
- **Verified:** yes (for the claim that the spec does not state onsets are on the grid)

**R12** · Stage 0 / Stage 2: baseline windows and the dataset
- **Issue:** there are already three baseline-window selectors:
  - `detectors/loco.effective_region_windows`, used by `assess.py:485`
  - `tools/modularity_null.py:45`, `baseline_window`
  - `tools/measure_recording_identity.py:73`, `baseline_window_sec`

  The proposal must not add a fourth. The input should come from `dataset.default()` (`src/bugarach/dataset.py:448`) or `_dataset_arg`, as `tools/modularity_null.py:66` does, so the contamination stop in `dataset.current()` (`dataset.py:546`) is inherited.
- **Severity:** LOW
- **Fix:** name `effective_region_windows` as the window source (the assessor's own, so the circular-shift null lines up) and `dataset.default()` as the input.
- **Verified:** yes

**R13** · Readout 1 and Check A: "leading eigenvalue"
- **Issue:** `assembly.stat_eigen` (`src/bugarach/assembly.py:159-175`) **cannot** be reused on D. It z-scores an events × ROI membership matrix and returns the leading eigenvalue of the ROI correlation matrix. The proposal already says this at lines 124–125, correctly. Use `np.linalg.eigvalsh` on the symmetric D. No existing helper computes Check A's "residual variance after the leading eigenvector".
- **Severity:** INFO (no defect)
- **Fix:** none.
- **Verified:** yes

**R14** · Stage 2 (line 147): order DI, OVX, MALE, ORX
- **Issue:** the prose is correct. Code must take the order from `bugarach.groups` (`GROUP_ORDER` at `src/bugarach/groups.py:16`; `in_group_order` at `groups.py:29`); `tests/test_group_order.py` enforces this.
- **Severity:** LOW
- **Fix:** name `in_group_order` in stage 2.
- **Verified:** yes

**R15** · Readout 2 (lines 103–106): "an overlap-tolerant grouping (mixed-membership or link communities)"
- **Issue:** **bugarach has no overlap-tolerant community method.** `graph.py` offers only `louvain` and `modularity` (`graph.py:151,221`), which produce a partition. Searching `src` and `tools` for link communities, mixed membership, stochastic block models, BigCLAM, NMF and clique percolation finds nothing. The only mentions are in docs, including the todo `docs/todo/2026-08-20-what-could-still-overturn-the-assembly-negative.md:21-22`. This is genuinely new code (or a new dependency), and the proposal does not scope it, name a library, or say whether it gets a clean-room spec.
- **Severity:** MEDIUM
- **Fix:** name the method and where it comes from, and say it is new. If the method is a published algorithm implemented in-house, consider the `docs/clean_room/` route.
- **Verified:** yes

**What I checked:** I compared every planned piece with the existing code:
- `graph.py`: `sttc`, `sttc_matrix`, `jitter_trains`, `modularity_vs_null`, `louvain`
- `assess.py`: `circular_shift_trains`, and `assess_coactivity`'s RNG and windows
- `assembly.py`: `stat_eigen`, `stat_dispersion`
- `tools/assembly_power.py`: `simulate_slice`
- `simulate.py`: `simulate_coordination`'s participant draw
- `detectors/coact.py`, `_shared.py` and `__init__.py`
- `detect_folder.py`: `DETECTORS`, `detector_params`, `with_microscope`
- `learn/encode.py`
- `dataset.py`, `groups.py`
- `tools/modularity_null.py`
- the vendoring gate (`check_vendor_freshness.sh`, `murderboard_freshness.sh`) and the stamps on `docs/session_protocol.md`, `tools/murderboard_freshness.sh` and `third_party/draughtsman/__init__.py`
- `pyproject.toml` extras and the CI install
- `clamor:clamor/malsburg1986.py`: the constants, `coactivity`, `control`, `modulate`, `selftest`, imports, and a personal-path scan
- a tree-wide search for overlap-tolerant community methods

I did not assess the licence claim, the q₀ discrepancy or the rate-neutrality derivation beyond the kernel's call contract; those belong to other roles.
