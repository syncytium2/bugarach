<!-- Verbatim role report, except that this machine's absolute paths are written as %USERPROFILE% and <darkroom> (the repository is public). The unedited original is in <darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-roles/. -->

GRANT 7 ok — Read, Grep, Glob, Bash
(SubagentHandback is also present. It is the hand-off channel, not an editing tool. I hold no Edit, Write or NotebookEdit.)

**Role 7: Reinventing the Wheel.** The artifact is `report.html`, blob 76c3270 (hash confirmed with `git hash-object`). It was built from `tools/build_fair_comparison_report.py` as committed at HEAD 805fee9.

**The working copy is being edited while I review.** `tools/build_fair_comparison_report.py` and the test file have uncommitted changes that remove `fig_nets` (Figure 2). All line numbers below refer to the committed file that built the artifact, not the working copy.

I edited no files. I ran read-only checks with the venv at `bugarach-worktrees/tune-bench-comparison/.venv`:
- recomputed the paired *t* values;
- recomputed the fold draws through `fold_maker`;
- scored the shipped LoCo and CoactDetect settings on the 24 crowded recordings.

One of my runs used a multiprocessing pool that kept respawning workers after they failed. I killed only that process tree (PID 20884); another session's pool (PID 11840) was left alone.

## Findings
Each row: location · issue · severity · suggested fix · verified against a source.

1. **Figure 2 is drawn by hand; the project's architecture-figure pipeline is not used** — `build_fair_comparison_report.py:204-257` (`_box`, `_arrow`, `fig_nets`), present in the built artifact.
   - **Canonical implementation:** the vendored draughtsman via `tools/make_architecture_diagram.py` (`DRAWABLE` at :96-113; coverage `check` at :123ff), and the committed `docs/learned/architecture.svg`. `docs/INDEX.md:123` says "never hand-edit".
   - That tool exists because a hand-drawn stage diagram silently left out architecture: max-pool, mean over cells, kernels, bypass, concat (docstring :7-51).
   - Fig 2 types its stage text (for example "at 4 widths", "loudest 4", "33 ROIs x time") with no coverage check.
   - Only `tube` has a draughtsman spec today.
   - **Severity:** major.
   - **Fix:** finish the removal already in the working copy and rebuild. If a picture of the nets is wanted, inline `docs/learned/architecture.svg` for tube the way `build_site.py` does, and add specs for the other three rather than hand boxes.
   - **Verified:** yes.

2. **Figure 1's inline-SVG raster copies the raster renderer without its rules** — `fig_problem`, :161-201.
   - Reusing `bugarach.ui.diagnostic.raster_panel`/`lane_panel` directly is not possible: they are HoloViews/Bokeh, and this page is inline-SVG only (`test_every_figure_is_inline_svg`). So a copy is justified, but it differs from the canonical one in three ways:
   - **(a) Row order.** It sorts by onset count over the *whole* recording (:165) and then draws a 940–1560 s window. `raster_panel` counts only inside the drawn extent (`diagnostic.py:364-384`, incident of 2026-09-07). I measured recording seed 1000: the two orders differ (Spearman 0.94). The in-window counts in drawn order are 111, 82, 94, 58, 54, 43, 32, 57… so the caption's "busiest ROI on top" is not quite true.
   - **(b) Tick height.** Ticks are 8 px in 10 px rows. `raster_panel`'s docstring (:339-349) keeps marks under about a third of the row pitch, because full-height dashes make every column look solid.
   - **(c) Distractor marker.** Distractors are drawn as filled orange ▼. `lane_panel` draws them hollow grey ▽ (:257-263), keeping filled ▼ for planted events.
   - **Severity:** minor.
   - **Fix:** sort with a stable argsort over counts inside `FIG1_WINDOW`, as `raster_panel` does. Better, add one inline-SVG `raster()`/`lane()` helper to the shared kit (see finding 8) that carries these rules. `build_surrogate_report.py:802` hand-rolls a second copy of the same raster.
   - **Verified:** yes.

3. **`Run.cmp` falls back to a copy of `_paired`** — :101-111.
   - **Canonical:** `tune_learned_vs_coact._paired`, `tools/tune_learned_vs_coact.py:1569-1575`, on branch `tune-bench-comparison` only. It cannot be imported from this branch, so a copy is reasonable.
   - **It matches exactly.** I recomputed every stored net-minus-coded comparison in `results.json` with the copy: the maximum difference in mean and in *t* is 0.
   - It drops two guards: the `len(d) < 2` branch, and the None→0.0 coercion that `summarize.column` applies (:1654-1655). Neither is hit by this data; a None would now crash rather than read as 0, which is the safer behaviour.
   - The copy is not just a fallback. It produces every coded-minus-CoactDetect cell in Table 2 (for example SCE +0.023, *t* = 3.10), which the run itself never computed.
   - **Severity:** minor.
   - **Fix:** add a test that pins the copy to `results.json["comparisons"]` for every stored pair. Cite `tune_learned_vs_coact.py:1569` and the branch in the docstring. Import the original once it lands on `main`.
   - **Verified:** yes.

4. **The provenance line drops the canonical dirty-tree guard** — :951-956.
   - **Canonical:** `build_surrogate_report.provenance_block`, `tools/build_surrogate_report.py:1960-1971`. It calls `provenance.git_dirty()` and, when the tree was dirty, says the commit "names a tree that exists nowhere else".
   - The built artifact reads `0.1.0+gbdbd77b.dirty` with no such sentence.
   - The named commit bdbd77b is not the one that holds the tool (805fee9), so the page cannot be regenerated from the commit it cites.
   - **Severity:** major.
   - **Fix:** move `provenance_block(tool, source)` into the shared kit, call it, and rebuild from a clean, committed tree.
   - **Verified:** yes.

5. **Choosing the darkroom destination is duplicated** — `main`, :969-994.
   - **Canonical:** `tools/figure_destination.py:19-43`.
   - `add_arguments` could be called as it is; the help text is identical.
   - `save` is matplotlib-only (`fig.savefig`), so its darkroom resolution was copied line for line.
   - **Severity:** minor.
   - **Fix:** call `figure_destination.add_arguments(ap)`. Split a `destination(args, subfolder) -> Path` out of `save` and use it here. That gives one implementation of the SAP006 default.
   - **Verified:** yes.

6. **The crowded check reuses goal 1's scoring but uses a different veto reference** — `tools/crowded_check_fair_comparison.py`.
   - **Reused correctly:** `search_all_settings._job`, `_key`, `TAIL`, `N_TAIL`.
   - **Matches goal 1 exactly:**
     - Seeds 1..`N_TAIL` equal `Evaluator.run`'s `self.seeds[:N_TAIL]` (`search_all_settings.py:228`).
     - The mean of the two backgrounds equals `Evaluator.summary` (:257-260).
     - The threshold `f1 >= ref - MAX_CROWDED_DROP` equals `make_admissible` (:291).
   - **(a) Reference setting.** For CoactDetect and LoCo the reference is the run's sliding base (:63). Goal 1's `main` uses the *shipped* `OPERATING_POINTS` (:875-889), with the comment "A veto is only as honest as its reference". The docstring says this openly.
     - I scored the shipped settings on the same 24 crowded recordings. LoCo scores 0.8165 (floor 0.7965) and CoactDetect 0.8077 (floor 0.7877).
     - **No verdict changes.** LoCo's gated choices (0.7713) fail against either reference, and every CoactDetect choice (0.820–0.837) passes either way.
   - **(b) Missing-reference guard.** When the reference is None, `make_admissible` admits the candidate (:285-286). Here a NaN reference refuses it (:99). No reference was NaN, so this had no effect.
   - **Severity:** minor.
   - **Fix:** record the shipped-point reference beside the one used in `crowded_check.json`, or state the difference in section 7.1. Factor a `crowded_ok(got, ref)` out of `make_admissible` so there is one veto clause, including one rule for a missing reference.
   - **Verified:** yes.

7. **The before-fix fold draw copies `fold_maker`/`train`/`pick_threshold` arithmetic in a script that was never committed** — the `fold_draws.json` "before_fix" half.
   - **Canonical:** `bugarach.learn.train.fold_maker` (`train.py:67-99`), `TRAIN_SEED_BLOCK`/`VAL_SEED_BLOCK` (:26-29), the draws in `train` (:174) and `pick_threshold` (:269).
   - **Canonical, pre-fix order:** `Plan.fold_recordings` (`tune_learned_vs_coact.py`; pre-fix use at `e8764aa^:770/792`; regime order quiet then busy, :103).
   - **Canonical, draw replay:** `Plan.fold_check.draws()` (:398-401) already replays these draws by calling `fold_maker(lambda r: r, recs)`.
   - **It matches exactly.** Recomputing through `fold_maker` reproduces all four `before_fix` entries (fitting and threshold recordings). The `as_run` half is also reproduced by the round-robin dealing plus `fold_maker`.
   - **But no code in the repository produces the file behind Figure 4.**
   - **Severity:** major (the figure's data cannot be reproduced, and the fix is to call existing code).
   - **Fix:** commit a small generator that calls `fold_maker` with identity `rec` over the pre-fix list, or add a test that recomputes `before_fix` that way. It is about 10 lines.
   - **Verified:** yes.

8. **The SVG page kit is imported from a 2,276-line report tool; there is no shared module** — :38.
   - `esc`, `num`, `table`, `Svg`, `figure`, `CSS` and `page` are defined only in `tools/build_surrogate_report.py` (:653-745, :1101-1134). The only other SVG producer is `third_party/draughtsman/render.py`, which does a different job.
   - Importing is correct; copying would be worse.
   - The costs:
     - The page silently follows any edit made for the surrogate report.
     - Importing pulls in `bugarach.surrogate_stats`.
     - The kit's render gate (`run_gate`, :2121) is not reused, so this page has none. Whether one is required is agent 10's call.
   - **Severity:** minor.
   - **Fix:** move the kit, plus `provenance_block` and `run_gate`, into a shared module (for example `tools/svg_page_kit.py`) and import it from both builders.
   - **Verified:** yes.

9. **Numbers are typed, or read from live code, where a canonical source or the run's record exists.**
   - "within {2.5:g} s" (:687) is a literal made to look computed; the source is `bugarach.score.TOL_SEC` (`score.py:60`).
   - "33 ROIs" (:166, :198, :240) and "15 planted events… 30%, 18% and 10%" (:678-679, :923) are typed; they are `BENCH_RECORDING` `n_roi`, `n_per_level` and `participation` (`bench.py:728-733`).
   - Every bench constant is read from the live `bench.BENCH_RECORDING`, not from `run.decl["bench_recording"]`, which records what actually ran. They agree today (I checked 8 keys), but nothing checks it.
   - **Severity:** minor.
   - **Fix:** read the constants from the declaration and from `score.TOL_SEC`, and assert live bench == declaration before simulating Figure 1.
   - **Verified:** yes.

10. **The display-name map is duplicated** — `NAME`, :47-49.
    - **Canonical pattern:** `{**TITLES, "cicada": "locust"}` (`make_bakeoff_summary_figure.py:53`, `make_detector_table.py:77`), or `search_all_settings.NAMES` (:635). The values match today.
    - **Severity:** minor.
    - **Fix:** build `NAME` from `TITLES` plus the locust override, and add the net names.
    - **Verified:** yes.

## Checked and clean
- **Time axis:** `Svg.time_axis` calls `bugarach.time_axis.ticks`/`label` (`time_axis.py:55, :74`), which `tests/test_time_axis.py` tests against the viewer's own BokehJS axis. This is correct reuse.
- **Figure 1's facts:** they come from `bench.make_recording`, `stream_trains` and `recording_extent`.
- **Refit collapses:** they use the run's own `failed_training_signature`.
- **Over-budget flags and selections:** read from the run's own files.

## Files
- `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\tools\build_fair_comparison_report.py`
- `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\tools\crowded_check_fair_comparison.py`
- `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\tools\build_surrogate_report.py`
- `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\tools\search_all_settings.py`
- `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\tools\figure_destination.py`
- `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\tools\make_architecture_diagram.py`
- `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\src\bugarach\ui\diagnostic.py`
- `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\src\bugarach\learn\train.py`
- `%USERPROFILE%\bugarach\bugarach-worktrees\tune-bench-comparison\tools\tune_learned_vs_coact.py`
- `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\fold_draws.json`
- `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\crowded_check.json`
