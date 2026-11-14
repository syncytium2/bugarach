GRANT 2 MISMATCH — missing none (WebSearch and WebFetch arrived as deferred tools and were loaded through ToolSearch); holds Edit, Write, PowerShell, Agent, Artifact, Skill, ToolSearch, Claude Docs batch/update, and deferred NotebookEdit, SendMessage and Dropbox and Gmail write tools

That mismatch is a finding about the run, for the ledger: this reviewer was spawned on a fallback path with editing tools. None of them was used on the repository. Writes went only to <scratch>/mb2/role02/.

# Role 2: DOI or Die. Chapter 1 (blob 0acfccbb)

**Scope.** I checked all 53 entries in the reference list, plus the named attributions in sections 1.2.3, 1.3.2, 1.4 (Prior work, Contributions), 1.5.6, 1.7, 1.8 and Table 1.9. I did not read anything under docs/reviews/.

**How I checked.**
- **Existence.** Every DOI (48, including the ones I found for references that print none) was resolved live through the doi.org handle API, and all 48 returned responseCode 1. Metadata was compared through the Crossref REST API.
- **References with no DOI:**
  - Kish 1995 was fetched live from the publisher, Statistics Sweden. Its page 1 reads JOS 11(1):55–77.
  - Greiner 1909 was checked through the zbMATH/JFM API: Z. Math. Phys. 57, 121–158, 225–260, 337–373.
  - Shah & Wainwright was checked on jmlr.org: 18(199):1–38.
  - Williams 2020 was checked on the NeurIPS 2020 proceedings site.
  - The arXiv preprints were checked through the arXiv API.
  - Finn & Johnson 1968: the RCA Review Sept 1968 issue scan returned 200 from the worldradiohistory archive.
- **Content.** Claims were checked against PDF text in <01-lit>. I rendered Kish 1995 pp. 63–64 as images.

## Findings
Each row gives location · issue · severity · suggested fix · verified against a source (yes/no).

1. **§1.2.3 (l.144–147), §1.4 Prior work (l.639–641): the wrong paper gets credit for the origin of cell-averaging CFAR.** · **High** · yes, to one step short of the root.
   - **The issue.** The chapter says Finn & Johnson (1968) were the ones who set the threshold "from an estimate of the background made in the reference cells around the cell under test." Their own footnotes 1–3 (p. 415) credit the clutter-estimate threshold to Finn's earlier papers.
   - **What Finn 1967 says.** Finn, H. M. (Dec 1967), "Adaptive Detection with Regulated Error Probabilities", *RCA Review* 28(4):653–678. I fetched it from the same archive and read it. Its summary on p. 653 already makes "the detection threshold at a resolution cell … proportional to an updated maximum-likelihood estimate of the output variance due to the clutter". On p. 658 that estimate is taken from "the N resolution cells surrounding the cell under test".
   - **The root.** Finn 1967 in turn cites Finn 1966, "Adaptive detection in clutter", Proc. Nat. Electronics Conf. 22:562 (Crossref: doi:10.1109/sap.1966.271149, pp. 562–567). That paper is paywalled, so I stopped one step short of the root.
   - **Same laboratory.** All three papers are by H. M. Finn at RCA (Moorestown and Camden).
   - **A misprint to avoid.** Finn & Johnson print Finn 1967 as "Vol. 29". The issue's contents page says Volume XXVIII, No. 4.
   - **Fix.** Credit Finn (1966, 1967) for the reference-cell threshold. Keep Finn & Johnson 1968 for the full analysis, including masking and target-pair resolution, both of which I confirmed are in it (pp. 415–416).

2. **References, Mariani et al. 2025: the first author's initial is wrong.** · **High** (wrong metadata) · yes.
   - The chapter gives "Mariani B". Both Crossref and the arXiv 2410.15018 PDF the chapter says it read give **Arturo** Mariani.
   - **Fix.** Change it to "Mariani A".

3. **§1.8.2 (l.1390), Table 1.9 row "One-template F": the root of the arcsine relation is missing, and the Greiner credit is unsupported.** · **Medium** · yes.
   - **What Kruskal 1958 actually says.** In §4 (p. 820) he gets ρ = sin(πτ/2) from the quadrant-measure relation, and in §3 he cites that relation to Cramér p. 290. His history section, §17, names **Sheppard 1899** as the originator of the quadrant measure and its population meaning. He never mentions Greiner.
   - **What Sheppard 1899 says.** Sheppard, W. F. (1899), *Phil Trans R Soc A* 192:101–167, doi:10.1098/rsta.1899.0003. I opened it from the Royal Society historical archive (it returned a PDF with no paywall). In §27, pp. 140–141, the double-median classes stand in the ratio (π − D):D with cos D = r. That is the arcsine relation.
   - **Greiner 1909.** It exists (JFM record, metadata matches) but was not opened. "Often credited to Greiner" has no source in hand.
   - **Fix.** Cite Sheppard 1899 as the root, Kruskal 1958 as the modern statement, and drop Greiner or give the source of the "often credited" claim.

4. **§1.4 Prior work (l.635–636): Malvache 2016 is cited for counting co-active cells against a threshold, but the method is much older.** · **Medium-low** · yes.
   - Cossart, Aronov & Yuste 2003, *Nature* 423:283–288 (doi:10.1038/nature01614; held at the top level of <01-lit>) already sets a threshold on the number of co-active cells per frame. It takes that threshold from interval-reshuffled surrogates (Methods: P < 0.05, 1,000 reshuffles). Its reference 12 for the reshuffling was not traced.
   - Malvache's own text does support the claim: Fig. 1 legend, "summed activity of cells (over a 200-ms window) … significance threshold".
   - **Fix.** Cite Cossart et al. 2003, or the earliest work found, as the origin, and Malvache 2016 as a modern instance.

5. **§1.4 (l.673–674), Table 1.9: Diggle 1978 is cited as the minimum-contrast source (⚠, paywalled).** · **Low-medium** · no.
   - Diggle 1978 exists: JRSS B 40(2):178–181, doi:10.1111/j.2517-6161.1978.tb01660.x. I did not read it.
   - The source usually cited for minimum contrast is Diggle 1979, *Biometrics* 35:87–101, doi:10.2307/2529938. Waagepetersen 2007 itself cites Diggle 2003 and Stoyan 1992 for it.
   - **Fix.** Check Diggle 1978 against the claim, or cite Diggle 1979. The paper is listed under "Papers needed" below.

6. **References, Møller & Waagepetersen: the year.** · **Low** · yes.
   - Crossref gives 2003 for the book (doi:10.1201/9780203496930), and Waagepetersen 2007 cites it as 2003. The chapter gives 2004.
   - **Fix.** Use 2003, or say why 2004 is used.

7. **References: incomplete entries.** · **Low** · yes.
   - Williams 2020 lacks the volume: NeurIPS 33.
   - Shah & Wainwright lacks the pages: 1–38.
   - Neyman & Scott lacks a page range.
   - Kish 1995 lacks the issue: 11(1).
   - Only Kreuz 2026 and Trunk 1978 print DOIs. The resolved DOIs for the rest are in <scratch>/mb2/role02/xref_out.txt.
   - **Fix.** Add the missing parts, and add DOIs throughout.

8. **Named attributions with no reference entry.** · **Low** · partly.
   - Marčenko–Pastur (l.688): not cited, though Peyrache 2010 and Lopes-dos-Santos 2011 cite it.
   - Ripley's pair-count function (l.674).
   - "Copeland counting": Shah & Wainwright credit Copeland 1951 [Cop51]. Borda is also named without a reference.
   - Grün 1996, which Table 1.9 names but which has no reference entry.
   - **Fix.** Add the references, or reword so these read plainly as names.

9. **Kreuz 2017, Mariani 2025, Shah & Wainwright 2018, Williams 2020 and Kreuz 2026 were read as preprints.** · **Low** · partly.
   - Each claim checked out against the preprint:
     - Kreuz 2017: the §3.1 quote "not sufficient to reliably compare two datasets with widely different number of spike trains and spikes" is verbatim, and §2.5 does reject the binomial null.
     - Mariani 2025: the extrapolation direct shift and overlapping events are in the abstract.
     - Kreuz 2026: §on SPIKE-order says the sorting is done "using simulated annealing".
     - Shah & Wainwright: "Copeland counting … a special case of the Borda count".
   - The wording in the journal versions was not compared.

10. **No-DOI checks that passed, recorded for the ledger.** · Info · yes.
    - The Grün 1999 PDF's first page prints "93 (1999)", but its running heads and Crossref give 94. The chapter's 94 is correct.
    - Crossref lists only Staude as author of Staude, Grün & Rotter 2010. The full-text XML has all three authors, so the chapter is correct.

## Claims verified against the source text
These were all correct:
- Rohling 1983:
  - guard cells in Fig. 3(b), used as a setup detail ("routine by 1983" is an inference, and the chapter states it honestly);
  - masking in Fig. 3;
  - the CA and CAGO comparison;
  - ordered-statistic CFAR introduced there.
- Finn & Johnson: they describe the noise-regulated CFAR that preceded them.
- Perkel 1967 does name the "cross-correlation histogram".
- Thomas 1949 gives quadrat counts only, with no scatter law.
- Diggle & Gratton's example is a pairwise-interaction inhibition process, not a cluster process.
- Waagepetersen: the Thomas K-function has a closed form, and the model is fitted by minimum contrast.
- Grün 1999, eq. 5: the fission probability under uniform jitter of ±s.
- Louis 2010:
  - uniform jitter with a binomial count;
  - the two-straight-line fit to Max2;
  - Fig. 6, two groups and then three;
  - the paper says it builds on Grün, Abeles & Diesmann 2008.
- Pazienti 2008, from its abstract.
- CuBIC: SIP and MIP (Kuhn 2003) are special cases.
- Wu & Müller 2005: simultaneous fit across binning times, with the variances of the cumulants.
- Kish 1995 p. 63, "a synthetic but useful 'ratio of homogeneity'", and p. 64, deft² = 1 + roh(n_c/a − 1).
- Kruskal 1958 §4.
- Tomlinson 2019: the DP net count and the shuffle null.
- Silva 2015: the best template is chosen in the shuffles too.
- Coppersmith 2006: the 5-approximation.
- Cecchini 2021 uses wide-field imaging.
- Williams 2020 is a Neyman–Scott model.
- DeFazio 2026 images at 10 Hz.
- Durbin 1951 really appeared in the Br J Psychol Statistical Section, vol. IV.

**Lab attributions checked by last author.** "Reimer … from Rotter's group" (Rotter is last author) and "the same group" for Cecchini 2021 and Mariani 2025 (Kreuz is last author) are consistent. I did not look up the affiliations separately.

## Fields searched and residuals
- **⚠ The novelty claim for g_n under Gaussian jitter (Contribution 1, Table 1.9).** I searched neuroscience (the Grün lineage), FCS cumulants and spatial point processes through the chapter's own sources, plus one web search of photon and quantum-optics coincidence counting. That search found Gaussian-jitter coincidence windows in photon counting but no closed form, so it is not conclusive. I did **not** search in depth:
  - nuclear and particle-physics coincidence counting with Gaussian timing resolution and finite bins, where the two-onset case may well be standard;
  - range distributions of normal samples (the chapter already discloses this one).
- **⚠ The lineage of fluorescence cumulant analysis before Müller 2004** (for example, moment analysis from 1990) was not searched.
- **⚠ Correspondence.** The chapter says no one has written to the Grün lab or the Kreuz group, so the "nobody was asked" residual stands. Before treating it as settled, ask Tony whether anyone ever wrote to Grün, Kreuz or Finn's successors.
- **Note.** The Kish 1965 PDF at the top level of <01-lit> is "Sampling Organizations and Groups of Unequal Sizes", not the book *Survey Sampling*. Do not use it as the Kish 1965 cited here.

## Papers needed (paywalled; not downloaded)
- Finn HM 1966, "Adaptive detection in clutter", doi:10.1109/sap.1966.271149: is it the root of the reference-cell threshold?
- Diggle PJ 1978, doi:10.1111/j.2517-6161.1978.tb01660.x: does it contain minimum contrast?

unreached: 0
