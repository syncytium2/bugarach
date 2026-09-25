GRANT 6 ok — Read, Grep, Glob, Bash, WebSearch, WebFetch

# Role 6 — RTFM: final-parameters report and the code behind it

**Grounding:** read ADR-0006/0008/0009, then `src/bugarach/event_floor.py`, the floor and validity functions in `bench.py`/`bench_slow.py`/`bench_combined.py`, `score.py`, `search_all_settings.py`, `score_bench_candidates.py`, `score_cross_stream.py`, `make_final_parameters_report.py`, and the detector internals the floor feeds (`coact.py`, `loco.py`, `sce.py`, `sync.py`). Checked the darkroom records against the page (`<darkroom>/bugarach/2026-09-25-final-parameters/`: every `search.json`, both `candidates.json`, `review_checks.json`, the DIAGNOSIS note), and re-ran several checks on the worktree code with the tune-bench-comparison venv.

## Confirmed (no finding)
- **ADR-0008 constants:** min 3 ROIs; a 2 s sliding window; per-ROI rigid shift in [−J, J) with J = 20 s; ≤1 call/hour; 1,000 draws; J trimmed at both ends.
- **Each recording's floor** comes from its own null, stretch included, with planted events kept in the null (ADR-0009 decision 1).
- **The grids:** `min_rois`/`min_n` are out of every grid and injected by `floored_params`, which refuses an override.
- **Don't-care scoring** follows ADR-0009 decision 2 (under-floor events leave recall; calls matched to them leave precision).
- **The elevated-rate recording** is its own recording with its own floor; seed offsets are correct; the out-of-stretch gate is quiet-only (disclosed).
- **Selection logic:** the held-out gain is a paired bootstrap median; `proposal()` picks the best held-out candidate whose interval is above zero (disclosed); the guard cap now runs before LoCo's branch.
- **Reproduced exactly:** the 0.0003 selection lead for combined SCE; 1.28/h (combined rate+context, busy, held-out); −0.044 (fast CoactDetect close-events vs sliding); −0.0207 (slow SCE); the Decision 3 held-out values; the two quoted docstring phrases.
- **Fast CoactDetect vs the binned point**, re-run on held-out close-events seeds 49–60: 0.97203 → 0.95552, a loss of **0.01651**, matching the page and `review_checks.json`.
- **Table 3**, re-derived from fresh seeds 6000–6023: every count and floor range matches (120/120/85/120/55/50; floors 5–6, 6–8, 6–7, 7–8, 6–7, 7–10).

## Findings (location · issue · severity · suggested fix · verified)

**1. Decision 3 heading ("the floor may be why") and its slow locust row** · major · verified yes (code + re-run)
- **Issue:** Slow locust's elevated-rate failure (7.24/min vs 4.0) cannot be the floor's doing. Locust has no participation setting (`FLOORED_SETTING`), and the elevated-rate recording plants nothing, so the scorer's floor never touches it.
- **The cause is ADR-0009 decision 1 (the stretch relocated out of the planted recording).** Shipped slow locust, quiet, seeds 1–8:

  | configuration | stretch rate | calls/min in the stretch |
  |---|---|---|
  | own elevated-rate recording (as now) | 0.0321 Hz | 5.00 |
  | own elevated-rate recording | 0.0291 Hz | 5.45 |
  | stretch inside a planted recording (old layout) | 0.0291 Hz | 1.83 (matching the budget's measured 1.93) |
  | stretch inside a planted recording | 0.0321 Hz | 2.28 |

- **All three benches' `MAX_PROBE_PER_MIN` ceilings were measured on the old layout at an older stretch rate:** fast 0.1271 Hz measured vs 0.1334 scored now; slow 0.0291 vs 0.0321; combined 0.1464 vs 0.1529.
- **Fix:** Re-attribute the slow locust row to the relocation; widen Decision 3's second question from "re-measure the precision swing" to "re-measure the elevated-rate ceilings under ADR-0009 too"; note that ADR-0009 decision 4 froze ceilings measured on a construction that decision 1 retired.

**2. Decision 3 (fast SPIKE-synch's precision swing) and Definitions (precision swing)** · major · verified yes (`064/phase3/candidates.json`)
- **Issue:** Fast SPIKE-synch's swing is entirely decoy calls: fresh-seed precision as scored is 0.699 quiet vs 0.847 busy, but without decoy calls 1.000 on both, with 84 decoy calls on quiet vs 23 on busy.
- **Mechanism:** decoys are planted at 6 participants (the middle level, label changed). The quiet floor is 5–6 and busy 6–8, so the floor-set `min_n` lets SPIKE-synch call decoys on quiet but mostly not on busy. The as-scored objective counts every decoy call as a false alarm, which ADR-0006 decision 1 says it is not. The page's mechanism ("sets aside different planted events") does not fit this detector.
- **Inconsistency on the same recording:** a 6-participant planted event under the floor is "don't care", but a call on a 6-participant decoy under the same floor is a false alarm.
- **Direction:** the gate is `abs()` while its rationale is a drop. Fast SPIKE-synch "fails" because busy precision is *higher* than quiet — the opposite direction to what `MAX_PRECISION_DROP` was written for ("falling 90 → 45").
- **Contrast:** rate+context's swing is genuine (0.992 quiet vs 0.764 busy without decoys), and the don't-care arithmetic ((H−a)/(D−a) < H/D) can plausibly deepen it on busy.
- **Fix:** In Decision 3, report the swing with and without decoy calls, state the decoy-under-floor asymmetry, say which direction each detector fails, and ask Tony whether decoys under the floor should be don't-care like planted events.

**3. Decisions 5 and 8, Table 1 (LoCo rows)** · major · verified yes (re-run)
- **Issue:** Under the floor, combined LoCo's own null threshold is inert. Shipped (percentile 99.9, context 120 s) and the pair candidate (percentile **1.0**, context 10 s) give identical calls on four held-out recordings (quiet/busy, seeds 49–50), and the search record agrees: held-out gain exactly 0 [0, 0] over 48 seeds. Combined LoCo is effectively "distinct ROIs in 0.5 s ≥ the ADR-0008 floor, merged at 8 s", and that is the version that "wins on fast" in Decision 8.
- **Same symptom elsewhere:** every LoCo search walked `threshold_pctile` down to 1 (97 → 94 → 88 → 76 → 52 → 4 → 1), which the page treats as bookkeeping ("cap").
- **Fix:** State in Decisions 5 and 8 that LoCo's calls on combined are decided by the floor, not by LoCo's test; a percentile run down to 1 says the detector's own test has become redundant, which bears on what "LoCo" means under ADR-0008.

**4. Methods caveat on SPIKE-synch `min_n`; Decision 2's slow SPIKE-synch row; Table 1** · major · verified yes (code; small re-run)
- **Issue:** How hard the floor bites on SPIKE-synch depends on `dt`. `binned_synchrony` keeps only the last writer per bin and bench onset times are continuous, so at 0.1 s bins onsets sharing a bin count once, while at 0.00625 s nearly every onset counts. The slow proposal moves `dt` 0.1 → 0.00625 (three extensions below the grid), so the search is tuning the effective stringency of ADR-0008's floor — a knob decision 6 removes from the search.
- **Measured** (slow, seeds 49–51, both backgrounds): the floor-set `min_n` removes 0–4 calls per recording at `dt` 0.1 and 0–2 at 0.00625.
- **Fix:** Extend the caveat (currently only "sums onsets, not distinct ROIs") to name the `dt` dependence; flag it on slow SPIKE-synch, which becomes adoptable if Tony rules a limit counts (Decision 2); consider pinning `dt` or counting distinct ROIs.

**5. Decision 4 (CoactDetect alpha)** · major (framing) · verified yes (code); the tail figures are illustrative, not bench-measured
- **Issue:** CoactDetect's p-value is a Gaussian tail from the mean/SD of a Poisson-binomial count (`0.5*erfc(z/√2)`). At `alpha` 1.4e-9 the cutoff is z ≈ 5.95, far outside where the normal approximation holds. With a Poisson proxy at a null mean of 1 ROI, the actual tail at that cutoff is ~8e-5, four orders of magnitude above nominal; the shipped 1e-4 (z ≈ 3.72) corresponds to ~4e-3.
- **Fix:** Present `alpha` as a z-cutoff (~5.9 SD vs ~3.7 now), not as a probability; otherwise "is 1e-9 shippable?" reads as an absurdly strict test when it is a moderate one.

**6. Decision 1 ("A paired gain … was not computed")** · minor · verified yes
- **Issue:** `064/phase3-3x3/review_checks.json` holds paired fresh-seed gains, all with intervals above zero: fast SCE +0.038 [0.017, 0.058]; combined SCE +0.017 [0.001, 0.033]; combined rate+context +0.090 [0.062, 0.115]; combined SPIKE-synch +0.021 [0.003, 0.040]. The tool that produced them (`tools/final_parameters_review_checks.py`) is untracked in the worktree.
- **Fix:** Replace the sentence with these numbers — they are the independent check Decision 1 needs — and commit the tool.

**7. Methods caveat "stability … not for the recordings scored here"** · minor · verified yes (re-run)
- **Issue:** Computed for fresh seeds 6000–6023, all three benches, both backgrounds: the half-draw floors match the full floor on 142 of 144 recordings. The two exceptions are both slow and off by 1 ROI (quiet 6014: halves 7/6, full 6; busy 6011: halves 8/7, full 7).
- **Fix:** Report this (and run the same check for seeds 1–96) instead of "not done".

**8. Figure 3 description** · minor · verified yes
- **Issue:** "every ROI's own event rate is raised to the background's 99th percentile" — the code sets every ROI to one fixed rate on both backgrounds, with 30 s ramps: the 99th percentile of per-cell rates over real 300 s baseline stretches (fast 0.1334 Hz, slow 0.0321 Hz, combined 0.1529 Hz).
- **Fix:** Reword the caption and give the rates.

**9. Methods caveat on the 2 s co-activity window** · minor · verified yes (code)
- **Issue:** The caveat names only the wider-window direction (where chance co-activity is higher) and misses the other: sliding LoCo counts in 0.5 s (combined) and 1 s (fast), where the 2 s floor sits *above* chance — which feeds finding 3.
- **Fix:** Add that direction.

**10. Methods caveats (missing)** · minor · verified yes (`bench.FLOORED_SETTING`)
- **Issue:** Rate+context, locust and chorus have no participation setting, so the floor reaches them only through scoring. They can make calls below the floor, which count as false alarms, while the other four detectors are stopped from making them. The same applies to the real-data run.
- **Fix:** State it, including which of the six coded detectors take the floor internally.

**11. `search_all_settings.bracketing` / Table 1 reasons** · minor · verified yes (`search.json` grids)
- **Issue:** An extension past a validity cap still counts as an extension: combined CoactDetect's context grid grew to 240 s, which `context_fits_the_null` refuses, so 120 s reads as interior and bracketed (disclosed only in prose). Slow LoCo's context of 120 s is labelled "edge", but it is ADR-0009 decision 5's hard cap.
- **Fix:** Treat an extension no valid state can reach as "limit"; file it as a code todo.

**12. Definitions (F1)** · minor · verified yes (`score.py`)
- **Issue:** "Each call matched … within 2.5 s" is incomplete. Matching uses the gap to the call's span/extent, so a call whose span contains the event matches at any distance, and merged binned SCE spans (the fast proposal adds a 10 s merge gap) widen this.
- **Fix:** "within 2.5 s of the call's span".

**13. Decision 2 (slow SPIKE-synch `C_min` = 0 at a limit)** · minor · verified yes (from the `bench_slow.py` docstring); not re-measured
- **Issue:** `bench_slow.py` records that every `C_min` from 0 to 0.03 gave identical calls on seeds 1–48 (the profile moves in steps of ~1/31), so this "limit" sits on a measured plateau — evidence Tony can use.
- **Fix:** Cite it in Decision 2.

## Files
- `docs/learned/runs/2026-09-25-final-parameters/README.md`
- `src/bugarach/bench.py` (`floored_params`, `ELEVATED_RATE_RECORDING`, `MAX_PROBE_PER_MIN`, `MAX_PRECISION_DROP`)
- `src/bugarach/bench_slow.py` (`ELEVATED_RATE_RECORDING` at 0.0321 Hz; budget comment says 0.0291 Hz)
- `src/bugarach/bench_combined.py`
- `src/bugarach/score.py`
- `src/bugarach/detectors/sync.py` (`binned_synchrony`, `min_n`)
- `src/bugarach/detectors/coact.py` (Gaussian p-value)
- `tools/search_all_settings.py` (`bracketing`, `extend`)
- `tools/final_parameters_review_checks.py` (untracked)
- `<darkroom>/bugarach/2026-09-25-final-parameters/064/phase3/candidates.json`
- `<darkroom>/bugarach/2026-09-25-final-parameters/064/phase3-3x3/review_checks.json`

No file edited.
