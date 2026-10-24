# Prior art on firing order within repeated events: replay, cortical sequences, sequence discovery, calcium imaging, ranking statistics

Scope: the Kreuz group (SPIKE-order, Synfire Indicator) and the Grün group (ASSET, SPADE, Elephant) are covered elsewhere and left out here.

## What is being checked

1. **Score sort.** Cells are ordered by the row sums of the net pairwise-lead matrix D (a Borda/Copeland-style score), then refined by local insertion. F is the net agreement with that order, as a share of pair co-participations.
2. **One template.** One fixed latency template (spread δ) with Gaussian jitter σ gives F = (2/π)·arctan(δ/σ), Greiner's relation for the population Kendall tau.
3. **M templates.** With M templates mixed at random, the signal falls as 1/√M.
4. **No order.** With no order, F has a finite-size bias of about c/√n̄, where n̄ is the number of events a pair shares (c ≈ 0.38 for Borda and 0.50 after search, at 33 cells and 10 per event). At 5–10 events, one template is detected only part of the time.

**Reading levels.** "Full text" means I read the article body, by text search over the full text or by a structured reading of the publisher or PMC page. "Abstract" means only the abstract or metadata. "Recollection" means a description from prior knowledge that I did not re-verify this session; treat these as leads to check.

---

## A. Hippocampal replay and preplay (rank-order methods)

### Lee & Wilson 2002, *Neuron* 36:1183–1194, doi:10.1016/S0896-6273(02)01096-6
- **Read:** abstract only (full text not open-access).
- **Method:** a "novel combinatorial decoding method" that finds sequences of four or more place cells firing in track order during slow-wave sleep.
- **Null:** from recollection, significance came from comparing match counts against shuffled cell orders, and against pre-experience sleep. Not verified.
- **Analytical or finite-size treatment:** none found in what I could read.
- **Closeness:** low. It uses an exact or near-exact sequence match against an external template. No score sort and no optimisation-bias treatment.

### Foster & Wilson 2006, *Nature* 440:680–683, doi:10.1038/nature04587
- **Read:** abstract only. The method is from recollection.
- **Method:** the firing order of cells in each candidate event is correlated with the place-field order from RUN, an external template. Significance comes from a cell-identity shuffle, and events need a minimum number of active cells.
- **Analytical null:** none, as far as I know.
- **Closeness:** low to moderate. It is per-event rank correlation against a template fixed outside the data, so no optimisation bias arises.

### Diba & Buzsáki 2007, *Nat Neurosci* 10:1241–1242, doi:10.1038/nn1961
- **Read:** full text (PMC author manuscript; supplementary methods not available).
- **Method:** "We defined the event sequence on the basis of the firing order of the first spikes from the neurons." Each event's order is rank-correlated with the place-field-peak order for each running direction, which is an external template. Events require "≥30% or ≥5 of the place cells, whichever was greater" to fire.
- **Null:** 500 surrogates per event made by shuffling neuron identities. An event is significant beyond the 95% range of its surrogates. Counts of significant events are compared to the number "expected by chance".
- **Analytical or finite-size treatment:** none. Small cell counts are not discussed beyond the ≥5-cell threshold.
- **Closeness:** low to moderate. Order is taken from first spikes, which is closer to our latency setting. The template is external.

### Davidson, Kloosterman & Wilson 2009, *Neuron* 63:497–507, doi:10.1016/j.neuron.2009.07.027
- **Read:** full text (PMC).
- **Method:** Bayesian decoding in 20 ms bins. The best-fitting line through the posterior is found by optimising over velocity and offset, and its likelihood is the "replay score".
- **Null:** three shuffles, including a "unit identity shuffle" and pseudo-events. The score is compared using a Monte Carlo p-value below 0.01 for each shuffle type.
- **Analytical or finite-size treatment:** none analytical. The relevant design choice is that the same optimisation (the line search) is re-run on every shuffle. That is the empirical cure for optimisation bias, and it corresponds to our search-versus-Borda difference in c.
- **Closeness:** moderate for point 4. It handles a search-inflated statistic, but only empirically.

### Dragoi & Tonegawa 2011, *Nature* 469:397–401, doi:10.1038/nature09633
- **Read:** full text (PMC).
- **Method:** spiking events need "at least four different place cells". Each event's firing order is rank-order correlated with a novel-arm place-field template.
- **Null:** significance against shuffled templates (97.5th percentile). The fraction of significant events is tested against a binomial chance level ("chance level (3.2%)"). "The median number of place cells active on the novel track participating in preplay events is six."
- **Analytical or finite-size treatment:** none. With four to six cells per event, each per-event rank correlation has a very coarse discrete null, and that is handled only by the shuffle.
- **Closeness:** low to moderate. There are few cells per event, as in our data, but the template is external.

### Silva, Feng & Foster 2015, *Nat Neurosci* 18:1772–1779, doi:10.1038/nn.4151
- **Read:** full text (PMC).
- **Method:** re-tests the preplay rank-order (Spearman) analysis with large ensembles.
- **Selection bias:** this is the key passage. When each event keeps "only the directional template … that maximized the absolute correlation", the shuffles must receive the same maximisation ("We likewise chose the best template for each shuffle"). The authors argue that the original preplay papers appear to have selected a template per event while drawing an unmaximised (unimodal) shuffle: "a choice of template was made for each event, but the unimodal shuffle distribution is inconsistent with this procedure." The median |ρ| rises from 0.174 to 0.245 purely from taking the larger of two templates.
- **Subsampling:** results were unchanged when cells were subsampled to the original reports' counts.
- **Analytical or finite-size treatment:** none. The argument is entirely empirical.
- **Closeness:** the closest replay paper to point 4. It shows explicitly that a maximum over candidate orders inflates absolute rank correlation, and that the null must be maximised in the same way. Here the maximum is over two templates; ours is over all N! orders. It gives no √n scaling.

### van der Meer, Kemere & Diba 2020, *Phil Trans R Soc B* 375:20190238, doi:10.1098/rstb.2019.0238
- **Read:** full text (PMC).
- **Content:** an inventory of shuffle types (spike-id, cell-id, circular place-field, column-cycle, time-swap) and of how each null can misfire. For example, the cell-id shuffle "tests against ensemble reactivation and sequence replay simultaneously". It lists "the percentage and/or number of active cells" as an experimenter choice that shifts null distributions. It notes that "decoded posterior probabilities during SWRs are sensitive to the number of co-active cells", and it recommends separating replay strength from the amount of evidence.
- **Analytical or finite-size treatment:** none. It recommends cross-validation and generative-model simulations.
- **Closeness:** conceptual support for point 4 (dependence on the number of cells and events), with no formula.

### Tirole, Huelin Gorriz, Takigawa, Kukovska & Bendor 2022, *eLife* 11:e79031, doi:10.7554/eLife.79031
"Experience-driven rate modulation is reinstated during hippocampal replay."
- **Read:** full text.
- **Method:** the main score is the weighted correlation of the decoded posterior. A Spearman rank-order score on median spike times is used as a control. An event must pass three shuffles (spike-train circular shift, place-field shift, circular position shift) at the 95th percentile. At least five active units are required.
- **Shuffle choice and finite size:** not studied in this paper.

The companion methods critique is **Takigawa, Huelin Gorriz, Tirole & Bendor 2024, *eLife* 13:e85635**, "Evaluating hippocampal replay without a ground truth" (full text read).
- Estimated false-positive rates range from about 2% to 18% across shuffles. Randomising along the same dimension used for detection gives a "substantial underestimation of the empirically estimated false-positive rate."
- For Spearman, using all spikes instead of the median spike violates independence and inflates false positives to about 17%.
- There is no analytical null for Spearman and no analysis by number of cells.
- **Closeness:** low to moderate. It confirms that the field calibrates nulls empirically and that within-event dependence inflates rank statistics.

### Replay summary
Every replay rank-order method correlates each event with a template taken from separate behaviour (RUN). The template is external, so the event-level null has mean zero and no optimisation bias arises. Nulls are always shuffles. No paper gives a closed-form null or a 1/√n bias. The only optimisation-bias discussion is Silva et al. 2015 (maximum over two templates). Davidson et al. 2009 handle optimisation bias implicitly by re-optimising on shuffles.

The pairwise antecedent of D_ij is **Skaggs & McNaughton 1996, *Science* 271:1870** (recollection; not opened). It uses the asymmetry ("temporal bias") of each pair's cross-correlogram during sleep, compared with the order during RUN. That is a pairwise-lead matrix, but it was not aggregated into a ranking. Nádasdy et al. 1999 (*J Neurosci*) used template matching with shuffles (recollection).

---

## B. Cortical sequences

### Luczak, Barthó, Marguet, Buzsáki & Harris 2007, *PNAS* 104:347–352, doi:10.1073/pnas.0605643104
- **Read:** full text, by a structured reading of the PMC page.
- **Method:** each neuron's latency is the "mean spike time within 200 ms of UP state onset". Consistency of the order is tested by split-half reliability ("R = 0.84, P < 0.001 for 180 cells pooled"). Triplets are tested against time-shuffled and common-excitability surrogates.
- **Analytical or finite-size treatment:** none. Recordings have 244–611 UP states, so few-event bias is not an issue.
- **Closeness:** moderate for points 1–2. Order comes from mean latency (a Borda-like centroid), and the split-half check implicitly avoids in-sample bias. No analytical null.

### Luczak, Barthó & Harris 2009, *Neuron* 62:413–425, doi:10.1016/j.neuron.2009.03.014
- **Read:** full text (PMC).
- **Method:** "Similarity to the mean response sequence was assessed by Spearman's rank correlation of single-trial firing times with the mean spike times computed from the same neurons' PETHs." Only trials with at least three active neurons are used, and the distribution is tested against zero with a t-test.
- **In-sample issue:** as written, the template (mean PETH) appears to include the trial being tested. A t-test against zero is then biased upward by roughly the item-total effect described in Section E. A leave-one-out may be in their Supplementary Fig. 4A, which I could not open. With hundreds of trials the bias is small for them, but this is exactly the structure of point 4.
- **Closeness:** moderate. It is the same construction (correlating each event with a template averaged over events) with no bias treatment in the main text.

### Luczak, McNaughton & Harris 2015, *Nat Rev Neurosci* 16:745–755, doi:10.1038/nrn4026
- **Read:** abstract and recollection.
- **Content:** a review of the "packet" concept, in which the latency order within packets is stereotyped across spontaneous and evoked events.
- **Analytical or finite-size treatment:** none.
- **Closeness:** conceptual only.

### Ikegaya et al. 2004, *Science* 304:559–564, doi:10.1126/science.1093173
- **Read:** abstract.
- **Method:** repeated intracellular motifs and repeated calcium-imaging cell sequences ("Sequences of active neurons … repeated in the same order"), with significance against shuffled or surrogate data (recollection).
- **Analytical null:** none.

### Mokeichev et al. 2007, *Neuron* 53:413–425, doi:10.1016/j.neuron.2007.01.017
- **Read:** abstract.
- **Finding:** "We found no evidence for the existence of deterministically generated cortical motifs … they appear by chance." The test uses three surrogate types that preserve coarse dynamics.
- **Closeness:** conceptual for point 4. A search over many candidates produces high-similarity "repeats" by chance, and surrogates must go through the same search. There is no analytical treatment.

### Abeles & Gerstein 1988, *J Neurophysiol* 60:909–924, doi:10.1152/jn.1988.60.3.909
- **Read:** abstract.
- **Method:** this is the one place with **analytical** expected counts. It gives "equations for calculating the number of patterns of given length and repetition that would be expected", with confidence limits from those expected numbers, for patterns of three to six spikes.
- **Closeness:** the analytical null covers counts of exact repeating spike patterns, not a rank-agreement statistic or the bias of a fitted order.

### Prut et al. 1998, *J Neurophysiol* 79:2857–2874, doi:10.1152/jn.1998.79.6.2857
- **Read:** abstract.
- **Method:** "The expected level of repetition was computed based on the firing rate and the pairwise correlation of the participating units, assuming a Poisson distribution of event counts." This is again an analytical null for precise-firing-sequence counts.
- **Related:** Baker & Lemon 2000 (*J Neurophysiol* 84:1770) later found such patterns "occur at chance levels" under better surrogates. That is cited inside Luczak 2009; I did not open it.
- **Closeness:** low.

### Schrader, Grün, Diesmann & Gerstein 2008, *J Neurophysiol* 100:2165–2176, doi:10.1152/jn.01245.2007
- **Read:** full text, by a structured reading of the PMC page.
- **Method:** an intersection matrix between time bins; synfire runs appear as diagonal stripes.
- **Null:** "Direct significance testing is not necessary." Controls are empirical, and the detection limit is found empirically (about 50–100 chain neurons; 300–500 if the chain is about 1% of the recorded pool).
- **Analytical treatment:** none. The only closed-form result is that k repeats give k(k−1)/2 stripes.
- **Closeness:** low.

---

## C. Sequence-discovery methods

### seqNMF: Mackevicius, Bahle, Williams, Gu, Denisenko, Goldman & Fee 2019, *eLife* 8:e38471, doi:10.7554/eLife.38471
- **Read:** full text.
- **Method:** convolutional NMF with a cross-factor penalty.
- **Null:** factor significance is tested **on held-out data**. Overlap with held-out data is compared with null factors built by "randomly circularly shifting each row of a factor independently". "Extracted factors were significant on held-out data compared to null (shuffled) factors even when training and test datasets each contained only 2 examples of each sequence." Cross-validation on masked data is also used to choose λ and K, and to guard against overfitting.
- **Analytical treatment:** none.
- **Closeness:** high in spirit for point 4. It recognises that a sequence fitted to the data scores above chance on that same data, and fixes this by a train/test split rather than by an analytical correction.

### PP-Seq: Williams, Degleris, Wang & Linderman 2020, *NeurIPS* 33 ("Point process models for sequence detection in high-dimensional neural spike trains")
- **Read:** not opened this session (recollection).
- **Method:** a Bayesian Neyman–Scott point-process model. Each sequence type gives each neuron an offset and a Gaussian width, so it is a generative version of our "fixed latency template + Gaussian jitter". It has several sequence types and is fitted by collapsed Gibbs sampling, with model checks on held-out ("speckled") data.
- **Analytical treatment:** no closed-form rank-agreement null that I know of.
- **Closeness:** the generative model matches points 2 and 3 (one template or M templates with Gaussian jitter), but the paper does not derive a Kendall-tau formula or a 1/√M law.

### Russo & Durstewitz 2017, *eLife* 6:e19428, "Cell assemblies at multiple time scales with arbitrary lag constellations" (CAD)
- **Read:** not opened. The PubMed lookup returned an ambiguous ID, so the text I downloaded was a different paper and was discarded.
- **Method (recollection):** agglomerative assembly building from pairwise tests of lagged co-activation counts. It uses a parametric test statistic with a correction for non-stationarity, instead of surrogates, and Bonferroni-type control.
- **Closeness:** pairwise lag statistics similar to D_ij, but it is assembly and lag detection, not ordering. It has no rank-agreement null.

### Grossberger, Battaglia & Vinck 2018, *PLoS Comput Biol* 14:e1006283, doi:10.1371/journal.pcbi.1006283 (SPOTDisClust)
- **Read:** full text.
- **Method:** each epoch is represented by the normalized cross-correlations of all neuron pairs: "two patterns [have] the same temporal structure when all neuron pairs have the same expected value of s′ij(τ)". Epochs are compared by optimal-transport distance and then clustered. This is a pairwise-order representation, a continuous analogue of D_ij per event, and clustering handles M templates.
- **Null and analytical treatment:** no analytical null or finite-size treatment of agreement. Validation uses ground-truth simulation.
- **Closeness:** moderate for points 1 and 3. Pairwise order is the primitive, and multiple patterns are separated by clustering rather than averaged, which avoids the 1/√M dilution. No formulas.

### Watanabe, Haga, Ikegaya, Fukai et al. 2019, *Front Neuroinform* 13:39, doi:10.3389/fninf.2019.00039
- **Read:** full text.
- **Method:** edit-similarity (Needleman–Wunsch) between binned windows, followed by clustering.
- **Null:** "surrogate data in which spikes of each neuron were randomly shuffled across time bins (this corresponds to the null model of homogeneous Poisson processes)", then Bayesian modelling of significance.
- **Analytical treatment:** none for order agreement.
- **Closeness:** low.

---

## D. Calcium imaging

- **Ikegaya et al. 2004:** calcium-imaging cell sequences with surrogate nulls. See Section B.
- **Villette, Malvache, Tressard, Dupuy & Cossart 2015, *Neuron* 88:357–366, doi:10.1016/j.neuron.2015.09.052.** Read: full text.
  - Recurring CA1 calcium sequences during running; "Statistical analysis using data reshuffling established that sequences were not occurring by chance (p < 0.001)".
  - Spearman slopes are used for distance and time coding.
  - No analytical null.
- **Kravets et al. 2022, *PLoS Biol* 20:e3001761 ("first responder" β-cells in pancreatic islets).** Read: full text (searched).
  - Order of first-phase responses is "consistent over time up to approximately 24 h". Leader cells and hub cells are defined by phase lag and connectivity, with comparisons by mixed-effects models.
  - No rank-agreement null and no finite-size treatment of order consistency.
  - Relevant as a field that reports cell-order consistency from few waves with ad hoc statistics.
- **Kuga et al. 2011, *J Neurosci* (astrocyte "glissandi").** Read: search-result snippet only.
  - Cells are ranked by activation order in successive waves, and a Spearman coefficient is computed for each pair of events: "Among 40 pairs in five glissandi, 32 (80%) exhibited a significance level of 5%".
  - This is an inter-event pairwise rank correlation with the textbook per-pair p-value. It has no fitted consensus, so no optimisation bias, and no pooled analytical null.
- **Cultured networks (recollection; not opened):**
  - Raichman & Ben-Jacob 2008, *J Neurosci Methods*: repeating rank-order motifs of first spikes in network bursts.
  - Shahaf et al. 2008, *PLoS Comput Biol*: "order-based representation" from the rank order of first spikes across electrodes.
  - Eytan & Marom 2006: leader neurons.
  - Bonifazi et al. 2009, *Science*: hub cells in early network oscillations, by onset order.
  - All use rank or onset order with shuffle or permutation nulls. I know of no analytical finite-size result in these.

**Summary:** in calcium-imaging and propagation-order work, consistency of order across few events is assessed with shuffles, per-pair Spearman p-values, or split-half correlations. I found no analytical null or c/√n bias.

---

## E. Statistics: ranking, concordance and optimised orders

### Greiner's relation (point 2)
- **Sources:** Greiner 1909; Esscher 1924; Kendall 1949, *Biometrika* 36:177; and in Kendall's *Rank Correlation Methods*. Recollection; standard result.
- **Result:** for a bivariate normal, τ = (2/π)·arcsin ρ.
- **Link to our formula:** with template latencies of spread δ and independent Gaussian jitter σ, ρ = δ/√(δ²+σ²), and arcsin(δ/√(δ²+σ²)) = arctan(δ/σ). Our F = (2/π)·arctan(δ/σ) is therefore Greiner's relation plus a trigonometric identity.
- **Generative model:** the model itself (each pair's lead probability Φ((μi−μj)/(σ√2))) is Thurstone's 1927 Case V paired-comparison model (Mosteller 1951). Bradley–Terry (1952) is its logistic analogue.
- **Verdict:** known.

### Kendall's coefficient of concordance W
- **Sources:** Friedman 1937; Kendall & Babington Smith 1939, *Ann Math Stat* 10:275, "The problem of m rankings". Recollection; standard.
- **Result:** for m complete rankings of N objects, W is computed from the rank sums, which are the **Borda scores**. Under the null of independent random rankings, E[W] = 1/m exactly, and m(N−1)W is approximately χ²(N−1).
- **Item–total identity:** the mean Spearman correlation between each ranking and the rank-sum consensus equals √W exactly (no ties). So under no order it is about **1/√m**. This is the √n finite-size bias of point 4, in its full-ranking, Spearman form. It is "known" in the sense that it follows in two lines from Kendall's W, though I did not find it stated as a "bias of agreement with a fitted order".
- **Mixture of templates (point 3):** the same algebra gives the 1/√M law. The correlation of one ranking with the sum of M independent rankings is 1/√M.
- **Check I ran (not literature):** a simulation with N = 33 and all cells in every event. F (net Kendall agreement with the Borda order) times √m was 0.66–0.68 for m = 5–80. This matches (2/π)·arcsin(1/√m) ≈ 0.64/√m to within finite-N corrections, since Greiner's relation applied to the item–total correlation gives the Kendall version.
  - With 10 of 33 cells per event, F·√n̄ fell to about 0.38 at large n̄. That reproduces our fitted c and shows that partial participation changes the constant. I found no published constant for this incomplete-ranking case.
- **Incomplete-block analogues:** Durbin 1951 (balanced incomplete blocks) and Skillings & Mack 1981 extend Friedman/Kendall tests to incomplete rankings with chi-square nulls (recollection). These are the nearest published analytical nulls for "each event ranks only a subset of cells".
- **Verdict:** the √n form is known through W. Our constants for partial participation and for the search-optimised order are not in the literature I found.

### Paired-comparison consistency
- **Kendall & Babington Smith 1940, *Biometrika* 31:324.** The coefficient of consistence (circular triads) and the coefficient of agreement u among judges, with exact or chi-square nulls.
- **Slater 1961, *Biometrika* 48:303,** "Inconsistencies in a schedule of paired comparisons". Slater's i is the minimum number of reversals needed to make a tournament transitive, which is exactly the optimum of our search. Slater tabulated its null distribution for small n by enumeration.
- All from recollection.
- **Closeness:** high for the objective. Slater's i is the unweighted version of our searched F.

### Linear ordering, Kemeny, feedback arc set
- **Kemeny 1959; Young & Levenglick 1978.** The Kemeny ranking is the maximum-likelihood estimate under the Mallows model (Mallows 1957). Recollection.
- **Hardness:** Kemeny ranking is NP-hard (Bartholdi, Tovey & Trick 1989; Dwork et al. 2001; Alon 2006 for tournaments).
- **Random tournaments (search results and recollection):**
  - Erdős & Moon 1965, *Canad Math Bull* 8:269.
  - Spencer 1971 (*Networks*) and 1980.
  - Fernandez de la Vega 1983, *J Combin Theory B* 35:328.
  - Result: the maximum number of arcs consistent with any ordering of a random tournament on n vertices is n²/4 + Θ(n^{3/2}). The optimised excess agreement is therefore of order 1/√n **in the number of items**.
  - Poljak, Rödl & Spencer 1988 give a polynomial algorithm that attains an excess of order n^{3/2}. I did not verify that title.
- **Relation to point 4:** this is the classical "maximised agreement under no order" result. Its √ scaling is over the number of items for a ±1 tournament. Our c/√n̄ is over events per pair, with N fixed. The two are related through weighted tournaments: each D_ij is a sum of n̄ random ±1 values, so the optimised weighted agreement scales as √n̄·g(N)/n̄. I did not find the weighted, sparse-participation version with an explicit constant.
- **Borda quality:** Coppersmith, Fleischer & Rudra 2006/2010 (SODA; *ACM Trans Algorithms*) show that "ordering by weighted number of wins" (Borda) is a 5-approximation for weighted feedback arc set, and that the bound is tight. This supports the score sort as a no-search approximation to the Kemeny/linear-ordering optimum.

### Ranking from pairwise comparisons (consistency)
- Zermelo 1929 and Bradley & Terry 1952 (MLE); Simons & Yao 1999 (*Ann Stat*: asymptotics as the number of items grows); Shah & Wainwright 2018 (*JMLR*: "Simple, robust and optimal ranking from pairwise comparisons", where Copeland counting is minimax-optimal for top-k recovery); Negahban, Oh & Shah 2017 (Rank Centrality); Rajkumar & Agarwal 2014 (*ICML*: Borda and other aggregation methods are consistent under some noise models, such as BTL and low-noise, but not all). All from recollection.
- **Closeness:** these justify points 1 and 2 (Borda/Copeland recovers a Thurstone/BTL order consistently). They address recovery error, not the null bias of the agreement statistic.

### Expected maximum of Kendall tau or Spearman rho over orderings
I found no paper that states E[max over orderings of agreement] ≈ c/√n for paired data with n observations per pair. The pieces are Kendall's W (E[W] = 1/m) for the Borda version and Erdős–Moon / Spencer / de la Vega for the optimised version on tournaments.

---

## Verdicts

| Point | Verdict | Basis |
|---|---|---|
| 1. Score (Borda/Copeland) sort of a pairwise-lead matrix, local refinement, net-agreement indicator | **Known** | Borda/Copeland on weighted tournaments, with a 5-approximation guarantee (Coppersmith et al.). Linear ordering / Kemeny / Slater objectives. Kendall's W uses the same rank sums. Neuroscience uses mean-latency orders (Luczak 2007) and pairwise leads (Skaggs & McNaughton 1996) without naming it Borda. The novelty is only in applying it to calcium events with partial participation. |
| 2. F = (2/π)·arctan(δ/σ) for one template with Gaussian jitter | **Known** | Greiner/Kendall τ = (2/π)·arcsin ρ with ρ = δ/√(δ²+σ²). The generative model is Thurstone Case V; PP-Seq is a modern neural version. |
| 3. 1/√M dilution with M random templates | **Partly known** | It follows from the item–total identity under Kendall's W (correlation of one ranking with a sum of M independent rankings is 1/√M). I found no neuroscience or ranking paper that states it for mixed sequence templates. The methods literature avoids it by clustering or factorising (seqNMF, PP-Seq, SPOTDisClust). |
| 4. No-order finite-size bias c/√n̄ (Borda and searched), and partial detection at 5–10 events | **Partly known** | The 1/√m form for agreement with the in-sample Borda consensus is implied by E[W] = 1/m (Kendall & Babington Smith 1939). The searched-order analogue is the n²/4 + Θ(n^{3/2}) random-tournament result, but that scaling is over items, not events. Max-selection bias is shown empirically for replay templates (Silva et al. 2015), and in-sample fit bias is handled by held-out testing (seqNMF). **Not found:** the explicit c for sparse participation (about 0.38 Borda, 0.50 search), the √n̄ scaling over events shared per pair, and power curves at 5–10 events. |

**Closest single prior work:** Kendall & Babington Smith 1939, "The problem of m rankings" (Kendall's W). It uses the same Borda rank sums, has an exact null expectation (E[W] = 1/m), and gives the 1/√m bias of each ranking's agreement with the consensus. Combined with Greiner's relation, it reproduces our full-participation constant (about 0.64–0.68).

Within neuroscience, the closest is Silva, Feng & Foster 2015: an empirical demonstration that maximising rank correlation over candidate orders inflates it, so the null must be maximised the same way.

**Could not open:**
- Full texts of Lee & Wilson 2002, Foster & Wilson 2006, Ikegaya 2004, Mokeichev 2007, Abeles & Gerstein 1988, Prut 1998 and Luczak 2015 (abstracts only).
- Russo & Durstewitz 2017 and Williams et al. 2020 (PP-Seq) were not opened.
- Supplementary methods of Diba & Buzsáki 2007 and Luczak et al. 2009, including whether Luczak 2009's template excludes the test trial.
- The primary texts of the statistics references (Kendall & Babington Smith 1939/1940, Slater 1961, Erdős–Moon 1965, Spencer, de la Vega 1983, Poljak–Rödl–Spencer, Shah & Wainwright, Rajkumar & Agarwal). These are cited from standard knowledge and search abstracts. The exact constants in the random-tournament bounds were not verified.
- Kuga et al. 2011 was seen only as a search snippet.
