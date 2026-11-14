GRANT 6 MISMATCH — missing none; holds Edit, Write, PowerShell, Agent, Artifact, Skill, Claude Docs MCP write tools (batch/update) and other non-grant tools. None of them was used: no file in the repository was written. My scratch files are in <scratch>/mb2/role06/ only. I imported the figure script with -B and PYTHONDONTWRITEBYTECODE, so no __pycache__ was written into the repo.

# Role 6 (RTFM): chapter-1-aim0.md (blob 0acfccbb) and figures/ch1_intro_figures.py

## What I grounded in (read, not from memory)
- **Repo code, read in full or in the relevant parts:**
  - detectors/count.py: `count_detect`, `count_sliding_detect`
  - detectors/sliding.py: `pieces`, `span_of`, `merge_runs`
  - simulate.py: placement, jitter, quantization and defaults
  - event_floor.py
  - assess.py `_clusters`: merge_bins = 2, wm = 1.5 × bin
  - tools/measure_jitter_correlogram.py: `pairs`, `hwhm`, pooling
  - tools/measure_coordination_rates.py: `population_cumulants`, `shifted`, `excess_cumulants`, `solve`
  - theory.py: `predicted_excess_cumulants`
  - blind_a/theory_floor.py
- **Primary sources in <01-lit>/radar and surrogates, read as extracted text:**
  - Finn & Johnson 1968, pp. 414–417 and abstract: CFAR as a generalisation of noise-regulated CFAR; reference cells exclude the cell under test; second-target masking.
  - Rohling 1983: CA vs CAGO compared; Fig. 3(b) "two guard cells directly adjacent to the test cell"; masking in Fig. 3; the clutter edge, where the threshold is underestimated when the clutter area is shorter than the reference window.
  - Perkel, Gerstein & Moore 1967: the term "cross-correlation histogram".
  - All the CFAR and correlogram attributions in 1.2.3 and 1.4 are supported by those pages.
- **Independent recomputation (scipy):**
  - Analytic floor: 6 cells at 0.0096 and 0.01 Hz, 12 at 0.05 Hz, 4 for a 0.2 s window. u₆ at 0.0096 Hz is 0.334 per hour.
  - g₂ = 0.5 at w = 2.079σ.
  - 2√(ln 2) ≈ 1.665.
  - Float bin assignment of frame times for 1 s and 2 s bins: 0 misassigned frames up to 2700 s.
  - The triangular-kernel lag pmf for rounding is correct, because the generator's event times are continuous (uniform/renewal), not on the frame grid.
- **The new code obeys the repo conventions:**
  - The CFAR sliding count is on whole frames over (t − w, t], which equals `sl.pieces` for on-grid onsets.
  - `cfar_calls` forms its runs and spans the same way `count_sliding_detect` does.
  - `count_detect`'s merge rule (edges[b] − edges[prev+1] ≤ 3) means at most one uncalled 2 s bin between called bins, as 1.3.4 says.
  - The correlogram statistic is pooled over recordings before `hwhm`, as shipped. Zero lag is halved in both obs and exp, and the prediction halves it too.
  - The assessor's description in 1.3.4 matches `_clusters`.
- **Numbers vs log:** every number in 1.1–1.3 and Table 1.1 that I cross-checked against ch1_intro_figures.log matches.

## Findings
Columns: location · issue · severity · suggested fix · verified against a source?

1. **1.3.3 ¶ "g₂ … Figure 1.4 D" and the Fig. 1.4 caption, D ("measured by the coordination-rates tool")**
   - **Issue:** D runs the tool's `excess_cumulants` at windows of 0.2, 0.5 and 8 s, which it does not ship (it ships 1, 2 and 4 s). The method trap: the surrogate's offset spacing is tied to the window (SURR_SPACING × wf = 2 windows). When 2w is comparable to σ√2, cells of one event shifted by ±2w, ±4w, … stay partly together, so the surrogate subtracts real pairs.
   - **My computation, with the exact permutation-offset distribution:** at σ = 0.5 s the surrogate keeps 10.2 % of event pairs at w = 0.2 s, 2.6 % at 0.5 s and 0.3 % at 1 s. In the sharp set it keeps ≤0.3 %.
   - **Effect:** the hard-core prediction drawn (0.109) times 0.898 gives 0.098, against a measured 0.100. So the jittered 0.2 s point's 8 % relative shortfall is the surrogate, not noise. The hard-core form (`theory.predicted_excess_cumulants` with train=None) does not model this.
   - **Why it matters:** "within about 0.02 at every window" is true in absolute terms, but at the shipped windows the leak is negligible. The figure validates the tool partly outside its shipped settings, and the text does not say so.
   - **Severity:** medium (low impact on conclusions).
   - **Fix:** say that 0.2, 0.5 and 8 s are not the tool's windows. Note that below about σ√2/2 the surrogate retains a share of the coordination (≈10 % at 0.2 s for the jittered set), or plot only 1, 2 and 4 s as "the tool" and mark the others as the statistic run off-setting.
   - **Verified:** yes (code plus computation).

2. **1.2.4 situation 4 ("CFAR raises its threshold to 10–12 cells in that stretch")**
   - **Issue:** the script prints this only for the draw shown (seed 1015: [10, 11, 12]). Over the 200 draws I re-ran:
     - the lowest CFAR threshold in 120–180 s was 9 cells in 32 draws, 10 in 146 and 11 in 22;
     - the highest was 11 in 17 draws, 12 in 128, 13 in 54 and 14 in 1.
   - So "10–12" is the shown draw, not the design.
   - **Severity:** low.
   - **Fix:** "9–14 cells across draws (10–12 in the draw shown)", or tie it explicitly to Fig. 1.2.
   - **Verified:** yes (re-run of `detector_runs`).

3. **1.2.4 situation 4 ("four of the five false alarms fall within 13 s of its ends") and the script docstring ("Every number the chapter quotes from these figures is printed by this script")**
   - **Issue:** the number is correct. My re-run puts the five CFAR busy-stretch false alarms at 5.6, 10.9, 11.2, 12.7 and 23.2 s from the nearest edge. But the script does not print it, so the docstring's claim is false for this sentence. The "10–12 cells" in finding 2 is likewise printed only for one draw.
   - **Severity:** low.
   - **Fix:** add a print of the CFAR false-alarm distances to the stretch edges (and the threshold range over draws).
   - **Verified:** yes.

4. **1.3.2 deficit formula d ≈ (Ek)²(1 − 1/N)/(Σnᵢ)² (also in the script's `deficit`)**
   - **Issue:** the counting is slightly off. The independent level C₀ is built on Σ_{i≠j} nᵢnⱼ ≈ (Σn)²(1 − 1/N), so the (1 − 1/N) cancels. The pairs the hard core removes are coordinated onsets from *different events*, which carry a (1 − 1/E) factor. That gives d ≈ (Ek)²(1 − 1/E)/(Σn)² (ignoring the tool's (L − k)/L edge factor).
   - **Numerically immaterial here:** 1 − 1/33 = 0.970 vs 1 − 1/45 = 0.978, so the level shifts by about 0.001.
   - **Severity:** low.
   - **Fix:** restate with the (1 − 1/E) factor, or call the expression an approximation and say what it neglects.
   - **Verified:** yes (derivation against the `pairs` code).

5. **1.3.2 last ¶ ("Five times the jitter makes the peak … a quarter as tall")**
   - **Issue:** the peak *above the level* (the area-carrying excess) scales as 1/σ: 17.4 vs 3.7, about 1/4.7. "A quarter" comes from comparing ratios that include the baseline (18.3 vs 4.6). The section's own point is that area is conserved and width scales with σ, so "a fifth as tall above the level" is the consistent statement.
   - **Severity:** low.
   - **Fix:** "and its excess above the level about a fifth as tall".
   - **Verified:** yes (log numbers).

6. **1.2.3 ("At 0.01 and 0.05 Hz the repository's own floor for the count detector, found by simulating chance … gives the same 6 and 12") and 1.6.1**
   - **Issue:** event_floor.py's floor is a *sliding* 2 s window count under a rigid-shift null, with `floor_of` taking the first K under budget (it does not check that every larger K is under budget too). It is the floor the bench assigns to the count detector, but it is not a floor of fixed 2 s bins. Fixed bins have a lower chance rate (Table 1.1: 0.1 vs 0.5 false alarms per hour in the quiet stretches).
   - 1.6.1 does say "2 s sliding window under a rigid-shift null". The 1.2.3 wording "floor for the count detector", placed right after the fixed-bin detector, can read as a fixed-bin floor.
   - **Severity:** low.
   - **Fix:** in 1.2.3, add "(a sliding-window floor, which the repository applies to both count detectors)".
   - **Verified:** yes (event_floor.py).

7. **1.3.4 ("397 of its 450 events (88 %) put at least 8 cells into some 1 s bin")**
   - **Issue:** `events_reaching` counts *all* distinct active cells in any 1 s bin overlapping te ± 1.5 s, background cells included, not only the event's participants. At 0.0096 Hz the background contributes about 0.3 cells per bin, which is small but not zero. The wording "events put … cells" implies participants only.
   - **Severity:** low.
   - **Fix:** "have at least 8 distinct cells active (background included) in some 1 s bin within 1.5 s of the event".
   - **Verified:** yes (code).

8. **"Reproducing this chapter" line for ch1_intro_figures.py ("Figures 1.1–1.3, Table 1.1, 1.2–1.3 numbers")**
   - **Issue:** the script produces Figures 1.1, 1.2 and **1.4**. Figure 1.3 is the 20261029 file from ch1_new_figures.py. The revision note in the same chapter correctly says "Figures 1.1, 1.2 and 1.4".
   - **Severity:** low.
   - **Fix:** "Figures 1.1, 1.2 and 1.4, Table 1.1, numbers of 1.2–1.3".
   - **Verified:** yes.

9. **The script's `plant` docstring ("one onset per cell per frame … as the generator rounds") vs Figure 1.4, which uses the generator**
   - **Issue:** `plant` de-duplicates (np.unique) per cell per frame. `simulate_coordination` does not (it sorts only), so in Fig. 1.4 a cell can carry two onsets in one frame. That is negligible at these rates.
   - The chapter's model statement in 1.3.1 does not claim de-duplication, so this is a script-comment precision issue only.
   - **Severity:** low.
   - **Fix:** note the difference in the docstring.
   - **Verified:** yes (simulate.py lines 995–1004).

## No findings
On the following I checked against source or code and found nothing wrong:
- The CFAR implementation:
  - reference and guard geometry;
  - clipping at the recording ends;
  - floor lookup;
  - run forming and merging, and the span window (start − w, end − DT].
- The analytic chance floor and its "every larger K" guard, including the 0.33 per hour figure.
- The scoring rule (one call finds one event) and the typical-draw selection (7 of 200).
- The correlogram prediction:
  - the triangular rounding kernel, via `scipy.integrate.quad` with the breakpoint at the lag;
  - zero-lag halving;
  - the HWHM read above the predicted level;
  - the bootstrap SE over recordings.
- The g₂ values and 2.08σ.
- The binomial chance shares (1.51e-05 at ≥5 cells, 7.79e-10 at ≥8).
- The surrogate offset span (64 s at 1 s), and the "35 %" figure for independent ±5 s shifts (it matches the tool's docstring).
- The Finn & Johnson and Rohling attributions, including masking, guard cells by 1983 and the clutter edge.
- Perkel's term.

I did not review sections 1.5–1.10 against their own scripts. The brief named the new intro code as the target, and those sections' numbers come from other scripts that I did not re-run.

unreached: 0
