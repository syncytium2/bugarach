# Does Elephant already implement the bugarach estimators? Code audit

**Scope.** I read the source of Elephant (NeuralEnsemble/elephant, `master` at commit `32f1b56`, 2026-06-16, version string `1.2.2b1`), its tutorials and release notes, and searched its GitHub issues and PRs. No Elephant code was executed. The comparison targets are the four bugarach items:

1. **Joint fit.** Recover participants per event, event rate and Gaussian onset jitter from population pair and triple counts (factorial cumulants) at several window widths. A window-sharing term g_n(w,σ) = E[(1 − range/w)+] links the widths.
2. **Population-count cumulant estimators.** Includes an at-most-one-event correction, or treatment of events held apart.
3. **Fast order indicator.** A net-lead (Borda) ranking over shared events. It has a closed form (2/π)·arctan(spread/jitter) for one latency template and an analytical no-order bias of about c/√(events per pair).
4. **Analytical nulls** for sequence or synfire statistics, in place of surrogates.

---

## 1. `elephant/cubic.py`: CuBIC (Staude, Rotter & Grün 2010)

- **Functions.**
  - `cubic(histogram, max_iterations, alpha)` (around line 64).
  - `_H03xi` (around line 149): the p-value.
  - `_kappamstar` (around line 193): the maximised cumulants.
  - `_kstat` (around line 221): wraps `scipy.stats.kstat` for orders 1–3.
- **Algorithm.**
  - Input is a single binned population count histogram, at one bin size chosen by the user.
  - It computes the first three k-statistics κ1, κ2, κ3.
  - For ξ = 1, 2, … it tests H0: κ3 ≤ κ*₃,ξ. Here κ*_m,ξ = [κ2(ξ^{m−1} − 1) − κ1(ξ^{m−1} − ξ)]/(ξ − 1) is the largest m-th cumulant that a compound Poisson process (CPP) with maximum correlation order ξ can produce, given κ1 and κ2.
  - It returns the smallest ξ that is not rejected. This is a **lower bound on the largest assembly order**.
- **Null.** Analytical. κ3 is treated as Gaussian with variance from Stuart & Ord:
  Var(k3) ≈ κ*6/L + 9(κ*4κ*2 + κ*3²)/(L−1) + 6Lκ*2³/((L−1)(L−2)),
  evaluated at the maximised cumulants. L is the number of bins.
- **Finite-size handling.**
  - k-statistics are unbiased for finite L.
  - The variance of k3 carries explicit L, L−1 and L−2 terms.
  - There is a hard error when κ2 < κ1, which happens for small populations or small bins.
- **Distance to bugarach.**
  - It estimates no event rate, no participants per event (no amplitude distribution) and no jitter.
  - It uses one bin size only, with no multi-window fit and no window-sharing term.
  - It uses ordinary cumulants of the count, not factorial cumulants or pair and triple counts.
  - It applies no at-most-one-event correction. Events that straddle a bin edge are split, and nothing models this.
  - Closest to items 1–2 in spirit: population-count cumulants and a CPP model. Far apart in what is estimated.

## 2. `elephant/asset/asset.py`: ASSET (Torre et al. 2016)

- **Class and methods.**
  - `ASSET.intersection_matrix` (around line 2128).
  - `probability_matrix_analytical` (around line 2298).
  - `probability_matrix_montecarlo` (around line 2173).
  - `joint_probability_matrix` (around line 2440).
  - `cluster_matrix_entries` (around line 2663), which uses DBSCAN on a stretched metric.
  - `extract_synchronous_events` (around line 2810).
  - `_JSFUniformOrderStat3D` (around line 652), with CPU, CUDA and OpenCL kernels.
- **Algorithm.**
  - It bins the spikes and builds a time-bin × time-bin matrix. Each entry I[i,j] is the number of neurons active in both bin i and bin j.
  - A repeated sequence of synchronous events shows up as a diagonal stripe in this matrix.
  - The stripes are found by thresholding the probability matrices and clustering.
- **Analytical null, step 1 (probability matrix).**
  - Each neuron's rate is estimated with a boxcar kernel.
  - The per-bin spike probability is p = 1 − exp(−rate·bin).
  - Under independence, I[i,j] is approximated as Poisson with mean Σ_k p_ik·p_jk (Le Cam's approximation).
  - The probability matrix is `pmat = poisson.cdf(imat − 1, Mu)`.
- **Analytical null, step 2 (joint probability matrix).**
  - A rectangular kernel is laid along the diagonal around each entry. It covers n = l(1+2w) − w(w+1) entries.
  - The `n_largest` = d largest pmat values in the kernel are taken.
  - Their joint p-value is computed **exactly** as a joint survival function of the top-d order statistics of n i.i.d. uniforms. This is a combinatorial sum over combinations with replacement, done in log space.
  - pmat values are capped at 1 − `min_p_value` so that one extreme entry cannot dominate.
- **Finite-size handling.**
  - The order-statistic joint p-value is exact for finite n and d.
  - The Poisson step is an approximation.
  - The rate estimate keeps the edge bins flat (border correction).
  - Nothing corrects for estimating the rate from the same data.
- **Ordering.** A sequence is a cluster of (bin_x, bin_y) pixels. Each pixel carries the set of neurons active in both bins. The tutorial orders the neurons by their first appearance along the cluster, in row-major `np.where` order. That amounts to **sorting neurons by their binned latency within one pair of occurrences**. There is no aggregation over events and no ranking statistic.
- **Distance to bugarach.**
  - It has an analytical null (item 4), but for "more overlap than chance between two time bins", not for an order statistic.
  - It does not produce a net-lead ranking (item 3).
  - It estimates no jitter or participation (item 1).
  - The order-statistics joint p-value is a reusable piece.

## 3. `elephant/spade.py`, `spade_src/`, `spike_train_surrogates.py`: SPADE (Torre 2013; Quaglio 2017; Stella 2019)

- **Functions.**
  - `spade` (around line 155).
  - `concepts_mining` (around line 556).
  - `_fpgrowth` (around line 792): the C++ `fim` back end, FP-growth by F. Porrmann.
  - `_fast_fca` (around line 1057): a pure-Python fallback.
  - `pvalue_spectrum` (around line 1196), with `_generate_binned_surrogates`, `_get_max_occ` and `_get_pvalue_spec`.
  - `test_signature_significance` (around line 1563): Bonferroni, Holm, FDR-BH and other corrections.
  - `approximate_stability` (around line 1736).
  - `pattern_set_reduction` (around line 1945).
- **Algorithm.**
  - The data are binned and laid out in a sliding window of `winlen` bins.
  - Frequent itemset mining then finds closed patterns: exact (neuron, bin-lag) sets that repeat at least `min_occ` times.
- **Pattern-spectrum filtering.**
  - Each pattern gets a signature: (size z, count c) for `'#'`, or (z, c, duration) for `'3d#'`.
  - For each surrogate data set, mining is run again and the **largest** count per (size[, duration]) is recorded.
  - The p-value of a signature (z, c) is the fraction of surrogates whose largest count is at least c. It is made monotone in size.
  - Signatures with p = 1 are masked, and multiple-testing correction is applied over the remaining signatures.
  - Pattern-set reduction then removes subset and superset patterns that are explained by others.
- **Null: surrogates only.** Supported methods are `dither_spikes` (the default), `dither_spikes_with_refractory_period`, `dither_spike_train`, `jitter_spikes`, `randomise_spikes`, `shuffle_isis`, `joint_isi_dithering`, `isi_dithering`, `trial_shifting` and `bin_shuffling`.
- **Finite-size handling.** None analytic. Significance is empirical, so the smallest attainable p-value is 1/n_surr, and the docstring recommends n_surr ≥ 1000 for 100 trains.
- **Runtime notes.**
  - Mining dominates the cost. A maintainer reply in issue #713 (2026) says "most of the cost is in pattern mining" and that "the SPADE module is due for a complete restructure"; they declined an accelerated surrogate backend.
  - Memory blows up unless `min_occ` and `min_spikes` are set high enough (issue #555).
  - There is MPI parallelism over surrogates.
  - Speed-up PRs: #280/#285/#286 (×7) and #419. The C++ wheels for macOS and Windows were restored in #695.
  - Issue #439 (open): the filtering steps are under-documented. Issue #620: confusion about the effective alpha.
- **Distance to bugarach.**
  - SPADE detects *exact* repeated lag patterns, which is the opposite of a jitter-tolerant order indicator.
  - Its null is entirely surrogate-based.
  - It covers none of items 1–4. Its surrogates could serve as an independent check on our analytical nulls.

## 4. `elephant/unitary_event_analysis.py`: Unitary Events (Grün et al. 1999, 2002, 2003)

- **Functions.**
  - `jointJ_window_analysis` (around line 683).
  - `n_emp_mat` and `n_exp_mat`, with `_n_exp_mat_analytic` and `_n_exp_mat_surrogate`.
  - `gen_pval_anal` (around line 505).
  - `jointJ` (around line 591).
- **Algorithm.**
  - Trials are binned and clipped to binary, then analysed in sliding windows (`win_size`, `win_step`).
  - Within each window it counts the bins that show an exact pattern hash. The hash also fixes which neurons are *silent*.
- **Null.** Analytical: the expected count is n_bins × Π_k p_k^{m_k}(1−p_k)^{1−m_k}, with p_k the per-window marginal. The p-value comes from a Poisson tail on that expectation. Variants are `analytic_TrialByTrial`, `analytic_TrialAverage`, and a surrogate method that shuffles each row.
- **Jitter and window handling.**
  - **No jitter tolerance.** Coincidences must fall in the same bin.
  - The "multiple-shift" or disjoint-window coincidence counting of Grün et al. 1999 is **not implemented** (a grep for shift, jitter or dither in the module finds nothing).
  - The window only sets where rates are estimated. The code warns when `win_size` or `win_step` is not a whole number of bins.
- **Distance to bugarach.** It is an analytical null for a synchrony count (item 4, partly). It has no multi-width fit, no window-sharing term and no ordering.

## 5. `elephant/cell_assembly_detection.py`: CAD (Russo & Durstewitz 2017)

- **Functions.**
  - `cell_assembly_detection` (around line 85).
  - `_test_pair` (around line 549).
  - `_chunking` (around line 449).
  - `_significance_pruning_step` and `_subgroup_pruning_step`.
- **Pairwise step.**
  - For each pair it builds the binned cross-correlogram over lags in [−max_lag, max_lag]. Count-valued bins are split into parallel binary processes.
  - **best_lag = argmax** of that correlogram.
  - The test statistic is the difference between the count at best_lag and the count at best_lag ∓ `reference_lag`. This is a local contrast that corrects for non-stationarity.
  - The difference is squared and divided by an analytical variance built from the marginal counts of each chunk, with chunks of `size_chunks`.
  - It is compared against F(1, n).
  - Alpha is Bonferroni-corrected over pairs × lags (issue #443, fixed in #576).
- **Agglomeration.**
  - The assembly's activation series is treated as a new "unit" and tested against further neurons.
  - The output lag list gives each member's lag relative to the *first agglomerated* unit, which is not necessarily the earliest.
- **Null.** Analytical (F-test). This is the most relevant precedent for item 4 at the pair level.
- **Ordering.** Each pair gets a direction, sign(best_lag), which is the **mode** of the latency-difference distribution. The cells are never ranked from these directions.

## 6. Other modules

- **`spike_train_correlation.py`.** `cross_correlation_histogram`, `spike_time_tiling_coefficient`, `covariance`, `correlation_coefficient` and `spike_train_timescale`. All are descriptive, with no null and no ordering statistic.
- **`statistics.py`.**
  - `Complexity` (around line 1333) and `complexity_pdf` build a population-count histogram.
  - With `spread` > 0, `Complexity` merges spikes separated by fewer than `spread` empty bins into one "event". That is a crude way to keep one event from being split, but it is not a correction to any estimator.
- **`spike_train_synchrony.py`.**
  - `spike_contrast` (Ciba 2018) scans many bin sizes, which is multi-timescale, but it only returns a synchrony index.
  - `Synchrotool` deletes or annotates synchronous spikes ("synchrofacts").
- **`functional_connectivity` (TSPE).** Edge-filtered cross-correlograms that give the delay and sign of each connection. It has no null and no population ordering.
- **`spike_train_generation.py`.** These are useful for validating our code:
  - `single_interaction_process(..., jitter=)` injects coincidences with **uniform** ±jitter per spike.
  - `compound_poisson_process(rate, amplitude_distribution, shift=)` draws CPP events with a given amplitude (participant) distribution. `shift` dithers each *whole train*, which acts as a fixed per-cell latency offset (a uniform latency template) rather than per-event jitter.
  - Neither generator produces Gaussian per-event jitter.
- **A grep of the whole package** for latency, synfire, Borda, rank order, precedence, cumulant or "multiple shift" finds nothing beyond the ASSET docstring example and CuBIC.

## 7. Docs, tutorials, issues and PRs

- **Tutorials.** `asset`, `spade`, `unitary_event_analysis`, `gpfa`, `granger_causality`, `statistics` and `parallel`. There is no CuBIC or CAD tutorial.
  - The ASSET tutorial recovers a synfire-chain permutation of neurons from the first-appearance order of one cluster.
- **Issues and PRs.** Searches for sequence, speed, faster, analytical, cubic, cumulant, synfire, order, latency and surrogate found:
  - **Speed:** ASSET GPU work (#351, #399, #404, #259, #333, #667), SPADE (#280, #419, #695, #713) and UE (#489).
  - **Open:** online UE (#491), UE with trials (#643), SPADE docs (#439).
  - Nothing proposes a cumulant-based fit of rate, participation or jitter, an order or net-lead statistic, or an analytical null for sequences.
  - CuBIC has not changed in substance since PR #50; later PRs fixed only the build, deprecations and 32-bit tests.

## 8. Own check: do CAD's or ASSET's ordering rules reduce to a net-lead ranking?

I wrote an independent simulation; no Elephant code was used. The model:

- 33 cells, 60 events, participation q = 0.6.
- A single latency template drawn uniformly over [0, spread] frames, plus Gaussian per-event jitter.
- Spike times binned at 1 frame; 20 replicates per row.

I compared five rankings against the true order (Kendall τ):

- **(a) Net lead.** For each cell, the sum over partners of sign(t_j − t_i) across shared events (Borda).
- **(b) CAD sign.** CAD's pairwise rule, best_lag = argmax of the binned correlogram, with sign(best_lag) then summed by Borda. CAD itself never does this aggregation.
- **(c) CAD anchor.** CAD's own output style: each cell's lag relative to an anchor unit. The anchor here is the true first cell, which is favourable to CAD.
- **(d) ASSET, one pair.** ASSET-style ordering from one pair of occurrences: cells whose binned relative latency matches within ±1 bin in both occurrences, sorted by bin.
- **(e) ASSET, all pairs.** The same ordering averaged over all occurrences, which is a mean binned latency.

| spread | jitter | (a) net lead | (b) CAD sign | (c) CAD anchor | (d) ASSET 1 pair | (e) ASSET mean | τ((b), (a)) | τ((e), (a)) |
|---|---|---|---|---|---|---|---|---|
| 4 | 0.5 | 0.91 | 0.91 | 0.83 | 0.79 | 0.94 | 0.91 | 0.92 |
| 4 | 1 | 0.88 | 0.85 | 0.69 | 0.71 | 0.89 | 0.88 | 0.91 |
| 4 | 2 | 0.81 | 0.73 | 0.42 | 0.46 | 0.81 | 0.80 | 0.89 |
| 2 | 2 | 0.67 | 0.55 | 0.20 | 0.22 | 0.66 | 0.67 | 0.86 |
| 8 | 1 | 0.92 | 0.92 | 0.82 | 0.90 | 0.95 | 0.91 | 0.93 |

**Exact identity.** When each cell fires at most once per event, a pair's net lead equals the correlogram mass at positive lags minus the mass at negative lags. The simulation confirms this exactly, for example 22 = 22. CAD instead uses the correlogram's **mode**.

**Reading.**

- Neither method reduces to a net-lead ranking as implemented.
- CAD's pairwise direction agrees with net lead in sign whenever the latency difference is symmetric and unimodal, as with Gaussian jitter. Summed by Borda, it gives nearly the same ranking, but it is noisier at high jitter because the mode is a less efficient statistic than the sign mass. CAD does not perform that aggregation.
- CAD's actual output (lags to one anchor) and ASSET's actual ordering (one pair of occurrences) both degrade quickly once jitter is comparable to spread.
- An ASSET-style ordering averaged over events (a mean-latency sort) comes close to net lead. Neither CAD nor ASSET provides an analytical bias or null for the ranking.

The script used:

```python
import numpy as np
from scipy.stats import kendalltau
rng = np.random.default_rng(1)

def simulate(N=33, E=60, q=0.6, spread=4.0, jitter=1.0, T_gap=50):
    lat = np.sort(rng.uniform(0, spread, N))[rng.permutation(N)]
    part = rng.random((E, N)) < q
    t = np.full((E, N), np.nan)
    onsets = np.arange(E) * T_gap + 10
    tt = onsets[:, None] + lat[None, :] + rng.normal(0, jitter, (E, N))
    t[part] = tt[part]
    return lat, t

def net_lead_rank(t):
    N = t.shape[1]; s = np.zeros(N)
    for i in range(N):
        for j in range(N):
            if i != j:
                both = ~np.isnan(t[:, i]) & ~np.isnan(t[:, j])
                s[i] += np.sign(t[both, j] - t[both, i]).sum()
    return s

def cad_like_rank(t, max_lag=6):          # argmax-lag per pair, Borda-summed
    b = np.floor(t); N = t.shape[1]; s = np.zeros(N)
    for i in range(N):
        for j in range(i + 1, N):
            both = ~np.isnan(b[:, i]) & ~np.isnan(b[:, j])
            d = (b[both, j] - b[both, i]).astype(int); d = d[np.abs(d) <= max_lag]
            if d.size:
                best = np.argmax(np.bincount(d + max_lag, minlength=2*max_lag+1)) - max_lag
                s[i] += np.sign(best); s[j] -= np.sign(best)
    return s

def cad_anchor_rank(t, anchor):           # lag of each unit to one anchor (mode)
    b = np.floor(t); lags = np.zeros(t.shape[1])
    for j in range(t.shape[1]):
        both = ~np.isnan(b[:, anchor]) & ~np.isnan(b[:, j])
        v, c = np.unique((b[both, j] - b[both, anchor]).astype(int), return_counts=True)
        lags[j] = v[np.argmax(c)] if v.size else 0
    return -lags

def asset_like_rank(t, e1, e2):           # one occurrence pair, sort by bin
    b = np.floor(t)
    r1 = b[e1] - np.nanmin(b[e1]); r2 = b[e2] - np.nanmin(b[e2])
    idx = np.where(~np.isnan(r1) & ~np.isnan(r2) & (np.abs(r1 - r2) <= 1))[0]
    return idx, -r1[idx]

def asset_mean_rank(t):
    b = np.floor(t); return -np.nanmean(b - np.nanmin(b, 1, keepdims=True), 0)

tau = lambda a, b: kendalltau(a, b).statistic
for spread, jitter in [(4, .5), (4, 1), (4, 2), (2, 2), (8, 1)]:
    rows = []
    for _ in range(20):
        lat, t = simulate(spread=spread, jitter=jitter); truth = -lat
        nl, cs = net_lead_rank(t), cad_like_rank(t)
        ca = cad_anchor_rank(t, int(np.argmin(lat)))
        idx, a1 = asset_like_rank(t, 0, 1); am = asset_mean_rank(t)
        rows.append([tau(nl, truth), tau(cs, truth), tau(ca, truth),
                     tau(a1, truth[idx]), tau(am, truth), tau(cs, nl), tau(am, nl)])
    print(spread, jitter, np.round(np.nanmean(rows, 0), 2))
```

---

## Verdicts

| Item | Verdict | Closest Elephant code |
|---|---|---|
| 1. Joint fit of participants, rate and Gaussian jitter from pair and triple counts across window widths, with g_n(w,σ) | **Not found** | CuBIC tests only a lower bound ξ on the largest correlation order, at one bin size, with no jitter or rate estimate. `spike_contrast` scans bin sizes but returns only a synchrony index. |
| 2. Population-count cumulant estimators with an at-most-one-event correction or events held apart | **Partly** | CuBIC uses unbiased k-statistics (κ1–κ3) and the Stuart & Ord finite-L variance of k3. There is no factorial-cumulant form, no at-most-one-event correction, and no treatment of events split across bins or held apart. `Complexity(spread=…)` only merges adjacent bins. |
| 3. Net-lead (Borda) order indicator with arctan closed form and c/√n no-order bias | **Not found** | CAD gives each pair a direction (the argmax lag), and ASSET orders neurons by bin within one pair of occurrences. Neither ranks cells by net lead or gives a closed form or bias. |
| 4. Analytical nulls for sequence or synfire statistics | **Partly** | Analytical nulls exist for *co-occurrence* statistics: ASSET (Poisson via Le Cam, plus an exact order-statistic joint p-value), UE (Poisson), CuBIC (Gaussian k3) and CAD (F-test with a variance corrected for non-stationarity). None tests an *ordering* statistic. SPADE relies on surrogates only. |

## Reusable code (BSD-3 licence)

1. **`scipy.stats.kstat`** (which CuBIC wraps) and the **Stuart & Ord Var(k3)** expression in `cubic._H03xi`. These are ready-made finite-sample cumulant estimates and variances, a baseline next to our factorial-cumulant estimators. `cubic()` itself is a cheap cross-check on the lower bound of the largest assembly size implied by our fit.
2. **`asset._JSFUniformOrderStat3D`.** The exact joint survival function of the top-d of n uniform order statistics, with GPU back ends. Use it if we combine several per-window or per-pair p-values in the same way.
3. **CAD's `_test_pair` variance.** An analytical, chunk-wise variance for a lag-contrast count. It is a template for an analytical null of a *pairwise* lead count under non-stationary rates.
4. **Generators for validation.** `single_interaction_process(jitter=…)` and `compound_poisson_process(amplitude_distribution, shift=…)` give ground-truth data with uniform jitter or latency, against which to test our fit's robustness. The Gaussian case stays in our own simulator.
5. **`spike_train_surrogates`** (`dither_spikes`, `trial_shifting`, `joint_isi_dithering`, `bin_shuffling`). These give an independent surrogate check of our analytical nulls. The bugarach analytical work does not need them at runtime.

Our own code stays necessary for:

- the multi-window joint fit and g_n(w,σ);
- factorial pair and triple counts with the at-most-one-event correction;
- the net-lead ranking, its closed form and its no-order bias.

## Open points a note to Grün's group could settle

1. **CuBIC with jitter and several bin sizes.** Has the group (Staude, Rotter or later work) derived or coded the bin-size dependence of the population-count cumulants under CPP with Gaussian onset jitter, equivalent to our g_n(w,σ)? Is there unreleased code for estimating the full amplitude distribution, as in the non-stationary or "inferring assembly activity" follow-ups, beyond the ξ test in Elephant?
2. **Finite-sample corrections.** Do they use an at-most-one-event (non-overlap) correction, or handle events split across bin edges, in any internal CuBIC variant? Would they accept factorial-cumulant estimators in `cubic.py`?
3. **Ordering statistics.** Is a population ordering statistic (net lead, Borda, or rank order) with an analytical null planned anywhere? This is relevant to the announced SPADE restructure and to ASSET's sequence ordering. Do they know prior results for the (2/π)·arctan(spread/jitter) form or the c/√n no-order bias?
4. **Analytical vs surrogate nulls for SPADE.** Given the maintainers' note that mining, not surrogates, dominates runtime, is there interest in an analytical pattern-spectrum null for jittered synchrony, as an alternative to surrogates?
5. **CAD lag statistic.** Is the argmax (mode) lag deliberate rather than a sign or mass contrast? Would they consider a net-lead aggregation of CAD's pairwise lags as a population ordering output?
6. **Calcium imaging.** Has anyone validated these modules on frame-rate event data, where bins are coarse, rates are low and events are long, rather than on spike trains?
