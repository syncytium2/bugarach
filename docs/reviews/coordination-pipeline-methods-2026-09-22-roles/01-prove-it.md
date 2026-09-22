# Role 1 — Prove It (round 1, verbatim as returned)

GRANT 1 ok — Read, Grep, Glob, Bash

# Role 1: claims and data check. Methods section (fast stream), round 1

**Artifact checked:** `docs\methods\coordination_pipeline_methods.md`. I spot-checked the built .html and .docx: they carry the same numbers and sentences as the source.

**What I checked it against:** the repo (main after pull, `34b3359`), `origin/tune-bench-comparison:tools/tune_learned_vs_coact.py`, the default export `2026-09-17_revised_2v_long_STEPS_AND_PINS_EXCLUDED`, and the 2026-09-21 full-cohort run folder. I also read `2026-09-17-full-search/{search.json, sliding5/search.json}` and `2026-09-18-replicate-run-status` in the darkroom.

I recomputed with scripts where I could. I did not edit any file.

## Findings

Each finding gives: location · issue · severity · suggested fix · whether I verified it against a source.

**F1 · Table 1 caption (l.166–167): "The other four use the settings they ship with, which the search did not change." · BLOCKING**
- This is false. The search that produced Table 1's CoactDetect and LoCo values is `2026-09-17-full-search/sliding5/search.json` (selection seeds 1–48, held-out seeds 49–96). The same run moved three of the other four detectors, and each move had a held-out gain whose 95% interval excludes zero:
  - SPIKE-synch `min_n` 3→2: +0.042 (0.030–0.054), close-events +0.051.
  - rate+context merge gap 3→8 s: +0.013 (0.009–0.018), close-events −0.008.
  - locust (99.99, 2 frames, 128-frame minimum distance): +0.119 (0.108–0.132), close-events +0.149, but stopped at the extension ceiling rather than at a bracketed optimum.
- Only binned SCE did not move.
- `HANDOFF-coded-detectors.md` l.343–346 lists these as "Still open, measured and not landed".
- **Fix:** say the search proposed changes for rate+context, SPIKE-synch and locust that were not adopted, and give the reason (or ⚠ it as pending).
- **Verified: yes.**

**F2 · l.91–92: "Every value agreed to four decimal places." · MAJOR**
- False. I recomputed both folders with `remeasure_bench`'s own estimators, and my steps-excluded numbers match `bench_measured.json` exactly:
  - rate shape 0.26878 → 0.26669
  - 300 s burst shape 1.79933 → 1.80005
  - 60 s burst shape 1.51575 → 1.51641
  - quiet and busy rates identical
- Commit `2120516` records the same moves ("largest move is 0.8% of the rate shape"). Only jitter, participation, n_roi and the two rates were identical to four decimals. The fact note's "other 7 agree to 4th decimal" is wrong at its source.
- **Fix:** "Five values were identical to four decimals; the three shape estimates moved by at most 0.8%, far inside their intervals."
- **Verified: yes (recomputed).**

**F3 · l.44–45 and l.81–84: the generator's parameters are described as "measured on the recorded data" in the stated windows · MAJOR**
- The values the bench actually uses were not produced by that measurement:
  - Rate shape 0.275 was fitted on a closed `.mat` archive (81 windows, 2,643 ROIs).
  - Burst shapes 1.547 and 1.388 were fitted on 85 windows. That is more recordings than the export's 84, so it is consistent with including the lab-withdrawn recording; I did not confirm that directly.
  - n_roi, jitter and participation came from a MATLAB summary (`bench.py` l.143–212; `remeasure_bench.py` docstring).
  - The two rates were derived 2026-08-20 from an older export that still had its artifacts.
- The 2026-09-17 bootstrap run only checked that these values fall inside the new intervals. The new estimates themselves are rate shape 0.269, burst 1.799 and 1.516, n_roi 31.5, jitter 0.319, quiet rate 0.00505.
- The sentence "Every measured value falls inside its 95% interval" also reverses the logic: it is the **benchmark** value that falls inside the interval of the measurement. n_roi 33 sits exactly at the upper bound (27–33).
- **Fix:** state the origin of each value and that the re-measurement is a consistency check. Rewrite as "every benchmark value lies inside the 95% interval of its re-measurement, except participation".
- **Verified: yes.**

**F4 · l.100–104: close-events test, "spacing matches the most crowded recorded data … 7 of 39 recordings" · MAJOR**
- Source is `tools/probe_real_crowding.py`, measured 2026-08-26 (commit `27e6c8f`):
  - "events" are **CoactDetect calls** at its then-shipped binned setting, not recorded events;
  - calls were counted over the **whole recording**, including senktide and high K+, not baseline;
  - the export was the one current then, with field steps and pins still in it;
  - 39 of 84 is the subset with at least 3 calls.
- A reader will take it as a property of the recorded events. It also conflicts with the rule that coordination properties come from baseline only.
- **Fix:** state the instrument, the scope and the folder, or re-measure on the current export in baseline windows.
- **Verified: yes** (tool code and docstring). I did not re-run the tool.

**F5 · l.217–219 against l.259–260: decoding threshold · MAJOR**
- The Decoding paragraph says the threshold maximises F1 on two held-aside recordings. The real-data model's 0.972 was **not** chosen that way.
- It is the **gated** threshold: the best inner-CV F1 over (configuration, threshold) pairs within the 1.6× CoactDetect false-alarm budget. See `tune_learned_vs_coact.py` l.1016–1028 and l.1519–1520, which overwrite the fit's own threshold for gated checkpoints.
- **Fix:** say that under the false-alarm-matched rule the threshold is part of the selected candidate, and that 0.972 came from that rule.
- **Verified: yes.**

**F6 · l.202: "Four architectures, each of 1,149–1,905 parameters" · MAJOR**
- That range is true only at the default configurations: tube 1,149; line_length 1,233; chorus_norm 1,897; chorus_gain_norm 1,905.
- I built the 24 configurations per architecture in `replicate1/configs/`. The comparison actually evaluated 1,122–4,565 parameters:
  - tube 1,122–4,307
  - line_length 1,179–4,565
  - chorus_norm 1,897–3,097
  - chorus_gain_norm 1,905–3,113
- **Fix:** give the default sizes and the tuned range separately.
- **Verified: yes (recomputed).**

**F7 · l.182–187: coordinate-search rule · MAJOR**
- The step list leaves out the rescue rule. When the current point is inadmissible, the search moves to the best admissible value even if F1 falls.
- Both Table 1 detectors started inadmissible: sliding CoactDetect at its shipped values ran 7.69 calls h⁻¹ against a limit of 7, and sliding LoCo ran 4.0 against 3. Their first moves were rescues that lowered F1: CoactDetect α 0.711→0.715, LoCo percentile 0.719→0.713.
- Other gaps:
  - The code moves only on a gain strictly greater than 0.002, not "at least".
  - Stage 2 (two-parameter grids for LoCo and locust) is omitted.
  - "Starting from its shipped setting" means the shipped values in sliding mode. The close-events reference, though, is the binned shipped point. Against their own sliding start, the Table 1 CoactDetect and LoCo lose 0.041 and 0.042 on close-events, which is over the 0.02 limit. Against the binned reference they gain.
- **Fix:** state the rescue rule, the stage-2 grids and the reference.
- **Verified: yes.**

**F8 · l.32–40: what the imaging pipeline removed · MAJOR (unit membership)**
The text lists two artifacts and one withdrawn recording. `PROVENANCE.md` also records:
- a dead-ROI roster that removed 66 ROIs from 15 recordings and never evaluated 18 recordings;
- two trailing treatments shorter than 240 s were dropped (e.g. `20240815a51` senktide);
- pinning below the census cut was left in place (`20260702_338`, `20260630_325`);
- `20260629_314` has never been screened for pinning. It is a TTX-first recording in the downstream 67.

Also:
- "In these windows an ROI reported the frame minimum" overstates it. The window is a deliberate envelope, the pinning inside it is intermittent, and some real events were removed with it.
- 381 and 83 are two-stream totals. The fast stream alone is 187 and 56. All 83 pinned events were in baseline.

**Fix:** list these producer decisions and the unscreened recording, and give fast-stream counts.
**Verified: yes.**

**F9 · l.162–163: "SPIKE-synch was verified to 10⁻⁹ against cSPIKE and PySpike" · MINOR**
- The PySpike check runs uncapped (`max_tau=1e6`) through a summed-coincidence identity, because PySpike's finite cap is broken (`tests/test_sync_detect.py` l.82–112). The 0.25 s capped profile actually used is verified against cSPIKE only.
- The cap is also cited only to Kreuz 2015 (SPIKY). The repo's own record attributes τ_max to Kreuz's 2017 paper (`docs/kreuz_note_2_apology.md` l.30).
- **Fix:** "profile verified to 10⁻⁹ against cSPIKE with the cap; against PySpike without it". Cite the source of the cap.
- **Verified:** yes for the tests; no for the paper itself.

**F10 · l.152–155: locust / CICADA attribution · MINOR**
- CICADA is named but not cited. `GLOSSARY.md` gives Zenodo 10.5281/zenodo.10041434 and Hamon et al. 2026.
- **Fix:** add the citation.
- **Verified:** yes (repo). No (the paper itself).

**F11 · l.302–304: "the widest CoactDetect call is 26.3 s, with 53 cells and 629 events" · MINOR**
- Correct only within senktide: `20250829_207`, OVX, 53 ROIs, amplitude 2.015 cells s⁻¹.
- Across the whole run the widest fast CoactDetect call is 37.6 s (high K+). The widest fast call of any detector is rate+context at 64.8 s (senktide, 37 cells, 1,046 events).
- "Widths above about 10 s" occur for rate+context (25 calls), LoCo (23) and CoactDetect (10), never for SCE, locust or SPIKE-synch.
- "Always less than 0.5 s apart" is an absolute nothing measures.
- **Fix:** scope the number and name the detectors affected.
- **Verified: yes (recomputed).**

**F12 · l.274–279: the 67 downstream recordings · MINOR**
- Counts are correct. The 67 come from **36 mice**, which the text does not say, so readers cannot see that recordings share animals.
- **Fix:** add the 36 mice (and, per group, the mice as well as the recordings).
- **Verified: yes.**

**F13 · l.76–78: event widths · MINOR**
- The quantiles were measured over **baseline-region** fast events (47,225) of the older 2026-08-18 export, not over all recorded fast events.
- On all fast events in the current export the upper quartile is 1.3 s. On current baseline regions it is 0.6/0.9/1.2, so the quoted values hold once scoped.
- **Fix:** say "baseline fast-event widths".
- **Verified: yes (recomputed).**

**F14 · l.9–10: "one row per event" · MINOR**
- 127 rows (87 fast, 40 slow) are `time_sec = NA` rows marking silent ROIs.
- **Fix:** mention them.
- **Verified: yes.**

**F15 · l.241–243: gated selection · MINOR**
- The comparison's coded search did not apply the Table 2 limits: no precision-change limit, and close-events only after the run. It also added a context ≤ 120 s validity rule and searched extra axes (`min_rois`, `detection_mode`, peak parameters).
- "The coordinate search above" implies the same rule.
- **Fix:** say that Table 2 was replaced by the two selection rules there.
- **Verified: yes** (`replicate1/meta.json` `hand_search`, `hand_axes`).

**F16 · l.270–272: which detectors run per window · MINOR**
- The learned detector also runs inside each window separately (`detect_folder._run_learned`); the text does not say so.
- LoCo, SCE and locust draw surrogates in one RNG sequence across **both** streams. So the fast-stream calls at seed 20260706 depend on the slow stream being present.
- **Fix:** add both points.
- **Verified: yes.**

**F17 · l.25–30: group definitions (DI, MALE, ORX, OVX) · MINOR**
- The export defines none of the four group expansions. The fact note flags them as coming from secondary sources.
- **Fix:** cite the lab record that defines them.
- **Verified: no.**

## Claim ledger

Each row gives the quoted value, where I checked it, what I found, and the verdict.

**Dataset and windows**

| quoted | checked against | found | verdict |
|---|---|---|---|
| 84 recordings / 2,630 ROIs / 44 mice | slices.csv | 84 / 2,630 / 44 | match |
| 168,755 fast / 95,320 slow events | event CSVs | same | match |
| groups (mice, recordings): DI 10/17, MALE 12/22, ORX 12/25, OVX 10/20 | slices.csv | same | match |
| frame interval 0.1 s, all recordings | slices.csv | 84 of 84 | match |
| field steps: 9 steps, 381 events, 9 recordings, ±2.0 s | tsv, PROVENANCE | same (both streams) | match (scope, F8) |
| pins: 8 windows, 83 events, 3 recordings | moco tsv | 8 / 83 / 3 | match |
| 1 withdrawn recording absent | PROVENANCE | 20250731_149 | match |
| 67 recordings = TTX 38 (11/9/9/9) + senktide 29 (6/5/10/8) | regions.csv | same | match |
| baseline window 17–20 min; treatment window 13–20 min; +2 min start, 20 min cap | regions.csv | same (all 67 follow the rule) | match |
| two short windows: 13.0 and 14.9 min | regions.csv | 13.0 and 14.94 | match |

**Simulator and bench**

| quoted | checked against | found | verdict |
|---|---|---|---|
| rate shape 0.275; burst shapes 1.547 (300 s) and 1.388 (60 s) | bench.py | same | match (origin, F3) |
| quiet 0.0052 / busy 0.0190 | REGIMES | same; current p25/p75 = 0.00505 / 0.01904 | match (origin, F3) |
| 15 planted events; 10/6/3 cells; renewal 120 s + gamma excess, CV 1; jitter 0.36 s | simulate.py, BENCH_RECORDING | same | match |
| 6 distractors × 6 cells, 120–1,100 s | code | same | match |
| elevated rate 1,200–1,500 s, 0.06 s⁻¹, 30 s ramp; no planted event within 120 s | code | same | match |
| widths: median 0.9, IQR 0.6–1.2 | quantile table | same (baseline only) | match (F13) |
| 2,700 s, 33 cells, 200 bootstrap draws | bench_measured.json | same | match |
| participation 0.190 (0.182–0.232) | bench_measured.json | 0.1905 (0.1818–0.2322) | match |
| agreement "to four decimal places" | recomputed | three values differ | **mismatch (F2)** |
| close-events: 10,800 s, 180 events, ≥6 s apart | TAIL_RECORDING | same | match |
| 7 of 39 recordings, crowding > 0.38, minimum gaps 6–26 s | bench.py docstring | same | match (provenance, F4) |

**Scoring and budgets**

| quoted | checked against | found | verdict |
|---|---|---|---|
| tolerance 2.5 s; one-to-one, closest pair first; precision excludes elevated-rate block | score.py, bench.py | same | match |
| Table 2 limits (18 values) | MAX_* constants | same | match |
| 0.002 move threshold, 3 extensions, 4 rounds, seeds 1–48 / 49–96, 400 bootstrap, 12 close-events seeds | search_all_settings.py | same (strictly >) | match (F7) |

**Coded detector settings (Table 1)**

| quoted | checked against | found | verdict |
|---|---|---|---|
| all 6 rows | run's detector_settings.csv + signature defaults | same | match |
| "search did not change" the other four | sliding5 search.json | three of four moved | **mismatch (F1)** |
| parity to 10⁻⁹ | tests | yes; PySpike check uncapped | partial (F9) |

**Learned detectors and comparison**

| quoted | checked against | found | verdict |
|---|---|---|---|
| 1,149–1,905 parameters | built all configurations | 1,122–4,565 | **mismatch (F6)** |
| 409.6 s crops; 41 thresholds from 10⁻⁴ to 0.9999; 2 s merge; pos_weight rule | train.py, meta | same | match |
| 4 × 12 seeds, 72 tuning recordings, 24 configurations (23 + default), 3 tuning / 5 refit seeds, 10 recordings per refit | meta.json | same | match |
| 1.6× CoactDetect budget | meta budgets | same | match |
| t > 3.182, factor √(3/7) | leaderboard.py; nb_factor 0.65465 | same | match |
| replicate model: fold 0, seed 2; threshold 0.972; F1 0.726 = upper middle of 20 refits | checkpoint (sha identical to the darkroom copy used), results.json | 0.97158; 0.72629; the two middle values 0.72418 / 0.72629 | match |
| surrogate seed 20260706 | run.json | same | match |

**Call measure**

| quoted | checked against | found | verdict |
|---|---|---|---|
| 1 s half-aperture, split at gaps > 0.5 s, amplitude = cells / max(width, 0.1 s), NaN below 2 cells | call_measure.py | same | match |
| 26.3 s / 53 cells / 629 events | calls_measured.csv | senktide only | match (scope, F11) |

**Citations**

| quoted | checked against | found | verdict |
|---|---|---|---|
| SPIKY 2015, Cossart 2003, Nadeau & Bengio 2003 | not checked against the papers | — | unverifiable (cap attribution, F9) |

## Sources the draft did not consult

- The group-membership record in slices.csv (`mouse_id`, `group_id`) was used. The count of mice among the 67 was not reported (F12).
- The withdrawal record (db4 `exclude`, via PROVENANCE) is honoured.
- The draft never used the dead-ROI roster, the dropped regions, or the pinning census gaps (`20260629_314` unscreened; two sub-threshold slices kept), even though all of them are in `PROVENANCE.md`, `READ_ME_FIRST_pinning.md` and `current_export.toml` beside the data (F8).
- `bench.MEASURED_ROLE` still names the archived `steps_excluded` folder, not the current default. That is a fact about the repo, not the draft, but it is why the bench record is not a record of the current export.
- There is no retraction or correction chain that bears on this draft. It is a first draft (`f6f0c26`), not a regeneration of an earlier export, so there was no older artifact to diff against.

---
*Transcription note: personal absolute paths were replaced with placeholders (sapper SAP004); nothing else was altered.*
