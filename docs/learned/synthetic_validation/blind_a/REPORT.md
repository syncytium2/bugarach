# Blind pass A: final report, verbatim (2026-10-23)

Kept so the goal page's attributions to blind pass A can be checked (murderboard 2026-10-23,
roles 1 and 3). The agent worked in a detached checkout of `main` at c442014a and ran against
the first Aim 1a record, now `../aim1_one_source_shared_seeds.json`. Personal paths are replaced
by `<worktree>`; nothing else is changed. Its scripts are beside this file and do not run in
place (their paths assume the worktree's `_scratch/`).

---

**Answer: yes, mostly.** The Aim 1a generator is a marked Neyman–Scott cluster process: Poisson background, plus m parents that each have k offspring in distinct cells, with Gaussian jitter σ on a 0.1 s grid. Both measuring tools are fixed functionals of counts in windows. Their expected outputs follow from (σ, k, m, b, N, T, w, K) in closed form, or with a one-dimensional integral or a small one-event Monte Carlo. I checked everything against the record and against 960 fresh recordings of my own. All scripts are in `<worktree>/_scratch/`. Nothing tracked was edited.

## 0. A design flaw found on the way (important)
The record's seeds are `1000+seed` for every cell, and `simulate_coordination` draws the background first. So **all 48 cells at one background rate share the same 5 background realisations**: 29 of 33 cells had identical background trains across two different cells (`check_shared_bg.py`).

- Errors in Figure 1 are therefore correlated across the whole panel, and there are effectively n = 5 replicates per background.
- At 0.05 Hz, the 5 shared backgrounds happen to have negative background-only f3 (mean −0.09, about −2.6 SE).
- Much of the "under-recovery at 0.05 Hz" in Figure 1 is this sampling accident and not a property of the tool (table A, "rec" vs "fresh").
- Fix: seed per cell, as `run_fresh.py` does (seed = 50000 + 100·cell + s).

## 1. Coordination-rates tool (`theory_common.py`, `theory_cr.py`, `compare_fresh.py`)
**Derivation.** Factorial cumulants add over independent components, and Poisson background contributes zero. Let P₂(w,σ) and P₃(w,σ) be the probability that 2 or 3 onsets of one event (jittered, then frame-rounded) fall in the same window, averaged over the event's position within the window; this is a one-dimensional integral over Gaussian bin masses. With min-sep larger than w, so no two events share a window:

- f₂ = λw[k(k−1)P₂ − λwk²]
- f₃ = λw[k(k−1)(k−2)P₃ − 3λwk²(k−1)P₂ + 2(λw)²k³]

`solve()` assumes P₂ = P₃ = 1, so it reports:
- k̂ = 2 + (k−2)P₃/P₂
- λ̂ = f₂ / (w·k̂(k̂−1))

For σ ≫ w, P₂ ≈ w/(2σ√π) and P₃/P₂ → 0. Hence k̂ → 2 and λ̂ inflates: **this is the whole "window must exceed jitter" behaviour**. The share is more robust because it scales as (k−1)P₂²/((k−2)P₃+P₂).

**Noise.** The noise uses Charlier polynomials, which are orthogonal under Poisson:
- Var f̂₂ = 2μ²/n and Var f̂₃ = 6μ³/n, with μ = Nbw and n = T/w.
- The tool averages two half-shifted window offsets, which multiplies these by 0.75 and 0.625.
- Event and event×background cross terms come from a one-event Monte Carlo.
- Draws of (f₂, f₃) are pushed through `solve()`.

**Table A — recovered ÷ planted, median pooled over participation, event count and seeds (as in Figure 1). th = theory, fresh = my 10 independent seeds per cell, rec = Aim 1a record.**

| b | w | σ | k th / fresh / rec | rate th / fresh / rec | share th / fresh / rec |
|---|---|---|---|---|---|
| .01 | 1 | .05 | .95 / .94 / .93 | 1.03 / 1.06 / 1.08 | .98 / 1.00 / 1.01 |
| .01 | 1 | .5 | .62 / .62 / .61 | 1.31 / 1.36 / 1.41 | .82 / .83 / .86 |
| .01 | 1 | 1 | .43 / .43 / .42 | 1.68 / 1.69 / 1.78 | .72 / .74 / .75 |
| .01 | 4 | 1 | .76 / .76 / .74 | 1.23 / 1.23 / 1.36 | .93 / .95 / .98 |
| .05 | 1 | .5 | .63 / .59 / .55 | 1.32 / 1.47 / 1.68 | .82 / .85 / .92 |
| .05 | 1 | 1 | .43 / .39 / .33 | 1.69 / 2.05 / 2.60 | .73 / .80 / .88 |
| .05 | 4 | 1 | .79 / .72 / .70 | 1.16 / 1.36 / 1.42 | .92 / .96 / .99 |

- Over all 72 cell×window combinations, the mean of f₂ (observed ÷ predicted) is 1.003 (IQR 0.98–1.02); for f₃ it is 0.987 (0.96–1.01).
- At 0.01 Hz, k agrees within 0.01–0.02 everywhere.
- **Residuals.**
  - There is a +3–5 % excess in λ that I have not explained.
  - At 0.05 Hz with k = 5, the error propagation fails: f₃ often goes negative, about 12 % of recordings return NaN, and the selection that removes them biases the medians.
  - My noise SDs are conservative: observed SD ÷ predicted is 0.6–0.9. The likely cause is that the surrogates share each cell's own counts, which I ignore.

**Detection SNR, a byproduct:** z₂ ≈ m·k(k−1)·P₂ / (N·b·√(1.5·w·T)). Treat it as accurate to within about 30 %.

## 2. An analytic correction: jitter for free (`invert_cr.py`)
The ratio f₂(w)/w = λk(k−1)P₂(w,σ) − O(λ²) depends on w only through σ. So the three windows the tool already computes identify σ. I fitted (σ, k, λ) jointly to the 6 cumulants by weighted least squares.

**Table B — fitted ÷ planted, median (IQR). Windows 1, 2, 4 s.**

| b | σ | σ̂/σ fresh | k̂/k fresh | λ̂/λ fresh | k̂/k on the record |
|---|---|---|---|---|---|
| .01 | .05 | 0.64 (0.20–1.56) | 0.99 | 1.02 | 1.01 |
| .01 | .2 | 1.04 (0.95–1.12) | 1.00 | 1.02 | 1.00 |
| .01 | 1 | 0.99 (0.93–1.10) | 1.02 | 1.01 | 1.02 |
| .05 | .2 | 0.97 (0.67–1.26) | 1.00 | 1.01 | 0.94 |
| .05 | .5 | 0.99 (0.91–1.05) | 0.97 | 1.06 | 0.96 |
| .05 | 1 | 1.01 (0.91–1.21) | 0.99 | 1.02 | 0.97 |

For comparison, the current naive 1 s estimates at b = 0.05, σ = 1 are k 0.39× and rate 2.05×.

- With windows of 0.5–8 s, σ at 0.05 s improves to 0.94 (0.37–1.39).
- σ below about 0.1 s (the frame) is only bounded from above. That is a resolution limit, not a defect of the fit.
- **This turns jitter from the weak parameter into a recovered one.** The fit assumes Gaussian jitter and fixed k; real data will need a mixture over k.

## 3. Assessment tool (`theory_assess.py`, output in `theory_assess.out`)
**Chance clusters, exact.** Under Poisson background, 1 s bins are independent, and each bin's count of active cells is Binomial(N, q) with q = 1−e^(−b).
- A cluster is a run of bins ≥ K, merged across gaps of up to 2 bins. Clusters start at r_K = p_K(1−p_K)², where p_K = P(Bin ≥ K).
- At N = 33, b = 0.05 this gives 7.97, 3.86 and 0.28 per minute at K = 3, 4, 6. A local Monte Carlo gives 7.98, 3.81 and 0.29.
- **That is the "8–16× event rate" in Figure 1.**

**Planted events.** Predicted clusters/min = 60[r_K(T−2Rm) + m·G]/T, where G is the expected number of clusters per event from a one-event neighbourhood Monte Carlo that uses bugarach's own `_clusters`. The `part_n_obs` and `jit_obs` predictions are mixture medians of chance and event clusters.

| case | clusters/min pred / obs | part pred / obs | jit pred / obs |
|---|---|---|---|
| b .05, K 3, σ .05, f .15, m 15 | 8.05 / 7.98 | 6 / 6 | .73 / .75 |
| b .05, K 6, σ .2, f .6, m 45 | 1.26 / 1.22 | 21 / 22 | .34 / .35 |
| b .01, K 6, σ .2, f .15, m 15 | .044 / .044 | 6 / 7 | .25 / .24 |
| b .01, K 4, σ 1, f .15, m 15 | .096 / .111 | 6 / 5 | .54 / .54 |
| b .01, K 4, σ .05, f .15, m 15 | .34 / .36 | 6 / 6 | **.17 / .31** |

- Across all 144 rows, the rate agrees within about 5–10 % (worse where counts are under one per recording), and participants within ±1.
- The jitter misses (as in the last row) are at low σ with k = 5. There the gathered set is bimodal (zero or one background cell inside ±1.5 s), so a median over about 15 clusters is unstable.
- **Why jitter saturates:** the ±1.5 s gather caps it. A Normal(0, 1) truncated at ±1.5 has SD 0.74, and background onsets within the window pull the value toward about 0.6–0.7.

## 4. ADR-0008 chance floor (`theory_floor.py`)
The up-crossing rate of the sliding 2 s distinct-cell count is u_K = (N−K+1)·b·Binom.pmf(K−1; N, 1−e^(−2b)). The chance floor is the smallest K with 3600·u_K ≤ 1 for all K' ≥ K. Comparing with `window_floor` at 100 draws:

| b (Hz) | 0.005 | 0.01 | 0.02 | 0.05 | 0.1 | 0.2 |
|---|---|---|---|---|---|---|
| Monte Carlo floor | 5 | 6 | 8 | 12 | 16 | 23 |
| analytic floor | 5 | 6 | 8 | 12 | 17 | 23 |

The formula overstates calls per hour by up to about 25 % at higher rates, probably because the sliding window moves in 0.1 s steps.

## 5. Other analytic routes
1. **Cumulant / window-capture** (sections 1–2). It extends to several sources linearly: f₂(w) = Σᵢ λᵢ·w·kᵢ(kᵢ−1)·P₂(w,σᵢ). For Aim 1c, whether the tools report one source or two becomes a rank and conditioning question on the window kernel matrix, which can be answered before simulating.
2. **Occupancy and scan statistics** for the K-threshold tools and detectors (sections 3–4). The count and binned-SCE detectors are thresholded versions of the same binned count, so their false-alarm rate is about r_K and their hit rate about G. I did not test this on the detectors.
3. **Point-process second-order theory.** The pairwise excess correlogram should be [λk(k−1)/(N(N−1)b²)]·Normal(τ; 0, 2σ²). That is a direct prediction for the correlogram tool, untested because the tool cannot yet read a synthetic folder.
4. **Likelihood / Fisher information** for the Neyman–Scott model. It would give Cramér–Rao bounds, which are the identifiability boundary Aim 1 asks for. I did not do this.
5. **Shared slow comodulation.** It should add f₂ ∝ N²b²w²·Var(multiplier) for w ≪ τ. That grows with w differently from coordination (about w⁰ for w ≫ σ), so the same multi-window fit could separate them. This is untested.

## 6. What still needs simulation
- Detectors with tuning loops and data-dependent rolling nulls: LoCo's rolling percentile and CoactDetect's local surrogates. Theory gives their limits, not their tuned operating point.
- Assembly recurrence (Aim 1b) and the `bugarach.assembly` test.
- Interactions under bursty or non-stationary background. Every formula here assumes Poisson; the rigid-shift nulls exist precisely because real data are not.
- Small-count regimes (k ≈ 5 at high background), where the error propagation and NaN selection break.
- The Aim 3 loop as a whole.

## Recommendation
1. Fix the seed sharing and re-issue Figure 1 before reading anything into the 0.05 Hz row.
2. Fit (σ, k, λ) across windows instead of running `solve()` per window. It recovers jitter to about 10 % for σ ≥ 0.2 s and k and rate to a few per cent, and the code is small.
3. Correct the assessment's cluster rate analytically, as (clusters/min − 60r_K)/G, and choose K from r_K directly rather than from a fixed value.
4. Place Aim 2's grid on dimensionless axes: σ/w (or σ/bin), the SNR z₂, and 60r_K/λ. Densify where z₂ ≈ 1–5 and around the floor ±1; uniform raw-parameter axes waste most cells on regions whose outcome is already predictable.
5. Simulation is still needed for the detectors themselves and for the non-Poisson cases, but theory can pick the cells and serve as the check on each run.

**Caveats.** The assessment predictions rely on a local Monte Carlo of a single event's neighbourhood, so they are semi-analytic rather than closed form. Everything assumes Poisson background, Gaussian jitter and fixed k.

**Scripts** (all in `<worktree>/_scratch/`):
- `theory_common.py`
- `theory_cr.py`
- `compare_fresh.py`
- `check_noise.py`
- `run_fresh.py`, whose output is `fresh_cr.json`
- `invert_cr.py`
- `theory_assess.py`, whose output is `theory_assess.out`
- `theory_floor.py`
- `check_shared_bg.py`
- the probes `probe_bias*.py` and `probe_seeds.py`
