GRANT 1 MISMATCH — missing Grep, Glob; holds Read, Bash (no forbidden editing tools)

# Claim verification: `docs/learned/tube_self_supervised/README.md`

I recomputed the numbers from the raw stage outputs, not from `summary.json`: all three bake-off seed files, `controls_lab/results.json`, `aggregate_leak/results.json`, the 360 rows of `training/results.jsonl`, `real_compare/{summary,events}.json`, `probe/line_vs_fuzz.json`, and the lab export folder for the window-edge shares. I also reran the summariser at HEAD on a scratch copy. Every section of the rebuilt `summary.json` is byte-identical to the committed one. So the summariser's computations hold, and the problems below are in the prose, the provenance and one tool.

The artifact's numbers are almost entirely correct. There are four medium findings: one pooling claim that one agreement column breaks, a sentence that compares two different quantities, a misread of Louis et al. 2010, and two sourcing claims wider than what the files can show.

## Findings

| # | location | issue | severity | suggested fix | verifiable against source? |
|---|---|---|---|---|---|
| F1 | "On real recordings" agreement table, first column (0.856/0.752 … 0.752/0.601), and the sentence "Every row pools its seeds" | `tools/tube_ssl_real_compare.py` computes `ref -&gt; det` against `detector_events[det][:1]`, which is **the seed-0 run only**. The second column (`det -&gt; ref`) pools all three seeds. So the column "share of CoactDetect's / LoCo's events it overlaps" is one training seed, while the page says every row pools its seeds. The ranking claim built on it ("`line` … fourth of the five here on overlap") also partly rests on one seed. | medium | Say the first column is seed 0 only, or pool the seeds in the tool and rerun that step. | yes |
| F2 | "Calls from models trained against rigid shift mostly hold one ROI or none … (median 0–1 within ±2 frames), against 0.07–0.13 for random times" | **Two different quantities are compared.** 0.07–0.13 is the random baseline's *share of calls with ≥ 3 ROIs* (0.073–0.132). The random baseline's *median* is 0 in all ten rows. The number is right but sits against the wrong statistic. | medium | Compare like with like: "share ≥ 3 of 0.13–0.24 against 0.07–0.13 for random times", or "median 0–1 against a random median of 0". | yes |
| F3 | Published-lineage section: "Louis, Borgelt &amp; Grün 2010 … warns that dropping is acceptable only where start and end rates match" | **Attribution inverted.** Louis 2010 (chapter 17, section 17.3.3) says *rolling* (wrapping) is acceptable for their data because start and end rates are the same, and that elsewhere the analysis window may need adjusting. It says nothing about when dropping is acceptable. What it does say correctly supports the rest of the sentence: it rolls "not to underestimate the expected coincidence count". | medium | "…and notes that rolling is itself acceptable only where start and end rates match." | yes (the PDF in the lit folder, `surrogates/`) |
| F4 | Header note: "Every number on this page is in `summary.json`" | Several numbers are **not keys in `summary.json`**: 1,501 window pairs, 84 recordings and 44 mice (they are in the raw `controls_lab`/`aggregate_leak` files only), 1.04–1.15 (a comment in `tests/test_line_vote.py`; I reran it and got 1.04–1.15), 0.31 s jitter (`generator_spec.json`), 0.36 s / 0.42 s / 47 slices (`docs/generator.md`), 25 ms (Stella 2022), 12 fields, 32 ROIs, 4,096 frames and 900 steps (tool constants and meta). The "10–69 %" tie range has to be derived: the per-cell `tie_share_max` in the summary includes the tube fits at 1.00. All of these are correct, but the summary does not contain them. | medium | Narrow the sentence to "every result quoted from this run's outputs", or add these keys to the summariser. | yes |
| F5 | Provenance: "every other stage at `b85b5c9` … the run records say `git_dirty: null`" | Only `aggregate_leak/meta.json` and `training/meta.json` record commit `b85b5c9` with `git_dirty: null`, and the bake-off files record `70201e7` / null. **`controls_lab/meta.json`, `real_compare/summary.json`, `probe/line_vs_fuzz.json` and the checkpoints carry no commit or dirty field.** For three stages the claim cannot be checked from the stored outputs. `summary.json` itself records `c82f560` with `git_dirty: true`; I confirmed HEAD reproduces it byte-for-byte, so that one is harmless. | low–medium | Say which run records carry the stamp, and that the controls, real-recording and probe outputs do not. | partly |
| F6 | Truth-reading coverage paragraph: "the tube family at both displacements and `line_bound` at 20 s cover 0.93 or more" | The `tube` cell on simulated recordings at 20 s has a median coverage of **0.9276**, below 0.93. | low | "0.92 or more". | yes |
| F7 | Figure 3 caption: "Panel C … both displacements pooled (24 fits per model)", against the prose "Panel C, the paired checks (… per-cell means)" | The prose ranges are per displacement (12 fits per cell). Pooled per model they would be: rigid shift 0.727–0.751, thinned 0.819–0.932, same-crop offset 0.486–0.527, independent crop 0.456–0.506, twins 0.475–0.550. The prose and the caption describe different units. | low | Make the prose and the caption use the same pooling. | yes |
| F8 | "10–69 % of crops in a cell" | This is the range over individual **fits**, not cells, with the two tube fits at 1.00 left out. Per-cell mean tie shares are 0.256–0.415. | low | "on 10–69 % of crops per fit (two `tube` fits tie on all of them)". | yes |
| F9 | Label-free threshold for the supervised models | On the bench (`tube_self_supervised.py`) the supervised and untrained label-free thresholds use rigid shifts at *J* = 10 s. On real recordings (`tube_ssl_real_compare.py` `sup_task`) they use *J* = 20 s. The page states neither, and its caveat that the bench and real operating points differ does not mention this second difference. | low | State the *J* each threshold uses. | yes |
| F10 | What waits on Tony, the shared-modulation question: "shared modulation on timescales of 10–45 s"; What this does not settle: "shifts … by 10–20 s, where it also removes shared modulation" | On the slow stream, rigid shift at 11.2 s reads 0.517 with interval [0.494, 0.550], which includes chance. The evidence begins at 22.4 s, as the same bullet says. The "10" lower bound goes past the data. | low | "22–45 s", or "detectable from 22.4 s, not at 11.2 s". | yes |
| F11 | Real-recordings table, LoCo row, compared with the version it replaces | Diffing against the replaced `real_compare/summary.json` (`c797218`): LoCo's real event rate moved **2.57 → 3.72 per 10 min**. CoactDetect (2.70) is unchanged. The page mentions the LoCo retune only for the bake-off. Every other difference I diffed is explained: training rows 288 → 360 (`line_bound` added), aggregate rows 16 → 80 (fitted banks added, initial bank unchanged), checkpoints differ only in threshold. | low | Add a short note that LoCo's production retune also moves its real-recording rate. | yes |
| F12 | Source of record for group membership | There is one: the export folder (`2026-09-03_revised_2v_long_STEPS_EXCLUDED`, with exclusions applied by the producer, per CLAUDE.md). It holds 84 fast baseline recordings from 44 mice, and `load()` refuses non-baseline windows. The leak tests are grouped by mouse, and the page flags that the real-recording statistics are pooled over events. **The folder also has four groups (DI, MALE, ORX, OVX; `by_group` in `controls_lab`), which the page pools without mentioning them.** | low | Add one sentence that the rows pool baseline recordings across the four groups. | yes |
| F13 | Attributions not in the lit folder | These could not be checked: Kreuz et al. 2022 *J Neurosci Methods* 381:109703; Kreuz, Mulansky &amp; Bozanic 2015; Mulansky &amp; Kreuz 2016; Diskin et al. 2022 (CFARnet); McFee, Salamon &amp; Bello 2018; Grün, Diesmann &amp; Aertsen 2002 / Grün 1996; Cossart, Aronov &amp; Yuste 2003; Zenodo DOI `10.5281/zenodo.10041434` (not in the Hamon 2026 preprint text). | low | Check by hand before this goes to outside readers. | no |
| F14 | "the three bake-offs sharing one Mac" | All three record the same platform string, but nothing records that they ran at the same time. | low | none needed beyond the ⚠ already there | no |

## Claim ledger

**Bake-off table** (recomputed from the three bakeoff JSONs; a fit with no F1 counts as 0)

| quoted | recomputed | verdict |
|---|---|---|
| line 0.698 ± 0.064, 0.64–0.78, recall 0.875, precision 0.584, probe 3.25, 66–67 s | 0.6975 ± 0.0639, 0.641–0.784, 0.875, 0.584, 3.25, 66.44–67.05 | match |
| line_bound 0.694 ± 0.040, 0.67–0.75, 0.881, 0.575, 3.50, 289–292 s | 0.6935 ± 0.0402, 0.666–0.753, 0.881, 0.575, 3.50, 289.36–292.40 | match |
| line_length 0.682 ± 0.038, 0.64–0.73, 0.842, 0.580, 4.42, 64–66 s | 0.682 ± 0.038, 0.640–0.733, 0.842, 0.580, 4.42, 64.07–65.55 | match |
| tube 0.654 ± 0.050, 0.61–0.72, 0.836, 0.544, 20.67, 7.7–8.2 s | 0.654 ± 0.050, 0.610–0.722, 0.836, 0.544, 20.67, 7.69–8.15 | match |
| tube_guard 0.643 ± 0.052, 0.59–0.69, 0.797, 0.548, 15.25, 7.3–7.7 s | 0.643 ± 0.052, 0.591–0.691, 0.797, 0.548, 15.25, 7.31–7.75 | match |
| tube_ratio / tube_ratio_guard / tiny / trace rows | 0.508 ± 0.025 … / 0.466 ± 0.054 … / 0.125 ± 0.000, recall 0.067, precision 1.000, 88.9–89.0 s / 0.120 ± 0.011 … 9.42–9.52 s | match |
| CoactDetect, LoCo, rate+context, binned SCE, locust, SPIKE-synch rows | 0.651 ± 0.044 … 1.25; 0.631 ± 0.046 … 3.50; 0.607 ± 0.082 … 26.50; 0.582 ± 0.072 … 59.75; 0.545 ± 0.052 … 239.25; 0.267 ± 0.072 … 8.75 | match |
| 1,305 parameters for both line and line_bound | 1305 / 1305 (the test pins them equal) | match |
| 4 folds × 2 recordings, 30 planted per fold | `seeds_per_fold` 2, 8 seeds, `n_planted` {30} | match |
| probe firings excluded from precision | line fold 0: 50 detected − 7 probe = 43 scored; precision 27/43 = 0.628 | match |
| CoactDetect unchanged by LoCo retune and event widths | per-fold F1 identical to replaced `line_bakeoff/bakeoff.json` and `docs/learned/bakeoff.json` | match |
| "+0.058 in the reviewed version was one seed" | replaced run's seed-0 line − line_length = +0.058; new seed 0 identical | match |

**Paired differences**, all eight rows: every fold value, mean, *t*(3), mean without the largest fold, and per-seed mean recomputed. Each matches to the digit (for example line − CoactDetect: −0.005/−0.004/+0.178/+0.018, +0.0468, 1.06, +0.0030, +0.063/+0.055/+0.023). Also matching: "carried by the third fold", since fold index 2 is the largest for all four margins over CoactDetect; "no more than 0.008"; and line − tube positive on 4/4 folds.

**Plant probe**: all 36 ratios for line, line_length, line_bound and tube were recomputed, and the ⚠ markers fall exactly where `abs(denominator) &lt; sd` (line and line_bound at plant 4 against burst). The fuzz ordering at plant 16 (1.99, 1.75, 1.60, 1.43) matches. Plant geometry in the code: burst onsets at frames 0/2/4/6 (0.6 s), fuzz offsets `randint(-15, 15)` (2.9 s), 32 ROIs, 12 fields, head depth 6. **Match.** The tool's docstring says the burst spans "0.4 s", but the page is right.

**Figure 1: per-ROI leak test** (`by_mouse` accuracy and interval)

| quoted | recomputed | verdict |
|---|---|---|
| fast rigid shift 0.497/0.505/0.502/0.505/0.486/0.492 | same | match |
| fast shared offset 0.498/0.502/0.495/0.516/0.504/0.509 | same | match |
| fast dither 0.738/0.761/0.784/0.794/0.775/0.785; lowest lower bound 0.70 | same; 0.699 | match |
| slow dither 0.60–0.77; shared offset 0.495–0.507; rigid shift 0.500–0.524 up to 11.2 s; 0.558 and 0.567, lower bounds 0.51 and 0.52 | 0.597–0.769; 0.495–0.507; 0.500–0.524; 0.558 [0.512], 0.567 [0.517] | match |
| 84 recordings, 1,501 pairs per stream, grouped by mouse | 84 / 1501 / 44 mice in both streams | match |
| drops 0.5 % and 1.1 % at 10 s and 20 s | 0.0053, 0.0108 | match |

**Figure 1: aggregate gate**: initial bank 0.664–0.688, 0.520–0.530, 0.442–0.536, 0.861–0.886, trace 0.657–0.674; fitted banks 0.654–0.684, 0.484–0.527, 0.469–0.592, 0.864–0.914, trace 0.619–0.643. **All match** (32 fitted rows = 2 models × 4 folds × 4 *J*). The findings bullet's 0.65–0.68 and 0.48–0.53 also match.

**Figure 3: training** (population SD; a fit with no true positive scores 0)

| quoted | recomputed | verdict |
|---|---|---|
| supervised table, all 20 cells including ± | e.g. line 0.571/0.668/0.697 ± 0.068/0.691 ± 0.064; tube 0.434/0.519/0.629 ± 0.064/0.662 ± 0.051 | match |
| trained and untrained table, all 50 values | e.g. line_length sim 20 s 0.386 \| 0.322; untrained line_length 0.291 \| 0.093 | match |
| untrained line_length 0.291 ahead of 14 of 20 trained cells | 0.29052; 14 | match |
| ≤ 1: 0.126–0.322 vs ≤ 0.093; ≤ 0.5: 0.070–0.250 vs ≤ 0.039 | 0.1259–0.3218 vs 0.0929; 0.0700–0.2495 vs 0.0392 | match |
| 12 fits per model per arm, 360 total; two validation recordings | 60 per arm; 360 rows; `n_val_seeds` {2} | match |
| 0–4 fits per cell at or above ln 2 | 0–4 | match |
| untrained / real-trained truth-reading 0.50–0.56 / 0.50–0.58; coverage 0.962–0.984 / 0.954–0.985; widths 23–128 s; supervised 0.005–0.010 | 0.503–0.559 / 0.499–0.577; 0.962–0.984 / 0.954–0.985; 23.2–128.1; 0.00495–0.0096 | match |
| sim-trained line 10 s 0.551 covering 0.035; line_length 20 s 0.620 covering 0.022; three cells at 0.36–0.50 | 0.551/0.035; 0.620/0.022; 0.363/0.499/0.496 | match |
| tube family and line_bound 20 s "cover 0.93 or more" | tube at 20 s = 0.928 | **mismatch** (F6) |
| grid edge in 4 of 360 fits, all `line` | 4; {line} | match |
| paired checks: 0.720–0.774; thinned 0.766–0.940; same-crop offset 0.484–0.555; independent crop 0.450–0.510; twins 0.456–0.575 | same (per-cell means) | match; units in tension with the caption (F7) |
| ties 10–69 %; some tube fits at 1.00 | per fit 0.095–0.690 plus two tube fits at 1.00 | match, wording (F8) |
| objective: 4,096 frames, 0.1 s, top 1 %, softplus(shift − real), 900 steps; three shifts for the threshold; a fifth thinned | `CROP` 4096, `grid_sec` 0.1, `TOPK_FRAC` 0.01, `STEPS` 900, `N_SURR_THRESHOLD` 3, `THIN_SHARE` 0.2 | match |

**On real recordings**

| quoted | recomputed | verdict |
|---|---|---|
| CoactDetect 2.70, 7, 1.00 \| 7, 1.00; LoCo 3.72, 6, 1.00 \| 7, 1.00 | same | match |
| supervised (five) 4.29–5.03; 4–5, 0.80–0.84; 5, 0.86–0.89 | 4.29–5.03; 4–5, 0.802–0.836; 5, 0.861–0.893 | match |
| trained (ten) 5.67–6.75; 0–1, 0.13–0.24; 2–4, 0.40–0.63 | 5.67–6.75; 0–1, 0.128–0.237; 2–4, 0.4047–0.630 | match |
| random 0–1, 0.06–0.18; 1, 0.19–0.29 | 0–1, 0.061–0.184; 1, 0.186–0.287 | match |
| "median 0–1 … against 0.07–0.13 for random" | random median 0; 0.073–0.132 is share ≥ 3 | **mismatch in kind** (F2) |
| agreement table, 20 values | all match `summary.json` | match; first column is seed 0 only (F1) |
| references agree 0.780 / 0.591; trained models 0.174–0.340 against chance 0.046–0.064 | same | match |
| floor of three ROIs for CoactDetect and LoCo | `min_rois: int = 3` in both detectors | match |
| edges: uniform 0.84 % / 2.1 %; supervised label-free 3.8–5.9 % / 5.6–7.1 %; bake-off threshold 1.6–2.2 % / 3.1–3.9 %; trained 1.1–3.7 % / 3.1–5.5 %; CoactDetect 3.3 / 4.7; LoCo 0.0 / 1.1; every supervised model higher at label-free | recomputed from `events.json` and the folder's windows: identical (e.g. 0.05649 → 5.6 %, 0.01649 → 1.6 %, 0.01148 → 1.1 %) | match |
| 12.8 s = 128-frame padded support | `max_center_frames` 128, kernel spans −k..k, dt 0.1 | match |
| 84 recordings from 44 mice; the 10 checkpoints are the seed-0, fold-0 fits out of 120 | 84 / 44 (export folder); `ssl-&lt;model&gt;-&lt;J&gt;-&lt;seed&gt;-&lt;fold&gt;` → -0-0; 5 × 2 × 3 × 4 = 120 | match |

**Library, tests, docs, environment**
- **Code claims about `line` and `line_bound`:** `line_bound` subtracts the floor and bounds the vote in time; the concentration channels are a narrow-to-next-wider ratio; `orientation=True` is registered; the encoder sorts rows busiest-first. **Match.**
- **Burst vote ratio:** `line_bound` burst/onset 1.04–1.15 when rerun (1.042–1.150). **Match.**
- **Rigid shift:** the numpy rigid shift uses `floor(t + 0.5 + u)`, the same formula as the Elephant path with `edges=True`, and the test checks the offset distribution. **Match.**
- **Versions:** Python 3.14.5 matches the run records. torch 2.14.0 and Elephant 1.2.1 match the named venv, but the run records do not store them.
- **Commits:** `ea350be` fixes `git_dirty: null` and is on the branch. **Match.**
- **Docs:** `docs/generator.md` gives 0.36 s against a 0.42 s null on 47 of 84 slices and calls it the least trustworthy number and an upper bound. MILESTONES has "no ranking; a table of performance" and reserves promotion to Tony. FOUNDATIONS §5 releases one real raster by name. **All match.**
- **Literature:**
  - Stella 2022 ranks trial shifting (dithering the entire train, Pipa 2008) most robust with D = 25 ms. **Match.**
  - Louis 2010 recommends train dithering and credits Pipa 2008 and Harrison &amp; Geman 2009. **Match.** Its rolling-versus-dropping condition is **inverted** on the page (F3).
  - Pipa 2008 credits the multiple-shift method of Grün et al. 1999. **Match.**
  - Dard 2022 uses an independent circular shift per cell with a threshold on co-active cells. **Match.**
  - Grün's Unitary Events chapter describes clipping. **Match.**
  - The Finn &amp; Johnson 1968 and Wang, Li &amp; Metze 2019 titles are consistent with the citations.
- **Reproduce table:** every CLI flag exists in the named tools.

## Scratch files
- `<scratchpad>/mb/run/summary.json`: the summariser rerun at HEAD, identical to the committed file apart from provenance.
- The one-seed agreement behind F1 is in `<worktree>/tools/tube_ssl_real_compare.py`, in `main()`:
  ```python
  agree[f"{ref} -&gt; {det}"] = agreement(detector_events[ref], detector_events[det][:1], rows_by_id, rng)
  ```
