GRANT 7 ok — Read, Grep, Glob, Bash

**Reuse audit — "Reinventing the Wheel"**, on `docs/learned/tube_self_supervised/README.md`, its two PNGs, the four new tools, `nets/line.py`, `nets/line_length.py` and the `fair_bakeoff.py` edit, against the production code named in the brief. Root for every path below: `<worktree>/`.

---

### Finding — the stale model roster in Figure 2

- **Location** · `<worktree>/tools/make_tube_ssl_figure.py:29` — `MODELS = {"tube": (...), "tube_guard": (...)}` — against `<worktree>/tools/tube_self_supervised.py:62` — `MODELS = ("tube", "tube_guard", "line", "line_length")`.
- **Issue** · The figure tool keeps its own hand-maintained copy of the model roster and it was not extended when `line` joined. I rendered the PNG: Figure 2, learning from rigid shift alone, plots **two** architectures, while its caption says *"Four architectures … 288 fits"* and the two tables under it quote `line` and `line_length` numbers that are nowhere in the picture. This is exactly the failure `<worktree>/src/bugarach/learn/nets/__init__.py:107-111` exists to prevent — *"there is deliberately no list of architecture names here: a list is a second place to edit"* — and the roster is now duplicated in four places (`tube_self_supervised.py:62`, `tools/tube_ssl_real_compare.py:62`, `tools/probe_line_vs_fuzz.py:123`, `tools/make_tube_ssl_figure.py:29`).
- **Severity** · High (the figure contradicts its own caption and the tables beside it).
- **Fix** · Derive the roster from the results file — `sorted({r["model"] for r in R})` — and take colours from a keyed palette, so a new architecture appears without an edit. Until it is redrawn, the caption must say which two models are plotted.
- **Verified against a source** · Yes — read the PNG and both source lines.

### Finding — Panel A re-draws `make_bakeoff_summary_figure.py`, and re-introduces its murderboarded defect

- **Location** · `<worktree>/tools/make_line_sensors_figure.py:23-29, 49-56` against `<worktree>/tools/make_bakeoff_summary_figure.py:1-30, 51-60, 224-236`.
- **Issue** · The bake-off panel — one row per detector, fold range as a line, mean as a dot, read from `bakeoff.json` — already exists as panel A of `bakeoff_intervals`. The new copy hardcodes `ORDER` in **descending F1** (line, tube, tube_guard, line_length, coact, loco, … tiny, trace) and inks `line` and `line_length` in colour against everything else in grey. The existing tool's header records the opposite rule as a murderboard finding of 2026-09-07, roles 4, 8 and 10: *"grouped by family … and NOT sorted by score — a bar chart sorted by F1 says 'ranking' before its label is read, and at four folds this table is intervals, not a ranking."* The report's own ⚠ agrees (the gain is inside the fold spread) while its figure is ordered as a leaderboard with the new model on top. The copy also re-types the detector display names instead of taking `ui.app.TITLES` (with the `cicada` → `locust` darkroom override the existing tool documents), and drops the ceiling, distractor and probe context panels.
- **Severity** · Medium-high.
- **Fix** · Call `make_bakeoff_summary_figure.py` for the bake-off panel and keep the new tool for the probe panel; or, minimally, group by family, stop score-ordering, and import `TITLES`.
- **Verified** · Yes — both files read; ordering checked against the README's own F1 column.

### Finding — neither new figure tool defaults to the darkroom, and one figure never got there

- **Location** · `<worktree>/tools/make_line_sensors_figure.py:40` and `<worktree>/tools/make_tube_ssl_figure.py:41` — `ap.add_argument("--out", required=True)`.
- **Issue** · The house pattern is `--out default=None` plus `--also`, falling back to `bugarach.paths.darkroom(create=True)`; it is implemented in the tool these duplicate (`make_bakeoff_summary_figure.py:225-226` and `:236`) and in `<worktree>/tools/run_learned_on_folder.py:171-177`. The consequence is measurable, not hypothetical: `line_sensors_fig.png` — Figure 1, the headline result — **is not in the darkroom at all**, and the darkroom's `tube_ssl_fig.png` is a 15:28 render that differs byte-wise from the 23:18 copy in `docs/learned/`. That is the 2026-08-18 incident verbatim. Note for adjudication: sapper **SAP006 does not fire**, because its `include` is `tools/build_*.py` and `tools/md_to_page.py` (`<worktree>/tools/sapper.py:121-128`), so this is the open todo `docs/todo/2026-08-18-figure-tools-require-out.md` gaining two rows rather than a rule breach.
- **Severity** · Medium.
- **Fix** · Adopt `default=None` + `darkroom()` + `--also` in both tools, and push both current PNGs to the darkroom now.
- **Verified** · Yes — ran sapper, resolved `paths.darkroom()`, compared the two copies.

### Finding — `line._dog` is a third copy of the difference-of-Gaussians kernel, with two silent divergences

- **Location** · `<worktree>/src/bugarach/learn/nets/line.py:129-139` against `<worktree>/src/bugarach/learn/nets/tube.py:109-121` and `tube.py:238-254`.
- **Issue** · The arithmetic matches the reference **exactly** — same `clamp(0.5, k/2)` on the centre, same `clamp(1.5, max_ratio)` on the ratio, same area normalisation, same per-scale gain — so this is duplication rather than divergence, and the shared-helper module beside `_dilated_stack` (`nets/__init__.py:84-104`) is where it belongs. Two things do differ and neither is stated: (a) `line.py:112-113` initialises the DoG centres at `log(2.0 · 2**i)` where `tube.py:103` starts at `log(1.0 · 2**i)`, with Tony's reason for the one-sample start quoted in `tube.py:94-101` — `line`'s own comment at `line.py:103-106` claims *"the same starting point tube uses"*, which is true of `log_smear` and not of `log_center`; (b) the guard variant normalises with `.clamp_min(eps)` (`tube.py:252-253`) and `line._dog` has no such guard.
- **Severity** · Medium.
- **Fix** · Hoist `_dog(...)` into `nets/__init__.py` and have all three call it; then either match the one-sample start or record why the count kernel starts at two samples.
- **Verified** · Yes — line-by-line comparison.

### Finding — `line` inherits tube's raw-channel bypass and drops the warning that goes with it

- **Location** · `<worktree>/src/bugarach/learn/nets/line.py:156` — `channels = [count, resp]` — against `<worktree>/src/bugarach/learn/nets/tube.py:148-151`.
- **Issue** · `line` sends four **raw count** channels to the head alongside the four zero-integral responses. That is the same construction `tube` marks *"⚠ THE BYPASS. `bright` is an absolute activity level and it goes to the head alongside the zero-integral responses, so the kernel's DC invariance is not the model's"* — and `line` passes four such channels where `tube` passes one. `line.py:57-61` and the report's *"a rising background raises the count everywhere and cancels"* both state the invariance as a property of the model. The reference does not; it files the drop-the-channel ablation as a todo instead.
- **Severity** · Medium (a claim about the architecture that its reference implementation explicitly refuses to make).
- **Fix** · Carry the bypass caveat into `line`'s docstring and into the report's "What holds", and file the drop-the-count-channels ablation the way `tube`'s is filed.
- **Verified** · Yes.

### Finding — the threshold search drops the edge-of-grid guard, and that is the cause of the flagged untrained anomaly

- **Location** · `<worktree>/tools/tube_self_supervised.py:232-236` (`quantile_grid`), `:244-259` (`label_free_threshold`), `:305-328` (`oracle_threshold`) against `<worktree>/src/bugarach/learn/train.py:228-295` and `bench.EdgeOfRange` at `<worktree>/src/bugarach/bench.py:1096`.
- **Issue** · Re-implementing `pick_threshold` in logit space is justified in the docstring and its pooling rule, seed block (`VAL_SEED_BLOCK + seed*1000 + i for i in range(4)`) and merge gap all match the reference exactly. What it drops is the **guard**: `pick_threshold` warns when the chosen point sits at either end of the searched grid, *"the search was still climbing when it stopped, so this is not an operating point"*. The report's own ⚠ — untrained `tube` scoring F1 0.507 while scoring 0.00 on every plant in the probe — is that failure. I confirmed the mechanism: at initialisation both `tube` and `line` are **constant functions**. Across background densities from 0.0 to 0.3 the mean logit moves by ~1e-5, and a planted 32-ROI line changes the peak logit by `+0.000e+00` at float32. So every untrained row in the run is a threshold artefact on a flat output, for all four architectures, and the cause sits in the shared `_dilated_stack` head at init rather than in anything `line` introduced.
- **Severity** · Medium.
- **Fix** · Port the boundary check: refuse (or flag in the record) a threshold that lands on `grid[0]`/`grid[-1]`, and add a near-constant-output guard (`z.ptp()` below tolerance → no operating point). The report's *"until that is chased, the untrained row says nothing"* can then be replaced with the answer.
- **Verified** · Yes — ran both architectures at init and measured.

### Finding — the rigid-shift edge margin is enforced when training and not when thresholding

- **Location** · `<worktree>/tools/tube_self_supervised.py:158-163` (margin enforced) against `:278-281` and `<worktree>/tools/tube_ssl_real_compare.py:82-85` (no margin).
- **Issue** · `rigid_frames` itself is an **exact** match to the reference mapping — I checked Elephant's `dither_spike_train` source (one offset per train, `u ~ U[-J, J)`, `edges=True` cutting to `[0, L)`) against `surrogates._centred`/`_back(..., "drop")` (`<worktree>/src/bugarach/surrogates.py:195-218`), and `floor(k + 0.5 + u)` kept on `[0, L)` is equivalent to Elephant's cut followed by the repo's floor. The divergence is in the **guard clause**: the training bank keeps crops `ceil(J/dt)+1` frames from the ends *"where rigid shift drops onsets"*, but the label-free threshold is set on surrogates of the whole recording, whose first and last *J* seconds are onset-depleted — a depleted edge fires less, so the threshold lands looser. The reference returns per-ROI `dropped` counts (`surrogates.py:383-386`) precisely so this is visible; the numpy copy discards them. On the lab baselines this is ~40 s of 1200 s. Related: the report's *"3–4 % of events sit within 5 s of a window edge, so it is not the window boundary"* checks 5 s where *J* is 10–20 s.
- **Severity** · Medium-low.
- **Fix** · Exclude ±*J* from the event count that sets the threshold (or count the dropped onsets and report them), and widen the edge check in the report to *J*.
- **Verified** · Yes — read Elephant's source in the Elephant venv and both call sites.

### Finding — a seventh `TOL_SEC`

- **Location** · `<worktree>/tools/tube_ssl_real_compare.py:60` — `TOL_SEC = 1.0` — against `<worktree>/src/bugarach/score.py:60-81`, `TOL_SEC = 2.5`.
- **Issue** · The scorer's tolerance has one home, and that module's docstring says why: *"One home, because it was six bare 1.5s … A calibration repeated at every call site is one that gets changed at four of them."* The new module redefines the same name at a different value. Every F1 in this report is matched at 2.5 s; the agreement percentages in "On real recordings" are matched at 1.0 s, and nothing in the report says the two rules differ. A detector-to-detector agreement window is a defensible separate choice — but it needs a different name and a sentence.
- **Severity** · Medium-low.
- **Fix** · Rename to `AGREE_TOL_SEC`, state in the report that agreement uses ±1 s while F1 uses ±2.5 s, and say why.
- **Verified** · Yes.

### Finding — "circularly shifted" is not the project's circular shift

- **Location** · `<worktree>/tools/tube_ssl_real_compare.py:33, 222, 236` against `<worktree>/src/bugarach/assess.py:340-353` and `<worktree>/src/bugarach/surrogates.py:350-365`.
- **Issue** · The null draws an **independent** uniform offset per event and wraps, which destroys the event sequence. The project's circular shift — the assessor's null, the one `surrogates.circular_shift` deliberately calls rather than copying *"so the screen measures the null the assessor actually uses, not a copy of it"* — slides a whole train by **one** lag. Calling the new one "circularly shifted" gives an established term a second meaning. The report's own table names it correctly ("random times in the same recordings"); the code does not.
- **Severity** · Low-medium.
- **Fix** · Rename in the docstrings to "random times within the window", or use `assess.circular_shift_trains` on the event sequence.
- **Verified** · Yes.

### Finding — the real-recording raster does not go through `encode`, and rounds differently

- **Location** · `<worktree>/tools/tube_self_supervised.py:84-90` (`raster_of`) and `:131-148` (`real_recordings`) against `<worktree>/src/bugarach/learn/encode.py:96-139` and `<worktree>/src/bugarach/surrogate_stats.py:204-215`.
- **Issue** · Three divergences from the encoder that every other model path uses. **Rounding**: the real path gets frames from `recordings_from_slices` (`surrogate_stats.py:212`, round-half-away-from-zero) while `encode` truncates (`encode.py:119`) — a half-frame, 0.05 s, systematic offset between the raster a model was trained on and the raster the same checkpoint sees if it is ever reloaded through `bugarach detect --model`. **Edge policy**: `encode` clips an out-of-extent onset onto the edge frame, `raster_of` drops it. **Row order**: `encode` sorts busiest-first and calls that a coordinate, not a label (`encode.py:20-30`); `raster_of` keeps producer order. The last is numerically harmless here — `tube` sums and `line` averages over ROIs, both permutation-invariant — but it means the report's justification at Figure 1's second ⚠ (*"the encoder sorts rows by rate"*) does not describe the path the real-recording numbers came from, and `checkpoint.ENCODING` (`<worktree>/src/bugarach/learn/checkpoint.py:56-62`) asserts the sorted contract for the checkpoints written from this path.
- **Severity** · Low-medium.
- **Fix** · Either route the real recordings through `encode` with an explicit `extent`, or state the two-line divergence in the tool docstring and in the report's method note.
- **Verified** · Yes — both conversions read.

### Finding — the saved checkpoints carry fabricated provenance

- **Location** · `<worktree>/tools/tube_ssl_real_compare.py:109-110` against `<worktree>/src/bugarach/learn/checkpoint.py:36-40`.
- **Issue** · `Trained(...)` is constructed without `train_seconds` or `threads`, so the file records `threads: 0` and `train_seconds: 0.0` — and `checkpoint`'s own docstring says threads is not optional *"because `train.THREADS` records reduction order changing F1 by 0.018 on this very code"*. `ssl_train` does call `pin_threads()` (`tube_self_supervised.py:192`), so the true value is available and is 1. `dt=0.1` is hardcoded in the same call where `r["dt"]` is in hand; I checked the folder and the lab dt is 0.1 s on every recording, so this is correct today and wrong the first time a checkpoint is written from another rig.
- **Severity** · Low-medium.
- **Fix** · Return threads and wall time from `ssl_train` and pass them; take `dt` from the recordings.
- **Verified** · Yes — read the folder's declared frame intervals (0.1 s) and the save path.

### Finding — the self-supervised machinery is library code living in a tool

- **Location** · `<worktree>/tools/tube_ssl_real_compare.py:51-55` and `<worktree>/tools/probe_line_vs_fuzz.py:41-44` — both `sys.path.insert` then `import tube_self_supervised as ts`.
- **Issue** · `ssl_train`, `probs`, `raster_of`, `rigid_frames`, `label_free_threshold`, `real_recordings` and `MERGE_GAP` now have three consumers, which makes `tube_self_supervised.py` a module, not a script — while its supervised counterpart lives in `src/bugarach/learn/train.py` with `tests/test_learn_fold_maker.py` and friends around it. Nothing tests any of it. Two consequences already visible: `task()` mutates the module global `STEPS` (`tube_self_supervised.py:398-400`) and `tube_ssl_real_compare.py:93` reaches in and sets `ts.STEPS` from outside, which is a shared mutable under a `spawn` pool.
- **Severity** · Medium (structural; it is why several of the divergences above went unnoticed).
- **Fix** · Promote the shared half to `src/bugarach/learn/selfsup.py` with the objective, the surrogate bank and the label-free threshold, and give it the test the trainer has. The tools then import it normally.
- **Verified** · Yes.

### Finding — the probe re-types the generator spec instead of reading it

- **Location** · `<worktree>/tools/probe_line_vs_fuzz.py:47-48` — `N_ROI, N_FRAMES, DT = 32, 6000, 0.1`, `BG_HZ = 0.0097` — against `docs/learned/generator_spec.json` (`n_roi: 32`, `bg_rate_hz: 0.009705882…`, `grid_sec: 0.1`), which the same process already reads through `ts.spec()`.
- **Issue** · The values match the spec today, so no number in the report is wrong. They are copies, and the probe imports the module that holds the reader.
- **Severity** · Low.
- **Fix** · Take them from `ts.spec()`.
- **Verified** · Yes.

### Finding — the burst plant is not the width its own docstring states

- **Location** · `<worktree>/tools/probe_line_vs_fuzz.py:16` and `:73-77`.
- **Issue** · The docstring says *"burst K — K/4 ROIs firing 4 times each inside 0.4 s"*; the code plants at `t0 + j * (BURST_FRAMES // 4 + 1)` for `j` in 0..3, i.e. frames `t0, +2, +4, +6` — a 0.6 s span at the 0.1 s grid, and `BURST_FRAMES` does not scale it the way its name implies (at 8 it would give 0.9 s). The report's Figure 1 legend says only "K/4 ROIs × 4", so the report is not wrong; the tool's stated parameter is.
- **Severity** · Low.
- **Fix** · Plant at `t0 + j * max(1, BURST_FRAMES // 4)` and state the realised span, or change the docstring to 0.6 s.
- **Verified** · Yes.

---

### Checked and clean — reuse that is correct, recorded so the absence is not read as a gap

- **The supervised control matches the bake-off exactly.** `tube_self_supervised.py:407-415` calls `learn.train.train` with `steps=900, crop=4096, batch=3, lr=fb.LR[name]` and `fold_maker` over `split.train(held)` — identical to `tools/fair_bakeoff.py:284-295`. The logit conversion of the bake-off threshold (`log(p/(1-p))`) is exactly equivalent, because `encode.decode` compares `score >= threshold` and the sigmoid is monotone.
- **`rigid_frames` reproduces `surrogates.rigid_shift`'s mapping exactly** (see the edge-margin finding); the per-ROI seeding difference is documented at `tube_self_supervised.py:18-22` and is a deliberate cost trade.
- **The parameter counts in the report's table are right.** I built all four: `line` 1,305, `tube` 1,149, `tube_guard` 1,149, `line_length` 1,233, `tiny` 2,393, `trace` 2,065. The "72 parameters" for orientation is exactly `3 extra input channels × width 8 × kernel 3`.
- **`line_length` as a registered architecture rather than a flag** is the right call and follows the 2×2 screen's own discipline; `fair_bakeoff.py`'s LR edit keeps both at the control's 1e-2 with the reason stated, matching the existing comment's logic.
- **Good reuse throughout**: `bench.fold_split`, `bench.pool_scores`, `score.score_stream`, `encode`/`decode`, `learn.train.fold_maker` and `VAL_SEED_BLOCK`, `learn.checkpoint.save`/`load`, `detect_folder.detect_slice` for CoactDetect and LoCo, `surrogate_stats.seed_of`, `surrogate_discriminator.mouse_folds`, `learn.train.pin_threads`, and the registry itself — `line` and `line_length` pick up `tests/test_learn_nets.py:137` (cell-count invariance over `sorted(ARCHITECTURES)`) and `tests/test_architectures_are_files.py` for free.
- **Per-analysis-window execution: checked, not a defect on this cohort.** `tube_ssl_real_compare.call_recording` scores one raster for the whole baseline window rather than going through `detect_folder.folder_analysis_windows` + `Trained.predict(extent=)` the way `tools/run_learned_on_folder.py:236-240` does, which `learn/train.py:117-127` says is what makes a learned model comparable with the six. I loaded the folder: every recording's baseline is a **single** 1200 s analysis window, so the two are equivalent here. It is a latent divergence — a folder whose baseline is split, or a comparison run outside the baseline, would silently give the learned model context the hand detectors were denied — and worth one line in the tool docstring.
- **Model-specific behavioural tests are hardwired to `tube`.** `tests/test_learn_nets.py:52-133` (DoG integrates to zero, uniform field cancels, one-cell-one-vote, the bypass channel) all build `ARCHITECTURES["tube"]`. `line` makes the same three claims and gets none of these; parametrising them would be close to free and would catch the bypass and the DoG-init divergence above.
