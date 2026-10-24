# Kreuz-group literature: how they sort for the Synfire Indicator, what null they use, and why they anneal

Prepared for the bugarach project (T. DeFazio), 2026-10-24. Read-only survey. This is a scratch report, so it contains exact quotes; the public repo should paraphrase them.

## What was read

Read in full:
- Kreuz, Satuvuori, Pofahl & Mulansky 2017, *New J Phys* 19:043028. Read from the lab library's copy, all sections and Appendix A.
- Mulansky & Kreuz 2016, PySpike, *SoftwareX*. The lab library's copy.
- Kreuz et al. 2022, *J Neurosci Methods* 381:109703. Read as arXiv 2205.09855v2.
- Mariani et al. 2025, *J Neurosci Methods* 416:110378. Read as arXiv 2410.15018. The published version itself was not checked.
- Kreuz 2026 review, *Biol Cybern* 120:21. Read as arXiv 2510.07140v2 (28 Jul 2026).
- Satuvuori, Malvestio & Kreuz 2020, "Measures of spike train synchrony and directionality", book chapter, arXiv 2001.04406.
- Cecchini et al. 2021, *PLoS Comput Biol* 17:e1008963. Main text plus the S2 Appendix ("SPIKE-Order method").
- Tomlinson et al. 2019, *Epilepsia* 60:898. Read from the PMC full text (PMC6488404, via PubMed), [doi:10.1111/epi.14720](https://doi.org/10.1111/epi.14720).
- PySpike source on GitHub (mariomulansky/PySpike, master): `spike_directionality.py` and `cython/cython_simulated_annealing.pyx`.

Not opened:
- Scholarpedia "SPIKE-order" article: the server returned 502 and an expired certificate.
- cSPIKE MATLAB/MEX source: not located. The parameters of its sort are unverified, so they may differ from PySpike's.
- Satuvuori et al. 2017 *J Neurosci Methods* (adaptive ISI/SPIKE/SPIKE-sync): not read in full. To my knowledge it covers only the symmetric measures, not SPIKE-order.
- Mulansky, Bozanic, Sburlea & Kreuz 2015 (EBCCSP), "A guide to time-resolved and parameter-free measures": not opened. The 2026 review cites it as the source of the Poisson expectation values for the three *symmetric* measures only (ISI, SPIKE, SPIKE-sync, e.g. C = 0.25). Nothing indicates it covers F.
- Searches of Google Scholar, arXiv, PubMed and the general web (no Semantic Scholar API) found no other Kreuz, Satuvuori, Mulansky, Pofahl or Mariani paper on spike-train ordering, and no paper by anyone that gives a non-annealing sort, a null expectation or a bias correction for F.

---

## 1. Kreuz et al. 2017, *New J Phys* (the source paper)

**Why they anneal (sec. 2.4, p. 8).** They give the full justification here:
> "The complexity of the problem to find the optimal spike train order is similar to the well-known traveling salesman problem [31]. For N spike trains there are N! permutations φ, so for large numbers of spike trains finding the optimal spike train order φs is a non-trivial problem and brute-force methods such as calculating the Fφ-value for all possible permutations are not feasible. Instead, one has to make use of methods such as parallel tempering [32] or simulated annealing [33] to search for the optimal order. Here we choose simulated annealing, a probabilistic technique which approximates the global optimum of a given function in a large search space."

So the argument is: brute force over N! orders is infeasible, therefore use a stochastic global search. They never compare annealing with a constructive or ranking method. The comparison to the TSP is loose. Formally, the problem is the **linear ordering problem**, also called weighted feedback-arc-set on a tournament, of the antisymmetric matrix D. That problem is NP-hard. But ranking by row sum (Borda or "weighted wins") is a known constant-factor approximation for it: Coppersmith, Fleischer & Rudra, SODA 2006 / *ACM Trans Algorithms* 2010. The Kreuz papers do not mention this literature.

**How the annealing works (sec. 2.4, p. 8).**
> "We start with the Fu-value from the unsorted permutation and then visit nearby permutations using the fundamental move of exchanging two neighboring spike trains within the current permutation. The update of the synfire indicator when exchanging the spike trains k and k+1 is simply given by ΔF = −2D(k,k+1). All moves with positive ΔF are accepted while the likelihood of accepting moves with negative ΔF is decreased along the way according to a standard slow cooling scheme."

- The start is the input order, with no heuristic initialisation. The only moves are swaps of adjacent trains.
- The paper does reduce F to a pairwise matrix: "Clearly, it is more efficient to sort the spike trains based on a pairwise analysis of the spike trains" (p. 7). That is eq. 13–14, F = 2·Σ_{n<m} D(n,m) / ((N−1)M). Once F is written this way, a row-sum score is the obvious next step, but the paper does not take it.

**Alternatives to annealing.** Parallel tempering is named as an alternative. Greedy search, ranking, Borda counts and sorting by mean SPIKE-order are not mentioned. There is one hint in the same direction: after sorting, "the first spike trains have predominantly high values (red) and the last spike trains predominantly low values (blue) of D(tk)" (p. 8). That is a description of the result, not a method.

**Computational cost.** No runtime for the sort is given. The discussion (p. 20) says only: "The new algorithm is conceptually simple, of low computational cost". The real dataset in Figs 12–13 has N = 163 neurons, and no timing is reported for it.

**Null and significance testing (sec. 2.5, p. 9).** They consider an analytical null and reject it:
> "If all coincident spike pairs would be independent, the probability distribution would be strictly binomial and we could calculate this likelihood analytically. However, the pairwise spike orders in coincident events involving multiple spike trains are not independent from each other, and so instead we estimate the likelihood numerically using a set of carefully constructed spike order surrogates."

- The surrogates keep each spike's SPIKE-synchronization value and swap leader and follower within randomly chosen coincident pairs. The number of swaps equals the number of coincident spikes, doubled for the first surrogate.
- "For each spike train surrogate we repeat exactly the same optimization procedure in the spike train permutation space that is done for the original dataset." This means the annealing runs 20 times per test: once for the data and 19 times for the surrogates. That is probably the main practical cost.
- Significance is declared when the data exceed all 19 surrogates (p* = 0.05). A z-score, z = (x − μ)/σ, is reported as a secondary indicator.
- To test a hypothesised order Fu, with no optimisation, they compare it against random permutations of the trains.

**Finite-size bias (sec. 3.1, p. 10–11).** They acknowledge the bias qualitatively but give no formula and no correction:
> "The fact that both of these values are non-zero is due to the finite size effect caused by the limited number of spikes. For more and more spike trains and/or spikes the expectation value even for the sorted case would converge towards zero."

The Fig. 9 caption says that for 20 Poisson trains "Both before and after sorting the synfire indicator is very close to zero."

**Comparing datasets with different spike counts (sec. 3.1, p. 11–12).** This is the passage that matters most for our finding (b):
> "the synfire indicator is strongly influenced by the statistics of the dataset and thus is in itself not sufficient to reliably compare two datasets with widely different number of spike trains and spikes. The surrogate analysis, on the other hand, can be used to compare datasets of different size since by preserving the spike numbers in the surrogates it explicitly takes the statistics of each dataset into account."

Their remedy is the surrogate z-score or p-value, not a corrected F. In Fig. 10, a mixed dataset has almost the same Fs as the Poisson dataset of Fig. 9, yet one is highly significant and the other is not.

**Data-handling details.**
- Appendix A: one of five calcium-imaging datasets was dropped because "the surrogate analysis ... proved to be unfeasible due to its excessive density of spontaneous activity." The paper does not say whether the obstacle was compute or the method.
- In sec. 3.2 the analysis is restricted to spikes with SPIKE-synchronization ≥ 0.7, which gives a mean ~110% increase in Fs.

**Closed form for one template.** None. Nothing like (2/π)·arctan(spread/jitter) or any other relation between F and jitter appears.

## 2. Mulansky & Kreuz 2016, PySpike (*SoftwareX*)

The paper predates the spike-order code. Its only mention is future work: "Current work is focused on the development of a spike order indicator ... A preliminary Python implementation already exists and will become part of an official PySpike release in the near future."

Its runtime figures concern the symmetric measures only: with the Cython backend, M = 1000 trains of ~500 spikes take 10–20 s, and cost scales linearly in spikes and quadratically in trains. It says nothing on sorting or a null.

**PySpike code (GitHub master).** This is what the annealing actually does.
- `optimal_spike_train_sorting` and `_optimal_spike_train_sorting_from_matrix` have the docstrings "optimize the order using simulated annealing" and "Finds the best sorting via simulated annealing".
- The start is the identity permutation, `p = np.arange(N)`.
- The schedule is T_start = 2·max(D), T_end = 1e-5·T_start, and cooling α = 0.9. That gives about 110 temperature levels.
- At each level the loop runs `while iterations < 100*N and succ_iter < 10*N`.
- Each move is a random swap of adjacent trains, with ΔA = −2·D[p_i, p_{i+1}] and Metropolis acceptance.
- It stops early if a temperature level accepts no swaps.
- The routine requires the Cython module and raises `NotImplementedError` without it.

So the annealing makes at most ~11,000·N proposals, each costing O(1). In compiled code it should not be slow. If our F pipeline is slow, the likely causes are:
- building the D matrix, which costs O(N²·spikes);
- the pure-Python path;
- or the 19× repetition over surrogates.

This is my inference from the code; I did not run it.

There is a second problem. With only adjacent swaps, a cold start from an arbitrary order, and a cooling that is fairly fast at α = 0.9 for large N, the search is not guaranteed to reach the optimum. A Borda start would be a natural improvement. The README says spike-order was added in v0.6.0 and that the latest version is 0.8.0 ("Adaptive and Rate Independent algorithms"). There is no sign of a different sorter.

## 3. Kreuz et al. 2022, *J Neurosci Methods* 381:109703 (arXiv 2205.09855)

- **Sorting.** Done exactly as in 2017: "The optimization procedure that we use to find the best spike train order is again based on simulated annealing (details can be found in [26]). While this sorting is not necessary for the correction itself, it renders the resulting rasterplots more intuitive and easier to read." (sec. 3.2). Here the sort is cosmetic.
- **Where annealing is justified, it is for the latency shifts, not the sort** (sec. 3.1): "simulated annealing, in contrast to a steepest descent (or 'greedy') algorithm, has the ability to recover from local (but non-global) minima." The search space there is continuous shifts, which "in principle ... is infinitely large".
- **The fast alternative is also for latency.** The "direct shift" uses only the first row of the spike-time-difference matrix: "while the shift cost is very fast to calculate, in general it gives only suboptimal results" (sec. 4.1).
- **Null and bias.** For pure Poisson trains (N = 10, ~9 spikes each), F "due to remaining random coincidences and persistent random order, respectively, gets quite close to but does not reach zero" (sec. 4.1, Fig. 4A). This is acknowledged and not corrected. The paper notes that C (SPIKE-sync) is an upper bound on F. F is then used across 260 recordings as an applicability criterion for latency correction, with no adjustment for spike count.
- **Runtime of the sort.** Not reported.

## 4. Mariani et al. 2025, *J Neurosci Methods* 416:110378 (arXiv 2410.15018)

- **Sorting.** Not addressed. "In this article the initial spike trains will always already be sorted from leader to follower." (sec. 3.2). The Synfire Indicator appears only as a descriptive quantity. Its definition (App. C, eq. C.7) repeats the 2017 argmax with no method stated.
- **Speed concerns latency correction only.** Annealing for latency "usually takes several magnitude longer to calculate as the complexity of computation is of the order N²" (sec. 3.3). Their fast alternative is the "Extrapolation direct shift", which fills in the spike-time-difference matrix (STDM) by transitivity and then averages each row: s_n = (1/N)·Σ_m δ(m,n) (eq. 13).
  - That is a mean-row-score estimator for latencies. It is the continuous analogue of our Borda sort.
  - It "achieves almost the same performance" as reduced-matrix annealing.
- **Runtime (footnote 3).** "applied both simulated annealing and the extrapolation direct shift to an experimental dataset with 183 spike trains and an average number of 13 spikes each. Even using Matlab EXecutables (MEX) compilation to speed up simulated annealing it took 861.8 seconds, as compared to only 9.7 seconds for direct shift ... ~88-fold ... asymptotic ... 130.7."
  - The same section says: "Since simulated annealing is not feasible for datasets with such an elevated number of spike trains, we restrict ourselves to the much faster extrapolation direct shift."
  - These figures are for **latency** annealing, not order annealing. Still, they show the group abandoning annealing for a row-average method once N reaches ~180.
- **Null and bias for F.** None. The only expectation value given is C = 0.25 for Poisson SPIKE-synchronization.

## 5. Kreuz 2026 review, *Biol Cybern* 120:21 (arXiv 2510.07140)

- **Sorting.** "In [12] the sorting is performed using simulated annealing with switching any two spike train as the elementary operation and the Synfire Indicator as the cost function to be maximized." (sec. 3, SPIKE-Order). This **conflicts** with the 2017 paper, the 2020 chapter and the PySpike code, which all swap *neighbouring* trains only. It may be a slip, or cSPIKE may differ. This is worth asking.
- **Annealing vs greedy.** The text once more refers to latency correction: "Unlike greedy algorithms, simulated annealing usually does not get stuck in local minima". It also says annealing "comes with a large computational cost of order N²" and that "For very large datasets this high computational cost of simulated annealing can actually be an exclusion criterion" (sec. 4).
- **Significance.** "it is highly recommended to evaluate the statistical significance of the optimized Synfire Indicator Fs using a set of carefully constructed spike train surrogates (not shown here but fully explained and visualized in [12])." In the conclusion, analytical Poisson expectations are cited only for the three symmetric measures [24]; for SPIKE-order it refers to "the spike train surrogate analysis".
- **Open problems the review itself names (conclusion).**
  - "it is still necessary to explore in more detail the intertwined relationship between the sorting of spike trains (which is based on latencies as well) and the latency correction itself [14]".
  - It also calls for more work on "the effect of unreliability in data acquisition ... particularly in cases in which larger and larger amounts of spiking activity are inferred from large-scale calcium imaging."
- **Software.** It says SPIKY, PySpike and cSPIKE "will soon also include the various algorithms for latency correction". No new sorter is mentioned.
- **Null and bias for F.** None. No runtime is given for the sort.

## 6. Satuvuori, Malvestio & Kreuz 2020, book chapter (arXiv 2001.04406)

This chapter repeats the 2017 text almost word for word:
- the TSP and N! argument;
- annealing with neighbour swaps, starting from the unsorted order;
- the surrogate test with 19 surrogates, re-optimised each time.

It has nothing new on speed, alternatives or the null.

## 7. Cecchini et al. 2021, *PLoS Comput Biol* (wide-field calcium imaging; Kreuz is senior author)

- **How the sort was used.** Pixels are the "spike trains", and threshold crossings are the "spikes". Spikes "not coincident with spikes in at least three quarters of the other spike trains" were filtered out. Then "we used the scalar Synfire Indicator [23] to also sort the spike trains in the rasterplot from overall leader to overall follower" (p. 6).
- **The sort was not used for statistics.** The quantities tested were all per event: duration, angle and smoothness, the last two from an SVD of the per-event SPIKE-order map.
- The S2 Appendix says only "For details on the optimization procedure, please refer to [1]", meaning the 2017 paper.
- **No surrogate test of F, no null, no bias correction.** Few events were handled by the ≥3/4 coincidence filter and by working per event. They used cSPIKE (MATLAB + MEX). No runtime is reported.

## 8. Tomlinson et al. 2019, *Epilepsia* 60:898 (via PubMed/PMC, [doi:10.1111/epi.14720](https://doi.org/10.1111/epi.14720))

This is the closest prior art to our score sort. They say their method "was adapted from an algorithm introduced by Kreuz et al." (Discussion 4.2), but they do **not** anneal.
- **Degree Preference (DP).** Each electrode gets a "Degree Preference" from its counts of upstream versus downstream positions within activation sequences, scaled from +100 (always the leader) to −100 (always the terminal spike). This is a per-node net-lead score, essentially a Borda/Copeland-type score.
- **Expected order = rank by score.** "the 'expected' sequence of network activation was defined based on the rank order of Overall DPs" (Methods 2.11).
- **Per-sequence reproducibility.** Each sequence is scored against that order on a −1…+1 scale ("fraction of steps in the 'observed' sequence that followed the order of the 'expected' sequence"). The reproducibility index R is the median of these scores.
- **Null.** Spike times are shuffled between electrodes within each sequence, 1000 permutations.
- **Dependence on network size.** R correlated with node count (r = −0.75), a size dependence they note but do not correct.
- Networks had 7–25 nodes. The authors are from a clinical group, not Kreuz's group.

---

## Direct answer to Tony's question

**Does the Kreuz group have a fast, non-annealing sort?** No. In every paper (2017, 2020, 2022, 2025, 2026), in Cecchini 2021 and in the PySpike code, the order that maximises F is found by simulated annealing, starting from the input order and swapping adjacent trains. None of these sources mentions a ranking initialisation, Borda/Copeland scores, a greedy or insertion search, or sorting by mean SPIKE-order.

The nearest things to our approach are:
- Mariani et al. 2025's "extrapolation direct shift", a row-average of the spike-time-difference matrix (STDM). It replaces annealing, but for **latency correction**, not for order.
- Tomlinson et al. 2019 (not Kreuz's group), which ranked electrodes by a net upstream/downstream score in a Kreuz-inspired analysis. They did not compare it with the F-optimal order.

**Do they have an analytical null or bias correction?** No. The 2017 paper:
- says the finite-size effect makes Poisson Fs > 0;
- explicitly considered and rejected an analytical binomial null because orders within multi-train events are dependent;
- states that F cannot be compared across datasets with very different numbers of trains or spikes.

Its remedy is the 19-surrogate test, with annealing re-run on each surrogate and a z-score reported. No source gives a c/√n̄ law, an expected Fs under no order, a corrected F, or a closed form such as (2/π)·arctan(spread/jitter). Our findings (b) and (c) appear new. Finding (b) agrees with their qualitative statement and gives it a quantitative form.

**Have they explained why they anneal rather than rank?** Only by the 2017 argument: the problem is like the TSP, there are N! permutations, brute force is infeasible, so use annealing or parallel tempering. The "escapes local minima, unlike greedy" argument appears only for latency correction (2022, 2025, 2026). They never consider that F is a linear function of a pairwise antisymmetric matrix, so that row-sum ranking is a natural constructive start. Nor do they report runtime or the optimality gap of the annealer.

Their own trajectory points our way. By 2025–26 they call annealing "an exclusion criterion" for large N and switch to a row-averaging direct method, though only for latency.

## Open points an email to Kreuz could settle

1. Did they ever try ranking by row sum of D (net lead count, Borda/Copeland) or by mean SPIKE-order, either as the sorter or as the annealer's starting order? If so, how close did it get to the annealed Fs?
2. Elementary move: is it swaps of neighbouring trains (2017 paper, 2020 chapter, PySpike) or swaps of any two trains (2026 review)? Does cSPIKE differ from PySpike in moves or cooling schedule? Do they know how often the annealer fails to reach the optimum on real data?
3. Do they have runtime figures for the order sort and the 19-surrogate test at N ≈ 100–200? Was the dropped dense dataset in the 2017 Appendix A a compute limit or a method limit?
4. Have they derived, or seen, the expected Fs under no order as a function of coincidences per pair, a finite-size or bias correction, or a recommended normalisation (e.g. surrogate z-score) for comparing recordings with different event counts? Would they endorse (Fs − E0[Fs]) / (1 − E0[Fs]) or the z-score as the comparable quantity?
5. Is a closed-form F for a single latency template with Gaussian jitter (the arctan form) known to them, or consistent with their simulations?
6. Are there plans or unpublished code for a faster sorter in PySpike or cSPIKE, given that the review says the packages "will soon" add the latency algorithms? Would they accept a Borda start plus insertion search as a contribution?
7. The 2026 review flags "the intertwined relationship between the sorting of spike trains ... and the latency correction" as open. Do they see the latency row-average and an order score as the same estimator, and does that settle the sort?
