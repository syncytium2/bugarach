GRANT 6 MISMATCH — missing none outright (WebSearch and WebFetch are held only as deferred tools, loadable through ToolSearch); holds forbidden tools Edit, Write, PowerShell, Agent, Artifact, Skill, ToolSearch and mcp__claude_ai_Claude_Docs__batch/update, plus deferred NotebookEdit and Dropbox and Gmail write tools. I used none of them. All my writes went to <scratch>/mb3/role06/: one rerun of the script with --out pointed there, and stdout from probes. I did not open docs/reviews/.

# Role 6 (RTFM): Chapter 1 intro figures (ch1_intro_figures.py) and chapter-1-aim0.md §1.2–1.3.4

## What I grounded in, read rather than taken from memory

**Papers:**
- Finn & Johnson 1968 (<01-lit>/bugarach/radar/finn_johnson_1968_ca_cfar.pdf, text pp. 1, 3, 10, 11, 25).
- Rohling 1983 (<01-lit>/bugarach/radar/rohling_1983_os_cfar.pdf, including the Fig. 3 caption).

**Library documentation (fetched pages):**
- scipy `integrate.quad`, the `points` argument.
- scipy `rv_discrete.sf`.
- numpy `searchsorted`, the `side` argument.
- matplotlib `Axes.step`, `where='post'`.

**Repository code:**
- `detectors/count.py`: `count_detect`, `count_sliding_detect`.
- `detectors/sliding.py`: `pieces`, `span_of`, `merge_runs`.
- `detectors/_shared.clip_sorted`.
- `simulate.simulate_coordination`: event placement, jitter and `matlab_round` quantization.
- `tools/measure_jitter_correlogram.py`: `pairs`, `hwhm`.
- `tools/measure_slow_comodulation.py`: `raster`, `_autocorr_rows`.
- `tools/measure_coordination_rates.py`: `_frames`, `population_cumulants`, `shifted`, `excess_cumulants`, `WINDOWS`.
- `docs/learned/synthetic_validation/theory.py`: `g`, `predicted_excess_cumulants`, `chance_clusters_per_min`.
- `blind_a/theory_floor.py`.

**Reproduction:** I reran the whole script at the shipped settings (<scratch>/mb3/role06/rerun.log). The output matches ch1_intro_figures.log line for line.

## Findings

| # | location | issue | severity | suggested fix | verified against a source? |
|---|---|---|---|---|---|
| 1 | chapter §1.2.3 ll. 150–160; item 4 ll. 224–230 | **The "CFAR" here is a plug-in rule, not Finn & Johnson's CFAR, and its false-alarm rate is not held constant.** Finn & Johnson set the threshold multiplier for the number N of reference cells, so that "the false-alarm probability is a function of K and is independent of the noise-power density. Thus, this is a CFAR system" (p. 10; eq. 36, P_FA = (1 + K²/N)^−N). Rohling's Fig. 3 likewise has "scaling factor T adjusted to Pfa". The script instead puts the 60 s reference estimate b̂ into the known-rate floor `chance_floor(b̂)`, which is the N → ∞ form, so noise in the estimate goes uncorrected. Measured at the shipped settings on flat Poisson backgrounds, with the first and last 35 s excluded and no events (about 500 h per rate): plug-in CFAR gives **0.63/h at 0.0096 Hz and 0.51/h at 0.05 Hz**. The same frame-based count with the rate known gives **0.26/h and 0.33/h**. The plug-in rate is 1.5–2.4× the known-rate rate and differs between the two backgrounds. It still stays under the 1/h allowance, because the integer floor sits below the budget. Two consequences for the prose. (a) "Applied here" implies the radar property carries over, and it does not. (b) Item 4 judges the 1.5/h busier-stretch rate (95 % interval 0.5–3.5) only against "the one-per-hour allowance" and blames the clutter edge alone. The right baseline is about 0.5/h on a flat 0.05 Hz background, so estimation noise is a second contributor alongside the edge. | moderate (the method's main invariant is misattributed; the numbers are right) | Add one sentence to §1.2.3: unlike Finn & Johnson's, whose multiplier is set for the size of the reference window, this threshold puts the estimate into the known-rate floor, so its chance-call rate is not fixed (on flat backgrounds 0.6/h at 0.0096 Hz and 0.5/h at 0.05 Hz, against 0.3/h with the rate known). In item 4, compare the 1.5/h with that 0.5/h baseline. Optionally add a flat-background control to `fig_detectors` so the log prints the baseline. | yes (both papers; my simulation used the script's own `plant`, `sliding_count`, `local_rate`, `chance_floor` and `cfar_calls` at the shipped 30 s reference, 5 s guard and 3 s merge gap; a smaller run through the repo's `count_sliding_detect` gave 0.23/h and 0.45/h at the known floors) |
| 2 | ch1_intro_figures.py docstring ll. 31–34 | **The window ends also differ from `count_sliding_detect`, not only the merge-gap ends.** The repo's `sliding.pieces` works on float times. In about 0.8 % of frame positions `x*0.1 + 2.0 > (x+20)*0.1`, so two onsets exactly 2.0 s apart both count in the repo's window. `sliding_count` is strictly half-open (t − w, t] on whole frames. A related quirk: `cfar_calls` calls `span_of(ev, starts[a] - w, …)`, whose lower bound is inclusive, so a call's span can include an onset that left the window exactly as the run began. `count_sliding_detect` has the same quirk. Effect on the numbers is negligible. | low | Extend the "two edge cases" sentence to three: window ties, as well as merge-gap ties. | yes (numerical check over frames 0–2400) |
| 3 | ch1_intro_figures.py l. 756; docstring ll. 38–39 | The `main` assertion "gives the count detector's simulated floors" compares the analytic formula with the hard-coded integers 6 and 12. It does not run the repository's simulated floor, so it guards the quotation in the chapter, not an agreement between methods. The chapter (ll. 137–141) already says this is agreement at two integer points, which is fair. | low | Reword the docstring: "asserts the formula gives the 6 and 12 cells §1.6.1 quotes from the simulated floor". | yes |
| 4 | ch1_intro_figures.py l. 608 | `np.nanstd(boot)` drops any bootstrap draw where `hwhm` returned NaN and does not report it, so the stated SE could rest on fewer than 500 draws. Unlikely to bite at these peak heights. | low | Print the count of finite draws beside the SE. | yes (code read) |

## Checked and found correct (no finding)

**Bin edges and float times:**
- For every frame time f·0.1 s up to 2700 s, the float bin index matches the integer one: `floor(t/2)` = f//20 for 2 s bins and `t//1` = f//10 for 1 s bins. No onset falls into a neighboring fixed bin through float error.
- The "x.95 s border" reasoning for event 2 holds.

**Sliding count and step plots:**
- `sliding_count` implements (t − w, t]: active at frames x … x + wf − 1.
- `step(where='post')` is the right choice for S and K_t. This matches the matplotlib docs: "[x[i], x[i+1]) has the value y[i]".

**Chance floor:**
- `chance_calls_per_hour` and `chance_floor` equal theory_floor's u_K and `floor_analytic`, including the guard that every larger K also meets the budget, with the minimum of 3 cells.
- The up-crossing formula leaves out jumps of two or more cells within one frame. That error is negligible at these rates, and the chapter's "errs toward a higher floor" is correct as stated.

**CFAR details:**
- `local_rate` takes the 30 s reference beyond a 5 s guard on either side, as the chapter says.
- The `searchsorted` 'left'/'left' pairs count onsets in [lo, hi).

**Statistics (all checked by hand):**
- The exact Poisson (Garwood) interval `chi2.ppf(.025, 2x)/2`, `chi2.ppf(.975, 2x+2)/2` is right; it gives 0.5–3.5/h for 5 in 200 min.
- `binom.sf(K−1, N, p)` = P(X ≥ K), as the scipy docs define sf.
- HWHM = σ√2·√(2 ln 2) = 2√(ln 2)·σ ≈ 1.665σ.
- g₂ = ½ at w = 2.08σ; I computed 2.0795 numerically.
- f₂ and f₃ are the factorial cumulants and equal zero for Poisson counts.

**Frame-rounding model for the correlogram:**
- The generator places event times continuously (`_place_renewal`), so frame phase is uniform.
- Under uniform phase, the triangular kernel in `predicted_lag_pmf` is the exact law of the rounded lag.
- Using `quad` with `points=[Lg]` inside a finite interval is valid per the scipy docs.

**Correlogram normalization:**
- `mjc.pairs` counts unordered onset pairs per |lag|, with zero lag counted once, against an expectation halved the same way.
- So the script's `peak_pred = n_rec·E·k(k−1)·pmf` with `peak_pred[0] /= 2` is consistently normalized.

**Coordination-rates tool:**
- It runs at its shipped `N_SURR` = 20 and shifted surrogates.
- The chapter correctly says only 1, 2 and 4 s are shipped windows (`mcr.WINDOWS`) and that 0.2, 0.5 and 8 s are off its settings.

**Model used for the bin figures:**
- `plant` thins the background correctly and rounds half away from zero for positive times, matching `matlab_round`.
- The 1 s bin survival compared against Binomial(N, 1 − e^(−b)) is the right null for background alone.

**Every number quoted** in §1.2.4, Table 1.1 and §1.3.2–1.3.4 matches the rerun log.

unreached: 0
