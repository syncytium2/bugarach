GRANT 7 MISMATCH — missing none; holds Edit, Write, NotebookEdit (deferred), PowerShell, Agent, Artifact, Skill, ToolSearch, Claude Docs batch, Claude Docs update, plus deferred Gmail, Dropbox, WebFetch, WebSearch and other MCP tools

I used only Read, Grep, Bash and one scratch script, `_scratch/r4-role-07/jitdef.py`. I edited no tracked file. **Blindness disclosure:** one Grep (`synfire|spike_train_order|...`, glob `*.py`) ran across the whole worktree and returned file *names* under `_scratch/r2-*`, `_scratch/r3-*` and `_scratch/role-06`. No contents were shown and I opened none of them. I did not touch `docs/reviews/`.

**What I checked:**
- `theory.py`, `aim1_one_source.py`, `membership_limit.py`, `order_limit.py`, `aim0_figures.py` and `aim1_figure.py`, against `tools/measure_coordination_rates.py` (`solve`, `measure`, `_frames`, `truth`, `_sim`, `DT`, `WINDOWS`).
- `src/bugarach/assess.py` (`_coact_count`, `_clusters`, `jit_defined`, defaults), `src/bugarach/event_floor.py` and `tools/measure_chance_floor.py` with `probe_field_size`.
- `src/bugarach/assembly.py` and `tools/assembly_power.py`.
- `tools/synfire_scan.py` and `tools/make_synfire_roi_figure.py`.
- `tools/measure_jitter_correlogram.py`, `src/bugarach/simulate.simulate_coordination` (flat field default, no latency templates, no assemblies), `src/bugarach/adapt.generator_params`, `tools/naming/artifact_name`, `src/bugarach/paths.darkroom`, and the figure convention in `docs/INDEX.md`.

**What is already reused correctly (no finding):**
- `theory.py` passes its predictions through `mcr.solve`, and takes `DT` and `WINDOWS` from the tool.
- `aim1_one_source.py` copies `mcr._sim`'s pipeline exactly: `_frames`, the `L-1` clip, `measure` with the default `N_SURR`, and `truth`.
- `membership_limit.py` imports `stat_dispersion`, `pvalues_margin`, `pvalues_uniform` and `AssemblyResult.verdict`. It uses `RandomState`, and runs margin then uniform on one stream, as `assess_assemblies` does.
- The ADR-0008 floors the page quotes (6 and 12 cells) come from the blind passes' calls to `event_floor.window_floor`, not from a re-implementation.
- The figure scripts use `naming.artifact_name` and `paths.darkroom`.
- `order_limit.py` re-implements order measurement because production has only the PySpike route (not installed) and no ordered-event generator. Its docstring and the page table the four ways it differs from PySpike, so that is justified.

**Findings** (location · issue · severity · suggested fix · verified against a source):

1. **`aim1_one_source.py:61` (`n_surrogates=120`) and the record's `assessor_settings` note.** The note says "only observation-based outputs are used here". That is false for `jit_defined`. `assess.py:589` sets `defined = bool(sd_obs) and bool(sds_null[K])`, so the flag depends on the surrogate ensemble, and the shipped default is 1000 surrogates.
   - At 0.01 Hz and K = 6, 17 of 80 recordings with 10+ cell events are marked undefined, spread across all four jitters (4 or 5 each). The closed form expects about 0.28 chance clusters across 120 background-only surrogates.
   - I reran four of those recordings at the identical seeds: at 120 surrogates `jit_defined` is False with 0 null clusters; at 1000 it is True with 2–12 null clusters. `jit_obs` was identical both times.
   - So points are missing from Figure 1 D (K = 6 series at 0.01 Hz), and the "(n defined / n)" counts that `aim1_summary` prints are an artifact of the reduced setting, not a property of the assessor. The caption "drawn only where the assessor marks it defined" hides this.
   - Severity: **medium**.
   - Fix: run the assessor at the shipped 1000 surrogates, or filter on `n_clusters_obs > 0` (observation only). Then correct the record's note and the caption.
   - Verified: yes (assess.py:589; rerun output above).

2. **`theory.py` `aim1_summary` ("smallest K with chance clusters at or below one per hour (the assessor's own rule)") and page line 72–73 "By the assessor's own rule".**
   - `bugarach.assess` has no such rule: `DEFAULT_MIN_ROIS` is a reported scan, not a choice.
   - The one-per-hour budget and the smallest-K search are ADR-0008's, in `event_floor.FA_PER_HOUR` and `event_floor.floor_of` (event_floor.py:45, 102). The code re-types `1 / 60` and re-writes the search with `next(...)`.
   - Severity: **low**.
   - Fix: import `FA_PER_HOUR` and apply `floor_of` to the closed-form curve. Reword the label as "ADR-0008's budget applied to the assessor's 1 s clusters".
   - Verified: yes.

3. **`theory.chance_clusters_per_min`** re-implements the assessor's cluster count in closed form. It matches `assess._coact_count` and `_clusters`:
   - an ROI counts once per bin, with p = 1 − e^(−b·bin);
   - a merge with a gap of at most `merge_bins` gives a start probability of q(1 − q)^`merge_bins`;
   - the defaults are read from the signature.

   It leaves out the ±`wm_factor`·bin gather filter (`_clusters` keeps a cluster only when at least K onsets gather). At 1.5 s this cannot drop a one-bin cluster, but it can drop a merged run. It is also homogeneous-rate only, which `simulate`'s default flat field (`bg_rate_shape=None`) satisfies, and its docstring points to `measure_chance_floor.poisson_binomial_sf` for the uneven case.
   - Severity: **low**, as documentation.
   - Fix: add one line to the docstring saying the gather filter is ignored and why it is negligible at a 1.5 s gather.
   - Verified: yes (assess.py:261–335).

4. **`aim0_figures.py` and `aim1_figure.py` output routing and renderer.** `docs/INDEX.md` row 174 states the house figure route: Playwright screenshots of `make_*_figure.py`, darkroom by default, a repo copy only with `--also`, and SAP006 blocks a required `--out`. Both new scripts write a repo copy by default unless `--no-repo` is passed, and draw with matplotlib.
   - Severity: **low**. The figures are meant to sit beside the goal page, so this may be intended, but the deviation is not stated. The figure-convention side is role 10's.
   - Fix: make the repo copy opt-in with `--also`, matching the convention, or say in the README why it differs.
   - Verified: yes (INDEX.md:174).

5. **Duplicated helpers inside the folder.**
   - `aim1_figure.py:154–166` inlines the `artifact_name.build` call and the PNG metadata that `aim0_figures.name()` and `save()` already provide.
   - `theory.check` and `aim1_summary` each rebuild the same per-condition grouping.
   - `membership_limit.py`'s verdict-word tally duplicates `tools/assembly_power.py` `VERDICTS` and `powers_verdict` (lines 240–282).
   - Severity: **low**. The two copies can drift.
   - Fix: share one helper, or import `assembly_power.VERDICTS`.
   - Verified: yes.

6. **Jitter estimators: the joint fit against `tools/measure_jitter_correlogram.py`.** The joint fit (`theory.fit_joint`) is a new jitter estimator, shown in Figure 1 next to the assessor's. The project's own bin-free jitter instrument, the correlogram's `pairs` and `hwhm`, takes in-memory frame trains and was not run on the same recordings. The plan already lists this comparison as owed (item 1, extract lines 401–404), so it is acknowledged.
   - Severity: **low**.
   - Fix: none beyond doing plan item 1 before the joint fit's jitter is quoted as a recovery result.
   - Verified: yes.

7. **`order_limit.py` docstring, "the null: relabelling or the fitted c / sqrt(n_bar) here".** The code has no relabelling null. Its no-order reference is order-free simulation (template SD 0), not `synfire_scan._relabel`.
   - Severity: **low**.
   - Fix: say "order-free simulation and the fitted c/√n̄", and keep the relabel null on the PySpike side of the comparison.
   - Verified: yes (order_limit.py versus synfire_scan.py:119).

**Run finding:** this reviewer took the inline fallback path and holds editing tools, as declared in the GRANT line above.
