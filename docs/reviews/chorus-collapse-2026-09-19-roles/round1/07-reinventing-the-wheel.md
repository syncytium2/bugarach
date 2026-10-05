GRANT 7 ok — Read, Grep, Glob, Bash

Role 7 (reuse auditor, "Reinventing the Wheel"), murderboard round 1. The artifact is `<worktrees>/chorus-collapse/docs/learned/chorus_collapse/index.html`, built by `<worktrees>/chorus-collapse/tools/diagnose_chorus_collapse.py` (tested by `tests/test_diagnose_chorus_collapse.py`). `train.py` references below are on branch replicate-run (`<worktrees>/weekend-runs`), which is the code the tool runs under `--code`. Main's `train.py` has no `deterministic_cuda`, `probabilities` or `THRESHOLD_GRID`.

**Overall:** the tool already reuses a lot: `R.Svg`, `R.x_axis`, `R.CSS`, `R.esc`, `R.Archive` for the tables, `R.THEIRS_FOLDER`/`MINE_FOLDER`, and from `train.py` `fold_maker`, `_recording`, `TRAIN_SEED_BLOCK`, `deterministic_cuda` and `pin_threads`. No re-implementation produced a wrong number that I could find. The inner-fit collapse counts match the replicate report exactly, the refit rule agrees fit by fit, and the replayed loop matches `train()` line by line. The findings are about duplication and fragility. **Blocking: none. Major: none. Minor: 10.**

## Findings

**1. The training loop is copied (items 1 and 5)**
- **Location:** `diagnose_chorus_collapse.py:196-248` (`replay`).
- **Issue:** the loop is a line-for-line copy of `train()` (weekend-runs `src/bugarach/learn/train.py:219-286`), made to add logging every 10 steps and a warm-up.
- **Does it match exactly?** Yes, checked line by line against the source:
  - Same order: `deterministic_cuda`, then `manual_seed(seed)`, then `pin_threads` (220-223).
  - Model built with `ARCHITECTURES[net].make(**overrides).to(dev)`, and Adam at the config lr.
  - Same seed list: `TRAIN_SEED_BLOCK + seed*1000 + i`.
  - Same data: `_recording(mk, s, 0.1, None)[:2]`.
  - Same `pos_weight` formula, including `max(pos, 1e-6)` and float32; same `pos_idx`; same `RandomState(seed)`; the same 50/50 event-centred or uniform crop draw and clip.
  - The forward hooks read values and change nothing.
  - The committed as-run replays assert that the replay differs from the saved checkpoint by exactly 0.0 (`page()` line 486).
- **Small differences, all harmless for these runs:**
  - `dt=0.1`, `stream=None` and `device="cuda"` are hard-coded rather than read from the fit's recorded `training` (`checkpoint.py:259`). They match only because `_run_fit` passed neither dt nor stream (`tune_learned_vs_coact.py:817-820`).
  - The `BENCH_SEEDS` collision assert (`train.py:231`) is dropped.
- **Could it call `train()` instead?** Yes, with no changes to `train()`:
  - The lr counterfactuals are just `T.train(net, mk, ..., lr=X, seed=seed, device="cuda", **overrides)`. There is a precedent on replicate-run: `tools/diagnose_chorus_training.py:97`, the PR #596 diagnosis.
  - Logging can use torch's global hooks, both present in the installed torch 2.14: `torch.nn.modules.module.register_module_forward_hook` (the `BCEWithLogitsLoss` module's output is the loss; the head GELUs; the model's logit), plus `torch.optim.optimizer.register_optimizer_step_pre_hook` to set the warm-up lr. lr only acts inside `step()`, so setting it before each step is equivalent to the copy's setting it before `zero_grad`.
  - Cost of this route: the hooks must ignore `pick_threshold`'s eval-mode passes (check `module.training`).
- **Severity:** minor.
- **Suggested fix:** replace the copy with `train()` plus global hooks. If the copy stays, read dt, stream and device from the checkpoint's `training` record.
- **Verified against a source:** yes.

**2. Collapse rule versus the replicate report (item 2)**
- **Location:** `collapse_table()`, lines 74-109; compare `make_replicate_report.py:247-282` (`archive_facts`).
- **Inner fits: the same rule and the same result.**
  - The rule is identical: exactly one call on every recording of every fold scored, at `own_index`.
  - The keys differ (recs hash here, fold pair in the report) but map one-to-one within a draw. `recs_hash` hashes the sorted set (`tune_learned_vs_coact.py:493-494`), and an inner fit's recordings are fixed by its pair (`:879-881`).
  - I checked the output: the committed `collapse_table.json` gives 146 and 153 of 432 fits (111 in both draws) for chorus_norm, and 75 and 75 (38 in both) for chorus_gain_norm. That is exactly the report's Table 2.
- **Refits: a different rule.**
  - The tool also applies the one-call rule to refits, and the page says each collapsed refit "puts a † beside its net in the replicate report".
  - The report's † actually comes from `R.seed_flags` (`make_replicate_report.py:146-156`), i.e. the run's `failed_training_signature` (F1 within 0.01 of 0.125 and threshold at the grid floor) or `f1_was_nan`, taken at the selection's threshold index (`tune_learned_vs_coact.py:1561-1582`).
  - I cross-checked against both draws' `results.json`: the two rules pick out the same 4 refits, fit by fit. One of the † entries (chorus_norm, second draw, gated) comes from `f1_was_nan` at threshold index 30, not from the one-call rule.
- **Severity:** minor.
- **Suggested fix:** take refit status from `R.seed_flags(R.load_run(folder), ...)`, or add an assert in `page()` that the two agree. Pull the `one_call` loop out of `archive_facts` into one shared function that both tools call.
- **Verified against a source:** yes (data and code).

**3. `fits.zip` opened directly (item 3)**
- **Location:** `census` line 140, `replay` line 183, `_load_fit` line 129.
- **Issue:** these open `fits.zip` with `zipfile` instead of going through `R.Archive` (`make_replicate_report.py:87-111`).
  - I checked the folders: the first draw's results hold `fits.tar.gz` and `scores.tar.gz`; the second draw's hold `fits.zip` and `scores.zip`. So census and replay cannot read the first draw at all. The page's Limits bullet ("the census and the replays use the second draw's fits") is at least partly caused by this reader.
  - The direct reads also skip `Archive`'s name normalisation (lines 101 and 109).
  - The `ZipFile` handles are never closed.
- **Severity:** minor.
- **Suggested fix:** add `Archive.read(name)` to `make_replicate_report`, or collect every needed member in one `items(lambda n: n in wanted)` pass.
- **Verified against a source:** yes.

**4. Checkpoint loaded through a temp file (item 4)**
- **Location:** `_load_fit`, lines 124-130.
- **Issue:** `checkpoint.load` only accepts a path (`src/bugarach/learn/checkpoint.py:184-199`, same on both branches). There is no bytes or dict loader, so the temp file is the only public route.
  - Two tools now work around this. `R.untuned_param_counts` (`make_replicate_report.py:2132-2155`) re-implements `peek` on bytes.
  - `replay`'s as-run branch writes a full checkpoint copy into `<work>/checkpoints` and never deletes it. `<work>` defaults to the darkroom folder. `census` does delete its copies. I found no leftover copies in the darkroom folder, so this is a code-path risk, not an observed one.
- **Severity:** minor.
- **Suggested fix:** use `tempfile.TemporaryDirectory()` as `make_replicate_report.py:477` does. Longer term, split `checkpoint.load` into `loads(text)` plus a path wrapper, so neither tool needs the workaround.
- **Verified against a source:** yes.

**5. The recording maker is duplicated (item 5)**
- **Location:** `replay`'s `planted()` and `REGIMES`, lines 51 and 190-194.
- **Issue:** this duplicates the tuning tool's `_planted` bench branch (`tune_learned_vs_coact.py:595-604`), `BENCH_REGIMES` (`:103`) and `seed_of`/`regime_of` (`:471-476`).
  - For bench runs it matches exactly: `make_recording(BENCH_REGIMES[regime], seed)`. The zero-difference checkpoint check confirms it.
  - It ignores the `home` simulation branch and never reads `meta.json` to confirm the run was a bench run.
- **Severity:** minor.
- **Suggested fix:** import `_planted` from the `--code` checkout's `tools/tune_learned_vs_coact.py`, with `sim` taken from `meta.json`. Then `fold_maker(lambda r: _planted(sim, r), recs)` is literally the `_run_fit` call (`:807`).
- **Verified against a source:** yes.

**6. The census forward pass is hand-rolled (item 5)**
- **Location:** `_probe_input` and `census`, lines 114-121 and 147-153.
- **Issue:**
  - It hard-codes `dt=0.1` although the loaded fit carries its own dt (`checkpoint.py:254`).
  - It does by hand what `T.probabilities(model, raster, logits=True)` (weekend-runs `train.py:101-114`) already does.
  - It moves each GPU-trained fit to the CPU. The run scored each fit on its training device (`model_device`), so census numbers use different arithmetic from the run's scoring.
  - The `logit_sd` metric itself is the same definition PR #596's tool used (`diagnose_chorus_training.py:53`): consistent.
- **Severity:** minor.
- **Suggested fix:** `enc = encode(sl, dt=tr.dt)` and `T.probabilities(tr.model, enc.raster, logits=True)`, leaving the model on its device. The GELU hooks still fire.
- **Verified against a source:** yes.

**7. Figure helpers and table markup (item 6)**
- **Location:** `fig_*` functions and `page()`, lines 269-399 and 515-529.
- **Issue:** `R.Svg`, `x_axis`, `CSS`, `esc` and `SVG_TITLE` are reused. What is new:
  - `fig()` and `ref_()` are re-typed. Their markup is identical to the report's (`make_replicate_report.py:1336-1344`), which cannot be imported because those helpers are nested inside `build()`.
  - Tables are written by hand and drift from the report's `tab()` (1346-1350): no `id="tab-n"` anchor and no scroll hint.
  - The rotated y-axis label is hand-written 3 times here and once in the report (757).
  - `polyline` is written through `svg.add` because `Svg` has no method for it.
- **Severity:** minor.
- **Suggested fix:** lift `fig`, `ref_` and `tab` to module level in `make_replicate_report`, and add `Svg.y_label` and `Svg.polyline` there.
- **Verified against a source:** yes.

**8. Palette tokens (item 6)**
- **Location:** `CSS_EXTRA`, lines 402-410.
- **Issue:**
  - `--c1` and `--c2` duplicate `R.CSS`'s `--draw-a` and `--draw-b` hex for hex, in all three theme blocks (`make_replicate_report.py:988-996`).
  - The colours now mean something else: blue/orange is first/second draw in the replicate report and working/collapsed here, so a reader moving between the two pages sees the same colours swap meaning.
  - `--c3` to `--c6` match the hexes other tools use in the same slot order (`make_rigid_shift_gates_figure.py:57-59`, `make_tube_ssl_figure.py:51-52`). No palette source exists in the repo to check the "validated order" claim against.
- **Severity:** minor.
- **Suggested fix:** define the slot tokens once in `R.CSS` and alias the draw tokens to them. Cite where the validated palette lives, or drop the claim.
- **Verified against a source:** partly. The duplicate hexes are confirmed; the "validated" claim could not be checked.

**9. Output and input handling (item 7)**
- **Location:** `main()` and `_results`, lines 56-58 and 704-758.
- **Issue:** the SAP006 convention is followed: `--out` defaults to the darkroom and `--also` writes the repo copy (`sapper.py:121-133`; report main 2168-2170). Three things differ from the report builder:
  - Writes are not atomic. The report writes a `.tmp` file and then replaces it (2195-2199).
  - `_results()` passes `darkroom()`'s `None` into `Path`, so it raises a `TypeError` instead of printing `unresolved_message` (report 2190-2192).
  - There are no `--mine`/`--theirs` style overrides for the input folders (report 2161-2164), so `table`, `census` and `replay` can only read the darkroom.
- **Severity:** minor.
- **Suggested fix:** follow `make_replicate_report.main`'s pattern for all three.
- **Verified against a source:** yes.

**10. Names and the lr grid are re-derived**
- **Location:** lines 86, 92, 102 and 266.
- **Issue:**
  - The fit and score filename regexes and the `configs/` path re-derive `recs_hash`, `fit_stem`, `score_path` and `config_path` (`tune_learned_vs_coact.py:493-506`) and the report's own parsing (`make_replicate_report.py:221-226`, 257).
  - The tool splits fit names on `parts[1]` where the report uses `parts[-3]`. The two are equivalent for these archives.
  - `LRS` is hard-coded. It matches the declared `_LR_STEPS` (`tune_learned_vs_coact.py:143`) today.
- **Severity:** minor.
- **Suggested fix:** read the lr grid from the run's declaration and configs, and share one filename parser with the report.
- **Verified against a source:** yes.

## What I checked
- Read all of `diagnose_chorus_collapse.py` and its test.
- Compared it against `train.py` on replicate-run (and diffed it against main's), `checkpoint.py` on both branches, and `make_replicate_report.py` (Archive, `archive_facts`, `seed_flags`, Svg, `x_axis`, CSS, `fig`/`tab`, `main`).
- Compared it against `tune_learned_vs_coact.py` on replicate-run (`_planted`, `_run_fit`, `_heldout`, path helpers, lr grid), `encode.py`, the nets, and `sapper.py` SAP006.
- Searched both worktrees for other copies of the training loop, other forward-hook or dead-unit code, other `checkpoint.load` callers and the palette hexes. That turned up PR #596's `tools/diagnose_chorus_training.py` (replicate-run only).
- Read-only data checks: the archive formats in both draws' results folders; `collapse_table.json` tallies against the report's Table 2; refit collapse against both draws' `results.json` `seed_flags`; whether leftover checkpoint copies exist in the work folder.
- I edited no files and wrote nothing to the scratchpad.
