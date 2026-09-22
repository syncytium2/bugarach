# Role 7 — Reinventing the Wheel (round 2, blind pass, verbatim as returned)

GRANT 7 ok — Read, Grep, Glob, Bash (plus SubagentHandback for the hand-off only; I hold no Edit, Write or NotebookEdit)

Role 7, Reinventing the Wheel. Blind pass on `docs\methods\coordination_pipeline_methods.md` at 464d995. I did not open the round-1 role reports. I did read the cover memo, `docs/methods/coordination_pipeline_methods_cover_memo.md`, while looking for provenance. F1, F2 and F4 overlap its §1 and §3. I checked each one against the code myself, and the evidence below is from the code, not from the memo.

## Findings

**F1: LoCo and locust rates count calls from outside the analysis window. The text says they don't. Severity: high. Verified: yes.**
- **Where:** methods l.351, "A call counts toward a window when its onset lies inside it". The same sentence underlies the whole *Rates* paragraph. Code is `tools/make_before_after_figure.py:96-108` and `:153-183`.
- **What happens:** LoCo and locust tag each call with its **raw period**, not its analysis window: `_tag_region` at `src/bugarach/detectors/loco.py:483-487` and `detectors/cicada.py:422-426` tests `raw_start <= onset < raw_end`. Then `detect_folder._run_nested` (`src/bugarach/detect_folder.py:541-555`) maps that label to the window's `region_idx`. `make_before_after_figure.counts` counts every such row and `rates` divides by `w.win_dur`.
- **Effect:** calls from the first 2 min of treatment, and from any baseline before its last 20 min, go into a numerator whose denominator leaves that time out.
- **Existing code it should use:** each detector already computes the in-window flag, `w.win_start <= onset < w.win_end`, returned as `in_stats_window` (loco.py:69, cicada.py:102, sce.py:426). `emit.COLUMNS` (`src/bugarach/emit.py:125-127`) drops it.
- **Not affected:** binned SCE in `analysis_mode="regional"` runs one pass per trimmed window ("within trimmed window by construction", sce.py:397). CoactDetect, rate+context and SPIKE-synch run per window (detect_folder.py:493-519).
- **Suggested fix:** carry `in_stats_window` through `emit` into `detections.csv`, or have `_run_nested` set `region_idx=None` when the flag is false. Then count on that flag rather than re-deriving membership from the period label, and regenerate. Until then, l.351 is untrue for two of the six detectors.

**F2: `measure_calls` works out a call's span itself instead of using the scorer's rule, and gets binned SCE wrong. Severity: high for SCE width and amplitude. Verified: yes.**
- **Where:** methods l.367-368 (the window of events considered is "anywhere within the call if the call is longer than 2 s"; the centre is onset plus half the reported width). Code is `tools/measure_calls.py:54-59` and `src/bugarach/call_measure.py:196-204`.
- **The existing rule:** the "which stretch does a call cover" rule lives in `src/bugarach/score.py:281-318`. `EXTENT_FIELD = "extent_sec"` is preferred over `width_sec`, because for binned SCE `width_sec` is `tlast - tfirst`, the spread of events in the bin (sce.py:336-342). `onset` is the first bin's start.
- **What `measure_calls` does instead:** it builds `(onset, onset + width_sec)` and a centre `onset + width/2`. For SCE that is the bin start plus half the event spread, so it can sit seconds before the events the call was made on. `call_measure.measure_call`'s own docstring (l.151-156) describes this failure for SCE and says widening fixes it. The widening uses the same wrong window, so it does not.
- **Scoring is fine:** methods l.189-190 ("binned SCE's interval is its bin") matches `score_stream`.
- **Suggested fix:** export `extent_sec` in `detections.csv` and have `measure_rows` take the call window and centre from it when present, using the same preference as `score_stream`. Then re-measure SCE. Until then, the section applies "one rule for every detector" to a wrong input for SCE.

**F3: Table 4's LoCo and CoactDetect settings are not what the pipeline ships, and no file in the tree records them. Severity: high for reproducibility. Verified: the code half yes; whether the recorded-data run used them, no.**
- **Where:** methods l.240 ("The settings chosen for CoactDetect and LoCo were adopted (Table 4)"), l.338 ("run on every recording with the Table 4 settings") and Table 4.
- **What the code ships:** `bugarach detect` without `--settings` takes `bench.OPERATING_POINTS` through `detect_folder.detector_params` (detect_folder.py:453-490). At this commit those points are **binned**:
  - LoCo: 99.5, merge 2 s (bench.py:538-539).
  - CoactDetect: context 60 s, α 1e-4, and the signature's merge gap of 3 s (bench.py:597-598).
  - Both carry "⚠ NOT YET SWITCHED TO SLIDING" (bench.py:532-537, 545, 595-602).
- **Where Table 4's values do appear:** only as prose in those `source` strings. LoCo sliding is 99.9, symmetric, merge 8 s, 120 s. CoactDetect sliding is α 1e-5, 120 s, merge 8 s, guard 1 s. I found no settings CSV in the tree carrying `window_mode` or these values; the only matches are per-fold bake-off files.
- **Suggested fix:** either land the switch in `OPERATING_POINTS` (the canonical home) or commit the settings CSV the run used, and cite it in the run record. Otherwise the methods claim a setting the code says is not adopted. Table 4's other rows do match (see below).

**F4: binned SCE is grouped with the per-window detectors, but the code runs it on the whole recording. Severity: low. Verified: yes.**
- **Where:** methods l.348-350 and `detect_folder.py:77-85, 113-115` (`NESTED = ("loco", "sce", "cicada")`).
- **Why it is only low:** the claim holds in effect. `sce_detect`'s default `analysis_mode="regional"` builds its own null per trimmed window (sce.py:10-15, 379-397), and l.339-340 already says SCE shares one RNG sequence across streams. But the code routes it with LoCo and locust.
- **Suggested fix:** one clause, e.g. "binned SCE runs on the whole recording but computes its null and threshold separately inside each analysis window".

**F5: `tools/run_learned_on_folder.py` copies `detect_folder._run_learned`. Severity: low to medium. Verified: yes.**
- **Where:** the copy is `run_learned_on_folder.py:233-251`; the original is `detect_folder.py:560-592`. Both do the same per-window `trained.predict(extent=...)` → `DetectedEvent` loop, with identical fields.
- **Divergence already present:** the tool throws away the settled slice from `folder_analysis_windows` (`_, wins = ...`) and predicts on the unsettled one. `detect_slice` passes the settled slice on (see the `folder_analysis_windows` docstring, detect_folder.py:249-253).
- **Unknown:** which of the two paths produced the recorded-data learned calls (methods l.342-346). I could not tell from the tree.
- **Suggested fix:** call `detect_slice(..., models=[trained])` or `_run_learned` from the tool, and name the path in the run record.

**F6: Figure 1's tool hard-codes the benchmark's participation levels and cell counts. Severity: low, but it bites on the open 0.18 → 0.19 decision. Verified: yes.**
- **Where:** `tools/make_methods_bench_figure.py:30, 50, 61-62`.
- **What it does:** `LEVELS = ((0.30,…),(0.18,…),(0.10,…))`, the tick labels "10 cells", "6 cells", "3 cells" and "distractor · 6 cells" are fixed, and rows are selected with `np.isclose(gt.frac, frac)`. The canonical values are `BENCH_RECORDING["participation"]`, `["n_roi"]` and `["distractor_frac"]` (bench.py). If participation moves to 0.19, the 18% row goes silently empty and the labels stay stale.
- **Suggested fix:** derive the levels, colour order and cell counts from `BENCH_RECORDING`, e.g. `round(frac * n_roi)`.
- **Justified re-implementation:** the tool builds its own lane rather than calling `diagnostic.lane_panel`. That is reasonable: with no detector lanes, `lane_panel` draws one "planted" row coloured found/missed, not one row per participation level.

**F7: `call_measure` reads `stream.locs` where the text and five of six detectors use `t50rise`. Severity: low, latent. Verified: yes.**
- **Where:** `call_measure.py:96` (`stream.locs`) against methods l.367 ("whose t50rise lies within…"). `detect_folder.ONSET_FIELD` (l.129-130) anchors five detectors on `t50rise`.
- **Why it doesn't matter today:** on an export folder `locs` is `t50rise` (`src/bugarach/io.py:162-167`), so today's numbers are unaffected.
- **Why it could:** on a store `Slice`, `locs` is the peak, and the measure would silently switch anchors.
- **Suggested fix:** read `stream.t50rise`, as `coact_detect` and `sync_detect` are called at detect_folder.py:512-514.

**F8: `make_before_after_figure` keeps its own detector display-name map. Severity: low. Verified: yes.**
- **Where:** `DETECTOR_NAME` at `make_before_after_figure.py:73-77`, beside `diagnostic.TITLES`.
- **Why a second copy exists:** the tool keeps it deliberately, because `TITLES` still says "sixth" for locust (diagnostic.py:288-291).
- **Suggested fix:** correct the name in `TITLES`, then use one map.

## Parts that match the code exactly

**Width and amplitude.** The ±1 s aperture and 0.5 s gap are `call_measure.DEFAULTS["fast"]`. The core is the group with most distinct cells, ties to more events and then nearest mean time. Width is the core's first-to-last onset. Amplitude is cells ÷ max(width, `dt`) with `dt` from the recording (0.1 s). It is NaN for one cell, and NaN or undefined when there are no events. For calls under 2 s, the union of aperture and call window equals the text's rule. `call_center` is onset + width/2. Source: call_measure.py:62, 158-204; measure_calls.py:51-59.

**Rates.** The denominator uses the one canonical window function, `detect_folder.folder_analysis_windows`, and does not work it out again (make_before_after_figure.py:80-93). Rates are calls ÷ `win_dur`, in minutes, not per cell. Baseline and first treatment only, via `--first-only` (`first_after`, no duplicate anywhere in src/tools).

**Per-window and per-recording runs.**
- Run per window: rate+context, CoactDetect, SPIKE-synch, and the learned models in `detect_folder`.
- LoCo's context clamps to raw period bounds (`clamp_context_to_region=True`, loco.py:434-435), so "context stops at period boundaries" is correct.
- locust uses `threshold_scope="global"` by default (cicada.py:65, 175).
- The seed is 20260706 (`RNG_SEED`, detect_folder.py:109).

**Scoring.** All of this matches `src/bugarach/score.py:60, 171-276` and `bench.py:1114-1160`:
- tolerance 2.5 s (`TOL_SEC`);
- a call is the interval [onset, onset + width], with gap 0 inside it;
- one-to-one, closest pair first (ties by distance to the span midpoint, which the text doesn't mention and doesn't need to);
- binned SCE is scored over its bins through `extent_sec`;
- rate+context's width includes the ±0.5 s pad (`CHARACTERIZATION_PAD_S`, rate.py:17, 47);
- distractor hits are false alarms;
- precision leaves out elevated-block calls (`BenchResult`, which counts overlap with the block rather than onset inside it: a harmless difference in wording).

**Table 4, apart from F3.**
- rate+context: 4.5 events s⁻¹, 60 s, 1 s, merge gap 3 s.
- binned SCE: 10 s, 98, 200 surrogates, `min_rois` 3, `merge_gap_sec` NaN (no merging).
- locust: 99.999, 1 synchronous frame, minimum distance 4 frames, 100 surrogates.
- SPIKE-synch: `C_threshold` 0.1, `C_min` 0.1, `tau_max` 0.25 s, `max_gap` 0.5 s, `min_n` 3.
- These all match `OPERATING_POINTS` and the signatures. Minimum cells = 3 is the `coact_detect` and `loco_detect` default.

**Figure 1 tool.** It uses `bench.make_recording("baseline_quiet", 1)`, `BENCH_RECORDING["hot_window"]` (1,200–1,500 s, the same as `gt.params`), `diagnostic.raster_panel` with nothing drawn on it, `ui.app._time_axis_hook`, and `make_generator_figures._write`, and it defaults to the darkroom. The recording has 15 planted events, 6 distractors, 33 cells and levels {0.1, 0.18, 0.3}, which matches the caption and l.62-92. `BENCH_RECORDING` agrees with the text on duration, jitter, spacing, shapes, block rate and ramp, and the distractor window.

## Surface examined
The methods text as a whole, plus these files in the worktree:
- `src/bugarach/call_measure.py`, `tools/measure_calls.py`
- `tools/make_before_after_figure.py`, `tools/make_methods_bench_figure.py`
- `src/bugarach/detect_folder.py`, `score.py`, `emit.py`, `io.py`
- `src/bugarach/bench.py` (`OPERATING_POINTS`, `BENCH_RECORDING`, `BenchResult`)
- `detectors/{sce,loco,cicada,rate}.py` and the signatures of `sync_detect`, `coact_detect` and `loco_detect`
- `src/bugarach/ui/diagnostic.py` (`lane_panel`, `raster_panel`)
- `tools/run_learned_on_folder.py`

I also searched the whole tree for any existing member-event or first-treatment helper and for any committed sliding-mode settings CSV. There is none of either, apart from the per-fold bake-off files.

---
*Transcription note: personal absolute paths were replaced with placeholders (sapper SAP004); nothing else was altered.*
