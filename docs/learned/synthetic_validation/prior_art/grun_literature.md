# Prior art in the Grün group for window sharing, event-spacing correction, joint fit and order indicator

Literature check, October 2026. Scope: Sonja Grün's group (RIKEN BSI, Jülich INM-6/IAS-6) and coworkers (Aertsen, Diesmann, Rotter, Staude, Pipa, Torre, Quaglio, Stella, Denker, Louis, Borgelt, Pazienti, Gerstein, Palm, G. Schneider).

## Items checked

1. **Window sharing.** One event's n participants have Gaussian onset jitter σ. The share of events whose n onsets all fall in one counting window of width w is g_n(w,σ) = E[(1 − R_n/w)+], where R_n is the range of the onsets. From the pair and triple factorial cumulants (f2, f3), the number of participants per event is k̂ = 2 + (k−2)·g3/g2.
2. **At-most-one-event term.** It corrects the cumulants when events are held at least 20 s apart rather than placed by a Poisson process.
3. **Joint fit.** Jitter, participants per event and event rate are fitted together from f2 and f3 at w = 1, 2 and 4 s.
4. **Order indicator.** D_ij is the net lead sign of cell i over cell j across their shared events. Cells are ranked by the row sums of D (a Borda count, O(N²), with no search). F is the net agreement as a share of co-participations. With one latency template, F = (2/π)·arctan(spread/jitter). With no order, F has a finite-size bias of about c/√n̄. With M templates the signal falls as 1/√M.

## How much of each paper we read

| Paper | Read |
|---|---|
| Grün, Diesmann, Grammont, Riehle & Aertsen 1999, J Neurosci Methods 94:67–79 | **Full text** (author-hosted PDF) |
| Grün, Abeles & Diesmann 2008, LNCS 5286:96–114 | **Full text** |
| Louis & Grün 2009, BMC Neurosci 10(Suppl 1):P253 (CNS*2009 poster abstract) | **Full text** (2 pages) |
| Louis, Borgelt & Grün 2010, Neural Netw 23(6):705–712 | **Abstract only.** The paper is paywalled and we found no preprint or author copy. Its content is described below from the 2009 poster and from the 2018 review that summarizes it. |
| Grün, Diesmann & Aertsen 2002, Neural Comput 14:43–80 (UE I) | Full text, searched by keyword |
| Grün, Riehle, Aertsen & Diesmann 2003, Nova Acta Leopoldina 332:189–206 | Full text, searched by keyword |
| Grün, Diesmann & Aertsen 2010, "Unitary event analysis", chapter in *Analysis of Parallel Spike Trains* | Full text, searched by keyword |
| Staude, Rotter & Grün 2010, J Comput Neurosci 29:327–350 (CuBIC) | Full text (PMC), searched by keyword |
| Staude, Grün & Rotter 2010, Front Comput Neurosci 4:16 | Abstract |
| Staude, Rotter & Grün 2008, Neural Comput 20:1973 | Abstract |
| Ehm, Staude & Rotter 2007, Electron J Stat 1:473–495 (empirical de-Poissonization) | Full text (arXiv 0711.1965), searched by keyword |
| Pazienti, Maldonado, Diesmann & Grün 2008, Brain Res 1225:39–46 | Abstract |
| Schrader, Grün, Diesmann & Gerstein 2008, J Neurophysiol 100:2165 | Full text (PMC) |
| Gerstein, Williams, Diesmann, Grün & Trengove 2012, J Neurosci Methods 206:54–64 | Abstract only |
| Torre, Picado-Muiño, Denker, Borgelt & Grün 2013, Front Comput Neurosci 7:132 (SPADE, synchronous patterns) | Full text (PMC) |
| Torre, Canova, Denker, Gerstein, Helias & Grün 2016, PLoS Comput Biol 12:e1004939 (ASSET) | Full text (PMC) |
| Quaglio, Yegenoglu, Torre, Endres & Grün 2017, Front Comput Neurosci 11:41 (SPADE, spatio-temporal patterns) | Full text (PMC) |
| Quaglio, Rostami, Torre & Grün 2018, Biol Cybern 112:57 (review of methods) | Full text (PMC) |
| Stella, Quaglio, Torre & Grün 2019, BioSystems 185:104022 (3d-SPADE) | Not opened. Its method is described here from Stella et al. 2022. |
| Stella, Bouss, Palm & Grün 2022, eNeuro 9:ENEURO.0505-21.2022 (surrogates) | Full text (PMC) |
| Palm, Paoletti, Ito, Stella & Grün 2026, Biol Cybern 120 ("A quality measure for repeating multiple-unit spike patterns") | Full text (PMC), searched by keyword |
| Gutzen et al. 2024, Cell Rep Methods (Cobrawap slow-wave pipeline; Denker, Grün coauthors) | Full text (PMC), searched by keyword |
| Schneider, Havenith & Nikolić 2006, Neural Comput 18:2387 (G. Schneider coauthored with Grün in 2003) | Abstract |
| Havenith et al. 2011, J Neurosci 31:8570 (applies the Schneider 2006 method) | Full text (PMC), Methods section |

---

## A. Window sharing, event spacing and the joint fit (items 1–3)

### Grün et al. 1999, J Neurosci Methods 94:67–79: "Detecting unitary events without discretization of time" (full text)

- **Model.** Two neurons with Poisson background. Injected coincidences arrive at rate u_c. One spike of the pair is a "jittered replica" of the other, displaced *uniformly* over ±s time steps: "The probability to be placed at any one of the 2s+1 possible positions is p_s = 1/(2s+1)."
- **Window sharing for pairs.** They derive the **"fission" probability F(s,b)**: the chance that a fixed grid of disjoint bins of width b splits a jittered pair (Eq. 5, Fig. 3). Detected injected coincidences are then n_c(s,b) = p_c (1 − F(s,b)) N(b) (Eq. 6). Here 1 − F(s,b) is our g_2 for one fixed spike and one uniformly jittered spike on a random grid phase.
- **Counts across bin widths.** The analytical observed count n(s,b) = injected + background (Eq. 11) is plotted against b = 1…11 ms for jitter s = 0…5 ms (Fig. 4) and matches simulation. Eq. 10 subtracts the bins "already occupied" by injected coincidences from the background count. This is a minor occupancy correction; it says nothing about how events are spaced.
- **Null.** Analytical (Poisson / binomial joint-surprise).
- **Finite-size or bias treatment.** None beyond the analytical null.
- **How close.**
  - Item 1: done for n = 2 with uniform discrete jitter. Not done for n ≥ 3 or for Gaussian jitter.
  - Item 3: the forward model of counts against window width is there, but nothing is fitted.
  - Item 2: absent.

### Grün, Diesmann & Aertsen 2002 (UE I) and Grün et al. 2003 (Nova Acta Leopoldina) (full text, searched)

- Both repeat the 1999 framework. Jitter is uniform: "the difference in spike times is uniformly distributed within the chosen jitter range."
- Detectability is studied as a function of bin size. Nothing new for items 1–3.

### Grün, Abeles & Diesmann 2008, LNCS 5286:96–114 (full text)

- **Model.** SIP_m / MIP_m mother-process models (after Kuhn et al. 2003), written in discrete time as Bernoulli processes. The mother process is Poisson, with insertion rate ε.
- **Measure.** The complexity distribution (the amplitude distribution of the population histogram), compared with a spike-randomization control.
- **Jitter (Section 5.4).** "For the sake of simplicity, here we decide for a rectangular distribution of spike times." Each spike is displaced uniformly within ±j/2 (j = 5h). The bin width is then varied from w = 1 to 20 ms.
- **Analytical results.** Binomial forms for the independent part and the dependent part, for example P_SIP,dep(ξ, w) = B(ξ − m, (N − m)w, p), with mean complexity m + w(N − m)p.
- **Jitter enters only qualitatively.** "If coincidences are jittered, only part of the coincidences are detected for wh < j … From wh = j on, all inserted coincidences are detected (neglecting debris due to exclusive binning; Grün et al., 1999)."
- **Estimating precision.** The proposed estimator is a heuristic: "This change of slope at w = j may be used as an indicator for the precision of synchronization in the data."
- **Rate.** The injection rate is a model parameter but is never estimated.
- **Null.** Analytical binomial, or surrogates by spike-time randomization. No test statistic is defined; the authors defer one to cumulant methods (Staude et al.).
- **How close.**
  - Item 1: the paper explicitly *neglects* the exclusive-binning loss, which is exactly what g_n models. There is no n-spike window-sharing probability and no Gaussian jitter.
  - Item 3: partly. It shares our goal (read size and precision off population counts across window widths), but uses a slope-change heuristic rather than a fit, and estimates no rate.
  - Item 2: absent (Poisson mother process).

### Louis & Grün 2009, BMC Neurosci 10(Suppl 1):P253 (full text of the poster abstract)

- **Model.** Bernoulli mother process per group. Spikes are copied with probability p and jitter "j = ±3 ms" (discrete, uniform). The data are binned at w, and the spike counts are summed across neurons.
- **Analytical claim.** "we obtain a relatively simple analytical prediction for the complexity distribution in the case that the synchronous groups are non-overlapping, for arbitrary firing rates, jitter and bin width."
- **Estimator.** Follow the second maximum of (predicted − independent) across bin widths and locate "the change in slope of the position of the second maximum". In their example the estimate came out at 7 ms = 2|j|+1 and a size of 30.
- **How close.**
  - Item 1: very likely contains an n-spike analogue of g_n, but for *uniform discrete* jitter and Bernoulli background. The formula is not shown in the abstract.
  - Item 3: partly. Size and precision are inferred across bin widths, but by locating a slope change, not by a joint fit. There is no estimate of event rate.
  - Item 2: absent.

### Louis, Borgelt & Grün 2010, Neural Netw 23:705–712 (abstract only)

- **Abstract.** They "devise a method to reliably extract the size and temporal precision of synchronous groups of neurons, even in the presence of strong rate covariations."
- **The 2018 review's summary.** Confidence intervals come from surrogates ("allow to accept or reject the null hypothesis of independence"). "Varying the bin size enables to determine the temporal jitter inherent to the synchronous events."
- **What we cannot tell** without the full text:
  - whether the jitter is still uniform (the 2009 poster used uniform);
  - whether the estimator is a formal fit or the slope-change rule;
  - whether the event (mother-process) rate is estimated.
- **Most likely reading,** given the poster and the 2008 chapter: uniform jitter, a heuristic across bin widths, the rate treated as a nuisance parameter.
- **This is the closest prior work to items 1 and 3.**

### Pazienti, Maldonado, Diesmann & Grün 2008, Brain Res 1225:39–46 (abstract)

- They derive "how dithering interacts with temporally jittered coincidences": the probability of detecting a coincidence "characteristically decays with the applied dither interval".
- This relationship lets them determine the precision of synchronization "for a single setting of tolerated temporal spread."
- **How close.**
  - Item 1: partly, for pairs only. The analytical quantity is detection probability as a function of jitter and dither width.
  - Item 3: estimates precision only, at one window, with dither as the varied quantity.
  - Not n-way, not Gaussian (unknown from the abstract), no rate or size.

### Staude, Rotter & Grün 2010 (CuBIC), J Comput Neurosci 29:327 (full text, searched)

- **Model.** Compound Poisson process (CPP). The population count Z in bins of width h has cumulants equal to h·ν times moments of the amplitude distribution A, from κ_m[Y_l] = ν_l h. This is the zero-jitter version of our f2/f3 → participants identity. CuBIC tests the order of correlation from the first few cumulants.
- **Jitter is not modelled.** "if the events … were copied … with a temporal jitter that is small with respect to the bin size h, the correlations among the counting variables will hardly be affected". The authors "expect CuBIC to tolerate imprecise coincidences with small but realistic jitter". The sensitivity to jitter "remains to be assessed systematically."
- **Null.** Analytical, from cumulant bounds under a maximal order ξ. The analysis uses a single bin width.
- **How close.**
  - Item 1: the cumulant-to-size identity is there with g = 1. The jitter factor g3/g2 is absent.
  - Item 3: no fit across window widths, no jitter parameter.
  - Item 2: absent (Poisson carrier process).
- **Staude, Grün & Rotter 2010 (abstract).** A non-stationary CPP version, with no jitter.
- **Staude, Rotter & Grün 2008 (abstract).** Separates coordination from rate covariation; no window-sharing formula is apparent.

### Ehm, Staude & Rotter 2007, Electron J Stat 1:473 (full text, searched)

- **Model.** The population count is a compound Poisson process. The "jump measure" (event rate for each amplitude) is estimated by Fourier inversion of the empirical characteristic function at *one* bin width h.
- **Jitter.** Not modelled: "we assumed that the 'coordinated' spikes … occur strictly simultaneously … this would not hamper our theory to the degree to which the 'jitter' is small enough compared to the width h". They note a "conflict of interest between 'small bins' … and 'large bins' which are less affected by jittered patterns."
- **How close.**
  - Item 3: estimates event rate and size jointly (the rate for each amplitude), but with no jitter and one window.
  - Item 2: the Poisson carrier is assumed.

### Verdict on items 1–3

- **The window-sharing idea started in this group** (the 1999 "fission" probability). It was extended qualitatively to n spikes and multiple bin widths (2008, 2009, 2010).
- **What we did not find** anywhere in this group:
  - (a) the n-participant, Gaussian-jitter form g_n = E[(1 − R_n/w)+];
  - (b) its use to correct the factorial-cumulant size estimate, k̂ = 2 + (k−2)·g3/g2;
  - (c) a correction for minimum event spacing (every model uses a Poisson or Bernoulli mother process);
  - (d) a formal joint fit of jitter, size and rate across window widths.

---

## B. Sequence, order and synfire work (item 4 and the nulls)

### ASSET: Torre et al. 2016, PLoS Comput Biol (full text)

- **Method.** An intersection matrix I_ij counts the neurons active in both time bin i and bin j. Repeated sequences of synchronous events show up as diagonal structures. Each entry I_ij is mapped to a cumulative probability P_ij. A joint probability J_ij is computed for the l largest neighbours along the 45° direction, both are thresholded, and DBSCAN clusters the result.
- **Null: analytical.** "the null hypothesis H0 that the spike trains are independent and marginally Poisson". Each I_ij is a Poisson-binomial variable. Its exact pmf needs 2^N terms, so they use Le Cam's Poisson approximation with λ = Σ_k p_ij(k). A Monte Carlo alternative "yielded results comparable to the analytical approach, yet at a considerably higher computational cost."
- **Finite-size and multiple testing.** Handled by the two thresholds α1 and α2 plus DBSCAN. There is no analytical bias term for a summary statistic.
- **Order.** Detects repeated *sequences* (diagonals), so the forward direction is implicit. There is no per-pair lead sign, no global ranking of cells, and no measure of order strength.
- **Runtime.** "the evaluation of a single entry took about 10 ms on a single core … the evaluation of a full matrix J of 200 × 200 entries took on average less than 7 minutes." Also: "increasing the number of neurons to be analyzed does not increase the computational cost".
- **How close to item 4.** Same family (sequence detection with an analytical null), but a different object: it detects repeated time-bin pairs and does not order cells.

### Schrader, Grün, Diesmann & Gerstein 2008, J Neurophysiol (full text)

- **Method.** The ASSET precursor: an intersection matrix normalized either by the smaller set size or by cosine similarity, then filtered with a 45° filter.
- **Null.** None formal: "Direct significance testing is not necessary since … the short diagonal lines in the matrix" are visually distinct. Dithering is used to show that sequence structure is destroyed.
- **Runtime.** Their "pattern program" baseline needed "a minimum of 21 iterations … (original and 20 surrogates)".
- **How close to item 4.** It does not order cells and has no null for order.

### Gerstein, Williams, Diesmann, Grün & Trengove 2012, J Neurosci Methods 206:54 (abstract only)

- **Method.** Extends the intersection matrix to higher rates and noise and adds "two additional tools based on properties of repeating firing patterns". The authors stress that repeating patterns alone are "not enough to infer the presence of synfire chains".
- **Not checkable** without the full text: whether either tool orders neurons or uses pairwise lead/lag.

### SPADE: Torre et al. 2013; Quaglio et al. 2017; Stella et al. 2019 (3d-SPADE); Stella et al. 2022

- **Method.**
  - Frequent itemset mining (FP-growth) on binned spike trains, with lags encoded as (neuron, bin offset) items.
  - Patterns are pooled by **signature** (z = size, c = count), plus **d = duration** in 3d-SPADE. Example from Stella 2022: "a pattern composed of four spikes … occurring 29 times, with a duration of 10 bins … has a signature of z = 4, c = 29, d = 10."
- **Pattern-spectrum null: surrogate only.**
  - "The probability of having a pattern with signature (z, c) under the null hypothesis H0 of independence is evaluated via a Monte-Carlo technique on surrogate data which are generated from the original data by dithering."
  - The p-value of a signature is the fraction of surrogates containing a pattern at or above it. Torre 2013 used K = 5000 surrogates; Stella 2022 used "e.g., 5000".
  - Stella 2022 found that classical uniform dithering causes false positives through spike loss in binning and clipping. They recommend trial shifting (TR-SHIFT) or other surrogates.
- **Multiple testing.** Testing signatures rather than patterns "reduces the multiple testing problem to a size that can be handled with standard statistical corrections".
  - Torre 2013: Bonferroni over signatures (m ≤ 50).
  - Quaglio 2017: FDR (Benjamini–Hochberg).
  - Stella 2022: Benjamini–Hochberg over occupied signatures "where (z, c+1, d) is not occupied".
- **Finite-size and overlap.** Pattern Set Reduction (PSR) removes false positives from chance overlap of a true pattern with background spikes. It re-tests each pattern conditionally on its sub- and super-patterns, using signature (z_A − z_B + h, c_A). No analytical finite-size bias term is given; thresholds come from the surrogates.
- **Runtime.**
  - Quaglio 2017: PSF "is quite compute time intensive (… for a data set of 22,500 spikes it would take about 1,366 days) if processed in a serial way". This is mitigated by "Trivial parallelization" across surrogates.
  - Stella 2022: "large analyses can still take up to several hours on a computer cluster."
- **Order.** SPADE finds specific repeated lag patterns. It has no global cell ranking, no direction statistic and no measure of order strength.
- **How close to item 4.** Different question: detecting specific repeated patterns versus measuring a global order. Different null: surrogate rather than analytical.

### Palm, Paoletti, Ito, Stella & Grün 2026, Biol Cybern (full text, searched)

- **Method.** Defines a "quality" (unlikeliness) for a pattern repetition from its signature (size, repetitions, duration, novelty). A formula "is derived for stationary spike trains" under independence. Analytical bounds are compared with spike-randomization simulations, and simpler proxies are proposed "for statistical tests that avoid the multiple testing problem".
- **How close.** This is the group's most recent *analytical* expectation for repeated patterns under no structure. It is still about pattern repetition, not about how strong a global order is. We found no F-like order statistic.

### Unitary events with delays

- The UE papers we read (1999, 2002, the 2010 chapter) treat synchrony within a coincidence window, using multiple shifts for jitter tolerance.
- We found no UE variant in the group with a fixed nonzero lag and an order statistic.
- Delayed-coincidence UE was developed outside the group: Tuleau-Malot et al. 2014; Chevallier & Laloë, arXiv 1406.0476. We did not read these.

### Cell ordering and leader–follower in the group's orbit

- **Schneider, Havenith & Nikolić 2006, Neural Comput 18:2387** (G. Schneider is a Grün coauthor, e.g. Schneider & Grün 2003). This is the **closest prior art to item 4** that we found.
  - Pairwise CCH peak offsets φ_jk are condensed into a "preferred firing time" per unit.
  - Havenith et al. 2011 describe it: "x_k is determined as the normalized sum of all time delays φ_jk of unit k with respect to all other units". That is a row-sum ranking, O(N²), with no search, the same algebra as our Borda count but using delay *magnitudes* rather than signs.
  - Consistency is measured by an "additivity error σ_Add".
  - From the abstract and the Methods of the 2011 application: no analytical relation to jitter (nothing like 2/π·arctan), no no-order finite-size bias (nothing like c/√n̄), no multi-template result (nothing like 1/√M). Havenith 2011 used shift predictors and binomial tests across sequences.
- **Cobrawap, Gutzen et al. 2024** (Denker and Grün coauthors). Wave "planarity" P = ‖Σ v_i‖ / Σ‖v_i‖ is a net-alignment share, structurally like F, but over spatial direction vectors. "Wave modes" come from k-means on the trigger-delay matrix (compare M templates). We found no null or bias treatment for P (no matches for surrogate, null or chance).
- **Not found in the group:** any leader–follower measure, any sequence-direction statistic with an analytical null, or any finite-size bias formula for an order statistic.

---

## C. Verdicts

| Item | Verdict | Closest prior art |
|---|---|---|
| 1. Window sharing g_n, k̂ = 2 + (k−2)·g3/g2 | **Partly done.** The pair case with uniform jitter is done (1999 "fission" F(s,b), so 1 − F = g_2). An n-spike version with uniform jitter probably exists in Louis & Grün 2009/2010 but was not seen. **Not found:** Gaussian jitter with n onsets via the range R_n, and the jitter-corrected factorial-cumulant size estimator. CuBIC and Ehm et al. give the zero-jitter cumulant–size link and explicitly leave jitter unmodelled. | Grün et al. 1999; Louis & Grün 2009; Louis et al. 2010; Staude et al. 2010 (CuBIC) |
| 2. At-most-one-event term (events ≥ 20 s apart) | **Not found.** Every model uses a Poisson or Bernoulli mother/carrier process. The 1999 "bins already occupied" subtraction is a different, minor correction. | none |
| 3. Joint fit of jitter, participants and rate across w = 1, 2, 4 s | **Partly done.** Same goal (size and precision from population counts across bin widths) in Grün et al. 2008 and Louis et al. 2009/2010, but by a slope-change heuristic, with uniform jitter, no rate estimate and no formal fit, as far as we could verify. Ehm et al. 2007 estimate rate per size jointly, at one bin width and with no jitter. | Grün et al. 2008; Louis & Grün 2009; Louis et al. 2010; Ehm et al. 2007 |
| 4. Order indicator F (Borda row sums of D_ij, (2/π)·arctan law, c/√n̄ bias, 1/√M) | **Not found in the Grün group.** Their sequence tools (Schrader 2008, ASSET, SPADE, 3d-SPADE, Palm 2026) detect repeated specific patterns, with an analytical Poisson null (ASSET, Palm 2026) or surrogate nulls (SPADE). None ranks cells or measures order strength. **Adjacent:** Schneider, Havenith & Nikolić 2006 rank cells by normalized row sums of pairwise CCH delays (O(N²), no search), which overlaps our ranking step but uses delays rather than signs and gives no analytical expectation or bias. Cobrawap's planarity is a net-alignment share with no bias treatment. | Schneider et al. 2006 / Havenith et al. 2011; Torre et al. 2016; Quaglio et al. 2017 |

**Runtime contrast for item 4.**
- SPADE significance testing is surrogate-bound: about 1,366 days serially for 22,500 spikes, and "several hours on a computer cluster" after optimization.
- ASSET is analytical, at about 10 ms per matrix entry (under 7 min for 200 × 200).
- The Borda/F indicator is O(N²) in pairs with an analytical expectation, which is a distinct speed claim. No group paper makes a comparable one for an order statistic.

## D. Open points that a short email to Sonja Grün could settle

1. Does Louis, Borgelt & Grün 2010 give a closed form for the probability that all n jittered spikes of an event share one bin? Which jitter distribution (uniform, or anything Gaussian)?
2. In that paper, is size and precision estimated by a formal fit across bin widths, or by the slope-change rule? Is the mother-process (event) rate estimated?
3. Has the group combined CuBIC-style (factorial) cumulants with a jitter or fission correction, as the CuBIC paper left open ("remains to be assessed systematically")?
4. Has anyone in the group modelled mother processes with a refractory period or minimum spacing (at most one event per window) rather than Poisson or Bernoulli events?
5. What are the "two additional tools" in Gerstein et al. 2012? Does either order neurons or use pairwise lead/lag?
6. Is the group aware of an analytical null or finite-size bias for a global order or sequence-direction statistic? Examples would be a net-lead-sign agreement measure, or Schneider et al.'s preferred firing time and additivity error. Does Elephant contain anything like it?
7. Practical question: is SPADE or ASSET suitable for calcium-imaging event onsets with second-scale jitter and about 33 ROIs, or would they consider an analytical order indicator complementary?

## E. What we could not open

- **Louis, Borgelt & Grün 2010, Neural Netw 23:705–712.** Paywalled; no author or repository copy found (not on Borgelt's publication page, not in OpenAlex OA locations). We read the abstract, the 2009 CNS poster and the 2018 review's description.
- **Stella, Quaglio, Torre & Grün 2019, BioSystems (3d-SPADE).** Not retrieved; its method is described here via Stella et al. 2022.
- **Gerstein et al. 2012, J Neurosci Methods.** Abstract only.
- **Abstract only:** Pazienti et al. 2008 (Brain Res); Staude, Rotter & Grün 2008 (Neural Comput); Schneider, Havenith & Nikolić 2006 (Neural Comput). We did read the Methods of Havenith et al. 2011, which uses the 2006 method.
- **Not checked:** delayed-coincidence UE outside the group (Tuleau-Malot et al.; Chevallier & Laloë), Pipa's NeuroXidence (lag handling), and Kleinjohann et al. 2022/2024 (multiple-synfire-chain model).
