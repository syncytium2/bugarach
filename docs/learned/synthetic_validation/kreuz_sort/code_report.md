# Kreuz group code and materials: SPIKE-Order sorting, the Synfire Indicator F, nulls

Prepared for Tony DeFazio (bugarach), 2026-10-24. This review was read-only. The downloads were made to a local scratch folder and are not kept in
the repository; they are public and can be fetched again:
- `pyspike_repo\`: git clone of github.com/mariomulansky/PySpike, master at f84efb3, v0.9.0, 2026-05-11.
- `pyspike_kevin_branch\`: export of the unmerged `origin/Kevin` branch, 2024.
- `cspike_zip\cSPIKE\`: cSPIKE v1.5, 2024-07-15, from thomaskreuz.org.
- `spiky_zip\SPIKY\`: SPIKY v3.1 beta, 2021-04-30.
- `papers\`: Kreuz 2017 NJP preprint (arXiv 1610.07986v4), the 2025/26 review (arXiv 2510.07140v2), and SPIKY docs as text.

The comparison script is my own re-implementation; I did not run any downloaded code. It is kept
beside this report as `compare.py`, with a multi-seed variant `compare2.py`. Their printed
output was not saved; rerun them to reproduce the numbers below.

---

## 1. PySpike, master (mariomulansky/PySpike)

### Sorting entry points
- `pyspike/spike_directionality.py` L511–535, `optimal_spike_train_sorting`:
  - It builds `D = spike_directionality_matrix(..., normalize=False)` and calls `_optimal_spike_train_sorting_from_matrix(D)`.
  - The docstring says it optimises "using simulated annealing" and cites the NJP paper.
- The same file, L474–505, `_optimal_spike_train_sorting_from_matrix`:
  - It sets `T_start = 2*np.max(D)`, `T_end = 1E-5*T_start` and `alpha = 0.9` (L490–492).
  - If Cython is missing, it raises `NotImplementedError("PySpike with Cython required for computing spike train sorting!")` (L494–498). So there is **no pure-Python sort and no fallback.**
- `pyspike/cython/cython_simulated_annealing.pyx` L44–82, `sim_ann_cython`:
  - **Start: the identity permutation `p = np.arange(N)` (L48).** This is the input order, not a random or smart start.
  - **Move: swap neighbours only.** `ind1 = rand() % (N-1)`, `ind2 = ind1+1` (L64–68). The change is `delta_A = -2*D[p[ind1],p[ind2]]` (L69).
  - **Acceptance:** Metropolis, `delta_A > 0 or exp(delta_A/T) > U` (L70). A zero change is always accepted.
  - **Per temperature level:** up to `100*N` proposals, or stop after `10*N` accepted moves (L61).
  - **Cooling:** geometric, `T *= 0.9` (L77). Going from 2·max D down to 1e-5 of that takes about **110 levels** (ln 1e-5 / ln 0.9 ≈ 109.3).
  - **Stop:** at T_end, or after the first level with no accepted move (L78–80). That level is an adjacent-swap local optimum.
  - **Budget:** at most ≈ 1.1×10⁴·N proposals. Each proposal is O(1), so the annealer costs O(N) per level and is cheap in Cython.
  - The code keeps **no best-so-far**; it returns the final state.
  - The RNG is **C `rand()` and is never seeded** (`grep srand/seed`: nothing). Results are deterministic from run to run, and `np.random.seed` does not affect them.
  - It returns `(p, A, total_iter)`. **A is the unnormalised upper-triangle sum, not F**, even though the docstrings call it "synfire indicator".
- **History.** The first version is commit 29e5047 (2015-08-12, Mulansky), in pure Python with the same schedule and identity start. It was ported to Cython in b9850d8 (2015-10-10) "for performance". It was merged to master through PR #39 (2018-09-20), which has an empty description and no comments. The schedule has not changed since 2015.
- **No rank, Borda, greedy or insertion sort exists anywhere** in master or in any branch. I grepped the repo and the full history.
- **Docs and examples** (`doc/tutorial.rst` L289–355, `examples/spike_train_order.py`): 20 Poisson trains → `optimal_spike_train_sorting`. There are no runtime figures, no justification for annealing and no null.

### Is the objective exactly a sum over ordered pairs of D?
**Yes.** Nothing makes a direct ranking inappropriate in principle.

- **D is built pairwise and is exactly antisymmetric by construction.**
  - `spike_directionality_matrix` L198–205 sets `D[i,j]=d; D[j,i]=-d`.
  - `d` = (# coincidences where i leads j) − (# where j leads i), from `cython_directionality.pyx`.
  - Each D_ij depends only on the spikes of trains i and j. The coincidence window τ is the bivariate adaptive window from the pair's own ISIs (`get_tau`). The `MRTS` threshold is a global constant fixed before the loop.
  - So D is a fixed weighted tournament and does not depend on the order.
- **The normalisation does not depend on the order.**
  - F = 2·Σ_{n<m} D_{π(n)π(m)} / ((N−1)·M), where M is the total spike count. This is Kreuz 2017, Eq. 14.
  - `test/test_directionality.py` ~L93–97 asserts `F = sum(triu(D))/num_spikes` (N=3).
  - `spike_train_order_multi` L456–467 divides Σe by Σm. Σm is the sum over pairs of (n_i + n_j) = (N−1)·M, a constant.
  - Maximising F therefore means **maximising Σ_{i before j} D_ij**. This is the **linear ordering problem**, the weighted feedback-arc-set problem on a tournament.
- **Consequences.**
  - The row sum r_i = Σ_j D_ij is the net lead count: the Borda score when D is weighted, the Copeland score when sign(D) is used. Sorting by r_i is the natural O(N²) first guess.
  - For tournaments, sorting by score is a constant-factor (5-) approximation for feedback arc set (Coppersmith, Fleischer and Rudra).
  - The problem is NP-hard in general, so an exact search is justified only for the last few percent.
  - None of the Kreuz materials mention the linear ordering problem or feedback arc set. The 2017 paper calls the problem "similar to the travelling salesman problem".
- **The only caveats I found are about the definition, not the ranking.**
  - D weights pairs by their raw coincidence counts, so high-rate pairs dominate. Borda inherits exactly the same weighting, so the two agree.
  - D changes with `max_tau`, which has been inert since 0.8.0 (Tony's PR #89). That changes the input, not the structure of the problem.
  - Minor bug: `spike_train_order_multi` L464 tests `if m == 0.0`, the last pair's m, instead of `m_total`.

### Issues, PRs and discussions
- There are 89 issues and PRs (`gh` listing). **None is about sorting speed, the annealer or the Synfire Indicator null.** Discussions are disabled (HTTP 410).
- Only tangential threads exist:
  - #13 (2016): a user asks for directionality; Mulansky points to the NJP paper and SPIKY.
  - #83: Kreuz answers a question about Poisson expectation values for the distances, not F.
  - #23: delay estimation.
- PR #89 (Tony, open): `max_tau` cap. It affects D and therefore `optimal_spike_train_sorting`, but not the algorithm.
- PR #85 (open): packaging only.

---

## 2. PySpike, unmerged `origin/Kevin` branch (KevinLin19, Apr–Aug 2024)

This branch is a port of the MATLAB tools in progress. It renames `spike_directionality` to `spike_order`.

- **The sort is unchanged.** `pyspike/spike_order.py` L588–614 is identical, including the identity start and the 2·max/1e-5/0.9 schedule. `cython_simulated_annealing.pyx` L44–82 is unchanged.
- **The surrogate test for F exists only here, not on master.** It is a port of Kreuz 2017 §2.4.
  - `pyspike/generate_surrogate.py` L5–69 `generate_surro`, and `Spike_Order_surro` L71–135. The Cython version is `pyspike/cython/cython_generate_surrogate.pyx` L36–92.
  - Each surrogate swaps the leader and follower labels inside randomly chosen coincidences, keeping every spike's time and its SPIKE-Sync value. It propagates the swap to the other coincidences that share those spikes, and rejects a swap if two coincidences of the same pair would share a spike.
  - It then **re-runs the annealer on each surrogate** (`_optimal_spike_train_sorting_from_matrix`) and returns the normalised F_s per surrogate. So the null is a null for the *maximised* F, and that absorbs the finite-size bias empirically.
  - **Port bugs.** The Python version aliases `indies2 = indies1` (L93), so the rollback after a rejected swap does nothing; the Cython version uses `.copy()`. It halves the swap count at `suc==0` (L48–49), whereas MATLAB halves at `suc==2`.
- **Latency correction**, which matches Kreuz 2022 and Mariani 2025, is in `pyspike/latency_correction.py`:
  - `Spike_time_difference_matrix` L6;
  - `latency_correction_extrapol` L91, the Extrapolation fast direct shift with a stop diagonal;
  - `latency_correction_intrapol` L131;
  - `sim_ann_latency_correction` L168, which also appears in the branch's `cython_simulated_annealing.pyx`.
  - The annealing here is over **time shifts** (T 1→1e-4, α 0.9, 100N/10N per level), not over orderings. **It does not touch the sort.** The direct-shift methods assume the trains are already in leader→follower order, because the stop diagonal is defined on the order.

---

## 3. cSPIKE v1.5 (MATLAB/MEX, Satuvuori and Kreuz)

Source: thomaskreuz.org/source-codes/cspike, zip at drive.google.com/file/d/1UQrsggj9MKXJqfVYKFuXOo9gws8XXOFE.

- `cSPIKEmex/Spike_train_order_sim_ann_MEX.c` L58–99 uses the **same algorithm**:
  - The start is the identity, `p[pc]=pc+1` (L74–76).
  - Moves are neighbour swaps; the change is −2·D(p[k−1],p[k]) (L82–83).
  - T0 = 2·max D, **T_end = T0/1e4** (≈ 88 levels), α = 0.9, 100N/10N per level, stop on a level with no accepted move.
  - It is seeded with `srand(time(NULL))`, so results vary from run to run.
- `SpikeTrainOrder/SpikeTrainOrderWithSurrogates.m`:
  - The default is 19 surrogates (L13–15), for p = 0.05.
  - It builds the antisymmetric matrix from `sum(sto_profs,2)/2` (L74–77), then calls the annealer once on the data (L79).
  - Surrogates come from `SPIKY_f_generate_surros_np_cSPIKE.m`, whose internal function name is `f_generate_spike_order_surros`. It re-anneals every surrogate (L39). The first surrogate gets `num_spikes` swaps and later ones half that (L17, L22–23).
- `f_generate_spike_order_surros.m` has a pure-MATLAB fallback for the swap loop.
- The documentation page (`/cspike/documentation`) says nothing about the sorting algorithm, runtime or null. The cSPIKE page says only that 19 surrogates are the default "for 5% confidence".
- `PopulationAnalysis/ALGO_Annealing.m`, `ALGO_Brute.m` and `ALGO_Bottom.m` are a separate population-coding algorithm (Satuvuori), not spike-train ordering.

## 4. SPIKY v3.1 beta (2021)

Source: drive.google.com/file/d/1T6B_BSWmr6aPxi7SUUiBhHurt1vqjz50.

- `SPIKY_m_functions/SPIKY_f_simann_sort.m` L1–34 is the pure-MATLAB annealer. It starts from the identity `p=1:N` (L7), with T0 = 2·max D, T_end = 1e-5·T0 and α = 0.9.
- The MEX versions are `SPIKY_MEX/SPIKE_order_sim_ann_MEX.c` and the `_alt.c` variant. They are identical except for the integer RNG, and both use T_end = T0/1e4.
- The callers are `SPIKY_m_files/SPIKY_Synfire_plot.m` L97–101 and the surrogate files (`SPIKY_Synfire_f_generate_surros.m` L197–200, `SPIKY_f_generate_surros.m` L200–203, `SPIKY_f_generate_surros_np.m` L104–105).
- **SPIKY already computes the Borda score and does not use it to sort.**
  - `SPIKY_Synfire_plot.m` L104 has `st_order=sum(ori_results.SPIKE_order.matrix_cum,2);`, the row sum (net lead count) per train.
  - It is only permuted (L124, `sorted_st_order=st_order(st_indy)`).
  - It feeds a commented-out colour line in `SPIKY_Synfire_subplot.m` L127.
  - It is never used as the annealer's starting point or as an alternative ranking.
- The SPIKY FAQ, Readme and loop docs in `SPIKY_Documentation/*.pdf` contain nothing on sorting, annealing, runtime or an F null. They cover only generic SPIKY_loop_surro significance.
- github.com/thomaskreuz/SPIKY dates from 2014, before SPIKE-Order, and is not relevant.

---

## 5. Papers and the website

### Kreuz et al. 2017, NJP 19:043028 (arXiv 1610.07986)
- **Why they anneal**, §2.3 (k2.txt L594, L718), quoted: "The complexity of the problem to find the optimal Spike Train Order is similar to the well-known travelling salesman problem … For N spike trains there are N! permutations … brute-force methods … are not feasible. Instead, one has to make use of methods such as parallel tempering … or simulated annealing … Here we choose simulated annealing … We start with the Fu-value from the unsorted permutation and then visit nearby permutations using the fundamental move of exchanging two neighboring spike trains … ΔF = −2D(k,k+1). All moves with positive ΔF are accepted while the likelihood of accepting moves with negative ΔF is decreased … according to a standard slow cooling scheme."
  - **No ranking or greedy method is considered or compared.**
  - **No runtime is given.** The abstract claims "low computational cost".
- **The null**, §2.4 (L765–773):
  - "If all coincident spike pairs would be independent, the probability distribution would be strictly binomial and we could calculate this likelihood analytically. However, the pairwise spike orders in coincident events involving multiple spike trains are not independent … so instead we estimate the likelihood numerically using a set of carefully constructed spike order surrogates."
  - Each surrogate is re-optimised: "we repeat exactly the same optimization procedure". The test reports p = 1/(s+1) with s = 19, plus a z-score.
  - For a pre-specified order, F_u is tested against random permutations.
  - The paper says Poisson trains give F_s ≈ 0 when "sufficiently long". **There is no analytical bias formula or correction.**
- "More efficient to sort … based on a pairwise analysis" (L549–555) refers to computing F from the pair matrix instead of the profile. It is not a ranking.

### Kreuz review, arXiv 2510.07140v2 (rev. 28 Jul 2026)
- §3: "In [12] the sorting is performed using simulated annealing with switching any two spike train as the elementary operation". This contradicts all three codebases, which swap **neighbours** only.
- It recommends the surrogate test of [12]. It mentions Poisson expectation values only for the distances (ref [24]), not for F.
- Open problems: "it is still necessary to explore in more detail the intertwined relationship between the sorting of spike trains (which is based on latencies as well) and the latency correction itself [14]."

### Mariani, Senocrate, …, Kreuz 2025, arXiv 2410.15018
- This is fast latency correction: Extrapolation direct shift, plus reduced-matrix annealing over **time shifts**, iterated with rematching.
- Runtime: annealing over shifts (MEX) **861.8 s versus 9.7 s** for the direct shift on their large set, about 88× faster. The asymptotic speed-up is 130.7×; both are O(N²).
- **It does not change the sort.** §3.2 assumes "the initial spike trains will always already be sorted from leader to follower". The paper says code will go into SPIKY, PySpike and cSPIKE; the Python form is on the Kevin branch (§2 above).

### Website (thomaskreuz.org)
- There are pages for SPIKY, PySpike, cSPIKE (with documentation, SpikeTrainSet and Subpopulations) and Directionality.
- I found no tutorial, slides or FAQ about sorting speed, alternatives or an F null. The only relevant items are "19 surrogates for 5%" and "MEX for speed".

### Other GitHub accounts
- **mariomulansky:** PySpike only; the other repos are unrelated.
- **thomaskreuz:** old SPIKY (2014) and SPIKY-paper.
- **KevinLin19:** nothing relevant outside the PySpike branch.
- **Satuvuori and Mariani:** no public repos found.
- **Code search** for `sim_ann_cython`, `SpikeTrainOrderWithSurrogates` and `optimal_spike_train_sorting` finds only vendored copies in third-party repos.

---

## 6. Check with my own re-implementation (not the downloaded code)

- **Setup.** I re-implemented PySpike's schedule exactly: identity start, neighbour swaps, T0 = 2 max D, T_end = 1e-5·T0, α = 0.9, 100N tries or 10N successes per level, stop on zero acceptances.
- **Synthetic D.** Each pair gets Poisson(40) coincidences, and P(lead) = 0.5 ± signal according to a hidden order. The input order is shuffled.
- **Result.** Values are A = Σ upper triangle (∝ F); "ins" means the insertion search runs to a local optimum.

| N | signal | anneal | Borda | Borda+ins | anneal+ins |
|---|---|---|---|---|---|
| 30 | 0.3 | 10626 | 10396 | 10626 | 10626 |
| 60 | 0.1 | 14210 | 13072 | 14210 | 14210 |
| 100 | 0.05 (4 seeds) | 14.0–16.4k | 17.2–18.2k | 20.0–20.7k | 20.0–20.8k |
| 200 | 0.03 (3 seeds) | 15.4–19.7k | 41.6–41.9k | 50.1–50.7k | 50.0–50.4k |
| 200 | 0 (null, 3 seeds) | 6.3–8.6k | 10.5–11.4k | 21.4–22.3k | 21.6–22.0k |

- **For N ≤ 60** the published schedule matches Borda followed by insertion.
- **For N ≥ 100 it under-converges badly.** It finishes below plain Borda, and at N = 200 it reaches only about 40% of the Borda-plus-insertion objective.
- **Cause.** The run ends at an adjacent-swap local optimum after ~8.7×10³·N proposals, and long-range moves need O(N²) neighbour swaps.
- **Null case.** The F_s it reports is about one third of what a better optimiser finds. Surrogate nulls built with the same weak optimiser are biased the same way. The significance test stays roughly self-consistent, but the absolute F_s values are optimiser-dependent.
- This is synthetic and indicative only; it should be confirmed on real D matrices.

---

## 7. Direct answer to Tony

1. **Fast sort?** No. Every Kreuz-group implementation sorts with the same 2015 simulated annealer: PySpike master and the 2024 branch, cSPIKE v1.5, and SPIKY v3.1 in MATLAB and MEX.
   - It starts from the input (identity) order, uses only neighbour swaps, and runs a fixed geometric schedule.
   - There is no rank, Borda, Copeland, greedy or insertion method, and no smart start.
   - The nearest thing is SPIKY's `st_order = sum(matrix_cum,2)` (`SPIKY_Synfire_plot.m` L104). That is exactly our net-lead score, computed and then unused.
2. **Analytical null or bias correction?** No. NJP 2017 §2.4 explicitly declines a binomial null because coincidences in multi-train events are not independent.
   - They use 19 "spike-order surrogates" that swap leader and follower labels, each re-annealed. This handles the finite-size bias of F_s implicitly, as a null for the maximum.
   - There is no c/√(coincidences) formula or analytical correction anywhere. The 2017 paper and the 2026 review state only that long Poisson trains give F_s ≈ 0.
   - Python surrogate code exists only on an unmerged PySpike branch, and it has bugs.
3. **Why anneal instead of rank?** The only stated rationale is the NJP 2017 sentence: "similar to the travelling salesman problem … N! permutations … not feasible … one has to make use of methods such as parallel tempering or simulated annealing".
   - They never relate the problem to the linear ordering or feedback-arc-set problem, and never mention score sorting.
   - Nothing in the objective makes a ranking inappropriate. D is pairwise, exactly antisymmetric and fixed, and the normaliser (N−1)M does not depend on the order. So F_s is exactly the linear-ordering objective on D, and the Borda sort is the natural first step, refined by insertion or exact methods.
   - Their annealer is cheap in absolute terms, at most ~10⁴·N O(1) steps. In Cython it is not the bottleneck; computing D and the 19 re-annealed surrogates (in MATLAB) are more likely what made it feel slow.
   - On synthetic tests the fixed schedule under-converges for N ≳ 100 and does worse than a plain Borda sort.

## 8. Open points a short email to Kreuz could settle
1. Did they ever try score (row-sum or Borda) sorting, or seed the annealer with it? SPIKY computes `st_order` but does not use it. Was annealing chosen for a reason beyond the TSP analogy, such as ties or spike trains with no coincidences?
2. Are they aware that the problem is exactly the linear ordering problem, given that D is pairwise, antisymmetric and has an order-independent normaliser? Do they see any case, such as adaptive τ or MRTS, where D_ij would depend on other trains?
3. Have they checked convergence of the 2·max D → 1e-5 (or 1e-4), α = 0.9, neighbour-swap schedule for N ≳ 100? Have they compared it with restarts or exact solutions? Should the Fs values in published large-N results (e.g. N = 140 El Niño) be taken as lower bounds?
4. The 2026 review says "switching any two spike trains", but the code swaps neighbours only. Which is intended?
5. Do they have, or would they accept, an analytical expectation or bias for F_s under the null, i.e. how it scales with coincidences per pair? Do they consider the re-annealed surrogate null a sufficient bias correction? Should surrogates and data share the same optimiser and starting point?
6. What is the status of the PySpike Kevin branch (surrogates and latency correction)? Note its `indies2 = indies1` aliasing bug and the swap-count difference from MATLAB. Would they welcome a PR adding a Borda/insertion sort as the default or as the annealer's starting point? This could go alongside PR #89.
7. How do they see the interplay between sorting and latency correction (their own stated open problem)? Should the trains be sorted before or after the shift alignment?
