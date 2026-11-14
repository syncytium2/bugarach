GRANT 7 MISMATCH — missing none; holds Edit, Write, PowerShell, Agent, Artifact, Skill, ToolSearch, Monitor, mcp__claude_ai_Claude_Docs__batch/update (and NotebookEdit offered as a deferred tool)

(I made no change to any file in the repository. All scratch work is under <scratch>/mb3/role07/: verify.py, verify_full.py, detail.py, shown.py and full200.txt. This is a finding about the run: the review took a fallback path with editing tools present.)

# Role 7: reuse audit of docs/dissertation/figures/ch1_intro_figures.py

**Bottom line:** the script's re-implementations are disclosed and mostly match the repository's code. I ran checks over all 200 seeds of Table 1.1, and none of the figure's or table's numbers change. One claim is overstated: the docstring says the repository's scorer "gives the same numbers". It gives the same counts but credits a different event of situation 3, so two lanes of Figure 1.2 colour the 3a/3b pair the opposite way from the repository's scorer.

## Findings

Each row gives location · issue · severity · suggested fix · verified against a source?

1. **`score()` (lines 224-238) and its docstring claim (lines 44-47).**
   - **Issue:** `score()` walks planted events in time order and takes the first call within 1 s. That is the rule `bugarach/score.py` (module docstring, lines 7-12) names as the one it replaced, because it can use up a call that better matches the next event. The repository's `score_detections` sorts all event-call pairs by distance and breaks ties by distance to the span's midpoint (lines 283-296).
   - **Check:** `score_detections(tol_sec=1.0, floor=None, widths=…)` on all 200 draws, plus the three control variants (event 4 left out, events 1 and 3 left out, merge gap 0.5 s).
     - The number found is identical in every case, so Table 1.1 and all printed shares stand.
     - Which event is credited differs whenever one call spans both 3a and 3b. In the 10-draw first pass, 5 of 10 draws differed for the sliding and CFAR detectors. Every difference was the same swap: 81 s credited here, 85 s by the repository.
     - In the draw shown in Figure 1.2 (seed 1015), the sliding and CFAR lanes mark 81 s green and 85 s red. The repository's scorer would mark 85 s green and 81 s red. The fixed-bin lane agrees (81 s both ways).
   - **Severity:** minor. The figure's colouring depends on the scorer, and the docstring's "same numbers" is true of counts only.
   - **Fix:** either take hits from `score_detections(...).hits` (with `tol_sec=1.0, floor=None`; that leaves out the don't-care rule, as the chapter wants), or reword the docstring to "gives the same counts; which of two events a merged call credits can differ (time order here, nearest midpoint there)". The caption's "one call finds one event at most" is true under both rules.
   - **Verified:** yes, by running it.

2. **`local_rate()` (lines 186-197), the CFAR background estimate.**
   - **Issue:** it re-implements the guarded context of `bugarach.detectors.rate.event_rate_context(guard_sec=…)` (rate.py lines 197-257), which is the repository's CFAR guard-cell code. The docstring discloses this ("window edges differ slightly").
   - **Check:** I substituted `event_rate_context(trains, (0, T), 1.0, context_sec=70, grid_dt=0.1, guard_sec=10) / N`, i.e. 30 s of reference beyond 5 s of guard on each side, matching the chapter's constants. Over 200 draws:
     - the per-instant threshold differs on at most 52 of 2401 frames per draw;
     - the per-draw CFAR outcome tuple (events 1-5 found, false alarm in each stretch) changes in 3 of 200 draws.
   - **Severity:** minor. The chapter says CFAR is built from the repository's guard idea. Using the repository's estimator would make "CFAR" here the repository's CFAR rather than a near copy, at a cost of at most about ±1.5 % on Table 1.1's CFAR shares.
   - **Fix:** call `event_rate_context(..., guard_sec=2*guard)` and divide by N, then regenerate the table. Or keep `local_rate` and state in the docstring that the repository's estimator moves 3 of 200 draws.
   - **Verified:** yes, by running it.

3. **`sliding_count()` (lines 172-183).**
   - **Issue:** it duplicates `bugarach.event_floor.coactive_counts` (event_floor.py lines 66-80). That function is the frame-based count of distinct cells in a sliding window that ADR-0008's floor itself uses.
   - **Check:** `coactive_counts(frames, L, wf)[s] == S[s + wf - 1]` held exactly in all 200 draws.
   - **Severity:** nit. It matches, but it is a second copy.
   - **Fix:** `S[wf-1:] = coactive_counts(...)`, with the first `wf - 1` frames handled as now. Or keep it and cite `coactive_counts` as the same count.
   - **Verified:** yes.

4. **`cfar_calls()` (lines 200-221), call forming.**
   - **Issue:** it reuses `sliding.merge_runs` and `sliding.span_of` as stated, but on frame runs rather than the continuous pieces from `sliding.pieces`. The docstring discloses the edge case: runs exactly the merge gap apart.
   - **Check:** I ran it at a constant threshold of 6 cells and compared it with `count_sliding_detect` on the same trains. The calls differ in 3 of 200 draws, consistent with the disclosed edge case. The CFAR shares are therefore not purely the threshold's effect: about 1.5 % of draws carry a call-forming difference too.
   - **Severity:** nit.
   - **Fix:** none needed beyond the existing disclosure. Optionally, give the "differs in two edge cases" sentence the 3 / 200 count.
   - **Verified:** yes.

5. **`chance_calls_per_hour()` / `chance_floor()` (lines 154-169) against `docs/learned/synthetic_validation/blind_a/theory_floor.py` (`u`, `floor_analytic`).**
   - The formula matches term for term: (n−K+1)·b·Binom.pmf(K−1; n, 1−e^{−bW}). So does the guard that every larger K must also meet the budget.
   - The script starts K at 3, which equals ADR-0008's max(3, ·) as stated in theory_floor's docstring.
   - Restating it is justified, because theory_floor.py runs a Monte Carlo loop at import (lines 13-22, as the docstring says).
   - `main`'s assert (6 cells at 0.01 Hz, 12 at 0.05 Hz) anchors it.
   - **Result:** no finding. Verified by reading: yes.

6. **`plant()` (lines 103-129) against `bugarach.simulate.simulate_coordination`.**
   - Reuse is not possible: the generator places events itself (renewal or uniform with min_sep) and keeps them out of `hot_window`. Figure 1.2 needs events at chosen times, including one inside the busier stretch.
   - It matches the generator on:
     - Poisson background per cell;
     - k cells chosen without replacement;
     - Gaussian jitter;
     - rounding half away from zero, like `matlab_round`.
   - Two differences:
     - the one-onset-per-frame rule, which is disclosed;
     - out-of-range onsets: the generator clamps them to [0, T] (simulate.py, distractor and event placement), while `plant` drops them. That is undisclosed, and immaterial here because all events sit at least 15 s from the ends.
   - **Severity:** nit.
   - **Fix:** optionally add "drops rather than clamps onsets outside the recording" to the docstring's list of differences.
   - **Verified:** yes, by reading.

7. **`tool_pairs()` (lines 530-537), the correlogram input.**
   - The correlogram tool's own `_sim` converts with `np.round(t/DT)`; the script uses `floor(t/DT + 0.5)`. The generator's onsets are already on the 0.1 s grid, so the two give identical frames. Neither applies `unique`, so duplicate onsets are treated the same way.
   - `mjc.pairs` and `mjc.hwhm` are called, not copied.
   - **Result:** no finding. Verified by reading: yes.

8. **Bootstrap for the HWHM (lines 606-611).**
   - The script resamples recordings and reports the SD as an SE. The tool's pooled block also resamples recordings (`main`, lines 418-420) but reports a 2.5-97.5 percentile interval.
   - Same resampling unit, different summary. The chapter labels it "bootstrap standard error", so this is correct as written.
   - **Result:** no finding. Verified by reading: yes.

9. **`hwhm_from_zero()` (lines 553-561).**
   - It is the same linear interpolation as `mjc.hwhm` (lines 117-132), applied to a predicted curve that already has its level subtracted. It lacks `mjc.hwhm`'s guard `p[0] <= 0 → nan`, which cannot trigger on a predicted peak.
   - **Result:** no finding. Verified by reading: yes.

10. **Excess pair counts (lines 631-640).**
    - The call `mcr.excess_cumulants([np.minimum(mcr._frames(t, 0, T), L-1) ...], L, wf, mcr.N_SURR, rng)` reproduces the tool's own `_sim` preparation exactly (measure_coordination_rates.py, lines 414-416).
    - The prediction calls `theory.predicted_excess_cumulants` and `theory.g`.
    - **Result:** no finding. Verified by reading: yes.

11. **`bin_count_survival()` / `events_reaching()` and the chance curve (lines 564-591, 656-657).**
    - The distinct-cell count per 1 s bin is the same count `count_detect` produces (`obs`, count.py lines 99-104). `stats.binom.sf(K-1, N, 1-e^{-b})` is the q inside `theory.chance_clusters_per_min` (theory.py lines 250-261).
    - Both match. They could be `count_detect(..., bin_sec=1).obs`, but the script would gain little.
    - **Severity:** nit, no action needed.
    - **Verified:** by reading: yes.

12. **`predicted_lag_pmf()` and the hard-core deficit `d` (lines 540-550, 616).**
    - I searched tools/, src/ and docs/learned/ (including correlogram_explainer/explain_correlogram.py and synthetic_validation/event_train.py) and found no existing predicted-correlogram function. This is new derivation, not reinvention, and belongs to the theory and maths roles.
    - **Result:** no finding.

## What I checked

Every function the script defines, against:
- `src/bugarach/detectors/{count,sliding,rate}.py`
- `src/bugarach/event_floor.py`, `src/bugarach/score.py`, `src/bugarach/simulate.py`
- `tools/measure_jitter_correlogram.py`, `tools/measure_coordination_rates.py`, `tools/measure_slow_comodulation.py` (`raster`)
- `docs/learned/synthetic_validation/theory.py` and `blind_a/theory_floor.py`
- `docs/learned/correlogram_explainer/explain_correlogram.py`

I located these through docs/INDEX.md (the rows on the count rule, the ADR-0008 floor as code, the correlogram and coordination-rate tools, what counts as a hit, the rate/CFAR mechanism, and synthetic validation).

The numerical checks (findings 1-4) ran the script's own `detector_runs` over seeds 1000-1199; the output is in <scratch>/mb3/role07/full200.txt.
