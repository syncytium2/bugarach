GRANT 7 ok — Read, Grep, Glob, Bash

**Reuse audit — "Reinventing the Wheel".** Surface examined: the seven tools scripts and two `learn/nets` modules named in the task, against `src/bugarach/{surrogates,score,bench,surrogate_stats,surrogate_discriminator,detect_folder}.py`, `src/bugarach/learn/{encode,train,checkpoint}.py`, `src/bugarach/learn/nets/`, `src/bugarach/detectors/_shared.py`, `tools/fair_bakeoff.py`, `tools/look_rigid_shift.py`, `tools/run_learned_on_folder.py`, `tests/test_registries_do_not_drift.py`, `tests/test_learn_nets.py`, `docs/INDEX.md`. One finding was settled by running a fit rather than by reading.

---

### The tube-channel reconstruction is built at initialisation values, not fitted ones

**Location** `tools/tube_aggregate_leak.py:54-56` (`CENTRES`, `SURROUND_RATIO = 8.0`, `WIDEN = 1`), `:65-74` (`dog_kernel`), `:77-92` (`bright_trace`) · reference `src/bugarach/learn/nets/tube.py:109` (`_kernels`) and `:139-145` (`forward`).
**Issue** The docstring claims the classifier sees "what `tube` sees … built the same way". It is built from `tube`'s **initial** parameters. I fitted a supervised `tube` exactly as the bake-off fits it (spec `docs/learned/generator_spec.json`, fold 0, seed 0, 900 steps, lr 1e-2) and read its parameters:

```
fitted centre widths (frames): [2.33 3.03 4.30 5.28]   -> kmin = 2
fitted surround ratios:        [21.1 16.6 11.8  9.70]
```

So the trained model widens each onset by **±2 frames** (`max_pool1d` at `2*kmin+1 = 5`) where the leak test uses `WIDEN = 1`; its surround is **9.7–21.1×** the centre where the leak test fixes 8.0; and its centre widths live in 2.3–5.3 frames where the test scans 1–128, six of whose eight scales the model never occupies. The largest, 128, is outside the model's own clamp — `_kernels` clamps the centre to `[0.5, k/2] = [0.5, 64]`, so `c128_*` is a feature of a kernel `tube` cannot have. Kernel support also differs: `dog_kernel` truncates at `±3s`, `_kernels` at a fixed `±128` for every scale, so at `c ≥ 16` the reference's surround is truncated inside one standard deviation and area-normalised over that truncation while the reimplementation is not. This is the Stage 1 gate the whole self-supervised run was licensed by ("a classifier reading tube's cells-mean channel could not tell real from a shared offset"), and the README's per-scale reading ("separated at event-width kernel scales") is read off this bank.
**Severity** High.
**Fix** Build the channel from a fitted model — instantiate `ARCHITECTURES["tube"].make()`, load or fit the weights, and call `_kernels`/the pooling path — or state in both the tool docstring and the README that the bank is tube-at-initialisation and that the fitted widen is ±2 frames with ratios near 10–21. Drop `c128` or raise it to the model's clamp.
**Verified** Yes — measured, one fit.

### The oracle threshold picker re-derives `pick_threshold` without its edge-of-grid guard

**Location** `tools/tube_self_supervised.py:305-328` (`oracle_threshold`) and `:232-236` (`quantile_grid`) · reference `src/bugarach/learn/train.py:228-295` (`pick_threshold`).
**Issue** The function reproduces `pick_threshold`'s seed block, its four validation recordings and its `pool_scores` rule faithfully — and drops the one guard that function carries two separate incidents for. `pick_threshold` warns when the chosen threshold lands on either end of its grid, because "an optimum at the edge means the search stopped while still climbing", and its comment records the optimum going "straight through the floor" the day `fold_maker` started handing it unseen recordings. `quantile_grid` spans `np.quantile(z, 1 - geomspace(0.5, 1e-6, 90))` — its **floor is the median of the pooled per-frame scores**, i.e. a threshold at which half of all frames fire — and `oracle_threshold` returns the argmax over it with no check at either end. The untrained arm is the visible symptom: the README reports its oracle-threshold detections covering 95–99 % of a recording, which is what a threshold pinned at the grid floor looks like. Two smaller divergences: `pick_threshold` skips a candidate when `pooled.n_scored <= 0`, this one checks only `n_planted`; and `pick_threshold` returns 0.5 when nothing scores, this one returns `None`, which `score_held_out` then silently skips (`if thr is None: continue`), so an arm with no oracle row and an arm whose oracle row failed look identical in `results.jsonl`.
**Severity** High.
**Fix** Carry the guard: warn (and record in the result row) when the chosen threshold is the first or last grid point, and widen the grid downward past the median. Better, give `pick_threshold` a `grid=` argument and call it, so there is one threshold picker with one guard.
**Verified** Yes, by reading both.

### The destruction half of the controls run duplicates `surrogate_stats.destruction` and loses its verdict rule

**Location** `tools/look_rigid_shift_controls.py:160-168` (`excess_k`), `:197-231` (`before_task`, `draw_task`), `:245-271` (`assemble`), `:58-60` (`VISIBILITY_FLOOR`) · reference `src/bugarach/surrogate_stats.py:1175-1195` (`coact_excess`) and `:1198-1266` (`destruction`).
**Issue** `destruction` already does all of this — both twins through `surrogates.generate` on the **same key**, `freeze_half` as a keyword with the same seeded-half construction, `coact_excess` on each, and then the row it computes. The tool re-derives it and keeps only `before` and `after`. Everything the library row carries that constitutes the verdict is gone: `retained` (the ratio the README's "0.41–0.49 against 0.00 and 1.00" is stating), `planted_visible`, `pair_share_planted_above`, and — the load-bearing one — the `before > 0 else nan` guard, which exists precisely so an invisible planted signal is reported as invisible rather than divided by. `VISIBILITY_FLOOR` is declared with a docstring pointing at `bugarach.confirm.rule.VISIBILITY_FLOOR`, written into `meta.json`, and **never read anywhere in the file** — the run records a floor it does not apply.
**Severity** High.
**Fix** Call `surrogate_stats.destruction` (see the bin-width finding below for the one thing that blocks it today) and report its rows; or, if the fine-grained task split is needed for the 37-second Cossart calls, compute the same row fields in `assemble` — `retained`, `planted_visible`, `pair_share_planted_above` — and either apply `VISIBILITY_FLOOR` or delete the constant.
**Verified** Yes, by reading both.

### "Destruction" now means two different bin widths in one tree

**Location** `tools/look_rigid_shift_controls.py:160-168` (`excess_k`, `bin_sec` from `tools/look_rigid_shift.py:57`, `BINS_SEC["fast"] = (1.0,)`) · reference `src/bugarach/surrogate_stats.py:1175-1195`, which fixes `bin_width_sec = (2 * DESTRUCTION_HALF_WINDOW_FRAMES + 1) * dt`.
**Issue** `coact_excess`'s bin is the assessor's ±2 frames — 5 frames, and the fast stream's frame interval is 0.1 s on every one of the 84 recordings in `steps_excluded` (checked `slices.csv`), so 0.5 s. `excess_k` runs at 1.0 s on fast, twice that, and does so under the same word. Every other destruction number in the tree is at the assessor's window. This is also the only thing preventing reuse of the library function.
**Severity** Medium.
**Fix** Give `coact_excess` an optional `bin_width_sec` (defaulting to the assessor's), thread it through `destruction`, and call them. State the bin beside any destruction number in the README.
**Verified** Yes — `coact_excess` read; frame interval read from the export folder's `slices.csv`.

### The model list is hand-copied into five files with no registry check, and the drift has already bitten

**Location** `tools/tube_self_supervised.py:62`, `tools/tube_ssl_real_compare.py:62`, `tools/probe_line_vs_fuzz.py:123`, `tools/make_tube_ssl_figure.py:31`, `tools/make_line_sensors_figure.py:23-32` · reference `tools/fair_bakeoff.py:57` plus `:207-209`, pinned by `tests/test_registries_do_not_drift.py:90-120`.
**Issue** The repo's settled answer to a hand-listed model tuple is not "don't" — it is "state it as a selection and make divergence fail out loud". `fair_bakeoff` writes `registered: sorted(ARCHITECTURES)` and `registered_but_not_run` into its provenance and is held to it by two tests. None of the five new copies does either: `meta.json` records `models` but never what was registered, so skipped and absent are indistinguishable in the record. The comment at `make_tube_ssl_figure.py:33-35` records the failure already happening inside this thread — "the figure showed only the tube family until 2026-09-16, when four reviewers found it plotting two architectures under a caption that said four." A registered architecture outside these lists is also a hard failure rather than an omission: `fb.LR[name]` raises `KeyError`, and `LR` is itself a hand-listed table in a tools script.
**Severity** Medium.
**Fix** Write `registered` and `registered_but_not_run` into `meta.json` alongside `models`; add a `--models` argument defaulting to the tuple; extend `test_registries_do_not_drift`'s ghost check to cover these files (its regex is one line per file). Move `LR` beside the registry — `Arch.cfg` or a `bench` table — so a new architecture cannot be registered without a learning rate.
**Verified** Yes.

### Checkpoints are written claiming an encoding contract the run did not use

**Location** `tools/tube_ssl_real_compare.py:105-118` · reference `src/bugarach/learn/checkpoint.py` (`ENCODING`, `save`, `load`) and `src/bugarach/learn/encode.py:96-139`.
**Issue** Three things in one call. First, every raster in the self-supervised path is built by `tube_self_supervised.raster_of`, which bypasses `encode()` and therefore its canonical row sort; `checkpoint.save` nonetheless stamps `ENCODING["row_order"] = "descending event count, ties by onset sequence — busiest first"` and `load` refuses any file whose encoding differs. The four architectures in this run are permutation-invariant over ROIs, so nothing is numerically wrong today — but the file states something untrue in the one field that exists to be trusted later, and the next order-sensitive architecture run through this script inherits it silently. Second, `dt=0.1` is hardcoded where `r["dt"]` is in hand two lines above; it happens to be right for this folder (all 84 recordings at 0.1 s) and the export folder is by contract replaceable. Third, `threshold=sigmoid(median logit)` "may round to 1.0", as the note says — a checkpoint loaded by `bugarach detect --model` would then threshold sigmoid output at exactly 1.0 and fire nearly everywhere, and the warning is in free-text `note` where no loader reads it.
**Severity** Medium.
**Fix** Encode real recordings through `encode()` (or add an encoding variant to `ENCODING` and stamp it honestly); pass `dt=r["dt"]`; and either refuse to save a model with no fixed operating point or add an explicit `threshold=None` state the loader can act on.
**Verified** Yes — frame interval checked against the folder's `slices.csv`.

### The agreement measure is a different matching rule from the scorer, under a name that shadows it

**Location** `tools/tube_ssl_real_compare.py:60` (`TOL_SEC = 1.0`) and `:221-239` (`agreement`) · reference `src/bugarach/score.py:60` (`TOL_SEC = 2.5`) and `:201-276` (`score_detections`).
**Issue** `score.py`'s tolerance carries a docstring explaining that it has **one home** "because it was six bare 1.5s". A module that imports from `bugarach` throughout now defines a module-level `TOL_SEC` with a different value, so two constants of the same name in one call graph mean different things. The rule differs in kind too, not only in width: `score_detections` matches greedily, closest pair first, **one-to-one**, with a midpoint tie-break; `agreement` credits an event if it overlaps *any* of the reference's events, with no consumption — so a detector that fragments one reference event into five calls scores five hits, and a reference event can be claimed by every call near it. The README notes the tolerance difference ("matched at ±1 s, where every F1 in this report is matched at the scorer's ±2.5 s") but not the rule difference, which is the larger one.
**Severity** Medium.
**Fix** Rename the constant (`AGREE_TOL_SEC`), and say in both the tool docstring and the README that agreement is a many-to-one overlap share and is not comparable with recall. If a one-to-one number is wanted, `score_detections` already computes it given a ground-truth-shaped object.
**Verified** Yes.

### The probe hand-rolls a background and plants the generator can make

**Location** `tools/probe_line_vs_fuzz.py:47-51` (`N_ROI`, `N_FRAMES`, `DT`, `BG_HZ = 0.0097`) and `:61-87` (`field`, `plant`) · reference `src/bugarach/simulate.py:367+` (`simulate_coordination`, with `participation`, `jitter_sec`, `bg_rate_shape`, `bg_burst_shape`) and `docs/learned/generator_spec.json`.
**Issue** Three constants are hand-copied from the generator spec that the sibling module already loads (`tube_self_supervised.spec()`): `n_roi` 32, `grid_sec` 0.1, and `bg_rate_hz` 0.009705882…, copied as `0.0097`. More consequential, the field is **flat** Poisson, where the spec turns on `bg_rate_shape = 0.275` and `bg_burst_shape = (1.547, 1.388)` and its own notes say why: "The bench's flat field is documented in the tree as easier than real data; leaving it flat would calibrate every detector for a recording nobody has." The quantity the probe exists to measure is whether `line` can judge a count against its own background, and it is measured on the one background the project decided not to use. The plants themselves (a line, a spread, a burst) are `participation` and `jitter_sec` in the generator's own vocabulary.
**Severity** Medium.
**Fix** Read `n_roi`, `grid_sec` and `bg_rate_hz` from the spec; add a run at `bg_rate_shape`/`bg_burst_shape` from the spec beside the flat one; consider building line/fuzz through `simulate_coordination` at `jitter_sec` 0 and 3 s so the probe and the bench share a generator.
**Verified** Yes.

### `line`'s behavioural claim is pinned by an exploratory tool, where `tube`'s is pinned by a test

**Location** `src/bugarach/learn/nets/line.py` (the "one ROI, one vote" and difference-of-Gaussians claims; its docstring directs the reader to `tools/probe_line_vs_fuzz.py`) · reference `tests/test_learn_nets.py:63` (`test_a_uniform_field_cancels_but_a_concentrated_one_does_not`), `:117` (`test_one_cell_one_vote_is_enforced_over_the_smallest_scale_only`), both on the `_tube()` fixture at `:49`; `:137` shows the parametrised-over-the-registry form already in use.
**Issue** The architecture is correctly placed in `src/` with a `@register` line and the ablation correctly delegates (`line_length.py:38` calls `build_line(orientation=False)`) — that half is right. What is not reused is the harness: `line` is the one architecture in the folder that actually *enforces* a vote bound (a sigmoid, where `tube`'s `max_pool1d` bounds nothing), and that claim has no test, while the two tests that pin the equivalent claims for `tube` sit one `@pytest.mark.parametrize` away. The README states the gap ("`line` is a day old and has never been reviewed as code, and the behavioural tests that pin `tube`'s claims are hardwired to `tube`"), so it is known — the point here is that the repair is reuse, not new work.
**Severity** Medium.
**Fix** Parametrise the two behavioural tests over the registry, or add a `line`-specific pair beside them, before any `line` number is promoted.
**Verified** Yes.

### The figure tools are a second figure stack

**Location** `tools/make_tube_ssl_figure.py:16-19,46` and `tools/make_line_sensors_figure.py:16-19,43` · reference `docs/INDEX.md` row "draw a figure — how this repo renders one"; `bugarach.paths.darkroom()`; `bugarach.ui.diagnostic`.
**Issue** Forty-two of the `tools/make_*.py` render through holoviews/bokeh plus Playwright; six use matplotlib, and five of those six are this thread's own tools. Twenty-six default their destination to `darkroom()`; both new tools take `--out` as required, which is the shape `docs/todo/2026-08-18-figure-tools-require-out.md` was opened for (SAP006's `include` list is deliberately narrow and does not reach figure tools, so nothing fires). Neither figure draws a raster or a time axis, so the raster and 60-base-tick conventions are not at risk here — this is about destination and stack, not about the drawing. Dead weight: `PLANTS` at `make_line_sensors_figure.py:33-36` is defined and never used.
**Severity** Low.
**Fix** `--out default=None` with `out = a.out or darkroom()` and `--also` for the repo copy, in both. Delete `PLANTS`. Whether the thread's matplotlib stack should be folded back into the holoviews one is a decision worth recording either way rather than letting five files settle it by accretion.
**Verified** Yes.

### Three different counts of co-active ROIs appear in one report

**Location** `tools/tube_aggregate_leak.py:77-92` (`bright_trace`: sliding, each onset widened ±1 frame, mean over ROIs), `tools/tube_ssl_real_compare.py:165-170` (`participation`: ROIs with an onset inside the event span ±2 frames) · reference `src/bugarach/detectors/_shared.py:63-75` (`distinct_coact`: distinct ROIs per **non-overlapping** bin, LoCo's own statistic) and `src/bugarach/surrogate_stats.py:93` (`DESTRUCTION_HALF_WINDOW_FRAMES = 2`, the assessor's window).
**Issue** These are genuinely different objects and none is wrong, but the README's real-recording table sets participation figures from the second beside CoactDetect and LoCo, whose own coactivity is the third. `participation`'s ±2 frames does coincide with the assessor's half-window, which is worth saying out loud in the tool. Separately, `measure()` recomputes participation for `coact` and `loco` rather than reading the `n_roi` those detectors already emit (`src/bugarach/emit.py:87-120`) — recomputing uniformly is the right call for comparability, but the emitted value is a free cross-check on the recomputation and is not used.
**Severity** Low.
**Fix** Name the window in the tool docstring as the assessor's ±2 frames; add a one-line comparison of recomputed against emitted `n_roi` for `coact`/`loco` in the summary.
**Verified** Yes.

### The window-clip idiom is written out five times

**Location** `tools/tube_self_supervised.py:87-88`, `:143-144`, `tools/tube_aggregate_leak.py:83-84`, `tools/look_rigid_shift_controls.py:77-78`, `tools/tube_ssl_real_compare.py:169` · reference `src/bugarach/surrogates.py:190-192` (`_in_window`) and `src/bugarach/detectors/_shared.py:78-85` (`clip_sorted`).
**Issue** All five copies are the half-open rule `(t >= s) & (t < e)`, which matches `_in_window` — so they agree, and they agree with the surrogate path they feed. Worth noting that `clip_sorted` is **closed** on the right, so the two library helpers already differ and neither is importable as a drop-in for the other. Not a defect in the new code; a small duplication that would go away if `_in_window` were public.
**Severity** Low.
**Fix** Promote `surrogates._in_window` (or add a public `windowed_trains`) and call it. Optional.
**Verified** Yes.

### The bake-off harness has become a library living in `tools/`

**Location** `tools/tube_self_supervised.py:121-122` (`import fair_bakeoff as fb; fb._make_recording`), `:409` and `tools/tube_ssl_real_compare.py:96,131`, `tools/probe_line_vs_fuzz.py:129` (`fb.LR[name]`) · reference `tools/fair_bakeoff.py:57-69,89-91`.
**Issue** Four tools scripts now import a **private** function and a constants table from a fifth. `_make_recording` is two lines around `bugarach.simulate.simulate_coordination`; `LR` is per-architecture configuration. Both belong beside the registry or in `bench`, where a new architecture picks them up for free — which is the same argument the registry itself was built on.
**Severity** Low.
**Fix** Move `LR` to `Arch.cfg` or `bench`; call `simulate_coordination(seed=…, **spec)` directly instead of reaching through `fb._make_recording`.
**Verified** Yes.

### The probe's own docstring disagrees with its plants

**Location** `tools/probe_line_vs_fuzz.py:15-16`.
**Issue** The docstring says burst is "4 times inside 0.4 s" and fuzz is "spread uniformly over 3 s". The code gives a burst at frames `t0, t0+2, t0+4, t0+6` — 0.6 s — and a fuzz drawn from `randint(-15, 15)`, i.e. 2.9 s. The README has both right (0.6 s and 2.9 s), so the stale numbers are in the code, not the page.
**Severity** Low.
**Fix** Correct the two numbers in the docstring, or derive them from `BURST_FRAMES` and `FUZZ_SEC`.
**Verified** Yes.

---

### One re-implementation that does match its reference

`tools/tube_self_supervised.py:97-104` (`rigid_frames`) against `src/bugarach/surrogates.py:368-386` (`rigid_shift`) plus `_centred`/`_back` at `:195-218`. The reference maps frame `k` to `floor((k + 0.5) + u)` and drops anything outside `[0, L)`; `rigid_frames` computes exactly that, one `u ~ U(-J, J)` per ROI, dropping the same way. Empty trains and output sort order both come out equivalent (a rigid shift preserves order). The declared divergence — one shared `RandomState` instead of Elephant's per-ROI seeding, so a bank of draws is cheap — is the only one, and the docstring states it. `tools/look_rigid_shift_controls.py:69-84` (`shared_shift`) uses the same arithmetic and rebases to absolute frames the way `_result` does at `:245`, so it is comparable with `sg.generate`'s output in the same call.

Worth one note that is not a defect: the boundary rule diverges from `encode()` rather than from `rigid_shift`. `encode` **clips** out-of-range onsets onto frames 0 and n−1 (`src/bugarach/learn/encode.py:119`), which `docs/INDEX.md` flags as firing on "every surrogate that displaces an onset in time"; `raster_of` drops them. At scoring time the real raster comes from `encode` (clip) and its threshold surrogates from `raster_of` (drop), so the two sides of the label-free threshold use different edge rules. Here the drop is the better rule and real recordings never trip the clip, so the asymmetry helps — but it is undeclared, and a reader reconciling this against the INDEX row will not be able to.
