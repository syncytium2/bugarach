GRANT 2 MISMATCH — missing none (Read, Grep, Glob, Bash, WebSearch, WebFetch all held; WebSearch/WebFetch arrived as deferred tools and were loaded); holds forbidden tools: Edit, Write, NotebookEdit (deferred), PowerShell, Agent, Artifact, Skill, plus write-capable MCP connectors (Claude Docs batch/update/create/delete, Dropbox, Gmail). None of the forbidden tools was used. Per the process file, this is a finding about the run: the run record's `roles:` line should say role 2 ran on a fallback grant.

# Role 2 — DOI or Die: citation and reference validation, Chapter 1 (blind verify, round 2)

Artifact: `docs/dissertation/chapter-1-aim0.md` (hash-object cdc8fbf6…, confirmed). I did not open `docs/reviews/chapter-1-aim0_2026-10-29*` and did not read the chapter's git history. Scratch files are in my work-r2-2 folder only.

## What I checked

- **Existence and metadata.** All 44 entries in the reference list were resolved against Crossref (DOI, authors, journal, volume, pages, year). JMLR, which Crossref does not index, was checked on jmlr.org. **Every reference exists, and its metadata matches the chapter.** No reference is fabricated or guessed. Notes:
  - Kreuz 2026 (*Biol Cybern* 120:21, doi 10.1007/s00422-026-01045-5) exists.
  - Wang 2024 was online in 2023; its volume 119 is dated 2024.
  - Peyrache 2010 was online in 2009.
- **Claims checked against the texts** in `<01-lit>/bugarach/synthetic_validation/` (and the text extractions), `<01-lit>/bugarach/coordination/`:
  - Grün 1999, eq. 5.
  - Louis, Borgelt & Grün 2010: uniform jitter and binomial counts, the Max2 change of slope, two straight lines, Fig. 6, and that it builds on Grün, Abeles & Diesmann 2008 (LNCS 5286:96–114, confirmed from its reference list).
  - Pazienti 2008.
  - CuBIC: lower bound on order, compound Poisson process, eq. 3, and Kuhn's SIP/MIP as special cases.
  - Thomas 1949 (count distribution only), Waagepetersen 2007 (Thomas K-function, eq. 7), Diggle & Gratton 1984.
  - Kish 1995, p. 64 (rendered and viewed).
  - Kruskal 1958, secs. 3–4, 6 and 17.
  - Kreuz 2017: the finite-size passage and the "not sufficient to reliably compare" quote.
  - Coppersmith 2006: factor of 5, and w_uv + w_vu = 1.
  - Shah & Wainwright: top-k, and comparisons independent across pairs.
  - Mariani 2025, Cecchini 2021, Peyrache 2010, Lopes-dos-Santos 2011, DeFazio 2026 (10 Hz imaging, fast and slow events).
- **Laboratories.** Last author and affiliation checked for Cecchini 2021, Kreuz 2022 and Mariani 2025 (all Kreuz, ISC-CNR Florence), and for CuBIC (RIKEN and Freiburg).
- **My own prior-art search** for contributions 1–3, 4, 6 and 7. Fields are listed at the end.

## Findings

| # | Location | Issue | Severity | Suggested fix | Verified against source |
|---|---|---|---|---|---|
| 1 | 1.1 Contributions 1–3; 1.9.1 rows "g_n…" and "A formal fit across windows…" | **Unsearched field with a close precedent: fluorescence fluctuation spectroscopy.** Müller 2004 (*Biophys J* 86:3981, doi 10.1529/biophysj.103.037887) links the factorial cumulants of binned counts to brightness and number of emitters, and derives the second factorial cumulant as a function of sampling time. Wu & Müller 2005, TIFCA (*Biophys J* 89:2721, doi 10.1529/biophysj.105.063685, PMC1366773), computes factorial cumulants at several rebinned sampling times and fits them for brightness, occupation number and diffusion time together. It also gives the variance of the cumulants. That is the joint fit's construction: factorial cumulants of a binned count across window widths, fitted for size (≈ k), number or rate (≈ λ) and timescale (≈ σ). It comes with the per-estimate uncertainty the chapter says the joint fit lacks (1.4.6, 1.9.4 item 3). The physics differs (diffusing emitters, not jittered clusters), so the g_n closed form may still be new. "A formal fit across windows that also recovers the event rate" cannot stand as a contribution without this field. | **blocking** | Cite Müller 2004 and Wu & Müller 2005 in 1.2.3 and 1.9.1. Narrow contribution 3 to the jittered cluster-process form (g₂, g₃, the hard-core term). Consider borrowing TIFCA's cumulant-variance expressions for the missing per-recording uncertainty. | yes (abstracts, via Europe PMC; full texts not opened) |
| 2 | 1.2.3 "Diggle 1983 ⚠; Diggle & Gratton 1984, who also fit models…"; 1.9.1 row "Fitting a cluster process by pair counts across scales" | **Misattribution.** Diggle & Gratton 1984 contains no cluster or Neyman–Scott process. Its spatial example (sec. 6) is a pairwise-interaction inhibition model, with a hard-core special case, fitted by matching simulated K-functions. For the minimum-contrast method it points to Diggle 1983, ch. 5. So the only opened source for "Neyman–Scott fitted by minimum contrast on K" is Waagepetersen 2007, a later restatement. The root, Diggle 1983, is ⚠. Earlier still is Diggle 1978, *JRSS B* 40:178 (doi 10.1111/j.2517-6161.1978.tb01660.x, not opened). | major | Cite Diggle & Gratton only for simulation-based fitting of implicit models. Its hard-core inhibition model is a nice link to the chapter's hard-core train. Pull Diggle 1983 ch. 5 (and Diggle 1978) for the cluster-process minimum contrast. | yes |
| 3 | 1.1 "two contributions (4 and the order bias in 6) are known in form from other fields" | **The summary contradicts 1.9.1.** In 1.9.1, contribution 5 (membership variance) is Kish's design effect, and the one-template F in 6 is Greiner's/Kruskal's relation. The order *bias* is listed there as having no formula in prior work. So the summary names the wrong part of 6 and leaves out 5. | major | Rewrite it to match: "4, 5 and the one-template F in 6 are known in form; the score sort is Copeland ranking." | yes (internal) |
| 4 | 1.9.1 "Fields not searched: … the hippocampal replay and cortical sequence literature (Lee & Wilson 2002; Luczak et al. 2007)" | **The chapter under-reports its own search.** `docs/learned/synthetic_validation/prior_art/order_literature.md` (and `prior_art/README.md`) record a search of replay (Lee & Wilson 2002 through Tirole et al. 2022) and of cortical sequences (Luczak 2007/2009/2015, Ikegaya, Abeles & Gerstein, Schrader 2008), mostly from abstracts. The chapter follows the goal page's older "⚠ Not searched" line. That search names **Silva, Feng & Foster 2015** (*Nat Neurosci* 18:1772, doi 10.1038/nn.4151) as the closest neuroscience precedent for the optimization bias of an in-sample order. The chapter does not cite it. | major | Say the replay and sequence field was searched at abstract level, and cite Silva et al. 2015 beside Kreuz 2017 in the "exact no-order mean" row and in 1.6.2. Reconcile the goal page with prior_art/. | yes (repo record; Silva metadata via Crossref; Silva text not opened by me) |
| 5 | 1.6.2 "Ranking by net wins is the textbook Copeland ranking…"; 1.9.1 "The score sort" row | **Missing closest precedent.** `kreuz_sort/literature_report.md` names Tomlinson et al. 2019 (*Epilepsia* 60:898, doi 10.1111/epi.14720, PMC6488404) as "the closest prior art to our score sort". They rank nodes by a net upstream/downstream score, score each sequence against that order, use a permutation null, and note a size dependence they do not correct. This is a different group from Kreuz's. The chapter cites only Schneider 2006 (⚠). | major | Cite Tomlinson et al. 2019 in 1.6.2 and 1.9.1. | yes (repo record of a full-text read; I did not reopen it) |
| 6 | 1.6.2 "they do not give a formula for it"; 1.9.1 "an analytical null for this indicator was not found" | **An omission that weakens the point.** Kreuz et al. 2017 (sec. 2.5) considered an analytical binomial null and rejected it, because "the pairwise spike orders in coincident events involving multiple spike trains are not independent". That is the same dependence the chapter raises against Shah & Wainwright. | minor | Say that Kreuz et al. considered and rejected an analytical null, and why. That makes the exact no-order mean a more pointed contribution. | yes |
| 7 | 1.6.2 One template "(Kruskal 1958, derived in secs. 3–4)"; 1.9.1 "(Kruskal 1958, who credits its meaning under the normal to Esscher 1924)" | **Origin not cited, and a loose paraphrase.** Kruskal takes the quadrant relation from Cramér (p. 290) and gets τ from it in sec. 4. He never mentions Greiner. Of Esscher he says only that Esscher gave "the population meaning of τ" and worked in the bivariate normal case; he does not credit the arcsine relation to Esscher. The relation is usually credited to Greiner 1909 (via Moran), with earlier calculations by Sheppard 1898/99 and Stieltjes 1889. The repository's own prior_art record calls it "Greiner's relation". Esscher 1924 is cited in the table but missing from the reference list. | minor | Credit Greiner 1909 (and Sheppard 1899), with Kruskal 1958 as the modern derivation. Fix the Esscher wording, and add Esscher, or drop the mention. | partly (Kruskal yes; Greiner and Sheppard from secondary web sources, not opened, ⚠) |
| 8 | 1.2.3 "The same group extended the approach to non-Poisson spike trains (Reimer et al. 2012 ⚠) and fitted rates per event size (Ehm, Staude & Rotter 2007 ⚠)" | **Wrong order, loose wording, and "same group".** (a) Ehm 2007 *predates* CuBIC (2010), so it is an antecedent, not an extension. (b) Reimer 2012's abstract describes a generator of correlated renewal (non-Poisson) trains and a robustness test of Ehm's de-Poissonization, finding results "more reliable for small analysis bins". It does not extend CuBIC. (c) Reimer and Ehm come from Rotter's Freiburg circle. CuBIC's last author is Grün, then at RIKEN BSI. "The same group" merges two labs through the shared author Staude. **Forward trace missing:** the CuBIC authors' own follow-up, Staude, Grün & Rotter 2010, *Front Comput Neurosci* 4:16 (doi 10.3389/fncom.2010.00016, PMC2906200, open access), adapts CuBIC to non-stationary rates. It bears on 1.9.5's shared-modulation prediction and is not cited. | major | Reword: "Ehm et al. 2007 had fitted rates per event size; Reimer et al. 2012 (Rotter's group) tested that method on renewal trains." Add Staude, Grün & Rotter 2010. Pull Reimer 2012 before claiming the general event-train form (see 9). | yes (abstracts via Europe PMC; CuBIC affiliations from the full text) |
| 9 | 1.1 Contribution 2; 1.9.1 "not found in spike-train or spatial statistics; Reimer et al. 2012 not read" | **Novelty claimed over an unread paper and an unsearched field.** The general form is a cluster process with a stationary non-Poisson center process. Its second- and third-order factorial moments, with the parent's pair correlation entering, are textbook point-process theory (Daley & Vere-Jones, ch. 6; Møller & Waagepetersen 2004; Møller & Christoffersen, arXiv 1711.08984, on cluster processes centered on non-Poisson states). 1.9.1 itself lists "factorial moments of cluster processes" as unsearched. "Not found in … spatial statistics" is too strong. The surrogate-dependence term may still be new. | major | Restrict the claim to the surrogate-dependence term and the at-most-one-event term *as applied to this tool*. Cite the general cluster-process moment formula. Read Reimer 2012 (doi 10.1016/j.jneumeth.2012.04.015, paywalled, for Tony). | partly (Møller & Christoffersen abstract only; textbooks not opened, ⚠) |
| 10 | 1.7 (whole section); 1.1 Contribution 7; 1.9.1 last row | **Contribution with no prior-art search, and an in-hand precedent not connected.** Mariani et al. 2025, already cited and in the library, is titled "…with overlapping global events". It says it is "the only method that allows to disentangle global events with overlap". That is the closest in-hand precedent for separating close events, and 1.7 does not mention it. Super-resolution and radar range resolution remain unsearched, as the chapter admits. | major | Cite Mariani 2025 in 1.7. Either search the resolution literature or move contribution 7 out of the contributions list into "results" with the ⚠ stated. | yes (Mariani) |
| 11 | 1.9.2 "Louis, Borgelt & Grün (2010, Fig. 6) separated two and three groups of different sizes" | **Overstated.** The text says Fig. 6(a)'s two groups (identical jitter) "are reliably distinguished", while in 6(b) "the correct identification of the three groups … is not as obvious". It also points to Schrader, Grün, Diesmann & Gerstein 2008 (*J Neurophysiol* 100:2165) for extracting overlapping groups. **PP-Seq** (Williams 2020), cited only as a generator, fits several sequence types with per-neuron offsets directly, which is the two-source problem. | minor | "separated two groups, and three less clearly". Cite Schrader 2008 and PP-Seq as prior art for separating sources in 1.9.2. | yes |
| 12 | 1.5, 1.9.1 "accidental-coincidence rates in particle physics and scan statistics (per the repository's prior-art record; not read here)"; "the assessor-specific run-start factor is new" | **Known-in-form claim with no citation at all.** Counting a clump only at its start (the q(1 − q)² factor) is the standard "declumping" of runs in scan statistics and Poisson-clumping theory (Arratia, Goldstein & Gordon 1990; Aldous 1989; Glaz, Naus & Wallenstein 2001). These are search targets I did not open. "New" is risky. | minor | Cite at least one accidental-coincidence source and one scan-statistics/declumping source. Call the run-start factor "the assessor-specific instance of declumping". | no (⚠, not opened) |
| 13 | 1.2.3 Assemblies, "building on Chapin & Nicolelis (1999 ⚠)" | **Not traced to the root.** Peyrache 2010 credits PCA of ensembles to Nicolelis et al. 1995 (*Science* 268:1353) *and* Chapin & Nicolelis 1999. Peyrache 2010 cites Marčenko & Pastur 1967 for the null. Lopes-dos-Santos 2011 credits the MP null to Peyrache 2010 [34] and 2009 [35], which supports the chapter. | minor | Add Nicolelis et al. 1995 and Marčenko & Pastur 1967. | yes |
| 14 | 1.6.2, 1.9.1 "Copeland ranking" | Copeland is named with no reference. Shah & Wainwright cite the root as [Cop51] (Copeland 1951, unpublished seminar notes). | minor | Cite Copeland 1951 as Shah & Wainwright do. | yes |
| 15 | 1.2.3 "building on Grün, Abeles & Diesmann (2008)" (no ⚠) vs 1.9.1 and the reference list (⚠) | The ⚠ marking is inconsistent. Louis 2010 confirms what the chapter says the 2008 paper did ("proposed in Grün et al. (2008)"), so the claim is supported one step removed. | minor | Mark ⚠ in 1.2.3 too, or open the LNCS chapter (doi 10.1007/978-3-540-88853-6_8). | yes (via Louis 2010) |
| 16 | References: Chapin 1999, Kreuz 2022, Kuhn 2003, Lopes-dos-Santos 2011, Peyrache 2009/2010, Schneider 2006, Staude 2008, Wang 2024 | **Entries incomplete.** No titles, and pages missing for some. Kreuz 2022 is "et al." only. Verified titles and DOIs: Chapin "Principal component analysis of neuronal ensemble activity reveals multidimensional somatosensory representations", 94:121–140, doi 10.1016/s0165-0270(99)00130-2. Kreuz T, Senocrate F, Cecchini G, Checcucci C, Allegra Mascaro AL, Conti E, et al. "Latency correction in sparse neuronal spike trains", doi 10.1016/j.jneumeth.2022.109703. Kuhn "Higher-order statistics of input ensembles and the response of simple model neurons", 15:67–101. Lopes-dos-Santos 2011 "Neuronal assembly detection and cell membership specification by principal component analysis". Peyrache 2009 "Replay of rule-learning related neural patterns in the prefrontal cortex during sleep", 12:919–926. Peyrache 2010 "Principal component analysis of ensemble recordings reveals cell assemblies at high temporal resolution", 29:309–325. Schneider "Spatiotemporal structure in large neuronal networks detected from cross-correlation", 18:2387–2413. Staude 2008 "Can spike coordination be differentiated from rate covariation?", 20:1973–1999. Wang 2024 "Spatiotemporal clustering with Neyman–Scott processes via connections to Bayesian nonparametric mixture models", 119:2382–2395. | minor | Complete the entries from these Crossref records. | yes |
| 17 | 1.2.3 "Rodriguez-Iturbe, Cox & Isham 1987 ⚠ … recover storm arrival rate and cells per storm" | A factual claim about an unread paper sits in the Background without hedging. It is also part of the novelty boundary for contribution 3. Secondary sources confirm it fits Neyman–Scott and Bartlett–Lewis models to 1–24 h statistics. That is not the same as confirming which parameters it recovers. | minor | Hedge the wording, or pull doi 10.1098/rspa.1987.0039 (paywalled, for Tony). Neyman, Scott & Shane 1953 (*ApJ* 117:92), counts-in-cells for the galaxy cluster model, is a further root to check for multi-scale count fitting. | no |

**Confirmed correct, no change needed:**
- Grün 1999 eq. 5 (the chapter's "±j" is the paper's s).
- Louis 2010's uniform-jitter binomial and two-line fit.
- Pazienti 2008.
- CuBIC's lower bound, carrier and eq. 3, and Kuhn's MIP as a special case.
- Thomas 1949 (no scatter law) and Waagepetersen's Thomas K-function.
- Kish 1995 pp. 63–64.
- The Kreuz 2017 quote.
- Coppersmith's factor 5 under weights that sum to one.
- Shah & Wainwright's independence assumption and JMLR 18(199).
- The Kreuz → Cecchini → Kreuz 2022 → Mariani lineage: Kreuz is last author on each, at ISC-CNR, so the "same group" wording is correct here.
- DeFazio 2026 (10 Hz imaging, fast and slow event types).

## Origin traces: where I stopped and why

- **Window sharing:** traced to Grün 1999, where the citations stop.
- **Multi-width reading:** Louis 2010 → Grün, Abeles & Diesmann 2008 (⚠, confirmed only through Louis).
- **Cumulant route:** CuBIC → Kuhn 2003 and Ehm 2007. Forward: Staude, Grün & Rotter 2010 and Reimer 2012 (abstracts only).
- **Cluster-process minimum contrast:** Waagepetersen 2007 → Diggle 1983 (⚠, not held). Diggle & Gratton 1984 is not on this path (finding 2).
- **τ–ρ relation:** Kruskal → Cramér, Esscher. Root is Greiner 1909 / Sheppard 1899, not opened.
- **Design effect:** Kish 1995 → Kish 1965 (⚠, not held).
- **Assembly PCA:** Lopes-dos-Santos → Peyrache 2010 → Chapin & Nicolelis 1999 and Nicolelis 1995 (not opened).
- **Order:** Kreuz 2017 → Kreuz 2026 (read per the repo record). Tomlinson 2019 (repo record) and Silva 2015 (repo record) are the side branches the chapter dropped.

## Literatures searched (my own search for this round)

- **Searched:**
  - Crossref and Europe PMC for all references.
  - Fluorescence fluctuation spectroscopy (FCA, TIFCA): **hit**, finding 1.
  - Cluster processes with non-Poisson parents (web): partial, finding 9.
  - History of the τ–ρ relation (web).
  - Rainfall Neyman–Scott models (web, abstract not reached).
  - The repository's prior_art/ and kreuz_sort/ records (for consistency, not as a substitute).
- **Not searched, residual ⚠:**
  - Photon-counting statistics in quantum optics beyond FCS (Mandel Q against bin time).
  - Counts-in-cells in astronomy (Neyman–Scott–Shane, and the later galaxy-clustering literature).
  - Daley & Vere-Jones / Møller & Waagepetersen texts (not opened).
  - Scan statistics and declumping (finding 12).
  - Super-resolution and radar range resolution for 1.7. The library's `radar/` shelf holds only CFAR papers.
  - Burst-detection merge rules (`coordination/cotterill_2016_burst_detector_comparison.pdf` is held and was not read).
  - 3d-SPADE / ASSET as the Grün group's later multi-scale work (forward trace of Louis 2010 not done beyond the repo record).

## Correspondence (asked of no one in this run)

1.9.1 says two enquiries (to the Grün lab and the Kreuz group) "have not been sent". But `docs/learned/synthetic_validation/kreuz_sort/README.md` says "a draft note is with Tony". **Residual ⚠, for Tony:** was the Kreuz note, or any note to Grün, Louis or Staude, ever sent or answered? If so, quote and date it. If not, finding 1 adds a third person worth one email: J. D. Müller (Minnesota), on whether TIFCA-style fits have been applied to jittered cluster processes.

## Paywalled or unopened items for Tony to pull

- Reimer et al. 2012, doi 10.1016/j.jneumeth.2012.04.015 (decides finding 9).
- Diggle 1983, *Statistical Analysis of Spatial Point Patterns*, ch. 5.
- Diggle 1978, doi 10.1111/j.2517-6161.1978.tb01660.x.
- Rodriguez-Iturbe, Cox & Isham 1987, doi 10.1098/rspa.1987.0039.
- Grün, Abeles & Diesmann 2008, doi 10.1007/978-3-540-88853-6_8.
- Wu & Müller 2005, full text (open access in PMC1366773).
- Greiner 1909 (Z. Math. Phys.).

## Sign-off

I would not sign until findings 1–5 and 8–10 are addressed. Finding 1 is the main one: the joint fit (contribution 3), and in part contribution 1, have a close methodological precedent in a field the chapter never searched.

Sources consulted on the web: [Wu & Müller 2005 (PMC1366773)](https://pmc.ncbi.nlm.nih.gov/articles/PMC1366773), [Müller 2004 (PMC1304299)](https://pmc.ncbi.nlm.nih.gov/articles/PMC1304299), [Wu, Singer & Müller TIFCA in cells (PMC4152916)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4152916), [Møller & Christoffersen, arXiv 1711.08984](https://arxiv.org/abs/1711.08984), [Kendall rank correlation (Greiner attribution)](https://en.wikipedia.org/wiki/Kendall_rank_correlation_coefficient), [Lindskog et al., Kendall's tau note](https://staff.math.su.se/lindskog/KendallsTau.pdf), [JMLR v18 paper 199](https://jmlr.org/papers/v18/16-206.html), [rainfall point-process review (ar5iv 1309.4632)](https://ar5iv.arxiv.org/html/1309.4632), Crossref and Europe PMC REST APIs.
