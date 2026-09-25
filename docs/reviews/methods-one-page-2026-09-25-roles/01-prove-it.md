GRANT 1 ok — Read, Grep, Glob, Bash (plus SubagentHandback, the report channel; no Edit/Write/NotebookEdit held)

# Role 1 (Prove It): claim and data check of `methods_one_page`

**Artifact:** `<repo>/docs/methods/one_page/methods_one_page.html`. I read the text from the HTML. The PDF is dated 20:25 and the HTML 20:03.

**PDF not checked:** I could not extract text from the PDF. `pdftotext` and `pdftoppm` are not installed, and `pypdf` crashes on import. So I have not confirmed that the PDF's text matches the HTML. That is a run limitation, and agent 10 should cover it.

**Scratch:** I wrote only `<scratch>/mb/r1_pdf.txt`, a failed extraction. No repo file was touched.

**Summary:** Nearly every number checks out against its source. There are three substantive problems:
- the stream definition contradicts the draft's own per-stream numbers;
- the Finn & Johnson citation is attached to CoactDetect, which the repo's own attribution table does not support;
- CoactDetect is described only in its sliding form, while fast's shipped operating point is still binned.

## Findings

Each row: location · issue · severity · suggested fix · verified against a source.

**1. Input, "detected by the same method and differing only in the width attached to each event"** · **Major**
- **Issue:** This is contradicted by the artifact's own numbers. If fast and slow differed only in width, they would carry the same onsets. The page itself gives different background rates (fast 0.0049/0.0169 Hz, slow 0.0024/0.0093 Hz) and different event counts per hour (9.7 against 22.0).
- **Where the error came from:** `docs/export_folder_spec.md` (the Extended 2026-08-28 note) says event *detection* is methodically identical in the two streams, and that the *exported duration* differs (half-prominence width for fast, peak minus t50rise for slow). The draft merged those two statements into "only the width differs".
- **Also:** the repo never says what makes the fast and slow signals different, so the page cannot say it either.
- **Fix, same length:** "detected by the same method in the fast and slow signal components, and exported with different width rules (…)". Ask the producer what separates the two components before stating it.
- **Verified:** yes.

**2. CoactDetect, "The method is a cell-averaging constant-false-alarm-rate (CFAR) test (Finn & Johnson, 1968)"** · **Major**
- **Issue:** This overstates the attribution.
  - The table in `docs/detector_history.md` §4 lists CoactDetect's CFAR *analogue* as "cell-averaging, per-cell test", with the attribution column left as "—".
  - Finn & Johnson is attributed to rate+context, and README.md says rate+context "does not carry the constant-false-alarm property".
  - README.md names the family CoactDetect belongs to as excess-coincidence testing against a rate-preserving null (Grün et al. 2002; Amarasingham et al. 2012).
  - The history records that the lab's detectors were designed independently and "reconstructed elements of CFAR".
- **Fix, same length:** "It is analogous to cell-averaging CFAR detection (Finn & Johnson, 1968)". Or cite Grün 2002 as the family instead.
- **Verified:** yes.

**3. CoactDetect paragraph: S(t) over (t − w, t], with an exact circular-shift null** · **Major**
- **Issue:** This describes only the sliding form. Fast's shipped operating point in `bench.OPERATING_POINTS['coact']` is still binned: 2 s bins, 100 Monte Carlo surrogates, α 1e-4, 60 s context. Its source string says "NOT YET SWITCHED TO SLIDING".
  - Slow and combined are shipped as sliding.
  - The search runs every stream in sliding form (`tools/search_all_settings.py --sliding`).
  - The 2026-09-24 detection run used a sliding proposal on fast that was never adopted.
- **Fix:** Confirm that the flow runs sliding on fast before shipping this sentence. If it does not, add "(fast: fixed 2 s bins, sampled null)". Optionally say the null is computed exactly (Poisson-binomial) rather than sampled; that costs no length.
- **Verified:** yes.

**4. Output, "onsets within a fixed aperture around the call's centre"** · **Minor**
- **Issue:** The aperture is not fixed. `call_measure.measure_call` widens it to cover the call's own reported span (`window=`) whenever the detector gives one. Two other omissions: the width is floored at one frame (0.1 s), and amplitude is NaN for a one-ROI core.
- **Fix:** "an aperture around the call's centre, widened to its span". A net-zero wording is possible.
- **Verified:** yes.

**5. Scoring, "matched one-to-one to planted events within 2.5 s"** · **Minor**
- **Issue:** The 2.5 s tolerance is measured to the call's *span* [onset, onset+width], not to a point. A call whose span contains the event matches at any distance (`score.score_detections`).
- **Fix:** "within 2.5 s of the call's span".
- **Verified:** yes.

**6. Scoring, "Precision, recall and F1 … are pooled over recordings"** · **Minor**
- **Issue:** Scores are pooled over seeds *within* each background, then averaged across the quiet and busy backgrounds (`mean_f1` in `search_all_settings.py` and `score_bench_candidates.py`).
- **Fix:** "pooled over recordings per background and averaged over the two backgrounds".
- **Verified:** yes.

**7. Scoring, "a precision drop of at most 0.10"** · **Minor**
- **Issue:** The value is right, but the sentence never says what the drop is measured between. `MAX_PRECISION_DROP` is the precision difference between the quiet and busy backgrounds at one setting. As written, a reader could take it for the retired close-events veto.
- **Fix:** "…between quiet and busy backgrounds".
- **Verified:** yes.

**8. Participation, "(fast 0.20)"** · **Minor**
- **Issue:** Every other parameter on the page gives all three streams; this one gives fast only. The middle levels are slow 0.375 and combined 0.25 (`bench_slow.BENCH_RECORDING`, `bench_combined.BENCH_RECORDING`).
- **Fix:** "(fast 0.20, slow 0.38, combined 0.25)". Adds about 3 words.
- **Verified:** yes.

**9. Input, "Every parameter taken from data below was measured on baseline windows only"** · **Minor**
- **Issue:** It sits just before the Participation floor paragraph, but the floor is computed for *every* window, treatment windows included. In `detect-66-floors`, 128 of the 194 fast CoactDetect windows are treatment windows. Treatment windows are also scored under the carried-over baseline floor (ADR-0008 decision 4), which the page omits.
- **Fix:** Narrow the claim to "Every simulation parameter…".
- **Verified:** yes.

**10. Dataset sentence: how the 66 were selected, and the groups spelled out** · **Minor**
- **Issue 1:** The page never says how the 66 were chosen. They are every recording whose first treatment was TTX (37) or senktide (29) (`2026-09-23-first-treatment-by-recording.csv`, `current_export.toml`).
- **Issue 2:** The spelled-out group names (diestrus, ovariectomized, orchidectomized) are not defined anywhere in the repo, so I cannot check them against a source.
- **Fix:** Add "whose first treatment was TTX or senktide" if space allows. Have Tony confirm the group names.
- **Verified:** partly (the counts yes, the names no).

**11. Output: `core_n_roi` on combined** · **Minor, for your information**
- **Issue:** The realistic-bench check shows combined's `core_n_roi` over-counts the planted participants in 75–84% of events (median +2 to +3 cells). ADR-0010 ruling 3 leaves adoption of `call_measure` to be decided per stream. The page presents width and amp as settled outputs on every stream.
- **Fix:** Nothing on this page (it is a Results matter), but the Methods should not imply validation.
- **Verified:** yes.

## Design record and unit membership

- **Source of record:** It exists. `slices.csv` in the export folder is not on this machine, but the committed `docs/learned/runs/2026-09-23-first-treatment-by-recording.csv` carries group, mouse and first treatment for 84 recordings, and `2026-09-24-detect-66-floors/windows.csv` carries group and mouse.
- **Reconciliation:** The 66 `slice_id`s in `real-intervals/windows.csv` give DI 17, OVX 17, MALE 13, ORX 19 recordings, 36 mice and 2,109 ROIs. All match the page.
- **Withdrawn unit:** `20250731_149` (db4 `exclude == 1`) is absent, as it should be.
- **Pinned recordings:** The four moco-pinned recordings are present with their pinned events removed by the producer. The `senktide_ttx` table carries no contamination note.
- **Shared subjects:** 66 recordings come from 36 mice. The page makes no claim of independence across recordings, and its bootstrap is over simulated seeds, so there is no finding here. Pooling gaps across recordings from the same mouse is descriptive only.

## Claim ledger

Columns: quoted value · cited source · recomputed value · verdict.

**Dataset (Input paragraph)**
- 66 recordings · `current_export.toml`; `real-intervals/windows.csv` · 66 distinct slice_ids · match
- 2,109 ROIs · `current_export.toml` note · 2,109 (summed `n_roi`) · match
- 36 mice · `detect-66-floors/README.md` · 36 distinct mice (first-treatment csv joined to the 66 ids) · match
- DI 17, OVX 17, MALE 13, ORX 19 · windows.csv · 17 / 17 / 13 / 19 · match
- 0.1 s frame grid · windows.csv `dt` · 0.1 on all 198 window-stream rows · match
- t50 (half-rise) onsets · `export_folder_spec.md` · `time_sec` = t50rise · match
- "fast and slow differ only in width" · `export_folder_spec.md` · detection identical, duration differs, event sets differ · **mismatch** (finding 1)
- Combined stream is a labelled union and keeps near-coincident onsets · `combined.py` · `combine()` concatenates and sorts; nothing dropped · match
- Detectors read onsets only · `combined.py` docstring; `encode.py` · match (for CoactDetect and chorus)
- Group names spelled out · no repo definition · — · unverifiable

**Participation floor**
- J = 20 s, uniform [−J, J), a shift per ROI · `event_floor.py` (`J_SEC`, `rigid_frames`) · match
- 1,000 shifts · `MIN_DRAWS` = 1000 · match
- 2 s window · `WINDOW_SEC` = 2.0 · match
- ≤ 1 per hour · `FA_PER_HOUR` = 1.0 · match
- ≥ 3 ROIs · `MINIMUM_ROIS` = 3 · match

**Parameters for simulation**
- Timing spread fast 0.105 s · `jitter-correlogram-senktide-ttx` · 0.10476 · match
- Timing spread slow 0.131 s · same run · 0.13057 · match
- Timing spread combined 0.150 s · `jitter-correlogram-combined-senktide-ttx` · 0.15027 · match
- Background fast 0.0049 / 0.0169 Hz · `coordination-rates-senktide-ttx` (adopted: 1 s window, fixed model) · 0.004948 / 0.016895 · match
- Background slow 0.0024 / 0.0093 Hz · same run · 0.00239 / 0.00932 · match
- Background combined 0.0071 / 0.0292 Hz · same run · 0.00708 / 0.02916 · match
- Gamma-distributed rate factors, fitted shapes · `bench.MEASURED_RATE_SHAPE` (0.291), `MEASURED_BURST_SHAPE`; `simulate.py` · match
- Participation, fast 0.20 · `bench_measured.json` · 0.203 · match (slow and combined omitted, finding 8)
- Gap medians 41.3 / 25.1 / 24.8 s · `real-intervals/summary.json` · 41.25 / 25.10 / 24.80 · match
- 9.7 / 22.0 / 25.3 events per hour · same · 9.717 / 22.047 / 25.3 · match
- Events located without a detector, peaks at or above the floor · `real-intervals/README.md` · match (events under 2 s apart are also merged; not stated)

**Simulated recordings**
- 32 ROIs, the measured median · windows.csv median 32; `BENCH_RECORDING` 32 · match
- 45 min · `duration_sec` 2700 · match
- Events per recording 7 / 17 / 19 · `bench.realistic_counts`: round(rate × 0.75) · 7.29→7, 16.54→17, 18.98→19 · match
- Gaps pooled over the four groups · `spacing_overrides`, pool = "pooled" · match
- Six decoys · `n_distractors` = 6 · match
- Empty recording at the quiet background · `NULL_RECORDING` · match
- 300 s stretch at the 99th percentile · `ELEVATED_RATE_RECORDING` 1200–1500 s; `probe_background_hz` 0.1334 = 99th percentile · match
- ORX variant · `SPACINGS` "orx" · match
- Seed sets disjoint; fast's doubled · `seed_factor`; the search, scorer and training seed ranges · match

**Scoring**
- 2.5 s · `score.TOL_SEC` · match (the tolerance is to the call's span, finding 5)
- Events under the floor are "don't care" · `score_detections`, `care` · match
- Merge count · `n_merged_calls` · match
- Empty-recording budgets 7 / 1 / 10 calls per hour · `MAX_FALSE_POSITIVES_PER_HOUR['coact']` in each bench · 7 / 1 / 10 · match
- 1 call per minute in the stretch · `MAX_PROBE_PER_MIN['coact']` = 1.0 on all three benches · match
- Precision drop 0.10 · `MAX_PRECISION_DROP['coact']` = 0.10 on all three · match (definition omitted, finding 7)

**CoactDetect**
- Sliding S(t), circular-shift null, z, α, guard, merge gap · `coact.py`, `sliding.py` · match for sliding mode; fast's shipped point is binned · **partial** (finding 3)
- Cell-averaging CFAR (Finn & Johnson 1968) · `detector_history.md` §4; README · attribution "—" for CoactDetect · **mismatch** (finding 2)
- α down to 6×10⁻¹⁶ · `ALPHA_CAP` = 6e-16 · match
- Contexts 20–120 s · `CONTEXT_MIN_SEC`, `CONTEXT_MAX_SEC` · match
- Guard ≤ ¼ of the context · `GUARD_MAX_CONTEXT_FRACTION` = 0.25 · match
- Adoption rules (bootstrap interval above 0, bracketed, within budgets, off-limit values are findings) · `score_bench_candidates.py`; ADR-0010 ruling 5 · match

**Chorus**
- chorus_norm architecture (shared per-ROI dilated filter, per-channel standardising, sigmoid vote) · `nets/chorus.py`, `chorus_norm.py` · match
- Pool: mean, SD, mean of the top 4 · `top_m` = 4 · match
- About ±27 s receptive field · per-ROI stack depth 4 → 31 frames; head depth 8 → 511 frames; together 541 frames = ±27.0 s · match
- chorus_norm_part: count, floor input, membership · `chorus_norm_part.py`; `participation.py` · match
- Adam, lr 0.01, 900 steps, 409.6 s crops · `train_learned_on_bench.py`: lr 1e-2, 900 steps, crop 4096 frames × 0.1 s · match
- Class-weighted BCE · `train.py`: `BCEWithLogitsLoss(pos_weight)` · match
- Planting at floor − 1, floor, floor + 1; sub-floor events labelled negative · `boundary_recording`, `floor_labels` · match
- 5 seeds; best on the test seeds within CoactDetect's empty-recording budget · `--seeds` default 0–4; module docstring · match
- 2,000 resamples, paired and over seeds · `score_bench_candidates.BOOTSTRAP` = 2000 · match

**Output**
- Apertures ±1 s / ±5 s / ±5 s; gaps 0.5 / 2.5 / 2.5 s · `call_measure.DEFAULTS` · match (the aperture is widened to the call's span, finding 4)
- Core = the group with the most distinct ROIs · `measure_call` · match
- Width = the core's first-to-last onset span · `core_span_sec` · match
- Amplitude = core ROIs ÷ width · `amplitude` · match
- Output columns onset, span, participating ROIs · `export_folder_spec.md` `detections.csv` (`onset_sec`, `width_sec`, `n_roi`) · match

**References**
- Finn & Johnson, RCA Review 29(3):414–464 · README.md · match (bibliographic details)
- Zaheer et al. 2017 · cited in `nets/chorus.py` · match (arXiv id not in the repo; correct from general knowledge)
- Yu & Koltun, Kingma & Ba, Efron · not cited elsewhere in the source tree · details consistent with the published records · not checkable from the repo

## Retractions checked
None of these reappears on the page:
- the retracted 0.36 s jitter;
- the 0.19 participation (replaced by 0.203);
- the retired close-events veto (`MAX_CROWDED_DROP`);
- the retired forward-only review filter;
- the 84-recording dataset of the 2026-09-22 draft.

## Key source files
- `<repo>/docs/export_folder_spec.md`
- `<repo>/docs/detector_history.md`
- `<repo>/README.md`
- `<repo>/src/bugarach/bench.py`
- `<repo>/src/bugarach/detectors/coact.py`
- `<repo>/src/bugarach/score.py`
- `<repo>/src/bugarach/call_measure.py`
- `<repo>/docs/learned/runs/2026-09-25-real-intervals/summary.json`
- `<repo>/docs/learned/runs/2026-09-23-first-treatment-by-recording.csv`
